import pytest
import os
import subprocess
import sys
from nanodoc import create_header, LINE_WIDTH, process_file, process_all, expand_directory, expand_bundles, verify_path, init, VERSION

# Import all test files
from tests import test_header, test_directory, test_bundles, test_line_numbers, test_toc, test_init
from tests import test_init_multiple_paths

def test_version():
    result = subprocess.run([sys.executable, "-m", "nanodoc", "--version"], capture_output=True, text=True)
    assert result.returncode == 0
    assert VERSION in result.stdout

def test_main_exception(tmpdir, monkeypatch):
    # Create a dummy file
    test_file = tmpdir.join("test_file.txt")
    test_file.write("test")

    # Mock the to_stds function to raise an exception
    def mock_to_stds(*args, **kwargs):
        raise Exception("Test exception")

    monkeypatch.setattr("nanodoc.to_stds", mock_to_stds)

    # Run nanodoc with the dummy file
    result = subprocess.run([sys.executable, "-m", "nanodoc", str(test_file)], capture_output=True, text=True)

    # Assert that the return code is 1 and the error message is printed
    assert result.returncode == 1
    assert "An error occurred: Test exception" in result.stderr

