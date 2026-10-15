# 根因報告：skill-form-rule－Rule5與SOP按需載入規範重複不一致

- 紀錄目錄：`specs/skill-engineering/11-skill-form-rule-Rule5與SOP按需載入規範重複不一致/`
- 問題證據：本次對話中對《AI x BDD》第二章第 7 單元「Skill 極速開發：如何展開有充分 Examples 的 Rule File？」的唯讀審查發現 F11（課程依據：20:01 Rule File 只在實際讀取的步驟點名；27:20 不應有專門 Read 的 Phase；22:19–23:46 按需載入規範由 skill-form-sop 的 RuleFile 把關）；`skill-form-rule` 的 `SKILL.md` 與 `rules/RuleFile-格式規範.md` Rule 5；`skill-form-sop` 的 `rules/SOP-按需載入-格式規範.md` Rule 1、Rule 2。沒有實際執行失敗的對話紀錄或產出物，落差只由檔案內容證明。
- 確認紀錄：使用者在終端看過 F11 的檔案證據、原因、影響、驗收與保留行為，以及最小修改前後片段後，回覆「① ② 都依建議修改」，並補充 ① 改為獨立的 `READ` 步驟。本報告是在該確認之後，依確認內容整理寫成；使用者沒有看過本檔案本身。

## 1. 使用者回報的問題

`skill-form-rule` 的 `RuleFile-格式規範` Rule 5 以 7 條條列重述了 `skill-form-sop` 的 `SOP-按需載入-格式規範` 已規範的載入步驟寫法，而且兩者不一致：Rule 5 要求每個 `READ` 步驟都寫出適用條件，也沒有禁止讀取專用 Phase，或要求 `READ` 與第一個依賴步驟在同一個 Phase 且相鄰。`skill-form-rule` 的 Phase 2 寫入步驟在呼叫者沒有負責時會更新目標 `SKILL.md` 的載入步驟，此時只依 Rule 5 檢查。使用者要求同一條規範只有一個來源。

## 2. 驗收條件

| 編號 | 驗收條件 | 來源 | 適用範圍 | 驗收情境 |
| ---- | -------- | ---- | -------- | -------- |
| E1 | `rules/RuleFile-格式規範.md` Rule 5 只保留本地核心要求（以 `READ` 步驟按需載入 RuleFile，且只載入當前任務需要的 RuleFile），載入步驟的提名位置、適用條件與載入結果命名改為引用 `skill-form-sop` 的 `rules/SOP-按需載入-格式規範.md`，不再重述其條文 | 本次 | 通用 | S4 |
| E2 | `skill-form-rule` 需要更新目標 `SKILL.md` 的載入步驟時，在寫入前讀取 `skill-form-sop` 的 `rules/SOP-按需載入-格式規範.md` 的所有 Rule 並納入完成檢查清單；寫出的載入步驟沒有讀取專用 Phase，`READ` 與第一個依賴步驟位於同一個 Phase 且之間只有其他 `READ`，RuleFile 路徑只出現在該 `READ` 步驟 | 本次 | 通用 | S1 |
| E3 | 以修改後的 Rule 5 與 `SOP-按需載入-格式規範` 檢查 `skill-form-rule` 與 `skill-derive-rule` 的 `SKILL.md`，兩者都通過，且兩份規範的判定不互相矛盾 | 本次 | 通用 | S4 |
| E4 | RuleFile 其餘格式要求與 Rule 5 的標題、Good／Bad Example 不變，`RuleFile-格式規範.md` 仍符合 Rule 1、8、9 | 既有 | 通用 | S1、S4 |
| E5 | 被 `skill-derive-rule`、`skill-engineering` 委派時，依呼叫者已確認的設計寫入，不另行設計；呼叫者負責更新目標 `SKILL.md` 時，不自行更新載入步驟 | 既有 | 通用 | S2、S3 |
| E6 | Skill 名稱、`description`、委派介面與確認點不變，`skill-form-sop` 不修改 | 既有 | 通用 | S4 |

## 3. 落差

| 驗收條件 | 預期 | 實際 | 證據 |
| -------- | ---- | ---- | ---- |
| E1 | Rule 5 不重述 `SOP-按需載入-格式規範` | Rule 5 第 2–4、6–7 條與 `SOP-按需載入` Rule 1 第 1、4、5、7 條及 Rule 2 表達同一組要求，且第 3、4 條的判準不同 | 觀察：`RuleFile-格式規範.md:151-156`；`SOP-按需載入-格式規範.md:3,6,7,9,46,48` |
| E2 | 更新載入步驟前已載入 `SOP-按需載入-格式規範` | `SKILL.md` Phase 1 只載入 `rules/RuleFile-格式規範.md` | 觀察：`skill-form-rule/SKILL.md:11,18` |
| E3 | 兩份規範對同一個 SOP 判定一致 | `skill-form-rule/SKILL.md:11` 是必定載入、沒有寫條件的 `READ`：依 Rule 5 第 3 條（`:152`）為不符合，依 `SOP-按需載入` Rule 1 第 4 條（`:6`）為符合 | 觀察：同上兩處 |

