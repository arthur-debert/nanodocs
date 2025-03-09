"""
File Selector screen for the nanodoc bundle maker.

This module provides a minimal implementation of the File Selector screen.
"""

import curses
import os
from typing import Any, Dict, Optional, Tuple

from ..logging import get_logger
from ..operations import change_directory
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
        self.selected_files = []

        logger.info(f"FileSelector initialized with directory: {self.directory}")

        # Create file list widget
        self.file_list = self._create_file_list_widget()

    def _create_file_list_widget(self):
        """Create the file list widget.

        Returns:
            The file list widget
        """
        from ..widgets.file_list import FileListWidget

        # Calculate dimensions for the file list widget
        list_start_y = 5
        list_height = self.height - list_start_y - 6

        # Create the widget
        file_list = FileListWidget(
            self.stdscr,
            2,  # x position
            list_start_y + 1,  # y position
            self.width - 4,  # width
            list_height,  # height
            "file_selector_list",
        )

        # Set up callbacks
        file_list.on_directory_change = self._handle_directory_change
        file_list.on_selection_change = self._handle_selection_change
        file_list.app_state = self.app_state

        # Initialize with current directory
        file_list.directory = self.directory
        file_list._load_files()

        return file_list

    def _handle_directory_change(self, directory, error=None):
        """Handle directory change.

        Args:
            directory: The new directory
            error: Optional error message
        """
        if error:
            self.show_error(f"Error accessing directory: {error}")
        else:
            self.directory = directory
            self.app_state["current_dir"] = directory
            logger.info(f"Directory changed to: {directory}")

    def _handle_selection_change(self, selected_files):
        """Handle selection change.

        Args:
            selected_files: The selected files
        """
        self.selected_files = selected_files
        logger.info(f"Selection changed: {selected_files}")

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

        # Render the file list widget
        self.file_list.render()

        # Render instructions
        self.safe_addstr(self.height - 5, 0, "Keyboard Controls:", curses.A_BOLD)
        self.safe_addstr(
            self.height - 4,
            2,
            "↑/↓/k/j: Navigate  |  SPACE: Select file  |  ENTER/→: Open directory  |  BACKSPACE/←: Parent dir",
        )
        self.safe_addstr(
            self.height - 3,
            2,
            "HOME/END: Jump to top/bottom  |  PgUp/PgDn: Page navigation  |  TAB: Focus next widget",
        )
        self.safe_addstr(
            self.height - 2,
            2,
            "d: Change directory  |  c: Clear selections  |  n: Next (with selected files)  |  q: Quit",
        )
        # Show selection count with appropriate color
        self.safe_addstr(
            self.height - 1,
            0,
            f"Selected: {len(self.selected_files)} files",
            curses.A_BOLD | curses.color_pair(2 if self.selected_files else 1),
        )

    def handle_input(self, key: int) -> Tuple[str, Optional[Dict[str, Any]]]:
        """Handle user input.

        Args:
            key: The key that was pressed

        Returns:
            Tuple of (next_screen, screen_params)
        """
        # Check for global keys
        logger.debug(f"Handling input key: {key}")
        if key != ord("q") and self.check_global_keys(key):
            logger.info(f"Global key handled: {key}")
            return "file_selector", None

        if key == ord("q"):
            logger.info("Quit key (q) pressed")
            raise KeyboardInterrupt

        elif key == ord("n"):
            # Go to Bundle Summary if files are selected
            selected_files = self.file_list.get_selected_files()
            if selected_files:
                logger.info(
                    f"Next key (n) pressed: Navigating to bundle_summary with {len(selected_files)} selected files"
                )

                return "bundle_summary", {"selected_files": selected_files}
            else:
                logger.info("Next key (n) pressed but no files selected")
                self.show_error("No files selected. Please select at least one file.")
                return "file_selector", None

        elif key == ord("c"):
            # Clear selections
            if self.file_list.get_selected_files():
                logger.info("Clear key (c) pressed: Clearing file selections")
                self.show_message(
                    "Selection Cleared", "All file selections have been cleared."
                )
            else:
                logger.info("Clear key (c) pressed but no files selected")
            return "file_selector", None

        elif key == ord("d"):
            # Change directory
            logger.info("Directory change key (d) pressed")
            new_dir = self.get_input("Enter directory path: ", 2, 0)
            if new_dir:
                logger.info(f"Attempting to change directory to: {new_dir}")
                try:
                    # Use operations module to change directory
                    new_dir_path = change_directory(self.directory, new_dir)
                    logger.info(f"Directory changed to: {new_dir_path}")
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

        # Pass the key to the file list widget
        handled, result = self.file_list.handle_input(key)
        if handled:
            logger.info(f"Key {key} handled by file list widget: {result}")
            return "file_selector", None

        # Log any unhandled keys for debugging
        else:
            logger.info(f"Unhandled key pressed: {key}")

        # Default: stay on this screen
        return "file_selector", None

    def _load_files(self):
        """Reload files in the current directory."""
        self.file_list.directory = self.directory
        self.file_list._load_files()
