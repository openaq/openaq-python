"""Base class and utlity functions for working with client transport."""

from __future__ import annotations

import http.client
import json
import logging
import ssl
import threading
import time
import urllib.parse
from collections import deque
from dataclasses import dataclass, field
from http import HTTPStatus
from typing import Any, Mapping

from openaq.core.exceptions import (
    BadGatewayError,
    BadRequestError,
    ForbiddenError,
    GatewayTimeoutError,
    HTTPRateLimitError,
    NotAuthorizedError,
    NotFoundError,
    ServerError,
    ServiceUnavailableError,
    TimeoutError,
    ValidationError,
)

logger = logging.getLogger(__name__)


@dataclass
class Timeout:
    """Configuration for request timeout values.

    Attributes:
        timeout: Default timeout in seconds applied to all values unless
            overridden.
        connect: Timeout in seconds for establishing a connection. Defaults to
            the value of ``timeout`` if not explicitly set.
        read: Timeout in seconds for reading a response.
        pool: Timeout in seconds to wait for a connection to become available
            from the connection pool.
    """

    timeout: float | None = 5.0
    connect: float | None = None
    read: float | None = 8.0
    pool: float | None = None

    def __post_init__(self) -> None:
        """Sets connect timeout to the default timeout value if not explicitly provided."""
        if self.connect is None:
            self.connect = self.timeout


@dataclass(kw_only=True)
class Limits:
    """Configuration for connection pool size and keep-alive behavior.

    Attributes:
        max_connections: Maximum number of connections allowed in the pool
            across all hosts.
        max_keepalive_connections: Maximum number of idle keep-alive connections
            per host.
        keepalive_expiry: Duration in seconds after which an idle connection is
            considered expired and discarded.
    """

    max_connections: int = 20
    max_keepalive_connections: int = 10
    keepalive_expiry: float = 30.0


class Headers(dict):
    """A case-insensitive dictionary for HTTP headers.

    Keys are normalized to lowercase on insertion and lookup, ensuring that
    header comparisons are case-insensitive as required by the HTTP spec.
    """

    def __init__(self, data: Mapping[str, str] | None = None) -> None:
        """Initializes Headers, optionally pre-populated from a mapping.

        Args:
            data: An optional mapping of header name-value pairs.
        """
        super().__init__()
        if data:
            for k, v in data.items():
                self[k] = v

    def __setitem__(self, key: str, value: str) -> None:
        """Sets a header, normalizing the key to lowercase."""
        super().__setitem__(key.lower(), value)

    def __getitem__(self, key: str) -> str:
        """Gets a header by key, normalizing the key to lowercase."""
        return super().__getitem__(key.lower())

    def __contains__(self, key: object) -> bool:
        """Checks if a header exists, normalizing the key to lowercase."""
        return super().__contains__(str(key).lower())

    def get(self, key: str, default: str | None = None) -> str | None:  # type: ignore[override]
        """Gets a header by key, normalizing the key to lowercase."""
        return super().get(key.lower(), default)

    def update(self, other: Mapping[str, str] | None = None, **kwargs: str) -> None:  # type: ignore[override]
        """Updates headers from a mapping or keyword arguments, normalizing keys to lowercase."""
        if other:
            for k, v in other.items():
                self[k] = v
        for k, v in kwargs.items():
            self[k] = v

    def copy(self) -> Headers:
        """Returns a shallow copy of this Headers instance.

        Returns:
            A new Headers instance with the same key-value pairs.
        """
        h = Headers()
        super(Headers, h).update(self)
        return h


class Response:
    """Represents an HTTP response returned from the server.

    Attributes:
        status_code: The HTTP status code of the response.
    """

    def __init__(
        self,
        status_code: int,
        raw_bytes: bytes,
        headers: http.client.HTTPMessage,
    ) -> None:
        """Initializes a Response.

        Args:
            status_code: The HTTP status code.
            raw_bytes: The raw response body as bytes.
            headers: The HTTP headers returned with the response.
        """
        self.status_code = status_code
        self._raw_bytes = raw_bytes
        self._http_headers = headers

    @property
    def text(self) -> str:
        """Decodes and returns the response body as a string.

        Uses the charset specified in the Content-Type header, falling back to
        UTF-8. Invalid byte sequences are replaced rather than raising an error.

        Returns:
            The response body as a decoded string.
        """
        charset = str(self._http_headers.get_param("charset") or "utf-8")
        try:
            return self._raw_bytes.decode(charset)
        except (LookupError, UnicodeDecodeError):
            return self._raw_bytes.decode("utf-8", errors="replace")

    @property
    def headers(self) -> Headers:
        """Returns the response headers as a case-insensitive Headers instance.

        Returns:
            A Headers instance containing the response headers.
        """
        return Headers(dict(self._http_headers))

    def json(self) -> Any:
        """Parses and returns the response body as JSON.

        Returns:
            The deserialized JSON content.
        """
        return json.loads(self._raw_bytes)


