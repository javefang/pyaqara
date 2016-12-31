"""Example for using pyaqara."""
import logging
import asyncio
import aqara.aqara as aqara

SERVER_IP = "0.0.0.0"
SERVER_PORT = 9898

def main():
    logging.basicConfig(level=logging.INFO)
    loop = asyncio.get_event_loop()
    event_handler = aqara.AqaraEventHandler()
    listen = loop.create_datagram_endpoint(lambda: aqara.AqaraClientProtocol(event_handler), local_addr=(SERVER_IP, SERVER_PORT))
    transport, protocol = loop.run_until_complete(listen)
    try:
        loop.run_forever()
    except KeyboardInterrupt:
        pass
    transport.close()
    loop.close()

if __name__=='__main__':
    main()
