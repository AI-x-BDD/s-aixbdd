# 工程藍圖：skill-form-rule－Rule5與SOP按需載入規範重複不一致

- 模式：優化
- 紀錄目錄：`specs/skill-engineering/11-skill-form-rule-Rule5與SOP按需載入規範重複不一致/`
- 根因報告：同一紀錄目錄的 `rca-report.md`。根因 R1、R2 與驗收條件的確認依據，是使用者在終端看過 F11 證據、原因、驗收、保留行為與最小修改前後片段後回覆「① ② 都依建議修改」；`rca-report.md` 與本藍圖都是在該回覆之後寫成，使用者尚未看過這兩份檔案
- 確認紀錄：2026-10-15 使用者看過本藍圖的白話說明後，於 Phase 4 回覆「ok，開始執行」：確認驗收條件 E1–E6、To-Be（① 拆開的 P1-3、② Rule 5 引用版）、施工工作項 W1、W2 與驗收情境 S1–S4；沒有推定驗收條件

## 1. 驗收條件

| 編號 | 驗收條件 | 來源 | 適用範圍 |
| ---- | -------- | ---- | -------- |
| E1 | `rules/RuleFile-格式規範.md` Rule 5 只保留本地核心要求（以 `READ` 步驟按需載入 RuleFile，且只載入當前任務需要的 RuleFile），載入步驟的提名位置、適用條件與載入結果命名改為引用 `skill-form-sop` 的 `rules/SOP-按需載入-格式規範.md`，不再重述其條文 | 本次 | 通用 |
| E2 | `skill-form-rule` 需要更新目標 `SKILL.md` 的載入步驟時，在寫入前讀取 `skill-form-sop` 的 `rules/SOP-按需載入-格式規範.md` 的所有 Rule 並納入完成檢查清單；寫出的載入步驟沒有讀取專用 Phase，`READ` 與第一個依賴步驟位於同一個 Phase 且之間只有其他 `READ`，RuleFile 路徑只出現在該 `READ` 步驟 | 本次 | 通用 |
| E3 | 以修改後的 Rule 5 與 `SOP-按需載入-格式規範` 檢查 `skill-form-rule` 與 `skill-derive-rule` 的 `SKILL.md`，兩者都通過，且兩份規範的判定不互相矛盾 | 本次 | 通用 |
| E4 | RuleFile 其餘格式要求與 Rule 5 的標題、Good／Bad Example 不變，`RuleFile-格式規範.md` 仍符合 Rule 1、8、9 | 既有 | 通用 |
| E5 | 被 `skill-derive-rule`、`skill-engineering` 委派時，依呼叫者已確認的設計寫入，不另行設計；呼叫者負責更新目標 `SKILL.md` 時，不自行更新載入步驟 | 既有 | 通用 |
| E6 | Skill 名稱、`description`、委派介面與確認點不變，`skill-form-sop` 不修改 | 既有 | 通用 |

## 2. To-Be SOP

````markdown
---
name: skill-form-rule
description: 撰寫或修改 Skill 之 rules/ 底下的 RuleFile（條列規則加正反範例）內容時，必須使用此 Skill；使用者提到 rule file、規則檔、格式規範時使用。要為某個 SOP 步驟新增規則並掛上載入步驟時，改用 skill-derive-rule。
---

# SOP

## Phase 1 -- 理解與設計

1. `READ` 使用者需求、目標 Skill 的 `SKILL.md` 與其 SOP 載入的其他 RuleFile 與樣板組、其 SOP 委派之腳本的介面說明，以及修改既有 RuleFile 時的目標 RuleFile。
2. `READ` `rules/RuleFile-格式規範.md` 的所有 Rule，建立完成檢查清單。
3. `READ` 需要更新目標 `SKILL.md` 的載入步驟時，讀取 `../skill-form-sop/rules/SOP-按需載入-格式規範.md` 的所有 Rule，補入完成檢查清單。
4. `THINK` 依已載入的完成檢查清單，確定每個 RuleFile 的主題與 Rule 清單；呼叫者提供已確認的設計（例如工程藍圖的工作項內容，或 skill-derive-* 的已確認提案）時，以該設計為內容，不另行設計，該設計不符合完成檢查清單時向呼叫者回報差異並停止。

完成條件：已確定目標檔案與 Rule 清單。

## Phase 2 -- 寫入與驗證

1. `WRITE` 依已載入的完成檢查清單修改目標 RuleFile；呼叫者沒有負責更新目標 `SKILL.md` 時，一併更新其中載入該 RuleFile 的步驟。
2. `CHECK` 逐條驗證完成檢查清單；若有任一項未通過，修正後重新檢查。

完成條件：所有檢查項目均已通過。
````

