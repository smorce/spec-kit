本プロダクトは仕様駆動TDDによるエンタープライズ級マイクロサービスアーキテクチャを採用します。 [000-architecture]で全体アーキテクチャを定義し、 001-XXX 以降に各マイクロサービス(ここでは feature として扱う)を定義します。
[000-architecture]は本プロダクト全体のマイクロサービスアーキテクチャを定義し、以後の各 feature の基盤とする。

Goal:
- 本プロダクトの仕様駆動TDDを前提に、エンタープライズ級マイクロサービス基盤の計画(plan.md)を作成する。

Tech stack:
- ローカルでの開発(個人プロジェクト)
- データの暗号化はしない
- データインサートと検索は MiniRAG フレームワーク(Python)を利用する

Front End:
- documents/フロントエンド を参考にする
- UI: `UIのサンプルイメージ。Neo4jではなくポスグレを使う.jpg`

Deliverables (write):
- `specs/[000-architecture]/plan.md`：以下の7章立て（1. Executive Summary/Goals, 2. NFR, 3. 全体アーキテクチャ, 4. 各マイクロサービス概要, 5. 技術スタックと選定理由(代替比較), 6. セキュリティ/コンプラ, 7. 運用/パフォーマンス）
- `specs/[001-XXX]/contracts/api-spec.json`：api-spec.json 作成
- `specs/[001-XXX]/contracts/signalr-spec.md`：signalr-spec.md 作成
- `specs/[001-XXX]/data-model.md`： data-model.md 作成
- `specs/[001-XXX]/plan.md`： plan.md 作成
- `specs/[001-XXX]/research.md`：主要な設計判断と代替案比較（ADR 形式で可）
- `specs/[001-XXX]/quickstart.md`：ローカル開発手順、環境変数、初期マイグレーション、実行方法

Collision Resolution Rules:
1. specs/001-XXX/spec.md を優先する
2. 不明な場合はユーザーに質問する

Out-of-scope:
- ここでは実装や詳細タスク化はしない。`/speckit.tasks` で分解、`/speckit.implement` で実行する。