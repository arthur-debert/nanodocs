"""
File Detail screen for the nanodoc bundle maker.

This module provides a minimal implementation of the File Detail screen.
"""

import os
import curses
from typing import Any, Dict, Optional, Tuple, List

from ..operations import load_file_content, format_range_display
from .base import Screen


class FileDetail(Screen):
    """File Detail screen for the bundle maker interface."""

    def __init__(self, stdscr, ui_defs: Dict[str, Any], app_state: Dict[str, Any]):
        """Initialize the File Detail screen."""
        super().__init__(stdscr, ui_defs, app_state)
        
        # Get current file
        self.current_file = self.app_state.get("current_file", "No file selected")
        self.file_content = []
        self.line_count = 0
        self.current_ranges = []
        self.scroll_position = 0
        self.input_mode = None  # None, 'start', or 'end'
        self.current_input = ""
        self.start_line = None
        
        # Load file content if file exists
        self._load_file_content()
        
        # Get current ranges for this file from app state
        self._load_current_ranges()
    
    def _load_file_content(self) -> None:
        """Load the content of the current file."""
        try:
            # Use operations module to load file content
            self.file_content, self.line_count = load_file_content(self.current_file)
        except (FileNotFoundError, PermissionError) as e:
            self.show_error(str(e))
            self.file_content = []
            self.line_count = 0
    
    def _load_current_ranges(self) -> None:
        """Load the current ranges for this file from app state."""
        content_items = self.app_state.get("content_items", [])
        for item in content_items:
            if item["file_path"] == self.current_file:
                self.current_ranges = item.get("ranges", [])
                break
    
    def render(self) -> None:
        """Render the File Detail screen."""
        # Render title
        self.render_title("NANODOC BUNDLE MAKER / FILE DETAIL")
        
        # Render file info
        self.safe_addstr(2, 0, f"Current File:", curses.A_BOLD)
        self.safe_addstr(3, 2, self.current_file, curses.color_pair(4))
        
        # Render file content with line numbers
        content_start_y = 4
        visible_lines = min(self.height - 10, self.line_count)
        
        if not self.file_content:
            self.safe_addstr(content_start_y, 0, "File is empty or could not be loaded.")
        else:
            # Display line numbers and content
            for i in range(visible_lines):
                line_idx = i + self.scroll_position
                if line_idx < self.line_count:
                    # Format line number with padding
                    line_num = f"{line_idx + 1:02d}"
                    
                    # Check if this line is in any selected range
                    is_selected = False
                    for r in self.current_ranges:
                        start = r.get("start", 1)
                        end = r.get("end")
                        if end is None:  # Entire file
                            is_selected = True
                            break
                        elif start <= (line_idx + 1) <= end:
                            is_selected = True
                            break
                    
                    # Display line with appropriate highlighting
                    if is_selected:
                        self.safe_addstr(content_start_y + i, 0, f"{line_num} | ", curses.A_BOLD | curses.color_pair(2))
                        self.safe_addstr(content_start_y + i, 5, self.file_content[line_idx].rstrip(), curses.A_BOLD | curses.color_pair(2))
                    else:
                        self.safe_addstr(content_start_y + i, 0, f"{line_num} | ", curses.color_pair(4))
                        self.safe_addstr(content_start_y + i, 5, self.file_content[line_idx].rstrip())
        
        # Render current ranges
        ranges_y = content_start_y + visible_lines + 1
        self.safe_addstr(ranges_y, 0, "Selected Ranges:", curses.A_BOLD)
        
        if not self.current_ranges:
            self.safe_addstr(ranges_y + 1, 2, "No ranges selected. Press SPACE to select entire file.", curses.color_pair(3))
        else:
            for i, r in enumerate(self.current_ranges):
                self.safe_addstr(ranges_y + 1 + i, 2, f"{i+1}. {format_range_display(r)}", curses.color_pair(2))
        
        # Render input mode if active
        if self.input_mode:
            input_y = ranges_y + (len(self.current_ranges) if self.current_ranges else 1) + 2
            if self.input_mode == 'start':
                self.safe_addstr(input_y, 0, "Enter start line:", curses.A_BOLD)
                self.safe_addstr(input_y, 17, self.current_input, curses.A_BOLD | curses.color_pair(4))
                self.safe_addstr(input_y + 1, 0, "Press TAB when done to enter end line")
            elif self.input_mode == 'end':
                self.safe_addstr(input_y, 0, f"Start line: {self.start_line}", curses.A_BOLD)
                self.safe_addstr(input_y + 1, 0, "Enter end line:", curses.A_BOLD)
                self.safe_addstr(input_y + 1, 15, self.current_input, curses.A_BOLD | curses.color_pair(4))
                self.safe_addstr(input_y + 2, 0, "Press ENTER when done to add range")
        
        # Render controls
        self.safe_addstr(self.height - 4, 0, "Controls (↑/↓ or k/j to scroll):", curses.A_BOLD)
        self.safe_addstr(self.height - 3, 2, "SPACE: Select entire file  |  0-9: Start line selection  |  TAB/ENTER: Confirm")
        self.safe_addstr(self.height - 2, 2, "↑/↓: Scroll  |  b: Back to Bundle Summary  |  q: Quit")
        
        # Show scroll indicator if needed
        if self.line_count > visible_lines:
            scroll_pct = min(100, int(100 * (self.scroll_position + visible_lines) / self.line_count))
            self.safe_addstr(self.height - 1, self.width - 15, f"Scroll: {scroll_pct}%", curses.color_pair(4))
            
            # Show more indicator if there are more lines below
            if self.scroll_position + visible_lines < self.line_count:
                self.safe_addstr(content_start_y + visible_lines - 1, self.width - 10, "↓ more ↓", curses.A_BOLD | curses.color_pair(4))
    
    def handle_input(self, key: int) -> Tuple[str, Optional[Dict[str, Any]]]:
        """Handle user input.
        
        Args:
            key: The key that was pressed
            
        Returns:
            Tuple of (next_screen, screen_params)
        """
        # Check for global keys
        if self.check_global_keys(key):
            return "file_detail", None
        
        if key == ord('q'):
            # Quit
            raise KeyboardInterrupt
            
        elif key == ord('b'):
            # Go back to Bundle Summary
            self._save_ranges()
            return "bundle_summary", None
            
        elif key == ord(' '):
            # Select entire file
            self.current_ranges = [{"start": 1, "end": None}]
            return "file_detail", None
            
        elif key == curses.KEY_UP or key == ord('k'):  # Up arrow or vim 'k'
            # Scroll up
            if self.scroll_position > 0:
                self.scroll_position -= 1
            return "file_detail", None
            
        elif key == curses.KEY_DOWN or key == ord('j'):  # Down arrow or vim 'j'
            # Scroll down
            if self.scroll_position < max(0, self.line_count - (self.height - 10)):
                self.scroll_position += 1
            return "file_detail", None
            
        elif key in [ord(str(i)) for i in range(10)]:
            # Start line selection
            if self.input_mode is None:
                self.input_mode = 'start'
                self.current_input = chr(key)
                return "file_detail", None
            elif self.input_mode in ['start', 'end']:
                # Add digit to current input
                self.current_input += chr(key)
                return "file_detail", None
                
        elif key == ord('\t'):  # Tab key
            # Confirm start line and move to end line selection
            if self.input_mode == 'start' and self.current_input:
                try:
                    self.start_line = int(self.current_input)
                    if 1 <= self.start_line <= self.line_count:
                        self.input_mode = 'end'
                        self.current_input = ""
                    else:
                        self.show_error(f"Line number out of range (1-{self.line_count})")
                        self.input_mode = None
                        self.current_input = ""
                except ValueError:
                    self.show_error("Invalid line number")
                    self.input_mode = None
                    self.current_input = ""
            return "file_detail", None
            
        elif key == ord('\n'):  # Enter key
            # Confirm end line and add range
            if self.input_mode == 'end' and self.current_input and self.start_line is not None:
                try:
                    end_line = int(self.current_input)
                    if self.start_line <= end_line <= self.line_count:
                        self.current_ranges.append({"start": self.start_line, "end": end_line})
                    else:
                        self.show_error(f"End line must be >= start line and <= {self.line_count}")
                except ValueError:
                    self.show_error("Invalid line number")
                
                # Reset input state
                self.input_mode = None
                self.current_input = ""
                self.start_line = None
            return "file_detail", None
        
        # Default: stay on this screen
        return "file_detail", None
    def _save_ranges(self) -> None:
        """Save the current ranges to the app state."""
        content_items = self.app_state.get("content_items", [])
        for item in content_items:
            if item["file_path"] == self.current_file:
                item["ranges"] = self.current_ranges
                break