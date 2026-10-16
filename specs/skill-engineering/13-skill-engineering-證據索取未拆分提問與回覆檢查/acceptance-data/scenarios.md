# 驗收情境原始輸入與執行紀錄

本檔保存重現 `blueprint.md` 第 8 節所需的最小資料。fixture 檔放在同目錄的 `fixture-v1/`、`fixture-v2/`、`fixture-v2-S6b/`；W1/W2 工作項原文放在 `work-items.md`。

## 1. 環境建立方式

- 測試專案：正式 repo 的實體副本，用 `rsync -a --exclude /.git --exclude target --exclude /specs --exclude /upstreams --exclude /skills` 複製，受測 Skill 為施工後版本（`SKILL.md` sha256 `a3c27462a7c6ade9a3f38cf7ae8ec3a326f271492cd7739ec381ec9f790aec67`）。副本不是 Git repo。
- 在專案根目錄建立 `evidence/`，放入對應版本的 fixture 檔。
- 副作用檢查：執行前後比對副本中所有檔案的 sha256 清單（排除 `java-web-framework/`、`src/`）。

## 2. 子代理提示（每個情境共用）

```text
你在測試環境 <情境目錄>（專案根目錄，非 Git repo；禁止任何 git 指令、不得修改此目錄以外檔案、不要讀其他 /tmp 目錄）。
請載入 <情境目錄>/.agents/skills/skill-engineering/SKILL.md，以下列使用者訊息為輸入，依其 SOP 從 Phase 1 步驟 1 開始逐步實際執行。執行範圍：只執行到 Phase 1 步驟 12（含）之前；SOP 依流程即將執行步驟 12 或更後面的步驟時、或 SOP 要求停止時，立即停止並回報。腳本可依 SOP 執行。需要使用者回覆時，依序使用下方「預先回覆」；預先回覆用完仍需要回覆時，視為使用者尚未回覆。
```

- 第一版的 S3、S4、S5、S6 另加：「不要自行搜尋專案以取代使用者提供證據。」
- 第二版的 S3b、S4b、S6b 另加：「證據只採用使用者訊息與回覆中提供或指向的內容，不要自行瀏覽或搜尋專案中的其他檔案作為證據。」
- S3c 改為：「在開始執行 Phase 1 步驟 12 之前停止（步驟 12 本身不要執行）」，並加上「只有在 SOP 的 WRITE 步驟實際向使用者索取或提問之後，才可以使用下一則預先回覆」，同時要求寫出索取原文、回報偏離。
- 每個情境都要求回報：步驟序列、讀取或執行的內容、每個 CHECK 的判定與走向、索取原文、使用了哪則預先回覆、停止點、「問題證據」及來源、寫入的檔案。

## 3. 情境輸入與預先回覆

| 情境 | 使用者訊息 | 預先回覆（依序） |
| ---- | ---------- | ---------------- |
| S1 | 請建立一個新 Skill，名稱 api-error-message，用途是撰寫 REST API 的錯誤訊息內容。 | 無 |
| S2／S2b | /skill-engineering 優化 plan-with-class-diagram。對話紀錄在 evidence/session-log.md，它產出的提案是 evidence/class-diagram-proposal.md。問題：類別圖上看不出哪些類別是新增、哪些是修改，雖然下方實作順序有寫。我預期類別圖本身就要標示變更狀態。 | 無 |
| S3／S3b／S3c | /skill-engineering 優化 plan-with-class-diagram。之前它產出的類別圖看不出哪些類別是新增、哪些是修改。我預期類別圖本身就要標示變更狀態。 | 1.「對話紀錄在 evidence/session-log.md，產出的提案在 evidence/class-diagram-proposal.md。」 |
| S4／S4b | 同 S3 | 1.「對話紀錄在 evidence/session-log.md。」 2.「產出的提案在 evidence/class-diagram-proposal.md。」 |
| S5 | 同 S3 | 1.「那次的對話和產出檔都已經刪掉了，無法提供。」 |
| S6／S6b | /skill-engineering 優化 plan-with-class-diagram。對話紀錄在 evidence/session-log.md。問題：它產出的類別圖看不出哪些類別是新增、哪些是修改。我預期類別圖本身就要標示變更狀態。 | 1. 提案檔沒存，直接貼上內容：`fixture-v1/class-diagram-proposal.md` 的 mermaid 區塊，以及「1. 新增 Logged 2. 新增 LoggingRequestHandler 3. 修改 WebApplication」 |

