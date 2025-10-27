# CSV Upload API仕様書

**ドキュメントバージョン**: 1.0.0  
**作成日**: 2025-10-27  
**ステータス**: Draft  
**API バージョン**: v1

---

## 📋 概要

本ドキュメントでは、OneRoster形式CSVファイルを受信するためのアップロードAPI仕様を定義します。

**目的**:
- SDS2RosterシステムからOneRoster形式CSVファイルを受信
- セキュアなファイル転送の実現
- 非同期処理によるスケーラビリティ確保

**対象読者**:
- システム開発者
- API連携担当者
- インフラエンジニア

---

## 🌐 エンドポイント概要

### ベースURL

| 環境 | URL |
|------|-----|
| 開発 | `https://api-dev.oneroster-hub.example.com` |
| ステージング | `https://api-stg.oneroster-hub.example.com` |
| Python本番 | `https://api-py.oneroster-hub.example.com` |
| JavaScript本番 | `https://api-js.oneroster-hub.example.com` |

### エンドポイント一覧

| メソッド | パス | 説明 |
|---------|------|------|
| POST | `/api/v1/upload` | CSVファイル一括アップロード |
| GET | `/api/v1/upload/{uploadId}` | アップロード状況確認 |
| GET | `/api/v1/health` | ヘルスチェック |
| GET | `/api/v1/version` | APIバージョン情報 |

---

## 🔐 認証

### 認証方式

**Entra ID Bearer Token + API Key**

```
Authorization: Bearer {entra_id_token}
X-API-Key: {api_key}
```

### Entra ID認証

**トークン取得例**:
```bash
curl -X POST https://login.microsoftonline.com/{tenant_id}/oauth2/v2.0/token \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "client_id={client_id}" \
  -d "client_secret={client_secret}" \
  -d "scope=api://oneroster-upload-api/.default" \
  -d "grant_type=client_credentials"
```

**レスポンス**:
```json
{
  "token_type": "Bearer",
  "expires_in": 3599,
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

### API Key

API Keyは事前にKey Vaultに保存され、送信側システムに配布されます。

**ヘッダー例**:
```
X-API-Key: your-api-key-here
```

---

## 📤 POST /api/v1/upload

### 概要

OneRoster形式のCSVファイルを一括アップロードします。

### リクエスト

**HTTPメソッド**: `POST`

**Content-Type**: `multipart/form-data`

**ヘッダー**:
```
Authorization: Bearer {azure_ad_token}
X-API-Key: {api_key}
Content-Type: multipart/form-data; boundary=----WebKitFormBoundary7MA4YWxkTrZu0gW
X-Request-ID: {uuid}
```

**リクエストボディ**:

| フィールド名 | 型 | 必須 | 説明 |
|------------|---|------|------|
| metadata | JSON | ✅ | メタデータ情報 |
| orgs | File | ✅ | 組織情報CSV |
| users | File | ✅ | ユーザー情報CSV |
| courses | File | ❌ | コース情報CSV |
| classes | File | ❌ | クラス情報CSV |
| enrollments | File | ❌ | 登録情報CSV |
| academicSessions | File | ❌ | 学期情報CSV |
| demographics | File | ❌ | 人口統計情報CSV |

**metadata JSON形式**:
```json
{
  "source": "sds2roster",
  "version": "python|javascript",
  "sourceDirectory": "20251027",
  "processingDate": "2025-10-27T10:30:00Z",
  "recordCounts": {
    "orgs": 150,
    "users": 2500,
    "courses": 80,
    "classes": 120,
    "enrollments": 3000
  },
  "checksum": {
    "orgs": "sha256:abc123...",
    "users": "sha256:def456..."
  }
}
```

**curlコマンド例**:
```bash
curl -X POST https://api-py.oneroster-hub.example.com/api/v1/upload \
  -H "Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGc..." \
  -H "X-API-Key: your-api-key-here" \
  -H "X-Request-ID: 550e8400-e29b-41d4-a716-446655440000" \
  -F "metadata=@metadata.json;type=application/json" \
  -F "orgs=@orgs.csv;type=text/csv" \
  -F "users=@users.csv;type=text/csv" \
  -F "courses=@courses.csv;type=text/csv" \
  -F "classes=@classes.csv;type=text/csv" \
  -F "enrollments=@enrollments.csv;type=text/csv"
