---
name: trunk-based-development
description: 依主幹式開發（Trunk-Based Development，TBD）規劃與審查工作拆分、branch 策略與整合方式。用在：收到需求或 ticket 時規劃要拆成幾個 PR、判斷一個變更該直接走短期 branch 還是需要 Feature Flag／Branch by Abstraction／新舊並存／Release Branch、大型重構或框架遷移（例如 Vuex → Pinia、Axios → Fetch）如何每天安全 merge main、舊版本 hotfix 怎麼修、檢查某個 branch 或 PR 是否活太久或太大、審查團隊的 Git workflow 算不算 TBD，以及比較 TBD 與 GitFlow。
---

# 主幹式開發（Trunk-Based Development）

# SOP

## Phase 1 -- 釐清情境與按主題載入判斷規則

1. `READ` 使用者需求，以及使用者提供的 branch、PR、CI、release 與工作目錄現況。
2. `THINK` 將本次任務標記為需求拆分規劃、workflow 審查、TBD 與 GitFlow 比較中的一個或多個模式，並判斷是否要求來源分級、特殊策略與完整案例；列出各模式需要的實際判斷主題與未知限制。
3. `READ` 依第 2 步的主題分支，讀取所選 RuleFile 的全部 Rule，並分別建立具名清單：需要判斷 trunk／main 是否可工作或需求／審查涉及核心整合時，讀取 rules/主幹式開發核心規則-格式規範.md，建立「TBD 核心規則檢查清單」；需要規劃 PR、branch 壽命、同步、驗證或刪除時，讀取 rules/主幹式開發需求拆分-格式規範.md，建立「TBD 需求拆分檢查清單」；需要標示官方／DORA／團隊來源或門檻時，讀取 rules/主幹式開發來源分級-格式規範.md，建立「TBD 來源分級檢查清單」；遇到不能曝光、大型重構、相容性遷移或 release／hotfix 時，讀取 rules/主幹式開發策略選擇-格式規範.md，建立「TBD 策略選擇檢查清單」；審查 workflow 或比較 TBD 與 GitFlow 時，讀取 rules/主幹式開發流程審查-格式規範.md，建立「TBD 流程審查檢查清單」；只有需要完整情境拆法時，才讀取 references/cases.md 並建立「TBD 案例參考」。未選中的檔案不載入。
4. `THINK` 只使用與模式相符的「TBD 核心規則檢查清單」、「TBD 需求拆分檢查清單」、「TBD 來源分級檢查清單」、「TBD 策略選擇檢查清單」、「TBD 流程審查檢查清單」與（若已建立）「TBD 案例參考」；需求規劃列出小批次、技巧、main 可工作理由與 branch 壽命，workflow 審查列出證據、違反項、導入前提與修正順序，TBD 與 GitFlow 比較明確比較隔離後一次整合與小批次持續整合，並對每項結論保留輸入事實、來源層級與未知限制。
5. `CHECK` 逐項確認已選的「TBD 核心規則檢查清單」、「TBD 需求拆分檢查清單」、「TBD 來源分級檢查清單」、「TBD 策略選擇檢查清單」、「TBD 流程審查檢查清單」與（若已建立）「TBD 案例參考」，以及已知限制；缺少的事實標為未知，不用未提供資訊補成結論。

完成條件：模式與主題分支已判定，只有必要的 RuleFile／案例資源已載入並命名，分析已覆蓋已選檢查項且未知限制已標明。

## Phase 2 -- 產出與交付檢查

1. `WRITE` 依 Phase 1 已載入且命名的適用清單產生結果。需求規劃使用下列固定格式；workflow 審查列出不符合項、證據、導入前提與修正順序；TBD 與 GitFlow 比較列出兩者的整合節奏、分支用途與 main 可工作條件。

~~~text
PR 1：<變更>  — 使用技巧：<無／Feature Flag／Abstraction／新舊並存>
PR 2：...
每個 PR merge 後 main 為什麼仍可工作：<說明>
預估 branch 壽命（含等 review）：<時間>
~~~

2. `CHECK` 逐條驗證 Phase 1 已選的具名清單、結果欄位、來源分級、未知限制與模式專屬輸出；未通過時修正後重新檢查。

完成條件：規劃、審查或比較結果已交付，且交付前 `CHECK` 的適用項目全部通過。
