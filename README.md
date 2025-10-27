# SDS2Roster

[![CI](https://github.com/nahisaho/SDS2Roster/workflows/CI/badge.svg)](https://github.com/nahisaho/SDS2Roster/actions/workflows/ci.yml)
[![Coverage](https://codecov.io/gh/nahisaho/SDS2Roster/branch/main/graph/badge.svg)](https://codecov.io/gh/nahisaho/SDS2Roster)
[![Python Version](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

Microsoft SDS（School Data Sync）形式をOneRoster CSV形式に変換するツール

## 📋 概要

SDS2Rosterは、Microsoft SDS形式のCSVファイルをOneRoster CSV形式に変換するPythonツールです。教育機関のデータ管理システム間でのデータ移行を効率化します。

## ✨ 主な機能

- **SDS → OneRoster変換**: Microsoft SDS形式からOneRoster形式への完全な変換
- **データ検証**: 変換前後のデータ整合性チェック
- **UUID v5 GUID生成**: 決定的なGUID生成による一貫性保証
- **Azure統合**: Blob StorageとTable Storageのサポート
- **CLI**: 使いやすいコマンドラインインターフェイス
- **高品質**: 97%+のコードカバレッジ、149個のテスト
- **拡張可能**: カスタムマッピングルールの追加が可能

## 🚀 クイックスタート

### 必要要件

- Python 3.10以上
- pip（Pythonパッケージマネージャー）

### インストール

1. リポジトリのクローン

```bash
git clone https://github.com/yourusername/SDS2Roster.git
cd SDS2Roster
```

2. 仮想環境の作成

```bash
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# または
.venv\Scripts\activate  # Windows
```

3. 依存関係のインストール

```bash
pip install -r requirements.txt
pip install -r requirements-dev.txt  # 開発用
```

4. パッケージのインストール（開発モード）

```bash
pip install -e .
```

## 💻 使い方

### 基本的な変換

```bash
sds2roster convert /path/to/sds/files /path/to/output
```

### データ検証のみ

```bash
sds2roster validate /path/to/sds/files
```

### バージョン確認

```bash
sds2roster version
```

### 詳細出力

```bash
sds2roster convert /path/to/sds/files /path/to/output --verbose
```

## ☁️ Azure統合

SDS2RosterはAzure Blob StorageとAzure Table Storageをサポートしています。

### Azure Blob Storageの使用

```python
from sds2roster.azure.blob_storage import BlobStorageClient

# 接続文字列で初期化
client = BlobStorageClient(
    connection_string="DefaultEndpointsProtocol=https;..."
)

# または、アカウント資格情報で初期化
client = BlobStorageClient(
    account_name="your_account",
    account_key="your_key"
)

# ファイルをアップロード
url = client.upload_file("local/file.csv", "remote/file.csv")

# ファイルをダウンロード
client.download_file("remote/file.csv", "local/file.csv")

# CSVコンテンツを直接読み込み
content = client.read_csv_content("data.csv")

# CSVコンテンツを直接書き込み
url = client.write_csv_content("data.csv", "header1,header2\nvalue1,value2")

# Blobをリスト表示
blobs = client.list_blobs(prefix="sds/")
```

### Azure Table Storageの使用

```python
from sds2roster.azure.table_storage import TableStorageClient

# 初期化
client = TableStorageClient(
    connection_string="DefaultEndpointsProtocol=https;..."
)

# 変換ジョブを記録
client.log_conversion(
    conversion_id="job-123",
    source_type="SDS",
    target_type="OneRoster",
    status="success",
    metadata={"files": 5, "records": 1000}
)

# 変換ステータスを更新
client.update_conversion_status(
    conversion_id="job-123",
    source_type="SDS",
    status="completed"
)

# 変換履歴を取得
conversions = client.list_conversions(source_type="SDS", status="success")

# 統計情報を取得
stats = client.get_conversion_stats(source_type="SDS")
print(f"Total: {stats['total']}, Success: {stats['success']}")
```

### 環境変数

Azure統合には以下の環境変数を設定してください：

```bash
# Azure Blob Storage
AZURE_STORAGE_CONNECTION_STRING=DefaultEndpointsProtocol=https;...
# または
AZURE_STORAGE_ACCOUNT_NAME=your_account_name
AZURE_STORAGE_ACCOUNT_KEY=your_account_key

# Azure Table Storage  
AZURE_TABLE_CONNECTION_STRING=DefaultEndpointsProtocol=https;...
```

## 📁 プロジェクト構造

```
SDS2Roster/
├── src/
│   └── sds2roster/
│       ├── __init__.py
│       ├── cli.py              # CLIエントリーポイント
│       ├── converter.py        # 変換ロジック
│       ├── models/             # データモデル
│       │   ├── sds.py
│       │   └── oneroster.py
│       ├── azure/              # Azure統合
│       └── utils/              # ユーティリティ
├── tests/
│   ├── unit/                   # 単体テスト
│   ├── integration/            # 統合テスト
│   └── conftest.py
├── docs/                       # ドキュメント
│   ├── requirements/
│   ├── architecture/
│   └── project/
├── pyproject.toml              # プロジェクト設定
├── requirements.txt            # 本番依存関係
├── requirements-dev.txt        # 開発依存関係
└── README.md
```

## 🧪 テスト

### すべてのテストを実行

```bash
pytest
```

### カバレッジ付きでテスト

```bash
pytest --cov=src/sds2roster --cov-report=html
```

### 単体テストのみ

```bash
pytest tests/unit/
```

### 統合テストのみ

```bash
pytest tests/integration/
```

## 🛠️ 開発

### コードフォーマット

```bash
# Black（フォーマッター）
black src/ tests/

# isort（インポート整理）
isort src/ tests/
```

### コード品質チェック

```bash
# flake8（Linter）
flake8 src/ tests/

# mypy（型チェック）
mypy src/
```

### すべてのチェックを一度に

```bash
black src/ tests/ && isort src/ tests/ && flake8 src/ tests/ && mypy src/ && pytest
```

## 📚 ドキュメント

詳細なドキュメントは`docs/`ディレクトリにあります：

- [要件定義](docs/requirements/)
- [アーキテクチャ設計](docs/architecture/)
- [プロジェクト管理](docs/project/)

## 🔧 環境変数

`.env`ファイルを作成して以下の環境変数を設定してください：

```bash
# Azure Storage
AZURE_STORAGE_CONNECTION_STRING=your_connection_string
AZURE_STORAGE_ACCOUNT_NAME=your_account_name
AZURE_STORAGE_ACCOUNT_KEY=your_account_key

# Azure Table Storage
AZURE_TABLE_CONNECTION_STRING=your_connection_string

# Application
LOG_LEVEL=INFO
```

## � テスト

### すべてのテストを実行

```bash
pytest tests/ -v
```

### カバレッジ付きでテストを実行

```bash
pytest tests/ --cov=src/sds2roster --cov-report=html
```

### 統合テストのみ実行

```bash
pytest tests/integration/ -v
```

### ユニットテストのみ実行

```bash
pytest tests/unit/ -v
```

### テスト統計

- **総テスト数**: 149個
- **成功率**: 100%
- **カバレッジ**: 97%+
- **ユニットテスト**: 140個
- **統合テスト**: 9個

## 🔍 コード品質

### リンター実行

```bash
# Ruff (高速リンター)
ruff check src/ tests/

# Black (コードフォーマッター)
black --check src/ tests/

# isort (インポート順序)
isort --check-only src/ tests/
```

### 型チェック

```bash
mypy src/
```

### すべてのチェックを実行

```bash
# フォーマット
black src/ tests/
isort src/ tests/

# リント
ruff check src/ tests/ --fix

# 型チェック
mypy src/

# テスト
pytest tests/ -v --cov=src/sds2roster
```

## 🚀 CI/CD

このプロジェクトはGitHub Actionsを使用した自動化されたCI/CDパイプラインを持っています。

### 継続的インテグレーション (CI)

プッシュまたはプルリクエストごとに自動実行:

- ✅ Python 3.10, 3.11, 3.12でのテスト
- ✅ コードフォーマットチェック (Black, isort)
- ✅ リンターチェック (Ruff)
- ✅ 型チェック (mypy)
- ✅ テストカバレッジレポート
- ✅ パッケージビルド
- ✅ 統合テスト
- ✅ CLIコマンド動作確認

### カバレッジレポート

- Codecovに自動アップロード
- プルリクエストにカバレッジ変化を表示
- 最小カバレッジ閾値: 90%

### リリースワークフロー

バージョンタグ (例: `v0.1.0`) をプッシュすると自動実行:

1. すべてのテストを実行
2. パッケージをビルド
3. GitHubリリースを作成
4. PyPIに公開 (設定時)

```bash
# リリースの作成
git tag -a v0.1.0 -m "Release version 0.1.0"
git push origin v0.1.0
```

### Dependabot

依存関係の自動更新:

- 週次でPythonパッケージをチェック
- 週次でGitHub Actionsをチェック
- 自動的にプルリクエストを作成

## �🤝 コントリビューション

貢献を歓迎します! 以下の手順に従ってください:

1. このリポジトリをフォーク
2. フィーチャーブランチを作成（`git checkout -b feature/amazing-feature`）
3. 変更をコミット（`git commit -m 'Add amazing feature'`）
4. ブランチにプッシュ（`git push origin feature/amazing-feature`）
5. プルリクエストを作成

### 開発ワークフロー

```bash
# リポジトリをクローン
git clone https://github.com/nahisaho/SDS2Roster.git
cd SDS2Roster

# 開発環境をセットアップ
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"

# 新しいブランチを作成
git checkout -b feature/your-feature

# コードを変更し、テストを追加

# コードをフォーマット
black src/ tests/
isort src/ tests/

# リンターチェック
ruff check src/ tests/ --fix

# テストを実行
pytest tests/ -v --cov=src/sds2roster

# コミットしてプッシュ
git add .
git commit -m "Add your feature"
git push origin feature/your-feature
```

### コーディング規約

- **PEP 8**: Python標準スタイルガイドに準拠
- **Black**: コードフォーマッター（行長：100文字）
- **isort**: インポート順序の自動整理
- **型ヒント**: すべての関数に型ヒントを使用
- **Docstring**: Google Styleでドキュメント化
- **テスト**: 新機能には必ずテストを追加
- **カバレッジ**: 最低90%のテストカバレッジを維持

### プルリクエストガイドライン

- [ ] すべてのテストが成功
- [ ] コードカバレッジが90%以上
- [ ] リンターとフォーマッターチェックに合格
- [ ] 型チェックに合格
- [ ] ドキュメントが更新されている
- [ ] CHANGELOGが更新されている（該当する場合）

## 📄 ライセンス

このプロジェクトはMITライセンスの下でライセンスされています。詳細は[LICENSE](LICENSE)ファイルを参照してください。

## 📞 サポート

問題が発生した場合：

1. [Issues](https://github.com/nahisaho/SDS2Roster/issues)で既存の問題を検索
2. 問題が見つからない場合は、新しいIssueを作成:
   - [バグレポート](.github/ISSUE_TEMPLATE/bug_report.md)
   - [機能リクエスト](.github/ISSUE_TEMPLATE/feature_request.md)
3. プロジェクトチームに連絡

## 🗺️ ロードマップ

- [x] プロジェクト構造のセットアップ
- [x] データモデルの実装
- [x] バリデーションユーティリティ
- [x] CSVパーサー/ライター
- [x] 変換ロジックの実装
- [x] CLIインターフェイス
- [x] ユニットテスト (140個)
- [x] 統合テスト (9個)
- [x] CI/CDパイプライン
- [x] Azure Blob Storage統合
- [x] Azure Table Storage統合
- [ ] Azure CLIコマンド
- [ ] パフォーマンス最適化
- [ ] 詳細なドキュメント
- [ ] 本番デプロイ

## 📊 プロジェクトステータス

- **バージョン**: 0.1.0
- **開発状態**: アクティブ開発中
- **テストカバレッジ**: 97%+
- **総テスト数**: 149個
- **Python互換性**: 3.10, 3.11, 3.12
- **安定性**: ベータ

## 🏆 品質メトリクス

| メトリクス | 値 |
|---------|-----|
| テストカバレッジ | 97%+ |
| 総テスト数 | 149 |
| ユニットテスト | 140 |
| 統合テスト | 9 |
| Python対応バージョン | 3.10+ |
| リンターエラー | 0 |
| 型チェックエラー | 0 |

## 🙏 謝辞

- [OneRoster](https://www.imsglobal.org/activity/onerosterlis) - IMS Global Learning Consortium
- [Microsoft SDS](https://sds.microsoft.com/) - School Data Sync
- **Python**: 3.10+
- **ライセンス**: MIT

---

**開発チーム** | [ドキュメント](docs/) | [Issue報告](https://github.com/yourusername/SDS2Roster/issues)
