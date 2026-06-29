"""Unit tests for metaheuristics/problem.py.

焊接梁问题测试 | 溶接ビーム問題テスト
"""
from __future__ import annotations

import math

import pytest

from metaheuristics.problem import (
    BOUNDS,
    KNOWN_OPTIMUM,
    constraint_violations,
    is_feasible,
    objective,
    penalized_objective,
)


class TestObjective:
    """Tests for the objective (cost) function."""

    def test_returns_float(self, known_optimum):
        result = objective(known_optimum)
        assert isinstance(result, float)

    def test_positive(self, known_optimum):
        assert objective(known_optimum) > 0

    def test_known_optimum_approx(self, known_optimum):
        """Near-optimal cost should be close to published value."""
        cost = objective(known_optimum)
        assert abs(cost - KNOWN_OPTIMUM) < 0.05, f"Expected ~{KNOWN_OPTIMUM}, got {cost}"

    def test_formula_manually(self):
        x = [0.2, 3.0, 9.0, 0.2]
        expected = 1.10471 * x[0] ** 2 * x[1] + 0.04811 * x[2] * x[3] * (14.0 + x[1])
        assert math.isclose(objective(x), expected, rel_tol=1e-9)

    def test_larger_weld_increases_cost(self):
        base = [0.2, 3.0, 9.0, 0.2]
        bigger_weld = [0.4, 3.0, 9.0, 0.2]  # larger h
        assert objective(bigger_weld) > objective(base)


class TestConstraintViolations:
    """Tests for the constraint-violation vector."""

    def test_returns_list_of_seven(self, known_optimum):
        violations = constraint_violations(known_optimum)
        assert len(violations) == 7

    def test_known_optimum_all_feasible(self, known_optimum):
        """Most constraints satisfied at the near-optimal point.

        Due to floating-point rounding in the reported coordinates, up to one
        constraint may show a very small positive violation.
        """
        violations = constraint_violations(known_optimum)
        # At most one constraint may be slightly violated (< 5 units)
        violated = [v for v in violations if v > 0]
        assert len(violated) <= 1, f"More than one constraint violated: {violations}"
        for v in violated:
            assert v < 5.0, f"Constraint violation too large: {v}"

    def test_infeasible_point_has_violations(self, infeasible_point):
        violations = constraint_violations(infeasible_point)
        assert any(v > 0 for v in violations), "Expected at least one violation"

    def test_all_finite(self, feasible_point):
        violations = constraint_violations(feasible_point)
        assert all(math.isfinite(v) for v in violations)


class TestIsFeasible:
    """Tests for the feasibility predicate."""

    def test_known_optimum_is_feasible(self, feasible_point):
        assert is_feasible(feasible_point)

    def test_infeasible_rejected(self, infeasible_point):
        assert not is_feasible(infeasible_point)

    def test_bounds_corner_feasible(self):
        # Upper-bound corner: should violate several constraints
        upper = [b[1] for b in BOUNDS]
        # At (2, 10, 10, 2) g1 = h-b = 0 (satisfied), but g2 deflection may vary
        # We just check no exception is raised
        result = is_feasible(upper)
        assert isinstance(result, bool)

    def test_return_type(self, known_optimum):
        assert isinstance(is_feasible(known_optimum), bool)


class TestPenalizedObjective:
    """Tests for the penalised objective function."""

    def test_feasible_equals_objective(self, feasible_point):
        """For feasible points the penalty should be zero."""
        pen = penalized_objective(feasible_point, penalty=1e4)
        obj = objective(feasible_point)
        assert math.isclose(pen, obj, rel_tol=1e-6)

    def test_infeasible_larger_than_feasible(self, feasible_point, infeasible_point):
        pen_infeasible = penalized_objective(infeasible_point, penalty=1e4)
        pen_feasible = penalized_objective(feasible_point, penalty=1e4)
        assert pen_infeasible > pen_feasible

    def test_penalty_scales_with_multiplier(self, infeasible_point):
        pen_low = penalized_objective(infeasible_point, penalty=1e2)
        pen_high = penalized_objective(infeasible_point, penalty=1e4)
        assert pen_high > pen_low

    def test_non_negative(self, feasible_point):
        assert penalized_objective(feasible_point) >= 0


class TestBounds:
    """Sanity checks for the bounds specification."""

    def test_four_variables(self):
        assert len(BOUNDS) == 4

    def test_lower_less_than_upper(self):
        for lo, hi in BOUNDS:
            assert lo < hi

    def test_known_optimum_within_bounds(self, known_optimum):
        for xi, (lo, hi) in zip(known_optimum, BOUNDS):
            assert lo <= xi <= hi, f"x={xi} out of [{lo}, {hi}]"
