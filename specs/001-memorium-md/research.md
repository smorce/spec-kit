# ADR: Memorium記憶管理フローの基盤設計

## Context
- ユーザーストーリーはチャット入力、プレビュー承認、検索、プロファイル更新を単一ユーザー向けに保証する必要がある。
- MiniRAG（PostgreSQL + pgvector）を既存資産として活用し、検索を3軸で提供することが必須。
- データ暗号化は実施しないという前提。

## Decision
1. **サービス分割**: Journal Ingestion / Preview Orchestrator / Memory Vault / Profile / Search Aggregation の5サービス構成。
2. **データ保存方式**: 記憶データはPostgreSQLへ平文保存し、MiniRAGに同期インサートする。
3. **リアルタイム通知**: SignalRを採用し、セッション更新・検索進行をリアルタイム配信。
4. **プロファイル管理**: YAMLファイル + Snapshotテーブルの二段構成で差分通知と履歴保持を両立。

## Alternatives
- **モノリシック構成**: 1アプリで完結させる。→ 将来拡張時に責務分割が困難、TDDサイクルでの境界テストが複雑。
- **グラフDB中心設計**: Neo4jに統合保存。→ documents/フロントエンド要件に反し、pgvector資産と不整合。
- **メッセージレス構成**: HTTP連携のみ。→ プレビュー生成の非同期化が困難、UX劣化。

## Consequences
- サービス間契約を明示でき、Spec-Plan-Taskの連鎖が管理しやすい。
- 平文保存によりアクセス権限管理が前提条件となるが、個人運用では許容範囲。
- SignalR採用により接続維持処理が必要となるが、即時反映体験を満たせる。
- MiniRAG依存が明確になり、将来他エンジンへ差し替える際はアダプタ層追加で対応可能。
