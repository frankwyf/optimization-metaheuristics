"""CLI runner for the metaheuristics package.

Provides a single entry point to run any algorithm on the welded-beam problem
with tabulated results and optional convergence plots.

メタヒューリスティクスパッケージの CLI ランナー。
元启发式算法包的命令行工具。
"""
from __future__ import annotations

import argparse
import time

import numpy as np

from metaheuristics.algorithms import (
    DifferentialEvolution,
    GeneticAlgorithm,
    ParticleSwarmOptimization,
    SimulatedAnnealing,
)
from metaheuristics.problem import KNOWN_OPTIMUM, KNOWN_OPTIMUM_X

# Algorithm registry
ALGORITHMS: dict[str, type] = {
    "ga": GeneticAlgorithm,
    "pso": ParticleSwarmOptimization,
    "sa": SimulatedAnnealing,
    "de": DifferentialEvolution,
}

# Default quick-run kwargs per algorithm
_QUICK_KWARGS: dict[str, dict] = {
    "ga": {"max_iteration": 50},
    "pso": {"iterations": 30},
    "sa": {"samples_per_temperature": 500},
    "de": {"max_iterations": 100},
}


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="metaheuristics-run",
        description="Run metaheuristic optimisation on the welded-beam problem.",
    )
    parser.add_argument(
        "algorithm",
        nargs="?",
        choices=sorted(ALGORITHMS),
        help="Algorithm to run (ga, pso, sa, de).",
    )
    parser.add_argument("--list", action="store_true", help="List available algorithms and exit.")
    parser.add_argument("--seed", type=int, default=None, help="Random seed for reproducibility.")
    parser.add_argument("--runs", type=int, default=5, help="Number of independent runs.")
    parser.add_argument("--no-plot", action="store_true", help="Disable convergence plot.")
    parser.add_argument("--verbose", action="store_true", help="Print per-iteration progress.")
    parser.add_argument("--quick", action="store_true", help="Use reduced iterations for testing.")

    # Algorithm-specific args
    parser.add_argument("--max-iteration", type=int, default=None, help="[GA] Max generations.")
    parser.add_argument("--pop-size", type=int, default=None, help="[GA/PSO/DE] Population size.")
    parser.add_argument("--iterations", type=int, default=None, help="[PSO/DE] Max iterations.")
    parser.add_argument(
        "--samples-per-temperature", type=int, default=None, help="[SA] Samples per T level."
    )
    return parser


def _format_table(headers: list[str], rows: list[list[str]], col_width: int = 14) -> str:
    """Simple fixed-width table formatter."""
    lines = []
    header_line = " | ".join(h.center(col_width) for h in headers)
    lines.append(header_line)
    lines.append("-" * len(header_line))
    for row in rows:
        lines.append(" | ".join(str(c).center(col_width) for c in row))
    return "\n".join(lines)


def list_algorithms() -> None:
    print("\nAvailable algorithms:")
    print("=" * 50)
    for name, cls in sorted(ALGORITHMS.items()):
        print(f"  {name:4s}  {cls.__name__}")
    print(f"\nKnown optimum: f(x*) = {KNOWN_OPTIMUM:.6f}")
    print(f"  x* = {KNOWN_OPTIMUM_X}")
    print()


