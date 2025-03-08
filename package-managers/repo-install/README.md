# Package Managers Setup

This directory contains scripts to set up the package-managers directory in a
new repository.

## Usage

When you copy the `package-managers` directory to a new repository, run the
`setup.sh` script to create the necessary symlinks and wrapper scripts:

```bash
# Navigate to the repository root
cd /path/to/your/repo

# Run the setup script
./package-managers/repo-install/setup.sh
```

## What the Setup Script Does

The `setup.sh` script performs the following actions:

1. Creates a symlink from `Formula` to `package-managers/brew/Formula` in the
   repository root
2. Creates a `bin` directory in the repository root with wrapper scripts for all
   the package management scripts
3. Updates GitHub workflow files if they exist to point to the new script
   locations
4. Copies the LICENSE file to the bin directory

## After Setup

After running the setup script, you can:

1. Remove the original `Debian` and `debian-build` directories if they exist, as
   their contents have been moved to `package-managers/debian/`
2. Use the scripts in the `bin` directory as before, which will now execute the
   scripts in the `package-managers` directory

## Directory Structure

After setup, your repository will have the following structure:

```text
your-repo/
├── bin/                           # Wrapper scripts
│   ├── about-py-package
│   ├── apt-update
│   ├── brew-update
│   └── ...
├── Formula -> package-managers/brew/Formula  # Symlink
└── package-managers/
    ├── brew/                      # Homebrew-related files
    │   ├── Formula/
    │   │   └── nanodoc.rb
    │   ├── brew-update
    │   └── ...
    ├── common/                    # Shared scripts
    │   ├── about-py-package
    │   └── ...
    ├── debian/                    # Debian/APT-related files
    │   ├── apt-update
    │   └── ...
    └── repo-install/              # Setup scripts
        ├── README.md
        └── setup.sh
```
