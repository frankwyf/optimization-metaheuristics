"""Evaluate algorithms on standard benchmark functions.

標準ベンチマーク関数でアルゴリズムを評価する。
在标准基准函数上评估算法。

Usage:
    python examples/benchmark_functions.py
"""
from __future__ import annotations

import numpy as np

from metaheuristics.benchmarks import BENCHMARKS


def run_de_on_benchmark(name: str, bench: dict, n_runs: int = 10) -> dict:
    """Run DE on a benchmark function and collect statistics."""
    costs = []
    for i in range(n_runs):
        rng = np.random.default_rng(i)
        bounds = bench["bounds"]
        func = bench["func"]
        dim = len(bounds)
        pop_size = 50

        # Init population
        pop = np.zeros((pop_size, dim))
        for j, (lo, hi) in enumerate(bounds):
            pop[:, j] = rng.uniform(lo, hi, size=pop_size)
        fitness = np.array([func(pop[k]) for k in range(pop_size)])

        # Run DE/rand/1/bin for 300 generations
        for _gen in range(300):
            for idx in range(pop_size):
                indices = list(range(pop_size))
                indices.remove(idx)
                r1, r2, r3 = rng.choice(indices, size=3, replace=False)
                mutant = pop[r1] + 0.8 * (pop[r2] - pop[r3])
                for j, (lo, hi) in enumerate(bounds):
                    mutant[j] = np.clip(mutant[j], lo, hi)

                # Binomial crossover
                trial = pop[idx].copy()
                j_rand = rng.integers(dim)
                for j in range(dim):
                    if rng.random() < 0.9 or j == j_rand:
                        trial[j] = mutant[j]

                trial_fit = func(trial)
                if trial_fit <= fitness[idx]:
                    pop[idx] = trial
                    fitness[idx] = trial_fit

        costs.append(float(fitness.min()))

    arr = np.array(costs)
    return {"best": arr.min(), "mean": arr.mean(), "std": arr.std()}


def main() -> None:
    print(f"{'Benchmark':<20} {'Best':>10} {'Mean':>10} {'Std':>10} {'Target':>10}")
    print("-" * 65)

    for name, bench in BENCHMARKS.items():
        stats = run_de_on_benchmark(name, bench)
        target = bench["global_minimum"]
        print(
            f"{bench['name']:<20} {stats['best']:>10.6f} {stats['mean']:>10.6f} "
            f"{stats['std']:>10.6f} {target:>10.4f}"
        )


if __name__ == "__main__":
    main()
