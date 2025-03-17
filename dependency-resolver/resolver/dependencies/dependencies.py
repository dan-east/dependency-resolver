import logging
from .dependency import Dependency

_logger = logging.getLogger(__name__)

class Dependencies() :
    
    def __init__(self) :
        self._dependencies:list[Dependency] = []

    def addDependency(self, dependency:Dependency) :
        """Adds a new dependency"""
        self._dependencies.append(dependency)

    def getDependencies(self) -> list[Dependency] :
        """Get a source with a given name"""
        return self._dependencies
    
    def getDependency(self, name:str) -> Dependency :
        """Returns the dependency with the given name, if it exists."""
        for dependency in self.getDependencies() :
            if dependency.getName() == name :
                return dependency