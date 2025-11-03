# to do

- 2025/11/03
  - task までできたので以下の手順で実装する(/speckit.analyze の指摘は受けたけど一旦実装に進む。指摘内容は これは見ないでください。アウトプットの内容.txt に書いた)
  - jj git init --colocate
    - これで .jj が作成される
  - jj bookmark track 001-memorium-md@origin
  - jj bookmark set 001-memorium-md
  - Cursor に「uv run --link-mode=copy orchestrate_jj_jules_from_specs.py」を実行してもらう
    - 多分、error: node:events:486 というエラーが出ると思うので、分析しててもらう。多分、片方の WS の送信ができていない。
    - クラウドの Jules には あなたは担当機能の実装エージェントです。 という最初の1行しか送信されていないし、WS も2つあるはずなのに 片方しか送信されていない。
  - もとに戻したいときは「.git」「.jj」「ws」の3つを削除する。次に「C:\Users\kbpsh\OneDrive\development\2025_11_03_Speckit_Backups\spec-kit」から「.git」だけ持ってくる。



- これでウォーターフォール型バイブコーディングが実践できる
  - S&P TOP10 効率的フロンティア
  - メモリーム
    - 一旦 Obsidian を優先する

### PowerShell ではなく WSL で作業しないとちゃんとプロンプトを読み込んでくれないので、ターミナルでは WSL を起動する。

流れ:
wsl で CodexCLI を起動する。
```001-memorium-mdブランチ ではこれは毎回最初にやる。/new したときも必要に応じて読み込む。====
プロジェクト憲章（.specify/memory/constitution.md）を読み込んでください。

データインサートと検索は MiniRAG でやりますが、MiniRAG のサンプルコードは「documents/MiniRAG/minirag_on_postgres のサンプルコード.py」を確認してください。MiniRAGは「dockerfile: Dockerfile.postgres」と「dockerfile: Dockerfile.minirag_on_postgre」の2つのコンテナで動かすため、実行したい場合は私に相談してください。
```
↓
/prompts:speckit.specify Memorium.md を確認してください。
↓
/prompts:speckit.clarify
↓
/prompts:speckit.plan {planの指示書はこちら.mdの内容を貼る}
↓
/prompts:speckit.checklist {speckit.checklist1 の指示書はこちら.mdの内容を貼る}
/new
/prompts:speckit.checklist {speckit.checklist2 の指示書はこちら.mdの内容を貼る}
/new
/prompts:speckit.checklist {speckit.checklist3 の指示書はこちら.mdの内容を貼る}



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
- /plan は Plan を作るだけ。タスク分解は /speckit.tasks、実装は /speckit.implement に流すのが基本ラインです。
- 本番レベルのLLMアプリケーションの12個の設計原則 の入れ込み方
  - constitution.md に“要約（原則の骨子）だけ”を入れ、本文はテンプレート化したチェックリストとして品質ゲートで回すのがおすすめ。
  - constitution（憲法）にはプロジェクトを貫く原則の「短い要約」を置きます（例：「エージェントはステートレス・リデューサとして設計する」「ツール呼び出しは構造化JSONのみ」等の見出し＋1行）。Spec Kitはまず /speckit.constitution でこの土台を作り、以後の仕様・計画・実装で参照します
- チェックリストは N個 用意したので、/speckit.checklist は N回 実行する。まとめると精度が落ちそうなので分割した
  - チェックリスト1: マイクロサービス実装チェックリスト
  - チェックリスト2: 本番レベルのLLMアプリ12個の設計原則チェックリスト

# 使い方

まずは CodexCLI を立ち上げて以下を実行する。
codex -m gpt-5-codex --yolo -c model_reasoning_effort="medium" --search "$@"

### エージェント内で順に実行(必要に応じて /new する)
/speckit.constitution  品質・テスト・UX一貫性・性能に関する原則を作って
/speckit.specify       何を作るか（WHAT/WHY）を定義。「ビジネスドメインとユースケース」を書く。この段階ではスタックや方式は書かないのが公式推奨
/speckit.clarify       曖昧さを解消（推奨オプション）
/speckit.plan          技術計画（スタック/アーキテクチャ）。マイクロサービス方針と生成してほしいドキュメントを明確に書く。
/speckit.checklist     設計の妥当性チェック。チェックリスト分 実行。
/speckit.tasks         実行タスクリスト生成。実装タスクをサービス単位に分割する。
/speckit.analyze       成果物間の整合性チェック（推奨オプション）
※ /speckit.implement     タスク実行・TDDで実装（タスク順にローカルCLIを叩きながら構築）
/speckit.implement は使わずに orchestrate_jj_jules_from_specs.py を使う。詳細は下記。
/speckit.codeReview.md

※任意ツール:
/speckit.clarify（不足要件の質疑応答）
/speckit.analyze（成果物間の整合性チェック）
/speckit.checklist（要件の網羅・明確性の検査。品質チェックリスト生成）


## orchestrate_jj_jules_from_specs.py

- WSL ではなく PowerShell で「uv run --link-mode=copy orchestrate_jj_jules_from_specs.py」を実行して実装する
- このスクリプトは「JJ + Jules」。
- このスクリプトを動かす前に git push して、事前にリポジトリを丸ごと別フォルダへバックアップを取っておく(jj を使うと Git が壊れることがあるらしい)
- 次に以下を実行する。001-memorium-md はブランチ名。
  - jj git init --colocate
  - jj status
  - git status
  - jj bookmark track 001-memorium-md@origin
  - jj bookmark set 001-memorium-md
  - jj git push


# AIコーディングの心得

https://qiita.com/chomado/items/764e67e104843a22bcde
- AI 駆動開発はマイクロサービスに向いててモノリスには向かない
- AI は便利だが、嘘をついたり誤魔化したり嬉々として破壊的変更をするので、うまく使おう
- 常に検証・テスト・レビューを実施​
  - /speckit.checklist
  - /speckit.analyze

# done

- 2025/11/03
  - ローカルで MiniRAG_on_postgres をテストした。とりあえずそれっぽく動いているので、一旦OK。
  - これが動かないと Spec kit でどうやって指示すれば良いか分からないので、動かせるかどうか確認して、サンプルコードにまとめて Spec kit が理解できるようにドキュメント化する
    - "documents/MiniRAG/minirag_on_postgres のサンプルコード.py" がサンプルコード。これでデータインサートと検索(メタデータフィルター付き)をすれば良い。



---
prompts/Instructions1.md を読んで、そこに書いてある指示を実行してください。
---
を実行。
