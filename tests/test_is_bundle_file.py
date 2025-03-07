import pytest
import os
from nanodoc import is_bundle_file

def test_is_bundle_file_with_valid_paths(tmpdir):
    # Create a test file that will be referenced in the bundle
    test_file = tmpdir.join("referenced_file.txt")
    test_file.write("Some content")
    
    # Create a bundle file that references the test file
    bundle_file = tmpdir.join("valid_bundle.txt")
    bundle_file.write(str(test_file) + "\n/another/path.txt")
    
    # Test that the bundle file is recognized as a bundle
    assert is_bundle_file(str(bundle_file)) == True

def test_is_bundle_file_with_content_file(tmpdir):
    # Create a regular content file
    content_file = tmpdir.join("content_file.txt")
    content_file.write("Line 1\nLine 2\nThis is not a file path")
    
    # Test that the content file is not recognized as a bundle
    assert is_bundle_file(str(content_file)) == False

def test_is_bundle_file_with_empty_file(tmpdir):
    # Create an empty file
    empty_file = tmpdir.join("empty_file.txt")
    empty_file.write("")
    
    # Test that an empty file is not recognized as a bundle
    assert is_bundle_file(str(empty_file)) == False

def test_is_bundle_file_with_invalid_paths(tmpdir):
    # Create a file with invalid paths
    invalid_bundle = tmpdir.join("invalid_bundle.txt")
    invalid_bundle.write("/nonexistent/file1.txt\n/another/nonexistent/file2.txt")
    
    # Test that a file with only invalid paths is not recognized as a bundle
    assert is_bundle_file(str(invalid_bundle)) == False

def test_is_bundle_file_with_mixed_content(tmpdir):
    # Create a test file that will be referenced in the bundle
    test_file = tmpdir.join("referenced_file.txt")
    test_file.write("Some content")
    
    # Create a file with a mix of valid path and regular content
    mixed_file = tmpdir.join("mixed_file.txt")
    mixed_file.write(str(test_file) + "\nThis is just some text\nNot a file path")
    
    # Test that a file with mixed content is recognized as a bundle
    # since the first valid line is a file path
    assert is_bundle_file(str(mixed_file)) == True

def test_is_bundle_file_with_nonexistent_file():
    # Test with a non-existent file
    assert is_bundle_file("/nonexistent/path/to/file.txt") == False

def test_is_bundle_file_with_directory(tmpdir):
    # Create a directory
    dir_path = tmpdir.mkdir("test_dir")
    
    # Test that a directory is not recognized as a bundle
    assert is_bundle_file(str(dir_path)) == False
