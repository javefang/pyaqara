"""Aqara Devices"""

import logging

from aqara.const import (
    AQARA_DEVICE_HT,
    AQARA_DEVICE_MOTION,
    AQARA_DEVICE_MAGNET,
    AQARA_DEVICE_SWITCH,
    AQARA_SWITCH_ACTION_CLICK,
    AQARA_SWITCH_ACTION_DOUBLE_CLICK,
    AQARA_SWITCH_ACTION_LONG_CLICK_PRESS
)

_LOGGER = logging.getLogger(__name__)

def create_device(model, sid):
    """Device factory"""
    if model == AQARA_DEVICE_HT:
        return AqaraHTSensor(sid)
    elif model == AQARA_DEVICE_MOTION:
        return AqaraMotionSensor(sid)
    elif model == AQARA_DEVICE_MAGNET:
        return AqaraContactSensor(sid)
    elif model == AQARA_DEVICE_SWITCH:
        return AqaraSwitchSensor(sid)
    else:
        raise RuntimeError('Unsupported device type: {} [{}]'.format(model, sid))

class AqaraBaseDevice(object):
    """AqaraBaseDevice"""
    def __init__(self, model, sid):
        self._model = model
        self._sid = sid
        self._update_callback = None

    @property
    def sid(self):
        """property: sid"""
        return self._sid

    @property
    def model(self):
        """property: model"""
        return self._model

    def set_update_callback(self, update_callback):
        """set update_callback"""
        self._update_callback = update_callback

    def on_update(self, data):
        """handler for sensor data update"""
        self.do_update(data)
        if self._update_callback != None:
            self._update_callback()

    def on_heartbeat(self, data):
        """handler for heartbeat"""
        self.do_heartbeat(data)
        if self._update_callback != None:
            self._update_callback()

    def do_update(self, data):
        """update sensor state according to data"""
        pass

    def do_heartbeat(self, data):
        """update heartbeat"""
        pass

    def log_warning(self, msg):
        """log warning"""
        self._log(_LOGGER.warning, msg)

    def _log(self, log_func, msg):
        """log"""
        log_func('[%s] %s: %s', self._model, self._sid, msg)

class AqaraHTSensor(AqaraBaseDevice):
    """AqaraHTSensor"""
    def __init__(self, sid):
        super().__init__(AQARA_DEVICE_HT, sid)
        self._temp = 0
        self._humid = 0

    @property
    def temperature(self):
        """property: temperature (unit: C)"""
        return self._temp

    @property
    def humidity(self):
        """property: humidity (unit: %)"""
        return self._humid

    def do_update(self, data):
        """update sensor state according to data"""
        if "temperature" in data:
            self._temp = self.parse_value(data["temperature"])
        if "humidity" in data:
            self._humid = self.parse_value(data["humidity"])

    @staticmethod
    def parse_value(str_value):
        """parse sensor_ht values"""
        return round(int(str_value) / 100, 1)


class AqaraContactSensor(AqaraBaseDevice):
    """AqaraContactSensor"""
    def __init__(self, sid):
        super().__init__(AQARA_DEVICE_MAGNET, sid)
        self._triggered = False
        self._voltage = 0

    @property
    def triggered(self):
        """property: triggered (bool)"""
        return self._triggered

    def do_update(self, data):
        """update sensor state according to data"""
        if "status" in data:
            self._triggered = data["status"] == "open"

    def do_heartbeat(self, data):
        """update heartbeat"""
        if "voltage" in data:
            self._voltage = int(data["voltage"])

class AqaraMotionSensor(AqaraBaseDevice):
    """AqaraMotionSensor"""
    def __init__(self, sid):
        super().__init__(AQARA_DEVICE_MOTION, sid)
        self._triggered = False
        self._voltage = 0

    @property
    def triggered(self):
        """property: triggered (bool)"""
        return self._triggered

    def do_update(self, data):
        """update sensor state according to data"""
        if "status" in data:
            self._triggered = data["status"] == "motion"
        else:
            self._triggered = False

    def do_heartbeat(self, data):
        """update heartbeat"""
        if "voltage" in data:
            self._voltage = int(data["voltage"])

class AqaraSwitchSensor(AqaraBaseDevice):
    """AqaraMotionSensor"""
    def __init__(self, sid):
        super().__init__(AQARA_DEVICE_SWITCH, sid)
        self._last_action = None
        self._voltage = 0

    @property
    def last_action(self):
        """property: last_action"""
        return self._last_action

    def do_update(self, data):
        """update sensor state according to data"""
        if "status" in data:
            status = data["status"]
            if status == 'click':
                self._last_action = AQARA_SWITCH_ACTION_CLICK
            elif status == 'double_click':
                self._last_action = AQARA_SWITCH_ACTION_DOUBLE_CLICK
            elif status == 'long_click_press':
                self._last_action = AQARA_SWITCH_ACTION_LONG_CLICK_PRESS
            else:
                self.log_warning('invalid status: ' + status)

    def do_heartbeat(self, data):
        """update heartbeat"""
        if "voltage" in data:
            self._voltage = int(data["voltage"])
