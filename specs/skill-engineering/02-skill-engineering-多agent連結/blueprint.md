# 工程藍圖：skill-engineering－多agent連結

- 模式：優化
- 紀錄目錄：`specs/skill-engineering/02-skill-engineering-多agent連結/`
- 根因報告：同一紀錄目錄的 `rca-report.md`，使用者已確認 E1–E7 與 R1
- 確認紀錄：使用者於 2026-09-25 在 Phase 4 回覆「確認，開始施工」，同意全部修改與施工工作項 W1、W2

## 1. 驗收條件

| 編號 | 驗收條件 | 來源 | 適用範圍 |
| ---- | -------- | ---- | -------- |
| E1 | 不論執行的 agent 為何，新建 Skill 的來源一律寫在專案的 `.agents/skills/<name>/` | 本次 | 通用 |
| E2 | 這台電腦安裝了 Claude Code（`CLAUDE_CONFIG_DIR` 或 `~/.claude` 存在）時，施工後 `.agents/skills` 中每個 Skill 在 `.claude/skills/` 都有同名、以相對路徑指向來源的 symlink，目錄不存在時自動建立；沒有安裝時不建立任何目錄或 symlink；兩種情況都不詢問使用者 | 本次 | 通用 |
| E3 | `.claude/skills/` 中與來源同名的實體目錄，或指向其他位置的 symlink，保持不變並回報 | 本次 | 通用 |
| E4 | 指向 `.agents/skills`、但來源已不存在的 symlink 會被移除 | 本次 | 通用 |
| E5 | 只存在 `.claude/skills/`、採模組化格式的實體目錄 Skill，只回報移轉建議，不自動搬移 | 本次 | 通用 |
| E6 | 可以在不修改任何檔案的情況下檢查 symlink 是否齊全，有缺漏或失效時以非零狀態結束 | 本次 | 通用 |
| E7 | 驗收條件、兩道確認閘門、施工與子代理實跑驗收的既有流程維持不變 | 既有 | 通用 |

## 2. To-Be SOP

````markdown
---
name: skill-engineering
description: 建立新 Skill，或依使用者回報的不滿意結果優化既有 Skill（包含透過上下游委派一起產出結果的相關 Skill）時，必須使用此 Skill；使用者提到建立 skill、create skill、改寫或優化 skill、skill 結果不如預期時使用。先定義驗收條件；優化時先做根因分析並取得使用者確認，再從預期重新設計、刪除無法追溯的流程與規則，並編排 skill-form-* 與 skill-derive-* 施工及實跑驗收。只為單一 SOP 步驟抽取單一部位時，改用對應的 skill-derive-*；只撰寫單一部位檔案時，改用對應的 skill-form-*。
---

# SOP

## Phase 1 -- 蒐證與定義預期

1. `READ` 使用者需求。
2. `THINK` 判定模式為新建或優化，並確定目標 Skill 名稱、本專案的所有 skills 目錄（例如 `.agents/skills`、`.claude/skills`、`skills`）、目標 Skill 所在的 skills 目錄與專案根目錄；新建模式的目標 Skill 一律位於專案的 `.agents/skills/<目標 Skill 名稱>/`，不論執行的 agent 為何。
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
7. `DELEGATE` 在本 Skill 目錄執行 `uv run --script scripts/sync_agent_links.py --project-root <專案根目錄絕對路徑>`，從標準輸出取得 JSON「連結同步結果」；若缺少 `uv`，依 https://docs.astral.sh/uv/getting-started/installation/ 的目前平台安裝說明安裝後重試，安裝失敗時回報原因並停止。
8. `CHECK` 退出狀態為零且「連結同步結果」為可解析的 JSON；失敗時依標準錯誤輸出修正後重新執行上一步，仍失敗時回報原因並停止。
9. `CHECK` 目標 Skill 的 frontmatter、SOP 與部位均與工程藍圖的 To-Be 及約束分配表一致，且部位中的範例與規則沒有互相矛盾。
10. `WRITE` 為每個驗收情境建立包含本次未提交修改的暫存專案複本，依情境描述準備測試環境，並記錄執行前的狀態（例如 `git status` 與相關檔案的雜湊值），以便比對副作用。
11. `CHECK` 每個測試環境均與其情境描述一致；不一致時修正測試環境。
12. `DELEGATE` 以不帶本次分析脈絡的子代理，只提供修改後 Skill 的路徑、測試環境位置、情境輸入與預先回覆，並要求回報每個確認閘門展示的內容與最終產出，逐一執行驗收情境，取得「驗收產出」；無法隔離副作用，或只驗證未受本次修改影響之步驟的情境，改為逐步演練並在驗收結果中註明。
13. `CHECK` 依驗收情境的判斷方式檢查「驗收產出」；情境失敗來自測試環境與情境描述不一致時，修正測試環境、記錄於驗收結果後重新執行該情境；失敗來自 Skill 時，優化模式返回 Phase 2 修正根因，新建模式返回 Phase 3 修正設計。
14. `WRITE` 將施工後結構診斷摘要、「連結同步結果」中的並存、衝突與移轉建議、各驗收情境的結果與驗收方式寫入工程藍圖的驗收結果段落，並向使用者回報結果與個案驗收條件的調整建議。

