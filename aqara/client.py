"""Aqara Client"""
import asyncio
import json
import logging

from .protocol import AqaraProtocol
from .const import (LISTEN_IP, LISTEN_PORT)

_LOGGER = logging.getLogger(__name__)

class AqaraClient(AqaraProtocol):
    """Aqara Client implementation."""

    @asyncio.coroutine
    def start(self, loop):
        """Start listening on gateway events"""
        listen = loop.create_datagram_endpoint(lambda: self, local_addr=(LISTEN_IP, LISTEN_PORT))
        transport, _protocol = yield from listen
        self.transport = transport
        _LOGGER.info("started")

    def stop(self):
        """Stop listening to gateway events"""
        if self.transport is None:
            _LOGGER.info("not started")
        else:
            self.transport.close()
            _LOGGER.info("stopped")

    def handle_message(self, msg, addr):
        """Override: handle_message implementation"""
        _LOGGER.debug(json.dumps(msg))

    def discover_gateways(self):
        """Ask all gateways to respond identity."""
        discovery_msg = {"cmd": "whois"}
        self.broadcast(discovery_msg)

    def discover_devices(self, gw_addr):
        """Ask a gateway to reply with the SID of all attached devices."""
        discover_devices_msg = {"cmd": "get_id_list"}
        self.unicast(gw_addr, discover_devices_msg)

    def read_device(self, gw_addr, sid):
        """Send a request to read device 'sid' on gateway 'gw_addr'"""
        read_msg = {"cmd": "read", "sid": sid}
        self.unicast(gw_addr, read_msg)

    def write_device(self, gw_addr, sid, data):
        """Send a request to write 'data' to device 'sid' on gateway 'gw_addr'"""
        raise NotImplementedError()

    def on_gateway_discovered(self, gw_sid, gw_addr):
        """Called when a gateway is discovered"""
        pass

    def on_devices_discovered(self, gw_sid, sids):
        """Called when list of devices of gateway is returned."""
        pass

    def on_device_read_ack(self, model, sid, data):
        """Called when a gateway send back ACK for a read request."""
        pass

    def on_device_write_ack(self, model, sid, data):
        """Called when a gateway send back ACK for a write request."""

    def on_device_report(self, model, sid, data):
        """Called when a device sent a status report."""
        pass

    def on_gateway_heartbeat(self, gw_sid, gw_addr, gw_token):
        """Called when a gateway heartbeat is received."""
        pass

    def on_device_heartbeat(self, sid, data):
        """Called when a device heartbeat is received."""
        pass
