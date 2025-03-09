"""
Bundle Summary screen for the nanodoc bundle maker.

This module provides a minimal implementation of the Bundle Summary screen.
"""

import os
import curses
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
                    "ranges": [{"start": 1, "end": None}]  # Entire file by default
                    # Note: end=None means "to the end of the file"
                    # This will be replaced with the actual line count when needed
                    # or kept as None to indicate "entire file"
                    # We'll display it as "entire file" in the UI
                })
            # Clear selected files
            self.app_state["selected_files"] = []
    
    def render(self) -> None:
        """Render the Bundle Summary screen."""
        # Render title
        self.render_title("NANODOC BUNDLE MAKER / BUNDLE SUMMARY")
        
        # Render bundle info
        self.safe_addstr(2, 0, "Bundle Contents:")
        
        # Show files in bundle
        content_items = self.app_state.get("content_items", [])
        self.cursor_position = min(getattr(self, 'cursor_position', 0), max(0, len(content_items) - 1))
        
        if content_items:
            self.safe_addstr(4, 0, f"Files in bundle ({len(content_items)}):")
            for i, item in enumerate(content_items):
                file_name = os.path.basename(item['file_path'])
                
                # Format ranges display
                ranges_text = ""
                if item['ranges']:
                    range_strs = []
                    for r in item['ranges']:
                        if r['end'] is None:
                            range_strs.append("entire file")
                        else:
                            if r['start'] == r['end']:
                                range_strs.append(f"line {r['start']}")
                            else:
                                range_strs.append(f"lines {r['start']}-{r['end']}")
                    ranges_text = ", ".join(range_strs)
                else:
                    ranges_text = "entire file"
                
                # Highlight the current selection
                attr = curses.A_NORMAL
                if i == self.cursor_position:
                    attr = curses.A_REVERSE
                
                self.safe_addstr(5 + i, 2, f"{i+1}. {file_name} ({ranges_text})", attr)
        else:
            self.safe_addstr(4, 0, "No files in bundle. Press 'a' to add files.")
        
        # Render options
        self.safe_addstr(self.height - 5, 0, "Controls:")
        self.safe_addstr(self.height - 4, 2, "↑/↓: Navigate, e: Edit selected file, r: Remove selected file")
        self.safe_addstr(self.height - 3, 2, "a: Add more files, s: Save bundle, q: Quit")
        self.safe_addstr(self.height - 1, 0, "Review bundle contents and edit as needed")
    
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
            if content_items and 0 <= self.cursor_position < len(content_items):
                current_file = content_items[self.cursor_position]["file_path"]
                return "file_detail", {"current_file": current_file}
            else:
                self.show_error("No files to edit")
                return "bundle_summary", None
        elif key == ord('r'):
            # Remove selected file
            content_items = self.app_state.get("content_items", [])
            if content_items and 0 <= self.cursor_position < len(content_items):
                del content_items[self.cursor_position]
                # Adjust cursor position if needed
                if self.cursor_position >= len(content_items) and len(content_items) > 0:
                    self.cursor_position = len(content_items) - 1
            return "bundle_summary", None
        elif key == ord('s'):
            # Save bundle (just a placeholder for now)
            self.show_message("Save Bundle", "Bundle saved successfully (placeholder).")
            return "bundle_summary", None
        elif key == ord('q'):
            # Quit
            raise KeyboardInterrupt
        elif key == curses.KEY_UP:
            # Move cursor up
            content_items = self.app_state.get("content_items", [])
            if content_items:
                self.cursor_position = max(0, self.cursor_position - 1)
            return "bundle_summary", None
        elif key == curses.KEY_DOWN:
            # Move cursor down
            content_items = self.app_state.get("content_items", [])
            if content_items:
                self.cursor_position = min(len(content_items) - 1, self.cursor_position + 1)
            return "bundle_summary", None
        
        # Initialize cursor_position if it doesn't exist
        if not hasattr(self, 'cursor_position'):
            self.cursor_position = 0
        
        # Default: stay on this screen
        return "bundle_summary", None