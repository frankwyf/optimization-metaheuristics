"""Reusable continuous optimization problem definitions."""
from __future__ import annotations

import math
from collections.abc import Callable, Sequence
from dataclasses import dataclass

Objective = Callable[[Sequence[float]], float]
ConstraintViolations = Callable[[Sequence[float]], Sequence[float]]


@dataclass(frozen=True)
class ProblemEvaluation:
    """Objective and constraint evaluation at one candidate point."""

    objective_value: float
    penalized_value: float
    is_feasible: bool
    violations: tuple[float, ...]


@dataclass(frozen=True)
class OptimizationProblem:
    """A bounded minimization problem with optional inequality constraints.

    Constraint values follow the convention ``g(x) <= 0`` for feasible points.
    Bounds are enforced by this type in addition to the supplied constraints.
    """

    name: str
    bounds: Sequence[tuple[float, float]]
    objective: Objective
    constraint_violations: ConstraintViolations | None = None
    known_optimum: float | None = None
    known_optimum_x: Sequence[float] | None = None
    penalty: float = 1e4

    def __post_init__(self) -> None:
        normalized_bounds = tuple((float(lo), float(hi)) for lo, hi in self.bounds)
        if not self.name.strip():
            raise ValueError("Problem name must not be empty")
        if not normalized_bounds:
            raise ValueError("Problem must define at least one dimension")
        if any(not math.isfinite(lo) or not math.isfinite(hi) or lo >= hi for lo, hi in normalized_bounds):
            raise ValueError("Each bound must contain finite values with lower < upper")
        if any(not math.isfinite(hi - lo) for lo, hi in normalized_bounds):
            raise ValueError("Each bound span must be finite")
        if not callable(self.objective):
            raise TypeError("objective must be callable")
        if self.constraint_violations is not None and not callable(self.constraint_violations):
            raise TypeError("constraint_violations must be callable or None")
        if not math.isfinite(self.penalty) or self.penalty < 0:
            raise ValueError("penalty must be finite and non-negative")
        if self.known_optimum is not None and not math.isfinite(self.known_optimum):
            raise ValueError("known_optimum must be finite or None")
        if self.known_optimum_x is not None:
            optimum_x = tuple(float(value) for value in self.known_optimum_x)
            if len(optimum_x) != len(normalized_bounds):
                raise ValueError("known_optimum_x dimension must match bounds")
            if not all(math.isfinite(value) for value in optimum_x):
                raise ValueError("known_optimum_x must contain only finite values")
            if any(
                not lo <= value <= hi
                for value, (lo, hi) in zip(optimum_x, normalized_bounds)
            ):
                raise ValueError("known_optimum_x must lie within the problem bounds")
            object.__setattr__(self, "known_optimum_x", optimum_x)
        object.__setattr__(self, "bounds", normalized_bounds)

    @property
    def dimension(self) -> int:
        """Number of decision variables."""
        return len(self.bounds)

    def _point(self, x: Sequence[float]) -> tuple[float, ...]:
        point = tuple(float(value) for value in x)
        if len(point) != self.dimension:
            raise ValueError(f"Expected {self.dimension} variables, received {len(point)}")
        if not all(math.isfinite(value) for value in point):
            raise ValueError("Candidate point must contain only finite values")
        return point

    def violations(self, x: Sequence[float]) -> tuple[float, ...]:
        """Return bound and problem constraint violations; feasible values are <= 0."""
        point = self._point(x)
        bound_violations = tuple(
            max(lo - value, value - hi, 0.0) for value, (lo, hi) in zip(point, self.bounds)
        )
        constraints = (
            tuple(float(value) for value in self.constraint_violations(point))
            if self.constraint_violations is not None
            else ()
        )
        if not all(math.isfinite(value) for value in constraints):
            raise ValueError("Constraint violations must be finite")
        return bound_violations + constraints

    def is_feasible(self, x: Sequence[float]) -> bool:
        """Return whether bounds and all supplied constraints are satisfied."""
        return all(value <= 0.0 for value in self.violations(x))

    def evaluate(self, x: Sequence[float]) -> ProblemEvaluation:
        """Evaluate objective and proportional positive-violation penalty."""
        point = self._point(x)
        value = float(self.objective(point))
        if not math.isfinite(value):
            raise ValueError("Objective value must be finite")
        violations = self.violations(point)
        feasible = all(violation <= 0.0 for violation in violations)
        total_violation = 0.0
        for violation in violations:
            total_violation += max(0.0, violation)
            if not math.isfinite(total_violation):
                raise ValueError("Constraint penalty must be finite")
        penalty = total_violation * self.penalty
        if not math.isfinite(penalty):
            raise ValueError("Constraint penalty must be finite")
        penalized_value = value + penalty
        if not math.isfinite(penalized_value):
            raise ValueError("Penalized objective value must be finite")
        return ProblemEvaluation(
            objective_value=value,
            penalized_value=penalized_value,
            is_feasible=feasible,
            violations=violations,
        )
