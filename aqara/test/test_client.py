"""Aqara Client Test"""
from unittest.mock import MagicMock

from ..client import AqaraClient

# Send tests

def test_discover_gateways():
    """Test if the correct message is sent for discover_gateways."""
    mock_client = AqaraClient()
    mock_client.broadcast = MagicMock()

    mock_client.discover_gateways()

    test_data = {"cmd": "whois"}
    mock_client.broadcast.assert_called_with(test_data)
