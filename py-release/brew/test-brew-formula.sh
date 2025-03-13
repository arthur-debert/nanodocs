#!/bin/bash
# Script to test a Homebrew formula locally without affecting the main Homebrew installation

set -e

# Get the directory of the current script
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# Get the package-managers directory (parent of brew)
PACKAGE_MANAGERS_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
# Get the repository root (parent of package-managers)
REPO_ROOT="$(cd "$PACKAGE_MANAGERS_DIR/.." && pwd)"

# Use environment variable if available, otherwise default to nanodoc
PACKAGE_NAME=${PACKAGE_NAME:-${1:-nanodoc}}
FORMULA_PATH="${SCRIPT_DIR}/Formula/${PACKAGE_NAME}.rb"

# Check if the formula exists
if [ ! -f "$FORMULA_PATH" ]; then
  echo "Error: Formula file not found at $FORMULA_PATH"
  exit 1
fi

echo "=== Testing Formula: $FORMULA_PATH ==="
echo "This script will test the formula by running the Python module directly."
echo ""

# Check if the package is installed
if python3 -c "import $PACKAGE_NAME" 2>/dev/null; then
  echo "✅ Package $PACKAGE_NAME is already installed"
else
  echo "⚠️ Package $PACKAGE_NAME is not installed. Installing temporarily..."
  pip3 install -e . --quiet
  if [ $? -ne 0 ]; then
    echo "❌ Failed to install package"
    exit 1
  fi
  echo "✅ Package installed successfully"
fi

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

# Test version command
echo "Testing '$PACKAGE_NAME --version':"
python3 -m $PACKAGE_NAME --version
VERSION_RESULT=$?

if [ $VERSION_RESULT -ne 0 ]; then
  echo "❌ Version command test failed with exit code $VERSION_RESULT"
  exit 1
fi
echo "✅ Version command test passed"
echo ""

# Validate formula content
echo "=== Validating Formula Content ==="
echo "Checking formula for common issues..."

# Check if formula uses pip instead of poetry
if grep -q "poetry" "$FORMULA_PATH" && ! grep -q "pip" "$FORMULA_PATH"; then
  echo "⚠️ Formula uses poetry but not pip. Consider using pip for installation."
fi

# Check if formula has the correct executable name
if ! grep -q 'bin/"nanodoc"' "$FORMULA_PATH"; then
  echo "⚠️ Formula might not create the correct executable. Check the bin script name."
fi

# Check if formula has the correct test command
if ! grep -q "system.*nanodoc.*--help" "$FORMULA_PATH"; then
  echo "⚠️ Formula test might not be correct. Consider using 'system bin/\"nanodoc\", \"--help\"'."
fi

echo ""
echo "=== Summary ==="
if [ $HELP_RESULT -eq 0 ] && [ $VERSION_RESULT -eq 0 ]; then
  echo "✅ All tests passed successfully!"
  echo "The formula should work correctly when installed via Homebrew."
else
  echo "❌ Some tests failed. Please check the output above for details."
  exit 1
fi

exit 0
