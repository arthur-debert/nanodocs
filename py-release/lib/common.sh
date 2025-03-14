#!/bin/bash

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Logging functions
log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Version validation
validate_version() {
    local version=$1
    if [[ ! $version =~ ^[0-9]+\.[0-9]+\.[0-9]+(-[a-zA-Z0-9.]+)?$ ]]; then
        log_error "Invalid version format: $version"
        log_error "Version must match: X.Y.Z or X.Y.Z-suffix"
        return 1
    fi
}

# Package name validation
validate_package_name() {
    local name=$1
    if [[ ! $name =~ ^[a-zA-Z][a-zA-Z0-9_-]*$ ]]; then
        log_error "Invalid package name: $name"
        log_error "Package name must start with a letter and contain only letters, numbers, underscores, and hyphens"
        return 1
    fi
}

# Check if running in GitHub Actions
is_github_actions() {
    [ -n "${GITHUB_ACTIONS:-}" ]
}

# Get the current version from pyproject.toml, setup.py, or VERSION file
get_current_version() {
    if [ -f "pyproject.toml" ]; then
        grep '^version = ' pyproject.toml | cut -d'"' -f2
    elif [ -f "setup.py" ]; then
        python3 -c "import re;print(re.search(r'version=['\"]([^'\"]+)['\"]', open('setup.py').read()).group(1))"
    elif [ -f "VERSION" ]; then
        cat VERSION
    else
        log_error "Could not determine current version"
        return 1
    fi
}

# Check if dependencies are installed
check_dependencies() {
    local missing=()
    for cmd in "$@"; do
        if ! command -v "$cmd" >/dev/null 2>&1; then
            missing+=("$cmd")
        fi
    done

    if [ ${#missing[@]} -ne 0 ]; then
        log_error "Missing required dependencies: ${missing[*]}"
        return 1
    fi
}

# Create temporary directory that gets cleaned up on exit
create_temp_dir() {
    local temp_dir
    temp_dir=$(mktemp -d)
    trap 'rm -rf "$temp_dir"' EXIT
    echo "$temp_dir"
}

# Check if a command succeeded and print appropriate message
check_status() {
    local status=$1
    local success_msg=${2:-"Operation completed successfully"}
    local error_msg=${3:-"Operation failed"}

    if [ $status -eq 0 ]; then
        log_info "$success_msg"
        return 0
    else
        log_error "$error_msg"
        return 1
    fi
}
