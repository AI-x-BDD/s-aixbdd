# 工程藍圖：skill-engineering－建立

- 模式：新建（同時修正既有 skill-form-*、skill-derive-* 的矛盾與委派協議）
- 紀錄目錄：`specs/skill-engineering/01-skill-engineering-建立/`
- 根因報告：不適用（新建模式）；本次為自舉建置，skill-engineering 尚不存在，流程由人工依本藍圖的方法執行
- 確認紀錄：使用者在對話中確認兩輪提案（編排機制、根因分析閘門與敢刪原則），並指示「照建置順序，每一點都依照建議內容」：derive 協議修改、另建 skill-form-description、紀錄存檔、子代理實跑驗收、先寫 audit 腳本並修正既有矛盾

## 1. 驗收條件

| 編號 | 驗收條件 | 來源 | 適用範圍 |
| ---- | -------- | ---- | -------- |
| E1 | 新建與優化兩種模式都從驗收條件推導 To-Be，並編排 `skill-form-*` 與 `skill-derive-*` 施工 | 本次 | 通用 |
| E2 | 優化模式先完成根因分析，根因報告經使用者確認後才提出工程藍圖 | 本次 | 通用 |
| E3 | 優化時每個既有元素都必須追溯到驗收條件或根因，無法追溯者刪除，並揭露淨增減 | 本次 | 通用 |
| E4 | 使用者只確認一次工程藍圖；被委派的 `skill-derive-*` 與 `skill-form-*` 以藍圖為已確認設計，不再重複詢問或另行設計 | 本次 | 通用 |
| E5 | 根因報告與工程藍圖存檔於 `specs/skill-engineering/<NN>-<Skill>-<主題>/` | 本次 | 通用 |
| E6 | 施工後以不帶分析脈絡的子代理實際執行驗收情境 | 本次 | 通用 |
| E7 | frontmatter 由新建的 `skill-form-description` 把關 | 本次 | 通用 |
| E8 | 機械檢查由腳本執行，既有 Skill 通過結構診斷且沒有 error | 本次 | 通用 |

## 2. To-Be SOP

````markdown
---
name: skill-engineering
description: 建立新 Skill，或依使用者回報的不滿意結果優化既有 Skill（包含透過上下游委派一起產出結果的相關 Skill）時，必須使用此 Skill；使用者提到建立 skill、create skill、改寫或優化 skill、skill 結果不如預期時使用。先定義驗收條件；優化時先做根因分析並取得使用者確認，再從預期重新設計、刪除無法追溯的流程與規則，並編排 skill-form-* 與 skill-derive-* 施工及實跑驗收。只為單一 SOP 步驟抽取單一部位時，改用對應的 skill-derive-*；只撰寫單一部位檔案時，改用對應的 skill-form-*。
---

# SOP

## Phase 1 -- 蒐證與定義預期

1. `READ` 使用者需求。
2. `THINK` 判定模式為新建或優化，並確定目標 Skill 名稱、本專案的所有 skills 目錄（例如 `.agents/skills`、`.claude/skills`、`skills`）、目標 Skill 所在的 skills 目錄與專案根目錄。
3. `READ` 新建模式時，讀取所有 skills 目錄中其他 Skill 的 `name` 與 `description`；已有 Skill 涵蓋需求時，向使用者說明並改以優化模式處理該 Skill。
4. `DELEGATE` 本次紀錄目錄尚未確定時，在本 Skill 目錄執行 `uv run --script scripts/next_record_dir.py --project-root <專案根目錄絕對路徑> --skill <目標 Skill 名稱> --topic <主題>`，從標準輸出 JSON 的 `record_dir` 取得「本次紀錄目錄」（編號為既有最大編號加一，不回補缺號）；`<主題>` 在新建模式為「建立」，在優化模式為不含空白的問題簡述。若缺少 `uv`，依 https://docs.astral.sh/uv/getting-started/installation/ 的目前平台安裝說明安裝後重試，安裝失敗時回報原因並停止。
5. `CHECK` 執行腳本時確認退出狀態為零且標準輸出為可解析的 JSON；失敗時依標準錯誤輸出修正參數後重試，仍失敗時回報原因並停止。
6. `READ` 優化模式時，讀取問題發生時的對話紀錄（本次對話上下文或使用者指定的紀錄檔）與不滿意的產出物，建立「問題證據」；缺少判斷所需的關鍵證據時，請使用者提供。
7. `DELEGATE` 優化模式時，在本 Skill 目錄執行 `uv run --script scripts/audit_skill.py --skills-root <skills 目錄絕對路徑> --skill <目標 Skill 名稱> --graph`，每個 skills 目錄各加一個 `--skills-root` 參數，從標準輸出取得 JSON「結構診斷」；若缺少 `uv`，依 https://docs.astral.sh/uv/getting-started/installation/ 的目前平台安裝說明安裝後重試，安裝失敗時回報原因並停止。
8. `CHECK` 執行腳本時確認退出狀態為零且標準輸出為可解析的 JSON；失敗時依標準錯誤輸出修正參數後重試，仍失敗時回報原因並停止。
9. `READ` 優化模式時，依「問題證據」與「結構診斷」的呼叫關係，讀取產出問題結果之 Skill 及其上下游 Skill 的 `SKILL.md`、所有 RuleFile 與樣板組，並以 `--help` 與檔頭說明了解每個腳本的介面，腳本與問題相關時才讀取全文，建立「產出鏈現況」。
10. `READ` 定義預期時，讀取 `rules/驗收條件-格式規範.md` 的所有 Rule，建立驗收條件檢查清單。
11. `THINK` 依已載入的驗收條件檢查清單，將使用者需求寫成驗收條件與驗收情境；優化模式另從「產出鏈現況」推導目標 Skill 的既有核心預期。
12. `CHECK` 逐條驗證驗收條件檢查清單；未通過時修正驗收條件與驗收情境。

