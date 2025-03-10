# Debian Packages

This directory contains Debian packages generated from PyPI packages.

The packages are automatically generated by the GitHub workflow in
`.github/workflows/update-apt-package.yml` when a new version is published to
PyPI.

## Installation

To install a package:

```bash
sudo apt install ./python3-<package_name>_<version>-1_all.deb
```

For example:

```bash
sudo apt install ./python3-nanodoc_0.3.1-1_all.deb
```

## Manual Generation

You can manually generate a Debian package using the `bin/update-apt-package.sh`
script:

```bash
bin/update-apt-package.sh <package_name>
```

This will generate a Debian package in this directory.
