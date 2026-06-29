"""Genetic Algorithm (GA) with Ant Colony-assisted restart for the welded-beam problem.

A binary-encoded GA with rank-based selection, two-point crossover, and
bitwise mutation. When the population stagnates, an Ant Colony Optimisation
(ACO) perturbation is applied to diversify the gene pool.

バイナリエンコードされた遺伝的アルゴリズム（GA）。
二进制编码的遗传算法（GA），用于焊接梁问题。

References
----------
Holland, J. H. (1992). Adaptation in Natural and Artificial Systems.
MIT Press.
"""
from __future__ import annotations

import copy
import math
from typing import Callable

import numpy as np

from metaheuristics.algorithms.base import BaseOptimiser, OptimisationResult
from metaheuristics.problem import BOUNDS, is_feasible, objective, penalized_objective

# Default hyperparameters
_POP_SIZE: int = 300
_CROSSOVER: float = 0.95  # Crossover probability
_MUTATION: float = 0.70   # Per-bit mutation probability
_NOCHANGE: int = 250       # Stagnation patience (generations)
_ELITE_FRAC: float = 0.50  # Fraction of elite individuals carried forward
_BIN_LEN: int = 64         # Binary bits per variable


# ---------------------------------------------------------------------------
# Individual (binary chromosome)
# ---------------------------------------------------------------------------
class _Individual:
    """Binary-encoded design vector with decode, crossover, and mutation.

    バイナリエンコードされた設計変数。
    二进制编码的设计变量。
    """

    _bounds = BOUNDS
    _bin_len = _BIN_LEN

    def __init__(self, chromosome: str | None = None) -> None:
        total = self._bin_len * len(self._bounds)
        self.chromosome: str = chromosome if chromosome is not None else "0" * total

    # ---- Encoding helpers ------------------------------------------------
    def _bin2float(self, bits: str, dim: int) -> float:
        lo, hi = self._bounds[dim]
        return lo + int(bits, 2) / float((2 ** self._bin_len) - 1) * (hi - lo)

    def _segments(self) -> list[str]:
        L = self._bin_len
        return [self.chromosome[i * L : (i + 1) * L] for i in range(len(self._bounds))]

    def decode(self) -> list[float]:
        """Decode chromosome to a real-valued design vector."""
        return [self._bin2float(seg, i) for i, seg in enumerate(self._segments())]

    # ---- Genetic operators -----------------------------------------------
    def randomize(self) -> None:
        """Assign a uniformly random chromosome."""
        bits = np.random.randint(0, 2, self._bin_len * len(self._bounds))
        self.chromosome = "".join(map(str, bits))

    def crossover(self, other: "_Individual") -> tuple[str, str]:
        """Two-point crossover returning two child chromosomes."""
        total = self._bin_len * len(self._bounds)
        lo, hi = sorted(np.random.choice(range(total), size=2, replace=False))
        c1 = self.chromosome[:lo] + other.chromosome[lo:hi] + self.chromosome[hi:]
        c2 = other.chromosome[:lo] + self.chromosome[lo:hi] + other.chromosome[hi:]
        return c1, c2

    def mutate(self, prob: float) -> None:
        """Flip each bit independently with probability *prob*.

        Only accepts the mutation if the resulting individual is feasible.
        """
        total = self._bin_len * len(self._bounds)
        flip_mask = np.random.rand(total) < prob
        mask_int = int("".join(str(int(b)) for b in flip_mask), 2)
        new_chrom = ("{:0%db}" % total).format(mask_int ^ int(self.chromosome, 2))
        candidate = _Individual(new_chrom).decode()
        if is_feasible(candidate):
            self.chromosome = new_chrom

    # ---- Fitness ----------------------------------------------------------
    def fitness(self) -> float:
        """Penalised objective (lower is better)."""
        x = self.decode()
        return penalized_objective(x)

    def __repr__(self) -> str:
        x = self.decode()
        return "h={:.6f} l={:.6f} t={:.6f} b={:.6f}".format(*x)


