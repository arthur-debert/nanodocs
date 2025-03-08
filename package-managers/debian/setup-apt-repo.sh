#!/bin/bash
# Script to set up a custom APT repository for nanodoc

set -e

# Ensure we're in the project root
cd "$(dirname "$0")/.."

# Create repository directory structure
REPO_DIR="apt-repo"
mkdir -p "$REPO_DIR/conf"

# Create distribution configuration
cat >"$REPO_DIR/conf/distributions" <<EOF
Origin: Arthur Debert
Label: nanodoc
Codename: stable
Architectures: all
Components: main
Description: Repository for nanodoc packages
SignWith: no
EOF

# Function to add a package to the repository
add_package() {
  local PACKAGE_PATH="$1"
  local REPO_DIR="$2"

  # Add the package to the repository
  reprepro -b "$REPO_DIR" includedeb stable "$PACKAGE_PATH"

  echo "Package added to repository: $PACKAGE_PATH"
}

# Check if a package path was provided
if [ -n "$1" ]; then
  # Add the specified package
  add_package "$1" "$REPO_DIR"
else
  # Look for packages in the Debian directory
  for package in Debian/python3-*.deb; do
    if [ -f "$package" ]; then
      add_package "$package" "$REPO_DIR"
    fi
  done
fi

# Generate GPG key if it doesn't exist
if [ ! -f ~/.gnupg/nanodoc-apt-key.gpg ]; then
  echo "Generating GPG key for signing the repository..."
  gpg --batch --gen-key <<EOF
Key-Type: RSA
Key-Length: 4096
Name-Real: Nanodoc APT Repository
Name-Email: nanodoc-apt@example.com
Expire-Date: 0
%no-protection
EOF

  # Export the public key
  gpg --export --armor nanodoc-apt@example.com >"$REPO_DIR/nanodoc-apt.key"
  echo "GPG key generated and exported to $REPO_DIR/nanodoc-apt.key"
fi

echo "Repository setup complete at $REPO_DIR"
echo ""
echo "To host this repository:"
echo "1. Commit the $REPO_DIR directory to your GitHub repository"
echo "2. Push the changes to GitHub"
echo ""
echo "For users to add this repository, they need to:"
echo "1. Add the repository: echo 'deb [trusted=yes] https://raw.githubusercontent.com/arthur-debert/nanodoc/main/$REPO_DIR stable main' | sudo tee /etc/apt/sources.list.d/nanodoc.list"
echo "3. Update package lists: sudo apt update"
echo "4. Install the package: sudo apt install python3-nanodoc"
