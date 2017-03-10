# Aqara Gateway Python Library

[![Build Status](https://travis-ci.org/javefang/pyaqara.svg?branch=master)](https://travis-ci.org/javefang/pyaqara)

Python binding for the Aqara devices, based on protocol defined [here](https://github.com/louisZL/lumi-gateway-local-api)

The aim of this project is to abstract the protocol implementation details away and let
developer focus on developing features and integrations on top of the Aqara hardware, with
a focus on [HomeAssistant](https://github.com/home-assistant/home-assistant) integration.
It also protect developers from breaking changes in the API.

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

### Discovery
Once started, the client will automatically discover all gateways.
It will also discover all attached devices (sensors) when each new gateway is discovered.

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
True

# magnet
>>> print(sensor_magnet.triggered)
True

# switch
>>> print(sensor_switch.last_action)
click
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

### Gateway function

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