# ---------------------------------------------------------------------------
# Ant Colony perturbation (diversification operator)
# ---------------------------------------------------------------------------
def _ant_colony_perturb(population: list[_Individual]) -> list[_Individual]:
    """Lightly perturb the population using pheromone-guided mutation.

    This is a lightweight diversification heuristic that replaces fully
    stagnated runs of pure ACO. It applies a high-rate mutation to each
    individual, weighted by their current fitness (pheromone analogy).

    集団をフェロモンガイド付き変異で軽く摂動させる。
    使用信息素引导的变异轻微扰动种群。
    """
    fitnesses = np.array([ind.fitness() for ind in population])
    # Normalise fitness so worse individuals mutate more
    min_f, max_f = fitnesses.min(), fitnesses.max()
    if max_f > min_f:
        mutation_rates = 0.3 + 0.5 * (fitnesses - min_f) / (max_f - min_f)
    else:
        mutation_rates = np.full(len(population), 0.5)

    perturbed = []
    for ind, rate in zip(population, mutation_rates):
        new_ind = copy.deepcopy(ind)
        new_ind.mutate(float(rate))
        perturbed.append(new_ind)
    return perturbed


# ---------------------------------------------------------------------------
# GA engine
# ---------------------------------------------------------------------------
class GeneticAlgorithm(BaseOptimiser):
    """Genetic Algorithm (binary encoding, elitism, ACO-assisted restart).

    遺伝的アルゴリズム（二値エンコーディング、エリート主義、ACO補助再起動）。
    遗传算法（二进制编码、精英策略、ACO辅助重启）。

    Parameters
    ----------
    seed:
        NumPy random seed.
    pop_size:
        Population size.
    crossover_prob:
        Probability of crossover between two selected parents.
    mutation_prob:
        Per-bit mutation probability.
    stagnation_patience:
        Generations without improvement before stopping / diversifying.
    elite_fraction:
        Fraction of top individuals carried unchanged to the next generation.
    history_transform:
        Optional callable applied to each fitness value before recording.
    """

    def __init__(
        self,
        seed: int | None = None,
        pop_size: int = _POP_SIZE,
        crossover_prob: float = _CROSSOVER,
        mutation_prob: float = _MUTATION,
        stagnation_patience: int = _NOCHANGE,
        elite_fraction: float = _ELITE_FRAC,
        history_transform: Callable[[float], float] = lambda x: x,
    ) -> None:
        if seed is not None:
            np.random.seed(seed)
        self.pop_size = pop_size
        self.crossover_prob = crossover_prob
        self.mutation_prob = mutation_prob
        self.stagnation_patience = stagnation_patience
        self.elite_fraction = elite_fraction
        self.history_transform = history_transform

    # ------------------------------------------------------------------
    # Selection
    # ------------------------------------------------------------------
    def _selection(
        self, population: list[_Individual], fitnesses: list[float]
    ) -> list[_Individual]:
        """Rank-based selection with elitism."""
        n_elite = int(self.elite_fraction * len(population))
        ranked = [ind for _, ind in sorted(zip(fitnesses, population), key=lambda t: t[0])]
        elites = ranked[:n_elite]

        # Probability proportional to inverse rank
        n_pool = len(elites)
        probs = np.arange(n_pool, 0, -1, dtype=float)
        diversity = 0.5
        probs = probs / probs.sum() * (1 - diversity) + diversity / n_pool

        new_population: list[_Individual] = list(reversed(elites))
        while len(new_population) < self.pop_size:
            p1, p2 = (
                np.random.choice(elites, p=probs),  # type: ignore[arg-type]
                np.random.choice(elites, p=probs),  # type: ignore[arg-type]
            )
            if np.random.rand() < self.crossover_prob:
                c1_chrom, c2_chrom = p1.crossover(p2)
                child1, child2 = _Individual(c1_chrom), _Individual(c2_chrom)
            else:
                child1, child2 = copy.deepcopy(p1), copy.deepcopy(p2)
            child1.mutate(self.mutation_prob)
            child2.mutate(self.mutation_prob)
            offspring = child1 if child1.fitness() < child2.fitness() else child2
            new_population.append(offspring)

        return new_population

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------
    def run(  # type: ignore[override]
        self,
        max_iteration: int = 1300,
        verbose: bool = True,
    ) -> OptimisationResult:
        """Run the GA and return the best individual found.

        GA を実行して最良の個体を返す。
        运行 GA 并返回找到的最优个体。

        Parameters
        ----------
        max_iteration:
            Hard upper bound on the number of generations.
        verbose:
            Print progress every 50 generations.

        Returns
        -------
        OptimisationResult
        """
        # Initialise population
        population: list[_Individual] = []
        for _ in range(self.pop_size):
            ind = _Individual()
            ind.randomize()
            population.append(ind)
        population.sort(key=lambda ind: ind.fitness())

        best = copy.deepcopy(population[0])
        patience_left = self.stagnation_patience
        stagnant_gens = 0
        cost_history: list[float] = []

        for gen in range(max_iteration):
            cost_history.append(self.history_transform(best.fitness()))

            # Early-stop / diversify
            if patience_left < 0:
                if best.fitness() < 1.8:
                    break
                if best.fitness() > 2.0:
                    population = _ant_colony_perturb(population)
                    patience_left = self.stagnation_patience // 2
                else:
                    break

            # Diversify if stuck in a local optimum
            if best.fitness() > 1.83 and stagnant_gens >= 70:
                n_keep = int(self.pop_size * self.elite_fraction)
                population.sort(key=lambda ind: ind.fitness())
                population = population[:n_keep] + _ant_colony_perturb(population[n_keep:])
                stagnant_gens = 0

            fitnesses = [ind.fitness() for ind in population]
            best_idx = int(np.argmin(fitnesses))

            if fitnesses[best_idx] < best.fitness():
                best = copy.deepcopy(population[best_idx])
                patience_left = self.stagnation_patience
                stagnant_gens = 0
            else:
                stagnant_gens += 1

            population = self._selection(population, fitnesses)
            patience_left -= 1

            if verbose and gen % 50 == 0:
                print(
                    f"[GA] gen={gen:5d}  best={self.history_transform(best.fitness()):.5f}"
                    f"  patience={patience_left}"
                )

        x = best.decode()
        feasible = is_feasible(x)
        return OptimisationResult(
            best_x=x,
            best_cost=objective(x) if feasible else best.fitness(),
            cost_history=cost_history,
            is_feasible=feasible,
        )


