"""Check release metadata using only the standard library (Python 3.10+)."""

from __future__ import annotations

import argparse
import ast
import re
from pathlib import Path


def check_release(root: Path, tag: str | None = None) -> str:
    """Reject mismatched version, citation, changelog, or release notes."""
    module = ast.parse((root / "metaheuristics/__init__.py").read_text(encoding="utf-8"))
    package_version = next(
        ast.literal_eval(node.value)
        for node in module.body
        if isinstance(node, ast.Assign)
        and any(
            isinstance(target, ast.Name) and target.id == "__version__" for target in node.targets
        )
    )
    if not re.fullmatch(r"\d+\.\d+\.\d+", package_version):
        raise ValueError("Release version must have the form MAJOR.MINOR.PATCH")
    if tag is not None and tag != f"v{package_version}":
        raise ValueError(f"Tag {tag!r} does not match v{package_version}")
    citation = (root / "CITATION.cff").read_text(encoding="utf-8")
    if f'version: "{package_version}"' not in citation:
        raise ValueError("CITATION.cff version does not match package version")
    changelog = (root / "CHANGELOG.md").read_text(encoding="utf-8")
    if f"## [{package_version}]" not in changelog:
        raise ValueError("CHANGELOG.md has no entry for the release version")
    notes = root / "docs/releases" / f"{package_version}.md"
    if not notes.is_file() or len(notes.read_text(encoding="utf-8").strip()) < 100:
        raise ValueError("Release notes are missing or empty")
    return package_version


def main() -> None:
    """Validate the source tree before building or tagging."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--tag")
    args = parser.parse_args()
    print(
        f"Release metadata verified: {check_release(Path(__file__).resolve().parents[1], args.tag)}"
    )


if __name__ == "__main__":
    main()