```

**TypeScript実装例**:
```typescript
import axios from 'axios';
import FormData from 'form-data';
import fs from 'fs';

async function uploadFiles(
  accessToken: string,
  apiKey: string,
  files: Record<string, string>,
  metadata: any
): Promise<any> {
  const formData = new FormData();
  
  // メタデータ追加
  formData.append('metadata', JSON.stringify(metadata), {
    contentType: 'application/json'
  });
  
  // ファイル追加
  for (const [name, path] of Object.entries(files)) {
    formData.append(name, fs.createReadStream(path), {
      filename: `${name}.csv`,
      contentType: 'text/csv'
    });
  }
  
  const response = await axios.post(
    'https://api-py.oneroster-hub.example.com/api/v1/upload',
    formData,
    {
      headers: {
        'Authorization': `Bearer ${accessToken}`,
        'X-API-Key': apiKey,
        'X-Request-ID': crypto.randomUUID(),
        ...formData.getHeaders()
      },
      timeout: 300000, // 5分
      maxContentLength: Infinity,
      maxBodyLength: Infinity
    }
  );
  
  return response.data;
}
```

### レスポンス

**ステータスコード**: `202 Accepted`

**レスポンスボディ**:
```json
{
  "uploadId": "upload-20251027-103045-a1b2c3d4",
  "status": "accepted",
  "message": "Files accepted and queued for processing",
  "receivedFiles": [
    "orgs.csv",
    "users.csv",
    "courses.csv",
    "classes.csv",
    "enrollments.csv"
  ],
  "metadata": {
    "totalFiles": 5,
    "totalSize": 15728640,
    "estimatedProcessingTime": 120
  },
  "links": {
    "self": "/api/v1/upload/upload-20251027-103045-a1b2c3d4",
    "status": "/api/v1/upload/upload-20251027-103045-a1b2c3d4"
  },
  "timestamp": "2025-10-27T10:30:45Z"
}
```

### エラーレスポンス

#### 400 Bad Request
```json
{
  "error": {
    "code": "INVALID_REQUEST",
    "message": "Missing required file: orgs.csv",
    "details": [
      {
        "field": "orgs",
        "issue": "Required file not provided"
      }
    ]
  },
  "timestamp": "2025-10-27T10:30:45Z"
}
```

#### 401 Unauthorized
```json
{
  "error": {
    "code": "UNAUTHORIZED",
    "message": "Invalid or expired access token"
  },
  "timestamp": "2025-10-27T10:30:45Z"
}
```

#### 403 Forbidden
```json
{
  "error": {
    "code": "FORBIDDEN",
    "message": "Invalid API key"
  },
  "timestamp": "2025-10-27T10:30:45Z"
}
```

#### 413 Payload Too Large
```json
{
  "error": {
    "code": "PAYLOAD_TOO_LARGE",
    "message": "Total file size exceeds 100MB limit",
    "details": {
      "maxSize": 104857600,
      "actualSize": 157286400
    }
  },
  "timestamp": "2025-10-27T10:30:45Z"
}
```

#### 500 Internal Server Error
```json
{
  "error": {
    "code": "INTERNAL_ERROR",
    "message": "An unexpected error occurred",
    "requestId": "550e8400-e29b-41d4-a716-446655440000"
  },
  "timestamp": "2025-10-27T10:30:45Z"
}
```

---

## 📊 GET /api/v1/upload/{uploadId}

### 概要

アップロードされたファイルの処理状況を確認します。

### リクエスト

**HTTPメソッド**: `GET`

**パスパラメータ**:
| パラメータ | 型 | 説明 |
|-----------|---|------|
| uploadId | string | アップロードID |

**ヘッダー**:
```
Authorization: Bearer {azure_ad_token}
X-API-Key: {api_key}
```

### レスポンス

**ステータスコード**: `200 OK`

**レスポンスボディ**:
```json
{
  "uploadId": "upload-20251027-103045-a1b2c3d4",
  "status": "processing",
  "progress": {
    "current": 3,
    "total": 5,
    "percentage": 60
  },
  "files": [
    {
      "name": "orgs.csv",
      "status": "completed",
      "recordsProcessed": 150,
      "errors": 0
    },
    {
      "name": "users.csv",
      "status": "completed",
      "recordsProcessed": 2500,
      "errors": 0
    },
    {
      "name": "courses.csv",
      "status": "processing",
      "recordsProcessed": 45,
      "errors": 0
    },
    {
      "name": "classes.csv",
      "status": "pending",
      "recordsProcessed": 0,
      "errors": 0
    },
    {
      "name": "enrollments.csv",
      "status": "pending",
      "recordsProcessed": 0,
      "errors": 0
    }
  ],
  "startTime": "2025-10-27T10:30:45Z",
  "estimatedCompletion": "2025-10-27T10:32:45Z",
  "timestamp": "2025-10-27T10:31:30Z"
}
```

**ステータス値**:
- `accepted` - 受付完了、処理待ち
- `processing` - 処理中
- `completed` - 処理完了
- `failed` - 処理失敗
- `partial_success` - 一部成功

---

## 🏥 GET /api/v1/health

### 概要

APIの稼働状況を確認します。

### レスポンス

**ステータスコード**: `200 OK`

```json
{
  "status": "healthy",
  "version": "1.0.0",
  "timestamp": "2025-10-27T10:30:45Z",
  "dependencies": {
    "database": "healthy",
    "storage": "healthy",
    "queue": "healthy"
  }
}
```

---

## 📌 GET /api/v1/version

### 概要

APIバージョン情報を取得します。

### レスポンス

**ステータスコード**: `200 OK`

```json
{
  "apiVersion": "1.0.0",
  "buildDate": "2025-10-20",
  "commit": "abc123def456",
  "supportedFormats": [
    "OneRoster 1.2"
  ]
}
```

---

## 🔒 セキュリティ要件

### 1. 認証

- Azure AD Bearer Token必須
- API Key必須
- トークン有効期限: 1時間
- API Keyローテーション: 90日ごと

### 2. ファイルサイズ制限

- 1ファイル最大: 50MB
- 合計最大: 100MB
- これを超える場合は分割アップロード

### 3. ファイル形式検証

- Content-Type: `text/csv`
- 文字エンコーディング: UTF-8
- CSVヘッダー検証
- OneRoster v1.2スキーマ準拠チェック

### 4. レート制限

| クライアント種別 | リクエスト/分 | リクエスト/時 |
|---------------|--------------|--------------|
| 開発環境 | 10 | 100 |
| ステージング | 30 | 500 |
| 本番環境 | 60 | 1000 |

### 5. ネットワークセキュリティ

- HTTPS必須（TLS 1.2以上）
- Private Endpoint推奨
- IP制限可能

---

## 📝 実装ガイド

### バックエンド実装（Azure Functions）

```typescript
import { app, HttpRequest, HttpResponseInit, InvocationContext } from '@azure/functions';
import { BlobServiceClient } from '@azure/storage-blob';
import { QueueClient } from '@azure/storage-queue';
import multipart from 'parse-multipart';

