# Aqara Gateway Python Library

## Important Constants
const MULTICAST_ADDRESS = '224.0.0.50';
const MULTICAST_PORT = 4321;
const SERVER_PORT = 9898;

## Protocol

Discovery
https://github.com/javefang/lumi-gateway-local-api/blob/master/device_discover.md

Read & Write
https://github.com/javefang/lumi-gateway-local-api/blob/master/device_read_write.md

heartbeat
https://github.com/javefang/lumi-gateway-local-api/blob/master/device_heartbeat.md


## Features

Supported
- Sensor discovery
- Active read sensor state
- Passive listen on sensor update
- Temp and Humid Sensor (hass sensor)
- Contact Sensor (hass binary sensor)
- Motion Sensor (hass binary sensor)
- Switch
- Sensor heartbeat (battery level)

Unsupported
- Gateway discovery (whois cmd)
- Write action (switch)
