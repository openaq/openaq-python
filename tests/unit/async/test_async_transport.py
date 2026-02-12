from unittest.mock import AsyncMock, MagicMock, patch

import httpx
import pytest

from openaq._async.transport import AsyncTransport


def request_matches(expected_request):
    def matcher(request):
        return (
            request.method == expected_request.method
            and request.url == expected_request.url
            and request.headers == expected_request.headers
        )

    return matcher


@pytest.mark.asyncio
@patch('httpx.AsyncClient')
async def test_send_request(mock_httpx_async_client):
    mock_client_instance = mock_httpx_async_client.return_value

    mock_response = MagicMock(spec=httpx.Response)
    mock_response.status_code = 200

    # Use AsyncMock for async method
    mock_client_instance.send = AsyncMock(return_value=mock_response)

    with patch('openaq._async.transport.check_response') as mock_check_response:
        mock_check_response.return_value = 'processed_response'

        transport = AsyncTransport()

        result = await transport.send_request(
            method='GET',
            url='https://api.openaq.org/v3/locations',
            params={'limit': '100'},
            headers={'x-api-key': 'foobar'},
        )

        mock_httpx_async_client.assert_called_once()
        expected_request = httpx.Request(
            method='GET',
            url='https://api.openaq.org/v3/locations',
            params={'limit': '100'},
            headers={'x-api-key': 'foobar'},
        )
        mock_client_instance.send.assert_called_once()
        actual_request = mock_client_instance.send.call_args[0][0]
        assert request_matches(expected_request)(actual_request)
        mock_check_response.assert_called_once_with(mock_response)
        assert result == 'processed_response'


@pytest.mark.asyncio
@patch('httpx.AsyncClient')
async def test_close(mock_httpx_async_client):
    mock_client_instance = mock_httpx_async_client.return_value
    # Use AsyncMock for async method
    mock_client_instance.aclose = AsyncMock()

    transport = AsyncTransport()
    await transport.close()

    mock_client_instance.aclose.assert_called_once()
