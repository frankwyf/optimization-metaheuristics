"""Sequential, reproducible multi-seed experiments without plotting dependencies."""

from __future__ import annotations

import csv
import inspect
import json
import platform
import statistics
import sys
import time
from collections.abc import Mapping, Sequence
from dataclasses import asdict, dataclass
from importlib.metadata import PackageNotFoundError, version
from pathlib import Path
from typing import Any

import numpy as np

from metaheuristics import __version__
from metaheuristics._validation import require_int
from metaheuristics.algorithms import (
    DifferentialEvolution,
    GeneticAlgorithm,
    ParticleSwarmOptimization,
    SimulatedAnnealing,
)
from metaheuristics.algorithms.base import BaseOptimiser, OptimisationResult
from metaheuristics.problems import OptimizationProblem

ALGORITHMS: dict[str, type[BaseOptimiser]] = {
    "ga": GeneticAlgorithm,
    "pso": ParticleSwarmOptimization,
    "sa": SimulatedAnnealing,
    "de": DifferentialEvolution,
}


def _optional_version(name: str) -> str | None:
    try:
        return version(name)
    except PackageNotFoundError:
        return None


@dataclass(frozen=True)
class ExperimentRun:
    """One explicitly seeded optimizer result and its measured wall time."""

    seed: int
    result: OptimisationResult
    runtime_seconds: float


@dataclass(frozen=True)
class ExperimentResult:
    """All runs of one algorithm/problem pair; unsuccessful runs are retained.

    Standard deviations use the population convention (ddof=0). Objective
    statistics include only feasible runs; penalty statistics include every run.
    """

    algorithm: str
    problem: OptimizationProblem
    runs: tuple[ExperimentRun, ...]
    algorithm_parameters: dict[str, Any]
    total_runtime_seconds: float

    @property
    def summary(self) -> dict[str, Any]:
        """Return descriptive statistics without discarding infeasible runs."""
        feasible = [run.result.objective_value for run in self.runs if run.result.is_feasible]
        penalized = [run.result.penalized_cost for run in self.runs]
        evaluations = [run.result.n_evaluations for run in self.runs]
        return {
            "runs": len(self.runs),
            "feasible_runs": len(feasible),
            "feasibility_rate": len(feasible) / len(self.runs),
            "best_feasible_objective": min(feasible) if feasible else None,
            "mean_feasible_objective": statistics.mean(feasible) if feasible else None,
            "std_feasible_objective": statistics.pstdev(feasible) if feasible else None,
            "best_penalized_value": min(penalized),
            "mean_penalized_value": statistics.mean(penalized),
            "std_penalized_value": statistics.pstdev(penalized),
            "std_ddof": 0,
            "objective_evaluation_std": statistics.pstdev(evaluations),
            "mean_runtime_seconds": statistics.mean(run.runtime_seconds for run in self.runs),
            "total_runtime_seconds": self.total_runtime_seconds,
            "mean_objective_evaluations": statistics.mean(evaluations),
            "seed_start": self.runs[0].seed,
            "algorithm_parameters": self.algorithm_parameters,
        }

    def to_dict(self, *, problem_key: str | None = None) -> dict[str, Any]:
        """Return schema v2 metadata, seeds, histories, diagnostics, and summaries.

        User-defined Python objective/constraint functions are not serialized;
        retain their source and dependency versions to replay custom problems.
        """
        key = problem_key if problem_key is not None else self.problem.name
        return {
            "schema_version": 2,
            "algorithm": self.algorithm,
            "problem": key,
            "seeds": [run.seed for run in self.runs],
            "problem_definition": {
                "name": self.problem.name,
                "bounds": [list(bound) for bound in self.problem.bounds],
                "known_optimum": self.problem.known_optimum,
                "known_optimum_x": self.problem.known_optimum_x,
                "penalty": self.problem.penalty,
            },
            "environment": {
                "python": sys.version,
                "platform": platform.platform(),
                "numpy": np.__version__,
                "package": __version__,
                "matplotlib": _optional_version("matplotlib"),
                "seaborn": _optional_version("seaborn"),
            },
            "summary": self.summary,
            "runs": [
                {
                    **asdict(run.result),
                    "seed": run.seed,
                    "algorithm": self.algorithm,
                    "problem": key,
                    "runtime_seconds": run.runtime_seconds,
                    "algorithm_parameters": self.algorithm_parameters,
                }
                for run in self.runs
            ],
        }

    def save(
        self, output_dir: str | Path, *, stem: str = "experiment", problem_key: str | None = None
    ) -> tuple[Path, Path]:
        """Save UTF-8 JSON and CSV; existing files with the same stem are replaced."""
        if (
            not stem
            or Path(stem).name != stem
            or "/" in stem
            or "\\" in stem
            or stem in (".", "..")
        ):
            raise ValueError("stem must be a non-empty filename without directories")
        payload = self.to_dict(problem_key=problem_key)
        # Serialize before opening files so invalid metadata cannot truncate them.
        encoded = json.dumps(payload, indent=2, allow_nan=False) + "\n"
        directory = Path(output_dir)
        directory.mkdir(parents=True, exist_ok=True)
        json_path, csv_path = directory / f"{stem}.json", directory / f"{stem}.csv"
        json_path.write_text(encoded, encoding="utf-8")
        fields = [
            "algorithm",
            "problem",
            "seed",
            "is_feasible",
            "objective_value",
            "penalized_cost",
            "n_evaluations",
            "runtime_seconds",
            "best_x",
        ]
        with csv_path.open("w", encoding="utf-8", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=fields)
            writer.writeheader()
            for record in payload["runs"]:
                writer.writerow(
                    {
                        **{name: record[name] for name in fields if name != "best_x"},
                        "best_x": json.dumps(record["best_x"]),
                    }
                )
        return json_path, csv_path


