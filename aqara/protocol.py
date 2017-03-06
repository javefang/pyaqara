"""
Aqara Protocol

Provide protocol level support for Aqara, feature including
- Join multicast group
- Receive / Send messages
- Encoding / Decoding messages
- Utility to unicast / broadcast messages
"""

import json
import logging
import socket
import struct

from aqara.const import (MCAST_ADDR, MCAST_PORT, GATEWAY_PORT)

_LOGGER = logging.getLogger(__name__)

class AqaraProtocol(object):
    """Base aqara client protocol."""

    def __init__(self):
        self.transport = None

    def connection_made(self, transport):
        """Implementation when connection is made."""
        self.transport = transport
        self._add_membership()

    def datagram_received(self, data, addr):
        """Implementation when datagram is received."""
        data_str = data.decode('utf-8')
        msg = json.loads(data_str)
        _LOGGER.debug('recv: %s', data_str)
        self.handle_message(msg, addr)

    def error_received(self, exc):
        """Implentation when error is received."""
        _LOGGER.error('error_received: %s', exc)

    def handle_message(self, data, addr):
        """Callback to handle new messages, override to add implementation."""
        _LOGGER.debug('handle_message from %s: %s', addr, json.dumps(data))

    def broadcast(self, msg):
        """Send a message to the Aqara multicast channel."""
        self._send(msg, (MCAST_ADDR, MCAST_PORT))

    def unicast(self, addr, msg):
        """Send a message to a specific gateway at <ip>"""
        self._send(msg, (addr, GATEWAY_PORT))

    def _send(self, msg, dest):
        """private: send a message as UDP packet."""
        _LOGGER.debug('send: %s', json.dumps(msg))
        data = json.dumps(msg).encode('utf-8')
        self.transport.sendto(data, dest)

    def _add_membership(self):
        """private: add multicast membership"""
        _LOGGER.debug("Joining multicast group...")
        sock = self.transport.get_extra_info("socket")
        group = socket.inet_aton(MCAST_ADDR)
        mreq = struct.pack("4sL", group, socket.INADDR_ANY)
        sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)
        _LOGGER.debug("Multicast membership added")
