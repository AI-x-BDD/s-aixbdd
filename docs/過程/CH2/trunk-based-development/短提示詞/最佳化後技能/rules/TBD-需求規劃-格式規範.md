# Rule 1 - 規劃需求的拆分流程

- 收到需求時，不先問「要開什麼 branch」，依序想：
  1. **切小**：把需求拆成多個能獨立整合的小變更。一張 Story／Ticket 不等於一個 branch 或一個 PR。
  2. **每個小變更開短期 branch**，目標是「這個小變更做完就 merge」，不是「整個 feature 做完才 merge」。
  3. **工作期間同步 main**，merge 前 branch 要跟 main 保持最新。
  4. **CI 驗證**：build → lint → unit test → 必要的 integration test；PR → review → CI green → merge。DORA 建議每個 commit 都觸發 build 與自動測試，回饋在幾分鐘內。
  5. **merge 後刪 branch**。

## Good Example

- 三天的付款報表需求拆成 API、查詢、權限三個 PR；每個 PR 都能獨立整合，並在 merge 前完成 build、lint 與測試。

## Bad Example

- 先問要開哪個 branch，接著以一個長期 feature branch 包含 API、UI、權限與測試，最後才一次 merge。

# Rule 2 - 規劃回答格式

- 規劃回答依序列出每個 PR 的變更與技巧、每個 PR merge 後 main 仍可工作的理由，以及含 review 等待的 branch 壽命。

## Good Example

- 三天的付款報表需求拆成 API、查詢、權限三個 PR；每個 PR 都說明採用的技巧、merge-safe 理由與包含 review 等待的 branch 壽命。

```text
PR 1：<變更>  — 使用技巧：<無／Feature Flag／Abstraction／新舊並存>
PR 2：...
每個 PR merge 後 main 為什麼仍可工作：<說明>
預估 branch 壽命（含等 review）：<時間>
```

## Bad Example

- 只列出 PR 名稱與開發天數，沒有變更與技巧、merge-safe 理由或含 review 的 branch 壽命。
