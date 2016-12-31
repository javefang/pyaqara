"""Example for using pyaqara."""
import logging
import asyncio
import aqara.aqara as aqara

SERVER_IP = "0.0.0.0"
SERVER_PORT = 9898

def main():
    logging.basicConfig(level=logging.INFO)
    loop = asyncio.get_event_loop()
    gateway_factory = aqara.AqaraGatewayFactory()
    gateway_factory.connect()
    try:
        loop.run_forever()
    except KeyboardInterrupt:
        pass
    gateway_factory.disconnect()
    loop.close()

if __name__=='__main__':
    main()
