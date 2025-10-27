# SDS2Roster アーキテクチャドキュメント

## 概要

SDS2Rosterは、Microsoft School Data Sync (SDS) 形式のCSVファイルをIMS OneRoster v1.2形式に変換するPythonベースのデータ変換ツールです。

## システム構成図

```
┌─────────────────────────────────────────────────────────────────┐
│                        SDS2Roster System                         │
└─────────────────────────────────────────────────────────────────┘

┌──────────────┐         ┌──────────────┐         ┌──────────────┐
│   SDS CSV    │────────▶│  Converter   │────────▶│  OneRoster   │
│   Files      │         │   Engine     │         │  CSV Files   │
└──────────────┘         └──────────────┘         └──────────────┘
       │                        │                         │
       │                        ▼                         │
       │                 ┌──────────────┐                │
       │                 │  Validator   │                │
       │                 └──────────────┘                │
       │                        │                         │
       ▼                        ▼                         ▼
┌──────────────────────────────────────────────────────────────────┐
│                      Azure Integration                            │
│  ┌──────────────┐           ┌──────────────┐                     │
│  │ Blob Storage │           │Table Storage │                     │
│  │   (Files)    │           │  (History)   │                     │
│  └──────────────┘           └──────────────┘                     │
└──────────────────────────────────────────────────────────────────┘
```

## レイヤーアーキテクチャ

```
┌────────────────────────────────────────────────────────────┐
│                      Presentation Layer                     │
│                                                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │     CLI      │  │  Python API  │  │    Docker    │     │
│  │   (Typer)    │  │  (Functions) │  │  Container   │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
└────────────────────────────────────────────────────────────┘
                            │
┌────────────────────────────────────────────────────────────┐
│                     Application Layer                       │
│                                                              │
│  ┌──────────────────────────────────────────────────┐      │
│  │         SDSToOneRosterConverter                  │      │
│  │  • convert()                                     │      │
│  │  • _convert_organizations()                      │      │
│  │  • _convert_users()                              │      │
│  │  • _convert_courses()                            │      │
│  │  • _convert_classes()                            │      │
│  │  • _convert_enrollments()                        │      │
│  │  • _convert_academic_sessions()                  │      │
│  └──────────────────────────────────────────────────┘      │
│                                                              │
│  ┌──────────────┐           ┌──────────────┐               │
│  │  Validator   │           │   Loaders    │               │
│  └──────────────┘           └──────────────┘               │
└────────────────────────────────────────────────────────────┘
                            │
┌────────────────────────────────────────────────────────────┐
│                       Domain Layer                          │
│                                                              │
│  ┌──────────────┐           ┌──────────────┐               │
│  │  SDS Models  │           │OneRoster     │               │
│  │  (Pydantic)  │           │Models        │               │
│  │              │           │(Pydantic)    │               │
│  │ • SDSSchool  │           │• OneRoster   │               │
│  │ • SDSStudent │           │  Org         │               │
│  │ • SDSTeacher │           │• OneRoster   │               │
│  │ • SDSSection │           │  User        │               │
│  │ • SDSEnroll  │           │• OneRoster   │               │
│  │   ment       │           │  Course      │               │
│  └──────────────┘           └──────────────┘               │
└────────────────────────────────────────────────────────────┘
                            │
┌────────────────────────────────────────────────────────────┐
│                   Infrastructure Layer                      │
│                                                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │   CSV I/O    │  │ Blob Storage │  │Table Storage │     │
│  │   (pandas)   │  │   Client     │  │   Client     │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
└────────────────────────────────────────────────────────────┘
```

## データフロー

### 1. 基本的な変換フロー

```
┌─────────────┐
│ SDS CSV     │
│ Files       │
└─────────────┘
       │
       │ load_sds_data()
       ▼
┌─────────────┐
│ SDSDataModel│
│ (Pydantic)  │
└─────────────┘
       │
       │ validate()
       ▼
┌─────────────┐
│ Validation  │
│ Success     │
└─────────────┘
       │
       │ converter.convert()
       ▼
┌─────────────┐
│OneRoster    │
│DataModel    │
└─────────────┘
       │
       │ write_oneroster_data()
       ▼
┌─────────────┐
│ OneRoster   │
│ CSV Files   │
└─────────────┘
```

