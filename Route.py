import datetime
from gc import garbage
import time


class Route:
    """A class that represents a RIPv2 route to destination node"""
    def __init__(self, destination, next_hop, metric):
        self.destination = destination
        self.next_hop = next_hop
        self.metric = metric
        self.deletion_timer = datetime.datetime.now()
        self.garbage_timer = None
        self.timer_limit = 30 # Mark a route for deletion after 30 seconds of not being heard from, or remove a route if it has been marked for deletion for 30 seconds
    
    def get_deletion_timer(self):
        """
            Converts the deletion timer into seconds
        """
        if self.deletion_timer:
            return (datetime.datetime.now() - self.deletion_timer).seconds
        return 0

    def get_garbage_timer(self):
        """
            Converts the garbage timer into seconds
        """
        if self.garbage_timer:
            return (datetime.datetime.now() - self.garbage_timer).seconds
        return 0
        
    def reset_timers(self):
        """
            Resets the timers for the current route
            Used if the router receives information about the route
        """
        self.deletion_timer = datetime.datetime.now()
        self.garbage_timer = None

    def mark_for_deletion(self):
        """
            Marks the route for deletion by starting the garbage timer
        """
        self.deletion_timer = None
        self.garbage_timer = datetime.datetime.now()
        self.metric = 16
    
    def check_timers(self):
        """
            Checks if the timers have gone over their time threshold 
            Returns an integer between 0 and 2.
            0: Route should be removed from table
            1: Route has been marked for deletion
            2: Route is okay
        """
        if self.get_garbage_timer() > self.timer_limit:
            return 0
        if self.get_deletion_timer() > self.timer_limit:
            print(f"Marking route to router {self.destination} for deletion")
            self.mark_for_deletion()
            return 1
        return 2

    def update_route(self, destination, next_hop, metric):
        """
            Updates the route with the given information
        """
        self.destination = destination
        self.next_hop = next_hop
        self.metric = metric
        self.reset_timers()
        