DEFAULT_TIMEOUT = Timeout(5.0, read=8.0)
DEFAULT_LIMITS = Limits(
    max_connections=20,
    max_keepalive_connections=10,
    keepalive_expiry=30.0,
)


@dataclass(slots=True)
class PooledConnection:
    """A pooled HTTPS connection with metadata for lifecycle management.

    Attributes:
        host: The hostname of the connection.
        connect_timeout: Timeout in seconds used when establishing the
            connection.
        last_used: Monotonic timestamp of when the connection was last returned
            to the pool, used to determine keep-alive expiry.
        conn: The underlying HTTPS connection object.
    """

    host: str
    connect_timeout: float | None
    last_used: float = field(default_factory=time.monotonic)
    conn: http.client.HTTPSConnection = field(init=False)

    def __post_init__(self) -> None:
        """Initializes the underlying HTTPS connection after the dataclass is created."""
        self.conn = http.client.HTTPSConnection(self.host, timeout=self.connect_timeout)


class ConnectionPool:
    """A thread-safe pool of reusable HTTPS connections.

    Manages a bounded set of connections across hosts, reusing idle connections
    where possible and blocking callers when the pool is at capacity.
    """

    def __init__(self, limits: Limits, connect_timeout: float | None) -> None:
        """Initializes the ConnectionPool.

        Args:
            limits: Pool size and keep-alive configuration.
            connect_timeout: Timeout in seconds for establishing new
                connections.
        """
        self._max_total = limits.max_connections
        self._max_idle = limits.max_keepalive_connections
        self._expiry = limits.keepalive_expiry
        self._connect_timeout = connect_timeout

        self._lock = threading.Lock()
        self._has_capacity = threading.Condition(self._lock)
        self._idle: dict[str, deque[PooledConnection]] = {}
        self._total: int = 0

    def _evict_expired(self, host: str) -> None:
        """Removes expired idle connections for a given host.

        Must be called while holding ``self._lock``.

        Args:
            host: The hostname whose idle connections should be checked for
                expiry.
        """
        q = self._idle.get(host)
        if not q:
            return
        now = time.monotonic()
        while q and (now - q[0].last_used) > self._expiry:
            pc = q.popleft()
            try:
                pc.conn.close()
            except Exception:
                pass
            self._total -= 1

    def acquire(self, host: str, pool_timeout: float | None = None) -> PooledConnection:
        """Checks out a connection for the given host.

        Reuses an idle connection if one is available, or creates a new one if
        the pool has capacity. Blocks until a connection becomes available or the
        timeout is exceeded.

        Args:
            host: The hostname to acquire a connection for.
            pool_timeout: Maximum number of seconds to wait for a connection to
                become available. Blocks indefinitely if ``None``.

        Returns:
            A PooledConnection ready for use.

        Raises:
            TimeoutError: If no connection becomes available within ``pool_timeout`` seconds.
        """
        deadline = (time.monotonic() + pool_timeout) if pool_timeout else None

        with self._has_capacity:
            while True:
                self._evict_expired(host)
                q = self._idle.get(host)
                if q:
                    pc = q.pop()
                    return pc
                if self._total < self._max_total:
                    self._total += 1
                    return PooledConnection(host, self._connect_timeout)
                if deadline is not None:
                    remaining = deadline - time.monotonic()
                    if remaining <= 0:
                        raise TimeoutError(
                            f"Connection pool exhausted for {host!r}: "
                            f"no slot available within {pool_timeout}s"
                        )
                    self._has_capacity.wait(timeout=remaining)
                else:
                    self._has_capacity.wait()

    def release(self, pc: PooledConnection, *, discard: bool = False) -> None:
        """Returns a connection to the pool after use.

        If ``discard`` is True, or the idle queue for the host is full, the
        connection is closed and removed from the total count instead.

        Args:
            pc: The PooledConnection to release.
            discard: If True, closes and discards the connection rather than
                returning it to the idle queue.
        """
        with self._has_capacity:
            if discard:
                try:
                    pc.conn.close()
                except Exception:
                    pass
                self._total -= 1
                self._has_capacity.notify_all()
                return
            q = self._idle.setdefault(pc.host, deque())
            if len(q) < self._max_idle:
                pc.last_used = time.monotonic()
                q.append(pc)
            else:
                try:
                    pc.conn.close()
                except Exception:
                    pass
                self._total -= 1
            self._has_capacity.notify_all()

    def close_all(self) -> None:
        """Closes all idle connections in the pool and resets its state."""
        with self._lock:
            for q in self._idle.values():
                for pc in q:
                    try:
                        pc.conn.close()
                    except Exception:
                        pass
            self._idle.clear()
            self._total = 0


