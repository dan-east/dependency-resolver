import logging
from .source import Source 

# Logging
_logger = logging.getLogger(__name__) # module name

class Sources :
    
    def __init__(self) :
        self._sources:dict = {}

    # Adds a source
    def addSource(self, name:str, source:Source) :
        self._sources[name] = source

    # Get a source with a given name
    def getSource(self, name:str) -> Source :
        return self._sources[name]
        
    # Get a list of all source names
    def getAllSourceName(self) -> list[str]:
        return [*self._sources]