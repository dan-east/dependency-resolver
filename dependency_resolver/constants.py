import os

# Defines where the home directory is - can be overridden
HOME_DIR = os.getenv("RESOLVER_HOME", os.getcwd())

# Default runtime directory
RUNTIME_DIR:str = os.getenv("RESOLVER_RUNTIME_DIR", f"{HOME_DIR}/dependency-resolver-runtime")

# Logging constants
LOG_DIR = os.getenv("RESOLVER_LOG_DIR", RUNTIME_DIR)
LOG_TO_FILE=f"{LOG_DIR}/resolver.log"
