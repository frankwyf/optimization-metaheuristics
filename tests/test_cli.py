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


class TestAlgorithmRegistry:
    def test_four_algorithms(self):
        assert len(ALGORITHMS) == 4
        assert set(ALGORITHMS.keys()) == {"ga", "pso", "sa", "de"}
