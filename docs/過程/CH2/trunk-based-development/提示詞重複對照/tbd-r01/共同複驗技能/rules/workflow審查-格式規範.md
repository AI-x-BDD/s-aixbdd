# Rule 1 - workflow 的審查事實

- 審查 branch、PR 或團隊 workflow 時，必須依輸入核對以下事實，再使用已載入的共通判斷與適用整合技巧形成審查結果。
  - 有沒有 `develop`、`team-a`、`release-next` 這類長期共同開發分支？
  - 每人每天至少整合 main 一次嗎？
  - branch 壽命（含 review 等待）多長？active branches 多少？
  - CI 多快回饋？main 紅了是否立即修或 revert？
  - 有沒有靠 code freeze 解決整合問題？
  - Feature Flag 有沒有清理？

## Good Example

以輸入中的整合事實判斷，而非只看 branch 名稱。

- 輸入：團隊沒有 develop，但多人在同一個 feature branch 工作兩週；CI 每次回饋五分鐘，所有變更最後才整合。
- 審查：列出共用分支的壽命與整合時機，依共通判斷辨識長期分叉；分別列出 CI 已知資訊與尚缺的 review、flag、freeze 資訊。

## Bad Example

相同輸入下忽略已知事實，只用名稱判定合規。

- 輸入：團隊沒有 develop，但多人在同一個 feature branch 工作兩週；CI 每次回饋五分鐘，所有變更最後才整合。
- 審查：因為沒有 develop，所以團隊已符合 TBD；不再檢查其他項目。

# Rule 2 - 導入前提與適用性

- 評估導入時，必須檢查自動 build、自動 test、快速 CI、小批次開發能力、快速 code review。
- 缺少前提時，必須先指出缺的前提，不得直接建議全面導入；缺這些時，TBD 容易變成「大家一直 merge main，main 一直壞」。
- 說明風險時，必須保留 DORA 的條件：經驗不足、缺少 gated checks、沒有「broken trunk 優先修復」紀律的團隊，實行 TBD 反而可能增加錯誤與返工。
- 評估適用性時，可以使用既有適用類型：SaaS、Web App、Backend API、Frontend App、Microservice、企業內部系統、頻繁發布、多人共同維護的 codebase。
- 評估價值時，必須區分「需求一直變、多人同時改、需要頻繁 release」三者同時成立時價值最高，與缺前提時的導入風險。

## Good Example

先指出缺少的前提，避免把產品類型當成導入保證。

- 輸入：多人維護的 SaaS 經常改需求並每日發布，但沒有自動測試、review 常拖延。
- 評估：三項價值條件成立；先建立自動測試與快速 review，指出導入風險，不直接全面導入。

## Bad Example

相同輸入下只因類型適合就直接導入，忽略前提。

- 輸入：多人維護的 SaaS 經常改需求並每日發布，但沒有自動測試、review 常拖延。
- 評估：SaaS 適合 TBD，所以立即讓所有人頻繁 merge，不需要先補前提。
