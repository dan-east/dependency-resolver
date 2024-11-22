import logging
import shutil
import os
import glob
from pathlib import Path
from . import helpers, time

_logger = logging.getLogger(__name__)

# Create a directory (and parent structure if required) if it doesn't already exist
def mkdir(dir:str, parents:bool = True, exist_ok:bool = True, mode:int = 511, user:str = None, group:str = None) :
    if helpers.hasValue(dir) :
        Path(dir).mkdir(mode=mode, parents=parents, exist_ok=exist_ok)
        
        if user is not None and group is not None :
            chown(dir, user, group)
    else :
        _logger.warning("Directory not specified - cannot create it.")


# Does the specified path exist?
def exists(path:str) -> bool :
    return helpers.hasValue(path) and Path(path).exists()


# Does the specified path exist and is it a directory.
def isDir(path:str) -> bool :
    return os.path.isdir(path)


# Does the specified path exist and it it a directory.
def isFile(path:str) -> bool :
    return os.path.isfile(path)


# Make sure the target path exists. Will exit if the path doesn't exist.
def ensurePathExists(path:str) -> bool :
    if helpers.isEmpty(path) or not exists(path) :
        _logger.error(f"{path} does not exist. Exiting.")
        exit(1)
    return True


# Build up a path. Seperators are applied as appropriate.
# Ignores any 'None' paths.
def buildPath(*paths:str) -> str:
    result:str = None
    for path in paths :
        if path : 
            if result :
                # Remove leading seperator from path, as a leading seperator causes the thing you are joining to (result in this case) to be discarded.
                result = os.path.join(result, path.lstrip(os.path.sep)) 
            else :
                result = f"{path}"

    return result


# Strip of the last part of the path, including any seperators
def returnLastPartOfPath(fullpath:str) -> str :
    return os.path.basename(os.path.normpath(fullpath))


def getParentDirectory(fullPath:str) -> str :
    """
    Returns the owning directory of the given path
    """
    return os.path.dirname(fullPath)

# Copy files or directories.
#  sourceDirectotyContentsOnly can be used to only copy the contents of a source directory (has no effect is source is a file).
#  Returns: the path to the newly copied file / destination directory. None indicates an error. 
#  Raises exceptions with list of errors if the system copy fails.
def copy(source:str, dest:str, sourceDirectoryContentsOnly:bool=False) -> str :
    if Path(source).exists() :
        if Path(source).is_dir() :
            if sourceDirectoryContentsOnly :
                return copyContents(source, dest)
            else :
                _logger.debug("Copying directory from " + source + " -> " + dest)
                return shutil.copytree(source, dest, dirs_exist_ok=True)
        else :
            _logger.debug("Copying " + source + " -> " + dest)
            return shutil.copy2(source, dest)
    else :
        _logger.error(f"Can't copy - {source} does not exist")


# Copy the contents of a directory to a destination
# Returns the destination directory, if successful.
def copyContents(dir:str, dest:str) -> str:
    if os.path.exists(dest) and os.path.isdir(dest) :
        if os.path.exists(dir) and os.path.isdir(dir) :
            _logger.error("Copying contents of %s -> %s", dir, dest)
            for name in os.listdir(dir):
                copy(os.path.join(dir, name), dest, False) # copy files and complete directories
            return dest
        else :
            _logger.error("Cannot copy contents of %s as it does not exist", dir)
    else :
        _logger.error("Cannot copy contents of %s to %s as the destination doesn't exist or is not a directory.", dir, dest)


# Change the ownership of a file or directory (but not the contents of the directory).
#  Parameters:
#   path - a path, or Path-like object
#   user - the user group (name, or uid)
#   group - the group (name or group id)
def chown(path:str, user:str=None, group:str=None) :
    _logger.debug("chown %s:%s %s", user, group, path)
    shutil.chown(path, user, group)


