"""Example for using pyaqara."""
import logging
import asyncio
import json
from aqara.client import AqaraClient

_LOGGER = logging.getLogger(__name__)

def main():
    logging.basicConfig(level=logging.DEBUG)
    loop = asyncio.get_event_loop()
    aqara_client = AqaraClient()
    loop.run_until_complete(aqara_client.start(loop))
    try:
        loop.run_forever()
    except KeyboardInterrupt:
        pass
    aqara_client.stop()
    loop.close()

if __name__=='__main__':
    main()
