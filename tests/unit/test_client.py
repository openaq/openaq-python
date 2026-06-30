import http
import os
import platform
from datetime import datetime, timedelta
from pathlib import Path
from unittest.mock import MagicMock, Mock, mock_open, patch

import pytest
from freezegun import freeze_time

from openaq import __version__
from openaq.client import OpenAQ, _check_api_key, _get_openaq_config, _has_toml
from openaq.core.exceptions import ApiKeyMissingError, RateLimitError
from openaq.core.transport import (
    DEFAULT_LIMITS,
    DEFAULT_TIMEOUT,
    Headers,
)

from .mocks import MockTransport

USER_AGENT = f"openaq-python-{__version__}-{platform.python_version()}"


@pytest.mark.parametrize(
    "api_key, expected_exception",
    [
        ("a" * 64, None),
        ("f" * 64, None),
        ("0" * 64, None),
        ("f" * 63, ApiKeyMissingError),
        ("f" * 65, ApiKeyMissingError),
        ("A" * 64, ApiKeyMissingError),
        ("g" * 64, ApiKeyMissingError),
        ("f" * 63 + "!", ApiKeyMissingError),
        ("", ApiKeyMissingError),
        (12345, ApiKeyMissingError),
        (None, ApiKeyMissingError),
        (b"f" * 64, ApiKeyMissingError),
    ],
    ids=[
        "invalid non-hex lowercase",
        "valid hex lowercase f",
        "valid hex lowercase 0",
        "too short 63 chars",
        "too long 65 chars",
        "uppercase hex rejected",
        "non-hex character",
        "special character",
        "empty string",
        "invalid type int",
        "invalid type None",
        "invalid type bytes",
    ],
)
def test__check_api_key(api_key, expected_exception):
    if expected_exception:
        with pytest.raises(expected_exception):
            _check_api_key(api_key)
    else:
        result = _check_api_key(api_key)
        assert result == api_key


def apply_rate_limit_headers(client, *, at, remaining, ttl):
    msg = http.client.HTTPMessage()
    msg["x-ratelimit-limit"] = "60"
    msg["x-ratelimit-remaining"] = str(remaining)
    msg["x-ratelimit-reset"] = str(ttl)
    with freeze_time(at):
        client._set_rate_limit(Headers(msg))


@pytest.fixture
def mock_config_file():
    mock_toml_content = b"""api-key='e7a3a978e3e018e932d666c481ff33b82b7150c6084c0de175755c5cb763a5c5'"""
    with patch.object(Path, "is_file", return_value=True):
        with patch(
            "builtins.open", mock_open(read_data=mock_toml_content)
        ) as mock_file:
            yield mock_file


