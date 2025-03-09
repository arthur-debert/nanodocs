"""
File list widget for the nanodoc bundle maker.

This module provides a widget for displaying and selecting files.
"""

import curses
import os
from typing import Any, Dict, List, Optional, Tuple

from ..logging import get_logger
from ..ui.base import ListItem, ListWidget

logger = get_logger("widgets.file_list")


class FileItem(ListItem):
    """Represents a file or directory item in the file list."""

    def __init__(self, parent_widget: "FileListWidget", name: str, is_directory: bool):
        """Initialize a file item.

        Args:
            parent_widget: The parent FileListWidget
            name: The name of the file or directory
            is_directory: Whether this item is a directory
        """
        super().__init__(parent_widget, name)
        self.is_directory = is_directory
        self.full_path = os.path.join(parent_widget.directory, name)
        logger.info(f"FileItem created: {self.full_path} (directory: {is_directory})")

    def on_focus(self) -> None:
        """Called when this item receives focus."""
        super().on_focus()
        # Add additional file-specific focus information
        if hasattr(self.parent_widget, "app_state"):
            self.parent_widget.app_state["focus"]["is_directory"] = self.is_directory
            self.parent_widget.app_state["focus"]["path"] = self.full_path
        logger.info(f"FileItem focused: {self.full_path}")

    def on_select(self) -> None:
        """Called when this item is selected."""
        if not self.is_directory:  # Only files can be selected
            super().on_select()
            logger.info(f"FileItem selected: {self.full_path}")

    def on_deselect(self) -> None:
        """Called when this item is deselected."""
        if not self.is_directory:  # Only files can be deselected
            super().on_deselect()
            logger.info(f"FileItem deselected: {self.full_path}")

    def get_display_text(self) -> str:
        """Get the display text for this item.

        Returns:
            The display text
        """
        if self.is_directory:
            return f"📁  {self.name}/"
        else:
            # Add file icon based on extension
            icon = "📄"
            if self.name.endswith((".txt", ".md")):
                icon = "📝"
            elif self.name.endswith((".py", ".js", ".c", ".cpp", ".java")):
                icon = "📜"

            prefix = "[X]" if self.is_selected else "[ ]"
            return f"{prefix} {icon} {self.name}"

    def get_state(self) -> Dict[str, Any]:
        """Get the state of this item.

        Returns:
            The item state
        """
        state = super().get_state()
        state.update({"is_directory": self.is_directory, "full_path": self.full_path})
        return state


