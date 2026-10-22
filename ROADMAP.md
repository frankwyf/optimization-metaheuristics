# Path toward a mature scientific library

The 1.3 series focuses on bounded scalar minimization, verifiable best-so-far
results, isolated randomness, reusable experiments, and tested release artifacts.
The package remains beta. More algorithms alone are not a maturity criterion.

| Priority | Work | Acceptance evidence |
|---|---|---|
| P0, 1.3 | Correct result semantics, explicit seed plans, input validation, core-only installation, installed-wheel CI, release guards | Deterministic regressions, full cross-platform CI, replayable exports, versioned wheel/sdist |
| P1, 1.4 | Common objective-evaluation budgets, stopping reasons, cancellation callback, per-evaluation convergence trace | Every optimizer respects the budget including initialization; callbacks cannot corrupt incumbent results |
| P1, 1.4 | Feasibility-first constraint strategy alongside the current penalty | Independent mathematical review, unit/scaling tests, documented opt-in behavior; unchanged canonical benchmarks |
| P1, 1.4 | Paired statistical comparison, confidence intervals, benchmark manifest | Predeclared seed plans, complete results, effect sizes, multiple-comparison guidance; no timing assertions in CI |
| P2 | Profile and vectorize expensive paths; optional batch evaluation | Profiling evidence and repeatable evaluation counts before changes; identical scalar/batch objective semantics |
| P2 | Parallel independent runs and restartable checkpoints | Explicit seed allocation independent of scheduling; serial/parallel equality tests; versioned checkpoint format |
| P2 | Type checking, generated reference docs, minimum/latest dependency jobs | Documented supported public API, verified examples, compatibility/deprecation policy |
| P3 | Plugin registry, mixed-integer variables, multiobjective optimization | Separate API proposals, mathematical definitions, reference implementations and benchmarks before inclusion |

Maintenance expectations: report numerical regressions with seed, settings, and
environment; review changes to mathematical operators independently; retain old
release assets; deprecate public API intentionally; keep security reports private.
A DOI, archived benchmark datasets, and additional maintainers would strengthen
research reuse once the release process has been exercised successfully.
