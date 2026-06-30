"""Tests for benchmark functions."""
from __future__ import annotations

import pytest

from metaheuristics.benchmarks import (
    BENCHMARKS,
    ackley,
    griewank,
    rastrigin,
    rosenbrock,
    schwefel,
    sphere,
)


class TestSphere:
    def test_at_optimum(self):
        assert sphere([0.0, 0.0]) == pytest.approx(0.0)

    def test_positive_definite(self):
        assert sphere([1.0, -2.0]) > 0

    def test_10d(self):
        assert sphere([0.0] * 10) == pytest.approx(0.0)
        assert sphere([1.0] * 10) == pytest.approx(10.0)


class TestRastrigin:
    def test_at_optimum(self):
        assert rastrigin([0.0, 0.0]) == pytest.approx(0.0)

    def test_away_from_origin(self):
        assert rastrigin([1.0, 1.0]) > 0

    def test_symmetric(self):
        assert rastrigin([1.0, -1.0]) == pytest.approx(rastrigin([-1.0, 1.0]))


class TestAckley:
    def test_at_optimum(self):
        assert ackley([0.0, 0.0]) == pytest.approx(0.0, abs=1e-10)

    def test_positive_away(self):
        assert ackley([1.0, 1.0]) > 0


class TestRosenbrock:
    def test_at_optimum(self):
        assert rosenbrock([1.0, 1.0]) == pytest.approx(0.0)

    def test_at_origin(self):
        # f(0,0) = 1
        assert rosenbrock([0.0, 0.0]) == pytest.approx(1.0)


class TestGriewank:
    def test_at_optimum(self):
        assert griewank([0.0] * 10) == pytest.approx(0.0)

    def test_positive(self):
        assert griewank([100.0] * 10) > 0


class TestSchwefel:
    def test_near_optimum(self):
        val = schwefel([420.9687, 420.9687])
        assert abs(val) < 1.0  # Very close to 0


class TestBenchmarkRegistry:
    def test_registry_not_empty(self):
        assert len(BENCHMARKS) >= 8

    def test_all_entries_have_required_keys(self):
        required = {"name", "func", "bounds", "global_minimum", "optimal_x"}
        for key, entry in BENCHMARKS.items():
            assert required.issubset(entry.keys()), f"Missing keys in {key}"

    def test_all_functions_callable_at_optimum(self):
        for key, entry in BENCHMARKS.items():
            val = entry["func"](entry["optimal_x"])
            assert val == pytest.approx(entry["global_minimum"], abs=1.0), (
                f"{key}: f(x*)={val}, expected {entry['global_minimum']}"
            )

    def test_dimensions_match(self):
        for key, entry in BENCHMARKS.items():
            assert len(entry["bounds"]) == len(entry["optimal_x"]), f"Dim mismatch in {key}"
