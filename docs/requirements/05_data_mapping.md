# SDS to OneRoster 変換ツール - データマッピング仕様

**文書バージョン**: 1.0.0  
**作成日**: 2025-10-27  
**最終更新**: 2025-10-27  
**ステータス**: Draft

---

## 1. データマッピング概要

本文書では、Microsoft School Data Sync (SDS) CSV形式からOneRoster v1.2 CSV形式へのデータマッピング仕様を定義する。

### 1.1 マッピングの原則

1. **完全性**: すべてのSDS必須フィールドをOneRosterフィールドにマッピング
2. **整合性**: エンティティ間の参照整合性を保証
3. **一意性**: sourcedId（GUID）の一意性を保証
4. **トレーサビリティ**: 元のSIS IDを保持（metadata/userIdsフィールド）
5. **準拠性**: OneRoster v1.2仕様に完全準拠

### 1.2 変換フロー

```mermaid
graph LR
    A[SDS CSV] --> B[パース]
    B --> C[バリデーション]
    C --> D[マッピング]
    D --> E[GUID生成]
    E --> F[整合性チェック]
    F --> G[OneRoster CSV]
    G --> H[検証]
    H --> I[出力]
```

---

## 2. エンティティマッピング

### 2.1 Organizations（組織）

**SDS入力**: `school.csv`  
**OneRoster出力**: `orgs.csv`

| OneRoster フィールド | 必須 | データ型 | SDS マッピング元 | 変換ルール |
|-------------------|------|---------|-----------------|----------|
| sourcedId | Yes | GUID | - | UUID v5生成（`org:{school.SIS ID}`） |
| status | Yes | Enum | - | 固定値: `"active"` |
| dateLastModified | Yes | DateTime | - | 変換実行日時（ISO 8601） |
| name | Yes | String | school.Name | そのまま使用 |
| type | Yes | Enum | - | 固定値: `"school"` |
| identifier | No | String | school.School Number | そのまま使用（存在する場合） |
| metadata | No | JSON | school.SIS ID | `{"sis_id": "{school.SIS ID}"}` |

**サンプル変換例**:

**SDS入力（school.csv）**:
```csv
SIS ID,Name,School Number
SCH001,Tokyo International School,TIS-001
SCH002,Osaka Tech High School,OTHS-002
```

**OneRoster出力（orgs.csv）**:
```csv
sourcedId,status,dateLastModified,name,type,identifier,metadata
550e8400-e29b-41d4-a716-446655440001,active,2025-10-27T10:30:00Z,Tokyo International School,school,TIS-001,"{""sis_id"":""SCH001""}"
550e8400-e29b-41d4-a716-446655440002,active,2025-10-27T10:30:00Z,Osaka Tech High School,school,OTHS-002,"{""sis_id"":""SCH002""}"
```

---

### 2.2 Users（ユーザー: 学生）

**SDS入力**: `student.csv`  
**OneRoster出力**: `users.csv`

| OneRoster フィールド | 必須 | データ型 | SDS マッピング元 | 変換ルール |
|-------------------|------|---------|-----------------|----------|
| sourcedId | Yes | GUID | - | UUID v5生成（`user:{student.SIS ID}`） |
| status | Yes | Enum | - | 固定値: `"active"` |
| dateLastModified | Yes | DateTime | - | 変換実行日時 |
| enabledUser | Yes | Boolean | - | 固定値: `true` |
| orgSourcedIds | Yes | Array[GUID] | student.School SIS ID | 組織のsourcedIdに変換 |
| role | Yes | Enum | - | 固定値: `"student"` |
| username | Yes | String | student.Username | そのまま使用 |
| userIds | No | JSON | student.SIS ID | `[{"type":"sisId","identifier":"{SIS ID}"}]` |
| givenName | Yes | String | student.First Name | そのまま使用 |
| familyName | Yes | String | student.Last Name | そのまま使用 |
| middleName | No | String | student.Middle Name | そのまま使用（存在する場合） |
| email | No | String | student.Secondary Email | そのまま使用（存在する場合） |
| sms | No | String | - | 空 |
| phone | No | String | - | 空 |
| agents | No | Array | - | 空 |
| grades | No | Array | student.Grade | 配列に変換: `["{Grade}"]` |
| password | No | String | - | 空 |

