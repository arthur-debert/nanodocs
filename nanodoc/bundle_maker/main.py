#!/usr/bin/env python3
"""
nanodoc-make-bundle - Interactive CLI for creating nanodoc bundles

This module provides an interactive ncurses-based interface for creating
nanodoc bundles by selecting files and specific parts of files.
"""

import curses
import logging
import os
import argparse

from .logging import configure_logging, get_logger
from .operations import load_ui_defs
from .screens.app import App
from .screens.file_selector import FileSelector
from .screens.file_detail import FileDetail
from .screens.bundle_summary import BundleSummary

# Get logger for this module
logger = get_logger("main")


class BundleMaker:
    """Interactive ncurses-based interface for creating nanodoc bundles."""

    def __init__(self, stdscr, ui_defs=None):
        """Initialize the BundleMaker with a curses screen.

        Args:
            stdscr: The curses standard screen
            ui_defs: Optional UI definitions
        """
        self.stdscr = stdscr
        self.ui_defs = ui_defs or load_ui_defs()
        
        logger.info("Initializing BundleMaker")
        
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
        
        logger.info("BundleMaker initialized")
    
    def _init_colors(self):
        """Initialize colors."""
        # Start color mode
        logger.debug("Initializing colors")
        curses.start_color()
        curses.use_default_colors()
        
        # Default color pairs
        curses.init_pair(1, curses.COLOR_WHITE, curses.COLOR_BLUE)  # Header
        curses.init_pair(2, curses.COLOR_GREEN, -1)  # Success
        curses.init_pair(3, curses.COLOR_RED, -1)  # Error
        curses.init_pair(4, curses.COLOR_YELLOW, -1)  # Highlight
        curses.init_pair(5, curses.COLOR_BLACK, curses.COLOR_WHITE)  # Status bar
        logger.debug("Colors initialized")
    
    def register_screens(self):
        """Register all screen classes with the app."""
        logger.debug("Registering screens")
        self.app.register_screen("file_selector", FileSelector)
        self.app.register_screen("file_detail", FileDetail)
        self.app.register_screen("bundle_summary", BundleSummary)
        logger.debug("Screens registered")
    
    def run(self):
        """Run the bundle maker interface."""
        try:
            logger.info("Starting bundle maker interface")
            # Start with the file selector screen
            self.app.run("file_selector")
            logger.info("Bundle maker interface completed")
            return None
        except KeyboardInterrupt:
            logger.info("Bundle maker interface interrupted by user")
            return None  # User cancelled with Ctrl+C or 'q'
        except Exception as e:
            logger.error(f"Error in bundle maker interface: {str(e)}", exc_info=True)
            raise


def main():
    """Main entry point for the nanodoc-make-bundle command."""
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="nanodoc bundle maker")
    parser.add_argument("--ui-defs", help="Path to UI definitions YAML file")
    parser.add_argument("--bundle", help="Path to bundle file to edit")
    parser.add_argument("--log-file", help="Path to log file")
    parser.add_argument("--log-level", 
                      choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
                      default="INFO",
                      help="Log level for console output")
    parser.add_argument("--debug", action="store_true", 
                      help="Enable debug mode (sets log level to DEBUG)")
    args = parser.parse_args()
    
    # Configure logging
    log_level = "DEBUG" if args.debug else args.log_level
    configure_logging(
        log_file=args.log_file,
        console_level=log_level,
        file_level="DEBUG"
    )
    
    logger.info("Bundle maker starting")
    
    # Load UI definitions if specified
    ui_defs = None
    if args.ui_defs:
        logger.info(f"Loading UI definitions from {args.ui_defs}")
        ui_defs = load_ui_defs(args.ui_defs)
    
    # Run the bundle maker
    try:
        return curses.wrapper(lambda stdscr: BundleMaker(stdscr, ui_defs).run())
    except Exception as e:
        logger.critical(f"Fatal error: {str(e)}", exc_info=True)
        return 1


if __name__ == "__main__":
    main()