---
name: trunk-based-development
description: 依主幹式開發（Trunk-Based Development，TBD）規劃與審查工作拆分、branch 策略與整合方式。用在：收到需求或 ticket 時規劃要拆成幾個 PR、判斷一個變更該直接走短期 branch 還是需要 Feature Flag／Branch by Abstraction／新舊並存／Release Branch、大型重構或框架遷移（例如 Vuex → Pinia、Axios → Fetch）如何每天安全 merge main、舊版本 hotfix 怎麼修、檢查某個 branch 或 PR 是否活太久或太大、審查團隊的 Git workflow 算不算 TBD，以及比較 TBD 與 GitFlow。
---

# SOP

## Phase 1 -- 理解任務與判斷基準

1. `READ` 使用者需求，以及需求提供的工作範圍、工期、branch／PR 現況、CI 與 review 流程、團隊 Git 規則；只讀取本次需求涉及的資料。
2. `THINK` 判定本次任務涉及需求規劃、branch／PR／workflow 審查（含導入與適用性評估）或 TBD 與 GitFlow 比較中的哪些工作，建立「任務範圍」。同時涉及多項時保留各項，不以單一分支排除其他工作。
3. `READ` 進行 TBD 判斷時，讀取 `rules/TBD判準-格式規範.md` 的所有 Rule，建立「TBD 判準檢查清單」。
4. `THINK` 依「任務範圍」與「TBD 判準檢查清單」建立本次的「共通判斷」，作為後續規劃、審查或比較的依據。

完成條件：已確定任務範圍，並建立後續分析可使用的共通判斷。

## Phase 2 -- 規劃、審查與交付

1. `THINK` 需求規劃時，**切小**：把需求拆成多個能獨立整合的小變更。一張 Story／Ticket 不等於一個 branch 或一個 PR。先判斷能否幾小時／一天內完成；否則嘗試再切小，對每個小變更重做判斷；仍不能時辨識功能不能曝光、大型程式重構、舊系統／相容性遷移或維護已發布版本的原因，建立「拆分與阻礙」。
2. `READ` 規劃、審查或比較需要判斷 Feature Flag、Branch by Abstraction、新舊並存或 Release Branch 的適用方式時，讀取 `rules/整合技巧-格式規範.md` 的所有 Rule，建立「整合技巧檢查清單」。
3. `READ` 本次需要完整拆法或案例對照時，讀取 `references/cases.md` 中相關情境，建立「案例對照」。
4. `THINK` 需求規劃時，依「拆分與阻礙」、「共通判斷」及已載入的「整合技巧檢查清單」與「案例對照」（若有），安排**每個小變更開短期 branch**，目標是「這個小變更做完就 merge」，不是「整個 feature 做完才 merge」。
5. `THINK` 需求規劃時，安排**工作期間同步 main**，merge 前 branch 要跟 main 保持最新。
6. `THINK` 需求規劃時，安排**CI 驗證**：build → lint → unit test → 必要的 integration test；PR → review → CI green → merge。DORA 建議每個 commit 都觸發 build 與自動測試，回饋在幾分鐘內。
7. `THINK` 需求規劃時，安排**merge 後刪 branch**。
8. `READ` 審查 branch、PR、團隊 workflow，或評估 TBD 導入與適用性時，讀取 `rules/workflow審查-格式規範.md` 的所有 Rule，建立「workflow 審查檢查清單」。
9. `THINK` 任務涉及審查、導入或適用性評估時，依「共通判斷」、「workflow 審查檢查清單」與已載入的「整合技巧檢查清單」及「案例對照」（若有），建立「審查結果」。
10. `THINK` 任務涉及 TBD 與 GitFlow 比較時，依「共通判斷」及已載入的「整合技巧檢查清單」與「案例對照」（若有）建立「比較結果」：GitFlow 類：先隔離 → 做完整 → 最後整合。TBD：先切小 → 持續整合 → 任何時候都保持可工作。TBD 主要改變拆分工作的方式，Git 操作本身變化不大。
11. `WRITE` 依任務範圍、共通判斷與已完成的規劃、審查結果或比較結果，建立回答草稿。需求規劃結果用這個格式給出：

    ```text
    PR 1：<變更>  — 使用技巧：<無／Feature Flag／Abstraction／新舊並存>
    PR 2：...
    每個 PR merge 後 main 為什麼仍可工作：<說明>
    預估 branch 壽命（含等 review）：<時間>
    ```

12. `CHECK` 依本主檔中本次適用的規劃與輸出要求、「TBD 判準檢查清單」及本次已載入的其他檢查清單，逐條對照回答草稿，確認是否符合需求；未通過時返回對應的分析步驟修正後重新檢查。
13. `WRITE` 向使用者交付通過檢查的回答。

完成條件：任務範圍內的規劃、審查或比較均已回答，並通過本次適用的檢查清單。

