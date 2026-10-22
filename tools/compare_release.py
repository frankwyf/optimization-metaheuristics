"""Run a fixed, complete before/after seed plan; use --source-root for old code.

Example: python tools/compare_release.py --source-root results/before --output results/before.json
"""

from __future__ import annotations

import argparse
import json
import platform
import statistics
import sys
import time
from dataclasses import asdict
from pathlib import Path


def main() -> None:
    """Record every run and descriptive statistics for a predeclared seed plan."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    sys.path.insert(0, str(args.source_root.resolve()))

    import numpy as np

    import metaheuristics
    from metaheuristics.algorithms import (
        DifferentialEvolution,
        GeneticAlgorithm,
        ParticleSwarmOptimization,
        SimulatedAnnealing,
    )
    from metaheuristics.benchmarks import get_benchmark_problem
    from metaheuristics.problem import WELDED_BEAM_PROBLEM

    plan = [
        ("ga", GeneticAlgorithm, {"pop_size": 16}, {"max_iteration": 20, "verbose": False}),
        ("pso", ParticleSwarmOptimization, {"pop": 16}, {"iterations": 20}),
        ("de", DifferentialEvolution, {"pop_size": 16}, {"max_iterations": 20}),
        (
            "sa",
            SimulatedAnnealing,
            {"t_max": 2.0, "t_min": 0.5, "cooling": 0.5},
            {"samples_per_temperature": 100},
        ),
    ]
    seeds = list(range(20))
    reports = []
    for problem in (get_benchmark_problem("sphere_2d"), WELDED_BEAM_PROBLEM):
        for name, algorithm, constructor, run_options in plan:
            runs = []
            for seed in seeds:
                optimizer = algorithm(problem=problem, seed=seed, **constructor)
                start = time.perf_counter()
                result = optimizer.run(**run_options)
                runs.append({**asdict(result), "runtime_seconds": time.perf_counter() - start})
            feasible = [run["objective_value"] for run in runs if run["is_feasible"]]
            reports.append(
                {
                    "algorithm": name,
                    "problem": problem.name,
                    "constructor": constructor,
                    "run_options": run_options,
                    "summary": {
                        "mean": statistics.mean(feasible) if feasible else None,
                        "std": statistics.pstdev(feasible) if feasible else None,
                        "feasibility_rate": len(feasible) / len(runs),
                        "best_objective": min(feasible) if feasible else None,
                        "mean_runtime_seconds": statistics.mean(
                            run["runtime_seconds"] for run in runs
                        ),
                        "mean_evaluations": statistics.mean(run["n_evaluations"] for run in runs),
                        "mean_final_penalized_value": statistics.mean(
                            run["penalized_cost"] for run in runs
                        ),
                        "nonmonotone_histories": sum(
                            any(b > a for a, b in zip(run["cost_history"], run["cost_history"][1:]))
                            for run in runs
                        ),
                    },
                    "runs": runs,
                }
            )
    payload = {
        "version": metaheuristics.__version__,
        "python": sys.version,
        "numpy": np.__version__,
        "platform": platform.platform(),
        "seeds": seeds,
        "std_ddof": 0,
        "reports": reports,
        "interpretation": "Paired implementation check, not a fair cross-algorithm budget comparison or a claim of quality improvement.",
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    print(f"Saved {len(reports) * len(seeds)} runs: {args.output}")


if __name__ == "__main__":
    main()
