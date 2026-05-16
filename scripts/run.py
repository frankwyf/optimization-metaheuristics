from __future__ import annotations

import argparse
import runpy
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ALGORITHMS = {
    "ga": ROOT / "final" / "GA.py",
    "pso": ROOT / "final" / "PSO.py",
    "sa": ROOT / "final" / "SA.py",
}


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Run one of the maintained optimization scripts from final/."
    )
    parser.add_argument(
        "algorithm",
        nargs="?",
        choices=sorted(ALGORITHMS),
        help="Algorithm to run: ga, pso, or sa.",
    )
    parser.add_argument(
        "--list",
        action="store_true",
        help="List available algorithms and exit.",
    )
    return parser


def list_algorithms() -> None:
    for name, path in sorted(ALGORITHMS.items()):
        print(f"{name}: {path.relative_to(ROOT)}")


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args, forwarded_args = parser.parse_known_args(argv)

    if args.list:
        list_algorithms()
        return 0

    if not args.algorithm:
        parser.print_help()
        return 1

    script_path = ALGORITHMS[args.algorithm]
    old_argv = sys.argv[:]
    try:
        sys.argv = [str(script_path), *forwarded_args]
        runpy.run_path(str(script_path), run_name="__main__")
    finally:
        sys.argv = old_argv
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
