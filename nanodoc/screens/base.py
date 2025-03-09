"""
Base screen class for the nanodoc bundle maker.

This module provides the base Screen class that all screen classes should inherit from.
It handles common functionality like rendering, key capture, and navigation.
"""

import curses
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional, Tuple


class Screen(ABC):
    """Base class for all screens in the bundle maker interface."""

    def __init__(self, stdscr, ui_defs: Dict[str, Any], app_state: Dict[str, Any]):
        """Initialize the screen.

        Args:
            stdscr: The curses standard screen
            ui_defs: The UI definitions loaded from YAML
            app_state: The shared application state
        """
        self.stdscr = stdscr
        self.ui_defs = ui_defs
        self.app_state = app_state
        self.height, self.width = stdscr.getmaxyx()

        # Set up error handling for curses
        self.safe_mode = True  # Enable safe mode by default

    def _get_string(self, key_path: str) -> str:
        """Get a string from the UI definitions using dot notation path."""
        keys = key_path.split(".")
        value = self.ui_defs["strings"]
        for k in keys:
            if k in value:
                value = value[k]
            else:
                # If key not found, return the key path as fallback
                return f"[{key_path}]"
        return value

    def safe_addstr(self, y: int, x: int, text: str, attr=0) -> None:
        """Safely add a string to the screen, handling curses errors.

        Args:
            y: The y-coordinate
            x: The x-coordinate
            text: The text to add
            attr: The text attributes
        """
        if not self.safe_mode:
            self.stdscr.addstr(y, x, text, attr)
            return

        try:
            # Check if coordinates are within screen bounds
            if y < 0 or y >= self.height or x < 0:
                return

            # Truncate text if it would go off screen
            max_len = self.width - x
            if max_len <= 0:
                return

            display_text = text
            if len(text) > max_len:
                display_text = text[:max_len]

            self.stdscr.addstr(y, x, display_text, attr)
        except curses.error:
            # Ignore curses errors
            pass

    def render_title(self, title: str) -> None:
        """Render the screen title.

        Args:
            title: The title to render
        """
        self.safe_addstr(0, 0, title, curses.A_BOLD | curses.color_pair(1))

    def render_status_line(self, status_text: str) -> None:
        """Render the status line at the bottom of the screen.

        Args:
            status_text: The status text to render
        """
        try:
            self.stdscr.addstr(
                self.height - 1, 0, " " * self.width, curses.color_pair(5)
            )
            self.stdscr.addstr(self.height - 1, 1, status_text, curses.color_pair(5))
        except curses.error:
            pass

    def get_input(self, prompt: str, y: int, x: int) -> str:
        """Get input from the user.

        Args:
            prompt: The prompt to display
            y: The y-coordinate for the input
            x: The x-coordinate for the input

        Returns:
            The user input
        """
        # Make sure y is within screen bounds
        y = min(y, self.height - 2)

        # Display the prompt
        self.safe_addstr(y, x, prompt)
        self.stdscr.refresh()

        # Enable cursor and echo for input
        curses.curs_set(1)
        curses.echo()

        # Create input window
        try:
            input_win = curses.newwin(1, self.width - x - 2, y + 1, x + 2)
            input_win.refresh()
            user_input = input_win.getstr().decode("utf-8").strip()
        except curses.error:
            user_input = ""

        # Disable cursor and echo
        curses.curs_set(0)
        curses.noecho()

        return user_input

    def show_message(self, title: str, message: str, color_pair: int = 1) -> None:
        """Show a message to the user.

        Args:
            title: The message title
            message: The message text
            color_pair: The color pair to use
        """
        self.stdscr.clear()
        self.safe_addstr(0, 0, title, curses.A_BOLD | curses.color_pair(color_pair))
        self.safe_addstr(2, 0, message)
        self.safe_addstr(4, 0, "Press any key to continue...")
        self.stdscr.refresh()
        self.stdscr.getch()

    def show_error(self, message: str) -> None:
        """Show an error message.

        Args:
            message: The error message to display
        """
        self.show_message("ERROR", message, 3)

    def show_success(self, message: str) -> None:
        """Show a success message.

        Args:
            message: The success message to display
        """
        self.show_message("SUCCESS", message, 2)

    def check_global_keys(self, key: int) -> bool:
        """Check if a global key was pressed and handle it.

        Args:
            key: The key that was pressed

        Returns:
            bool: True if a global key was handled, False otherwise
        """
        if key == ord("q") or key == ord("Q"):
            # Quit without confirmation
            raise KeyboardInterrupt
        elif key == ord("h") or key == ord("H"):
            # Show help dialog
            self.show_help()
            return True

        return False

    def show_help(self) -> None:
        """Show the help dialog."""
        self.stdscr.clear()
        self.safe_addstr(
            0,
            0,
            self._get_string("screen_title_help"),
            curses.A_BOLD | curses.color_pair(1),
        )

        # Display help text
        help_text = self._get_string("help_text")
        lines = help_text.strip().split("\n")
        for i, line in enumerate(lines):
            self.safe_addstr(2 + i, 0, line)

        # Wait for a key press
        self.safe_addstr(
            2 + len(lines) + 2, 0, self._get_string("common.continue_prompt")
        )
        self.stdscr.refresh()
        self.stdscr.getch()

    @abstractmethod
    def render(self) -> None:
        """Render the screen."""

    @abstractmethod
    def handle_input(self) -> Tuple[str, Optional[Dict[str, Any]]]:
        """Handle user input.

        Returns:
            Tuple of (next_screen, screen_params) where:
            - next_screen is the name of the next screen to show
            - screen_params is an optional dictionary of parameters to pass to the next screen
        """

    def run(self) -> Tuple[str, Optional[Dict[str, Any]]]:
        """Run the screen.

        Returns:
            Tuple of (next_screen, screen_params) where:
            - next_screen is the name of the next screen to show
            - screen_params is an optional dictionary of parameters to pass to the next screen
        """
        self.stdscr.clear()
        self.render()
        self.stdscr.refresh()
        return self.handle_input()
