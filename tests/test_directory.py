import pytest
import os
from nanodoc import expand_directory

def test_expand_directory(tmpdir):
    # Create directory structure
    dir_path = tmpdir.mkdir("test_dir")
    nested_dir = dir_path.mkdir("nested_dir")
    test_file_txt = dir_path.join("test_file.txt")
    test_file_txt.write("test")
    test_file_md = dir_path.join("test_file.md")
    test_file_md.write("test")
    test_file_other = dir_path.join("test_file.other")
    test_file_other.write("test")
    nested_file_txt = nested_dir.join("nested_file.txt")
    nested_file_txt.write("test")

    # Call expand_directory
    expanded_files = expand_directory(str(dir_path))

    # Assert that only .txt and .md files are included, and nested files are included
    assert str(test_file_txt) in expanded_files
    assert str(test_file_md) in expanded_files
    assert str(nested_file_txt) in expanded_files
    assert str(test_file_other) not in expanded_files

def test_expand_directory_empty(tmpdir):
    dir_path = tmpdir.mkdir("empty_dir")
    expanded_files = expand_directory(str(dir_path))
    assert expanded_files == []
