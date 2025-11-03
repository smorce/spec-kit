---
description: "Task list for Memorium記憶管理フロー feature"
---

# Tasks: Memorium記憶管理フロー

**Input**: `/specs/001-memorium-md/` の設計ドキュメント（plan.md, spec.md, research.md, data-model.md, contracts/, quickstart.md）  
**Prerequisites**: MiniRAGスタック・PostgreSQL・NATS JetStream のローカル起動（quickstart.md参照）

**Tests**: 本機能はTDD必須。各ユーザーストーリーでテストタスクを最初に実施し、Red→Green→Refactor順を維持すること。

**Organization**: タスクはユーザーストーリー単位で並べ、独立した検証が可能なインクリメントを保証する。

## Format: `[ID] [P?] [Story] Description`
- **[P]**: 並列実行可能（異なるファイルを編集し依存がないもの）
- **[Story]**: US1/US2/US3 等のラベル。共通基盤は Setup / Foundation / Polish を使用。
- 各タスクには明示的なファイルパスまたはコマンドを含める。

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: マルチサービス構成の土台を用意し、以降のフェーズで共通利用できる開発環境を整備する。

- [ ] T001 [Setup] `services/` 配下に `orchestrator_gateway`, `journal_ingestion`, `preview_orchestrator`, `memory_vault`, `profile_service`, `search_aggregation` の各 `src/` と `tests/` ディレクトリ群を作成し、`__init__.py` プレースホルダを配置する。
- [ ] T002 [P] [Setup] ルートの `pyproject.toml` を作成し、FastAPI・uvicorn・pydantic-settings・asyncpg・nats-py・structlog・schemathesis・pytest・playwright 等の共通依存を定義する。
- [ ] T003 [P] [Setup] ルートに `docker-compose.yaml` を追加し、quickstart記載の MiniRAG / PostgreSQL / NATS / Traefik サービスを参照する基本構成を記述する。
- [ ] T004 [P] [Setup] `env/.env.spec` を新規作成し、`PG_HOST`, `PG_DATABASE`, `NATS_URL`, `PROFILE_DIR` など quickstart の環境変数テンプレートを定義する。

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: 全ユーザーストーリーの前提となる共通ライブラリ・インフラ設定・テスト基盤を用意する。完了前にUS作業を開始しないこと。

- [ ] T005 [Foundation] `common/config/settings.py` を実装し、pydantic-settings を用いたサービス共通設定ローダーを定義する。
- [ ] T006 [P] [Foundation] `common/logging/structlog_config.py` を追加し、JSON Lines 形式の構造化ログ設定と共通ミドルウェアフックを提供する。
- [ ] T007 [P] [Foundation] `common/messaging/nats_client.py` を作成し、JetStream コンシューマ/プロデューサの初期化ヘルパーを実装する。
- [ ] T008 [Foundation] `infrastructure/database/alembic.ini` と `infrastructure/database/env.py` を用意し、PostgreSQL + asyncpg で共有スキーマをマイグレーションできるよう設定する。
- [ ] T009 [P] [Foundation] ルートの `tests/conftest.py` を実装し、PostgreSQL/NATS テストフィクスチャと FastAPI TestClient ファクトリを用意する。
- [ ] T010 [Foundation] `services/orchestrator_gateway/src/app.py` に FastAPI アプリ本体・共通ミドルウェア・SignalR Hub マウントプレースホルダを実装する。
- [ ] T011 [P] [Foundation] `docker/docker-compose.services.yaml` を追加し、各サービスコンテナのビルド設定・ネットワーク・依存サービスリンクを定義する。

**Checkpoint**: Foundationalフェーズ完了後にのみユーザーストーリーのタスクへ進む。

---

## Phase 3: User Story 1 - チャット経由で日記を構造化する (Priority: P1) 🎯 MVP

