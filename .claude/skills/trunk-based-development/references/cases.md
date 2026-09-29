# TBD 實戰案例

## 目錄

- 小 Bug
- 三天功能：會員搜尋
- 大型重構：Axios → Fetch wrapper
- 框架遷移：Vuex → Pinia
- 一週的功能：Feature Flag
- 舊版本 Hotfix
- 參考資料

## 小 Bug

按鈕顏色錯誤，30 分鐘可完成，不需要特殊技巧：

```text
short-lived branch → fix → test → PR → merge
branch 活 30 分鐘
```

## 三天功能：會員搜尋

不要：

```text
feature/member-search
（UI、API、權限、排序、分頁、追蹤、測試全部做完再 merge）
```

改成每個都能獨立整合的 PR：

```text
PR 1：加入 API client
PR 2：加入搜尋輸入框
PR 3：加入基本搜尋
PR 4：加入分頁
PR 5：加入權限
```

每個 PR 開自己的短期 branch（例如 `feature/member-search-input`），做完就 merge 並刪除。前面的功能還不能讓使用者看到時，用 Feature Flag 關起來。

## 大型重構：Axios → Fetch wrapper

需要一星期，不能一天完成，也不能讓 main 壞掉 → Branch by Abstraction：

```text
建立 HTTP abstraction
↓ merge
Axios 接 abstraction
↓ merge
加入 Fetch implementation
↓ merge
逐步切換
↓ merge
刪 Axios
```

比讓 `refactor/http-client` 活兩星期更符合 TBD。

## 框架遷移：Vuex → Pinia

錯誤：`feature/migrate-pinia` 工作 3 週，最後 merge。

TBD 做法，每天 merge：

```text
Day 1：建立 abstraction
Day 2：舊 Vuex 接 abstraction
Day 3：增加 Pinia implementation
Day 4：逐步切換
Day 5：移除 Vuex
```

新舊程式碼暫時一起存在 main。官方把這種需要多天的大修改列為 Branch by Abstraction 的主要用途。

## 一週的功能：Feature Flag

新的下注介面，週一只有 UI、週二 API 完成一半、週三測試中、週五才開放。

不要：`feature/new-betting-ui` 放五天。

改成 main 上 `newBettingUI = false`，每天照樣 merge：

```text
Mon → UI
Tue → API
Wed → validation
Thu → tracking
Fri → flag ON
```

程式已經部署，但功能還沒對使用者開放（Deploy ≠ Release）。功能穩定後刪除 flag。

## 舊版本 Hotfix

Production 是 1.5，main 已開始 1.6，現在 1.5 有 bug。

不要：在 `release/1.5` 修 bug，再往 main merge 一大包。

較典型作法（fix on trunk first）：

```text
main 完成 bug fix → 驗證 → cherry-pick 到 release/1.5
```

這樣 main 不會漏掉修正。`release/1.5` 只負責 1.5 的穩定、bug fix 與發布，不能繼續開 1.6 功能。

## 參考資料

- [Trunk Based Development 官方首頁](https://trunkbaseddevelopment.com/)
- [Short-Lived Feature Branches](https://trunkbaseddevelopment.com/short-lived-feature-branches/)：branch 壽命、Story 拆 PR、merge 前同步 main。
- [DORA：Trunk-Based Development](https://dora.dev/capabilities/trunk-based-development/)：每天整合、branch < 1 天、CI 速度、broken trunk 處理。
- [You're Doing It Wrong](https://trunkbaseddevelopment.com/youre-doing-it-wrong/)：看起來像 TBD 其實不是的做法。
- [Feature Flags](https://trunkbaseddevelopment.com/feature-flags/)
- [Branch by Abstraction](https://trunkbaseddevelopment.com/branch-by-abstraction/)（[繁體中文](https://tw.trunkbaseddevelopment.com/branch-by-abstraction/)）
- [Branch for Release](https://trunkbaseddevelopment.com/branch-for-release/)
