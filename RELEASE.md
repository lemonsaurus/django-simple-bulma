# Release Process

This document outlines the release process for django-simple-bulma.

## Overview

Releases are automated through GitHub Actions when a new GitHub release is published. The workflow consists of:

1. **Version Bump**: Automatically updates the version in `pyproject.toml` based on the release tag
2. **Build & Publish**: Builds the package and publishes to PyPI

## Creating a Release

### 1. Tag Format Requirements

Release tags must follow semantic versioning with an optional `v` prefix:

- ✅ `v1.2.3` (recommended)
- ✅ `1.2.3` 
- ✅ `v2.0.0-beta.1`
- ❌ `release-1.2.3`
- ❌ `1.2` (must be full semver)

### 2. Release Procedure

1. **Ensure Clean State**
   - All desired changes are merged to `main`
   - All CI checks are passing
   - Local repository is up to date with `main`

2. **Create GitHub Release**
   - Go to [Releases](https://github.com/lemonsaurus/django-simple-bulma/releases)
   - Click "Create a new release"
   - Enter tag version (e.g., `v1.2.3`)
   - Set target branch to `main`
   - Fill in release title and description
   - Click "Publish release"

3. **Automated Process**
   - GitHub Actions will automatically:
     - Update the version in `pyproject.toml` to match the tag
     - Commit the version bump back to the repository
     - Build the package using UV
     - Publish to PyPI using the configured token

### 3. Version Numbering Guidelines

Follow [Semantic Versioning 2.0.0](https://semver.org/):

- **MAJOR** (`X.0.0`): Breaking changes, incompatible API changes
- **MINOR** (`1.X.0`): New features, backwards compatible
- **PATCH** (`1.2.X`): Bug fixes, backwards compatible

Examples:
- `v0.9.7` → `v0.9.8` (bug fix)
- `v0.9.8` → `v0.10.0` (new features)  
- `v0.10.5` → `v1.0.0` (breaking changes, stable API)

### 4. Pre-release Versions

For testing releases:
- `v1.2.3-alpha.1` (early testing)
- `v1.2.3-beta.1` (feature complete, testing)
- `v1.2.3-rc.1` (release candidate)

Mark pre-releases as "pre-release" in GitHub.

## Troubleshooting

### Release Failed to Publish

1. Check the [Actions tab](https://github.com/lemonsaurus/django-simple-bulma/actions) for error details
2. Common issues:
   - PyPI token expired → Update `PYPI_TOKEN` secret
   - Version already exists on PyPI → Use a different version number
   - Submodule issues → Ensure all submodules are properly configured

### Version Not Updated in Repository

The release workflow should automatically commit version updates back to the repository. If this fails:

1. Check that the GitHub Actions bot has write permissions
2. Verify the workflow has the correct `contents: write` permission
3. Manually update the version and create a new release

## Manual Version Update (Emergency Only)

If automated version bumping fails, you can manually update:

```bash
# Update version in pyproject.toml
uv version 1.2.3

# Commit and push
git add pyproject.toml
git commit -m "🔖 bump version to 1.2.3"
git push origin main

# Then create the GitHub release
```

## Verification

After a successful release:

1. ✅ New version appears on [PyPI](https://pypi.org/project/django-simple-bulma/)
2. ✅ Version in `pyproject.toml` matches the release tag
3. ✅ GitHub release is marked as "Latest release"
4. ✅ Installation works: `pip install django-simple-bulma==X.Y.Z`