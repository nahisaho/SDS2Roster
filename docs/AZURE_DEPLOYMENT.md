# Azure デプロイメントガイド

このガイドでは、SDS2RosterをAzure環境にデプロイする方法を詳しく説明します。

## 目次

1. [前提条件](#前提条件)
2. [Azure Storage のセットアップ](#azure-storage-のセットアップ)
3. [Azure Container Instances へのデプロイ](#azure-container-instances-へのデプロイ)
4. [Azure Container Apps へのデプロイ](#azure-container-apps-へのデプロイ)
5. [Azure Functions へのデプロイ](#azure-functions-へのデプロイ)
6. [Azure Kubernetes Service (AKS) へのデプロイ](#azure-kubernetes-service-aks-へのデプロイ)
7. [CI/CD パイプラインの設定](#cicd-パイプラインの設定)
8. [モニタリングとログ](#モニタリングとログ)

---

## 前提条件

### 必要なツール

1. **Azure CLI**: Azure リソースの管理
   ```bash
   # インストール (Ubuntu/Debian)
   curl -sL https://aka.ms/InstallAzureCLIDeb | sudo bash
   
   # インストール (macOS)
   brew update && brew install azure-cli
   
   # バージョン確認
   az --version
   ```

2. **Docker**: コンテナイメージのビルド
   ```bash
   docker --version  # 20.10以上推奨
   ```

3. **Git**: ソースコードの管理
   ```bash
   git --version
   ```

### Azure アカウント

1. Azureアカウントにログイン:
   ```bash
   az login
   ```

2. サブスクリプションを設定:
   ```bash
   # サブスクリプション一覧を表示
   az account list --output table
   
   # デフォルトサブスクリプションを設定
   az account set --subscription "<サブスクリプション名またはID>"
   ```

3. リソースグループを作成:
   ```bash
   az group create \
     --name sds2roster-rg \
     --location japaneast
   ```

---

## Azure Storage のセットアップ

### 1. Storage Account の作成

```bash
# Storage Account 作成
az storage account create \
  --name sds2rosterstorage \
  --resource-group sds2roster-rg \
  --location japaneast \
  --sku Standard_LRS \
  --kind StorageV2 \
  --allow-blob-public-access false

# 接続文字列を取得
STORAGE_CONNECTION_STRING=$(az storage account show-connection-string \
  --name sds2rosterstorage \
  --resource-group sds2roster-rg \
  --output tsv)

echo $STORAGE_CONNECTION_STRING
```

### 2. Blob Container の作成

```bash
# Blob Container 作成
az storage container create \
  --name sds2roster \
  --account-name sds2rosterstorage \
  --auth-mode login

# または接続文字列を使用
az storage container create \
  --name sds2roster \
  --connection-string "$STORAGE_CONNECTION_STRING"
```

### 3. Table Storage の作成

```bash
# Table作成 (SDKまたはポータルから)
# Python SDKを使用する場合:
python -c "
from azure.data.tables import TableServiceClient
service = TableServiceClient.from_connection_string('$STORAGE_CONNECTION_STRING')
service.create_table('conversions')
print('Table created successfully')
"
```

### 4. アクセス権限の設定

```bash
# 自分のユーザーにStorage Blob Data Contributor権限を付与
USER_OBJECT_ID=$(az ad signed-in-user show --query id -o tsv)

az role assignment create \
  --role "Storage Blob Data Contributor" \
  --assignee $USER_OBJECT_ID \
  --scope /subscriptions/<subscription-id>/resourceGroups/sds2roster-rg/providers/Microsoft.Storage/storageAccounts/sds2rosterstorage

# Storage Table Data Contributor権限も付与
az role assignment create \
  --role "Storage Table Data Contributor" \
  --assignee $USER_OBJECT_ID \
  --scope /subscriptions/<subscription-id>/resourceGroups/sds2roster-rg/providers/Microsoft.Storage/storageAccounts/sds2rosterstorage
```

---

## Azure Container Instances へのデプロイ

### 1. Azure Container Registry (ACR) の作成

```bash
# ACR作成
az acr create \
  --name sds2rosteracr \
  --resource-group sds2roster-rg \
  --sku Basic \
  --location japaneast

# ACRログインを有効化
az acr update --name sds2rosteracr --admin-enabled true

# 認証情報を取得
ACR_USERNAME=$(az acr credential show --name sds2rosteracr --query username -o tsv)
ACR_PASSWORD=$(az acr credential show --name sds2rosteracr --query passwords[0].value -o tsv)
```

### 2. Dockerイメージのビルドとプッシュ

```bash
# ACRにログイン
az acr login --name sds2rosteracr

# Dockerイメージをビルド
docker build -t sds2roster:latest .

# タグ付け
docker tag sds2roster:latest sds2rosteracr.azurecr.io/sds2roster:latest

# プッシュ
docker push sds2rosteracr.azurecr.io/sds2roster:latest

# イメージを確認
az acr repository list --name sds2rosteracr --output table
```

### 3. Container Instance の作成

```bash
# Container Instance作成
az container create \
  --resource-group sds2roster-rg \
  --name sds2roster-aci \
  --image sds2rosteracr.azurecr.io/sds2roster:latest \
  --registry-login-server sds2rosteracr.azurecr.io \
  --registry-username $ACR_USERNAME \
  --registry-password $ACR_PASSWORD \
  --environment-variables \
    AZURE_STORAGE_CONNECTION_STRING="$STORAGE_CONNECTION_STRING" \
    AZURE_CONTAINER_NAME="sds2roster" \
    AZURE_TABLE_NAME="conversions" \
  --secure-environment-variables \
    AZURE_STORAGE_CONNECTION_STRING="$STORAGE_CONNECTION_STRING" \
  --cpu 2 \
  --memory 4 \
  --restart-policy OnFailure

# ステータス確認
az container show \
  --resource-group sds2roster-rg \
  --name sds2roster-aci \
  --query "{Status:instanceView.state, IP:ipAddress.ip}" \
  --output table

# ログ確認
az container logs \
  --resource-group sds2roster-rg \
  --name sds2roster-aci
```

### 4. 変換ジョブの実行

```bash
# コンテナでコマンドを実行
az container exec \
  --resource-group sds2roster-rg \
  --name sds2roster-aci \
  --exec-command "sds2roster convert /data/input /data/output"
```

---

## Azure Container Apps へのデプロイ

### 1. Container Apps 環境の作成

```bash
# Azure Container Apps 拡張機能をインストール
az extension add --name containerapp --upgrade

# Container Apps環境を作成
az containerapp env create \
  --name sds2roster-env \
  --resource-group sds2roster-rg \
  --location japaneast

# Log Analytics Workspaceを確認
az monitor log-analytics workspace list \
  --resource-group sds2roster-rg \
  --output table
```

### 2. Container App の作成

```bash
# Container App作成
az containerapp create \
  --name sds2roster-app \
  --resource-group sds2roster-rg \
  --environment sds2roster-env \
  --image sds2rosteracr.azurecr.io/sds2roster:latest \
  --registry-server sds2rosteracr.azurecr.io \
  --registry-username $ACR_USERNAME \
  --registry-password $ACR_PASSWORD \
  --secrets \
    storage-connection-string="$STORAGE_CONNECTION_STRING" \
  --env-vars \
    AZURE_STORAGE_CONNECTION_STRING=secretref:storage-connection-string \
    AZURE_CONTAINER_NAME="sds2roster" \
    AZURE_TABLE_NAME="conversions" \
  --cpu 2.0 \
  --memory 4.0Gi \
  --min-replicas 0 \
  --max-replicas 10 \
  --scale-rule-name azure-queue \
  --scale-rule-type azure-queue \
  --scale-rule-metadata \
    queueName=conversion-jobs \
    queueLength=10 \
    connectionFromEnv=AZURE_STORAGE_CONNECTION_STRING

# アプリのURLを取得
az containerapp show \
  --name sds2roster-app \
  --resource-group sds2roster-rg \
  --query properties.configuration.ingress.fqdn \
  --output tsv
```

### 3. ジョブとして実行 (推奨)

```bash
# Container Apps Job作成
az containerapp job create \
  --name sds2roster-job \
  --resource-group sds2roster-rg \
  --environment sds2roster-env \
  --trigger-type Manual \
  --image sds2rosteracr.azurecr.io/sds2roster:latest \
  --registry-server sds2rosteracr.azurecr.io \
  --registry-username $ACR_USERNAME \
  --registry-password $ACR_PASSWORD \
  --secrets storage-connection-string="$STORAGE_CONNECTION_STRING" \
  --env-vars \
    AZURE_STORAGE_CONNECTION_STRING=secretref:storage-connection-string \
  --cpu 2.0 \
  --memory 4.0Gi \
  --command "sds2roster" "convert" "/data/input" "/data/output"

# ジョブ実行
az containerapp job start \
  --name sds2roster-job \
  --resource-group sds2roster-rg

# 実行履歴確認
az containerapp job execution list \
  --name sds2roster-job \
  --resource-group sds2roster-rg \
  --output table
```

---

## Azure Functions へのデプロイ

### 1. Function App の作成

```bash
# Function App用のStorage Account作成
az storage account create \
  --name sds2rosterfunc \
  --resource-group sds2roster-rg \
  --location japaneast \
  --sku Standard_LRS

# Function App作成 (Python 3.11)
az functionapp create \
  --name sds2roster-func \
  --resource-group sds2roster-rg \
  --storage-account sds2rosterfunc \
  --consumption-plan-location japaneast \
  --runtime python \
  --runtime-version 3.11 \
  --functions-version 4 \
  --os-type Linux

# Application Insightsを有効化
az monitor app-insights component create \
  --app sds2roster-insights \
  --location japaneast \
  --resource-group sds2roster-rg \
  --application-type web

APPINSIGHTS_KEY=$(az monitor app-insights component show \
  --app sds2roster-insights \
  --resource-group sds2roster-rg \
  --query instrumentationKey -o tsv)

az functionapp config appsettings set \
  --name sds2roster-func \
  --resource-group sds2roster-rg \
  --settings \
    APPINSIGHTS_INSTRUMENTATIONKEY=$APPINSIGHTS_KEY \
    AZURE_STORAGE_CONNECTION_STRING="$STORAGE_CONNECTION_STRING" \
    AZURE_CONTAINER_NAME="sds2roster" \
    AZURE_TABLE_NAME="conversions"
```

### 2. Function コードの作成

プロジェクト構造:
```
sds2roster-function/
├── host.json
├── requirements.txt
├── convert/
│   ├── __init__.py
│   └── function.json
└── local.settings.json
```

**convert/__init__.py**:
```python
import logging
import azure.functions as func
from sds2roster.converter import SDSToOneRosterConverter
from sds2roster.loaders import load_sds_data
from sds2roster.writers import write_oneroster_data
from sds2roster.azure.blob_storage import BlobStorageClient
from sds2roster.azure.table_storage import TableStorageClient
import os
from tempfile import TemporaryDirectory

def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('SDS2Roster conversion function triggered')

    try:
        # パラメータ取得
        input_path = req.params.get('input_path')
        output_path = req.params.get('output_path')
        
        if not input_path or not output_path:
            return func.HttpResponse(
                "Please specify 'input_path' and 'output_path' parameters",
                status_code=400
            )

        # Azure Storage クライアント初期化
        connection_string = os.environ['AZURE_STORAGE_CONNECTION_STRING']
        blob_client = BlobStorageClient(
            connection_string=connection_string,
            container_name=os.environ['AZURE_CONTAINER_NAME']
        )
        table_client = TableStorageClient(
            connection_string=connection_string,
            table_name=os.environ['AZURE_TABLE_NAME']
        )

        # 変換開始ログ
        conversion_id = table_client.log_conversion(
            source_type='SDS',
            output_path=output_path,
            status='InProgress'
        )

        # 一時ディレクトリで処理
        with TemporaryDirectory() as tmp_dir:
            # 入力データをダウンロード
            local_input = f"{tmp_dir}/input"
            local_output = f"{tmp_dir}/output"
            blob_client.download_directory(input_path, local_input)

            # データ変換
            sds_data = load_sds_data(local_input)
            converter = SDSToOneRosterConverter()
            oneroster_data = converter.convert(sds_data)
            result = write_oneroster_data(oneroster_data, local_output)

            # 結果をアップロード
            blob_client.upload_directory(local_output, output_path)

            # エンティティ数をログ
            table_client.log_entity_counts(conversion_id, result)
            table_client.update_conversion_status(conversion_id, 'Success')

            return func.HttpResponse(
                f"Conversion completed successfully. Conversion ID: {conversion_id}",
                status_code=200
            )

    except Exception as e:
        logging.error(f"Conversion failed: {str(e)}")
        if 'conversion_id' in locals():
            table_client.update_conversion_status(
                conversion_id,
                'Failed',
                error_message=str(e)
            )
        return func.HttpResponse(
            f"Conversion failed: {str(e)}",
            status_code=500
        )
```

**convert/function.json**:
```json
{
  "scriptFile": "__init__.py",
  "bindings": [
    {
      "authLevel": "function",
      "type": "httpTrigger",
      "direction": "in",
      "name": "req",
      "methods": ["get", "post"]
    },
    {
      "type": "http",
      "direction": "out",
      "name": "$return"
    }
  ]
}
```

**requirements.txt**:
```txt
azure-functions
sds2roster
```

### 3. デプロイ

```bash
# プロジェクトディレクトリに移動
cd sds2roster-function

# デプロイ
func azure functionapp publish sds2roster-func

# Function URLを取得
FUNCTION_URL=$(az functionapp function show \
  --name sds2roster-func \
  --resource-group sds2roster-rg \
  --function-name convert \
  --query invokeUrlTemplate -o tsv)

echo "Function URL: $FUNCTION_URL"

# テスト実行
curl "$FUNCTION_URL?input_path=input/&output_path=output/" \
  -H "x-functions-key: <function-key>"
```

---

## Azure Kubernetes Service (AKS) へのデプロイ

### 1. AKS クラスターの作成

```bash
# AKS作成
az aks create \
  --resource-group sds2roster-rg \
  --name sds2roster-aks \
  --node-count 2 \
  --node-vm-size Standard_D2s_v3 \
  --enable-managed-identity \
  --generate-ssh-keys \
  --attach-acr sds2rosteracr

# kubectl設定
az aks get-credentials \
  --resource-group sds2roster-rg \
  --name sds2roster-aks

# クラスター確認
kubectl get nodes
```

### 2. Kubernetes マニフェストの作成

**k8s/namespace.yaml**:
```yaml
apiVersion: v1
kind: Namespace
metadata:
  name: sds2roster
```

**k8s/secret.yaml**:
```yaml
apiVersion: v1
kind: Secret
metadata:
  name: azure-storage-secret
  namespace: sds2roster
type: Opaque
stringData:
  connection-string: "<AZURE_STORAGE_CONNECTION_STRING>"
```

**k8s/job.yaml**:
```yaml
apiVersion: batch/v1
kind: Job
metadata:
  name: sds2roster-conversion
  namespace: sds2roster
spec:
  template:
    spec:
      containers:
      - name: sds2roster
        image: sds2rosteracr.azurecr.io/sds2roster:latest
        command: ["sds2roster", "convert", "/data/input", "/data/output"]
        env:
        - name: AZURE_STORAGE_CONNECTION_STRING
          valueFrom:
            secretKeyRef:
              name: azure-storage-secret
              key: connection-string
        - name: AZURE_CONTAINER_NAME
          value: "sds2roster"
        - name: AZURE_TABLE_NAME
          value: "conversions"
        resources:
          requests:
            memory: "2Gi"
            cpu: "1000m"
          limits:
            memory: "4Gi"
            cpu: "2000m"
      restartPolicy: OnFailure
  backoffLimit: 3
```

**k8s/cronjob.yaml** (定期実行用):
```yaml
apiVersion: batch/v1
kind: CronJob
metadata:
  name: sds2roster-scheduled
  namespace: sds2roster
spec:
  schedule: "0 2 * * *"  # 毎日午前2時
  jobTemplate:
    spec:
      template:
        spec:
          containers:
          - name: sds2roster
            image: sds2rosteracr.azurecr.io/sds2roster:latest
            command: ["sds2roster", "convert", "/data/input", "/data/output"]
            env:
            - name: AZURE_STORAGE_CONNECTION_STRING
              valueFrom:
                secretKeyRef:
                  name: azure-storage-secret
                  key: connection-string
          restartPolicy: OnFailure
```

### 3. デプロイ

```bash
# NamespaceとSecret作成
kubectl apply -f k8s/namespace.yaml
kubectl apply -f k8s/secret.yaml

# Jobデプロイ
kubectl apply -f k8s/job.yaml

# Job状態確認
kubectl get jobs -n sds2roster
kubectl get pods -n sds2roster

# ログ確認
kubectl logs -n sds2roster job/sds2roster-conversion

# CronJob設定 (定期実行)
kubectl apply -f k8s/cronjob.yaml
kubectl get cronjobs -n sds2roster
```

---

## CI/CD パイプラインの設定

### GitHub Actions ワークフロー

**.github/workflows/deploy-azure.yml**:
```yaml
name: Deploy to Azure

on:
  push:
    branches: [ main ]
    tags: [ 'v*' ]
  workflow_dispatch:

env:
  ACR_NAME: sds2rosteracr
  IMAGE_NAME: sds2roster

jobs:
  build-and-push:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v4
    
    - name: Azure Login
      uses: azure/login@v1
      with:
        creds: ${{ secrets.AZURE_CREDENTIALS }}
    
    - name: ACR Login
      run: |
        az acr login --name ${{ env.ACR_NAME }}
    
    - name: Build and Push Docker Image
      run: |
        IMAGE_TAG=${GITHUB_SHA::8}
        docker build -t ${{ env.ACR_NAME }}.azurecr.io/${{ env.IMAGE_NAME }}:$IMAGE_TAG .
        docker build -t ${{ env.ACR_NAME }}.azurecr.io/${{ env.IMAGE_NAME }}:latest .
        docker push ${{ env.ACR_NAME }}.azurecr.io/${{ env.IMAGE_NAME }}:$IMAGE_TAG
        docker push ${{ env.ACR_NAME }}.azurecr.io/${{ env.IMAGE_NAME }}:latest
    
    - name: Update Container App
      run: |
        az containerapp update \
          --name sds2roster-app \
          --resource-group sds2roster-rg \
          --image ${{ env.ACR_NAME }}.azurecr.io/${{ env.IMAGE_NAME }}:${GITHUB_SHA::8}
```

### Azure DevOps パイプライン

**azure-pipelines.yml**:
```yaml
trigger:
- main

pool:
  vmImage: 'ubuntu-latest'

variables:
  acrName: 'sds2rosteracr'
  imageName: 'sds2roster'
  resourceGroup: 'sds2roster-rg'

stages:
- stage: Build
  jobs:
  - job: BuildImage
    steps:
    - task: Docker@2
      inputs:
        containerRegistry: 'ACRServiceConnection'
        repository: $(imageName)
        command: 'buildAndPush'
        Dockerfile: '**/Dockerfile'
        tags: |
          $(Build.BuildId)
          latest

- stage: Deploy
  dependsOn: Build
  jobs:
  - deployment: DeployToAzure
    environment: 'production'
    strategy:
      runOnce:
        deploy:
          steps:
          - task: AzureCLI@2
            inputs:
              azureSubscription: 'AzureServiceConnection'
              scriptType: 'bash'
              scriptLocation: 'inlineScript'
              inlineScript: |
                az containerapp update \
                  --name sds2roster-app \
                  --resource-group $(resourceGroup) \
                  --image $(acrName).azurecr.io/$(imageName):$(Build.BuildId)
```

---

## モニタリングとログ

### Application Insights の設定

```bash
# Application Insightsのメトリクスを確認
az monitor app-insights metrics show \
  --app sds2roster-insights \
  --resource-group sds2roster-rg \
  --metric requests/count \
  --aggregation count

# カスタムクエリ実行
az monitor app-insights query \
  --app sds2roster-insights \
  --resource-group sds2roster-rg \
  --analytics-query "requests | where timestamp > ago(1h) | summarize count() by resultCode"
```

### ログ監視

```bash
# Container Apps ログ
az containerapp logs show \
  --name sds2roster-app \
  --resource-group sds2roster-rg \
  --follow

# AKS ログ
kubectl logs -f deployment/sds2roster -n sds2roster

# Log Analytics クエリ
az monitor log-analytics query \
  --workspace <workspace-id> \
  --analytics-query "ContainerAppConsoleLogs_CL | where TimeGenerated > ago(1h) | order by TimeGenerated desc"
```

### アラート設定

```bash
# 失敗率が高い場合のアラート
az monitor metrics alert create \
  --name sds2roster-high-failure-rate \
  --resource-group sds2roster-rg \
  --scopes /subscriptions/<subscription-id>/resourceGroups/sds2roster-rg/providers/Microsoft.App/containerApps/sds2roster-app \
  --condition "avg requests/failed > 5" \
  --window-size 5m \
  --evaluation-frequency 1m \
  --action <action-group-id>
```

---

## コスト最適化

### 推奨構成

| シナリオ | 推奨サービス | 月間推定コスト |
|---------|------------|-------------|
| 小規模・不定期 | Container Instances | ¥1,000 - ¥5,000 |
| 中規模・定期実行 | Container Apps Jobs | ¥5,000 - ¥20,000 |
| 大規模・常時稼働 | AKS (2 nodes) | ¥20,000 - ¥50,000 |
| イベント駆動 | Azure Functions (Consumption) | ¥1,000 - ¥10,000 |

### コスト削減のヒント

1. **Auto-scaling**: 需要に応じた自動スケーリング
2. **Reserved Instances**: 長期利用の場合は予約インスタンス
3. **Spot Instances**: 優先度の低いワークロード用
4. **Storage tiers**: アクセス頻度に応じたストレージ階層

---

## トラブルシューティング

一般的な問題については [トラブルシューティングガイド](TROUBLESHOOTING.md) を参照してください。

Azure特有の問題:
- [Azure Container Apps トラブルシューティング](https://learn.microsoft.com/ja-jp/azure/container-apps/troubleshooting)
- [AKS トラブルシューティング](https://learn.microsoft.com/ja-jp/azure/aks/troubleshooting)
- [Azure Functions トラブルシューティング](https://learn.microsoft.com/ja-jp/azure/azure-functions/functions-diagnostics)

---

## 次のステップ

- [ユーザーガイド](USER_GUIDE.md) でCLIの使い方を確認
- [アーキテクチャドキュメント](ARCHITECTURE.md) でシステム設計を理解
- [GitHub Actions](.github/workflows/) でCI/CDを自動化

---

**最終更新**: 2025年10月
