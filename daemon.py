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
        self.outputs = config[2]
        # TODO Have no idea if sockets can actually be stored in a list then just retrieved later
        self.input_sockets = self.create_input_sockets()

    def create_input_sockets(self):
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

    def send_initial_message(self):
        """
        Sends neighbouring routers message with just the RIP packet common header, so they add this router to routing
        tables
        """
        init_packet = RIPPacket(self.router_id)
        send_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        for port in self.outputs:
            send_socket.connect((LOCAL_HOST, port))
            send_socket.sendall(init_packet)
