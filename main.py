"""Example for using pyaqara."""
import logging
import asyncio
import os
import sys
from aqara.client import AqaraClient

logging.basicConfig(level=logging.DEBUG)
_LOGGER = logging.getLogger(__name__)

def check_var(key):
    if key not in os.environ:
        _LOGGER.error("Environment variable '%s' not set", key)
        sys.exit(1)

def handle_new_device(sender, device):
    _LOGGER.info('Discovered new device %s', device.sid)

def handle_new_gateway(sender, gateway):
    _LOGGER.info('Discovered new gateway %s, connecting...', gateway.sid)
    gateway.subscribe(handle_new_device)
    gateway.connect()

def main():
    logging.basicConfig(level=logging.DEBUG)
    loop = asyncio.get_event_loop()

    check_var("AQARA_GW_SID")
    check_var("AQARA_GW_SECRET")
    gw_sid = os.environ["AQARA_GW_SID"]
    gw_secret = os.environ["AQARA_GW_SECRET"]

    aqara_client = AqaraClient({gw_sid: gw_secret})
    aqara_client.subscribe(handle_new_gateway)
    loop.run_until_complete(aqara_client.start(loop))
    try:
        loop.run_forever()
    except KeyboardInterrupt:
        pass
    aqara_client.stop()
    loop.close()

if __name__=='__main__':
    main()
