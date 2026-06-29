# Security Policy · 安全政策 · セキュリティポリシー

## English

### Supported Versions

| Version | Supported          |
| ------- | ------------------ |
| 1.x     | :white_check_mark: |
| < 1.0   | :x:                |

### Scope

This project is a **research / educational** numerical optimisation library.
It does not handle user authentication, network connections, file-system
access outside the repository, or any sensitive user data.  The primary
security concern is dependency vulnerabilities.

### Reporting a Vulnerability

If you discover a security vulnerability, **please do not open a public
GitHub Issue**.  Instead:

1. E-mail the maintainer directly (see the repository profile for contact
   details) with the subject line `[SECURITY] optimization-metaheuristics`.
2. Include a description of the vulnerability, reproduction steps, and its
   potential impact.
3. You will receive an acknowledgement within **5 business days**.
4. We aim to release a patch within **30 days** of a confirmed report.

We follow [responsible disclosure](https://en.wikipedia.org/wiki/Responsible_disclosure)
principles.

### Dependency Security

Dependencies are declared in `requirements.txt` and `pyproject.toml`.
To check for known CVEs in the installed environment:

```bash
pip install pip-audit
pip-audit
```

---

## 中文

### 支持的版本

| 版本  | 支持状态           |
| ----- | ------------------ |
| 1.x   | :white_check_mark: |
| < 1.0 | :x:                |

### 范围

本项目是一个**研究/教育用途**的数值优化库。它不处理用户身份验证、网络连接、
仓库外的文件系统访问或任何敏感用户数据。主要的安全关注点是依赖项漏洞。

### 报告漏洞

如果您发现安全漏洞，**请不要提交公开的 GitHub Issue**。请：

1. 直接通过电子邮件联系维护者（联系方式见仓库主页），邮件主题填写
   `[SECURITY] optimization-metaheuristics`。
2. 描述漏洞、复现步骤及潜在影响。
3. 我们将在 **5 个工作日内**确认收到您的报告。
4. 我们目标在确认报告后 **30 天内**发布补丁。

我们遵循[负责任的披露](https://en.wikipedia.org/wiki/Responsible_disclosure)原则。

---

## 日本語

### サポートバージョン

| バージョン | サポート状況       |
| ---------- | ------------------ |
| 1.x        | :white_check_mark: |
| < 1.0      | :x:                |

### スコープ

本プロジェクトは**研究・教育目的**の数値最適化ライブラリです。
ユーザー認証、ネットワーク接続、リポジトリ外のファイルシステムアクセス、
または機密ユーザーデータを扱いません。
主なセキュリティ上の懸念は依存関係の脆弱性です。

### 脆弱性の報告

セキュリティ上の脆弱性を発見した場合、**公開の GitHub Issue は開かないでください**。
代わりに：

1. メンテナーに直接メール（リポジトリプロフィールの連絡先参照）でご連絡ください。
   件名は `[SECURITY] optimization-metaheuristics` としてください。
2. 脆弱性の説明、再現手順、潜在的な影響を含めてください。
3. **5 営業日以内**に受領確認をお送りします。
4. 確認された報告から **30 日以内**にパッチをリリースすることを目標としています。

私たちは[責任ある開示](https://en.wikipedia.org/wiki/Responsible_disclosure)の原則に従います。
