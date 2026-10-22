"""Tests for the CLI runner (scripts/run.py)."""
from __future__ import annotations

import pytest

from scripts.run import ALGORITHMS, build_parser, main


class TestCLIParser:
    def test_list_flag(self):
        parser = build_parser()
        args = parser.parse_args(["--list"])
        assert args.list is True

    def test_algorithm_choices(self):
        parser = build_parser()
        for algo in ("ga", "pso", "sa", "de"):
            args = parser.parse_args([algo, "--no-plot", "--seed", "42"])
            assert args.algorithm == algo
            assert args.no_plot is True
            assert args.seed == 42

    def test_quick_flag(self):
        parser = build_parser()
        args = parser.parse_args(["de", "--quick"])
        assert args.quick is True


class TestCLIMain:
    def test_list_returns_zero(self, capsys):
        assert main(["--list"]) == 0
        out = capsys.readouterr().out
        assert "ga" in out
        assert "de" in out

    def test_no_args_returns_one(self):
        assert main([]) == 1

    @pytest.mark.parametrize("algo", ["sa", "pso", "de", "ga"])
    def test_quick_run(self, algo, capsys):
        result = main([algo, "--seed", "42", "--runs", "1", "--no-plot", "--quick"])
        assert result == 0
        out = capsys.readouterr().out
        assert "Run  1:" in out or "Run 1:" in out

    def test_de_runs_produce_stats(self, capsys):
        main(["de", "--seed", "10", "--runs", "2", "--no-plot", "--quick"])
        out = capsys.readouterr().out
        assert "Summary Statistics" in out
        assert "Best" in out

    def test_pso_pop_size_option(self, capsys):
        assert main(["pso", "--seed", "42", "--runs", "1", "--pop-size", "10", "--iterations", "1", "--no-plot"]) == 0
        assert "Run  1:" in capsys.readouterr().out

    def test_runs_must_be_positive(self):
        with pytest.raises(SystemExit):
            main(["pso", "--runs", "0", "--no-plot"])

    def test_custom_problem_and_artifact_export(self, tmp_path, capsys):
        import csv
        import json

        assert main([
            "de", "--problem", "sphere_2d", "--seed", "42", "--runs", "2",
            "--pop-size", "8", "--iterations", "2", "--no-plot", "--output-dir", str(tmp_path),
        ]) == 0
        output = capsys.readouterr().out
        assert "Sphere (2D)" in output
        payload = json.loads((tmp_path / "experiment_de_sphere_2d.json").read_text())
        assert len(payload["runs"]) == 2
        with (tmp_path / "experiment_de_sphere_2d.csv").open(newline="") as handle:
            assert len(list(csv.DictReader(handle))) == 2


class TestAlgorithmRegistry:
    def test_four_algorithms(self):
        assert len(ALGORITHMS) == 4
        assert set(ALGORITHMS.keys()) == {"ga", "pso", "sa", "de"}


def test_unseeded_export_records_replayable_seeds(tmp_path):
    import json

    from metaheuristics.experiments import run_experiment
    from scripts.run import get_problem

    assert main(["de", "--problem", "sphere_2d", "--runs", "2", "--pop-size", "4", "--iterations", "1", "--no-plot", "--output-dir", str(tmp_path)]) == 0
    payload = json.loads((tmp_path / "experiment_de_sphere_2d.json").read_text())
    assert all(isinstance(seed, int) for seed in payload["seeds"])
    replay = run_experiment("de", get_problem("sphere_2d"), seeds=payload["seeds"], optimizer_options={"pop_size": 4}, run_options={"max_iterations": 1})
    assert [record["best_x"] for record in payload["runs"]] == [run.result.best_x for run in replay.runs]


@pytest.mark.parametrize("argv", [["sa", "--pop-size", "4"], ["ga", "--iterations", "2"], ["de", "--samples-per-temperature", "2"], ["pso", "--max-iteration", "2"], ["de", "--seed", "-1"]])
def test_unsupported_or_invalid_options_are_cli_errors(argv):
    with pytest.raises(SystemExit) as exc:
        main(argv + ["--no-plot"])
    assert exc.value.code == 2


def test_cli_version(capsys):
    from metaheuristics import __version__

    with pytest.raises(SystemExit) as exc:
        main(["--version"])
    assert exc.value.code == 0
    assert __version__ in capsys.readouterr().out


def test_core_cli_works_when_plotting_imports_are_blocked(monkeypatch):
    import sys

    monkeypatch.setitem(sys.modules, "matplotlib", None)
    monkeypatch.setitem(sys.modules, "seaborn", None)
    assert main(["de", "--problem", "sphere_2d", "--seed", "7", "--runs", "1", "--pop-size", "4", "--iterations", "0", "--no-plot"]) == 0


def test_requested_plot_failure_is_reported(monkeypatch, capsys):
    import sys

    monkeypatch.setitem(sys.modules, "matplotlib.pyplot", None)
    assert main(["de", "--problem", "sphere_2d", "--seed", "7", "--runs", "1", "--pop-size", "4", "--iterations", "0"]) == 1
    assert "Plotting failed" in capsys.readouterr().err
