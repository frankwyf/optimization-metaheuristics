# 最適化メタヒューリスティクス（日本語ガイド）

## 目的

この文書は、メイン README を補足する日本語ドキュメントです。

## 現行の実行対象

最新の実行スクリプトは `final/` にあります。

- `final/GA.py`：遺伝的アルゴリズム
- `final/PSO.py`：粒子群最適化
- `final/SA.py`：焼きなまし法

## 旧実験コード

`legacy/` には探索段階のスクリプトを保存しています。
公開用ベースラインとしては `final/` を使用してください。

## 再現手順（推奨）

1. Python 仮想環境を作成して有効化する。
2. `requirements.txt` から依存関係をインストールする。
3. `scripts/run.py` から対象アルゴリズムを実行する。
4. 複数回実行し、収束挙動と実行時間を比較する。

例:

```bash
python scripts/run.py ga --seed 7 --runs 1 --max-iteration 50 --no-plot
python scripts/run.py pso --seed 7 --runs 1 --iterations 20 --no-plot
python scripts/run.py sa --seed 7 --runs 1 --samples-per-temperature 200 --no-plot
```

## 公開時の運用

- 公開結果は `final/` の実装を基準にする。
- `legacy/` は履歴参照用として扱う。
- 反復回数、個体数、乱数条件などの設定を明記する。
- 参考画像は `docs/assets/welded-beam-contours.png` に整理済み。
