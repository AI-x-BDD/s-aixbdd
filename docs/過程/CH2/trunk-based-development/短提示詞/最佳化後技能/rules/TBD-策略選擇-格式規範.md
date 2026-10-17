# Rule 1 - 決策樹與技巧選擇

- 依下列決策樹判斷變更策略：

```text
我要做一個變更
│
├─ 幾小時／一天內可完成？
│   └─ Yes → short-lived branch → CI + Review → merge main
│
└─ No → 能不能切更小？
    ├─ Yes → 切小 → 多個 PR，每個回到上一步判斷
    └─ No → 為什麼？
        ├─ 功能還不能曝光     → Feature Flag
        ├─ 大型程式重構       → Branch by Abstraction
        ├─ 舊系統／相容性遷移 → 新舊並存（Strangler）
        └─ 維護已發布版本     → Release Branch
```

- 變更幾小時／一天內可完成時，使用 short-lived branch，經 CI 與 review 後 merge main。
- 不能一天完成時先判斷能否切更小；能切小就拆成多個 PR，每個 PR 回到上一個判斷。
- 不能切小時依原因選擇：功能還不能曝光 → Feature Flag；大型程式重構 → Branch by Abstraction；舊系統／相容性遷移 → 新舊並存（Strangler）；維護已發布版本 → Release Branch。
- 未完成的工作不靠 branch 藏起來，靠小批次、Feature Flag、抽象層、向後相容、CI、自動測試。
- Feature Flag：程式每天 merge，flag 關閉，最後打開（Deploy ≠ Release）；功能上線後要刪 flag，官方警告不清理的 flag 會變成技術債。
- Branch by Abstraction：建立 abstraction → 舊實作接上 → 加入新實作 → 逐步切換 → 刪舊實作；每一步都 merge main。
- 新舊並存：改 API 時先讓舊 API 與新 API 並存 → consumer 遷移 → 刪舊 API；不能讓 main 處在「API 改了、前端還沒跟上」的中間狀態。
- Release Branch：很晚才切，只負責該版本的穩定、bug fix、發布，不能承載新功能；Bug 先修在 main（fix on trunk first），驗證後再 cherry-pick 到 release branch；不能只在 release branch 修再回灌 main。

## Good Example

- 供應商 SDK 替換不能中斷付款流程時，先用 abstraction 接住舊實作，再加入新實作並逐步切換，每步都可 merge main；功能尚未準備好時以關閉的 flag 隱藏。

## Bad Example

- 以 `feature/sdk-migration` 分支存放三週，最後一次切換全部 consumer，期間 main 沒有新舊實作共存，也沒有先在 main 修 bug 再 cherry-pick 到 release branch。
