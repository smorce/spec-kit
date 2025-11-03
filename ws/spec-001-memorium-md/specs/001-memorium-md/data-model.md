# Memorium Data Model

## 1. JournalSession

| フィールド | 型 | 説明 |
|------------|----|------|
| id | UUID | セッション識別子 |
| status | ENUM(draft, previewing, ready, committed) | 現在ステータス |
| started_at | TIMESTAMP WITH TIME ZONE | セッション開始日時 |
| updated_at | TIMESTAMP WITH TIME ZONE | 最終更新日時 |
| draft_payload | JSONB | 最新入力のスナップショット（プレビュー生成用） |
| preview_snapshot | JSONB | 最後に生成したプレビュー |

### 関連:
- `JournalMessage` (1:N)

## 2. JournalMessage

| フィールド | 型 | 説明 |
|------------|----|------|
| id | UUID | メッセージ識別子 |
| session_id | UUID (FK → JournalSession) | 紐づくセッション |
| role | ENUM(user, assistant) | 発話者 |
| content | TEXT | メッセージ本文 |
| created_at | TIMESTAMP WITH TIME ZONE | 作成日時 |

## 3. MemoryRecord

| フィールド | 型 | 説明 |
|------------|----|------|
| id | UUID | 記憶識別子 |
| importance | SMALLINT | 重要度 (1-10) |
| semantic_tags | TEXT[] | セマンティック記憶ラベル |
| episodic_tags | TEXT[] | エピソード記憶ラベル |
| structured_journal | TEXT | 整形済み本文 |
| summary | TEXT | 要約 |
| commentary | TEXT | 解説 |
| metadata | JSONB | 追加メタデータ（セッションIDなど） |
| created_at | TIMESTAMP WITH TIME ZONE | 保存日時 |

### MiniRAG連携
- `MiniRAG.documents` にも同期インサート（構造化本文 + メタデータ、pgvector埋め込み）。

## 4. ExtractedEntity

| フィールド | 型 | 説明 |
|------------|----|------|
| id | UUID | エンティティ識別子 |
| memory_id | UUID (FK → MemoryRecord) | 紐づく記憶 |
| label | TEXT | エンティティ名 |
| category | ENUM(person, place, topic, object, event) | エンティティ種別 |
| score | NUMERIC(5,4) | 信頼度 |

## 5. ProfileSnapshot

| フィールド | 型 | 説明 |
|------------|----|------|
| version | BIGSERIAL | バージョン番号 |
| content | TEXT | YAML本文 |
| created_at | TIMESTAMP WITH TIME ZONE | 生成日時 |
| diff_summary | TEXT | ハイライト箇条書き |

### YAMLファイル
- 最新プロファイルは`storage/profile/current.yaml`に平文保存。

## 6. SearchResultCache (任意)

| フィールド | 型 | 説明 |
|------------|----|------|
| request_id | UUID | 検索要求ID |
| payload | JSONB | 返却済み結果 |
| expired_at | TIMESTAMP WITH TIME ZONE | キャッシュ期限 |

## 制約

- `JournalSession.id`, `JournalMessage.id`, `MemoryRecord.id` はUUID v4を採用。
- `semantic_tags`, `episodic_tags` はMiniRAGメタデータと揃えるためlowercase snake_caseで保持。
- MiniRAGの`metadata->>'text_field'`には`structured_journal`または`summary`を設定し、検索系統識別に利用。
- データは暗号化しない前提のため、OSユーザー権限でアクセス制御する。
