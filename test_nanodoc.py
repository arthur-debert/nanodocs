import pytest
import os
import subprocess
from nanodoc import create_header, LINE_WIDTH, process_file, process_all, expand_directory, expand_bundles, verify_path, init, VERSION

# Import all test files
from tests import test_header, test_directory, test_bundles, test_line_numbers, test_toc, test_init
from tests import test_init_multiple_paths

def test_version():
    result = subprocess.run(["python", "nanodoc.py", "--version"], capture_output=True, text=True)
    assert result.returncode == 0
    assert f"nanodoc.py {VERSION}" in result.stdout

