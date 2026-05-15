# Optimization Metaheuristics

Metaheuristic optimization experiments for the welded beam
constrained-design benchmark.

## Included experiment runners

| File | Algorithm |
|------|-----------|
| `final/GA.py` | Genetic Algorithm |
| `final/PSO.py` | Particle Swarm Optimization |
| `final/SA.py` | Simulated Annealing |
| `Snake.py` | Snake Optimizer (exploratory) |
| `Whale.py` | Whale Optimization Algorithm (exploratory) |
| `Golden_jackal.py` | Golden Jackal Optimizer (exploratory) |
| `general.py` | Shared objective function and constraints |

## Quick start

```bash
python -m venv .venv
.venv\Scripts\activate          # Windows PowerShell
# source .venv/bin/activate       # macOS / Linux

pip install -r requirements.txt
python final/GA.py
```

Replace `final/GA.py` with `final/PSO.py` or `final/SA.py` to run other
experiment sets.

## What to expect

These scripts are experiment-style runners, not a packaged library. They
typically:

- print optimization statistics to the console
- open Matplotlib windows
- plot convergence behavior across repeated runs

## Benchmark problem

The **welded beam design** problem minimizes fabrication cost subject to
stress, deflection, and buckling constraints. It is a standard benchmark in
constrained engineering optimization.

Variables: weld height (x1), weld length (x2), beam height (x3), beam
thickness (x4).

## License

[MIT](LICENSE)
