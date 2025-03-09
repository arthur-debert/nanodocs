"""
Navigation class for the nanodoc bundle maker.

This module provides the Navigation class that handles screen transitions
and maintains the application state.
"""

from typing import Any, Dict, Optional, Type

from .base import Screen


class Navigation:
    """Navigation class for the bundle maker interface."""

    def __init__(self, stdscr, ui_defs: Dict[str, Any]):
        """Initialize the navigation.

        Args:
            stdscr: The curses standard screen
            ui_defs: The UI definitions loaded from YAML
        """
        self.stdscr = stdscr
        self.ui_defs = ui_defs
        self.app_state = {
            "content_items": [],
            "current_dir": None,
            "selected_files": [],
            "current_file": None,
        }
        self.screens = {}
        self.current_screen = None

    def register_screen(self, name: str, screen_class: Type[Screen]) -> None:
        """Register a screen class.

        Args:
            name: The name of the screen
            screen_class: The screen class
        """
        self.screens[name] = screen_class

    def navigate_to(
        self, screen_name: str, params: Optional[Dict[str, Any]] = None
    ) -> None:
        """Navigate to a screen.

        Args:
            screen_name: The name of the screen to navigate to
            params: Optional parameters to pass to the screen

        Raises:
            ValueError: If the screen is not registered
        """
        if screen_name not in self.screens:
            raise ValueError(f"Screen '{screen_name}' not registered")

        # Update app state with params
        if params:
            self.app_state.update(params)

        # Create and run the screen
        screen = self.screens[screen_name](self.stdscr, self.ui_defs, self.app_state)
        self.current_screen = screen_name

        # Run the screen and get the next screen to navigate to
        next_screen, next_params = screen.run()

        # Navigate to the next screen if specified
        if next_screen:
            self.navigate_to(next_screen, next_params)

    def run(self, initial_screen: str = "file_selector") -> None:
        """Run the navigation.

        Args:
            initial_screen: The name of the initial screen to show
        """
        try:
            self.navigate_to(initial_screen)
        except KeyboardInterrupt:
            # User cancelled with Ctrl+C or 'q'
            pass
