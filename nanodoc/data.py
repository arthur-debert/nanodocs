import os
from dataclasses import dataclass
from typing import List, Optional, Tuple, Union


@dataclass
class LineRange:
    """A class representing a range of lines in a file.

    Attributes:
        start (int): The start line number (1-indexed).
        end (Union[int, str]): The end line number (1-indexed) or 'X' for end of file.
    """

    start: int
    end: Union[int, str]  # Can be an integer or 'X' for end of file

    def is_single_line(self) -> bool:
        """Check if this range represents a single line."""
        return self.start == self.end and isinstance(self.end, int)

    def is_full_file(self) -> bool:
        """Check if this range represents the entire file."""
        return self.start == 1 and self.end == "X"

    def normalize(self, max_lines: int) -> Tuple[int, int]:
        """Convert to actual line numbers based on file length.

        Args:
            max_lines (int): The total number of lines in the file.

        Returns:
            tuple: A tuple of (start, end) line numbers.
        """
        end = max_lines if self.end == "X" else self.end
        return (self.start, end)

    def to_string(self) -> str:
        """Convert to string representation for display."""
        if self.is_single_line():
            return f"L{self.start}"
        elif self.end == "X":
            return f"L{self.start}-X"
        else:
            return f"L{self.start}-{self.end}"


@dataclass
class ContentItem:
    """A class representing a file and its line ranges.

    Attributes:
        original_arg (str): The original argument used to specify this content.
        file_path (str): The path to the file.
        ranges (List[LineRange]): A list of LineRange objects.
        content (Optional[str]): The cached content from the file.
    """

    original_arg: str
    file_path: str
    ranges: List[LineRange]
    content: Optional[str] = None

    def validate(self) -> bool:
        """Validate that the file exists and ranges are valid.

        Returns:
            bool: True if the content item is valid.

        Raises:
            FileNotFoundError: If the file does not exist.
            PermissionError: If the file is not readable.
            IsADirectoryError: If the path is a directory.
            ValueError: If a line reference is invalid or out of range.
        """
        # Check file existence and readability
        if not os.path.exists(self.file_path):
            raise FileNotFoundError(f"File not found: {self.file_path}")
        if not os.access(self.file_path, os.R_OK):
            raise PermissionError(f"File is not readable: {self.file_path}")
        if os.path.isdir(self.file_path):
            raise IsADirectoryError(
                f"Path is a directory, not a file: {self.file_path}"
            )

        # Validate ranges against file content
        with open(self.file_path, "r") as f:
            lines = f.readlines()

        max_lines = len(lines)
        for range_obj in self.ranges:
            start, end = range_obj.normalize(max_lines)
            if start <= 0 or end <= 0 or start > max_lines or end > max_lines:
                raise ValueError(
                    f"Line reference out of range: {range_obj.to_string()} "
                    f"(file has {max_lines} lines)"
                )
            if start > end:
                raise ValueError(
                    f"Start line must be less than or equal to end line: {range_obj.to_string()}"
                )

        return True

    def is_valid(self) -> bool:
        """Check if the content item is valid without raising exceptions."""
        try:
            return self.validate()
        except Exception:
            return False

    def load_content(self) -> str:
        """Load and cache the content from the file."""
        if self.content is not None:
            return self.content

        with open(self.file_path, "r") as f:
            all_lines = f.readlines()

        max_lines = len(all_lines)
        result = []

        for range_obj in self.ranges:
            start, end = range_obj.normalize(max_lines)
            result.extend(all_lines[start - 1 : end])

        self.content = "".join(result).rstrip("\n")
        return self.content

    def get_content(self) -> str:
        """Get the content, loading it if necessary."""
        if self.content is None:
            return self.load_content()
        return self.content
