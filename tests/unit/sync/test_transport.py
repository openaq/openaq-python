from unittest.mock import patch, MagicMock
import httpx
from openaq._sync.transport import Transport


def request_matches(expected_request):
    def matcher(request):
        return (
            request.method == expected_request.method
            and request.url == expected_request.url
            and request.headers == expected_request.headers
        )

    return matcher


@patch('httpx.Client')
def test_send_request(mock_httpx_client):
    mock_client_instance = mock_httpx_client.return_value

    mock_response = MagicMock(spec=httpx.Response)
    mock_response.status_code = 200

    mock_client_instance.send.return_value = mock_response

    with patch('openaq._sync.transport.check_response') as mock_check_response:
        mock_check_response.return_value = 'processed_response'

        transport = Transport()

        result = transport.send_request(
            method='GET',
            url='https://api.openaq.org/v3/locations',
            params={'limit': '100'},
            headers={'x-api-key': 'foobar'},
        )

        mock_httpx_client.assert_called_once()
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


@patch('httpx.Client')
def test_close(mock_httpx_client):
    mock_client_instance = mock_httpx_client.return_value
    transport = Transport()
    transport.close()
    mock_client_instance.close.assert_called_once()