### 2. データマッピング詳細

```
SDS Models                    OneRoster Models
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

SDSSchool                    OneRosterOrg
  ├─ SIS_ID         ────────▶  sourcedId
  ├─ Name           ────────▶  name
  ├─ School_Number  ────────▶  identifier
  └─ ...            ────────▶  type: "school"

SDSStudent                   OneRosterUser
  ├─ SIS_ID         ────────▶  sourcedId
  ├─ Username       ────────▶  username
  ├─ First_Name +            
  │  Last_Name      ────────▶  givenName, familyName
  ├─ Email          ────────▶  email
  ├─ School_SIS_ID  ────────▶  orgSourcedIds[]
  └─ ...            ────────▶  role: "student"

SDSTeacher                   OneRosterUser
  ├─ SIS_ID         ────────▶  sourcedId
  ├─ Username       ────────▶  username
  ├─ First_Name +
  │  Last_Name      ────────▶  givenName, familyName
  ├─ Email          ────────▶  email
  ├─ School_SIS_ID  ────────▶  orgSourcedIds[]
  └─ ...            ────────▶  role: "teacher"

SDSSection                   OneRosterClass + OneRosterCourse
  ├─ SIS_ID         ────────▶  class.sourcedId
  ├─ Section_Name   ────────▶  class.title, course.title
  ├─ Section_Number ────────▶  class.classCode
  ├─ Course_Subject ────────▶  course.courseCode
  ├─ Term_*         ────────▶  academicSession.*
  └─ School_SIS_ID  ────────▶  class.schoolSourcedId

SDSEnrollment                OneRosterEnrollment
  ├─ Section_SIS_ID ────────▶  classSourcedId
  ├─ SIS_ID         ────────▶  userSourcedId
  └─ Role           ────────▶  role
```

### 3. Azure統合フロー

```
┌────────────────────────────────────────────────────────┐
│                  Local Processing                       │
│                                                         │
│  ┌──────────┐   convert   ┌──────────┐                │
│  │   SDS    │────────────▶│OneRoster │                │
│  │   Data   │             │   Data   │                │
│  └──────────┘             └──────────┘                │
│                                  │                      │
└──────────────────────────────────┼──────────────────────┘
                                   │
                                   ▼
┌────────────────────────────────────────────────────────┐
│              Azure Blob Storage                         │
│                                                         │
│  upload_file() / upload_directory()                    │
│       │                                                 │
│       ├─ orgs.csv                                       │
│       ├─ users.csv                                      │
│       ├─ courses.csv                                    │
│       ├─ classes.csv                                    │
│       ├─ enrollments.csv                                │
│       └─ academicSessions.csv                           │
└────────────────────────────────────────────────────────┘
                    │
                    ▼
┌────────────────────────────────────────────────────────┐
│            Azure Table Storage                          │
│                                                         │
│  log_conversion()                                       │
│       │                                                 │
│       ├─ conversion_id (PartitionKey)                   │
│       ├─ timestamp (RowKey)                             │
│       ├─ source_type                                    │
│       ├─ status                                         │
│       ├─ output_path                                    │
│       └─ entity_counts                                  │
└────────────────────────────────────────────────────────┘
```

## コンポーネント詳細

### 1. Converter (変換エンジン)

**ファイル**: `src/sds2roster/converter.py`

**責任**:
- SDSデータモデルをOneRosterデータモデルに変換
- データマッピングロジックの実装
- GUID生成とメタデータ作成

**主要メソッド**:
```python
class SDSToOneRosterConverter:
    def convert(self, sds_data: SDSDataModel) -> OneRosterDataModel
    def _convert_organizations(self, sds_data: SDSDataModel) -> list[OneRosterOrg]
    def _convert_users(self, sds_data: SDSDataModel) -> list[OneRosterUser]
    def _convert_courses(self, sds_data: SDSDataModel) -> list[OneRosterCourse]
    def _convert_classes(self, sds_data: SDSDataModel) -> list[OneRosterClass]
    def _convert_enrollments(self, sds_data: SDSDataModel) -> list[OneRosterEnrollment]
    def _convert_academic_sessions(self, sds_data: SDSDataModel) -> list[OneRosterAcademicSession]
```

