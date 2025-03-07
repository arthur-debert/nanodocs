import pytest
from nanodoc import create_header, LINE_WIDTH

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
