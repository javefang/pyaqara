"""Aqara Devices"""

import json
import logging

from pydispatch import dispatcher
from aqara.const import (
    AQARA_DEVICE_HT,
    AQARA_DEVICE_MOTION,
    AQARA_DEVICE_MAGNET,
    AQARA_DEVICE_SWITCH,
    AQARA_SWITCH_ACTION_CLICK,
    AQARA_SWITCH_ACTION_DOUBLE_CLICK,
    AQARA_SWITCH_ACTION_LONG_CLICK_PRESS,
    AQARA_SWITCH_ACTION_LONG_CLICK_RELEASE,
    AQARA_DATA_VOLTAGE,
    AQARA_DATA_STATUS,
    AQARA_DATA_TEMPERATURE,
    AQARA_DATA_HUMIDITY
)

HASS_UPDATE_SIGNAL = "update_hass_sensor"
HASS_HEARTBEAT_SIGNAL = "heartbeat_hass_sensor"

_LOGGER = logging.getLogger(__name__)

BUTTON_ACTION_MAP = {
    "click": AQARA_SWITCH_ACTION_CLICK,
    "double_click": AQARA_SWITCH_ACTION_DOUBLE_CLICK,
    "long_click_press": AQARA_SWITCH_ACTION_LONG_CLICK_PRESS,
    "long_click_release": AQARA_SWITCH_ACTION_LONG_CLICK_RELEASE
}

def create_device(gateway, model, sid):
    """Device factory"""
    if model == AQARA_DEVICE_HT:
        return AqaraHTSensor(gateway, sid)
    elif model == AQARA_DEVICE_MOTION:
        return AqaraMotionSensor(gateway, sid)
    elif model == AQARA_DEVICE_MAGNET:
        return AqaraContactSensor(gateway, sid)
    elif model == AQARA_DEVICE_SWITCH:
        return AqaraSwitchSensor(gateway, sid)
    else:
        raise RuntimeError('Unsupported device type: {} [{}]'.format(model, sid))

class AqaraBaseDevice(object):
    """AqaraBaseDevice"""
    def __init__(self, model, gateway, sid):
        self._gateway = gateway
        self._model = model
        self._sid = sid
        self._voltage = None

    @property
    def sid(self):
        """property: sid"""
        return self._sid

    @property
    def model(self):
        """property: model"""
        return self._model

    @property
    def voltage(self):
        """property: voltage"""
        return self._voltage

    def subscribe_update(self, handle_update):
        """subscribe to sensor update event"""
        dispatcher.connect(handle_update, signal=HASS_UPDATE_SIGNAL, sender=self)

    def unsubscribe_update(self, handle_update):
        """unsubscribe from sensor update event"""
        dispatcher.disconnect(handle_update, signal=HASS_UPDATE_SIGNAL, sender=self)

    def subscribe_heartbeat(self, handle_heartbeat):
        """subscirbe to sensor heartbeat event"""
        dispatcher.connect(handle_heartbeat, signal=HASS_HEARTBEAT_SIGNAL, sender=self)

    def unsubscribe_heartbeat(self, handle_heartbeat):
        """unsubscribe from sensor heartbeat event"""
        dispatcher.disconnect(handle_heartbeat, signal=HASS_HEARTBEAT_SIGNAL, sender=self)

    def update_now(self):
        """force read sensor data"""
        self._gateway.read_device(self._sid)

    def on_update(self, data):
        """handler for sensor data update"""
        self.log_info("on_update: {}".format(json.dumps(data)))
        if AQARA_DATA_VOLTAGE in data:
            self._voltage = data[AQARA_DATA_VOLTAGE]
        self.do_update(data)
        dispatcher.send(signal=HASS_UPDATE_SIGNAL, sender=self)

    def on_heartbeat(self, data):
        """handler for heartbeat"""
        self.log_info("on_heartbeat: {}".format(json.dumps(data)))
        if AQARA_DATA_VOLTAGE in data:
            self._voltage = data[AQARA_DATA_VOLTAGE]
        self.do_heartbeat(data)
        dispatcher.send(signal=HASS_HEARTBEAT_SIGNAL, sender=self)

    def do_update(self, data):
        """update sensor state according to data"""
        pass

    def do_heartbeat(self, data):
        """update heartbeat"""
        pass

    def log_warning(self, msg):
        """log warning"""
        self._log(_LOGGER.warning, msg)

    def log_info(self, msg):
        """log info"""
        self._log(_LOGGER.info, msg)

    def log_debug(self, msg):
        """log debug"""
        self._log(_LOGGER.debug, msg)

    def _log(self, log_func, msg):
        """log"""
        log_func('%s [%s]: %s', self.sid, self.model, msg)

class AqaraHTSensor(AqaraBaseDevice):
    """AqaraHTSensor"""
    def __init__(self, gateway, sid):
        super().__init__(AQARA_DEVICE_HT, gateway, sid)
        self._temperature = 0
        self._humidity = 0

    @property
    def temperature(self):
        """property: temperature (unit: C)"""
        return self._temperature

    @property
    def humidity(self):
        """property: humidity (unit: %)"""
        return self._humidity

    def do_update(self, data):
        if AQARA_DATA_TEMPERATURE in data:
            self._temperature = self.parse_value(data[AQARA_DATA_TEMPERATURE])
        if AQARA_DATA_HUMIDITY in data:
            self._humidity = self.parse_value(data[AQARA_DATA_HUMIDITY])

    def do_heartbeat(self, data):
        # heartbeat for HT sensor contains the same data as report
        self.do_update(data)

    @staticmethod
    def parse_value(str_value):
        """parse sensor_ht values"""
        return round(int(str_value) / 100, 1)


class AqaraContactSensor(AqaraBaseDevice):
    """AqaraContactSensor"""
    def __init__(self, gateway, sid):
        super().__init__(AQARA_DEVICE_MAGNET, gateway, sid)
        self._triggered = False

    @property
    def triggered(self):
        """property: triggered (bool)"""
        return self._triggered

    def do_update(self, data):
        if AQARA_DATA_STATUS in data:
            self._triggered = data[AQARA_DATA_STATUS] == "open"

    def do_heartbeat(self, data):
        self.do_update(data)

class AqaraMotionSensor(AqaraBaseDevice):
    """AqaraMotionSensor"""
    def __init__(self, gateway, sid):
        super().__init__(AQARA_DEVICE_MOTION, gateway, sid)
        self._triggered = False

    @property
    def triggered(self):
        """property: triggered (bool)"""
        return self._triggered

    def do_update(self, data):
        if AQARA_DATA_STATUS in data:
            self._triggered = data[AQARA_DATA_STATUS] == "motion"
        else:
            self._triggered = False

class AqaraSwitchSensor(AqaraBaseDevice):
    """AqaraMotionSensor"""
    def __init__(self, gateway, sid):
        super().__init__(AQARA_DEVICE_SWITCH, gateway, sid)
        self._action = None

    @property
    def action(self):
        """property: last_action"""
        return self._action

    def do_update(self, data):
        if AQARA_DATA_STATUS in data:
            status = data[AQARA_DATA_STATUS]
            if status in BUTTON_ACTION_MAP:
                self._action = BUTTON_ACTION_MAP[status]
            else:
                self.log_warning('invalid status: {}' % status)
