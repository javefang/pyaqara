"""
Aqara Gateway

Gateway abstraction

Features:
- Call discovery
- Persist list of sensors
- Control gateway lights

"""

import json
import binascii

from Crypto.Cipher import AES
from pydispatch import dispatcher
from aqara.device import (create_device, AqaraBaseDevice)
from aqara.const import (
    AQARA_ENCRYPT_IV,
    AQARA_DEVICE_GATEWAY,
    AQARA_MID_STOP,
    AQARA_EVENT_NEW_DEVICE
)

class AqaraGateway(AqaraBaseDevice):
    """Aqara Gateway implementation."""
    def __init__(self, client, sid, addr, secret):
        super().__init__(AQARA_DEVICE_GATEWAY, self, sid)
        self._client = client
        self._addr = addr
        self._cipher = AES.new(secret, AES.MODE_CBC, IV=AQARA_ENCRYPT_IV)
        self._token = None
        self._device_props = {
            "rgbw": 0,
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
    def rgbw(self):
        """property: rgbw"""
        return self._device_props["rgbw"]

    @property
    def illumination(self):
        """property: illumination"""
        return self._device_props["illumination"]

    @property
    def proto_version(self):
        """property: proto_version"""
        return self._device_props["proto_version"]

    def connect(self):
        """Start the gateway"""
        self.discover_devices()
        self.read_device(self._sid)

    def discover_devices(self):
        """discover devices attached to this gateway"""
        self.log_info('discovering devices...')
        self._client.discover_devices(self._addr)

    def read_device(self, sid):
        """force read the value of a device attached to this gateway"""
        self._client.read_device(self._addr, sid)

    def write_device(self, device, data, meta):
        """write data to device"""
        data["key"] = self._make_key()
        self._client.write_device(self._addr, device.model, device.sid, data, meta)

    def set_light(self, rgbw):
        """Set gateway light (rgbw)"""
        self._device_props["rgbw"] = rgbw
        data = {
            "rgb": rgbw,
        }
        meta = {
            "short_id": 0,
            "key": 8
        }
        self.write_device(self, data, meta)

    def play_ringtone(self, mid):
        """Play ringtone id 'mid'"""
        self._set_mid(mid)

    def stop_ringtone(self):
        """Stop playing ringtone"""
        self._set_mid(AQARA_MID_STOP)

    def on_devices_discovered(self, sids):
        """Callback when devices are discovered"""
        for sid in sids:
            self._client.read_device(self._addr, sid)

    def on_read_ack(self, model, sid, data):
        """Callback on read_ack"""
        self.log_debug("on_read_ack: [{}] {}: {}".format(model, sid, json.dumps(data)))
        if model == "gateway" and sid == self.sid:
            # handle read_ack for gateway itself
            self.on_update(data)
        else:
            # handle read_ack for devices attached to this gateway
            if sid not in self._devices:
                new_device = create_device(self, model, sid)
                self.log_info("added new device {} [{}]".format(sid, model))
                self._devices[sid] = new_device
                dispatcher.send(signal=AQARA_EVENT_NEW_DEVICE, device=new_device, sender=self)
            self._try_update_device(model, sid, data)

    def on_write_ack(self, model, sid, data):
        """Callback on write_ack"""
        self.log_debug("on_write_ack: {} [{}]: {}".format(sid, model, json.dumps(data)))
        if model == "gateway" and sid == self.sid:
            # handle write_ack for gateway
            self.on_update(data)

    def on_device_report(self, model, sid, data):
        """Callback on report"""
        self.log_debug("on_report: {} [{}]: {}".format(sid, model, json.dumps(data)))
        self._try_update_device(model, sid, data)

    def on_device_heartbeat(self, model, sid, data, gw_token):
        """Callback on heartbeat"""
        self.log_debug("on_heartbeat: {} [{}]: {}".format(sid, model, json.dumps(data)))
        if sid == self._sid:
            # handle as gateway heartbeat
            self._token = gw_token
        else:
            # handle as device heartbeat
            self._try_update_device(model, sid, data)

    def do_update(self, data):
        if "rgb" in data:
            self._device_props["rgbw"] = data["rgb"]
        if "illumination" in data:
            self._device_props["illumination"] = data["illumination"]
        if "proto_version" in data:
            self._device_props["proto_version"] = data["proto_version"]

    def subscribe(self, handle_new_device):
        """Subscribe to new device event."""
        dispatcher.connect(handle_new_device, signal=AQARA_EVENT_NEW_DEVICE, sender=self)

    def unsubscribe(self, handle_new_device):
        """Unsubscribe from new device event."""
        dispatcher.disconnect(handle_new_device, signal=AQARA_EVENT_NEW_DEVICE, sender=self)

    def _try_update_device(self, model, sid, data):
        """Update device data"""
        if sid not in self._devices:
            self.log_warning('unregistered device: {} [{}]'.format(model, sid))
            return
        self._devices[sid].on_update(data)


    def _try_heartbeat_device(self, model, sid, data):
        """Send heartbeat to device"""
        if sid not in self._devices:
            self.log_warning('unregistered device: {} [{}]'.format(model, sid))
            return
        self._devices[sid].on_heartbeat(data)

    def _make_key(self):
        return binascii.hexlify(self._cipher.encrypt(self._token)).decode("utf-8")

    def _set_mid(self, mid):
        data = {
            "mid": mid,
        }
        meta = {
            "short_id": 0,
            "key": 8
        }
        self.write_device(self, data, meta)
