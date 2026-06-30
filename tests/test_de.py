"""Tests for the Differential Evolution algorithm."""
from __future__ import annotations

import pytest

from metaheuristics.algorithms.de import DifferentialEvolution


class TestDESmoke:
    """Basic smoke tests for DifferentialEvolution."""

    def test_returns_result(self):
        de = DifferentialEvolution(seed=42, pop_size=20)
        result = de.run(max_iterations=10)
        assert result.best_x is not None
        assert len(result.best_x) == 4
        assert result.best_cost > 0

    def test_cost_history_recorded(self):
        de = DifferentialEvolution(seed=99, pop_size=20)
        result = de.run(max_iterations=15)
        # initial + 15 iterations = 16 entries
        assert len(result.cost_history) == 16

    def test_cost_decreases_monotonically(self):
        de = DifferentialEvolution(seed=7, pop_size=30)
        result = de.run(max_iterations=20)
        for i in range(1, len(result.cost_history)):
            assert result.cost_history[i] <= result.cost_history[i - 1]

    def test_deterministic_with_seed(self):
        r1 = DifferentialEvolution(seed=123, pop_size=20).run(max_iterations=10)
        r2 = DifferentialEvolution(seed=123, pop_size=20).run(max_iterations=10)
        assert r1.best_cost == r2.best_cost
        assert r1.best_x == r2.best_x

    def test_verbose_no_crash(self, capsys):
        de = DifferentialEvolution(seed=1, pop_size=10)
        de.run(max_iterations=3, verbose=True)
        captured = capsys.readouterr()
        assert "[DE]" in captured.out

    def test_larger_population(self):
        de = DifferentialEvolution(seed=42, pop_size=50)
        result = de.run(max_iterations=50)
        assert result.best_cost < 100  # should find something reasonable


class TestDEHyperparams:
    """Test hyperparameter variations."""

    @pytest.mark.parametrize("f", [0.3, 0.8, 1.5])
    def test_mutation_factor(self, f):
        de = DifferentialEvolution(seed=42, pop_size=20, f=f)
        result = de.run(max_iterations=10)
        assert result.best_cost > 0

    @pytest.mark.parametrize("cr", [0.1, 0.5, 0.9])
    def test_crossover_rate(self, cr):
        de = DifferentialEvolution(seed=42, pop_size=20, cr=cr)
        result = de.run(max_iterations=10)
        assert result.best_cost > 0

    def test_minimum_pop_size(self):
        # pop_size < 4 should be clamped to 4
        de = DifferentialEvolution(seed=42, pop_size=2)
        assert de.pop_size == 4
        result = de.run(max_iterations=5)
        assert result.best_cost > 0
