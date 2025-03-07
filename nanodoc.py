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

def setup_logging(to_stderr=False):
    """Configure logging based on requirements"""
    global logger
    logger = logging.getLogger("nanodoc")
    logger.setLevel(logging.INFO)
    
    # Remove any existing handlers
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)
    
    # Create handler to the appropriate stream
    stream = sys.stderr if to_stderr else sys.stdout
    handler = logging.StreamHandler(stream)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    return logger

# Initialize logger at the module level
logger = setup_logging()

def create_header(text, char="#"):
    logger.info(f"Entering create_header with text='{text}', char='{char}'")
    padding = (LINE_WIDTH - len(text) - 2) // 2
    header = char * padding + " " + text + " " + char * padding
    # Adjust if the header is shorter than LINE_WIDTH due to odd padding
    header += char * (LINE_WIDTH - len(header))
    return header

def expand_directory(directory, extensions=[".txt", ".md"]):
    logger.info(f"Entering expand_directory with directory='{directory}', extensions='{extensions}'")
    matches = []
    for root, _, filenames in os.walk(directory):
        for filename in filenames:
            for ext in extensions:
                if filename.endswith(ext):
                    matches.append(os.path.join(root, filename))
                    break  # Avoid matching multiple extensions
    return sorted(matches)


def verify_path(path):
    logger.info(f"Entering verify_path with path='{path}'")
    if not os.path.isfile(path):
        print(f"Error: Path is not a file: {path}")
        sys.exit(127)
    return path


def expand_bundles(bundle_file):
    logger.info(f"Entering expand_bundles with bundle_file='{bundle_file}'")
    try:
        with open(bundle_file, "r") as f:
            lines = [line.strip() for line in f]
    except FileNotFoundError:
        print(f"Error: Bundle file not found: {bundle_file}")
        sys.exit(127)

    return lines


def get_source_files(source):
    logger.info(f"Entering get_source_files with source='{source}'")
    if os.path.isdir(source):
        files = expand_directory(source)
        return sorted(files)
    elif glob.glob(f"{source}.bundle*"):
        return expand_bundles(source)
    else:
        return [source]

def process_file(file_path, line_number_mode, line_counter):
    logger.info(f"Entering process_file with file_path='{file_path}', line_number_mode='{line_number_mode}', line_counter={line_counter}")
    try:
        with open(file_path, "r") as f:
            lines = f.readlines()
    except FileNotFoundError:
        return f"Error: File not found: {file_path}\n", 0

    header = create_header(os.path.basename(file_path)) + "\n"
    output = header

    for i, line in enumerate(lines):
        if line_number_mode == "all":
            output += f"{line_counter + i + 1:4d}: {line}"
        elif line_number_mode == "file":
            output += f"{i + 1:4d}: {line}"
        else:
            output += line
    return output, len(lines)

def process_all(verified_sources, line_number_mode, generate_toc):
    logger.info(f"Entering process_all with verified_sources='{verified_sources}', line_number_mode='{line_number_mode}', generate_toc={generate_toc}")
    output_buffer = ""
    line_counter = 0

    toc = ""
    if generate_toc:
        toc += create_header("TOC") + "\n"
        for source_file in verified_sources:
            toc += f"{os.path.basename(source_file)}\n"
        toc += "\n"

    # Custom sort to ensure .txt files come before .md files when base names match
    def file_sort_key(path):
        base_name = os.path.splitext(os.path.basename(path))[0]
        ext = os.path.splitext(path)[1]
        # This ensures test_file.txt comes before test_file.md
        ext_priority = 0 if ext == '.txt' else 1 if ext == '.md' else 2
        return (base_name, ext_priority)
    
    # Sort the verified sources with custom sorting
    verified_sources = sorted(verified_sources, key=file_sort_key)

    for source_file in verified_sources:
        if line_number_mode == "file":
            line_counter = 0
        file_output, num_lines = process_file(source_file, line_number_mode, line_counter)
        output_buffer += file_output
        line_counter += num_lines

    if generate_toc:
        output_buffer = toc + output_buffer

    print(f"Generate TOC: {generate_toc}")
    return output_buffer

def is_bundle_file(file_path):
    """
    Determine if a file is a bundle file by checking if its lines look like file paths.
    A file is considered a bundle if its first non-empty line points to an existing file.
    """
    logger.info(f"Checking if {file_path} is a bundle file")
    try:
        with open(file_path, 'r') as f:
            # Check the first few non-empty lines
            for _ in range(5):  # Check up to 5 lines
                line = f.readline().strip()
                if not line:
                    continue
                # If this line exists as a file, assume it's a bundle file
                if os.path.isfile(line):
                    return True
                # If we have a line that doesn't look like a file path, it's not a bundle
                return False
            return False
    except:
        return False

def init(srcs, verbose=False, line_number_mode=None, generate_toc=False):
    logger.info(f"Entering init with srcs='{srcs}', verbose={verbose}, line_number_mode='{line_number_mode}', generate_toc={generate_toc}")
    
    # Keep track of original source files provided as arguments
    original_sources = set(srcs)
    
    expanded_sources = [f for source in srcs for f in get_source_files(source)]
    
    verified_sources = []
    for source in expanded_sources:
        if source != "help":
            # Only treat files as bundles if they were directly provided as arguments
            # and end with .txt extension AND the content looks like file paths
            if source in original_sources and os.path.isfile(source) and source.endswith(".txt") and is_bundle_file(source):
                # expand the bundle
                bundle_files = expand_bundles(source)
                for file in bundle_files:
                    verified_sources.append(verify_path(file))
            else:
                verified_sources.append(verify_path(source))

    if not verified_sources:
        return "Error: No valid source files found."

    output = process_all(verified_sources, line_number_mode, generate_toc)
    return output

def to_stds(srcs, verbose=False, line_number_mode=None, generate_toc=False):
    if verbose:
        logger.setLevel(logging.DEBUG)
    result = init(srcs, verbose, line_number_mode, generate_toc)
    if verbose:
        print(result)

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
        # Don't log anything for help output
        print(__doc__)
        sys.exit(0)

    if not args.sources and args.help is None:
        parser.print_usage()
        sys.exit(0)

    # Set up logging to stderr to avoid mixing with output content
    logger = setup_logging(to_stderr=True)

    if args.v:
        logger.setLevel(logging.DEBUG)
    
    line_number_mode = None
    if args.n == 1:
        line_number_mode = "file"
    elif args.n >= 2:
        line_number_mode = "all"

    expanded_sources = []
    for source in args.sources:
        expanded_sources.extend(get_source_files(source))

    to_stds(
        srcs=args.sources,
        verbose=args.v,
        line_number_mode=line_number_mode,
        generate_toc=args.toc,
    )