### 2. Loaders (データ読み込み)

**ファイル**: `src/sds2roster/loaders.py`

**責任**:
- CSV形式のSDSデータを読み込み
- Pydanticモデルへの変換
- データ検証

**主要関数**:
```python
def load_sds_data(input_dir: str | Path) -> SDSDataModel
def load_csv_to_model(csv_path: Path, model_class: Type[BaseModel]) -> list
```

### 3. Writers (データ書き込み)

**ファイル**: `src/sds2roster/writers.py`

**責任**:
- OneRosterデータをCSV形式で出力
- manifest.json と userIds.json の生成
- ファイルシステムへの書き込み

**主要関数**:
```python
def write_oneroster_data(data: OneRosterDataModel, output_dir: str | Path) -> Dict[str, int]
def write_csv_from_models(file_path: Path, models: list[BaseModel]) -> None
```

### 4. Azure Blob Storage Client

**ファイル**: `src/sds2roster/azure/blob_storage.py`

**責任**:
- Azure Blob Storageへのファイルアップロード/ダウンロード
- CSVデータの直接読み書き
- ディレクトリの一括操作

**主要メソッド**:
```python
class BlobStorageClient:
    def upload_file(self, local_path: str | Path, blob_name: str) -> None
    def download_file(self, blob_name: str, local_path: str | Path) -> None
    def upload_directory(self, local_dir: str | Path, blob_prefix: str) -> List[str]
    def download_directory(self, blob_prefix: str, local_dir: str | Path) -> List[str]
    def read_csv_content(self, blob_name: str) -> List[Dict[str, str]]
    def write_csv_content(self, blob_name: str, data: List[Dict[str, str]]) -> None
    def list_blobs(self, prefix: str = "") -> List[str]
    def delete_blob(self, blob_name: str) -> None
    def blob_exists(self, blob_name: str) -> bool
```

### 5. Azure Table Storage Client

**ファイル**: `src/sds2roster/azure/table_storage.py`

**責任**:
- 変換履歴の記録
- 統計情報の管理
- 変換ジョブの追跡

**主要メソッド**:
```python
class TableStorageClient:
    def log_conversion(self, source_type: str, output_path: str, status: str, error_message: Optional[str] = None) -> str
    def update_conversion_status(self, conversion_id: str, status: str, error_message: Optional[str] = None) -> None
    def get_conversion(self, conversion_id: str) -> Optional[Dict[str, Any]]
    def list_conversions(self, source_type: Optional[str] = None, status: Optional[str] = None, limit: int = 100) -> List[Dict[str, Any]]
    def get_conversion_stats(self) -> Dict[str, int]
    def log_entity_counts(self, conversion_id: str, entity_counts: Dict[str, int]) -> None
    def delete_conversion(self, conversion_id: str) -> None
    def cleanup_old_records(self, days: int = 30) -> int
```

### 6. CLI (コマンドラインインターフェース)

**ファイル**: `src/sds2roster/cli.py`

**責任**:
- ユーザーコマンドの処理
- 引数の解析とバリデーション
- プログレス表示とログ出力

**主要コマンド**:
```bash
sds2roster convert <input> <output>     # データ変換
sds2roster validate <input>              # データ検証
sds2roster version                       # バージョン表示
sds2roster upload <source> <dest>        # Azureアップロード
sds2roster download <source> <dest>      # Azureダウンロード
sds2roster log [options]                 # 変換履歴記録
sds2roster list-jobs [options]           # ジョブ一覧表示
```

## データモデル

### SDS (入力)

```python
class SDSDataModel(BaseModel):
    schools: List[SDSSchool]           # 学校情報
    students: List[SDSStudent]         # 生徒情報
    teachers: List[SDSTeacher]         # 教師情報
    sections: List[SDSSection]         # セクション(クラス)情報
    enrollments: List[SDSEnrollment]   # 在籍情報
```

### OneRoster (出力)

