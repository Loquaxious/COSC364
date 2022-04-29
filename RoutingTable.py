from Route import *
import sys


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
        routes_to_remove = set()
        send_updates = False
        for i in range(len(self.routes)):
            timer_check_result = self.routes[i].check_timers()
            if timer_check_result == 0:
                routes_to_remove.add(i)
                [routes_to_remove.add(x.destination) if x.next_hop == self.routes[i].destination else '' for x in self.routes]
            if timer_check_result in [0, 1]:
                send_updates = True
        
        # Go from highest index to smallest to avoid index out of bounds
        print(routes_to_remove)
        for i in sorted(routes_to_remove, reverse=True):
            print(i)
            print(f"Removing route to router {self.routes[i].destination}")
            del self.routes[i]
        
        return send_updates

def main():
    """Testing"""
    table = RoutingTable()
    print(table)
    table.add_route(4, 2, 1)
    table.add_route(14, 2, 15)
    table.add_route(9, 3, 16)
    print(table)
    print(table.get_route_by_router(9))

if __name__ == "__main__":  
    main()