## 3. 差異表

### 刪除

| 元素 | 位置 | 理由 |
| ---- | ---- | ---- |
| Rule 5 第 1–4、6–7 條 | `rules/RuleFile-格式規範.md:150-153,155-156` | R1（衝突）：與 `skill-form-sop` 的 `SOP-按需載入-格式規範` Rule 1、2 重複存放或判準不一致；依 `重新設計` Rule 3 只保留一個來源（併入下列 Rule 5 改寫） |

### 修改、合併、改換存放位置與新增

| 元素 | 動作 | 內容 | 追溯 |
| ---- | ---- | ---- | ---- |
| `rules/RuleFile-格式規範.md` Rule 5 條列 | 修改 | 七條換成兩條：本地核心「必須以 `READ` 步驟按需載入 RuleFile，且只載入當前任務需要的 RuleFile」，以及引用 `skill-form-sop` 的 `rules/SOP-按需載入-格式規範.md`；標題與 Good／Bad Example 不變 | R1、E1、E3、E4（C2、C3） |
| Phase 1 -- 理解與設計 新增 `READ` 步驟 3 | 新增 | 需要更新目標 `SKILL.md` 的載入步驟時，讀取 `../skill-form-sop/rules/SOP-按需載入-格式規範.md` 的所有 Rule，補入完成檢查清單 | R2、E2（C4） |
| Phase 1 原步驟 3 `THINK` | 重新編號為 4 | 內容不變 | E5 |

### 保留

| 元素 | 追溯 | 約束 |
| ---- | ---- | ---- |
| frontmatter | E6 | 無（只概述用途與分流） |
| P1-1、P1-2、P1-4（原 P1-3）、P2-1、P2-2 與兩個 Phase 的完成條件 | E2、E5、E6 | C1、C5、C6 |
| Rule 1–4、6–9 | E4 | 各 Rule 自己的格式要求（C7） |
| Rule 5 標題與 Good／Bad Example | E4 | 示範 C2 |

## 4. 淨增減

| 項目 | As-Is | To-Be | 增減 |
| ---- | ----- | ----- | ---- |
| Phase | 2 | 2 | 0 |
| 步驟 | 5 | 6 | +1 |
| RuleFile | 1 | 1 | 0 |
| Rule | 9 | 9 | 0 |
| 樣板組 | 0 | 0 | 0 |
| 腳本 | 0 | 0 | 0 |

- 步驟 +1（P1-3）：對應 R2（未載入）與 E2。依 `重新設計` Rule 4 的順序考慮：沒有可刪除的既有內容能表達這項載入；改寫 P1-2 在同一個 `READ` 步驟讀兩份檔案也能處理（`SOP-按需載入` Rule 1 允許同一步驟載入多個參考檔），使用者明確選擇拆成獨立步驟，讓適用條件只屬於該檔案、較清楚；這不是課程的硬性規定。
- Rule 5 條列 7 → 2，淨減 5 條。

## 5. 約束分配表

| 編號 | 約束 | 所屬步驟 | 存放位置 | 理由 |
| ---- | ---- | -------- | -------- | ---- |
| C1 | 修改或建立 RuleFile 前讀取目標 Skill 的 `SKILL.md`、其他部位與目標 RuleFile | P1-1 | 步驟內文 | 讀取哪些輸入，屬於控制平面 |
| C2 | 擁有 RuleFile 的 `SKILL.md` 必須以 `READ` 步驟按需載入，且只載入當前任務需要的 RuleFile | P2-1、P2-2 | `rules/RuleFile-格式規範.md` Rule 5 | 需要判斷且有正反例；`SOP-按需載入` 沒有表達「只載入當前任務需要的 RuleFile」 |
| C3 | 載入步驟的提名位置、適用條件與載入結果命名 | P2-1、P2-2 | `skill-form-sop` 的 `rules/SOP-按需載入-格式規範.md` Rule 1、2 | 既有單一來源；本 Skill 只引用，不重述 |
| C4 | 需要更新目標 `SKILL.md` 的載入步驟時才載入 C3 | P1-3 | 步驟內文 | 屬於載入條件與執行順序 |
| C5 | 呼叫者提供已確認設計時不另行設計，不符合時回報並停止 | P1-4 | 步驟內文 | 分支與停止位置 |
| C6 | 呼叫者沒有負責更新目標 `SKILL.md` 時一併更新載入步驟 | P2-1 | 步驟內文 | 分支 |
| C7 | RuleFile 的結構、主題、引用、檔名語言、規則說明、強度用詞、範例格式與正反範例 | P2-1、P2-2 | `rules/RuleFile-格式規範.md` Rule 1–4、6–9 | 既有，不變 |

## 6. 施工工作項