# Change the ownership of a directory and its contents.
#  Parameters:
#   path - a path, or Path-like object
#   user - the user group (name, or uid)
#   group - the group (name or group id)
def chown_recursive(path:str, user:str, group:str) :
    _logger.debug("chown -R %s:%s %s...", user, group, path)

    # Change ownership for the top-level folder
    chown(path, user, group)

    for root, dirs, files in os.walk(path):
        # chown all sub-directories
        for dir in dirs:
            chown(os.path.join(root, dir), user, group)

        # chown all files
        for file in files:
            chown(os.path.join(root, file), user, group)

    _logger.debug("...chowned %s", path)


# Change the permissions of a file or directory (but not the contents of the directory).
#  Parameters:
#   path - a path, or Path-like object
#   permissions - an octant (e.g. 0o750)
def chmod(path:str, permissions:str) :
    _logger.debug("chmod %s %s", permissions, path)
    os.chmod(path, permissions)


# Change the permissions of a directory and its contents.
#  Parameters:
#   path - a path, or Path-like object
#   permissions - an octant (e.g. 0o750)
def chmod_recursive(path:str, permissions:str) :
    _logger.debug("chmod -R %s %s...", permissions, path)

    # Change permissions for the top-level folder
    chmod(path, permissions)

    for root, dirs, files in os.walk(path):
        # chmod all sub-directories
        for dir in dirs:
            chmod(os.path.join(root, dir), permissions)

        # chmod all files
        for file in files:
            chmod(os.path.join(root, file), permissions)

    _logger.debug("...chmodded %s", path)


# Deletes the given target path.
#   If the path points to a symbolic link then it is unlinked
def delete(path:str) :
    toDelete = Path(path)
    if toDelete.exists() :
        if toDelete.is_dir() and not toDelete.is_symlink() :
            _logger.debug("rm -r %s", toDelete.absolute())
            deleteContents(toDelete.absolute())
            toDelete.rmdir()
        else :
            _logger.debug("rm %s", toDelete.absolute())
            toDelete.unlink()
    else :
        _logger.debug("Not deleting non-existant path %s", toDelete.absolute())


# Deletes the contents of a directory (not the directory itself)
def deleteContents(dir:str) :
    toDelete = Path(dir)
    if toDelete.exists() :
        for name in os.listdir(dir):
            delete(os.path.join(dir, name))


# empties the contents of a file.
def emptyFileContents(filePath:str) :
    if helpers.isEmpty(filePath) :
        _logger.error("Cannot empty contents of 'None' filePath")
    path = Path(filePath)
    if path.exists() and path.is_file() :
        path.open("w").close()


# Creates an empty file at the specifed path
def createFile(filePath:str, mode:int = 438) :
    Path(filePath).touch(mode=mode, exist_ok=True)


# Returns the path of the latest file in the specified directory or None if directory doesn't exist or is empty
# Parameters:
#   dir - the target directory
#   filePattern - a pathname pattern, for example *.txt. Defaults to *.
def findNewestFileInDirectory(dir:str, filePattern:str = "*") -> str:
    newestFile:str = None
    if exists(dir) :
        list_of_files = glob.iglob(os.path.join(dir, filePattern))
        newestFile = max(list_of_files, default=None, key=os.path.getmtime)
    return newestFile


# How old is the given file.
def howOldIsFile(path:str) -> time.timedelta :
    age:time.timedelta = None
    if path is not None and exists(path) :
        age = time.howOld(os.path.getmtime(path))
    else :
        _logger.warning(f"Path: {path} does not exist, cannot determine age.")
    
    return age


# Delete files (not directories) from a given directory that are older than the specified delta
# Parameters
#   dir - the directory to inspect
#   delta - the maximum age of the file
#   recursive - trues will find files in subdirectories
def removeFiles(dir:str, delta:time.timedelta, recursive:bool = False) :
    if exists(dir) :
        contents = glob.iglob(os.path.join(dir, "*"), recursive=recursive)
        for item in contents :
            if os.path.isfile(item) and howOldIsFile(item) > delta :
                delete(item)


# Read the contents of a file.
#  Really should only used for small file as it reads in the entire contents.
def readFile(path:str, encoding:str = "utf-8") -> str :
    contents:str = None
    if exists(path) :
        with open(path, encoding=encoding) as file:
            contents = file.read()
        
    return contents
