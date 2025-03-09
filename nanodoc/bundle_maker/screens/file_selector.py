"""
File Selector screen for the nanodoc bundle maker.

This module provides a minimal implementation of the File Selector screen.
"""

import os
from typing import Any, Dict, Optional, Tuple
import re
import curses

from ..operations import get_directory_contents, change_directory, get_parent_directory
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
        self.directories = []
        self.cursor_position = 0
        
        # Load files in the current directory
        self._load_files()
    
    def _load_files(self) -> None:
        """Load files from the current directory."""
        try:
            # Use operations module to get directory contents
            self.files, self.directories = get_directory_contents(self.directory)
        except (PermissionError, FileNotFoundError) as e:
            self.show_error(f"Error accessing directory: {str(e)}")
            # Revert to parent directory if possible
            parent_dir = get_parent_directory(self.directory)
            self.directory = parent_dir
            self.app_state["current_dir"] = parent_dir
            self._load_files()  # Try again with parent directory
        except Exception as e:
            self.show_error(f"Error: {str(e)}")

    def render(self) -> None:
        """Render the File Selector screen."""
        # Render title
        self.render_title("NANODOC BUNDLE MAKER / FILE SELECTOR")

        # Render directory info
        self.safe_addstr(2, 0, "Current Directory:")
        self.safe_addstr(3, 2, self.directory)
        
        # Render directory and file list
        list_start_y = 5
        self.safe_addstr(list_start_y, 0, "Directories and Files:")
        
        if not self.directories and not self.files:
            self.safe_addstr(list_start_y + 1, 2, "No entries found in this directory.")
        else:
            # Calculate visible items
            max_visible = self.height - list_start_y - 6
            total_entries = len(self.directories) + len(self.files)
            
            # Adjust cursor position if needed
            if self.cursor_position >= total_entries:
                self.cursor_position = max(0, total_entries - 1)
            
            # Calculate scroll position to keep cursor visible
            scroll_offset = 0
            if total_entries > max_visible:
                if self.cursor_position >= max_visible:
                    scroll_offset = self.cursor_position - max_visible + 1
                    if scroll_offset + max_visible > total_entries:
                        scroll_offset = total_entries - max_visible
            
            # Display directories first
            visible_count = 0
            for i, directory in enumerate(self.directories):
                if i < scroll_offset:
                    continue
                if visible_count >= max_visible:
                    break
                
                attr = curses.A_NORMAL
                if i == self.cursor_position:
                    attr = curses.A_REVERSE
                
                self.safe_addstr(list_start_y + 1 + visible_count, 2, f"📁 {directory}", attr)
                visible_count += 1
            
            # Display files
            for i, file in enumerate(self.files):
                idx = i + len(self.directories)
                if idx < scroll_offset:
                    continue
                if visible_count >= max_visible:
                    break
                
                prefix = "[ ]"
                if file in self.selected_files:
                    prefix = "[X]"
                
                attr = curses.A_NORMAL
                if idx == self.cursor_position:
                    attr = curses.A_REVERSE
                
                self.safe_addstr(list_start_y + 1 + visible_count, 2, f"{prefix} {file}", attr)
                visible_count += 1
        
        # Render instructions
        self.safe_addstr(self.height - 4, 0, "Controls: ↑/↓: Navigate, SPACE: Select file, ENTER: Open directory")
        self.safe_addstr(self.height - 3, 0, "d: Change directory, c: Clear selections, n: Next, q: Quit")
        self.safe_addstr(self.height - 1, 0, f"Selected: {len(self.selected_files)} files")

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
                
        elif key == ord("c"):
            # Clear selections
            if self.selected_files:
                self.selected_files = []
                self.show_message("Selection Cleared", "All file selections have been cleared.")
            return "file_selector", None
                
        elif key == ord("d"):
            # Change directory
            new_dir = self.get_input("Enter directory path: ", 2, 0)
            if new_dir:
                try:
                    # Use operations module to change directory
                    new_dir_path = change_directory(self.directory, new_dir)
                    self.directory = new_dir_path
                    self.app_state["current_dir"] = new_dir_path
                    self._load_files()
                    self.cursor_position = 0
                except NotADirectoryError as e:
                    self.show_error(str(e))
                except Exception as e:
                    self.show_error(f"Error changing directory: {str(e)}")
            return "file_selector", None
            
        elif key == ord('\n'):  # Enter key
            # Enter directory if cursor is on a directory
            if 0 <= self.cursor_position < len(self.directories):
                dir_name = self.directories[self.cursor_position]
                new_dir = os.path.join(self.directory, dir_name)
                try:
                    # Use operations module to change directory
                    new_dir_path = change_directory(self.directory, dir_name)
                    self.directory = new_dir_path
                    self.app_state["current_dir"] = new_dir_path
                    self._load_files()
                    self.cursor_position = 0
                except NotADirectoryError as e:
                    self.show_error(str(e))
                except Exception as e:
                    self.show_error(f"Error changing directory: {str(e)}")
            return "file_selector", None
            
        elif key == ord(" "):  # Space key
            # Toggle selection of current file
            # Only allow selecting files, not directories
            file_idx = self.cursor_position - len(self.directories)
            if file_idx >= 0 and file_idx < len(self.files):
                current_file = self.files[file_idx]
                if current_file in self.selected_files:
                    self.selected_files.remove(current_file)
                else:
                    self.selected_files.append(current_file)
            elif self.cursor_position < len(self.directories):
                # If it's a directory, show a message
                if len(self.directories) > 0:
                    self.show_message("Directory Selected", "Press ENTER to open directory. Only files can be selected.")
                else:
                    self.selected_files.append(current_file)
            return "file_selector", None
            
        elif key == curses.KEY_UP:
            # Move cursor up
            self.cursor_position = max(0, self.cursor_position - 1)
            return "file_selector", None
            
        elif key == curses.KEY_DOWN:
            # Move cursor down
            total_entries = len(self.directories) + len(self.files)
            if total_entries > 0:
                self.cursor_position = min(total_entries - 1, self.cursor_position + 1)
            return "file_selector", None

        # Default: stay on this screen
        return "file_selector", None