def _encode_params(
    params: Mapping[str, str | int | float | bool] | None,
) -> str:
    """Encodes a mapping of query parameters into a URL query string.

    Boolean values are serialized as lowercase strings (``true``/``false``)
    to match common API conventions.

    Args:
        params: A mapping of parameter names to values, or ``None``.

    Returns:
        A percent-encoded query string, or an empty string if ``params`` is
        ``None`` or empty.
    """
    if not params:
        return ""
    return urllib.parse.urlencode(
        {k: str(v).lower() if isinstance(v, bool) else v for k, v in params.items()}
    )


class Transport:
    """Handles sending HTTP requests over a managed connection pool.

    Wraps a ConnectionPool to provide a request interface with configurable
    timeouts, automatic retry on stale connections, and response validation.
    """

    def __init__(
        self,
        timeout: float | Timeout | None = DEFAULT_TIMEOUT,
        limits: Limits = DEFAULT_LIMITS,
    ) -> None:
        """Initializes the Transport.

        Args:
            timeout: Timeout configuration for connect, read, and pool wait
                durations. Accepts a Timeout instance, a single float applied to
                all phases, or ``None`` to disable timeouts entirely.
            limits: Connection pool size and keep-alive configuration.
        """
        if isinstance(timeout, Timeout):
            self._connect_timeout = timeout.connect
            self._read_timeout = timeout.read
            self._pool_timeout = timeout.pool
        elif isinstance(timeout, (int, float)):
            self._connect_timeout = float(timeout)
            self._read_timeout = float(timeout)
            self._pool_timeout = None
        else:
            self._connect_timeout = None
            self._read_timeout = None
            self._pool_timeout = None

        self._pool = ConnectionPool(limits, self._connect_timeout)

    def _raw_request(
        self,
        method: str,
        host: str,
        path: str,
        headers: Mapping[str, str],
    ) -> Response:
        """Sends a raw HTTP request, retrying once on a stale connection.

        Attempts the request up to twice. If the first attempt fails due to a
        stale connection, the connection is discarded and the request is
        retried. If the second attempt fails, the exception is raised to the
        caller.

        Args:
            method: The HTTP method (e.g. ``'GET'``, ``'POST'``).
            host: The target hostname.
            path: The request path, including any query string.
            headers: A mapping of HTTP headers to include with the request.

        Returns:
            A Response containing the status code, headers, and body.

        Raises:
            OSError: If the connection fails on both attempts.
            http.client.HTTPException: If an HTTP protocol error occurs on both attempts.
        """
        for attempt in range(2):
            pc = self._pool.acquire(host, self._pool_timeout)
            try:
                pc.conn.request(method, path, headers=dict(headers))
                if self._read_timeout is not None and pc.conn.sock is not None:
                    pc.conn.sock.settimeout(self._read_timeout)
                raw = pc.conn.getresponse()
                body = raw.read()
                resp = Response(raw.status, body, raw.msg)
                self._pool.release(pc)
                return resp

            except ssl.SSLCertVerificationError as exc:
                self._pool.release(pc, discard=True)
                logger.error(
                    "SSL certificate verification failed for %s: %s. "
                    "On macOS, run 'Install Certificates.command' in your Python "
                    "installation directory to fix this.",
                    host,
                    exc,
                )
                raise

            except ssl.SSLError as exc:
                self._pool.release(pc, discard=True)
                logger.error("SSL error for %s: %s", host, exc)
                raise

            except (OSError, http.client.HTTPException) as exc:
                self._pool.release(pc, discard=True)
                if attempt == 1:
                    raise
                logger.debug("Stale connection, retrying: %s", exc)

        raise RuntimeError("unreachable")  # pragma: no cover

    def send_request(
        self,
        method: str,
        url: str,
        params: Mapping[str, str | int | float | bool] | None,
        headers: Headers | Mapping[str, str],
    ) -> Response:
        """Builds and sends an HTTP request, returning a validated response.

        Appends encoded query parameters to the URL if provided, then dispatches
        the request through the connection pool.

        Args:
            method: The HTTP method (e.g. ``'GET'``, ``'POST'``).
            url: The fully qualified request URL.
            params: Optional query parameters to append to the URL.
            headers: HTTP headers to include with the request.

        Returns:
            A validated Response object.
        """
        qs = _encode_params(params)
        if qs:
            separator = "&" if "?" in url else "?"
            url = f"{url}{separator}{qs}"

        logger.debug(
            "Sending request to: %s",
            url,
            extra={"method": method, "url": url, "params": params},
        )

        parsed = urllib.parse.urlparse(url)
        host = parsed.netloc
        path = parsed.path or "/"
        if parsed.query:
            path = f"{path}?{parsed.query}"

        res = self._raw_request(method.upper(), host, path, headers)
        logger.debug("Received response: %s from %s", res.status_code, url)
        return check_response(res)

    def close(self) -> None:
        """Closes all pooled connections and releases pool resources."""
        self._pool.close_all()


