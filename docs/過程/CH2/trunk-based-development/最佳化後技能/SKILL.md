---
name: trunk-based-development
description: 依主幹式開發（Trunk-Based Development，TBD）規劃與審查工作拆分、branch 策略與整合方式。用在：收到需求或 ticket 時規劃要拆成幾個 PR、判斷一個變更該直接走短期 branch 還是需要 Feature Flag／Branch by Abstraction／新舊並存／Release Branch、大型重構或框架遷移（例如 Vuex → Pinia、Axios → Fetch）如何每天安全 merge main、舊版本 hotfix 怎麼修、檢查某個 branch 或 PR 是否活太久或太大、審查團隊的 Git workflow 算不算 TBD，以及比較 TBD 與 GitFlow。
---

# SOP

## Phase 1 -- 理解與分析

1. `READ` 使用者需求，以及使用者提供的變更、branch／PR 或團隊 workflow 資訊，建立「需求輸入」。
2. `THINK` 依「需求輸入」判定本次涉及變更規劃、branch／PR／workflow 審查、導入評估、GitFlow 比較或判準說明，並辨識需要使用的規則主題，建立「任務範圍」；同時涉及多種用途或規則主題時保留所有適用項目。
3. `READ` 讀取 `rules/TBD判準-格式規範.md` 的所有 Rule，建立「TBD 判準檢查清單」。
4. `READ` 「任務範圍」涉及變更規劃、branch／PR／workflow 審查，或其他用途需要判斷小批次、整合驗證、Feature Flag、Abstraction、相容遷移、Release Branch、hotfix 或六題自檢時，讀取 `rules/變更規劃-格式規範.md` 的所有 Rule，建立「變更規劃檢查清單」。
5. `READ` 「任務範圍」涉及 branch／PR／workflow 審查、導入評估或 GitFlow 比較時，讀取 `rules/工作流程評估-格式規範.md` 的所有 Rule，建立「工作流程評估檢查清單」。
6. `READ` 需要以具體案例輔助本次分析時，讀取 `references/cases.md` 中與「任務範圍」相關的案例及參考資料，建立「案例參考」。
7. `THINK` 依「需求輸入」、「任務範圍」、「TBD 判準檢查清單」，以及本次已載入的「變更規劃檢查清單」、「工作流程評估檢查清單」與「案例參考」，形成適用用途的規劃、審查、比較或判準分析，建立「分析結果」；發現尚需未載入的規則主題時，返回步驟 2 更新任務範圍後重新載入，不以未載入規則作判斷。

完成條件：已確定任務範圍，並取得依適用檢查清單形成的分析結果。

## Phase 2 -- 產出與檢查

1. `WRITE` 依「分析結果」、「TBD 判準檢查清單」，以及本次已載入的「變更規劃檢查清單」與「工作流程評估檢查清單」，形成符合「需求輸入」的「回覆草稿」。
2. `CHECK` 核對「任務範圍」的適用規則均已載入並實際使用，再逐條驗證「回覆草稿」符合「需求輸入」、「TBD 判準檢查清單」，以及本次已載入的「變更規劃檢查清單」與「工作流程評估檢查清單」；缺少適用規則時返回 Phase 1 步驟 2，分析有誤時返回 Phase 1 步驟 7，其餘未通過項返回步驟 1 修正。
3. `WRITE` 向使用者交付已通過檢查的回覆。

完成條件：回覆涵蓋本次需求，所有適用檢查清單均通過，且已交付使用者。