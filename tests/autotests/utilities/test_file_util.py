"""
Unit tests for dependency_resolver.resolver.utilities.file_util.

These tests cover boundary conditions, use mocks where appropriate
"""

import os
import tempfile
import shutil
import stat
import pytest
from unittest import mock

import dependency_resolver.resolver.utilities.file_util as file_util

@pytest.fixture
def temp_dir():
    """Fixture to create and clean up a temporary directory."""
    d = tempfile.mkdtemp()
    yield d
    shutil.rmtree(d, ignore_errors=True)

@pytest.fixture
def temp_file():
    """Fixture to create and clean up a temporary file."""
    fd, path = tempfile.mkstemp()
    os.close(fd)
    yield path
    if os.path.exists(path):
        os.remove(path)

def test_mkdir_creates_directory(temp_dir):
    """Test that mkdir creates a new directory."""
    new_dir = os.path.join(temp_dir, "subdir")
    with mock.patch("dependency_resolver.resolver.utilities.file_util.helpers.hasValue", return_value=True):
        file_util.mkdir(new_dir)
    assert os.path.isdir(new_dir)

def test_mkdir_with_user_group_calls_chown(temp_dir):
    """Test that mkdir calls chown when user and group are provided."""
    new_dir = os.path.join(temp_dir, "subdir2")
    with mock.patch("dependency_resolver.resolver.utilities.file_util.helpers.hasValue", return_value=True), \
         mock.patch("dependency_resolver.resolver.utilities.file_util.chown") as mock_chown:
        file_util.mkdir(new_dir, user="user", group="group")
        mock_chown.assert_called_once_with(new_dir, "user", "group")

def test_mkdir_no_dir_logs_warning(caplog):
    """Test that mkdir logs a warning if no directory is specified."""
    with mock.patch("dependency_resolver.resolver.utilities.file_util.helpers.hasValue", return_value=False):
        file_util.mkdir(None) # type: ignore - its a test for no directory
    assert "Directory not specified" in caplog.text

def test_exists_true_and_false(temp_file):
    """Test exists returns True for existing path and False otherwise."""
    with mock.patch("dependency_resolver.resolver.utilities.file_util.helpers.hasValue", return_value=True):
        assert file_util.exists(temp_file)
    with mock.patch("dependency_resolver.resolver.utilities.file_util.helpers.hasValue", return_value=False):
        assert not file_util.exists(temp_file)

def test_isDir_and_isFile(temp_dir, temp_file):
    """Test isDir and isFile for both files and directories."""
    assert file_util.isDir(temp_dir)
    assert not file_util.isDir(temp_file)
    assert file_util.isFile(temp_file)
    assert not file_util.isFile(temp_dir)

def test_ensurePathExists_exists(temp_file):
    """Test ensurePathExists returns True if the path exists."""
    with mock.patch("dependency_resolver.resolver.utilities.file_util.helpers.isEmpty", return_value=False):
        assert file_util.ensurePathExists(temp_file)

def test_ensurePathExists_not_exists_exits():
    """Test ensurePathExists exits if the path does not exist."""
    with mock.patch("dependency_resolver.resolver.utilities.file_util.helpers.isEmpty", return_value=False), \
         mock.patch("dependency_resolver.resolver.utilities.file_util.exists", return_value=False):
        with pytest.raises(SystemExit):
            file_util.ensurePathExists("not_a_real_path")

def test_buildPath_various_cases():
    """Test buildPath with various combinations of arguments."""
    assert file_util.buildPath("a", "b", "c") == os.path.join("a", "b", "c")
    assert file_util.buildPath(None, "b", None, "c") == os.path.join("b", "c")  # type: ignore - used to test None handling
    assert file_util.buildPath() == ""
    assert file_util.buildPath("/a", "b") == os.path.join("/a", "b")

def test_returnLastPartOfPath_and_getParentDirectory():
    """Test returnLastPartOfPath and getParentDirectory functions."""
    path = "/tmp/foo/bar.txt"
    assert file_util.returnLastPartOfPath(path) == "bar.txt"
    assert file_util.getParentDirectory(path) == "/tmp/foo"

def test_getUserDirectory():
    """Test getUserDirectory returns the user's home directory."""
    assert os.path.expanduser("~") in file_util.getUserDirectory()

def test_copy_file_and_directory(temp_dir):
    """Test copying a file and a directory."""
    src_file = os.path.join(temp_dir, "file.txt")
    with open(src_file, "w") as f:
        f.write("abc")
    dest_file = os.path.join(temp_dir, "file2.txt")
    with mock.patch("dependency_resolver.resolver.utilities.file_util.helpers.hasValue", return_value=True):
        assert file_util.copy(src_file, dest_file)
        assert os.path.exists(dest_file)
    # Directory copy
    src_dir = os.path.join(temp_dir, "srcdir")
    os.mkdir(src_dir)
    dest_dir = os.path.join(temp_dir, "destdir")
    with mock.patch("dependency_resolver.resolver.utilities.file_util.helpers.hasValue", return_value=True):
        assert file_util.copy(src_dir, dest_dir)
        assert os.path.isdir(dest_dir)

def test_copy_nonexistent_source(temp_dir, caplog):
    """Test copy logs an error and returns False if the source does not exist."""
    with mock.patch("dependency_resolver.resolver.utilities.file_util.helpers.hasValue", return_value=True):
        assert not file_util.copy("not_a_real_file", os.path.join(temp_dir, "dest"))
    assert "does not exist" in caplog.text

