# 統合テストガイド

## ローカル統合テスト（Azureなし）

Azure接続が不要なエンドツーエンドテスト:

```bash
# ローカル統合テストのみ実行
pytest tests/integration/test_end_to_end.py -v

# または、Azureテストを除外して実行
pytest tests/integration/ -m "not azure" -v
```

## Azure統合テスト（Azurite必須）

### 前提条件

Azurite (Azure Storage Emulator) が必要です。以下のいずれかの方法でインストール:

#### 方法1: Docker (推奨)

```bash
# docker-composeで起動
docker compose up -d azurite

# または docker run
docker run -d -p 10000:10000 -p 10001:10001 -p 10002:10002 \
  --name azurite \
  mcr.microsoft.com/azure-storage/azurite
```

#### 方法2: npm

```bash
# グローバルインストール
npm install -g azurite

# 起動
azurite --blobPort 10000 --queuePort 10001 --tablePort 10002
```

### Azure E2Eテストの実行

```bash
# Azureテストのみ実行（Azuriteが起動している必要があります）
pytest -m azure -v

# 個別にAzure E2Eテストを実行
pytest tests/integration/test_azure_e2e.py -v

# CLI Azure E2Eテストを実行
pytest tests/integration/test_cli_azure_e2e.py -v
```

### テストマーカーの使用

このプロジェクトでは以下のpytestマーカーを使用しています:

- `unit`: ユニットテスト
- `integration`: 統合テスト（ローカル）
- `azure`: Azure統合テスト（Azurite必須）
- `slow`: 低速テスト
- `benchmark`: パフォーマンステスト

```bash
# Azureテストを除外
pytest -m "not azure"

# ユニットテストのみ
pytest -m unit

# 統合テストのみ（Azureを含む）
pytest -m integration

# ローカル統合テストのみ（Azureを除く）
pytest -m "integration and not azure"
```

## トラブルシューティング

### Azuriteが起動しない

- ポート10000-10002が使用中でないか確認: `netstat -an | grep 10000`
- Azuriteのログを確認: `docker logs azurite`

### 接続エラー

- 接続文字列が正しいか確認
- Azuriteが起動しているか確認: `curl http://127.0.0.1:10000`
