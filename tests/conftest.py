import logging

import pytest


@pytest.fixture
def caplog(caplog):
    """Fixture to capture log messages."""
    caplog.set_level(logging.DEBUG)
    return caplog
