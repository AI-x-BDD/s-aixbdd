---
name: trunk-based-development
description: 依主幹式開發（Trunk-Based Development，TBD）規劃與審查工作拆分、branch 策略與整合方式。用在：收到需求或 ticket 時規劃要拆成幾個 PR、判斷一個變更該直接走短期 branch 還是需要 Feature Flag／Branch by Abstraction／新舊並存／Release Branch、大型重構或框架遷移（例如 Vuex → Pinia、Axios → Fetch）如何每天安全 merge main、舊版本 hotfix 怎麼修、檢查某個 branch 或 PR 是否活太久或太大、審查團隊的 Git workflow 算不算 TBD，以及比較 TBD 與 GitFlow。
---

# SOP

## Phase 1 -- 分析需求與判斷策略

1. `READ` 使用者需求與已提供的專案規範；有既有 branch、PR、CI 或團隊 workflow 資訊時，一併讀取作為「任務輸入」。
2. `THINK` 依「任務輸入」判定本次涉及變更規劃、workflow 審查、導入評估或 GitFlow 比較，可同時適用多種任務。
3. `READ` 進行變更規劃、審查、導入評估或 GitFlow 比較時，讀取 `rules/TBD判準-格式規範.md` 的所有 Rule，建立「TBD判準檢查清單」。
4. `THINK` 依「任務輸入」與已載入的「TBD判準檢查清單」，判定相關事實對應的規則來源與分級，形成「基本判斷」。
5. `READ` 任務涉及變更規劃、branch 或 PR 審查、技巧使用審查或團隊 workflow 審查時，讀取 `rules/變更規劃-格式規範.md` 的所有 Rule，建立「變更規劃檢查清單」。
6. `THINK` 已載入「變更規劃檢查清單」時，依「任務輸入」、「基本判斷」與該清單，形成「變更方案」或「拆分與技巧審查結果」。
7. `READ` 任務涉及團隊 workflow 審查、導入評估或 GitFlow 比較時，讀取 `rules/Workflow評估-格式規範.md` 的所有 Rule，建立「Workflow評估檢查清單」。
8. `THINK` 已載入「Workflow評估檢查清單」時，依「任務輸入」、「基本判斷」、適用時的「拆分與技巧審查結果」及已載入的「TBD判準檢查清單」與「Workflow評估檢查清單」，形成符合任務範圍的「評估結論」。
9. `READ` 需要完整情境拆法協助具體化方案或說明評估時，讀取 `references/cases.md` 中相應案例；需要核對規則來源時讀取其中的參考資料，建立「案例與來源參考」。
10. `THINK` 已載入「案例與來源參考」時，將相應案例對照「變更方案」、「拆分與技巧審查結果」或「評估結論」，具體化本次內容。
11. `CHECK` 逐條驗證已載入的「TBD判準檢查清單」，以及適用時的「變更規劃檢查清單」與「Workflow評估檢查清單」；未通過時返回本 Phase 對應的判斷步驟修正並重新檢查。

完成條件：已依任務形成「基本判斷」及適用的「變更方案」、「拆分與技巧審查結果」或「評估結論」，並通過所有已載入檢查清單。

## Phase 2 -- 安排整合與交付

1. `THINK` 涉及變更規劃時，依「變更方案」安排整合流程：每個小變更開短期 branch，工作期間同步 main，merge 前 branch 要跟 main 保持最新；build → lint → unit test → 必要的 integration test；PR → review → CI green → merge；merge 後刪 branch。
2. `WRITE` 依「基本判斷」及已載入的檢查清單，向使用者呈現「變更方案」與其整合安排、「拆分與技巧審查結果」或符合任務範圍的「評估結論」。規劃結果用這個格式給出：

   ```text
   PR 1：<變更>  — 使用技巧：<無／Feature Flag／Abstraction／新舊並存>
   PR 2：...
   每個 PR merge 後 main 為什麼仍可工作：<說明>
   預估 branch 壽命（含等 review）：<時間>
   ```

3. `CHECK` 交付內容符合「任務輸入」與所有已載入的檢查清單；未通過時返回 Phase 1 對應的判斷步驟或本 Phase 的整合安排步驟修正，再更新交付內容並重新檢查。

完成條件：使用者要求的規劃、審查、導入評估或比較已呈現，且交付內容符合所有已載入檢查清單。
