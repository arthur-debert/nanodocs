#!/bin/bash

# Check if package exists on PyPI
pypi_package_exists() {
    local package_name=$1
    local version=$2

    # Try to get package info from PyPI
    if curl -s "https://pypi.org/pypi/$package_name/$version/json" | grep -q "404 Not Found"; then
        return 1
    fi
    return 0
}

# Get latest version from PyPI
get_pypi_latest_version() {
    local package_name=$1

    # Get latest version from PyPI
    local version
    version=$(curl -s "https://pypi.org/pypi/$package_name/json" |
        python3 -c "import sys, json; print(json.load(sys.stdin)['info']['version'])" 2>/dev/null)

    if [ -n "$version" ]; then
        echo "$version"
        return 0
    fi
    return 1
}

# Install package from local dist directory
install_local_package() {
    local package_name=$1
    local version=$2
    local temp_venv

    # Create temporary virtual environment
    temp_venv=$(create_temp_dir)/venv
    python3 -m venv "$temp_venv"

    # Activate virtual environment
    # shellcheck disable=SC1090
    source "$temp_venv/bin/activate"

    # Install package
    if [ -n "$version" ]; then
        pip install "dist/$package_name-$version.tar.gz"
    else
        # Find latest version in dist directory
        local dist_file
        dist_file=$(ls -t dist/"$package_name"-*.tar.gz | head -n1)
        pip install "$dist_file"
    fi

    local status=$?

    # Deactivate virtual environment
    deactivate

    return $status
}

# Install package from PyPI
install_pypi_package() {
    local package_name=$1
    local version=$2
    local temp_venv

    # Create temporary virtual environment
    temp_venv=$(create_temp_dir)/venv
    python3 -m venv "$temp_venv"

    # Activate virtual environment
    # shellcheck disable=SC1090
    source "$temp_venv/bin/activate"

    # Install package
    if [ -n "$version" ]; then
        pip install "$package_name==$version"
    else
        pip install "$package_name"
    fi

    local status=$?

    # Deactivate virtual environment
    deactivate

    return $status
}
