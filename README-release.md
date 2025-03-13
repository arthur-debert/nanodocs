# Release Process

This document explains how to create releases and update package managers for
the project.

## Overview

The release process consists of three main steps:

1. **PyPI Release**: Publishing the package to PyPI and creating a GitHub
   release
2. **APT Package Update**: Generating and updating the Debian package
3. **Homebrew Formula Update**: Generating and updating the Homebrew formula

## Using the `new-release` Command

The `new-release` command provides a unified interface for managing releases. By
default, it performs a complete release process, including PyPI release and
package manager updates.

### Basic Usage

```bash
# Create a complete release (PyPI + APT + Homebrew)
bin/new-release

# Create a release with custom release notes
bin/new-release --release-notes release-notes.md
```

### Selective Publishing

You can choose which targets to publish to:

```bash
# Only publish to PyPI
bin/new-release --publish-to=pypi

# Only update package managers
bin/new-release --publish-to=apt,brew

# Only update APT package
bin/new-release --publish-to=apt
```

### Local Execution

By default, the command triggers GitHub workflows. You can run everything
locally instead:

```bash
# Run the entire process locally
bin/new-release --local
```

### Selective Steps

You can choose which steps of the process to run:

```bash
# Only build package manager manifests
bin/new-release --build

# Build and verify, but don't commit
bin/new-release --build --verify

# Only commit previously generated manifests
bin/new-release --commit
```

### Force Update

You can force updates even if no changes are detected:

```bash
# Force update all package managers
bin/new-release --force
```

### Combining Options

You can combine the options for more specific control:

```bash
# Update only the APT package locally, only building it
bin/new-release --publish-to=apt --local --build

# Update both package managers, but only commit changes
bin/new-release --publish-to=apt,brew --commit
```

## Advanced Usage

### Specifying Version

By default, the version is read from `pyproject.toml`. You can override it:

```bash
bin/new-release --version=1.2.3
```

### Debugging Package Manager Updates

For debugging package manager updates:

```bash
# Debug APT package generation
bin/new-release --publish-to=apt --local --build

# Debug Homebrew formula generation
bin/new-release --publish-to=brew --local --build
```

## Legacy Scripts

The following scripts are still available for more granular control:

- `bin/pypi-new-release`: Trigger PyPI release via GitHub workflow
- `bin/pypi-to-apt`: Convert PyPI package to APT package
- `bin/pypi-to-brew`: Convert PyPI package to Homebrew formula
- `bin/test-apt-package.sh`: Test APT package
- `bin/test-brew-formula.sh`: Test Homebrew formula
- `bin/update-apt-package.sh`: Full APT package update process
- `bin/update-brew-formula.sh`: Full Homebrew formula update process
- `bin/apt-update`: Trigger GitHub workflow for APT update
- `bin/brew-update`: Trigger GitHub workflow for Homebrew update
- `bin/update-all-packages`: Update both APT and Homebrew packages
