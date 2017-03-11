"""Constants of the aqara protocol"""

MCAST_ADDR = "224.0.0.50"
MCAST_PORT = 4321

LISTEN_IP = "0.0.0.0"
LISTEN_PORT = 9898

GATEWAY_PORT = 9898

AQARA_DEVICE_HT = 'sensor_ht'
AQARA_DEVICE_MOTION = 'motion'
AQARA_DEVICE_MAGNET = 'magnet'
AQARA_DEVICE_SWITCH = 'switch'
AQARA_DEVICE_GATEWAY = 'gateway'

AQARA_SWITCH_ACTION_CLICK = 'click'
AQARA_SWITCH_ACTION_DOUBLE_CLICK = 'double_click'
AQARA_SWITCH_ACTION_LONG_CLICK_PRESS = 'long_click_press'
AQARA_SWITCH_ACTION_LONG_CLICK_RELEASE = 'long_click_release'


AQARA_ENCRYPT_IV = b'\x17\x99\x6d\x09\x3d\x28\xdd\xb3\xba\x69\x5a\x2e\x6f\x58\x56\x2e'
AQARA_ENCRYPT_DUMMY_PASSWORD = 'thisisa16bsecret'

AQARA_DEFAULT_VOLTAGE = 9999 # set to a large number when unknown
