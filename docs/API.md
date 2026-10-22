# Python API

Install the package in a project-local environment: `python -m pip install .`.
For development use `python -m pip install -e '.[dev,plot]'`; for published wheels,
install the versioned asset from the GitHub Release or PyPI when available.
macOS SSD setup is described in [DEVELOPMENT.md](../DEVELOPMENT.md).

## Problems

```python
from metaheuristics import OptimizationProblem
from metaheuristics.algorithms import DifferentialEvolution

problem = OptimizationProblem(
    name="constrained-sphere",
    bounds=((-5.0, 5.0),) * 3,
    objective=lambda x: sum(value ** 2 for value in x),
    constraint_violations=lambda x: (1.0 - x[0] - x[1],),
)
result = DifferentialEvolution(problem=problem, seed=42, pop_size=40).run(max_iterations=100)
print(result.objective_value, result.is_feasible, result.constraint_violations)
```

Problems minimize a scalar objective. Bounds must have finite endpoints, positive
finite spans, and at least one dimension. Constraint callbacks return values with
`g(x) <= 0` meaning feasible. Evaluation adds
`penalty * sum(max(0, g(x)))` plus bound violations to the raw objective.
Non-finite input, objective, constraint, or penalized values raise `ValueError`.
No feasibility tolerance or objective rescaling is applied implicitly.

The default problem is `metaheuristics.problem.WELDED_BEAM_PROBLEM`. Existing
functions in `metaheuristics.problem` retain the engineering equations.
`get_benchmark_problem("sphere_2d")` in `metaheuristics.benchmarks` adapts the
standard registry; `BENCHMARKS` lists the available keys.

## Optimizers

| Class | Constructor settings | Run settings |
|---|---|---|
| `GeneticAlgorithm` | `pop_size >= 2`, crossover/mutation probabilities in [0,1], positive `stagnation_patience`, `elite_fraction` selecting at least one individual | `max_iteration >= 0`, `verbose` |
| `ParticleSwarmOptimization` | `pop >= 1`, finite non-negative `w`, `c1`, `c2` | `iterations >= 0`, `verbose` |
| `SimulatedAnnealing` | `t_max > t_min > 0`, `0 < cooling < 1` | `samples_per_temperature >= 1`, `verbose` |
| `DifferentialEvolution` | positive `pop_size` (1–3 clamp to 4), `0 <= f <= 2`, `0 <= cr <= 1` | `max_iterations >= 0`, `verbose` |

All accept `problem` and a non-negative integer `seed` (or `None`). Each instance
owns its random generators. Calling `run()` again on the same instance continues
its random stream; create a fresh instance for an exact replay. SA uses uniform
global proposals, rather than a local neighborhood. GA's historical welded-beam
restart thresholds apply only when the default problem is selected implicitly.
The CLI and experiment API pass problems explicitly, so use generic GA restarts.

## Results

`OptimisationResult` includes `best_x`, `objective_value`, `penalized_cost`,
`is_feasible`, `constraint_violations`, `n_evaluations`, `seed`, and `cost_history`.
Selection minimizes the penalized value; a feasible point is not guaranteed.
`best_cost` is the raw objective for feasible results and penalized otherwise.
The evaluation counter counts objective evaluations, including initial candidates;
constraint-only feasibility checks and rejected mutations are not objective calls.

For default settings, histories contain initial best plus each completed
generation, PSO iteration, or SA temperature stage. GA's optional
`history_transform` transforms history values only. These are different work units;
compare evaluation counts and measured time, not history length across algorithms.

## Experiments

```python
from metaheuristics.benchmarks import get_benchmark_problem
from metaheuristics.experiments import run_experiment

experiment = run_experiment(
    "de", get_benchmark_problem("sphere_2d"),
    seeds=list(range(20)),
    optimizer_options={"pop_size": 40},
    run_options={"max_iterations": 100},
)
print(experiment.summary)
experiment.save("results/de-sphere", stem="experiment")
```

`run_experiment` runs a fresh optimizer per supplied seed in order. Constructor
`seed` and `problem` are reserved. Options must be finite JSON values. All runs are
retained; errors propagate and are never converted into a successful result.
The return value exposes `runs` (each with seed, result, and runtime), `summary`,
`to_dict()`, and `save(output_dir, stem=...)`. Saving replaces files with the same
stem; use a different directory or stem to retain previous experiments.

Schema v2 JSON contains environment metadata, problem metadata, actual seeds,
effective settings, summaries, and full per-run histories. CSV contains scalar run
diagnostics and JSON-encoded `best_x`. No plotting packages are imported by this API.
