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
nanodocs --toc -v                            # Verbose bundle with table of contents
nanodocs  some_directory                   # will add all files in directory
nanodocs  bundle_file                         # bundle_file is a txt docuument with files paths on lines
```

"""
import argparse
import os
import glob
import sys
import logging

VERSION = "0.1.0"
LINE_WIDTH = 80

# Custom exception for bundle file errors
class BundleError(Exception):
    pass

# Initialize logger at the module level - disabled by default
logger = logging.getLogger("nanodoc")
logger.setLevel(logging.CRITICAL)  # Start with logging disabled

def setup_logging(to_stderr=False, enabled=False):
    """Configure logging based on requirements"""
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

def create_header(text, char="#"):
    logger.debug(f"Creating header with text='{text}', char='{char}'")
    padding = (LINE_WIDTH - len(text) - 2) // 2
    header = char * padding + " " + text + " " + char * padding
    # Adjust if the header is shorter than LINE_WIDTH due to odd padding
    header += char * (LINE_WIDTH - len(header))
    return header

def expand_directory(directory, extensions=[".txt", ".md"]):
    logger.debug(f"Expanding directory with directory='{directory}', extensions='{extensions}'")
    matches = []
    for root, _, filenames in os.walk(directory):
        for filename in filenames:
            if any(filename.endswith(ext) for ext in extensions):
                matches.append(os.path.join(root, filename))
    return sorted(matches)


def verify_path(path):
    logger.debug(f"Verifying path: {path}")
    if not os.path.isfile(path):
        raise FileNotFoundError(f"Error: Path is not a file: {path}")
    return path


def expand_bundles(bundle_file):
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
    logger.debug(f"Getting source files for: {source}")
    if os.path.isdir(source):
        return sorted(expand_directory(source))
    elif is_bundle_file(source):
        return expand_bundles(source)
    else:
        return [source]

def process_file(file_path, line_number_mode, line_counter):
    logger.debug(f"Processing file: {file_path}, line_number_mode: {line_number_mode}, line_counter: {line_counter}")
    try:
        with open(file_path, "r") as f:
            lines = f.readlines()
    except FileNotFoundError:
        return f"Error: File not found: {file_path}\n", 0

    header = create_header(os.path.basename(file_path)) + "\n"
    output = header

    for i, line in enumerate(lines):
        line_number = ""
        if line_number_mode == "all":
            line_number = f"{line_counter + i + 1:4d}: "
        elif line_number_mode == "file":
            line_number = f"{i + 1:4d}: "
        output += line_number + line
    return output, len(lines)

def process_all(verified_sources, line_number_mode, generate_toc):
    logger.debug(f"Processing all files, line_number_mode: {line_number_mode}, generate_toc: {generate_toc}")
    output_buffer = ""
    line_counter = 0

    # Custom sort to ensure .txt files come before .md files when base names match
    def file_sort_key(path):
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
            toc_line_numbers[source_file] = current_line + 1  # +1 for the file header
            with open(source_file, 'r') as f:
                file_lines = len(f.readlines())
            current_line += file_lines + 1  # +1 for the file header

    # Create TOC with line numbers
    toc = ""
    if generate_toc:
        toc += create_header("TOC") + "\n"
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
    for source_file in verified_sources:
        if line_number_mode == "file":
            line_counter = 0
        file_output, num_lines = process_file(source_file, line_number_mode, line_counter)
        output_buffer += file_output
        line_counter += num_lines

    if generate_toc:
        output_buffer = toc + output_buffer

    return output_buffer

def is_bundle_file(file_path):
    """
    Determine if a file is a bundle file by checking if its lines look like file paths.
    A file is considered a bundle if its first non-empty line points to an existing file.
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

def init(srcs, verbose=False, line_number_mode=None, generate_toc=False):
    logger.debug(f"Initializing with sources: {srcs}, verbose: {verbose}, line_number_mode: {line_number_mode}, generate_toc: {generate_toc}")
    
    verified_sources = []
    for source in srcs:
        try:
            for file in get_source_files(source):
                verified_sources.append(verify_path(file))
        except FileNotFoundError as e:
            print(e)
            sys.exit(1)

    if not verified_sources:
        return "Error: No valid source files found."

    output = process_all(verified_sources, line_number_mode, generate_toc)
    return output

def to_stds(srcs, verbose=False, line_number_mode=None, generate_toc=False):
    # Enable logging only when verbose is True
    setup_logging(to_stderr=True, enabled=verbose)
    try:    
        result = init(srcs, verbose, line_number_mode, generate_toc)
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
        )
        print(output)
    except Exception as e:
        print(f"An error occurred: {e}")
        sys.exit(1)