**サンプル変換例**:

**SDS入力（student.csv）**:
```csv
SIS ID,School SIS ID,Username,First Name,Last Name,Secondary Email,Grade
STU001,SCH001,taro.tanaka,Taro,Tanaka,taro@example.com,10
STU002,SCH001,hanako.sato,Hanako,Sato,hanako@example.com,11
```

**OneRoster出力（users.csv）**:
```csv
sourcedId,status,dateLastModified,enabledUser,orgSourcedIds,role,username,userIds,givenName,familyName,middleName,email,sms,phone,agents,grades,password
660e8400-e29b-41d4-a716-446655440001,active,2025-10-27T10:30:00Z,true,550e8400-e29b-41d4-a716-446655440001,student,taro.tanaka,"[{""type"":""sisId"",""identifier"":""STU001""}]",Taro,Tanaka,,taro@example.com,,,,,"[""10""]",
660e8400-e29b-41d4-a716-446655440002,active,2025-10-27T10:30:00Z,true,550e8400-e29b-41d4-a716-446655440001,student,hanako.sato,"[{""type"":""sisId"",""identifier"":""STU002""}]",Hanako,Sato,,hanako@example.com,,,,,"[""11""]",
```

---

### 2.3 Users（ユーザー: 教員）

**SDS入力**: `teacher.csv`  
**OneRoster出力**: `users.csv`（学生と同じファイル）

| OneRoster フィールド | 必須 | データ型 | SDS マッピング元 | 変換ルール |
|-------------------|------|---------|-----------------|----------|
| sourcedId | Yes | GUID | - | UUID v5生成（`user:{teacher.SIS ID}`） |
| status | Yes | Enum | - | 固定値: `"active"` |
| dateLastModified | Yes | DateTime | - | 変換実行日時 |
| enabledUser | Yes | Boolean | - | 固定値: `true` |
| orgSourcedIds | Yes | Array[GUID] | teacher.School SIS ID | 組織のsourcedIdに変換 |
| role | Yes | Enum | - | 固定値: `"teacher"` |
| username | Yes | String | teacher.Username | そのまま使用 |
| userIds | No | JSON | teacher.SIS ID | `[{"type":"sisId","identifier":"{SIS ID}"}]` |
| givenName | Yes | String | teacher.First Name | そのまま使用 |
| familyName | Yes | String | teacher.Last Name | そのまま使用 |
| middleName | No | String | teacher.Middle Name | そのまま使用（存在する場合） |
| email | No | String | teacher.Secondary Email | そのまま使用（存在する場合） |
| sms | No | String | - | 空 |
| phone | No | String | - | 空 |
| agents | No | Array | - | 空 |
| grades | No | Array | - | 空（教員には学年なし） |
| password | No | String | - | 空 |

**サンプル変換例**:

**SDS入力（teacher.csv）**:
```csv
SIS ID,School SIS ID,Username,First Name,Last Name,Secondary Email
TCH001,SCH001,jiro.yamada,Jiro,Yamada,yamada@example.com
TCH002,SCH001,yuki.suzuki,Yuki,Suzuki,suzuki@example.com
```

**OneRoster出力（users.csv）**:
```csv
sourcedId,status,dateLastModified,enabledUser,orgSourcedIds,role,username,userIds,givenName,familyName,middleName,email,sms,phone,agents,grades,password
770e8400-e29b-41d4-a716-446655440001,active,2025-10-27T10:30:00Z,true,550e8400-e29b-41d4-a716-446655440001,teacher,jiro.yamada,"[{""type"":""sisId"",""identifier"":""TCH001""}]",Jiro,Yamada,,yamada@example.com,,,,,
770e8400-e29b-41d4-a716-446655440002,active,2025-10-27T10:30:00Z,true,550e8400-e29b-41d4-a716-446655440001,teacher,yuki.suzuki,"[{""type"":""sisId"",""identifier"":""TCH002""}]",Yuki,Suzuki,,suzuki@example.com,,,,,
```

---

### 2.4 Courses（コース）

**SDS入力**: `section.csv`  
**OneRoster出力**: `courses.csv`

