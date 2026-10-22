"""Experiments must be replayable, honestly summarized, and usable without plots."""

from __future__ import annotations

import csv
import json

import pytest

from metaheuristics.benchmarks import get_benchmark_problem
from metaheuristics.problems import OptimizationProblem


def test_explicit_seed_sequence_can_be_replayed(tmp_path):
    from metaheuristics.experiments import run_experiment

    kwargs = dict(
        algorithm="de",
        problem=get_benchmark_problem("sphere_2d"),
        seeds=[7, 2, 19],
        optimizer_options={"pop_size": 8},
        run_options={"max_iterations": 3},
    )
    first = run_experiment(**kwargs)
    second = run_experiment(**kwargs)
    assert [run.seed for run in first.runs] == [7, 2, 19]
    assert [run.result for run in first.runs] == [run.result for run in second.runs]
    assert first.summary["runs"] == 3
    assert first.summary["feasibility_rate"] == 1.0
    assert first.summary["std_ddof"] == 0
    assert first.summary["algorithm_parameters"]["constructor"]["pop_size"] == 8
    assert first.summary["algorithm_parameters"]["run"]["max_iterations"] == 3
    json_path, csv_path = first.save(tmp_path, stem="trial")
    payload = json.loads(json_path.read_text(encoding="utf-8"))
    assert payload["schema_version"] == 2
    assert payload["seeds"] == [7, 2, 19]
    assert payload["environment"]["package"]
    assert all(run["n_evaluations"] == 32 for run in payload["runs"])
    with csv_path.open(encoding="utf-8", newline="") as handle:
        assert [int(row["seed"]) for row in csv.DictReader(handle)] == [7, 2, 19]


def test_all_infeasible_runs_are_retained_with_null_feasible_stats():
    from metaheuristics.experiments import run_experiment

    problem = OptimizationProblem(
        name="impossible",
        bounds=((0.0, 1.0),),
        objective=lambda x: x[0],
        constraint_violations=lambda x: (1.0,),
    )
    experiment = run_experiment(
        "de",
        problem,
        seeds=[0, 1],
        optimizer_options={"pop_size": 4},
        run_options={"max_iterations": 0},
    )
    assert len(experiment.runs) == 2
    assert experiment.summary["feasibility_rate"] == 0.0
    assert experiment.summary["mean_feasible_objective"] is None
    assert experiment.summary["std_feasible_objective"] is None
    json.dumps(experiment.to_dict(), allow_nan=False)


def test_finite_large_objectives_do_not_overflow_summary():
    from metaheuristics.experiments import run_experiment

    problem = OptimizationProblem(name="large", bounds=((0.0, 1.0),), objective=lambda x: 1e308)
    experiment = run_experiment(
        "de",
        problem,
        seeds=[1, 2, 3],
        optimizer_options={"pop_size": 4},
        run_options={"max_iterations": 0},
    )
    assert experiment.summary["mean_feasible_objective"] == 1e308
    assert experiment.summary["std_feasible_objective"] == 0.0
    json.dumps(experiment.to_dict(), allow_nan=False)


@pytest.mark.parametrize("seeds", [[], [-1], [True], [1.5]])
def test_invalid_seed_plan_is_rejected(seeds):
    from metaheuristics.experiments import run_experiment

    with pytest.raises(ValueError, match="seed"):
        run_experiment("de", get_benchmark_problem("sphere_2d"), seeds=seeds)


def test_cannot_override_problem_or_seed_through_options():
    from metaheuristics.experiments import run_experiment

    with pytest.raises(ValueError, match="seed.*problem"):
        run_experiment(
            "de", get_benchmark_problem("sphere_2d"), seeds=[0], optimizer_options={"seed": 8}
        )
