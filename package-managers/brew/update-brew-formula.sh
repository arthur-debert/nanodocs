#!/bin/bash
# Script to update the Homebrew formula for nanodoc using the license from bin/LICENSE

# Default package name is nanodoc if not provided
PACKAGE_NAME=${1:-nanodoc}

# Get the script directory
SCRIPT_DIR="$(dirname "$0")"
# Get the project root (two levels up from the script)
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
# Change to the project root
cd "$PROJECT_ROOT"

set -e

# Ensure the Formula directory exists
mkdir -p package-managers/brew/Formula

# Make sure the script is executable
chmod +x package-managers/brew/pypi-to-brew

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
if python package-managers/brew/pypi-to-brew "${PACKAGE_NAME}" | grep -v "Collecting\|Installing\|Successfully\|cached\|notice\|Downloading" >"$TEMP_FILE"; then
  # Check if the output is not empty
  if [ -s "$TEMP_FILE" ]; then
    # Copy the output to the formula file
    cp "$TEMP_FILE" "package-managers/brew/Formula/${PACKAGE_NAME}.rb"
    echo "Formula updated successfully: package-managers/brew/Formula/${PACKAGE_NAME}.rb"

    # Test the formula
    echo "Testing the formula..."
    chmod +x "$SCRIPT_DIR/test-brew-formula.sh"
    "$SCRIPT_DIR/test-brew-formula.sh" "$PACKAGE_NAME"

    if [ $? -ne 0 ]; then
      echo "❌ Formula tests failed."
      exit 1
    fi

    echo "✅ Formula tests completed successfully."
    echo "To install the formula locally, you can run:"
    echo "  brew install --build-from-source package-managers/brew/Formula/${PACKAGE_NAME}.rb"

    # Check if we're in a GitHub repository and gh CLI is available
    if command -v gh &>/dev/null && git rev-parse --is-inside-work-tree &>/dev/null; then
      echo ""
      echo "Would you like to trigger a GitHub workflow to update the Homebrew formula? (y/n)"
      read -r TRIGGER_WORKFLOW

      if [[ ${TRIGGER_WORKFLOW} == "y" || ${TRIGGER_WORKFLOW} == "Y" ]]; then
        # Get the current branch
        BRANCH=$(git branch --show-current)

        echo "Triggering Homebrew formula update workflow on branch ${BRANCH}..."
        gh workflow run update-homebrew-formula.yml --ref "${BRANCH}"

        # Wait a moment for the workflow to be registered
        echo "Waiting for workflow to start..."
        sleep 2

        # Get the run ID of the latest workflow
        RUN_ID=$(gh run list --workflow="Update Homebrew Formula" --limit 1 --json databaseId --jq '.[0].databaseId')

        # Display the status of the workflow run
        echo "Latest workflow run status:"
        echo ""
        gh run list --workflow="Update Homebrew Formula" --limit 1

        if [[ -n ${RUN_ID} ]]; then
          echo ""
          echo "You can check the detailed status with:"
          echo "gh run view ${RUN_ID}"
          echo ""
          echo "Watching workflow progress in real-time..."
          gh run watch "${RUN_ID}"
        fi
      fi
    fi
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
