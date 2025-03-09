"""Tests for the bundle maker functionality."""

import os
import sys
from unittest.mock import MagicMock, patch

from nanodoc.bundle_maker import BundleMaker
from nanodoc.data import Bundle, ContentItem, LineRange


def test_bundle_maker_imports():
    """Test that the bundle maker module can be imported."""
    from nanodoc.bundle_maker import main

    assert callable(main)


def test_add_file_part():
    """Test adding file parts to the bundle."""
    # Create a mock BundleMaker instance
    with (
        patch("curses.initscr"),
        patch("curses.start_color"),
        patch("curses.use_default_colors"),
        patch("curses.init_pair"),
        patch("curses.curs_set"),
    ):
        # Create a mock stdscr
        mock_stdscr = MagicMock()
        mock_stdscr.getmaxyx.return_value = (25, 80)

        bundle_maker = BundleMaker(mock_stdscr)
        bundle_maker.content_items = []

        # Test adding a full file
        bundle_maker._add_file_part("test.txt", 1, "X")
        assert len(bundle_maker.content_items) == 1
        assert bundle_maker.content_items[0].file_path == "test.txt"
        assert len(bundle_maker.content_items[0].ranges) == 1
        assert bundle_maker.content_items[0].ranges[0].start == 1
        assert bundle_maker.content_items[0].ranges[0].end == "X"

        # Test adding a single line
        bundle_maker._add_file_part("another.txt", 5, 5)
        assert len(bundle_maker.content_items) == 2
        assert bundle_maker.content_items[1].file_path == "another.txt"
        assert bundle_maker.content_items[1].ranges[0].start == 5
        assert bundle_maker.content_items[1].ranges[0].end == 5

        # Test adding a range
        bundle_maker._add_file_part("another.txt", 10, 20)
        # Should add to the existing ContentItem for another.txt
        assert len(bundle_maker.content_items) == 2
        assert len(bundle_maker.content_items[1].ranges) == 2
        assert bundle_maker.content_items[1].ranges[1].start == 10
        assert bundle_maker.content_items[1].ranges[1].end == 20


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
