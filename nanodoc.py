import argparse
import os
import glob
import sys

LINE_WIDTH = 80

def create_header(text, char="#"):
    padding = (LINE_WIDTH - len(text) - 2) // 2
    header = char * padding + " " + text + " " + char * padding
    # Adjust if the header is shorter than LINE_WIDTH due to odd padding
    header += char * (LINE_WIDTH - len(header))
    return header

def expand_directory(directory, extensions=[".txt", ".md"]):
    matches = []
    for root, _, filenames in os.walk(directory):
        for filename in filenames:
            for ext in extensions:
                if filename.endswith(ext):
                    matches.append(os.path.join(root, filename))
                    break  # Avoid matching multiple extensions
    return matches


def verify_path(path):
    if not os.path.isfile(path):
        print(f"Error: Path is not a file: {path}")
        sys.exit(127)
    return path


def expand_bundles(bundle_file):
    try:
        with open(bundle_file, "r") as f:
            lines = [line.strip() for line in f]
    except FileNotFoundError:
        print(f"Error: Bundle file not found: {bundle_file}")
        sys.exit(127)

    return lines


def get_source_files(source):
    if os.path.isdir(source):
        return expand_directory(source)
    elif glob.glob(f"{source}.bundle*"):
        return expand_bundles(source)
    else:
        return [source]

def process_file(file_path, line_number_mode, line_counter):
    try:
        with open(file_path, "r") as f:
            lines = f.readlines()
    except FileNotFoundError:
        return f"Error: File not found: {file_path}\n", 0

    header = create_header(os.path.basename(file_path)) + "\n"
    output = header

    for i, line in enumerate(lines):
        if line_number_mode == "all" or line_number_mode == "file":
            output += f"{line_counter + i + 1:4d}: {line}"
        else:
            output += line
    return output, len(lines)

def process_all(verified_sources, line_number_mode, generate_toc):
    output_buffer = ""
    line_counter = 0

    toc = ""
    if generate_toc:
        toc += create_header("TOC") + "\n"
        for source_file in verified_sources:
            toc += f"{os.path.basename(source_file)}\n"
        toc += "\n"

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

def init(srcs, verbose=False, line_number_mode=None, generate_toc=False):
    expanded_sources = [f for source in srcs for f in get_source_files(source)]
    verified_sources = [verify_path(source) for source in expanded_sources]

    output = process_all(verified_sources, line_number_mode, generate_toc)
    if verbose:
        print(output)

    print(f"Verbose: {verbose}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Generate documentation from source code."
    )
    parser.add_argument("-v", action="store_true", help="Enable verbose mode")
    parser.add_argument(
        "-n",
        action="count",
        default=0,
        help="Enable line number mode (one -n for file, two for all)",
    )
    parser.add_argument("--toc", action="store_true", help="Generate table of contents")
    parser.add_argument("sources", nargs="+", help="Source file(s)")

    args = parser.parse_args()

    line_number_mode = None
    if args.n == 1:
        line_number_mode = "file"
    elif args.n >= 2:
        line_number_mode = "all"

    expanded_sources = []
    for source in args.sources:
        expanded_sources.extend(get_source_files(source))

    init(
        srcs=args.sources,
        verbose=args.v,
        line_number_mode=line_number_mode,
        generate_toc=args.toc,
    )