完成條件：已判定模式與本次紀錄目錄，驗收條件與驗收情境均通過驗收條件檢查清單；優化模式另已取得問題證據、結構診斷與產出鏈現況。

## Phase 2 -- 根因分析與確認

1. `CHECK` 新建模式時略過本 Phase，進入 Phase 3。
2. `READ` 分析根因時，讀取 `rules/根因分析-格式規範.md` 的所有 Rule，建立根因分析檢查清單。
3. `THINK` 依已載入的根因分析檢查清單，以「問題證據」沿「產出鏈現況」演練 SOP，找出第一個偏離點。
4. `THINK` 依根因分析檢查清單確定根因與缺陷類型，並依「結構診斷」的呼叫關係列出影響範圍。
5. `CHECK` 逐條驗證根因分析檢查清單；未通過時補充證據或修正分析。
6. `READ` 撰寫根因報告時，讀取 `templates/rca-report.md` 與 `templates/rca-report.example.md`，建立根因報告樣板組。
7. `WRITE` 依已載入的根因報告樣板組，將根因報告寫入本次紀錄目錄的 `rca-report.md`，並向使用者展示。
8. `CHECK` 使用者回覆：對驗收條件有異議，或補充內容改變了驗收條件時，返回 Phase 1；對根因有異議時，依回覆補充證據並重新執行本 Phase；確認且補充內容不改變驗收條件與根因時，將補充記入根因報告並視為確認；未明確確認時停止執行。使用者確認根因不在 Skill，或所有落差都只來自個案驗收條件時，回報結論與個案驗收條件的調整建議後結束，不進入 Phase 3。

完成條件：新建模式已略過本 Phase；優化模式的使用者已明確確認根因報告中的驗收條件與根因，且根因位於 Skill 內。

## Phase 3 -- 從預期重新設計

1. `READ` 設計 To-Be 時，讀取 `rules/重新設計-格式規範.md` 與 `rules/約束分配-格式規範.md` 的所有 Rule，建立設計檢查清單。
2. `THINK` 依已載入的設計檢查清單，從驗收條件（優化模式另含已確認的根因）推導 To-Be 的 frontmatter、Phase、步驟與每個步驟的約束。
3. `THINK` 依設計檢查清單為每條約束指定存放位置。
4. `THINK` 依設計檢查清單，將 To-Be 與「產出鏈現況」中的目標 Skill（新建模式為空）對照，產生差異表、淨增減與回歸情境。
5. `READ` 規劃施工時，讀取 `rules/施工委派-格式規範.md` 的所有 Rule，建立施工委派檢查清單。
6. `THINK` 依已載入的施工委派檢查清單，將差異整理成施工工作項與工作項內容，每個工作項的狀態設為「待施工」。
7. `CHECK` 逐條驗證設計檢查清單與施工委派檢查清單；未通過時修正設計與施工工作項。
8. `READ` 撰寫工程藍圖時，讀取 `templates/engineering-blueprint.md` 與 `templates/engineering-blueprint.example.md`，建立工程藍圖樣板組。
9. `WRITE` 依已載入的工程藍圖樣板組，將工程藍圖寫入本次紀錄目錄的 `blueprint.md`，驗收結果段落暫寫「尚未施工」。

