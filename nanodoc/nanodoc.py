#! /usr/bin/env python3
""""
# nanodocs

nanodocs is an ultra-lightweight documentation generator. no frills: concat
multiples files into a single document, adding a title separator.

## FEATURES

- Combine multiple text files
- Title Separator
- Flexible file selection
- [optional] Line Numbers: either per file or global (useful for addressing
  sections)
- [optional] Add table of contents

text files into a single document with formatted headers and optional line
numbering. It can process files provided as arguments or automatically find
`.txt` and `.md` files in the current directory.

## Usage

```bash
nanodocs [options] [file1.txt file2.txt ...]
```

## Specifying Files

nanodocs offers three ways to specify the files you want to bundle:

1. **Explicit File List:** Provide a list of files directly as arguments.

    ```bash
    nanodocs file1.txt file2.md chapter3.txt
    ```

2. **Directory:** Specify a directory, and nanodocs will include all `.txt` and
    `.md` files found within it.

    ```bash
    nanodocs docs/
    ```

3. **Bundle File:** Create a text file (e.g., `bundle.txt`) where each line
    contains the path to a file you want to include. nanodocs will read this
    file and bundle the listed files.

    ```text
    # bundle.txt
    file1.txt
    docs/chapter2.md
    /path/to/another_file.txt
    ```

    ```bash
    nanodocs bundle.txt
    ```

## Options

- `-v, --verbose`: Enable verbose output
- `-n`: Enable per-file line numbering (01, 02, etc.)
- `-nn`: Enable global line numbering (001, 002, etc.)
- `--toc`: Include a table of contents at the beginning
| - `--no-header`: Hide file headers completely
| - `--header-seq`: Add sequence numbers to headers
|   - `numerical`: Use numbers (1., 2., etc.)
|   - `letter`: Use letters (a., b., etc.)
|   - `roman`: Use roman numerals (i., ii., etc.)
| - `--header-style`: Change how filenames are displayed
|   - `filename` (default): Just the filename
|   - `path`: Full file path
|   - `nice`: Formatted title (removes extension, replaces - and _ with spaces, title case, adds original filename in parentheses)
- `-h, --help`: Show this help message

Between files, a separator line is inserted with the format:

```bash
########################## File Name  #########################################
```

The script will exit with an error if no files are found to bundle.

## Examples

```bash
nanodocs -n intro.txt chapter1.txt           # Bundle with per-file numbering
nanodocs -nn --toc                           # Bundle all files with TOC and global numbers
nanodocs --toc -v                            # Verbose bundle with TOC
nanodocs some_directory                      # Add all files in directory
| nanodocs --no-header file1.txt file2.txt     # Hide headers
| nanodocs --header-seq=roman file1.txt        # Use roman numerals (i., ii., etc.)
| nanodocs --header-style=nice file1.txt       # Use nice formatting (Title Case (filename.txt))
nanodocs  bundle_file                         # bundle_file is a txt docuument with files paths on lines
```

"""
import argparse
import os
import glob
import sys
import logging

import re

# Version and configuration constants
VERSION = "0.1.0"
LINE_WIDTH = 80

# Custom exception for bundle file errors
class BundleError(Exception):
    """Custom exception for handling errors related to bundle files."""
    pass

# Initialize logger at the module level - disabled by default
logger = logging.getLogger("nanodoc")
logger.setLevel(logging.CRITICAL)  # Start with logging disabled

def setup_logging(to_stderr=False, enabled=False):
    """Configure logging based on requirements.
    
    Args:
        to_stderr (bool): If True, logs to stderr instead of stdout.
        enabled (bool): If True, sets logging level to DEBUG, otherwise CRITICAL.
        
    Returns:
        logger: Configured logging object.
    """
    global logger
    if not logger.hasHandlers():  # Only set up logging once
        # Set initial log level
        level = logging.DEBUG if enabled else logging.CRITICAL
        logger.setLevel(level)
        
        # Create handler to the appropriate stream
        stream = sys.stderr if to_stderr else sys.stdout
        handler = logging.StreamHandler(stream)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    else:
        # If handlers are already set, just adjust the level
        level = logging.DEBUG if enabled else logging.CRITICAL
        logger.setLevel(level)
    return logger

