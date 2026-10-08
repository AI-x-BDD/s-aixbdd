# 根因報告：skill-form-rule－RuleFile重述其他部位

- 紀錄目錄：`specs/skill-engineering/07-skill-form-rule-RuleFile重述其他部位/`
- 問題證據：`specs/skill-engineering/03-plan-with-class-diagram-類別圖未標註新增修改刪除/blueprint.md` 第 7-1 節（W5 由 `skill-form-rule` 施工）；`specs/skill-engineering/04-plan-with-class-diagram-規則重複存放/rca-report.md` R5–R8；05 紀錄的 05-S1、05-S2 驗收產出；`skill-form-rule` 的 `SKILL.md` 與 `rules/RuleFile-格式規範.md`
- 確認紀錄：2026-09-25 使用者回覆「都依照建議」，同意比照 06 為 `skill-form-rule` 建立第二道關卡：寫入 RuleFile 時讀取同一個 Skill 的其他部位，條列不得重述其他部位已規範的內容

## 1. 使用者回報的問題

RuleFile 的條列重述了樣板組、其他 RuleFile 或腳本已經規範的內容，例如 `類別圖輸出` Rule 1 重述樣板骨架的結構、Rule 6 列舉圖例的標記。步驟層級的重述已經由 06 的 `skill-form-sop` 在寫入時攔截，但 RuleFile 層級沒有對應的關卡；`skill-derive-rule` 或直接使用 `skill-form-rule` 修改 RuleFile 時，也不會經過 `skill-engineering` 的設計檢查。

## 2. 驗收條件

| 編號 | 驗收條件 | 來源 | 適用範圍 | 驗收情境 |
| ---- | -------- | ---- | -------- | -------- |
| E1 | `skill-form-rule` 寫入或修改 RuleFile 後，目標 RuleFile 的 Rule 不重述同一個 Skill 其他 RuleFile、樣板組、腳本或 SOP 步驟內文已規範的要求；呼叫者提供的已確認設計含有重述時，向呼叫者回報差異並停止 | 本次 | 通用 | S1、S2 |
| E2 | Rule 仍在本檔內完整說明自己的核心要求，只以引用補充共用定義 | 既有 | 通用 | S1 |
| E3 | RuleFile 其餘格式要求不受影響：固定結構、單一主題、強度用詞、範例格式 | 既有 | 通用 | S1、S2 |
| E4 | 被 `skill-derive-rule`、`skill-engineering` 委派時，依呼叫者已確認的設計寫入，不另行設計 | 既有 | 通用 | S2、S3 |

## 3. 落差

| 驗收條件 | 預期 | 實際 | 證據 |
| -------- | ---- | ---- | ---- |
| E1 | 03 紀錄修改樣板時，`skill-form-rule` 發現 `類別圖輸出` Rule 1 重述樣板骨架 | W5 由 `skill-form-rule` 施工，同步改寫 Rule 1 第 2 條配合新樣板，沒有指出它重述骨架 | 觀察：03 藍圖第 7-1 節 W5、W6 |
| E1 | RuleFile 層級的重述有寫入時的關卡 | 05-S1、05-S2 的藍圖都保留了重述樣板的 Rule 1 與列舉圖例的 Rule 6；若照藍圖施工，`skill-form-rule` 也沒有規則會攔下 | 觀察：兩份藍圖的「保留」表；`RuleFile-格式規範` 全文 |

## 4. 演練表

`skill-form-rule`（重播 03 紀錄的 W5）：

| 步驟 | 應載入 | 實際載入 | 應產出 | 實際產出 | 判定 |
| ---- | ------ | -------- | ------ | -------- | ---- |
| P1-1 | 目標 `SKILL.md`、目標 RuleFile，以及判斷重述所需的同一個 Skill 其他部位 | 觀察：步驟只要求讀取使用者需求、目標 `SKILL.md` 與目標 RuleFile | 能判斷 Rule 是否重述其他部位的輸入 | 推論：沒有讀取樣板組，無法比對 Rule 1 與骨架（依據 P1-1 內文） | 偏離 |
| P1-2 | 完成檢查清單 | 觀察：`RuleFile-格式規範` Rule 1–9 | 完成檢查清單 | 觀察：Rule 2 只規範「一個 RuleFile 一個主題」，Rule 3 只規範引用與循環引用，沒有任何條列禁止 Rule 重述其他部位 | 偏離 |
| P1-3、P2-1、P2-2 | 完成檢查清單 | 觀察：已使用 | 依設計寫入並驗證 | 觀察：依 W5 寫入，驗證通過 | 一致（檢查本身無法發現問題） |

第一個偏離點：P1-1。

## 5. 根因

| 編號 | 位置 | 缺陷類型 | 說明與證據 | 反事實檢驗 |
| ---- | ---- | -------- | ---------- | ---------- |
| R1 | `skill-form-rule`／`rules/RuleFile-格式規範.md`／Rule 3 | 缺失 | 觀察：Rule 3 規範跨檔引用，但沒有禁止 Rule 重述同一個 Skill 其他部位已規範的要求 | 假設 Rule 3 禁止重述其他部位：P2-2 會把 `類別圖輸出` Rule 1 第 1–3 條判為違反 |
| R2 | `skill-form-rule`／`SKILL.md`／P1-1 | 未載入 | 觀察：P1-1 只讀取目標 `SKILL.md` 與目標 RuleFile。推論：不讀取樣板組與其他 RuleFile，就無法比對 Rule 是否重述 | 假設 P1-1 讀取同一個 Skill 的其他 RuleFile、樣板組與腳本介面：配合 R1，P2-2 可以比對出 04 的 R5–R8 |

## 6. 被排除的假設

| 假設 | 缺陷類型 | 排除依據 |
| ---- | -------- | -------- |
| H1：只靠 `skill-engineering` 設計階段的檢查就足夠 | 交接缺陷 | 觀察：`skill-derive-rule` 與直接使用 `skill-form-rule` 都不經過 `skill-engineering` 的設計階段；06 的經驗顯示，寫入時的關卡能攔下設計階段漏掉的重述 |
| H2：Rule 3 第 2 條「本檔內完整說明核心要求」與禁止重述互相矛盾 | 衝突 | 推論：核心要求是本 Rule 自己的判準，重述指的是其他部位已經存放的要求；兩者規範的對象不同，可以並存 |

## 7. 影響範圍

依結構診斷，直接委派 `skill-form-rule` 的 Skill 有：`skill-derive-rule`、`skill-engineering`。

## 8. 待確認事項

1. 第 2 節的驗收條件是否正確、完整？E2–E4 是為了確保修改後既有行為不受影響而加入的既有預期。
2. 是否同意第 5 節的根因 R1、R2？