**マッピング戦略**: SDSの`section`はOneRosterの`classes`に対応するが、OneRosterには`courses`が必要。SDSには明示的なコース情報がないため、`section.Course SIS ID`または`section.Course Name`からコースを抽出する。

| OneRoster フィールド | 必須 | データ型 | SDS マッピング元 | 変換ルール |
|-------------------|------|---------|-----------------|----------|
| sourcedId | Yes | GUID | - | UUID v5生成（`course:{section.Course SIS ID or section.SIS ID}`） |
| status | Yes | Enum | - | 固定値: `"active"` |
| dateLastModified | Yes | DateTime | - | 変換実行日時 |
| schoolYearSourcedId | No | GUID | - | academicSession.sourcedIdを参照 |
| title | Yes | String | section.Course Name | そのまま使用（存在しない場合はSection Nameを使用） |
| courseCode | No | String | section.Course SIS ID | そのまま使用（存在する場合） |
| grades | No | Array | - | 空（コースレベルでは学年指定なし） |
| orgSourcedId | Yes | GUID | section.School SIS ID | 組織のsourcedIdに変換 |
| subjects | No | Array | - | 空 |
| subjectCodes | No | Array | - | 空 |
| metadata | No | JSON | section.Course SIS ID | `{"course_sis_id": "{Course SIS ID}"}` |

**サンプル変換例**:

**SDS入力（section.csv）**:
```csv
SIS ID,School SIS ID,Section Name,Course SIS ID,Course Name
SEC001,SCH001,Mathematics 10A,MATH10,Mathematics 10
SEC002,SCH001,Mathematics 10B,MATH10,Mathematics 10
SEC003,SCH001,English 11A,ENG11,English 11
```

**OneRoster出力（courses.csv）**:
```csv
sourcedId,status,dateLastModified,schoolYearSourcedId,title,courseCode,grades,orgSourcedId,subjects,subjectCodes,metadata
880e8400-e29b-41d4-a716-446655440001,active,2025-10-27T10:30:00Z,990e8400-e29b-41d4-a716-446655440001,Mathematics 10,MATH10,,550e8400-e29b-41d4-a716-446655440001,,,"{""course_sis_id"":""MATH10""}"
880e8400-e29b-41d4-a716-446655440002,active,2025-10-27T10:30:00Z,990e8400-e29b-41d4-a716-446655440001,English 11,ENG11,,550e8400-e29b-41d4-a716-446655440001,,,"{""course_sis_id"":""ENG11""}"
```

**注意**: 同じ`Course SIS ID`を持つ複数のSectionは、1つのCourseにまとめる。

---

### 2.5 Classes（クラス）

**SDS入力**: `Section.csv`  
**OneRoster出力**: `classes.csv`

| OneRoster フィールド | 必須 | データ型 | SDS マッピング元 | 変換ルール |
|-------------------|------|---------|-----------------|----------|
| sourcedId | Yes | GUID | - | UUID v5生成（`class:{Section.SIS ID}`） |
| status | Yes | Enum | - | 固定値: `"active"` |
| dateLastModified | Yes | DateTime | - | 変換実行日時 |
| title | Yes | String | Section.Section Name | そのまま使用 |
| grades | No | Array | - | 空 |
| courseSourcedId | Yes | GUID | Section.Course SIS ID | courses.sourcedIdに変換 |
| classCode | No | String | Section.SIS ID | そのまま使用 |
| classType | Yes | Enum | - | 固定値: `"scheduled"` |
| location | No | String | - | 空 |
| schoolSourcedId | Yes | GUID | Section.School SIS ID | orgs.sourcedIdに変換 |
| termSourcedIds | No | Array[GUID] | - | 空（termは未定義） |
| subjects | No | Array | - | 空 |
| subjectCodes | No | Array | - | 空 |
| periods | No | Array | - | 空 |
| metadata | No | JSON | Section.SIS ID | `{"section_sis_id": "{Section.SIS ID}"}` |

**サンプル変換例**:

**SDS入力（Section.csv）**:
```csv
SIS ID,School SIS ID,Section Name,Course SIS ID
SEC001,SCH001,Mathematics 10A,MATH10
SEC002,SCH001,Mathematics 10B,MATH10
```