def test_copyContents(temp_dir):
    """Test copyContents copies files from source to destination directory."""
    src = os.path.join(temp_dir, "src")
    dest = os.path.join(temp_dir, "dest")
    os.mkdir(src)
    os.mkdir(dest)
    file1 = os.path.join(src, "a.txt")
    with open(file1, "w") as f:
        f.write("hi")
    with mock.patch("dependency_resolver.resolver.utilities.file_util.copy") as mock_copy:
        file_util.copyContents(src, dest)
        mock_copy.assert_called_with(file1, dest, False)

def test_chown_and_chown_recursive(temp_dir):
    """Test chown and chown_recursive functions."""
    with mock.patch("shutil.chown") as mock_chown:
        file_util.chown(temp_dir, "user", "group")
        mock_chown.assert_called_once_with(temp_dir, "user", "group")
    # chown_recursive
    subdir = os.path.join(temp_dir, "subdir")
    os.mkdir(subdir)
    file = os.path.join(subdir, "file.txt")
    with open(file, "w") as f:
        f.write("x")
    with mock.patch("dependency_resolver.resolver.utilities.file_util.chown") as mock_chown:
        file_util.chown_recursive(temp_dir, "user", "group")
        assert mock_chown.call_count >= 2

def test_chmod_and_chmod_recursive(temp_dir):
    """Test chmod and chmod_recursive functions."""
    file = os.path.join(temp_dir, "file.txt")
    with open(file, "w") as f:
        f.write("x")
    file_util.chmod(file, 0o600)
    assert stat.S_IMODE(os.stat(file).st_mode) == 0o600
    # chmod_recursive
    with mock.patch("dependency_resolver.resolver.utilities.file_util.chmod") as mock_chmod:
        file_util.chmod_recursive(temp_dir, 0o700)
        assert mock_chmod.call_count >= 1

def test_delete_and_deleteContents(temp_dir):
    """Test delete removes files and deleteContents removes directory contents."""
    file = os.path.join(temp_dir, "file.txt")
    with open(file, "w") as f:
        f.write("x")
    file_util.delete(file)
    assert not os.path.exists(file)
    # Directory
    subdir = os.path.join(temp_dir, "subdir")
    os.mkdir(subdir)
    file2 = os.path.join(subdir, "file2.txt")
    with open(file2, "w") as f:
        f.write("y")
    file_util.deleteContents(subdir)
    assert not os.path.exists(file2)
    assert os.path.exists(subdir)

def test_emptyFileContents(temp_file):
    """Test emptyFileContents truncates the file."""
    with open(temp_file, "w") as f:
        f.write("something")
    file_util.emptyFileContents(temp_file)
    with open(temp_file) as f:
        assert f.read() == ""

def test_createFile(temp_dir):
    """Test createFile creates a new file."""
    file_path = os.path.join(temp_dir, "newfile.txt")
    file_util.createFile(file_path)
    assert os.path.exists(file_path)

def test_findNewestFileInDirectory(temp_dir):
    """Test findNewestFileInDirectory returns the newest file."""
    file1 = os.path.join(temp_dir, "a.txt")
    file2 = os.path.join(temp_dir, "b.txt")
    with open(file1, "w") as f:
        f.write("1")
    with open(file2, "w") as f:
        f.write("2")
    os.utime(file1, (1, 1))
    os.utime(file2, (2, 2))
    assert file_util.findNewestFileInDirectory(temp_dir, "*.txt") == file2

def test_howOldIsFile(temp_file):
    """Test howOldIsFile returns the correct age."""
    with mock.patch("dependency_resolver.resolver.utilities.file_util.time_util.howOld", return_value=42):
        with mock.patch("dependency_resolver.resolver.utilities.file_util.exists", return_value=True):
            assert file_util.howOldIsFile(temp_file) == 42

def test_howOldIsFile_path_none_logs_warning(caplog):
    """Test howOldIsFile logs a warning and returns None if path does not exist."""
    with mock.patch("dependency_resolver.resolver.utilities.file_util.exists", return_value=False):
        assert file_util.howOldIsFile(None) is None # type: ignore - testing None handling
    assert "does not exist" in caplog.text

def test_removeFiles(temp_dir):
    """Test removeFiles deletes files older than the threshold."""
    file1 = os.path.join(temp_dir, "a.txt")
    with open(file1, "w") as f:
        f.write("1")
    with mock.patch("dependency_resolver.resolver.utilities.file_util.howOldIsFile", return_value=100), \
         mock.patch("dependency_resolver.resolver.utilities.file_util.delete") as mock_delete, \
         mock.patch("dependency_resolver.resolver.utilities.file_util.exists", return_value=True):
        file_util.removeFiles(temp_dir, 10) # type:ignore - threshold is 10 seconds
        mock_delete.assert_called_with(file1)

def test_readFile(temp_file):
    """Test readFile returns file contents."""
    with open(temp_file, "w", encoding="utf-8") as f:
        f.write("hello world")
    with mock.patch("dependency_resolver.resolver.utilities.file_util.exists", return_value=True):
        assert file_util.readFile(temp_file) == "hello world"


def test_readListFromFile_error():
    """Test readFile raised error if file does not exist."""
    with pytest.raises(file_util.FileError):
        file_util.readListFromFile('does_not_exist.txt') 
        