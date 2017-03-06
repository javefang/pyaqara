"""Aqara Devices"""
def __parse_value(str_value):
    return round(int(str_value) / 100, 1)

class AqaraBaseDevice(object):
    def __init__(self, sid, update_callback):
        self._sid = sid
        self._update_callback = update_callback

    @property
    def sid(self):
        return self._sid

    def on_update(self, data):
        self.do_update(data)
        self._update_callback()

    def do_update(self, data):
        pass

class AqaraHTSensor(AqaraBaseDevice):
    def __init__(self, sid, update_callback):
        super().__init__(sid, update_callback)
        self._temp = 0
        self._humid = 0

    @property
    def temperature(self):
        return self._temp

    @property
    def humidity(self):
        return self._humid

    def do_update(self, data):
        if "temperature" in data:
            self._temp = __parse_value(data["temperature"])
        if "humidity" in data:
            self._humid = __parse_value(data["humidity"])

class AqaraContactSensor(AqaraBaseDevice):
    def __init__(self, sid, update_callback):
        super().__init__(sid, update_callback)
        self._open = False

    @property
    def triggered(self):
        return self._triggered

    def do_update(self, data):
        if "status" in data:
            self._open = data["status"] == "open"