| 順序 | 工作項 | 執行者 | 目標 | 內容 | 約束 | 狀態 |
| ---- | ------ | ------ | ---- | ---- | ---- | ---- |
| 1 | W1 | `skill-form-sop` | `skill-form-rule` 的 `SKILL.md` 中 Phase 1 -- 理解與設計，讀取 `rules/RuleFile-格式規範.md` 的 `READ` 步驟之後 | 新增條件式 `READ` 步驟，原 `THINK` 步驟重新編號 | C4 | 已完成 |
| 2 | W2 | `skill-form-rule` | `rules/RuleFile-格式規範.md` Rule 5 條列 | 七條換成兩條 | C2、C3 | 已完成 |

- 執行者依據：`施工委派` Rule 1。W1 屬於「建立或修改 SOP」；新增載入的是 `skill-form-sop` 既有的 RuleFile，不是 `skill-form-rule` 的部位，因此不屬於「新增部位，或改變部位的載入步驟」。W2 屬於「修改既有部位內容，不改變載入步驟」。順序依 `施工委派` Rule 3：胖 SOP 在修改既有部位內容之前。

### 工作項內容

#### W1：SOP 修改

| 步驟 | 修改後全文 |
| ---- | ---------- |
| Phase 1 -- 理解與設計，緊接讀取 `rules/RuleFile-格式規範.md` 的 `READ` 步驟之後新增 | `READ` 需要更新目標 `SKILL.md` 的載入步驟時，讀取 `../skill-form-sop/rules/SOP-按需載入-格式規範.md` 的所有 Rule，補入完成檢查清單。 |
| Phase 1 -- 理解與設計中確定主題的 `THINK` 步驟 | 編號由 3 改為 4，內文不變 |

#### W2：`rules/RuleFile-格式規範.md` Rule 5 條列

修改前（`:150-156`）：

```markdown
- 擁有 RuleFile 的 `SKILL.md` 必須指定 RuleFile 的相對路徑。
- RuleFile 的路徑必須只出現在實際讀取該檔案的 `READ` 步驟。
- `READ` 步驟必須指定適用的任務或條件。
- `READ` 步驟必須在確認 RuleFile 適用後，且在第一個依賴該 RuleFile 的 `THINK`、`WRITE` 或 `CHECK` 步驟之前執行。
- 擁有多個 RuleFile 時，`SKILL.md` 必須只載入當前任務需要的 RuleFile。
- `READ` 步驟必須讀取適用 RuleFile 的所有 Rule，並為載入結果指定明確名稱。
- 後續步驟必須使用該名稱引用載入結果，不得重複 RuleFile 的路徑。
```

修改後：

```markdown
- 擁有 RuleFile 的 `SKILL.md` 必須以 `READ` 步驟按需載入 RuleFile，且只載入當前任務需要的 RuleFile。
- 載入步驟的提名位置、適用條件與載入結果命名，依 `skill-form-sop` 的 `rules/SOP-按需載入-格式規範.md`。
```

## 7. 驗收情境

情境在包含本次未提交修改的暫存專案複本中執行，並在複本的 `.agents/skills/` 下建立測試用的 Skill。