**OneRoster出力（classes.csv）**:
```csv
sourcedId,status,dateLastModified,title,grades,courseSourcedId,classCode,classType,location,schoolSourcedId,termSourcedIds,subjects,subjectCodes,periods,metadata
aa0e8400-e29b-41d4-a716-446655440001,active,2025-10-27T10:30:00Z,Mathematics 10A,,880e8400-e29b-41d4-a716-446655440001,SEC001,scheduled,,550e8400-e29b-41d4-a716-446655440001,,,,,"{""section_sis_id"":""SEC001""}"
aa0e8400-e29b-41d4-a716-446655440002,active,2025-10-27T10:30:00Z,Mathematics 10B,,880e8400-e29b-41d4-a716-446655440001,SEC002,scheduled,,550e8400-e29b-41d4-a716-446655440001,,,,,"{""section_sis_id"":""SEC002""}"
```

---

### 2.6 Enrollments（登録: 学生）

**SDS入力**: `StudentEnrollment.csv`  
**OneRoster出力**: `enrollments.csv`

| OneRoster フィールド | 必須 | データ型 | SDS マッピング元 | 変換ルール |
|-------------------|------|---------|-----------------|----------|
| sourcedId | Yes | GUID | - | UUID v5生成（`enrollment:student:{Student SIS ID}:{Section SIS ID}`） |
| status | Yes | Enum | - | 固定値: `"active"` |
| dateLastModified | Yes | DateTime | - | 変換実行日時 |
| classSourcedId | Yes | GUID | StudentEnrollment.Section SIS ID | classes.sourcedIdに変換 |
| schoolSourcedId | Yes | GUID | Section.School SIS ID | orgs.sourcedIdに変換（Sectionから取得） |
| userSourcedId | Yes | GUID | StudentEnrollment.Student SIS ID | users.sourcedIdに変換 |
| role | Yes | Enum | - | 固定値: `"student"` |
| primary | No | Boolean | - | 固定値: `true` |
| beginDate | No | Date | - | 空（SDSに該当フィールドなし） |
| endDate | No | Date | - | 空 |
| metadata | No | JSON | - | `{}` |

**サンプル変換例**:

**SDS入力（StudentEnrollment.csv）**:
```csv
Section SIS ID,Student SIS ID
SEC001,STU001
SEC001,STU002
SEC002,STU001
```

**OneRoster出力（enrollments.csv）**:
```csv
sourcedId,status,dateLastModified,classSourcedId,schoolSourcedId,userSourcedId,role,primary,beginDate,endDate,metadata
bb0e8400-e29b-41d4-a716-446655440001,active,2025-10-27T10:30:00Z,aa0e8400-e29b-41d4-a716-446655440001,550e8400-e29b-41d4-a716-446655440001,660e8400-e29b-41d4-a716-446655440001,student,true,,,{}
bb0e8400-e29b-41d4-a716-446655440002,active,2025-10-27T10:30:00Z,aa0e8400-e29b-41d4-a716-446655440001,550e8400-e29b-41d4-a716-446655440001,660e8400-e29b-41d4-a716-446655440002,student,true,,,{}
bb0e8400-e29b-41d4-a716-446655440003,active,2025-10-27T10:30:00Z,aa0e8400-e29b-41d4-a716-446655440002,550e8400-e29b-41d4-a716-446655440001,660e8400-e29b-41d4-a716-446655440001,student,true,,,{}
```

---

### 2.7 Enrollments（登録: 教員）

**SDS入力**: `TeacherRoster.csv`  
**OneRoster出力**: `enrollments.csv`（学生と同じファイル）

| OneRoster フィールド | 必須 | データ型 | SDS マッピング元 | 変換ルール |
|-------------------|------|---------|-----------------|----------|
| sourcedId | Yes | GUID | - | UUID v5生成（`enrollment:teacher:{Teacher SIS ID}:{Section SIS ID}`） |
| status | Yes | Enum | - | 固定値: `"active"` |
| dateLastModified | Yes | DateTime | - | 変換実行日時 |
| classSourcedId | Yes | GUID | TeacherRoster.Section SIS ID | classes.sourcedIdに変換 |
| schoolSourcedId | Yes | GUID | Section.School SIS ID | orgs.sourcedIdに変換 |
| userSourcedId | Yes | GUID | TeacherRoster.Teacher SIS ID | users.sourcedIdに変換 |
| role | Yes | Enum | - | 固定値: `"teacher"` |
| primary | No | Boolean | - | 固定値: `true` |
| beginDate | No | Date | - | 空 |
| endDate | No | Date | - | 空 |
| metadata | No | JSON | - | `{}` |

