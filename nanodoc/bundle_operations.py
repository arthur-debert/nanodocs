#!/usr/bin/env python3
"""
Pure functions for bundle maker operations.

This module contains standalone functions that handle data operations for the bundle maker,
separating the business logic from the UI code.
"""

import logging
import os
from typing import Any, Dict, List, Optional, Tuple, Union

import yaml

from .data import Bundle, ContentItem, LineRange, save_bundle
from .files import (
    create_content_item,
    expand_directory,
    get_file_content,
)
from .formatting import apply_style_to_filename

logger = logging.getLogger("nanodoc")


def load_ui_defs(ui_def_path: Optional[str] = None) -> Dict[str, Any]:
    """Load UI definitions from YAML file.

    Args:
        ui_def_path: Path to the UI definitions YAML file. If None, uses the default path.

    Returns:
        Dictionary containing the UI definitions
    """
    if ui_def_path is None:
        # Get the default path to the ui-def.yaml file
        ui_def_path = os.path.join(os.path.dirname(__file__), "ui-def.yaml")

    try:
        with open(ui_def_path, "r") as f:
            return yaml.safe_load(f)
    except Exception as e:
        logger.error(f"Error loading UI definitions: {str(e)}")
        print(f"Error loading UI definitions: {str(e)}")
        return {
            "strings": {
                "app_name": "NANODOC BUNDLE MAKER",
                "screen_title_directory": "NANODOC BUNDLE MAKER / DIRECTORY SELECTION",
                "help_text": "NANODOC BUNDLE MAKER HELP\n\nPress any key to close this help dialog.",
            },
            "colors": {},
        }


def get_files_in_directory(
    directory: str, extensions: Optional[List[str]] = None
) -> List[str]:
    """Get a list of files in the directory with the specified extensions.

    Args:
        directory: The directory to search for files
        extensions: List of file extensions to include (e.g., [".txt", ".md"])

    Returns:
        List of file paths
    """
    if not extensions:
        extensions = [".txt", ".md"]  # Default to text and markdown files

    return expand_directory(directory, extensions=extensions)


def get_file_content_with_lines(file_path: str) -> Tuple[str, List[str]]:
    """Get the content of a file and split it into lines.

    Args:
        file_path: Path to the file

    Returns:
        Tuple of (content, lines)
    """
    content = get_file_content(file_path)
    lines = content.splitlines()
    return content, lines


def format_nice_title(filename: str) -> str:
    """Format a filename in 'nice' style using the existing formatting function."""
    return apply_style_to_filename(filename, "nice", filename).split(" (")[
        0
    ]  # Remove the parentheses part


def get_selected_files(
    directory: str, extensions: Optional[List[str]] = None
) -> List[str]:
    """Get a list of selected files from a directory.

    Args:
        directory: The directory to search for files
        extensions: List of file extensions to include

    Returns:
        List of selected file paths
    """
    return get_files_in_directory(directory, extensions)


def create_bundle_from_files(file_paths: List[str], bundle_path: str) -> str:
    """Create a bundle from a list of file paths.

    Args:
        file_paths: List of file paths to include in the bundle
        bundle_path: Path to save the bundle

    Returns:
        Path to the saved bundle file
    """
    content_items = [create_content_item(path) for path in file_paths]
    bundle = Bundle(file_path=bundle_path, content_items=content_items)
    save_bundle(bundle)
    return bundle_path


def add_file_part_to_bundle(
    content_items: List[ContentItem], file_path: str, start: int, end: Union[int, str]
) -> List[ContentItem]:
    """Add a part of a file to the bundle.

    Args:
        content_items: List of existing ContentItem objects
        file_path: Path to the file to add
        start: Start line number (1-indexed)
        end: End line number (1-indexed) or "X" for end of file

    Returns:
        Updated list of ContentItem objects
    """
    # Create a LineRange object
    line_range = LineRange(start, end)

    # Check if we already have a ContentItem for this file
    for item in content_items:
        if item.file_path == file_path:
            # Add this range to the existing ContentItem
            item.ranges.append(line_range)
            return content_items

    # Create a new ContentItem
    original_arg = file_path
    if end != "X" or start != 1:
        # Add line reference to original_arg if not the entire file
        range_str = f"L{start}" if start == end else f"L{start}-{end}"
        original_arg = f"{file_path}:{range_str}"

    content_item = ContentItem(
        original_arg=original_arg,
        file_path=file_path,
        ranges=[line_range],
        content=None,
    )

    # Add to our list
    return content_items + [content_item]


def save_bundle_to_file(content_items: List[ContentItem], bundle_path: str) -> str:
    """Save the bundle to a file.

    Args:
        content_items: List of ContentItem objects
        bundle_path: Path to save the bundle

    Returns:
        Path to the saved bundle file
    """
    # Create a Bundle object
    bundle = Bundle(file_path=bundle_path, content_items=content_items)

    # Save the bundle
    save_bundle(bundle)

    return bundle_path


def get_bundle_summary(content_items: List[ContentItem]) -> Dict[str, List[Dict]]:
    """Get a summary of the bundle contents.

    Args:
        content_items: List of ContentItem objects

    Returns:
        Dictionary with file paths as keys and lists of range information as values
    """
    # Group ContentItems by file path
    file_groups = {}
    for item in content_items:
        if item.file_path not in file_groups:
            file_groups[item.file_path] = []

        for range_obj in item.ranges:
            range_info = {}
            if range_obj.start == 1 and range_obj.end == "X":
                range_info["type"] = "entire_file"
            elif range_obj.start == range_obj.end:
                range_info["type"] = "single_line"
                range_info["line"] = range_obj.start
            else:
                range_info["type"] = "line_range"
                range_info["start"] = range_obj.start
                range_info["end"] = range_obj.end

            file_groups[item.file_path].append(range_info)

    return file_groups
