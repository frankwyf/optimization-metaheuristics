"""Abstract base class shared by all optimisers.

全最適化アルゴリズムが共有する抽象基底クラス。
所有优化器共享的抽象基类。
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Sequence
from dataclasses import dataclass, field

from metaheuristics.problem import WELDED_BEAM_PROBLEM
from metaheuristics.problems import OptimizationProblem, ProblemEvaluation


@dataclass
class OptimisationResult:
    """Container for the outcome of a single optimisation run.

    単回最適化実行の結果コンテナ。
    单次优化运行结果容器。

    Attributes
    ----------
    best_x:
        Candidate vector returned by the algorithm.
    best_cost:
        Historical result value: raw objective when feasible, penalized value otherwise.
    cost_history:
        Sequence of search values recorded by the algorithm.
    is_feasible:
        Whether *best_x* satisfies problem bounds and constraints.
    """

    best_x: list[float]
    best_cost: float
    cost_history: list[float] = field(default_factory=list)
    is_feasible: bool = True
    objective_value: float | None = None
    penalized_cost: float | None = None
    n_evaluations: int = 0
    seed: int | None = None
    constraint_violations: tuple[float, ...] = ()


class BaseOptimiser(ABC):
    """Minimal interface every optimiser must implement.

    すべての最適化アルゴリズムが実装すべき最小インターフェース。
    每个优化器必须实现的最小接口。
    """

    def __init__(self, problem: OptimizationProblem | None = None, seed: int | None = None) -> None:
        self.problem = problem if problem is not None else WELDED_BEAM_PROBLEM
        self.seed = seed
        self.n_evaluations = 0

    def _start_run(self) -> None:
        self.n_evaluations = 0

    def _evaluate(self, x: Sequence[float]) -> ProblemEvaluation:
        self.n_evaluations += 1
        return self.problem.evaluate(x)

    def _make_result(
        self,
        x: list[float],
        evaluation: ProblemEvaluation,
        cost_history: list[float],
    ) -> OptimisationResult:
        # best_cost preserves the project's historical feasible/raw and
        # infeasible/penalized convention; objective_value is always raw.
        return OptimisationResult(
            best_x=x,
            best_cost=evaluation.objective_value if evaluation.is_feasible else evaluation.penalized_value,
            cost_history=cost_history,
            is_feasible=evaluation.is_feasible,
            objective_value=evaluation.objective_value,
            penalized_cost=evaluation.penalized_value,
            n_evaluations=self.n_evaluations,
            seed=self.seed,
            constraint_violations=evaluation.violations,
        )

    @abstractmethod
    def run(self, **kwargs) -> OptimisationResult:  # type: ignore[override]
        """Execute the optimisation and return the result."""
        ...
