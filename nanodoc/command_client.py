#!/usr/bin/env python3
"""
Command client for the nanodoc bundle maker.

This script demonstrates how to send commands to the bundle maker app
and read the log file to see the results.
"""

import json
import os
import tempfile
import time
from typing import Any, Dict, List, Optional


class CommandClient:
    """Client for sending commands to the bundle maker app."""

    def __init__(self):
        """Initialize the command client."""
        self.command_file = os.path.join(tempfile.gettempdir(), "nanodoc_commands.json")
        self.log_file = os.path.join(tempfile.gettempdir(), "nanodoc_log.json")
        
        # Ensure the command file exists
        if not os.path.exists(self.command_file):
            with open(self.command_file, 'w') as f:
                f.write('[]')
    
    def send_command(self, command: str, params: Optional[Dict[str, Any]] = None) -> None:
        """Send a command to the bundle maker app.
        
        Args:
            command: The command to send
            params: Optional parameters for the command
        """
        if params is None:
            params = {}
        
        # Read existing commands
        try:
            with open(self.command_file, 'r') as f:
                commands = json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            commands = []
        
        # Add new command
        commands.append({
            'command': command,
            'params': params
        })
        
        # Write updated commands
        with open(self.command_file, 'w') as f:
            json.dump(commands, f, indent=2)
        
        print(f"Sent command: {command}")
    
    def send_key(self, key: str) -> None:
        """Send a key press event to the bundle maker app.
        
        Args:
            key: The key to send (a single character)
        """
        self.send_command('send_event', {
            'event': 'key_press',
            'key': key
        })
    
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
    parser.add_argument('--key', type=str, help='Send a key press event')
    parser.add_argument('--navigate', type=str, help='Send a navigation event')
    parser.add_argument('--state', action='store_true', help='Get the current state')
    parser.add_argument('--logs', action='store_true', help='Print the logs')
    
    args = parser.parse_args()
    
    client = CommandClient()
    
    if args.key:
        client.send_key(args.key)
    
    if args.navigate:
        client.navigate_to(args.navigate)
    
    if args.state:
        state = client.get_state()
        print(f"Current state: {json.dumps(state, indent=2)}")
    
    if args.logs:
        client.print_logs()
    
    # If no arguments were provided, print help
    if not (args.key or args.navigate or args.state or args.logs):
        parser.print_help()


if __name__ == '__main__':
    main()