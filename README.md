# Optimization Metaheuristics

Metaheuristic optimization experiments for the welded beam constrained-design benchmark.

This repository is prepared as an open-source release version with:

- a cleaned top-level structure
- stable runnable scripts grouped in `final/`
- legacy exploratory scripts isolated in `legacy/`
- multilingual documentation under `docs/`

## Language Docs

- English companion: [docs/README.en.md](docs/README.en.md)
- Chinese: [docs/README.zh-CN.md](docs/README.zh-CN.md)
- Japanese: [docs/README.ja.md](docs/README.ja.md)

## Release Notes

- English release notes: [docs/RELEASE_NOTES.en.md](docs/RELEASE_NOTES.en.md)
- Chinese release notes: [docs/RELEASE_NOTES.zh-CN.md](docs/RELEASE_NOTES.zh-CN.md)
- Japanese release notes: [docs/RELEASE_NOTES.ja.md](docs/RELEASE_NOTES.ja.md)

## Repository Layout

| Path | Description |
|------|-------------|
| `final/GA.py` | Genetic Algorithm runner (current version) |
| `final/PSO.py` | Particle Swarm Optimization runner (current version) |
| `final/SA.py` | Simulated Annealing runner (current version) |
| `scripts/run.py` | Unified CLI entrypoint for maintained algorithms |
| `general.py` | Shared objective and constraint definitions |
| `legacy/` | Archived exploratory scripts not maintained as release baseline |
| `docs/` | Release docs and multilingual guides |
| `.github/workflows/ci.yml` | Minimal CI for dependency install and syntax validation |

## Quick Start

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python scripts/run.py ga
```

Use `python scripts/run.py pso` or `python scripts/run.py sa` to run other algorithms.

Lightweight reproducible examples:

```bash
python scripts/run.py ga --seed 7 --runs 1 --max-iteration 50 --no-plot
python scripts/run.py pso --seed 7 --runs 1 --iterations 20 --no-plot
python scripts/run.py sa --seed 7 --runs 1 --samples-per-temperature 200 --no-plot
```

List supported algorithms:

```bash
python scripts/run.py --list
```

Example benchmark visualization asset: [docs/assets/welded-beam-contours.png](docs/assets/welded-beam-contours.png)

## Benchmark Problem

The welded beam design problem minimizes fabrication cost subject to stress,
deflection, and buckling constraints.

Design variables:

- `x1`: weld height
- `x2`: weld length
- `x3`: beam height
- `x4`: beam thickness

## Open-Source Release Notes

- No API keys, tokens, private credentials, or local absolute paths are stored.
- Legacy exploratory code is preserved separately for reproducibility.
- Current release baseline is the `final/` directory.
- A minimal GitHub Actions workflow validates dependency installation and Python syntax.

## License

[MIT](LICENSE)
