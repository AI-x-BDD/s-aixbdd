# 工程藍圖：skill-form-rule－RuleFile重述其他部位

- 模式：優化
- 紀錄目錄：`specs/skill-engineering/07-skill-form-rule-RuleFile重述其他部位/`
- 根因報告：同一紀錄目錄的 `rca-report.md`；使用者已同意建立第二道關卡（「都依照建議」）
- 施工差異：2026-09-25 施工 W1 時，新版 `skill-form-sop` 讀取 `RuleFile-格式規範` 後，檢查出 `skill-form-rule` P1-3「確定每個 RuleFile 的單一主題與必要 Rule」重述 Rule 2（一個 RuleFile 只處理一個主題）的判準；停止施工，W1、W2 維持「待施工」，返回 Phase 3；重新設計為 W1 一併修改 P1-3，2026-09-25 使用者回覆「確認」
- 確認紀錄：2026-09-25 使用者於 Phase 4 回覆「確認」：同意施工工作項 W1、W2、施工順序（07 → 05 第二輪），以及既有驗收條件 E2–E4

## 1. 驗收條件

| 編號 | 驗收條件 | 來源 | 適用範圍 |
| ---- | -------- | ---- | -------- |
| E1 | `skill-form-rule` 寫入或修改 RuleFile 後，目標 RuleFile 的 Rule 不重述同一個 Skill 其他 RuleFile、樣板組、腳本或 SOP 步驟內文已規範的要求；呼叫者提供的已確認設計含有重述時，向呼叫者回報差異並停止 | 本次 | 通用 |
| E2 | Rule 仍在本檔內完整說明自己的核心要求，只以引用補充共用定義 | 既有 | 通用 |
| E3 | RuleFile 其餘格式要求不受影響：固定結構、單一主題、強度用詞、範例格式 | 既有 | 通用 |
| E4 | 被 `skill-derive-rule`、`skill-engineering` 委派時，依呼叫者已確認的設計寫入，不另行設計 | 既有 | 通用 |

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
3. `THINK` 依已載入的完成檢查清單，確定每個 RuleFile 的主題與 Rule 清單；呼叫者提供已確認的設計（例如工程藍圖的工作項內容，或 skill-derive-* 的已確認提案）時，以該設計為內容，不另行設計，該設計不符合完成檢查清單時向呼叫者回報差異並停止。

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
| 無 | — | 依 `重新設計` Rule 2 逐一檢查 As-Is，沒有無法追溯或重複存放的元素 |

### 修改、合併、改換存放位置與新增

| 元素 | 動作 | 內容 | 追溯 |
| ---- | ---- | ---- | ---- |
| P1-1 | 修改 | 讀取範圍加上「其 SOP 載入的其他 RuleFile 與樣板組、其 SOP 委派之腳本的介面說明」 | R2、E1（C2） |
| P1-3 | 修改 | 「確定每個 RuleFile 的單一主題與必要 Rule」改為「確定每個 RuleFile 的主題與 Rule 清單」（施工差異） | 「單一主題」重述 `RuleFile-格式規範` Rule 2（C3） |
| `rules/RuleFile-格式規範.md` Rule 3 | 修改 | 標題改為「跨部位引用只能補充本地規則，不得重述」；第 1 條的引用對象加上樣板組與腳本；新增第 4 條「Rule 不得重述同一個 Skill 其他 RuleFile、樣板組、腳本或 SOP 步驟內文已規範的要求。」；正反範例各加 Example 2：RuleFile 只規範樣板無法保證的判準，以及 RuleFile 重述樣板骨架的段落結構 | R1、E1、E2（C1） |

### 保留

| 元素 | 追溯 | 約束 |
| ---- | ---- | ---- |
| frontmatter | E3、E4：description 的觸發與分流不受影響 | 無（只概述用途與觸發情境） |
| P1-2、Phase 2 的步驟與兩個 Phase 的完成條件 | E3、E4；P1-3 已規定以呼叫者的設計為內容，不符合時回報差異並停止 | 無（只載入、依設計寫入與驗證） |
| `rules/RuleFile-格式規範.md` Rule 1、2、4–9 與 Rule 3 第 2、3 條 | E2、E3 | 各 Rule 自己的格式要求，沒有其他存放位置 |

