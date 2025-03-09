"""
File Selector screen for the nanodoc bundle maker.

This module provides a minimal implementation of the File Selector screen.
"""

import os
from typing import Any, Dict, Optional, Tuple

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

    def render(self) -> None:
        """Render the File Selector screen."""
        # Render title
        self.render_title("NANODOC BUNDLE MAKER / FILE SELECTOR")

        # Render basic content
        self.safe_addstr(2, 0, f"Current Directory: {self.directory}")
        self.safe_addstr(
            4, 0, "This is a minimal implementation of the File Selector screen."
        )
        self.safe_addstr(
            6, 0, "Press 'q' to quit or 'n' to go to Bundle Summary screen."
        )

    def handle_input(self) -> Tuple[str, Optional[Dict[str, Any]]]:
        """Handle user input."""
        key = self.stdscr.getch()

        # Check for global keys
        if self.check_global_keys(key):
            return "file_selector", None

        if key == ord("q"):
            # Quit
            raise KeyboardInterrupt
        elif key == ord("n"):
            # Go to Bundle Summary
            return "bundle_summary", {
                "selected_files": [self.directory + "/README.txt"]
            }
        elif key == ord("d"):
            # Change directory (just a demo, doesn't actually change directory)
            self.app_state["current_dir"] = os.path.dirname(self.directory)
            return "file_selector", None

        # Default: stay on this screen
        return "file_selector", None
