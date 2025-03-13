PY-RELEASE

A drop-in solution for managing Python package releases across multiple platforms:
- PyPI releases
- GitHub releases
- APT packages
- Homebrew formulas

Supports both local execution and GitHub Actions workflows.

1. INSTALLATION

   1.1 Copy the py-release directory to your project root
   1.2 Run the setup script:
       ./py-release/setup # will install dependencies if not available [deps]

2. USAGE

2.1 The new-release command. By default it will publish to all targets using GitHub Actions.

    py-release/new-release

Options:

    --target=<target>       Specify a target to publish to (can be used multiple times)
                            Valid targets: pypi, apt, brew, github
    --local                 Run locally instead of using GitHub Actions
    --build                 Only build package manager manifests
    --verify                Only verify/test package manager manifests
    --commit                Only commit package manager manifests
    --force                 Force update even if no changes detected
    --version=<version>     Specify version (default: from pyproject.toml)
    --package-name=<name>   Specify package name (default: from pyproject.toml
                        or PACKAGE_NAME environment variable)

Examples:

    py-release/new-release --target=brew --target=apt --local
    py-release/new-release --target=pypi --target=github
    py-release/new-release --target=github --local
    py-release/new-release --target=brew --package-name=my package --local

You can also set the package name using an environment variable:
PACKAGE_NAME=my-package py-release/new-release --target=brew --local

2.2 GitHub Workflow

The unified workflow (package-release.yml) can be triggered manually or
automatically after a GitHub release is published.

Workflow inputs:
- targets: Comma-separated list of targets (pypi,brew,apt,github)
- force_update: Force update even if no changes detected
- steps: Comma-separated list of steps (build,verify,commit)
- package_name: Name of the package (default: project name)
- release_notes: Custom release notes content

3. DIRECTORY STRUCTURE

   After setup, your repository will have the following structure:

   your-repo/
   ├── .github/workflows/
   │   └── package-release.yml        # Unified workflow file
   └── py-release/
       ├── Brewfile                   # Homebrew dependencies
       ├── new-release               # Main release script
       ├── package-release.yml       # Template workflow file
       ├── requirements.txt          # Python dependencies
       ├── setup                     # Setup script
       ├── brew/                     # Homebrew-related files
       │   ├── Formula/
       │   │   └── <package_name>.rb
       │   ├── pypi-to-brew          # Generate Homebrew formula
       │   └── test-brew-formula.sh  # Test Homebrew formula
       ├── common/                   # Shared scripts
       │   └── new-release.py        # Main release script implementation
       └── debian/                   # Debian/APT-related files
           ├── pypi-to-apt           # Generate APT package
           └── test-apt-package.sh   # Test APT package

4. PACKAGE-SPECIFIC INFORMATION

   4.1 Debian/APT Packages

   Debian packages are generated from PyPI packages and stored in:
   py-release/debian/<package_name>-<version>/

   To install a generated package manually:
   sudo apt install ./python3-<package_name>_<version>-1_all.deb

   Note: When generating a new Debian package, old package directories for
   previous versions are automatically cleaned up to prevent repository clutter.

   4.2 Homebrew Formulas

   Homebrew formulas are generated from PyPI packages and stored in:
   py-release/brew/Formula/<package_name>.rb

   To install a generated formula manually:
   brew install --formula ./py-release/brew/Formula/<package_name>.rb

5. WHAT THE SETUP SCRIPT DOES

   The setup script performs the following actions:
   - Creates necessary directories (.github/workflows, etc.)
   - Installs dependencies using Homebrew (if available)
   - Installs Python dependencies from requirements.txt
   - Sets up the GitHub workflow file
   - Makes all scripts executable

[deps]
    - Python 3.7+
    - Poetry
    - GitHub CLI (gh)
    - Jinja2 (for templating)
    - Twine (for PyPI uploads)
    - For local APT builds: dpkg-deb, devscripts, debhelper