完成條件：工程藍圖的所有施工工作項均為「已完成」，施工後結構診斷沒有 `error`，Skill 連結已依是否安裝 Claude Code 同步，所有驗收情境均已通過，且驗收結果已寫入工程藍圖並回報使用者。
````

## 3. 差異表

### 刪除

| 元素 | 位置 | 理由 |
| ---- | ---- | ---- |
| 無 | — | 既有元素均可追溯至 E7 或 01 號紀錄的驗收條件；本次根因為缺失，沒有需要刪除或改寫的既有內容 |

### 修改、合併、改換存放位置與新增

| 元素 | 動作 | 內容 | 追溯 |
| ---- | ---- | ---- | ---- |
| Phase 1 步驟 2 | 修改 | 加上「新建模式的目標 Skill 一律位於專案的 `.agents/skills/<目標 Skill 名稱>/`，不論執行的 agent 為何」 | R1、E1 |
| Phase 5 步驟 7、8 | 新增 | 執行 `scripts/sync_agent_links.py` 同步 Claude Code 連結，並檢查執行結果 | R1、E2–E5 |
| Phase 5 原步驟 7–12 | 修改 | 依序改為步驟 9–14，內文不變 | 編號連續 |
| Phase 5 步驟 14 | 修改 | 回報內容加上「連結同步結果」中的並存、衝突與移轉建議 | E3、E5 |
| Phase 5 完成條件 | 修改 | 加上「Skill 連結已依是否安裝 Claude Code 同步」 | E2 |
| `scripts/sync_agent_links.py` | 新增 | 偵測 Claude Code、同步 symlink、提供 `--check` 檢查模式 | E2–E6 |

### 保留

| 元素 | 追溯 |
| ---- | ---- |
| frontmatter（`name` 與 `description`） | E7：description 描述的流程不變，且不寫入流程細節 |
| Phase 1 其餘步驟、Phase 2–4 全部步驟與完成條件 | E7 |
| Phase 5 步驟 1–6 | E7 |
| 五個 RuleFile、兩組樣板 | E7 |
| `scripts/audit_skill.py`、`scripts/next_record_dir.py` | E7 |

## 4. 淨增減

| 項目 | As-Is | To-Be | 增減 |
| ---- | ----- | ----- | ---- |
| Phase | 5 | 5 | 0 |
| 步驟 | 43 | 45 | +2 |
| RuleFile | 5 | 5 | 0 |
| Rule | 24 | 24 | 0 |
| 樣板組 | 2 | 2 | 0 |
| 腳本 | 2 | 3 | +1 |

淨增加的理由：R1 屬於缺失類型，「Skill 要給哪些 agent 使用」沒有表達在任何既有部位中，沒有可刪除、改寫或改換存放位置的內容能處理它；新增的兩個步驟與一個腳本都對應 E2–E6。

## 5. 約束分配表

| 編號 | 約束 | 所屬步驟 | 存放位置 | 理由 |
| ---- | ---- | -------- | -------- | ---- |
| C1 | 新建 Skill 的來源一律在 `.agents/skills` | P1-2 | 步驟內文 | 一句話即可完整表達，不需要正反例；不是可由程式完成的工作 |
| C2 | 依是否安裝 Claude Code 建立或略過 symlink，並自動建立 `.claude/skills/` | P5-7 | `scripts/sync_agent_links.py` | 輸入輸出明確、每次施工都要重複執行，結果可由程式判斷 |
| C3 | 同名實體目錄與外部 symlink 保持不變並記錄 | P5-7 | `scripts/sync_agent_links.py` | 同上 |
| C4 | 移除指向 `.agents/skills` 的失效 symlink | P5-7 | `scripts/sync_agent_links.py` | 同上 |
| C5 | 只存在 `.claude/skills/` 的模組化實體目錄只記錄為移轉建議 | P5-7 | `scripts/sync_agent_links.py` | 以 SKILL.md 是否含 `# SOP` 判斷，可由程式完成 |
| C6 | 不修改檔案的檢查模式 | 無（供使用者或其他流程手動執行） | `scripts/sync_agent_links.py` 的 `--check` | 與 C2–C5 共用同一套判斷，放在同一腳本可避免重複實作 |
| C7 | 向使用者回報並存、衝突與移轉建議 | P5-14 | 步驟內文 | 屬於回報流程，一句話即可表達 |

