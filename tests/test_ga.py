"""Unit and smoke tests for the Genetic Algorithm.

遗传算法测试 | 遺伝的アルゴリズムテスト
"""
from __future__ import annotations

import pytest

from metaheuristics.algorithms.base import OptimisationResult
from metaheuristics.algorithms.ga import GeneticAlgorithm, _Individual


class TestIndividual:
    """Unit tests for the binary-encoded Individual class."""

    def test_randomize_sets_chromosome(self):
        ind = _Individual()
        ind.randomize()
        assert len(ind.chromosome) == 64 * 4
        assert set(ind.chromosome).issubset({"0", "1"})

    def test_decode_returns_four_floats(self):
        ind = _Individual()
        ind.randomize()
        x = ind.decode()
        assert len(x) == 4
        assert all(isinstance(v, float) for v in x)

    def test_decode_within_bounds(self):
        from metaheuristics.problem import BOUNDS

        for _ in range(10):
            ind = _Individual()
            ind.randomize()
            for xi, (lo, hi) in zip(ind.decode(), BOUNDS):
                assert lo <= xi <= hi

    def test_crossover_produces_two_chromosomes(self):
        p1, p2 = _Individual(), _Individual()
        p1.randomize()
        p2.randomize()
        c1, c2 = p1.crossover(p2)
        assert len(c1) == len(p1.chromosome)
        assert len(c2) == len(p2.chromosome)

    def test_fitness_returns_float(self):
        ind = _Individual()
        ind.randomize()
        f = ind.fitness()
        assert isinstance(f, float)


class TestGASmoke:
    """Quick integration tests — very few generations for CI speed."""

    def test_returns_result_type(self):
        ga = GeneticAlgorithm(seed=42, pop_size=30)
        result = ga.run(max_iteration=5, verbose=False)
        assert isinstance(result, OptimisationResult)

    def test_result_has_four_design_vars(self):
        ga = GeneticAlgorithm(seed=0, pop_size=30)
        result = ga.run(max_iteration=5, verbose=False)
        assert len(result.best_x) == 4

    def test_cost_history_non_empty(self):
        ga = GeneticAlgorithm(seed=1, pop_size=30)
        result = ga.run(max_iteration=5, verbose=False)
        assert len(result.cost_history) > 0

    def test_cost_history_monotone(self):
        """Best cost should never increase between recorded generations."""
        ga = GeneticAlgorithm(seed=3, pop_size=40)
        result = ga.run(max_iteration=20, verbose=False)
        for i in range(1, len(result.cost_history)):
            assert result.cost_history[i] <= result.cost_history[i - 1] + 1e-9

    def test_best_cost_positive(self):
        ga = GeneticAlgorithm(seed=2, pop_size=30)
        result = ga.run(max_iteration=5, verbose=False)
        assert result.best_cost > 0

    def test_reproducible_with_seed(self):
        r1 = GeneticAlgorithm(seed=55, pop_size=30).run(max_iteration=5, verbose=False)
        r2 = GeneticAlgorithm(seed=55, pop_size=30).run(max_iteration=5, verbose=False)
        assert r1.best_cost == pytest.approx(r2.best_cost, rel=1e-6)

    def test_is_feasible_attribute_is_bool(self):
        ga = GeneticAlgorithm(seed=5, pop_size=30)
        result = ga.run(max_iteration=5, verbose=False)
        assert isinstance(result.is_feasible, bool)

    def test_verbose_does_not_crash(self, capsys):
        ga = GeneticAlgorithm(seed=6, pop_size=30)
        ga.run(max_iteration=60, verbose=True)
        captured = capsys.readouterr()
        assert "[GA]" in captured.out


class TestGAHyperparams:
    """Tests for different hyperparameter combinations."""

    def test_high_crossover_prob(self):
        ga = GeneticAlgorithm(seed=10, pop_size=20, crossover_prob=1.0)
        result = ga.run(max_iteration=3, verbose=False)
        assert result.best_cost > 0

    def test_low_mutation_prob(self):
        ga = GeneticAlgorithm(seed=11, pop_size=20, mutation_prob=0.01)
        result = ga.run(max_iteration=3, verbose=False)
        assert len(result.best_x) == 4

    def test_large_population(self):
        ga = GeneticAlgorithm(seed=12, pop_size=100)
        result = ga.run(max_iteration=3, verbose=False)
        assert result.best_cost > 0
