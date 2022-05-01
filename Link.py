class Link:
    """Class that represents a link between two neighbouring routers"""
    def __init__(self, port, metric, router_id):
        """
            Initializes a link object
        """
        self.port = port
        self.metric = metric
        self.router_id = router_id
    
    def __repr__(self):
        """
            Defines how python should represent a Link object
        """
        return f"Link({self.port}, {self.metric}, {self.router_id})"