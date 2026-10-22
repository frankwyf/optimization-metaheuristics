"""Behavioral regressions for public optimizer inputs and best-so-far results."""

from __future__ import annotations

from types import SimpleNamespace

import pytest

from metaheuristics.algorithms import (
    DifferentialEvolution,
    GeneticAlgorithm,
    ParticleSwarmOptimization,
    SimulatedAnnealing,
)
from metaheuristics.algorithms.ga import _Individual
from metaheuristics.problems import OptimizationProblem


@pytest.fixture
def linear_problem():
    return OptimizationProblem(name="linear", bounds=((0.0, 1.0),), objective=lambda x: x[0])


def test_sa_keeps_best_when_a_worse_state_is_accepted(monkeypatch, linear_problem):
    sa = SimulatedAnnealing(problem=linear_problem, seed=7, t_max=2.0, t_min=1.0)
    candidates = iter(([0.1], [0.2]))
    monkeypatch.setattr(sa, "_random_point", lambda: [0.5])
    monkeypatch.setattr(sa, "_neighbour", lambda: next(candidates))
    monkeypatch.setattr(sa, "_rng", SimpleNamespace(random=lambda: 0.0))

    result = sa.run(samples_per_temperature=2)

    assert result.best_x == [0.1]
    assert result.objective_value == 0.1
    assert result.penalized_cost == 0.1
    assert result.cost_history == [0.5, 0.1]
    assert result.n_evaluations == 3


def test_ga_includes_improvement_in_last_generation(monkeypatch, linear_problem):
    ga = GeneticAlgorithm(problem=linear_problem, seed=7, pop_size=4)
    monkeypatch.setattr(
        ga,
        "_selection",
        lambda population, fitnesses: [
            _Individual(bounds=tuple(linear_problem.bounds)) for _ in population
        ],
    )

    result = ga.run(max_iteration=1, verbose=False)

    assert result.best_x == [0.0]
    assert result.penalized_cost == 0.0
    assert len(result.cost_history) == 2
    assert result.cost_history[-1] == result.penalized_cost


@pytest.mark.parametrize(
    "algorithm",
    [GeneticAlgorithm, ParticleSwarmOptimization, SimulatedAnnealing, DifferentialEvolution],
)
@pytest.mark.parametrize("seed", [-1, 1.5, True])
def test_rejects_invalid_seed(algorithm, seed):
    with pytest.raises(ValueError, match="seed"):
        algorithm(seed=seed)


@pytest.mark.parametrize(
    "algorithm, options, name",
    [
        (GeneticAlgorithm, {"pop_size": 2.5}, "pop_size"),
        (GeneticAlgorithm, {"crossover_prob": -0.1}, "crossover_prob"),
        (GeneticAlgorithm, {"mutation_prob": float("nan")}, "mutation_prob"),
        (GeneticAlgorithm, {"stagnation_patience": 0}, "stagnation_patience"),
        (ParticleSwarmOptimization, {"pop": 0}, "pop"),
        (ParticleSwarmOptimization, {"pop": True}, "pop"),
        (ParticleSwarmOptimization, {"w": float("inf")}, "w"),
        (ParticleSwarmOptimization, {"c1": -1.0}, "c1"),
        (ParticleSwarmOptimization, {"c2": float("nan")}, "c2"),
        (DifferentialEvolution, {"pop_size": 0}, "pop_size"),
        (DifferentialEvolution, {"f": 2.1}, "f"),
        (DifferentialEvolution, {"cr": -0.1}, "cr"),
        (SimulatedAnnealing, {"t_max": float("inf")}, "t_max"),
        (SimulatedAnnealing, {"t_min": 0.0}, "t_min"),
        (SimulatedAnnealing, {"t_max": 1.0, "t_min": 2.0}, "t_max"),
        (SimulatedAnnealing, {"cooling": 1.0}, "cooling"),
        (SimulatedAnnealing, {"cooling": 0.0}, "cooling"),
    ],
)
def test_invalid_constructor_options_fail_immediately(algorithm, options, name):
    with pytest.raises(ValueError, match=name):
        algorithm(**options)


@pytest.mark.parametrize(
    "optimizer, options, name",
    [
        (lambda p: GeneticAlgorithm(problem=p, pop_size=4), {"max_iteration": -1}, "max_iteration"),
        (lambda p: ParticleSwarmOptimization(problem=p, pop=4), {"iterations": 1.5}, "iterations"),
        (
            lambda p: DifferentialEvolution(problem=p, pop_size=4),
            {"max_iterations": -1},
            "max_iterations",
        ),
        (
            lambda p: SimulatedAnnealing(problem=p),
            {"samples_per_temperature": 0},
            "samples_per_temperature",
        ),
    ],
)
def test_invalid_run_options_fail_before_evaluation(optimizer, options, name, linear_problem):
    instance = optimizer(linear_problem)
    with pytest.raises(ValueError, match=name):
        instance.run(**options)
    assert instance.n_evaluations == 0


@pytest.mark.parametrize(
    "algorithm, constructor, options",
    [
        (GeneticAlgorithm, {"pop_size": 4}, {"max_iteration": 0, "verbose": False}),
        (ParticleSwarmOptimization, {"pop": 4}, {"iterations": 0}),
        (DifferentialEvolution, {"pop_size": 4}, {"max_iterations": 0}),
    ],
)
def test_zero_iterations_returns_initial_best(algorithm, constructor, options, linear_problem):
    result = algorithm(problem=linear_problem, seed=7, **constructor).run(**options)
    assert result.n_evaluations == 4
    assert result.cost_history == [result.penalized_cost]


def test_bounds_reject_non_finite_span():
    with pytest.raises(ValueError, match="span"):
        OptimizationProblem(name="wide", bounds=((-1e308, 1e308),), objective=lambda x: 0.0)


def test_sa_rejects_cooling_that_stalls_at_subnormal_precision(linear_problem):
    sa = SimulatedAnnealing(problem=linear_problem, seed=7, t_max=1e-323, t_min=5e-324, cooling=0.9)
    with pytest.raises(ValueError, match="floating-point precision"):
        sa.run(samples_per_temperature=1)
