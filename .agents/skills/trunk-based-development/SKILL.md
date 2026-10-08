---
name: trunk-based-development
description: 依主幹式開發（Trunk-Based Development，TBD）規劃與審查工作拆分、branch 策略與整合方式。用在：收到需求或 ticket 時規劃要拆成幾個 PR、判斷一個變更該直接走短期 branch 還是需要 Feature Flag／Branch by Abstraction／新舊並存／Release Branch、大型重構或框架遷移（例如 Vuex → Pinia、Axios → Fetch）如何每天安全 merge main、舊版本 hotfix 怎麼修、檢查某個 branch 或 PR 是否活太久或太大、審查團隊的 Git workflow 算不算 TBD，以及比較 TBD 與 GitFlow。
---

# 主幹式開發（Trunk-Based Development）

核心目的：不要讓大家的程式碼分開太久。所有人圍繞單一 trunk（`main`）工作，不建立長期開發分支，持續把小變更整合回 main，main 任何時候都保持可工作、可發布。

回答時區分規則來源：

- **TBD 官方**：TrunkBasedDevelopment.com。
- **DORA**：Google DORA 的 DevOps 研究，標準通常比官方嚴格。
- **團隊規則**：TBD 沒規定、由團隊自行決定的部分。

Branch 壽命兩邊標準不同：官方認為短期 branch 通常 1～2 天；DORA 以不到一天為目標。不要把「2 天」說成硬性標準。

## 規則分級

**核心規則**（違反就不算 TBD）：

1. 沒有長期開發分支。
2. 頻繁整合 main。DORA：至少每天一次，一天多次更好。
3. main 保持可工作。CI 紅了先修 main，不繼續開發新功能；DORA 建議立即修或立即 revert，不是「晚上再看」。

**強烈建議**：branch 非常短命（官方約 1～2 天，DORA < 1 天）；active branches 盡量少；不靠 code freeze 解決整合問題；merge 後刪 branch。

**團隊自行決定**（不要說成 TBD 的要求）：squash／merge commit／rebase merge、同步 main 用 merge 還是 rebase、branch 命名、reviewer 人數、GitHub 或 GitLab、是否禁止 direct push。

## 規劃需求的流程

收到需求時，不先問「要開什麼 branch」，依序想：

1. **切小**：把需求拆成多個能獨立整合的小變更。一張 Story／Ticket 不等於一個 branch 或一個 PR。
2. **每個小變更開短期 branch**，目標是「這個小變更做完就 merge」，不是「整個 feature 做完才 merge」。
3. **工作期間同步 main**，merge 前 branch 要跟 main 保持最新。
4. **CI 驗證**：build → lint → unit test → 必要的 integration test；PR → review → CI green → merge。DORA 建議每個 commit 都觸發 build 與自動測試，回饋在幾分鐘內。
5. **merge 後刪 branch**。

規劃結果用這個格式給出：

```text
PR 1：<變更>  — 使用技巧：<無／Feature Flag／Abstraction／新舊並存>
PR 2：...
每個 PR merge 後 main 為什麼仍可工作：<說明>
預估 branch 壽命（含等 review）：<時間>
```

## Decision Tree

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

未完成的工作不靠 branch 藏起來，靠小批次、Feature Flag、抽象層、向後相容、CI、自動測試。

### 技巧要點

- **Feature Flag**：程式每天 merge，flag 關閉，最後打開（Deploy ≠ Release）。功能上線後要刪 flag，官方警告不清理的 flag 會變成技術債。
- **Branch by Abstraction**：建立 abstraction → 舊實作接上 → 加入新實作 → 逐步切換 → 刪舊實作。每一步都 merge main。
- **新舊並存**：改 API 時先讓舊 API 與新 API 並存 → consumer 遷移 → 刪舊 API。不要讓 main 處在「API 改了、前端還沒跟上」的中間狀態。
- **Release Branch**：很晚才切，只負責該版本的穩定、bug fix、發布，不能承載新功能開發。Bug 先修在 main（fix on trunk first），驗證後再 cherry-pick 到 release branch；只在 release branch 修再回灌 main 是官方列出的錯誤模式。

各情境的完整拆法（小 bug、三天功能、大型重構、Vuex → Pinia、一週的 Feature Flag 功能、舊版 hotfix）見 [references/cases.md](references/cases.md)。

## 常見錯誤

- **「我們都從 main 開 branch，所以是 TBD」**：feature branch 活 2～3 週就不是 TBD。
- **一張 Story = 一個 branch = 一個 PR**：一張 Story 可以拆成 refactor、API、UI、cleanup 多個 PR，這樣更符合 TBD。
- **為了 merge 小，把不能工作的程式 merge main**：每一步都要保持可工作，用新舊並存處理跨層改動。
- **PR 很小但等 review 3 天**：效果跟三天 branch 一樣。branch 壽命要算入等 review 的時間。DORA 把重量級、非同步、耗時的 review 流程列為 TBD 常見阻礙。
- **多人在同一個 feature branch 開發**、**branch 一直不刪**、**接近 release 就 code freeze**：都是官方 You're Doing It Wrong 列出的模式。

## 審查團隊的 workflow

檢查是否真的在做 TBD：

- 有沒有 `develop`、`team-a`、`release-next` 這類長期共同開發分支？
- 每人每天至少整合 main 一次嗎？
- branch 壽命（含 review 等待）多長？active branches 多少？
- CI 多快回饋？main 紅了是否立即修或 revert？
- 有沒有靠 code freeze 解決整合問題？
- Feature Flag 有沒有清理？

導入前提：自動 build、自動 test、快速 CI、小批次開發能力、快速 code review。缺這些時，TBD 容易變成「大家一直 merge main，main 一直壞」。DORA 指出經驗不足、缺 gated checks、沒有「broken trunk 優先修復」紀律的團隊，實行 TBD 反而可能增加錯誤與返工。遇到這種團隊，先指出缺的前提，不要直接建議全面導入。

適合：SaaS、Web App、Backend API、Frontend App、Microservice、企業內部系統、頻繁發布、多人共同維護的 codebase。需求一直變、多人同時改、需要頻繁 release 三者同時成立時價值最高。

## TBD 與 GitFlow

- GitFlow 類：先隔離 → 做完整 → 最後整合。
- TBD：先切小 → 持續整合 → 任何時候都保持可工作。

TBD 主要改變拆分工作的方式，Git 操作本身變化不大。

## 送出前檢查

1. 能不能切到一天內可以 merge？
2. 這個 PR 現在 merge，main 還能正常工作嗎？
3. 未完成功能能不能用 Feature Flag 隱藏？
4. 大改造能不能用 abstraction 讓新舊實作共存？
5. CI 能不能快速告訴我這次改動有沒有破壞系統？
6. 這個 branch 明天還會存在嗎？是的話，檢查是不是切得太大。
