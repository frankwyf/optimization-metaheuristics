"""Compare all algorithms on the welded-beam problem.

全アルゴリズムを焊接梁问题上比較する例。
在焊接梁问题上比较所有算法的示例。

Usage:
    python examples/compare_algorithms.py
"""
from __future__ import annotations

import numpy as np

from metaheuristics.algorithms import (
    DifferentialEvolution,
    GeneticAlgorithm,
    ParticleSwarmOptimization,
    SimulatedAnnealing,
)
from metaheuristics.problem import KNOWN_OPTIMUM


def main() -> None:
    n_runs = 5
    seed = 42

    algorithms = {
        "GA": lambda s: GeneticAlgorithm(seed=s).run(max_iteration=200, verbose=False),
        "PSO": lambda s: ParticleSwarmOptimization(seed=s).run(iterations=50, verbose=False),
        "SA": lambda s: SimulatedAnnealing(seed=s).run(samples_per_temperature=5000, verbose=False),
        "DE": lambda s: DifferentialEvolution(seed=s).run(max_iterations=200, verbose=False),
    }

    print(f"{'Algorithm':<6} {'Best':>10} {'Mean':>10} {'Std':>10} {'Feasible':>10}")
    print("-" * 50)

    all_histories: dict[str, list[float]] = {}

    for name, run_fn in algorithms.items():
        costs = []
        best_history = None
        best_cost = float("inf")

        for i in range(n_runs):
            result = run_fn(seed + i)
            costs.append(result.best_cost)
            if result.best_cost < best_cost:
                best_cost = result.best_cost
                best_history = result.cost_history

        arr = np.array(costs)
        feasible_count = sum(1 for c in costs if c < 100)  # rough heuristic
        print(
            f"{name:<6} {arr.min():>10.4f} {arr.mean():>10.4f} "
            f"{arr.std():>10.4f} {feasible_count:>6}/{n_runs}"
        )
        if best_history:
            all_histories[name] = best_history

    print(f"\nKnown optimum: {KNOWN_OPTIMUM:.4f}")

    # Plot if matplotlib available
    try:
        import matplotlib.pyplot as plt

        from metaheuristics.utils.visualization import plot_convergence

        plot_convergence(all_histories, title="Algorithm Comparison — Welded Beam")
        plt.tight_layout()
        plt.savefig("comparison.png", dpi=150, bbox_inches="tight")
        print("\nPlot saved: comparison.png")
        plt.show()
    except Exception as e:
        print(f"\n(Plot skipped: {e})")


if __name__ == "__main__":
    main()
