import re
import sys
from tabnanny import check

ROUTER_ID = None
INPUT_PORTS = []
OUTPUT_PORTS = []

def parseConfigFile(config):
    checkedConfig = []

    for lineNum in range(len(config)):
        
        # Remove any comments from lines
        for i in range(len(config[lineNum])):
            if config[lineNum][i] == '#':
                config[lineNum] = config[lineNum][:i]
                break

        config[lineNum] = config[lineNum].strip() # Remove leading and trailing whitespace

        if config[lineNum] != '': # If line isn't empty
            checkedConfig.append([config[lineNum], lineNum + 1])

    

    return checkedConfig

def organiseConfigInfo(checkedConfig):
    # Check no header names are the same
    if checkedConfig[0][0] == checkedConfig[1][0] or checkedConfig[0][0] == checkedConfig[2][0] or checkedConfig[1][0] == checkedConfig[2][0]:
        message = "Error: Two or more config headers are the same. There must be one line for each of 'router-id', 'input-ports' and 'output-ports'"
        return False, message, None
    for config, lineNum in checkedConfig:
        if config[0] == 'router-id':
            routerIDData = config
            routerIDLine = lineNum
        elif config[0] == 'input-ports':
            inputPortsData = config
            inputPortsLine = lineNum
        elif config[0] == 'output-ports':
            outputPortsData = config
            outputPortsLine = lineNum
        else:
            message = "Error: Invalid config header. There must be one line for each of 'router-id', 'input-ports' and 'output-ports'"
            return False, message, None

    return True, '', [routerIDData, routerIDLine, inputPortsData, inputPortsLine, outputPortsData, outputPortsLine]


def checkConfigRouterID(routerIDData, routerIDLine):
    global ROUTER_ID

    # Check only two values on router id line
    if len(routerIDData) == 2:
        try:
            # Check id number is an integer in the correct range
            ROUTER_ID = int(routerIDData[1])
            if ROUTER_ID < 1 or ROUTER_ID > 64000:
                message = f"Error: Invalid format on line {routerIDLine}. Router ID must be an integer between 1 and 64000."
                return False, message
                
        except: 
            message = f"Error: Invalid format on line {routerIDLine}. Router ID must be an integer."
            return False, message
    else:
        message = f"Error: Invalid format on line {routerIDLine}. Correct format is 'router-id, {{integer between 1 and 64000}}'"
        return False, message
    return True, None

def checkConfigInputPorts(inputPortsData, inputPortsLine):
    global INPUT_PORTS
    
    # Check at least two values on input port line
    if len(inputPortsData) >= 2:
        try:
            for portIndex in range(1, len(inputPortsData)):
                # Check port number is an integer in the correct range
                port = int(inputPortsData[portIndex])
                if port < 1024 or port > 64000:
                    message = f"Error: Invalid format on line {inputPortsLine}. Port number {portIndex} must be an integer between 1024 and 64000."
                    return False, message
                else:
                    if port in INPUT_PORTS: # If port number is duplicated
                        repeatedPortIndex = INPUT_PORTS.index(port) + 1
                        message = f"Error: Invalid format on line {inputPortsLine}. Port numbers {repeatedPortIndex} and {portIndex} are duplicates." 
                        return False, message
                    else:
                        INPUT_PORTS.append(port)
                
        except: 
            message = f"Error: Invalid format on line {inputPortsLine}. Port number {portIndex} must be an integer."
            return False, message

    else:
        message = f"Invalid format on line {inputPortsLine}. Correct format is 'input-ports, {{one or more integers between 1024 and 64000 separated by ', '}}'"
        return False, message
    
    return True, None

def checkConfigOutputPorts(outputPortsData, outputPortsLine):
    global OUTPUT_PORTS

        # Check at least two values on output port line
    if len(outputPortsData) >= 2:
        try:
            for portIndex in range(1, len(outputPortsData)):
                # Check port number is an integer in the correct range
                port = int(outputPortsData[portIndex])
                if port < 1024 or port > 64000:
                    message = f"Error: Invalid format on line {outputPortsLine}. Port number {portIndex} must be an integer between 1024 and 64000."
                    return False, message
                else:
                    if port in INPUT_PORTS: # If port number is duplicated
                        repeatedPortIndex = INPUT_PORTS.index(port) + 1
                        message = f"Error: Invalid format on line {outputPortsLine}. Port numbers {repeatedPortIndex} and {portIndex} are duplicates." 
                        return False, message
                    else:
                        INPUT_PORTS.append(port)
                
        except: 
            message = f"Error: Invalid format on line {outputPortsLine}. Port number {portIndex} must be an integer."
            return False, message

    else:
        message = f"Invalid format on line {outputPortsLine}. Correct format is 'input-ports, {{one or more integers between 1024 and 64000 separated by ', '}}'"
        return False, message

    return True, None


def readConfigFile(filename):
    with open(filename, 'r') as data:
        data = data.read()
        if data:
            config = data.splitlines()

    checkedConfig = parseConfigFile(config)

    for i in range(len(checkedConfig)):
        checkedConfig[i][0] = checkedConfig[i][0].split(', ')

    configOkay, message, configData = organiseConfigInfo(checkedConfig)
    if not configOkay:
        return False, message

    routerIDData, routerIDLine, inputPortsData, inputPortsLine, outputPortsData, outputPortsLine = configData

    routerIDOkay, message = checkConfigRouterID(routerIDData, routerIDLine)
    if not routerIDOkay:
        return False, message

    inputPortsOkay, message = checkConfigInputPorts(inputPortsData, inputPortsLine)
    if not inputPortsOkay:
        return False, message

    outputPortsOkay, message = checkConfigOutputPorts(outputPortsData, outputPortsLine)
    if not outputPortsOkay:
        return False, message

    
    return True, None


def main(filename):
    validConfig, errorMessage = readConfigFile(filename)
    if not validConfig:
        print(errorMessage)
        quit()
    print(INPUT_PORTS)
    

if __name__=="__main__":
    if len(sys.argv) != 2:
        print("Error: You must input exactly one parameter which is the config file name")
    else:
        filename = sys.argv[1]
        main(filename)