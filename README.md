# to do

- これでウォーターフォール型バイブコーディングが実践できる
  - S&P TOP10 効率的フロンティア
  - メモリーム
    - 一旦 Obsidian を優先する

/speckit.specify に以下の内容を入れる。

======================
# Memorium（MVP）

## 目的

* 日記から記憶を取りこみ、**構造化して保存**し、あとから**自分の探し方で引き出せる**ようにする。
* **個人利用（私だけ）**を前提に、**初期費用・月額固定費ゼロ**で運用する。

## 対象ユーザー

* 開発者である私本人のみ。スケールは不要。

## ユーザーストーリー（要点）

1. チャットUIで日記を入力すると、対話で内容を深掘りし、保存前に**プレビュー**（重要度・記憶タイプ・整形テキスト・要約・解説）が出る。承認すると保存される。
2. 保存後、その回で抽出された**エンティティ**が画面に表示される。
3. 検索画面で自然文を入れると、**複数の検索方法**（キーワード／意味／関係）を**並列**に走らせ、**結合した結果**が見える。重要度や日付で絞り込める。
4. 応答や要約は、蓄積した**プロファイル**（価値観・言葉遣いなど）を軽く反映する。

## スコープ

### 入力

* チャットでの深掘り・確認（中断や修正ができるガイダンスつき）。
* プレビュー形式：

  ```json
  {
    "重要度": "1-10の整数",
    "記憶タイプ": { "セマンティック記憶": [], "エピソード記憶": [] },
    "構造化された日記": "...",
    "サマリー": "...",
    "解説": "..."
  }
  ```
* 承認後に保存する項目：セマンティック記憶／エピソード記憶／構造化された日記／サマリー／メタデータ（importance:int）。
* 保存完了時に抽出エンティティを表示。保存後に**プロファイル更新**を行う。

### 出力（検索）

* 単一の検索UI。自然文で検索。
* **キーワード／意味／関係**の3系統を並列に実行し、0件や閾値未満は除外、**残りを結合して提示**（ランキングはしない）。
* 検索前に重要度・日付でフィルタできる。

### プロファイリング

* 日記登録のたびに、価値観・思考傾向・言葉遣いを更新。保存形式は**YAML**。

## 受け入れ基準（MVP）

* 入力：対話→プレビュー→承認→保存が通る。
* 表示：保存完了時にその回のエンティティが出る。
* 検索：3系統が並列で動き、0件ソースは除外し、**結合結果**を出す。
* プロファイル：更新され、応答に軽く反映される。
* 前提条件：個人利用・ゼロ初期コストで運用できる。
======================



codex -m gpt-5-codex --yolo -c model_reasoning_effort="medium" --search "$@"

codex -m gpt-5-codex --yolo -c model_reasoning_effort="high" --search "$@"


# Spec Kit の CLI（specify）をツールとしてインストール

```
uv tool install specify-cli --from git+https://github.com/github/spec-kit.git
```

# アップデート

```
uv tool install specify-cli --force --from git+https://github.com/github/spec-kit.git
```

# カレントディレクトリに CodexCLI + PowerShell (ps) 用のプロジェクトを作る (Spec Kit 初期化)

```
specify init --here --force --ai codex --script ps
```
カレントディレクトリ名が<PROJECT_NAME>になる。

以下が出力結果:
---
## 🚀 Next Steps

1. **プロジェクトディレクトリに移動済みです！**
2. **Codexを使用する前に環境変数 `CODEX_HOME` を設定してください（PowerShell例）:**
```
setx CODEX_HOME 'C:\Users\kbpsh\OneDrive\development\Spec\spec-kit\.codex'
```
3. **エージェントのスラッシュコマンドを使い始めましょう:**
   - `/speckit.constitution` &nbsp;&nbsp;&nbsp;プロジェクト原則の作成
   - `/speckit.specify` &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;基本仕様の作成
   - `/speckit.plan` &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;実装計画の作成
   - `/speckit.tasks` &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;実行可能なタスクの生成
   - `/speckit.implement` &nbsp;&nbsp;&nbsp;&nbsp;実装の実行

## 💡 Enhancement Commands（品質＆信頼性向上のための追加コマンド）
- **`/speckit.clarify`（オプション）**  
  計画前に構造化質問で曖昧さを解消します（`/speckit.plan`の前に実行推奨）。
- **`/speckit.analyze`（オプション）**  
  成果物間の整合性・一貫性レポートを生成します（`/speckit.tasks`の後、`/speckit.implement`の前）。
