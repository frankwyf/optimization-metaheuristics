"""Small shared validators for public numerical parameters."""

from __future__ import annotations

import math
from numbers import Integral, Real


def require_int(name: str, value: int, minimum: int = 0) -> None:
    """Require a non-boolean integer greater than or equal to a minimum."""
    if isinstance(value, bool) or not isinstance(value, Integral) or value < minimum:
        raise ValueError(f"{name} must be an integer >= {minimum}")


def require_real(name: str, value: float, minimum: float = 0.0, maximum: float = math.inf) -> None:
    """Require a finite real parameter in an inclusive range."""
    if (
        isinstance(value, bool)
        or not isinstance(value, Real)
        or not math.isfinite(value)
        or not minimum <= value <= maximum
    ):
        raise ValueError(f"{name} must be finite and in [{minimum}, {maximum}]")