**Goal**: セッション開始から深掘り質問・プレビュー生成・SignalR通知までを一貫して実装する。  
**Independent Test**: モック日記を入力し、プレビューの必須フィールド（重要度・記憶タイプ・構造化本文・サマリー・解説）が生成され承認待ち状態になることを確認する。

### Tests for User Story 1（必須・先行実施）

- [ ] T012 [P] [US1] `tests/contracts/test_journal_sessions_contract.py` に schemathesis で `POST /journal-sessions`, `POST /journal-sessions/{sessionId}/messages`, `GET /journal-sessions/{sessionId}/preview` の契約テスト（失敗ケース含む）を追加する。
- [ ] T013 [P] [US1] `tests/integration/test_journal_preview_flow.py` にチャット対話からプレビュー生成までの統合テスト（NATSスタブを使用）を作成する。
- [ ] T014 [P] [US1] `services/preview_orchestrator/tests/test_prompt_generator.py` に質問生成・重要度スコアリングのユニットテストを実装する。

### Implementation for User Story 1

- [ ] T015 [US1] `services/journal_ingestion/src/models/journal_session.py` に `JournalSession` モデルと状態遷移補助メソッドを定義する。
- [ ] T016 [P] [US1] `services/journal_ingestion/src/models/journal_message.py` に `JournalMessage` モデルとロールバリデーションを実装する。
- [ ] T017 [US1] `services/journal_ingestion/migrations/versions/0001_create_journal_tables.py` を作成し、セッション/メッセージテーブルをマイグレーションする。
- [ ] T018 [US1] `services/journal_ingestion/src/repository/session_repository.py` にセッション作成・メッセージ追加・ドラフト更新のリポジトリ層を実装する。
- [ ] T019 [P] [US1] `services/preview_orchestrator/src/services/prompt_engine.py` に深掘り質問生成ロジックとテンプレート管理を実装する。
- [ ] T020 [US1] `services/preview_orchestrator/src/services/preview_builder.py` にプレビュー整形（構造化本文・サマリー・解説・重要度計算）を実装する。
- [ ] T021 [US1] `services/orchestrator_gateway/src/api/journal.py` に `POST /journal-sessions`, `POST /journal-sessions/{sessionId}/messages`, `GET /journal-sessions/{sessionId}/preview` のルーター処理と依存解決を実装する。
- [ ] T022 [P] [US1] `services/orchestrator_gateway/src/signalr/journal_hub.py` に `/hubs/journal` Hub（`sessionStateUpdated`, `assistantPrompt`, `previewReady`, `sessionClosed`）のイベント骨格を導入する。
- [ ] T023 [US1] `services/orchestrator_gateway/src/service_bus/journal_handlers.py` に NATS イベント購読・プレビュー更新通知パイプラインを実装する。
- [ ] T024 [P] [US1] `services/preview_orchestrator/src/workers/preview_pipeline.py` にメッセージ受信→プレビュー再計算→SignalR通知までの非同期ワーカーを実装する。

**Checkpoint**: US1の契約・統合・ユニットテストがGreenとなり、チャット→プレビュー承認待ちが独立して動作することを確認。

---

## Phase 4: User Story 2 - 保存後に抽出エンティティとプロファイルを確認する (Priority: P2)

**Goal**: プレビュー承認後の記憶保存・エンティティ抽出・プロファイル差分提示を実装し、保存結果が即時確認できるようにする。  
**Independent Test**: 承認後にエンティティ一覧とプロファイル差分が返却されることを検証すれば完了。

### Tests for User Story 2（必須・先行実施）

- [ ] T025 [P] [US2] `tests/contracts/test_memory_and_profile_contract.py` に `POST /journal-sessions/{sessionId}/preview/confirm` と `GET /profile` の契約テスト（保存成功/バリデーション失敗）を追加する。
- [ ] T026 [P] [US2] `tests/integration/test_memory_persistence_flow.py` に承認→永続化→エンティティ抽出→プロファイル更新までの統合テストを実装する。
- [ ] T027 [P] [US2] `services/profile_service/tests/test_profile_diff.py` に YAML 差分生成とハイライト要約のユニットテストを実装する。

