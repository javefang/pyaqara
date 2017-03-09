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

from aqara.device import (create_device)
from aqara.const import (AQARA_ENCRYPT_IV)

_LOGGER = logging.getLogger(__name__)

def encrypt(token, secret):
    """Encrypt gateway token with secret"""
    cipher = AES.new(secret, AES.MODE_CBC, IV=AQARA_ENCRYPT_IV)
    return binascii.hexlify(cipher.encrypt(token)).decode("utf-8")

def encode_light_rgb(brightness, red, green, blue):
    """Encode rgb value used to control the gateway light"""
    return brightness << 24 + red << 16 + green << 8 + blue

class AqaraGateway(object):
    """Aqara Gateway implementation."""
    def __init__(self, client, sid, addr, secret=None):
        self._model = "gateway"
        self._client = client
        self._sid = sid
        self._addr = addr
        self._secret = secret
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

    def set_light(self, brightness, red, green, blue):
        """Set gateway light (color and brightness)"""
        rgb = encode_light_rgb(brightness, red, green, blue)
        data = {
            "rgb": rgb,
            "key": encrypt(self._token, self._secret)
        }
        meta = {
            "short_id": 0,
            "key": 8
        }
        self._client.write_device(self._addr, self._model, self._sid, data, meta)

    def on_devices_discovered(self, sids):
        """Callback when devices are discovered"""
        for sid in sids:
            self._client.read_device(self._addr, sid)

    def on_read_ack(self, model, sid, data):
        """Callback on read_ack"""
        _LOGGER.debug("on_read_ack: [%s] %s: %s", model, sid, json.dumps(data))
        if sid not in self._devices:
            self._devices[sid] = create_device(model, sid)
        self._try_update_device(model, sid, data)

    def on_write_ack(self, model, sid, data):
        """Callback on write_ack"""
        _LOGGER.debug("on_write_ack: [%s] %s: %s", model, sid, json.dumps(data))

    def on_report(self, model, sid, data):
        """Callback on report"""
        _LOGGER.debug("on_report: [%s] %s: %s", model, sid, json.dumps(data))
        if sid == self._sid:
            # handle as gateway report
            pass
        else:
            # handle as device report
            self._try_update_device(model, sid, data)

    def on_heartbeat(self, model, sid, data, gw_token):
        """Callback on heartbeat"""
        _LOGGER.debug("on_heartbeat: [%s] %s: (token=%s) %s",
                      model, sid, gw_token, json.dumps(data))
        if sid == self._sid:
            # handle as gateway heartbeat
            self._token = gw_token
        else:
            # handle as device heartbeat
            pass

    def _try_update_device(self, model, sid, data):
        """Update device data"""
        if sid not in self._devices:
            _LOGGER.warning('unregistered device: %s [%s]', model, sid)
        self._devices[sid].on_update(data)
