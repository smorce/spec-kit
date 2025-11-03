# 1. Executive Summary / Goals

- Memoriumは個人向け記憶管理SaaSを想定しつつ、仕様駆動TDDでエンタープライズ級のマイクロサービス基盤を整備する。
- 入力（ジャーナルセッション）、構造化プレビュー、保存、検索、プロファイル更新を疎結合なサービス群で分担し、MiniRAGベースの検索基盤とフロントエンドを連携させる。
- 将来的な複数ユーザーや追加チャネルへの拡張を阻害しないよう、API契約とイベント契約を先に固めてから機能ごとにTDDで実装できる計画を提示する。

# 2. NFR (Non-Functional Requirements)

- 可用性: ローカル運用を前提に99.0%（稼働時間目標）だが、サービスが停止してもジャーナルの一時保存ファイルから復旧可能にする。
- 一貫性: 保存と検索結果の同期ラグは1分以内。MiniRAGパイプラインの非同期処理で遅延を監視する。
- 性能: 1セッションあたりプレビュー生成を30秒以内、検索応答を2秒以内に収める。
- 観測性: 各サービスは構造化ログ（JSON Lines）とメトリクス（Prometheus互換）を発行し、ローカルGrafanaダッシュボードで確認できるようにする。
- テスト性: すべてのインターフェースについて契約テストを先行し、CIでユニット＋コンポーネントテストを自動化できる構成を計画する。
- メンテナンス性: サービス単位でデプロイ可能なDocker Compose構成を維持し、設定は`.env.spec`のみに依存させる。

# 3. 全体アーキテクチャ

- フロントエンドSPA（ローカル静的ホスト）→ API Gateway → バックエンドサービス群。SignalR Hubでリアルタイム更新を通知。
- データ層はPostgreSQL + pgvector（MiniRAG同梱）とYAMLファイルストア（プロファイル用）。イベント配信にNATS JetStreamを採用し、非同期連携を実現。
- サービスメッシュ代替として、ローカルではTraefikをIngress兼サービスディスカバリに利用。将来Istio等に移行可能な設計とする。
- アプリケーションサービスは以下のドメイン境界に分割:
  - Journal Ingestion Service
  - Preview Orchestrator Service
  - Memory Vault Service
  - Profile Service
  - Search Aggregation Service
- 共通基盤として`orchestrator-gateway`がGraphQL/REST/SignalRエンドポイントを提供し、BFFの役割を担う。

# 4. 各マイクロサービス概要

| サービス | 主要責務 | 入出力 | 依存先 |
|-----------|-----------|--------|--------|
| orchestrator-gateway | フロントエンド統合窓口、セッション管理、認証プレースホルダ | REST/SignalR | Journal Ingestion, Preview Orchestrator, Search Aggregation |
| Journal Ingestion Service | ジャーナルセッション状態管理、ドラフト保存 | REST, NATSイベント | PostgreSQL |
| Preview Orchestrator Service | 深掘り質問生成、プレビュー生成、承認ワークフロー | REST, SignalR通知, NATSイベント | MiniRAG (推論), Profile Service |
| Memory Vault Service | 承認済み記憶の永続化、エンティティ抽出、MiniRAGインサート | REST, NATSイベント | PostgreSQL + MiniRAG |
| Profile Service | YAMLプロファイル更新、差分計算 | REST | ファイルシステム |
| Search Aggregation Service | キーワード/意味/関係検索実行と結合 | REST | MiniRAG API, Memory Vault |

# 5. 技術スタックと選定理由 (代替比較)

- Backend: Python FastAPI各サービス + uvicorn。理由: MiniRAGとの親和性、asyncサポート。代替候補: Node.js（同一言語）だがMiniRAG統合コストが高い。
- データ: PostgreSQL + pgvector（MiniRAG仕様）。代替: SQLite（軽量だがベクトル検索不可）、Neo4j（グラフ強いが導入コスト高）。
- メッセージング: NATS JetStream。代替: RabbitMQ（学習コスト高）、Kafka（ローカル構築が重い）。
- フロントエンド: 既存資料ベースのSPA（可能ならReact/Vue想定だが実装未定）。代替: Server-side RenderはSignalR要件と合わず除外。
- インフラ: Docker Composeローカル起動。代替: Kubernetes（個人用途でオーバーキル）。
- テスト: pytest + schemathesisで契約検証。代替: behave(BDD)は初期コスト大。

# 6. セキュリティ / コンプライアンス

- 個人利用前提のため暗号化無し。ただしローカル環境のアクセス制御（OSユーザー権限）を依存条件として明記。
- API Gatewayでレート制限とCSRFトークン検証を導入予定（将来多ユーザー対応を見越した仕様のみ定義）。
- MiniRAG・PostgreSQLの認証はDocker Compose内の共有ネットワークに限定し、外部公開ポートを遮断。
- ログに機微情報（生テキスト）を保存しないようマスキングルールを定義予定。

# 7. 運用 / パフォーマンス

- 監視: Loki + Promtail + Grafanaでログ/メトリクスを可視化。Compose内で起動。
- スケーリング: 現状は単一インスタンスだが、サービスごとにコンテナ分割済みのためDocker Composeで簡易水平スケールが可能。
- デプロイ: `uv run --link-mode=copy` を用いたPython依存管理と`docker compose up`で再現。CI想定としてGitHub Actionsテンプレートを後続タスクで追加。
- バックアップ: PostgreSQLは週次ダンプ、YAMLプロファイルはGitでバージョン管理。MiniRAG埋め込み再生成は再処理で回復可能。EOF
