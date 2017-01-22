"""Aqara Client Test"""
from .. import client
from unittest.mock import MagicMock

MCAST_ADDR = "224.0.0.50"
MCAST_PORT = 4321
SERVER_PORT = 9898

def test_handle_message():
    # setup
    mock_client = client.AqaraMessagingProtocol()
    mock_client.handle_message = MagicMock()
    test_data = { "model": "test" }
    test_addr = "127.0.0.1"

    # run test
    mock_client.datagram_received(test_data, test_addr)

    # assert
    mock_client.handle_message.assert_called_with(test_data, test_addr)

def test_unicast():
    mock_client = client.AqaraMessagingProtocol()
    mock_client._send = MagicMock()
    test_data = { "cmd": "read" }
    test_addr = "10.8.8.8"

    mock_client.unicast(test_addr, test_data)

    mock_client._send.assert_called_with(test_addr, SERVER_PORT, test_data)

def test_broadcast():
    mock_client = client.AqaraMessagingProtocol()
    mock_client._send = MagicMock()
    test_data = { "cmd": "read" }

    mock_client.broadcast(test_data)

    mock_client._send.assert_called_with(MCAST_ADDR, MCAST_PORT, test_data)
