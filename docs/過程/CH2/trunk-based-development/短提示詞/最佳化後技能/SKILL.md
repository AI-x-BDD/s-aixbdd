---
name: trunk-based-development
description: 依主幹式開發（Trunk-Based Development，TBD）規劃與審查工作拆分、branch 策略與整合方式。用在：收到需求或 ticket 時規劃要拆成幾個 PR、判斷一個變更該直接走短期 branch 還是需要 Feature Flag／Branch by Abstraction／新舊並存／Release Branch、大型重構或框架遷移（例如 Vuex → Pinia、Axios → Fetch）如何每天安全 merge main、舊版本 hotfix 怎麼修、檢查某個 branch 或 PR 是否活太久或太大、審查團隊的 Git workflow 算不算 TBD，以及比較 TBD 與 GitFlow。
---

# SOP

## Phase 1 -- 分析 TBD 任務

1. `READ` 使用者需求、ticket、branch／PR／workflow 現況與已提供的團隊規則，建立「TBD 任務輸入」。
2. `THINK` 依「TBD 任務輸入」判定適用的判斷主題：規則來源與 branch 壽命、規則分級、需求規劃、策略選擇、常見錯誤、團隊 workflow 審查、TBD 與 GitFlow 比較、送出前檢查；建立「TBD 判斷範圍」。
3. `READ` 依「TBD 判斷範圍」只載入適用主題的 RuleFile 全部 Rule，並依下列條件載入各主題：回答需要使用來源或 branch 壽命規則（例如規劃輸出 branch 壽命），或使用者要求區分來源時，讀取 `rules/TBD-來源與壽命-格式規範.md`，建立「TBD 來源規則」；回答需要使用核心規則、強烈建議或團隊選項的強度判斷，或使用者要求規則分級時，讀取 `rules/TBD-規則分級-格式規範.md`，建立「TBD 分級規則」；判斷範圍包含需求拆分或 PR 規劃時，讀取 `rules/TBD-需求規劃-格式規範.md`，建立「TBD 需求規劃規則」；判斷範圍包含 branch 策略或技巧選擇時，讀取 `rules/TBD-策略選擇-格式規範.md`，建立「TBD 策略規則」；判斷範圍包含 branch／PR／merge 違反模式時，讀取 `rules/TBD-常見錯誤-格式規範.md`，建立「TBD 常見錯誤規則」；判斷範圍包含團隊 Git workflow 或導入前提時，讀取 `rules/TBD-workflow審查-格式規範.md`，建立「TBD workflow 審查規則」；判斷範圍包含 TBD 與 GitFlow 比較時，讀取 `rules/TBD-GitFlow比較-格式規範.md`，建立「TBD GitFlow 比較規則」；需求規劃、branch／PR 檢查或團隊 workflow 審查有交付前對應事項時，或使用者明確要求交付前檢查時，讀取 `rules/TBD-送出前檢查-格式規範.md`，建立「TBD 送出前檢查規則」；未涉及的主題不載入。
4. `READ` 需要完整情境案例時，讀取 `references/cases.md`，建立「TBD 案例參考」；只需通用規則時不載入。
5. `THINK` 依「TBD 判斷範圍」、已載入的具名判斷規則（包括適用的「TBD 來源規則」、「TBD 分級規則」、「TBD 需求規劃規則」、「TBD 策略規則」、「TBD 常見錯誤規則」、「TBD workflow 審查規則」、「TBD GitFlow 比較規則」與「TBD 送出前檢查規則」）與「TBD 案例參考」（若已建立），建立「TBD 產出設計」。

完成條件：已建立「TBD 任務輸入」與「TBD 判斷範圍」；每個適用主題的 RuleFile 已載入並建立對應具名結果；未涉及主題未載入；需要完整案例時也已建立「TBD 案例參考」；「TBD 產出設計」已指出要回答的模式與相關判斷。

## Phase 2 -- 產出與驗證

1. `WRITE` 依「TBD 產出設計」與已載入的具名判斷規則產生對應的規劃、審查或比較回答；需求規劃使用「TBD 需求規劃規則」指定的規劃格式，其他模式使用各自已載入的規則。
2. `CHECK` 依已載入的具名判斷規則逐條驗證回答的相關規則、決策理由與檢查結果；有載入「TBD 送出前檢查規則」時執行其內部六項檢查，不要求把六項檢查逐項展示在回答中；未通過時回到 Phase 1 步驟 5 修正，缺少輸入時依對應規則中的導入前提指出限制。

完成條件：已產出對應模式的回答，且已載入的具名判斷規則均完成逐條驗證；內部送出前檢查若適用已完成；未通過項目已修正或缺少輸入的限制已回報。

# 主幹式開發（Trunk-Based Development）

核心目的：不要讓大家的程式碼分開太久。所有人圍繞單一 trunk（`main`）工作，不建立長期開發分支，持續把小變更整合回 main，main 任何時候都保持可工作、可發布。

各情境的完整拆法（小 bug、三天功能、大型重構、Vuex → Pinia、一週的 Feature Flag 功能、舊版 hotfix）見 [references/cases.md](references/cases.md)。
