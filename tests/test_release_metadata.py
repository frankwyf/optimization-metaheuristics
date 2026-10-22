"""Release guards must reject inconsistent source metadata and tags."""

from __future__ import annotations

from pathlib import Path

import pytest

from tools.check_release import check_release


def test_current_release_metadata_is_consistent():
    from metaheuristics import __version__

    assert check_release(Path(__file__).resolve().parents[1], f"v{__version__}") == __version__


def test_wrong_tag_is_rejected():
    with pytest.raises(ValueError, match="Tag"):
        check_release(Path(__file__).resolve().parents[1], "v999.0.0")


@pytest.mark.parametrize("missing", ["citation", "changelog", "notes"])
def test_incomplete_release_is_rejected(tmp_path, missing):
    (tmp_path / "metaheuristics").mkdir()
    (tmp_path / "metaheuristics/__init__.py").write_text('__version__ = "1.0.0"\n')
    (tmp_path / "CITATION.cff").write_text(
        'version: "0.9.0"' if missing == "citation" else 'version: "1.0.0"'
    )
    (tmp_path / "CHANGELOG.md").write_text("" if missing == "changelog" else "## [1.0.0]")
    (tmp_path / "docs/releases").mkdir(parents=True)
    if missing != "notes":
        (tmp_path / "docs/releases/1.0.0.md").write_text("Release notes. " * 20)
    with pytest.raises(ValueError):
        check_release(tmp_path)
