"""Welded-beam design problem — canonical single-source definition.

The welded beam is a classic 4-variable, 7-constraint cost-minimisation
benchmark (Deb 1991) widely used to compare metaheuristic algorithms.

Variable layout (0-indexed)
---------------------------
x[0]  weld height  h  ∈ [0.1, 2.0]  in
x[1]  weld length  l  ∈ [0.1, 10.0] in
x[2]  bar height   t  ∈ [0.1, 10.0] in
x[3]  bar thickness b  ∈ [0.1, 2.0]  in

References
----------
Deb, K. (1991). Optimal design of a welded beam via genetic algorithms.
AIAA Journal, 29(11), 2013-2015.

焊接梁设计问题 — 规范单一定义（Deb 1991）。

溶接ビーム設計問題 — 正規の単一ソース定義（Deb 1991）。
"""
from __future__ import annotations

import math
from typing import Sequence

# ---------------------------------------------------------------------------
# Search-space bounds: [(lower, upper), ...]
# ---------------------------------------------------------------------------
BOUNDS: list[tuple[float, float]] = [
    (0.1, 2.0),   # x[0]: weld height h
    (0.1, 10.0),  # x[1]: weld length l
    (0.1, 10.0),  # x[2]: bar height  t
    (0.1, 2.0),   # x[3]: bar thickness b
]

# ---------------------------------------------------------------------------
# Physical constants (imperial units)
# ---------------------------------------------------------------------------
_P: float = 6_000.0   # Applied load           (lb)
_L: float = 14.0      # Beam length             (in)
_E: float = 30e6      # Young's modulus         (psi)
_G_EFF: float = 48e6  # Effective shear modulus used in buckling formula (psi)
_TAU_MAX: float = 13_600.0  # Max allowable shear stress  (psi)
_SIGMA_MAX: float = 30_000.0  # Max allowable normal stress (psi)
_DELTA_MAX: float = 0.25  # Max allowable deflection    (in)

# Near-optimal reference value from literature
KNOWN_OPTIMUM: float = 1.7248


# ---------------------------------------------------------------------------
# Objective function
# ---------------------------------------------------------------------------
def objective(x: Sequence[float]) -> float:
    """Fabrication cost — the quantity to minimise.

    製造コスト — 最小化する目的関数。
    制造成本 — 最小化目标函数。

    Parameters
    ----------
    x:
        Design vector [h, l, t, b].

    Returns
    -------
    float
        Fabrication cost (dimensionless cost expression).
    """
    return 1.10471 * x[0] ** 2 * x[1] + 0.04811 * x[2] * x[3] * (14.0 + x[1])


# ---------------------------------------------------------------------------
# Internal engineering quantities
# ---------------------------------------------------------------------------
def _shear_stress(x: Sequence[float]) -> float:
    """Combined shear stress at the weld (psi)."""
    r = math.sqrt(x[1] ** 2 / 4.0 + ((x[0] + x[2]) / 2.0) ** 2)
    m = _P * (x[1] / 2.0 + _L)
    j = 2.0 * math.sqrt(2.0) * x[0] * x[1] * (x[1] ** 2 / 12.0 + ((x[0] + x[2]) / 2.0) ** 2)
    tau_primary = _P / (math.sqrt(2.0) * x[0] * x[1])
    tau_secondary = m * r / j
    return math.sqrt(
        tau_primary ** 2
        + tau_secondary ** 2
        + 2.0 * tau_primary * tau_secondary * x[1] / (2.0 * r)
    )


def _deflection(x: Sequence[float]) -> float:
    """End deflection of the beam (in)."""
    return 2.1952 / (x[2] ** 3 * x[3])  # = 4PL³/(Et³b)


def _buckling_load(x: Sequence[float]) -> float:
    """Critical buckling load of the beam (lb)."""
    return (4.013 * _E * x[2] * x[3] ** 3 / (6.0 * _L ** 2)) * (
        1.0 - x[2] / (2.0 * _L) * math.sqrt(_E / _G_EFF)
    )


def _normal_stress(x: Sequence[float]) -> float:
    """Normal (bending) stress at the loaded end (psi)."""
    return 504_000.0 / (x[3] * x[2] ** 2)  # = 6PL/(bt²)


# ---------------------------------------------------------------------------
# Constraint functions
# ---------------------------------------------------------------------------
def constraint_violations(x: Sequence[float]) -> list[float]:
    """Per-constraint violation amounts.

    Convention: value ≤ 0 means the constraint is satisfied;
    positive value indicates the degree of violation.

    各制約違反量。
    各约束违反量。

    Parameters
    ----------
    x:
        Design vector [h, l, t, b].

    Returns
    -------
    list[float]
        Seven violation values [g1, g2, g3, g4, g5, g6, g7].
    """
    return [
        x[0] - x[3],                    # g1: h ≤ b  (weld height ≤ bar thickness)
        _deflection(x) - _DELTA_MAX,    # g2: δ ≤ 0.25 in
        _P - _buckling_load(x),         # g3: Pcr ≥ P  (no buckling)
        _shear_stress(x) - _TAU_MAX,    # g4: τ ≤ 13 600 psi
        _normal_stress(x) - _SIGMA_MAX, # g5: σ ≤ 30 000 psi
        0.125 - x[0],                   # g6: h ≥ 0.125 in
        objective(x) - 5.0,             # g7: cost ≤ 5
    ]


def is_feasible(x: Sequence[float]) -> bool:
    """Return True if *x* satisfies all seven constraints.

    すべての制約が満たされていれば True を返す。
    如果满足所有七个约束，则返回 True。

    Parameters
    ----------
    x:
        Design vector [h, l, t, b].
    """
    return all(v <= 0.0 for v in constraint_violations(x))


def penalized_objective(x: Sequence[float], penalty: float = 1e4) -> float:
    """Objective value augmented with a proportional constraint penalty.

    Used internally by optimisers to guide search toward the feasible region.

    目的関数値に比例した制約ペナルティを加算したもの。
    目标函数值加上比例约束惩罚项。

    Parameters
    ----------
    x:
        Design vector [h, l, t, b].
    penalty:
        Penalty multiplier applied to the sum of positive violations.
    """
    cost = objective(x)
    total_penalty = sum(max(0.0, v) for v in constraint_violations(x)) * penalty
    return cost + total_penalty
