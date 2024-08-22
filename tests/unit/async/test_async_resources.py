from openaq._async.models.base import AsyncResourceBase

from unittest.mock import MagicMock


def test_sync_resource_base_init():
    mock_client = MagicMock()
    resource = AsyncResourceBase(client=mock_client)
    assert resource._client == mock_client
