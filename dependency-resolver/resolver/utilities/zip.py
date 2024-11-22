import logging
import zipfile
from zipfile import ZipFile
from . import file
from .errors import ZipError

_logger = logging.getLogger(__name__)

def unzip(zipPath:str, targetDir:str) -> bool :
    """
    Unzip (extracts all from) the specified zip file to the specified directory.

    Parameters:
        zipPath - the path to the zip file to extract.
        targetDir - the directory to zip into.

    Raises:
        ZipError if an error is encountered.
    """
    _logger.debug(f"Unzipping {zipPath} -> {targetDir}")
    _validateZipPath(zipPath)
    _validateTargetDirectory(targetDir)
    file.mkdir(targetDir, mode=0o744) # make target directory in case it doesn't exist.
    try :
        with _createZipFile(zipPath) as zip :
            zip.extractall(targetDir)
    except Exception as exc :
        _logger.error(f"Unable to extract zip file at {zipPath}", exc_info=True)
        raise ZipError(f"Unable to extract zip file at {zipPath}") from exc


def isValidZipPath(zipPath:str) -> bool :
    """Returns true if the file at the specified path is a zip file."""
    try :
        _validateZipPath(zipPath)
        return True
    except ZipError :
        return False


# Checks to see if the path is actually a zip file.
def _validateZipPath(zipPath:str) :
    if zipPath :
        if file.exists(zipPath) :
            if not zipfile.is_zipfile(zipPath) :
                _logger.error(f"{zipPath} is not a zip file.")
                raise ZipError(f"{zipPath} is not a zip file.")
        else :
            _logger.error(f"Specified zip file {zipPath} does not exist.")
            raise ZipError(f"Specified zip file {zipPath} does not exist.")
    else :
        _logger.error("Path to the zip file has not been specified.")
        raise ZipError("Path to the zip file has not been specified.")


# Checks to see it the target directory is valid
def _validateTargetDirectory(targetDir:str) :
    if targetDir :
        if file.exists(targetDir) and not file.isDir(targetDir) :
            _logger.error(f"The target directory {targetDir} is actually a file (at least its not a directory).")
            raise ZipError(f"The target directory {targetDir} already exists but is a file.")    
    else :
        _logger.error("The target directory has not been specified.")
        raise ZipError("The target directory has not been specified.")


def _createZipFile(path:str, mode:str = 'r') -> ZipFile :
    return ZipFile(path, mode=mode)