import logging
from sys import exit

_logger=logging.getLogger(__name__)

# Exits the program is the given variable is None.
#  logger: uses the caller's modules' logger in a attempt to make any resulting logs more contextually relevant
def assertSet(logger:logging.Logger, message:str, variable:any) :
    if not isSet(logger, message, variable) : 
        exit(1)

def isSet(logger:logging.Logger, message:str, variable:any):
    if variable :
        return True
    else :
        logger.error(message)
        return False    

# Tests string to see if it is empty (None, or contain no characters).
def isEmpty(variable:str) -> bool :
    return variable is None or len(variable) == 0

# Test string to see if it holds a value (not None or empty string)
def hasValue(variable:str) -> bool :
    return not isEmpty(variable)

# Add a string to a list of strings if it is not empty
def addIfNotNone(strings:list[str], string:str) :
    if string :
        strings.append(string)

# Returns the key in the given dict or None if it not present
def getKey(config:dict, key) -> any :
    if key not in config :
        return None
    else :
        return config[key]