def run_experiment(
    algorithm: str,
    problem: OptimizationProblem,
    *,
    seeds: Sequence[int],
    optimizer_options: Mapping[str, Any] | None = None,
    run_options: Mapping[str, Any] | None = None,
) -> ExperimentResult:
    """Run a fresh optimizer per seed and retain every result.

    Seeds must be explicit non-negative integers. Options must be JSON values;
    constructor ``seed`` and ``problem`` are reserved. Runs are sequential, so
    objective callbacks need not be pickleable. Reproducibility requires a
    deterministic objective and the same implementation and dependencies.
    """
    if algorithm not in ALGORITHMS:
        raise ValueError(f"Unknown algorithm {algorithm!r}; choose from {sorted(ALGORITHMS)}")
    if not isinstance(problem, OptimizationProblem):
        raise TypeError("problem must be an OptimizationProblem")
    seed_plan = tuple(seeds)
    if not seed_plan:
        raise ValueError("seeds must not be empty")
    for seed in seed_plan:
        require_int("seed", seed)
    constructor = dict(optimizer_options or {})
    if {"seed", "problem"}.intersection(constructor):
        raise ValueError("seed and problem must be passed as experiment arguments")
    run_kwargs = {"verbose": False, **dict(run_options or {})}
    try:
        json.dumps({"constructor": constructor, "run": run_kwargs}, allow_nan=False)
    except (TypeError, ValueError) as exc:
        raise ValueError("Experiment options must be finite JSON values") from exc
    records = []
    parameters = None
    start = time.perf_counter()
    for seed in seed_plan:
        optimizer = ALGORITHMS[algorithm](problem=problem, seed=int(seed), **constructor)
        if parameters is None:
            bound_run = inspect.signature(optimizer.run).bind(**run_kwargs)
            bound_run.apply_defaults()
            parameters = {
                "constructor": {
                    name: value
                    for name, value in vars(optimizer).items()
                    if name not in ("seed", "n_evaluations")
                    and isinstance(value, (str, int, float, bool, type(None)))
                },
                "run": dict(bound_run.arguments),
            }
        run_start = time.perf_counter()
        result = optimizer.run(**run_kwargs)
        records.append(ExperimentRun(int(seed), result, time.perf_counter() - run_start))
    return ExperimentResult(
        algorithm, problem, tuple(records), parameters, time.perf_counter() - start
    )