def run_algorithm(algo_name: str, args: argparse.Namespace) -> None:
    """Run the specified algorithm multiple times and report statistics."""
    cls = ALGORITHMS[algo_name]
    n_runs = args.runs

    # Build run kwargs from quick defaults + explicit CLI overrides
    run_kwargs: dict = {"verbose": args.verbose}
    if args.quick:
        run_kwargs.update(_QUICK_KWARGS.get(algo_name, {}))

    if algo_name == "ga" and args.max_iteration is not None:
        run_kwargs["max_iteration"] = args.max_iteration
    elif algo_name == "pso" and args.iterations is not None:
        run_kwargs["iterations"] = args.iterations
    elif algo_name == "sa" and args.samples_per_temperature is not None:
        run_kwargs["samples_per_temperature"] = args.samples_per_temperature
    elif algo_name == "de" and args.iterations is not None:
        run_kwargs["max_iterations"] = args.iterations

    print(f"\n{'='*60}")
    print(f"  Algorithm: {cls.__name__} ({algo_name.upper()})")
    print(f"  Runs: {n_runs} | Seed: {args.seed or 'random'}")
    print(f"{'='*60}\n")

    results = []
    cost_histories = {}
    t0 = time.perf_counter()

    for i in range(n_runs):
        seed_i = (args.seed + i) if args.seed is not None else None
        ctor_kwargs: dict = {"seed": seed_i}
        if args.pop_size is not None and algo_name in ("ga", "pso", "de"):
            ctor_kwargs["pop_size"] = args.pop_size

        opt = cls(**ctor_kwargs)

        # Filter run_kwargs to valid params for this algorithm
        filtered: dict = {"verbose": run_kwargs.get("verbose", False)}
        if algo_name == "ga" and "max_iteration" in run_kwargs:
            filtered["max_iteration"] = run_kwargs["max_iteration"]
        elif algo_name == "pso" and "iterations" in run_kwargs:
            filtered["iterations"] = run_kwargs["iterations"]
        elif algo_name == "sa" and "samples_per_temperature" in run_kwargs:
            filtered["samples_per_temperature"] = run_kwargs["samples_per_temperature"]
        elif algo_name == "de" and "max_iterations" in run_kwargs:
            filtered["max_iterations"] = run_kwargs["max_iterations"]

        result = opt.run(**filtered)
        results.append(result)
        cost_histories[f"Run {i+1}"] = result.cost_history

        status = "feasible" if result.is_feasible else "infeasible"
        print(f"  Run {i+1:2d}: cost={result.best_cost:.6f}  [{status}]")

    elapsed = time.perf_counter() - t0

    # Statistics
    costs = np.array([r.best_cost for r in results])
    feasible_costs = np.array([r.best_cost for r in results if r.is_feasible])
    n_feasible = len(feasible_costs)

    print(f"\n{'─'*60}")
    print("  Summary Statistics")
    print(f"{'─'*60}")

    headers = ["Metric", "Value"]
    rows = [
        ["Best", f"{costs.min():.6f}"],
        ["Worst", f"{costs.max():.6f}"],
        ["Mean", f"{costs.mean():.6f}"],
        ["Std Dev", f"{costs.std():.6f}"],
        ["Feasible", f"{n_feasible}/{n_runs}"],
        ["Time (s)", f"{elapsed:.2f}"],
    ]
    if n_feasible > 0:
        rows.append(["Best feasible", f"{feasible_costs.min():.6f}"])
    print(_format_table(headers, rows))

    known_opt = KNOWN_OPTIMUM
    if n_feasible > 0:
        gap = (feasible_costs.min() - known_opt) / known_opt * 100
        print(f"\n  Gap to known optimum ({known_opt:.6f}): {gap:+.2f}%")

    best_result = min(results, key=lambda r: r.best_cost)
    print(f"\n  Best solution: x = {[f'{v:.6f}' for v in best_result.best_x]}")
    print(f"  Feasible: {best_result.is_feasible}")
    print()

    # Plot convergence
    if not args.no_plot and n_runs > 0:
        try:
            import matplotlib.pyplot as plt

            from metaheuristics.utils.visualization import plot_convergence, plot_run_statistics

            fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))
            plot_convergence(cost_histories, title=f"{cls.__name__} Convergence", ax=ax1)
            if n_feasible > 0:
                plot_run_statistics(
                    {algo_name.upper(): feasible_costs.tolist()},
                    title="Run Statistics",
                    ax=ax2,
                )
            plt.tight_layout()
            plt.savefig(f"convergence_{algo_name}.png", dpi=150, bbox_inches="tight")
            print(f"  Plot saved: convergence_{algo_name}.png")
            plt.show()
        except Exception as e:
            print(f"  (Plot skipped: {e})")


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.list:
        list_algorithms()
        return 0

    if not args.algorithm:
        parser.print_help()
        return 1

    run_algorithm(args.algorithm, args)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
