import re
import sys
import os

from ConfigParser import ConfigParser

ROUTER_ID = None
INPUT_PORTS = []
OUTPUT_PORTS = {}
ROUTING_TABLE = {}




def main(filename):
    configParser = ConfigParser()
    
    try:
        ROUTER_ID, INPUT_PORTS, OUTPUT_PORTS = configParser.read_config_file(filename)
    except Exception as exception:
        print(exception)
        quit()
    print(ROUTER_ID)
    print(INPUT_PORTS)
    print(OUTPUT_PORTS)
    

if __name__=="__main__":
    if len(sys.argv) != 2:
        print("Error: You must input exactly one parameter which is the config file name")
    else:
        filename = sys.argv[1]
        main(filename)