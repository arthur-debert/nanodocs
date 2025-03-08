#!/bin/bash
# Setup script for package-managers
# This script creates the necessary symlinks and setup when the package-managers
# directory is copied to a new repository.

set -e

# Get the directory of the current script
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# Get the package-managers directory (parent of repo-install)
PACKAGE_MANAGERS_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
# Get the repository root (parent of package-managers)
REPO_ROOT="$(cd "$PACKAGE_MANAGERS_DIR/.." && pwd)"

echo "Setting up package-managers in $REPO_ROOT..."

# Create Formula symlink
echo "Creating Formula symlink..."
ln -sf "$PACKAGE_MANAGERS_DIR/brew/Formula" "$REPO_ROOT/Formula"

# Create bin directory and wrapper scripts
echo "Creating bin directory and wrapper scripts..."
mkdir -p "$REPO_ROOT/bin"

# Create wrapper scripts for brew-related scripts
for script in brew-update pypi-to-brew test-brew-formula.sh update-brew-formula.sh; do
  echo "Creating wrapper for $script..."
  cat >"$REPO_ROOT/bin/$script" <<EOF
#!/bin/bash
# Wrapper script for package-managers/brew/$script

# Get the directory of the current script
SCRIPT_DIR="\$(cd "\$(dirname "\${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="\$(cd "\$SCRIPT_DIR/.." && pwd)"

# Execute the actual script with all arguments passed through
"\$PROJECT_ROOT/package-managers/brew/$script" "\$@"
EOF
  chmod +x "$REPO_ROOT/bin/$script"
done

# Create wrapper scripts for debian-related scripts
for script in apt-update docker-apt-build pypi-to-apt setup-apt-repo.sh update-apt-package.sh test-apt-package.sh; do
  echo "Creating wrapper for $script..."
  cat >"$REPO_ROOT/bin/$script" <<EOF
#!/bin/bash
# Wrapper script for package-managers/debian/$script

# Get the directory of the current script
SCRIPT_DIR="\$(cd "\$(dirname "\${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="\$(cd "\$SCRIPT_DIR/.." && pwd)"

# Execute the actual script with all arguments passed through
"\$PROJECT_ROOT/package-managers/debian/$script" "\$@"
EOF
  chmod +x "$REPO_ROOT/bin/$script"
done

# Create wrapper scripts for common scripts
for script in about-py-package package-update pypi-new-release; do
  echo "Creating wrapper for $script..."
  cat >"$REPO_ROOT/bin/$script" <<EOF
#!/bin/bash
# Wrapper script for package-managers/common/$script

# Get the directory of the current script
SCRIPT_DIR="\$(cd "\$(dirname "\${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="\$(cd "\$SCRIPT_DIR/.." && pwd)"

# Execute the actual script with all arguments passed through
"\$PROJECT_ROOT/package-managers/common/$script" "\$@"
EOF
  chmod +x "$REPO_ROOT/bin/$script"
done

# Copy LICENSE to bin directory
echo "Copying LICENSE to bin directory..."
cp "$PACKAGE_MANAGERS_DIR/common/LICENSE" "$REPO_ROOT/bin/LICENSE"

# Update GitHub workflow files if they exist
GITHUB_DIR="$REPO_ROOT/.github"
if [ -d "$GITHUB_DIR" ]; then
  echo "Updating GitHub workflow files..."

  # Update update-apt-package.yml
  APT_WORKFLOW="$GITHUB_DIR/workflows/update-apt-package.yml"
  if [ -f "$APT_WORKFLOW" ]; then
    echo "Updating $APT_WORKFLOW..."
    sed -i.bak 's|bin/pypi-to-apt|package-managers/debian/pypi-to-apt|g' "$APT_WORKFLOW"
    sed -i.bak 's|bin/about-py-package|package-managers/common/about-py-package|g' "$APT_WORKFLOW"
    sed -i.bak 's|bin/update-apt-package.sh|package-managers/debian/update-apt-package.sh|g' "$APT_WORKFLOW"
    sed -i.bak 's|./Debian/|./package-managers/debian/|g' "$APT_WORKFLOW"
    sed -i.bak 's|git add Debian/|git add package-managers/debian/|g' "$APT_WORKFLOW"
    rm -f "$APT_WORKFLOW.bak"
  fi

  # Update update-homebrew-formula.yml
  BREW_WORKFLOW="$GITHUB_DIR/workflows/update-homebrew-formula.yml"
  if [ -f "$BREW_WORKFLOW" ]; then
    echo "Updating $BREW_WORKFLOW..."
    sed -i.bak 's|bin/pypi-to-brew|package-managers/brew/pypi-to-brew|g' "$BREW_WORKFLOW"
    sed -i.bak 's|bin/update-brew-formula.sh|package-managers/brew/update-brew-formula.sh|g' "$BREW_WORKFLOW"
    sed -i.bak 's|Formula/|package-managers/brew/Formula/|g' "$BREW_WORKFLOW"
    sed -i.bak 's|git add Formula/|git add package-managers/brew/Formula/|g' "$BREW_WORKFLOW"
    rm -f "$BREW_WORKFLOW.bak"
  fi
fi

echo "Setup complete!"
echo "You can now remove the original Debian and debian-build directories if they exist,"
echo "as their contents have been moved to package-managers/debian/."
