# Developer Guide · 开发指南 · 開発者ガイド

## Setup / 环境搭建 / セットアップ

```bash
git clone https://github.com/frankwyf/optimization-metaheuristics.git
cd optimization-metaheuristics
python -m venv .venv
source .venv/bin/activate   # Linux/macOS
# .venv\Scripts\activate    # Windows
pip install -e ".[dev]"
pre-commit install
```

## Common Tasks / 常用命令 / よく使うコマンド

| Task | Command |
|------|---------|
| Run tests | `make test` or `pytest tests/ -v --cov=metaheuristics` |
| Lint | `make lint` or `ruff check metaheuristics/ scripts/ tests/ examples/` |
| Format | `make format` |
| Run all algorithms | `make run-all` |
| Clean artifacts | `make clean` |
| Build wheel | `python -m build` |

On Windows, run the underlying Python and Ruff commands directly if GNU Make is not installed.

## Architecture / 架构 / アーキテクチャ

```
metaheuristics/
├── problem.py       ← Problem definition (objective + constraints)
├── benchmarks.py    ← Standard test functions (Sphere, Rastrigin, etc.)
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
2. Subclass `BaseOptimiser` and implement `run() -> OptimisationResult`
3. Register in `metaheuristics/algorithms/__init__.py`
4. Add to `ALGORITHMS` dict in `scripts/run.py`
5. Write tests in `tests/test_your_algo.py`
6. Run `make lint test` to verify

## Release Process / 发布流程 / リリースプロセス

```bash
# Bump version in pyproject.toml + metaheuristics/__init__.py
# Update CHANGELOG.md
git tag v1.x.0
git push origin v1.x.0  # triggers release workflow → GitHub Release + PyPI
```
