#!/usr/bin/env python3
"""
new-release - Unified command for managing releases

This script provides a single entry point for creating PyPI releases and
updating package managers. It supports various options to control what
gets published, where the work is done, and which steps of the process
to execute.

Usage:
    new-release [options]

Options:
    --target=<target>       Specify a target to publish to 
                            (can be used multiple times)
                            Valid targets: pypi, apt, brew, github
    --local                 Run everything locally instead of using 
                            GitHub Actions
    --build                 Only build package manager manifests
    --verify                Only verify/test package manager manifests
    --commit                Only commit package manager manifests
    --force                 Force update even if no changes detected
    --version=<version>     Specify version (default: from pyproject.toml)
    --package-name=<name>   Specify package name (default: from
                            pyproject.toml or PACKAGE_NAME env var)
    --help                  Show this help message
"""

import argparse
import os
import subprocess
import sys
from pathlib import Path
import shutil


def parse_args():
    parser = argparse.ArgumentParser(
        description="Unified command for managing releases",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__.split("Usage:")[1]
    )
    
    # Add --target argument (can be specified multiple times)
    parser.add_argument(
        "--target", 
        action="append",
        dest="targets",
        choices=["pypi", "apt", "brew", "github"],
        help="Target to publish to (can be used multiple times)"
    )
    
    # Keep --publish-to for backward compatibility
    parser.add_argument(
        "--publish-to", 
        dest="publish_to",
        help="[DEPRECATED] Use --target instead"
    )
    
    parser.add_argument(
        "--local", 
        action="store_true",
        help="Run everything locally instead of using GitHub Actions"
    )
    
    # Process steps (if any specified, only do those steps)
    step_group = parser.add_argument_group("Process steps")
    step_group.add_argument(
        "--build", 
        action="store_true",
        help="Only build package manager manifests"
    )
    step_group.add_argument(
        "--verify", 
        action="store_true",
        help="Only verify/test package manager manifests"
    )
    step_group.add_argument(
        "--commit", 
        action="store_true",
        help="Only commit package manager manifests"
    )
    
    parser.add_argument(
        "--force", 
        action="store_true",
        help="Force update even if no changes detected"
    )
    
    parser.add_argument(
        "--version",
        help="Specify version (default: from pyproject.toml)"
    )
    
    parser.add_argument(
        "--release-notes",
        help="Path to release notes file"
    )
    
    parser.add_argument(
        "--package-name",
        help=("Specify package name (default: from pyproject.toml or "
              "PACKAGE_NAME env var)")
    )
    
    return parser.parse_args()


def run_command(cmd, check=True, capture_output=True):
    """Run a command and optionally return its output"""
    print(f"Running: {' '.join(cmd)}")
    if capture_output:
        result = subprocess.run(
            cmd, check=check, text=True, capture_output=True
        )
        return result.stdout.strip()
    else:
        subprocess.run(cmd, check=check, text=True)
        return None


def get_script_path(script_name):
    """Get the absolute path to a script in the repository"""
    repo_root = Path(__file__).parent.parent.parent
    
    # Map script names to their locations in the py-release directory
    script_locations = {
        "pypi-new-release": "common/pypi-new-release",
        "pypi-to-apt": "debian/pypi-to-apt",
        "test-apt-package.sh": "debian/test-apt-package.sh",
        "apt-update": "debian/apt-update",
        "pypi-to-brew": "brew/pypi-to-brew",
        "test-brew-formula.sh": "brew/test-brew-formula.sh",
        "brew-update": "brew/brew-update",
        "about-py-package": "common/about-py-package",
        "trigger-workflow": "common/trigger-workflow"
    }
    
    if script_name in script_locations:
        return repo_root / "py-release" / script_locations[script_name]
    else:
        # Fallback to bin directory for any scripts not in the mapping
        return repo_root / "bin" / script_name


def get_version():
    """Get the current version from pyproject.toml using poetry"""
    try:
        return run_command(["poetry", "version", "-s"])
    except Exception as e:
        print(f"Error getting version: {e}")
        sys.exit(1)


def get_package_name():
    """
    Get the package name from pyproject.toml.
    Returns the name of the package as defined in pyproject.toml.
    """
    try:
        # Try to get the package name from pyproject.toml using poetry
        result = run_command(["poetry", "version"], check=False)
        if result:
            # The output format is "package-name version"
            return result.split()[0]
    except Exception as e:
        print(f"Warning: Could not determine package name from pyproject.toml: {e}")
    
    # Fallback to a default name
    return "unknown-package"


