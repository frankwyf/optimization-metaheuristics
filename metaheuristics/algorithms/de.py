"""Differential Evolution (DE/rand/1/bin) for bounded minimization problems.

DE is a population-based stochastic direct-search method that uses vector
differences for perturbation (Storn & Price, 1997). The DE/rand/1/bin
variant is implemented here.

差分進化（DE）最適化アルゴリズム。
差分进化（DE）优化器，用于焊接梁问题。

References
----------
Storn, R., & Price, K. (1997). Differential Evolution – A Simple and
Efficient Heuristic for Global Optimization over Continuous Spaces.
Journal of Global Optimization, 11(4), 341-359.
"""
from __future__ import annotations

import numpy as np

from metaheuristics._validation import require_int, require_real
from metaheuristics.algorithms.base import BaseOptimiser, OptimisationResult
from metaheuristics.problems import OptimizationProblem

# Default hyperparameters
_POP: int = 100
_F: float = 0.8  # Differential weight (mutation factor)
_CR: float = 0.9  # Crossover probability
_ITERS: int = 500  # Maximum generations


class DifferentialEvolution(BaseOptimiser):
    """Differential Evolution (DE/rand/1/bin).

    差分進化（DE/rand/1/bin）。
    差分进化（DE/rand/1/bin）。

    Parameters
    ----------
    seed:
        Random seed for reproducibility.
    pop_size:
        Population size (must be >= 4).
    f:
        Differential weight / mutation factor in [0, 2].
    cr:
        Crossover probability in [0, 1].
    """

    def __init__(
        self,
        seed: int | None = None,
        pop_size: int = _POP,
        f: float = _F,
        cr: float = _CR,
        problem: OptimizationProblem | None = None,
    ) -> None:
        super().__init__(problem=problem, seed=seed)
        require_int("pop_size", pop_size, 1)
        require_real("f", f, 0.0, 2.0)
        require_real("cr", cr, 0.0, 1.0)
        self._rng = np.random.default_rng(self.seed)
        self.pop_size = max(pop_size, 4)
        self.f = f
        self.cr = cr

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------
    def _init_population(self) -> np.ndarray:
        """Initialise population uniformly within bounds."""
        pop = np.zeros((self.pop_size, self.problem.dimension))
        for j, (lo, hi) in enumerate(self.problem.bounds):
            pop[:, j] = self._rng.uniform(lo, hi, size=self.pop_size)
        return pop

    def _mutate(self, pop: np.ndarray, target_idx: int) -> np.ndarray:
        """DE/rand/1 mutation: v = x_r1 + F * (x_r2 - x_r3)."""
        indices = list(range(self.pop_size))
        indices.remove(target_idx)
        r1, r2, r3 = self._rng.choice(indices, size=3, replace=False)
        mutant = pop[r1] + self.f * (pop[r2] - pop[r3])
        # Clip to bounds
        for j, (lo, hi) in enumerate(self.problem.bounds):
            mutant[j] = np.clip(mutant[j], lo, hi)
        return mutant

    def _crossover(self, target: np.ndarray, mutant: np.ndarray) -> np.ndarray:
        """Binomial crossover."""
        d = self.problem.dimension
        trial = target.copy()
        j_rand = self._rng.integers(d)
        for j in range(d):
            if self._rng.random() < self.cr or j == j_rand:
                trial[j] = mutant[j]
        return trial

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------
    def run(  # type: ignore[override]
        self,
        max_iterations: int = _ITERS,
        verbose: bool = False,
    ) -> OptimisationResult:
        """Run DE and return the best result found.

        DE を実行して最良の結果を返す。
        运行 DE 并返回找到的最佳结果。

        Parameters
        ----------
        max_iterations:
            Maximum number of generations.
        verbose:
            Print progress to stdout.

        Returns
        -------
        OptimisationResult
        """
        require_int("max_iterations", max_iterations)
        self._start_run()
        pop = self._init_population()
        evaluations = [self._evaluate(pop[i].tolist()) for i in range(self.pop_size)]
        fitness = np.array([evaluation.penalized_value for evaluation in evaluations])

        best_idx = int(np.argmin(fitness))
        best_x = pop[best_idx].copy()
        best_fit = fitness[best_idx]
        best_evaluation = evaluations[best_idx]
        cost_history: list[float] = [float(best_fit)]

        for gen in range(max_iterations):
            for i in range(self.pop_size):
                mutant = self._mutate(pop, i)
                trial = self._crossover(pop[i], mutant)
                trial_evaluation = self._evaluate(trial.tolist())
                trial_fit = trial_evaluation.penalized_value

                # Greedy selection
                if trial_fit <= fitness[i]:
                    pop[i] = trial
                    fitness[i] = trial_fit

                    if trial_fit < best_fit:
                        best_x = trial.copy()
                        best_fit = trial_fit
                        best_evaluation = trial_evaluation

            cost_history.append(float(best_fit))
            if verbose:
                print(f"[DE] gen={gen + 1:4d}  best={best_fit:.5f}")

        return self._make_result(best_x.tolist(), best_evaluation, cost_history)
