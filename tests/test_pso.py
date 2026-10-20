"""Unit and smoke tests for the Particle Swarm Optimisation algorithm.

粒子群优化算法测试 | 粒子群最適化テスト
"""
from __future__ import annotations

import random

import numpy as np

from metaheuristics.algorithms.base import OptimisationResult
from metaheuristics.algorithms.pso import ParticleSwarmOptimization


class TestPSOSmoke:
    """Quick integration tests — tiny swarm and few iterations for CI speed."""

    def test_returns_result_type(self):
        pso = ParticleSwarmOptimization(seed=42, pop=20)
        result = pso.run(iterations=5)
        assert isinstance(result, OptimisationResult)

    def test_result_has_four_design_vars(self):
        pso = ParticleSwarmOptimization(seed=0, pop=20)
        result = pso.run(iterations=5)
        assert len(result.best_x) == 4

    def test_cost_history_length(self):
        pso = ParticleSwarmOptimization(seed=1, pop=20)
        result = pso.run(iterations=5)
        # history includes the initial evaluation → iterations + 1
        assert len(result.cost_history) == 6

    def test_best_cost_positive(self):
        pso = ParticleSwarmOptimization(seed=2, pop=20)
        result = pso.run(iterations=5)
        assert result.best_cost > 0

    def test_reproducible_with_seed(self):
        r1 = ParticleSwarmOptimization(seed=77, pop=20).run(iterations=5)
        r2 = ParticleSwarmOptimization(seed=77, pop=20).run(iterations=5)
        assert r1 == r2

    def test_instances_are_independent_of_run_order(self):
        expected = ParticleSwarmOptimization(seed=77, pop=20).run(iterations=5)
        first = ParticleSwarmOptimization(seed=77, pop=20)
        second = ParticleSwarmOptimization(seed=77, pop=20)

        second.run(iterations=5)
        actual = first.run(iterations=5)

        assert actual == expected

    def test_is_feasible_attribute_is_bool(self):
        pso = ParticleSwarmOptimization(seed=5, pop=20)
        result = pso.run(iterations=5)
        assert isinstance(result.is_feasible, bool)


class TestPSOHyperparams:
    """Tests that different hyperparameter combinations run without error."""

    def test_large_population(self):
        pso = ParticleSwarmOptimization(seed=10, pop=100)
        result = pso.run(iterations=3)
        assert result.best_cost > 0

    def test_custom_weights(self):
        pso = ParticleSwarmOptimization(seed=11, pop=20, w=0.7, c1=2.0, c2=2.0)
        result = pso.run(iterations=5)
        assert len(result.best_x) == 4

    def test_verbose_does_not_crash(self, capsys):
        pso = ParticleSwarmOptimization(seed=13, pop=10)
        pso.run(iterations=3, verbose=True)
        captured = capsys.readouterr()
        assert "[PSO]" in captured.out

    def test_gbest_improves_or_stays(self):
        """Global best should never get worse as iterations increase."""
        pso = ParticleSwarmOptimization(seed=20, pop=30)
        result = pso.run(iterations=10)
        history = result.cost_history
        for i in range(1, len(history)):
            assert history[i] <= history[i - 1] + 1e-9, (
                f"Global best worsened at step {i}: {history[i-1]} → {history[i]}"
            )

    def test_does_not_pollute_global_random_generators(self):
        original_python_state = random.getstate()
        original_numpy_state = np.random.get_state()

        try:
            random.seed(101)
            np.random.seed(202)
            python_state = random.getstate()
            numpy_state = np.random.get_state()

            pso = ParticleSwarmOptimization(seed=303, pop=20)

            python_unchanged = random.getstate() == python_state
            numpy_unchanged = _numpy_state_equal(np.random.get_state(), numpy_state)
            assert python_unchanged and numpy_unchanged, (
                f"after construction: Python unchanged={python_unchanged}, "
                f"NumPy unchanged={numpy_unchanged}"
            )

            pso.run(iterations=5)

            python_unchanged = random.getstate() == python_state
            numpy_unchanged = _numpy_state_equal(np.random.get_state(), numpy_state)
            assert python_unchanged and numpy_unchanged, (
                f"after run: Python unchanged={python_unchanged}, "
                f"NumPy unchanged={numpy_unchanged}"
            )
        finally:
            random.setstate(original_python_state)
            np.random.set_state(original_numpy_state)


def _numpy_state_equal(actual: tuple, expected: tuple) -> bool:
    return (
        actual[0] == expected[0]
        and np.array_equal(actual[1], expected[1])
        and actual[2:] == expected[2:]
    )
