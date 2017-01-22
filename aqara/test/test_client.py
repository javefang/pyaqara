"""Aqara Client Test"""
import json
from asyncio import DatagramTransport
from unittest.mock import MagicMock

from .. import client
from ..const import (MCAST_ADDR, MCAST_PORT, GATEWAY_PORT)

def test_handle_message():
    """test_handle_message"""
    mock_client = client.AqaraMessagingProtocol()
    mock_client.handle_message = MagicMock()
    test_data = {"model": "test"}
    test_addr = "10.10.10.10"

    # run test
    mock_client.datagram_received(test_data, test_addr)

    # assert
    mock_client.handle_message.assert_called_with(test_data, test_addr)

def test_unicast():
    """test_unicast"""
    mock_transport = DatagramTransport()
    mock_transport.sendto = MagicMock()
    mock_client = client.AqaraMessagingProtocol()
    mock_client.transport = mock_transport
    test_data = {"cmd": "read"}
    test_addr = "10.10.10.10"

    mock_client.unicast(test_addr, test_data)

    test_data_encoded = json.dumps(test_data).encode('utf-8')
    mock_transport.sendto.assert_called_with(test_data_encoded, (test_addr, GATEWAY_PORT))

def test_broadcast():
    """test_broadcast"""
    mock_transport = DatagramTransport()
    mock_transport.sendto = MagicMock()
    mock_client = client.AqaraMessagingProtocol()
    mock_client.transport = mock_transport
    test_data = {"cmd": "read"}

    mock_client.broadcast(test_data)

    test_data_encoded = json.dumps(test_data).encode('utf-8')
    mock_transport.sendto.assert_called_with(test_data_encoded, (MCAST_ADDR, MCAST_PORT))
