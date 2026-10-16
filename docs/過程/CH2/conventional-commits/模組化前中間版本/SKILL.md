---
name: conventional-commits
description: 依 Conventional Commits 1.0.0 判斷 commit type、scope 與 breaking change，並撰寫或審查 commit message。用在：根據 git diff 寫 commit message、判斷該用 feat／fix／refactor／chore 等哪個 type、檢查既有 commit message 是否合規、處理一個 commit 混了多種修改要不要拆、dependency／CSS／revert 等容易誤判的情境，以及設計團隊的 type／scope 規則。
---

# Conventional Commits

依「修改目的」決定 type，不依「改了哪種檔案」。回答時區分規則來源：官方規定（CC 1.0.0 的 MUST）、官方建議（FAQ）、業界慣例（Angular／commitlint）、團隊規則。

## 格式（官方規定）

```text
<type>[optional scope][!]: <description>

[optional body]

[optional footer(s)]
```

- type、`:`、一個空格、description 都必須有。
- scope 可選，描述 codebase 的區域。
- description 與 body 之間空一行。
- Breaking change 可在 type／scope 後加 `!`，或以大寫 footer `BREAKING CHANGE: <說明>` 標示，兩者也可並用。官方規格第 16 條允許 `BREAKING-CHANGE: <說明>` 作為同義 footer；空格版與連字號版都合規。小寫 `breaking change:` 不符合此大寫要求。
- 官方依據：[Conventional Commits 1.0.0 規格第 11～16 條](https://www.conventionalcommits.org/en/v1.0.0/#specification)。

只有 `feat`、`fix`、`BREAKING CHANGE` 有官方語意，並對應 SemVer：

```text
fix             → PATCH
feat            → MINOR
BREAKING CHANGE → MAJOR
```

`docs`、`style`、`refactor`、`perf`、`test`、`build`、`ci`、`chore`、`revert` 是業界慣例（`@commitlint/config-conventional`、Angular），官方只允許使用其他 type，沒有定義語意。專案的 type／scope 慣例可自行約定，但不能把與官方規格衝突的要求說成官方規定。

## Decision Tree

```text
依修改目的分類：
├─ 新增以前沒有的能力             → feat
├─ 修正原本應正常卻出錯的行為     → fix
├─ 功能不變、改善效能             → perf
├─ 功能不變、整理程式結構         → refactor
├─ 只改文件                       → docs
├─ 只改測試                       → test
├─ 只改格式／空白                 → style
├─ build 系統／依賴維護           → build
├─ CI 設定                        → ci
└─ 其他維護雜務                   → chore
```

分類為預設慣例；dependency 等跨類型情境仍依實際目的判斷。

分辨 feat／fix 時問：「以前本來就應該能做到嗎？」應該能卻不能 → `fix`；以前根本沒有 → `feat`。

## 常見誤判

- **依檔案選 type**：`.css` 不等於 `style`、`package.json` 不等於 `chore`、新增程式碼不等於 `feat`（`+ if (user == null) return` 可能是修 crash，用 `fix`）。
- **`style` 指程式格式**（Prettier、空白、分號），不是 CSS／UI 樣式。產品要求的 UI 外觀改動用 `feat` 或 `fix`。
- **什麼都 `chore`**：`chore: fix login`、`chore: add export` 等於沒有 convention。
- **`refactor` 偷帶行為改變**：`refactor` 是既不修 bug 也不加功能的修改。重構時順便修 bug，目的若是修錯就用 `fix`，或拆成兩個 commit。
- **scope 範例**：沒有專案明文規則或既有慣例時，`fix(auth):` 通常比 `fix(UserLoginDialogModal.vue):` 更容易辨識功能區域；檔名並非官方禁止的寫法。

dependency 升級、CSS 修改、revert、type 寫錯、squash merge 等情境的判斷與範例，見 [references/cases.md](references/cases.md)。

## 範例

```text
feat(report): add Excel export
fix(table): ignore stale pagination responses
refactor(user): migrate profile component to Composition API
docs(api): document authentication
style: format source files
chore(deps): update Vue to 3.6
```

有 body 的 fix：

```text
fix(search): prevent stale responses replacing latest results

Ignore responses whose request ID does not match the latest request.
```

Breaking change 標示範例：

```text
feat(api)!: replace users endpoint with members endpoint
```

```text
feat(api): replace users endpoint with members endpoint

BREAKING CHANGE: /users/:id has been replaced by /members/:id
```

## 送出前檢查

1. 這個 commit 只有一個主要目的嗎？
2. 是新增能力，還是修原本的錯誤？
3. 都不是的話，真正性質是什麼？
4. scope 能讓人更快知道影響區域嗎？
5. 有沒有讓原本正常的使用方式失效？

# SOP

## Phase 1 -- 判斷與交付

1. `READ` 使用者需求與提供的變更摘要或待審查訊息；依 repository 產生訊息時，讀取 `git status`、`git diff --staged`，沒有 staged 時讀取 `git diff`，建立「本次輸入」。
2. `READ` 有專案環境時，讀取適用的 CONTRIBUTING 規範、commitlint 設定與 `git log --oneline -30`，建立「專案慣例」；沒有專案環境時採用本 Skill 的預設慣例。
3. `THINK` 從「本次輸入」找出修改目的，依開頭的來源分類區分官方規格、官方建議、業界慣例與團隊規則。
4. `THINK` 確認是否為單一 logical change；混了多個無關目的時，依官方 FAQ 建議拆成多個 commit，提出拆分方式與各自的 message。
5. `THINK` 依 Decision Tree 與「專案慣例」決定 type。
6. `THINK` 決定 scope：優先遵守專案明文規則；沒有規則時沿用既有慣例，再以功能、模組、package 或 domain 為預設建議。檔名若能代表影響區域，也可以使用；scope 的官方要求見格式區。
7. `THINK` 判斷是否破壞既有使用方式（API、設定、資料格式、公開介面）；依格式區的官方規定處理 breaking 標示。
8. `WRITE` 撰寫或審查 description：使用祈使句，說明實際改了什麼；`fix: fix bug`、`update`、`misc changes` 不合格。語言優先依專案明文規則，再沿用 git log 慣例。
9. `WRITE` 需要時補充 body：為什麼改、之前發生什麼、為什麼選這種解法。小改動不用 body。
10. `CHECK` 依格式區、判斷規則、「專案慣例」及送出前檢查逐項核對訊息或審查結論；未通過時修正後重查。
11. `DELEGATE` 使用者明確要求 commit 時才使用 Git 建立 commit；只要求訊息或審查時交付文字結果，不變更 index 或檔案。

完成條件：訊息或審查結論已通過檢查，規則來源可辨識，且 Git 操作符合使用者授權範圍。