def local_pypi_release(version, release_notes_file=None, steps=None):
    """Perform a local PyPI release"""
    print(f"Performing local PyPI release for version {version}")
    
    # Default to all steps if not provided
    if steps is None:
        steps = ["build", "verify", "commit"]
    
    # Build the package
    if "build" in steps:
        run_command(["poetry", "build"], capture_output=False)
    
    # Upload to PyPI (verify step for PyPI)
    if "verify" in steps and "build" in steps:
        run_command(["poetry", "publish"], capture_output=False)
    
    # Create GitHub release (commit step for PyPI)
    if "commit" in steps and "build" in steps:
        if shutil.which("gh"):
            tag_name = f"v{version}"
            release_cmd = [
                "gh", "release", "create", tag_name, 
                "--title", f"Release {tag_name}"
            ]
            
            # Add release notes if provided
            if release_notes_file:
                with open(release_notes_file, 'r') as f:
                    notes = f.read()
                release_cmd.extend(["--notes", notes])
            else:
                release_cmd.append("--generate-notes")
            
            # Add distribution files
            dist_files = list(Path("dist").glob("*"))
            for file in dist_files:
                release_cmd.append(str(file))
            
            run_command(release_cmd, capture_output=False)
        else:
            print("GitHub CLI not found. Skipping GitHub release creation.")
            print("To create a GitHub release manually, run:")
            print(f"  gh release create v{version} "
                  f"--title 'Release v{version}' dist/*")


def workflow_pypi_release(release_notes_file=None):
    """Trigger PyPI release workflow"""
    cmd = [str(get_script_path("trigger-workflow"))]
    
    if release_notes_file:
        cmd.extend(["--field", f"release_notes={release_notes_file}"])
    
    # Use the unified workflow
    cmd.extend(["--workflow", "Package Release", "--field", "publish_to=pypi"])
    
    try:
        run_command(cmd, capture_output=False)
        print("PyPI release workflow triggered successfully!")
    except subprocess.CalledProcessError as e:
        print("Warning: PyPI release workflow trigger failed:")
        print(f"  {e}")
        print("Continuing with the release process...")


def local_apt_build(package_name, force=False):
    """Build APT package locally"""
    cmd = [str(get_script_path("pypi-to-apt")), package_name]
    run_command(cmd, capture_output=False)


def local_apt_verify(package_name):
    """Verify APT package locally"""
    cmd = [str(get_script_path("test-apt-package.sh")), package_name]
    run_command(cmd, capture_output=False)


def local_apt_commit(package_name, version, force=False):
    """Commit APT package changes locally"""
    # Check if there are changes
    has_changes = False
    try:
        result = run_command(
            ["git", "diff", "--quiet", "py-release/debian/"], 
            check=False
        )
        has_changes = result.returncode != 0
    except Exception:  # Catch specific exceptions when possible
        has_changes = True
    
    if not has_changes and not force:
        print("No changes to APT package, skipping commit")
        return
    
    # Commit changes
    run_command(["git", "add", "py-release/debian/"])
    commit_msg = f"Update APT package for {package_name} to version {version}"
    try:
        run_command(["git", "commit", "-m", commit_msg])
        print("✅ Changes committed locally. To push, run: git push")
    except subprocess.CalledProcessError:
        print("No changes to commit or commit failed")


def local_brew_build(package_name, force=False):
    """Build Homebrew formula locally"""
    cmd = [str(get_script_path("pypi-to-brew")), package_name]
    run_command(cmd, capture_output=False)


def local_brew_verify(package_name):
    """Verify Homebrew formula locally"""
    cmd = [str(get_script_path("test-brew-formula.sh")), package_name]
    run_command(cmd, capture_output=False)


def local_brew_commit(package_name, version, force=False):
    """Commit Homebrew formula changes locally"""
    # Check if there are changes
    has_changes = False
    formula_path = f"py-release/brew/Formula/{package_name}.rb"
    try:
        result = run_command(
            ["git", "diff", "--quiet", formula_path], 
            check=False
        )
        has_changes = result.returncode != 0
    except Exception:  # Catch specific exceptions when possible
        has_changes = True
    
    if not has_changes and not force:
        print("No changes to Homebrew formula, skipping commit")
        return
    
    # Commit changes
    run_command(["git", "add", formula_path])
    commit_msg = (f"Update Homebrew formula for {package_name} "
                  f"to version {version}")
    try:
        run_command(["git", "commit", "-m", commit_msg])
        print("✅ Changes committed locally. To push, run: git push")
    except subprocess.CalledProcessError:
        print("No changes to commit or commit failed")


def workflow_apt_update(package_name, steps=None, force=False):
    """Trigger APT package update workflow"""
    cmd = [str(get_script_path("trigger-workflow"))]
    
    # Add steps parameter if provided
    if steps:
        steps_str = ",".join(steps)
        cmd.extend(["--field", f"steps={steps_str}"])
    
    # Add force parameter if true
    if force:
        cmd.extend(["--field", "force_update=true"])
    
    # Use the unified workflow
    cmd.extend(["--workflow", "Package Release", "--field", "publish_to=apt"])
    
    try:
        run_command(cmd, capture_output=False)
        print("APT package update workflow triggered successfully!")
    except subprocess.CalledProcessError as e:
        print("Warning: APT package update workflow trigger failed:")
        print(f"  {e}")
        print("Continuing with the release process...")


