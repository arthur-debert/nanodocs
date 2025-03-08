# Nanodoc APT Repository on GitHub

This document explains how to use the Nanodoc APT repository hosted directly on
GitHub.

## For Repository Maintainers

The APT packages are automatically generated and committed to the `Debian/`
directory by the GitHub workflow. No additional setup is required for hosting
the repository.

## For Users

To install nanodoc from GitHub, you have two options:

### Option 1: Direct Installation

The simplest approach is to download and install the package directly:

```bash
# Download the package
wget https://github.com/arthur-debert/nanodoc/raw/main/Debian/python3-nanodoc_0.3.1-1_all.deb

# Install the package
sudo apt install ./python3-nanodoc_0.3.1-1_all.deb
```

### Option 2: Set up GitHub as an APT Repository

For a more traditional APT repository experience:

1. Create a sources list file:

```bash
sudo tee /etc/apt/sources.list.d/nanodoc.list > /dev/null << EOF
deb [trusted=yes] https://raw.githubusercontent.com/arthur-debert/nanodoc/main/Debian ./
EOF
```

1. Update your package lists:

```bash
sudo apt update
```

1. Install nanodoc:

```bash
sudo apt install python3-nanodoc
```

Note: This approach uses `[trusted=yes]` to bypass GPG signing requirements,
which is acceptable for personal use but not recommended for production
environments.

## GitHub Workflow

The APT package is automatically updated when a new version is released to PyPI.
The GitHub workflow:

1. Detects new releases
2. Builds the Debian package
3. Tests the package
4. Commits it to the repository

You can manually trigger this process with:

```bash
bin/package-update apt
```

## Creating a Proper APT Repository Structure (Optional)

If you want a more traditional APT repository structure, you can use the
`bin/setup-apt-repo.sh` script to create it:

```bash
# Install required tools
sudo apt-get install reprepro gnupg

# Run the setup script
bin/setup-apt-repo.sh

# Commit the apt-repo directory to your repository
git add apt-repo
git commit -m "Add APT repository structure"
git push
```

Users would then use:

```bash
# Add the repository to sources
echo "deb [trusted=yes] https://raw.githubusercontent.com/arthur-debert/nanodoc/main/apt-repo stable main" | sudo tee /etc/apt/sources.list.d/nanodoc.list

# Update and install
sudo apt update
sudo apt install python3-nanodoc
```
