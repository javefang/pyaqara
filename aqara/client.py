"""
Aqara Client

A client implementation to receive Aqara events and send control messages.

Feature includes:
- Discover gateways
- Discover devices of a gateway
- Subscribe to updates for devices
- Read values from a device (async)
- Send control command to a device (async)
- Heartbeat

"""
import asyncio
import json
import logging

from aqara.protocol import AqaraProtocol
from aqara.gateway import AqaraGateway
from aqara.const import (LISTEN_IP, LISTEN_PORT)

_LOGGER = logging.getLogger(__name__)

def _extract_data(msg):
    return json.loads(msg["data"])

class AqaraClient(AqaraProtocol):
    """Aqara Client implementation."""
    def __init__(self, gw_secrets=None):
        super().__init__()
        self.transport = None
        self._gw_secrets = {} if gw_secrets is None else gw_secrets
        self._gateways = {}
        self._device_to_gw = {}

    @property
    def gateways(self):
        """property: gateways"""
        return self._gateways

    @asyncio.coroutine
    def start(self, loop):
        """Start listening on gateway events"""
        listen = loop.create_datagram_endpoint(lambda: self, local_addr=(LISTEN_IP, LISTEN_PORT))
        transport, _protocol = yield from listen
        self.transport = transport
        self.discover_gateways()
        _LOGGER.info("started")

    def stop(self):
        """Stop listening to gateway events"""
        if self.transport is None:
            _LOGGER.info("not started")
        else:
            self.transport.close()
            _LOGGER.info("stopped")

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

    def write_device(self, gw_addr, model, sid, data, meta=None):
        """Send a request to write 'data' to device 'sid' on gateway 'gw_addr'"""
        write_msg = {
            "cmd": "write",
            "model": model,
            "sid": sid,
            "data": json.dumps(data)
        }

        if meta != None:
            write_msg.update(meta)

        self.unicast(gw_addr, write_msg)

    def handle_message(self, msg, src_addr):
        """Override: handle_message implementation"""
        _LOGGER.debug("handle_message from %s", src_addr)

        cmd = msg["cmd"]
        sid = msg["sid"]

        if cmd == "iam":
            addr = msg["ip"]
            self.on_gateway_discovered(sid, addr)
        elif cmd == "get_id_list_ack":
            sids = _extract_data(msg)
            self.on_devices_discovered(sid, sids)
        elif cmd == "read_ack":
            model = msg["model"]
            data = _extract_data(msg)
            self.on_read_ack(model, sid, data)
        elif cmd == "write_ack":
            model = msg["model"]
            data = _extract_data(msg)
            self.on_write_ack(model, sid, data)
        elif cmd == "report":
            model = msg["model"]
            data = _extract_data(msg)
            self.on_report(model, sid, data)
        elif cmd == "heartbeat":
            model = msg["model"]
            data = _extract_data(msg)
            gw_token = None if "token" not in msg else msg["token"]
            self.on_heartbeat(model, sid, data, gw_token)

    def on_gateway_discovered(self, gw_sid, gw_addr):
        """Called when a gateway is discovered"""
        gw_secret = None
        if gw_sid in self._gw_secrets:
            gw_secret = self._gw_secrets[gw_sid]
        gateway = AqaraGateway(self, gw_sid, gw_addr, gw_secret)
        self._gateways[gw_sid] = gateway
        self._device_to_gw[gw_sid] = gateway
        gateway.connect()

    def on_devices_discovered(self, gw_sid, sids):
        """Called when list of devices of gateway is returned."""
        if gw_sid not in self._gateways:
            _LOGGER.error("on_devices_discovered(): sid not found %s", gw_sid)
            return
        gateway = self._gateways[gw_sid]
        for sid in sids:
            self._device_to_gw[sid] = gateway
        gateway.on_devices_discovered(sids)

    def on_read_ack(self, model, sid, data):
        """Called when a gateway send back ACK for a read request."""
        if sid not in self._gateways:
            _LOGGER.error("on_read_ack(): sid not found %s", sid)
            return
        self._gateways[sid].on_read_ack(model, sid, data)

    def on_write_ack(self, model, sid, data):
        """Called when a gateway send back ACK for a write request."""
        if sid not in self._gateways:
            _LOGGER.error("on_write_ack(): sid not found %s", sid)
            return
        self._gateways[sid].on_write_ack(model, sid, data)

    def on_report(self, model, sid, data):
        """Called when a device sent a status report."""
        if sid not in self._device_to_gw:
            _LOGGER.warning("on_report(): sid not found %s", sid)
            return
        self._device_to_gw[sid].on_report(model, sid, data)

    def on_heartbeat(self, model, sid, data, gw_token):
        """Called when a heartbeat is received."""
        if sid not in self._device_to_gw:
            _LOGGER.warning("on_heartbeat(): sid not found %s", sid)
            return
        self._device_to_gw[sid].on_heartbeat(model, sid, data, gw_token)
