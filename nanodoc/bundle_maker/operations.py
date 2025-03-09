"""
Operations for the nanodoc bundle maker.

This module provides utility functions for the bundle maker.
"""

import logging
import os
import re
import tempfile
import yaml
from typing import Dict, List, Optional, Tuple, Union, Any

from nanodoc.data import Bundle, ContentItem, LineRange, save_bundle
from nanodoc.files import expand_directory, get_file_content, create_content_item, verify_content
from nanodoc.formatting import apply_style_to_filename

logger = logging.getLogger("nanodoc")

def load_ui_defs(ui_def_path: Optional[str] = None) -> Dict[str, Any]:
    """Load UI definitions from YAML file.
    
    Args:
        ui_def_path: Path to the UI definitions YAML file
        
    Returns:
        Dictionary of UI definitions
    """
    # Get the path to the ui-def.yaml file if not provided
    if ui_def_path is None:
        ui_def_path = os.path.join(os.path.dirname(__file__), "..", "ui-def.yaml")
    
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
                "help_text": "NANODOC BUNDLE MAKER HELP\n\nPress any key to close this help dialog."
            }
        }


def get_files_in_directory(directory: str, extensions: Optional[List[str]] = None) -> List[str]:
    """Get a list of files in the directory with the specified extensions.
    
    Args:
        directory: The directory to search for files
        extensions: List of file extensions to include
        
    Returns:
        List of file paths
    """
    if not extensions:
        extensions = [".txt", ".md"]  # Default to text and markdown files
    
    return expand_directory(directory, extensions=extensions)


def get_file_content_with_lines(file_path: str) -> Tuple[str, List[str]]:
    """Get the content of a file and its lines.
    
    Args:
        file_path: The path to the file
        
    Returns:
        Tuple of (content, lines)
    """
    content = get_file_content(file_path)
    lines = content.splitlines()
    return content, lines


def format_nice_title(filename: str) -> str:
    """Format a filename in 'nice' style using the existing formatting function."""
    return apply_style_to_filename(filename, "nice", filename).split(" (")[0]  # Remove the parentheses part


def get_selected_files(directory: str, extensions: Optional[List[str]] = None) -> List[str]:
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


def get_directory_contents(directory: str) -> Tuple[List[str], List[str]]:
    """Get the files and directories in a directory.
    
    Args:
        directory: The directory to get contents from
        
    Returns:
        Tuple of (files, directories) lists
    
    Raises:
        PermissionError: If the directory cannot be accessed
        FileNotFoundError: If the directory does not exist
    """
    try:
        # Get all entries in the directory
        entries = os.listdir(directory)
        
        # Separate files and directories
        files = []
        directories = []
        for entry in entries:
            full_path = os.path.join(directory, entry)
            if os.path.isdir(full_path):
                directories.append(entry)
            elif os.path.isfile(full_path):
                files.append(entry)
        
        # Sort the lists
        files.sort()
        directories.sort()
        
        return files, directories
    except (PermissionError, FileNotFoundError) as e:
        # Re-raise the exception to be handled by the caller
        raise e
    except Exception as e:
        # For unexpected errors, log and re-raise
        logger.error(f"Unexpected error getting directory contents: {str(e)}")
        raise e


def change_directory(current_dir: str, new_dir: str) -> str:
    """Change to a new directory, validating it exists and is accessible.
    
    Args:
        current_dir: The current directory
        new_dir: The new directory to change to
        
    Returns:
        The new directory path if successful
        
    Raises:
        NotADirectoryError: If the path is not a directory
        PermissionError: If the directory cannot be accessed
        FileNotFoundError: If the directory does not exist
    """
    # Handle relative paths
    if not os.path.isabs(new_dir):
        new_dir = os.path.join(current_dir, new_dir)
    
    # Normalize the path
    new_dir = os.path.normpath(new_dir)
    
    # Check if the directory exists and is accessible
    if not os.path.exists(new_dir):
        raise FileNotFoundError(f"Directory not found: {new_dir}")
    if not os.path.isdir(new_dir):
        raise NotADirectoryError(f"Not a directory: {new_dir}")
    if not os.access(new_dir, os.R_OK):
        raise PermissionError(f"Cannot access directory: {new_dir}")
    
    return new_dir


def get_parent_directory(directory: str) -> str:
    """Get the parent directory of a given directory.
    
    Args:
        directory: The current directory
        
    Returns:
        The parent directory path
    """
    parent_dir = os.path.dirname(directory)
    if parent_dir == directory:
        # We're at the root directory
        return directory
    return parent_dir


def load_file_content(file_path: str) -> Tuple[List[str], int]:
    """Load the content of a file.
    
    Args:
        file_path: The path to the file
        
    Returns:
        Tuple of (lines, line_count)
        
    Raises:
        FileNotFoundError: If the file does not exist
        PermissionError: If the file cannot be read
    """
    if not os.path.isfile(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")
    
    try:
        with open(file_path, 'r') as f:
            lines = f.readlines()
        return lines, len(lines)
    except PermissionError:
        raise PermissionError(f"Cannot read file: {file_path}")
    except Exception as e:
        logger.error(f"Error reading file: {str(e)}")
        raise e


def format_range_display(range_obj: Dict[str, Any]) -> str:
    """Format a range object for display.
    
    Args:
        range_obj: A range object with 'start' and 'end' keys
        
    Returns:
        A formatted string representation of the range
    """
    start = range_obj.get("start", 1)
    end = range_obj.get("end")
    
    if end is None:
        return "entire file"
    elif start == end:
        return f"line {start}"
    else:
        return f"lines {start}-{end}"


def save_bundle_to_file(content_items: List[Dict[str, Any]], bundle_name: str) -> str:
    """Save a bundle to a file.
    
    Args:
        content_items: List of content items to include in the bundle
        bundle_name: Name of the bundle file
        
    Returns:
        Path to the saved bundle file
    """
    # Convert content items to ContentItem objects
    items = []
    for item in content_items:
        file_path = item["file_path"]
        ranges = []
        for r in item["ranges"]:
            start = r["start"]
            end = r["end"]
            ranges.append(LineRange(start, end if end is not None else "X"))
        items.append(ContentItem(original_arg=file_path, file_path=file_path, ranges=ranges))
    
    # Create and save the bundle
    bundle_path = os.path.join(os.getcwd(), bundle_name)
    bundle = Bundle(file_path=bundle_path, content_items=items)
    save_bundle(bundle)
    
    return bundle_path