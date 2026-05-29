import http.client
import ssl
import threading
import time
from unittest import mock

import pytest

from openaq.core.transport import (
    ConnectionPool,
    Headers,
    Limits,
    PooledConnection,
    Response,
    Timeout,
    TimeoutError,
    Transport,
    _encode_params,
)


def make_response(
    status_code: int, body: bytes = b"", headers: dict | None = None
) -> Response:
    msg = http.client.HTTPMessage()
    if headers:
        for key, value in headers.items():
            msg[key] = value
    return Response(status_code, body, msg)


def make_raw_response(
    status: int = 200, body: bytes = b"{}", headers: dict | None = None
):
    msg = http.client.HTTPMessage()
    if headers:
        for k, v in headers.items():
            msg[k] = v
    raw = mock.Mock()
    raw.status = status
    raw.read.return_value = body
    raw.msg = msg
    return raw


def test_explicit_connect_overrides_timeout():
    t = Timeout(10.0, connect=3.0)
    assert t.connect == 3.0


class TestHeaders:
    def test_keys_are_lowercased_on_set(self):
        h = Headers()
        h["Content-Type"] = "application/json"
        assert "content-type" in h

    def test_get_is_case_insensitive(self):
        h = Headers({"X-API-Key": "abc"})
        assert h["x-api-key"] == "abc"
        assert h["X-API-Key"] == "abc"

    def test_contains_is_case_insensitive(self):
        h = Headers({"Accept": "application/json"})
        assert "accept" in h
        assert "Accept" in h
        assert "ACCEPT" in h

    def test_get_with_default(self):
        h = Headers()
        assert h.get("missing") is None
        assert h.get("missing", "default") == "default"

    def test_update_lowercases_keys(self):
        h = Headers()
        h.update({"X-Custom": "value"})
        assert "x-custom" in h

    def test_copy_is_independent(self):
        h = Headers({"key": "value"})
        h2 = h.copy()
        h2["key"] = "changed"
        assert h["key"] == "value"


class TestEncodeParams:
    def test_none_returns_empty(self):
        assert _encode_params(None) == ""

    def test_empty_dict_returns_empty(self):
        assert _encode_params({}) == ""

    def test_string_value(self):
        assert _encode_params({"key": "value"}) == "key=value"

    def test_int_value(self):
        assert _encode_params({"limit": 100}) == "limit=100"

    def test_float_value(self):
        assert _encode_params({"lat": 1.5}) == "lat=1.5"

    def test_bool_true_lowercased(self):
        assert _encode_params({"active": True}) == "active=true"

    def test_bool_false_lowercased(self):
        assert _encode_params({"active": False}) == "active=false"

    def test_multiple_params(self):
        result = _encode_params({"limit": 10, "page": 2})
        assert "limit=10" in result
        assert "page=2" in result


class TestResponse:
    def test_text_decodes_utf8(self):
        r = make_response(200, "héllo".encode("utf-8"))
        assert r.text == "héllo"

    def test_text_uses_charset_from_headers(self):
        msg = http.client.HTTPMessage()
        msg["Content-Type"] = "text/plain; charset=latin-1"
        r = Response(200, "café".encode("latin-1"), msg)
        assert r.text == "café"

    def test_text_falls_back_on_bad_charset(self):
        msg = http.client.HTTPMessage()
        msg["Content-Type"] = "text/plain; charset=nonexistent"
        r = Response(200, b"hello", msg)
        assert r.text == "hello"

    def test_json_parses_body(self):
        r = make_response(200, b'{"key": "value"}')
        assert r.json() == {"key": "value"}


class TestConnectionPool:
    def make_pool(self, max_connections=5, max_keepalive=3, expiry=30.0):
        limits = Limits(
            max_connections=max_connections,
            max_keepalive_connections=max_keepalive,
            keepalive_expiry=expiry,
        )
        return ConnectionPool(limits, connect_timeout=None)

    def test_acquire_creates_new_connection(self):
        pool = self.make_pool()
        pc = pool.acquire("api.openaq.org")
        assert isinstance(pc, PooledConnection)
        assert pc.host == "api.openaq.org"

    def test_acquire_reuses_idle_connection(self):
        pool = self.make_pool()
        pc = pool.acquire("api.openaq.org")
        pool.release(pc)
        pc2 = pool.acquire("api.openaq.org")
        assert pc is pc2

    def test_release_discard_closes_and_decrements(self):
        pool = self.make_pool()
        pc = pool.acquire("api.openaq.org")
        pc.conn.close = mock.Mock()
        pool.release(pc, discard=True)
        assert pool._total == 0
        pc.conn.close.assert_called_once()

    def test_idle_capped_at_max_keepalive(self):
        pool = self.make_pool(max_connections=10, max_keepalive=2)
        conns = [pool.acquire("api.openaq.org") for _ in range(3)]
        for pc in conns:
            pc.conn.close = mock.Mock()
            pool.release(pc)
        assert len(pool._idle["api.openaq.org"]) == 2

    def test_evicts_expired_connections(self):
        pool = self.make_pool(expiry=0.01)
        pc = pool.acquire("api.openaq.org")
        pool.release(pc)
        time.sleep(0.02)
        pool.acquire("api.openaq.org")
        assert pool._total == 1

    def test_blocks_when_pool_full(self):
        pool = self.make_pool(max_connections=1)
        pc = pool.acquire("api.openaq.org")

        acquired = threading.Event()
        result = []

        def try_acquire():
            acquired.set()
            result.append(pool.acquire("api.openaq.org", pool_timeout=1.0))

        t = threading.Thread(target=try_acquire)
        t.start()
        acquired.wait()
        time.sleep(0.05)
        pool.release(pc)
        t.join(timeout=2.0)
        assert len(result) == 1

    def test_raises_on_pool_timeout(self):
        pool = self.make_pool(max_connections=1)
        pool.acquire("api.openaq.org")
        with pytest.raises(TimeoutError, match="Connection pool exhausted"):
            pool.acquire("api.openaq.org", pool_timeout=0.05)

    def test_close_all_clears_pool(self):
        pool = self.make_pool()
        pc = pool.acquire("api.openaq.org")
        pool.release(pc)
        pool.close_all()
        assert pool._idle == {}
        assert pool._total == 0


