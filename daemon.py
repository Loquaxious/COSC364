import socket

from ripPacket import *
from ConfigParser import *

LOCAL_HOST = '127.0.0.1'


class Daemon:
    """
    The daemon program that runs the RIP protocol on the routers
    """
    def __init__(self, config_file):
        """
        Initialises the router's information: Gets router id, input ports, output ports using the ConfigParser class
        :param config_file: string, config filename (or file path) of the relevant router for getting routing information
        """
        config = ConfigParser.read_config_file(config_file)
        self.router_id = config[0]
        self.input_ports = config[1]
        self.output_ports = config[2]
        self.sockets = self.create_sockets()

    def create_sockets(self):
        """
        Creates, binds and stores a socket for every input port
        :return: list of sockets
        """
        sockets = []
        for port in self.inputs:
            temp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            temp_socket.bind(LOCAL_HOST, port)
            sockets.append(temp_socket)
        return sockets
