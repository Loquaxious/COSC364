COMMAND = 0x02  # As always a response packet
VERSION = 0x02  # Version number is always 2 as stated in 4.2 of the assignment specification


class RIPPacket:
    """
    Python class that represents a RIP message
    """

    def __init__(self, src_id):
        """
        Initialises the common header of the RIP message as a byte array
        :param src_id: the source id of the router the packet is being sent from
        """
        if is_router_id_valid(src_id):
            self.src_id = src_id
            self.packet = bytearray(4)
            self.packet[0] = COMMAND
            self.packet[1] = VERSION
            self.packet[2] = src_id >> 8
            self.packet[3] = (src_id & 0x00FF)
        else:
            print("Error: Failed to create RIP packet. Source router id is invalid")
            raise ValueError

    def append_entry(self, router_id, metric):
        """
        Appends a RIP packet entry onto the common header of the RIP packet and returns it
        :param router_id: router_id of the router the packet concerns
        :param next_hop: the router id of the next hop router in the path
        :param metric: the cost metric of the path to the destination
        :return: the RIP packet (byte array) including the common header and packet entry(ies)
        """
        rip_entry = bytearray(20)

        # Checks that there is not more than 25 entries in the message (The max given in the RIP spec)
        if len(self.packet) > 500:
            print('Cannot add more that 25 entries to a packet')
            return

        # Check for the value of the Router ID and print for debugging
        if is_router_id_valid(router_id):
            rip_entry[4] = router_id >> 24
            rip_entry[5] = (router_id & 0x00FF0000) >> 16
            rip_entry[6] = (router_id & 0x0000FF00) >> 8
            rip_entry[7] = (router_id & 0x000000FF)
        else:
            # Drop entry as invalid router id
            print("Dropped entry as invalid router id")
            # return self.packet

        # Check for the value of the metric and print for debugging
        if is_metric_valid(metric):
            rip_entry[16] = metric >> 24
            rip_entry[17] = (metric & 0x00FF0000) >> 16
            rip_entry[18] = (metric & 0x0000FF00) >> 8
            rip_entry[19] = (metric & 0x000000FF)
        else:
            # Drop the entry as invalid metric
            print("Dropped the entry as invalid metric")
            # return self.packet

        self.packet.extend(rip_entry)
        # return self.packet

    def refresh_entries(self):
        """Reverts the message back to just the common header (deletes all entries)"""
        self.packet = self.packet[:4]


def is_router_id_valid(router_id):
    """
    Checks to see if the router id valid
    :param router_id: an integer representing the router id
    :return: boolean, true if id is valid, false if not
    """
    return 0 < router_id < 64001


def is_metric_valid(metric):
    """
    Checks to see if the given cost metric is a valid value
    :param metric: integer, the cost metric of a RIP path
    :return: boolean, true if value is valid, false if not
    """
    return 0 < metric < 17


# def main():
#     # Testing
#     test = RIPPacket(1)
#     print(test.packet)
#     print(RIPPacket(64000).packet)
#     # print(RIPPacket(0))
#     # print(RIPPacket(64001))
#
#     print(test.packet)
#     test.rip_packet_entry(3000, 0, 0)
#     test.rip_packet_entry(3000, 1, 17)
#     test.rip_packet_entry(3000, 64001, 1)
#     test.rip_packet_entry(3000, 1, 1)
#     test.rip_packet_entry(3000, 64000, 16)
#     print(test.packet)
#     print(test.packet[-1])
#
#
# if __name__ == '__main__':
#     main()
