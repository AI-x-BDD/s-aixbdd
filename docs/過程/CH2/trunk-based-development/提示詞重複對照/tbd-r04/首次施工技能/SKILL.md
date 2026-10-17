---
name: trunk-based-development
description: 依主幹式開發（Trunk-Based Development，TBD）規劃與審查工作拆分、branch 策略與整合方式。用在：收到需求或 ticket 時規劃要拆成幾個 PR、判斷一個變更該直接走短期 branch 還是需要 Feature Flag／Branch by Abstraction／新舊並存／Release Branch、大型重構或框架遷移（例如 Vuex → Pinia、Axios → Fetch）如何每天安全 merge main、舊版本 hotfix 怎麼修、檢查某個 branch 或 PR 是否活太久或太大、審查團隊的 Git workflow 算不算 TBD，以及比較 TBD 與 GitFlow。
---

本次重構尚未經學員實際驗證。

# SOP

## Phase 1 -- 確認任務與判準

1. `READ` 使用者需求，以及使用者提供的工作範圍、branch／PR 現況與團隊 workflow，建立「任務輸入」。
2. `THINK` 依「任務輸入」辨識本次涉及需求規劃、技巧諮詢、branch／PR／workflow 審查、導入評估或 GitFlow 比較的哪些任務，建立「任務類型」；同時涉及多類時，各自套用相關步驟。
3. `READ` 讀取 `rules/共通判準-格式規範.md` 的所有 Rule，建立「共通判準檢查清單」。
4. `THINK` 依「任務輸入」與已載入的「共通判準檢查清單」判斷本次適用的規則及其來源，建立「任務判準」。

完成條件：已辨識任務類型，且任務判準可對應已載入的共通判準檢查清單。

## Phase 2 -- 規劃或審查

1. `THINK` 規劃需求時，先把需求拆成能獨立整合的小變更，一張 Story／Ticket 不等於一個 branch 或一個 PR。逐項判斷幾小時／一天內能否完成；不能時先嘗試切小並重新判斷，仍不能時依原因選擇：功能還不能曝光用 Feature Flag、大型程式重構用 Branch by Abstraction、舊系統／相容性遷移用新舊並存（Strangler）、維護已發布版本用 Release Branch，建立「變更切分」。
2. `READ` 「變更切分」需使用整合技巧，或「任務輸入」涉及技巧諮詢、遷移、hotfix 或特定技巧的審查時，讀取 `rules/整合技巧-格式規範.md` 的所有 Rule，建立「整合技巧檢查清單」。
3. `THINK` 已載入「整合技巧檢查清單」時，依該清單、「任務輸入」、「任務判準」及已有的「變更切分」分析所需技巧，建立「技巧分析」。
4. `READ` 規劃需求且需要完整拆法時，讀取 `references/cases.md` 的相關案例，建立「案例參考」。
5. `THINK` 規劃需求時，依「變更切分」、「任務判準」及已取得的「技巧分析」、「案例參考」形成「整合計畫」：每個小變更開短期 branch，目標是「這個小變更做完就 merge」，不是「整個 feature 做完才 merge」；工作期間同步 main，merge 前 branch 要跟 main 保持最新；CI 驗證為 build → lint → unit test → 必要的 integration test，PR → review → CI green → merge；DORA 建議每個 commit 都觸發 build 與自動測試，回饋在幾分鐘內；merge 後刪 branch。
6. `READ` 審查 branch／PR／團隊 workflow 或評估導入時，讀取 `rules/工作流程審查-格式規範.md` 的所有 Rule，建立「工作流程審查檢查清單」。
7. `THINK` 已載入「工作流程審查檢查清單」時，依該清單、「任務輸入」、「任務判準」及已取得的「技巧分析」形成「審查結果」。
8. `THINK` 比較 TBD 與 GitFlow 時，形成「比較結果」：GitFlow 類是先隔離 → 做完整 → 最後整合；TBD 是先切小 → 持續整合 → 任何時候都保持可工作。TBD 主要改變拆分工作的方式，Git 操作本身變化不大。
9. `CHECK` 依已載入的「共通判準檢查清單」及本次適用且已載入的「整合技巧檢查清單」、「工作流程審查檢查清單」，逐條驗證本次產生的「整合計畫」、「技巧分析」、「審查結果」與「比較結果」；未通過時返回對應分析步驟修正後重查。

完成條件：本次任務所需的分析或計畫已產生，且符合本次適用且已載入的檢查清單。

## Phase 3 -- 檢查與交付

1. `WRITE` 依「任務輸入」與已通過檢查的本次計畫或分析建立答覆草稿；規劃結果用這個格式給出：

   ```text
   PR 1：<變更>  — 使用技巧：<無／Feature Flag／Abstraction／新舊並存>
   PR 2：...
   每個 PR merge 後 main 為什麼仍可工作：<說明>
   預估 branch 壽命（含等 review）：<時間>
   ```

2. `CHECK` 確認答覆草稿涵蓋「任務輸入」，並符合本次適用且已載入的檢查清單；送出前依原六題檢查適用的計畫或建議：能不能切到一天內可以 merge？這個 PR 現在 merge，main 還能正常工作嗎？未完成功能能不能用 Feature Flag 隱藏？大改造能不能用 abstraction 讓新舊實作共存？CI 能不能快速告訴我這次改動有沒有破壞系統？這個 branch 明天還會存在嗎？是的話，檢查是不是切得太大。未通過時返回對應分析或草稿步驟修正後重查。
3. `WRITE` 向使用者展示已通過檢查的答覆。

完成條件：使用者已收到涵蓋其任務、通過適用檢查的規劃或分析結果。
