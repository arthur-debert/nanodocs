import pytest
import os
from nanodoc.nanodoc import create_header, LINE_WIDTH, process_file, process_all, expand_directory, expand_bundles, expand_args, verify_path, init
import sys
from io import StringIO

def test_init_no_files_errors(tmpdir):
    # Create a temporary directory
    empty_dir = tmpdir.mkdir("empty")

    # Call init with the empty directory
    result = init([str(empty_dir)])

    # Assert that an error message is returned without checking the exact text
    assert result.startswith("Error:")
    assert "files found" in result

def test_init_one_file_no_line_numbers(tmpdir):
    # Create a test file
    test_file = tmpdir.join("test_file.txt")
    test_file.write("Line 1\nLine 2")

    # Call init with the test file
    result = init([str(test_file)])

    # Assert that the file content is printed without line numbers
    assert "Line 1" in result
    assert "Line 2" in result
    assert "1:" not in result
    assert "2:" not in result

def test_init_one_file_file_line_numbers(tmpdir):
    # Create a test file
    test_file = tmpdir.join("test_file.txt")
    test_file.write("Line 1\nLine 2")

    # Call init with the test file and file line numbers
    result = init([str(test_file)], line_number_mode="file")

    # Assert that the file content is printed with file line numbers
    assert "1: Line 1" in result
    assert "2: Line 2" in result

def test_init_one_file_all_line_numbers(tmpdir):
    # Create a test file
    test_file = tmpdir.join("test_file.txt")
    test_file.write("Line 1\nLine 2")

    # Call init with the test file and all line numbers
    result = init([str(test_file)], line_number_mode="all")

    # Assert that the file content is printed with all line numbers
    assert "1: Line 1" in result
    assert "2: Line 2" in result

def test_init_toc(tmpdir):
    # Create a test file
    test_file = tmpdir.join("test_file.txt")
    test_file.write("Line 1\nLine 2")

    # Call init with the test file and TOC generation
    result = init([str(test_file)], generate_toc=True)

    # Assert that the TOC is generated and the file content is printed
    assert create_header("TOC") in result
    assert "test_file.txt" in result
    assert "Line 1" in result
    assert "Line 2" in result

@pytest.mark.skip(reason="Not implemented")
def test_init_bundle_error(tmpdir):
    # Create a test bundle file with non-existent paths
    bundle_file = tmpdir.join("test_bundle.txt")
    bundle_file.write("/nonexistent/file1.txt")

    # Call init with the bundle file
    result = init([str(bundle_file)])
    
    # Assert that an error message is returned
    assert "Error:" in result
    assert "bundle" in result