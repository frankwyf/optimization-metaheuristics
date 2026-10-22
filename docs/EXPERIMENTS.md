# Reproducible experiments

1. Save the package commit/version, Python and NumPy versions, objective source,
   bounds, constraints, penalty, full algorithm settings, and seed list.
2. Choose seeds and budgets before examining outcomes. Keep every run, including
   infeasible results; do not select the best seeds for the final report.
3. Use the same settings for paired before/after runs. Fixes can change RNG
   consumption, so changed trajectories do not alone imply statistical improvement.
4. Report feasible-only mean, population standard deviation (`ddof=0`), best
   feasible objective, feasibility rate, all-run penalized mean/std, evaluation
   counts, runtime, and convergence histories. `null` means no feasible run, not zero.
5. Compare algorithm cost using objective evaluations and timing. Iterations,
   generations, and temperature stages are not equal budgets. Feasibility checks
   also cost time but do not increment the objective evaluation counter.

```bash
python -m metaheuristics de --problem sphere_2d --seed 42 --runs 20 \
  --pop-size 40 --iterations 100 --no-plot --output-dir results/de-sphere
```

Omitting `--seed` generates a start seed and records every actual seed. To replay
an arbitrary exported plan, read `payload["seeds"]` and pass it to
`run_experiment(..., seeds=payload["seeds"], ...)` with the saved settings.
For the CLI's consecutive plan, reuse the first seed and run count.

Exact result replay assumes deterministic objective/constraint callbacks and the
same implementation/dependencies. Cross-version or cross-platform bitwise equality
is not promised. Wall-clock timing is never part of deterministic equality.
Callbacks that use randomness must manage their own RNG explicitly.

The optimizer minimizes a fixed penalty score. Poorly scaled constraints or an
insufficient penalty can favor infeasible candidates. Always inspect feasibility
and the original objective separately. A low penalty value is not proof of a valid
engineering design. Statistical tests, confidence intervals, and evaluation-budget
stopping are future work in [ROADMAP.md](../ROADMAP.md).
