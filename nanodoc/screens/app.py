"""
App class for the nanodoc bundle maker.

This module provides the App class that handles screen transitions
and maintains the application state.
"""

import os
import tempfile
import queue
from typing import Any, Dict, Optional, Type

from .base import Screen
from .command_handler import CommandHandler


class App:
    """App class for the bundle maker interface."""

    def __init__(self, stdscr, ui_defs: Dict[str, Any]):
        """Initialize the app.

        Args:
            stdscr: The curses standard screen
            ui_defs: The UI definitions loaded from YAML
        """
        self.stdscr = stdscr
        self.ui_defs = ui_defs
        self.app_state = {
            "content_items": [],
            "current_dir": os.environ.get("PWD", os.getcwd()),
            "selected_files": [],
            "current_file": None,
        }
        self.event_queue = queue.Queue()
        
        self.screens = {}
        self.current_screen = None

        
        # Set up command handler
        self.command_file = os.path.join(tempfile.gettempdir(), "nanodoc_commands.json")
        self.log_file = os.path.join(tempfile.gettempdir(), "nanodoc_log.json")
        self.command_handler = CommandHandler(
            self.command_file,
            self.log_file,
            self.app_state
        )
        # Register event handler
        self.command_handler.register_command('send_event', 
                                             lambda params: self._handle_event(params))
        
        self.command_handler.start()
    def register_screen(self, name: str, screen_class: Type[Screen]) -> None:
        """Register a screen class.

        Args:
            name: The name of the screen
            screen_class: The screen class
        """
        self.screens[name] = screen_class
        
    def _handle_event(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle an event from the command handler.
        
        Args:
            params: The event parameters
            
        Returns:
            The result of handling the event
        """
        if 'event' in params:
            self.event_queue.put(params)
            return {'result': 'success', 'event': params['event']}

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
            
        # Log navigation
        self.command_handler.log(f"Navigating to screen: {screen_name}", params)

        # Create and run the screen
        screen = self.screens[screen_name](self.stdscr, self.ui_defs, self.app_state)
        self.current_screen = screen_name

        # Prepare the screen
        self.stdscr.clear()
        screen.render()
        self.stdscr.refresh()
        
        # Process input and events
        next_screen = None
        next_params = None
        
        while next_screen is None:
            # Check for events from command handler
            try:
                event = self.event_queue.get_nowait()
                if event.get('event') == 'key_press' and 'key' in event:
                    key = event['key']
                    if isinstance(key, str) and len(key) == 1:
                        key = ord(key)
                    # Process the key as if it came from the user
                    next_screen, next_params = screen.handle_input(key)
                elif event.get('event') == 'navigate' and 'screen' in event:
                    next_screen = event['screen']
                    next_params = event.get('params')
            except queue.Empty:
                # No events, get input from user
                key = self.stdscr.getch()
                next_screen, next_params = screen.handle_input(key)

            # Re-render the screen after each input
            self.stdscr.clear()
            screen.render()
            self.stdscr.refresh()

        # Navigate to the next screen if specified
        if next_screen:
            self.navigate_to(next_screen, next_params)

    def run(self, initial_screen: str = "file_selector") -> None:
        """Run the app.

        Args:
            initial_screen: The name of the initial screen to show
        """
        try:
            self.navigate_to(initial_screen)
        except KeyboardInterrupt:
            self.command_handler.log("Application terminated by user")
        finally:
            # Stop the command handler
            self.command_handler.stop()
            self.command_handler.log("Application closed")
