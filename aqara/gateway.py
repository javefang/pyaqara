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

from aqara.device import (create_device)

_LOGGER = logging.getLogger(__name__)

class AqaraGateway(object):
    """Aqara Gateway implementation."""
    def __init__(self, client, sid, addr):
        self._client = client
        self._sid = sid
        self._addr = addr
        self._token = None
        self._devices = {}

    @property
    def devices(self):
        """property: devices"""
        return self._devices

    @property
    def addr(self):
        """property: addr"""
        return self._addr

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
        if sid not in self._devices:
            self._devices[sid] = create_device(model, sid)
        self._update_device(model, sid, data)

    def on_write_ack(self, model, sid, data):
        """Callback on write_ack"""
        _LOGGER.debug("on_write_ack: [%s] %s: %s", model, sid, json.dumps(data))

    def on_report(self, model, sid, data):
        """Callback on report"""
        _LOGGER.debug("on_report: [%s] %s: %s", model, sid, json.dumps(data))
        self._update_device(model, sid, data)

    def on_heartbeat(self, data, gw_token):
        """Callback on heartbeat"""
        _LOGGER.debug("on_heartbeat: %s: (token=%s) %s", self._sid, gw_token, json.dumps(data))
        self._token = gw_token

    def on_device_heartbeat(self, sid, data):
        """Callback on device heartbeat"""
        _LOGGER.debug("on_device_heartbeat [%s]: %s", sid, json.dumps(data))

    def _update_device(self, model, sid, data):
        """Update device data"""
        if sid not in self._devices:
            _LOGGER.warning('unregistered device: %s [%s]', model, sid)
        self._devices[sid].on_update(data)
