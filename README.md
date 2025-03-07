# Nanodoc

Nanodoc is a minimalist document bundler designed for small-scale documentation needs like hints, prompts, or reminders. It combines multiple text files into a single document with neat formatting.

## Features

- Combines multiple text files into a single document
- Adds clear title separators between pages
- Supports optional line numbering (per file or global)
- Can generate a table of contents
- Flexible file selection methods

## Usage

Basic usage:
```bash
nanodoc file1.txt file2.txt
```

With line numbering and TOC:
```bash
nanodoc -n file1.txt file2.txt              # Per-file line numbering
nanodoc -nn file1.txt file2.txt             # Global line numbering
nanodoc -nn --toc file1.txt file2.txt       # Global numbering with TOC
```

## File Selection Options

Nanodoc is flexible in how you specify the files to bundle:

1. **Individual files**: Provide file paths as arguments
   ```bash
   nanodoc welcome.txt guide.txt reference.txt
   ```

2. **Directories**: Include all .txt and .md files in a directory
   ```bash
   nanodoc docs/
   ```

3. **Bundle files**: Create a text file containing a list of file paths
   ```bash
   nanodoc my-bundle.txt
   ```
   Where my-bundle.txt contains:
   ```
   intro.txt
   chapter1.md
   appendix.txt
   ```

## Command Line Options

- `-v, --verbose`: Enable verbose output with detailed logging
- `-n`: Add per-file line numbering (01, 02, etc.)
- `-nn`: Add global line numbering (001, 002, etc.)
- `--toc`: Generate a table of contents at the beginning
- `-h, --help`: Display help information

## Example Output

```
########################## welcome.txt #######################################
This is the content of welcome.txt
With multiple lines
Of helpful information

########################## guide.txt ########################################
The guide contains more detailed information
About how to use the application
With step-by-step instructions
```

With line numbering (-n):
```
########################## welcome.txt #######################################
   1: This is the content of welcome.txt
   2: With multiple lines
   3: Of helpful information

########################## guide.txt ########################################
   1: The guide contains more detailed information
   2: About how to use the application
   3: With step-by-step instructions
```

## Installation

```bash
pip install nanodoc
# or
git clone https://github.com/yourusername/nanodoc.git
cd nanodoc
pip install -e .
```

## Contributing

Contributions are welcome! Feel free to open issues or submit pull requests.

## License

MIT License