def create_header(text, char="#", header_seq=None, seq_index=0, header_style=None, original_path=None):
    """Create a formatted header with the given text.
    
    Args:
        text (str): The text to include in the header.
        char (str): The character to use for the header border.
        header_seq (str): The header sequence type (numerical, letter, roman, or None).
        seq_index (int): The index of the file in the sequence.
        header_style (str): The header style (filename, path, nice, or None).
        original_path (str): The original file path (used for path and nice styles).
        
    Returns:
        str: A formatted header string with the text centered.
    """
    logger.debug(f"Creating header with text='{text}', char='{char}'")
    # padding = (LINE_WIDTH - len(text) - 2) // 2

    # Apply header style if specified
    if header_style and original_path:
        if header_style == "path":
            # Use the full file path
            text = original_path
        elif header_style == "nice":
            # Remove extension, replace - and _ with spaces, title case, then add filename in parentheses
            filename = os.path.basename(original_path)
            basename = os.path.splitext(filename)[0]  # Remove extension
            
            # Replace - and _ with spaces
            nice_name = re.sub(r'[-_]', ' ', basename)
            
            # Title case
            nice_name = nice_name.title()
            
            # Add filename in parentheses
            text = f"{nice_name} ({filename})"
    
    # Apply sequence prefix if header_seq is specified
    if header_seq:
        if header_seq == "numerical":
            # Numerical sequence: 1., 2., etc.
            prefix = f"{seq_index + 1}. "
            text = prefix + text
        elif header_seq == "letter":
            # Letter sequence: a., b., etc.
            # ASCII 'a' is 97, so we add seq_index to get the right letter
            letter = chr(97 + (seq_index % 26))
            prefix = f"{letter}. "
            text = prefix + text
        elif header_seq == "roman":
            # Roman numerals: i., ii., etc.
            roman_numerals = ['i', 'ii', 'iii', 'iv', 'v', 'vi', 'vii', 'viii', 'ix', 'x', 'xi', 'xii', 'xiii', 'xiv', 'xv']
            prefix = f"{roman_numerals[seq_index % len(roman_numerals)]}. "
            text = prefix + text
    
    # Left-adjusted header (no # characters)
    header = text
    # Adjust if the header is shorter than LINE_WIDTH due to odd padding
    # header += char * (LINE_WIDTH - len(header))
    return header

def expand_directory(directory, extensions=[".txt", ".md"]):
    """Find all files in a directory with specified extensions.
    
    Args:
        directory (str): The directory path to search.
        extensions (list): List of file extensions to include.
        
    Returns:
        list: A sorted list of file paths matching the extensions.
    """
    logger.debug(f"Expanding directory with directory='{directory}', extensions='{extensions}'")
    matches = []
    for root, _, filenames in os.walk(directory):
        for filename in filenames:
            if any(filename.endswith(ext) for ext in extensions):
                matches.append(os.path.join(root, filename))
    return sorted(matches)

def verify_path(path):
    """Verify that a given path exists and is a file.
    
    Args:
        path (str): The file path to verify.
        
    Returns:
        str: The verified path.
        
    Raises:
        FileNotFoundError: If the path is not a valid file.
    """
    logger.debug(f"Verifying path: {path}")
    if not os.path.isfile(path):
        raise FileNotFoundError(f"Error: Path is not a file: {path}")
    return path

def expand_bundles(bundle_file):
    """Extract list of files from a bundle file.
    
    Args:
        bundle_file (str): Path to the bundle file.
        
    Returns:
        list: A list of valid file paths contained in the bundle.
        
    Raises:
        BundleError: If bundle file not found or contains no valid files.
    """
    logger.debug(f"Expanding bundles from file: {bundle_file}")
    try:
        with open(bundle_file, "r") as f:
            lines = [line.strip() for line in f if line.strip()]  # Skip empty lines
    except FileNotFoundError:
        raise BundleError(f"Bundle file not found: {bundle_file}")
    
    expanded_files = []
    for line in lines:
        if not os.path.isfile(line):
            logger.warning(f"File not found in bundle: {line}")  # Log the missing file
        else:
            expanded_files.append(line)
    
    if not expanded_files:
        raise BundleError(f"No valid files found in bundle: {bundle_file}")

    return expanded_files

def get_source_files(source):
    """Get list of source files based on the type of input.
    
    Args:
        source (str): A file path, directory path, or bundle file.
        
    Returns:
        list: A list of source file paths.
    """
    logger.debug(f"Getting source files for: {source}")
    if os.path.isdir(source):
        return sorted(expand_directory(source))
    elif is_bundle_file(source):
        return expand_bundles(source)
    else:
        return [source]

