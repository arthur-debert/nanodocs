# Bundle Maker Logging System

The bundle maker application includes a comprehensive logging system to help
with debugging and troubleshooting. This document explains how to use the
logging system.

## Log Levels

The logging system supports the following log levels, in order of increasing
severity:

1. DEBUG - Detailed information, typically of interest only when diagnosing
   problems
2. INFO - Confirmation that things are working as expected
3. WARNING - An indication that something unexpected happened, or may happen in
   the future
4. ERROR - Due to a more serious problem, the software has not been able to
   perform some function
5. CRITICAL - A serious error, indicating that the program itself may be unable
   to continue running

## Log Components

The logging system is organized into components, each with its own logger:

- `ui` - Base UI components
- `widgets` - UI widgets
- `screens` - Screen components
- `main` - Main application code

Each component can have its own log level, allowing you to control the verbosity
of logs for different parts of the application.

## Log File Location

All log files are stored in the `/tmpmp/nanodoc-logs` directory by default. This directory is created automatically if it doesn't exist. Each log file is named with a timestamp to avoid overwriting previous logs.

## Command-Line Options

The bundle maker application supports the following command-line options for
logging:

- `--log-file PATH` - Specify the path to the log file (defaults to tmp/nanodoc-logs directory)
- `--log-level LEVEL` - Set the console log level (DEBUG, INFO, WARNING, ERROR,
  CRITICAL)
- `--debug` - Enable debug mode (sets log level to DEBUG)

Example:

```bash
python -m nanodoc.bundle_maker --debug --log-file tmp/nanodoc-logs/bundle_maker.log
```

## Debug Script

For convenience, a debug script is provided that runs the bundle maker with
debug logging enabled:

```bash
./run_bundle_maker_debug.py
```

This script creates a timestamped log file in the `/tmpmp/nanodoc-logs` directory and sets the
log level to DEBUG.

## Viewing Logs

The log file contains detailed information about the application's behavior.
Each log entry includes:

- Timestamp
- Logger name
- Log level
- Message

Example log entry:

```log
2025-03-09 01:00:00,000 - nanodoc.bundle_maker.ui - DEBUG - Widget created: file_list at (0, 0) with size (80, 24)
```

## Adding Logging to Your Code

To add logging to your code, use the `get_logger` function from the logging
module:

```python
from nanodoc.bundle_maker.logging import get_logger

logger = get_logger("your_component")

# Log messages at different levels
logger.debug("Debug message")
logger.info("Info message")
logger.warning("Warning message")
logger.error("Error message")
logger.critical("Critical message")
```

## Setting Log Levels Programmatically

You can set the log level for a component programmatically using the
`set_log_level` function:

```python
from nanodoc.bundle_maker.logging import set_log_level

set_log_level("your_component", "DEBUG")
```

## Testing the Logging System

A test script is provided to verify the logging system:

```bash
python -m unittest tests.test_logging
```

This script tests the basic functionality of the logging system, including
getting loggers, setting log levels, and logging to a file.
