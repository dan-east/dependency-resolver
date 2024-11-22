import logging
import os
from ..utilities import file
from ..dependencies.dependency import Dependency
from ..errors.errors import FetchError, ResolveError

_logger = logging.getLogger(__name__)

class Cache() :
    # When we download something in the cache we have to give it a file name.
    #  This may the the target name of the dependency, but if not specified then we use this default.
    #  This is a possible clash, but it needs to be something deterministic for a dependency.
    defaultDownloadName:str = "downloadedSource"


    def __init__(self, cacheRoot:str = None) :
        """
        Construct the cache.
            Parameters:
                cacheRoot - the home/root directory of the cache. All downloaded sources will be added somewhere in this directory.
        """
        self._setCacheRoot(cacheRoot)


    def clean(self) :
        """Empty the cache"""
        if file.exists(self._getCachePath()) :
            _logger.info(f"Cleaning cache: {self._getCachePath()}")
            file.deleteContents(self._getCachePath())
        

    def init(self, cacheName:str = None) :
        """
        Initialises the cache. 
        Must be called before it is used.

        Parameters:
            cacheName - Can give this cache a specific name. All sources will be downloaded under this name, seperating the from the rest of the cache. Optional.
        """
        self._setCacheName(cacheName)
        file.mkdir(self._getCachePath(), mode=0o755) # make sure the cache directory exists


    def fetchDependency(self, dependency:Dependency, alwaysFetch:bool = False) :
        """
        Fetches a dependancy's source into the cache.
        
        Parameters:
            dependency - the dependency to fetch.
            alwaysFetch - will always fetch the dependency's source, even if it is already in the cache.
        """
        _logger.debug(f"Downloading dependency {dependency.getName()}...")
        
        if alwaysFetch or not self._isCached(dependency) :
            targetDir:str = self._generateCacheLocation(dependency)
            if targetDir and not file.exists(targetDir) :
                _logger.debug(f"Trying to create cache location: {targetDir}")
                file.mkdir(targetDir, mode=0o755)

            if targetDir and file.isDir(targetDir) :
                cacheDownloadPath:str = self._generateCacheDownloadPath(dependency)
                if file.exists(cacheDownloadPath) :
                    file.delete(cacheDownloadPath)

                targetName:str = self._generateCachedFileName(dependency)
                dependency.fetchSource(targetDir, targetName)
                _logger.debug(f"...successfully cached dependency {dependency.getName()}: source {dependency.getSource().getName()}::{dependency.getSourcePath()} -> {targetDir}/{targetName}.")
            else :
                _logger.debug(f"...failed to cache dependency {dependency.getName()} - the cache already has a file (not a directory) at the target download location in the cache ({targetDir}): source {dependency.getSource().getName()}::{dependency.getSourcePath()} -> {targetDir}/{targetName}.")
                raise FetchError(f"Failed to cache dependency {dependency.getName()} - the cache already has a file (not a directory) at the target download location in the cache ({targetDir}).")
        else :
            _logger.debug(f"...dependency {dependency.getName()} already in cache.")
            

    def resolveDependency(self, dependency:Dependency, targetHomeDir:str, onlyMissing:bool = False) :
        """
        Resolves a dependancy by performing its Resolve action from the fetched source in the cache into the target location.
        
        Parameters:
            dependency - the dependency to resolve.
            targetHome - Each dependency is relative the configuration that defines it. This is the path to that directory.
            onlyMissing - only resolve missing dependencies. Non filesystem copies (for example unzipping) resolve actions are always completed.
        """
        _logger.debug(f"Resolving dependency {dependency.getName()}...")
        if self._isCached(dependency) :
            dependency.resolve(self._generateCacheDownloadPath(dependency), targetHomeDir)
            _logger.debug(f"...successfully resolved dependency {dependency.getName()}.")
        else :
            _logger.debug(f"...dependency {dependency.getName()} not in cache.")
            raise ResolveError(f"Failed to resolve dependency {dependency.getName()} - the source has not been fetched to the cache.")


    # Generates the path to the directory (inside the cache) that the source of the dependency is fetched to.
    def _generateCacheLocation(self, dependency:Dependency) -> str :
        # cache location is based on the source name and the source path   
        return file.buildPath(self._getCachePath(), dependency.getSource().getName(), dependency.getSourcePath())


    # Generates the a name to use in the cache to represent the fetched source.
    # Usually the target name of the dependency, if thats been specified.
    def _generateCachedFileName(self, dependency:Dependency) -> str :
        cacheName:str = dependency.getTargetName()
        if not cacheName and dependency.getSourcePath() : # use the end of the source path if specified.
            cacheName = file.returnLastPartOfPath(dependency.getSourcePath())
        if not cacheName : # just use a default name
            cacheName = self.defaultDownloadName 
        return cacheName


    # Return to the full path (including the file name) of the fetched dependency in the cache.
    def _generateCacheDownloadPath(self, dependency:Dependency) -> str :
        return file.buildPath(self._generateCacheLocation(dependency), self._generateCachedFileName(dependency))
    

    # Sets the root of this cache.
    def _setCacheRoot(self, cacheRoot:str = None) :
        if cacheRoot :
            if not file.exists(cacheRoot) or (file.exists(cacheRoot) and file.isDir(cacheRoot)) :
                self._cacheRoot:str = cacheRoot
            else :
                _logger.error(f"Unable to create cache with a root of {cacheRoot} - a file already exists at this location (at least its not a directory - could be a permission thing also).")
                exit(1)
        else :
            self._cacheRoot:str = file.buildPath(os.getcwd(), "resolverCache") # same place as being run from.
        
        _logger.debug(f"Caching to {self._getCacheRoot()}")


    # Returns the root path of the cache
    def _getCacheRoot(self) -> str :
        return self._cacheRoot

    # Sets the name of this cache. This can be used to use a specific cache for a project rather than using the same cache for everything.
    def _setCacheName(self, cacheName:str) :
        if cacheName is None :
            self._cacheName = "default"
        else :
            self._cacheName = cacheName
    
        self._setCachePath(self._getCacheRoot(), self._getCacheName())


    # Returns the name of the cache - this is configurable for each project (and is often the name of the project)
    def _getCacheName(self) -> str :
        return self._cacheName
    
    # Constructs and sets the path for the cache.
    def _setCachePath(self, root:str, name:str) :
         self._cachePath:str = file.buildPath(root, name)
    
    # Returns the path for this cache
    def _getCachePath(self) -> str :
        return self._cachePath
    
    # Is there an entry in the cache for this dependency already?
    def _isCached(self, dependency:Dependency) -> bool :
        return file.exists(self._generateCacheDownloadPath(dependency))