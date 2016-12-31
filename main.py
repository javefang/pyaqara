"""Example for using pyaqara."""
import logging
import asyncio
import json
from aqara.aqara import AbstractAqaraEventHandler

class AqaraGatewayFactory(AbstractAqaraEventHandler):
    def handle_heartbeat(self, model, sid, data):
        """Example of overriding the default implementation"""
        print("GatewayFactory::heartbeat: model=%s, sid=%s, data=%s", model, sid, json.dumps(data))

def main():
    logging.basicConfig(level=logging.INFO)
    loop = asyncio.get_event_loop()
    gateway_factory = AqaraGatewayFactory()
    gateway_factory.subscribe()
    try:
        loop.run_forever()
    except KeyboardInterrupt:
        pass
    gateway_factory.unsubscribe()
    loop.close()

if __name__=='__main__':
    main()
