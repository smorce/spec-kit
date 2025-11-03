# LLM本番品質チェックリスト: Memorium記憶管理フロー

**Branch**: `001-memorium-md`  
**Updated**: 2025-11-03  
**Purpose**: プロトタイプのMemorium記憶管理フローを、本番運用可能なLLMアプリケーションへ引き上げるために必要な設計・実装原則の遵守状況を可視化する。  
**Scope**: [000-architecture], [001-memorium-md]  
**Stack Assumptions**: ローカル単一ユーザー運用 / データ暗号化なし（平文保存） / MiniRAG（`documents/MiniRAG`）による挿入・検索

## 適用する原則とチェック項目

### 原則1: Natural Language → Tool Calls
- [ ] 000-architecture: すべてのツール（MiniRAG検索、メモリ保存、プロファイル更新等）の引数・戻り値をPydanticあるいはOpenAPI Schemaで定義し、リポジトリでバージョン管理している。
- [ ] 001-memorium-md: 記憶管理エージェントが使うツール呼び出しは、仕様上「どのツールをどの順序・引数で呼ぶか」の判断に限定され、ビジネスロジックはアプリコード側に実装されている。

### 原則2: Own Your Prompts
- [ ] 000-architecture: プロンプト資産を`libs/prompts/`（もしくは合意済みの専用ディレクトリ）に集約し、コミット差分が必ずレビュー対象になるようCODEOWNERSまたはPath Filterを設定している。
- [ ] 001-memorium-md: 記憶化・検索・プロファイル更新の各プロンプトについてゴールデンスナップショットテストを整備し、CIで`uv run --link-mode=copy pytest`などに組み込んでいる。

### 原則3: Own Your Context Window
- [ ] 000-architecture: システム履歴の圧縮手法（要約・抽出・構造化）の設計を仕様に明記し、それぞれ単体テストで回帰保証している。
- [ ] 001-memorium-md: 「システムプロンプト＋圧縮済み履歴＋ユーザー入力＋MiniRAG検索結果」という入力テンプレートをPlanに固定し、テストでトークン上限内に収まることを検証している。

### 原則4: Tools are Structured Outputs
- [ ] 000-architecture: LLM出力をアプリ側で厳格にパースする層を用意し、型・許可コマンド・値域チェックを通過できない場合のフォールバック方針（再試行・ユーザー向けエラー）を定義済みである。
- [ ] 001-memorium-md: 記憶保存・プロファイル更新のレスポンスはPydanticモデルで検証し、MiniRAGへの書き込み前に失敗した場合は状態をロールバックしてセッションを再開できる。

### 原則5: Unify Execution State & Business State
- [ ] 000-architecture: `thread_id / messages[] / metadata`を持つ永続スキーマを単一のストア（例: SQLiteファイル）で管理し、実行状態とビジネスデータの整合性を自動テストで検証している。
- [ ] 001-memorium-md: ジャーナルセッションは常にスレッドスキーマから復元でき、途中離脱後の再開時にMemoriumのビジネス状態（プレビュー、プロファイル差分）がズレないことを確認している。

### 原則6: Launch / Pause / Resume with Simple APIs
- [ ] 000-architecture: 再開用API（例: `POST /threads/{id}/resume`）とセッション作成APIをHTTPレベルで定義し、仕様書とテスト（E2Eまたは統合テスト）で中断→再開フローをカバーしている。
- [ ] 001-memorium-md: ローカルUIやCLIからの再開操作がAPIに集約され、エラー時はユーザー向けメッセージを英語で返す実装を確認できる。

### 原則8: Own Your Control Flow
- [ ] 000-architecture: 1ターンを「LLM呼び出し→ツール実行→状態更新」の純粋関数として定義し、リトライや指数バックオフのポリシーをコード化して動作検証している。
- [ ] 001-memorium-md: 閾値不足の検索結果やMiniRAG書き込み失敗時の制御フローがPlanに明記され、ユースケースごとのリトライ上限と失敗時通知がテストで確認できる。

### 原則9: Compact Errors into Context Window
- [ ] 000-architecture: 例外発生時に要約ダイジェストを生成し次ターンへ注入する仕組みを定義し、失敗回数に応じてエスカレーション（ユーザー通知や処理停止）する閾値を明文化している。
- [ ] 001-memorium-md: MiniRAGアクセス失敗やプロファイル更新不整合時のエラーサマリーが履歴に残り、次ターンで再指示に活用されることを自動テストで確認している。

### 原則10: Small, Focused Agents
- [ ] 000-architecture: 各エージェントの想定ターン数（3〜20）と責務境界をPlanで宣言し、サブエージェント分割基準（例: 記憶化、検索、プロファイル調整）をドキュメント化している。
- [ ] 001-memorium-md: 記憶管理エージェントが質問生成・要約・保存確認の3段階以内で収束することをプロンプト設計とテストで保証している。

### 原則12: Make Your Agent a Stateless Reducer
- [ ] 000-architecture: 全処理はスレッドストアに保存された状態から導出でき、サーバープロセス内の可変グローバル状態に依存しない。楽観ロックまたは悲観ロック戦略を選定し記録している。
- [ ] 001-memorium-md: MiniRAGへの書き込み・読み出しは同一トランザクション境界で扱い、ロールバック時にスレッド状態とビジネスデータが同期することを確認している。

## 除外した原則

- Contact Humans with Tool Calls: ローカル単一ユーザー運用であり、人間オペレーター連携の要件が仕様に存在しないため除外。
- Trigger from Anywhere: 本機能はチャットUI起点のみを想定しており、Cron/Webhook等の複数エントリポイント統合は当面のスコープ外。
