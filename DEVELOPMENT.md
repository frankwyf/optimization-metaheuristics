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
# Bump version in pyproject.toml + metaheuristics/__init__.py
# Update CHANGELOG.md
git tag v1.x.0
git push origin v1.x.0  # triggers release workflow → GitHub Release + PyPI
```
