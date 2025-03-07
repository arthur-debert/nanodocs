import pytest
import os
import subprocess
import sys
from nanodoc.nanodoc import create_header, LINE_WIDTH, process_file, process_all, expand_directory, expand_bundles, verify_path, VERSION

# Get the parent directory of the current module
MODULE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Path to the nanodoc script
NANODOC_SCRIPT = os.path.join(MODULE_DIR, "nanodoc", "nanodoc.py")

def test_help():
    result = subprocess.run(["python", NANODOC_SCRIPT, "help"], capture_output=True, text=True)
    assert result.returncode == 0
    assert "# nanodocs" in result.stdout

def test_no_args():
    result = subprocess.run(["python", NANODOC_SCRIPT], capture_output=True, text=True)
    assert result.returncode == 0
    assert "usage: nanodoc.py" in result.stdout
    assert "# nanodocs" not in result.stdout
