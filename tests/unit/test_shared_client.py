from pathlib import Path
import platform

from unittest.mock import mock_open, patch

import pytest

from openaq.shared.client import _get_openaq_config, _has_toml
from tests.unit.mocks import MockTransport


def test_tomllib_conditional_import():
    if int(platform.python_version_tuple()[1]) >= 11:
        assert _has_toml == True
    else:
        assert _has_toml == False


def test__get_openaq_config_file_exists():
    mock_toml_content = b"""
        api-key = 'openaq-1a2b3c4d5e6f7g8h9i0j1k2l3m4n5o6p'
    """
    expected_config = {"api-key": "openaq-1a2b3c4d5e6f7g8h9i0j1k2l3m4n5o6p"}

    with patch.object(Path, 'is_file', return_value=True):
        with patch(
            'builtins.open', mock_open(read_data=mock_toml_content)
        ) as mock_file:
            result = None
            if int(platform.python_version_tuple()[1]) >= 11:
                result = _get_openaq_config()
                assert result == expected_config
                mock_file.assert_called_once_with(
                    Path(Path.home() / ".openaq.toml"), 'rb'
                )
            else:
                assert result == None
