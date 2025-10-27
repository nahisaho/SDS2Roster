# Azurite を使用したローカル開発環境のセットアップ

## 前提条件

Azurite (Azure Storage Emulator) が必要です。以下のいずれかの方法でインストール:

### 方法1: Docker (推奨)

```bash
# docker-composeで起動
docker compose up -d azurite

# または docker run
docker run -d -p 10000:10000 -p 10001:10001 -p 10002:10002 \
  --name azurite \
  mcr.microsoft.com/azure-storage/azurite
```

### 方法2: npm

```bash
# グローバルインストール
npm install -g azurite

# 起動
azurite --blobPort 10000 --queuePort 10001 --tablePort 10002
```

## Azure E2Eテストの実行

```bash
# 環境変数設定
export AZURE_STORAGE_CONNECTION_STRING="DefaultEndpointsProtocol=http;AccountName=devstoreaccount1;AccountKey=Eby8vdM02xNOcqFlqUwJPLlmEtlCDXJ1OUzFT50uSRZ6IFsuFq2UVErCz4I6tq/K1SZFPTOtr/KBHBeksoGMGw==;BlobEndpoint=http://127.0.0.1:10000/devstoreaccount1;TableEndpoint=http://127.0.0.1:10002/devstoreaccount1;"

# Azure E2Eテストを実行
pytest tests/integration/test_azure_e2e.py -v

# CLI E2Eテストを実行
pytest tests/integration/test_cli_azure_e2e.py -v

# すべての統合テストを実行
pytest tests/integration/ -v
```

## Azuriteなしでテストをスキップ

```bash
# Azure E2Eテストをスキップ
SKIP_AZURE_TESTS=true pytest tests/ -v
```

## トラブルシューティング

### Azuriteが起動しない

- ポート10000-10002が使用中でないか確認: `netstat -an | grep 10000`
- Azuriteのログを確認: `docker logs azurite`

### 接続エラー

- 接続文字列が正しいか確認
- Azuriteが起動しているか確認: `curl http://127.0.0.1:10000`