完成條件：設計檢查清單與施工委派檢查清單均已通過，工程藍圖已寫入本次紀錄目錄。

## Phase 4 -- 確認藍圖

1. `WRITE` 依工程藍圖的段落順序向使用者展示工程藍圖，並逐條標出來源為推定或適用範圍無法判斷的驗收條件，以及所有刪除項目；新建模式的驗收條件在此首次取得確認。
2. `CHECK` 使用者回覆；對驗收條件有異議時返回 Phase 1，要求修改其他內容時返回 Phase 3，未明確確認時停止執行；確認時將確認內容與推定驗收條件的回覆寫入工程藍圖的確認紀錄。

完成條件：使用者已明確確認目前版本的工程藍圖。

## Phase 5 -- 施工與驗收

1. `READ` 已確認的工程藍圖中各施工工作項的狀態，建立「待施工清單」。
2. `WRITE` 依施工委派檢查清單，刪除「待施工清單」中標記刪除的整個部位檔案，並在工程藍圖將這些工作項標記為「已完成」。
3. `DELEGATE` 依施工委派檢查清單的順序，將「待施工清單」中其餘工作項逐項交給指定的 `skill-form-*` 或 `skill-derive-*`，傳入該工作項內容作為已確認的設計，每完成一項即在工程藍圖將其標記為「已完成」。
4. `CHECK` 「待施工清單」的工作項均已標記為「已完成」；因施工差異停止時，將差異記錄於工程藍圖並返回 Phase 3，重新進入本 Phase 時只施工狀態為「待施工」的工作項。
5. `DELEGATE` 在本 Skill 目錄執行 `uv run --script scripts/audit_skill.py --skills-root <skills 目錄絕對路徑> --skill <已修改的 Skill 名稱>`，每個 skills 目錄與每個已修改的 Skill 各加一個參數，取得「施工後結構診斷」；若缺少 `uv`，依 https://docs.astral.sh/uv/getting-started/installation/ 的目前平台安裝說明安裝後重試，安裝失敗時回報原因並停止。
6. `CHECK` 退出狀態為零，且「施工後結構診斷」沒有任何 `error`；有 `error` 時依施工委派檢查清單修正後重新執行上一步。
7. `CHECK` 目標 Skill 的 frontmatter、SOP 與部位均與工程藍圖的 To-Be 及約束分配表一致，且部位中的範例與規則沒有互相矛盾。
8. `WRITE` 為每個驗收情境建立包含本次未提交修改的暫存專案複本，依情境描述準備測試環境，並記錄執行前的狀態（例如 `git status` 與相關檔案的雜湊值），以便比對副作用。
9. `CHECK` 每個測試環境均與其情境描述一致；不一致時修正測試環境。
10. `DELEGATE` 以不帶本次分析脈絡的子代理，只提供修改後 Skill 的路徑、測試環境位置、情境輸入與預先回覆，並要求回報每個確認閘門展示的內容與最終產出，逐一執行驗收情境，取得「驗收產出」；無法隔離副作用，或只驗證未受本次修改影響之步驟的情境，改為逐步演練並在驗收結果中註明。
11. `CHECK` 依驗收情境的判斷方式檢查「驗收產出」；情境失敗來自測試環境與情境描述不一致時，修正測試環境、記錄於驗收結果後重新執行該情境；失敗來自 Skill 時，優化模式返回 Phase 2 修正根因，新建模式返回 Phase 3 修正設計。
12. `WRITE` 將施工後結構診斷摘要、各驗收情境的結果與驗收方式寫入工程藍圖的驗收結果段落，並向使用者回報結果與個案驗收條件的調整建議。

完成條件：工程藍圖的所有施工工作項均為「已完成」，施工後結構診斷沒有 `error`，所有驗收情境均已通過，且驗收結果已寫入工程藍圖並回報使用者。
````

## 3. 差異表

### 刪除

| 元素 | 位置 | 理由 |
| ---- | ---- | ---- |
| `rules/sop-格式規範.md`（非 RuleFile 格式，含標題與 Purpose） | skill-form-sop | 內容改寫為 `rules/SOP-格式規範.md` 的 RuleFile 格式；與按需載入規則重疊的部分合併，不保留兩份 |
| `rules/SOP-按需載入格式規範.md` 的 Rule 1、Rule 4 | skill-form-sop | 不屬於按需載入主題，移入 `SOP-格式規範.md`（Rule 4、Rule 5） |
| 範例中的 `API-錯誤訊息格式規範.md` 等檔名 | skill-form-rule、skill-derive-rule 的 RuleFile | 違反 `<主題>-格式規範.md` 命名，改為 `API-錯誤訊息-格式規範.md` |

