# 容易誤判的情境

## 目錄

- Dependency 升級
- CSS 修改
- Options API → Composition API
- 一個 commit 同時符合兩個 type
- Revert
- Commit type 寫錯
- Squash merge 與 feature branch 的暫存 commit
- 工具鏈：commitlint 與 semantic-release

## Dependency 升級

沒有唯一答案，看升級目的（業界慣例）：

```text
純維護                   → chore(deps): update Vue to 3.6
為了修實際 bug           → fix(deps): update Vue to resolve hydration issue
為了使用新的產品能力     → feat: support <新能力>
```

`package.json` 有變動時，先問這次修改真正的目的。

## CSS 修改

`style` 在 Angular-style convention 指程式格式，CC 官方沒有定義。

```text
產品需求（CTA 改成新品牌樣式） → feat(checkout): update checkout CTA appearance
樣式原本就錯（按鈕顏色不符規格） → fix(<scope>): ...
重新排列 CSS、跑 Prettier       → style: format stylesheets
```

## Options API → Composition API

UI 與行為完全不變時，不是 `feat`：

```text
refactor(user): migrate profile component to Composition API
```

## 一個 commit 同時符合兩個 type

官方 FAQ 建議可以的話拆成多個 commit：

```text
feat(search): add employee search
fix(date): correct timezone conversion
```

比 `feat: add search and fix date bug` 好。如果 staged 內容混在一起，建議用 `git add -p` 分批 stage。

## Revert

官方刻意交給工具處理，只建議一種寫法（官方建議，細節由工具與團隊決定）：

```text
revert: remove experimental checkout

Refs: 676104e
```

## Commit type 寫錯

例如 `fix: add Excel export` 應該是 `feat`。

- 還沒 merge 或 release：官方 FAQ 建議用 rebase 修改歷史（最近一個 commit 用 `git commit --amend`）。
- 已經正式發布或推到共用分支：不要為了漂亮的歷史改公開的 Git history，依 release 流程處理。改寫已 push 的歷史前一定要先問使用者。

## Squash merge 與 feature branch 的暫存 commit

官方 FAQ 承認 squash merge workflow。feature branch 裡的 `wip`、`review fix` 可以不合規，只要 squash 進 `main` 時的 message 合規即可，例如 `feat(report): add Excel export`。需要保持乾淨的是 `main` 的 history。

## 工具鏈：commitlint 與 semantic-release

- commitlint 檢查 commit message，常搭配 `@commitlint/config-conventional`。專案有 `commitlint.config.*` 或 `.commitlintrc*` 時，讀它確認允許的 type、scope 與長度限制。
- semantic-release 依 commit 決定版本：`feat`、`fix`、`BREAKING CHANGE` 直接決定版本號，type 用錯版本號就跟著錯。有自動 release 的專案要特別注意 feat／fix／breaking 的判斷。
- 一次性 demo、學習 sandbox 用 CC 沒問題，但不需要為它建立 commitlint、Husky、release pipeline。
