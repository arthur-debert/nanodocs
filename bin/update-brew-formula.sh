#!/bin/bash
# Script to update the Homebrew formula for nanodoc using the license from bin/LICENSE

set -e

# Ensure we're in the project root
cd "$(dirname "$0")/.."

# Ensure the Formula directory exists
mkdir -p Formula

# Make sure the script is executable
chmod +x bin/pypi-to-brew

# Run the pypi-to-brew script and filter out pip installation messages
echo "Generating Homebrew formula for nanodoc..."
python bin/pypi-to-brew nanodoc | grep -v "Collecting\|Installing\|Successfully\|cached\|notice" >Formula/nanodoc.rb

echo "Formula updated successfully: Formula/nanodoc.rb"
echo "To test the formula locally, you can run:"
echo "  brew install --build-from-source Formula/nanodoc.rb"
