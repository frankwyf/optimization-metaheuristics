"""CLI runner for algorithms on welded-beam and standard benchmark problems."""
from __future__ import annotations

import argparse
import secrets
import sys
from pathlib import Path
from typing import Any

from metaheuristics import __version__ as package_version
from metaheuristics.benchmarks import BENCHMARKS, get_benchmark_problem
from metaheuristics.experiments import ALGORITHMS, run_experiment
from metaheuristics.problem import KNOWN_OPTIMUM, KNOWN_OPTIMUM_X, WELDED_BEAM_PROBLEM

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
    parser.add_argument("--version", action="version", version=f"%(prog)s {package_version}")
    parser.add_argument("--list", action="store_true", help="List algorithms and problems, then exit.")
    parser.add_argument("--problem", choices=sorted(PROBLEMS), default="welded-beam")
    parser.add_argument("--seed", type=_non_negative_int, default=None, help="First seed; each run increments it by one.")
    parser.add_argument("--runs", type=_positive_int, default=5, help="Number of independent runs.")
    parser.add_argument("--no-plot", action="store_true", help="Disable convergence plot.")
    parser.add_argument("--verbose", action="store_true", help="Print per-iteration progress.")
    parser.add_argument("--quick", action="store_true", help="Use reduced iterations for testing.")
    parser.add_argument("--output-dir", type=Path, default=None, help="Save JSON/CSV results and plots here.")
    parser.add_argument("--max-iteration", type=_non_negative_int, default=None, help="[GA] Max generations.")
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


def run_algorithm(algo_name: str, args: argparse.Namespace) -> None:
    """Run one algorithm repeatedly and optionally export machine-readable data."""
    cls = ALGORITHMS[algo_name]
    problem = get_problem(args.problem)
    kwargs = _run_kwargs(algo_name, args)
    runs = []
    cost_histories: dict[str, list[float]] = {}

    print(f"\n{'=' * 68}")
    print(f"  Algorithm: {cls.__name__} ({algo_name.upper()})")
    print(f"  Problem: {problem.name} ({problem.dimension} dimensions)")
    print(f"  Runs: {args.runs} | Seed: {args.seed if args.seed is not None else 'random'}")
    print(f"{'=' * 68}\n")

    seed_start = args.seed if args.seed is not None else secrets.randbits(32)
    constructor_kwargs = {}
    if args.pop_size is not None and algo_name in ("ga", "pso", "de"):
        constructor_kwargs["pop" if algo_name == "pso" else "pop_size"] = args.pop_size
    experiment = run_experiment(
        algo_name, problem, seeds=[seed_start + index for index in range(args.runs)],
        optimizer_options=constructor_kwargs, run_options=kwargs,
    )
    for index, run in enumerate(experiment.runs):
        result = run.result
        runs.append((run.seed, result, run.runtime_seconds))
        cost_histories[f"Run {index + 1}"] = result.cost_history
        status = "feasible" if result.is_feasible else "infeasible"
        print(
            f"  Run {index + 1:2d}: objective={result.objective_value:.6f} "
            f"[{status}] evaluations={result.n_evaluations} seed={run.seed}"
        )
    summary = experiment.summary
    total_elapsed = experiment.total_runtime_seconds
    feasible_values = [run.result.objective_value for run in experiment.runs if run.result.is_feasible]
    n_feasible = len(feasible_values)
    rows = [
        ["Best feasible", f"{summary['best_feasible_objective']:.6f}" if n_feasible else "n/a"],
        ["Mean feasible", f"{summary['mean_feasible_objective']:.6f}" if n_feasible else "n/a"],
        ["Std Dev", f"{summary['std_feasible_objective']:.6f}" if n_feasible else "n/a"],
        ["Feasible", f"{n_feasible}/{args.runs}"],
        ["Mean evaluations", f"{summary['mean_objective_evaluations']:.1f}"],
        ["Time (s)", f"{total_elapsed:.3f}"],
    ]
    print(f"\n{'=' * 68}\n  Summary Statistics\n{'=' * 68}")
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

    if args.output_dir is not None:
        json_path, csv_path = experiment.save(
            args.output_dir, stem=f"experiment_{algo_name}_{args.problem}", problem_key=args.problem
        )
        print(f"  Results saved: {json_path} and {csv_path}")

    if not args.no_plot:
        try:
            import matplotlib.pyplot as plt

            from metaheuristics.utils.visualization import plot_convergence, plot_run_statistics

            fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))
            plot_convergence(cost_histories, title=f"{cls.__name__} Convergence", ax=ax1)
            if n_feasible:
                plot_run_statistics({algo_name.upper(): feasible_values}, ax=ax2)
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
            raise RuntimeError(f"Plotting failed: {exc}. Install .[plot] or use --no-plot.") from exc


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if args.list:
        list_algorithms()
        return 0
    if not args.algorithm:
        parser.print_help()
        return 1
    allowed = {
        "pop_size": {"ga", "pso", "de"},
        "iterations": {"pso", "de"},
        "max_iteration": {"ga"},
        "samples_per_temperature": {"sa"},
    }
    for option, algorithms in allowed.items():
        if getattr(args, option) is not None and args.algorithm not in algorithms:
            parser.error(f"--{option.replace('_', '-')} is not supported by {args.algorithm}")
    try:
        run_algorithm(args.algorithm, args)
    except (ValueError, TypeError) as exc:
        parser.error(str(exc))
    except (OSError, RuntimeError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
