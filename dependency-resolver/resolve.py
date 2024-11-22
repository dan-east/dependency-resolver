#!/usr/bin/env python3

import argparse
import logging
import traceback
import constants
from collections.abc import Sequence
from resolver.utilities import dependencies, file, helpers, log
from resolver.configuration.configuration import Configuration
from resolver.project.project import Project
from resolver.cache.cache import Cache

_logger = logging.getLogger(__name__)


# Sets up the whole shebang
def _init() :
    log.setupRootLogging(constants.LOG_TO_FILE)


# Deals with all the command-line interface
def _commandRunner() :
    parser = argparse.ArgumentParser(description="Fetch and resolve external dependencies for a project.")
    subparsers = parser.add_subparsers()
    _installRequiredPackages(subparsers)
    _printConfig(subparsers)
    _validateConfig(subparsers)
    _updateSourceCache(subparsers)
    _resolveDependencies(subparsers)
    args = parser.parse_args()
    args.func(args)


# Install any required python libraries.
def _installRequiredPackages(subparsers) :
    runner = subparsers.add_parser("install_python_dependencies", help="Install any extra non-default python library dependencies using pip.")
    runner.set_defaults(func=_installRequiredPackagesCommand)
    
def _installRequiredPackagesCommand(args:Sequence[str]) :
    requiredPackages:list[str] = ["requests"] # todo - could externalise this list at some point.
    dependencies.installPackages(requiredPackages)
   

# Print the configuration at the specified path.
def _printConfig(subparsers) :
    runner = subparsers.add_parser("print_config", help="Print the target JSON configuration.")
    runner.add_argument("--configPath", "-c", help='The path to the configuration file', required=True)
    runner.set_defaults(func=_printCommand)

def _printCommand(args:Sequence[str]) :
    _createConfiguration(args).printConfiguration()


# Validate (check for missing required attributes) the configuration at the specified path.
def _validateConfig(subparsers) : 
    runner = subparsers.add_parser("validate_config", help="Validate (find any missing required attributes) in the target JSON configuration.")
    runner.add_argument("--configPath", "-c", help='The path to the configuration file', required=True)
    runner.set_defaults(func=_validateCommand)

def _validateCommand(args:Sequence[str]) :
    _createConfiguration(args).validateConfiguration()


# Update every dependencies source in the cache.
def _updateSourceCache(subparsers) :
    runner = subparsers.add_parser("update_cache", help="Download sources and cache them.")
    runner.add_argument("--clean", action="store_true", help='Clean the cache and logs before downloading Sources. Essentially rebuilds the cache for the given configuration.')
    runner.add_argument("--force", action="store_true", help='Force the update of any source for this project.')
    runner.add_argument("--configPath", "-c", help='The path to the configuration file', required=True)
    runner.add_argument("--cacheRoot", "-R", help='The root of the cache to use for the downloads.', required=False)
    runner.set_defaults(func=_updateSourceCacheCommand)

def _updateSourceCacheCommand(args:Sequence[str]) :
    project:Project = _createProject(args)

    # delete the current log file.
    if args.clean :
        _clean(project=project)

    project.fetchDependencies(alwaysFetch=args.force)


# Update every dependencies source in the cache.
def _resolveDependencies(subparsers) :
    runner = subparsers.add_parser("resolve_from_cache", help="Resolve all dependencies. Must have performed an update_cache to fetch the sources first.")
    runner.add_argument("--configPath", "-c", help='The path to the configuration file', required=True)
    runner.add_argument("--cacheRoot", "-R", help='The root of the cache to use for the downloads.', required=False)
    runner.set_defaults(func=_resolveDependenciesCommand)

def _resolveDependenciesCommand(args:Sequence[str]) :
    _createProject(args).resolveDependencies()
     


# Cleans the log and cache
def _clean(project:Project = None) :
    _resetLogFile()
    _logger.debug("Cleaned log file")
    if project :
        project.clean()
        

# Empties the existing contents of the log file.
#  Helpful when testing.
def _resetLogFile() :
    file.emptyFileContents(constants.LOG_TO_FILE)


# Instansiate the Dependencies class from the supplied command-line arguments.
def _createConfiguration(args:Sequence[str]) -> Configuration :
    if args and helpers.hasValue(args.configPath) :
        return Configuration(configurationPath=args.configPath)

    return Configuration("config.json") # todo - allow some default.


# Creates and checks the config for errors.
def _loadConfiguration(args:Sequence[str]) -> Configuration :
    config:Configuration = _createConfiguration(args)
    if config.numberOfErrors() < 0 :
        message:str = "Errors detected in the configuration - please run validate_config command for details."
        print(message)
        _logger.error(message)
        exit(1)
    
    return config


# Instansiate the Project with the specified configuration.
def _createProject(args:Sequence[str]) -> Project :
    project:Project = Project(_loadConfiguration(args), _createCache(args))
    return project


# Instansiate the Cache. A cacheName can be used to specify a seperate cache to use.
def _createCache(args:Sequence[str]) -> Cache :
    if args :
        return Cache(cacheRoot=args.cacheRoot)

# the entry point
try :
    if __name__ == "__main__" :
        _init()
        _commandRunner()
except Exception :
    _logger.error(f"Command caught the exception (may not be harmful): {traceback.format_exc()}")
    raise
