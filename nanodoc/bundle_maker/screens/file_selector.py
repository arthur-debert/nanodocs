"""
File Selector screen for the nanodoc bundle maker.

This module provides a minimal implementation of the File Selector screen.
"""

import os
from typing import Any, Dict, Optional, Tuple
import curses

from .base import Screen


class FileSelector(Screen):
    """File Selector screen for the bundle maker interface."""

    def __init__(self, stdscr, ui_defs: Dict[str, Any], app_state: Dict[str, Any]):
        """Initialize the File Selector screen."""
        super().__init__(stdscr, ui_defs, app_state)

        # Initialize directory
        if not self.app_state.get("current_dir"):
            self.app_state["current_dir"] = os.environ.get("PWD", os.getcwd())

        self.directory = self.app_state["current_dir"]
        self.files = []
        self.selected_files = []
        self.cursor_position = 0
        
        # Load files in the current directory
        self._load_files()
    
    def _load_files(self) -> None:
        """Load files from the current directory."""
        try:
            self.files = [f for f in os.listdir(self.directory) 
                         if os.path.isfile(os.path.join(self.directory, f))]
            self.files.sort()
        except Exception as e:
            self.files = []
            self.show_error(f"Error loading files: {str(e)}")

    def render(self) -> None:
        """Render the File Selector screen."""
        # Render title
        self.render_title("NANODOC BUNDLE MAKER / FILE SELECTOR")

        # Render directory info
        self.safe_addstr(2, 0, f"Current Directory: {self.directory}")
        
        # Render file list
        self.safe_addstr(4, 0, "Files:")
        
        if not self.files:
            self.safe_addstr(6, 2, "No files found in this directory.")
        else:
            for i, file in enumerate(self.files[:min(len(self.files), self.height - 10)]):
                prefix = "[ ]"
                if file in self.selected_files:
                    prefix = "[X]"
                
                attr = 0
                if i == self.cursor_position:
                    attr = curses.A_REVERSE
                
                self.safe_addstr(6 + i, 2, f"{prefix} {file}", attr)
        
        # Render instructions
        self.safe_addstr(self.height - 4, 0, "Controls: ↑/↓: Navigate, SPACE: Select, d: Change directory")
        self.safe_addstr(self.height - 3, 0, "n: Next (Bundle Summary), q: Quit")
        self.safe_addstr(self.height - 1, 0, "Select files to include in the bundle")

    def handle_input(self, key: int) -> Tuple[str, Optional[Dict[str, Any]]]:
        """Handle user input.
        
        Args:
            key: The key that was pressed
            
        Returns:
            Tuple of (next_screen, screen_params)
        """
        # Check for global keys
        if self.check_global_keys(key):
            return "file_selector", None

        if key == ord("q"):
            raise KeyboardInterrupt
            
        elif key == ord("n"):
            # Go to Bundle Summary if files are selected
            if self.selected_files:
                selected_paths = [os.path.join(self.directory, f) for f in self.selected_files]
                return "bundle_summary", {
                    "selected_files": selected_paths
                }
            else:
                self.show_error("No files selected. Please select at least one file.")
                return "file_selector", None
                
        elif key == ord("d"):
            # Change directory
            new_dir = self.get_input("Enter directory path: ", 2, 0)
            if new_dir:
                try:
                    if os.path.isdir(new_dir):
                        self.directory = new_dir
                        self.app_state["current_dir"] = new_dir
                        self._load_files()
                        self.cursor_position = 0
                    else:
                        self.show_error(f"Not a directory: {new_dir}")
                except Exception as e:
                    self.show_error(f"Error changing directory: {str(e)}")
            return "file_selector", None
            
        elif key == ord(" "):  # Space key
            # Toggle selection of current file
            if self.files and 0 <= self.cursor_position < len(self.files):
                current_file = self.files[self.cursor_position]
                if current_file in self.selected_files:
                    self.selected_files.remove(current_file)
                else:
                    self.selected_files.append(current_file)
            return "file_selector", None
            
        elif key == curses.KEY_UP:
            # Move cursor up
            self.cursor_position = max(0, self.cursor_position - 1)
            return "file_selector", None
            
        elif key == curses.KEY_DOWN:
            # Move cursor down
            if self.files:
                self.cursor_position = min(len(self.files) - 1, self.cursor_position + 1)
            return "file_selector", None

        # Default: stay on this screen
        return "file_selector", None