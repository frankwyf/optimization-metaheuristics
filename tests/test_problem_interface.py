"""Tests for the generic problem definition and optimizer integration."""
from __future__ import annotations

import pytest

from metaheuristics.algorithms import (
    DifferentialEvolution,
    GeneticAlgorithm,
    ParticleSwarmOptimization,
    SimulatedAnnealing,
)
from metaheuristics.benchmarks import get_benchmark_problem
from metaheuristics.problem import (
    KNOWN_OPTIMUM_X,
    WELDED_BEAM_PROBLEM,
    constraint_violations,
    objective,
    penalized_objective,
)
from metaheuristics.problems import OptimizationProblem


def sphere_problem(dimensions: int = 3) -> OptimizationProblem:
    return OptimizationProblem(
        name=f"sphere_{dimensions}d",
        bounds=tuple([(-5.0, 5.0)] * dimensions),
        objective=lambda x: sum(value * value for value in x),
        known_optimum=0.0,
        known_optimum_x=tuple([0.0] * dimensions),
    )


class TestOptimizationProblem:
    def test_unconstrained_problem_evaluation(self):
        problem = sphere_problem(2)
        evaluation = problem.evaluate([3.0, 4.0])
        assert evaluation.objective_value == 25.0
        assert evaluation.penalized_value == 25.0
        assert evaluation.is_feasible

    def test_constraints_and_bounds_are_included_in_feasibility(self):
        problem = OptimizationProblem(
            name="constrained",
            bounds=((0.0, 1.0),),
            objective=lambda x: x[0],
            constraint_violations=lambda x: (0.5 - x[0],),
            penalty=10.0,
        )
        assert not problem.evaluate([0.25]).is_feasible
        assert problem.evaluate([0.75]).is_feasible
        outside = problem.evaluate([1.5])
        assert not outside.is_feasible
        assert outside.penalized_value > outside.objective_value

    @pytest.mark.parametrize(
        "bounds, known_x",
        [(((0.0, 0.0),), None), (((0.0, 1.0),), (0.5, 0.5))],
    )
    def test_rejects_invalid_bounds_and_optimum_dimension(self, bounds, known_x):
        with pytest.raises(ValueError):
            OptimizationProblem(
                name="invalid",
                bounds=bounds,
                objective=lambda x: x[0],
                known_optimum_x=known_x,
            )

    def test_rejects_wrong_dimension_and_non_finite_values(self):
        problem = sphere_problem(2)
        with pytest.raises(ValueError):
            problem.evaluate([1.0])
        with pytest.raises(ValueError):
            problem.evaluate([1.0, float("nan")])

    def test_benchmark_adapter_preserves_metadata(self):
        problem = get_benchmark_problem("sphere_2d")
        result = problem.evaluate(problem.known_optimum_x)
        assert result.objective_value == pytest.approx(problem.known_optimum)
        assert result.is_feasible

    def test_welded_beam_adapter_preserves_canonical_formulas(self):
        infeasible = [1.5, 1.0, 1.0, 0.1]
        adapted = WELDED_BEAM_PROBLEM.evaluate(infeasible)
        assert adapted.objective_value == objective(infeasible)
        assert adapted.penalized_value == penalized_objective(infeasible)
        assert adapted.violations[-7:] == tuple(constraint_violations(infeasible))
        assert WELDED_BEAM_PROBLEM.evaluate(KNOWN_OPTIMUM_X).is_feasible


@pytest.mark.parametrize(
    "algorithm,kwargs,run_kwargs",
    [
        (GeneticAlgorithm, {"pop_size": 12}, {"max_iteration": 3, "verbose": False}),
        (ParticleSwarmOptimization, {"pop": 12}, {"iterations": 3}),
        (
            SimulatedAnnealing,
            {"t_max": 2.0, "t_min": 0.5, "cooling": 0.5},
            {"samples_per_temperature": 5},
        ),
        (DifferentialEvolution, {"pop_size": 12}, {"max_iterations": 3}),
    ],
)
def test_algorithms_accept_generic_three_dimensional_problem(algorithm, kwargs, run_kwargs):
    result = algorithm(problem=sphere_problem(), seed=17, **kwargs).run(**run_kwargs)
    assert len(result.best_x) == 3
    assert result.is_feasible
    assert result.objective_value == pytest.approx(sum(x * x for x in result.best_x))
    assert result.n_evaluations > 0


def test_optimizer_result_reports_generic_constraint_diagnostics():
    problem = OptimizationProblem(
        name="constrained-sphere",
        bounds=((-1.0, 1.0),) * 2,
        objective=lambda x: sum(value * value for value in x),
        constraint_violations=lambda x: (0.25 - x[0],),
    )
    result = DifferentialEvolution(problem=problem, seed=91, pop_size=12).run(max_iterations=3)
    expected = problem.evaluate(result.best_x)
    assert result.is_feasible == expected.is_feasible
    assert result.objective_value == expected.objective_value
    assert result.penalized_cost == expected.penalized_value
    assert result.constraint_violations == expected.violations
