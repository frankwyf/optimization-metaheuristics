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

1. Run each script in `final/` at least once in a clean environment.
2. Verify figures, stats, and console outputs are expected.
3. Confirm no generated local artifacts are unintentionally tracked.
4. Re-check license and README links.
