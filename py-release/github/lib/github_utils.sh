#!/bin/bash

# Check if a GitHub release exists
github_release_exists() {
    local package_name=$1
    local version=$2

    # Try to get release info from GitHub
    if gh release view "v$version" &>/dev/null; then
        return 0
    fi
    return 1
}

# Create GitHub release assets directory
prepare_release_assets() {
    local assets_dir=".github/release-assets"
    mkdir -p "$assets_dir"
    echo "$assets_dir"
}

# Generate release notes
generate_release_notes() {
    local version=$1
    local package_name=$2
    local notes_file
    notes_file=$(prepare_release_assets)/release-notes.md

    {
        echo "# $package_name v$version"
        echo
        echo "## Changes"
        echo
        # Get changes since last tag
        if git describe --tags --abbrev=0 &>/dev/null; then
            local last_tag
            last_tag=$(git describe --tags --abbrev=0)
            git log --pretty=format:"* %s" "$last_tag"..HEAD
        else
            git log --pretty=format:"* %s"
        fi
    } >"$notes_file"

    echo "$notes_file"
}

# Validate release assets
validate_release_assets() {
    local assets_dir=".github/release-assets"

    # Check if assets directory exists
    if [ ! -d "$assets_dir" ]; then
        return 1
    fi

    # Check if release notes exist
    if [ ! -f "$assets_dir/release-notes.md" ]; then
        return 1
    fi

    return 0
}

# Create GitHub release
create_github_release() {
    local version=$1
    local package_name=$2
    local notes_file=$3

    gh release create "v$version" \
        --title "$package_name v$version" \
        --notes-file "$notes_file" \
        "$notes_file"
}

# Get latest GitHub release version
get_github_latest_version() {
    local package_name=$1

    # Get latest release version from GitHub
    gh release list --limit 1 | awk '{print $1}' | sed 's/^v//'
}
