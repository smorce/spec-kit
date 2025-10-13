# =========================================
# Windows（PowerShell）: jj と Jules Tools をグローバル導入
# =========================================

# 0) 事前チェック
node -v 2>$null; if ($LASTEXITCODE -ne 0) { Write-Host "[INFO] Node.js が無ければ公式配布や winget で導入してください（LTS推奨）" }

# 1) jj を winget または scoop で導入（公式手順）
#    どちらか一方でOK
winget install jj-vcs.jj
# scoop がある人は：
# scoop install main/jj

# 2) 初期設定（ユーザー名/メール）
jj config set --user user.name  "smorce"
jj config set --user user.email "smorcepie@gmail.com"

# 3) シェル補完（PowerShell）を永続化（公式手順）
if (!(Test-Path $PROFILE)) { New-Item -ItemType File -Path $PROFILE -Force | Out-Null }
$line = 'Invoke-Expression (& { (jj util completion power-shell | Out-String) })'
if (-not (Select-String -Path $PROFILE -Pattern [regex]::Escape($line) -Quiet)) {
  Add-Content -Path $PROFILE -Value $line
}
. $PROFILE   # 現在のセッションにも反映

# 4) Jules Tools を npm で導入（公式手順）
npm install -g @google/jules
→これがWindowsでできるようにしたい。
→サポートされた。


# 5) 初回ログイン（ブラウザで Google 認証）
jules login
→駄目だ。Windowsのサポート待ち。WSLを使っても認証できない。
→firefoxをすぐに閉じたら Your browser should open for authentication. If not, please visit: の文字が出て
URL をクリックして GoogleChrome の方で認証できた。
ただ、Jules の方は WSL に切り替えないといけないからちょっと使いづらいかも。
→Windowsでできた。

# 6) GitHub 連携（ブラウザ）： https://jules.google.com → GitHub 連携 → 対象リポジトリ選択

# 7) 確認
jj --version
jules version
jules remote list --repo
→Windowsでできた。

# 8) 既存 Git リポジトリで jj を共同配置モードに
Set-Location C:\path\to\your\repo
jj git init --colocate
jj status

# 9) Jules の TUI（対話ダッシュボード）を開く
jules

=============


# PowerShell 7+/5.1 用
# 目的: gemini CLI の代わりに「jj 経由で jules」を使って
#       複数ワークスペース(=擬似エージェント)を並列実行する

$ErrorActionPreference = "Stop"
$ProgressPreference = "SilentlyContinue"

# 0) 前提: jules CLI を導入・ログイン済み
#    npm install -g @google/jules
#    jules login
#    jules のサブコマンドは "remote new / list / pull" を使います。

# 1) jj から jules を呼べる別名を作る（1回だけ）
#    aliases.jules は TOML の配列として設定します。
jj config set --user aliases.jules '["util", "exec", "--", "jules"]'

# 2) ワークスペース（擬似エージェント）を作る
#    jj workspace add は複数作業コピーを追加します。
New-Item -Path "ws" -ItemType Directory -Force | Out-Null
jj workspace add ws/coordinator
1..3 | ForEach-Object { jj workspace add ("ws/backend-{0}"  -f $_) }
1..3 | ForEach-Object { jj workspace add ("ws/frontend-{0}" -f $_) }
1..2 | ForEach-Object { jj workspace add ("ws/test-{0}"     -f $_) }

# 3) 各ワークスペースで jules にタスクを投げる（並列）
function Invoke-JulesTaskIn {
  param([string]$Dir, [string]$Prompt)
  Start-Job -ScriptBlock {
    param($D, $P)
    Set-Location -Path $D
    & jj jules remote new --repo . --session $P
  } -ArgumentList $Dir, $Prompt
}

$jobs = @()
$root = (Get-Location).Path

$jobs += Invoke-JulesTaskIn -Dir (Join-Path $root "ws/coordinator") `
         -Prompt "全体計画を作り、バックエンド/フロント/テストに配分する"

1..3 | ForEach-Object {
  $i = $_
  $jobs += Invoke-JulesTaskIn -Dir (Join-Path $root ("ws/backend-{0}" -f $i)) `
           -Prompt ("APIサービス backend-{0} を実装。仕様は README のとおり。単体テスト付き" -f $i)
}

1..3 | ForEach-Object {
  $i = $_
  $jobs += Invoke-JulesTaskIn -Dir (Join-Path $root ("ws/frontend-{0}" -f $i)) `
           -Prompt ("UIコンポーネント frontend-{0} を実装。Storybook 追加。lint/format 対応" -f $i)
}

1..2 | ForEach-Object {
  $i = $_
  $jobs += Invoke-JulesTaskIn -Dir (Join-Path $root ("ws/test-{0}" -f $i)) `
           -Prompt ("E2E テスト test-{0} を Playwright で作成。CI に組み込み" -f $i)
}

# 送信完了を待つ（Jules の実処理は非同期で継続）
Wait-Job -Job $jobs | Out-Null
Receive-Job -Job $jobs | Write-Output
Remove-Job -Job $jobs | Out-Null

# 4) セッションIDを確認（必要に応じて pull）
jules remote list --session
# 完了したものを個別に:
# jules remote pull --session <SESSION_ID>

# 5) すべてのWSの作業結果を 1 つのマージコミットに統合
#    他WSの作業中コミットは「workspace名@」で参照できます。
$parents = @(
  "ws/backend-1@", "ws/backend-2@", "ws/backend-3@",
  "ws/frontend-1@", "ws/frontend-2@", "ws/frontend-3@",
  "ws/test-1@", "ws/test-2@", "ws/coordinator@"
)
& jj new $parents
jj commit -m "各エージェント出力を統合"

Write-Host "done."