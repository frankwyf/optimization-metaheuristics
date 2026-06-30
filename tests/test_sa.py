"""Unit and smoke tests for the Simulated Annealing algorithm.

模拟退火算法测试 | シミュレーテッド・アニーリングテスト
"""
from __future__ import annotations

import pytest

from metaheuristics.algorithms.base import OptimisationResult
from metaheuristics.algorithms.sa import SimulatedAnnealing


class TestSimulatedAnnealingSmoke:
    """Quick integration tests — small iteration counts for CI speed."""

    def test_returns_result_type(self):
        sa = SimulatedAnnealing(seed=42)
        result = sa.run(samples_per_temperature=200)
        assert isinstance(result, OptimisationResult)

    def test_result_has_four_design_vars(self):
        sa = SimulatedAnnealing(seed=0)
        result = sa.run(samples_per_temperature=200)
        assert len(result.best_x) == 4

    def test_cost_history_non_empty(self):
        sa = SimulatedAnnealing(seed=1)
        result = sa.run(samples_per_temperature=200)
        assert len(result.cost_history) > 0

    def test_best_cost_positive(self):
        sa = SimulatedAnnealing(seed=2)
        result = sa.run(samples_per_temperature=200)
        assert result.best_cost > 0

    def test_reproducible_with_seed(self):
        r1 = SimulatedAnnealing(seed=99).run(samples_per_temperature=200)
        r2 = SimulatedAnnealing(seed=99).run(samples_per_temperature=200)
        assert r1.best_cost == pytest.approx(r2.best_cost, rel=1e-6)

    def test_is_feasible_attribute_is_bool(self):
        sa = SimulatedAnnealing(seed=7)
        result = sa.run(samples_per_temperature=200)
        assert isinstance(result.is_feasible, bool)


class TestSimulatedAnnealingHyperparams:
    """Tests that hyperparameter variations do not crash and produce valid output."""

    def test_higher_temperature_range(self):
        sa = SimulatedAnnealing(seed=10, t_max=50.0, t_min=0.1)
        result = sa.run(samples_per_temperature=100)
        assert result.best_cost > 0

    def test_fast_cooling(self):
        sa = SimulatedAnnealing(seed=11, cooling=0.1)
        result = sa.run(samples_per_temperature=100)
        assert len(result.cost_history) > 0

    def test_slow_cooling(self):
        sa = SimulatedAnnealing(seed=12, cooling=0.9)
        result = sa.run(samples_per_temperature=50)
        assert result.best_cost > 0

    def test_verbose_does_not_crash(self, capsys):
        sa = SimulatedAnnealing(seed=13)
        sa.run(samples_per_temperature=100, verbose=True)
        captured = capsys.readouterr()
        assert "[SA]" in captured.out
