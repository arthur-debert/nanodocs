#!/usr/bin/env python3
"""
Command client for the nanodoc bundle maker.

This script provides a client for sending commands to the bundle maker app
and reading the log file to see the results.
"""

import json
import os
import tempfile
import time
import curses
from typing import Any, Dict, List, Optional

# Map of special key names to curses key codes
KEY_MAPPING = {
    'KEY_UP': curses.KEY_UP,
    'KEY_DOWN': curses.KEY_DOWN,
    'KEY_LEFT': curses.KEY_LEFT,
    'KEY_RIGHT': curses.KEY_RIGHT,
    'KEY_ENTER': 10,  # Enter key
    'KEY_BACKSPACE': curses.KEY_BACKSPACE,
    'KEY_HOME': curses.KEY_HOME,
    'KEY_END': curses.KEY_END,
    'KEY_NPAGE': curses.KEY_NPAGE,  # Page Down
    'KEY_PPAGE': curses.KEY_PPAGE,  # Page Up
    'KEY_F1': curses.KEY_F1,
    'KEY_F2': curses.KEY_F2,
    'KEY_F3': curses.KEY_F3,
    'KEY_F4': curses.KEY_F4,
    'KEY_F5': curses.KEY_F5,
}

class CommandClient:
    """Client for sending commands to the bundle maker app."""

    def __init__(self):
        """Initialize the command client."""
        self.command_file = os.path.join(tempfile.gettempdir(), "nanodoc_commands.json")
        self.log_file = os.path.join(tempfile.gettempdir(), "nanodoc_log.json")
        self.response_file = os.path.join(tempfile.gettempdir(), "nanodoc_response.json")
        
        # Ensure the command file exists
        if not os.path.exists(self.command_file):
            self._reset_command_file()
        self._reset_command_file()  # Always reset the command file on initialization
    
    def send_command(self, command: str, params: Optional[Dict[str, Any]] = None) -> None:
        """Send a command to the bundle maker app.
        
        Args:
            command: The command to send
            params: Optional parameters for the command
        """
        if params is None:
            params = {}
        
        # Reset response file
        self._reset_response_file()
        
        # Write the command directly to the file
        with open(self.command_file, 'w') as f:
            json.dump([{
                'command': command,
                'params': params
            }], f, indent=2)
            
        print(f"Sent command: {command}")
    
    def _reset_command_file(self):
        """Reset the command file to an empty array."""
        try:
            with open(self.command_file, 'w') as f:
                f.write('[]')
        except Exception as e:
            print(f"Error resetting command file: {e}")
    
    def _reset_log_file(self):
        """Reset the log file to an empty array."""
        with open(self.log_file, 'w') as f:
            f.write('[]')
            
    def _reset_response_file(self):
        """Reset the response file to an empty object."""
        try:
            with open(self.response_file, 'w') as f:
                f.write('{}')
        except Exception as e:
            print(f"Error resetting response file: {e}")
    
    def send_key(self, key: str) -> None:
        """Send a key press event to the bundle maker app.
        
        Args:
            key: The key to send (a single character or special key name)
        """
        key_value = key
        
        # Handle special keys
        if key in KEY_MAPPING:
            key_value = KEY_MAPPING[key]
        elif len(key) == 1:
            key_value = key  # Single character key
            
        # Print the key code for debugging
        if isinstance(key_value, int):
            print(f"Sending key code: {key_value}")
        else:
            print(f"Sending key: {key_value}")
            
        self.send_command('send_event', {
            'event': 'key_press',
            'key': key_value
        })
        
        # Wait a moment for the response
        time.sleep(0.5)
        
        # Get and print the response
        self.get_response()
    
    def navigate_to(self, screen: str, params: Optional[Dict[str, Any]] = None) -> None:
        """Send a navigation event to the bundle maker app.
        
        Args:
            screen: The screen to navigate to
            params: Optional parameters for the screen
        """
        event_params = {
            'event': 'navigate',
            'screen': screen
        }
        if params:
            event_params['params'] = params
        
        self.send_command('send_event', event_params)
    
    def get_state(self) -> Dict[str, Any]:
        """Get the current state of the bundle maker app.
        
        Returns:
            The current state
        """
        self.send_command('get_state')
        time.sleep(0.5)  # Wait for the command to be processed
        return self.read_logs()
    
    def read_logs(self) -> List[Dict[str, Any]]:
        """Read the log file.
        
        Returns:
            The logs
        """
        try:
            with open(self.log_file, 'r') as f:
                logs = json.load(f)
            return logs
        except (json.JSONDecodeError, FileNotFoundError):
            return []
            
    def get_response(self) -> Dict[str, Any]:
        """Get the response from the last command.
        
        Returns:
            The response data
        """
        try:
            with open(self.response_file, 'r') as f:
                content = f.read().strip()
                if not content:
                    return {}
                response = json.loads(content)
            print(f"Response: {json.dumps(response, indent=2)}")
            return response
        except (json.JSONDecodeError, FileNotFoundError) as e:
            print(f"Error reading response: {e}")
            return {}
    
    def print_logs(self) -> None:
        """Print the logs."""
        logs = self.read_logs()
        for log in logs:
            timestamp = log.get('timestamp', 0)
            message = log.get('message', '')
            data = log.get('data', {})
            print(f"[{timestamp}] {message}")
            if data:
                print(f"  Data: {json.dumps(data, indent=2)}")


def main():
    """Main entry point for the command client."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Command client for the nanodoc bundle maker')
    parser.add_argument('--key', type=str, help='Send a key press event (e.g., "a", "KEY_UP", "KEY_DOWN")')
    parser.add_argument('--navigate', type=str, help='Send a navigation event')
    parser.add_argument('--state', action='store_true', help='Get the current state')
    parser.add_argument('--logs', action='store_true', help='Print the logs')
    parser.add_argument('--focus', action='store_true', help='Get the current focus')
    
    args = parser.parse_args()
    
    client = CommandClient()
    
    if args.key:
        client.send_key(args.key)
    
    if args.navigate:
        client.navigate_to(args.navigate)
    
    if args.state:
        state = client.get_state()
        print(f"Current state: {json.dumps(state, indent=2)}")
        
    if args.focus:
        client.send_command('get_focus')
        time.sleep(0.5)
        client.get_response()
    
    if args.logs:
        client.print_logs()
    
    # If no arguments were provided, print help
    if not (args.key or args.navigate or args.state or args.logs or args.focus):
        parser.print_help()


if __name__ == '__main__':
    main()