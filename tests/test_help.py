import os
import subprocess

# Get the parent directory of the current module
MODULE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Path to the nanodoc script
NANODOC_SCRIPT = os.path.join(MODULE_DIR, "nanodoc", "nanodoc.py")


def test_help():
    result = subprocess.run(
        ["python", NANODOC_SCRIPT, "help"], capture_output=True, text=True
    )
    assert result.returncode == 0
    assert "# nanodoc" in result.stdout


def test_no_args():
    result = subprocess.run(["python", NANODOC_SCRIPT], capture_output=True, text=True)
    assert result.returncode == 0
    assert "usage: nanodoc.py" in result.stdout
    assert "# nanodoc" not in result.stdout
