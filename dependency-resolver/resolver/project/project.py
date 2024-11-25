import logging
from .creator import Creator
from ..utilities import helpers
from ..errors.errors import FetchError, ResolveError
from ..configuration.configuration import Configuration
from ..configuration.attributes import ConfigAttributes
from ..sources.sources import Sources
from ..dependencies.dependencies import Dependencies
from ..dependencies.dependency import Dependency
from ..cache.cache import Cache

_logger = logging.getLogger(__name__)

class Project :
    def __init__(self, configuration: Configuration, cache:Cache) :
        """
        Construct the Project.
        This will parse the given configuration.

        Parameters:
            configuration - the configuration to use for this project.
            cache - used as a place to store fetched sources.
        """
        helpers.assertSet(_logger, "Configuration is not set", configuration)
        if configuration.numberOfErrors() > 0 :
            print(f"There are syntax errors in the configuration. To view them run the validate_config command.")
            exit(1)
        self._config:Configuration = configuration
        self._creator:Creator = Creator(self._getConfiguration())
        self._parseConfig()
        self.setCache(cache)
        

    def fetchDependencies(self, alwaysFetch:bool = False) :
        """ 
        Fetch the sources of all the dependencies. 
        
        Parameters:
            alwaysFetch - Fetch the dependency source even if they are already in the cache.
        """
        _logger.debug(f"Fetching all dependencies (force download = {alwaysFetch})")

        # A map of dependendcies already downloaded this fetch
        alreadyDownloaded:list[str] = []

        print(f"Fetching {len(self._getDependencies().getDependencies())} dependencies:")
        count:int = 0
        for dependency in self._getDependencies().getDependencies() :
            count += 1
            if not self._hasBeenDownloaded(alreadyDownloaded, dependency) : 
                print(f"{count}-{dependency.getName()} : Fetching...")
                try :
                    self._fetchDependency(dependency, alwaysFetch)
                    self._addDownloaded(alreadyDownloaded, dependency)
                    print(f"{count}-{dependency.getName()} : Fetched.")
                except FetchError as error:
                    print(f"{count}-{dependency.getName()} : Failed :: {error}.")
            else :
                print(f"{count}-{dependency.getName()} : Already fetched.")
        
        _logger.debug(f"...fetched dependencies.")


    def _fetchDependency(self, dependency:Dependency, alwaysFetch:bool = False) :
        """ 
        Fetch the source of specified dependency. 
        
        Parameters:
            alwaysFetch - Fetch the dependency source even if it is already in the cache.

        Raises:
            FetchError if an error is encountered during the fetch
        """
        _logger.debug(f"Fetching all dependency {dependency.getName()} (force download = {alwaysFetch})")
        self._getCache().fetchDependency(dependency, alwaysFetch)
        _logger.debug(f"...fetched dependency {dependency.getName()}.")
        

    def resolveFetchedDependencies(self, onlyMissing:bool = False) :
        """
        Resolve the dependencies by moving their fetched source to the target location.

        Parameters:
            onlyMissing - Only resolve those sources that are missing at the required direction. Note actions that are not file copies (e.g. unzipping) are always resolved.
        """
        _logger.debug(f"Resolving all dependencies (only missing = {onlyMissing})")

        print(f"Resolving {len(self._getDependencies().getDependencies())} dependencies:")
        count:int = 0
        for dependency in self._getDependencies().getDependencies() :
            count += 1
            print(f"{count}-{dependency.getName()} : Resolving...")
            try :
                self._resolveDependency(dependency, onlyMissing)
                print(f"{count}-{dependency.getName()} : Resolved.")
            except ResolveError as error:
                print(f"{count}-{dependency.getName()} : Failed :: {error}.")
        
        _logger.debug(f"...resolved dependencies.")


    def _resolveDependency(self, dependency:Dependency, onlyMissing:bool = False) :
        """ 
        Fetch the source of specified dependency. 
        
        Parameters:
            onlyMissing - Only resolve those sources that are missing at the required direction. Note actions that are not file copies (e.g. unzipping) are always resolved.

        Raises:
            ResolveError if an error is encountered during the resolve action
        """
        _logger.debug(f"Resolving dependency {dependency.getName()} (only missing = {onlyMissing})")
        self._getCache().resolveDependency(dependency, self._getConfiguration().getConfigurationHome(), onlyMissing)
        _logger.debug(f"...resolved dependency {dependency.getName()}.")


    def resolveDependencies(self, alwaysFetch:bool = False, onlyMissing:bool = False) :
        """
        Resolve all dependencies. Fetch any sources prior to resolving them.

        Parameters:
            onlyMissing - Only resolve those sources that are missing at the required direction. Note actions that are not file copies (e.g. unzipping) are always resolved.
        """
        _logger.debug(f"Fetching and resolving dependencies (force download = {alwaysFetch})")
        self.fetchDependencies(alwaysFetch)
        self.resolveFetchedDependencies(onlyMissing)
        _logger.debug(f"...fetched and resolved dependencies.")


    # Uses the Creator to parse all the dependencies.
    def _parseConfig(self) :
        self._parseProjectName()
        self._sources:Sources = self._creator.createSources()
        self._dependencies:Dependencies = self._creator.createDependencies(self._getSources())

    # Parses the name of this project from the configuration
    def _parseProjectName(self) :
        self._projectName:str = helpers.getKey(self._getConfiguration().getConfiguration(), ConfigAttributes.PROJECT_NAME)
        helpers.assertSet(_logger, "Configuration must specify a Project name (attribute: project)", self._getProjectName())

    # Returns the Configuration.
    def _getConfiguration(self) -> Configuration :
        return self._config
  
    # Returns the name of this project
    def _getProjectName(self) -> str :
        return self._projectName
    
    # Return all the Sources for this project
    def _getSources(self) -> Sources :
        return self._sources
    
    # Return all the dependencies for this project
    def _getDependencies(self) -> Dependencies :
        return self._dependencies

    def setCache(self, cache:Cache) :
        """
        Overwrites the cache for this project.
        """
        self._cache:Cache = cache
        cache.init(self._getProjectName())
        
    # Returns the cache.
    def _getCache(self) :
        return self._cache
    
    # Remember we have already downloaded this source target.
    def _addDownloaded(self, alreadyDownloaded:list[str], dependency:Dependency) :
        alreadyDownloaded.append(dependency.getAbsoluteSourcePath())

    # Checks to we if we have already downloaded this source target.
    def _hasBeenDownloaded(self, alreadyDownloaded:list[str],  dependency:Dependency) :
        return dependency.getAbsoluteSourcePath() in alreadyDownloaded