app.http('uploadFiles', {
  methods: ['POST'],
  authLevel: 'anonymous',
  route: 'v1/upload',
  handler: async (request: HttpRequest, context: InvocationContext): Promise<HttpResponseInit> => {
    try {
      // 認証チェック
      const authResult = await validateAuth(request);
      if (!authResult.valid) {
        return {
          status: 401,
          jsonBody: { error: { code: 'UNAUTHORIZED', message: authResult.error } }
        };
      }
      
      // リクエストボディ解析
      const bodyBuffer = await request.arrayBuffer();
      const boundary = multipart.getBoundary(request.headers.get('content-type')!);
      const parts = multipart.Parse(Buffer.from(bodyBuffer), boundary);
      
      // メタデータ取得
      const metadataPart = parts.find(p => p.name === 'metadata');
      const metadata = JSON.parse(metadataPart!.data.toString());
      
      // uploadId生成
      const uploadId = `upload-${new Date().toISOString().replace(/[:.]/g, '-')}-${crypto.randomUUID().substring(0, 8)}`;
      
      // Blob Storageに保存
      const blobClient = BlobServiceClient.fromConnectionString(process.env.STORAGE_CONNECTION!);
      const containerClient = blobClient.getContainerClient('uploads');
      
      const uploadedFiles: string[] = [];
      
      for (const part of parts) {
        if (part.name === 'metadata') continue;
        
        const blobName = `${uploadId}/${part.filename}`;
        const blockBlobClient = containerClient.getBlockBlobClient(blobName);
        
        await blockBlobClient.upload(part.data, part.data.length, {
          blobHTTPHeaders: {
            blobContentType: 'text/csv'
          }
        });
        
        uploadedFiles.push(part.filename!);
      }
      
      // キューにメッセージ送信（非同期処理）
      const queueClient = new QueueClient(
        process.env.STORAGE_CONNECTION!,
        'file-processing-queue'
      );
      
      await queueClient.sendMessage(
        Buffer.from(JSON.stringify({
          uploadId,
          files: uploadedFiles,
          metadata
        })).toString('base64')
      );
      
      // レスポンス返却
      return {
        status: 202,
        jsonBody: {
          uploadId,
          status: 'accepted',
          message: 'Files accepted and queued for processing',
          receivedFiles: uploadedFiles,
          metadata: {
            totalFiles: uploadedFiles.length,
            totalSize: parts.reduce((sum, p) => sum + (p.data?.length || 0), 0)
          },
          links: {
            self: `/api/v1/upload/${uploadId}`,
            status: `/api/v1/upload/${uploadId}`
          },
          timestamp: new Date().toISOString()
        }
      };
      
    } catch (error) {
      context.error('Upload failed:', error);
      return {
        status: 500,
        jsonBody: {
          error: {
            code: 'INTERNAL_ERROR',
            message: 'An unexpected error occurred'
          }
        }
      };
    }
  }
});
```

---

## 🔄 シーケンス図

```mermaid
sequenceDiagram
    participant Client as SDS2Roster
    participant API as Upload API
    participant Blob as Blob Storage
    participant Queue as Storage Queue
    participant Processor as File Processor
    participant DB as Database
    
    Client->>API: POST /api/v1/upload<br/>(CSV files)
    API->>API: 認証検証
    API->>API: ファイル検証
    
    loop 各ファイル
        API->>Blob: ファイル保存
    end
    
    API->>Queue: 処理キュー登録
    API-->>Client: 202 Accepted<br/>(uploadId)
    
    Queue->>Processor: メッセージ取得
    
    loop 各ファイル
        Processor->>Blob: ファイル読み込み
        Processor->>Processor: データ処理
        Processor->>DB: データ保存
    end
    
    Processor->>DB: ステータス更新（completed）
    
    Client->>API: GET /api/v1/upload/{uploadId}
    API->>DB: ステータス取得
    API-->>Client: 200 OK<br/>(status: completed)
```

---

## 📋 テストケース

### 正常系

1. **必須ファイルのみアップロード**
   - orgs.csv, users.csv
   - 期待結果: 202 Accepted

2. **全ファイルアップロード**
   - 7つすべてのCSVファイル
   - 期待結果: 202 Accepted

3. **ステータス確認**
   - GET /api/v1/upload/{uploadId}
   - 期待結果: 200 OK with progress

### 異常系

1. **必須ファイル欠落**
   - users.csvのみ
   - 期待結果: 400 Bad Request

2. **認証エラー**
   - 無効なトークン
   - 期待結果: 401 Unauthorized

3. **ファイルサイズ超過**
   - 150MBのファイル
   - 期待結果: 413 Payload Too Large

4. **不正なCSVフォーマット**
   - ヘッダー不一致
   - 期待結果: 400 Bad Request

---

## 📝 変更履歴

| バージョン | 日付 | 変更内容 |
|----------|------|---------|
| 1.0.0 | 2025-10-27 | 初版作成 |

---

**文書管理責任者**: API Architect  
**最終更新日**: 2025-10-27  
**ドキュメントステータス**: Draft
