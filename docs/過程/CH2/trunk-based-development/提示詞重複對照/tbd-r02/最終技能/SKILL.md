---
name: trunk-based-development
description: 依主幹式開發（Trunk-Based Development，TBD）規劃與審查工作拆分、branch 策略與整合方式。用在：收到需求或 ticket 時規劃要拆成幾個 PR、判斷一個變更該直接走短期 branch 還是需要 Feature Flag／Branch by Abstraction／新舊並存／Release Branch、大型重構或框架遷移（例如 Vuex → Pinia、Axios → Fetch）如何每天安全 merge main、舊版本 hotfix 怎麼修、檢查某個 branch 或 PR 是否活太久或太大、審查團隊的 Git workflow 算不算 TBD，以及比較 TBD 與 GitFlow。
---

# SOP

## Phase 1 -- 分析、規劃與審查

1. `READ` 使用者需求、已提供的團隊 Git workflow 規則與 branch／PR／CI 現況，建立「任務輸入」。
2. `THINK` 依「任務輸入」判定本次涉及需求拆分與整合規劃、branch／PR／團隊 workflow 審查、技巧選擇或 TBD 與 GitFlow 比較，建立「任務類型」。
3. `READ` 進行 TBD 規劃、審查或比較時，讀取 `rules/主幹整合-格式規範.md` 的所有 Rule，建立「主幹整合檢查清單」。
4. `READ` 「任務類型」涉及需求拆分、整合方案、技巧選擇或任何 branch／PR／團隊 workflow 審查時，讀取 `rules/變更拆分-格式規範.md` 的所有 Rule，建立「變更拆分檢查清單」；一般審查即使未點名具體技巧也適用。
5. `THINK` 依「任務輸入」、「主幹整合檢查清單」及本次適用且已載入的「變更拆分檢查清單」分析整合現況、規則來源與適用範圍，建立「整合判斷」。
6. `READ` 已載入「變更拆分檢查清單」且需要參照完整拆分案例時，讀取 `references/cases.md`，建立「實戰案例參照」。
7. `THINK` 依「任務輸入」、「整合判斷」、「主幹整合檢查清單」，以及本次有載入的「變更拆分檢查清單」與「實戰案例參照」，形成「建議草稿」。規劃短期 branch／PR 路徑時，依切小、每個小變更開短期 branch、工作期間及 merge 前同步 main、build → lint → unit test → 必要的 integration test、PR → review → CI green → merge、merge 後刪 branch 的順序安排整合；此為短期 branch／PR 路徑，不將該路徑擴張為所有團隊必用的 Git 操作。
8. `CHECK` 先依「任務類型」核對步驟 3、4 的載入條件是否均已履行；有應載未載的清單時返回對應 READ，重新執行其後的分析與草稿步驟。再逐條驗證「建議草稿」是否符合「任務輸入」及所有適用的具名檢查清單；使用「實戰案例參照」時一併核對與清單的一致性。內容未通過時返回步驟 7 修正草稿後重新檢查。
9. `WRITE` 向使用者交付通過檢查的「建議草稿」；規劃結果使用以下格式，審查或比較任務依「任務類型」交付對應判斷：

   ```text
   PR 1：<變更>  — 使用技巧：<無／Feature Flag／Abstraction／新舊並存>
   PR 2：...
   每個 PR merge 後 main 為什麼仍可工作：<說明>
   預估 branch 壽命（含等 review）：<時間>
   ```

完成條件：已交付符合需求與本次載入清單的規劃、審查或比較結果；本次適用的清單均已在使用前載入，且已逐條檢查。
