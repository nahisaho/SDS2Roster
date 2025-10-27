# SDS2Roster ユーザーガイド

SDS2Rosterは、Microsoft School Data Sync (SDS) 形式のCSVファイルをOneRoster v1.2形式に変換するPythonツールです。

## 目次

1. [インストール](#インストール)
2. [クイックスタート](#クイックスタート)
3. [基本的な使い方](#基本的な使い方)
4. [Azure統合](#azure統合)
5. [Docker使用方法](#docker使用方法)
6. [よくある質問](#よくある質問)

---

## インストール

### 必要要件

- Python 3.10以上
- pip (Pythonパッケージマネージャー)

### 方法1: pipでインストール

```bash
pip install sds2roster
```

### 方法2: ソースからインストール

```bash
git clone https://github.com/nahisaho/SDS2Roster.git
cd SDS2Roster
pip install -e .
```

### インストールの確認

```bash
sds2roster version
```

---

## クイックスタート

### 1. SDSデータの準備

SDS形式のCSVファイルを用意します:

```
sds_data/
├── School.csv
├── Student.csv
├── Teacher.csv
├── Section.csv
└── StudentEnrollment.csv
```

### 2. 変換の実行

```bash
sds2roster convert sds_data/ output/
```

### 3. 結果の確認

```bash
ls output/
# orgs.csv
# users.csv
# courses.csv
# classes.csv
# enrollments.csv
# academicSessions.csv
# manifest.json
# userIds.json
```

---

## 基本的な使い方

### コマンド一覧

#### convert - データ変換

SDSデータをOneRoster形式に変換:

```bash
sds2roster convert <入力ディレクトリ> <出力ディレクトリ> [オプション]

# 例: 詳細ログ付きで変換
sds2roster convert ./sds_data ./output --verbose

# 例: 既存ファイルを上書き
sds2roster convert ./sds_data ./output --force
```

**オプション:**
- `-v, --verbose`: 詳細なログ出力
- `-f, --force`: 既存の出力ディレクトリを上書き

#### validate - データ検証

変換前にSDSデータを検証:

```bash
sds2roster validate <入力ディレクトリ> [オプション]

# 例: 詳細な検証レポート
sds2roster validate ./sds_data --verbose
```

**検証内容:**
- 必須ファイルの存在確認
- CSVフォーマットの妥当性
- データ整合性チェック
- 参照整合性の確認

#### version - バージョン表示

```bash
sds2roster version
```

---

## Azure統合

### Azure Storage への アップロード/ダウンロード

#### 環境変数の設定

```bash
export AZURE_STORAGE_CONNECTION_STRING="DefaultEndpointsProtocol=https;AccountName=<アカウント名>;AccountKey=<アクセスキー>;EndpointSuffix=core.windows.net"
```

#### ファイルのアップロード

```bash
# 単一ファイル
sds2roster upload output/orgs.csv orgs.csv --container sds2roster

# ディレクトリ全体
sds2roster upload output/ converted/ --container sds2roster
```

#### ファイルのダウンロード

```bash
# 単一ファイル
sds2roster download orgs.csv ./downloaded/orgs.csv --container sds2roster

# ディレクトリ全体
sds2roster download converted/ ./downloaded/ --container sds2roster
```

### 変換履歴の記録

```bash
# 変換をログに記録
sds2roster log \
  --source SDS \
  --output /data/output \
  --status Success \
  --table conversions
```

### 変換履歴の確認

```bash
# すべてのジョブをリスト
sds2roster list-jobs --table conversions

# ステータスでフィルター
sds2roster list-jobs --table conversions --status Success

# ソースタイプでフィルター
sds2roster list-jobs --table conversions --source SDS
```

---

## Docker使用方法

### Dockerイメージのビルド

```bash
docker build -t sds2roster:latest .
```

### Dockerで変換を実行

```bash
docker run --rm \
  -v $(pwd)/sds_data:/data/input:ro \
  -v $(pwd)/output:/data/output \
  sds2roster:latest convert /data/input /data/output
```

### docker-composeで実行

```bash
# Azuriteと一緒に起動
docker-compose up -d

# 変換を実行
docker-compose run sds2roster convert /data/input /data/output
```

---

## Python APIの使用

### プログラムからの使用

```python
from sds2roster.converter import SDSToOneRosterConverter
from sds2roster.loaders import load_sds_data
from sds2roster.writers import write_oneroster_data

# SDSデータを読み込み
sds_data = load_sds_data("./sds_data")

# 変換を実行
converter = SDSToOneRosterConverter()
oneroster_data = converter.convert(sds_data)

# OneRoster形式で出力
write_oneroster_data(oneroster_data, "./output")

print(f"✓ 変換完了:")
print(f"  Organizations: {len(oneroster_data.orgs)}")
print(f"  Users: {len(oneroster_data.users)}")
print(f"  Courses: {len(oneroster_data.courses)}")
print(f"  Classes: {len(oneroster_data.classes)}")
print(f"  Enrollments: {len(oneroster_data.enrollments)}")
```

### Azure Storage APIの使用

```python
from sds2roster.azure.blob_storage import BlobStorageClient
from sds2roster.azure.table_storage import TableStorageClient

# Blob Storage クライアント
blob_client = BlobStorageClient(
    connection_string="<接続文字列>",
    container_name="sds2roster"
)

# ファイルをアップロード
blob_client.upload_file("output/orgs.csv", "orgs.csv")

# CSVデータを直接読み書き
data = [{"id": "1", "name": "School 1"}]
blob_client.write_csv_content("schools.csv", data)
schools = blob_client.read_csv_content("schools.csv")

# Table Storage クライアント
table_client = TableStorageClient(
    connection_string="<接続文字列>",
    table_name="conversions"
)

# 変換をログに記録
conversion_id = table_client.log_conversion(
    source_type="SDS",
    output_path="/data/output",
    status="Success"
)

# 統計を取得
stats = table_client.get_conversion_stats()
print(f"Total: {stats['total']}, Success: {stats['success']}")
```

---

## よくある質問

### Q: どのSDSバージョンに対応していますか?

A: Microsoft School Data Sync v2.x のCSV形式に対応しています。

### Q: 大規模なデータセットの変換にはどのくらい時間がかかりますか?

A: パフォーマンステスト結果:
- 1,000学生: 約0.05秒 (38,000レコード/秒)
- 10,000学生: 約0.34秒 (61,000レコード/秒)
- 100,000学生: 約5秒以内 (推定)

### Q: エラーが発生した場合はどうすればいいですか?

A: 
1. まず`validate`コマンドでデータを検証
2. `--verbose`オプションで詳細ログを確認
3. [トラブルシューティングガイド](TROUBLESHOOTING.md)を参照
4. それでも解決しない場合はIssueを作成

### Q: OneRosterのどのバージョンに準拠していますか?

A: OneRoster v1.2 に準拠しています。

### Q: Azure統合は必須ですか?

A: いいえ、ローカルでの変換のみの使用も可能です。Azure統合はオプション機能です。

### Q: Windows/Mac/Linuxで動作しますか?

A: はい、Python 3.10以上がインストールされていれば、すべてのOSで動作します。

---

## 次のステップ

- [アーキテクチャドキュメント](ARCHITECTURE.md) - システム設計の詳細
- [トラブルシューティング](TROUBLESHOOTING.md) - 問題解決ガイド
- [API リファレンス](../README.md#api-reference) - プログラミングAPI
- [コントリビューション](../CONTRIBUTING.md) - 開発に参加する

---

## サポート

問題や質問がある場合:
- [GitHub Issues](https://github.com/nahisaho/SDS2Roster/issues)
- [ディスカッション](https://github.com/nahisaho/SDS2Roster/discussions)
