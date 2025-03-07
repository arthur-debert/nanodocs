import pytest
import os
from nanodoc import create_header, LINE_WIDTH, process_file

def test_process_file_no_line_numbers(tmpdir):
    test_file = tmpdir.join("test_file.txt")
    test_file.write("Line 1\nLine 2")
    file_path = str(test_file)
    output, _ = process_file(file_path, None, 0)
    assert "Line 1" in output
    assert "Line 2" in output
    assert "1:" not in output
    assert "2:" not in output

def test_process_file_with_line_numbers_all(tmpdir):
    test_file = tmpdir.join("test_file.txt")
    test_file.write("Line 1\nLine 2")
    file_path = str(test_file)
    output, _ = process_file(file_path, "all", 0)
    assert "1: Line 1" in output
    assert "2: Line 2" in output

def test_process_file_with_line_numbers_file(tmpdir):
    test_file = tmpdir.join("test_file.txt")
    test_file.write("Line 1\nLine 2")
    file_path = str(test_file)
    output, _ = process_file(file_path, "file", 0)
    assert "1: Line 1" in output
    assert "2: Line 2" in output

def test_process_file_not_found():
    file_path = "nonexistent_file.txt"
    output, _ = process_file(file_path, None, 0)
    assert "Error: File not found" in output

def test_process_file_header_assignment(tmpdir):
    test_file = tmpdir.join("test_file.txt")
    test_file.write("test")
    file_path = str(test_file)
    output, _ = process_file(file_path, None, 0)
    header = create_header(os.path.basename(file_path)) + "\n"
    assert output.startswith(header)
