# Conventional Commits：從不熟到能獨立判斷

> Conventional Commits 描述的是這次修改的意圖與影響。

所以不用死背 `feat / fix / refactor / chore`。每次 commit 前，先問：

```text
這次改動在做什麼？
        ↓
有新增能力嗎？
有修正錯誤嗎？
有破壞既有相容性嗎？
        ↓
才決定 type
```

本筆記以目前的正式版本 Conventional Commits 1.0.0 為準。

---

## 0. 資料來源

本筆記參考以下資料，其中以第一份為主：

1. [Conventional Commits 1.0.0 官方規格](https://www.conventionalcommits.org/en/v1.0.0/)
2. [Semantic Versioning 2.0.0](https://semver.org/spec/v2.0.0.html)
3. commitlint 官方文件
4. Angular Commit Message Guidelines
5. semantic-release 官方文件

閱讀時要分清楚每條規則屬於哪一種：

| 分類         | 意思                                          |
| ------------ | --------------------------------------------- |
| **官方規定** | Conventional Commits 規格明確 MUST / MUST NOT |
| **官方建議** | 官方 FAQ 建議這樣做                           |
| **業界慣例** | 很多人這樣使用，但 CC 沒有強制                |
| **團隊規則** | 公司自己決定                                  |
| **實務經驗** | 用來協助你判斷模糊案例                        |

例如 `feat`、`fix` 和 `BREAKING CHANGE` 在規格中有正式語意。`docs`、`style`、`refactor`、`perf`、`test`、`build`、`ci`、`chore` 雖然非常常見，但 Conventional Commits 並沒有規定它們代表什麼，[官方只是允許使用其他 type](https://www.conventionalcommits.org/en/v1.0.0/#summary)。

---

## 1. 核心目的

沒有規範時，Git history 很容易變成這樣：

```text
fix
update
修改
again
update css
bug fix
final
final 2
```

這時執行 `git log`，你根本不知道發生過什麼。Conventional Commits 會把它變成：

```text
feat(auth): add Google login
fix(cart): prevent duplicate checkout
refactor(order): extract price calculator
docs(api): document authentication
```

人能讀，程式也能讀。[官方列出的用途](https://www.conventionalcommits.org/en/v1.0.0/#why-use-conventional-commits)包括：

- 自動產生 CHANGELOG
- 自動判斷版本
- 清楚表達修改內容
- 觸發 CI/CD
- 讓 Git history 更容易理解

---

## 2. 格式與組成

[官方格式](https://www.conventionalcommits.org/en/v1.0.0/#summary)如下：

```text
<type>[optional scope][!]: <description>

[optional body]

[optional footer(s)]
```

以 `fix(auth): prevent expired token reuse` 為例，拆開來是：

```text
fix
│
├── type
│
(auth)
│
├── scope
│
prevent expired token reuse
│
└── description
```

### type

type 回答「這個 commit 是什麼性質的修改？」。其中 `feat` 和 `fix` 由[官方正式定義](https://www.conventionalcommits.org/en/v1.0.0/#specification)：

```text
feat = 新功能
fix  = 修 Bug
```

### scope

scope 回答「影響哪個區域？」，例如：

```text
feat(auth):
fix(cart):
refactor(order):
```

[官方規定](https://www.conventionalcommits.org/en/v1.0.0/#specification) scope 是可選的，而且應描述 codebase 的某個區域。實務上可能是 `auth`、`checkout`、`order`、`user`、`admin`、`api`、`router`；Monorepo 則可能是：

```text
feat(web):
fix(api):
feat(shared):
```

scope 要用哪些名稱，通常屬於團隊規則。

### description

description 是[官方要求](https://www.conventionalcommits.org/en/v1.0.0/#specification)的必要部分，用一句話說明「這次實際改了什麼？」。例如：

```text
fix(login): prevent duplicate login requests
```

`fix(login): fix bug` 則沒有提供任何資訊。

### body

需要更多資訊時才寫 body。[官方允許 body](https://www.conventionalcommits.org/en/v1.0.0/#specification)，並要求 description 與 body 之間空一行：

```text
fix(search): prevent stale responses replacing latest results

Ignore responses whose request ID does not match the latest request.
```

實務上 body 最有價值的是回答三件事：為什麼要改、之前發生什麼、為什麼選這種解法。Angular 的實務規範也要求 body 說明修改動機。

---

## 3. 方法論：真正的判斷順序

依照改了什麼檔案來判斷，很容易出錯：

```text
改 Vue → feat？
改 CSS → style？
改 test → test？
```

應該依序問：

```text
① 使用者 / 系統以前能不能做到？
        ↓
② 現在是不是新增能力？
        ↓
③ 還是在修正本來應該正常的東西？
        ↓
④ 還是行為完全沒變，只整理內部？
        ↓
⑤ 有沒有破壞既有使用方式？
```

簡化成對照：

```text
新增能力             → feat
修正錯誤             → fix
行為不變，只整理程式 → refactor
只改文件             → docs
只改測試             → test
```

其中 `refactor`、`docs`、`test` 是常見 convention，不是 CC 強制規格。

---

## 4. 完整工作流程

完成一段修改後，依這個順序走：

```text
看 diff
↓
找出修改目的
↓
判斷是不是一個完整的 logical change
↓
判斷 feat / fix / 其他
↓
判斷是否需要 scope
↓
判斷是否 Breaking Change
↓
寫 description
↓
必要時寫 body/footer
↓
commit
```

例如 diff 裡出現：

```diff
+ export function exportToExcel() {}
```

先別因為「新增了一個 function」就用 `feat`。要先問使用者是不是因此得到以前沒有的能力，是的話才寫成：

```text
feat(report): add Excel export
```

---

## 5. 官方規則

以下規則出自 [Conventional Commits 規格](https://www.conventionalcommits.org/en/v1.0.0/#specification)。

### ① 一定要有 type

格式必須包含 type、`:` 和一個空格。要寫：

```text
feat: add export
```

不能只寫 `add export`。

### ② 新功能用 `feat`

官方定義：

```text
feat = adds a new feature
```

### ③ Bug fix 用 `fix`

```text
fix = bug fix
```

### ④ scope 可有可無

以下兩種都合法：

```text
fix: prevent crash
fix(parser): prevent crash
```

### ⑤ Breaking Change 要明確標記

官方有兩種合法方式。第一種是在 type 或 scope 後面加 `!`：

```text
feat!: change authentication API
feat(auth)!: change token format
```

第二種是加上 `BREAKING CHANGE` footer：

```text
feat: change authentication API

BREAKING CHANGE: tokens must now be passed in the Authorization header
```

---

## 6. Decision Tree

不知道該用哪個 type 時，直接跑這棵樹：

```text
這次修改有改變系統行為嗎？
│
├─ 沒有
│   │
│   ├─ 只改文件 → docs
│   ├─ 只改測試 → test
│   ├─ 整理程式結構 → refactor
│   └─ 工具/設定/雜務 → build / ci / chore
│
└─ 有
    │
    ├─ 新增以前沒有的能力？ → feat
    │
    └─ 原本應該正常，但其實錯了？ → fix

    決定 feat 或 fix 之後，再問：
    是否破壞既有使用方式？
    └─ 是 → 加 ! 或 BREAKING CHANGE
```

其中 `feat`、`fix` 和 breaking change 是官方語意，其他分類是常見的業界 convention。

---

## 7. feat vs fix

分辨時問：「以前本來就應該能做到嗎？」

### 本來就應該可以，結果不能 → `fix`

例如需求本來就是「使用者登入後可以看到會員資料」，但某些帳號看不到。修好之後：

```text
fix(member): display profile for imported accounts
```

### 以前根本沒有這個能力 → `feat`

例如以前完全沒有 Excel 匯出，新增之後：

```text
feat(report): add Excel export
```

---

## 8. refactor

`refactor` 最簡單的 Mental Model：

> 外面看起來一樣，裡面換了一種寫法。

例如之前呼叫 `calculatePrice()`，現在還是呼叫 `calculatePrice()`，輸入輸出完全一樣，只是把 500 行的 component 拆成 `usePrice()`、`useDiscount()`、`useTax()`。這比較像：

```text
refactor(order): extract pricing logic
```

Angular 將 `refactor` 定義為：

> 不修 bug，也不新增 feature 的程式修改。

所以如果你在重構時順便修掉 Bug，用 `refactor` 不一定對。真正的目的如果是修錯誤，就該用 `fix`。

---

## 9. style 的常見誤解

在常見的 Angular-style convention 中，`style` 通常指 formatting、whitespace、semicolon 這類程式格式，跟 CSS 或 UI 樣式無關，很多前端工程師會搞混。這個用法來自業界 convention，Conventional Commits 官方沒有定義。

例如用 Prettier 重新格式化，可以寫：

```text
style: format source files
```

但如果是「把登入按鈕改成紅色」這種產品 UI 需求，下面的寫法也完全可能比 `style` 更合理：

```text
feat(login): update primary button appearance
```

---

## 10. chore 是什麼？

`chore` 是最容易被濫用的 type。常見理解是「不屬於產品 feature 或 bug fix 的維護工作」，例如：

```text
chore: update eslint config
chore: update development dependencies
```

Conventional Commits 官方沒有定義 `chore` 的語意，[只是允許使用其他 type](https://www.conventionalcommits.org/en/v1.0.0/#summary)。所以 `chore` 到底包含什麼，應由團隊決定。

---

## 11. Breaking Change

白話來說，Breaking Change 就是：

> 你改完之後，原本正常使用你東西的人，可能必須修改他的程式。

例如 API 原本是 `GET /users/:id`，改成 `GET /members/:id` 之後，舊程式呼叫 `GET /users/123` 會直接壞掉。這時要寫成：

```text
feat(api)!: replace users endpoint with members endpoint
```

或者：

```text
feat(api): replace users endpoint with members endpoint

BREAKING CHANGE: /users/:id has been replaced by /members/:id
```

Conventional Commits [將 Breaking Change 對應到](https://www.conventionalcommits.org/en/v1.0.0/#summary) Semantic Versioning 的 MAJOR。

---

## 12. Conventional Commits 與 SemVer

Conventional Commits 描述修改，Semantic Versioning 描述版本。[Conventional Commits 官方](https://www.conventionalcommits.org/en/v1.0.0/#summary)明確寫了兩者的對應關係：

```text
fix             → PATCH   1.2.3 → 1.2.4
feat            → MINOR   1.2.3 → 1.3.0
BREAKING CHANGE → MAJOR   1.2.3 → 2.0.0
```

[SemVer 本身的規則](https://semver.org/spec/v2.0.0.html#summary)則是：

```text
PATCH = 相容的 bug fix
MINOR = 相容的新功能
MAJOR = 不相容 API 修改
```

---

## 13. scope 怎麼判斷

scope 應該對應功能、模組、package 或 domain：

```text
fix(auth):
fix(schedule):
fix(employee):
feat(report):
```

用檔名當 scope，例如 `fix(UserDialog.vue):`，通常不好。你的 Vue 專案可能會建立 `auth`、`employees`、`schedules`、`reports`、`settings` 這些 scope。這屬於團隊規則，像 Angular 就直接維護自己的合法 scope 清單。

---

## 14. 一個 commit 同時符合兩個 type 怎麼辦？

例如同一次修改裡新增了搜尋功能，又順便修了日期 Bug，看起來同時是 `feat` 和 `fix`。[官方 FAQ](https://www.conventionalcommits.org/en/v1.0.0/#what-do-i-do-if-the-commit-conforms-to-more-than-one-of-the-commit-types) 建議，可以的話就拆成多個 commit：

```text
feat(search): add employee search
fix(date): correct timezone conversion
```

拆開通常比合在一起的 `feat: add search and fix date bug` 更好。

---

## 15. 案例一：新增功能

需求：新增「匯出 Excel」。

- **分析**：以前不能匯出 Excel，現在可以。
- **判斷**：新增能力。
- **Commit**：

```text
feat(report): add Excel export
```

---

## 16. 案例二：修正錯誤

Bug：切換頁碼太快時，舊 API response 會蓋掉新資料。

- **分析**：產品原本就應該顯示最新頁面，現在行為錯誤。
- **判斷**：不是新增能力，是修錯誤。
- **Commit**：

```text
fix(table): ignore stale pagination responses
```

如果需要解釋原因，加上 body：

```text
fix(table): ignore stale pagination responses

Only apply responses matching the latest request ID.
```

---

## 17. 案例三：容易誤判成 feat 的 refactor

把 component 從 Options API 改成 Composition API，UI 完全一樣。很多新人會寫：

```text
feat: migrate component to Composition API
```

但這次沒有新功能，比較合理的是：

```text
refactor(user): migrate profile component to Composition API
```

---

## 18. 案例四：dependency update

把 Vue 3.5 升到 Vue 3.6，該用 `chore`、`build`、`fix` 還是 `feat`？沒有唯一答案，要看為什麼升級。

純維護：

```text
chore(deps): update Vue to 3.6
```

為了修某個實際 Bug，可能是：

```text
fix(deps): update Vue to resolve hydration issue
```

為了使用新的產品能力，也可能是：

```text
feat: support ...
```

所以看到 package.json 有變動，也要先問這次修改真正的目的是什麼，再選 type。

---

## 19. 案例五：CSS 修改

修改：

```css
button {
  color: red;
}
```

是不是 `style`，要看修改目的。如果這是產品需求，例如「CTA 按鈕改成新的品牌樣式」，可能寫成：

```text
feat(checkout): update checkout CTA appearance
```

如果只是重新排列 CSS、跑 Prettier、調整空格或格式，才比較像：

```text
style: format stylesheets
```

---

## 20. Revert

Conventional Commits 沒有完整規定 revert 的語意與版本影響，[官方刻意交給工具處理](https://www.conventionalcommits.org/en/v1.0.0/#how-does-conventional-commits-handle-revert-commits)，只提供一種建議寫法：

```text
revert: remove experimental checkout

Refs: 676104e
```

所以 revert 的寫法屬於官方建議，細節由工具與團隊規則決定。

---

## 21. commit 寫錯怎麼辦？

例如寫成 `fix: add Excel export`，實際上應該是 `feat: add Excel export`。

如果還沒 merge 或 release，[官方建議](https://www.conventionalcommits.org/en/v1.0.0/#what-do-i-do-if-i-accidentally-use-the-wrong-commit-type)可以用 `git rebase -i` 修改歷史。如果已經正式發布，就不要為了漂亮的歷史亂改公開的 Git history，怎麼處理要看 release 流程。

---

## 22. 所有人都必須從第一個 commit 遵守嗎？

不一定。[官方 FAQ](https://www.conventionalcommits.org/en/v1.0.0/#do-all-my-contributors-need-to-use-the-conventional-commits-specification) 明確承認 Squash Merge 的 workflow。開發者 branch 裡可以有 `fix`、`wip`、`review fix`、`again` 這類 commit，只要最後 merge PR 時 squash 成：

```text
feat(report): add Excel export
```

就可以。

需要保持乾淨的可能只有 `main` 的 history，feature branch 裡的暫存 commit 不用。

---

## 23. 什麼時候特別值得用？

| 專案類型              | 價值     |
| --------------------- | -------- |
| 多人專案              | 值得     |
| 需要 CHANGELOG        | 非常值得 |
| library / npm package | 非常值得 |
| 自動 release          | 幾乎必要 |
| 長期維護專案          | 值得     |
| Monorepo              | 很有價值 |

---

## 24. 什麼時候價值比較低？

例如一次性 demo、學習 sandbox、幾小時後就刪掉的 prototype。你當然還是可以用，但建立 commitlint、Husky、release pipeline 和 scope 規則，可能比專案本身還複雜。這時候不用過度工程化。

---

## 25. 常見錯誤

### 錯誤 1：根據檔案種類選 type

```text
.vue → feat
.css → style
.spec.js → test
package.json → chore
```

這是錯的，應該先看修改目的。

### 錯誤 2：什麼都 chore

```text
chore: fix login
chore: add export
chore: refactor api
```

最後跟沒有 convention 差不多。

### 錯誤 3：什麼都 feat

「新增程式碼」不等於「新增 feature」。例如：

```diff
+ if (user == null) return
```

這可能其實是在修 crash，應該用 `fix`。

### 錯誤 4：refactor 偷帶行為改變

例如一個標成 `refactor(auth): simplify authentication` 的 commit，實際上同時包含重構、改 token 過期規則和修 bug。這會讓 history 很難理解。

### 錯誤 5：scope 太細

`fix(UserLoginDialogModal.vue):` 通常沒有必要，`fix(auth):` 比較合理。

---

## 26. commitlint 是什麼角色？

Conventional Commits 是規格，commitlint 是幫你檢查 commit message 的工具。例如 CI 可以擋下 `hello world` 這種訊息，要求寫成 `feat: add search`。

commitlint 支援 type、scope、subject、body、footer 等規則，也能使用 [`@commitlint/config-conventional`](https://github.com/conventional-changelog/commitlint/tree/master/%40commitlint/config-conventional)。

---

## 27. semantic-release 是什麼角色？

可以理解成：

```text
Conventional Commits
        ↓
semantic-release 讀 commit
        ↓
決定版本
        ↓
產生 Release / CHANGELOG
```

semantic-release 的 commit analyzer 可以根據 commit 判斷 release 類型。這時 `feat`、`fix`、`BREAKING CHANGE` 會直接決定版本號，type 用錯，版本號就跟著錯。

---

## 28. 實戰速查表

| 情況               | 建議 type               | 性質                     |
| ------------------ | ----------------------- | ------------------------ |
| 新增使用者能力     | `feat`                  | **官方**                 |
| 修正錯誤行為       | `fix`                   | **官方**                 |
| 不相容修改         | `!` / `BREAKING CHANGE` | **官方**                 |
| 只改文件           | `docs`                  | 業界慣例                 |
| 行為不變的程式重構 | `refactor`              | 業界慣例                 |
| 改善效能           | `perf`                  | 業界慣例                 |
| 只改測試           | `test`                  | 業界慣例                 |
| 格式、空格等       | `style`                 | 業界慣例                 |
| CI 設定            | `ci`                    | 業界慣例                 |
| build system       | `build`                 | 業界慣例                 |
| 維護雜務           | `chore`                 | 業界慣例                 |
| 回復 commit        | `revert`                | 官方有建議，但未完整規範 |

這些常見類型可在 [commitlint](https://github.com/conventional-changelog/commitlint/tree/master/%40commitlint/config-conventional) 和 Angular conventions 看到，但團隊可以修改。

---

## 29. 工作時真正要記的 Checklist

準備 commit 前只問 5 題：

```text
1. 這個 commit 只有一個主要目的嗎？
          ↓
2. 是新增能力，還是修原本錯誤？
          ↓
3. 如果都不是，真正性質是什麼？
          ↓
4. scope 能不能讓人更快知道影響區域？
          ↓
5. 有沒有讓原本正常使用方式失效？
```

對應的答案：

```text
新增能力 → feat
修錯     → fix
行為不變 → refactor / docs / test / ...
不相容   → ! 或 BREAKING CHANGE
```


---

## 30. 進階能力

學完 Conventional Commits，下一層應該串這些：

```text
Git commit 設計
        ↓
Atomic Commit
（一個 commit 一個完整目的）
        ↓
Conventional Commits
        ↓
Squash / Rebase
        ↓
commitlint
        ↓
SemVer
        ↓
CHANGELOG
        ↓
semantic-release
        ↓
CI/CD 自動發布
```

如果一個 commit 同時包含新功能、bug fix、refactor、格式化和 dependency update，怎麼選 type 都很痛苦，所以要先做好 Atomic Commit。[官方 FAQ](https://www.conventionalcommits.org/en/v1.0.0/#what-do-i-do-if-the-commit-conforms-to-more-than-one-of-the-commit-types) 也建議，一個 commit 同時符合多個 type 時，盡可能拆成多個 commit。

---

## 最後的能力地圖

```text
完全不懂
↓
知道基本格式
feat(scope): description
↓
知道 feat / fix / breaking change
↓
不再根據「改什麼檔案」選 type
↓
開始根據「修改目的」判斷
↓
會區分 feat / fix / refactor
↓
會合理使用 scope
↓
會拆 Atomic Commit
↓
會處理 Breaking Change
↓
會處理 revert / dependency / mixed changes
↓
會建立團隊 type / scope 規則
↓
接 commitlint
↓
接 SemVer / semantic-release
↓
能獨立設計整個 Commit → Release 流程
```

---

## 參考連結

[Conventional Commits 1.0.0（約定式提交）](https://www.conventionalcommits.org/en/v1.0.0/)

[Conventional Commits：Summary（摘要）](https://www.conventionalcommits.org/en/v1.0.0/#summary)

[Conventional Commits：Specification（規範條文）](https://www.conventionalcommits.org/en/v1.0.0/#specification)

[Conventional Commits：Why Use（為什麼要用）](https://www.conventionalcommits.org/en/v1.0.0/#why-use-conventional-commits)

[Conventional Commits FAQ：一個 commit 符合多個 type](https://www.conventionalcommits.org/en/v1.0.0/#what-do-i-do-if-the-commit-conforms-to-more-than-one-of-the-commit-types)

[Conventional Commits FAQ：用錯 commit type](https://www.conventionalcommits.org/en/v1.0.0/#what-do-i-do-if-i-accidentally-use-the-wrong-commit-type)

[Conventional Commits FAQ：所有人都要遵守嗎](https://www.conventionalcommits.org/en/v1.0.0/#do-all-my-contributors-need-to-use-the-conventional-commits-specification)

[Conventional Commits FAQ：怎麼處理 revert commit](https://www.conventionalcommits.org/en/v1.0.0/#how-does-conventional-commits-handle-revert-commits)

[SemVer 2.0.0（語意化版本）](https://semver.org/spec/v2.0.0.html)

[SemVer：Summary（摘要）](https://semver.org/spec/v2.0.0.html#summary)

[commitlint 的 config-conventional（預設規則組）](https://github.com/conventional-changelog/commitlint/tree/master/%40commitlint/config-conventional)
