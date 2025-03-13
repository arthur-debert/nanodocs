#!/bin/bash
# Update APT package script
# This script generates a Debian package for a PyPI package and stores it in a designated directory

set -e

# Default values
NON_INTERACTIVE=false
PACKAGE_NAME="nanodoc"
FORCE_UPDATE=false
OUTPUT_DIR="package-managers/debian"

# Parse command line arguments
while [[ $# -gt 0 ]]; do
  case $1 in
  --non-interactive)
    NON_INTERACTIVE=true
    shift
    ;;
  --force)
    FORCE_UPDATE=true
    shift
    ;;
  --output-dir)
    OUTPUT_DIR="$2"
    shift 2
    ;;
  *)
    # Assume it's the package name
    PACKAGE_NAME="$1"
    shift
    ;;
  esac
done

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
  echo "To test the package, run: $SCRIPT_DIR/test-apt-package.sh $PACKAGE_NAME"
fi

# Check if we're in a GitHub repository and gh CLI is available
if command -v gh &>/dev/null && git rev-parse --is-inside-work-tree &>/dev/null; then
  if [[ ${NON_INTERACTIVE} == false ]]; then
    echo ""
    echo "Would you like to trigger a GitHub workflow to update the APT package? (y/n)"
    read -r TRIGGER_WORKFLOW

    if [[ ${TRIGGER_WORKFLOW} == "y" || ${TRIGGER_WORKFLOW} == "Y" ]]; then
      TRIGGER_WORKFLOW=true
    else
      TRIGGER_WORKFLOW=false
    fi
  else
    # In non-interactive mode, we always trigger the workflow
    TRIGGER_WORKFLOW=true
  fi

  if [[ ${TRIGGER_WORKFLOW} == true ]]; then
    # Get the current branch
    BRANCH=$(git branch --show-current)

    echo "Triggering APT package update workflow on branch ${BRANCH}..."
    gh workflow run update-apt-package.yml --ref "${BRANCH}" --field force_update=${FORCE_UPDATE} --field package_name=${PACKAGE_NAME}

    if [[ ${NON_INTERACTIVE} == false ]]; then
      # Wait a moment for the workflow to be registered
      echo "Waiting for workflow to start..."
      sleep 2

      # Get the run ID of the latest workflow
      RUN_ID=$(gh run list --workflow="Update APT Package" --limit 1 --json databaseId --jq '.[0].databaseId')

      # Display the status of the workflow run
      echo "Latest workflow run status:"
      echo ""
      gh run list --workflow="Update APT Package" --limit 1

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
fi
