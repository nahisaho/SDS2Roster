# SDS2Roster トラブルシューティングガイド

このガイドでは、SDS2Rosterの使用中に発生する可能性のある一般的な問題と解決方法を説明します。

## 目次

1. [インストールの問題](#インストールの問題)
2. [データ変換の問題](#データ変換の問題)
3. [Azure統合の問題](#azure統合の問題)
4. [パフォーマンスの問題](#パフォーマンスの問題)
5. [Docker関連の問題](#docker関連の問題)
6. [よくあるエラーメッセージ](#よくあるエラーメッセージ)

---

## インストールの問題

### 問題: `pip install sds2roster` が失敗する

**症状**:
```bash
ERROR: Could not find a version that satisfies the requirement sds2roster
```

**解決方法**:
1. Pythonバージョンを確認:
   ```bash
   python --version  # 3.10以上が必要
   ```

2. pipをアップグレード:
   ```bash
   pip install --upgrade pip
   ```

3. ソースからインストール:
   ```bash
   git clone <repository-url>
   cd SDS2Roster
   pip install -e .
   ```

### 問題: 依存関係のインストールエラー

**症状**:
```bash
ERROR: Failed building wheel for [package-name]
```

**解決方法**:
1. ビルドツールをインストール:
   ```bash
   # Ubuntu/Debian
   sudo apt-get install python3-dev build-essential
   
   # macOS
   xcode-select --install
   
   # Windows
   # Visual Studio Build Toolsをインストール
   ```

2. 仮想環境を使用:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # Linux/Mac
   .venv\Scripts\activate     # Windows
   pip install -e .
   ```

---

## データ変換の問題

### 問題: "Required CSV file not found"

**症状**:
```
FileNotFoundError: Required CSV file not found: School.csv
```

**解決方法**:
1. 必須ファイルを確認:
   ```bash
   ls input_directory/
   # 必要: School.csv, Student.csv, Teacher.csv, Section.csv, StudentEnrollment.csv
   ```

2. ファイル名の大文字小文字を確認 (正確に一致する必要があります)

3. ファイルが空でないことを確認:
   ```bash
   wc -l input_directory/*.csv
   ```

### 問題: データ検証エラー

**症状**:
```
ValidationError: 2 validation errors for SDSSchool
  sis_id: Field required
  name: Field required
```

**解決方法**:
1. validateコマンドで詳細を確認:
   ```bash
   sds2roster validate input_directory/ --verbose
   ```

2. CSVヘッダーを確認:
   ```bash
   head -n 1 input_directory/School.csv
   ```
   期待されるヘッダー: `SIS_ID,Name,School_Number,...`

3. 必須フィールドが欠落していないか確認

4. CSVファイルのエンコーディングを確認 (UTF-8推奨):
   ```bash
   file -i input_directory/School.csv
   ```

### 問題: 変換後のデータが不完全

**症状**:
- 一部のレコードが出力されない
- 関連データが欠落している

**解決方法**:
1. 入力データの参照整合性を確認:
   ```bash
   sds2roster validate input_directory/ --verbose
   ```

2. ログで警告メッセージを確認:
   ```bash
   sds2roster convert input/ output/ --verbose 2>&1 | grep WARNING
   ```

3. SDSデータの関連性を確認:
   - 生徒の `School_SIS_ID` が `School.csv` の `SIS_ID` に存在するか
   - 在籍の `Section_SIS_ID` が `Section.csv` の `SIS_ID` に存在するか
   - 在籍の `SIS_ID` が `Student.csv` または `Teacher.csv` に存在するか

### 問題: 日付フォーマットエラー

**症状**:
```
ValueError: time data 'XX/XX/XXXX' does not match format
```

**解決方法**:
1. 日付フォーマットを確認 (期待: `YYYY-MM-DD` または `MM/DD/YYYY`)

2. Excelで開く際の自動変換に注意

3. CSVを直接編集して修正:
   ```bash
   # 例: MM/DD/YYYY → YYYY-MM-DD
   sed -i 's|01/15/2024|2024-01-15|g' input_directory/Section.csv
   ```

---

## Azure統合の問題

### 問題: Azure接続エラー

**症状**:
```
ClientAuthenticationError: Authentication failed
```

**解決方法**:
1. 接続文字列を確認:
   ```bash
   echo $AZURE_STORAGE_CONNECTION_STRING
   ```

2. 接続文字列フォーマットを確認:
   ```bash
   export AZURE_STORAGE_CONNECTION_STRING="DefaultEndpointsProtocol=https;AccountName=<name>;AccountKey=<key>;EndpointSuffix=core.windows.net"
   ```

3. ネットワーク接続を確認:
   ```bash
   ping <storage-account-name>.blob.core.windows.net
   ```

4. ファイアウォール設定を確認 (Azure Portal)

### 問題: "Container not found"

**症状**:
```
ResourceNotFoundError: The specified container does not exist
```

**解決方法**:
1. コンテナが存在するか確認:
   ```bash
   az storage container list --account-name <account-name>
   ```

2. コンテナを作成:
   ```bash
   az storage container create --name sds2roster --account-name <account-name>
   ```

3. コンテナ名のスペルを確認

### 問題: アクセス権限エラー

**症状**:
```
HttpResponseError: This request is not authorized
```

**解決方法**:
1. アクセスキーが正しいか確認

2. RBAC権限を確認:
   - Storage Blob Data Contributor
   - Storage Table Data Contributor

3. Managed Identityを使用する場合:
   ```python
   from azure.identity import DefaultAzureCredential
   
   blob_client = BlobStorageClient(
       account_url="https://<account>.blob.core.windows.net",
       credential=DefaultAzureCredential(),
       container_name="sds2roster"
   )
   ```

### 問題: Azuriteが起動しない

**症状**:
```
Error: Address already in use
```

**解決方法**:
1. ポートを確認:
   ```bash
   netstat -an | grep 10000
   lsof -i :10000
   ```

2. プロセスを停止:
   ```bash
   kill -9 <PID>
   ```

3. 別のポートを使用:
   ```bash
   azurite --blobPort 10010 --tablePort 10012
   ```

---

## パフォーマンスの問題

### 問題: 変換が遅い

**症状**:
- 大規模データセット (100K+ レコード) の処理に時間がかかる

**解決方法**:
1. データサイズを確認:
   ```bash
   wc -l input_directory/*.csv
   ```

2. メモリ使用量を監視:
   ```bash
   # 別ターミナルで実行
   watch -n 1 'ps aux | grep sds2roster'
   ```

3. チャンキング処理を有効化 (将来実装予定):
   ```python
   converter = SDSToOneRosterConverter(chunk_size=10000)
   ```

4. システムリソースを増やす:
   - より多くのRAMを割り当て
   - より高速なCPUを使用

### 問題: メモリ不足エラー

**症状**:
```
MemoryError: Unable to allocate array
```

**解決方法**:
1. 使用可能なメモリを確認:
   ```bash
   free -h  # Linux
   ```

2. スワップメモリを増やす

3. データを分割して処理:
   ```bash
   # 生徒データを分割
   split -l 50000 Student.csv student_part_
   
   # 各パートを個別に処理
   for file in student_part_*; do
     sds2roster convert input/ output_$file/
   done
   ```

---

## Docker関連の問題

### 問題: Dockerイメージビルドエラー

**症状**:
```
ERROR: failed to solve: process "/bin/sh -c pip install ." did not complete successfully
```

**解決方法**:
1. Dockerバージョンを確認:
   ```bash
   docker --version  # 20.10以上推奨
   ```

2. BuildKitを有効化:
   ```bash
   export DOCKER_BUILDKIT=1
   docker build -t sds2roster:latest .
   ```

3. キャッシュをクリア:
   ```bash
   docker builder prune -a
   ```

### 問題: docker-composeがコマンドを見つけられない

**症状**:
```
The command 'docker-compose' could not be found
```

**解決方法**:
1. Docker Compose v2を使用:
   ```bash
   docker compose up -d  # ハイフンなし
   ```

2. Docker Composeをインストール:
   ```bash
   # Linux
   sudo curl -L "https://github.com/docker/compose/releases/download/v2.20.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
   sudo chmod +x /usr/local/bin/docker-compose
   ```

### 問題: ボリュームマウントの権限エラー

**症状**:
```
PermissionError: [Errno 13] Permission denied: '/data/output'
```

**解決方法**:
1. ディレクトリの権限を確認:
   ```bash
   ls -la data/
   ```

2. 権限を修正:
   ```bash
   chmod -R 755 data/
   ```

3. Dockerコンテナのユーザーを指定:
   ```bash
   docker run --user $(id -u):$(id -g) -v ./data:/data sds2roster
   ```

---

## よくあるエラーメッセージ

### `ModuleNotFoundError: No module named 'sds2roster'`

**原因**: パッケージがインストールされていない

**解決策**:
```bash
pip install -e .
# または
pip install sds2roster
```

### `TypeError: 'NoneType' object is not subscriptable`

**原因**: 必須データが欠落している

**解決策**:
1. 入力データを検証
2. すべての必須フィールドが存在するか確認
3. NULL/空値を確認

### `UnicodeDecodeError: 'utf-8' codec can't decode`

**原因**: CSVファイルのエンコーディングがUTF-8ではない

**解決策**:
```bash
# エンコーディングを確認
file -i input_directory/School.csv

# UTF-8に変換
iconv -f ISO-8859-1 -t UTF-8 School.csv > School_utf8.csv
```

### `KeyError: 'SIS_ID'`

**原因**: CSVヘッダーが期待される形式と異なる

**解決策**:
1. ヘッダー名を確認 (大文字小文字が重要)
2. 余分なスペースや特殊文字を削除
3. BOM (Byte Order Mark) を削除:
   ```bash
   sed -i '1s/^\xEF\xBB\xBF//' School.csv
   ```

### `ResourceExistsError: The specified container already exists`

**原因**: Azureコンテナが既に存在する (通常は問題なし)

**解決策**: エラーは無視できます。または、`--force`オプションを使用

---

## デバッグ手順

### 1. 詳細ログを有効化

```bash
# CLIで詳細ログ
sds2roster convert input/ output/ --verbose

# Pythonで詳細ログ
import logging
logging.basicConfig(level=logging.DEBUG)
```

### 2. データを検証

```bash
# 変換前に検証
sds2roster validate input_directory/ --verbose

# サンプルデータでテスト
head -n 100 input_directory/Student.csv > test/Student.csv
sds2roster convert test/ output_test/
```

### 3. 環境を確認

```bash
# Pythonバージョン
python --version

# インストールされたパッケージ
pip list | grep -E "(sds2roster|pydantic|pandas|azure)"

# 環境変数
env | grep AZURE
```

### 4. テストを実行

```bash
# ユニットテスト
pytest tests/ -v

# 特定のテスト
pytest tests/test_converter.py -v

# カバレッジ付き
pytest tests/ --cov=sds2roster
```

---

## サポートを受ける前に

問題を報告する前に、以下の情報を収集してください:

1. **環境情報**:
   ```bash
   python --version
   pip list | grep sds2roster
   uname -a  # Linux/Mac
   ```

2. **エラーメッセージ**:
   - 完全なスタックトレース
   - エラーが発生したコマンド

3. **入力データ**:
   - CSVファイルの構造 (ヘッダー)
   - データサイズ
   - サンプルデータ (機密情報を除く)

4. **実行ログ**:
   ```bash
   sds2roster convert input/ output/ --verbose > debug.log 2>&1
   ```

---

## さらなるヘルプ

それでも問題が解決しない場合:

1. **ドキュメントを確認**:
   - [ユーザーガイド](USER_GUIDE.md)
   - [アーキテクチャドキュメント](ARCHITECTURE.md)
   - [README](../README.md)

2. **GitHubで検索**:
   - [Issues](https://github.com/yourusername/SDS2Roster/issues)
   - [Discussions](https://github.com/yourusername/SDS2Roster/discussions)

3. **新しいIssueを作成**:
   - 上記の情報を含める
   - 再現手順を詳しく説明
   - 期待される動作と実際の動作を明記

4. **コミュニティに質問**:
   - [GitHub Discussions](https://github.com/yourusername/SDS2Roster/discussions)
   - Stack Overflow (タグ: `sds2roster`)

---

## よくある質問と回答

### Q: Windows環境で動作しますか?

A: はい、Python 3.10以上がインストールされていれば動作します。ただし、パスの区切り文字には注意してください。

### Q: 変換にどのくらい時間がかかりますか?

A: データサイズによります:
- 1,000学生: ~0.05秒
- 10,000学生: ~0.34秒
- 100,000学生: ~5秒

### Q: クラウド環境で実行できますか?

A: はい、以下の環境で実行可能:
- Azure Functions
- Azure Container Instances
- AWS Lambda (カスタムランタイム)
- Google Cloud Run

### Q: カスタムマッピングは可能ですか?

A: はい、Converterクラスを継承してカスタマイズできます。詳細は[アーキテクチャドキュメント](ARCHITECTURE.md#拡張性)を参照。

---

**最終更新**: 2025年10月
