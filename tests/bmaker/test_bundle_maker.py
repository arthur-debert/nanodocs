"""Tests for the bundle maker functionality."""

import os
import sys

from nanodoc.data import Bundle, ContentItem, LineRange


def test_bundle_maker_imports():
    """Test that the bundle maker module can be imported."""
    from nanodoc.makerapp import main

    assert callable(main)


def test_nanodoc_maker_flag(monkeypatch, capsys):
    """Test that the --maker flag launches the bundle maker."""
    # Mock the bundle_maker_main function
    mock_called = False

    def mock_bundle_maker_main():
        nonlocal mock_called
        mock_called = True

    # Patch sys.argv and the bundle_maker_main function
    monkeypatch.setattr(sys, "argv", ["nanodoc", "--maker"])
    monkeypatch.setattr("nanodoc.nanodoc.bundle_maker_main", mock_bundle_maker_main)

    # Import and run the main function
    from nanodoc.nanodoc import main

    main()

    # Check that the bundle_maker_main function was called
    assert mock_called, "bundle_maker_main was not called when --maker flag was used"


def test_bundle_creation_workflow():
    """Test the full bundle creation workflow with mocked user input."""
    # This is a more complex test that would require mocking curses and user input
    # For now, we'll just test the basic functionality
    sample_file = os.path.join(os.path.dirname(__file__), "..", "samples", "cake.txt")

    # Create a ContentItem manually
    content_item = ContentItem(
        original_arg=f"{sample_file}:L1-5",
        file_path=sample_file,
        ranges=[LineRange(1, 5)],
        content=None,
    )

    # Create a Bundle
    bundle = Bundle(file_path="test_bundle.txt", content_items=[content_item])

    # Check that the bundle has the expected content
    assert len(bundle.content_items) == 1
    assert bundle.content_items[0].file_path == sample_file
    assert len(bundle.content_items[0].ranges) == 1
    assert bundle.content_items[0].ranges[0].start == 1
    assert bundle.content_items[0].ranges[0].end == 5
