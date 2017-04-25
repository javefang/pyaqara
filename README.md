# Aqara Gateway Python Library

[![Build Status](https://travis-ci.org/javefang/pyaqara.svg?branch=master)](https://travis-ci.org/javefang/pyaqara)

Python binding for the Aqara devices, based on protocol defined [here](https://github.com/louisZL/lumi-gateway-local-api)

The aim of this project is to abstract the protocol implementation details away and let
developer focus on developing features and integrations on top of the Aqara hardware, with
a focus on [HomeAssistant](https://github.com/home-assistant/home-assistant) integration.
It also protect developers from breaking changes in the API.

Package available on Pypi
```
$ pip3 install pyaqara
```

## Features

Supported Features
- Gateway discovery
- Sensor discovery
- Listen on sensor update
- Read sensor state

Supported Hardwares
  + Temperature and Humidity Sensor
  + Contact Sensor
  + Motion Sensor
  + Aqara Switch Sensor
  + Gateway LED (brightness and color)
  + Gateway Ringtone

## API
### Configuration
Create an instance of AqaraClient, and provide your gateway SIDs and secrets as a dictionary, for Example
```
from aqara.client import AqaraClient

client = AqaraClient({
  "my_gateway_sid": "my_gateway_secret",
  "my_second_gateway_sid": "my_second_gateway_secret"
})
```

### Bootstrap
The API need to be running in an event loop.
```
import asyncio

loop = asyncio.get_event_loop()
loop.run_until_complete(client.start(loop))

try:
  loop.run_forever()
except KeyboardInterrupt:
  pass
client.stop()
loop.close()
```

### Event Handling
Currently the library allow subscription to two events.

#### AQARA_EVENT_NEW_GATEWAY
This event is fired by the ** client ** when a new gateway is discovered. Caller
must subscribe after client is created but before starting the client to avoid
missing events. Usually you would also need to initialise the gateway in the handler.

```
from aqara.const import AQARA_EVENT_NEW_GATEWAY

def handle_new_gateway(sender, gateway):
    _LOGGER.info('Discovered new gateway %s, connecting...', gateway.sid)
    gateway.subscribe(handle_new_device)
    gateway.connect()

client.subscribe(handle_new_gateway)
```

#### AQARA_EVENT_NEW_DEVICE
This event is fired by the ** gateway ** when a new device is discovered. Caller
must subscribe after a gateway is discovered, this usually happens in the new gateway
handler (see above). If you are integrating this library with other system, this
is a good chance to add new devices to the system.

```
from aqara.const import AQARA_EVENT_NEW_DEVICE

def handle_new_device(sender, device):
    _LOGGER.info('Discovered new device %s', device.sid)

gateway.subscribe(handle_new_device)
```

### Discovery
Once started, the client will automatically discover all
gateways. Once a gateway is discovered, you can initialise it
by calling `gateway.connect()`, which will fetch its state and
trigger a device discover.

You can trigger a manual discovery of gateways later
```
client.discover_gateways()
```

Get a list of discovered gateways
```
gateways = client.gateway
```

Get a list of discovered devices of a gateway
```
devices = gateways[0].devices
```

Trigger a manual discovery of devices on a gateway
```
gateway.discover_devices()
```

### Devices
To get type of a device (sensor)
```
print(device.model)
```

To access device data
```
# sensor_ht
>>> print(sensor_ht.temperature)
23.51

>>> print(sensor_ht.humidity)
60.15

# motion
>>> print(sensor_motion.triggered)
True | False

# magnet
>>> print(sensor_magnet.triggered)
True | False

# switch
>>> print(sensor_switch.action)
click | double_click | long_click_press | long_click_release
```

Sensor properties are updated automatically when reports are received.
To subscribe to updates, set a callback function:
```
def on_sensor_update():
  print(sensor.triggered)

sensor.set_update_callback(on_sensor_update)
```

Force update a sensor immediately
```
client.update_now()
```

### Gateway

#### Set gateway light
You can set the brightness and color (RGB) of the gateway LED ring light,
each parameter is an integer ranging from 0-255.

```
# brightness: 77
# red: 255
# green: 79
# blue: 0
gateway.set_light(77, 255, 79, 0) # warm orange
```

#### Play Ringtone
Play system ringtone via the gateway's built-in speaker

```
# mid range for system ringtone is 0-8, 10-13, 20-29, or > 10000 for user defined ringtones
gateway.mid_play(mid)
```
