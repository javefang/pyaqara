"""Example for using pyaqara."""
import logging
import asyncio
import os
import sys
from aqara.client import AqaraClient

_LOGGER = logging.getLogger(__name__)

def check_var(key):
    if key not in os.environ:
        _LOGGER.error("Environment variable '%s' not set", key)
        sys.exit(1)

def main():
    logging.basicConfig(level=logging.DEBUG)
    loop = asyncio.get_event_loop()

    check_var("AQARA_GW_SID")
    check_var("AQARA_GW_SECRET")
    gw_sid = os.environ["AQARA_GW_SID"]
    gw_secret = os.environ["AQARA_GW_SECRET"]

    aqara_client = AqaraClient({gw_sid: gw_secret})
    loop.run_until_complete(aqara_client.start(loop))
    try:
        loop.run_forever()
    except KeyboardInterrupt:
        pass
    aqara_client.stop()
    loop.close()

if __name__=='__main__':
    main()
