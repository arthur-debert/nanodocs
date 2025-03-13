PACKAGE MANAGERS

A drop-in solution for managing Python package releases across multiple platforms:
- PyPI releases
- GitHub releases
- APT packages
- Homebrew formulas

Supports both local execution and GitHub Actions workflows.

1. INSTALLATION

   1.1 Copy the package-managers directory to your project root
   1.2 Run the setup script:
       ./package-managers/repo-install/setup.sh
   1.3 Dependencies:
       - Python 3.7+
       - Poetry
       - GitHub CLI (gh)
       - Jinja2 (for templating)
       - Twine (for PyPI uploads)
       - For local APT builds: dpkg-deb, devscripts, debhelper

2. USAGE

   2.1 The new-release command

   bin/new-release [options]

   Options:
   --target=<target>       Specify a target to publish to (can be used multiple times)
                           Valid targets: pypi, apt, brew, github
   --local                 Run locally instead of using GitHub Actions
   --build                 Only build package manager manifests
   --verify                Only verify/test package manager manifests
   --commit                Only commit package manager manifests
   --force                 Force update even if no changes detected
   --version=<version>     Specify version (default: from pyproject.toml)

   Examples:
   bin/new-release --target=brew --target=apt --local
   bin/new-release --target=pypi --target=github
   bin/new-release --target=github --local

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
   ├── bin/                           # Wrapper scripts
   │   └── new-release                # Main release script
   ├── .github/workflows/
   │   └── package-release.yml        # Unified workflow file
   └── package-managers/
       ├── brew/                      # Homebrew-related files
       │   ├── Formula/
       │   │   └── <package_name>.rb
       │   ├── pypi-to-brew           # Generate Homebrew formula
       │   └── test-brew-formula.sh   # Test Homebrew formula
       ├── common/                    # Shared scripts
       │   └── new-release.py         # Main release script implementation
       ├── debian/                    # Debian/APT-related files
       │   ├── pypi-to-apt            # Generate APT package
       │   └── test-apt-package.sh    # Test APT package
       └── repo-install/              # Setup scripts
           ├── package-release.yml    # Template workflow file
           ├── requirements.txt       # Python dependencies
           ├── setup.sh               # Setup script
           └── new-release            # Template wrapper script

4. PACKAGE-SPECIFIC INFORMATION

   4.1 Debian/APT Packages

   Debian packages are generated from PyPI packages and stored in:
   package-managers/debian/<package_name>-<version>/

   To install a generated package manually:
   sudo apt install ./python3-<package_name>_<version>-1_all.deb

   4.2 Homebrew Formulas

   Homebrew formulas are generated from PyPI packages and stored in:
   package-managers/brew/Formula/<package_name>.rb

   To install a generated formula manually:
   brew install --formula ./package-managers/brew/Formula/<package_name>.rb

5. WHAT THE SETUP SCRIPT DOES

   The setup.sh script performs the following actions:
   - Creates necessary directories (bin, .github/workflows, etc.)
   - Installs dependencies using Homebrew (if available)
   - Installs Python dependencies from requirements.txt
   - Copies the new-release script to the bin directory
   - Sets up the GitHub workflow file
   - Removes deprecated workflow files
   - Makes all scripts executable
