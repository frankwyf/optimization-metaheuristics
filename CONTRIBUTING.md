# Contributing Guide · 贡献指南 · コントリビューションガイド

---

## English

Thank you for considering contributing to **optimization-metaheuristics**!

### Ways to Contribute
- Report bugs or suggest improvements via [GitHub Issues](https://github.com/frankwyf/optimization-metaheuristics/issues)
- Submit pull requests for bug fixes, new features, or documentation improvements
- Improve or add translations to the trilingual documentation
- Add new benchmark problems or algorithm implementations

### Development Setup
```bash
git clone https://github.com/frankwyf/optimization-metaheuristics.git
cd optimization-metaheuristics
python -m venv .venv
# Windows
.venv\Scripts\activate
# Linux / macOS
source .venv/bin/activate
pip install -r requirements.txt
pip install pytest pytest-cov ruff
```

### Code Style
- We use [ruff](https://github.com/astral-sh/ruff) for linting and formatting.
- Run `ruff check metaheuristics/ scripts/` before submitting a PR.
- All new public functions must include a docstring.
- Prefer bilingual (English + one other language) inline comments.

### Testing
```bash
# From the repository root
python -m pytest tests/ -v
```
New code should include tests. All existing tests must pass.

### Pull Request Process
1. Fork the repository and create a feature branch (`git checkout -b feat/my-feature`).
2. Write tests for new functionality.
3. Ensure the CI suite passes locally.
4. Open a PR with a clear description of the change and its motivation.
5. One maintainer review and approval is required before merging.

### Commit Message Convention
Follow [Conventional Commits](https://www.conventionalcommits.org/):
```
feat: add Differential Evolution algorithm
fix: correct J formula in PSO velocity update
docs: add Japanese translation for SECURITY.md
test: cover SA cooling-rate edge cases
```

---

## 中文

感谢您考虑为 **optimization-metaheuristics** 做出贡献！

### 贡献方式
- 通过 [GitHub Issues](https://github.com/frankwyf/optimization-metaheuristics/issues) 报告错误或提出改进建议
- 提交 PR 修复 Bug、添加新功能或改进文档
- 改进或添加三语文档翻译
- 添加新的基准问题或算法实现

### 开发环境搭建
```bash
git clone https://github.com/frankwyf/optimization-metaheuristics.git
cd optimization-metaheuristics
python -m venv .venv
.venv\Scripts\activate  # Windows
source .venv/bin/activate  # Linux/macOS
pip install -r requirements.txt
pip install pytest pytest-cov ruff
```

### 代码风格
- 使用 [ruff](https://github.com/astral-sh/ruff) 进行代码检查和格式化
- 提交 PR 前运行 `ruff check metaheuristics/ scripts/`
- 所有新的公共函数必须包含文档字符串
- 建议使用双语（英文+其他语言）内联注释

### 测试
```bash
python -m pytest tests/ -v
```
新代码需包含测试用例，且不得破坏现有测试。

### PR 流程
1. Fork 仓库并创建功能分支（`git checkout -b feat/my-feature`）
2. 为新功能编写测试
3. 确保 CI 在本地通过
4. 提交 PR 并清晰描述更改内容及原因
5. 需要一位维护者审核并批准后方可合并

---

## 日本語

**optimization-metaheuristics** へのご貢献をご検討いただきありがとうございます！

### 貢献方法
- [GitHub Issues](https://github.com/frankwyf/optimization-metaheuristics/issues) を通じてバグ報告や改善提案を行う
- バグ修正・新機能・ドキュメント改善のプルリクエストを送る
- 三カ国語ドキュメントの翻訳を改善・追加する
- 新しいベンチマーク問題やアルゴリズム実装を追加する

### 開発環境のセットアップ
```bash
git clone https://github.com/frankwyf/optimization-metaheuristics.git
cd optimization-metaheuristics
python -m venv .venv
.venv\Scripts\activate    # Windows
source .venv/bin/activate  # Linux / macOS
pip install -r requirements.txt
pip install pytest pytest-cov ruff
```

### コードスタイル
- [ruff](https://github.com/astral-sh/ruff) を使用してリントとフォーマットを行います
- PR 提出前に `ruff check metaheuristics/ scripts/` を実行してください
- 新しいパブリック関数にはドキュメント文字列が必要です
- バイリンガル（英語＋他言語）のインラインコメントを推奨します

### テスト
```bash
python -m pytest tests/ -v
```
新しいコードにはテストが必要です。既存のテストはすべて通過する必要があります。

### プルリクエストのプロセス
1. リポジトリをフォークし、機能ブランチを作成する（`git checkout -b feat/my-feature`）
2. 新機能のテストを作成する
3. CI がローカルで通ることを確認する
4. 変更内容と理由を明確に説明した PR を開く
5. マージ前にメンテナー 1 名のレビューと承認が必要です
