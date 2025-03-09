#!/usr/bin/env python3
"""
Reset the command and log files for the nanodoc bundle maker.
"""

import json
import os
import tempfile

def main():
    """Reset the command and log files."""
    command_file = os.path.join(tempfile.gettempdir(), "nanodoc_commands.json")
    log_file = os.path.join(tempfile.gettempdir(), "nanodoc_log.json")
    
    # Reset command file
    with open(command_file, 'w') as f:
        json.dump([], f)
    
    # Reset log file
    with open(log_file, 'w') as f:
        json.dump([], f)
    
    print(f"Reset command file: {command_file}")
    print(f"Reset log file: {log_file}")

if __name__ == "__main__":
    main()