# ---------------------------------------------------------------------------
# Convenience: reproduce the original __main__ entry point
# ---------------------------------------------------------------------------
def _run_cli(
    runs: int = 20,
    max_iteration: int = 1300,
    seed: int | None = None,
    show_plot: bool = True,
) -> None:
    """CLI-facing runner matching the original final/GA.py behaviour."""
    import time

    import matplotlib.pyplot as plt

    if seed is not None:
        np.random.seed(seed)

    ga = GeneticAlgorithm()
    best_costs: list[float] = []

    for run_idx in range(runs):
        t0 = time.time()
        result = ga.run(max_iteration=max_iteration, verbose=True)
        elapsed = time.time() - t0
        best_costs.append(result.best_cost if result.is_feasible else math.nan)

        plt.plot(result.cost_history)
        plt.xlabel(f"Generation ({len(result.cost_history)})")
        plt.ylabel("Best objective")
        plt.title(
            f"GA run {run_idx+1}/{runs}  min={min(result.cost_history):.4f}"
            f"  time={elapsed:.1f}s"
        )
        print(f"Run {run_idx+1}: best_x={result.best_x}  cost={result.best_cost:.6f}")
        if show_plot:
            plt.show()
        else:
            plt.close()

    print(
        f"\nSummary over {runs} runs:"
        f"\n  mean={np.nanmean(best_costs):.5f}"
        f"  min={np.nanmin(best_costs):.5f}"
        f"  max={np.nanmax(best_costs):.5f}"
        f"  std={np.nanstd(best_costs):.5f}"
    )
