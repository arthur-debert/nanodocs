# Incremental Test Plan for Release Process

This document outlines a step-by-step approach to testing the new unified
release process. Each step builds on the previous one, gradually increasing
complexity and scope.

## Prerequisites

Before starting the tests, ensure:

1. You have a working Python environment with Poetry installed
2. You have the GitHub CLI (`gh`) installed and authenticated
3. You have appropriate permissions for the repository
4. You have a test PyPI account for testing releases
5. For APT package tests on non-Debian systems, you need Docker installed

## Test Sequence

### Phase 1: Local Testing of Individual Components

#### Test 1.1: Local PyPI Build Only

```bash
# Test building the PyPI package locally without publishing
bin/new-release --publish-to=pypi --local --build
```

**Expected outcome**: Package is built in the `dist/` directory but not
published.

#### Test 1.2: Local APT Package Build Only

```bash
# Test building the APT package locally
bin/new-release --publish-to=apt --local --build
```

**Expected outcome**: APT package is generated in the `package-managers/debian/`
directory.

#### Test 1.3: Local Homebrew Formula Build Only

```bash
# Test building the Homebrew formula locally
bin/new-release --publish-to=brew --local --build
```

**Expected outcome**: Homebrew formula is generated in the
`package-managers/brew/Formula/` directory.

### Phase 2: Local Testing of Verification

#### Test 2.1: Local APT Package Verification

```bash
# Test verifying the APT package locally
bin/new-release --publish-to=apt --local --build --verify
```

**Expected outcome**: APT package is built and then verified with tests.

#### Test 2.2: Local Homebrew Formula Verification

```bash
# Test verifying the Homebrew formula locally
bin/new-release --publish-to=brew --local --build --verify
```

**Expected outcome**: Homebrew formula is built and then verified with tests.

### Phase 3: Local Testing of Complete Processes

#### Test 3.1: Complete Local APT Process

```bash
# Test the complete APT package process locally
bin/new-release --publish-to=apt --local
```

**Expected outcome**: APT package is built, verified, and changes are committed
(after confirmation).

#### Test 3.2: Complete Local Homebrew Process

```bash
# Test the complete Homebrew formula process locally
bin/new-release --publish-to=brew --local
```

**Expected outcome**: Homebrew formula is built, verified, and changes are
committed (after confirmation).

#### Test 3.3: Complete Local Process for All Package Managers

```bash
# Test the complete process for all package managers locally
bin/new-release --publish-to=apt,brew --local
```

**Expected outcome**: Both APT package and Homebrew formula are built, verified,
and changes are committed.

### Phase 4: Testing GitHub Workflow Triggers

#### Test 4.1: Trigger APT Workflow

```bash
# Test triggering the APT package workflow
bin/new-release --publish-to=apt
```

**Expected outcome**: GitHub workflow for APT package update is triggered.

#### Test 4.2: Trigger Homebrew Workflow

```bash
# Test triggering the Homebrew formula workflow
bin/new-release --publish-to=brew
```

**Expected outcome**: GitHub workflow for Homebrew formula update is triggered.

#### Test 4.3: Trigger Both Package Manager Workflows

```bash
# Test triggering both package manager workflows
bin/new-release --publish-to=apt,brew
```

**Expected outcome**: GitHub workflows for both APT package and Homebrew formula
updates are triggered.

### Phase 5: Testing PyPI Release Process

**Note**: These tests involve actual publishing to PyPI. Use a test PyPI
instance or ensure you're ready to publish a new version.

#### Test 5.1: Local PyPI Release

```bash
# Test local PyPI release
bin/new-release --publish-to=pypi --local
```

**Expected outcome**: Package is built, published to PyPI, and a GitHub release
is created.

#### Test 5.2: PyPI Release via GitHub Workflow

```bash
# Test PyPI release via GitHub workflow
bin/new-release --publish-to=pypi
```

**Expected outcome**: GitHub workflow for PyPI release is triggered.

### Phase 6: Testing Complete Release Process

#### Test 6.1: Complete Local Release Process

```bash
# Test the complete release process locally
bin/new-release --local
```

**Expected outcome**: Package is published to PyPI, GitHub release is created,
and both APT package and Homebrew formula are updated.

#### Test 6.2: Complete Release Process via GitHub Workflows

```bash
# Test the complete release process via GitHub workflows
bin/new-release
```

**Expected outcome**: All GitHub workflows are triggered in the correct
sequence.

## Additional Test Cases

### Testing Force Updates

```bash
# Test forcing updates even when no changes are detected
bin/new-release --force
```

### Testing with Custom Version

```bash
# Test specifying a custom version
bin/new-release --version=1.2.3
```

### Testing with Release Notes

```bash
# Test providing custom release notes
bin/new-release --release-notes release-notes.md
```

## Troubleshooting

If any test fails:

1. Check the error messages for clues
2. Verify that all required dependencies are installed
3. Ensure you have the necessary permissions
4. Check the logs of any GitHub workflows that were triggered
5. Try running the individual scripts directly to isolate the issue
