本プロダクトは仕様駆動TDDによるエンタープライズ級マイクロサービスアーキテクチャを採用します。 [000-architecture]で全体アーキテクチャを定義し、 001-feature 以降に各マイクロサービス(ここでは feature として扱う)を定義します。
[000-architecture]は本プロダクト全体のマイクロサービスアーキテクチャを定義し、以後の各 feature の基盤とする。

Goal:
- 本プロダクトの仕様駆動TDDを前提に、エンタープライズ級マイクロサービス基盤の計画(plan.md)を作成する。

Tech stack (serverless/edge):
- Next.js (SSR) → OpenNext 経由 Cloudflare Workers（SSR/API/Middleware）
- DB: Neon (serverless PostgreSQL)
- Auth: Supabase Auth（JWT、RLS: 原則 `user_id = auth.uid()`）
- Storage: Cloudflare R2（画像配信は Cloudflare Images）
- データの暗号化はしない

Architecture principles:
- Database per Service、同期/非同期の使い分け、イベント駆動（必要に応じ Saga/CQRS 検討）
- API Gateway／データ分割／イベント流を明示
- 可観測性：構造化ログ、メトリクス、分散トレーシング（W3C Trace Context 伝播）

Front End:
- documents/フロントエンド を参考に Cloudflare で動くように実装する
- UI: `UIのサンプルイメージ。Neo4jではなくポスグレを使う.jpg`

Deliverables (write):
- `specs/[000-architecture]/plan.md`：以下の7章立て（1. Executive Summary/Goals, 2. NFR, 3. 全体アーキテクチャ, 4. 各マイクロサービス概要, 5. 技術スタックと選定理由(代替比較), 6. セキュリティ/コンプラ, 7. 運用/パフォーマンス）
- `specs/[000-architecture]/research.md`：主要な設計判断と代替案比較（ADR 形式で可）
- `specs/[000-architecture]/quickstart.md`：ローカル開発手順、環境変数、初期マイグレーション、実行方法

NFR targets (例値はダミーなので合理的に提案して更新してよい):
- p95 レイテンシ X ms（要ページ/エンドポイント別の目標）、可用性 99.9% 以上、RPO ≤ Y 分、RTO ≤ Z 分、監査ログ保持 年数 N

Collision Resolution Rules:
1. specs/001-memorium-md/spec.md を優先する
2. 不明な場合はユーザーに質問する

Out-of-scope:
- ここでは実装や詳細タスク化はしない。`/speckit.tasks` で分解、`/speckit.implement` で実行する。