**サンプル変換例**:

**SDS入力（TeacherRoster.csv）**:
```csv
Section SIS ID,Teacher SIS ID
SEC001,TCH001
SEC002,TCH002
```

**OneRoster出力（enrollments.csv）**:
```csv
sourcedId,status,dateLastModified,classSourcedId,schoolSourcedId,userSourcedId,role,primary,beginDate,endDate,metadata
cc0e8400-e29b-41d4-a716-446655440001,active,2025-10-27T10:30:00Z,aa0e8400-e29b-41d4-a716-446655440001,550e8400-e29b-41d4-a716-446655440001,770e8400-e29b-41d4-a716-446655440001,teacher,true,,,{}
cc0e8400-e29b-41d4-a716-446655440002,active,2025-10-27T10:30:00Z,aa0e8400-e29b-41d4-a716-446655440002,550e8400-e29b-41d4-a716-446655440001,770e8400-e29b-41d4-a716-446655440002,teacher,true,,,{}
```

---

### 2.8 AcademicSessions（学期）

**SDS入力**: なし（SDSにはacademicSessionの概念がない）  
**OneRoster出力**: `academicSessions.csv`

**生成ルール**: OneRoster v1.2では`academicSessions`が必須のため、デフォルト値を生成する。

| OneRoster フィールド | 必須 | データ型 | 変換ルール |
|-------------------|------|---------|----------|
| sourcedId | Yes | GUID | 固定GUID生成（例: `990e8400-e29b-41d4-a716-446655440001`） |
| status | Yes | Enum | 固定値: `"active"` |
| dateLastModified | Yes | DateTime | 変換実行日時 |
| title | Yes | String | 固定値: `"2025 Academic Year"` |
| type | Yes | Enum | 固定値: `"schoolYear"` |
| startDate | Yes | Date | 固定値: `"2025-04-01"` （日本の学年開始） |
| endDate | Yes | Date | 固定値: `"2026-03-31"` （日本の学年終了） |
| parentSourcedId | No | GUID | 空（最上位の学年） |
| schoolYear | Yes | String | 固定値: `"2025"` |
| metadata | No | JSON | `{"auto_generated": true}` |

**サンプル出力（academicSessions.csv）**:
```csv
sourcedId,status,dateLastModified,title,type,startDate,endDate,parentSourcedId,schoolYear,metadata
990e8400-e29b-41d4-a716-446655440001,active,2025-10-27T10:30:00Z,2025 Academic Year,schoolYear,2025-04-01,2026-03-31,,2025,"{""auto_generated"":true}"
```

**注意**: 将来的にSDSに学期情報が追加された場合、この仕様を更新する。

---

### 2.9 Manifest（マニフェスト）

**SDS入力**: なし  
**OneRoster出力**: `manifest.csv`

**生成ルール**: OneRoster CSVパッケージのメタデータを定義。

**サンプル出力（manifest.csv）**:
```csv
propertyName,value
manifest.version,1.0
oneroster.version,1.2
file.orgs,bulk
file.users,bulk
file.courses,bulk
file.classes,bulk
file.enrollments,bulk
file.academicSessions,bulk
source.systemName,Microsoft School Data Sync
source.systemCode,SDS
```

---

## 3. GUID生成仕様

### 3.1 UUID v5生成アルゴリズム

**名前空間UUID**: `12345678-1234-5678-1234-567812345678`（組織固有に変更推奨）

**生成ロジック**:
```python
import uuid

# 組織固有の名前空間UUID
NAMESPACE_SDS = uuid.UUID('12345678-1234-5678-1234-567812345678')

def generate_sourced_id(entity_type: str, sis_id: str) -> str:
    """
    決定論的なGUID生成
    
    Args:
        entity_type: エンティティタイプ（org, user, course, class, enrollment）
        sis_id: SDS SIS ID
    
    Returns:
        UUID v5形式のGUID
    """
    name = f"{entity_type}:{sis_id}"
    return str(uuid.uuid5(NAMESPACE_SDS, name))

# 使用例
org_guid = generate_sourced_id("org", "SCH001")
# 結果: "550e8400-e29b-41d4-a716-446655440001"（決定論的）
```

