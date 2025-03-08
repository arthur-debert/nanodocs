# PyPI to APT Package Generator

This project provides tools to generate Debian packages from PyPI packages. It
includes:

1. A script to generate Debian package files from a PyPI package
2. A Docker-based build environment to build and test the Debian package

## Prerequisites

- Docker installed on your system
- Python 3.x

## Files

- `bin/pypi-to-apt`: Script to generate Debian package files from a PyPI package
- `bin/docker-apt-build`: Script to build and test Debian packages using Docker
- `Dockerfile.apt`: Dockerfile for the Debian package build environment

## Usage

### Building a Debian Package from a PyPI Package

To build a Debian package from a PyPI package, run:

```bash
bin/docker-apt-build <package_name>
```

For example, to build a Debian package for the `nanodoc` package:

```bash
bin/docker-apt-build nanodoc
```

This will:

1. Build a Docker image with the necessary Debian packaging tools
2. Run a container with the current project directory mounted as a volume
3. Generate Debian package files for the specified PyPI package
4. Build the Debian package
5. Install the package in the container
6. Test the package by running it with `--help`

The built Debian package will be available in the `/tmp/debian-build` directory.

### Manual Usage

If you want more control over the process, you can use the `pypi-to-apt` script
directly:

```bash
# Generate and build a Debian package
bin/pypi-to-apt <package_name> [--output-dir <output_directory>]
```

By default, the package will be built in `/tmp/debian-build`. You can specify a
different output directory with the `--output-dir` option.

## How It Works

The `pypi-to-apt` script:

1. Creates a temporary directory and virtual environment
2. Installs the specified PyPI package
3. Extracts metadata from the package
4. Creates a Debian package structure with the necessary files
5. Builds the package using `dpkg-deb`
6. Outputs the .deb file to the specified directory (default:
   `/tmp/debian-build`)

The `docker-apt-build` script:

1. Builds a Docker image with the necessary Debian packaging tools
2. Runs a container with the current project directory mounted
3. Executes the `pypi-to-apt` script inside the container
4. Installs and tests the Debian package

## Running on macOS

Since Debian packaging tools are designed for Linux, this project uses Docker to
provide a Linux environment for building Debian packages. This allows you to
build Debian packages on macOS or any other platform that supports Docker.