### Implementation for User Story 2

- [ ] T028 [US2] `services/memory_vault/src/models/memory_record.py` に `MemoryRecord` モデルを定義し、MiniRAG同期用メタデータを含める。
- [ ] T029 [P] [US2] `services/memory_vault/src/models/extracted_entity.py` に `ExtractedEntity` モデルを実装する。
- [ ] T030 [P] [US2] `services/profile_service/src/models/profile_snapshot.py` に `ProfileSnapshot` モデルとバージョン管理ロジックを実装する。
- [ ] T031 [US2] `services/memory_vault/migrations/versions/0001_create_memory_tables.py` を作成し、記憶・エンティティ用テーブルとインデックスを追加する。
- [ ] T032 [P] [US2] `services/profile_service/migrations/versions/0001_create_profile_snapshot.py` を作成し、スナップショットテーブルとシーケンスを追加する。
- [ ] T033 [US2] `services/memory_vault/src/services/memory_writer.py` に承認済みレコード保存と MiniRAG 同期キュー送信を実装する。
- [ ] T034 [P] [US2] `services/memory_vault/src/services/entity_extractor.py` にエンティティ抽出・スコアリング処理を実装する。
- [ ] T035 [US2] `services/profile_service/src/services/profile_updater.py` に YAML 差分生成とハイライト抽出を実装する。
- [ ] T036 [P] [US2] `services/orchestrator_gateway/src/service_bus/preview_confirmation_handler.py` に承認イベント処理と Memory Vault / Profile Service 呼び出しを実装する。
- [ ] T037 [US2] `services/orchestrator_gateway/src/api/journal.py` に `POST /journal-sessions/{sessionId}/preview/confirm` エンドポイントと保存結果DTOを追加する。
- [ ] T038 [P] [US2] `services/orchestrator_gateway/src/signalr/profile_events.py` に `/hubs/journal` の `sessionClosed` 通知でエンティティ一覧とプロファイルハイライトを配信する処理を実装する。
- [ ] T039 [US2] `services/profile_service/src/api/profile_controller.py` に `GET /profile` のFastAPIルーターを実装する。

**Checkpoint**: US1 + US2 のテストがGreenとなり、保存完了画面でエンティティとプロファイル差分を確認できること。

---

## Phase 5: User Story 3 - 自然文検索で複数軸から記憶を引き出す (Priority: P3)

**Goal**: キーワード・意味・関係検索を並列実行し、フィルタを適用した統合結果とSignalR進捗通知を提供する。  
**Independent Test**: 代表クエリに対して3系統のうち結果があるソースのみが結合され、0件ソースは除外されることを確認する。

### Tests for User Story 3（必須・先行実施）

- [ ] T040 [P] [US3] `tests/contracts/test_search_contract.py` に `GET /search` の契約テスト（フィルタ組合せ・0件レスポンス）を追加する。
- [ ] T041 [P] [US3] `tests/integration/test_search_aggregation_flow.py` に3系統検索の並列実行と結果マージを検証する統合テストを実装する。
- [ ] T042 [P] [US3] `services/search_aggregation/tests/test_result_merger.py` にスコア閾値フィルタとソース結合のユニットテストを実装する。

### Implementation for User Story 3

- [ ] T043 [US3] `services/search_aggregation/src/services/search_router.py` に検索リクエスト調停とMiniRAG呼び出しオーケストレーションを実装する。
- [ ] T044 [P] [US3] `services/search_aggregation/src/clients/minirag_client.py` に MiniRAG キーワード/意味/関係検索クライアントを実装する。
- [ ] T045 [P] [US3] `services/search_aggregation/src/services/filter_pipeline.py` に閾値・フィルタ・ソース別スコア評価ロジックを実装する。
- [ ] T046 [US3] `services/orchestrator_gateway/src/api/search.py` に `GET /search` ルーターとレスポンスDTOを実装する。
- [ ] T047 [P] [US3] `services/orchestrator_gateway/src/signalr/search_hub.py` に `/hubs/search` Hub（`searchProgress`, `searchCompleted`, `searchFailed`）を実装する。
- [ ] T048 [US3] `services/search_aggregation/src/repository/search_cache_repository.py` に `SearchResultCache` の読み書きとTTL管理を実装する。
- [ ] T049 [P] [US3] `services/search_aggregation/migrations/versions/0001_create_search_cache.py` を作成し、検索キャッシュテーブルを追加する。

