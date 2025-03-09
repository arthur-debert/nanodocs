"""
Logging configuration for the nanodoc bundle maker.

This module provides logging configuration for the bundle maker application.
It sets up loggers for different components and provides a file handler for
logging to a file.
"""

import logging
import os
import atexit
import datetime
import sys
import tempfile
from typing import Dict, Optional

# Log directory - ensure it's always an absolute path
LOG_DIR = '/tmp/nanodoc/logs/'
if not os.path.isabs(LOG_DIR):
    LOG_DIR = os.path.abspath(LOG_DIR)

# Create log directory if it doesn't exist
os.makedirs(LOG_DIR, exist_ok=True)

# Default log file path with timestamp
DEFAULT_LOG_FILE = os.path.join(LOG_DIR, f"nanodoc_bundle_maker_{datetime.datetime.now().strftime('%Y%m%d')}.log")
loggers: Dict[str, logging.Logger] = {}
handlers: Dict[str, logging.Handler] = {}

# Log levels
LOG_LEVELS = {
    "DEBUG": logging.DEBUG,
    "INFO": logging.INFO,
    "WARNING": logging.WARNING,
    "ERROR": logging.ERROR,
    "CRITICAL": logging.CRITICAL,
}


def get_logger(name: str) -> logging.Logger:
    """Get a logger instance for the specified name.
    
    Args:
        name: The name of the logger
        
    Returns:
        A logger instance
    """
    if name in loggers:
        return loggers[name]
    
    logger = logging.getLogger(f"nanodoc.bundle_maker.{name}")
    loggers[name] = logger
    
    return logger


def configure_logging(
    log_file: Optional[str] = None,
    console_level: str = "INFO",
    file_level: str = "DEBUG",
    ui_level: str = "DEBUG",
    screens_level: str = "INFO",
    widgets_level: str = "DEBUG",
) -> None:
    """Configure logging for the bundle maker application.
    
    Args:
        log_file: Path to the log file (default: nanodoc_bundle_maker.log in temp dir)
        console_level: Log level for console output
        file_level: Log level for file output
        ui_level: Log level for UI components
        screens_level: Log level for screen components
        widgets_level: Log level for widget components
    """
    # Use default log file if not specified
    if log_file is None:
        log_file = DEFAULT_LOG_FILE
    
    # Convert string levels to logging levels
    console_level = LOG_LEVELS.get(console_level.upper(), logging.INFO)
    file_level = LOG_LEVELS.get(file_level.upper(), logging.DEBUG)
    ui_level = LOG_LEVELS.get(ui_level.upper(), logging.DEBUG)
    screens_level = LOG_LEVELS.get(screens_level.upper(), logging.INFO)
    widgets_level = LOG_LEVELS.get(widgets_level.upper(), logging.DEBUG)
    
    # Configure root logger
    root_logger = logging.getLogger("nanodoc")
    root_logger.setLevel(logging.DEBUG)
    
    # Remove existing handlers
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    # Create console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(console_level)
    console_format = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    handlers["console"] = console_handler
    console_handler.setFormatter(console_format)
    root_logger.addHandler(console_handler)
    
    # Create file handler
    file_handler = logging.FileHandler(log_file, mode="w")
    file_handler.setLevel(file_level)
    file_format = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    handlers["file"] = file_handler
    file_handler.setFormatter(file_format)
    root_logger.addHandler(file_handler)
    
    # Configure component loggers
    configure_component_logger("ui", ui_level)
    configure_component_logger("screens", screens_level)
    configure_component_logger("widgets", widgets_level)
    
    # Log configuration
    root_logger.info(f"Logging configured: console={console_level}, file={file_level}")
    root_logger.info(f"Log file: {log_file}")
    root_logger.info(f"Component levels: ui={ui_level}, screens={screens_level}, widgets={widgets_level}")
    
    # Register cleanup function to close handlers
    atexit.register(_cleanup_handlers)


def _cleanup_handlers():
    """Close all handlers to prevent resource warnings."""
    for handler in handlers.values():
        handler.close()


def configure_component_logger(component: str, level: int) -> None:
    """Configure a logger for a specific component.
    
    Args:
        component: The component name
        level: The log level
    """
    logger = logging.getLogger(f"nanodoc.bundle_maker.{component}")
    logger.setLevel(level)
    
    # Create the logger instance in the loggers dict
    loggers[component] = logger


def set_log_level(component: str, level: str) -> None:
    """Set the log level for a specific component.
    
    Args:
        component: The component name
        level: The log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    """
    if component not in loggers:
        configure_component_logger(component, logging.INFO)
    
    level_value = LOG_LEVELS.get(level.upper(), logging.INFO)
    loggers[component].setLevel(level_value)
    
    # Log the level change
    root_logger = logging.getLogger("nanodoc")
    root_logger.info(f"Log level for {component} set to {level}")


def get_log_file() -> str:
    """Get the current log file path.
    
    Returns: 
        The path to the log file
    """
    return DEFAULT_LOG_FILE