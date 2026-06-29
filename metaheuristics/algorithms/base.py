"""Abstract base class shared by all optimisers.

全最適化アルゴリズムが共有する抽象基底クラス。
所有优化器共享的抽象基类。
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field


@dataclass
class OptimisationResult:
    """Container for the outcome of a single optimisation run.

    単回最適化実行の結果コンテナ。
    单次优化运行结果容器。

    Attributes
    ----------
    best_x:
        Best design vector found [h, l, t, b].
    best_cost:
        Objective value at *best_x* (feasible only; penalty excluded).
    cost_history:
        Sequence of best-so-far costs recorded each iteration/epoch.
    is_feasible:
        Whether *best_x* satisfies all seven constraints.
    """

    best_x: list[float]
    best_cost: float
    cost_history: list[float] = field(default_factory=list)
    is_feasible: bool = True


class BaseOptimiser(ABC):
    """Minimal interface every optimiser must implement.

    すべての最適化アルゴリズムが実装すべき最小インターフェース。
    每个优化器必须实现的最小接口。
    """

    @abstractmethod
    def run(self, **kwargs) -> OptimisationResult:  # type: ignore[override]
        """Execute the optimisation and return the result."""
        ...
