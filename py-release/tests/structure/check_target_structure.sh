#!/bin/bash
set -e

# Get the directory of the current script
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PY_RELEASE_DIR="$(cd "$SCRIPT_DIR/../.." && pwd)"

# Source common functions
source "$PY_RELEASE_DIR/lib/common.sh"

# List of all targets
TARGETS=(pypi github apt brew)

# Required files for each target
REQUIRED_FILES=(
    "build"
    "check"
    "publish"
    "verify"
    "lib"
)

# Common functions that should be used
COMMON_FUNCTIONS=(
    "log_info"
    "log_error"
    "log_warn"
    "check_dependencies"
    "validate_version"
    "check_status"
)

check_target_structure() {
    local target=$1
    local target_dir="$PY_RELEASE_DIR/$target"
    local status=0

    log_info "Checking structure for target: $target"

    # Check if target directory exists
    if [ ! -d "$target_dir" ]; then
        log_error "Target directory $target_dir does not exist"
        return 1
    fi

    # Check required files and directories
    for file in "${REQUIRED_FILES[@]}"; do
        if [ ! -e "$target_dir/$file" ]; then
            log_error "Missing required file/directory: $file"
            status=1
        elif [ "$file" != "lib" ] && [ ! -x "$target_dir/$file" ]; then
            log_error "Script $file is not executable"
            status=1
        fi
    done

    # Check for target-specific utils in lib directory
    if [ ! -d "$target_dir/lib" ]; then
        log_error "Missing lib directory for target-specific utilities"
        status=1
    fi

    # Check common function usage in scripts
    for script in build check publish verify; do
        if [ -f "$target_dir/$script" ]; then
            log_info "Checking common function usage in $script"
            for func in "${COMMON_FUNCTIONS[@]}"; do
                if ! grep -q "$func" "$target_dir/$script"; then
                    log_warn "Script $script might not be using common function: $func"
                fi
            done
        fi
    done

    # Check argument handling
    for script in build check publish verify; do
        if [ -f "$target_dir/$script" ]; then
            log_info "Checking argument handling in $script"

            # Check for version argument handling
            if ! grep -q -- "--version=" "$target_dir/$script"; then
                log_error "Script $script missing --version argument handling"
                status=1
            fi

            # Check for package-name argument handling
            if ! grep -q -- "--package-name=" "$target_dir/$script"; then
                log_error "Script $script missing --package-name argument handling"
                status=1
            fi

            # Check for force argument handling
            if ! grep -q -- "--force" "$target_dir/$script"; then
                log_error "Script $script missing --force argument handling"
                status=1
            fi
        fi
    done

    return $status
}

main() {
    local overall_status=0

    # Check each target
    for target in "${TARGETS[@]}"; do
        if ! check_target_structure "$target"; then
            overall_status=1
        fi
    done

    if [ $overall_status -eq 0 ]; then
        log_info "All structure tests passed!"
    else
        log_error "Some structure tests failed"
    fi

    return $overall_status
}

# Run main if script is executed directly
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi
