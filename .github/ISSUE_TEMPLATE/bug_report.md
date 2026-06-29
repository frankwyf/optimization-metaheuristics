---
name: Bug report / 错误报告 / バグ報告
about: Report a reproducible bug
title: "[BUG] "
labels: bug
assignees: ''
---

## Description / 描述 / 説明

A clear and concise description of what the bug is.

## Steps to Reproduce / 复现步骤 / 再現手順

```python
# Minimal reproducible example
from metaheuristics.algorithms.sa import SimulatedAnnealing
sa = SimulatedAnnealing(seed=42)
result = sa.run(samples_per_temperature=200)
```

## Expected Behaviour / 预期行为 / 期待される動作

What you expected to happen.

## Actual Behaviour / 实际行为 / 実際の動作

What actually happened. Include full traceback if applicable.

## Environment / 环境 / 環境

- OS: [e.g. Ubuntu 22.04 / Windows 11]
- Python version: [e.g. 3.11.4]
- numpy version: [e.g. 1.26.0]
- matplotlib version: [e.g. 3.8.0]
- Package version: [e.g. 1.1.0]

## Additional Context / 附加信息 / 追加情報

Any other context about the problem.
