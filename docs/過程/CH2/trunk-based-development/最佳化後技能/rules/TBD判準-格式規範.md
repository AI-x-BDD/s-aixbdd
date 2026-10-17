# Rule 1 - 核心目的與核心規則

- 回答必須以核心目的為準：不要讓大家的程式碼分開太久。所有人圍繞單一 trunk（`main`）工作，不建立長期開發分支，持續把小變更整合回 main，main 任何時候都保持可工作、可發布。
- 判斷是否為 TBD 時，必須使用以下核心規則（違反就不算 TBD）。
  1. 沒有長期開發分支。
  2. 頻繁整合 main。DORA：至少每天一次，一天多次更好。
  3. main 保持可工作。CI 紅了先修 main，不繼續開發新功能；DORA 建議立即修或立即 revert，不是「晚上再看」。

## Good Example

以實際整合與 main 狀態判斷。

- 情境：main 的 CI 紅了，同時有新功能待開發。
- 做法：先立即修復或 revert，保持 main 可工作；新功能維持小批次頻繁整合。

## Bad Example

同一情境延後處理 main。

- 情境：main 的 CI 紅了，同時有新功能待開發。
- 做法：繼續新功能，到晚上再看 main；平時長期分支各做幾週才整合。

# Rule 2 - 規則來源與 branch 壽命

- 回答時必須區分規則來源。
  - **TBD 官方**：TrunkBasedDevelopment.com。
  - **DORA**：Google DORA 的 DevOps 研究，標準通常比官方嚴格。
  - **團隊規則**：TBD 沒規定、由團隊自行決定的部分。
- 說明 branch 壽命時，必須保留兩邊標準不同：官方認為短期 branch 通常 1～2 天；DORA 以不到一天為目標。不得把「2 天」說成硬性標準。
- branch 壽命必須算入等 review 的時間。PR 很小但等 review 3 天，效果跟三天 branch 一樣。DORA 把重量級、非同步、耗時的 review 流程列為 TBD 常見阻礙。

## Good Example

比較來源並將等待算進存活時間。

- 情境：開發半天、等 review 三天。
- 判斷：壽命約三天半；官方通常 1～2 天與 DORA 不到一天的目標不同，不能只算開發半天，也不將兩天稱為硬性上限。

## Bad Example

相同現況忽略等待並混淆來源。

- 情境：開發半天、等 review 三天。
- 判斷：「branch 只有半天，符合官方規定的最長兩天。」

# Rule 3 - 強烈建議

- 必須將下列事項維持為強烈建議，與核心規則及團隊選擇分開。
  - branch 應非常短命，壽命說明使用 Rule 2 的來源區分。
  - active branches 應維持少量。
  - 應避免靠 code freeze 解決整合問題。
  - merge 後應刪 branch。

## Good Example

遵循建議並保持其分級，不自行發明門檻。

- 情境：一次小變更已 merge。
- 做法：刪除完成的 branch，讓 active branches 保持少量；日常持續整合，不等 release 前 freeze 才解決整合問題。

## Bad Example

相同工作長期累積完成分支並依賴 freeze。

- 情境：多次小變更已 merge。
- 做法：branch 一直不刪，接近 release 才 code freeze 解決累積的整合問題；另宣稱 active branches 超過任意自訂數字就必定不算 TBD。

# Rule 4 - 團隊自行決定

- 團隊可以自行決定以下事項，不得將其說成 TBD 的要求：squash／merge commit／rebase merge、同步 main 用 merge 還是 rebase、branch 命名、reviewer 人數、GitHub 或 GitLab、是否禁止 direct push。

## Good Example

把 Git 操作選項與 TBD 判準分開。

- 情境：團隊採用 merge commit 與 merge 同步 main。
- 判斷：這些選項本身不違反 TBD，應回到本檔的核心規則與建議判斷。

## Bad Example

同一選項被誤當為定義。

- 情境：團隊採用 merge commit 與 merge 同步 main。
- 判斷：「必須 squash 或 rebase 才算 TBD。」