def process_file(file_path, line_number_mode, line_counter, show_header=True, header_seq=None, seq_index=0, header_style=None):
    """Process a single file and format its content.
    
    Args:
        file_path (str): The path of the file to process.
        line_number_mode (str): The line numbering mode ('file', 'all', or None).
        line_counter (int): The current global line counter.
        
        show_header (bool): Whether to show the header.
        header_seq (str): The header sequence type (numerical, letter, roman, or None).
        seq_index (int): The index of the file in the sequence.
        header_style (str): The header style (filename, path, nice, or None).
    Returns:
        tuple: (str, int) Processed file content with header and line numbers,
               and the number of lines in the file.
    """
    logger.debug(f"Processing file: {file_path}, line_number_mode: {line_number_mode}, line_counter: {line_counter}")
    try:
        with open(file_path, "r") as f:
            lines = f.readlines()
    except FileNotFoundError:
        return f"Error: File not found: {file_path}\n", 0

    output = ""
    if show_header:
        header = "\n" + create_header(os.path.basename(file_path), header_seq=header_seq, seq_index=seq_index, header_style=header_style, original_path=file_path) + "\n\n"
        output = header
    

    for i, line in enumerate(lines):
        line_number = ""
        if line_number_mode == "all":
            line_number = f"{line_counter + i + 1:4d}: "
        elif line_number_mode == "file":
            line_number = f"{i + 1:4d}: "
        output += line_number + line
    return output, len(lines)

def process_all(verified_sources, line_number_mode, generate_toc, show_header=True, header_seq=None, header_style=None):
    """Process all source files and combine them.
    
    Args:
        verified_sources (list): List of verified source file paths.
        line_number_mode (str): Line numbering mode ('file', 'all', or None).
        generate_toc (bool): Whether to generate a table of contents.
        
        show_header (bool): Whether to show headers.
        header_seq (str): The header sequence type (numerical, letter, roman, or None).
        header_style (str): The header style (filename, path, nice, or None).
    Returns:
        str: The combined content of all files with formatting.
    """
    logger.debug(f"Processing all files, line_number_mode: {line_number_mode}, generate_toc: {generate_toc}")
    output_buffer = ""
    line_counter = 0

    # Custom sort to ensure .txt files come before .md files when base names match
    def file_sort_key(path):
        """Key function for sorting files by name then extension priority."""
        base_name = os.path.splitext(os.path.basename(path))[0]
        ext = os.path.splitext(path)[1]
        # This ensures test_file.txt comes before test_file.md
        ext_priority = 0 if ext == '.txt' else 1 if ext == '.md' else 2
        return (base_name, ext_priority)
    
    # Sort the verified sources with custom sorting
    verified_sources = sorted(verified_sources, key=file_sort_key)

    # Pre-calculate line numbers for TOC if needed
    toc_line_numbers = {}
    current_line = 0

    if generate_toc:
        # Calculate the size of the TOC header
        toc_header_lines = 2  # Header line + blank line

        # Calculate the size of each TOC entry (filename + line number)
        toc_entries_lines = len(verified_sources)

        # Add blank line after TOC
        toc_footer_lines = 1

        # Total TOC size
        toc_size = toc_header_lines + toc_entries_lines + toc_footer_lines
        current_line = toc_size

        # Calculate line numbers for each file
        for source_file in verified_sources:
            # Add 3 for the file header (1 for the header line, 2 for the blank lines)
            toc_line_numbers[source_file] = current_line + 3
            with open(source_file, 'r') as f:
                file_lines = len(f.readlines())
            # Add file lines plus 3 for the header (1 for header line, 2 for blank lines)
            current_line += file_lines + 3

    # Create TOC with line numbers
    toc = ""
    if generate_toc:
        toc += "\n" + create_header("TOC", header_seq=None) + "\n\n"
        max_filename_length = max(len(os.path.basename(file)) for file in verified_sources)

        for source_file in verified_sources:
            filename = os.path.basename(source_file)
            line_num = toc_line_numbers[source_file]
            # Format the TOC entry with dots aligning the line numbers
            dots = "." * (max_filename_length - len(filename) + 5)
            toc += f"{filename} {dots} {line_num}\n"

        toc += "\n"

    # Reset line counter for actual file processing
    line_counter = 0

    # Process each file
    for i, source_file in enumerate(verified_sources):
        if line_number_mode == "file":
            line_counter = 0
        file_output, num_lines = process_file(source_file, line_number_mode, line_counter, show_header, header_seq, i, header_style)
        output_buffer += file_output
        line_counter += num_lines

    if generate_toc:
        output_buffer = toc + output_buffer

    return output_buffer

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
        with open(file_path, 'r') as f:
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
                    return False # Not a bundle file if a line is not a valid file
            return False # Not a bundle file if none of the first 5 lines are valid files
    except FileNotFoundError:
        return False
    except Exception as e:
        logger.error(f"Error checking bundle file: {e}")
        return False

