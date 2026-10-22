# Open-Source Release Checklist

## Desensitization

- [x] Remove secrets and credentials (API keys, tokens, passwords, private keys).
- [x] Remove local absolute paths and machine-specific identifiers.
- [x] Keep only project-relevant benchmark data and plots.
- [x] Separate exploratory or unstable code from release baseline.

## Structure

- [x] Keep maintained runnable scripts in `final/`.
- [x] Move exploratory scripts to `legacy/`.
- [x] Add multilingual supporting docs in `docs/`.
- [x] Ensure top-level README links to all language docs.

## Reproducibility

- [x] Dependencies declared in `requirements.txt`.
- [x] Entrypoint scripts documented in README.
- [x] Optional: add deterministic fixed-seed mode for all algorithms.
- [x] Optional: add automated syntax and CLI smoke checks in CI.

## Before Tagging a Release

1. Update the single package version, citation, changelog, and versioned release notes.
2. Run `make release-check lint test build` in the repository `.venv` with external caches.
3. Check all four algorithms, seeded replay, optional headless plotting, and installed-wheel imports.
4. Review the entire diff, inspect CI, and obtain maintainer approval under CONTRIBUTING.md.
5. Tag the merged master commit; check version/ancestry gates and the repeated release CI.
6. Verify GitHub release notes, wheel/sdist, and SHA-256 checksums.
7. Verify the separate PyPI Trusted Publisher job and the version on PyPI before claiming it is published.
8. Record actual commands, outcomes, scientific limitations, and storage use.

The historical `final/` examples are preserved for compatibility, but are not the
installable library or the acceptance baseline for new releases.
