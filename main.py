"""Example for using pyaqara."""
import logging
import asyncio
import os
from aqara.client import AqaraClient

logging.basicConfig(level=logging.INFO)
_LOGGER = logging.getLogger(__name__)

def main():
    logging.basicConfig(level=logging.DEBUG)
    loop = asyncio.get_event_loop()
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
