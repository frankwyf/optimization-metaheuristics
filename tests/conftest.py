"""Shared fixtures for the test suite."""
from __future__ import annotations

import pytest


@pytest.fixture
def known_optimum() -> list[float]:
    """Near-optimal design vector (from general.py __main__), cost ≈ 1.724.

    Note: due to floating-point rounding this point may sit very slightly
    outside the feasible region for g5 (bending stress).  Tests that require
    strict feasibility should use *feasible_point* instead.
    """
    return [0.205986, 3.471328, 9.020224, 0.206480]


@pytest.fixture
def infeasible_point() -> list[float]:
    """A clearly infeasible design vector (all variables at lower bound)."""
    return [0.1, 0.1, 0.1, 0.1]


@pytest.fixture
def feasible_point() -> list[float]:
    """A strictly feasible design vector (verified against all 7 constraints).

    h=0.25, l=6.0, t=8.5, b=0.25 → cost ≈ 2.46, all constraints satisfied.
    """
    return [0.25, 6.0, 8.5, 0.25]
