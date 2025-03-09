"""
Test the logging system for the bundle maker.

This module tests the logging configuration and functionality.
"""

import os
import tempfile
import unittest

from nanodoc.bundle_maker.logging import (
    configure_logging,
    get_logger,
    get_log_file,
    set_log_level,
)


class TestLogging(unittest.TestCase):
    """Test the logging system."""

    def setUp(self):
        """Set up the test."""
        # Create a test log directory
        self.log_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "tmp", "nanodoc-logs", "test")
        os.makedirs(self.log_dir, exist_ok=True)
        
        # Create a test log file
        self.log_file = os.path.join(tempfile.gettempdir(), "test_nanodoc_bundle_maker.log")
        
        # Configure logging
        configure_logging(
            log_file=self.log_file,
            console_level="ERROR",  # Minimize console output during tests
            file_level="DEBUG",
            ui_level="DEBUG",
            screens_level="DEBUG",
            widgets_level="DEBUG",
        )
    
    def tearDown(self):
        """Clean up after the test."""
        # Remove the log file
        if os.path.exists(self.log_file) and "test_nanodoc_bundle_maker.log" in self.log_file:
            os.remove(self.log_file)
    
    def test_get_logger(self):
        """Test getting a logger."""
        logger = get_logger("test")
        self.assertIsNotNone(logger)
        
        # Log a message
        logger.info("Test message")
        
        # Check that the message was logged to the file
        with open(self.log_file, "r") as f:
            log_content = f.read()
        
        self.assertIn("Test message", log_content)
    
    def test_set_log_level(self):
        """Test setting the log level."""
        # Set the log level for a component
        set_log_level("test", "DEBUG")
        
        # Get the logger
        logger = get_logger("test")
        
        # Log messages at different levels
        logger.debug("Debug message")
        logger.info("Info message")
        logger.warning("Warning message")
        logger.error("Error message")
        
        # Check that all messages were logged to the file
        with open(self.log_file, "r") as f:
            log_content = f.read()
        
        self.assertIn("Debug message", log_content)
        self.assertIn("Info message", log_content)
        self.assertIn("Warning message", log_content)
        self.assertIn("Error message", log_content)
        
        # Set the log level to WARNING
        set_log_level("test", "WARNING")
        
        # Clear the log file
        with open(self.log_file, "w") as f:
            f.write("")
        
        # Log messages at different levels
        logger.debug("Debug message 2")
        logger.info("Info message 2")
        logger.warning("Warning message 2")
        logger.error("Error message 2")
        
        # Check that only WARNING and ERROR messages were logged to the file
        with open(self.log_file, "r") as f:
            log_content = f.read()
        
        self.assertNotIn("Debug message 2", log_content)
        self.assertNotIn("Info message 2", log_content)
        self.assertIn("Warning message 2", log_content)
        self.assertIn("Error message 2", log_content)
    
    def test_get_log_file(self):
        """Test getting the log file path."""
        log_file = get_log_file()
        self.assertIsNotNone(log_file)
        self.assertTrue(os.path.exists(os.path.dirname(log_file)))


if __name__ == "__main__":
    unittest.main()