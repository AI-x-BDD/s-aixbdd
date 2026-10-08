# ch1

目前完成 ch1 範圍的三個 Skill：`double-diamond`、`trunk-based-development`、`conventional-commits`，分別處理開工前先想清楚要做什麼、怎麼拆開並整合回
`main`，以及 commit message 怎麼寫。

每個 Skill 都是先寫學習筆記（`docs/`），再把判斷時用得到的部分整理成 Skill。之後我從
[Coding Dojo](https://codingdojo.org/) 挑了 String
Calculator 題目，拆成 8 個開發步驟，用這三個 Skill 實作，並把過程記錄在 `docs/過程/`。

## Skills 與設計想法

### `double-diamond`

- **用途**：依雙鑽石原則（Discover → Define → Develop →
  Deliver）釐清需求，判斷收到的需求是問題還是已經是解法，再展開並比較多個方案。
- **使用時機**：收到需求或 ticket、準備動手實作之前。
- **使用方式**：`/double-diamond <需求>`（Claude Code）或 `$double-diamond <需求>`（Codex），例如
  `/double-diamond docs/需求清單.md`。
- **設計想法**：這個 Skill 要防兩件事：還沒釐清就認定問題，以及還沒比較就選定做法。回答時區分官方定義（Design
  Council）、業界慣例與實務判斷，避免把個人判斷說成官方規定。完整案例放在 `references/cases.md`。
- **驗證狀態**：已在 String Calculator Step
  1～8 使用。AI 曾回答目標已經明確、不需要再進行其他動作，我猜可能是因為需求已經先拆成 8 個小步驟。

### `trunk-based-development`

- **用途**：依主幹式開發（TBD）規劃工作怎麼拆、要不要開短期分支，以及怎麼合併回
  `main`；也能審查分支或 PR 是否活太久、切太大。
- **使用時機**：決定要做什麼之後、實作之前，用來規劃拆分；或 commit 之後，用來檢查怎麼收尾。
- **使用方式**：`/trunk-based-development`，或在雙鑽石分析後輸入 `/trunk-based-development 依建議`。
- **設計想法**：規則分成三級：核心規則（違反就不算 TBD）、強烈建議、團隊自行決定。squash、branch 命名這類由團隊決定的事，Skill 會標明不是 TBD 的要求。branch 壽命等標準會分開列出 TBD 官方與 DORA 的說法。
- **驗證狀態**：三個 Skill 中行為最不穩定的一個。Step 1～5、7、8 有呼叫，Step 6 沒有獨立呼叫。有時在實作前規劃（Step
  2、5），有時在 commit 後檢查收尾（Step 3、4）。開分支也沒有變成固定流程，Step 7、8 直接在 `main` 開發。

### `conventional-commits`

- **用途**：依 Conventional Commits 1.0.0 判斷 commit type、scope 與 breaking change，撰寫或審查 commit message。
- **使用時機**：實作完成、準備 commit 時。
- **使用方式**：`/conventional-commits`；要建立 commit 時輸入 `/conventional-commits commit`，避免只得到草稿。
- **設計想法**：依「修改目的」決定 type，不依「改了哪種檔案」。回答時區分官方規定、官方建議、業界慣例與團隊規則。dependency 升級、CSS 修改、revert 等容易誤判的情境放在
  `references/cases.md`。另外有幾條不在原筆記中的規則，是 AI 生成 Skill 時補上的，例如先用 `git log`
  沿用既有 scope、已 push 的歷史改寫前先詢問。
- **驗證狀態**：已在 Step
  1～8 使用。不同 agent、不同 Step 的結果不一致：有時直接 commit，有時只給草稿。後來我在指令後面加上
  `commit`，明確要求建立 commit。

## 實作驗證：String Calculator

需求依 `docs/需求清單.md`
分成 8 步，從基本加法開始，依序加入任意數量的數字、換行分隔、結尾分隔符檢查、自訂分隔符、負數驗證、複合錯誤回報，最後加入乘法。完成後共有 64 個測試，push 到
`main` 時由 GitHub Actions 執行 `mvn -B test`。

過程中我用了 Codex 和 Claude Code 兩種 agent（Step 3、4 的紀錄註明使用 Claude Code）。Step
4 之後，我整理出下面這套順序，Step 5 照著執行：

| 步驟 | 指令                              | 要完成的事                         |
| ---- | --------------------------------- | ---------------------------------- |
| 1    | `/double-diamond <需求>`          | 比較方案，決定這次做什麼           |
| 2    | `/trunk-based-development 依建議` | 決定怎麼拆、怎麼合併，建立短期分支 |
| 3    | `do it`                           | 實作與測試                         |
| 4    | `/conventional-commits commit`    | 建立 commit                        |
| 5    | `收尾`                            | 合併、push、確認 CI、刪分支        |

實際使用後的觀察：

- 同一個 Skill 在 Codex 與 Claude Code 上的行為略有差異。差異不大，但有時會影響下一步的判斷。
- 前幾次在實作前開分支的操作，沒有變成每次都會執行的固定流程。Step 8 我追問為什麼沒開分支，Agent 回答沒有特別理由。
- 沒有輸入 TBD 指令時，Agent 有時也會開分支，但紀錄裡看不出背後是否呼叫了 TBD Skill。

完整過程見 `docs/過程/1.md`～`8.md`，整體比較見 `docs/過程/三個技能的實作觀察.md`。
