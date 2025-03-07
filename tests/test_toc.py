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
    assert create_header("TOC") in output
    assert "test_file1.txt" in output
    assert "test_file2.txt" in output
    assert output.startswith(create_header("TOC"))

