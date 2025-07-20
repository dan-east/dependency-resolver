import pytest
import dependency_resolver.resolver.utilities.errors_util as errors_util

def test_project_error():
    with pytest.raises(errors_util.ProjectError):
        raise errors_util.ProjectError('project error')

def test_utility_error():
    with pytest.raises(errors_util.UtilityError):
        raise errors_util.UtilityError('utility error')
