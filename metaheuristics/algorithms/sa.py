"""Simulated Annealing (SA) optimizer for bounded minimization problems.

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

from metaheuristics._validation import require_int, require_real
from metaheuristics.algorithms.base import BaseOptimiser, OptimisationResult
from metaheuristics.problems import OptimizationProblem

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
        problem: OptimizationProblem | None = None,
    ) -> None:
        super().__init__(problem=problem, seed=seed)
        require_real("t_max", t_max)
        require_real("t_min", t_min)
        require_real("cooling", cooling, 0.0, 1.0)
        if not 0.0 < t_min < t_max:
            raise ValueError("t_max must be greater than t_min > 0")
        if not 0.0 < cooling < 1.0:
            raise ValueError("cooling must be strictly between 0 and 1")
        self._rng = np.random.default_rng(self.seed)
        self.t_max = t_max
        self.t_min = t_min
        self.cooling = cooling

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------
    def _random_point(self) -> list[float]:
        """Sample a uniformly random design vector within bounds."""
        return [float(self._rng.uniform(lo, hi)) for lo, hi in self.problem.bounds]

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
        require_int("samples_per_temperature", samples_per_temperature, 1)
        self._start_run()
        xs = self._random_point()
        current_evaluation = self._evaluate(xs)
        best_evaluation = current_evaluation
        best_cost = best_evaluation.penalized_value
        best_x = xs[:]

        t = self.t_max
        cost_history: list[float] = [best_cost]

        while t > self.t_min:
            for _ in range(samples_per_temperature):
                candidate = self._neighbour()
                candidate_evaluation = self._evaluate(candidate)
                current_cost = candidate_evaluation.penalized_value
                delta = current_evaluation.penalized_value - current_cost

                if delta >= 0:
                    # Better or equal — always accept
                    current_evaluation = candidate_evaluation
                else:
                    # Worse — accept with Boltzmann probability
                    if math.exp(delta / t) > self._rng.random():
                        current_evaluation = candidate_evaluation
                if current_cost < best_cost:
                    best_cost = current_cost
                    best_x = candidate[:]
                    best_evaluation = candidate_evaluation

            next_t = t * self.cooling
            if next_t >= t:
                raise ValueError("cooling does not decrease temperature at floating-point precision")
            t = next_t
            cost_history.append(best_cost)

            if verbose:
                print(f"[SA] T={t:.4f}  best={best_cost:.5f}")

        return self._make_result(best_x, best_evaluation, cost_history)
