"""Standard benchmark functions for metaheuristic algorithm evaluation.

メタヒューリスティクスの標準ベンチマーク関数。
用于元启发式算法评估的标准基准函数。

This module provides a library of well-known test functions so users can
evaluate and compare algorithms beyond the welded-beam problem.
"""
from __future__ import annotations

import math
from dataclasses import dataclass

import numpy as np


@dataclass(frozen=True)
class BenchmarkFunction:
    """Description of a benchmark optimisation problem.

    ベンチマーク最適化問題の定義。
    基准优化问题定义。

    Attributes
    ----------
    name:
        Human-readable function name.
    func:
        Callable(x) → float where x is a list or array.
    bounds:
        Per-dimension (lower, upper) bounds.
    global_minimum:
        Known global minimum value.
    optimal_x:
        One known global minimizer (may not be unique).
    """

    name: str
    bounds: list[tuple[float, float]]
    global_minimum: float
    optimal_x: list[float]

    def __call__(self, x: list[float] | np.ndarray) -> float:
        """Evaluate the benchmark function at point x."""
        raise NotImplementedError("Subclasses must provide evaluation")


# ---------------------------------------------------------------------------
# Benchmark function implementations
# ---------------------------------------------------------------------------

def sphere(x: list[float] | np.ndarray) -> float:
    """Sphere function: f(x) = Σ xi².  Global min: f(0,...,0) = 0.

    球面関数。球面函数。
    """
    return float(np.sum(np.asarray(x) ** 2))


def rastrigin(x: list[float] | np.ndarray) -> float:
    """Rastrigin function. Global min: f(0,...,0) = 0.

    ラストリギン関数。Rastrigin 函数。
    """
    arr = np.asarray(x)
    n = len(arr)
    return float(10 * n + np.sum(arr**2 - 10 * np.cos(2 * math.pi * arr)))


def ackley(x: list[float] | np.ndarray) -> float:
    """Ackley function (2D default). Global min: f(0,...,0) = 0.

    アクリー関数。Ackley 函数。
    """
    arr = np.asarray(x, dtype=float)
    n = len(arr)
    sum_sq = np.sum(arr**2)
    sum_cos = np.sum(np.cos(2 * math.pi * arr))
    return float(
        -20 * np.exp(-0.2 * np.sqrt(sum_sq / n))
        - np.exp(sum_cos / n)
        + 20
        + math.e
    )


def rosenbrock(x: list[float] | np.ndarray) -> float:
    """Rosenbrock function. Global min: f(1,...,1) = 0.

    ローゼンブロック関数。Rosenbrock 函数。
    """
    arr = np.asarray(x, dtype=float)
    return float(np.sum(100 * (arr[1:] - arr[:-1] ** 2) ** 2 + (1 - arr[:-1]) ** 2))


def griewank(x: list[float] | np.ndarray) -> float:
    """Griewank function. Global min: f(0,...,0) = 0.

    グリエワンク関数。Griewank 函数。
    """
    arr = np.asarray(x, dtype=float)
    sum_part = np.sum(arr**2) / 4000
    indices = np.arange(1, len(arr) + 1)
    prod_part = np.prod(np.cos(arr / np.sqrt(indices)))
    return float(sum_part - prod_part + 1)


def schwefel(x: list[float] | np.ndarray) -> float:
    """Schwefel function. Global min: f(420.9687,...) ≈ 0.

    シュヴェーフェル関数。Schwefel 函数。
    """
    arr = np.asarray(x, dtype=float)
    n = len(arr)
    return float(418.9829 * n - np.sum(arr * np.sin(np.sqrt(np.abs(arr)))))


# ---------------------------------------------------------------------------
# Registry of pre-configured benchmark problems
# ---------------------------------------------------------------------------

BENCHMARKS: dict[str, dict] = {
    "sphere_2d": {
        "name": "Sphere (2D)",
        "func": sphere,
        "bounds": [(-5.12, 5.12)] * 2,
        "global_minimum": 0.0,
        "optimal_x": [0.0, 0.0],
    },
    "sphere_10d": {
        "name": "Sphere (10D)",
        "func": sphere,
        "bounds": [(-5.12, 5.12)] * 10,
        "global_minimum": 0.0,
        "optimal_x": [0.0] * 10,
    },
    "rastrigin_2d": {
        "name": "Rastrigin (2D)",
        "func": rastrigin,
        "bounds": [(-5.12, 5.12)] * 2,
        "global_minimum": 0.0,
        "optimal_x": [0.0, 0.0],
    },
    "rastrigin_10d": {
        "name": "Rastrigin (10D)",
        "func": rastrigin,
        "bounds": [(-5.12, 5.12)] * 10,
        "global_minimum": 0.0,
        "optimal_x": [0.0] * 10,
    },
    "ackley_2d": {
        "name": "Ackley (2D)",
        "func": ackley,
        "bounds": [(-5.0, 5.0)] * 2,
        "global_minimum": 0.0,
        "optimal_x": [0.0, 0.0],
    },
    "rosenbrock_2d": {
        "name": "Rosenbrock (2D)",
        "func": rosenbrock,
        "bounds": [(-5.0, 10.0)] * 2,
        "global_minimum": 0.0,
        "optimal_x": [1.0, 1.0],
    },
    "griewank_10d": {
        "name": "Griewank (10D)",
        "func": griewank,
        "bounds": [(-600.0, 600.0)] * 10,
        "global_minimum": 0.0,
        "optimal_x": [0.0] * 10,
    },
    "schwefel_2d": {
        "name": "Schwefel (2D)",
        "func": schwefel,
        "bounds": [(-500.0, 500.0)] * 2,
        "global_minimum": 0.0,
        "optimal_x": [420.9687, 420.9687],
    },
}