### 3.2 エンティティタイプ別GUID生成

| エンティティ | entity_type | sis_id例 | GUID例 |
|------------|------------|---------|--------|
| Organizations | `"org"` | `"SCH001"` | `550e8400-...` |
| Users（学生） | `"user"` | `"STU001"` | `660e8400-...` |
| Users（教員） | `"user"` | `"TCH001"` | `770e8400-...` |
| Courses | `"course"` | `"MATH10"` | `880e8400-...` |
| Classes | `"class"` | `"SEC001"` | `aa0e8400-...` |
| Enrollments（学生） | `"enrollment"` | `"student:STU001:SEC001"` | `bb0e8400-...` |
| Enrollments（教員） | `"enrollment"` | `"teacher:TCH001:SEC001"` | `cc0e8400-...` |
| AcademicSessions | `"academicSession"` | `"2025"` | `990e8400-...` |

**重要**: 同じSIS IDから常に同じGUIDが生成されるため、べき等性が保証される。

---

## 4. データ型変換ルール

### 4.1 文字列（String）

| SDS | OneRoster | 変換ルール |
|-----|-----------|----------|
| 任意の文字列 | String | トリミング（前後の空白削除）、最大長チェック |

### 4.2 列挙型（Enum）

| OneRoster フィールド | 許可値 | SDS マッピング |
|-------------------|--------|--------------|
| status | `active`, `tobedeleted` | 固定値: `"active"` |
| role | `student`, `teacher`, `administrator`, etc. | `"student"` or `"teacher"` |
| type（org） | `school`, `district`, `local`, etc. | 固定値: `"school"` |
| classType | `homeroom`, `scheduled`, etc. | 固定値: `"scheduled"` |

### 4.3 日付時刻（DateTime）

| SDS | OneRoster | 変換ルール |
|-----|-----------|----------|
| - | ISO 8601形式 | `YYYY-MM-DDTHH:MM:SSZ`（UTC） |

**生成例**:
```python
from datetime import datetime

# 現在時刻をISO 8601形式で取得
date_last_modified = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')
# 結果: "2025-10-27T10:30:00Z"
```

### 4.4 日付（Date）

| SDS | OneRoster | 変換ルール |
|-----|-----------|----------|
| - | ISO 8601形式 | `YYYY-MM-DD` |

### 4.5 ブール値（Boolean）

| SDS | OneRoster | 変換ルール |
|-----|-----------|----------|
| - | `true` or `false` | 固定値: `true` |

### 4.6 配列（Array）

| SDS | OneRoster | 変換ルール |
|-----|-----------|----------|
| 単一値 | JSON配列 | `["value"]` |
| カンマ区切り | JSON配列 | `["value1", "value2"]` |

**例**:
```python
# 学年の変換
sds_grade = "10"
oneroster_grades = f'["{sds_grade}"]'
# 結果: '["10"]'

# 複数の組織ID
sds_school_ids = "SCH001,SCH002"
oneroster_org_ids = [generate_sourced_id("org", sid.strip()) for sid in sds_school_ids.split(",")]
# 結果: ["550e8400-...", "550e8400-..."]
```

### 4.7 JSON（Object）

| SDS | OneRoster | 変換ルール |
|-----|-----------|----------|
| SIS ID | JSON Object | `{"sis_id": "{SIS ID}"}` |

**例**:
```python
import json

sds_sis_id = "STU001"
oneroster_metadata = json.dumps({"sis_id": sds_sis_id})
# 結果: '{"sis_id": "STU001"}'
```

---

## 5. 整合性チェック

### 5.1 外部キー参照整合性

| 参照元 | フィールド | 参照先 | チェック内容 |
|--------|----------|--------|------------|
| users | orgSourcedIds | orgs.sourcedId | すべての組織IDが存在するか |
| classes | courseSourcedId | courses.sourcedId | コースIDが存在するか |
| classes | schoolSourcedId | orgs.sourcedId | 組織IDが存在するか |
| enrollments | classSourcedId | classes.sourcedId | クラスIDが存在するか |
| enrollments | userSourcedId | users.sourcedId | ユーザーIDが存在するか |
| enrollments | schoolSourcedId | orgs.sourcedId | 組織IDが存在するか |

