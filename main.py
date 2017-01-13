"""Example for using pyaqara."""
import logging
import asyncio
import json
from aqara.aqara import AbstractAqaraEventHandler

_LOGGER = logging.getLogger(__name__)

class AqaraGatewayFactory(AbstractAqaraEventHandler):
    def handle_heartbeat(self, model, sid, data):
        """Example of overriding the default implementation"""
        _LOGGER.info("GatewayFactory::heartbeat: model=%s, sid=%s, data=%s", model, sid, json.dumps(data))

def main():
    logging.basicConfig(level=logging.DEBUG)
    loop = asyncio.get_event_loop()
    gateway_factory = AqaraGatewayFactory()
    loop.run_until_complete(gateway_factory.start(loop))
    try:
        loop.run_forever()
    except KeyboardInterrupt:
        pass
    gateway_factory.stop()
    loop.close()

if __name__=='__main__':
    main()
