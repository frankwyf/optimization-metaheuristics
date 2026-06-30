"""
optimization-metaheuristics
===========================
Metaheuristic optimization algorithms (GA, PSO, SA, DE) benchmarked on the
welded-beam engineering design problem.

Quick start
-----------
>>> from metaheuristics.problem import objective, is_feasible
>>> from metaheuristics.algorithms.sa import SimulatedAnnealing
>>> sa = SimulatedAnnealing(seed=42)
>>> result = sa.run(samples_per_temperature=500)
>>> print(result.best_cost)
"""
from __future__ import annotations

__version__ = "1.2.0"
__author__ = "frankwyf"
__license__ = "MIT"

from metaheuristics import benchmarks, problem  # noqa: F401

__all__ = ["benchmarks", "problem", "__version__"]
