
"""
Program for putting together a RIP packet
Author: Logan Lee
Student ID: 26029766
"""
COMMAND = 0x02 # As awlays a response packet
VERSION = 0x02 # Version number is always 2 as stated in 4.2 of the assignment specification


def rip_packet_header(router_id):
    packet = bytearray(4)
    packet[0] = COMMAND
    packet[1] = VERSION
    packet[2] = router_id >> 8
    packet[3] = (router_id & 0x00FF)
    print(packet)


def rip_packet_entry():
    rip_entry = bytearray(20)

    rip_entry[0] # addr family identifier (0 if one entry in packet and metric of 16 (inf))
    rip_entry[1] # addr family identifier

    # Do a check for the value of the Router ID and print for debugging
    rip_entry[4] # router id
    rip_entry[5] # router id
    rip_entry[6] # router id
    rip_entry[7] # router id

    # Do a check for the value of the metric and print for debugging
    rip_entry[16] # metric
    rip_entry[17] # metric
    rip_entry[18] # metric
    rip_entry[19] # metric


# def main():
#
#
#
# if __name__ == '__main__':
#     main()