class TestTransport:
    def make_transport(self, **kwargs) -> Transport:
        return Transport(**kwargs)

    def patch_pool(self, transport, raw_response):
        pc = mock.Mock()
        pc.conn.sock = None
        pc.host = "api.openaq.org"
        pc.conn.getresponse.return_value = raw_response
        acquire = mock.patch.object(transport._pool, 'acquire', return_value=pc)
        release = mock.patch.object(transport._pool, 'release')
        return acquire, release, pc

    def test_float_timeout_sets_both(self):
        t = Transport(timeout=5.0)
        assert t._connect_timeout == 5.0
        assert t._read_timeout == 5.0

    def test_send_request_encodes_params_in_path(self):
        transport = self.make_transport()
        raw = make_raw_response()
        acquire, release, pc = self.patch_pool(transport, raw)

        with acquire, release:
            transport.send_request(
                "GET", "https://api.openaq.org/v3/locations", {"limit": 10}, Headers()
            )
            call_path = pc.conn.request.call_args[0][1]
            assert "limit=10" in call_path

    def test_send_request_appends_params_with_ampersand_when_query_exists(self):
        transport = self.make_transport()
        raw = make_raw_response()
        acquire, release, pc = self.patch_pool(transport, raw)

        with acquire, release:
            transport.send_request(
                "GET",
                "https://api.openaq.org/v3/locations?page=1",
                {"limit": 10},
                Headers(),
            )
            call_path = pc.conn.request.call_args[0][1]
            assert "page=1" in call_path
            assert "limit=10" in call_path
            assert "&limit=10" in call_path

    def test_send_request_no_params_leaves_url_unchanged(self):
        transport = self.make_transport()
        raw = make_raw_response()
        acquire, release, pc = self.patch_pool(transport, raw)

        with acquire, release:
            transport.send_request(
                "GET", "https://api.openaq.org/v3/locations", None, Headers()
            )
            call_path = pc.conn.request.call_args[0][1]
            assert call_path == "/v3/locations"

    def test_retries_on_stale_connection(self):
        transport = self.make_transport()
        raw = make_raw_response()
        acquire, release, pc = self.patch_pool(transport, raw)
        pc.conn.getresponse.side_effect = [OSError("stale"), raw]

        with acquire, release:
            resp = transport._raw_request("GET", "api.openaq.org", "/v3/locations", {})
            assert resp.status_code == 200
            assert pc.conn.getresponse.call_count == 2

    def test_raises_after_two_failures(self):
        transport = self.make_transport()
        raw = make_raw_response()
        acquire, release, pc = self.patch_pool(transport, raw)
        pc.conn.getresponse.side_effect = OSError("stale")

        with acquire, release:
            with pytest.raises(OSError):
                transport._raw_request("GET", "api.openaq.org", "/v3/locations", {})

    def test_send_request_uppercases_method(self):
        transport = Transport()
        transport._raw_request = mock.Mock(
            return_value=Response(200, b'{}', http.client.HTTPMessage())
        )

        transport.send_request(
            "get", "https://api.openaq.org/v3/locations/1", None, Headers()
        )

        method = transport._raw_request.call_args.args[0]
        assert method == "GET"

    @pytest.mark.parametrize(
        "exc",
        [
            ssl.SSLCertVerificationError("cert verify failed"),
            ssl.SSLError("ssl error"),
        ],
    )
    def test_ssl_error_discards_connection_and_raises(self, exc):
        transport = self.make_transport()
        raw = make_raw_response()
        acquire, release, pc = self.patch_pool(transport, raw)
        pc.conn.request.side_effect = exc

        with acquire, release as mock_release:
            with pytest.raises(ssl.SSLError):
                transport._raw_request("GET", "api.openaq.org", "/v3/locations", {})
            mock_release.assert_called_once_with(pc, discard=True)

    def test_ssl_error_logs(self):
        transport = self.make_transport()
        raw = make_raw_response()
        acquire, release, pc = self.patch_pool(transport, raw)
        pc.conn.request.side_effect = ssl.SSLCertVerificationError("cert verify failed")

        with acquire, release:
            with pytest.raises(ssl.SSLCertVerificationError):
                with mock.patch("openaq.core.transport.logger") as mock_logger:
                    transport._raw_request("GET", "api.openaq.org", "/v3/locations", {})
            mock_logger.error.assert_called_once()

    def test_ssl_error_does_not_retry(self):
        transport = self.make_transport()
        raw = make_raw_response()
        acquire, release, pc = self.patch_pool(transport, raw)
        pc.conn.request.side_effect = ssl.SSLError("SSL error")

        with acquire, release:
            with pytest.raises(ssl.SSLError):
                transport._raw_request("GET", "api.openaq.org", "/v3/locations", {})
            assert pc.conn.request.call_count == 1