## 4. 演練表

`skill-form-rule`（情境：使用者直接使用本 Skill 為某個 Skill 撰寫 RuleFile，且呼叫者沒有負責更新目標 `SKILL.md`。沒有實際執行紀錄，「實際載入」依步驟內文觀察，「實際產出」無證據）：

| 步驟 | 應載入 | 實際載入 | 應產出 | 實際產出 | 判定 |
| ---- | ------ | -------- | ------ | -------- | ---- |
| P1-1 | 使用者需求、目標 `SKILL.md` 與其部位 | 觀察：步驟內文 `SKILL.md:10` 涵蓋 | 目標現況 | 無證據 | 一致 |
| P1-2 | 單一來源、與 `skill-form-sop` 一致的載入步驟判準 | 觀察：載入 Rule 5，其中 `:152-153` 與 `SOP-按需載入:6-8` 不一致，且其餘條列重述該檔 | 完成檢查清單 | 觀察：完成檢查清單包含與 `SOP-按需載入` 衝突的條文 | 偏離 |
| P1-3 | 完成檢查清單 | 觀察：已使用 | Rule 清單 | 無證據 | 無證據 |
| P2-1 | 完成檢查清單 | 觀察：已使用 | 符合 `SOP-按需載入` 的載入步驟 | 無證據（推論：可能寫出讀取專用 Phase 或不相鄰的 `READ`，依據 P1-2 的觀察） | 無證據 |
| P2-2 | 完成檢查清單 | 觀察：已使用 | 能攔下不符合 `SOP-按需載入` 的載入步驟 | 推論：清單沒有讀取專用 Phase 與相鄰的判準，無法攔下（依據 P1-2 的觀察） | 無證據 |

第一個偏離點：P1-2。

## 5. 根因

| 編號 | 位置 | 缺陷類型 | 說明與證據 | 反事實檢驗 |
| ---- | ---- | -------- | ---------- | ---------- |
| R1 | `skill-form-rule`／`rules/RuleFile-格式規範.md`／Rule 5 | 衝突 | 觀察：同一組載入步驟約束同時存放於 Rule 5（`:151-156`）與 `skill-form-sop` 的 `SOP-按需載入-格式規範` Rule 1、2，且 `:152-153` 與 `:6-8` 的判準不一致 | 只改正 R1：Rule 5 改為引用後，P1-2 的完成檢查清單只有引用、沒有判準，P2-2 無法檢查 E2；需與 R2 一起改正 |
| R2 | `skill-form-rule`／`SKILL.md`／Phase 1 -- 理解與設計 | 未載入 | 觀察：P2-1（`:18`）會更新目標 `SKILL.md` 的載入步驟，但 Phase 1 沒有任何步驟載入 `SOP-按需載入-格式規範`（`:10-12`） | R1、R2 一起改正：P1 依條件載入 `SOP-按需載入` 補入完成檢查清單，P2-1 依同一來源寫載入步驟，P2-2 可檢查讀取專用 Phase 與相鄰位置，E1–E3 可滿足 |

## 6. 被排除的假設

| 假設 | 缺陷類型 | 排除依據 |
| ---- | -------- | -------- |
| H1：上游沒有把 SOP 載入步驟交給 `skill-form-sop` | 交接缺陷 | 觀察：`skill-derive-rule/SKILL.md:31` 已委派 `skill-form-sop` 更新載入步驟；問題只出現在 `skill-form-rule` 自己更新載入步驟的情況（`SKILL.md:18`） |
| H2：`description` 與 P2-1 的分流邊界不一致，導致不該由本 Skill 處理的任務進入 | 觸發缺陷 | 推論：沒有觀察到錯誤觸發的紀錄；此項是審查中的 F12，使用者決定本次排除，不能作為本次根因 |
| H3：落差來自模型能力或個案輸入 | 非 Skill 問題 | 觀察：不一致存在於 Skill 檔案本身（`RuleFile-格式規範.md:152-153`），與執行的模型和輸入無關 |

## 7. 影響範圍

依結構診斷，直接委派 `skill-form-rule` 的 Skill 有 `skill-derive-rule` 與 `skill-engineering`；間接呼叫者為委派 `skill-derive-rule` 的 `skill-engineering`。

## 8. 待確認事項

1. 第 2 節的驗收條件是否正確、完整？E1–E3 對應終端展示的驗收項目，E4–E6 對應展示的保留行為。
2. 是否同意第 5 節的根因 R1、R2？
3. 仍缺少的證據：沒有實際執行失敗的紀錄，P2-1、P2-2 的實際產出為無證據；本次由驗收情境 S1 取得行為證據。
