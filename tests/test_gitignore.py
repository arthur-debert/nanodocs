"""Tests for gitignore functionality in file expansion."""

import os
import tempfile
from pathlib import Path

from nanodoc.files import expand_directory, get_gitignore_spec


def test_get_gitignore_spec():
    """Test getting a pathspec from a .gitignore file."""
    with tempfile.TemporaryDirectory() as temp_dir:
        # No .gitignore file
        assert get_gitignore_spec(temp_dir) is None

        # Create a .gitignore file
        gitignore_path = os.path.join(temp_dir, ".gitignore")
        with open(gitignore_path, "w") as f:
            f.write("*.log\n")
            f.write("node_modules/\n")
            f.write("build/\n")

        # Get the spec
        spec = get_gitignore_spec(temp_dir)
        assert spec is not None

        # Test matching
        assert spec.match_file("test.log")
        assert spec.match_file("node_modules/package.json")
        assert spec.match_file("build/output.txt")
        assert not spec.match_file("test.txt")
        assert not spec.match_file("src/main.js")


def test_expand_directory_with_gitignore():
    """Test that expand_directory respects .gitignore patterns."""
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create a directory structure
        temp_path = Path(temp_dir)

        # Create .gitignore
        with open(temp_path / ".gitignore", "w") as f:
            f.write("ignored.txt\n")
            f.write("ignored_dir/\n")

        # Create files
        (temp_path / "file1.txt").write_text("content")
        (temp_path / "file2.md").write_text("content")
        (temp_path / "ignored.txt").write_text("should be ignored")

        # Create directories with files
        ignored_dir = temp_path / "ignored_dir"
        ignored_dir.mkdir()
        (ignored_dir / "ignored_file.txt").write_text("should be ignored")

        normal_dir = temp_path / "normal_dir"
        normal_dir.mkdir()
        (normal_dir / "normal_file.txt").write_text("should be included")

        # Expand the directory
        files = expand_directory(temp_dir)

        # Check results
        file_paths = [os.path.basename(f) for f in files]
        assert "file1.txt" in file_paths
        assert "file2.md" in file_paths
        assert "normal_file.txt" in file_paths
        assert "ignored.txt" not in file_paths
        assert "ignored_file.txt" not in file_paths
