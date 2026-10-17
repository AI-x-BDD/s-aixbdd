# Rule 1 - 規則來源與 branch 壽命

- 回答時，必須區分規則來源：
  - **TBD 官方**：TrunkBasedDevelopment.com。
  - **DORA**：Google DORA 的 DevOps 研究，標準通常比官方嚴格。
  - **團隊規則**：TBD 沒規定、由團隊自行決定的部分。
- 說明 branch 壽命時，必須保留兩邊標準的不同：官方認為短期 branch 通常 1～2 天；DORA 以不到一天為目標。不得把「2 天」說成硬性標準。
- 估計與審查 branch 壽命時，必須算入等 review 的時間。DORA 把重量級、非同步、耗時的 review 流程列為 TBD 常見阻礙。

## Good Example

分別說明來源與建議強度，計入等待整合的時間。

- 情境：PR 很小，但等 review 三天。
- 回答：branch 壽命包含等待 review，不能只算寫程式的時間。官方通常 1～2 天，DORA 目標不到一天，兩天不是硬性標準；應檢查 review 阻礙。

## Bad Example

相同情境忽略等待時間，並把來源建議說成硬規則。

- 情境：PR 很小，但等 review 三天。
- 回答：程式只寫了半小時，所以 branch 壽命半小時；TBD 一律規定兩天內，跟 review 無關。

# Rule 2 - TBD 核心與建議分級

- 必須依核心目的判斷：不要讓大家的程式碼分開太久。所有人圍繞單一 trunk（`main`）工作，不建立長期開發分支，持續把小變更整合回 main，main 任何時候都保持可工作、可發布。
- 核心規則必須包含沒有長期開發分支、頻繁整合 main、main 保持可工作；違反核心規則就不算 TBD。
- 說明整合頻率時，必須區分 DORA 的要求：至少每天一次，一天多次更好。
- CI 紅了必須先修 main，不得繼續開發新功能；DORA 建議立即修或立即 revert，不是「晚上再看」。
- branch 應非常短命；active branches 應維持少量；應避免靠 code freeze 解決整合問題。這些是強烈建議，不能當成新增硬性門檻。
- 未完成的工作應靠小批次、Feature Flag、抽象層、向後相容、CI、自動測試持續整合，不得靠長期開發分支藏起來。
- 辨識錯誤模式時，必須保留 TBD 官方 You're Doing It Wrong 對長期 feature branch、多人在同一個 feature branch 開發、接近 release 就 code freeze 等模式的歸因。

## Good Example

用實際整合行為判斷，清楚區分核心與建議。

- 情境：團隊都從 main 開 branch，但 feature branch 活兩到三週。
- 判斷：從 main 開始不等於 TBD；這是長期開發分支，違反核心。應切小並持續安全整合；少量 active branches 屬強烈建議。

## Bad Example

相同情境把分支起點當成足夠條件。

- 情境：團隊都從 main 開 branch，但 feature branch 活兩到三週。
- 判斷：因為從 main 開始，所以符合 TBD，不必在意何時整合。

# Rule 3 - 團隊自行決定的 Git 規則

- 下列項目可以由團隊自行決定，不得說成 TBD 的要求：squash／merge commit／rebase merge、同步 main 用 merge 還是 rebase、branch 命名、reviewer 人數、GitHub 或 GitLab、是否禁止 direct push。

## Good Example

將 Git 操作選擇與方法論判準分開。

- 情境：團隊選擇 squash merge，要求一位 reviewer，使用 GitLab。
- 回答：這些由團隊決定；是否符合 TBD 仍依整合行為判斷。

## Bad Example

相同情境用團隊選擇冒充方法論規定。

- 情境：團隊選擇 squash merge，要求一位 reviewer，使用 GitLab。
- 回答：TBD 規定必須 merge commit、兩位 reviewer，且只能使用 GitHub。

# Rule 4 - 送出前六題

- 送出前，必須使用以下六題檢查回答；六題是自我檢查提示，不把「branch 明天仍存在」改成一律違規。

1. 能不能切到一天內可以 merge？
2. 這個 PR 現在 merge，main 還能正常工作嗎？
3. 未完成功能能不能用 Feature Flag 隱藏？
4. 大改造能不能用 abstraction 讓新舊實作共存？
5. CI 能不能快速告訴我這次改動有沒有破壞系統？
6. 這個 branch 明天還會存在嗎？是的話，檢查是不是切得太大。

## Good Example

檢查計畫是否能安全整合，把跨日當作重新檢視切分的訊號。

- 情境：計畫中的 branch 明天仍會存在。
- 檢查：逐題檢視小批次、main、隱藏方式、抽象、CI 與壽命，重新看能否切小；跨日不直接推成違反硬性門檻。

## Bad Example

相同情境略過其他檢查，直接把提示變成硬規則。

- 情境：計畫中的 branch 明天仍會存在。
- 檢查：不再看其他五題，因為活到明天就一律不是 TBD。