class TestClient:
    @pytest.fixture()
    def setup(self):
        self.client = OpenAQ(
            api_key="e7a3a978e3e018e932d666c481ff33b82b7150c6084c0de175755c5cb763a5c5",
            _transport=MockTransport(),
        )

    @pytest.fixture()
    def mock_openaq_api_key_env_vars(self):
        with patch.dict(
            os.environ,
            {
                "OPENAQ_API_KEY": "e7a3a978e3e018e932d666c481ff33b82b7150c6084c0de175755c5cb763a5c5"
            },
        ):
            yield

    def test_transport_property(self, setup):
        assert isinstance(self.client._transport, MockTransport)
        with pytest.raises(AttributeError):
            self.client.transport = MockTransport()

    def test_default_client_params(self, setup):
        assert self.client._base_url == "https://api.openaq.org/v3/"

    def test_default_headers(self, setup):
        assert self.client.headers["User-Agent"] == USER_AGENT
        assert self.client.headers["Accept"] == "application/json"

    def test_custom_headers(self, setup):
        self.client = OpenAQ(
            api_key="e7a3a978e3e018e932d666c481ff33b82b7150c6084c0de175755c5cb763a5c5",
            base_url="https://mycustom.openaq.org",
            _transport=MockTransport(),
        )
        assert (
            self.client.headers["X-API-Key"]
            == "e7a3a978e3e018e932d666c481ff33b82b7150c6084c0de175755c5cb763a5c5"
        )

    def test_client_params(self, setup):
        self.client = OpenAQ(
            api_key="e7a3a978e3e018e932d666c481ff33b82b7150c6084c0de175755c5cb763a5c5",
            base_url="https://mycustom.openaq.org",
            _transport=MockTransport(),
        )
        assert self.client._base_url == "https://mycustom.openaq.org"

    def test_api_env_var(self, mock_openaq_api_key_env_vars):
        client = OpenAQ(_transport=MockTransport())
        assert (
            client.api_key
            == "e7a3a978e3e018e932d666c481ff33b82b7150c6084c0de175755c5cb763a5c5"
        )

    @pytest.mark.usefixtures("mock_config_file")
    def test_api_key_from_config(self):
        if int(platform.python_version_tuple()[1]) >= 11:
            client = OpenAQ(_transport=MockTransport())
            assert (
                client.api_key
                == "e7a3a978e3e018e932d666c481ff33b82b7150c6084c0de175755c5cb763a5c5"
            )
        else:
            with pytest.raises(ApiKeyMissingError):
                client = OpenAQ(_transport=MockTransport())

    def test_api_key_arg_override_env_var(self, setup, mock_openaq_api_key_env_vars):
        assert (
            self.client.api_key
            == "e7a3a978e3e018e932d666c481ff33b82b7150c6084c0de175755c5cb763a5c5"
        )

    def test_api_key_arg_override_config(self, setup, mock_config_file):
        assert (
            self.client.api_key
            == "e7a3a978e3e018e932d666c481ff33b82b7150c6084c0de175755c5cb763a5c5"
        )

    def test_api_key_arg_override_env_vars_config(
        self, setup, mock_openaq_api_key_env_vars, mock_config_file
    ):
        assert (
            self.client.api_key
            == "e7a3a978e3e018e932d666c481ff33b82b7150c6084c0de175755c5cb763a5c5"
        )

    def test_raises_api_key_missing_error_when_key_is_none(self):
        with pytest.raises(ApiKeyMissingError):
            OpenAQ(api_key=None, _transport=MockTransport())

    @patch("openaq.client.datetime")
    @patch("time.sleep")
    @patch("openaq.client.logger")
    def test_wait_for_rate_limit_reset_waits_when_positive(
        self, mock_logger, mock_sleep, mock_datetime, setup
    ):
        now = datetime(2026, 2, 12, 0, 0, 0)
        mock_datetime.now.return_value = now
        self.client._rate_limit_reset_datetime = now + timedelta(seconds=5)

        self.client._wait_for_rate_limit_reset()

        mock_sleep.assert_called_once_with(5)
        mock_logger.info.assert_called_once_with(
            "Rate limit hit. Waiting %s seconds for reset.", 5
        )

    @patch("openaq.client.datetime")
    @patch("time.sleep")
    @patch("openaq.client.logger")
    def test_wait_for_rate_limit_reset_waits_minimum_when_zero(
        self, mock_logger, mock_sleep, mock_datetime, setup
    ):
        """ttl=0 from server should still wait 1 second to avoid racing the boundary."""
        now = datetime(2026, 2, 12, 0, 0, 0)
        mock_datetime.now.return_value = now
        self.client._rate_limit_reset_datetime = now

        self.client._wait_for_rate_limit_reset()

        mock_sleep.assert_called_once_with(1)
        mock_logger.info.assert_called_once_with(
            "Rate limit hit. Waiting %s seconds for reset.", 1
        )

    @patch("openaq.client.datetime")
    @patch("time.sleep")
    @patch("openaq.client.logger")
    def test_wait_for_rate_limit_reset_waits_minimum_when_negative(
        self, mock_logger, mock_sleep, mock_datetime, setup
    ):
        """Reset time in the past (e.g. key expired mid-flight) should still wait 1 second."""
        now = datetime(2026, 2, 12, 0, 0, 1)
        mock_datetime.now.return_value = now
        self.client._rate_limit_reset_datetime = datetime(2026, 2, 12, 0, 0, 0)

        self.client._wait_for_rate_limit_reset()

        mock_sleep.assert_called_once_with(1)
        mock_logger.info.assert_called_once_with(
            "Rate limit hit. Waiting %s seconds for reset.", 1
        )

    @patch("openaq.client.datetime")
    @patch("time.sleep")
    @patch("openaq.client.logger")
    def test_wait_for_rate_limit_reset_waits_minimum_when_far_negative(
        self, mock_logger, mock_sleep, mock_datetime, setup
    ):
        """Reset time well in the past should also wait the minimum 1 second."""
        now = datetime(2026, 2, 12, 0, 0, 0)
        mock_datetime.now.return_value = now
        self.client._rate_limit_reset_datetime = now - timedelta(seconds=5)

        self.client._wait_for_rate_limit_reset()

        mock_sleep.assert_called_once_with(1)
        mock_logger.info.assert_called_once_with(
            "Rate limit hit. Waiting %s seconds for reset.", 1
        )

    @patch("openaq.client.datetime")
    @patch("time.sleep")
    @patch("openaq.client.logger")
    def test_wait_for_rate_limit_reset_never_sleeps_zero(
        self, mock_logger, mock_sleep, mock_datetime, setup
    ):
        now = datetime(2026, 6, 16, 0, 0, 59)
        mock_datetime.now.return_value = now
        self.client._rate_limit_reset_datetime = now

        self.client._wait_for_rate_limit_reset()

        call_args = mock_sleep.call_args[0][0]
        assert (
            call_args >= 1
        ), f"sleep({call_args}) is too short. Must wait at least 1 second when ttl=0."

    def test_close_closes_transport(self, setup):
        self.client._transport.close = Mock()
        self.client.close()
        self.client._transport.close.assert_called_once()

    def test_context_manager_enter_returns_client(self, setup):
        with self.client as ctx_client:
            assert ctx_client is self.client

    def test_context_manager_exit_closes_transport(self, setup):
        self.client._transport.close = Mock()
        with self.client:
            pass
        self.client._transport.close.assert_called_once()

    def test_context_manager_exit_closes_even_with_exception(self, setup):
        self.client._transport.close = Mock()
        with pytest.raises(ValueError):
            with self.client:
                raise ValueError("Test exception")
        self.client._transport.close.assert_called_once()

    def test_blocks_after_custom_limit(self):
        client = OpenAQ(
            api_key="e7a3a978e3e018e932d666c481ff33b82b7150c6084c0de175755c5cb763a5c5",
            _transport=MockTransport(),
            auto_wait=False,
            rate_limit_override=5,
        )
        client._rate_limit_reset_datetime = datetime.now() + timedelta(seconds=60)
        for _ in range(5):
            client._check_rate_limit()

        with pytest.raises(RateLimitError):
            client._check_rate_limit()

    def test_allows_exactly_override_requests(self):
        limit = 10
        client = OpenAQ(
            api_key="e7a3a978e3e018e932d666c481ff33b82b7150c6084c0de175755c5cb763a5c5",
            _transport=MockTransport(),
            auto_wait=False,
            rate_limit_override=limit,
        )
        client._rate_limit_reset_datetime = datetime.now() + timedelta(seconds=60)
        success_count = 0
        for _ in range(limit + 5):
            try:
                client._check_rate_limit()
                success_count += 1
            except RateLimitError:
                break

        assert success_count == limit

    def test_raises_when_exhausted_and_auto_wait_false(self, setup):
        self.client._auto_wait = False
        self.client._rate_limit_remaining = 0.0
        self.client._rate_limit_reset_datetime = datetime.now() + timedelta(seconds=30)

        with pytest.raises(RateLimitError):
            self.client._check_rate_limit()

    @freeze_time("2026-02-12T00:00:00")
    def test_error_message_includes_reset_seconds(self, setup):
        self.client._auto_wait = False
        self.client._rate_limit_remaining = 0.0
        self.client._rate_limit_reset_datetime = datetime(2026, 2, 12, 0, 0, 30)

        with pytest.raises(RateLimitError, match="30"):
            self.client._check_rate_limit()

    @patch("time.sleep")
    def test_waits_when_exhausted_and_auto_wait_true(self, mock_sleep, setup):
        self.client._auto_wait = True
        self.client._rate_limit_remaining = 0.0
        self.client._rate_limit_reset_datetime = datetime.now() + timedelta(seconds=10)

        self.client._check_rate_limit()

        mock_sleep.assert_called_once()

    @patch("time.sleep")
    def test_resets_capacity_after_wait(self, mock_sleep, setup):
        self.client._auto_wait = True
        self.client._rate_limit_remaining = 0.0
        self.client._rate_limit_reset_datetime = datetime.now() + timedelta(seconds=10)

        self.client._check_rate_limit()

        assert self.client._rate_limit_remaining == self.client._rate_limit_capacity - 1

    def test_set_rate_limit_updates_remaining_from_headers(self, setup):
        headers = Headers({"x-ratelimit-remaining": "45", "x-ratelimit-reset": "60"})
        self.client._set_rate_limit(headers)
        assert self.client._rate_limit_remaining == 45

    def test_set_rate_limit_server_remaining_overrides_local_count(self, setup):
        self.client._rate_limit_remaining = 50.0
        headers = Headers({"x-ratelimit-remaining": "30", "x-ratelimit-reset": "60"})
        self.client._set_rate_limit(headers)
        assert self.client._rate_limit_remaining == 30

    def test_set_rate_limit_updates_reset_datetime_from_headers(self, setup):
        headers = Headers({"x-ratelimit-remaining": "45", "x-ratelimit-reset": "30"})
        before = datetime.now() + timedelta(seconds=29)
        self.client._set_rate_limit(headers)
        after = datetime.now() + timedelta(seconds=32)

        assert before < self.client._rate_limit_reset_datetime < after

    def test_set_rate_limit_missing_headers_does_not_raise(self, setup):
        headers = Headers({})
        try:
            self.client._set_rate_limit(headers)
        except Exception as e:
            pytest.fail(f"Unexpected exception raised: {e}")

    def test_set_rate_limit_remaining_allows_further_requests(self, setup):
        headers = Headers({"x-ratelimit-remaining": "2", "x-ratelimit-reset": "30"})
        self.client._set_rate_limit(headers)
        self.client._auto_wait = False

        self.client._check_rate_limit()
        self.client._check_rate_limit()

        with pytest.raises(RateLimitError):
            self.client._check_rate_limit()

    def test_do_calls_transport_with_correct_args(self, setup):
        mock_response = MagicMock()
        mock_response.headers = Headers({})
        self.client._transport.send_request = Mock(return_value=mock_response)

        self.client._do("get", "locations/1")

        call_kwargs = self.client._transport.send_request.call_args
        assert call_kwargs.kwargs["url"] == "https://api.openaq.org/v3/locations/1"
        assert call_kwargs.kwargs["method"] == "get"

    def test_do_passes_params_to_transport(self, setup):
        mock_response = MagicMock()
        mock_response.headers = Headers({})
        self.client._transport.send_request = Mock(return_value=mock_response)

        self.client._do("get", "/test", params={"limit": 100, "page": 1})

        call_kwargs = self.client._transport.send_request.call_args
        assert call_kwargs.kwargs["params"] == {"limit": 100, "page": 1}

    def test_do_passes_custom_headers_to_transport(self, setup):
        mock_response = MagicMock()
        mock_response.headers = Headers({})
        self.client._transport.send_request = Mock(return_value=mock_response)

        self.client._do("get", "/test", headers={"X-Custom-Header": "value"})

        call_kwargs = self.client._transport.send_request.call_args
        assert "x-custom-header" in call_kwargs.kwargs["headers"]

    def test_do_syncs_rate_limit_from_response_headers(self, setup):
        mock_response = MagicMock()
        mock_response.headers = Headers(
            {"x-ratelimit-remaining": "42", "x-ratelimit-reset": "30"}
        )
        self.client._transport.send_request = Mock(return_value=mock_response)

        self.client._do("get", "/test")

        assert self.client._rate_limit_remaining == 42

    def test_do_raises_before_sending_when_rate_limited(self, setup):
        self.client._auto_wait = False
        self.client._rate_limit_remaining = 0
        self.client._rate_limit_reset_datetime = datetime.now() + timedelta(seconds=30)
        self.client._transport.send_request = Mock()

        with pytest.raises(RateLimitError):
            self.client._do("get", "/test")

        self.client._transport.send_request.assert_not_called()

    def test_default_timeout_applied_to_transport(self):
        client = OpenAQ(
            api_key="e7a3a978e3e018e932d666c481ff33b82b7150c6084c0de175755c5cb763a5c5"
        )
        assert client._transport._connect_timeout == DEFAULT_TIMEOUT.connect
        assert client._transport._read_timeout == DEFAULT_TIMEOUT.read

    def test_default_limits_applied_to_transport(self):
        client = OpenAQ(
            api_key="e7a3a978e3e018e932d666c481ff33b82b7150c6084c0de175755c5cb763a5c5"
        )
        assert client._transport._pool._max_total == DEFAULT_LIMITS.max_connections
        assert (
            client._transport._pool._max_idle
            == DEFAULT_LIMITS.max_keepalive_connections
        )

    def test_do_does_not_produce_double_slash_in_url(self, setup):
        """Leading slash on path should not create double slash when base_url has trailing slash."""
        mock_response = MagicMock()
        mock_response.headers = Headers({})
        self.client._transport.send_request = Mock(return_value=mock_response)

        self.client._do("get", "/locations/1")

        call_kwargs = self.client._transport.send_request.call_args
        url = call_kwargs.kwargs["url"]
        assert "//" not in url.replace(
            "https://", ""
        ), f"URL contains double slash: {url}"

    def test_raises_value_error_for_base_url_without_scheme(self):
        with pytest.raises(ValueError, match="Invalid base_url"):
            OpenAQ(
                api_key="e7a3a978e3e018e932d666c481ff33b82b7150c6084c0de175755c5cb763a5c5",
                base_url="api.openaq.org/v3/",
                _transport=MockTransport(),
            )

    def test_raises_value_error_for_base_url_without_netloc(self):
        with pytest.raises(ValueError, match="Invalid base_url"):
            OpenAQ(
                api_key="e7a3a978e3e018e932d666c481ff33b82b7150c6084c0de175755c5cb763a5c5",
                base_url="https://",
                _transport=MockTransport(),
            )

    def test_production_replay_20260628(self, setup):
        apply_rate_limit_headers(
            self.client, at="2026-06-28 17:55:44.59+00", remaining=1, ttl=11
        )
        with freeze_time("2026-06-28 17:55:50.1+00"):
            self.client._check_rate_limit()

            apply_rate_limit_headers(
                self.client, at="2026-06-28 17:55:50.1+00", remaining=0, ttl=10
            )

        with (
            freeze_time("2026-06-28 17:55:45.1+00"),
            patch("time.sleep") as mock_sleep,
        ):
            self.client._check_rate_limit()

            mock_sleep.assert_called_once()
            sleep_time = mock_sleep.call_args[0][0]

            assert sleep_time >= 15.0

        with freeze_time("2026-06-28 17:56:01.000000+00"):
            with patch("time.sleep") as mock_sleep_after_reset:
                self.client._check_rate_limit()
                mock_sleep_after_reset.assert_not_called()


def test_tomllib_conditional_import():
    if int(platform.python_version_tuple()[1]) >= 11:
        assert _has_toml == True
    else:
        assert _has_toml == False


def test__get_openaq_config_file_exists():
    mock_toml_content = b"""
        api-key = 'e7a3a978e3e018e932d666c481ff33b82b7150c6084c0de175755c5cb763a5c5'
    """
    expected_config = {
        "api_key": "e7a3a978e3e018e932d666c481ff33b82b7150c6084c0de175755c5cb763a5c5"
    }

    with patch.object(Path, "is_file", return_value=True):
        with patch(
            "builtins.open", mock_open(read_data=mock_toml_content)
        ) as mock_file:
            result = None
            if int(platform.python_version_tuple()[1]) >= 11:
                result = _get_openaq_config()
                assert result == expected_config
                mock_file.assert_any_call(
                    Path(Path.home() / ".config" / "openaq" / "config.toml"), "rb"
                )
            else:
                assert result == None
