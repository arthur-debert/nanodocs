import pytest
import os
from nanodoc import create_header, LINE_WIDTH, process_file

def test_create_header_centered():
    text = "Test Header"
    header = create_header(text)
    assert text in header
    assert len(header) == LINE_WIDTH

def test_create_header_custom_char():
    text = "Test Header"
    char = "*"
    header = create_header(text, char)
    assert header.startswith(char)
    assert header.endswith(char)
    assert len(header) == LINE_WIDTH

def test_create_header_empty_text():
    text = ""
    header = create_header(text)
    assert len(header) == LINE_WIDTH

def test_create_header_long_text():
    text = "This is a very long header that exceeds the maximum line width"
    header = create_header(text)
    assert len(header) == LINE_WIDTH

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
    output, _ = process_file("non_existent_file.txt", None, 0)
    assert "Error: File not found" in output
