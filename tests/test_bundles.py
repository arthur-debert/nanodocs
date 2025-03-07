import pytest
import os
from nanodoc.nanodoc import expand_bundles, verify_path
from nanodoc.nanodoc import BundleError

def test_expand_bundles_valid(tmpdir):
    bundle_file = tmpdir.join("test_bundle.txt")
    test_file1 = tmpdir.join("test_file1.txt")
    test_file1.write("Line 1")
    test_file2 = tmpdir.join("test_file2.txt")
    test_file2.write("Line 2")
    bundle_file.write(str(test_file1) + "\n" + str(test_file2))

    expanded_files = expand_bundles(str(bundle_file))
    assert str(test_file1) in expanded_files
    assert str(test_file2) in expanded_files

def test_expand_bundles_with_invalid_files(tmpdir):
    bundle_file = tmpdir.join("test_bundle.txt")
    test_file1 = tmpdir.join("test_file1.txt")
    test_file1.write("Line 1")
    bundle_file.write(str(test_file1) + "\n/nonexistent/file.txt")
    
    # The function should return all paths, even invalid ones
    expanded_files = expand_bundles(str(bundle_file))
    assert str(test_file1) in expanded_files
    assert "/nonexistent/file.txt" in expanded_files

def test_expand_bundles_not_found(tmpdir):
    with pytest.raises(FileNotFoundError) as excinfo:
        expand_bundles("non_existent_bundle.txt")
    assert "No such file or directory" in str(excinfo.value)

def test_verify_path_not_found():
    with pytest.raises(FileNotFoundError) as excinfo:
        verify_path("/nonexistent/file.txt")
    assert "Path does not exist" in str(excinfo.value)

def test_verify_path_is_directory(tmpdir):
    dir_path = tmpdir.mkdir("test_dir")
    with pytest.raises(IsADirectoryError) as excinfo:
        verify_path(str(dir_path))
    assert "Path is a directory" in str(excinfo.value)

def test_verify_path_valid(tmpdir):
    test_file = tmpdir.join("test_file.txt")
    test_file.write("Line 1")
    
    # Should return the path if valid
    assert verify_path(str(test_file)) == str(test_file)

def test_expand_bundles_empty(tmpdir):
    bundle_file = tmpdir.join("test_bundle.txt")
    bundle_file.write("")
    
    # Should return an empty list for an empty bundle
    expanded_files = expand_bundles(str(bundle_file))
    assert expanded_files == []