### 修改、合併、改換存放位置與新增

| 元素 | 動作 | 內容 | 追溯 |
| ---- | ---- | ---- | ---- |
| `skill-engineering`（SKILL.md、5 個 RuleFile、2 組樣板、2 個腳本） | 新增 | 編排器本體 | E1–E6、E8 |
| `skill-form-description`（SKILL.md、`rules/Skill描述-格式規範.md`） | 新增 | frontmatter 的格式與觸發邊界 | E7 |
| `skill-form-sop/rules/SOP-格式規範.md`、`SOP-按需載入-格式規範.md` | 改寫、改名 | RuleFile 格式；載入步驟與第一個依賴步驟之間只允許其他載入步驟；定義 `DELEGATE`、`CHECK` 語意 | E8 |
| `skill-form-sop` Phase 1 | 修改 | 按需載入第二份 RuleFile；目標 SKILL.md 改為修改時才讀取 | E8 |
| 五個 `skill-form-*` Phase 1 `THINK` | 修改 | 呼叫者提供已確認設計時不另行設計，不符檢查清單時回報差異並停止 | E4 |
| 三個 `skill-derive-*` Phase 1 `THINK` 與 Phase 2 | 修改 | 以工程藍圖工作項為分析結果並驗證；Before／After 與藍圖一致時視為已確認 | E4 |
| `skill-form-rule` Phase 1、Phase 2 | 修改 | 條件式讀取既有 RuleFile；只有呼叫者不負責 SKILL.md 時才更新載入步驟 | E8 |
| `skill-form-script` Phase 2 | 修改 | 測試資料放在目標 Skill 以外的暫存目錄 | E8 |
| `skill-derive-template/rules/樣板抽取分析-格式規範.md` Rule 1、Rule 4 | 修改 | 允許之後才寫入檔案的草稿；載入位置規則與 SOP 按需載入規則一致 | E8 |
| 七個 `skill-form-*`、`skill-derive-*` 的 `description` | 修改 | 補上相鄰 Skill 分流與英文觸發關鍵字 | E7 |

### 保留

| 元素 | 追溯 |
| ---- | ---- |
| `plan-with-class-diagram` 全部 | 不在本次範圍；通過結構診斷 |
| 三個 `skill-derive-*` 的分析與委派 RuleFile（除上表修改外） | E1：施工時的第二道檢查 |
| 其餘 `skill-form-*` RuleFile | E8 |

## 4. 淨增減

| 項目 | As-Is | To-Be | 增減 |
| ---- | ----- | ----- | ---- |
| Skill | 8 | 10 | +2 |
| Phase | 20 | 27 | +7 |
| 步驟 | 78 | 127 | +49 |
| RuleFile | 13 | 19 | +6 |
| Rule | 50 | 81 | +31 |
| 樣板組 | 1 | 3 | +2 |
| 腳本 | 1 | 3 | +2 |

淨增加全部來自新建的 `skill-engineering`（5 個 Phase、43 個步驟、24 條 Rule、2 組樣板、2 個腳本）與 `skill-form-description`（2 個 Phase、6 個步驟、4 條 Rule）。既有 Skill 的步驟數不變；`skill-form-sop` 的 Rule 由 4 條增為 7 條，是把非 RuleFile 格式的條列改寫為可檢查的 Rule 與正反範例。

## 5. 約束分配表

| 編號 | 約束 | 所屬步驟 | 存放位置 | 理由 |
| ---- | ---- | -------- | -------- | ---- |
| C1 | 紀錄目錄編號為既有最大編號加一 | P1-4 | `scripts/next_record_dir.py` | 輸入輸出明確，驗收時實際發生過 AI 算錯編號的情形 |
| C2 | SOP、RuleFile、樣板組、腳本的結構與孤兒部位檢查、Skill 呼叫圖 | P1-7、P5-5 | `scripts/audit_skill.py` | 可由程式判斷，每次施工後都要重複執行 |
| C3 | 驗收條件的格式、來源、適用範圍與驗收情境 | P1-11 | `rules/驗收條件-格式規範.md` | 需要判斷，需要正反例 |
| C4 | 證據、演練、缺陷類型、反事實、非 Skill 結論與報告範圍 | P2-3、P2-4 | `rules/根因分析-格式規範.md` | 需要判斷，需要正反例 |
| C5 | 從預期推導、舉證責任、根因位置、先刪改後新增、淨增減、呼叫者回歸 | P3-2、P3-4 | `rules/重新設計-格式規範.md` | 需要判斷，需要正反例 |
| C6 | 唯一存放位置與存放位置的選擇順序 | P3-3 | `rules/約束分配-格式規範.md` | 需要判斷，需要正反例 |
| C7 | 執行者分工、胖 SOP、施工順序、委派內容與施工差異 | P3-6、P5-3 | `rules/施工委派-格式規範.md` | 需要判斷，需要正反例 |
| C8 | 根因報告的結構 | P2-7 | `templates/rca-report.{md,example.md}` | 規範整份產出檔案 |
| C9 | 工程藍圖的結構 | P3-9 | `templates/engineering-blueprint.{md,example.md}` | 規範整份產出檔案 |
| C10 | 兩道確認閘門、返回路徑與略過條件 | P2-8、P4-2 | SOP 流程 | 屬於流程分支與使用者確認 |

