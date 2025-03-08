#!/bin/bash
# Update APT package script
# This script generates a Debian package for a PyPI package and stores it in a designated directory

set -e

# Get the package name from the command line or use default
PACKAGE_NAME=${1:-nanodoc}
OUTPUT_DIR="Debian"

# Create the output directory if it doesn't exist
mkdir -p "$OUTPUT_DIR"

echo "Generating Debian package for $PACKAGE_NAME..."

# Make the pypi-to-apt script executable
chmod +x bin/pypi-to-apt
chmod +x bin/about-py-package

# Generate the Debian package
bin/pypi-to-apt "$PACKAGE_NAME" --output-dir "$OUTPUT_DIR"

echo "Debian package for $PACKAGE_NAME has been generated in $OUTPUT_DIR/"

# Test the package if we're running in a Debian-based environment
if [ -f /etc/debian_version ]; then
  echo "Testing the Debian package..."

  # Install the package
  sudo apt install -y ./$OUTPUT_DIR/python3-$PACKAGE_NAME*.deb

  # Test the package by running it with --help
  python3 -m $PACKAGE_NAME --help

  echo "Package test completed successfully"
else
  echo "Not running on a Debian-based system, skipping package test"
  echo "To test the package, run: sudo apt install -y ./$OUTPUT_DIR/python3-$PACKAGE_NAME*.deb"
fi
