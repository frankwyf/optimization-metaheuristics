"""Particle Swarm Optimisation (PSO) for the welded-beam problem.

PSO simulates the social behaviour of a swarm (Kennedy & Eberhart, 1995).
Each particle remembers its personal best position and is attracted toward
the global best position discovered by the swarm.

粒子群最適化（PSO）。
粒子群优化（PSO）。

References
----------
Kennedy, J., & Eberhart, R. (1995). Particle swarm optimization.
Proceedings of ICNN'95, vol. 4, pp. 1942-1948.
"""
from __future__ import annotations

import random as _random

import numpy as np

from metaheuristics.algorithms.base import BaseOptimiser, OptimisationResult
from metaheuristics.problem import BOUNDS, is_feasible, objective, penalized_objective

# Default hyperparameters
_POP: int = 500
_W: float = 0.5    # Inertia weight
_C1: float = 1.5   # Cognitive (personal-best) coefficient
_C2: float = 1.5   # Social (global-best) coefficient
_ITERS: int = 100  # Number of velocity-update iterations

# Per-dimension velocity clamp: ±20 % of the range
_V_CLAMP = [(-(hi - lo) * 0.2, (hi - lo) * 0.2) for lo, hi in BOUNDS]


def _random_feasible_particle(rng: random) -> np.ndarray:  # type: ignore[type-arg]
    """Sample a random initial position that satisfies all constraints.

    拘束を満たす乱数初期位置をサンプリングする。
    采样满足所有约束的随机初始位置。
    """
    for _ in range(10_000):
        x = np.array([rng.uniform(lo, hi) for lo, hi in BOUNDS])
        if is_feasible(x.tolist()):
            return x
    # Fall back to an unconstrained point (optimizer will apply penalty)
    return np.array([rng.uniform(lo, hi) for lo, hi in BOUNDS])


class ParticleSwarmOptimization(BaseOptimiser):
    """Particle Swarm Optimisation (PSO).

    粒子群最適化（PSO）。
    粒子群优化（PSO）。

    Parameters
    ----------
    seed:
        Random seed for reproducibility.
    pop:
        Swarm size (number of particles).
    w:
        Inertia weight.
    c1:
        Cognitive acceleration coefficient.
    c2:
        Social acceleration coefficient.
    """

    def __init__(
        self,
        seed: int | None = None,
        pop: int = _POP,
        w: float = _W,
        c1: float = _C1,
        c2: float = _C2,
    ) -> None:
        if seed is not None:
            _random.seed(seed)
            np.random.seed(seed)
        self._rng = _random.Random(seed)
        self.pop = pop
        self.w = w
        self.c1 = c1
        self.c2 = c2

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------
    def _init_swarm(self) -> tuple[np.ndarray, np.ndarray]:
        """Initialise positions and velocities."""
        positions = np.zeros((self.pop, 4))
        for i in range(self.pop):
            positions[i] = _random_feasible_particle(self._rng)
        velocities = np.zeros((self.pop, 4))
        return positions, velocities

    def _eval_swarm(self, positions: np.ndarray) -> np.ndarray:
        """Compute penalised objective for every particle."""
        return np.array([penalized_objective(positions[i].tolist()) for i in range(self.pop)])

    def _update_velocity(
        self,
        velocities: np.ndarray,
        positions: np.ndarray,
        pbest_pos: np.ndarray,
        gbest_pos: np.ndarray,
    ) -> np.ndarray:
        """Standard PSO velocity update with per-dimension clamping."""
        n, d = velocities.shape
        r1 = np.random.rand(n, d)
        r2 = np.random.rand(n, d)
        new_v = (
            self.w * velocities
            + self.c1 * r1 * (pbest_pos - positions)
            + self.c2 * r2 * (gbest_pos - positions)
        )
        # Clamp per dimension
        for j, (v_lo, v_hi) in enumerate(_V_CLAMP):
            new_v[:, j] = np.clip(new_v[:, j], v_lo, v_hi)
        return new_v

    @staticmethod
    def _clip_positions(positions: np.ndarray) -> np.ndarray:
        """Clip positions to the search-space bounds."""
        for j, (lo, hi) in enumerate(BOUNDS):
            positions[:, j] = np.clip(positions[:, j], lo, hi)
        return positions

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------
    def run(  # type: ignore[override]
        self,
        iterations: int = _ITERS,
        verbose: bool = False,
    ) -> OptimisationResult:
        """Run PSO and return the best result found.

        PSO を実行して最良の結果を返す。
        运行 PSO 并返回找到的最佳结果。

        Parameters
        ----------
        iterations:
            Number of velocity-update iterations.
        verbose:
            Print progress to stdout.

        Returns
        -------
        OptimisationResult
        """
        positions, velocities = self._init_swarm()

        fitness = self._eval_swarm(positions)
        pbest_pos = positions.copy()
        pbest_fit = fitness.copy()

        gbest_idx = int(np.argmin(pbest_fit))
        gbest_pos = pbest_pos[gbest_idx].copy()
        gbest_fit = float(pbest_fit[gbest_idx])

        cost_history: list[float] = [gbest_fit]

        for it in range(iterations):
            velocities = self._update_velocity(velocities, positions, pbest_pos, gbest_pos)
            positions = self._clip_positions(positions + velocities)

            fitness = self._eval_swarm(positions)

            # Update personal bests
            improved = fitness < pbest_fit
            pbest_pos[improved] = positions[improved].copy()
            pbest_fit[improved] = fitness[improved]

            # Update global best
            best_idx = int(np.argmin(pbest_fit))
            if pbest_fit[best_idx] < gbest_fit:
                gbest_pos = pbest_pos[best_idx].copy()
                gbest_fit = float(pbest_fit[best_idx])

            cost_history.append(gbest_fit)
            if verbose:
                print(f"[PSO] iter={it+1:4d}  gbest={gbest_fit:.5f}")

        best_x = gbest_pos.tolist()
        feasible = is_feasible(best_x)
        return OptimisationResult(
            best_x=best_x,
            best_cost=objective(best_x) if feasible else gbest_fit,
            cost_history=cost_history,
            is_feasible=feasible,
        )
