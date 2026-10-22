# optimization-metaheuristics

[![CI](https://github.com/frankwyf/optimization-metaheuristics/actions/workflows/ci.yml/badge.svg)](https://github.com/frankwyf/optimization-metaheuristics/actions/workflows/ci.yml)
[![Python](https://img.shields.io/badge/python-3.10%20|%203.11%20|%203.12-blue)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

Metaheuristic optimization algorithms (GA · PSO · SA · DE) benchmarked on the
**welded-beam constrained engineering design problem** (Deb 1991).

**1.3.0:** reusable bounded problems, explicit multi-seed experiments, optional
plots, and verified distribution builds. Research/education beta.
[API reference](docs/API.md) · [Experiment and replay guide](docs/EXPERIMENTS.md) ·
[Release notes](docs/releases/1.3.0.md) · [Roadmap](ROADMAP.md)

中文：本版本补齐可重放实验、最佳解语义、参数校验及发行包验证；项目仍处于研究用途的 Beta 阶段。
日本語：再現可能な実験、最良解の保持、入力検証、配布物の検証を整備した研究用ベータ版です。

---

**[English](#english) · [中文](#中文) · [日本語](#日本語)**

---

## English

### Overview

This repository provides four testable metaheuristic algorithms. They run on
the welded-beam engineering benchmark by default and accept reusable bounded
optimization problems, including the standard functions in `benchmarks.py`:

| Algorithm | Module | Description |
|-----------|--------|-------------|
| Genetic Algorithm | `metaheuristics/algorithms/ga.py` | Binary-encoded, rank-selection, ACO-assisted restart |
| Particle Swarm Optimization | `metaheuristics/algorithms/pso.py` | Standard PSO with inertia weight and velocity clamping |
| Simulated Annealing | `metaheuristics/algorithms/sa.py` | Geometric cooling schedule |
| Differential Evolution | `metaheuristics/algorithms/de.py` | DE/rand/1/bin variant (Storn & Price 1997) |

A **benchmarks module** (`metaheuristics/benchmarks.py`) provides Sphere,
Rastrigin, Ackley, Rosenbrock, Griewank, and Schwefel problems for comparison.
The CLI can save run records and summaries as JSON and CSV when `--output-dir`
is specified. Core installation requires NumPy; install `.[plot]` for figures.

### Benchmark Problem

The **welded beam design** minimises fabrication cost subject to 7 engineering
constraints (shear stress, deflection, buckling load, bending stress, geometry).

Design variables:
- `x[0]` — weld height *h* ∈ [0.1, 2.0] in
- `x[1]` — weld length *l* ∈ [0.1, 10.0] in
- `x[2]` — bar height *t* ∈ [0.1, 10.0] in
- `x[3]` — bar thickness *b* ∈ [0.1, 2.0] in

Known near-optimal cost: **≈ 1.7248** (Deb 1991)

### Quick Start

```bash
git clone https://github.com/frankwyf/optimization-metaheuristics.git
cd optimization-metaheuristics
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

On Windows, use `python -m venv .venv` and activate `.venv\Scripts\activate` before installing dependencies.

**Run via the unified CLI:**
```bash
python scripts/run.py sa  --seed 42 --runs 3 --no-plot --quick
python scripts/run.py pso --seed 42 --runs 3 --no-plot --quick
python scripts/run.py ga  --seed 42 --runs 3 --no-plot --quick
python scripts/run.py de  --seed 42 --runs 3 --no-plot --quick
python scripts/run.py --list   # list all supported algorithms
python scripts/run.py de --problem sphere_2d --seed 42 --runs 20 --no-plot \
  --pop-size 40 --iterations 500 --output-dir ./results
```

**Use the package directly:**
```python
from metaheuristics.algorithms.sa import SimulatedAnnealing
from metaheuristics.problem import objective, is_feasible

sa = SimulatedAnnealing(seed=42)
result = sa.run(samples_per_temperature=20_000)
print(f"cost={result.best_cost:.5f}  feasible={result.is_feasible}")
print(f"x = {result.best_x}")
```

**Define a custom problem:**
```python
from metaheuristics.algorithms import DifferentialEvolution
from metaheuristics.problems import OptimizationProblem

problem = OptimizationProblem(
    name="my-sphere",
    bounds=((-5.0, 5.0),) * 3,
    objective=lambda x: sum(value**2 for value in x),
    known_optimum=0.0,
    known_optimum_x=(0.0, 0.0, 0.0),
)
result = DifferentialEvolution(problem=problem, seed=42, pop_size=40).run(max_iterations=100)
print(result.objective_value, result.is_feasible, result.n_evaluations)
```

`objective_value` always reports the raw objective. `penalized_cost` reports the
search value including constraint penalties; `best_cost` retains its legacy
meaning for compatibility. Result files record seeds, algorithm settings,
problem bounds, evaluation counts, runtime, and available library versions.

### Repository Layout

```
optimization-metaheuristics/
├── metaheuristics/          # Main installable package
│   ├── problem.py           # Welded-beam problem (canonical)
│   ├── problems.py          # Generic bounded problem interface
│   ├── benchmarks.py        # Standard test functions (Sphere, Rastrigin, etc.)
│   ├── algorithms/
│   │   ├── base.py          # BaseOptimiser + OptimisationResult
│   │   ├── ga.py            # Genetic Algorithm
│   │   ├── pso.py           # Particle Swarm Optimization
│   │   ├── sa.py            # Simulated Annealing
│   │   └── de.py            # Differential Evolution
│   └── utils/
│       └── visualization.py # Convergence-curve & box-plot helpers
├── tests/                   # pytest test suite
├── scripts/run.py           # Unified CLI entry point
├── final/                   # Standalone scripts (backward compat)
├── legacy/                  # Archived exploratory code
└── docs/                    # Multilingual documentation
```

### Testing

```bash
python -m pip install -e ".[dev]"
python -m pytest tests/ -v --cov=metaheuristics
```

### Documentation

| Language | File |
|----------|------|
| English | [docs/README.en.md](docs/README.en.md) |
| 中文 | [docs/README.zh-CN.md](docs/README.zh-CN.md) |
| 日本語 | [docs/README.ja.md](docs/README.ja.md) |

### Citation

If you use this repository in academic work, please cite:

```bibtex
@software{frankwyf_metaheuristics_2026,
  title   = {optimization-metaheuristics},
  author  = {frankwyf},
  year    = {2026},
  url     = {https://github.com/frankwyf/optimization-metaheuristics},
  license = {MIT}
}
```

See [CITATION.cff](CITATION.cff) for full metadata.

### License

[MIT](LICENSE) · [Developer Guide](DEVELOPMENT.md) · [Contributing](CONTRIBUTING.md) · [Code of Conduct](CODE_OF_CONDUCT.md) · [Security](SECURITY.md)

---

## 中文

### 概述

本仓库提供四种经典元启发式算法的简洁、可测试 Python 实现，
应用于焊接梁约束工程设计基准问题（Deb 1991）：

| 算法 | 模块 | 说明 |
|------|------|------|
| 遗传算法 | `metaheuristics/algorithms/ga.py` | 二进制编码、排名选择、ACO 辅助重启 |
| 粒子群优化 | `metaheuristics/algorithms/pso.py` | 标准 PSO，惯性权重和速度钳制 |
| 模拟退火 | `metaheuristics/algorithms/sa.py` | 几何降温 |
| 差分进化 | `metaheuristics/algorithms/de.py` | DE/rand/1/bin 变体 (Storn & Price 1997) |

### 快速开始

```bash
git clone https://github.com/frankwyf/optimization-metaheuristics.git
cd optimization-metaheuristics
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

Windows PowerShell 用户可运行 `python -m venv .venv` 创建环境，再运行 `.venv\Scripts\Activate.ps1` 激活。

**使用统一命令行界面：**
```bash
python scripts/run.py sa --seed 42 --runs 3 --no-plot --quick
python scripts/run.py pso --seed 42 --runs 3 --no-plot --quick
python scripts/run.py ga --seed 42 --runs 3 --no-plot --quick
python scripts/run.py de --seed 42 --runs 3 --no-plot --quick
python scripts/run.py de --problem sphere_2d --seed 42 --runs 20 --no-plot \
  --pop-size 40 --iterations 500 --output-dir ./results
```

`--output-dir` 会保存 JSON/CSV 逐次运行记录与汇总数据。核心安装只需 NumPy；
需要图表时安装 `pip install -e ".[plot]"`。

**直接使用包：**
```python
from metaheuristics.algorithms.sa import SimulatedAnnealing

sa = SimulatedAnnealing(seed=42)
result = sa.run(samples_per_temperature=20_000)
print(f"cost={result.best_cost:.5f}  可行={result.is_feasible}")
```

**自定义目标函数：**
```python
from metaheuristics.algorithms import DifferentialEvolution
from metaheuristics.problems import OptimizationProblem

problem = OptimizationProblem(
    name="my-sphere",
    bounds=((-5.0, 5.0),) * 3,
    objective=lambda x: sum(value**2 for value in x),
    known_optimum=0.0,
    known_optimum_x=(0.0, 0.0, 0.0),
)
result = DifferentialEvolution(problem=problem, seed=42, pop_size=40).run(max_iterations=100)
print(result.objective_value, result.is_feasible, result.n_evaluations)
```

### 许可证

[MIT](LICENSE) · [开发指南](DEVELOPMENT.md) · [贡献指南](CONTRIBUTING.md) · [行为准则](CODE_OF_CONDUCT.md) · [安全政策](SECURITY.md)

---

## 日本語

### 概要

本リポジトリは、溶接ビーム制約工学設計ベンチマーク問題（Deb 1991）に
適用された 4 つの古典的メタヒューリスティックアルゴリズムの
クリーンでテスト可能な Python 実装を提供します：

| アルゴリズム | モジュール | 説明 |
|---|---|---|
| 遺伝的アルゴリズム | `metaheuristics/algorithms/ga.py` | バイナリエンコード・ランク選択・ACO 補助再起動 |
| 粒子群最適化 | `metaheuristics/algorithms/pso.py` | 慣性重みと速度クランピングを持つ標準 PSO |
| シミュレーテッド・アニーリング | `metaheuristics/algorithms/sa.py` | 幾何学的冷却 |
| 差分進化 | `metaheuristics/algorithms/de.py` | DE/rand/1/bin 変種 (Storn & Price 1997) |

### クイックスタート

```bash
git clone https://github.com/frankwyf/optimization-metaheuristics.git
cd optimization-metaheuristics
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

Windows PowerShell では `python -m venv .venv` で環境を作成し、`.venv\Scripts\Activate.ps1` で有効化してください。

**統合 CLI の使用：**
```bash
python scripts/run.py sa --seed 42 --runs 3 --no-plot --quick
python scripts/run.py pso --seed 42 --runs 3 --no-plot --quick
python scripts/run.py ga --seed 42 --runs 3 --no-plot --quick
python scripts/run.py de --seed 42 --runs 3 --no-plot --quick
```

**パッケージの直接使用：**
```python
from metaheuristics.algorithms.sa import SimulatedAnnealing

sa = SimulatedAnnealing(seed=42)
result = sa.run(samples_per_temperature=20_000)
print(f"cost={result.best_cost:.5f}  実行可能={result.is_feasible}")
```

### ライセンス

[MIT](LICENSE) · [開発者ガイド](DEVELOPMENT.md) · [コントリビューションガイド](CONTRIBUTING.md) · [行動規範](CODE_OF_CONDUCT.md) · [セキュリティポリシー](SECURITY.md)

