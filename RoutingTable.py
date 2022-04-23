from Route import *
class RoutingTable:
    """
        A routing table that holds information about routes the router knows of
    """
    def __init__(self):
        """
            Initializes the Routing Table with an empty list of routes
        """
        self.routes = []

    def __str__(self):
        """
            Returns the table in a readable string format
        """
        
        table = [
            "+----------------+----------------+----------------+----------------+----------------+",
            "| Destination    | Next Hop       | Metric         | Deletion Timer | Garbage Timer  |",
            "+----------------+----------------+----------------+----------------+----------------+"
        ]

        for route in self.routes:
            table.append("| {0:<14} | {1:<14} | {2:<14} | {3:<14} | {4:<14} |".format(route.destination, route.next_hop, route.metric, route.get_deletion_timer(), route.get_garbage_timer()))
        table.append("+----------------+----------------+----------------+----------------+----------------+")
        return "\n".join(table)

    def check_route_known(self, router_id):
        """
            Checks if the given router exists in a route in the routing table
        """
        return router_id in [route.destination for route in self.routes]

    def add_route(self, destination, next_hop, metric):
        """
            Adds a new route to the routing table then sorts the list to stay in order of router id
        """
        self.routes.append(Route(destination, next_hop, metric))
        self.routes = sorted(self.routes, key=lambda x: x.destination)
    
    def get_route_by_router(self, router_id):
        """
            Looks for a route with the given router_id and returns it if found, returns None otherwise
        """
        for route in self.routes:
            if route.destination == router_id:
                return route

    def check_route_timers(self):
        """
            Runs through the routes in the table and marks them for deletion if the deletion timer is up.
            Removes routes from the table if the route garbage collection timer is up
        """
        routes_to_remove = []
        for i in range(len(self.routes)):
            if self.routes[i].check_timers():
                routes_to_remove.append(i)
        
        for i in routes_to_remove:
            print(f"Removing route to router {self.routes[i].destination}")
            del self.routes[i]
