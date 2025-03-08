################################################################################
# Argument Expansion - Functions that turn arguments into a verified list of
# paths
################################################################################


import logging
import os

logger = logging.getLogger("nanodoc")
logger.setLevel(logging.CRITICAL)  # Start with logging disabled


def parse_line_reference(line_ref):
    """Parse a line reference string into a list of (start, end) tuples.

    Args:
        line_ref (str): The line reference string (e.g., "L5", "L10-20",
                        "L5,L10-20,L30")

    Returns:
        list: A list of (start, end) tuples representing line ranges.

    Raises:
        ValueError: If the line reference is invalid.
    """
    if not line_ref:
        raise ValueError("Empty line reference")

    parts = []
    for part in line_ref.split(","):
        if not part.startswith("L"):
            raise ValueError(f"Invalid line reference format: {part}")

        # Remove the 'L' prefix
        num_part = part[1:]

        if "-" in num_part:
            # Range reference
            try:
                start, end = map(int, num_part.split("-"))
                if start <= 0 or end <= 0:
                    raise ValueError(f"Line numbers must be positive: {part}")
                if start > end:
                    raise ValueError(
                        "Start line must be less than or equal " f"to end line: {part}"
                    )
                parts.append((start, end))
            except ValueError as e:
                if "must be positive" in str(e) or "must be less than" in str(e):
                    raise
                raise ValueError(f"Invalid line range format: {part}")
        else:
            # Single line reference
            try:
                line_num = int(num_part)
                if line_num <= 0:
                    raise ValueError(f"Line number must be positive: {part}")
                parts.append((line_num, line_num))
            except ValueError as e:
                if "must be positive" in str(e):
                    raise
                raise ValueError(f"Invalid line number format: {part}")

    return parts


def get_file_content(file_path, line=None, start=None, end=None, parts=None):
    """Get content from a file, optionally selecting specific lines or ranges.

    Args:
        file_path (str): The path to the file.
        line (int, optional): A specific line number to get (1-indexed).
        start (int, optional): The start line of a range (1-indexed).
        end (int, optional): The end line of a range (1-indexed).
        parts (list, optional): A list of (start, end) tuples representing
                               line ranges.

    Returns:
        str: The selected content from the file.

    Raises:
        FileNotFoundError: If the file does not exist.
        ValueError: If a line reference is out of range.
    """
    try:
        with open(file_path, "r") as f:
            lines = f.readlines()
    except FileNotFoundError:
        raise FileNotFoundError(f"File not found: {file_path}")

    # If no specific parts are requested, return the entire file
    if line is None and start is None and end is None and parts is None:
        return "".join(lines)

    # Convert to 0-indexed for internal use
    max_line = len(lines)

    # Handle single line
    if line is not None:
        if line <= 0 or line > max_line:
            raise ValueError(
                "Line reference out of range: " f"{line} (file has {max_line} lines)"
            )
        return lines[line - 1].rstrip("\n")

    # Handle range
    if start is not None and end is not None:
        if start <= 0 or end <= 0 or start > max_line or end > max_line:
            raise ValueError(
                "Line reference out of range: "
                f"{start}-{end} (file has {max_line} lines)"
            )
        # Join the lines and remove the trailing newline if present
        content = "".join(lines[start - 1 : end])
        return content.rstrip("\n")

    # Handle multiple parts
    if parts is not None:
        result = []
        for start, end in parts:
            if start <= 0 or end <= 0 or start > max_line or end > max_line:
                raise ValueError(
                    "Line reference out of range: "
                    f"{start}-{end} (file has {max_line} lines)"
                )
            result.extend(lines[start - 1 : end])
        # Join the lines and remove the trailing newline if present
        content = "".join(result)
        return content.rstrip("\n")

    # Default case
    return "".join(lines)


def expand_directory(directory, extensions=[".txt", ".md"]):
    """Find all files in a directory with specified extensions.

    This function expands a directory path into a list of file paths.

    Args:
        directory (str): The directory path to search.
        extensions (list): List of file extensions to include.

    Returns:
        list: A sorted list of file paths matching the extensions (not validated).
    """
    logger.debug(
        f"Expanding directory with directory='{directory}', "
        f"extensions='{extensions}'"
    )
    matches = []
    for root, _, filenames in os.walk(directory):
        for filename in filenames:
            if any(filename.endswith(ext) for ext in extensions):
                matches.append(os.path.join(root, filename))
    return sorted(matches)


def expand_bundles(bundle_file):
    """Extract list of files from a bundle file.

    This function expands a bundle file into a list of file paths.

    Args:
        bundle_file (str): Path to the bundle file.

    Returns:
        list: A list of file paths contained in the bundle (not validated).

    Raises:
        FileNotFoundError: If bundle file not found or contains no valid files.
    """
    # Extract file path if there's a line reference
    file_path = bundle_file
    line_ref = None
    if ":L" in bundle_file:
        file_path, line_ref = bundle_file.split(":L", 1)
        line_ref = "L" + line_ref

    logger.debug(f"Expanding bundles from file: {bundle_file}")

    try:
        # If there's a line reference, only read the specified lines
        if line_ref:
            try:
                parts = parse_line_reference(line_ref)
                content = get_file_content(file_path, parts=parts)
                lines = [line.strip() for line in content.splitlines() if line.strip()]
            except ValueError as e:
                raise FileNotFoundError(
                    "Invalid line reference in bundle file: " f"{str(e)}"
                )
        else:
            # Read the entire file
            content = get_file_content(file_path)
            lines = [line.strip() for line in content.splitlines() if line.strip()]
    except FileNotFoundError:
        raise FileNotFoundError(f"Bundle file not found: {file_path}")

    expanded_files = []
    for line in [line for line in lines if line and not line.startswith("#")]:
        expanded_files.append(line)

    # Note: validation is now done separately

    return expanded_files