def init(srcs, verbose=False, line_number_mode=None, generate_toc=False, show_header=True, header_seq=None, header_style=None):
    """Initialize and process the sources.
    
    Args:
        srcs (list): List of source file paths, directories, or bundle files.
        verbose (bool): Whether to enable verbose logging.
        line_number_mode (str): Line numbering mode ('file', 'all', or None).
        generate_toc (bool): Whether to generate a table of contents.
        show_header (bool): Whether to show headers.
        header_seq (str): The header sequence type (numerical, letter, roman, or None).
        header_style (str): The header style (filename, path, nice, or None).
        
    Returns:
        str: The processed output.
    """
    logger.debug(f"Initializing with sources: {srcs}, verbose: {verbose}, line_number_mode: {line_number_mode}, generate_toc: {generate_toc}")
    
    verified_sources = []
    for source in srcs:
        try:
            for file in get_source_files(source):
                verified_sources.append(verify_path(file))
        except BundleError as e:
            return f"{e}"
        except FileNotFoundError as e:
            print(e)
            sys.exit(1)

    if not verified_sources:
        return "Error: No valid source files found."

    output = process_all(verified_sources, line_number_mode, generate_toc, show_header, header_seq, header_style)
    return output

def to_stds(srcs, verbose=False, line_number_mode=None, generate_toc=False, show_header=True, header_seq=None, header_style=None):
    """Process sources and return the result as a string.
    
    This function handles setting up logging and error handling.
    
    Args:
        srcs (list): List of source file paths, directories, or bundle files.
        verbose (bool): Whether to enable verbose logging.
        line_number_mode (str): Line numbering mode ('file', 'all', or None).
        generate_toc (bool): Whether to generate a table of contents.
        show_header (bool): Whether to show headers.
        header_seq (str): The header sequence type (numerical, letter, roman, or None).
        header_style (str): The header style (filename, path, nice, or None).
        
    Returns:
        str: The processed output.
        
    Raises:
        Exception: Any error encountered during processing.
    """
    # Enable logging only when verbose is True
    setup_logging(to_stderr=True, enabled=verbose)
    try:    
        result = init(srcs, verbose, line_number_mode, generate_toc, show_header, header_seq, header_style)
    except Exception as e:
        raise e
    
    # Always print the result to stdout
    return result

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Generate documentation from source code.",
        formatter_class=argparse.RawTextHelpFormatter,
    )
    parser.add_argument("-v", action="store_true", help="Enable verbose mode")
    parser.add_argument(
        "-n",
        action="count",
        default=0,
        help="Enable line number mode (one -n for file, two for all)",
    )
    parser.add_argument("--toc", action="store_true", help="Generate table of contents")
    parser.add_argument("--no-header", action="store_true", help="Hide file headers")
    parser.add_argument("--header-seq", choices=["numerical", "letter", "roman"], 
                      help="Add sequence numbers to headers (numerical, letter, or roman)")
    parser.add_argument("--header-style", choices=["filename", "path", "nice"], default="filename",
                      help="Header style: filename (default), path (full path), or nice (formatted title)")
    
    parser.add_argument("sources", nargs="*", help="Source file(s)")
    parser.add_argument(
        "--version", action="version", version=f"%(prog)s {VERSION}"
    )
    parser.add_argument(
        "help",
        nargs="?",
        help="Show program's manual",
        default=None,
        choices=["help"],
    )

    args = parser.parse_args()

    # Handle help command before any logging occurs
    if args.help == "help" or (len(sys.argv) == 2 and sys.argv[1] == "help"):
        print(__doc__)
        sys.exit(0)

    if not args.sources and args.help is None:
        parser.print_usage()
        sys.exit(0)

    line_number_mode = None
    if args.n == 1:
        line_number_mode = "file"
    elif args.n >= 2:
        line_number_mode = "all"

    try:
        output = to_stds(
            srcs=args.sources,
            verbose=args.v,
            line_number_mode=line_number_mode,
            generate_toc=args.toc,
            show_header=not args.no_header,
            header_seq=args.header_seq,
            header_style=args.header_style,
        )
        print(output)
    except Exception as e:
        print(f"An error occurred: {e}")
        sys.exit(1)
