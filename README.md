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

# codexの設定ファイルのパスを通す

```
setx CODEX_HOME 'C:\Users\kbpsh\OneDrive\development\Spec\spec-kit\.codex'   
```




---
prompts/Instructions1.md を読んで、そこに書いてある指示を実行してください。
---
を実行。