## 6. 施工工作項

| 順序 | 工作項 | 執行者 | 目標 | 內容 | 約束 | 狀態 |
| ---- | ------ | ------ | ---- | ---- | ---- | ---- |
| 1 | W1 | `skill-form-sop` | `skill-engineering/SKILL.md` | 寫入胖 SOP：修改 P1-2、在 Phase 5 插入待抽取的連結同步步驟與檢查步驟、修改最後的回報步驟與完成條件 | C1、C2–C5、C7 | 已完成 |
| 2 | W2 | `skill-derive-script` | Phase 5 -- 施工與驗收的 `WRITE` 連結同步步驟 | 抽出 `scripts/sync_agent_links.py`，並把該步驟與下一個 `CHECK` 改為 To-Be SOP 的 P5-7、P5-8 | C2–C6 | 已完成 |

### 工作項內容

#### W1：胖 SOP

以現行 `SKILL.md` 為基礎，只做以下修改，其餘內文保留原文：

- Phase 1 步驟 2 改為 To-Be SOP 的 P1-2 全文。
- Phase 5 在原步驟 6 之後插入以下兩個步驟（待 W2 抽取），原步驟 7–12 依序改為 9–14：

```markdown
7. `WRITE` 這台電腦安裝了 Claude Code（環境變數 `CLAUDE_CONFIG_DIR` 指向的目錄或 `~/.claude` 存在）時，為專案 `.agents/skills` 中的每個 Skill 在專案的 `.claude/skills/` 建立同名、以相對路徑指向來源的 symlink，`.claude/skills/` 不存在時先建立；已有同名實體目錄或指向其他位置的 symlink 時保持不變並記錄為並存或衝突；移除指向 `.agents/skills` 但來源已不存在的 symlink；只存在於 `.claude/skills/` 且含 `# SOP` 的實體目錄記錄為移轉建議；沒有安裝 Claude Code 時不建立任何目錄或 symlink；全程不詢問使用者，建立「連結同步結果」。
8. `CHECK` 「連結同步結果」中的每個 `.agents/skills` Skill 均已連結、並存或記錄為衝突，且沒有殘留失效的 symlink；未通過時修正後重新執行上一步。
```

- Phase 5 步驟 14 與完成條件改為 To-Be SOP 的全文。

#### W2：`scripts/sync_agent_links.py`

- 命令：`uv run --script scripts/sync_agent_links.py --project-root <專案根目錄絕對路徑> [--check]`，在 skill-engineering 目錄執行。
- Python：`>=3.11`；`dependencies = []`。
- 偵測：環境變數 `CLAUDE_CONFIG_DIR` 有值時以該目錄是否存在判斷，否則以 `~/.claude` 是否存在判斷。
- 來源：`<專案根目錄>/.agents/skills/` 下含 `SKILL.md` 的子目錄；來源目錄不存在時視為沒有 Skill。
- 沒有安裝 Claude Code：不建立、不修改任何檔案，輸出 `claude_code: "not_installed"`，退出狀態 0。
- 已安裝時，依 `.claude/skills/<name>` 的現況處理：

| 現況 | 一般模式 | `--check` |
| ---- | -------- | --------- |
| `.claude/skills/` 不存在 | 建立目錄 | 記錄為缺漏 |
| 不存在 | 建立相對路徑 symlink（`../../.agents/skills/<name>`） | 記錄為缺漏 |
| 已是指向來源的 symlink | 不動，記錄為正常 | 同左 |
| 實體目錄 | 不動，記錄為並存 | 同左 |
| 指向其他位置的 symlink | 不動，記錄為衝突 | 同左 |

- 失效連結：`.claude/skills/` 中指向 `.agents/skills` 但來源不存在的 symlink，一般模式刪除並記錄，`--check` 只記錄。
- 移轉建議：`.claude/skills/` 中名稱不在 `.agents/skills`、為實體目錄且 `SKILL.md` 含 `# SOP` 行的 Skill，只記錄。
- 輸出：JSON 欄位 `claude_code`、`claude_config_dir`、`skills_dir_created`、`created`、`ok`、`removed`、`coexisting`、`conflicts`、`migration_suggestions`、`missing`、`dangling`。
- 退出狀態：成功為 0；`--check` 發現缺漏或失效連結為 1；建立或刪除 symlink 失敗時在標準錯誤輸出指出原因並以 1 結束；參數無效為 2。
- 副作用：只建立 `.claude/skills/` 目錄、建立 symlink、刪除指向 `.agents/skills` 的失效 symlink；不修改任何實體目錄或指向其他位置的 symlink；不使用網路。

