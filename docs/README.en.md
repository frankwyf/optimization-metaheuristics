# Optimization Metaheuristics (English Companion)

## Scope

This document complements the main repository README and provides additional release-oriented notes.

## Stable Algorithms

The latest runnable versions are in `final/`:

- `final/GA.py`: Genetic Algorithm
- `final/PSO.py`: Particle Swarm Optimization
- `final/SA.py`: Simulated Annealing

## Legacy Algorithms

Exploratory drafts are archived in `legacy/` and are kept for reference only.
They may contain unfinished logic and are not the recommended baseline for benchmarking.

## Reproducibility

1. Create and activate a virtual environment.
2. Install dependencies from `requirements.txt`.
3. Run one algorithm through `scripts/run.py`.
4. Repeat multiple runs to compare convergence and runtime behavior.

Examples:

```bash
python scripts/run.py ga --seed 7 --runs 1 --max-iteration 50 --no-plot
python scripts/run.py pso --seed 7 --runs 1 --iterations 20 --no-plot
python scripts/run.py sa --seed 7 --runs 1 --samples-per-temperature 200 --no-plot
```

## Suggested Release Usage

- Use `final/` scripts for published plots and reported metrics.
- Treat `legacy/` scripts as historical exploration.
- Keep benchmark settings (population size, iteration count, random seed policy) explicit when reporting results.
- Example visualization asset: `docs/assets/welded-beam-contours.png`.
