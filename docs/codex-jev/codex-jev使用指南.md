# Codex × Jev 使用指南

Jev 判斷任務類型，Codex 將適合的工作交給輕量子代理；主模型不會被切換。
這是 Codex 工作環境設定，課程產出的 Skill 不依賴 Jev。

## 最快開始

- **已設定且路由開啟**：直接在本專案使用 Codex，不必另外輸入 Jev 指令，也不必每次重做連線測試。
- **不確定是否開啟**：執行下方查詢。`enabled` 與 `credential_available` 都是 `true` 只代表本地開關與金鑰已備妥，不檢查 API、Hook 信任、模型權限或強制停用的環境變數；有疑問依「未派工時怎麼查？」處理。
- **第一次使用或換電腦**：依下列第 1～5 步設定一次。

```sh
python3 .codex/hooks/jev_router.py status
```

查詢在專案根目錄的終端執行。2026-10-15 本機已完成設定與派工驗收；目前開關以查詢結果為準。

## 首次設定（依序操作）

以下步驟以 **macOS 終端**為準，需有 Git、`python3`（3.9 以上）與已登入的 Codex CLI。
本次驗證版本為 `0.162.1`，帳號需能使用 `gpt-6-luna`。現行 Hook 使用 POSIX shell 語法，Windows 未驗證。

### 1. 準備設定檔

將整個 `docs/codex-jev/` 目錄帶到目標 Git 專案，保留指南與以下四個安裝用檔案，無需取得原電腦的 `.codex/`：

```text
docs/codex-jev/codex-jev使用指南.md
docs/codex-jev/install.py
docs/codex-jev/hooks.json
docs/codex-jev/jev_router.py
docs/codex-jev/jev_light.toml
```

只帶指南不夠，四個安裝用檔案須一起帶走；尚未提交的檔案不會隨 clone 出現。
在目標專案根目錄執行 `git rev-parse --show-toplevel` 確認位置，再執行：

```sh
python3 docs/codex-jev/install.py
```

看到「安裝完成」或「設定已一致」再繼續。安裝器會先檢查所有來源與衝突、合併 Jev Hook，
保留其他 Hook，並將狀態目錄加入 `.gitignore`；缺檔或同名內容不同時會停止並回報，不覆蓋。
需要先預覽時執行 `python3 docs/codex-jev/install.py --check`，不會寫入檔案。

| 安裝來源 | 執行時的位置 |
| --- | --- |
| [hooks.json](hooks.json) | `.codex/hooks.json` |
| [jev_router.py](jev_router.py) | `.codex/hooks/jev_router.py` |
| [jev_light.toml](jev_light.toml) | `.codex/agents/jev_light.toml` |

同名腳本、代理或 Jev Hook 與安裝來源不同時，先比對並決定保留或更新，再重新安裝；不要刪除既有設定以強迫安裝。
執行的是 `.codex/` 裡的副本，`docs/codex-jev/` 是安裝來源。更新來源檔後，已安裝的副本不會自動更新。
不要搬移原電腦的 `.codex/jev-router/`；安裝器不複製金鑰、信任或開關狀態，也不主動變更既有開關。
接著執行 `python3 .codex/hooks/jev_router.py off`，確認設定期間路由關閉，再進行第 2 步。

### 2. 安全設定金鑰

在 TypeSafe 建立有效且有可用額度的 API key，執行以下指令，再於隱藏輸入提示中貼入金鑰：

```sh
security add-generic-password -U -a "$(id -un)" -s codex-jev-router -w
```

`-w` 必須放最後，讓系統提示輸入；不要把金鑰接在指令後、寫進 repo 或貼進對話。
Hook 可直接讀取 Keychain，不需重啟 Codex。
若選用 `TYPESAFE_API_KEY` 環境變數，須在設定它的同一終端啟動 Codex；環境變數優先於 Keychain。

### 3. 驗證連線

先執行 `python3 .codex/hooks/jev_router.py status`，確認 `credential_available` 為 `true`。這只表示讀得到金鑰，不代表有效。
再於專案根目錄執行以下測試，會送出一次不含私人資料的 Jev API 請求，不會開啟路由：

