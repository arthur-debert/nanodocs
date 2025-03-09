"""Fixtures for tests."""

import os

import pytest


def get_project_root():
    """Get the absolute path to the project root directory."""
    # The project root is three directories up from this file
    return os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


def get_path_from_root(relative_path):
    """Get the absolute path from a path relative to the project root."""
    return os.path.join(get_project_root(), relative_path)


@pytest.fixture
def project_paths():
    """Fixture to get paths relative to the project root."""
    return ProjectPaths()


class ProjectPaths:
    """Helper class to get paths relative to the project root."""

    def __init__(self):
        self.root = get_project_root()

    def get(self, relative_path):
        """Get the absolute path from a path relative to the project root."""
        return os.path.join(self.root, relative_path)

    @property
    def samples_dir(self):
        """Get the absolute path to the samples directory."""
        return self.get("samples")

    @property
    def nanodoc_script(self):
        """Get the absolute path to the nanodoc script."""
        return self.get("nanodoc/nanodoc.py")

    def sample_file(self, filename):
        """Get the absolute path to a sample file."""
        return os.path.join(self.samples_dir, filename)


@pytest.fixture
def project_file(project_paths):
    """
    Fixture to get a file path relative to the project root.

    This fixture can be parametrized with a file path relative to the project root.
    """

    def _get_file(relative_path):
        return project_paths.get(relative_path)

    return _get_file


@pytest.fixture
def sample_file(project_paths):
    """
    Fixture to get a sample file path.

    This fixture can be parametrized with a sample file name.
    """

    def _get_sample_file(filename):
        return project_paths.sample_file(filename)

    return _get_sample_file
