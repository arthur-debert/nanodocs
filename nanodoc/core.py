import logging
import os

from .files import get_file_content
from .formatting import apply_style_to_filename, create_header

logger = logging.getLogger("nanodoc")
logger.setLevel(logging.CRITICAL)  # Start with logging disabled


def generate_table_of_contents(verified_sources, style=None):
    """Generate a table of contents for the given source files.

    Args:
        verified_sources (list): List of file paths or list of tuples (file_path, line_parts).
        style (str): The header style (filename, path, nice, or None).

    Returns:
        tuple: (str, dict) The table of contents string and a dictionary
               mapping source files to their line numbers in the final document.
    """
    logger.debug(f"Generating table of contents for {len(verified_sources)} files")

    # Convert to list of tuples if it's a list of strings
    processed_sources = []
    for item in verified_sources:
        if isinstance(item, tuple):
            processed_sources.append(item)
        else:
            # It's a string (file path)
            processed_sources.append((item, None))

    # Calculate line numbers for TOC
    toc_line_numbers = {}
    current_line = 0

    # Calculate the size of the TOC header
    toc_header_lines = 2  # Header line + blank line

    # Calculate the size of each TOC entry (filename + line number)
    toc_entries_lines = len(processed_sources)

    # Add blank line after TOC
    toc_footer_lines = 1

    # Total TOC size
    toc_size = toc_header_lines + toc_entries_lines + toc_footer_lines
    current_line = toc_size

    # Calculate line numbers for each file
    for source_file, line_parts in processed_sources:
        # Add 3 for the file header (1 for the header line, 2 for the blank lines)
        toc_line_numbers[source_file] = current_line + 3
        if line_parts:
            content = get_file_content(source_file, parts=line_parts)
        else:
            content = get_file_content(source_file)
        file_lines = len(content.splitlines())
        # Add file lines plus 3 for the header (1 for header, 2 for blank lines)
        current_line += file_lines + 3

    # Create TOC with line numbers
    toc = ""
    toc += "\n" + create_header("TOC", sequence=None, style=style) + "\n\n"

    # Format filenames according to header style
    formatted_filenames = {}
    for source_file, line_parts in processed_sources:
        filename = os.path.basename(source_file)
        formatted_name = apply_style_to_filename(filename, style, source_file)
        # Add line range information if present
        if line_parts:
            range_info = []
            for start, end in line_parts:
                if start == end:
                    range_info.append(f"L{start}")
                else:
                    range_info.append(f"L{start}-{end}")
            formatted_name += f" ({', '.join(range_info)})"
        formatted_filenames[source_file] = formatted_name

    max_filename_length = max(
        len(formatted_name) for formatted_name in formatted_filenames.values()
    )

    for source_file, line_parts in processed_sources:
        formatted_name = formatted_filenames[source_file]
        line_num = toc_line_numbers[source_file]
        # Format the TOC entry with dots aligning the line numbers
        dots = "." * (max_filename_length - len(formatted_name) + 5)
        toc += f"{formatted_name} {dots} {line_num}\n"

    toc += "\n"

    return toc, toc_line_numbers


def process_file(
    file_path,
    line_number_mode,
    line_counter,
    show_header=True,
    sequence=None,
    seq_index=0,
    style=None,
    line_parts=None,
):
    """Process a single file and format its content.

    Args:
        file_path (str): The path of the file to process.
        line_number_mode (str): The line numbering mode ('file', 'all', or None).
        line_counter (int): The current global line counter.
        show_header (bool): Whether to show the header.
        sequence (str): The header sequence type (numerical, letter, roman,
                        or None).
        seq_index (int): The index of the file in the sequence.
        style (str): The header style (filename, path, nice, or None).
        line_parts (list, optional): A list of (start, end) tuples representing
                                    line ranges to include.
    Returns:
        tuple: (str, int) Processed file content with header and line
               numbers, and the number of lines in the file.
    """
    logger.debug(
        f"Processing file: {file_path}, line_number_mode: {line_number_mode}, "
        f"line_counter: {line_counter}, line_parts: {line_parts}"
    )
    try:
        if line_parts:
            # Get only the specified lines
            content = get_file_content(file_path, parts=line_parts)
            # We need to get all lines to determine the actual line numbers
            with open(file_path, "r") as f:
                all_lines = f.readlines()

            # Create a list of lines to include with their original line numbers
            lines_with_numbers = []
            for start, end in line_parts:
                for i in range(start - 1, end):
                    if i < len(all_lines):
                        lines_with_numbers.append((i + 1, all_lines[i]))

            # Sort by line number to maintain order
            lines_with_numbers.sort(key=lambda x: x[0])
        else:
            # Get the entire file content
            content = get_file_content(file_path)
            lines = content.splitlines(True)  # Keep the newline characters
            # Create a list of lines with their line numbers (1-indexed)
            lines_with_numbers = [(i + 1, line) for i, line in enumerate(lines)]
    except FileNotFoundError:
        return f"Error: File not found: {file_path}\n", 0

    output = ""
    if show_header:
        header = (
            "\n"
            + create_header(
                os.path.basename(file_path),
                sequence=sequence,
                seq_index=seq_index,
                style=style,
                original_path=file_path,
            )
            + "\n\n"
        )
        output = header

    for i, (line_num, line) in enumerate(lines_with_numbers):
        line_number = ""
        if line_number_mode == "all":
            line_number = f"{line_counter + i + 1:4d}: "
        elif line_number_mode == "file":
            line_number = f"{line_num:4d}: "
        output += line_number + line
    return output, len(lines_with_numbers)


def process_all(
    verified_sources,
    line_number_mode=None,
    generate_toc=False,
    show_header=True,
    sequence=None,
    style=None,
):
    """Process all source files and combine them into a single document.

    This is the main entry point for both command-line usage and testing.

    Args:
        verified_sources (list): List of file paths or list of tuples (file_path, line_parts).
        line_number_mode (str): Line numbering mode ('file', 'all', or None).
        generate_toc (bool): Whether to generate a table of contents.
        show_header (bool): Whether to show headers.
        sequence (str): The header sequence type (numerical, letter, roman,
                        or None).
        style (str): The header style (filename, path, nice, or None).
    Returns:
        str: The combined content of all files with formatting.
    """
    logger.debug(
        f"Processing all files, line_number_mode: {line_number_mode}, "
        f"generate_toc: {generate_toc}"
    )
    output_buffer = ""
    line_counter = 0

    # Convert to list of tuples if it's a list of strings
    processed_sources = []
    for item in verified_sources:
        if isinstance(item, tuple):
            processed_sources.append(item)
        else:
            # It's a string (file path)
            processed_sources.append((item, None))

    # Generate table of contents if needed
    toc = ""
    if generate_toc:
        toc, _ = generate_table_of_contents(verified_sources, style)

    # Reset line counter for actual file processing
    line_counter = 0

    # Process each file
    for i, (source_file, line_parts) in enumerate(processed_sources):
        if line_number_mode == "file":
            line_counter = 0
        file_output, num_lines = process_file(
            source_file,
            line_number_mode,
            line_counter,
            show_header,
            sequence,
            i,
            style,
            line_parts,
        )
        output_buffer += file_output
        line_counter += num_lines

    if generate_toc:
        output_buffer = toc + output_buffer

    return output_buffer
