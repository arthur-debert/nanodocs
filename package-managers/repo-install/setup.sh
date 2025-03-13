#!/bin/bash
# Setup script for package-managers
# This script creates the necessary directory structure, symlinks, and scripts
# when the package-managers directory is copied to a new repository.

set -e

# Get the directory of the current script
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# Get the package-managers directory (parent of repo-install)
PACKAGE_MANAGERS_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
# Get the repository root (parent of package-managers)
REPO_ROOT="$(cd "$PACKAGE_MANAGERS_DIR/.." && pwd)"

echo "Setting up package-managers in $REPO_ROOT..."

# Create necessary directories
echo "Creating necessary directories..."
mkdir -p "$REPO_ROOT/bin"
mkdir -p "$REPO_ROOT/.github/workflows"
mkdir -p "$PACKAGE_MANAGERS_DIR/brew/Formula"
mkdir -p "$PACKAGE_MANAGERS_DIR/debian"

# Install dependencies if Homebrew is available
if command -v brew &>/dev/null; then
  echo "Installing dependencies using Homebrew..."
  brew bundle --file="$SCRIPT_DIR/Brewfile"
else
  echo "Homebrew not found. Please install the following dependencies manually:"
  echo "- GitHub CLI (gh)"
  echo "- Python"
  echo "- Poetry"
fi

# Create the new-release script in bin
echo "Creating bin/new-release script..."
cp "$SCRIPT_DIR/new-release" "$REPO_ROOT/bin/new-release"
chmod +x "$REPO_ROOT/bin/new-release"

# Handle the GitHub workflow file
echo "Setting up GitHub workflow..."

# Define the workflow paths
WORKFLOW_TEMPLATE="$SCRIPT_DIR/package-release.yml"
WORKFLOW_DESTINATION="$REPO_ROOT/.github/workflows/package-release.yml"

# Copy the workflow file to the GitHub workflows directory
if [ -f "$WORKFLOW_TEMPLATE" ]; then
  echo "Installing workflow file to .github/workflows/..."
  cp "$WORKFLOW_TEMPLATE" "$WORKFLOW_DESTINATION"
else
  echo "Error: Could not find package-release.yml template."
  echo "Please ensure the file exists at: $WORKFLOW_TEMPLATE"
  exit 1
fi

# Make all scripts executable
echo "Making scripts executable..."
find "$PACKAGE_MANAGERS_DIR" -type f \( -name "*.py" -o -name "*.sh" \) -print0 | xargs -0 chmod +x

echo "Setup complete!"
echo ""
echo "To use the package manager system:"
echo "1. Run 'bin/new-release --help' to see available options"
echo "2. For local builds: 'bin/new-release --local --publish-to=brew,apt'"
echo "3. For GitHub Actions: 'bin/new-release --publish-to=pypi,brew,apt'"
echo ""
echo "The GitHub workflow is available at: $WORKFLOW_DESTINATION"