## 4. 淨增減

| 項目 | As-Is | To-Be | 增減 |
| ---- | ----- | ----- | ---- |
| Phase | 2 | 2 | 0 |
| 步驟 | 5 | 5 | 0 |
| RuleFile | 1 | 1 | 0 |
| Rule | 9 | 9 | 0 |
| 樣板組 | 0 | 0 | 0 |
| 腳本 | 0 | 0 | 0 |

- 條列 +1（Rule 3 第 4 條）：R1 是「缺失」。依 `重新設計` Rule 4 的順序考慮：沒有表達這項約束的既有內容可以刪除；第 1 條規範「可以引用什麼」，改寫成同時規範「不得重述」會讓一條承擔兩個要求；這項約束需要判斷語意，無法放在腳本或樣板。
- 範例：Rule 3 正反範例各增加一組。

## 5. 約束分配表

| 編號 | 約束 | 所屬步驟 | 存放位置 | 理由 |
| ---- | ---- | -------- | -------- | ---- |
| C1 | Rule 不得重述同一個 Skill 其他部位已規範的要求 | P2-1、P2-2 | `rules/RuleFile-格式規範.md` Rule 3 | 需要判斷兩段文字是否表達同一要求，腳本無法判斷；不是產出檔的整體結構；需要正反例；屬於跨部位引用的既有主題 |
| C2 | 修改或建立 RuleFile 時，讀取同一個 Skill 的其他部位 | P1-1 | 步驟內文 | 屬於讀取哪些輸入，是控制平面 |
| C3 | 一個 RuleFile 只處理一個主題 | P1-3 | `rules/RuleFile-格式規範.md` Rule 2 | 既有，不變 |

## 6. 施工工作項

| 順序 | 工作項 | 執行者 | 目標 | 內容 | 約束 | 狀態 |
| ---- | ------ | ------ | ---- | ---- | ---- | ---- |
| 1 | W1 | `skill-form-sop` | `skill-form-rule` 的 `SKILL.md` 中 Phase 1 -- 理解與設計讀取使用者需求的 `READ` 步驟與確定主題的 `THINK` 步驟 | 擴大讀取範圍；刪除判準用詞 | C2、C3 | 已完成 |
| 2 | W2 | `skill-form-rule` | `rules/RuleFile-格式規範.md` Rule 3 | 改寫標題、第 1 條，新增第 4 條與 Example 2 | C1 | 已完成 |

### 工作項內容

#### W1：SOP 修改

| 步驟 | 修改後全文 |
| ---- | ---------- |
| Phase 1 -- 理解與設計中讀取使用者需求的 `READ` 步驟 | `READ` 使用者需求、目標 Skill 的 `SKILL.md` 與其 SOP 載入的其他 RuleFile 與樣板組、其 SOP 委派之腳本的介面說明，以及修改既有 RuleFile 時的目標 RuleFile。 |
| Phase 1 -- 理解與設計中確定主題的 `THINK` 步驟 | 「確定每個 RuleFile 的單一主題與必要 Rule」改為「確定每個 RuleFile 的主題與 Rule 清單」，其餘文字不變 |

#### W2：`rules/RuleFile-格式規範.md` Rule 3

完成後全文應與同目錄下的 `W2-RuleFile-格式規範.md` 逐字一致。內容見第 3 節。

## 7. 驗收情境

情境在包含本次未提交修改的暫存專案複本中執行，並在複本的 `.agents/skills/` 下建立測試用的 Skill。

