# 优化元启发式项目说明（中文）

## 文档定位

本文件是主 README 的中文配套文档，用于开源发布场景下的快速说明。

## 当前可用算法

最新版可运行代码在 `final/` 目录：

- `final/GA.py`：遗传算法
- `final/PSO.py`：粒子群算法
- `final/SA.py`：模拟退火算法

## 历史探索代码

`legacy/` 目录保存历史实验脚本，仅用于参考与追溯，不作为当前发布基线。
这些脚本可能包含未完成逻辑或占位实现。

## 复现实验建议

1. 创建并激活 Python 虚拟环境。
2. 安装 `requirements.txt` 中依赖。
3. 通过 `scripts/run.py` 运行任意维护中的算法。
4. 多次重复运行，对比收敛曲线和耗时统计。

示例：

```bash
python scripts/run.py ga --seed 7 --runs 1 --max-iteration 50 --no-plot
python scripts/run.py pso --seed 7 --runs 1 --iterations 20 --no-plot
python scripts/run.py sa --seed 7 --runs 1 --samples-per-temperature 200 --no-plot
```

## 发布建议

- 对外报告结果时，以 `final/` 目录脚本为准。
- 在论文或报告中明确参数设置（迭代次数、种群规模、随机策略）。
- 将 `legacy/` 视为历史记录，不建议直接用于基准对比结论。
- 示例图资源已整理到 `docs/assets/welded-beam-contours.png`。
