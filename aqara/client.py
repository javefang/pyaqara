"""Aqara Client"""

import json
import logging
import socket
import struct

_LOGGER = logging.getLogger(__name__)
MCAST_GROUP = "224.0.0.50"
MCAST_PORT = 4321
SERVER_IP = "0.0.0.0"
SERVER_PORT = 9898

class AqaraMessagingProtocol(object):
    """Base aqara client protocol."""

    def __init__(self):
        self.transport = None

    def connection_made(self, transport):
        """Implementation when connection is made."""
        self.transport = transport
        self._add_membership()

    def datagram_received(self, data, addr):
        """Implementation when datagram is received."""
        self.handle_message(data, addr)

    def error_received(self, exc):
        """Implentation when error is received."""
        _LOGGER.error('error_received: %s', exc)

    def handle_message(self, data, addr):
        """Callback to handle new messages, override to add implementation."""
        _LOGGER.debug('handle_message from %s: %s', addr, json.dumps(data))

    def broadcast(self, msg):
        """Send a message to the Aqara multicast channel."""
        self._send(MCAST_GROUP, MCAST_PORT, msg)

    def unicast(self, addr, msg):
        """Send a message to a specific gateway at <ip>"""
        self._send(addr, SERVER_PORT, msg)

    def _send(self, addr, port, msg):
        """private: send a message as UDP packet."""
        data = json.dumps(msg).encode('utf-8')
        self.transport.sendto(data, (addr, port))

    def _add_membership(self):
        """private: add multicast membership"""
        _LOGGER.debug("Joining multicast group...")
        sock = self.transport.get_extra_info("socket")
        group = socket.inet_aton(MCAST_GROUP)
        mreq = struct.pack("4sL", group, socket.INADDR_ANY)
        sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)
        _LOGGER.debug("Multicast membership added")
