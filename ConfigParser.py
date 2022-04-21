import os


class ConfigParser:
    INPUT_PORTS = []
    OUTPUT_PORTS = {}
    ROUTER_ID = None
    def parse_config_file(self, config):
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

    def organise_config_info(self, checked_config):
        """
            Check that all the headers are there and retreive the data for each of the sections
        """
        if len(checked_config) != 3:
            raise Exception("Error: Invalid config header. There must be one line for each of 'router-id', 'input-ports' and 'output-ports'")
        # Check no header names are the same
        if checked_config[0][0][0] == checked_config[1][0][0] or checked_config[0][0][0] == checked_config[2][0][0] or checked_config[1][0][0] == checked_config[2][0][0]:
            raise Exception("Error: Two or more config headers are the same. There must be one line for each of 'router-id', 'input-ports' and 'output-ports'")
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
                raise Exception("Error: Invalid config header. There must be one line for each of 'router-id', 'input-ports' and 'output-ports'")

        return (router_id_data, router_id_line, input_ports_data, input_ports_line, output_ports_data, output_ports_line)


    def check_config_router_id(self, router_id_data, router_id_line):
        """
            Check that the router id is valid and assign it to the global variable
        """
        # Check only two values on router id line (header and router id)
        if len(router_id_data) == 2:
            try:
                # Check id number is an integer in the correct range
                self.ROUTER_ID = int(router_id_data[1])
                if self.ROUTER_ID < 1 or self.ROUTER_ID > 64000:
                    raise Exception(f"Error: Invalid format on line {router_id_line}. Router ID must be an integer between 1 and 64000.")

            except ValueError: 
                raise Exception(f"Error: Invalid format on line {router_id_line}. Router ID must be an integer.")

        else:
            raise Exception(f"Error: Invalid format on line {router_id_line}. Correct format is 'router-id, {{integer between 1 and 64000}}'")

    def check_config_input_ports(self, input_ports_data, input_ports_line):
        """
            Check that the input ports are valid and aren't duplicated, then save them to the global variable
        """
        # Check at least two values on input port line (header and one input port)
        if len(input_ports_data) >= 2:
            try:
                for port_index in range(1, len(input_ports_data)):
                    # Check port number is an integer in the correct range
                    port = int(input_ports_data[port_index])
                    if port < 1024 or port > 64000:
                        raise Exception(f"Error: Invalid format on line {input_ports_line}. Port number {port_index} must be an integer between 1024 and 64000.")
                    else:
                        if port in self.INPUT_PORTS: # If port number is duplicated
                            repeated_port_index = self.INPUT_PORTS.index(port) + 1
                            raise Exception(f"Error: Invalid format on line {input_ports_line}. Port numbers {repeated_port_index} and {port_index} are duplicates." )
                        else:
                            self.INPUT_PORTS.append(port)
            except ValueError: 
                raise Exception(f"Error: Invalid format on line {input_ports_line}. Port number {port_index} must be an integer.")
        else:
            raise Exception(f"Error: Invalid format on line {input_ports_line}. Correct format is 'input-ports, {{one or more integers between 1024 and 64000 separated by ', '}}'")

    def check_config_output_ports(self, output_ports_data, output_ports_line):
        """
            Check that the output ports are valid, aren't duplicated, and have valid metric and router ids, then save them to the global variable
            and build the initial routing table
        """
            # Check at least two values on output port line (header and one output port)
        if len(output_ports_data) >= 2:
            for port_index in range(1, len(output_ports_data)):
                port_data = output_ports_data[port_index].split("-")
                # Check port number is an integer in the correct range
                try:
                    port = int(port_data[0])
                except: 
                    raise Exception(f"Error: Invalid format on line {output_ports_line}. Port number {port_index} must be an integer.")

                try:
                    metric = int(port_data[1])
                except: 
                    raise Exception(f"Error: Invalid format on line {output_ports_line}. Metric for port number {port_index} must be an integer.")

                try:
                    router_id = int(port_data[2])
                except: 
                    raise Exception(f"Error: Invalid format on line {output_ports_line}. Router id for port number {port_index} must be an integer.")

                if port < 1024 or port > 64000:
                    raise Exception(f"Error: Invalid format on line {output_ports_line}. Port number {port_index} must be an integer between 1024 and 64000.")

                else:
                    if port in self.OUTPUT_PORTS: # If port number is duplicated
                        repeated_port_index = list(self.OUTPUT_PORTS.keys()).index(port) + 1
                        raise Exception(f"Error: Invalid format on line {output_ports_line}. Port numbers {repeated_port_index} and {port_index} are duplicates." )

                    elif port in self.INPUT_PORTS: # If an output port is also listed as an input port
                        input_port_index = self.INPUT_PORTS.index(port) + 1
                        raise Exception(f"Error: Invalid format on line {output_ports_line}. Output port {port_index} and input port {input_port_index} are duplicates." )

                    else:
                        self.OUTPUT_PORTS[port] = router_id
        else:
            raise Exception(f"Error: Invalid format on line {output_ports_line}. Correct format is 'input-ports, {{integer between 1024 and 64000}}-{{link metric}}-{{router id}}'")


    def read_config_file(self, filename):
        """
            Read data from the given config filename then check that the contents are valid
        """
        if not os.path.isfile(filename):
            raise Exception("Error: Config file must exist")
        with open(filename, 'r') as data:
            data = data.read()
            if data:
                config = data.splitlines()
            else:
                raise Exception("Error: Config file must not be empty")

        checked_config = self.parse_config_file(config)

        for i in range(len(checked_config)):
            checked_config[i][0] = checked_config[i][0].split(', ')

        config_data = self.organise_config_info(checked_config)

        router_id_data, router_id_line, input_ports_data, input_ports_line, output_ports_data, output_ports_line = config_data

        self.check_config_router_id(router_id_data, router_id_line)
        self.check_config_input_ports(input_ports_data, input_ports_line)
        self.check_config_output_ports(output_ports_data, output_ports_line)

        
        return (self.ROUTER_ID, self.INPUT_PORTS, self.OUTPUT_PORTS)