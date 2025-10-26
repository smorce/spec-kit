# ファイル名: orchestrate_jj_jules_from_specs.py
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# ===============================================================
# このスクリプトは何をする？
# ---------------------------------------------------------------
# - specs/ 配下の「機能ディレクトリ」を列挙し、各機能ごとに疑似エージェント用
#   ワークスペース（jj workspace）を作ります。
# - 各エージェントに jules のセッションを並列投入し、コードレビューを依頼します。
# - 最後に、すべてのエージェントによるレビュー結果（修正コード）を 1 つの
#   マージコミットへ統合します。
#
# 使い方（Usage）
# ---------------------------------------------------------------
# 0) 前提
#    - jj が使える既存の jj リポジトリ直下で実行してください（`jj status` が通ること）。
#    - jules CLI を導入・ログイン（npm -g @google/jules / `jules login`）。
#    - Rich が未導入なら: `pip install rich`
#
# 1) 既定の specs/ を使う（基本はこれ）
#    $ python orchestrate_jj_jules_from_specs.py
#
# 2) specs の場所を変える
#    $ python orchestrate_jj_jules_from_specs.py --specs-dir path/to/specs
#
# 3) 対象機能を絞り込む（前方一致 / 正規表現）
#    # 例: ディレクトリ名が "001-" で始まる機能だけ
#    $ python orchestrate_jj_jules_from_specs.py --starts-with 001-
#    # 例: ディレクトリ名が \d{3}-.* にマッチ
#    $ python orchestrate_jj_jules_from_specs.py --name-regex "^\d{3}-"
#
# 4) 送信後の pull（必要に応じて）
#    $ jules remote list --session
#    # 完了した ID を見て
#    $ jules remote pull --session <SESSION_ID>
# ===============================================================

from __future__ import annotations
import argparse
import concurrent.futures as cf
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Iterable, List, Tuple

from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress
from rich.table import Table
import rich.traceback

rich.traceback.install(show_locals=False)
console = Console()

ROOT = Path.cwd()
WS_ROOT = ROOT / "ws"
DEFAULT_SPECS_DIR = ROOT / "specs"

MERGE_MESSAGE = "各エージェントによるレビュー結果を統合"

# ▼ プロンプトテンプレート
CODE_REVIEWER_PROMPT_TEMPLATE = """あなたはコードレビュー担当エージェントです。

【機能名】{feature_name}
【機能仕様ディレクトリ】{feature_dir}
【レビュー対象コードのディレクトリ】{workspace_dir}

### あなたのタスク: 包括的なコード品質レビューを実施し、改善が必要な点をマークダウン形式の文書にまとめる

あなたは、指定された機能の実装コードに対して、包括的なコード品質レビューを実施する責任があります。
特に、以下の点を重点的に確認し、改善が必要な点がある場合はそれらをマークダウン形式の文書にまとめ、{workspace_dir}/code_quality_review_results.md に保存してください。

1.  **設計原則の遵守**:
    -   DRY (Don't Repeat Yourself), KISS (Keep It Simple, Stupid), YAGNI (You Ain't Gonna Need It)
    -   SOLID原則
2.  **テスト品質**:
    -   機能追加に対応するテストコードが追加・更新されているか？
    -   テストは十分なカバレッジを持ち、意図が明確で読みやすいか？
3.  **コード品質と保守性**:
    -   コードは読みやすく、保守性が高いか？
    -   命名は適切か？
    -   複雑すぎるロジックはないか？
"""

SECURITY_REVIEWER_PROMPT_TEMPLATE = """あなたはセキュリティレビュー担当エージェントです。

【機能名】{feature_name}
【機能仕様ディレクトリ】{feature_dir}
【レビュー対象コードのディレクトリ】{workspace_dir}

### あなたのタスク: セキュリティ脆弱性レビューを実施し、脆弱性やリスクがある場合はそれらをマークダウン形式の文書にまとめる

あなたは、指定された機能の実装コードに対して、セキュリティ脆弱性のレビューを専門的に実施する責任があります。
特に、以下の点を重点的に確認し、脆弱性やリスクがある場合はそれらをマークダウン形式の文書にまとめ、{workspace_dir}/security_vulnerability_review_results.md に保存してください。

1.  **プロジェクトの性質の考慮**:
    -   このプロジェクトの性質に基づいて、セキュリティ脆弱性を考慮してください。
"""

