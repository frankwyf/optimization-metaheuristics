"""Optional plotting smoke tests, skipped in core-only installations."""
from __future__ import annotations

import os

import pytest

os.environ.setdefault("MPLBACKEND", "Agg")

def test_convergence_and_statistics_plots_render_headlessly():
    pytest.importorskip("matplotlib")
    pytest.importorskip("seaborn")
    import matplotlib.pyplot as plt

    from metaheuristics.utils.visualization import plot_convergence, plot_run_statistics

    figure, (axis1, axis2) = plt.subplots(1, 2)
    plot_convergence({"DE": [3.0, 2.0, 1.0]}, ax=axis1)
    plot_run_statistics({"DE": [1.0, 1.2, 1.1]}, ax=axis2)
    figure.canvas.draw()
    assert axis1.get_title() == "Convergence Comparison"
    assert axis2.get_title() == "Multi-run Statistics"
    plt.close(figure)


def test_headless_cli_saves_plot_without_opening_a_gui(tmp_path, monkeypatch):
    matplotlib = pytest.importorskip("matplotlib")
    pytest.importorskip("seaborn")
    matplotlib.use("Agg", force=True)
    import matplotlib.pyplot as plt

    from scripts.run import main

    monkeypatch.setattr(plt, "show", lambda *_args, **_kwargs: pytest.fail("GUI show called"))
    assert (
        main(
            [
                "de",
                "--problem",
                "sphere_2d",
                "--seed",
                "42",
                "--runs",
                "1",
                "--pop-size",
                "8",
                "--iterations",
                "2",
                "--output-dir",
                str(tmp_path),
            ]
        )
        == 0
    )
    assert (tmp_path / "convergence_de_sphere_2d.png").is_file()