## 6. 施工工作項

| 順序 | 工作項 | 執行者 | 目標 | 內容 | 約束 | 狀態 |
| ---- | ------ | ------ | ---- | ---- | ---- | ---- |
| 1 | W1 | 人工（自舉） | `skill-engineering/scripts/audit_skill.py` | 結構診斷與呼叫圖腳本，並以違規測試資料驗證每一項檢查 | C2 | 已完成 |
| 2 | W2 | 人工（自舉） | skill-form-sop、skill-form-rule | 修正結構診斷與審查發現的既有矛盾 | E8 | 已完成 |
| 3 | W3 | 人工（自舉） | 三個 skill-derive-* | 加入工程藍圖確認協議 | E4 | 已完成 |
| 4 | W4 | 人工（自舉） | skill-form-description | 新建 Skill | E7 | 已完成 |
| 5 | W5 | 人工（自舉） | skill-engineering | SKILL.md、5 個 RuleFile、2 組樣板、`next_record_dir.py` | C1、C3–C10 | 已完成 |
| 6 | W6 | 人工（自舉） | 全部 | 依三輪驗收的摩擦清單修正 | E1–E8 | 已完成 |

### 工作項內容

各工作項的完整內容即為上述路徑中的現行檔案；本藍圖的第 2 節記錄 `skill-engineering` 的 To-Be SOP，第 3 節記錄其他 Skill 的修改範圍。

## 7. 驗收情境

| 編號 | 驗證 | 類型 | 輸入 | 預先回覆 | 判斷方式 |
| ---- | ---- | ---- | ---- | -------- | -------- |
| S1 | E1、E4–E8 | 本次 | 新建 `changelog-from-diff`：依 staged 變更產生 Keep a Changelog 條目，寫入前確認 | Phase 4 回覆「確認」 | 新 Skill 結構診斷 0 error；紀錄目錄含 `blueprint.md`；子代理實跑情境均通過 |
| S2 | E1–E6、E8 | 本次 | 優化 `plan-with-class-diagram`：計畫目錄編號重複（03 已被使用） | 閘門 A、閘門 B 均回覆「確認」 | 根因定位到編號步驟；修改後編號不重複；子代理實跑通過 |
| S3 | E1、E4–E8 | 回歸 | 第一輪修正後，新建 `adr-writer`；專案已有紀錄 01 與 03 | Phase 4 回覆「確認」並接受全部推定條件 | 紀錄編號為 04；工作項內容完整；子代理實跑通過 |

## 8. 驗收結果

- 結構診斷：本專案 `.agents/skills` 中 10 個模組化 Skill 均為 0 個 error、0 個 warning（`skill-creator` 為官方格式，不在範圍）。
- S1 通過：子代理在暫存專案複本中依 SOP 完成全部 Phase；新 Skill 0 error，5 個驗收情境以子代理實跑通過（其中一個因測試環境與情境不符，修正環境後重跑通過）。回報 26 項摩擦，已依本藍圖第 3 節修正。
- S2 通過：根因為 `plan-with-class-diagram` P1-7 的編號由 AI 判斷（載體過弱），改由腳本計算並刪除重複的結構描述；子代理實跑得到 `04` 與 `06`（有缺號時不回補）。回報 21 項摩擦，已修正；其中「skill-engineering 自己的紀錄編號也由 AI 判斷」促成 C1 的 `next_record_dir.py`。
- S3 通過：紀錄編號為 `04`；ADR 流水號同樣交給腳本；兩個情境以子代理實跑通過。回報 15 項摩擦，已修正（derive-* 以藍圖為分析結果、確認紀錄欄位、載入位置規則與結構診斷一致等）。
- 靜態審查：不帶脈絡的審查子代理核對 15 項修正與新問題，回報 14 項新問題，均已修正。
- 個案驗收條件：無。
