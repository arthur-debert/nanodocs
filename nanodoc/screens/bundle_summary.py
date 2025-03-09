"""
Bundle Summary screen for the nanodoc bundle maker.

This module provides a minimal implementation of the Bundle Summary screen.
"""

import os
from typing import Any, Dict, Optional, Tuple

from .base import Screen


class BundleSummary(Screen):
    """Bundle Summary screen for the bundle maker interface."""

    def __init__(self, stdscr, ui_defs: Dict[str, Any], app_state: Dict[str, Any]):
        """Initialize the Bundle Summary screen."""
        super().__init__(stdscr, ui_defs, app_state)
        
        # Process selected files if any
        if self.app_state.get("selected_files"):
            # Add selected files to content items
            for file_path in self.app_state["selected_files"]:
                self.app_state.setdefault("content_items", []).append({
                    "file_path": file_path,
                    "ranges": [{"start": 1, "end": "X"}]  # Entire file
                })
            # Clear selected files
            self.app_state["selected_files"] = []
    
    def render(self) -> None:
        """Render the Bundle Summary screen."""
        # Render title
        self.render_title("NANODOC BUNDLE MAKER / BUNDLE SUMMARY")
        
        # Render content
        self.safe_addstr(2, 0, "Bundle Summary Screen (Minimal Implementation)")
        
        # Show files in bundle
        content_items = self.app_state.get("content_items", [])
        if content_items:
            self.safe_addstr(4, 0, f"Files in bundle: {len(content_items)}")
            for i, item in enumerate(content_items):
                self.safe_addstr(5 + i, 2, f"- {item['file_path']}")
        else:
            self.safe_addstr(4, 0, "No files in bundle")
        
        # Render options
        self.safe_addstr(self.height - 4, 0, "Options:")
        self.safe_addstr(self.height - 3, 2, "a - Add more files (go to File Selector)")
        self.safe_addstr(self.height - 2, 2, "e - Edit file (go to File Detail)")
        self.safe_addstr(self.height - 1, 2, "q - Quit")
    
    def handle_input(self, key: int) -> Tuple[str, Optional[Dict[str, Any]]]:
        """Handle user input.
        
        Args:
            key: The key that was pressed
            
        Returns:
            Tuple of (next_screen, screen_params)
        """
        # Check for global keys
        if self.check_global_keys(key):
            return "bundle_summary", None
        
        if key == ord('a'):
            # Add more files
            return "file_selector", None
        elif key == ord('e'):
            # Edit file (go to File Detail)
            # For demo purposes, just use the first file if available
            content_items = self.app_state.get("content_items", [])
            if content_items:
                current_file = content_items[0]["file_path"]
                return "file_detail", {"current_file": current_file}
            else:
                self.show_error("No files to edit")
                return "bundle_summary", None
        elif key == ord('q'):
            # Quit
            raise KeyboardInterrupt
        
        # Default: stay on this screen
        return "bundle_summary", None
