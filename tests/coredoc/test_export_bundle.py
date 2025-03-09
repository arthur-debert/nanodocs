import os

from nanodoc.data import (
    Bundle,
    ContentItem,
    LineRange,
    create_bundle_content,
    save_bundle,
)
from nanodoc.files import get_files_from_args
from nanodoc.nanodoc import export_bundle_file


def test_create_bundle_content():
    """Test creating bundle content from ContentItems."""
    # Create some test ContentItems
    item1 = ContentItem(
        original_arg="file1.txt",
        file_path="file1.txt",
        ranges=[LineRange(1, "X")],  # Full file
    )
    item2 = ContentItem(
        original_arg="file2.txt:L5-10",
        file_path="file2.txt",
        ranges=[LineRange(5, 10)],  # Specific range
    )
    item3 = ContentItem(
        original_arg="file3.txt:L1,L5-10",
        file_path="file3.txt",
        ranges=[LineRange(1, 1), LineRange(5, 10)],  # Multiple ranges
    )

    # Create bundle content
    content = create_bundle_content([item1, item2, item3])

    # Check that the content is correct
    expected_lines = [
        "# nanodoc bundle file",
        "# This file contains a list of files to be bundled by nanodoc",
        "# Each line represents a file path, optionally with line references",
        "",
        "file1.txt",
        "file2.txt:L5-10",
        "file3.txt:L1,L5-10",
    ]
    expected_content = "\n".join(expected_lines)
    assert content == expected_content


def test_save_bundle(tmp_path):
    """Test saving a bundle to a file."""
    # Create a temporary bundle file path
    bundle_file = tmp_path / "test_bundle.txt"

    # Create some test ContentItems
    item1 = ContentItem(
        original_arg="file1.txt",
        file_path="file1.txt",
        ranges=[LineRange(1, "X")],
    )
    item2 = ContentItem(
        original_arg="file2.txt:L5-10",
        file_path="file2.txt",
        ranges=[LineRange(5, 10)],
    )

    # Create a Bundle
    bundle = Bundle(file_path=str(bundle_file), content_items=[item1, item2])

    # Save the bundle
    save_bundle(bundle)

    # Check that the file exists
    assert bundle_file.exists()

    # Check the content of the file
    with open(bundle_file, "r") as f:
        content = f.read()

    expected_lines = [
        "# nanodoc bundle file",
        "# This file contains a list of files to be bundled by nanodoc",
        "# Each line represents a file path, optionally with line references",
        "",
        "file1.txt",
        "file2.txt:L5-10",
    ]
    expected_content = "\n".join(expected_lines)
    assert content == expected_content


def test_export_bundle_file(tmp_path, monkeypatch):
    """Test exporting a bundle file."""
    # Create a temporary bundle file path
    bundle_file = tmp_path / "test_export_bundle.txt"

    # Create some test ContentItems
    item1 = ContentItem(
        original_arg="file1.txt",
        file_path="file1.txt",
        ranges=[LineRange(1, "X")],
    )
    item2 = ContentItem(
        original_arg="file2.txt:L5-10",
        file_path="file2.txt",
        ranges=[LineRange(5, 10)],
    )

    # Mock the save_bundle function to avoid file operations
    def mock_save_bundle(bundle):
        assert bundle.file_path == str(bundle_file)
        assert len(bundle.content_items) == 2
        assert bundle.content_items[0].file_path == "file1.txt"
        assert bundle.content_items[1].file_path == "file2.txt"

    monkeypatch.setattr("nanodoc.nanodoc.save_bundle", mock_save_bundle)

    # Export the bundle
    result = export_bundle_file([item1, item2], str(bundle_file))

    # Check that the export was successful
    assert result is True


def test_export_bundle_integration(tmp_path, monkeypatch):
    """Integration test for exporting a bundle file."""
    # Create temporary test files
    test_dir = tmp_path / "test_files"
    test_dir.mkdir()

    file1 = test_dir / "file1.txt"
    file1.write_text("Line 1\nLine 2\nLine 3\n")

    file2 = test_dir / "file2.txt"
    file2.write_text("Line A\nLine B\nLine C\n")

    # Create a temporary bundle file path
    bundle_file = tmp_path / "test_bundle.txt"

    # Change to the test directory
    original_dir = os.getcwd()
    os.chdir(test_dir)

    try:
        # Get ContentItems from args
        args = ["file1.txt", "file2.txt:L2-3"]
        content_items = get_files_from_args(args)

        # Export the bundle
        result = export_bundle_file(content_items, str(bundle_file))

        # Check that the export was successful
        assert result is True

        # Check that the bundle file exists
        assert bundle_file.exists()

        # Check the content of the bundle file
        with open(bundle_file, "r") as f:
            content = f.read()

        # The bundle should contain file1.txt and file2.txt:L2-3
        assert "file1.txt" in content
        assert "file2.txt:L2-3" in content or "file2.txt:L2-L3" in content
    finally:
        # Change back to the original directory
        os.chdir(original_dir)
