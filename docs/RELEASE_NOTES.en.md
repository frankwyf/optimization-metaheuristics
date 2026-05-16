# Release Notes (English)

## Release Scope

This release prepares the repository for public open-source publication.

## Changes

- Cleaned the top-level structure and moved exploratory scripts into `legacy/`.
- Kept the current release baseline in `final/`.
- Added a unified CLI runner at `scripts/run.py`.
- Added lightweight runtime parameters for seed, repeat count, and no-plot mode.
- Added multilingual documentation in Chinese, Japanese, and English.
- Added a minimal GitHub Actions workflow for dependency installation and syntax validation.
- Moved the loose root plot into `docs/assets/` as a documentation asset.
- Rechecked the repository for common sensitive data patterns before release.

## Suggested Commit Message

```text
chore: prepare open-source release with unified CLI, CI, and multilingual docs
```