| 編號 | 驗證 | 類型 | 輸入 | 預先回覆 | 判斷方式 |
| ---- | ---- | ---- | ---- | -------- | -------- |
| S1 | E1、E2、E3 | 本次 | 測試用 Skill `invoice-writer`：樣板骨架固定「抬頭、明細、合計」三個區段；`rules/發票內容-格式規範.md` Rule 1 重述「發票必須依序包含抬頭、明細與合計三個區段」，Rule 2 規定金額顯示兩位小數。需求：使用 `skill-form-rule` 在該 RuleFile 新增一條 Rule，規定明細每一列必須有品項編號 | 無 | 新 Rule 已加入；沒有任何 Rule 重述骨架的區段結構；Rule 2 保留；RuleFile 仍符合固定結構、編號連續與範例格式 |
| S2 | E1、E3、E4 | 回歸（呼叫者 `skill-derive-rule`） | 測試用 Skill `meeting-minutes-writer`：樣板骨架固定「決議、待辦」兩段；`WRITE` 步驟內文寫著「會議紀錄必須依序包含決議與待辦兩段；每個待辦必須寫出負責人與期限」。需求：使用 `skill-derive-rule` 為這個 `WRITE` 步驟展開 RuleFile | Before／After 回覆「確認」 | 最後寫入的 RuleFile 不包含「依序包含決議與待辦兩段」；若已確認的提案包含這項要求，`skill-form-rule` 回報差異並停止；抽取後的步驟不殘留已抽取的判準 |
| S3 | E4 | 回歸（呼叫者 `skill-engineering`） | 05 第二輪的 W5、W6 由 `skill-engineering` 委派新版 `skill-form-rule` 施工 | 無 | 施工時 `skill-form-rule` 讀取 `skill-engineering` 的其他 RuleFile、樣板組與腳本介面，依 Rule 3 檢查，寫入結果與 To-Be 逐字一致，或回報差異 |

## 8. 驗收結果

- 施工後結構診斷：`skill-form-rule` 0 個 error、0 個 warning；`SKILL.md`、`rules/RuleFile-格式規範.md` 與 W1、W2 逐字一致。連結同步：10 個連結正常，沒有衝突或缺漏。
- 施工差異：1 次（`skill-form-rule` P1-3 的判準用詞），由新版 `skill-form-sop` 攔下，經使用者確認後併入 W1。
- 驗收方式：S1、S2 在包含本次修改的暫存專案複本（`scratchpad/accept2/`）中，由不帶本次分析脈絡的子代理執行；測試用 Skill 建立在複本內，執行前先提交基準。
- S1 通過（E1–E3）：子代理在 P1-1 讀取了 `invoice-writer` 的樣板組，依新的 Rule 3 第 4 條刪除重述骨架三個區段的舊 Rule 1；「金額兩位小數」保留並改為 Rule 1；新增的品項編號 Rule 通過 9 項格式檢查；只修改目標 RuleFile。子代理另外指出樣板範例的明細列沒有品項編號、與新 Rule 衝突，並說明修改樣板屬於 `skill-form-template`，沒有自行修改。
- S2 通過（E1、E3、E4；呼叫者 `skill-derive-rule`）：最後寫入的 RuleFile 不包含樣板已固定的段落順序。第一版 After 把段落順序留在步驟內文，由 `skill-form-sop` 依 `SOP-格式規範` Rule 4 回報差異並停止；修正後重新確認才寫入。`skill-form-rule` 依已確認的提案寫入，沒有差異。
- S3 通過（E4；呼叫者 `skill-engineering`）：05 第二輪的 W5、W6 由新版 `skill-form-rule` 施工；它讀取了 `skill-engineering` 的其他 RuleFile、樣板組與腳本介面，依 Rule 3 檢查後沒有差異，寫入結果與 To-Be 逐字一致。
- 觀察（既有，與本次修改無關）：`skill-derive-rule` 的 DELEGATE 步驟被下游回報差異時，SOP 沒有規定返回 Phase 2 或停止；它的 Phase 1 看不到 SOP 格式規範，要到委派寫入時才發現重述。
- 真實專案副作用：沒有。
