# Changelog · 变更日志 · 変更履歴

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [1.2.0] — 2026-06-30

### Added
- **Differential Evolution (DE)** algorithm — `metaheuristics/algorithms/de.py`
  implementing DE/rand/1/bin variant (Storn & Price 1997)
- **Benchmarks module** — `metaheuristics/benchmarks.py` with standard test
  functions: Sphere, Rastrigin, Ackley, Rosenbrock, Griewank, Schwefel
- **Rewritten CLI** — `scripts/run.py` now uses the package directly with
  tabulated results, multi-run statistics, and `--quick` mode
- Tests for DE (13 tests), benchmarks (17 tests), and CLI (11 tests) — total 97
- Release workflow (`.github/workflows/release.yml`) with PyPI publish
- `KNOWN_OPTIMUM_X` vector added to `problem.py`

### Changed
- CI lint target now includes `tests/` directory
- CLI smoke tests use `--quick` flag instead of algorithm-specific args
- Version bumped to 1.2.0

---

## [1.1.0] — 2026-06-30

### Added
- `metaheuristics/` proper Python package with:
  - `problem.py` — canonical single-source welded-beam problem definition with
    `objective`, `is_feasible`, `constraint_violations`, and `penalized_objective`
  - `algorithms/ga.py` — refactored GA with type hints, elitism, and
    ACO-assisted diversification
  - `algorithms/pso.py` — refactored PSO with corrected velocity-bounds indexing
    (bug fix: was using particle index *i* instead of dimension index *j*)
  - `algorithms/sa.py` — refactored SA with fixed `adjust` logic and adaptive
    reheating
  - `algorithms/base.py` — `BaseOptimiser` abstract class and `OptimisationResult`
    dataclass
  - `utils/visualization.py` — convergence-curve and box-plot helpers
- `tests/` test suite (56 tests) covering `problem.py`, GA, PSO, and SA
- `pyproject.toml` — modern build system metadata, ruff config, pytest config
- `CONTRIBUTING.md` — trilingual (EN / ZH / JA) contribution guide
- `CODE_OF_CONDUCT.md` — trilingual Contributor Covenant
- `SECURITY.md` — trilingual vulnerability-disclosure policy
- `CITATION.cff` — machine-readable citation metadata
- `.github/workflows/ci.yml` — 3-job CI: tests (3×Python), ruff lint, CLI smoke
- `.github/ISSUE_TEMPLATE/bug_report.md` — structured bug-report template
- `.github/ISSUE_TEMPLATE/feature_request.md` — feature-request template
- `.github/PULL_REQUEST_TEMPLATE.md` — PR checklist
- `requirements.txt` updated to include `seaborn>=0.12`

### Changed
- Updated `scripts/run.py` help text and forward compatibility notes
- Removed hardcoded Chinese-only font fallbacks from `final/` scripts (kept for
  backward compatibility but now optional via matplotlib's default font)

### Fixed
- PSO `m2()`: velocity-bounds check used particle index `i` instead of dimension
  index `j` (original `final/PSO.py` bug preserved for backward compat; fixed in
  `metaheuristics/algorithms/pso.py`)
- SA `adjust()`: returned list of penalised scalars instead of a valid design
  vector (original `final/SA.py` bug preserved for backward compat; fixed in
  `metaheuristics/algorithms/sa.py`)
- `general.py` `constraint6` sign convention inconsistency (documented in
  `metaheuristics/problem.py` docstring)

---

## [1.0.0] — 2025-12-01

### Added
- Initial open-source release
- `final/GA.py`, `final/PSO.py`, `final/SA.py` — clean standalone algorithm scripts
- `scripts/run.py` — unified CLI entry point
- `general.py` — shared objective and constraint definitions
- `legacy/` — archived exploratory scripts
- `docs/` — multilingual documentation (EN / ZH / JA)
- `.github/workflows/ci.yml` — minimal syntax-validation CI
- MIT License
