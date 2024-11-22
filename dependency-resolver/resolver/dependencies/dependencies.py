import logging
from .dependency import Dependency

_logger = logging.getLogger(__name__)

class Dependencies() :
    
    def __init__(self) :
        self._dependencies:list[Dependency] = []

    # Adds a dependency
    def addDependency(self, dependency:Dependency) :
        self._dependencies.append(dependency)

    # Get a source with a given name
    def getDependencies(self) -> list[Dependency]:
        return self._dependencies
    