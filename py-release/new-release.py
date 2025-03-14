#!/usr/bin/env python3
import argparse
import os
import sys
import subprocess
from typing import List, Optional


class ReleaseTarget:
    def __init__(self, name: str, base_dir: str):
        self.name = name
        self.base_dir = base_dir
        self.steps = ["build", "check", "publish", "verify"]

    def run_step(
        self,
        step: str,
        version: Optional[str] = None,
        package_name: Optional[str] = None,
        force: bool = False,
    ) -> int:
        if step not in self.steps:
            print(f"Error: Unknown step '{step}' for target '{self.name}'")
            return 1

        script = os.path.join(self.base_dir, self.name, step)
        cmd = [script]

        if version:
            cmd.append(f"--version={version}")
        if package_name:
            cmd.append(f"--package-name={package_name}")
        if force:
            cmd.append("--force")

        return subprocess.call(cmd)


def get_available_targets(base_dir: str) -> List[str]:
    """Return list of available targets by checking directories."""
    return [
        d
        for d in os.listdir(base_dir)
        if os.path.isdir(os.path.join(base_dir, d)) and d not in ["lib", "common"]
    ]


def main():
    # Get py-release directory
    py_release_dir = os.path.dirname(os.path.abspath(__file__))

    # Get available targets
    targets = get_available_targets(py_release_dir)

    parser = argparse.ArgumentParser(
        description="Manage releases across multiple platforms"
    )
    parser.add_argument("--target", choices=targets, help="Specific target to run")
    parser.add_argument(
        "--local", action="store_true", help="Run locally instead of GitHub Actions"
    )
    parser.add_argument("--build", action="store_true", help="Run until build step")
    parser.add_argument("--check", action="store_true", help="Run until check step")
    parser.add_argument("--publish", action="store_true", help="Run until publish step")
    parser.add_argument("--verify", action="store_true", help="Run all steps (default)")
    parser.add_argument(
        "--force", action="store_true", help="Force update even if no changes"
    )
    parser.add_argument("--version", help="Override version")
    parser.add_argument("--package-name", help="Override package name")

    args = parser.parse_args()

    # Determine which step to run until
    if args.build:
        final_step = "build"
    elif args.check:
        final_step = "check"
    elif args.publish:
        final_step = "publish"
    else:  # Default to verify
        final_step = "verify"

    # Determine which targets to run
    targets_to_run = [args.target] if args.target else targets

    # Create target objects
    target_objects = [ReleaseTarget(t, py_release_dir) for t in targets_to_run]

    # Run each target through the steps
    for target in target_objects:
        print(f"\nProcessing target: {target.name}")
        for step in target.steps:
            if (
                subprocess.call(
                    ["chmod", "+x", os.path.join(py_release_dir, target.name, step)]
                )
                != 0
            ):
                print(
                    f"Error: Could not make {step} script executable for {target.name}"
                )
                return 1

            result = target.run_step(
                step,
                version=args.version,
                package_name=args.package_name,
                force=args.force,
            )

            if result != 0:
                print(f"Error: {step} failed for target {target.name}")
                return result

            if step == final_step:
                break

    return 0


if __name__ == "__main__":
    sys.exit(main())