**検証コード例**:
```python
def validate_foreign_keys(data: dict) -> list[str]:
    """外部キー参照整合性を検証"""
    errors = []
    
    # orgs.sourcedIdのセット作成
    org_ids = {org["sourcedId"] for org in data["orgs"]}
    
    # users.orgSourcedIdsの検証
    for user in data["users"]:
        for org_id in user["orgSourcedIds"]:
            if org_id not in org_ids:
                errors.append(f"User {user['sourcedId']}: Invalid orgSourcedId {org_id}")
    
    return errors
```

### 5.2 必須フィールドチェック

| エンティティ | 必須フィールド |
|------------|--------------|
| orgs | sourcedId, status, dateLastModified, name, type |
| users | sourcedId, status, dateLastModified, enabledUser, orgSourcedIds, role, username, givenName, familyName |
| courses | sourcedId, status, dateLastModified, title, orgSourcedId |
| classes | sourcedId, status, dateLastModified, title, courseSourcedId, classType, schoolSourcedId |
| enrollments | sourcedId, status, dateLastModified, classSourcedId, schoolSourcedId, userSourcedId, role |
| academicSessions | sourcedId, status, dateLastModified, title, type, startDate, endDate, schoolYear |

---

## 6. エラーハンドリング

### 6.1 マッピングエラーの分類

| エラータイプ | 重大度 | 対応 |
|------------|--------|------|
| 必須フィールド欠損（SDS） | Critical | 処理中断、エラー通知 |
| 外部キー参照エラー | Critical | 処理中断、エラー通知 |
| データ型不一致 | High | スキップ、警告ログ |
| オプションフィールド欠損 | Low | デフォルト値設定、警告ログ |
| GUID生成失敗 | Critical | 処理中断、エラー通知 |

### 6.2 エラーメッセージ例

```json
{
  "error_type": "missing_required_field",
  "severity": "critical",
  "entity_type": "student",
  "file_name": "Student.csv",
  "row_number": 42,
  "field_name": "First Name",
  "message": "必須フィールド 'First Name' が欠損しています。",
  "recommendation": "CSVファイルを確認し、該当行のFirst Name列にデータを入力してください。"
}
```

---

## 7. パフォーマンス最適化

### 7.1 バッチ処理

- 1万レコードごとにバッチ処理
- メモリ使用量を制限（最大2GB）
- ストリーミング処理でメモリ効率化

### 7.2 並列処理

- 独立したエンティティ（orgs, academicSessions）を並列変換
- マルチスレッド処理（最大4スレッド）

### 7.3 キャッシング

- GUID生成結果をメモリキャッシュ
- 外部キー参照をインデックス化（辞書型）

---

## 8. バージョン管理

| バージョン | 対応SDS形式 | 対応OneRoster形式 | 変更内容 |
|-----------|-----------|-----------------|---------|
| 1.0.0 | SDS v2.1 | OneRoster v1.2 | 初版（基本エンティティ対応） |
| 1.1.0 | SDS v2.1 | OneRoster v1.2 | Demographics対応（予定） |
| 2.0.0 | SDS v3.0 | OneRoster v1.2 | SDS v3.0対応（予定） |

---

## 9. 関連ドキュメント

- [プロジェクト概要](./01_project_overview.md)
- [機能要件定義](./02_functional_requirements.md)
- [非機能要件定義](./03_non_functional_requirements.md)
- [ユーザーストーリー](./04_user_stories.md)

---

## 10. 承認履歴

| 日付 | 承認者 | 役割 | ステータス |
|------|--------|------|-----------|
| 2025-10-27 | - | Requirements Analyst | Draft |
| - | - | Data Architect | Pending |
| - | - | Technical Lead | Pending |

---

## 11. 変更履歴

| バージョン | 日付 | 変更内容 | 変更者 |
|-----------|------|---------|--------|
| 1.0.0 | 2025-10-27 | 初版作成 | Requirements Analyst |
