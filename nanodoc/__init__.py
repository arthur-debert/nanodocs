# Import and re-export all public functions and classes from nanodoc.py
from .nanodoc import (
    VERSION,
    LINE_WIDTH,
    BundleError,
    setup_logging,
    apply_style_to_filename,
    apply_sequence_to_text,
    create_header,
    expand_directory,
    verify_path,
    expand_bundles,
    get_source_files,
    process_file,
    process_all,
    is_bundle_file,
    init,
    to_stds
)

# Set up the logger
from .nanodoc import logger