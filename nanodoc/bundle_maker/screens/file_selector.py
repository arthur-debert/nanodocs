"""
File Selector screen for the nanodoc bundle maker.

This module provides a minimal implementation of the File Selector screen.
"""

import os
from typing import Any, Dict, Optional, Tuple
import re
import curses

from ..operations import get_directory_contents, change_directory, get_parent_directory
from ..logging import get_logger
from .base import Screen

logger = get_logger("screens.file_selector")

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

        logger.info(f"FileSelector initialized with directory: {self.directory}")
        
        # Load files in the current directory
        self._load_files()
    
    def _load_files(self) -> None:
        """Load files from the current directory."""
        try:
            logger.info(f"Loading files from directory: {self.directory}")
            # Use operations module to get directory contents
            self.files, self.directories = get_directory_contents(self.directory)
            logger.info(f"Loaded {len(self.directories)} directories and {len(self.files)} files")
        except (PermissionError, FileNotFoundError) as e:
            logger.error(f"Error accessing directory {self.directory}: {str(e)}")
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
        logger.debug("Rendering FileSelector screen")
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
                
                self.safe_addstr(list_start_y + 1 + visible_count, 2, f"📁  {directory}/", attr)
                visible_count += 1
            
            # Display files
            for i, file in enumerate(self.files):
                idx = i + len(self.directories)
                if idx < scroll_offset:
                    continue
                if visible_count >= max_visible:
                    break
                
                prefix = "[ ]"
                checkbox_attr = curses.A_NORMAL
                if file in self.selected_files:
                    prefix = "[X]"
                    checkbox_attr = curses.color_pair(2) | curses.A_BOLD
                else:
                    checkbox_attr = curses.A_NORMAL
                    
                attr = curses.A_NORMAL
                if idx == self.cursor_position:
                    attr = curses.A_REVERSE
                
                # Add file icon based on extension
                icon = "📄"
                if file.endswith(('.txt', '.md')):
                    icon = "📝"
                elif file.endswith(('.py', '.js', '.c', '.cpp', '.java')):
                    icon = "📜"
                
                # Display checkbox with appropriate color
                self.safe_addstr(list_start_y + 1 + visible_count, 2, prefix, 
                               checkbox_attr if idx != self.cursor_position else attr)
                # Display file icon and name
                self.safe_addstr(list_start_y + 1 + visible_count, 2 + len(prefix) + 1, 
                               f"{icon} {file}", attr)
                visible_count += 1
        
        # Render instructions
        self.safe_addstr(self.height - 5, 0, "Controls:", curses.A_BOLD)
        self.safe_addstr(self.height - 4, 2, "↑/↓ or k/j: Navigate  |  SPACE: Select file  |  ENTER: Open directory  |  BACKSPACE: Parent dir")
        self.safe_addstr(self.height - 3, 2, "d: Change directory  |  c: Clear selections  |  n: Next (with selected files)  |  q: Quit")
        # Show selection count with appropriate color
        self.safe_addstr(self.height - 1, 0, f"Selected: {len(self.selected_files)} files", curses.A_BOLD | curses.color_pair(2 if self.selected_files else 1))

    def handle_input(self, key: int) -> Tuple[str, Optional[Dict[str, Any]]]:
        """Handle user input.
        
        Args:
            key: The key that was pressed
            
        Returns:
            Tuple of (next_screen, screen_params)
        """
        # Check for global keys
        logger.debug(f"Handling input key: {key}")
        if self.check_global_keys(key):
            return "file_selector", None

        if key == ord("q"):
            raise KeyboardInterrupt
            
        elif key == ord("n"):
            # Go to Bundle Summary if files are selected
            if self.selected_files:
                logger.info(f"Navigating to bundle_summary with {len(self.selected_files)} selected files")
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
                logger.info("Clearing file selections")
                self.selected_files = []
                self.show_message("Selection Cleared", "All file selections have been cleared.")
            return "file_selector", None

        elif key == ord("d"):
            # Change directory
            new_dir = self.get_input("Enter directory path: ", 2, 0)
            if new_dir:
                logger.info(f"Attempting to change directory to: {new_dir}")
                try:
                    # Use operations module to change directory
                    new_dir_path = change_directory(self.directory, new_dir)
                    logger.info(f"Changed directory to: {new_dir_path}")
                    self.directory = new_dir_path
                    self.app_state["current_dir"] = new_dir_path
                    self._load_files()
                    self.cursor_position = 0
                except NotADirectoryError as e:
                    logger.error(f"Not a directory: {new_dir} - {str(e)}")
                    self.show_error(str(e))
                except Exception as e:
                    self.show_error(f"Error changing directory: {str(e)}")
            return "file_selector", None

        elif key == ord('\n'):  # Enter key
            # Enter directory if cursor is on a directory
            if 0 <= self.cursor_position < len(self.directories):
                dir_name = self.directories[self.cursor_position]
                logger.info(f"Attempting to enter directory: {dir_name}")
                new_dir = os.path.join(self.directory, dir_name)
                try:
                    # Use operations module to change directory
                    new_dir_path = change_directory(self.directory, dir_name)
                    logger.info(f"Entered directory: {new_dir_path}")
                    self.directory = new_dir_path
                    self.app_state["current_dir"] = new_dir_path
                    self._load_files()
                    self.cursor_position = 0
                except NotADirectoryError as e:
                    logger.error(f"Not a directory: {dir_name} - {str(e)}")
                    self.show_error(str(e))
                except Exception as e:
                    self.show_error(f"Error changing directory: {str(e)}")
            return "file_selector", None

        elif key in (curses.KEY_BACKSPACE, 8, 127):  # Backspace/Delete key (different codes for different terminals)
            # Navigate to parent directory
            try:
                logger.info("Navigating to parent directory")
                parent_dir = get_parent_directory(self.directory)
                if parent_dir != self.directory:  # Only if we're not at the root
                    logger.info(f"Parent directory: {parent_dir}")
                    self.directory = parent_dir
                    self.app_state["current_dir"] = parent_dir
                    self._load_files()
                    self.cursor_position = 0
            except Exception as e:
                self.show_error(f"Error navigating to parent directory: {str(e)}")
            return "file_selector", None

        elif key == ord(" "):  # Space key
            # Toggle selection of current file
            # Only allow selecting files, not directories
            file_idx = self.cursor_position - len(self.directories)
            if file_idx >= 0 and file_idx < len(self.files):
                current_file = self.files[file_idx]
                if current_file in self.selected_files:
                    logger.info(f"Deselecting file: {current_file}")
                    self.selected_files.remove(current_file)
                else:
                    logger.info(f"Selecting file: {current_file}")
                    self.selected_files.append(current_file)
            elif self.cursor_position < len(self.directories):
                # If it's a directory, show a message
                if len(self.directories) > 0:
                    self.show_message("Directory Selected", "Press ENTER to open directory. Only files can be selected.")
            return "file_selector", None

        elif key == curses.KEY_UP or key == ord('k'):  # Up arrow or vim 'k'
            # Move cursor up
            logger.debug(f"Moving cursor up from position {self.cursor_position}")
            self.cursor_position = max(0, self.cursor_position - 1)
            return "file_selector", None

        elif key == curses.KEY_DOWN or key == ord('j'):  # Down arrow or vim 'j'
            # Move cursor down
            total_entries = len(self.directories) + len(self.files)
            logger.debug(f"Moving cursor down from position {self.cursor_position}")
            if total_entries > 0:
                self.cursor_position = min(total_entries - 1, self.cursor_position + 1)
            return "file_selector", None
            
        elif key == curses.KEY_DOWN:  # This is now redundant but kept for compatibility
            # Move cursor down
            total_entries = len(self.directories) + len(self.files)
            if total_entries > 0:
                self.cursor_position = min(total_entries - 1, self.cursor_position + 1)
            return "file_selector", None
            
        elif key == curses.KEY_LEFT:
            # Navigate to parent directory (same as backspace)
            try:
                logger.info("Navigating to parent directory (left key)")
                parent_dir = get_parent_directory(self.directory)
                if parent_dir != self.directory:  # Only if we're not at the root
                    logger.info(f"Parent directory: {parent_dir}")
                    self.directory = parent_dir
                    self.app_state["current_dir"] = parent_dir
                    self._load_files()
                    self.cursor_position = 0
            except Exception as e:
                self.show_error(f"Error navigating to parent directory: {str(e)}")
            return "file_selector", None
            
        elif key == curses.KEY_RIGHT:
            # Enter directory (same as Enter key) if cursor is on a directory
            if 0 <= self.cursor_position < len(self.directories):
                return self.handle_input(ord('\n'))  # Reuse Enter key logic

        # Default: stay on this screen
        return "file_selector", None