#!/usr/bin/env python3
"""
nanodoc-make-bundle - Interactive CLI for creating nanodoc bundles

This module provides an interactive ncurses-based interface for creating
nanodoc bundles by selecting files and specific parts of files.
"""

import curses
import logging

from .bundle_operations import load_ui_defs
from .screens.app import App
from .screens.bundle_summary import BundleSummary
from .screens.file_detail import FileDetail
from .screens.file_selector import FileSelector

logger = logging.getLogger("nanodoc")
logger.setLevel(logging.CRITICAL)  # Start with logging disabled


class BundleMaker:
    """Interactive ncurses-based interface for creating nanodoc bundles."""

    def __init__(self, stdscr):
        """Initialize the BundleMaker with a curses screen.

        Args:
            stdscr: The curses standard screen
        """
        self.stdscr = stdscr
        self.ui_defs = load_ui_defs()

        # Set up the screen
        curses.curs_set(0)  # Hide cursor
        self.stdscr.clear()
        self.stdscr.refresh()

        # Initialize colors
        self._init_colors()

        # Initialize app
        self.app = App(stdscr, self.ui_defs)

        # Register screens
        self.register_screens()

    def _init_colors(self):
        """Initialize colors."""
        # Start color mode
        curses.start_color()
        curses.use_default_colors()

        # Default color pairs
        curses.init_pair(1, curses.COLOR_WHITE, curses.COLOR_BLUE)  # Header
        curses.init_pair(2, curses.COLOR_GREEN, -1)  # Success
        curses.init_pair(3, curses.COLOR_RED, -1)  # Error
        curses.init_pair(4, curses.COLOR_YELLOW, -1)  # Highlight
        curses.init_pair(5, curses.COLOR_BLACK, curses.COLOR_WHITE)  # Status bar

    def register_screens(self):
        """Register all screen classes with the app."""
        self.app.register_screen("file_selector", FileSelector)
        self.app.register_screen("file_detail", FileDetail)
        self.app.register_screen("bundle_summary", BundleSummary)

    def run(self):
        """Run the bundle maker interface."""
        try:
            # Start with the file selector screen
            self.app.run("file_selector")
            return None
        except KeyboardInterrupt:
            return None  # User cancelled with Ctrl+C or 'q'


def main():
    """Main entry point for the nanodoc-make-bundle command."""
    return curses.wrapper(lambda stdscr: BundleMaker(stdscr).run())


if __name__ == "__main__":
    main()
