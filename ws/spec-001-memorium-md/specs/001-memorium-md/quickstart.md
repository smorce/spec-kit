# Memorium Quickstart

## 前提条件
- Docker Desktop / Docker Compose v2
- Python 3.11 + uv (`pip install uv`)
- Node.js 20.x（フロントエンドビルドに備える）

## リポジトリ構成
```
spec-kit/
  documents/
    MiniRAG/    # MiniRAGフレームワーク一式
    フロントエンド/ # UIサンプル・静的資産
  specs/
    000-architecture/
    001-memorium-md/
```

## セットアップ手順
1. MiniRAGスタックを起動:
   ```bash
   cd documents/MiniRAG
   docker compose up -d
   ```
2. Python依存取得（サービス共通）:
   ```bash
   cd spec-kit
   uv sync
   ```
3. Backendサービス起動（例: orchestrator-gateway）:
   ```bash
   uv run --link-mode=copy python run_gateway.py
   ```
4. SignalRクライアント（フロントエンド）開発サーバー:
   ```bash
   cd documents/フロントエンド
   npm install
   npm run dev
   ```

## 環境変数
| 変数 | 説明 | デフォルト |
|------|------|------------|
| `PG_HOST` | PostgreSQLホスト | `localhost` |
| `PG_PORT` | PostgreSQLポート | `5432` |
| `PG_USER` | DBユーザー | `postgres` |
| `PG_PASSWORD` | DBパスワード | `postgres` |
| `PG_DATABASE` | DB名 | `minirag` |
| `PROFILE_DIR` | プロファイルYAML保存先 | `storage/profile` |
| `NATS_URL` | NATS JetStream接続 | `nats://localhost:4222` |

## 初期マイグレーション
```bash
uv run --link-mode=copy alembic upgrade head
psql -h $PG_HOST -U $PG_USER -d $PG_DATABASE -f documents/MiniRAG/002_add_text_field_to_existing_chunks.sql
```

## 実行確認
1. `POST /api/v1/journal-sessions` に初期入力を送信。
2. SignalR `/hubs/journal` に接続し、`assistantPrompt` イベントを受け取る。
3. `POST /api/v1/journal-sessions/{id}/preview/confirm` 後に`/search`で結果が複数ソースから返ることを確認。

## トラブルシューティング
- MiniRAGが起動しない: `docker compose logs minirag_app` で依存が満たされているか確認。
- SignalR切断: クライアント側の再接続ロジックを有効化し、RESTフォールバックでメッセージ連携。
- プロファイルYAML競合: バックアップを`specs/001-memorium-md/storage/profile/backup/`に手動保存。
