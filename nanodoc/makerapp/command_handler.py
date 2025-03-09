"""
Command handler for the nanodoc bundle maker.

This module provides a command handler that watches a file for commands
and executes them in the app.
"""

import json
import os
import threading
import tempfile
import time
from typing import Any, Callable, Dict, List, Optional


class CommandHandler:
    """Command handler for the bundle maker interface."""

    def __init__(self, command_file: str, log_file: str, app_state: Dict[str, Any]):
        """Initialize the command handler.
        
        Args:
            command_file: The path to the command file
            log_file: The path to the log file
            app_state: The shared application state
        """
        self.command_file = command_file
        self.log_file = log_file
        self.app_state = app_state
        self.response_file = os.path.join(tempfile.gettempdir(), "nanodoc_response.json")
        self.running = False
        self.command_handlers = {}
        self.last_modified = 0
        
        # Create the files if they don't exist
        self._ensure_files_exist()
        
        # Register default commands
        self._register_default_commands()
    
    def _ensure_files_exist(self):
        """Ensure the command and log files exist."""
        # Create the command file if it doesn't exist
        if not os.path.exists(self.command_file):
            with open(self.command_file, 'w') as f:
                f.write('[]')
        
        # Create the log file if it doesn't exist
        if not os.path.exists(self.log_file):
            with open(self.log_file, 'w') as f:
                f.write('[]')
        
        # Get the last modified time of the command file
        self.last_modified = os.path.getmtime(self.command_file)
    
    def _register_default_commands(self):
        """Register default commands."""
        self.register_command('get_state', self._handle_get_state)
        self.register_command('set_state', self._handle_set_state)
        self.register_command('navigate', self._handle_navigate)
        self.register_command('get_focus', self._handle_get_focus)
        self.register_command('send_key', self._handle_send_key)
    
    def register_command(self, command: str, handler: Callable):
        """Register a command handler.
        
        Args:
            command: The command to register
            handler: The handler function for the command
        """
        self.command_handlers[command] = handler
    
    def _handle_get_state(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle the get_state command.
        
        Args:
            params: The command parameters
            
        Returns:
            The current app state
        """
        return {'state': self.app_state}
    
    def _handle_set_state(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle the set_state command.
        
        Args:
            params: The command parameters
            
        Returns:
            The updated app state
        """
        if 'state' in params:
            self.app_state.update(params['state'])
        return {'state': self.app_state}
    
    def _handle_navigate(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle the navigate command.
        
        Args:
            params: The command parameters
            
        Returns:
            The result of the navigation
        """
        if 'screen' in params:
            self.app_state['next_screen'] = params['screen']
            if 'params' in params:
                self.app_state['next_screen_params'] = params['params']
            return {'result': 'success', 'screen': params['screen']}
        return {'result': 'error', 'message': 'No screen specified'}
        
    def _handle_get_focus(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle the get_focus command.
        
        Args:
            params: The command parameters
            
        Returns:
            The current focus information
        """
        focus_info = self.app_state.get('focus', {})
        self._send_response({'focus': focus_info})
        return {'focus': focus_info}
    
    def _handle_send_key(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle the send_key command.
        
        Args:
            params: The command parameters
            
        Returns:
            The result of the key press
        """
        if 'key' in params:
            key = params['key']
            if isinstance(key, str) and len(key) == 1:
                self.app_state['next_key'] = ord(key)
                return {'result': 'success', 'key': key}
            elif isinstance(key, int):
                self.app_state['next_key'] = key
                result = {'result': 'success', 'key': key}
                # Send response with key info
                self._send_response(result)
                return result
        return {'result': 'error', 'message': 'Invalid key'}
    
    def log(self, message: str, data: Optional[Dict[str, Any]] = None):
        """Log a message to the log file.
        
        Args:
            message: The message to log
            data: Optional data to include in the log
        """
        log_entry = {
            'timestamp': time.time(),
            'message': message
        }
        if data:
            log_entry['data'] = data
        
        try:
            # Read existing logs
            with open(self.log_file, 'r') as f:
                logs = json.load(f)
            
            # Add new log entry
            logs.append(log_entry)
            
            # Write updated logs
            with open(self.log_file, 'w') as f:
                json.dump(logs, f, indent=2)
        except Exception as e:
            print(f"Error logging to file: {e}")
            
    def _send_response(self, data: Dict[str, Any]):
        """Send a response to the response file.
        
        Args:
            data: The response data
        """
        try:
            with open(self.response_file, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"Error sending response: {e}")
            
    
    def check_for_commands(self):
        """Check for new commands in the command file."""
        try:
            # Check if the command file has been modified
            current_modified = os.path.getmtime(self.command_file)
            if current_modified <= self.last_modified:
                return
            
            # Update last modified time
            self.last_modified = current_modified
            
            # Read commands from file
            try:
                with open(self.command_file, 'r') as f:
                    content = f.read().strip()
                    if not content:  # Handle empty file
                        commands = []
                    else:
                        commands = json.loads(content)
            except json.JSONDecodeError:
                commands = []  # Reset commands if file is corrupted
            
            # Process commands
            for command in commands:
                if 'command' in command:
                    self._process_command(command)
            
            # Clear the command file
            with open(self.command_file, 'w') as f:
                f.write('[]')
        except Exception as e:
            print(f"Error checking for commands: {e}")
    
    def _process_command(self, command_data: Dict[str, Any]):
        """Process a command.
        
        Args:
            command_data: The command data
        """
        command = command_data.get('command')
        params = command_data.get('params', {})
        
        if command in self.command_handlers:
            try:
                result = self.command_handlers[command](params)
                self.log(f"Executed command: {command}", {
                    'params': params,
                    'result': result
                })
            except Exception as e:
                self.log(f"Error executing command: {command}", {
                    'params': params,
                    'error': str(e)
                })
        else:
            self.log(f"Unknown command: {command}", {
                'params': params
            })
    
    def start(self):
        """Start the command handler."""
        self.running = True
        self.log("Command handler started")
        
        # Start the command handler thread
        self.thread = threading.Thread(target=self._run)
        self.thread.daemon = True
        self.thread.start()
    
    def stop(self):
        """Stop the command handler."""
        self.running = False
        self.log("Command handler stopped")
    
    def _run(self):
        """Run the command handler."""
        while self.running:
            self.check_for_commands()
            time.sleep(0.5)  # Check every 500ms