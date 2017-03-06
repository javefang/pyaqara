"""Aqara Client Test"""
from unittest.mock import MagicMock

from aqara.client import AqaraClient

# Send tests

def test_discover_gateways():
    """Test if the correct message is sent for discover_gateways."""
    mock_client = AqaraClient()
    mock_client.broadcast = MagicMock()

    mock_client.discover_gateways()

    test_data = {"cmd": "whois"}
    mock_client.broadcast.assert_called_with(test_data)

def test_discover_devices():
    """Test if the correct message is sent for discover_devices."""
    mock_client = AqaraClient()
    mock_client.unicast = MagicMock()
    gw_addr = "10.10.10.10"
    test_data = {"cmd": "get_id_list"}

    mock_client.discover_devices(gw_addr)

    mock_client.unicast.assert_called_with(gw_addr, test_data)

def test_read_device():
    """Test if the correct message is sent for read_device."""
    mock_client = AqaraClient()
    mock_client.unicast = MagicMock()
    gw_addr = "10.10.10.10"
    test_sid = "123456"

    mock_client.read_device(gw_addr, test_sid)

    expected_data = {"cmd": "read", "sid": test_sid}
    mock_client.unicast.assert_called_with(gw_addr, expected_data)