| 編號 | 驗證 | 類型 | 輸入 | 預先回覆 | 判斷方式 |
| ---- | ---- | ---- | ---- | -------- | -------- |
| S1 | E2、E4 | 本次 | 測試用 Skill `invoice-checker`：`SKILL.md` 只有 Phase 1（1. `READ` 使用者提供的發票資料；2. `THINK` 判斷發票欄位是否齊全；3. `WRITE` 寫出檢查報告；4. `CHECK` 檢查報告是否列出所有缺漏欄位），沒有 `rules/`。需求：直接使用 `skill-form-rule` 建立 `rules/發票欄位-格式規範.md`，一條 Rule 規定「統一編號必須是 8 位數字」，並由 `skill-form-rule` 自行更新 `SKILL.md` 讓步驟 2 使用此規則 | 無 | 執行紀錄顯示讀取了 `skill-form-sop` 的 `SOP-按需載入-格式規範.md`；新 RuleFile 符合 `RuleFile-格式規範` Rule 1、8、9；`SKILL.md` 沒有讀取專用 Phase，載入該 RuleFile 的 `READ` 與第一個依賴步驟在同一個 Phase 且之間只有 `READ`，路徑只出現在該 `READ` 步驟，載入結果有名稱並被後續步驟引用 |
| S2 | E5 | 回歸（呼叫者 `skill-derive-rule`） | 測試用 Skill `meeting-notes-writer`：`SKILL.md` Phase 1（1. `READ` 會議逐字稿；2. `THINK` 整理決議與待辦；3. `WRITE` 寫出會議紀錄；4. `CHECK` 每個待辦都有負責人）。需求：使用 `skill-derive-rule` 為 `WRITE` 步驟展開規則「每個待辦必須寫出期限」 | Before／After 回覆「確認」 | `skill-form-rule` 只寫入已確認的 RuleFile 與 Rule，沒有自行修改 `SKILL.md`；`SKILL.md` 的載入步驟由 `skill-form-sop` 更新，且符合 `SOP-按需載入-格式規範` |
| S3 | E5 | 回歸（呼叫者 `skill-engineering`） | 本藍圖的 W2 由 `skill-engineering` 委派修改後的 `skill-form-rule` 施工 | 無 | 施工時 `skill-form-rule` 依已確認的 W2 寫入，結果與 W2 修改後全文逐字一致，或回報差異並停止；因呼叫者 `skill-engineering` 負責 SOP，不讀取 `SOP-按需載入-格式規範`，也不修改 `SKILL.md` |
| S4 | E1、E3、E4、E6 | 本次 | 施工後的 `skill-form-rule/SKILL.md`、`rules/RuleFile-格式規範.md`、`skill-derive-rule/SKILL.md` 與 `skill-form-sop` 目錄 | 無 | Rule 5 只有兩條條列，第二條引用 `skill-form-sop` 的檔案，其他條列與 `SOP-按需載入` Rule 1、2 沒有相同要求；以 Rule 5 加 `SOP-按需載入` 檢查兩個 `SKILL.md` 都通過且判定一致；Rule 5 標題與範例、其他 Rule、`description` 與 `skill-form-sop` 都沒有差異 |

## 8. 驗收結果

- 施工後結構診斷：`audit_skill.py` 檢查 `skill-form-rule`、`skill-derive-rule`，0 error、0 warning；`../skill-form-sop/` 路徑不被視為本 Skill 部位，兩側目錄下該路徑都存在。
- 同步：`./scripts/sync-skills.sh --from agents` 與 `--check` 退出狀態皆為 0，結果「兩邊一致」；同步輸出沒有只存在於目標端的 Skill。`git diff --check` 通過。
- To-Be 比對：`SKILL.md` 與第 2 節 To-Be 逐字一致；Rule 5 與 W2 修改後全文一致；`description`、其他 Rule、`skill-form-sop` 均無差異。

| 情境 | 驗收方式 | 結果 | 證據 |
| ---- | -------- | ---- | ---- |
| S1 | 無上下文子代理，於 `/tmp/f11-accept-S1` 複本執行 | 通過 | 子代理執行 P1-3 時讀取了 `skill-form-sop/rules/SOP-按需載入-格式規範.md`；新 RuleFile 符合 Rule 1、8、9；`invoice-checker/SKILL.md` 新增的 `READ` 位於 Phase 1、緊接第一個依賴的 `THINK`，路徑只出現一次，載入結果「發票欄位檢查清單」被後續步驟引用，沒有讀取專用 Phase |
| S2 | 無上下文子代理，於 `/tmp/f11-accept-S2` 複本執行 | 通過 | `skill-form-rule` 因條件不成立未讀取 `SOP-按需載入`，只寫入已確認的 RuleFile，沒有修改 `SKILL.md`；`SKILL.md` 由 `skill-form-sop` 更新，`READ` 與第一個依賴的 `WRITE` 相鄰。附註：`skill-derive-rule` 在提案中自行多加一條 Rule（期限未提及時標示待確認），經預先回覆「確認」後寫入；這屬於上游提案行為，不在本次 E5 判斷範圍 |
| S3 | 逐步演練（本次 W2 施工，由帶分析脈絡的主代理執行，非隔離子代理） | 通過 | W2 由 `skill-form-rule` 依已確認內容寫入，`git diff` 與 W2 修改後全文一致；呼叫者負責 SOP，P1-3 條件不成立未讀取，W2 未修改 `SKILL.md` |
| S4 | 逐步演練（靜態檢查） | 通過 | Rule 5 只剩兩條，第二條引用 `skill-form-sop`；以 Rule 5 加 `SOP-按需載入` 檢查 `skill-form-rule/SKILL.md`（P1-2 必定載入不需條件、P1-3 條件式且與 P1-4 之間只有 `READ`）與 `skill-derive-rule/SKILL.md`（P1-3→P1-4、P3-1→P3-2 相鄰）都通過，原 `:152` 與 `SOP-按需載入:6` 的矛盾已消失 |

- 個案驗收條件：無。
- 限制：S1、S2 只驗證 Skill 文件的寫出結果，沒有實際執行測試 Skill；S3、S4 為演練而非隔離執行。F3、F4、F6、F12 依使用者決定未處理。
