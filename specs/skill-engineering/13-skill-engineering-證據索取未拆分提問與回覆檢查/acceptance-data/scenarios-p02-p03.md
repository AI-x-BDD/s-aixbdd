# P02／P03 驗收情境原始輸入與執行紀錄

本檔保存重現 `blueprint.md` 8.3b 所需的最小資料。執行結果與判定以 8.3b 的表格為準。

## 1. 環境

- P02 驗收（run8）：測試專案複製自施工後的正式 repo，排除 `.git`、`target`、`specs`、`upstreams`、根目錄 `skills` 與 `docs/mindsets`。受測 `SKILL.md` 為 P01 版，`根因分析-格式規範.md` 為 P02 版（sha256 `cf6247a3…93b3`）。
- P03 驗收（run9）：同樣的專案副本，`SKILL.md` 換成 P03 版（sha256 `73b7f315…6c3e`）。
- 每個副本有自己的 `UV_CACHE_DIR`，不是 Git repo；副作用以執行前後的 sha256 清單比對（排除 `java-web-framework/`、`src/`）。

## 2. 子代理提示（共用）

```text
你在測試環境 <情境目錄>（專案根目錄，非 Git repo；禁止任何 git 指令；不得修改此目錄以外檔案；不要讀其他 /tmp 目錄）。執行 `uv` 時一律加上 `UV_CACHE_DIR=<情境>.uv`。工具遇到權限審核時等待結果；被拒絕就如實回報，不要繞過。
請載入 <情境目錄>/.agents/skills/skill-engineering/SKILL.md，以下列使用者訊息為輸入，依其 SOP 從 Phase 1 步驟 1 開始逐步實際執行，每一步都照 SOP 做（含 WRITE 向使用者索取的步驟，請寫出索取原文）。執行範圍：在開始執行 Phase 1 步驟 12 之前停止（步驟 12 本身不要執行）；SOP 要求停止時也立即停止。
使用者互動：只有在 SOP 的 WRITE 步驟實際向使用者索取或提問之後，才可以使用下一則「預先回覆」；預先回覆用完仍需要回覆時，視為使用者尚未回覆。證據只採用使用者訊息與回覆中提供或指向的內容，不要自行瀏覽或搜尋專案中的其他檔案作為證據。
```

- S7（兩個版本）在最後一句加上「（包含訊息中指名的 Skill 檔案位置）」。
- R1 的執行範圍改為「從 Phase 1 執行到 Phase 2 的使用者確認步驟，並依該步驟對回覆的判定行動；不要執行 Phase 3 以後的任何步驟」，並允許在副本內寫入 SOP 要求的紀錄檔。

## 3. 情境輸入、預先回覆與 fixture

| 情境 | 使用者訊息 | 預先回覆 | `evidence/` 內容 |
| ---- | ---------- | -------- | ---------------- |
| S2、S2c、R1 | /skill-engineering 優化 plan-with-class-diagram。對話紀錄在 evidence/session-log.md，它產出的提案是 evidence/class-diagram-proposal.md。問題：類別圖上看不出哪些類別是新增、哪些是修改，雖然下方實作順序有寫。我預期類別圖本身就要標示變更狀態。 | S2、S2c：無；R1：1.「我還在想，先不要往下做。」 | `fixture-v2/` 兩檔 |
| S3 | /skill-engineering 優化 plan-with-class-diagram。之前它產出的類別圖看不出哪些類別是新增、哪些是修改。我預期類別圖本身就要標示變更狀態。 | 1.「對話紀錄在 evidence/session-log.md，產出的提案在 evidence/class-diagram-proposal.md。」 | `fixture-v2/` 兩檔 |
| S4 | 同 S3 | 1.「對話紀錄在 evidence/session-log.md。」 2.「產出的提案在 evidence/class-diagram-proposal.md。」 | `p02-run8/fixtures/S4-session-log.md`（改名為 `session-log.md`，不含輸出內容）與 `fixture-v2/class-diagram-proposal.md` |
| S5 | 同 S3 | 1.「那次的對話和產出檔都已經刪掉了，無法提供。」 | 無 |
| S6 | /skill-engineering 優化 plan-with-class-diagram。對話紀錄在 evidence/session-log.md。問題：它產出的類別圖看不出哪些類別是新增、哪些是修改。我預期類別圖本身就要標示變更狀態。 | 1. 提案檔沒存，貼上 `fixture-v1/class-diagram-proposal.md` 的 mermaid 區塊與「1. 新增 Logged 2. 新增 LoggingRequestHandler 3. 修改 WebApplication」 | `fixture-v2-S6b/session-log.md` |
| S7（P02、P03） | /skill-engineering 優化 plan-with-class-diagram。它的 SKILL.md Phase 1 步驟 12 在步驟內文重抄了 rules/類別圖輸出-格式規範.md Rule 6 第 1 條的整句規則，同一條規則存在兩處。我預期步驟只引用已載入的檢查清單，不重述規則內容。 | 無 | 無；副本中的 `plan-with-class-diagram/SKILL.md` 依 `p02-run8/fixtures/S7-plan-with-class-diagram.diff` 注入重複句 |
| S8 | /skill-engineering 優化 plan-with-class-diagram。上週用它規劃 Logging 功能時，產出的類別圖完全看不出哪些類別是新增、哪些是修改，我很不滿意。我預期類別圖本身就要標示變更狀態。 | 無 | 無 |
| S9 | /skill-engineering 優化 plan-with-class-diagram。對話紀錄在 evidence/session-log.md，產出檔沒有另外保存。問題：它產出的類別圖看不出哪些類別是新增、哪些是修改。我預期類別圖本身就要標示變更狀態。 | 無 | `p02-run8/fixtures/S9-session-log.md`（改名為 `session-log.md`，第 7 則含完整輸出） |

- 執行前核對：S4 的第一則回覆只提供不含輸出內容的紀錄（紀錄中沒有 `classDiagram`），所以第一次補充確實不足以核對現象。

## 4. 結果與副作用

- 每個情境的實際路徑、判定與偏離見 `blueprint.md` 8.3b。
- run8 的 S2～S9：執行前後的 sha256 清單一致（各 170～172 個檔案）。R1：只新增了 SOP 要求的 `specs/skill-engineering/01-plan-with-class-diagram-優化類別圖標示變更狀態/rca-report.md`（副本內，全文見 `p02-run8/R1-rca-report.md`）。
- run9 的 S7、S2c：執行前後的 sha256 清單一致。S7 的執行者曾在副本根目錄建立兩個暫存檔，之後自行刪除。
