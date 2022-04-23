import os
import random
import select
import socket
import sys
from time import sleep

from RoutingTable import *
from RIPPacket import *
from ConfigParser import *

LOCAL_HOST = '127.0.0.1'


class Daemon:
    """
    The daemon program that runs the RIP protocol on the routers
    """
    def __init__(self, config_filename):
        """
        Initialises the router's information: Gets router id, input ports, output ports using the ConfigParser class
        :param config_filename: string, config filename (or file path) of the relevant router for getting routing information
        """
        config = ConfigParser().read_config_file(config_filename)
        self.router_id = config[0]
        self.input_ports = config[1]
        self.output_links = config[2]
        self.input_sockets = self.create_input_sockets()
        self.blocking_time = 1 # only block for 1 second each loop
        self.routing_table = RoutingTable()
        self.periodic_update_timer = datetime.datetime.now() # Timer for periodic updates
        self.periodic_update_timer_limit = 30 + random.randrange(-5, 5) # How long the periodic timer update should wait for

    def create_input_sockets(self):
        """
        Creates, binds and stores a socket for every input port
        :return: list of sockets
        """
        sockets = []
        for port in self.input_ports:
            temp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            temp_socket.bind((LOCAL_HOST, port))
            sockets.append(temp_socket)
        return sockets

    def send_initial_message(self):
        """
        Sends neighbouring routers message with just the RIP packet common header, so they add this router to routing
        tables
        """
        init_packet = RIPPacket(self.router_id).packet
        send_socket = self.input_sockets[0]
        for port in self.output_links.get_ports_list():
            try:
                send_socket.sendto(init_packet, (LOCAL_HOST, port))
            except:
                pass

    def close_sockets(self):
        """
            Closes all open sockets to quit the program
        """
        for socket in self.sockets:
            socket.close()
        self.sockets.clear()

    def receive_packets(self):
        """
            Checks all incoming ports for packets ready to be read. If there are packets, it reads them and interprets the data.
        """
        readable_sockets, _, _ = select.select(self.input_sockets, [], [], self.blocking_time)

        for socket in readable_sockets:
            data, _ = socket.recvfrom(4096)
            self.process_packet(data)

    def process_packet(self, data):
        """
            Takes a bytecode array that contains a RIP packet then first checks the data, then, if the routes are applicable to 
            this router (packet came from a router in its output ports), it updates its forwarding table with the new data
            :param data: bytecode array, contains a RIP packet
        """

        routing_table_updated = False

        rip_header = data[:4]
        rip_data = data[4:]
        command = rip_header[0]
        version = rip_header[1]
        next_hop_router_id = int.from_bytes(rip_header[2:], "big")

        if command != 2:
            print("Error: Incoming packet command is invalid")
            return
        if version != 2:
            print("Error: Incoming packet version is invalid")
            return
        if not (0 < next_hop_router_id < 64001):
            print("Error: Incoming packet router id is invalid")
            return
        if not self.output_links.check_router_in_outputs(next_hop_router_id):
            print("Discarding packet: Router id not in outputs")
            return

        print(f"Received packet from router {next_hop_router_id}")

        if not self.routing_table.check_route_known(next_hop_router_id):
            link = self.output_links.get_link_by_router(next_hop_router_id)
            self.routing_table.add_route(next_hop_router_id, next_hop_router_id, link.metric)
            routing_table_updated = True
        else:
            self.routing_table.get_route_by_router(next_hop_router_id).reset_timers()
        routes = []

        for i in range(0, int(len(rip_data)) - 20, 20):
            routes.append(rip_data[i:i + 20])
        
        for route in routes:
            # Check if the incoming router id is valid
            router_id = route[2]
            if not (0 < router_id < 64001):
                print("Discarding route: Incoming route router id is invalid")
                continue
            if router_id == self.router_id: 
                print("Discarding router: Router id is the same as host router")
                continue

            metric = route[2] + self.output_links.get_link_by_router(router_id).metric
            if not (0 < metric < 17):
                print("Discarding route: Incoming route metric is invalid")
                continue
            
            route_object = self.routing_table.get_route_by_router(router_id)
            if route_object:
                if metric == 16:
                    route_object.mark_for_deletion()
                    routing_table_updated = True
                    continue
                elif metric < route_object.metric:
                    route_object.metric = metric
                    route_object.next_hop = next_hop_router_id
                    routing_table_updated = True
                route_object.reset_timers()
            else:
                self.routing_table.add_route(router_id, next_hop_router_id, metric)
                routing_table_updated = True
        
        if routing_table_updated:
            print("Sending update message")
            self.send_initial_message()
    
    def get_periodic_update_timer(self):
        """
            Converts the update timer into seconds
        """
        return (datetime.datetime.now() - self.periodic_update_timer).seconds
    
    def reset_periodic_update_timer(self):
        """
            Resets the update timer to the current time
        """
        self.periodic_update_timer = datetime.datetime.now()

    def check_periodic_update_timer(self):
        """
            Checks if the update timer has expired, if so, sends out updates then resets the timer
        """
        if self.get_periodic_update_timer() > self.periodic_update_timer_limit:
            print("Sending periodic updates")
            # self.send_update_packets()
            self.send_initial_message()
            self.reset_periodic_update_timer()
    
    def check_route_timers(self):
        """
            Tells the routing table to check the timers for all its routes
        """
        self.routing_table.check_route_timers()
    
    def print_routing_table(self):
        """
            Clears the terminal then prints the routing table
        """
        if os.name == "nt": # OS is windows
            os.system("cls")
        else: # MacOS or Linux
            os.system("clear")
        
        print(self.routing_table)
        



            
        
        



def main(config_filename):
    """
        Runs the RIP Daemon
        :param config_filename: string, config filename (or file path) of the relevant router for getting routing information
    """
    daemon = Daemon(config_filename)
    print(daemon.router_id)
    print(daemon.input_ports)
    print(daemon.output_links)
    daemon.send_initial_message()
    while(1):
        daemon.print_routing_table()
        daemon.receive_packets()
        daemon.check_periodic_update_timer()
        daemon.check_route_timers()
        sleep(2)
    daemon.close_sockets()

if __name__=="__main__":
    if len(sys.argv) != 2:
        print("Error: You must input exactly one parameter which is the config file name")
    else:
        config_filename = sys.argv[1]
        main(config_filename)
        try:
            main(config_filename)
        except Exception as exception:
            print(exception)
            quit()