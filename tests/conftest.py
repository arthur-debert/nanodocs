import logging

import pytest
from fixtures import project_paths, project_file, sample_file



@pytest.fixture
def caplog(caplog):
    """Fixture to capture log messages."""
    caplog.set_level(logging.DEBUG)
    return caplog
