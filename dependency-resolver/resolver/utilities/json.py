import logging
import json
from . import file

# Logging
_logger = logging.getLogger(__name__) # module name

# Returns an object representing the deserialised JSON document from a file or None if it can't open or decode the JSON
def parseFromFile(path:str) -> any :
    try :
        if file.exists(path) :
            with open(path) as openFile:
                _logger.debug(f"Opening JSON file at {path}")
                return json.load(fp=openFile)
        else :
            _logger.error(f"Cannot open non-existant file at {path}")            
    except json.JSONDecodeError as e :    
        _logger.error(f"Unable to decode JSON in file at {path} : {e}")

    return None
