# Rule 1 - 依前提與情境評估導入

- 評估導入時，必須檢查自動 build、自動 test、快速 CI、小批次開發能力與快速 code review。
- 必須指出經驗不足、缺 gated checks、沒有「broken trunk 優先修復」紀律時的風險；DORA 指出這類團隊實行 TBD 反而可能增加錯誤與返工。
- 缺少上述前提時，必須先指出缺的前提，不得直接建議全面導入。
- 可以依適用情境說明價值：SaaS、Web App、Backend API、Frontend App、Microservice、企業內部系統、頻繁發布、多人共同維護的 codebase。需求一直變、多人同時改、需要頻繁 release 三者同時成立時價值最高。

## Good Example

先指出團隊缺少的前提，沒有把改 branch 命名當成完成導入。

- 情境：SaaS 團隊沒有自動測試，review 需要三天，打算明天全面導入 TBD。
- 評估：先補自動 build/test、快速 CI 與 gated checks，縮短 review，建立 broken trunk 優先修復紀律，再逐步導入；團隊仍有小批次開發能力與經驗需要評估。

## Bad Example

相同團隊缺少安全前提，卻被直接建議全面導入。

- 情境：SaaS 團隊沒有自動測試，review 需要三天，打算明天全面導入 TBD。
- 評估：明天把 branch 改名為 `short-task/*`，所有人開始直接整合 main，就算完成導入。

# Rule 2 - 比較工作拆分與整合方式

- 比較時必須依工作拆分與整合方式說明差異：GitFlow 類先隔離 → 做完整 → 最後整合；TBD 先切小 → 持續整合 → 任何時候都保持可工作。
- 必須保留此判斷：TBD 主要改變拆分工作的方式，Git 操作本身變化不大。

## Good Example

比較聚焦工作隔離多久及如何整合，沒有以單一 Git 操作替代判斷。

- 情境：甲團隊用 merge commit，將完整功能留在開發線後才整合；乙團隊也用 merge commit，但把需求切小持續整合。
- 比較：甲符合 GitFlow 類的先隔離再整合思路；乙符合 TBD 的切小持續整合思路。兩者都用 merge commit，不影響這項區分。

## Bad Example

相同兩團隊只以 squash 與否分類，沒有比較工作方式。

- 情境：甲團隊用 merge commit，將完整功能留在開發線後才整合；乙團隊也用 merge commit，但把需求切小持續整合。
- 比較：兩隊都沒有 squash，所以都不是 TBD。
