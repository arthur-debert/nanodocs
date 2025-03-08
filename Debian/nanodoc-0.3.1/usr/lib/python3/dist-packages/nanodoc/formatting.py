################################################################################
# Formatting - Functions related to headers, line numbers, and table of contents
################################################################################


import logging
import os
import re

logger = logging.getLogger("nanodoc")
logger.setLevel(logging.CRITICAL)  # Start with logging disabled


def apply_style_to_filename(filename, style, original_path=None):
    """Apply the specified style to a filename.

    Args:
        filename (str): The filename to style.
        style (str): The style to apply (filename, path, nice, or None).
        original_path (str, optional): The original file path (used for path and nice styles).

    Returns:
        str: The styled filename.
    """
    logger.debug(f"Applying style '{style}' to filename '{filename}'")

    if not style or style == "filename" or not original_path:
        return filename

    if style == "path":
        # Use the full file path
        return original_path
    elif style == "nice":
        # Remove extension, replace - and _ with spaces, title case,
        # then add filename in parentheses
        basename = os.path.splitext(filename)[0]  # Remove extension

        # Replace - and _ with spaces
        nice_name = re.sub(r"[-_]", " ", basename)

        # Title case
        nice_name = nice_name.title()

        # Add filename in parentheses
        return f"{nice_name} ({filename})"

    # Default to filename if style is not recognized
    return filename


def to_roman(num):
    """Convert integer to roman numeral.

    Args:
        num (int): A positive integer to convert.

    Returns:
        str: Roman numeral representation of the input.
    """
    if not isinstance(num, int) or num <= 0:
        raise ValueError("Input must be a positive integer")

    val = [1000, 900, 500, 400, 100, 90, 50, 40, 10, 9, 5, 4, 1]
    syms = ["M", "CM", "D", "CD", "C", "XC", "L", "XL", "X", "IX", "V", "IV", "I"]

    roman_num = ""
    i = 0
    while num > 0:
        for _ in range(num // val[i]):
            roman_num += syms[i]
            num -= val[i]
        i += 1
    return roman_num.lower()


def format_pos(style, position):
    """Format the sequence prefix based on the sequence type.

    Args:
        style (str): The sequence type (numerical, letter, roman).
        position (int): The index of the item in the sequence.

    Returns:
        str: The formatted sequence prefix.
    """
    if not style:
        return ""

    # Calculate one-indexed number first
    pos_one_indexed = position + 1

    # Dictionary mapping styles to formatting functions
    style_formatters = {
        "numerical": lambda n: f"{int(n)}. ",
        "letter": lambda n: f"{chr(96 + ((n - 1) % 26) + 1)}. ",
        "roman": lambda n: f"{to_roman(n)}. ",
    }

    # Use the appropriate formatter or return empty string if style not found
    return style_formatters.get(style, lambda _: "")(pos_one_indexed)


def apply_sequence_to_text(text, sequence, seq_index):
    """Apply the specified sequence to text."""
    prefix = format_pos(sequence, seq_index)
    return prefix + text if prefix else text


def create_header(
    text, char="#", sequence=None, seq_index=0, style=None, original_path=None
):
    """Create a formatted header with the given text.

    Args:
        text (str): The text to include in the header.
        char (str): The character to use for the header border.
        sequence (str): The header sequence type (numerical, letter, roman, or None).
        seq_index (int): The index of the file in the sequence.
        style (str): The header style (filename, path, nice, or None).
        original_path (str): The original file path (used for path and nice
                            styles).

    Returns:
        str: A formatted header string with the text centered.
    """
    # Apply style to the text if original_path is provided
    if original_path:
        filename = os.path.basename(original_path)
        styled_text = apply_style_to_filename(filename, style, original_path)
    else:
        styled_text = text

    # Apply sequence to the styled text
    header = apply_sequence_to_text(styled_text, sequence, seq_index)
    logger.debug(
        f"Creating header with text='{text}', char='{char}', final: '{header}'"
    )

    return header
