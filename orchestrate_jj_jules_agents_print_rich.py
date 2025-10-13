# ファイル名: orchestrate_jj_jules_agents_rich.py
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
目的:
  - jj の別名経由で jules CLI を呼び出す
  - 複数ワークスペース(=擬似エージェント)へ並列にセッションを投げる
  - 仕上げに、各ワークスペースの作業を 1 つのマージコミットへ統合する
前提:
  - jj が使える既存の jj リポジトリ直下で実行してください
  - jules CLI は導入・ログイン済み（npm -g @google/jules / jules login）
  - Rich が未導入なら: pip install rich
"""

from __future__ import annotations
import argparse
import concurrent.futures as cf
import os
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

# ---- 既定値（必要に応じて上書き）----
DEFAULT_BACKEND_COUNT = 3
DEFAULT_FRONTEND_COUNT = 3
DEFAULT_TEST_COUNT = 2
MERGE_MESSAGE = "各エージェント出力を統合"

COORDINATOR_PROMPT = "全体計画を作り、バックエンド/フロント/テストに配分する"
BACKEND_PROMPT_TMPL = "APIサービス backend-{i} を実装。仕様は README のとおり。単体テスト付き"
FRONTEND_PROMPT_TMPL = "UIコンポーネント frontend-{i} を実装。Storybook 追加。lint/format 対応"
TEST_PROMPT_TMPL = "E2E テスト test-{i} を Playwright で作成。CI に組み込み"
# -------------------------------------


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="jj + jules 並列オーケストレーション")
    p.add_argument("--backend", type=int, default=DEFAULT_BACKEND_COUNT, help="backend の数（0可）")
    p.add_argument("--frontend", type=int, default=DEFAULT_FRONTEND_COUNT, help="frontend の数（0可）")
    p.add_argument("--test", type=int, default=DEFAULT_TEST_COUNT, help="test の数（0可）")
    p.add_argument("--no-coordinator", action="store_true", help="coordinator を作らない")
    return p.parse_args()


ARGS = parse_args()


def check_cmd(cmd: str) -> None:
    if shutil.which(cmd) is None:
        raise RuntimeError(f"コマンドが見つかりません: {cmd}")


def run(cmd: List[str], cwd: Path | None = None) -> Tuple[int, str, str]:
    """subprocess の薄いラッパー（UTF-8で取り扱い）"""
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


def ensure_alias_for_jules() -> None:
    # aliases.jules = ["util","exec","--","jules"]
    code, out, err = run(
        ["jj", "config", "set", "--user", "aliases.jules", '["util","exec","--","jules"]']
    )
    if code != 0:
        raise RuntimeError(f"jj の別名設定に失敗しました: {err or out}")


def ensure_repo_context() -> None:
    # ここで jj が現在リポジトリを認識できるか軽く確認
    code, out, err = run(["jj", "status"])
    if code != 0:
        raise RuntimeError(
            "このディレクトリは jj リポジトリではないようです。jj リポジトリ直下で実行してください。\n"
            f"詳細: {err or out}"
        )


def create_workspaces() -> List[Tuple[Path, str]]:
    """
    ワークスペースの物理ディレクトリ作成 + `jj workspace add`。
    返り値は (作業ディレクトリ, プロンプト) のペア一覧。
    """
    WS_ROOT.mkdir(parents=True, exist_ok=True)
    pairs: List[Tuple[Path, str]] = []

    # coordinator（無効化可能）
    if not ARGS.no_coordinator:
        pairs.append((WS_ROOT / "coordinator", COORDINATOR_PROMPT))

    # backend
    for i in range(1, ARGS.backend + 1):
        pairs.append((WS_ROOT / f"backend-{i}", BACKEND_PROMPT_TMPL.format(i=i)))

    # frontend
    for i in range(1, ARGS.frontend + 1):
        pairs.append((WS_ROOT / f"frontend-{i}", FRONTEND_PROMPT_TMPL.format(i=i)))

    # test
    for i in range(1, ARGS.test + 1):
        pairs.append((WS_ROOT / f"test-{i}", TEST_PROMPT_TMPL.format(i=i)))

    if not pairs:
        raise RuntimeError("作成するワークスペースが 0 件です。引数を見直してください。")

    with Progress(transient=True) as progress:
        task = progress.add_task("[bold]ワークスペースを作成中...", total=len(pairs))
        for workdir, _ in pairs:
            workdir.parent.mkdir(parents=True, exist_ok=True)
            code, out, err = run(["jj", "workspace", "add", str(workdir)])
            if code != 0 and "already exists" not in (err + out):
                raise RuntimeError(f"ワークスペース作成に失敗: {workdir}\n{err or out}")
            progress.advance(task)

    return pairs


def invoke_jules_in(dir_and_prompt: Tuple[Path, str]) -> Tuple[Path, int, str, str]:
    d, prompt = dir_and_prompt
    # jj jules remote new --repo . --session "<prompt>"
    code, out, err = run(
        ["jj", "jules", "remote", "new", "--repo", ".", "--session", prompt], cwd=d
    )
    return d, code, out, err


def dispatch_all(pairs: Iterable[Tuple[Path, str]]) -> None:
    # 並列で投下 + 結果をテーブル表示
    pairs_list = list(pairs)
    results: List[Tuple[str, str]] = []
    with Progress(transient=True) as progress:
        task = progress.add_task("[bold]Jules セッションを送信中...", total=len(pairs_list))
        with cf.ThreadPoolExecutor(max_workers=os.cpu_count() or 8) as ex:
            futs = [ex.submit(invoke_jules_in, p) for p in pairs_list]
            for fut in cf.as_completed(futs):
                d, code, out, err = fut.result()
                if code == 0:
                    last = (out or "").splitlines()[-1] if out else "ok"
                    results.append((str(d), f"submitted: {last}"))
                else:
                    results.append((str(d), f"error: {err or out}"))
                progress.advance(task)

    table = Table(title="送信結果")
    table.add_column("Workspace")
    table.add_column("Status / Message")
    for ws, msg in sorted(results, key=lambda x: x[0]):
        table.add_row(ws, msg)
    console.print(table)


def list_sessions() -> None:
    code, out, err = run(["jules", "remote", "list", "--session"])
    if code == 0:
        console.print(Panel.fit(out, title="Jules Sessions", border_style="green"))
    else:
        console.print(Panel.fit(err or out, title="Jules Sessions (取得失敗)", border_style="red"))


def build_dynamic_parents() -> List[str]:
    """
    すべてのワークスペース名から動的に parents を作る。
    - backend*, frontend*, test* は ARGS の数に基づいて列挙
    - coordinator は有効時のみ追加
    """
    parents: List[str] = []
    parents += [str(WS_ROOT / f"backend-{i}") + "@" for i in range(1, ARGS.backend + 1)]
    parents += [str(WS_ROOT / f"frontend-{i}") + "@" for i in range(1, ARGS.frontend + 1)]
    parents += [str(WS_ROOT / f"test-{i}") + "@" for i in range(1, ARGS.test + 1)]
    if not ARGS.no_coordinator:
        parents += [str(WS_ROOT / "coordinator") + "@"]
    return parents


def merge_all_results() -> None:
    parents = build_dynamic_parents()
    if not parents:
        raise RuntimeError("マージ対象の親がありません。引数を見直してください。")

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


def main() -> None:
    # 1) 依存の存在チェック
    check_cmd("jj")
    check_cmd("jules")

    console.print(Panel.fit("jj + jules 並列オーケストレーション", border_style="cyan"))

    # 2) jj 別名（冪等に実行）
    ensure_alias_for_jules()
    console.log("aliases.jules を設定しました（jj util exec 経由）")

    # 3) jj リポジトリ配下か確認
    ensure_repo_context()
    console.log("jj リポジトリを確認しました")

    # 4) ワークスペースの作成
    pairs = create_workspaces()
    console.log(f"{len(pairs)} 個のワークスペースを用意しました")

    # 5) 各ワークスペースで jules を並列実行してセッション作成
    dispatch_all(pairs)

    # 6) セッション一覧（pull は必要に応じて手動で）
    list_sessions()
    console.print("[dim]例: 完了したセッションだけ pull する場合は、一覧の ID を選んで[/dim]")
    console.print("[dim]    jules remote pull --session <SESSION_ID>[/dim]")

    # 7) 各ワークスペースの結果を 1 つのマージコミットへ
    merge_all_results()

    console.print(Panel.fit("Done.", border_style="cyan"))


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        console.print(Panel.fit(f"[bold red]ERROR[/bold red]\n{e}", border_style="red"))
        sys.exit(1)