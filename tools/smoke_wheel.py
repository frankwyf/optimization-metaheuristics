"""Run with ``python -I`` after installing a wheel, outside editable imports."""

from __future__ import annotations

import importlib.util
from pathlib import Path

import metaheuristics
from metaheuristics.benchmarks import get_benchmark_problem
from metaheuristics.experiments import run_experiment
from scripts.run import main

source_root = Path(__file__).resolve().parents[1]
assert not Path(metaheuristics.__file__).resolve().is_relative_to(source_root / "metaheuristics")
assert Path(metaheuristics.__file__).with_name("py.typed").is_file()
assert main(["--list"]) == 0
for algorithm, constructor, options in (
    ("ga", {"pop_size": 4}, {"max_iteration": 2}),
    ("pso", {"pop": 4}, {"iterations": 2}),
    ("de", {"pop_size": 4}, {"max_iterations": 2}),
    ("sa", {"t_max": 2.0, "t_min": 1.0}, {"samples_per_temperature": 2}),
):
    result = run_experiment(
        algorithm,
        get_benchmark_problem("sphere_2d"),
        seeds=[7, 13],
        optimizer_options=constructor,
        run_options=options,
    )
    assert len(result.runs) == 2 and result.summary["feasibility_rate"] == 1.0
print(f"Installed wheel OK: {metaheuristics.__version__}, {metaheuristics.__file__}")
print(f"Plotting installed: {importlib.util.find_spec('matplotlib') is not None}")