AGENTS = [
    {
        "name": "code_reviewer",
        "suffix": "code-review",
        "prompt_template": CODE_REVIEWER_PROMPT_TEMPLATE,
    },
    {
        "name": "security_reviewer",
        "suffix": "security-review",
        "prompt_template": SECURITY_REVIEWER_PROMPT_TEMPLATE,
    },
]

# ---------- 引数処理 ----------

def parse_args() -> argparse.Namespace:
    """コマンドライン引数を読み取る。

    Returns:
        argparse.Namespace: specs の場所やフィルタ条件などを含む設定。
    """
    p = argparse.ArgumentParser(description="specs/ をスキャンして機能ごとに疑似エージェントを起動")
    p.add_argument("--specs-dir", type=Path, default=DEFAULT_SPECS_DIR, help="機能フォルダ群の場所（既定: ./specs）")
    p.add_argument("--starts-with", type=str, default=None, help="ディレクトリ名の前方一致フィルタ")
    p.add_argument("--name-regex", type=str, default=None, help="ディレクトリ名の正規表現フィルタ")
    p.add_argument("--require-tasks", action="store_true", help="tasks.md があるフォルダだけを対象にする")
    return p.parse_args()

ARGS = parse_args()

# ---------- ユーティリティ ----------

def check_cmd(cmd: str) -> None:
    """外部コマンドが PATH から実行できるか確認する。

    Args:
        cmd (str): コマンド名。

    Raises:
        RuntimeError: コマンドが見つからない場合。
    """
    if shutil.which(cmd) is None:
        raise RuntimeError(f"コマンドが見つかりません: {cmd}")

