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
- Breaking change 二選一或並用：type／scope 後加 `!`，或 footer 寫 `BREAKING CHANGE: <說明>`。

只有 `feat`、`fix`、`BREAKING CHANGE` 有官方語意，並對應 SemVer：

```text
fix             → PATCH
feat            → MINOR
BREAKING CHANGE → MAJOR
```

`docs`、`style`、`refactor`、`perf`、`test`、`build`、`ci`、`chore`、`revert` 是業界慣例（`@commitlint/config-conventional`、Angular），官方只允許使用其他 type，沒有定義語意。專案若有 commitlint 設定或 CONTRIBUTING 規範，以專案規則為準。

## 工作流程

1. 讀 diff（`git diff --staged`，沒有 staged 就看 `git diff` 與 `git status`）。
2. 找出修改目的。檔案類型只是線索，不是判斷依據。
3. 確認是不是單一 logical change。混了多個目的（例如新功能＋順手修 bug＋格式化），依官方 FAQ 建議拆成多個 commit，提出拆分方式與各自的 message。
4. 用下方 Decision Tree 決定 type。
5. 決定 scope：對應功能、模組、package 或 domain（`auth`、`checkout`、`report`），不用檔名（不要 `fix(UserDialog.vue):`）。先看 `git log --oneline -30` 沿用專案既有的 scope。
6. 判斷是否破壞既有使用方式（API、設定、資料格式、公開介面）。是就加 `!` 或 `BREAKING CHANGE` footer。
7. 寫 description：祈使句、說明實際改了什麼。`fix: fix bug`、`update`、`misc changes` 不合格。語言沿用專案 git log 的慣例。
8. 需要時寫 body：為什麼改、之前發生什麼、為什麼選這種解法。小改動不用 body。
9. 使用者要求 commit 才執行 commit；只要求寫 message 就只給 message。

## Decision Tree

```text
這次修改有改變系統行為嗎？
│
├─ 沒有
│   ├─ 只改文件         → docs
│   ├─ 只改測試         → test
│   ├─ 只改格式／空白   → style
│   ├─ 整理程式結構     → refactor
│   ├─ build 系統／依賴 → build
│   ├─ CI 設定          → ci
│   └─ 其他維護雜務     → chore
│
└─ 有
    ├─ 新增以前沒有的能力？           → feat
    ├─ 原本就該正常，但其實是錯的？   → fix
    └─ 行為相同但更快？               → perf

決定後再問：是否破壞既有使用方式？是 → 加 ! 或 BREAKING CHANGE
```

分辨 feat／fix 時問：「以前本來就應該能做到嗎？」應該能卻不能 → `fix`；以前根本沒有 → `feat`。

## 常見誤判

- **依檔案選 type**：`.css` 不等於 `style`、`package.json` 不等於 `chore`、新增程式碼不等於 `feat`（`+ if (user == null) return` 可能是修 crash，用 `fix`）。
- **`style` 指程式格式**（Prettier、空白、分號），不是 CSS／UI 樣式。產品要求的 UI 外觀改動用 `feat` 或 `fix`。
- **什麼都 `chore`**：`chore: fix login`、`chore: add export` 等於沒有 convention。
- **`refactor` 偷帶行為改變**：`refactor` 是既不修 bug 也不加功能的修改。重構時順便修 bug，目的若是修錯就用 `fix`，或拆成兩個 commit。
- **scope 太細**：`fix(UserLoginDialogModal.vue):` → `fix(auth):`。

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

Breaking change 兩種寫法：

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
