import re
import sys
from tabnanny import check

ROUTER_ID = None
INPUT_PORTS = []
OUTPUT_PORTS = {}
ROUTING_TABLE = {}

def parse_config_file(config):
    """
        Parse the given config file by removing whitespace and ignoring comments
    """
    checked_config = []

    for line_num in range(len(config)):
        
        # Remove any comments from lines
        for i in range(len(config[line_num])):
            if config[line_num][i] == '#':
                config[line_num] = config[line_num][:i]
                break

        config[line_num] = config[line_num].strip() # Remove leading and trailing whitespace

        if config[line_num] != '': # If line isn't empty
            checked_config.append([config[line_num], line_num + 1])

    

    return checked_config

def organise_config_info(checked_config):
    """
        Check that all the headers are there and retreive the data for each of the sections
    """
    if len(checked_config) != 3:
        message = "Error: Invalid config header. There must be one line for each of 'router-id', 'input-ports' and 'output-ports'"
        return False, message, None
    # Check no header names are the same
    if checked_config[0][0] == checked_config[1][0] or checked_config[0][0] == checked_config[2][0] or checked_config[1][0] == checked_config[2][0]:
        message = "Error: Two or more config headers are the same. There must be one line for each of 'router-id', 'input-ports' and 'output-ports'"
        return False, message, None
    for config, line_num in checked_config:
        if config[0] == 'router-id':
            router_id_data = config
            router_id_line = line_num
        elif config[0] == 'input-ports':
            input_ports_data = config
            input_ports_line = line_num
        elif config[0] == 'output-ports':
            output_ports_data = config
            output_ports_line = line_num
        else:
            message = "Error: Invalid config header. There must be one line for each of 'router-id', 'input-ports' and 'output-ports'"
            return False, message, None

    return True, '', [router_id_data, router_id_line, input_ports_data, input_ports_line, output_ports_data, output_ports_line]


def check_config_router_id(router_id_data, router_id_line):
    """
        Check that the router id is valid and assign it to the global variable
    """
    global ROUTER_ID

    # Check only two values on router id line (header and router id)
    if len(router_id_data) == 2:
        try:
            # Check id number is an integer in the correct range
            ROUTER_ID = int(router_id_data[1])
            if ROUTER_ID < 1 or ROUTER_ID > 64000:
                message = f"Error: Invalid format on line {router_id_line}. Router ID must be an integer between 1 and 64000."
                return False, message
                
        except: 
            message = f"Error: Invalid format on line {router_id_line}. Router ID must be an integer."
            return False, message
    else:
        message = f"Error: Invalid format on line {router_id_line}. Correct format is 'router-id, {{integer between 1 and 64000}}'"
        return False, message
    return True, None

def check_config_input_ports(input_ports_data, input_ports_line):
    """
        Check that the input ports are valid and aren't duplicated, then save them to the global variable
    """
    global INPUT_PORTS
    
    # Check at least two values on input port line (header and one input port)
    if len(input_ports_data) >= 2:
        try:
            for port_index in range(1, len(input_ports_data)):
                # Check port number is an integer in the correct range
                port = int(input_ports_data[port_index])
                if port < 1024 or port > 64000:
                    message = f"Error: Invalid format on line {input_ports_line}. Port number {port_index} must be an integer between 1024 and 64000."
                    return False, message
                else:
                    if port in INPUT_PORTS: # If port number is duplicated
                        repeated_port_index = INPUT_PORTS.index(port) + 1
                        message = f"Error: Invalid format on line {input_ports_line}. Port numbers {repeated_port_index} and {port_index} are duplicates." 
                        return False, message
                    else:
                        INPUT_PORTS.append(port)
                
        except: 
            message = f"Error: Invalid format on line {input_ports_line}. Port number {port_index} must be an integer."
            return False, message

    else:
        message = f"Invalid format on line {input_ports_line}. Correct format is 'input-ports, {{one or more integers between 1024 and 64000 separated by ', '}}'"
        return False, message
    
    return True, None

def check_config_output_ports(output_ports_data, output_ports_line):
    """
        Check that the output ports are valid, aren't duplicated, and have valid metric and router ids, then save them to the global variable
        and build the initial routing table
    """
    global OUTPUT_PORTS
    global ROUTING_TABLE

        # Check at least two values on output port line (header and one output port)
    if len(output_ports_data) >= 2:
        for port_index in range(1, len(output_ports_data)):
            port_data = output_ports_data[port_index].split("-")
            # Check port number is an integer in the correct range
            try:
                port = int(port_data[0])
            except: 
                message = f"Error: Invalid format on line {output_ports_line}. Port number {port_index} must be an integer."
                return False, message

            try:
                metric = int(port_data[1])
            except: 
                message = f"Error: Invalid format on line {output_ports_line}. Metric for port number {port_index} must be an integer."
                return False, message

            try:
                router_id = int(port_data[2])
            except: 
                message = f"Error: Invalid format on line {output_ports_line}. Router id for port number {port_index} must be an integer."
                return False, message

            if port < 1024 or port > 64000:
                message = f"Error: Invalid format on line {output_ports_line}. Port number {port_index} must be an integer between 1024 and 64000."
                return False, message
            else:
                if port in OUTPUT_PORTS: # If port number is duplicated
                    repeated_port_index = list(OUTPUT_PORTS.keys()).index(port) + 1
                    message = f"Error: Invalid format on line {output_ports_line}. Port numbers {repeated_port_index} and {port_index} are duplicates." 
                    return False, message
                else:
                    next_hop = router_id
                    flag = False
                    timeout = 0
                    garbage_collection = 0
                    ROUTING_TABLE[router_id] = [metric, next_hop, flag, timeout, garbage_collection]
                    OUTPUT_PORTS[port] = router_id

    else:
        message = f"Invalid format on line {output_ports_line}. Correct format is 'input-ports, {{integer between 1024 and 64000}}-{{link metric}}-{{router id}}'"
        return False, message

    return True, None


def read_config_file(filename):
    """
        Read data from the given config filename then check that the contents are valid
    """
    with open(filename, 'r') as data:
        data = data.read()
        if data:
            config = data.splitlines()
        else:
            message = "Config file must not be empty"
            return False, message

    checked_config = parse_config_file(config)

    for i in range(len(checked_config)):
        checked_config[i][0] = checked_config[i][0].split(', ')

    config_okay, message, config_data = organise_config_info(checked_config)
    if not config_okay:
        return False, message

    router_id_data, router_id_line, input_ports_data, input_ports_line, output_ports_data, output_ports_line = config_data

    router_id_okay, message = check_config_router_id(router_id_data, router_id_line)
    if not router_id_okay:
        return False, message

    input_ports_okay, message = check_config_input_ports(input_ports_data, input_ports_line)
    if not input_ports_okay:
        return False, message

    output_ports_okay, message = check_config_output_ports(output_ports_data, output_ports_line)
    if not output_ports_okay:
        return False, message

    
    return True, None


def main(filename):
    valid_config, error_message = read_config_file(filename)
    if not valid_config:
        print(error_message)
        quit()
    print(INPUT_PORTS)
    print(OUTPUT_PORTS)
    

if __name__=="__main__":
    if len(sys.argv) != 2:
        print("Error: You must input exactly one parameter which is the config file name")
    else:
        filename = sys.argv[1]
        main(filename)