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

def __parse_value(str_value):
    return round(int(str_value) / 100, 1)

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
    def __init__(self, name, sid):
        self._name = name
        self._sid = sid
        self._update_callback = None

    @property
    def sid(self):
        """property: sid"""
        return self._sid

    def set_update_callback(self, update_callback):
        """set update_callback"""
        self._update_callback = update_callback

    def on_update(self, data):
        """update sensor data"""
        self.do_update(data)
        if self._update_callback != None:
            self._update_callback()

    def do_update(self, data):
        """update sensor state according to data"""
        pass

    def log_warning(self, msg):
        """log warning"""
        self._log(_LOGGER.warning, msg)

    def _log(self, log_func, msg):
        """log"""
        log_func('[%s] %s: %s', self._name, self._sid, msg)

class AqaraHTSensor(AqaraBaseDevice):
    """AqaraHTSensor"""
    def __init__(self, sid):
        super().__init__('HT', sid)
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
            self._temp = __parse_value(data["temperature"])
        if "humidity" in data:
            self._humid = __parse_value(data["humidity"])

class AqaraContactSensor(AqaraBaseDevice):
    """AqaraContactSensor"""
    def __init__(self, sid):
        super().__init__('Contact', sid)
        self._triggered = False

    @property
    def triggered(self):
        """property: triggered (bool)"""
        return self._triggered

    def do_update(self, data):
        if "status" in data:
            self._triggered = data["status"] == "open"

class AqaraMotionSensor(AqaraBaseDevice):
    """AqaraMotionSensor"""
    def __init__(self, sid):
        super().__init__('Motion', sid)
        self._triggered = False

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

class AqaraSwitchSensor(AqaraBaseDevice):
    """AqaraMotionSensor"""
    def __init__(self, sid):
        super().__init__('Switch', sid)
        self._last_action = None

    @property
    def last_action(self):
        """property: last_action"""
        return self._last_action

    def do_update(self, data):
        """update sensor state according to data"""
        if "status" not in data:
            self.log_warning('missing status in event data')
            self._last_action = None
            return

        status = data["status"]

        if status == 'click':
            self._last_action = AQARA_SWITCH_ACTION_CLICK
        elif status == 'double_click':
            self._last_action = AQARA_SWITCH_ACTION_DOUBLE_CLICK
        elif status == 'long_click_press':
            self._last_action = AQARA_SWITCH_ACTION_LONG_CLICK_PRESS
        else:
            self.log_warning('invalid status: ' + status)
