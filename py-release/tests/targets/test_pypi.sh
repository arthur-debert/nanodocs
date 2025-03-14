#!/bin/bash
set -e

# Get the directory of the current script
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PY_RELEASE_DIR="$(cd "$SCRIPT_DIR/../.." && pwd)"

# Source common functions
source "$PY_RELEASE_DIR/lib/common.sh"

# Test configuration
TEST_VERSION="0.0.1-test"
TEST_PACKAGE="py-release-test"
TEST_PROJECT_DIR=""

setup() {
    # Create temporary project directory
    TEST_PROJECT_DIR=$(mktemp -d)
    log_info "Created test project directory: $TEST_PROJECT_DIR"

    # Create minimal Python project
    cd "$TEST_PROJECT_DIR"

    # Create pyproject.toml
    cat >pyproject.toml <<EOF
[tool.poetry]
name = "$TEST_PACKAGE"
version = "$TEST_VERSION"
description = "Test package for py-release QA"
authors = ["Test <test@example.com>"]

[tool.poetry.dependencies]
python = "^3.7"

[build-system]
requires = ["poetry-core"]
build-backend = "poetry.core.masonry.api"
EOF

    # Create package directory and __init__.py
    mkdir "$TEST_PACKAGE"
    echo 'def hello(): return "Hello from py-release test"' >"$TEST_PACKAGE/__init__.py"

    # Initialize git repo (needed for some operations)
    git init
    git add .
    git commit -m "Initial commit"

    # Install py-release
    "$PY_RELEASE_DIR/setup" "$TEST_PROJECT_DIR"
}

cleanup() {
    if [ -n "$TEST_PROJECT_DIR" ] && [ -d "$TEST_PROJECT_DIR" ]; then
        log_info "Cleaning up test directory: $TEST_PROJECT_DIR"
        rm -rf "$TEST_PROJECT_DIR"
    fi
}

test_build() {
    log_info "Testing PyPI build step..."

    cd "$TEST_PROJECT_DIR"
    if ! "$PY_RELEASE_DIR/pypi/build" --version="$TEST_VERSION" --package-name="$TEST_PACKAGE"; then
        log_error "Build step failed"
        return 1
    fi

    # Verify dist files were created
    if [ ! -d "dist" ] || [ -z "$(ls -A dist)" ]; then
        log_error "No distribution files were created"
        return 1
    fi

    log_info "Build step passed"
    return 0
}

test_check() {
    log_info "Testing PyPI check step..."

    cd "$TEST_PROJECT_DIR"
    if ! "$PY_RELEASE_DIR/pypi/check" --version="$TEST_VERSION" --package-name="$TEST_PACKAGE"; then
        log_error "Check step failed"
        return 1
    fi

    log_info "Check step passed"
    return 0
}

test_publish() {
    log_info "Testing PyPI publish step..."
    log_warn "This is a manual test as it requires PyPI credentials"
    log_info "To test manually:"
    log_info "1. Set up PyPI credentials (~/.pypirc or environment)"
    log_info "2. Run: $PY_RELEASE_DIR/pypi/publish --version=$TEST_VERSION --package-name=$TEST_PACKAGE"
    log_info "3. Verify package appears on PyPI"

    # For now, we'll skip this test
    log_warn "Skipping publish test - requires manual verification"
    return 0
}

test_verify() {
    log_info "Testing PyPI verify step..."
    log_warn "This test depends on successful publish"
    log_info "To test manually after publishing:"
    log_info "1. Run: $PY_RELEASE_DIR/pypi/verify --version=$TEST_VERSION --package-name=$TEST_PACKAGE"
    log_info "2. Verify package can be installed from PyPI"

    # For now, we'll skip this test
    log_warn "Skipping verify test - requires manual verification"
    return 0
}

main() {
    local status=0

    # Set up trap to clean up on exit
    trap cleanup EXIT

    # Setup test environment
    setup

    # Run tests
    if ! test_build; then
        status=1
    fi

    if ! test_check; then
        status=1
    fi

    if ! test_publish; then
        status=1
    fi

    if ! test_verify; then
        status=1
    fi

    if [ $status -eq 0 ]; then
        log_info "All PyPI tests completed successfully!"
    else
        log_error "Some PyPI tests failed"
    fi

    return $status
}

# Run main if script is executed directly
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi
