import pytest
import os
from nanodoc import create_header, LINE_WIDTH, process_all

def test_process_all_toc_generation(tmpdir):
    test_file1 = tmpdir.join("test_file1.txt")
    test_file1.write("Line 1")
    test_file2 = tmpdir.join("test_file2.txt")
    test_file2.write("Line 2")
    file_paths = [str(test_file1), str(test_file2)]
    output = process_all(file_paths, None, True)
    assert "TOC" in output
    assert "test_file1.txt" in output
    assert "test_file2.txt" in output
    assert output.startswith("\nTOC\n\n")

def test_process_all_with_no_header(tmpdir):
    test_file1 = tmpdir.join("test_file1.txt")
    test_file1.write("Line 1")
    test_file2 = tmpdir.join("test_file2.txt")
    test_file2.write("Line 2")
    file_paths = [str(test_file1), str(test_file2)]
    
    output = process_all(file_paths, None, False, show_header=False)
    
    assert "Line 1" in output
    assert "Line 2" in output
    assert "test_file1.txt" not in output
    assert "test_file2.txt" not in output

def test_process_all_with_header_sequence(tmpdir):
    test_file1 = tmpdir.join("test_file1.txt")
    test_file1.write("Line 1")
    test_file2 = tmpdir.join("test_file2.txt")
    test_file2.write("Line 2")
    file_paths = [str(test_file1), str(test_file2)]
    
    # Test numerical sequence
    output = process_all(file_paths, None, False, sequence="numerical")
    assert "1. test_file1.txt" in output
    assert "2. test_file2.txt" in output
    
    # Test letter sequence
    output = process_all(file_paths, None, False, sequence="letter")
    assert "a. test_file1.txt" in output
    assert "b. test_file2.txt" in output

def test_process_all_with_header_style(tmpdir):
    test_file1 = tmpdir.join("test_file1.txt")
    test_file1.write("Line 1")
    file_paths = [str(test_file1)]
    
    output = process_all(file_paths, None, False, style="nice")
    assert "Test File1 (test_file1.txt)" in output