## 7. 驗收情境

| 編號 | 驗證 | 類型 | 輸入 | 預先回覆 | 判斷方式 |
| ---- | ---- | ---- | ---- | -------- | -------- |
| S1 | E1、E2、E3、E4、E5、E7 | 本次 | 暫存專案複本（這台電腦已安裝 Claude Code），`.claude/skills/` 另外放入：指向 `../../.agents/skills/old-skill` 的失效 symlink、指向暫存目錄外部的 symlink `ext-tool`、只存在此處且含 `# SOP` 的實體目錄 `legacy-notes`。需求：「建立一個 Skill `todo-harvester`：掃描指定目錄中的 TODO 與 FIXME 註解，整理成 Markdown 清單寫入 `docs/todo.md`，寫入前先讓使用者確認。」（需求不提及存放目錄） | Phase 4 回覆「確認」 | 新 Skill 的實體目錄在 `.agents/skills/todo-harvester/`；`.claude/skills/todo-harvester` 是指向它的相對 symlink；`old-skill` 已刪除；`skill-creator`、`ext-tool`、`legacy-notes` 未被修改，且回報中列為並存、衝突或移轉建議；過程中沒有詢問連結相關問題 |
| S2 | E2、E6 | 本次 | 同一份暫存專案複本的另一份，刪除 `.claude/skills/` 中兩個 symlink；分別以 `CLAUDE_CONFIG_DIR` 指向不存在的目錄執行一般模式，以及以實際安裝狀態執行 `--check` | 無 | 未安裝時沒有建立或修改任何檔案且退出狀態 0；`--check` 列出兩個缺漏、退出狀態 1，且檔案未被修改 |

## 8. 驗收結果

- 施工後結構診斷：`skill-engineering` 為 0 個 error、0 個 warning；新腳本只由 Phase 5 步驟 7 執行，沒有孤兒部位。
- 腳本自測（`skill-form-script`）：建立、正常、並存、同名衝突、失效連結刪除、移轉建議、非模組化實體目錄略過、未安裝不動作、`--check` 不修改且缺漏時退出 1、重複執行不變、無效專案根目錄退出 2、無法寫入時退出 1，全部符合設計。
- 真實專案同步：`claude_code` 為 installed；10 個模組化 Skill 為 ok，`skill-creator` 為並存；沒有建立或刪除任何連結。
- 測試環境修正：S1 原描述以名稱不同的 `ext-tool` 驗證 E3，但 E3 只涵蓋同名項目，情境描述與驗收條件不一致；改為另外加入同名的外部連結 `skill-form-rule -> /tmp`，並保留 `ext-tool` 驗證「不相關的連結不被修改」。
- S1 通過（在暫存專案複本中以不帶分析脈絡的子代理實際執行）：需求未提及目錄，新 Skill 仍寫在 `.agents/skills/todo-harvester/`；`.claude/skills/todo-harvester` 為相對 symlink；`old-skill` 失效連結已刪除；`skill-creator`（並存）、`skill-form-rule`（衝突）、`ext-tool`、`legacy-notes`（移轉建議）均未修改，且並存、衝突與移轉建議都出現在最後的回報中；過程中沒有詢問連結相關問題；Phase 4 閘門與實跑驗收流程照常進行。
- S2 通過（以子代理實際執行腳本）：`CLAUDE_CONFIG_DIR` 指向不存在的目錄時回報 not_installed、退出 0，沒有任何檔案變動；以實際安裝狀態執行 `--check` 時列出 `skill-derive-rule` 與 `skill-form-sop` 兩個缺漏、退出 1，沒有任何檔案變動。
- 個案驗收條件：無。
