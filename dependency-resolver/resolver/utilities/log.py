import logging
import logging.handlers
import sys
import os.path

# Logging
_logger = logging.getLogger(__name__) # module name


# Call once to set up logging.
def setupRootLogging(logToFile:str):
  os.makedirs(os.path.dirname(logToFile), 0o666, True) # make sure the parent directory exists

  root = logging.getLogger(None)
  root.setLevel(logging.DEBUG)

  formatter = logging.Formatter('%(asctime)s : %(levelname)s : %(module)s.%(funcName)s(%(lineno)d) >> %(message)s')

  stdout_handler = logging.StreamHandler(sys.stdout)
  stdout_handler.setLevel(logging.INFO)
  stdout_handler.setFormatter(formatter)
  root.addHandler(stdout_handler)
  
  file_handler = logging.handlers.RotatingFileHandler(logToFile, "a", 10*1024*1024, 3)
  file_handler.setLevel(logging.DEBUG)
  file_handler.setFormatter(formatter)
  root.addHandler(file_handler)

  _logger.debug("Logging set up")