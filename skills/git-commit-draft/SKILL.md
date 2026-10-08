---
name: git-commit-draft
description: 根據目前 Git 變更產出 commit message 草稿預覽，但不實際建立 commit，支援 Conventional Commit 風格與多版本 wording 比較。
---

# Git Commit Draft

根據目前 repository 的變更內容，產出可預覽、可修改的 Git commit 草稿，但不得直接執行 `git commit`。

## 使用時機

- 先看 commit message 草稿
- 比較 2 到 3 個 commit 寫法
- 用 Conventional Commit 風格整理訊息
- 先確認 wording，再決定是否真的 commit

## 語言偏好

- 預設使用繁體中文說明
- `type` 必須維持英文 Conventional Commit 關鍵字，例如 `feat`、`fix`、`improvement`、`docs`、`refactor`
- 預設產出「英文 type + 中文 description」的 commit 草稿
- 例如：`fix(pk10): 調整單式清空號碼按鈕顏色`
- 不要把 `type` 翻成中文
- 除非用戶明確要求，否則不要優先產出全英文版本
- 若需要備選版本，可補充一版較自然的英文 commit，但中文版本仍應放在前面

## 核心原則

- 只產出草稿，不建立 commit
- 不自動 `git add`
- 不自動 `git commit`
- 不自動 `git push`
- 若偵測到疑似 secrets 檔案，必須明確警告
- 若變更明顯混雜多個主題，必須提醒應拆成多個 commit

## 工作流程

### 1. 檢查目前 Git 狀態

優先查看：

```bash
git status --short
git diff --staged
git diff
git log -5 --oneline
```

判斷規則：

- 若已有 staged changes，優先以 staged diff 起草
- 若沒有 staged changes，改以 working tree diff 起草
- 若 staged 與 unstaged 同時存在，需明確說明草稿是根據哪一部分產生

### 2. 分析變更意圖

根據 diff 判斷：

- `type`: `feat`、`fix`、`improvement`、`docs`、`style`、`refactor`、`perf`、`test`、`build`、`ci`、`chore`、`revert`
- `scope`: 可選，用括號包覆，例如 `(pk10)`、`(api)`，通常用模組名、目錄名、功能名
- `description`: 一行摘要，使用祈使語氣，盡量控制在 72 字元內
- `body`: 可選，用條列式呈現（每行以 `- ` 開頭，一點一個變更目的／原因）
- `footer`: 可選，用於 issue reference 或 breaking change

### 3. 產出草稿預覽

預設至少回傳：

- 1 個推薦草稿（含結構說明）
- 1 到 2 個備選草稿（含各自的說明）
- 使用清晰的格式分隔不同草稿與說明
- 說明文字以繁體中文撰寫

每個草稿都應包含：

- **類型 type**: Conventional Commit 類型（英文）
- **可選的作用範圍 scope**: 模組或功能名稱
- **描述 description**: 一行摘要（預設繁體中文）
- **可選的正文 body**: 條列式補充說明（每點以 `- ` 開頭）
- **可選的頁腳 footer**: issue reference 或 breaking change

若變更內容很單純，也可以只提供：

- 1 個推薦草稿（含說明）
- 1 個備選草稿（含說明）

### 4. 嚴格禁止直接提交

不得執行：

```bash
git add
git commit
git push
```

除非用戶在後續訊息中明確要求真正建立 commit，否則此 skill 僅止於草稿預覽。

## 回覆格式

```text
<類型 type>[可選的作用範圍 scope]: <描述 description>

- [可選的正文 body 條列點 1]
- [可選的正文 body 條列點 2]

[可選的頁腳 footer]

<說明內容（全部移到訊息區塊之後）>
```

## 撰寫規則

- 使用祈使語氣：`add`、`fix`、`update`，不要用 `added`、`fixed`
- `type` 一律使用英文標準值，不可自創中文 type
- `body` 一律使用條列式（每行以 `- ` 開頭），一點一個變更目的；優先描述變更目的，不要只是列出改了哪些檔案
- `scope` 只在有助辨識時才加
- 只有真正 breaking change 才使用 `!` 或 `BREAKING CHANGE:`
- 如果 diff 顯示是 UI 微調，優先使用清楚的功能描述，不要寫得過度抽象
- description 預設可用自然、精簡的繁體中文，不必強制英文
- 若中文 description 過長，優先縮短語意，不要硬塞過多細節

## 風險檢查

若發現以下情況，必須在草稿前先提醒：

- `.env`、金鑰、憑證、token 類檔案出現在變更中
- 同時混有功能、重構、格式化等不同類型的大量變更
- 目前變更不足以推斷明確意圖

## 最後一步

輸出草稿後，停在預覽階段。可補一句：

- 「如果你要，我可以再幫你縮短、改語氣，或補一版英文 commit。」
- 「如果你選好其中一版，我再幫你微調，不會直接 commit。」