def run(cmd: List[str], cwd: Path | None = None) -> Tuple[int, str, str]:
    """サブプロセスを実行し、終了コード・標準出力・標準エラーを返す。

    Args:
        cmd (List[str]): 実行コマンド（引数を含む）。
        cwd (Path | None): 実行ディレクトリ。

    Returns:
        Tuple[int, str, str]: (returncode, stdout_stripped, stderr_stripped)
    """
    proc = subprocess.run(
        cmd,
        cwd=str(cwd) if cwd else None,
        text=True,
        encoding="utf-8",
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    return proc.returncode, proc.stdout.strip(), proc.stderr.strip()

# ---------- jj まわり ----------

def ensure_alias_for_jules() -> None:
    """`jj util exec` を別名で呼べるように設定する。

    Notes:
        `aliases.jules = ["util","exec","--","jules"]` を user スコープに設定。
        これで `jj jules ...` が使えるようになる。
    """
    code, out, err = run(
        ["jj", "config", "set", "--user", "aliases.jules", '["util","exec","--","jules"]']
    )
    if code != 0:
        raise RuntimeError(f"jj の別名設定に失敗しました: {err or out}")

def ensure_repo_context() -> None:
    """実行ディレクトリが jj リポジトリかざっくり確認する。"""
    code, out, err = run(["jj", "status"])
    if code != 0:
        raise RuntimeError(
            "このディレクトリは jj リポジトリではないようです。jj リポジトリ直下で実行してください。\n"
            f"詳細: {err or out}"
        )

def jj_workspace_add(path: Path) -> None:
    """指定ディレクトリで jj の作業コピー（workspace）を作成する。

    Args:
        path (Path): ワークスペースのパス。

    Raises:
        RuntimeError: 作成に失敗した場合（既存は許容）。
    """
    code, out, err = run(["jj", "workspace", "add", str(path)])
    if code != 0 and "already exists" not in (err + out):
        raise RuntimeError(f"ワークスペース作成に失敗: {path}\n{err or out}")

# ---------- specs スキャン ----------

def find_feature_dirs(specs_dir: Path) -> List[Path]:
    """specs 配下の機能ディレクトリ一覧を取得する。

    フィルタ条件（前方一致・正規表現・tasks.md の存在）に従って抽出。

    Args:
        specs_dir (Path): specs フォルダ。

    Returns:
        List[Path]: 機能ディレクトリのパス一覧（名前順）。
    """
    if not specs_dir.exists():
        raise RuntimeError(f"specs ディレクトリが見つかりません: {specs_dir}")

    dirs = [p for p in specs_dir.iterdir() if p.is_dir()]
    if ARGS.starts_with:
        dirs = [p for p in dirs if p.name.startswith(ARGS.starts_with)]
    if ARGS.name_regex:
        pat = re.compile(ARGS.name_regex)
        dirs = [p for p in dirs if pat.search(p.name)]
    if ARGS.require_tasks:
        dirs = [p for p in dirs if (p / "tasks.md").exists()]

    return sorted(dirs, key=lambda p: p.name)

# ---------- エージェント生成・投下 ----------

def make_workspace_name(feature_dir: Path, agent_suffix: str) -> str:
    """機能ディレクトリ名とエージェント接尾辞からワークスペース名を作る。

    例: specs/001-create-taskify, "code-review" -> ws/spec-001-create-taskify-code-review
    """
    return f"spec-{feature_dir.name}-{agent_suffix}"

def build_feature_prompt(feature_dir: Path, ws_dir: Path, prompt_template: str) -> str:
    """機能用の共通プロンプトを作る。"""
    return prompt_template.format(
        feature_name=feature_dir.name,
        feature_dir=str(feature_dir),
        workspace_dir=str(ws_dir),
    )

def create_feature_workspaces(feature_dirs: List[Path]) -> List[Tuple[Path, str]]:
    """機能ごと x エージェントごとにワークスペースを作り、(ws_dir, prompt) を返す。

    物理ディレクトリ作成ののち、`jj workspace add` を実行する。
    """
    results: List[Tuple[Path, str]] = []
    total_ws = len(feature_dirs) * len(AGENTS)
    with Progress(transient=True) as progress:
        task = progress.add_task("[bold]ワークスペースを作成中...", total=total_ws)
        for fdir in feature_dirs:
            for agent in AGENTS:
                ws_name = make_workspace_name(fdir, agent["suffix"])
                ws_dir = WS_ROOT / ws_name
                ws_dir.parent.mkdir(parents=True, exist_ok=True)
                jj_workspace_add(ws_dir)
                prompt = build_feature_prompt(fdir, ws_dir, agent["prompt_template"])
                results.append((ws_dir, prompt))
                progress.advance(task)
    return results

def invoke_jules_in(dir_and_prompt: Tuple[Path, str]) -> Tuple[Path, int, str, str]:
    """指定ワークスペース（作業コピー）で jules セッションを 1 件作る。"""
    d, prompt = dir_and_prompt
    code, out, err = run(["jj", "jules", "remote", "new", "--repo", ".", "--session", prompt], cwd=d)
    return d, code, out, err

def dispatch_all(pairs: Iterable[Tuple[Path, str]]) -> None:
    """すべてのワークスペースに並列でセッションを投下し、結果を表にする。"""
    pairs_list = list(pairs)
    rows: List[Tuple[str, str]] = []
    with Progress(transient=True) as progress:
        task = progress.add_task("[bold]Jules セッションを送信中...", total=len(pairs_list))
        with cf.ThreadPoolExecutor(max_workers=os.cpu_count() or 8) as ex:
            futs = [ex.submit(invoke_jules_in, p) for p in pairs_list]
            for fut in cf.as_completed(futs):
                d, code, out, err = fut.result()
                msg = (out or "").splitlines()[-1] if (code == 0 and out) else (err or out or "error")
                rows.append((str(d), ("submitted: " if code == 0 else "error: ") + msg))
                progress.advance(task)

    table = Table(title="送信結果")
    table.add_column("Workspace")
    table.add_column("Status / Message")
    for ws, msg in sorted(rows, key=lambda x: x[0]):
        table.add_row(ws, msg)
    console.print(table)

def list_sessions() -> None:
    """`jules remote list --session` を表示する。"""
    code, out, err = run(["jules", "remote", "list", "--session"])
    if code == 0:
        console.print(Panel.fit(out, title="Jules Sessions", border_style="green"))
    else:
        console.print(Panel.fit(err or out, title="Jules Sessions (取得失敗)", border_style="red"))

# ---------- マージ ----------

def build_dynamic_parents_from_feature_dirs(feature_dirs: List[Path]) -> List[str]:
    """機能ワークスペースから親コミット参照（workspace@）を動的に作る。"""
    parents: List[str] = []
    for fdir in feature_dirs:
        for agent in AGENTS:
            ws_name = make_workspace_name(fdir, agent["suffix"])
            parents.append(str(WS_ROOT / ws_name) + "@")
    return parents

def merge_all_results(feature_dirs: List[Path]) -> None:
    """`jj new <親...>` で多親マージし、`jj describe -m` でメッセージを付ける。"""
    parents = build_dynamic_parents_from_feature_dirs(feature_dirs)
    if not parents:
        raise RuntimeError("マージ対象の親がありません。specs のヒットが 0 件です。")

    table = Table(title="マージ対象の親コミット（順序）")
    table.add_column("Parent")
    for p in parents:
        table.add_row(p)
    console.print(table)

    with console.status("[bold]マージコミットを作成中..."):
        code, out, err = run(["jj", "new", *parents])
        if code != 0:
            raise RuntimeError(f"マージコミット作成に失敗しました: {err or out}")
        code, out, err = run(["jj", "describe", "-m", MERGE_MESSAGE])
        if code != 0:
            raise RuntimeError(f"コミットメッセージ設定に失敗しました: {err or out}")

    console.print(Panel.fit(f"✅ {MERGE_MESSAGE}", border_style="green"))

# ---------- メイン ----------

def main() -> None:
    """準備 → specs の機能抽出 → WS 作成 → 並列送信 → 一覧 → マージ。"""
    # 依存
    check_cmd("jj")
    check_cmd("jules")

    console.print(Panel.fit("specs → 機能別エージェント起動（jj + jules）", border_style="cyan"))

    # jj 準備
    ensure_alias_for_jules()
    console.log("aliases.jules を設定しました（jj util exec 経由）")
    ensure_repo_context()
    console.log("jj リポジトリを確認しました")

    # 機能列挙
    feature_dirs = find_feature_dirs(ARGS.specs_dir)
    if not feature_dirs:
        raise RuntimeError(f"対象機能が見つかりませんでした: {ARGS.specs_dir}")

    table = Table(title=f"対象機能（{len(feature_dirs)}）")
    table.add_column("Feature Dir")
    for d in feature_dirs:
        table.add_row(str(d))
    console.print(table)

    # WS 作成
    pairs = create_feature_workspaces(feature_dirs)  # (ws_dir, prompt)
    console.log(f"{len(pairs)} 個のワークスペースを用意しました")

    # 並列送信
    dispatch_all(pairs)

    # 一覧表示（pull は必要に応じて）
    list_sessions()
    console.print("[dim]例: 完了したセッションだけ pull する場合は、一覧の ID を選んで[/dim]")
    console.print("[dim]    jules remote pull --session <SESSION_ID>[/dim]")

    # マージ
    merge_all_results(feature_dirs)

    console.print(Panel.fit("Done.", border_style="cyan"))

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        console.print(Panel.fit(f"[bold red]ERROR[/bold red]\n{e}", border_style="red"))
        sys.exit(1)