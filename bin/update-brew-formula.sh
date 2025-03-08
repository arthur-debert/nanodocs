#!/bin/bash
# Script to update the Homebrew formula for nanodoc using the license from bin/LICENSE

# Default package name is nanodoc if not provided
PACKAGE_NAME=${1:-nanodoc}

set -e

# Ensure we're in the project root
cd "$(dirname "$0")/.."

# Ensure the Formula directory exists
mkdir -p Formula

# Make sure the script is executable
chmod +x bin/pypi-to-brew

# Install jinja2 if it's not already installed
if ! python -c "import jinja2" &>/dev/null; then
  echo "Installing jinja2..."
  pip install jinja2
fi

# Run the pypi-to-brew script and filter out pip installation messages
echo "Generating Homebrew formula for ${PACKAGE_NAME}..."

# Create a temporary file for the output
TEMP_FILE=$(mktemp)

# Run the script and capture the output
if python bin/pypi-to-brew "${PACKAGE_NAME}" | grep -v "Collecting\|Installing\|Successfully\|cached\|notice\|Downloading" >"$TEMP_FILE"; then
  # Check if the output is not empty
  if [ -s "$TEMP_FILE" ]; then
    # Copy the output to the formula file
    cp "$TEMP_FILE" "Formula/${PACKAGE_NAME}.rb"
    echo "Formula updated successfully: Formula/${PACKAGE_NAME}.rb"
    echo "To test the formula locally, you can run:"
    echo "  brew install --build-from-source Formula/${PACKAGE_NAME}.rb"
  else
    echo "Error: Generated formula is empty. Keeping the existing formula."
    exit 1
  fi
else
  echo "Error: Failed to generate formula. Keeping the existing formula."
  exit 1
fi

# Clean up the temporary file
rm -f "$TEMP_FILE"
