"""CLI runner for algorithms on welded-beam and standard benchmark problems."""
from __future__ import annotations

import argparse
import csv
import json
import platform
import sys
import time
from dataclasses import asdict
from importlib.metadata import PackageNotFoundError, version
from pathlib import Path
from typing import Any

import numpy as np

from metaheuristics import __version__ as package_version
from metaheuristics.algorithms import (
    DifferentialEvolution,
    GeneticAlgorithm,
    ParticleSwarmOptimization,
    SimulatedAnnealing,
)
from metaheuristics.benchmarks import BENCHMARKS, get_benchmark_problem
from metaheuristics.problem import KNOWN_OPTIMUM, KNOWN_OPTIMUM_X, WELDED_BEAM_PROBLEM

ALGORITHMS: dict[str, type] = {
    "ga": GeneticAlgorithm,
    "pso": ParticleSwarmOptimization,
    "sa": SimulatedAnnealing,
    "de": DifferentialEvolution,
}

PROBLEMS = {"welded-beam": WELDED_BEAM_PROBLEM, **{name: None for name in BENCHMARKS}}

_QUICK_KWARGS: dict[str, dict[str, int]] = {
    "ga": {"max_iteration": 50},
    "pso": {"iterations": 30},
    "sa": {"samples_per_temperature": 500},
    "de": {"max_iterations": 100},
}

_RUN_DEFAULTS: dict[str, dict[str, int]] = {
    "ga": {"max_iteration": 1300},
    "pso": {"iterations": 100},
    "sa": {"samples_per_temperature": 20_000},
    "de": {"max_iterations": 500},
}


def _positive_int(value: str) -> int:
    parsed = int(value)
    if parsed <= 0:
        raise argparse.ArgumentTypeError("must be a positive integer")
    return parsed


def _non_negative_int(value: str) -> int:
    parsed = int(value)
    if parsed < 0:
        raise argparse.ArgumentTypeError("must be a non-negative integer")
    return parsed


def get_problem(name: str):
    """Resolve a built-in problem by registry key."""
    if name == "welded-beam":
        return WELDED_BEAM_PROBLEM
    return get_benchmark_problem(name)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="metaheuristics-run",
        description="Run a metaheuristic optimizer on a built-in problem.",
    )
    parser.add_argument(
        "algorithm",
        nargs="?",
        choices=sorted(ALGORITHMS),
        help="Algorithm to run (ga, pso, sa, de).",
    )
    parser.add_argument("--list", action="store_true", help="List algorithms and problems, then exit.")
    parser.add_argument("--problem", choices=sorted(PROBLEMS), default="welded-beam")
    parser.add_argument("--seed", type=int, default=None, help="First seed; each run increments it by one.")
    parser.add_argument("--runs", type=_positive_int, default=5, help="Number of independent runs.")
    parser.add_argument("--no-plot", action="store_true", help="Disable convergence plot.")
    parser.add_argument("--verbose", action="store_true", help="Print per-iteration progress.")
    parser.add_argument("--quick", action="store_true", help="Use reduced iterations for testing.")
    parser.add_argument("--output-dir", type=Path, default=None, help="Save JSON/CSV results and plots here.")
    parser.add_argument("--max-iteration", type=_positive_int, default=None, help="[GA] Max generations.")
    parser.add_argument("--pop-size", type=_positive_int, default=None, help="Population size (GA/PSO/DE).")
    parser.add_argument("--iterations", type=_non_negative_int, default=None, help="[PSO/DE] Iteration count.")
    parser.add_argument(
        "--samples-per-temperature",
        type=_positive_int,
        default=None,
        help="[SA] Samples per temperature level.",
    )
    return parser


def _format_table(headers: list[str], rows: list[list[str]], col_width: int = 16) -> str:
    header_line = " | ".join(header.center(col_width) for header in headers)
    lines = [header_line, "-" * len(header_line)]
    lines.extend(" | ".join(str(value).center(col_width) for value in row) for row in rows)
    return "\n".join(lines)


def list_algorithms() -> None:
    print("\nAvailable algorithms:")
    for name, cls in sorted(ALGORITHMS.items()):
        print(f"  {name:4s}  {cls.__name__}")
    print("\nAvailable problems:")
    for name in sorted(PROBLEMS):
        problem = get_problem(name)
        optimum = "unknown" if problem.known_optimum is None else f"{problem.known_optimum:.6g}"
        print(f"  {name:18s} {problem.dimension:2d}D  {problem.name}  optimum={optimum}")
    print(f"\nWelded-beam reference: f(x*) = {KNOWN_OPTIMUM:.6f}; x* = {KNOWN_OPTIMUM_X}\n")