**Checkpoint**: US1〜US3 のテストがすべてGreenとなり、検索UIへのSignalR通知を含めて統合動作すること。

---

## Final Phase: Polish & Cross-Cutting Concerns

**Purpose**: 観測性・E2E・運用整備など複数ストーリーに跨る仕上げを行う。

- [ ] T050 [Polish] `docs/runbooks/memorium-mvp.md` にローカル起動手順・依存サービス・トラブルシューティングをまとめる。
- [ ] T051 [P] [Polish] `tests/e2e/playwright/journal_to_search.spec.ts` にチャット→保存→検索を跨ぐE2Eシナリオを追加する。
- [ ] T052 [Polish] `scripts/ci.sh` を作成し、契約テスト→ユニット→統合→E2E→k6検索負荷テスト実行までのCIパイプラインコマンドを定義する。

---

## Dependencies & Execution Order

- Setup (Phase 1) → Foundational (Phase 2) → US1 (Phase 3) → US2 (Phase 4) → US3 (Phase 5) → Polish。各フェーズは前フェーズ完了後に着手。
- `services/orchestrator_gateway/src/api/journal.py` は T021 完了後に T037 を適用（同一ファイルのため順序厳守）。
- データベースマイグレーションは各サービスごとに番号付けし、前提となるモデル定義タスク（例: T015→T017, T028→T031, T048→T049）を完了してから実行する。
- SignalR Hub 実装タスクは対応するAPIルーター完了後に検証する（例: T021→T022、T046→T047）。
- Polish フェーズは全ユーザーストーリーが独立テストを通過した後に着手する。

### User Story Dependency Graph

```
Setup → Foundational → US1 → US2 → US3 → Polish
                   └──────────────┘
```

US2とUS3はFoundational完了後に並列着手可能だが、MVP観点ではUS1完了を優先し、US2がUS1の保存イベントを前提とする。

---

## Parallel Execution Examples

- **US1**: T012・T013・T014 を並列でRed化 → T016・T019・T022・T024 を並列実装し、T018・T020・T021・T023で順次連結。
- **US2**: T025・T026・T027 を同時着手 → モデル系 T029・T030 を並列実装→サービス層 T034・T035・T036・T038 を並列化。
- **US3**: T040・T041・T042 を同時にRed化 → クライアント/フィルタ T044・T045 を並列→キャッシュ関連 T048・T049 を同時進行。

---

## Implementation Strategy

### MVP First
1. Phase 1〜2 を完了し共通基盤とコンテナを起動可能にする。
2. Phase 3 (US1) のテストをGreenにしてチャット→プレビュー動線をMVPとして検証。
3. 必要ならここでレビュー/デモを実施し、以降のストーリー導入を判断。

### Incremental Delivery
1. US2 で保存とプロファイル更新を追加し、保存体験を拡張。
2. US3 で検索体験を実装し、価値の最大化を図る。
3. Polish フェーズで運用・E2E・CIを整えリリース品質に引き上げる。

### Validation
- 各ユーザーストーリーは独立した契約/統合/ユニットテストを保持しており、単独で受け入れ判定が可能。
- Foundational フェーズで共通インフラを先行整備したため、US1〜US3 の実装は互いに干渉せず並列化できる。
- Polish フェーズで横断的な非機能要件（Runbook, CI, E2E）を網羅し、全タスク完了時点でデモ・リリース可能な状態を保証する。

---
