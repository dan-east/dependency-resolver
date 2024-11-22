import logging
from .resolveAction import ResolveAction
from ..utilities import helpers, file
from ..sources.source import Source
from ..configuration.attributes import ConfigAttributes

# Logging
_logger = logging.getLogger(__name__) # module name

# Models each dependency, i.e this thing over here needs to go here.
# An action may be defined to perform on the source file as part of resolving this dependency, for example unzip the source file.
class Dependency :

    def __init__(self, name:str, targetDir:str, targetName:str, source:Source, sourcePath:str = None, resolveAction:ResolveAction = None, description:str = None) :
        """
            Parameters:
                targetDir - the path to the target location for the dependancy. This path is relative to the project location (the dir containing the dependancies json configuration)
                targetName - The target file name. Can be None to represent a directory target.
                source - optional. Defines the base url and protocol of the dependency source. Overwrites the sourceProtocol if specified.
                sourcePath - the path to the source. Can be absolute or relative to the base atttibute of the optional source parameter.
                resolveAction - optional. Defines an action carried out when resolving this action.
                description - optional. Can be used to describe the dependancy.
        """
        helpers.assertSet(_logger, f"The dependency have a {ConfigAttributes.DEPENDENCY_NAME} attribute in dependency: {ConfigAttributes.DEPENDENCY_TARGET_DIR}={targetDir}, {ConfigAttributes.DEPENDENCY_TARGET_NAME}={targetName}, {ConfigAttributes.DEPENDENCY_SOURCE_PATH}={sourcePath}.", source)
        helpers.assertSet(_logger, f"The {ConfigAttributes.DEPENDENCY_SOURCE_DEPENDENCY} attribute must be specified in dependency: {ConfigAttributes.DEPENDENCY_TARGET_DIR}={targetDir}, {ConfigAttributes.DEPENDENCY_TARGET_NAME}={targetName}, {ConfigAttributes.DEPENDENCY_SOURCE_PATH}={sourcePath}.", source)
        helpers.assertSet(_logger, f"The {ConfigAttributes.DEPENDENCY_TARGET_DIR} attribute must be set in dependency: {ConfigAttributes.DEPENDENCY_TARGET_NAME}={targetName}, {ConfigAttributes.DEPENDENCY_SOURCE_DEPENDENCY}={source.getName()}, {ConfigAttributes.DEPENDENCY_SOURCE_PATH}: {sourcePath}", targetDir)
        self._name:str = name
        self._targetDir:str = targetDir
        self._targetName:str = targetName      
        self._source:Source = source
        self._sourcePath:str = sourcePath
        self._resolveAction:ResolveAction = resolveAction
        self._description:str = description


    def getName(self) :
        """Returns the name of this dependency"""
        return self._name


    def getTargetPath(self) -> str :
        """Returns the full target path for the dependency."""
        return file.buildPath(self._targetDir, self._targetName)


    def isTargetDirectory(self) -> bool :
        """Returns True if the target path is a directory (opposed to a file)."""
        return helpers.isEmpty(self._targetName)
    

    def getTargetDirectory(self) -> str :
        """Returns the target directory for this dependency."""
        return self._targetDir


    def getTargetName(self) -> str :
        """Returns the target file name for this dependency."""
        return self._targetName

    
    def getAbsoluteSourcePath(self) -> str :
        """Returns the source complete path to this dependency's source. May include the protocol depending on how the source is fetched."""
        return self.getSource().getAbsoluteSourcePath(self.getSourcePath())
    

    def getSource(self) -> Source :
        """Returns the Source of this dependency."""
        return self._source
    

    def getSourcePath(self) -> str :
        """Returns the Source path of this dependency."""
        return self._sourcePath
    

    def fetchSource(self, targetDir:str, targetName:str) :
        """
        Fetches (downloads) the source of this dependency to a specified directory. The download is saved with the given name.

        Parameters:
            targetDir  - fetch this dependency's source to the directory at this path.
            targetName - the filename to give this fetched source in the target directory.

        Raises:
            FetchError if this fails to fetch successfully.
        """
        helpers.assertSet(_logger, f"Cannot fetch the source {self.getSource().getName()} - the target destination was not specified.", targetDir)
        helpers.assertSet(_logger, f"Cannot fetch the source {self.getSource().getName()} - the target filename was not specified.", targetName)
        self.getSource().fetch(self.getSourcePath(), targetDir, targetName)


    def resolve(self, sourcePath:str, targetHomeDir:str) :
        """
        Resolves this dependency. The source must have been fetched first.

        Parameters:
            sourcePath - the path to the fetched source. Most likely points inside a cache.
            targetHomeDir - the place in the filesystem to add it.

        Raises:
            ResolveError if this fails to resolve successfully.
        """
        helpers.assertSet(_logger, f"Cannot resolve the dependency {self.getName()} - the source path wasn't set", sourcePath)
        helpers.assertSet(_logger, f"Cannot resolve the dependency {self.getName()} - the destination directory path wasn't set", targetHomeDir)        
        targetDir:str = file.buildPath(targetHomeDir, self.getTargetDirectory())
        file.mkdir(targetDir, mode=0o744) # just in case
        self._getResolveAction().resolve(sourcePath, targetDir) 
        

    # Returns the resolve action for this dependency.
    def _getResolveAction(self) -> ResolveAction :
        return self._resolveAction