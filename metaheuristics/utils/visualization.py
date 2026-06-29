"""Visualisation utilities for optimisation results.

最適化結果の可視化ユーティリティ。
优化结果可视化工具。
"""
from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import matplotlib.axes

import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns

sns.set_style("whitegrid")

# Use a font that has good Unicode coverage on most platforms
plt.rcParams["font.family"] = "DejaVu Sans"
plt.rcParams["axes.unicode_minus"] = False


def plot_convergence(
    cost_histories: dict[str, list[float]],
    title: str = "Convergence Comparison",
    xlabel: str = "Iteration",
    ylabel: str = "Best Objective Value",
    ax: matplotlib.axes.Axes | None = None,
) -> matplotlib.axes.Axes:
    """Plot convergence curves for one or more algorithms.

    一つ以上のアルゴリズムの収束曲線をプロットする。
    绘制一个或多个算法的收敛曲线。

    Parameters
    ----------
    cost_histories:
        Mapping of algorithm name → list of best-so-far costs.
    title:
        Figure title.
    xlabel:
        X-axis label.
    ylabel:
        Y-axis label.
    ax:
        Existing Axes to draw on (creates a new figure if None).

    Returns
    -------
    matplotlib.axes.Axes
    """
    if ax is None:
        _, ax = plt.subplots(figsize=(10, 5))
    for name, history in cost_histories.items():
        ax.plot(history, label=name)
    ax.set_title(title)
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    ax.legend()
    return ax


def plot_run_statistics(
    results_per_algo: dict[str, list[float]],
    title: str = "Multi-run Statistics",
    ax: matplotlib.axes.Axes | None = None,
) -> matplotlib.axes.Axes:
    """Box-plot of best costs across repeated runs per algorithm.

    アルゴリズムごとに複数回実行の最良コストの箱ひげ図。
    每个算法多次运行的最优成本箱线图。

    Parameters
    ----------
    results_per_algo:
        Mapping of algorithm name → list of best costs from each run.
    title:
        Figure title.
    ax:
        Existing Axes to draw on.

    Returns
    -------
    matplotlib.axes.Axes
    """
    if ax is None:
        _, ax = plt.subplots(figsize=(8, 5))
    labels = list(results_per_algo.keys())
    data = [results_per_algo[k] for k in labels]
    ax.boxplot(data, labels=labels, patch_artist=True)
    ax.set_title(title)
    ax.set_ylabel("Best feasible cost")

    # Annotate with mean ± std
    for i, (label, values) in enumerate(results_per_algo.items(), start=1):
        arr = np.asarray(values)
        ax.text(
            i,
            np.nanmax(arr) * 1.01,
            f"μ={np.nanmean(arr):.4f}\nσ={np.nanstd(arr):.4f}",
            ha="center",
            fontsize=8,
        )
    return ax
