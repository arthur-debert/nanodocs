#!/bin/bash
# Update APT package script
# This script generates a Debian package for a PyPI package and stores it in a designated directory

set -e

# Get the package name from the command line or use default
PACKAGE_NAME=${1:-nanodoc}
OUTPUT_DIR="package-managers/debian"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Create the output directory if it doesn't exist
mkdir -p "$OUTPUT_DIR"

echo "Generating Debian package for $PACKAGE_NAME..."

# Make the pypi-to-apt script executable
chmod +x package-managers/debian/pypi-to-apt
chmod +x package-managers/common/about-py-package

# Generate the Debian package
package-managers/debian/pypi-to-apt "$PACKAGE_NAME" --output-dir "$OUTPUT_DIR"

echo "Debian package for $PACKAGE_NAME has been generated in $OUTPUT_DIR"

# Test the package using the dedicated test script
if [ -f /etc/debian_version ]; then
  echo "Running comprehensive tests for the Debian package..."

  # Make the test script executable
  chmod +x "$SCRIPT_DIR/test-apt-package.sh"

  # Run the test script
  "$SCRIPT_DIR/test-apt-package.sh" "$PACKAGE_NAME"

  if [ $? -ne 0 ]; then
    echo "❌ Package tests failed."
    exit 1
  fi

  echo "✅ Package tests completed successfully."
else
  echo "Not running on a Debian-based system, skipping package test"
  echo "To test the package, run: sudo apt install -y ./$OUTPUT_DIR/python3-$PACKAGE_NAME*.deb"
fi
