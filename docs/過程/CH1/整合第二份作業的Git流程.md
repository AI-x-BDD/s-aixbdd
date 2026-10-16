# 整合第二份作業的 Git 流程

第二份作業原本在另一個 repo（[stevecyj/skills](https://github.com/stevecyj/skills)），這次把它整合進本 repo（AI-x-BDD/s-aixbdd），目標是：

- 兩個 repo 的 commit 歷史都完整保留（SHA、訊息、作者、日期都不變）
- 不改動原本的 stevecyj/skills
- 第一份作業的 `homework-01` 標記不動

## 先懂幾個名詞

| 名詞 | 意思 |
| ---- | ---- |
| remote | 遠端 repo 的別名。`origin` 指向 AI-x-BDD/s-aixbdd；這次另外加了 `hw02-skills` 指向 stevecyj/skills |
| branch | 一條 commit 線的名字。這次在新分支 `integrate/homework-02-skills` 上整合，`main` 先不動 |
| tag | 釘在某個 commit 上的標記。`homework-01` 是 annotated tag（標記本身也是一個物件，有自己的 SHA `9f2d61b`），它指向的 commit 是 `30df60e` |
| merge commit | 有兩個 parent 的 commit，把兩條歷史接在一起，兩邊原本的 commit 都保留 |
| unrelated histories | 兩個 repo 從來沒有共同的祖先 commit。Git 預設拒絕合併這種歷史，要加 `--allow-unrelated-histories` |
| fast-forward（快轉） | 本機分支落後遠端、自己又沒有新 commit 時，直接把分支指標往前移到遠端的 commit，不會產生新 commit |
| PR（Pull Request） | 在 GitHub 上請求把一個分支合進另一個分支，可以先看差異、跑 CI，再決定合併 |

## 流程

### 1. 檢查起點

```bash
git remote -v                     # 確認 origin 是 AI-x-BDD/s-aixbdd
git status --porcelain            # 沒有輸出 = 工作區乾淨，沒有未提交的修改
git rev-parse homework-01^{commit}
```

- `homework-01` 是 annotated tag，`git rev-parse homework-01` 會得到標記物件本身的 SHA（`9f2d61b`）。
- 加上 `^{commit}` 才會得到它指向的 commit：`30df60e`，跟第一份作業確認的版本一致。

### 2. 加一個唯讀的 remote，取得第二份作業

```bash
git remote add hw02-skills https://github.com/stevecyj/skills.git
git remote set-url --push hw02-skills DISABLED-read-only
git fetch hw02-skills --no-tags
```

- `set-url --push` 把 push 的網址設成無效值，這樣就不可能不小心推到 stevecyj/skills。
- `fetch` 只下載 commit，不會改動本機任何分支或檔案。下載後可以用 `hw02-skills/main` 指到第二份作業最新的 commit：`9ed9c46`。
- `--no-tags`：不把對方的 tag 一起抓進來。

### 3. 開新分支，合併但先不 commit

```bash
git switch -c integrate/homework-02-skills
git merge --no-commit --no-ff --allow-unrelated-histories hw02-skills/main
```

| 參數 | 作用 |
| ---- | ---- |
| `--no-commit` | 合併完先停下來，讓我檢查和修改，之後再自己 commit |
| `--no-ff` | 一定要產生 merge commit |
| `--allow-unrelated-histories` | 允許合併沒有共同祖先的兩個 repo |

合併時只有 `README.md` 衝突，因為兩邊都有這個檔案（add/add 衝突）。其他檔案路徑沒有重疊，直接合進來。

合併中的狀態：

- `HEAD` = 第一份作業 `30df60e`
- `MERGE_HEAD` = 第二份作業 `9ed9c46`（檔案 `.git/MERGE_HEAD` 存在就代表 merge 還沒完成）

### 4. 解決衝突與調整內容

- `README.md`：手動把兩邊內容整合成一份，再 `git add README.md` 標記為已解決。
- `.claude/skills/` 裡的 symlink 改成實體目錄：

  ```bash
  git rm --cached .claude/skills/<名稱>   # 從 Git 移除 symlink 的紀錄，檔案系統另外刪除
  scripts/sync-skills.sh --from agents   # 從 .agents/skills 複製實體內容過來
  git add .claude/skills
  ```

- 其他文件修改完後，用 `git add -A` 全部 stage。

commit 前用這兩行檢查「原本的東西有沒有被改或刪」：

```bash
git diff --cached --name-status HEAD | grep -v '^A'        # 跟第一份作業比
git diff --cached --name-status MERGE_HEAD | grep -v '^A'  # 跟第二份作業比
```

- `--cached`：比較的是已 stage、準備 commit 的內容。
- `--name-status`：只列檔名和狀態代碼（`A` 新增、`M` 修改、`D` 刪除）。
- `grep -v '^A'`：濾掉新增的檔案，只看修改和刪除。

### 5. 建立 merge commit

```bash
git commit
```

因為 `MERGE_HEAD` 存在，這次 commit 自動成為 merge commit：`0f451d3`，兩個 parent 是 `30df60e` 和 `9ed9c46`。

確認兩邊歷史都在：

```bash
git log -1 --format=%P                      # 看 parent，應該有兩個
git merge-base --is-ancestor 30df60e HEAD   # exit 0 代表 30df60e 在歷史中
git merge-base --is-ancestor 9ed9c46 HEAD
```

### 6. 推送分支，開 PR

```bash
git push -u origin integrate/homework-02-skills
gh pr create --base main --head integrate/homework-02-skills ...
```

- 只推分支，沒有推 tag。
- `-u`：設定本機分支追蹤遠端分支，之後 `git pull`、`git push` 不用再指定。
- 開 PR 後 GitHub Actions 自動執行（`pull_request` 事件）。這次 CI 通過，PR 是 https://github.com/AI-x-BDD/s-aixbdd/pull/1 。

### 7. 用 merge commit 合併 PR

合併前確認：PR 的 head 還是 `0f451d3`、CI 通過、`homework-01` 還指向 `30df60e`。

```bash
gh pr merge 1 --merge --match-head-commit 0f451d3bfa894816c7a4bfe080baec32ff570112
```

- `--merge`：等於網頁上的「Create a merge commit」。
- `--match-head-commit`：PR 的 head 不是這個 commit 時拒絕合併，避免合到後來才推上去、沒檢查過的內容。
- 沒加 `--delete-branch`，所以整合分支保留著。

GitHub 產生第二個 merge commit `14cf25b`（Merge pull request #1），parent 是 `30df60e`（原本的 main）和 `0f451d3`。合併後 main 上的 CI（`push` 事件）也通過。

### 8. 更新本機 main

```bash
git switch main
git pull --ff-only
git rev-parse main origin/main   # 兩行都是 14cf25b... 就代表一樣
```

`--ff-only`：只接受快轉。本機有遠端沒有的 commit 時會直接失敗，不會偷偷產生新的 merge commit。

## 合併後的結果

```text
*   14cf25b Merge pull request #1        ← GitHub 合併 PR 產生
|\
| *   0f451d3 chore: 整合第二份作業 ...   ← 本機建立的 merge commit
| |\
| | * 9ed9c46 ... 第二份作業 17 個 commit（2026-08-14 ～ 09-25）
| | * ...
| | * e29572b feat: add shared agent skills repository
| |
|/
* 30df60e ... 第一份作業 37 個 commit（2026-09-29 ～ 10-08）
* ...
* bc3aea2 chore: initial commit
```

- main 共 56 個 commit：第一份作業 37 個、第二份作業 17 個，加上 2 個 merge commit。
- 這是示意圖，實際看用 `git log --graph --oneline main`。

## 容易誤會的地方

### 為什麼第二份作業的 commit 排在第一份作業前面

GitHub 的 commit 列表依日期排序。第二份作業的 commit 本來就比較早（8/14～9/25），第一份作業是 9/29～10/8，所以第二份作業會排在比較舊的位置。commit 沒被改，只是照原本日期排列。用 `git log --graph` 才看得出兩條線是平行的。

### 為什麼檔案旁邊只看到最新的 commit 訊息

GitHub 的檔案列表只顯示「最後一次改到這個檔案的 commit」。在 merge commit 裡改過的檔案（README、CLAUDE.md、`.claude/skills/` 等）就會顯示 merge commit 的訊息。完整歷史要看 PR 的 Commits 分頁或 `git log`。

### 合併 PR 不能選 squash 或 rebase

| 合併方式 | 結果 |
| -------- | ---- |
| Create a merge commit | 保留所有 commit，多一個 merge commit（這次用的） |
| Squash and merge | 所有 commit 壓成一個，原本的歷史不會進到 main |
| Rebase and merge | commit 被重新疊在 main 後面，SHA 全部改變 |

### 本機的 pull 設定是 rebase

這台電腦的 Git 設定有 `pull.rebase=true` 和 `branch.autosetuprebase=always`，所以 `git push -u` 時顯示「set up to track ... by rebasing」。

在有 merge commit 的分支上，如果遠端有新 commit，直接 `git pull` 會用 rebase，可能把 merge commit 攤平。更新時改用：

- `git pull --ff-only`：只快轉，不行就停下來
- `git pull --no-rebase`：用 merge 的方式更新

### 本機自己再 merge 一次，跟遠端不會一樣

PR 在 GitHub 上合併後，本機要用 `git pull --ff-only` 快轉到遠端的 commit。如果在本機另外執行 `git merge`，會產生一個不同 SHA 的 merge commit，本機和遠端的歷史就分岔了。

## 常用的核對指令

| 想確認的事 | 指令 |
| ---------- | ---- |
| 工作區有沒有未提交的修改 | `git status --short` |
| tag 指向哪個 commit | `git rev-parse homework-01^{commit}` |
| 某個 commit 在不在歷史中 | `git merge-base --is-ancestor <commit> <分支>`，exit 0 代表在 |
| 本機和遠端是否一樣 | `git fetch` 後 `git rev-parse main origin/main` |
| 看分支圖 | `git log --graph --oneline` |
| PR 包含哪些 commit | `gh pr view 1 --json commits` |
| CI 結果 | `gh run list --branch main` |