def is_bundle_file(file_path):
    """Determine if a file is a bundle file by checking its contents.

    A file is considered a bundle if its first non-empty, non-comment line
    points to an existing file.

    Args:
        file_path (str): The path to the file to check.

    Returns:
        bool: True if the file appears to be a bundle file, False otherwise.
    """
    logger.debug(f"Checking if {file_path} is a bundle file")
    try:
        with open(file_path, "r") as f:
            # Check the first few non-empty lines
            for _ in range(5):  # Check up to 5 lines
                line = f.readline().strip()
                if not line:
                    continue
                if line.startswith("#"):  # Skip comment lines
                    continue
                # If this line exists as a file, assume it's a bundle file
                if os.path.isfile(line):
                    return True
                else:
                    # Not a bundle file if a line is not a valid file
                    return False
            # Not a bundle file if none of the first 5 lines are valid files
            return False
    except FileNotFoundError:
        return False
    except Exception as e:
        logger.error(f"Error checking bundle file: {e}")
        return False


def expand_args(args):
    """Expand a list of arguments into a flattened list of file paths.

    This function expands a list of arguments (file paths, directory paths, or
    bundle files) into a flattened list of file paths by calling the appropriate
    expander for each argument.

    Args:
        args (list): A list of file paths, directory paths, or bundle files.

    Returns:
        list: A flattened list of file paths (not validated).
    """
    logger.debug(f"Expanding arguments: {args}")

    def expand_single_arg(arg):
        """Helper function to expand a single argument."""
        logger.debug(f"Expanding argument: {arg}")

        # Extract file path if there's a line reference
        file_path = arg
        if ":L" in arg:
            file_path = arg.split(":L", 1)[0]

        if os.path.isdir(arg):  # Directory path
            return expand_directory(arg)
        elif is_bundle_file(file_path):  # Bundle file
            return expand_bundles(arg)
        else:
            return [arg]  # Regular file path

    # Use list comprehension with sum to flatten the list of lists
    return sum([expand_single_arg(arg) for arg in args], [])


def verify_path(path):
    """Verify that a given path exists, is readable, and is not a directory.

    If the path includes a line reference (e.g., file.txt:L10 or
    file.txt:L5-10), the line reference is validated against the file content.

    Args:
        path (str): The file path to verify.

    Returns:
        str: The verified path (without line reference).

    Raises:
        FileNotFoundError: If the path does not exist.
        PermissionError: If the file is not readable.
        IsADirectoryError: If the path is a directory.
        ValueError: If the line reference is invalid or out of range.
    """
    logger.debug(f"Verifying file path: {path}")

    # Check if the path includes a line reference
    file_path = path
    line_ref = None

    if ":L" in path:
        file_path, line_ref = path.split(":L", 1)
        line_ref = "L" + line_ref

    # Verify the file path
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Error: Path does not exist: {file_path}")
    if not os.access(file_path, os.R_OK):
        raise PermissionError(f"Error: File is not readable: {file_path}")
    if os.path.isdir(file_path):
        raise IsADirectoryError(
            "Error: Path is a directory, not a file: " f"{file_path}"
        )

    # Validate line reference if present
    if line_ref:
        try:
            parts = parse_line_reference(line_ref)
            # Validate that all referenced lines exist in the file
            get_file_content(file_path, parts=parts)
        except ValueError as e:
            raise ValueError(f"Invalid line reference in {path}: {str(e)}")

    return file_path


def file_sort_key(path):
    """Key function for sorting files by name then extension priority."""
    base_name = os.path.splitext(os.path.basename(path))[0]
    ext = os.path.splitext(path)[1]
    # This ensures test_file.txt comes before test_file.md
    ext_priority = 0 if ext == ".txt" else 1 if ext == ".md" else 2
    return (base_name, ext_priority)


def get_files_from_args(srcs):
    """Process the sources and return a list of verified file paths.

    Args:
        srcs (list): List of source file paths, directories, or bundle files.

    Returns:
        list: A list of verified file paths.
    """
    # Phase 1: Expand all arguments into a flat list of file paths
    expanded_files = expand_args(srcs)
    if not expanded_files:
        return []
    # Phase 2: Validate all file paths
    verified_sources = []
    for file_path in expanded_files:
        try:
            verified_sources.append(verify_path(file_path))
        except (FileNotFoundError, PermissionError, IsADirectoryError):
            pass  # Skip invalid files
    # Sort the verified sources with custom sorting
    verified_sources = sorted(verified_sources, key=file_sort_key)
    return verified_sources