def check_response(res: Response) -> Response:
    """Checks the HTTP response of the request.

    Args:
        res: a Response object

    Returns:
        Response

    Raises:
        BadRequestError: Raised for HTTP 400 error, indicating a client request error.
        NotAuthorizedError: Raised for HTTP 401 error, indicating the client is not authorized.
        ForbiddenError: Raised for HTTP 403 error, indicating the request is forbidden.
        NotFoundError: Raised for HTTP 404 error, indicating a resource is not found.
        TimeoutError: Raised for HTTP 408 error, indicating the request has timed out.
        ValidationError: Raised for HTTP 422 error, indicating invalid request parameters.
        HTTPRateLimitError: Raised for HTTP 429 error, indicating rate limit exceeded.
        ServerError: Raised for HTTP 500 error, indicating an internal server error or unexpected server-side issue.
        BadGatewayError: Raised for HTTP 502, indicating that the gateway or proxy received an invalid response from the upstream server.
        ServiceUnavailableError: Raised for HTTP 503, indicating that the server is not ready to handle the request.
        GatewayTimeoutError: Raised for HTTP 504 error, indicating a gateway timeout.
    """
    if res.status_code >= HTTPStatus.OK and res.status_code < HTTPStatus.BAD_REQUEST:
        return res
    elif res.status_code == HTTPStatus.BAD_REQUEST:
        logger.exception(f"HTTP {res.status_code} - {res.text}")
        raise BadRequestError(res.text)
    elif res.status_code == HTTPStatus.NOT_FOUND:
        logger.exception(f"HTTP {res.status_code} - {res.text}")
        raise NotFoundError(res.text)
    elif res.status_code == HTTPStatus.REQUEST_TIMEOUT:
        logger.exception(f"HTTP {res.status_code} - {res.text}")
        raise TimeoutError(res.text)
    elif res.status_code == HTTPStatus.FORBIDDEN:
        logger.exception(f"HTTP {res.status_code} - {res.text}")
        raise ForbiddenError(res.text)
    elif res.status_code == HTTPStatus.UNPROCESSABLE_ENTITY:
        logger.exception(f"HTTP {res.status_code} - {res.text}")
        raise ValidationError(res.text)
    elif res.status_code == HTTPStatus.TOO_MANY_REQUESTS:
        logger.exception(f"HTTP {res.status_code} - {res.text}")
        raise HTTPRateLimitError(res.text)
    elif res.status_code == HTTPStatus.UNAUTHORIZED:
        logger.exception(f"HTTP {res.status_code} - {res.text}")
        raise NotAuthorizedError(res.text)
    elif res.status_code == HTTPStatus.INTERNAL_SERVER_ERROR:
        logger.exception(f"HTTP {res.status_code} - {res.text}")
        raise ServerError(res.text)
    elif res.status_code == HTTPStatus.BAD_GATEWAY:
        logger.exception(f"HTTP {res.status_code} - {res.text}")
        raise BadGatewayError(res.text)
    elif res.status_code == HTTPStatus.SERVICE_UNAVAILABLE:
        logger.exception(f"HTTP {res.status_code} - {res.text}")
        raise ServiceUnavailableError(res.text)
    elif res.status_code == HTTPStatus.GATEWAY_TIMEOUT:
        logger.exception(f"HTTP {res.status_code} - {res.text}")
        raise GatewayTimeoutError(
            "Your request timed out on the server. "
            "Consider reducing the complexity of your request."
        )
    else:
        logger.exception(f"HTTP {res.status_code} - {res.text}")
        raise Exception