class FileListWidget(ListWidget):
    """Widget for displaying and selecting files."""

    def __init__(
        self, stdscr, x: int, y: int, width: int, height: int, name: str = "file_list"
    ):
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

        # Initialize directory
        self.directory = os.environ.get("PWD", os.getcwd())

        # Set up callbacks
        self.on_directory_change = None
        self.on_file_open = None

        # Set up item callbacks
        self.on_item_select = self._handle_item_select
        self.on_item_deselect = self._handle_item_deselect

        logger.info(f"FileListWidget initialized with directory: {self.directory}")

        # Load files in the current directory
        self._load_files()

    def _handle_item_select(self, item: FileItem) -> None:
        """Handle item selection.

        Args:
            item: The selected item
        """
        if hasattr(self, "on_selection_change"):
            selected_items = self.get_selected_items()
            selected_files = [item.name for item in selected_items]
            logger.info(f"Selection changed: {selected_files}")
            if self.on_selection_change:
                self.on_selection_change(selected_files)

    def _handle_item_deselect(self, item: FileItem) -> None:
        """Handle item deselection.

        Args:
            item: The deselected item
        """
        if hasattr(self, "on_selection_change"):
            selected_items = self.get_selected_items()
            selected_files = [item.name for item in selected_items]
            logger.info(f"Selection changed: {selected_files}")
            if self.on_selection_change:
                self.on_selection_change(selected_files)

    def _load_files(self) -> None:
        """Load files from the current directory."""
        try:
            logger.info(f"Loading files from directory: {self.directory}")
            # Clear existing items
            self.clear_items()

            # Get directory contents
            entries = sorted(os.listdir(self.directory))
            directories = []
            files = []

            # Separate directories and files
            for entry in entries:
                path = os.path.join(self.directory, entry)
                if os.path.isdir(path):
                    directories.append(entry)
                elif os.path.isfile(path):
                    files.append(entry)

            # Add directories first
            for directory in sorted(directories):
                self.add_item(FileItem(self, directory, True))

            # Then add files
            for file in sorted(files):
                self.add_item(FileItem(self, file, False))

            logger.info(f"Loaded {len(directories)} directories and {len(files)} files")
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

    def _handle_input_self(self, key: int) -> Tuple[bool, Optional[Dict[str, Any]]]:
        """Handle input for the file list.

        Args:
            key: The key that was pressed

        Returns:
            Tuple of (handled, result)
        """
        # First, let the base class handle common navigation keys
        handled, result = super()._handle_input_self(key)
        if handled:
            return handled, result

        # Handle file list specific keys
        if key == curses.KEY_LEFT or key in (curses.KEY_BACKSPACE, 8, 127):
            # Navigate to parent directory
            logger.info(f"Left/Backspace key pressed (code: {key})")
            parent_dir = os.path.dirname(self.directory)
            if parent_dir != self.directory:  # Only if we're not at the root
                logger.info(f"Navigating to parent directory: {parent_dir}")
                self.directory = parent_dir
                self._load_files()
                if self.on_directory_change:
                    self.on_directory_change(self.directory)
                return True, {"action": "directory_change", "directory": parent_dir}
            else:
                logger.info("Already at root directory")
                return True, {"action": "directory_change", "status": "at_root"}

        elif key == curses.KEY_RIGHT or key == ord("\n"):  # Enter key
            # Enter directory if cursor is on a directory
            if (
                self.cursor_position < len(self.items)
                and self.items[self.cursor_position].is_directory
            ):
                item = self.items[self.cursor_position]
                logger.info(
                    f"Right/Enter key pressed (code: {key}) on directory: {item.name}"
                )
                new_dir = os.path.join(self.directory, item.name)
                try:
                    logger.debug(f"Checking if {new_dir} is a directory")
                    if os.path.isdir(new_dir):
                        logger.info(f"Entering directory: {dir_name}")
                        self.directory = new_dir
                        self._load_files()
                        if self.on_directory_change:
                            self.on_directory_change(self.directory)
                        return True, {
                            "action": "directory_change",
                            "directory": new_dir,
                        }
                except Exception as e:
                    logger.error(f"Error entering directory {new_dir}: {str(e)}")
                    if self.on_directory_change:
                        self.on_directory_change(self.directory, str(e))
            elif self.cursor_position < len(self.items):
                # Open file if cursor is on a file
                item = self.items[self.cursor_position]
                if not item.is_directory and self.on_file_open:
                    logger.info(f"Right/Enter key pressed (code: {key}) on file")
                    logger.info(f"Opening file: {item.name}")
                    self.on_file_open(item.full_path)
                    return True, {"action": "file_open", "file": item.full_path}
            else:
                logger.info(
                    f"Right/Enter key pressed (code: {key}) but not on valid item"
                )
                return True, {"action": "invalid_selection"}

        return False, None

    def on_focus_in(self) -> None:
        """Called when the widget receives focus."""
        # Update the app state with focus information
        logger.info(f"FileListWidget received focus at position {self.cursor_position}")
        if hasattr(self, "app_state"):
            self.app_state["focus"] = {
                "widget": self.name,
                "position": self.cursor_position,
                "directory": self.directory,
            }

    def on_focus_out(self) -> None:
        """Called when the widget loses focus."""
        logger.info("FileListWidget lost focus")

    def get_selected_files(self) -> List[str]:
        """Get the list of selected files with full paths.

        Returns:
            List of selected file paths
        """
        selected_items = self.get_selected_items()
        selected_files = [
            item.full_path for item in selected_items if not item.is_directory
        ]
        logger.debug(f"Getting selected files: {selected_files}")
        return selected_files

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
        for item in self.items:
            if item.is_selected:
                item.on_deselect()

        logger.info("Selection cleared")
        if self.on_selection_change:
            self.on_selection_change([])
