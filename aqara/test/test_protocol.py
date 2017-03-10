"""Aqara Client Test"""
import json

from asyncio import DatagramTransport
from unittest.mock import MagicMock
from aqara import protocol
from aqara.const import (MCAST_ADDR, MCAST_PORT, GATEWAY_PORT)

def test_handle_message():
    """test_handle_message"""
    mock_protocol = protocol.AqaraProtocol()
    mock_protocol.handle_message = MagicMock()
    test_data = json.dumps({"model": "test"}).encode('utf-8')
    test_addr = "10.10.10.10"

    # run test
    mock_protocol.datagram_received(test_data, test_addr)

    # assert
    test_data_decoded = json.loads(test_data.decode('utf-8'))
    mock_protocol.handle_message.assert_called_with(test_data_decoded, test_addr)

def test_unicast():
    """test_unicast"""
    mock_transport = DatagramTransport()
    mock_transport.sendto = MagicMock()
    mock_protocol = protocol.AqaraProtocol()
    mock_protocol.transport = mock_transport
    test_data = {"cmd": "read"}
    test_addr = "10.10.10.10"

    mock_protocol.unicast(test_addr, test_data)

    test_data_encoded = json.dumps(test_data).encode('utf-8')
    mock_transport.sendto.assert_called_with(test_data_encoded, (test_addr, GATEWAY_PORT))

def test_broadcast():
    """test_broadcast"""
    mock_transport = DatagramTransport()
    mock_transport.sendto = MagicMock()
    mock_protocol = protocol.AqaraProtocol()
    mock_protocol.transport = mock_transport
    test_data = {"cmd": "read"}

    mock_protocol.broadcast(test_data)

    test_data_encoded = json.dumps(test_data).encode('utf-8')
    mock_transport.sendto.assert_called_with(test_data_encoded, (MCAST_ADDR, MCAST_PORT))
