# Developer Guide · 开发指南 · 開発者ガイド

## Setup / 环境搭建 / セットアップ

```bash
# Put the repository on the external SSD before creating its environment.
python3.12 -m venv .venv
source .venv/bin/activate

# Keep package caches, tool runtimes, and temporary files beside the repository
# on the same external volume. Run these exports in the shell that installs.
DEV_STORAGE="$(cd .. && pwd -P)/.codex-dev-storage"
mkdir -p "$DEV_STORAGE"/{uv-cache,uv-python,uv-python-bin,uv-tools,uv-tool-bin,pip-cache,xdg-cache,xdg-data,tmp,matplotlib}
export UV_CACHE_DIR="$DEV_STORAGE/uv-cache"
export UV_PYTHON_INSTALL_DIR="$DEV_STORAGE/uv-python"
export UV_PYTHON_BIN_DIR="$DEV_STORAGE/uv-python-bin"
export UV_TOOL_DIR="$DEV_STORAGE/uv-tools"
export UV_TOOL_BIN_DIR="$DEV_STORAGE/uv-tool-bin"
export PIP_CACHE_DIR="$DEV_STORAGE/pip-cache"
export XDG_CACHE_HOME="$DEV_STORAGE/xdg-cache"
export XDG_DATA_HOME="$DEV_STORAGE/xdg-data"
export TMPDIR="$DEV_STORAGE/tmp"
export MPLCONFIGDIR="$DEV_STORAGE/matplotlib"

python -m pip install -e ".[dev,plot]"
```

For Windows PowerShell, create the repository-local environment with `py -3.12 -m venv .venv`, activate `.venv\Scripts\Activate.ps1`, then install `.[dev,plot]`. On macOS, verify the repository and shared storage mount with `pwd -P`, `diskutil info`, and `df -h` before installing. If using uv to install Python, its install and cache paths above keep that runtime on the external volume. Set `MPLBACKEND=Agg` for headless or CI runs.

## Common Tasks / 常用命令 / よく使うコマンド

| Task | macOS/Linux command |
|------|---------|
| Run tests | `make test` or `python -m pytest tests/ -v --cov=metaheuristics` |
| Lint | `make lint` or `python -m ruff check metaheuristics/ scripts/ tests/ examples/` |
| Format | `make format` |
| Run all algorithms | `make run-all` |
| Clean artifacts | `make clean` |
| Build wheel | `python -m build` (install `build` in `.venv` first) |

On Windows, run the Python and Ruff commands from the activated `.venv` if GNU Make is not installed.

## Architecture / 架构 / アーキテクチャ

```
metaheuristics/
├── problem.py       ← Canonical welded-beam objective + constraints
├── problems.py      ← Generic bounded problem and evaluation interface
├── benchmarks.py    ← Standard functions and problem adapters
├── algorithms/
│   ├── base.py      ← BaseOptimiser ABC + OptimisationResult
│   ├── ga.py        ← Genetic Algorithm
│   ├── pso.py       ← Particle Swarm Optimization
│   ├── sa.py        ← Simulated Annealing
│   └── de.py        ← Differential Evolution
└── utils/
    └── visualization.py  ← Plotting helpers
```

### Adding a New Algorithm / 添加新算法 / 新しいアルゴリズムの追加

1. Create `metaheuristics/algorithms/your_algo.py`
2. Subclass `BaseOptimiser`, accept `problem` and `seed`, and implement `run()`
3. Register in `metaheuristics/algorithms/__init__.py`
4. Add to `ALGORITHMS` dict in `scripts/run.py`
5. Write tests in `tests/test_your_algo.py`, including a small custom problem
6. Run `make lint test` to verify

## Release Process / 发布流程 / リリースプロセス

```bash
# Change the sole version in metaheuristics/__init__.py; update CITATION.cff,
# CHANGELOG.md, and docs/releases/<version>.md in a reviewed PR.
make release-check lint test build
# Merge only after CI and the maintainer review required by CONTRIBUTING.md.
# Tag the merged master commit; never tag an unmerged feature branch.
git tag -a v1.x.0 <merged-commit> -m "Release 1.x.0"
git push origin v1.x.0
```

The tag workflow validates version and master ancestry, repeats the entire CI
suite, builds from the source archive, checks metadata with Twine, and runs the
installed wheel with isolated imports. The GitHub Release contains versioned
notes, the wheel, sdist, and SHA-256 manifest. Inspect every release job before
announcing publication. GitHub publication and PyPI publication are separate outcomes.

For PyPI, configure a Trusted Publisher (or pending publisher for the first upload)
with owner `frankwyf`, repository `optimization-metaheuristics`, workflow
`release.yml`, and environment `pypi`. OIDC grants `id-token: write` only to the
publishing job. No long-lived upload token is needed. Setup follows the
[PyPI Trusted Publishing guide](https://docs.pypi.org/trusted-publishers/using-a-publisher/).
Account login/2FA or environment approval must be completed by an authorized owner.
Do not suppress an upload failure with `skip-existing` or move a published tag.
After fixing an upload-only issue, re-run the failed publishing job; a code change
requires a new patch version and tag.

`workflow_dispatch` is available for recovery, but must be run against an existing
version tag; branch dispatches fail validation. A prior GitHub Release must not be
overwritten by re-running all jobs.

## Numerical review and compatibility

See [API.md](docs/API.md), [EXPERIMENTS.md](docs/EXPERIMENTS.md), and
[ROADMAP.md](ROADMAP.md). Python 3.10–3.14, NumPy 1.24 on Python 3.10, latest
compatible NumPy, macOS and Windows are exercised by CI. Local verification should
report the actual tested interpreter; a matrix definition is not a passing result.
The legacy `final/` and `legacy/` scripts are historical compatibility examples;
new code and published installs use the package and unified CLI.
