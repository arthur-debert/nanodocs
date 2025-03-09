#!/usr/bin/env python3
"""
nanodoc-make-bundle - Interactive CLI for creating nanodoc bundles

This module provides an interactive ncurses-based interface for creating
nanodoc bundles by selecting files and specific parts of files.
"""

import curses
import logging
import os
import re
from typing import List, Optional, Tuple, Union

from .data import Bundle, ContentItem, LineRange, save_bundle
from .files import expand_directory, get_file_content

logger = logging.getLogger("nanodoc")
logger.setLevel(logging.CRITICAL)  # Start with logging disabled


class BundleMaker:
    """Interactive ncurses-based interface for creating nanodoc bundles."""

    def __init__(self, stdscr):
        """Initialize the BundleMaker with a curses screen.

        Args:
            stdscr: The curses standard screen
        """
        self.stdscr = stdscr
        self.content_items: List[ContentItem] = []
        self.current_dir = os.environ.get("PWD", os.getcwd())
        self.max_files_to_show = 20
        self.max_preview_lines = 10
        self.max_context_lines = 20
        self.height, self.width = stdscr.getmaxyx()
        self.formatting = None  # Will be set from nanodoc.formatting

        # Initialize colors
        curses.start_color()
        curses.use_default_colors()
        curses.init_pair(1, curses.COLOR_WHITE, curses.COLOR_BLUE)  # Header
        curses.init_pair(2, curses.COLOR_GREEN, -1)  # Success
        curses.init_pair(3, curses.COLOR_RED, -1)  # Error
        curses.init_pair(4, curses.COLOR_YELLOW, -1)  # Highlight
        curses.init_pair(5, curses.COLOR_BLACK, curses.COLOR_WHITE)  # Status bar

        # Set up the screen
        curses.curs_set(0)  # Hide cursor
        self.stdscr.clear()
        self.stdscr.refresh()

    def run(self) -> Optional[str]:
        """Run the bundle maker interface.

        Returns:
            str: Path to the saved bundle file, or None if cancelled
        """
        try:
            # Get directory to search for files
            search_dir = self._get_directory()
            if search_dir is None:
                return None  # User cancelled

            # Main loop for adding files to the bundle
            while True:
                # Show current bundle contents
                self._show_bundle_contents()

                # Ask user to select a file
                file_path = self._select_file(search_dir)
                if file_path is None:
                    break  # User is done adding files

                # Process the selected file
                self._process_file(file_path)

            # Save the bundle if there are any content items
            if self.content_items:
                return self._save_bundle()
            return None

        except KeyboardInterrupt:
            return None  # User cancelled with Ctrl+C

    def _get_directory(self) -> Optional[str]:
        """Prompt the user for a directory to search for files.

        Returns:
            str: The selected directory path, or None if cancelled
        """
        self.stdscr.clear()
        self.stdscr.addstr(
            0, 0, "NANODOC BUNDLE MAKER", curses.A_BOLD | curses.color_pair(1)
        )
        self.stdscr.addstr(
            2,
            0,
            "Enter a directory to search for files (or press Enter for current directory):",
        )
        self.stdscr.addstr(3, 0, f"Current directory: {self.current_dir}")
        self.stdscr.refresh()

        # Enable cursor and echo for input
        curses.curs_set(1)
        curses.echo()

        # Get user input
        input_win = curses.newwin(1, self.width - 2, 5, 2)
        input_win.refresh()
        user_input = input_win.getstr().decode("utf-8").strip()

        # Disable cursor and echo
        curses.curs_set(0)
        curses.noecho()

        if user_input == "":
            return self.current_dir
        elif user_input.lower() == "q":
            return None  # User cancelled
        else:
            # Expand ~ to home directory
            expanded_path = os.path.expanduser(user_input)

            # Check if the path exists and is a directory
            if os.path.isdir(expanded_path):
                return os.path.abspath(expanded_path)
            else:
                self._show_error(f"Invalid directory: {expanded_path}")
                return self._get_directory()  # Try again

    def _select_file(self, directory: str) -> Optional[str]:
        """Let the user select a file from the directory.

        Args:
            directory: The directory to search for files

        Returns:
            str: The selected file path, or None if done adding files
        """
        self.stdscr.clear()
        self.stdscr.addstr(0, 0, "SELECT A FILE", curses.A_BOLD | curses.color_pair(1))
        self.stdscr.addstr(1, 0, f"Directory: {directory}")
        self.stdscr.addstr(2, 0, "Enter a file path, or:")
        self.stdscr.addstr(3, 0, "- Enter 'q' to finish and save the bundle")
        self.stdscr.addstr(4, 0, "- Enter 'd' to change directory")

        # Get list of text and markdown files in the directory
        files = expand_directory(directory, extensions=[".txt", ".md"])

        # Display files with constraints
        if files:
            self.stdscr.addstr(6, 0, "Available files:")
            for i, file_path in enumerate(files[: self.max_files_to_show]):
                rel_path = os.path.relpath(file_path, directory)
                self.stdscr.addstr(7 + i, 2, f"{i+1}. {rel_path}")

            if len(files) > self.max_files_to_show:
                self.stdscr.addstr(
                    7 + self.max_files_to_show,
                    2,
                    f"... and {len(files) - self.max_files_to_show} more files",
                )
        else:
            self.stdscr.addstr(
                6, 0, "No text or markdown files found in this directory."
            )

        # Prompt for file selection
        prompt_line = 8 + min(len(files), self.max_files_to_show) + 1
        self.stdscr.addstr(
            prompt_line,
            0,
            "Enter file number, path, 'q' to finish, or 'd' to change directory: ",
        )
        self.stdscr.refresh()

        # Enable cursor and echo for input
        curses.curs_set(1)
        curses.echo()

        # Get user input
        input_win = curses.newwin(1, self.width - 2, prompt_line + 1, 2)
        input_win.refresh()
        user_input = input_win.getstr().decode("utf-8").strip()

        # Disable cursor and echo
        curses.curs_set(0)
        curses.noecho()

        if user_input.lower() == "q":
            return None  # User is done adding files
        elif user_input.lower() == "d":
            new_dir = self._get_directory()
            if new_dir:
                return self._select_file(new_dir)
            return self._select_file(
                directory
            )  # Stay in current directory if cancelled
        elif user_input.isdigit():
            # User entered a file number
            file_num = int(user_input)
            if 1 <= file_num <= len(files) and file_num <= self.max_files_to_show:
                return files[file_num - 1]
            else:
                self._show_error("Invalid file number")
                return self._select_file(directory)  # Try again
        else:
            # User entered a file path
            file_path = user_input

            # If not an absolute path, make it relative to the current directory
            if not os.path.isabs(file_path):
                file_path = os.path.join(directory, file_path)

            # Check if the file exists
            if os.path.isfile(file_path):
                return file_path
            else:
                self._show_error(f"File not found: {file_path}")
                return self._select_file(directory)  # Try again

    def _process_file(self, file_path: str) -> None:
        """Process a selected file, allowing the user to add parts of it to the bundle.

        Args:
            file_path: The path to the file to process
        """
        while True:
            # Show file preview
            filename = os.path.basename(file_path)
            nice_title = self._format_nice_title(filename)
            self.stdscr.clear()
            self.stdscr.addstr(1, 0, f"File: {file_path}")

            try:
                # Get file content for preview
                content = get_file_content(file_path)
                lines = content.splitlines()

                # Display title
                self.stdscr.addstr(
                    0, 0, nice_title, curses.A_BOLD | curses.color_pair(1)
                )

                # Show initial preview with formatted line numbers
                for i, line in enumerate(lines[: self.max_preview_lines]):
                    line_num = i + 1
                    self.stdscr.addstr(
                        3 + i, 0, f"{line_num:02d}: {line[:self.width-4]}"
                    )

                if len(lines) > self.max_preview_lines:
                    self.stdscr.addstr(3 + self.max_preview_lines, 0, "...")
                    self.stdscr.addstr(
                        4 + self.max_preview_lines, 0, f"Total lines: {len(lines)}"
                    )

                # Ask what to do with this file
                options_line = 5 + self.max_preview_lines + 1
                self.stdscr.addstr(options_line, 0, "Actions:", curses.A_BOLD)
                self.stdscr.addstr(options_line + 1, 2, "[SPACE] Add entire file")
                self.stdscr.addstr(options_line + 2, 2, "[0-9] Select part of the file")
                self.stdscr.addstr(options_line + 3, 2, "[B] Skip this file")
                self.stdscr.addstr(options_line + 5, 0, "Press a key to continue...")
                self.stdscr.refresh()

                # Get user choice
                choice = self.stdscr.getch()

                if choice == ord("a") or choice == ord(" "):
                    # Add entire file (a or SPACE)
                    self._add_file_part(file_path, 1, "X")
                    self._show_success(
                        f"Added entire file: {os.path.basename(file_path)}"
                    )
                    break
                elif 48 <= choice <= 57:  # 0-9 keys
                    # Select part of the file
                    if self._select_file_part(file_path, lines):
                        # If user added a part, ask if they want to add more parts
                        if not self._ask_add_more_parts(file_path):
                            break
                    else:
                        # User cancelled selection
                        break
                elif choice == ord("b") or choice == ord("B"):
                    # Skip this file
                    break

            except Exception as e:
                self._show_error(f"Error processing file: {str(e)}")
                break

    def _format_nice_title(self, filename):
        """Format a filename in 'nice' style (similar to nanodoc's formatting)."""
        # Remove extension
        basename = os.path.splitext(filename)[0]

        # Replace - and _ with spaces
        nice_name = re.sub(r"[-_]", " ", basename)

        # Title case
        return nice_name.title()

    def _interactive_line_selection(
        self, file_path: str, lines: List[str]
    ) -> Optional[Tuple[int, Union[int, str]]]:
        """Interactive line selection interface.

        Args:
            file_path: Path to the file
            lines: Lines of the file

        Returns:
            Tuple of (start_line, end_line) or None if cancelled
        """
        filename = os.path.basename(file_path)
        nice_title = self._format_nice_title(filename)
        max_lines = len(lines)

        # State variables
        current_input = ""
        selection_mode = "start"  # "start" or "end"
        start_line = None

        while True:
            self.stdscr.clear()

            # Display title
            self.stdscr.addstr(0, 0, nice_title, curses.A_BOLD | curses.color_pair(1))

            # Display file content with line numbers
            display_lines = min(max_lines, self.max_preview_lines)
            for i in range(display_lines):
                line_num = i + 1
                # Format line number with padding
                line_num_str = f"{line_num:02d}"

                # Determine if this line should be highlighted
                highlight = False
                if (
                    selection_mode == "start"
                    and current_input
                    and int(current_input or "0") == line_num
                ):
                    highlight = True
                elif selection_mode == "end" and start_line is not None:
                    if (
                        start_line
                        <= line_num
                        <= (int(current_input or "0") if current_input else start_line)
                    ):
                        highlight = True

                # Display the line
                if highlight:
                    self.stdscr.addstr(
                        i + 2,
                        0,
                        f"{line_num_str}: {lines[i][:self.width-4]}",
                        curses.color_pair(4) | curses.A_BOLD,
                    )
                else:
                    self.stdscr.addstr(
                        i + 2, 0, f"{line_num_str}: {lines[i][:self.width-4]}"
                    )

            # If there are more lines, show an indicator
            if max_lines > self.max_preview_lines:
                self.stdscr.addstr(
                    display_lines + 2,
                    0,
                    f"... ({max_lines - display_lines} more lines)",
                )

            # Status bar
            status_line = display_lines + 3
            status_text = ""
            if selection_mode == "start":
                if current_input:
                    line_num = min(int(current_input), max_lines)
                    status_text = f"Start: L{line_num}"
                else:
                    status_text = "Start: Type line number"
            else:  # selection_mode == "end"
                if current_input:
                    line_num = min(int(current_input), max_lines)
                    status_text = f"Range: L{start_line}-{line_num}"
                else:
                    status_text = f"Range: L{start_line}-? (Type end line)"

            # Display status bar
            self.stdscr.addstr(status_line, 0, " " * self.width, curses.color_pair(5))
            self.stdscr.addstr(status_line, 1, status_text, curses.color_pair(5))

            # Action menu
            action_line = status_line + 2
            self.stdscr.addstr(action_line, 0, "Actions:", curses.A_BOLD)

            if selection_mode == "start":
                self.stdscr.addstr(action_line + 1, 2, "[0-9] Type line number")
                self.stdscr.addstr(action_line + 2, 2, "[SPACE] Add entire file")
                self.stdscr.addstr(action_line + 3, 2, "[TAB] Set start line")
                self.stdscr.addstr(action_line + 4, 2, "[B] Go back")
            else:  # selection_mode == "end"
                self.stdscr.addstr(action_line + 1, 2, "[0-9] Type line number")
                self.stdscr.addstr(action_line + 2, 2, "[ENTER] Select range")
                self.stdscr.addstr(action_line + 3, 2, "[B] Go back")

            self.stdscr.refresh()

            # Get user input
            key = self.stdscr.getch()

            # Process key
            if key == ord("b") or key == ord("B"):
                # Go back
                if selection_mode == "end":
                    # Go back to start selection
                    selection_mode = "start"
                    current_input = str(start_line)
                    start_line = None
                else:
                    # Cancel selection
                    return None
            elif key == ord(" "):
                # Add entire file
                if selection_mode == "start":
                    return (1, "X")
            elif key == 9:  # TAB key
                # Set start line
                if selection_mode == "start" and current_input:
                    start_line = min(int(current_input), max_lines)
                    selection_mode = "end"
                    current_input = ""
            elif key == 10 or key == 13:  # ENTER key
                # Select range
                if selection_mode == "end" and start_line is not None:
                    end_line = min(int(current_input or str(start_line)), max_lines)
                    return (start_line, end_line)
                elif selection_mode == "start" and current_input:
                    # Single line selection
                    line_num = min(int(current_input), max_lines)
                    return (line_num, line_num)
            elif 48 <= key <= 57:  # 0-9 keys
                # Add digit to current input
                digit = chr(key)
                new_input = current_input + digit

                # Validate that the number is within range
                if int(new_input) <= max_lines:
                    current_input = new_input
            elif key == 127 or key == 8:  # BACKSPACE key
                # Remove last digit
                if current_input:
                    current_input = current_input[:-1]

        return None

    def _select_file_part(self, file_path: str, lines: List[str]) -> bool:
        """Let the user select a part of a file to add to the bundle.

        Args:
            file_path: The path to the file
            lines: The lines of the file

        Returns:
            bool: True if a part was added, False otherwise
        """
        # Use the interactive line selection interface
        result = self._interactive_line_selection(file_path, lines)
        if result:
            start_line, end_line = result
            self._add_file_part(file_path, start_line, end_line)
            msg = (
                f"Added line {start_line}"
                if start_line == end_line
                else f"Added lines {start_line}-{end_line}"
            )
            self._show_success(f"{msg} from {os.path.basename(file_path)}")
            return True
        return False  # User cancelled

    def _show_line_context(self, lines: List[str], line_num: int) -> None:
        """Show context around a specific line.

        Args:
            lines: The lines of the file
            line_num: The line number to show context around (1-indexed)
        """
        self.stdscr.clear()
        self.stdscr.addstr(0, 0, "LINE CONTEXT", curses.A_BOLD | curses.color_pair(1))

        # Calculate context range
        start = max(1, line_num - 2)
        end = min(len(lines), line_num + self.max_context_lines - 3)

        # Show context
        self.stdscr.addstr(2, 0, f"Showing lines {start} to {end}:")

        for i in range(start, end + 1):
            # Highlight the selected line
            if i == line_num:
                self.stdscr.addstr(
                    3 + (i - start),
                    0,
                    f"{i}: {lines[i-1][:self.width-4]}",
                    curses.color_pair(4) | curses.A_BOLD,
                )
            else:
                self.stdscr.addstr(
                    3 + (i - start), 0, f"{i}: {lines[i-1][:self.width-4]}"
                )

        self.stdscr.refresh()

    def _get_line_number(
        self, prompt: str, min_val: int, max_val: int, file_content: str = None
    ) -> Optional[int]:
        """Get a line number from the user.

        Args:
            prompt: The prompt to display
            min_val: The minimum valid line number
            max_val: The maximum valid line number
            file_content: The content of the file to display (optional)

        Returns:
            int: The selected line number, or None if cancelled
        """
        self.stdscr.clear()
        self.stdscr.addstr(0, 0, "SELECT LINE", curses.A_BOLD | curses.color_pair(1))

        # Show file content if provided
        content_start_line = 2
        if file_content:
            self.stdscr.addstr(content_start_line, 0, "File content:")
            content_start_line += 1

            # Display file content (first 10 lines or less)
            lines = file_content.splitlines()[: self.max_preview_lines]
            for i, line in enumerate(lines):
                self.stdscr.addstr(
                    content_start_line + i, 0, f"{i+1}: {line[:self.width-4]}"
                )

            content_start_line += len(lines) + 1

        # Show prompt and instructions
        self.stdscr.addstr(
            content_start_line, 0, f"Valid range: {min_val} to {max_val}"
        )
        self.stdscr.addstr(content_start_line + 1, 0, prompt)
        self.stdscr.addstr(content_start_line + 2, 0, "Enter 'q' to cancel")
        self.stdscr.refresh()

        # Enable cursor and echo for input
        curses.curs_set(1)
        curses.echo()

        # Get user input
        input_win = curses.newwin(1, self.width - 2, content_start_line + 3, 2)
        input_win.refresh()
        user_input = input_win.getstr().decode("utf-8").strip()

        # Disable cursor and echo
        curses.curs_set(0)
        curses.noecho()

        if user_input.lower() == "q":
            return None  # User cancelled

        try:
            line_num = int(user_input)
            if min_val <= line_num <= max_val:
                return line_num
            else:
                self._show_error(f"Line number must be between {min_val} and {max_val}")
                return self._get_line_number(
                    prompt, min_val, max_val, file_content
                )  # Try again
        except ValueError:
            self._show_error("Invalid input. Please enter a number.")
            return self._get_line_number(
                prompt, min_val, max_val, file_content
            )  # Try again

    def _add_file_part(self, file_path: str, start: int, end: Union[int, str]) -> None:
        """Add a part of a file to the bundle.

        Args:
            file_path: The path to the file
            start: The start line number (1-indexed)
            end: The end line number (1-indexed) or "X" for end of file
        """
        # Create a LineRange object
        line_range = LineRange(start, end)

        # Check if we already have a ContentItem for this file
        for item in self.content_items:
            if item.file_path == file_path:
                # Add this range to the existing ContentItem
                item.ranges.append(line_range)
                return

        # Create a new ContentItem
        original_arg = file_path
        if end != "X" or start != 1:
            # Add line reference to original_arg if not the entire file
            range_str = f"L{start}" if start == end else f"L{start}-{end}"
            original_arg = f"{file_path}:{range_str}"

        content_item = ContentItem(
            original_arg=original_arg,
            file_path=file_path,
            ranges=[line_range],
            content=None,
        )

        # Add to our list
        self.content_items.append(content_item)

    def _ask_add_more_parts(self, file_path: str) -> bool:
        """Ask if the user wants to add more parts from the same file.

        Args:
            file_path: The path to the file

        Returns:
            bool: True if the user wants to add more parts, False otherwise
        """
        self.stdscr.clear()
        self.stdscr.addstr(
            0, 0, "ADD MORE PARTS?", curses.A_BOLD | curses.color_pair(1)
        )
        self.stdscr.addstr(
            2, 0, f"Do you want to add more parts from {os.path.basename(file_path)}?"
        )
        self.stdscr.addstr(4, 0, "y - Yes, add more parts")
        self.stdscr.addstr(5, 0, "n - No, move to next file")
        self.stdscr.refresh()

        choice = self.stdscr.getch()
        return choice == ord("y")

    def _show_bundle_contents(self) -> None:
        """Show the current contents of the bundle."""
        self.stdscr.clear()
        self.stdscr.addstr(
            0, 0, "BUNDLE CONTENTS", curses.A_BOLD | curses.color_pair(1)
        )

        if not self.content_items:
            self.stdscr.addstr(2, 0, "Bundle is empty. Add some files to get started.")
        else:
            self.stdscr.addstr(
                2, 0, f"Current bundle has {len(self.content_items)} items:"
            )

            # Group ContentItems by file path
            file_groups = {}
            for item in self.content_items:
                if item.file_path not in file_groups:
                    file_groups[item.file_path] = []
                file_groups[item.file_path].append(item)

            # Display grouped items
            line = 4
            for file_path, items in file_groups.items():
                self.stdscr.addstr(line, 0, os.path.basename(file_path))
                line += 1

                for i, item in enumerate(items):
                    for j, range_obj in enumerate(item.ranges):
                        if range_obj.start == 1 and range_obj.end == "X":
                            range_str = "entire file"
                        elif range_obj.start == range_obj.end:
                            range_str = f"line {range_obj.start}"
                        else:
                            end_str = range_obj.end if range_obj.end != "X" else "end"
                            range_str = f"lines {range_obj.start}-{end_str}"

                        self.stdscr.addstr(line, 2, f"- {range_str}")
                        line += 1

                line += 1  # Add space between files

        self.stdscr.addstr(self.height - 1, 0, "Press any key to continue...")
        self.stdscr.refresh()
        self.stdscr.getch()

    def _save_bundle(self) -> str:
        """Save the bundle to a file.

        Returns:
            str: The path to the saved bundle file
        """
        self.stdscr.clear()
        self.stdscr.addstr(0, 0, "SAVE BUNDLE", curses.A_BOLD | curses.color_pair(1))
        self.stdscr.addstr(
            2, 0, "Enter a filename for the bundle (default: nanodoc-bundle.txt):"
        )
        self.stdscr.refresh()

        # Enable cursor and echo for input
        curses.curs_set(1)
        curses.echo()

        # Get user input
        input_win = curses.newwin(1, self.width - 2, 4, 2)
        input_win.refresh()
        user_input = input_win.getstr().decode("utf-8").strip()

        # Disable cursor and echo
        curses.curs_set(0)
        curses.noecho()

        # Use default filename if none provided
        bundle_path = user_input if user_input else "nanodoc-bundle.txt"

        # If not an absolute path, make it relative to the current directory
        if not os.path.isabs(bundle_path):
            bundle_path = os.path.join(self.current_dir, bundle_path)

        try:
            # Create a Bundle object
            bundle = Bundle(file_path=bundle_path, content_items=self.content_items)

            # Save the bundle
            save_bundle(bundle)

            self._show_success(f"Bundle saved to {bundle_path}")
            return bundle_path

        except Exception as e:
            self._show_error(f"Error saving bundle: {str(e)}")
            return self._save_bundle()  # Try again

    def _show_error(self, message: str) -> None:
        """Show an error message.

        Args:
            message: The error message to display
        """
        self.stdscr.clear()
        self.stdscr.addstr(0, 0, "ERROR", curses.A_BOLD | curses.color_pair(3))
        self.stdscr.addstr(2, 0, message)
        self.stdscr.addstr(4, 0, "Press any key to continue...")
        self.stdscr.refresh()
        self.stdscr.getch()

    def _show_success(self, message: str) -> None:
        """Show a success message.

        Args:
            message: The success message to display
        """
        self.stdscr.clear()
        self.stdscr.addstr(0, 0, "SUCCESS", curses.A_BOLD | curses.color_pair(2))
        self.stdscr.addstr(2, 0, message)
        self.stdscr.addstr(4, 0, "Press any key to continue...")
        self.stdscr.refresh()
        self.stdscr.getch()


def main():
    """Main entry point for the nanodoc-make-bundle command."""
    return curses.wrapper(lambda stdscr: BundleMaker(stdscr).run())


if __name__ == "__main__":
    main()
