"""
optimization-metaheuristics
===========================
Reusable metaheuristic optimization algorithms (GA, PSO, SA, DE) with a
welded-beam default and standard continuous optimization benchmarks.

Quick start
-----------
>>> from metaheuristics.problem import objective, is_feasible
>>> from metaheuristics.algorithms.sa import SimulatedAnnealing
>>> sa = SimulatedAnnealing(seed=42)
>>> result = sa.run(samples_per_temperature=500)
>>> print(result.best_cost)
"""
from __future__ import annotations

__version__ = "1.3.0"
__author__ = "frankwyf"
__license__ = "MIT"

from metaheuristics import benchmarks, problem  # noqa: F401
from metaheuristics.problems import OptimizationProblem

__all__ = ["OptimizationProblem", "benchmarks", "problem", "__version__"]
