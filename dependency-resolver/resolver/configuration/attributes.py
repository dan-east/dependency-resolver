import logging
from enum import StrEnum

_logger = logging.getLogger(__name__)

class ConfigAttributes(StrEnum) :
    # top level
    PROJECT_NAME = "project"
    VERSION = "version"
    
    # sources
    SOURCES = "sources"
    SOURCE_NAME = "name"
    SOURCE_BASE = "base"
    SOURCE_DESCRIPTION = "description"

    SOURCE_PROTOCOL = "protocol"
    PROTOCOL_HTTPS = "https"
    PROTOCOL_FS = "filesystem"

    SOURCE_TYPE = "type"
    TYPE_ABSOLUTE = "absolute"
    TYPE_PROJECT = "project"

    # dependencies
    DEPENDENCIES = "dependencies"
    DEPENDENCY_NAME = "name"
    DEPENDENCY_DESCRIPTION = "description"
    DEPENDENCY_TARGET_DIR = "target_dir"
    DEPENDENCY_TARGET_NAME = "target_name"
    DEPENDENCY_SOURCE_DEPENDENCY = "source"
    DEPENDENCY_SOURCE_PATH = "source_path"

    RESOLVE_ACTION = "resolve_action"
    RESOLVE_COPY = "copy"
    RESOLVE_UNZIP = "unzip"
    RESOLVE_UNTAR = "untar"