```python
class OneRosterDataModel(BaseModel):
    orgs: List[OneRosterOrg]                           # 組織(学校)
    users: List[OneRosterUser]                         # ユーザー(生徒・教師)
    courses: List[OneRosterCourse]                     # コース
    classes: List[OneRosterClass]                      # クラス
    enrollments: List[OneRosterEnrollment]             # 在籍情報
    academic_sessions: List[OneRosterAcademicSession]  # 学期情報
```

## デプロイメントオプション

### 1. ローカル実行

```bash
pip install sds2roster
sds2roster convert input/ output/
```

### 2. Docker実行

```bash
docker build -t sds2roster:latest .
docker run -v ./data:/data sds2roster convert /data/input /data/output
```

### 3. Docker Compose (開発環境)

```bash
docker-compose up -d
docker-compose run sds2roster convert /data/input /data/output
```

### 4. Azure Container Instances (クラウド)

```bash
az container create \
  --resource-group myResourceGroup \
  --name sds2roster \
  --image myregistry.azurecr.io/sds2roster:latest \
  --environment-variables \
    AZURE_STORAGE_CONNECTION_STRING=<connection-string>
```

### 5. Azure Functions (サーバーレス)

```python
import azure.functions as func
from sds2roster.converter import SDSToOneRosterConverter
from sds2roster.loaders import load_sds_data
from sds2roster.writers import write_oneroster_data

def main(req: func.HttpRequest) -> func.HttpResponse:
    # Blob Storageからデータ読み込み
    # 変換実行
    # 結果をBlob Storageに保存
    return func.HttpResponse("Conversion completed")
```

## パフォーマンス特性

### ベンチマーク結果

| データセット | 処理時間 | スループット | メモリ使用量 |
|------------|---------|------------|------------|
| 1K 学生    | 0.05秒  | 38K rec/s  | < 50MB     |
| 10K 学生   | 0.34秒  | 61K rec/s  | < 150MB    |
| 100K 学生  | ~5秒    | ~50K rec/s | < 500MB    |

### スケーラビリティ

- **水平スケーリング**: 複数インスタンスでの並列処理可能
- **垂直スケーリング**: メモリ効率的な設計により大規模データ対応
- **非同期処理**: Azure Functionsでのイベント駆動処理対応

## セキュリティ考慮事項

### 1. 認証と認可

- **Azure Storage**: 接続文字列またはManaged Identity
- **アクセス制御**: RBACによる細かい権限管理
- **環境変数**: 機密情報の安全な管理

### 2. データ保護

- **転送時の暗号化**: HTTPS/TLS通信
- **保存時の暗号化**: Azure Storage Service Encryption
- **データ検証**: Pydanticによる入力検証

### 3. ログとモニタリング

- **変換履歴**: Azure Table Storageに記録
- **エラーログ**: 詳細なエラー情報の保存
- **監査証跡**: すべての操作を追跡可能

## 拡張性

### カスタムマッピングの追加

```python
from sds2roster.converter import SDSToOneRosterConverter

class CustomConverter(SDSToOneRosterConverter):
    def _convert_users(self, sds_data):
        # カスタムロジック
        users = super()._convert_users(sds_data)
        # 追加処理
        return users
```

### プラグインアーキテクチャ

将来的にプラグインシステムを実装予定:
- カスタムバリデーター
- カスタムライター
- カスタム変換ルール

## 技術スタック

| レイヤー | 技術 |
|---------|------|
| 言語 | Python 3.10+ |
| データ検証 | Pydantic 2.x |
| CSV処理 | pandas |
| CLI | Typer + Rich |
| Azure SDK | azure-storage-blob, azure-data-tables, azure-identity |
| テスト | pytest + pytest-cov + pytest-mock |
| CI/CD | GitHub Actions |
| コンテナ | Docker + Docker Compose |
| 品質管理 | black, isort, ruff, mypy |

## 参考資料

- [Microsoft SDS Documentation](https://docs.microsoft.com/en-us/schooldatasync/)
- [IMS OneRoster v1.2 Specification](https://www.imsglobal.org/oneroster-v12-final-specification)
- [Azure Storage Documentation](https://docs.microsoft.com/en-us/azure/storage/)
- [Pydantic Documentation](https://docs.pydantic.dev/)
