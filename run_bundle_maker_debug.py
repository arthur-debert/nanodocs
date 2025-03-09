#!/usr/bin/env python3
"""
Run the bundle maker with debug logging enabled.

This script runs the bundle maker with debug logging enabled and
specifies a log file in the current directory.
"""

import os
import sys
import tempfile
from datetime import datetime
import pathlib

# Add the parent directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

# Import the bundle maker

from nanodoc.makerapp.logging import get_logger
from nanodoc.makerapp.main import main
logger = get_logger("bmaker")

# Log directory

if __name__ == "__main__":
    # Create a timestamped log file name
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Set up command line arguments
    
    # Print information
    print(f"Running bundle maker with debug logging enabled")
    print("Press Ctrl+C or 'q' to quit")
    print()
    
    # Run the bundle maker
    try:
        main()
    except KeyboardInterrupt:
        print("\nBundle maker terminated by user")
    except Exception as e:
        print(f"\nError: {str(e)}")
    
    # Print log file location
    print(f"\nLog file: {os.path.abspath(log_file)}")
    print("You can examine this file to see detailed logs of the application's behavior")