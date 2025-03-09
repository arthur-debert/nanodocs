"""
Operations for the nanodoc bundle maker.

This module provides utility functions for the bundle maker.
"""

import logging
import os
import re
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