import asyncio
import json
import logging
import socket
import struct

_LOGGER = logging.getLogger(__name__)
MCAST_GROUP = "224.0.0.50"
MCAST_PORT = 4321
SERVER_IP = "0.0.0.0"
SERVER_PORT = 9898

class AbstractAqaraEventHandler(object):
    """Implementation for an Aqara Gateway."""

    def __init__(self):
        self.transport = None

    @asyncio.coroutine
    def start(self, loop):
        """Subscribe to gateway events"""
        listen = loop.create_datagram_endpoint(lambda: AqaraClientProtocol(self), local_addr=(SERVER_IP, SERVER_PORT))
        transport, protocol = yield from listen
        self.transport = transport
        _LOGGER.info("subscribed to gateway events")

    def stop(self):
        """Unsubscribe from gateway events"""
        if self.transport is None:
            _LOGGER.info("not subscribed")
        else:
            self.transport.close()
            _LOGGER.info("unsubscribed from gateway events")

    def handle_new_gateway(self, ip, sid):
        """Process a new gateway"""
        _LOGGER.info("New gateway: ip=%s, sid=%s", ip, sid)

    def handle_new_device_list(self, gateway_sid, sids):
        """Process a get_id_list_ack message."""
        _LOGGER.info("New device list: gateway_sid=%s, device_list:%s", gateway_sid, ', '.join(sids))

    def handle_read_ack(self, model, sid, data):
        """Process a read ack."""
        _LOGGER.info("Read ACK: model=%s, sid=%s, data=%s", model, sid, json.dumps(data))

    def handle_report(self, model, sid, data):
        """Process a report message."""
        _LOGGER.info("Report: model=%s, sid=%s, data=%s", model, sid, json.dumps(data))

    def handle_heartbeat(self, model, sid, data):
        """Process a heartbeat"""
        _LOGGER.info("Heartbeat: model=%s, sid=%s, data=%s", model, sid, json.dumps(data))

class AqaraClientProtocol(object):
    def __init__(self, gateway_factory):
        self.gateway_factory = gateway_factory
        self.gateway_reg = {}
        self.transport = None

    def connection_made(self, transport):
        self.transport = transport
        self._add_membership()
        self._discover_gateway()

    def datagram_received(self, data, addr):
        data_str = data.decode()
        msg = json.loads(data_str)
        _LOGGER.debug("packet from %s: %s", addr, data_str)
        self._handle_msg(msg)

    def _add_membership(self):
        _LOGGER.debug("Joining multicast group...")
        sock = self.transport.get_extra_info("socket")
        group = socket.inet_aton(MCAST_GROUP)
        mreq = struct.pack("4sL", group, socket.INADDR_ANY)
        sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)
        _LOGGER.debug("Multicast membership added")

    def _handle_iam(self, ip, sid):
        self.gateway_factory.handle_new_gateway(ip, sid)
        _LOGGER.debug("discover devices (gateway_sid=%s)", sid)
        self.gateway_reg[sid] = ip
        self._discover_gateway_devices(ip)

    def _handle_get_id_list_ack(self, gateway_sid, sids):
        _LOGGER.debug("device list: %s (gateway_sid=%s)", sids, gateway_sid)
        self.gateway_factory.handle_new_device_list(gateway_sid, sids)
        gateway_ip = self.gateway_reg[gateway_sid]
        for sid in sids:
            self._force_read(gateway_ip, sid)

    def _handle_msg(self, msg):
        cmd = msg["cmd"]
        if cmd == "iam":
            ip = msg["ip"]
            sid = msg["sid"]
            self._handle_iam(ip, sid)
        elif cmd == "get_id_list_ack":
            gateway_sid = msg["sid"]
            sids = json.loads(msg["data"])
            self._handle_get_id_list_ack(gateway_sid, sids)
        elif cmd == "report":
            model = msg["model"]
            sid = msg["sid"]
            data = json.loads(msg["data"])
            self.gateway_factory.handle_report(model, sid, data)
        elif cmd == "read_ack":
            model = msg["model"]
            sid = msg["sid"]
            data = json.loads(msg["data"])
            self.gateway_factory.handle_read_ack(model, sid, data)
        elif cmd == "heartbeat":
            model = msg["model"]
            sid = msg["sid"]
            data = json.loads(msg["data"])
            self.gateway_factory.handle_heartbeat(model, sid, data)
        else:
            _LOGGER.warning('unknown command: cmd=%s, data=%s', cmd, json.dumps(msg))

    def _discover_gateway(self):
        _LOGGER.debug("discover gateway")
        self._broadcast({"cmd": "whois"})

    def _discover_gateway_devices(self, gateway_ip):
        self._unicast(gateway_ip, {"cmd": "get_id_list"})

    def _force_read(self, gateway_ip, sid):
        _LOGGER.debug("Force read: %s", sid)
        self._unicast(gateway_ip, {"cmd": "read", "sid": sid})

    def _broadcast(self, msg):
        self._send(MCAST_GROUP, MCAST_PORT, msg)

    def _unicast(self, gateway_ip, msg):
        self._send(gateway_ip, SERVER_PORT, msg)

    def _send(self, ip, port, msg):
        data = json.dumps(msg).encode('utf-8')
        self.transport.sendto(data, (ip, port))
