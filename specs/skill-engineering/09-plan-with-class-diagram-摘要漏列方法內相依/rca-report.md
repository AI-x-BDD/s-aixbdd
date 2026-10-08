# 根因報告：plan-with-class-diagram－摘要漏列方法內相依

- 紀錄目錄：`specs/skill-engineering/09-plan-with-class-diagram-摘要漏列方法內相依/`
- 問題證據：本次對話上下文（08 驗收中 S1、S2 子代理的回報；使用者要求處理「腳本抓不到只在方法內部用到的類別」）；以 `java-web-framework`、入口 `io.github.stevecyj.webframework.WebApplication` 執行 `scripts/inspect_java_classes.py` 的輸出；`WebApplication.java` 第 19、24、34 行；上一輪紀錄 `specs/skill-engineering/08-plan-with-class-diagram-重構優化/` 與 `04-plan-with-class-diagram-規則重複存放/` 的驗收觀察
- 確認紀錄：2026-09-25 使用者回覆「好，確認執行修改」，確認 E1–E4（含推定的 E2）與 R1

## 1. 使用者回報的問題

類別結構腳本只追蹤繼承、欄位與方法簽章，不追蹤方法本體。只在方法本體中使用的專案內類別不會出現在摘要中。目前的實跑都靠 AI 在閱讀入口類別時順便看到，才把這些類別補回來；如果漏掉的類別只出現在 AI 沒有打開的檔案中，類別圖就會少一個既有協作類別，而且沒有任何提示。

## 2. 驗收條件

| 編號 | 驗收條件 | 來源 | 適用範圍 | 驗收情境 |
| ---- | -------- | ---- | -------- | -------- |
| E1 | 需求涉及 Java 原始碼時，摘要類別在方法本體中引用、但摘要沒有列出的專案內類別，會在建立「相關程式碼現況」之前被列出並檢視；以 `java-web-framework`、入口 `WebApplication` 執行時，`LoggingHandler` 會被列出 | 本次 | 通用 | S1、S2 |
| E2 | 對相同輸入，腳本既有的輸出內容（`classes`、`relations`、未解析引用、`omitted_class_count`、`truncated`）不變 | 推定（理由：使用者要求補上漏列的類別，沒有要求改變既有摘要；既有內容不變，才不會影響 04 E9 的上限與截斷判斷） | 通用 | S1 |
| E3 | 提案檔依序包含兩個頂層 Section 並寫入 `specs/plan/<NN>-<計畫名稱>/class-diagram-proposal.md`；類別圖通過 Mermaid 語法檢查、每個類別有一個圖例標記、圖文一致；實作順序正確；使用者確認前不修改程式碼（08 紀錄 E3–E7） | 既有 | 通用 | S2 |
| E4 | 需求涉及 Java 原始碼時，以類別結構腳本取得有上限的摘要，並檢視未解析引用與截斷狀態後再閱讀相關程式碼（08 紀錄 E9） | 既有 | 通用 | S1、S2 |

驗收情境：

| 編號 | 驗證 | 類型 | 輸入 | 預先回覆 | 判斷方式 |
| ---- | ---- | ---- | ---- | -------- | -------- |
| S1 | E1、E2、E4 | 本次 | 以修改前與修改後的腳本，分別對 `java-web-framework` 執行入口 `WebApplication`、`Router`、`io.github.stevecyj.webframework.example.UserController` 三次 | 無 | 修改後的輸出列出 `WebApplication` 方法本體中的 `LoggingHandler`；沒有列出只出現在註解中的 `Logged`；三個入口的既有輸出內容與修改前逐字相同 |
| S2 | E1、E3、E4 | 本次 | 包含本次修改的專案複本，需求：讓 `java-web-framework` 的請求日誌多記錄處理耗時（毫秒） | Phase 2 回覆「先不要實作」 | 子代理回報檢視了腳本列出的方法本體引用，且「相關程式碼現況」包含 `LoggingHandler`；E3 同 08 紀錄 S1 的判斷方式；`git status` 只有新增的提案目錄 |

08 紀錄的 E8（確認後依順序實作）只涉及 Phase 3，本次不修改，不另設情境。

## 3. 落差