- **`/speckit.checklist`（オプション）**  
  仕様の要件（完全性・明確さ・一貫性）をチェックリスト形式で検証します（`/speckit.plan`の後に実施）。
---

# インストールしたら codex の設定ファイルのパスを通す

```
setx CODEX_HOME 'C:\Users\kbpsh\OneDrive\development\Spec\spec-kit\.codex'
```

# パスを通したら動作確認する

```
specify check
```

# Codex の /speckit. がメニューに出てこない問題の対処方法

ホーム側の方の .codex フォルダにある prompts フォルダしか認識されないバグがあるため、ルートディレクトリにある prompts フォルダを更新してから、以下のスクリプトを実行してホーム側の .codex/prompts を最新化する。

```
.specify/scripts/powershell/copy-prompts.ps1
```

# Spec kit の仕様

実務フローは Constitution → Specify → Plan → Tasks → Implement の順で、必要に応じて Clarify / Analyze / Checklist を挿入して品質を高めます。

# ポイント

- Spec Kit は「Spec → Plan → Tasks → Implement」のゲート制で回すので、1つのプロンプトに詰め込みすぎないこと
- 仕様段階(specify)は技術選定を持ち込まない（What/Whyに集中） → その後のPlanでHowを決める
- /plan はコンテキスト（目的）＋技術選定＋原則＋出力ファイルの厳密指定に絞ると、モデルがテンプレに沿った plan.mdを安定生成します
- /plan はPlan を作るだけ。タスク分解は /speckit.tasks、実装は /speckit.implement に流すのが基本ラインです。
- 本番レベルのLLMアプリケーションの12個の設計原則 の入れ込み方
  - constitution.md に“要約（原則の骨子）だけ”を入れ、本文はテンプレート化したチェックリストとして品質ゲートで回すのがおすすめ。
  - constitution（憲法）にはプロジェクトを貫く原則の「短い要約」を置きます（例：「エージェントはステートレス・リデューサとして設計する」「ツール呼び出しは構造化JSONのみ」等の見出し＋1行）。Spec Kitはまず /speckit.constitution でこの土台を作り、以後の仕様・計画・実装で参照します
- チェックリストは2つ用意したので、/speckit.checklist は2回実行する。まとめると精度が落ちそうなので分割した
  - チェックリスト1: マイクロサービス実装チェックリスト
  - チェックリスト2: 本番レベルのLLMアプリ12個の設計原則チェックリスト

# 使い方

まずは CodexCLI を立ち上げて以下を実行する。
codex -m gpt-5-codex --yolo -c model_reasoning_effort="medium" --search "$@"

### エージェント内で順に実行
/speckit.constitution  品質・テスト・UX一貫性・性能に関する原則を作って
/speckit.specify       何を作るか（WHAT/WHY）を定義。「ビジネスドメインとユースケース」を書く。この段階ではスタックや方式は書かないのが公式推奨
/speckit.clarify       曖昧さを解消（推奨オプション）
/speckit.checklist     （仕様が固まった直後に）仕様の抜け漏れチェック。チェックリスト分 実行。
/speckit.plan          技術計画（スタック/アーキテクチャ）。マイクロサービス方針と生成してほしいドキュメントを明確に書く。specs/<feature>/plan.md / data-model.md / contracts/ ... など複数の技術文書を出すので、ここにArchitecture.md / Design.md / OpenAPI.yaml を追加で作る旨を盛り込む。SpecKitに合わせるなら各サービスを**“機能（feature）”**として扱うと運用が楽。
/speckit.checklist     2回目のチェック。設計の妥当性チェック。チェックリスト分 実行。
/speckit.tasks         実行タスクリスト生成。実装タスクをサービス単位に分割する。
/speckit.analyze       成果物間の整合性チェック（推奨オプション）
※ /speckit.implement     タスク実行・TDDで実装（タスク順にローカルCLIを叩きながら構築）
/speckit.implement は使わずに「uv run orchestrate_jj_jules_from_specs.py」を実行してこれで実装する。このスクリプトは「JJ + Jules」。


※任意ツール:
/speckit.clarify（不足要件の質疑応答）
/speckit.analyze（成果物間の整合性チェック）
/speckit.checklist（要件の網羅・明確性の検査。品質チェックリスト生成）




---
prompts/Instructions1.md を読んで、そこに書いてある指示を実行してください。
---
を実行。
