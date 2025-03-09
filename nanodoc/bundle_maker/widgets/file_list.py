"""
File list widget for the nanodoc bundle maker.

This module provides a widget for displaying and selecting files.
"""

import curses
import os
from typing import Any, Dict, List, Optional, Tuple

from ..logging import get_logger
from ..ui.base import Widget

logger = get_logger("widgets.file_list")


class FileListWidget(Widget):
    """Widget for displaying and selecting files."""

    def __init__(self, stdscr, x: int, y: int, width: int, height: int, name: str = "file_list"):
        """Initialize the file list widget.
        
        Args:
            stdscr: The curses standard screen
            x: The x coordinate of the widget
            y: The y coordinate of the widget
            width: The width of the widget
            height: The height of the widget
            name: The name of the widget
        """
        super().__init__(stdscr, x, y, width, height, name)
        
        self.directory = os.environ.get("PWD", os.getcwd())
        self.files = []
        self.directories = []
        self.selected_files = []
        self.cursor_position = 0
        self.scroll_offset = 0
        self.on_directory_change = None
        self.on_selection_change = None
        self.on_file_open = None
        logger.info(f"FileListWidget created with directory: {self.directory}")
        
        # Load files in the current directory
        self._load_files()
    
    def _load_files(self) -> None:
        """Load files from the current directory."""
        try:
            logger.info(f"Loading files from directory: {self.directory}")
            # Get all entries in the directory
            entries = os.listdir(self.directory)
            
            # Separate files and directories
            self.files = []
            self.directories = []
            for entry in entries:
                full_path = os.path.join(self.directory, entry)
                if os.path.isdir(full_path):
                    self.directories.append(entry)
                elif os.path.isfile(full_path):
                    self.files.append(entry)
            
            # Sort the lists
            self.files.sort()
            self.directories.sort()
            
            # Reset cursor and scroll position
            self.cursor_position = 0
            self.scroll_offset = 0
            
            logger.info(f"Loaded {len(self.directories)} directories and {len(self.files)} files")
        except (PermissionError, FileNotFoundError) as e:
            # Handle directory access errors
            logger.error(f"Error accessing directory {self.directory}: {str(e)}")
            if self.on_directory_change:
                self.on_directory_change(self.directory, str(e))
            
            # Try to navigate to parent directory
            parent_dir = os.path.dirname(self.directory)
            if parent_dir and parent_dir != self.directory:
                logger.info(f"Navigating to parent directory: {parent_dir}")
                self.directory = parent_dir
                self._load_files()
    
    def _render_self(self) -> None:
        """Render the file list."""
        if not self.is_visible:
            return
        
        logger.debug(f"Rendering file list with {len(self.directories)} directories and {len(self.files)} files")
        # Calculate visible items
        max_visible = self.height
        total_entries = len(self.directories) + len(self.files)
        
        # Adjust cursor position if needed
        if self.cursor_position >= total_entries:
            self.cursor_position = max(0, total_entries - 1)
        
        # Calculate scroll position to keep cursor visible
        if total_entries > max_visible:
            if self.cursor_position >= self.scroll_offset + max_visible:
                self.scroll_offset = self.cursor_position - max_visible + 1
            elif self.cursor_position < self.scroll_offset:
                self.scroll_offset = self.cursor_position
        
        # Display directories first
        visible_count = 0
        for i, directory in enumerate(self.directories):
            if i < self.scroll_offset:
                continue
            if visible_count >= max_visible:
                break
            
            attr = curses.A_NORMAL
            if i == self.cursor_position:
                attr = curses.A_REVERSE
            
            self.safe_addstr(visible_count, 0, f"📁  {directory}/", attr)
            visible_count += 1
        
        # Display files
        for i, file in enumerate(self.files):
            idx = i + len(self.directories)
            if idx < self.scroll_offset:
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
            self.safe_addstr(visible_count, 0, prefix, 
                           checkbox_attr if idx != self.cursor_position else attr)
            # Display file icon and name
            self.safe_addstr(visible_count, len(prefix) + 1, 
                           f"{icon} {file}", attr)
            visible_count += 1
    
    def _handle_input_self(self, key: int) -> Tuple[bool, Optional[Dict[str, Any]]]:
        """Handle input for the file list.
        
        Args:
            key: The key that was pressed
            
        Returns:
            Tuple of (handled, result)
        """
        total_entries = len(self.directories) + len(self.files)
        
        if key == curses.KEY_UP or key == ord('k'):
            # Move cursor up
            logger.debug(f"Moving cursor up from position {self.cursor_position}")
            if self.cursor_position > 0:
                self.cursor_position -= 1
                return True, {"action": "move", "direction": "up"}
        
        elif key == curses.KEY_DOWN or key == ord('j'):
            # Move cursor down
            if total_entries > 0:
                logger.debug(f"Moving cursor down from position {self.cursor_position}")
                self.cursor_position = min(total_entries - 1, self.cursor_position + 1)
                return True, {"action": "move", "direction": "down"}
        
        elif key == curses.KEY_LEFT or key in (curses.KEY_BACKSPACE, 8, 127):
            # Navigate to parent directory
            parent_dir = os.path.dirname(self.directory)
            logger.info(f"Navigating to parent directory: {parent_dir}")
            if parent_dir != self.directory:  # Only if we're not at the root
                self.directory = parent_dir
                self._load_files()
                if self.on_directory_change:
                    self.on_directory_change(self.directory)
                return True, {"action": "directory_change", "directory": parent_dir}
        
        elif key == curses.KEY_RIGHT or key == ord('\n'):  # Enter key
            # Enter directory if cursor is on a directory
            if 0 <= self.cursor_position < len(self.directories):
                dir_name = self.directories[self.cursor_position]
                logger.info(f"Entering directory: {dir_name}")
                new_dir = os.path.join(self.directory, dir_name)
                try:
                    logger.debug(f"Checking if {new_dir} is a directory")
                    if os.path.isdir(new_dir):
                        self.directory = new_dir
                        self._load_files()
                        if self.on_directory_change:
                            self.on_directory_change(self.directory)
                        return True, {"action": "directory_change", "directory": new_dir}
                except Exception as e:
                    logger.error(f"Error entering directory {new_dir}: {str(e)}")
                    if self.on_directory_change:
                        self.on_directory_change(self.directory, str(e))
            elif self.on_file_open and len(self.directories) <= self.cursor_position < total_entries:
                # Open file if cursor is on a file
                file_idx = self.cursor_position - len(self.directories)
                file_name = self.files[file_idx]
                logger.info(f"Opening file: {file_name}")
                file_path = os.path.join(self.directory, file_name)
                logger.debug(f"Full file path: {file_path}")
                self.on_file_open(file_path)
                return True, {"action": "file_open", "file": file_path}
        
        elif key == ord(" "):  # Space key
            # Toggle selection of current file
            file_idx = self.cursor_position - len(self.directories)
            if file_idx >= 0 and file_idx < len(self.files):
                logger.debug(f"Toggling selection of file at index {file_idx}")
                current_file = self.files[file_idx]
                if current_file in self.selected_files:
                    logger.info(f"Deselecting file: {current_file}")
                    self.selected_files.remove(current_file)
                else:
                    logger.info(f"Selecting file: {current_file}")
                    self.selected_files.append(current_file)
                
                if self.on_selection_change:
                    self.on_selection_change(self.selected_files)
                
                return True, {"action": "selection_change", "selected": self.selected_files}
        
        return False, None
    
    def on_focus_in(self) -> None:
        """Called when the widget receives focus."""
        # Update the app state with focus information
        logger.info(f"FileListWidget received focus at position {self.cursor_position}")
        if hasattr(self, 'app_state'):
            self.app_state["focus"] = {
                "widget": self.name,
                "position": self.cursor_position,
                "directory": self.directory
            }
    
    def on_focus_out(self) -> None:
        """Called when the widget loses focus."""
        logger.info("FileListWidget lost focus")
        
    
    def get_selected_files(self) -> List[str]:
        """Get the list of selected files with full paths.
        
        Returns:
            List of selected file paths
        """
        logger.debug(f"Getting selected files: {self.selected_files}")
        return [os.path.join(self.directory, f) for f in self.selected_files]
    
    def change_directory(self, directory: str) -> bool:
        """Change to a new directory.
        
        Args:
            directory: The new directory path
            
        Returns:
            True if successful, False otherwise
        """
        try:
            logger.info(f"Changing directory to: {directory}")
            if os.path.isdir(directory):
                self.directory = directory
                self._load_files()
                if self.on_directory_change:
                    self.on_directory_change(self.directory)
                return True
            logger.error(f"Not a directory: {directory}")
            return False
        except Exception as e:
            logger.error(f"Error changing directory to {directory}: {str(e)}")
            if self.on_directory_change:
                self.on_directory_change(self.directory, str(e))
            return False
    
    def clear_selection(self) -> None:
        """Clear the current file selection."""
        if self.selected_files:
            self.selected_files = []
            if self.on_selection_change:
                logger.info("Selection cleared")
                self.on_selection_change(self.selected_files)