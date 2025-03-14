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

2. CONCEPTS

2.1 Release Targets
    There are two distinct target types:
    - Push targets (github, pypi): We push releases to external services
    - Pull targets (apt, brew): We maintain package definitions in our repo

2.2 Release Steps
    Each target follows these steps in sequence:
    
    build  → Generate required artifacts
            - PyPI: Build distribution files
            - GitHub: Prepare release notes and assets
            - APT: Generate debian package
            - Brew: Generate formula file
    
    check  → Test locally before publishing
            - PyPI: Install from local dist
            - GitHub: Validate release assets
            - APT: Install local package
            - Brew: Install local formula
    
    publish→ Make changes available
            - PyPI: Upload to PyPI
            - GitHub: Create release
            - APT: Commit package to repo
            - Brew: Commit formula to repo
    
    verify → Test as end user
            - PyPI: Install from PyPI
            - GitHub: Check release via API
            - APT: Install via apt
            - Brew: Install via brew

3. USAGE

3.1 The new-release command
    By default runs all steps for all targets using GitHub Actions:
    
    ./py-release/new-release

    Options:
    --target=<target>     Specify target (pypi,apt,brew,github)
    --local              Run locally instead of GitHub Actions
    --build             Run until build step
    --check             Run until check step
    --publish           Run until publish step
    --verify            Run all steps (default)
    --force             Force update even if no changes
    --version=<ver>     Override version
    --package-name=<n>  Override package name

    Examples:
    ./py-release/new-release --target=brew --check --local
    ./py-release/new-release --target=pypi --publish
    PACKAGE_NAME=foo ./py-release/new-release --target=apt

3.2 Direct Target Scripts
    Each target has individual scripts for each step:
    
    ./py-release/pypi/build   # Build PyPI package
    ./py-release/apt/check    # Test APT package
    ./py-release/brew/publish # Commit Brew formula
    ./py-release/github/verify# Verify GitHub release

4. DIRECTORY STRUCTURE

   your-repo/
   └── py-release/
       ├── new-release       # Main entry point
       ├── setup            # Setup script
       ├── lib/             # Shared utilities
       ├── pypi/            # PyPI release scripts
       │   ├── build       # Build distribution
       │   ├── check       # Test local install
       │   ├── publish     # Upload to PyPI
       │   ├── verify      # Test PyPI install
       │   └── lib/        # PyPI-specific utilities
       ├── github/          # GitHub release scripts
       │   ├── build       # Prepare release
       │   ├── check       # Validate assets
       │   ├── publish     # Create release
       │   ├── verify      # Verify via API
       │   └── lib/        # GitHub-specific utilities
       ├── apt/             # APT package scripts
       │   ├── build       # Generate package
       │   ├── check       # Test local install
       │   ├── publish     # Commit to repo
       │   ├── verify      # Test apt install
       │   └── lib/        # APT-specific utilities
       └── brew/            # Homebrew scripts
           ├── build       # Generate formula
           ├── check       # Test local install
           ├── publish     # Commit to repo
           ├── verify      # Test brew install
           └── lib/        # Homebrew-specific utilities

5. DEPENDENCIES [deps]
    - Python 3.7+
    - Poetry
    - GitHub CLI (gh)
    - Jinja2 (for templating)
    - Twine (for PyPI uploads)
    - For local APT builds: dpkg-deb, devscripts, debhelper
