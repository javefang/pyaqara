"""
Aqara Gateway

Gateway abstraction

Features:
- Call discovery
- Persist list of sensors
- Control gateway lights

"""

import logging
import json

_LOGGER = logging.getLogger(__name__)

class AqaraGateway(object):
    """Aqara Gateway implementation."""
    def __init__(self, client, sid, addr):
        self._client = client
        self._sid = sid
        self._addr = addr
        self._token = None

    def connect(self):
        """Start the gateway"""
        self._client.discover_devices(self._addr)

    def on_devices_discovered(self, sids):
        """Callback when devices are discovered"""
        for sid in sids:
            self._client.read_device(self._addr, sid)

    def on_read_ack(self, model, sid, data):
        """Callback on read_ack"""
        _LOGGER.debug("on_read_ack: [%s] %s: %s", model, sid, json.dumps(data))

    def on_write_ack(self, model, sid, data):
        """Callback on write_ack"""
        _LOGGER.debug("on_write_ack: [%s] %s: %s", model, sid, json.dumps(data))

    def on_report(self, model, sid, data):
        """Callback on report"""
        _LOGGER.debug("on_report: [%s] %s: %s", model, sid, json.dumps(data))

    def on_heartbeat(self, sid, data, gw_token):
        """Callback on heartbeat"""
        _LOGGER.debug("on_heartbeat: %s: (token=%s) %s", sid, gw_token, json.dumps(data))
        self._token = gw_token
