#!/bin/bash
# Script to test a Debian package locally on a Debian-based system
# This script can be run on GitHub Actions or any Debian-based system

set -e

# Get the directory of the current script
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# Get the package-managers directory (parent of debian)
PACKAGE_MANAGERS_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
# Get the repository root (parent of package-managers)
REPO_ROOT="$(cd "$PACKAGE_MANAGERS_DIR/.." && pwd)"

# Use environment variable if available, otherwise default to nanodoc
PACKAGE_NAME=${PACKAGE_NAME:-${1:-nanodoc}}
OUTPUT_DIR="${SCRIPT_DIR}"

# Check if we're running on a Debian-based system
if [ ! -f /etc/debian_version ]; then
  echo "Error: This script must be run on a Debian-based system"
  echo "You can use docker-apt-build.sh to test on non-Debian systems"
  exit 1
fi

echo "=== Testing Debian Package for $PACKAGE_NAME ==="

# Find the latest .deb package
DEB_PACKAGE=$(find "$OUTPUT_DIR" -name "python3-${PACKAGE_NAME}*.deb" -type f -printf "%T@ %p\n" | sort -nr | head -1 | cut -d' ' -f2-)

if [ -z "$DEB_PACKAGE" ]; then
  echo "Error: No .deb package found for $PACKAGE_NAME in $OUTPUT_DIR"
  echo "Please build the package first using update-apt-package.sh"
  exit 1
fi

echo "Found package: $DEB_PACKAGE"

# Check if the package is already installed
if dpkg -l | grep -q "python3-$PACKAGE_NAME"; then
  echo "Package python3-$PACKAGE_NAME is already installed, removing it first..."
  sudo apt-get remove -y "python3-$PACKAGE_NAME"
fi

# Install the package
echo "Installing package..."
sudo apt-get install -y "$DEB_PACKAGE"
if [ $? -ne 0 ]; then
  echo "❌ Failed to install package"
  exit 1
fi
echo "✅ Package installed successfully"

echo ""
echo "=== Testing Package Functionality ==="

# Test help command
echo "Testing '$PACKAGE_NAME --help':"
python3 -m $PACKAGE_NAME --help
HELP_RESULT=$?

if [ $HELP_RESULT -ne 0 ]; then
  echo "❌ Help command test failed with exit code $HELP_RESULT"
  exit 1
fi
echo "✅ Help command test passed"
echo ""

# Test version command if available
echo "Testing '$PACKAGE_NAME --version':"
python3 -m $PACKAGE_NAME --version
VERSION_RESULT=$?

if [ $VERSION_RESULT -ne 0 ]; then
  echo "⚠️ Version command test failed with exit code $VERSION_RESULT"
  echo "This might be expected if the package doesn't support --version"
  VERSION_RESULT=0 # Don't fail the entire test for this
else
  echo "✅ Version command test passed"
fi
echo ""

# Check if the executable is properly installed
EXECUTABLE_PATH=$(which $PACKAGE_NAME 2>/dev/null || echo "")
if [ -z "$EXECUTABLE_PATH" ]; then
  echo "⚠️ Executable '$PACKAGE_NAME' not found in PATH"
else
  echo "✅ Executable found at: $EXECUTABLE_PATH"

  # Test the executable
  echo "Testing executable '$PACKAGE_NAME --help':"
  $PACKAGE_NAME --help
  EXEC_RESULT=$?

  if [ $EXEC_RESULT -ne 0 ]; then
    echo "❌ Executable test failed with exit code $EXEC_RESULT"
    exit 1
  fi
  echo "✅ Executable test passed"
fi
echo ""

# Validate package content
echo "=== Validating Package Content ==="
echo "Checking package files..."

# List package files
dpkg -L "python3-$PACKAGE_NAME"

# Check for common issues
if ! dpkg -L "python3-$PACKAGE_NAME" | grep -q "/usr/bin/$PACKAGE_NAME"; then
  echo "⚠️ Package might not create the correct executable in /usr/bin"
fi

if ! dpkg -L "python3-$PACKAGE_NAME" | grep -q "/usr/lib/python3/dist-packages/$PACKAGE_NAME"; then
  echo "⚠️ Package might not install Python modules in the correct location"
fi

echo ""
echo "=== Summary ==="
if [ $HELP_RESULT -eq 0 ]; then
  echo "✅ All tests passed successfully!"
  echo "The package should work correctly when installed via apt."
else
  echo "❌ Some tests failed. Please check the output above for details."
  exit 1
fi

exit 0
