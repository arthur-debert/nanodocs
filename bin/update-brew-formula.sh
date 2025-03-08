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

# Run the pypi-to-brew script and filter out pip installation messages
echo "Generating Homebrew formula for ${PACKAGE_NAME}..."
# Using || true to ignore the return value of the pipeline
python bin/pypi-to-brew "${PACKAGE_NAME}" | grep -v "Collecting\|Installing\|Successfully\|cached\|notice" >"Formula/${PACKAGE_NAME}.rb" || true

echo "Formula updated successfully: Formula/${PACKAGE_NAME}.rb"
echo "To test the formula locally, you can run:"
echo "  brew install --build-from-source Formula/${PACKAGE_NAME}.rb"
