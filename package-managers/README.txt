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
       - For local APT builds: dpkg-deb, devscripts, debhelper

2. USAGE

   2.1 The new-release command

   bin/new-release [options]

   Options:
   --publish-to=<targets>  Comma-separated list of targets (pypi,brew,apt)
   --local                 Run locally instead of using GitHub Actions
   --build                 Only build package manager manifests
   --verify                Only verify/test package manager manifests
   --commit                Only commit package manager manifests
   --force                 Force update even if no changes detected
   --version=<version>     Specify version (default: from pyproject.toml)

   2.2 GitHub Workflow

   The unified workflow (package-release.yml) can be triggered manually or 
   automatically after a GitHub release is published.

   Workflow inputs:
   - publish_to: Comma-separated list of targets (pypi,brew,apt)
   - force_update: Force update even if no changes detected
   - steps: Comma-separated list of steps (build,verify,commit)
   - package_name: Name of the package (default: project name)
   - release_notes: Custom release notes content
