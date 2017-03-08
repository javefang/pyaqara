"""Aqara Client Test"""
from unittest.mock import MagicMock

from aqara.client import AqaraClient

# Send tests

def test_discover_gateways():
    """Test if the correct message is sent for discover_gateways."""
    mock_client = AqaraClient()
    mock_client.broadcast = MagicMock()

    mock_client.discover_gateways()

    cmd_whois = {"cmd": "whois"}
    mock_client.broadcast.assert_called_with(cmd_whois)

def test_discover_devices():
    """Test if the correct message is sent for discover_devices."""
    mock_client = AqaraClient()
    mock_client.unicast = MagicMock()
    gw_addr = "10.10.10.10"
    cmd_get_id_list = {"cmd": "get_id_list"}

    mock_client.discover_devices(gw_addr)

    mock_client.unicast.assert_called_with(gw_addr, cmd_get_id_list)

def test_read_device():
    """Test if the correct message is sent for read_device."""
    mock_client = AqaraClient()
    mock_client.unicast = MagicMock()
    gw_addr = "10.10.10.10"
    test_sid = "123456"

    mock_client.read_device(gw_addr, test_sid)

    expected_data = {"cmd": "read", "sid": test_sid}
    mock_client.unicast.assert_called_with(gw_addr, expected_data)

def test_handle_message_iam():
    """Test if a gateway is created after message "iam" is received"""
    src_addr = "10.10.10.10"
    msg_iam = {
        "cmd": "iam",
        "ip": "10.10.10.10",
        "sid": "123456"
    }

    mock_client = AqaraClient()
    mock_client.unicast = MagicMock()
    mock_client.handle_message(msg_iam, src_addr)

    assert len(mock_client.gateways.keys()) == 1
