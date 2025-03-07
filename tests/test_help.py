import pytest
import os
import subprocess
from nanodoc import create_header, LINE_WIDTH, process_file, process_all, expand_directory, expand_bundles, verify_path, init, VERSION

def test_help():
    result = subprocess.run(["python", "nanodoc.py", "help"], capture_output=True, text=True)
    assert result.returncode == 0
    assert "# nanodocs" in result.stdout

def test_no_args():
    result = subprocess.run(["python", "nanodoc.py"], capture_output=True, text=True)
    assert result.returncode == 0
    assert "usage: nanodoc.py" in result.stdout
    assert "# nanodocs" not in result.stdout
