"""
Unit tests for the validateConfiguration method of the Configuration class.

These tests use example JSON files from the examples directory as configuration sources.
They check that validateConfiguration prints the correct output for valid and invalid configurations.
All tests are self-contained and suitable for CI environments.
"""
import os
import pytest
from dependency_resolver.resolver.configuration.configuration import Configuration

# Directory containing test JSON example files
EXAMPLES_DIR = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "../../resolver/examples")
)

def test_validateConfiguration_valid_json(capsys):
    """
    Test that validateConfiguration prints 'Valid' for a valid configuration.
    """
    valid_path = os.path.join(EXAMPLES_DIR, "valid.json")
    config = Configuration(valid_path)
    config.validateConfiguration()
    captured = capsys.readouterr()
    assert "Valid" in captured.out
    assert os.path.basename(valid_path) in captured.out

   
def test_validate_missing_project_name(capsys):
    """
    Test that validateConfiguration prints 'Invalid' for an invalid configuration.
    """
    invalid_path = os.path.join(EXAMPLES_DIR, "missing_project_name.json")
    config = Configuration(invalid_path)
    config.validateConfiguration()
    captured = capsys.readouterr()
    assert "Invalid" in captured.out
    assert os.path.basename(invalid_path) in captured.out


def test_validate_missing_dependency_name(capsys):
    """
    Test that validateConfiguration prints 'Invalid' for an invalid configuration.
    """
    invalid_path = os.path.join(EXAMPLES_DIR, "missing_dependency_name.json")
    config = Configuration(invalid_path)
    config.validateConfiguration()
    captured = capsys.readouterr()
    assert "Invalid" in captured.out
    assert os.path.basename(invalid_path) in captured.out
   

def test_validate_missing_dependency_source(capsys):
    """
    Test that validateConfiguration prints 'Invalid' for an invalid configuration.
    """
    invalid_path = os.path.join(EXAMPLES_DIR, "missing_dependency_source.json")
    config = Configuration(invalid_path)
    config.validateConfiguration()
    captured = capsys.readouterr()
    assert "Invalid" in captured.out
    assert os.path.basename(invalid_path) in captured.out


def test_validate_missing_dependency_target_dir(capsys):
    """
    Test that validateConfiguration prints 'Invalid' for an invalid configuration.
    """
    invalid_path = os.path.join(EXAMPLES_DIR, "missing_dependency_target_dir.json")
    config = Configuration(invalid_path)
    config.validateConfiguration()
    captured = capsys.readouterr()
    assert "Invalid" in captured.out
    assert os.path.basename(invalid_path) in captured.out


def test_validate_missing_source_name(capsys):
    """
    Test that validateConfiguration prints 'Invalid' for an invalid configuration.
    """
    invalid_path = os.path.join(EXAMPLES_DIR, "missing_source_name.json")
    config = Configuration(invalid_path)
    config.validateConfiguration()
    captured = capsys.readouterr()
    assert "Invalid" in captured.out
    assert os.path.basename(invalid_path) in captured.out


def test_validate_missing_source_protocol(capsys):
    """
    Test that validateConfiguration prints 'Invalid' for an invalid configuration.
    """
    invalid_path = os.path.join(EXAMPLES_DIR, "missing_source_protocol.json")
    config = Configuration(invalid_path)
    config.validateConfiguration()
    captured = capsys.readouterr()
    assert "Invalid" in captured.out
    assert os.path.basename(invalid_path) in captured.out


def test_validateConfiguration_handles_missing_file(tmp_path):
    """
    Test that Configuration exits if the configuration file does not exist.
    """
    missing_path = tmp_path / "does_not_exist.json"
    with pytest.raises(SystemExit):
        Configuration(str(missing_path)).validateConfiguration()
