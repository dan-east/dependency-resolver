import logging
import subprocess
from subprocess import CompletedProcess

_logger = logging.getLogger(__name__) # module name


# Runs an external command.
#  Uses shell. Spaces in the command need /" escaping.
#  Returns the (standard) output of the command.
#  Throws an subprocess.CalledProcessError if there is an error (failure exit code).
def runExternal(command:str, verifySuccess:bool = True) -> str :
    _logger.debug(f"Executing command: {command}")
    result:CompletedProcess = subprocess.run(command, shell=True, capture_output=True, text=True)

    if _logger.isEnabledFor(logging.DEBUG) :
        if result.stdout is not None and len(result.stdout) > 0 :
            _logger.debug(f"stdout: {result.stdout}")
        if result.stderr is not None and len(result.stderr) > 0 :
            _logger.debug(f"stderr: {result.stderr}")

    if verifySuccess :
        result.check_returncode() # checks the return code and exits if failure indicated.

    return result.stdout


# Runs an external command.
#  Parameters:
#   args - the command split up into individual parts.
#  Returns the (standard) output of the command.
#  Throws an subprocess.CalledProcessError if there is an error (failure exit code).
def runExternalArgs(parameters:list[any], verifySuccess:bool = True) -> str :
    result:CompletedProcess = subprocess.run(parameters, capture_output=True, text=True)

    if _logger.isEnabledFor(logging.DEBUG) :
        if result.stdout is not None and len(result.stdout) > 0 :
            _logger.debug(f"stdout: {result.stdout}")
        if result.stderr is not None and len(result.stderr) > 0 :
            _logger.debug(f"stderr: {result.stderr}")

    if verifySuccess :
        result.check_returncode() # checks the return code and exits if failure indicated.

    return result.stdout