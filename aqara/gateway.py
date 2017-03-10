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
import binascii

from Crypto.Cipher import AES
from aqara.device import (create_device, AqaraBaseDevice)
from aqara.const import (AQARA_ENCRYPT_IV, AQARA_DEVICE_GATEWAY)

_LOGGER = logging.getLogger(__name__)

def encode_light_rgb(brightness, red, green, blue):
    """Encode rgb value used to control the gateway light"""
    return (brightness << 24) + (red << 16) + (green << 8) + blue

class AqaraGateway(AqaraBaseDevice):
    """Aqara Gateway implementation."""
    def __init__(self, client, sid, addr, secret):
        super().__init__(AQARA_DEVICE_GATEWAY, self, sid)
        self._client = client
        self._addr = addr
        self._cipher = AES.new(secret, AES.MODE_CBC, IV=AQARA_ENCRYPT_IV)
        self._token = None
        self._properties = {
            "rgb": 0,
            "illumination": 0,
            "proto_version": None,
            "voltage": 0
        }
        self._devices = {}
        self._devices[sid] = self

    @property
    def devices(self):
        """property: devices"""
        return self._devices

    @property
    def addr(self):
        """property: addr"""
        return self._addr

    @property
    def rgb(self):
        """property: rgb"""
        return self._properties["rgb"]

    @property
    def illumination(self):
        """property: illumination"""
        return self._properties["illumination"]

    @property
    def proto_version(self):
        """property: proto_version"""
        return self._properties["proto_version"]

    def connect(self):
        """Start the gateway"""
        self.discover_devices()
        self.read_device(self._sid)

    def discover_devices(self):
        """discover devices attached to this gateway"""
        self._client.discover_devices(self._addr)

    def read_device(self, sid):
        """force read the value of a device attached to this gateway"""
        self._client.read_device(self._addr, sid)

    def write_device(self, device, data, meta):
        """write data to device"""
        data["key"] = self._make_key()
        self._client.write_device(self._addr, device.model, device.sid, data, meta)

    def set_light(self, brightness, red, green, blue):
        """Set gateway light (color and brightness)"""
        rgb = encode_light_rgb(brightness, red, green, blue)
        self._properties["rgb"] = rgb
        data = {
            "rgb": rgb,
        }
        meta = {
            "short_id": 0,
            "key": 8
        }
        self.write_device(self, data, meta)

    def on_devices_discovered(self, sids):
        """Callback when devices are discovered"""
        for sid in sids:
            self._client.read_device(self._addr, sid)

    def on_read_ack(self, model, sid, data):
        """Callback on read_ack"""
        _LOGGER.debug("on_read_ack: [%s] %s: %s", model, sid, json.dumps(data))
        if sid not in self._devices:
            self._devices[sid] = create_device(self, model, sid)
        self._try_update_device(model, sid, data)

    def on_write_ack(self, model, sid, data):
        """Callback on write_ack"""
        _LOGGER.debug("on_write_ack: [%s] %s: %s", model, sid, json.dumps(data))

    def on_device_report(self, model, sid, data):
        """Callback on report"""
        _LOGGER.debug("on_report: [%s] %s: %s", model, sid, json.dumps(data))
        self._try_update_device(model, sid, data)

    def on_device_heartbeat(self, model, sid, data, gw_token):
        """Callback on heartbeat"""
        _LOGGER.debug("on_heartbeat: [%s] %s: (token=%s) %s",
                      model, sid, gw_token, json.dumps(data))
        if sid == self._sid:
            # handle as gateway heartbeat
            self._token = gw_token
        else:
            # handle as device heartbeat
            self._try_update_device(model, sid, data)

    def on_update(self, data):
        if "rgb" in data:
            self._properties["rgb"] = data["rgb"]
        if "illumination" in data:
            self._properties["illumination"] = data["illumination"]
        if "proto_version" in data:
            self._properties["proto_version"] = data["proto_version"]

    def _try_update_device(self, model, sid, data):
        """Update device data"""
        if sid not in self._devices:
            _LOGGER.warning('unregistered device: %s [%s]', model, sid)
            return
        self._devices[sid].on_update(data)


    def _try_heartbeat_device(self, model, sid, data):
        """Send heartbeat to device"""
        if sid not in self._devices:
            _LOGGER.warning('unregistered device: %s [%s]', model, sid)
            return
        self._devices[sid].on_heartbeat(data)

    def _make_key(self):
        return binascii.hexlify(self._cipher.encrypt(self._token)).decode("utf-8")