def _run_kwargs(algo_name: str, args: argparse.Namespace) -> dict[str, Any]:
    kwargs: dict[str, Any] = {**_RUN_DEFAULTS[algo_name], "verbose": args.verbose}
    if args.quick:
        kwargs.update(_QUICK_KWARGS[algo_name])
    if algo_name == "ga" and args.max_iteration is not None:
        kwargs["max_iteration"] = args.max_iteration
    elif algo_name == "pso" and args.iterations is not None:
        kwargs["iterations"] = args.iterations
    elif algo_name == "sa" and args.samples_per_temperature is not None:
        kwargs["samples_per_temperature"] = args.samples_per_temperature
    elif algo_name == "de" and args.iterations is not None:
        kwargs["max_iterations"] = args.iterations
    return kwargs


def _save_results(
    output_dir: Path,
    algorithm: str,
    problem_name: str,
    problem: Any,
    run_records: list[dict[str, Any]],
    summary: dict[str, Any],
) -> tuple[Path, Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    stem = f"experiment_{algorithm}_{problem_name}"
    json_path = output_dir / f"{stem}.json"
    csv_path = output_dir / f"{stem}.csv"
    payload = {
        "schema_version": 1,
        "algorithm": algorithm,
        "problem": problem_name,
        "problem_definition": {
            "name": problem.name,
            "bounds": [list(bound) for bound in problem.bounds],
            "known_optimum": problem.known_optimum,
            "known_optimum_x": problem.known_optimum_x,
            "penalty": problem.penalty,
        },
        "environment": {
            "python": sys.version,
            "platform": platform.platform(),
            "numpy": np.__version__,
            "package": package_version,
            "matplotlib": _optional_package_version("matplotlib"),
            "seaborn": _optional_package_version("seaborn"),
        },
        "summary": summary,
        "runs": run_records,
    }
    json_path.write_text(json.dumps(payload, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    with csv_path.open("w", newline="", encoding="utf-8") as handle:
        fields = [
            "algorithm", "problem", "seed", "is_feasible", "objective_value",
            "penalized_cost", "n_evaluations", "runtime_seconds", "best_x",
        ]
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for record in run_records:
            writer.writerow(
                {
                    **{key: record[key] for key in fields if key != "best_x"},
                    "best_x": json.dumps(record["best_x"]),
                }
            )
    return json_path, csv_path


def _optional_package_version(package_name: str) -> str | None:
    try:
        return version(package_name)
    except PackageNotFoundError:
        return None


def _optimizer_parameters(optimizer: Any) -> dict[str, Any]:
    """Return scalar constructor settings, excluding runtime objects."""
    skip = {"problem", "_rng", "_np_rng", "history_transform", "n_evaluations"}
    return {
        name: value
        for name, value in vars(optimizer).items()
        if name not in skip and isinstance(value, (str, int, float, bool, type(None)))
    }


def run_algorithm(algo_name: str, args: argparse.Namespace) -> None:
    """Run one algorithm repeatedly and optionally export machine-readable data."""
    cls = ALGORITHMS[algo_name]
    problem = get_problem(args.problem)
    kwargs = _run_kwargs(algo_name, args)
    runs = []
    cost_histories: dict[str, list[float]] = {}
    effective_parameters: dict[str, Any] | None = None

    print(f"\n{'=' * 68}")
    print(f"  Algorithm: {cls.__name__} ({algo_name.upper()})")
    print(f"  Problem: {problem.name} ({problem.dimension} dimensions)")
    print(f"  Runs: {args.runs} | Seed: {args.seed if args.seed is not None else 'random'}")
    print(f"{'=' * 68}\n")

    total_start = time.perf_counter()
    for index in range(args.runs):
        seed = args.seed + index if args.seed is not None else None
        constructor_kwargs: dict[str, Any] = {"seed": seed, "problem": problem}
        if args.pop_size is not None and algo_name in ("ga", "pso", "de"):
            constructor_kwargs["pop" if algo_name == "pso" else "pop_size"] = args.pop_size
        optimizer = cls(**constructor_kwargs)
        if effective_parameters is None:
            effective_parameters = _optimizer_parameters(optimizer)
        start = time.perf_counter()
        result = optimizer.run(**kwargs)
        elapsed = time.perf_counter() - start
        runs.append((seed, result, elapsed))
        cost_histories[f"Run {index + 1}"] = result.cost_history
        status = "feasible" if result.is_feasible else "infeasible"
        print(
            f"  Run {index + 1:2d}: objective={result.objective_value:.6f} "
            f"[{status}] evaluations={result.n_evaluations}"
        )
    total_elapsed = time.perf_counter() - total_start

    feasible_values = np.array(
        [result.objective_value for _, result, _ in runs if result.is_feasible], dtype=float
    )
    all_penalized = np.array([result.penalized_cost for _, result, _ in runs], dtype=float)
    n_feasible = len(feasible_values)
    summary: dict[str, Any] = {
        "runs": args.runs,
        "feasible_runs": n_feasible,
        "feasibility_rate": n_feasible / args.runs,
        "best_feasible_objective": float(feasible_values.min()) if n_feasible else None,
        "mean_feasible_objective": float(feasible_values.mean()) if n_feasible else None,
        "std_feasible_objective": float(feasible_values.std()) if n_feasible else None,
        "best_penalized_value": float(all_penalized.min()),
        "objective_evaluation_std": float(np.std([r.n_evaluations for _, r, _ in runs])),
        "mean_runtime_seconds": float(np.mean([elapsed for _, _, elapsed in runs])),
        "total_runtime_seconds": total_elapsed,
        "mean_objective_evaluations": float(np.mean([r.n_evaluations for _, r, _ in runs])),
        "seed_start": args.seed,
        "algorithm_parameters": {
            "constructor": effective_parameters,
            "run": kwargs,
        },
    }
    rows = [
        ["Best feasible", f"{summary['best_feasible_objective']:.6f}" if n_feasible else "n/a"],
        ["Mean feasible", f"{summary['mean_feasible_objective']:.6f}" if n_feasible else "n/a"],
        ["Std Dev", f"{summary['std_feasible_objective']:.6f}" if n_feasible else "n/a"],
        ["Feasible", f"{n_feasible}/{args.runs}"],
        ["Mean evaluations", f"{summary['mean_objective_evaluations']:.1f}"],
        ["Time (s)", f"{total_elapsed:.3f}"],
    ]
    print(f"\n{'─' * 68}\n  Summary Statistics\n{'─' * 68}")
    print(_format_table(["Metric", "Value"], rows))
    if n_feasible and problem.known_optimum not in (None, 0.0):
        gap = (summary["best_feasible_objective"] - problem.known_optimum) / abs(problem.known_optimum) * 100
        print(f"\n  Gap to known optimum ({problem.known_optimum:.6f}): {gap:+.2f}%")
    best_result = min(
        (result for _, result, _ in runs),
        key=lambda result: result.objective_value if result.is_feasible else float("inf"),
    ) if n_feasible else min((result for _, result, _ in runs), key=lambda result: result.penalized_cost)
    print(f"\n  Best solution: x = {[float(value) for value in best_result.best_x]}")
    print(f"  Feasible: {best_result.is_feasible}\n")

    run_records = []
    for seed, result, elapsed in runs:
        record = asdict(result)
        record.update(
            algorithm=algo_name,
            problem=args.problem,
            runtime_seconds=elapsed,
            algorithm_parameters=summary["algorithm_parameters"],
        )
        record["seed"] = seed
        run_records.append(record)
    if args.output_dir is not None:
        json_path, csv_path = _save_results(
            args.output_dir, algo_name, args.problem, problem, run_records, summary
        )
        print(f"  Results saved: {json_path} and {csv_path}")

    if not args.no_plot:
        try:
            import matplotlib.pyplot as plt

            from metaheuristics.utils.visualization import plot_convergence, plot_run_statistics

            fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))
            plot_convergence(cost_histories, title=f"{cls.__name__} Convergence", ax=ax1)
            if n_feasible:
                plot_run_statistics({algo_name.upper(): feasible_values.tolist()}, ax=ax2)
            else:
                ax2.set_axis_off()
            fig.tight_layout()
            if args.output_dir is not None:
                plot_path = args.output_dir / f"convergence_{algo_name}_{args.problem}.png"
                fig.savefig(plot_path, dpi=150, bbox_inches="tight")
                print(f"  Plot saved: {plot_path}")
            if getattr(fig.canvas, "required_interactive_framework", None) is not None:
                plt.show()
            plt.close(fig)
        except Exception as exc:
            print(f"  (Plot skipped: {exc})")


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