```sh
python3 - <<'PY'
import runpy
router = runpy.run_path('.codex/hooks/jev_router.py')
key = router['load_api_key']()
if not key:
    raise SystemExit('讀不到金鑰，請先完成第 2 步。')
try:
    answer = router['fetch_answer']('將 abc 轉成大寫，僅需純文字轉換。', key)
    print('API 連線成功；選項：', answer['choice'])
except Exception as error:
    print('連線失敗：', type(error).__name__, getattr(error, 'code', ''))
    raise SystemExit(1)
PY
```

### 4. 信任並開啟

在專案根目錄執行 `codex`，依提示信任專案，再於 `/hooks` 審閱並信任本專案的 `UserPromptSubmit`。
確認 Hooks 與子代理功能未被停用後，另開終端、切到同一專案根目錄，執行：

```sh
python3 .codex/hooks/jev_router.py on
```

開啟後，本輪輸入（包含貼入的內容）會送到 TypeSafe 分流；處理私人資料前先 `off`。
回到 Codex，繼續第 5 步測試派工。
金鑰、Hook 信任與開關狀態不會隨 Git 自動搬到新電腦。

### 5. 驗證自動派工

可輸入：「純文字格式轉換，無需讀寫檔案或參考其他對話。請將 abc 轉成大寫，只輸出結果。」

在 Codex 子代理畫面確認 `jev_light` 與實際模型。只看到 `ABC` 不代表有派工；
`codex exec --json` 也可能漏掉建立事件。本次驗收另以父 session 的 `spawn_agent`
及子 session 的模型紀錄確認成功。

同一題也可能未達 0.9 門檻而留在主代理，不能只憑一次未派工就判定故障。

## 日常開關與狀態

在專案根目錄的終端執行：

```sh
python3 .codex/hooks/jev_router.py status  # 查詢
python3 .codex/hooks/jev_router.py off     # 關閉
python3 .codex/hooks/jev_router.py on      # 開啟
```

`status` 顯示開關與金鑰是否可取得；Hook 是否信任，請在 Codex 的 `/hooks` 查看。
開關跨重啟保留，不必每次重新開啟。

## 哪些工作會分流？

| 工作 | 處理方式 |
| --- | --- |
| 明確的找路徑、列項目、計數、文字格式轉換 | Jev 判為 `light` 且機率與 confidence 均 ≥ 0.9 時，指示派給 `jev_light`（`gpt-6-luna`／`high`） |
| 寫檔、修改 Skill、課程審查、根因分析、設計、多步驟任務 | 留給主代理 |
| 資料不足、低信心、缺少金鑰、API 失敗或逾時 | 留給主代理 |

主代理仍須遵守完整對話、專案規範與使用者確認點。0.9 是試驗門檻，不代表正確率。

## 未派工時怎麼查？

依序檢查：

1. **開關與金鑰**：`status` 應顯示 `enabled: true`、`credential_available: true`；啟動環境的 `JEV_ROUTER_DISABLE=1` 會強制停用。
2. **Hook**：在 `/hooks` 確認本專案 Hook 已信任且啟用；Hook 定義變更後須重新審閱。`python3`、`git` 必須在 Codex 的執行環境可用。
3. **API**：重跑連線測試。`401` 先查金鑰；`429` 查額度或速率限制；逾時則查網路與服務狀態。
4. **模型與任務**：確認帳號有 `gpt-6-luna` 權限、子代理功能已開啟；多步驟、課程審查或低信心任務留在主代理屬正常行為。

不要為了看到派工就直接降低門檻。API 成功、Hook 啟用與子代理實際執行是三項不同的驗證。

## 資料與驗證範圍

- 開啟後，本輪輸入會送到 TypeSafe，包含你貼入的內容；不自動傳送歷史對話或專案檔案。處理私人資料前先 `off`。
- 目前只做輸入時的任務分流，不自動檢查中途的改善提案。
- 已驗證假設任務的完整派工鏈；尚未驗證真實複習工作的長期品質或成本節省。
- 安裝器已用乾淨暫存 Git 專案驗證安裝、合併、重複執行與失敗保護；尚未以第二台實體電腦驗證。

相關設定：`.codex/hooks.json`、`.codex/hooks/jev_router.py`、`.codex/agents/jev_light.toml`。
