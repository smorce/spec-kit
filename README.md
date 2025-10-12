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

╭────────────────────────────────────────── Next Steps ──────────────────────────────────────────╮
│                                                                                                │
│  1. You're already in the project directory!                                                   │
│  2. Set CODEX_HOME environment variable before running Codex: setx CODEX_HOME                  │
│  'C:\Users\kbpsh\OneDrive\development\Spec\spec-kit\.codex'                                    │
│  3. Start using slash commands with your AI agent:                                             │
│     2.1 /speckit.constitution - Establish project principles                                   │
│     2.2 /speckit.specify - Create baseline specification                                       │
│     2.3 /speckit.plan - Create implementation plan                                             │
│     2.4 /speckit.tasks - Generate actionable tasks                                             │
│     2.5 /speckit.implement - Execute implementation                                            │
│                                                                                                │
╰────────────────────────────────────────────────────────────────────────────────────────────────╯

╭───────────────────────────────────── Enhancement Commands ─────────────────────────────────────╮
│                                                                                                │
│  Optional commands that you can use for your specs (improve quality & confidence)              │
│                                                                                                │
│  ○ /speckit.clarify (optional) - Ask structured questions to de-risk ambiguous areas before    │
│  planning (run before /speckit.plan if used)                                                   │
│  ○ /speckit.analyze (optional) - Cross-artifact consistency & alignment report (after          │
│  /speckit.tasks, before /speckit.implement)                                                    │
│  ○ /speckit.checklist (optional) - Generate quality checklists to validate requirements        │
│  completeness, clarity, and consistency (after /speckit.plan)                                  │
│                                                                                                │
╰────────────────────────────────────────────────────────────────────────────────────────────────╯

# インストールしたら codex の設定ファイルのパスを通す

```
setx CODEX_HOME 'C:\Users\kbpsh\OneDrive\development\Spec\spec-kit\.codex'
```

# パスを通したら動作確認する

```
specify check
```

# Codex の /speckit. がメニューに出てこない問題の対処方法

ホーム側の方の .codex フォルダにある prompts フォルダしか認識されないバグがあるため、以下のスクリプトを実行してホーム側の .codex/prompts を最新化する。

```
.specify/scripts/powershell/copy-prompts.ps1
```




# 使い方
まずは CodexCLI を立ち上げて以下を実行する。

*   **/prompts:speckit.constitution - プロジェクトの原則を確立**
    *   開発の基本的なルールや方針（例えば、使用するプログラミング言語の規約など）をAIに定義させます。


/speckit.constitution 私が今まで使っていたプロンプトが AGENTS.md です。こちらを参照して .specify/memory/constitution.md を更新してください。やってほしいことは  AGENTS.md の内容を理解した上で .specify/memory/constitution.md のフォーマットを崩さずに AI エージェントが仕様、計画、実装の各フェーズで参照するプロジェクトの基本ガイドラインを含む統治原則を作成することです。



コード品質とテスト方針、UI一貫性、性能要件について原則を作って




*   **/prompts:speckit.specify - ベースライン仕様を作成**
    *   作りたいソフトウェアが「何を」「なぜ」実現するものなのかをAIに伝え、詳細な仕様書を作成させます。

*   **/prompts:speckit.plan - 実装計画を作成**
    *   仕様書をもとに、どのような技術（プログラミング言語、フレームワークなど）を使って「どのように」作るかの技術的な計画をAIに立てさせます。

*   **/prompts:speckit.tasks - 実行可能なタスクを生成**
    *   計画をもとに、実装に必要な作業を具体的なタスクの一覧としてAIに細かく分解させます。

*   **/prompts:speckit.implement - 実装を実行**
    *   生成されたタスクリストに従って、AIに実際のコーディング（実装）を開始させます。





---
prompts/Instructions1.md を読んで、そこに書いてある指示を実行してください。
---
を実行。