def workflow_brew_update(package_name, steps=None, force=False):
    """Trigger Homebrew formula update workflow"""
    cmd = [str(get_script_path("trigger-workflow"))]
    
    # Add steps parameter if provided
    if steps:
        steps_str = ",".join(steps)
        cmd.extend(["--field", f"steps={steps_str}"])
    
    # Add force parameter if true
    if force:
        cmd.extend(["--field", "force_update=true"])
    
    # Use the unified workflow
    cmd.extend(["--workflow", "Package Release", "--field", "publish_to=brew"])
    
    try:
        run_command(cmd, capture_output=False)
        print("Homebrew formula update workflow triggered successfully!")
    except subprocess.CalledProcessError as e:
        print("Warning: Homebrew formula update workflow trigger failed:")
        print(f"  {e}")
        print("Continuing with the release process...")


def create_github_release(version, release_notes_file=None):
    """Create a GitHub release locally"""
    if not shutil.which("gh"):
        print("GitHub CLI not found. Please install it to create GitHub releases.")
        print("See: https://cli.github.com/")
        return
    
    tag_name = f"v{version}"
    release_cmd = [
        "gh", "release", "create", tag_name, 
        "--title", f"Release {tag_name}"
    ]
    
    # Add release notes if provided
    if release_notes_file:
        with open(release_notes_file, 'r') as f:
            notes = f.read()
        release_cmd.extend(["--notes", notes])
    else:
        release_cmd.append("--generate-notes")
    
    # Add distribution files if they exist
    dist_path = Path("dist")
    if dist_path.exists():
        dist_files = list(dist_path.glob("*"))
        for file in dist_files:
            release_cmd.append(str(file))
    
    try:
        run_command(release_cmd, capture_output=False)
        print(f"✅ GitHub release {tag_name} created successfully!")
    except subprocess.CalledProcessError as e:
        print(f"Warning: Failed to create GitHub release: {e}")
        print("You can create it manually with:")
        print(f"  gh release create {tag_name} --title 'Release {tag_name}'")


def workflow_github_release(version, release_notes_file=None):
    """Trigger GitHub release workflow"""
    cmd = [str(get_script_path("trigger-workflow"))]
    
    if release_notes_file:
        cmd.extend(["--field", f"release_notes={release_notes_file}"])
    
    # Use the unified workflow
    cmd.extend(["--workflow", "Package Release", "--field", "targets=github"])
    
    try:
        run_command(cmd, capture_output=False)
        print("GitHub release workflow triggered successfully!")
    except subprocess.CalledProcessError as e:
        print("Warning: GitHub release workflow trigger failed:")
        print(f"  {e}")
        print("Continuing with the release process...")


def main():
    args = parse_args()
    
    # Process targets
    targets = []
    if args.targets:
        targets = args.targets
    elif args.publish_to:
        targets = args.publish_to.split(",")
    else:
        # Default targets if none specified
        targets = ["pypi", "apt", "brew"]
    
    # Get version
    version = args.version or get_version()
    print(f"Using version: {version}")
    
    # Determine which steps to run
    steps = []
    if args.build:
        steps.append("build")
    if args.verify:
        steps.append("verify")
    if args.commit:
        steps.append("commit")
    
    # If no steps specified, run all steps
    if not steps:
        steps = ["build", "verify", "commit"]
    
    # Get package name from arguments, environment variable, or pyproject.toml
    package_name = args.package_name
    if not package_name:
        package_name = os.environ.get("PACKAGE_NAME")
    if not package_name:
        package_name = get_package_name()
    
    print(f"Using package name: {package_name}")
    
    # Process GitHub release if requested
    if "github" in targets:
        if args.local:
            # Create GitHub release locally
            create_github_release(version, args.release_notes)
        else:
            # Trigger GitHub workflow for GitHub release
            workflow_github_release(version, args.release_notes)
    
    # Process PyPI release if requested
    if "pypi" in targets:
        if args.local:
            # Run local PyPI release
            local_pypi_release(version, args.release_notes, steps)
        else:
            # Trigger GitHub workflow for PyPI release
            workflow_pypi_release(args.release_notes)
    
    # Process APT package if requested
    if "apt" in targets:
        if args.local:
            # Run local APT package update
            if "build" in steps:
                local_apt_build(package_name, args.force)
            if "verify" in steps:
                local_apt_verify(package_name)
            if "commit" in steps:
                local_apt_commit(package_name, version, args.force)
        else:
            # Trigger GitHub workflow for APT package update
            workflow_apt_update(package_name, steps, args.force)
    
    # Process Homebrew formula if requested
    if "brew" in targets:
        if args.local:
            # Run local Homebrew formula update
            if "build" in steps:
                local_brew_build(package_name, args.force)
            if "verify" in steps:
                local_brew_verify(package_name)
            if "commit" in steps:
                local_brew_commit(package_name, version, args.force)
        else:
            # Trigger GitHub workflow for Homebrew formula update
            workflow_brew_update(package_name, steps, args.force)
    
    print("Release process completed successfully!")


if __name__ == "__main__":
    main() 