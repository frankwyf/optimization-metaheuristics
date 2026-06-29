"""Simulated Annealing (SA) optimiser for the welded-beam problem.

Simulated Annealing is a probabilistic technique that escapes local optima by
accepting worse solutions with a temperature-dependent probability that
decreases over time (Kirkpatrick et al., 1983).

シミュレーテッド・アニーリング（SA）最適化アルゴリズム。
模拟退火（SA）优化器，用于焊接梁问题。

References
----------
Kirkpatrick, S., Gelatt, C. D., & Vecchi, M. P. (1983). Optimization by
simulated annealing. Science, 220(4598), 671-680.
"""
from __future__ import annotations

import math

import numpy as np

from metaheuristics.algorithms.base import BaseOptimiser, OptimisationResult
from metaheuristics.problem import BOUNDS, is_feasible, objective, penalized_objective

# Default hyperparameters
_T_MAX: float = 20.0   # Initial temperature
_T_MIN: float = 0.01   # Stopping temperature
_COOLING: float = 0.5  # Geometric cooling ratio  T ← T × R
_SAMPLES: int = 20_000  # Candidate evaluations per temperature level


class SimulatedAnnealing(BaseOptimiser):
    """Simulated Annealing optimiser.

    シミュレーテッド・アニーリング最適化アルゴリズム。
    模拟退火优化器。

    Parameters
    ----------
    seed:
        NumPy random seed for reproducibility.
    t_max:
        Starting temperature.
    t_min:
        Stopping temperature.
    cooling:
        Multiplicative cooling coefficient (0 < cooling < 1).
    """

    def __init__(
        self,
        seed: int | None = None,
        t_max: float = _T_MAX,
        t_min: float = _T_MIN,
        cooling: float = _COOLING,
    ) -> None:
        self._rng = np.random.default_rng(seed)
        self.t_max = t_max
        self.t_min = t_min
        self.cooling = cooling

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------
    def _random_point(self) -> list[float]:
        """Sample a uniformly random design vector within bounds."""
        return [float(self._rng.uniform(lo, hi)) for lo, hi in BOUNDS]

    def _neighbour(self) -> list[float]:
        """Generate a random candidate (uniform restart within bounds)."""
        return self._random_point()

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------
    def run(  # type: ignore[override]
        self,
        samples_per_temperature: int = _SAMPLES,
        verbose: bool = False,
    ) -> OptimisationResult:
        """Run the SA and return the best result found.

        SA を実行して最良の結果を返す。
        运行 SA 并返回找到的最佳结果。

        Parameters
        ----------
        samples_per_temperature:
            Number of candidate solutions evaluated at each temperature.
        verbose:
            Print progress to stdout.

        Returns
        -------
        OptimisationResult
        """
        xs = self._random_point()
        best_cost = penalized_objective(xs)
        best_x = xs[:]

        t = self.t_max
        cost_history: list[float] = []
        count = 0

        while t > self.t_min:
            count += 1
            for _ in range(samples_per_temperature):
                candidate = self._neighbour()
                current_cost = penalized_objective(candidate)
                delta = best_cost - current_cost

                if delta >= 0:
                    # Better or equal — always accept
                    best_cost = current_cost
                    best_x = candidate[:]
                else:
                    # Worse — accept with Boltzmann probability
                    if math.exp(delta / t) > self._rng.random():
                        best_cost = current_cost
                        best_x = candidate[:]

            t *= self.cooling
            cost_history.append(objective(best_x) if is_feasible(best_x) else best_cost)

            if verbose:
                print(f"[SA] T={t:.4f}  best={best_cost:.5f}")

        feasible = is_feasible(best_x)
        return OptimisationResult(
            best_x=best_x,
            best_cost=objective(best_x) if feasible else best_cost,
            cost_history=cost_history,
            is_feasible=feasible,
        )
