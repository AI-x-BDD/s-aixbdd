# Rule 1 - 區分來源與 branch 壽命目標

- 回答時必須區分規則來源：TBD 官方為 TrunkBasedDevelopment.com；DORA 為 Google DORA 的 DevOps 研究；團隊規則是 TBD 沒規定、由團隊自行決定的部分。
- 說明 branch 壽命時，必須區分官方通常 1～2 天與 DORA 以不到一天為目標；不得把「2 天」說成硬性國際標準。

## Good Example

同一問題分別列出來源與目標，沒有把建議變成硬性界線。

- 情境：團隊問 branch 活兩天是否必然違反 TBD。
- 回答：官方短期 branch 通常約 1～2 天；DORA 以不到一天為目標。兩天不是硬性國際標準，還要檢查整合方式與其他核心規則。

## Bad Example

相同問題將不同來源混成單一硬性規定。

- 情境：團隊問 branch 活兩天是否必然違反 TBD。
- 回答：TBD、DORA 和團隊規範都一樣，國際標準規定超過兩天必然違規。

# Rule 2 - 區分核心規則與強烈建議

- 必須以單一 trunk（`main`）為整合主線，不得建立長期開發分支；只從 main 開 branch 但 feature branch 活 2～3 週，仍不算 TBD。
- 必須頻繁整合 main。DORA 的要求是至少每天一次，一天多次更好。
- 必須讓 main 任何時候保持可工作、可發布；不得為了小批次而整合不能工作的程式。
- CI 紅了必須先修 main，不得繼續開發新功能；DORA 建議立即修或立即 revert，不是「晚上再看」。
- Branch 應非常短命、active branches 應維持少量；不得把這些強烈建議當作團隊自行選的 merge 方法，也不得為其另造硬性數字門檻。
- 應避免靠 code freeze 解決整合問題；多人在同一 feature branch 開發、branch 一直不刪、接近 release 就 code freeze，必須辨識為官方列出的錯誤模式。
- 說明 CI 回饋時，應保留 DORA 建議：每個 commit 觸發 build 與自動測試，回饋在幾分鐘內。

## Good Example

同一團隊以小變更持續整合，優先處理 broken trunk，並區分核心與建議。

- 情境：團隊從 main 開工作分支，正在評估是否符合 TBD。
- 回答：目前是少量短命分支，每天整合小變更；main 紅了立即修復或 revert，未整合不能工作的程式，符合核心方向。仍應維持短壽命與少量 active branches。

## Bad Example

相同團隊只看分支起點，忽略長期隔離及 broken trunk。

- 情境：團隊從 main 開工作分支，正在評估是否符合 TBD。
- 回答：只要從 main 開 branch 就符合；大家共用同一 feature branch 三週，月底合 main，紅燈晚上再修，release 前 code freeze 即可。

# Rule 3 - 保留團隊工作流的決策空間

- 必須將下列項目歸為團隊自行決定：squash／merge commit／rebase merge、同步 main 用 merge 還是 rebase、branch 命名、reviewer 人數、GitHub 或 GitLab、是否禁止 direct push。
- 不得將這些團隊選項說成 TBD 的必要要求。

## Good Example

同一個團隊可以選擇自己的整合方式，不因 Git 命令被錯誤分類。

- 情境：團隊同步 main 用 merge，整合用 merge commit，只有一位 reviewer。
- 回答：這些由團隊決定，TBD 沒規定一定要 rebase、squash 或兩位 reviewer；應以核心規則評估工作方式。

## Bad Example

相同團隊被額外套上沒有依據的必要條件。

- 情境：團隊同步 main 用 merge，整合用 merge commit，只有一位 reviewer。
- 回答：必須改用 rebase、squash、兩位 reviewer 並禁止 direct push，否則一定不是 TBD。
