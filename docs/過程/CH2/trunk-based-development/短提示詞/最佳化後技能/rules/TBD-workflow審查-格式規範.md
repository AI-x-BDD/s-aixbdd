# Rule 1 - 團隊 workflow 審查與導入前提

- 檢查是否真的在做 TBD：

- 有沒有 `develop`、`team-a`、`release-next` 這類長期共同開發分支？
- 每人每天至少整合 main 一次嗎？
- branch 壽命（含 review 等待）多長？active branches 多少？
- CI 多快回饋？main 紅了是否立即修或 revert？
- 有沒有靠 code freeze 解決整合問題？
- Feature Flag 有沒有清理？
- 導入前提是自動 build、自動 test、快速 CI、小批次開發能力與快速 code review。缺少這些時，先指出前提不足，不直接建議全面導入；否則可能變成大家一直 merge main、main 一直壞。經驗不足、缺少 gated checks、沒有「broken trunk 優先修復」紀律時，TBD 反而可能增加錯誤與返工。
- 適合：SaaS、Web App、Backend API、Frontend App、Microservice、企業內部系統、頻繁發布、多人共同維護的 codebase。需求一直變、多人同時改、需要頻繁 release 三者同時成立時價值最高；不把三者同時存在寫成所有團隊的導入前提。

## Good Example

- workflow 有長期 `develop`、CI 失敗仍繼續開發且 review 等待兩天時，回答列出這些缺口並要求先改善前提。

## Bad Example

- 只看到所有人從 main 開 branch，就直接判定團隊已符合 TBD，不檢查 CI、review 與 broken trunk 處理。
