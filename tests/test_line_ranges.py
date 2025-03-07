import pytest
import os
from nanodoc.nanodoc import get_file_content, verify_path, parse_line_reference

def test_parse_line_reference_single_line():
    # Test parsing a single line reference
    result = parse_line_reference("L10")
    assert result == [(10, 10)]

def test_parse_line_reference_range():
    # Test parsing a range reference
    result = parse_line_reference("L5-10")
    assert result == [(5, 10)]

def test_parse_line_reference_multiple():
    # Test parsing multiple references
    result = parse_line_reference("L5,L10-15,L20")
    assert result == [(5, 5), (10, 15), (20, 20)]

def test_parse_line_reference_invalid():
    # Test parsing invalid references
    with pytest.raises(ValueError):
        parse_line_reference("L")
    
    with pytest.raises(ValueError):
        parse_line_reference("L-5")
    
    with pytest.raises(ValueError):
        parse_line_reference("L5-")
    
    with pytest.raises(ValueError):
        parse_line_reference("L5-3")  # End less than start

def test_get_file_content_entire_file(tmpdir):
    # Test getting the entire file content
    test_file = tmpdir.join("test_file.txt")
    test_file.write("Line 1\nLine 2\nLine 3\nLine 4\nLine 5")
    file_path = str(test_file)
    
    content = get_file_content(file_path)
    assert content == "Line 1\nLine 2\nLine 3\nLine 4\nLine 5"

def test_get_file_content_single_line(tmpdir):
    # Test getting a single line
    test_file = tmpdir.join("test_file.txt")
    test_file.write("Line 1\nLine 2\nLine 3\nLine 4\nLine 5")
    file_path = str(test_file)
    
    content = get_file_content(file_path, line=3)
    assert content == "Line 3"

def test_get_file_content_line_range(tmpdir):
    # Test getting a range of lines
    test_file = tmpdir.join("test_file.txt")
    test_file.write("Line 1\nLine 2\nLine 3\nLine 4\nLine 5")
    file_path = str(test_file)
    
    content = get_file_content(file_path, start=2, end=4)
    assert content == "Line 2\nLine 3\nLine 4"

def test_get_file_content_multiple_parts(tmpdir):
    # Test getting multiple parts
    test_file = tmpdir.join("test_file.txt")
    test_file.write("Line 1\nLine 2\nLine 3\nLine 4\nLine 5")
    file_path = str(test_file)
    
    content = get_file_content(file_path, parts=[(1, 1), (3, 4)])
    assert content == "Line 1\nLine 3\nLine 4"

def test_get_file_content_line_out_of_range(tmpdir):
    # Test getting a line that is out of range
    test_file = tmpdir.join("test_file.txt")
    test_file.write("Line 1\nLine 2\nLine 3")
    file_path = str(test_file)
    
    with pytest.raises(ValueError) as excinfo:
        get_file_content(file_path, line=10)
    assert "Line reference out of range" in str(excinfo.value)

def test_verify_path_with_line_reference_valid(tmpdir):
    # Test verifying a path with a valid line reference
    test_file = tmpdir.join("test_file.txt")
    test_file.write("Line 1\nLine 2\nLine 3\nLine 4\nLine 5")
    file_path = str(test_file)
    
    # Valid single line
    result = verify_path(f"{file_path}:L3")
    assert result == file_path
    
    # Valid range
    result = verify_path(f"{file_path}:L2-4")
    assert result == file_path
    
    # Valid multiple
    result = verify_path(f"{file_path}:L1,L3-4,L5")
    assert result == file_path

def test_verify_path_with_line_reference_invalid(tmpdir):
    # Test verifying a path with an invalid line reference
    test_file = tmpdir.join("test_file.txt")
    test_file.write("Line 1\nLine 2\nLine 3")
    file_path = str(test_file)
    
    # Invalid line number (too high)
    with pytest.raises(ValueError) as excinfo:
        verify_path(f"{file_path}:L10")
    assert "Line reference out of range" in str(excinfo.value)
    
    # Invalid range (end too high)
    with pytest.raises(ValueError) as excinfo:
        verify_path(f"{file_path}:L2-10")
    assert "Line reference out of range" in str(excinfo.value)
    
    # Invalid multiple (one invalid)
    with pytest.raises(ValueError) as excinfo:
        verify_path(f"{file_path}:L1,L10")
    assert "Line reference out of range" in str(excinfo.value)