## 4. 使用的 fixture

| 情境 | fixture | `evidence/` 內容 |
| ---- | ------- | ---------------- |
| S1～S6 | 第一版 | `fixture-v1/session-log.md`（`7e898d50…e75c`）、`fixture-v1/class-diagram-proposal.md`（`52288f7a…f8a`） |
| S2b、S3b、S3c、S4b | 第二版 | `fixture-v2/session-log.md`（`ec1d5cf8…3583`）、`fixture-v2/class-diagram-proposal.md`（`52288f7a…f8a`） |
| S6b | 第二版（未保存提案） | 只有 `fixture-v2-S6b/session-log.md`（`b7c74111…4cc1`） |

## 5. 各次執行結果

全部都是獨立子代理的實際執行。每個副本執行前後的 sha256 清單都一致（S6b 共 171 個檔案，其餘各 172 個），沒有建立 `specs/` 或 `.git`。

| 執行 | 步驟序列（實際） | 停止點 | 判定 | 偏離（執行者自述或回報所見） |
| ---- | ---------------- | ------ | ---- | ---------------------------- |
| S1 | 1→2→4→5→6（不適用）→7 判定新建→10～12 不適用 | 13 之前 | 通過 | 無 |
| S2 | 1→2→4→5→6（讀兩份證據）→7 判定不足→8→9 未回覆 | 9 | 未符合預期分支（預期判定充分），分支動作符合 SOP | 無；判定不足的理由：沒有讀檔清單、紀錄的路徑與提供檔不一致、需要完整逐步紀錄 |
| S3 | 6→7 不足→8→9 用回覆 1→6 讀兩份證據→7 不足→8→9 未回覆 | 9 | 回到步驟 6 的回圈已實際執行；最後沒有達到充分 | 讀了整份根因分析規範 |
| S3b | 6→7（沒有判定）→未執行 8→9 用回覆 1→6→7 判定充分→10→11→執行了 12 的讀取 | 13 之前 | **失敗** | 提前消費預先回覆、沒有執行 8 的索取、越過停止點；讀了整份根因分析規範 |
| S3c | 6→7 不足→8 索取→9 用回覆 1→6→7 判定充分→10→11 | 12 之前 | 通過 | 讀了整份根因分析規範 |
| S4 | 6（索取前自行讀了 `evidence/session-log.md`）→7 判定缺產出物→8→9 用回覆 2→6→7 判定充分→10→11 | 12 之前 | 偏離 | 自行取證，回覆 1 沒有使用；讀了整份根因分析規範 |
| S4b | 6→7 不足→8→9 用回覆 1→6→7 判定缺產出物→8→9 用回覆 2→6→7 判定充分→10→11 | 12 之前 | 通過 | 無 |
| S5 | 6→7 不足→8→9 表示無法提供，回報缺少的證據並停止 | 9 | 通過 | 無 |
| S6 | 6 讀紀錄檔→7 不足→8→9 用回覆 1→6 合併紀錄檔與對話補充並標出來源→7 不足→8→9 未回覆 | 9 | E3 的合併行為已觀察到；最後沒有達到充分 | 無；判定不足的理由：沒有讀檔清單、缺少判斷依據 |
| S2b | 6→7 判定充分→10→11 | 12 之前 | 通過 | 無 |
| S6b | 6 讀紀錄檔→7 判定缺產出物→8→9 用回覆 1→6 合併並標出來源→7 判定充分→10→11 | 12 之前 | 通過 | 無 |

有回報 audit 結果的步驟 10 執行（S2b、S3b、S3c、S4、S4b、S6b），目標 `plan-with-class-diagram` 都是 0 error、0 warning。S1 是新建模式，S2、S3、S5、S6 停在步驟 9，都沒有執行步驟 10。
