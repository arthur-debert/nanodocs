import subprocess


def test_help(project_paths):
    """Test that the help command works."""
    result = subprocess.run(
        ["python", project_paths.nanodoc_script, "help"], capture_output=True, text=True
    )
    assert result.returncode == 0
    assert "# nanodoc" in result.stdout


def test_no_args(project_paths):
    """Test that running nanodoc with no arguments shows usage information."""
    result = subprocess.run(
        ["python", project_paths.nanodoc_script], capture_output=True, text=True
    )
    assert result.returncode == 0
    assert "usage: nanodoc" in result.stdout
    assert "# nanodoc" not in result.stdout