| 驗收條件 | 預期 | 實際 | 證據 |
| -------- | ---- | ---- | ---- |
| E1 | 摘要或其他輸出列出 `LoggingHandler` | 摘要只列 8 個類別，沒有 `LoggingHandler`；也沒有任何欄位提示方法本體中還有其他專案內類別 | 觀察：腳本輸出的 `classes`；`WebApplication.java` 第 24、34 行呼叫 `LoggingHandler.decorate(...)`；`references()` 只走訪繼承、欄位、參數、回傳型別與 `throws` |
| E1 | 建立「相關程式碼現況」前有步驟要求檢視這些類別 | P1-5 只寫「依摘要選擇相關原始碼深入閱讀」 | 觀察：`SKILL.md` P1-4、P1-5；08 S1、S2 子代理都是在閱讀入口類別 `WebApplication` 時自行發現，屬於巧合而不是流程保證 |

## 4. 演練表

`plan-with-class-diagram`（以 08 S1 的輸入演練）：

| 步驟 | 應載入 | 實際載入 | 應產出 | 實際產出 | 判定 |
| ---- | ------ | -------- | ------ | -------- | ---- |
| P1-1、P1-2 | 無 | 無 | 專案輸入、入口類別 | 觀察：入口為 `WebApplication` | 一致 |
| P1-3 | 腳本 | 觀察：已執行 | 涵蓋入口相關協作類別的摘要 | 觀察：8 個類別，缺少方法本體中的 `LoggingHandler` | 偏離 |
| P1-4 | 腳本輸出 | 觀察：已檢視 | 判斷摘要是否足以選擇原始碼 | 觀察：只檢視未解析引用與截斷；`truncated: false` 讓摘要看起來完整 | 偏離（承接 P1-3） |
| P1-5 | 摘要 | 觀察：已使用 | 相關程式碼現況 | 觀察：子代理因閱讀 `WebApplication` 才發現 `LoggingHandler` | 一致（巧合） |
| P1-6 以後 | — | — | — | 觀察：類別圖包含 `LoggingHandler` | 一致 |

第一個偏離點：P1-3（`DELEGATE` 執行類別結構腳本）。

## 5. 根因

| 編號 | 位置 | 缺陷類型 | 說明與證據 | 反事實檢驗 |
| ---- | ---- | -------- | ---------- | ---------- |
| R1 | `plan-with-class-diagram`／`scripts/inspect_java_classes.py`／`references()` 的走訪範圍，以及 `SKILL.md` P1-4、P1-5 | 缺失 | 觀察：「方法本體中引用的專案內類別也要納入相關程式碼現況」這項預期，沒有寫在腳本、步驟或 RuleFile 的任何地方。腳本只走訪型別宣告層級；P1-4、P1-5 也沒有要求補查。推論：目前能補回來，只是因為入口類別一定會被打開（依據第 3 節的兩項觀察） | 假設預期已表達：P1-3 的輸出列出 `LoggingHandler`，P1-4 會檢視這份清單，P1-5 會依清單閱讀。即使漏掉的類別出現在 AI 沒有打開的檔案中，也會被列出，E1 可以滿足 |

## 6. 被排除的假設

| 假設 | 缺陷類型 | 排除依據 |
| ---- | -------- | -------- |
| H2：模型沒有仔細閱讀原始碼 | 非 Skill 問題 | 觀察：08 S1、S2 與 04 S1、S2 的子代理都有補讀，模型能力足夠；問題在於沒有任何部位保證補讀 |
| H3：腳本的 `--max-classes` 上限太小，類別被截斷 | 載體過弱 | 觀察：`truncated: false`、`omitted_class_count: 0`；`LoggingHandler` 是完全沒有被走訪，不是被截斷 |
| H4：`Logged` 也被漏掉 | 缺失 | 觀察：`Logged` 只出現在 `WebApplication.java` 第 19 行的 Javadoc `{@link Logged}`，不是程式碼中的相依，不列入是正確的 |

## 7. 影響範圍

無：沒有其他 Skill 委派 `plan-with-class-diagram`。`skill-engineering` 與其他 Skill 都不使用這支腳本。

## 8. 待確認事項

1. 第 2 節的驗收條件是否正確、完整？
2. 是否同意根因 R1？
3. E2 是推定：修改後，腳本既有的輸出內容保持不變，只新增資訊。是否同意？
