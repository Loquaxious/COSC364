from Link import *

class OutputLinks:
    def __init__(self):
        """
            Initializes the object by creating an empty list of links
        """
        self.links = []

    def __repr__(self):
        """
            Defines how python should represent an OutputLinks object
        """
        return f"OutputLinks({[link for link in self.links]})"
    
    def add_link(self, port, metric, router_id):
        """
            Creates a new link with the given values and adds it to its list of links
        """
        self.links.append(Link(port, metric, router_id))

    def get_link_by_port(self, port):
        """
            Looks for a link with the given port and returns it if found, returns None otherwise
        """
        for link in self.links:
            if link.port == port:
                return link
    
    def get_link_by_router(self, router_id):
        """
            Looks for a link with the given router_id and returns it if found, returns None otherwise
        """
        for link in self.links:
            if link.router_id == router_id:
                return link

    def get_ports_list(self):
        """
            Returns a list of ports in the output links
        """
        return [link.port for link in self.links]

    def check_router_in_outputs(self, router_id):
        """
            Checks if the given router id is in the output links
        """
        return router_id in [link.router_id for link in self.links]