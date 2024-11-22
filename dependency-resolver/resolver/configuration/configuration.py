import logging
from .attributes import ConfigAttributes
from ..utilities import helpers, json, file

_logger = logging.getLogger(__name__)

class Configuration :
    def __init__(self, configurationPath:str) :
        helpers.assertSet(_logger, f"Please specify path to configuration JSON file", configurationPath)
        self._configPath:str = configurationPath
        self._loadConfigutation()

    # Load the configuration 
    def _loadConfigutation(self) :
        if file.isFile(self._getConfigurationPath()) :
            self._config:dict = json.parseFromFile(self._getConfigurationPath())
            helpers.assertSet(_logger, f"Unable to load the JSON representation in the path {self._getConfigurationPath()}", self.getConfiguration()) # make sure we managed to open the configuration
            _logger.debug(f"Loaded configuration: {self.getConfiguration()}")
        else :
            _logger.debug(f"Cannot load configuration - file doesn't exist at {self._getConfigurationPath()}")
            exit(1) # a terminal condition.


    # Returns the loaded configuration path
    def _getConfigurationPath(self) -> str :
        """Returns the path to the configuration file."""
        return self._configPath
    
    def getConfigurationHome(self) -> str :
        """Returns the path to the direcory the configuration file was loaded from. All dependency targets are relative to this directory."""
        return file.getParentDirectory(self._getConfigurationPath())

    # Returns the loaded configuration.
    def getConfiguration(self) -> dict :
        return self._config
                
    # Prints the loaded configuration.
    def printConfiguration(self) :
        print(self.getConfiguration())

    # Finds any errors (required attributes that are missing) in the configuration and prints them.
    def validateConfiguration(self) :
        errors:list[str] = self._findAnyConfigErrors()
        if len(errors) > 0 :
            print(f"Invalid: the configuration at {self._getConfigurationPath()} contains {len(errors)} error(s):")
            count:int = 0
            for error in errors:
                count += 1
                print(f"  {count} -> {error}")
        else :
            print(f"Valid: the configuration at {self._getConfigurationPath()} doesn't contain any errors.")              

    # Returns the number of configuration errors (missing required attributes).
    def numberOfErrors(self) -> int :
        return len(self._findAnyConfigErrors())


    # Finds any errors (required attributes that are missing) in the configuration and returns a list of them.
    def _findAnyConfigErrors(self) -> list[str] :
        config:dict = self.getConfiguration()
        errors:list[str] = []
        self._validateProjectName(config, errors)
        self._validateSources(config, errors)
        self._validateDependencies(config, errors)
        return errors

    # Adds any errors to a list of previous errors.    
    def _validateProjectName(self, config:dict, errors:list[str]) :
        helpers.addIfNotNone(errors, self._doesKeyExist(config, ConfigAttributes.PROJECT_NAME, False))
        
    # Adds any sources errors to a list of previous errors.    
    def _validateSources(self, config:dict, errors:list[str]) :
        key:str = ConfigAttributes.SOURCES
        error:str = self._doesKeyExist(config, key, False)
        if error :
            errors.append(error)
        else :
            for source in config.get(key) :
                self._validateSource(source, errors)
        
    # Adds any errors found in the source to a list of previous errors.
    def _validateSource(self, source:dict, errors:list[str]) :
        helpers.addIfNotNone(errors, self._doesKeyExist(source, ConfigAttributes.SOURCE_NAME))
        helpers.addIfNotNone(errors, self._doesKeyExist(source, ConfigAttributes.SOURCE_PROTOCOL))
                             
    # Adds any sources errors to  a list of previous errors.    
    def _validateDependencies(self, config:dict, errors:list[str]) :
        key:str = ConfigAttributes.DEPENDENCIES
        error:str = self._doesKeyExist(config, key, False)
        if error :
            errors.append(error)
        else :
            for dependency in config.get(key) :
                self._validateDependency(dependency, errors)
        
    # Adds any errors found in the source to a list of previous errors.
    def _validateDependency(self, dependency:dict, errors:list[str]) :
        helpers.addIfNotNone(errors, self._doesKeyExist(dependency, ConfigAttributes.DEPENDENCY_TARGET_DIR))
        helpers.addIfNotNone(errors, self._doesKeyExist(dependency, ConfigAttributes.DEPENDENCY_SOURCE_DEPENDENCY))


    # Checks to see if a key has been specified in the config. Returns an error message if missing/empty.
    def _doesKeyExist(self, config:dict, key, context:bool = True) -> str :
        if key not in config or not config[key] :
            error:str = f"Required attribute {key} is not specified or is empty."
            if context :
                error=f"{error} In: {config}."
            return error
