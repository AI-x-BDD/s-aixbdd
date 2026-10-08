# 工程藍圖：plan-with-class-diagram－重構優化

- 模式：優化
- 紀錄目錄：`specs/skill-engineering/08-plan-with-class-diagram-重構優化/`
- 根因報告：同一紀錄目錄的 `rca-report.md`；使用者已確認 E1–E10 與 R1–R4，推定的 E1 經使用者同意作為判斷標準，H8 維持現狀（「好，同意」）
- 確認紀錄：2026-09-25 使用者於 Phase 4 回覆「確認」：同意沒有刪除項目、W1–W4 施工工作項與施工順序，以及推定的 E1（已於根因報告確認）

## 1. 驗收條件

| 編號 | 驗收條件 | 來源 | 適用範圍 |
| ---- | -------- | ---- | -------- |
| E1 | 目標 Skill 的 frontmatter、SOP 與兩份 RuleFile 逐條通過 `skill-form-description`、`skill-form-sop`、`skill-form-rule` 的完成檢查清單；RuleFile 以 GFM 渲染後，每個 Mermaid 關係符號都完整顯示 | 推定（使用者已同意） | 通用 |
| E2 | 不改變既有行為：修改前後 E3–E10 都成立；計畫目錄的編號規則、提案檔結構、圖例、確認閘門與 Phase 轉移條件的意義都不變 | 本次 | 通用 |
| E3 | 提案檔依序包含「類別圖」與「設計說明與實作順序」兩個頂層 Section，並寫入 `specs/plan/<NN>-<計畫名稱>/class-diagram-proposal.md` | 既有 | 通用 |
| E4 | 類別圖通過 Mermaid 語法檢查且不含 `classDef` 或 `style`；類別圖、設計說明與實作順序使用相同的類別名稱，描述的變更類型也一致 | 既有 | 通用 |
| E5 | 每個類別帶有一個圖例中的類別標記；`<<modified>>` 類別至少有一個帶標記的成員；成員與關係標記的位置符合圖例 | 既有 | 通用 |
| E6 | 實作順序把被依賴者排在依賴者之前，刪除步驟排在所有依賴者改寫之後 | 既有 | 通用 |
| E7 | 使用者明確確認提案前，不修改任何程式碼 | 既有 | 通用 |
| E8 | 使用者確認後，程式碼依已確認提案的實作順序實作並回報驗證結果；實際狀態需要改變類別圖時，返回 Phase 1 重新取得確認 | 既有 | 通用 |
| E9 | 需求涉及 Java 原始碼時，以類別結構腳本取得有上限的摘要，並檢視未解析引用與截斷狀態後再閱讀相關程式碼 | 既有 | 通用 |
| E10 | 觸發範圍不變：實作或重構前會新增或變更類別的請求使用本 Skill；不涉及類別新增或變更的請求不使用本 Skill | 既有 | 通用 |

## 2. To-Be SOP

````markdown
---
name: plan-with-class-diagram
description: 實作或重構會新增或變更類別的功能前，必須使用此 Skill；先提出 Mermaid 類別圖提案並取得使用者明確確認，再依已確認的類別圖與相依順序實作。使用者要求先規劃類別或先畫類別圖（class diagram）再實作時使用。
---

# SOP

## Phase 1 -- 分析與提案

1. `READ` 使用者需求、專案規範、Java 原始碼路徑（若有），以及專案根目錄下既有的 `specs/plan/` 計畫目錄（若存在），建立「專案輸入」。
2. `THINK` 若「專案輸入」顯示本次需求涉及 Java 原始碼，依需求與原始碼路徑選定完整名稱的入口類別。
3. `DELEGATE` 若已選定 Java 入口類別，在本 Skill 目錄執行 `uv run --script scripts/inspect_java_classes.py --project-root <專案根目錄絕對路徑> --entry <完整類別名稱>`，從標準輸出取得 JSON 類別結構摘要；若缺少 `uv`，依 https://docs.astral.sh/uv/getting-started/installation/ 的目前平台安裝說明安裝後重試，安裝失敗時回報原因並停止此步驟。
4. `CHECK` 執行腳本時確認退出狀態為零且標準輸出為可解析的 JSON，並檢視未解析引用及截斷狀態；失敗時依標準錯誤輸出修正入口並重試，仍失敗時回報原因。
5. `READ` 已取得類別結構摘要時依摘要選擇相關原始碼深入閱讀；未取得摘要時直接閱讀相關程式碼，建立「相關程式碼現況」。
6. `READ` 設計類別時，讀取 `rules/類別設計-格式規範.md` 的所有 Rule，建立類別設計檢查清單。
7. `THINK` 依「相關程式碼現況」與已載入的類別設計檢查清單，設計類別與實作順序。
8. `CHECK` 逐條驗證類別設計檢查清單；未通過時修正設計。
9. `THINK` 決定本次計畫名稱及下一個可用的兩位數編號 `<NN>`（從既有最大編號加一，沒有既有計畫時從 `01` 開始）。
10. `READ` 產生類別圖時，讀取 `rules/類別圖輸出-格式規範.md` 的所有 Rule，建立類別圖輸出檢查清單。
11. `READ` `templates/class-diagram-proposal.md` 與 `templates/class-diagram-proposal.example.md`，載入骨架與範例，命名載入結果為「類別圖提案樣板組」。
12. `WRITE` 依已載入的類別圖輸出檢查清單與「類別圖提案樣板組」，建立計畫目錄，將完整 Markdown 類別圖提案檔寫入專案根目錄下的 `specs/plan/<NN>-<本次計畫名稱>/class-diagram-proposal.md`。
13. `CHECK` 逐條驗證類別圖輸出檢查清單，並確認提案檔位於指定路徑且涵蓋需求。

完成條件：類別設計與類別圖輸出檢查清單均已通過，完整 Markdown 類別圖提案檔可供使用者評估，且程式碼尚未修改。

## Phase 2 -- 確認提案

1. `WRITE` 向使用者展示完整 Markdown 類別圖提案檔，並請求明確確認。
2. `CHECK` 使用者回覆；要求修改時返回 Phase 1，未明確確認時停止執行。

完成條件：使用者已明確確認目前版本的 Markdown 類別圖提案檔與實作順序。

## Phase 3 -- 按圖開發與驗證

1. `READ` 已確認的 Markdown 類別圖提案檔、最新的相關程式碼與專案規範。
2. `THINK` 比對最新的相關程式碼與已確認的 Markdown 類別圖提案檔；實際狀態需要改變類別圖時，返回 Phase 1 修訂並重新取得確認。
3. `WRITE` 依已確認的 Markdown 類別圖提案檔中的實作順序修改程式碼。
4. `CHECK` 類別組織符合已確認的 Markdown 類別圖提案檔中的類別圖，並執行適用的測試、型別檢查與 lint。

完成條件：程式碼符合已確認的 Markdown 類別圖提案檔中的類別圖，且所有適用驗證結果已回報。
````

## 3. 差異表

### 刪除

| 元素 | 位置 | 理由 |
| ---- | ---- | ---- |
| 無 | — | R1–R4 都不是重複存放，沒有無法追溯的元素；逐一標記的結果見下兩表 |

### 修改、合併、改換存放位置與新增

| 元素 | 動作 | 內容 | 追溯 |
| ---- | ---- | ---- | ---- |
| frontmatter `description` | 修改 | 改為中文；以「必須使用此 Skill」「時使用」表達觸發；保留「先提案、取得確認、再依相依順序實作」的關鍵行為；關鍵字只限「先規劃類別或先畫類別圖再實作」，不擴大觸發範圍；`name` 不變 | R1、E1、E10 |
| P1-7 | 修改 | 刪除「；並決定本次計畫名稱及下一個可用的兩位數編號…」，只保留類別設計與實作順序 | R2、E1、E6（C11） |
| P1-9（新） | 新增 | 由 P1-7 拆出的計畫名稱與編號步驟，文字保留原文，放在 P1-8 之後、兩個載入步驟之前；原 P1-9～P1-12 改為 P1-10～P1-13，內文不變 | R2、E3（C12）。刪除：編號是寫入路徑的必要輸入，不能刪；改寫：只改寫 P1-7 仍是兩個行為；改換存放位置：P1-1～P1-13 每個步驟各有不同的行為，併入任一步驟都會再次違反 `SOP-格式規範` Rule 2；腳本：使用者確認 H8 不採用 |
| `rules/類別設計-格式規範.md` Rule 4 範例 | 修改 | 範例由 1 組改為 2 組：Example 1 排序（Good 保留原文，新增同情境的 Bad），Example 2 循環相依（新增同情境的 Good，Bad 保留原文並補上相依原因）；條列不變 | R3、E1、E6（C11）。刪除：刪除循環條列會失去約束；改寫：把既有正反例改成同一個重點，另一個重點就沒有範例 |
| `rules/類別圖輸出-格式規範.md` Rule 4 對應表 | 修改 | 第一條列加上「下列」，表格改為巢狀條列，六組對應逐字不變 | R4、E1、E4（C5） |

### 保留

| 元素 | 追溯 | 約束 |
| ---- | ---- | ---- |
| frontmatter `name` | E10 | 無（識別名稱） |
| 三個 Phase 的標題與完成條件 | Phase 1：E3–E7；Phase 2：E7；Phase 3：E8 | 無（只概述結果，不重述判斷細節） |
| P1-1、P1-2、P1-5、P1-6 | E9、E6 | 無（只讀取、選定入口或載入） |
| P1-3、P1-4 | E9 | C15（委派腳本；檢視未解析引用與截斷屬於控制平面） |
| P1-8 | E6 | C8–C11（只引用類別設計檢查清單） |
| P1-10、P1-11（原 P1-9、P1-10） | E3–E5 | 無（只載入） |
| P1-12（原 P1-11） | E3 | C13 |
| P1-13（原 P1-12） | E3、E4 | C14 |
| P2-1、P2-2 | E7 | C16 |
| P3-1、P3-4 | E8 | 無（只讀取、驗證與回報） |
| P3-2 | E8 | C18 |
| P3-3 | E8 | C17 |
| `rules/類別設計-格式規範.md` Rule 1～3、Rule 4 條列 | E6 | C8–C11 |
| `rules/類別圖輸出-格式規範.md` Rule 1～3、Rule 4 其餘條列與範例、Rule 5、Rule 6 | E4、E5 | C2–C7 |
| 類別圖提案樣板組 | E3、E5 | C1 |
| `scripts/inspect_java_classes.py` | E9 | C15（H7：`ruff` 只提示參數數量，實跑正確） |

## 4. 淨增減

| 項目 | As-Is | To-Be | 增減 |
| ---- | ----- | ----- | ---- |
| Phase | 3 | 3 | 0 |
| 步驟 | 18 | 19 | +1 |
| RuleFile | 2 | 2 | 0 |
| Rule | 10 | 10 | 0 |
| 樣板組 | 1 | 1 | 0 |
| 腳本 | 1 | 1 | 0 |

- 步驟 +1：R2，由 P1-7 拆出，文字沒有增加；刪除、改寫與改換存放位置都無法處理的理由見第 3 節。
- 內容增加：`類別設計` Rule 4 新增兩個範例（排序的 Bad、循環的 Good），R3 缺失類型，理由見第 3 節。
- 內容不變：`description` 改寫語言與觸發用詞，範圍不變；`類別圖輸出` Rule 4 只改表現格式。
- 沒有刪除：本次落差都是格式規範的不符合，不是重複存放或無法追溯的內容。

## 5. 約束分配表

| 編號 | 約束 | 所屬步驟 | 存放位置 | 理由 |
| ---- | ---- | -------- | -------- | ---- |
| C1 | 提案檔的整體結構：`%%{init}%%` 配色、`classDiagram` 開頭、圖例、兩個頂層 Section | P1-12 | 類別圖提案樣板組 | 約束整份產出檔案的結構；腳本無法產生填入的設計內容 |
| C2 | 不得使用 `classDef`、`style`，展示前通過 Mermaid 語法檢查 | P1-12、P1-13 | `類別圖輸出` Rule 1 | 需要判斷填入的陳述式；語法檢查需要 Mermaid 執行環境，03 紀錄已判定不建腳本；樣板無法限制填入內容 |
| C3 | 圖中類別完整、名稱與程式碼一致、不加入無關類別 | P1-12 | `類別圖輸出` Rule 2 | 需要依設計判斷，需要正反例 |
| C4 | 類別成員維持設計層級 | P1-12 | `類別圖輸出` Rule 3 | 需要判斷，需要正反例 |
| C5 | 類別關係使用對應的 Mermaid 符號，並標示影響理解的 multiplicity、方向與標籤 | P1-12 | `類別圖輸出` Rule 4 | 需要判斷關係種類；樣板以區塊填位符號產生關係，無法逐條保證 |
| C6 | 類別圖與設計說明、實作順序互相對應 | P1-12 | `類別圖輸出` Rule 5 | 需要判斷語意一致，需要正反例 |
| C7 | 每個類別的變更標記判定與成員、關係標記的位置 | P1-12 | `類別圖輸出` Rule 6 | 需要依「相關程式碼現況」逐類別判斷；圖例只定義意義（C1） |
| C8 | 類別與責任可追溯至需求 | P1-7 | `類別設計` Rule 1 | 需要判斷，需要正反例 |
| C9 | 類別責任具有明確邊界 | P1-7 | `類別設計` Rule 2 | 需要判斷，需要正反例 |
| C10 | 類別關係符合實際語意 | P1-7 | `類別設計` Rule 3 | 需要判斷，需要正反例 |
| C11 | 實作順序依相依性排列、涵蓋所有變更類別、刪除排在最後、處理循環相依 | P1-7 | `類別設計` Rule 4 | 需要判斷相依關係，需要正反例 |
| C12 | 計畫名稱，以及下一個可用的兩位數編號（既有最大編號加一，沒有時從 `01` 開始） | P1-9 | P1-9 步驟內文 | 編號部分符合腳本條件，但使用者確認 H8 維持現狀（三次實跑都正確，改用腳本需要 1 個腳本與 2 個步驟）；計畫名稱需要判斷；不是整份檔案的結構；一句話即可表達，不需要正反例 |
| C13 | 提案檔寫入 `specs/plan/<NN>-<本次計畫名稱>/class-diagram-proposal.md` | P1-12 | P1-12 步驟內文 | 只屬於單一步驟，一句話即可表達 |
| C14 | 提案檔涵蓋需求 | P1-13 | P1-13 步驟內文 | 只屬於單一步驟，一句話即可表達（04 紀錄 H9） |
| C15 | 摘要上限的預設值、找不到入口時失敗、輸出數量不超過上限 | P1-3、P1-4 | `scripts/inspect_java_classes.py` | 輸入輸出明確且可由程式判斷；腳本已實作 |
| C16 | 使用者明確確認前不修改程式碼，要求修改時返回 Phase 1 | P2-2 | SOP 流程 | 屬於使用者確認與 Phase 轉移 |
| C17 | 確認後依已確認提案的實作順序修改程式碼 | P3-3 | SOP 流程 | 屬於執行順序 |
| C18 | 實際狀態需要改變類別圖時返回 Phase 1 重新確認 | P3-2 | SOP 流程 | 屬於分支與 Phase 轉移 |

## 6. 施工工作項

| 順序 | 工作項 | 執行者 | 目標 | 內容 | 約束 | 狀態 |
| ---- | ------ | ------ | ---- | ---- | ---- | ---- |
| 1 | W1 | `skill-form-description` | `SKILL.md` frontmatter 的 `description` | 改為中文並寫明觸發用詞，範圍不變 | 無（`description` 不是存放位置） | 已完成 |
| 2 | W2 | `skill-form-sop` | Phase 1 -- 分析與提案中「設計類別與實作順序；並決定本次計畫名稱」的 `THINK` 步驟 | 拆成兩個 `THINK` 步驟並重新編號 | C11、C12 | 已完成 |
| 3 | W3 | `skill-form-rule` | `rules/類別設計-格式規範.md` Rule 4 | 範例改為兩組同情境的正反範例 | C11 | 已完成 |
| 4 | W4 | `skill-form-rule` | `rules/類別圖輸出-格式規範.md` Rule 4 | 符號對應表改為巢狀條列 | C5 | 已完成 |

### 工作項內容

#### W1：frontmatter `description`

`name` 不變，`description` 改為：

```text
實作或重構會新增或變更類別的功能前，必須使用此 Skill；先提出 Mermaid 類別圖提案並取得使用者明確確認，再依已確認的類別圖與相依順序實作。使用者要求先規劃類別或先畫類別圖（class diagram）再實作時使用。
```

`skill-form-description` Phase 2 的觸發演練使用 S4 的六個請求；判斷結果必須與修改前的 `description` 相同。

#### W2：SOP 修改

依第 2 節 To-Be SOP 修改，其餘步驟保留原文：

1. Phase 1 -- 分析與提案中「設計類別與實作順序」的 `THINK` 步驟改為：`THINK` 依「相關程式碼現況」與已載入的類別設計檢查清單，設計類別與實作順序。
2. 在同一 Phase 的「逐條驗證類別設計檢查清單」`CHECK` 步驟之後，新增：`THINK` 決定本次計畫名稱及下一個可用的兩位數編號 `<NN>`（從既有最大編號加一，沒有既有計畫時從 `01` 開始）。
3. 之後的四個步驟（載入類別圖輸出規則、載入樣板組、寫入提案檔、驗證類別圖輸出）編號各加一，內文不變。

#### W3：`rules/類別設計-格式規範.md` Rule 4

標題與五條條列保留原文，`## Good Example` 與 `## Bad Example` 改為：

````markdown
## Good Example

### Example 1

- 實作順序先建立契約與實作者，再改寫依賴契約的服務，最後才刪除已沒有依賴者的舊類別，且涵蓋所有預計新增、修改與刪除的類別。

情境：

- `SqlOrderRepository` 實作 `OrderRepository`。
- `OrderService` 原本依賴 `LegacyOrderDao`，本次改為依賴 `OrderRepository`，並刪除 `LegacyOrderDao`。
- 實作順序：`OrderRepository`、`SqlOrderRepository`、`OrderService`、刪除 `LegacyOrderDao`。

### Example 2

- 發現 `OrderService` 與 `OrderRepository` 互相依賴後，先調整設計解除循環，再排出線性順序。

情境：

- `OrderService` 依賴 `OrderRepository`。
- `OrderRepository` 為了產生訂單編號而依賴 `OrderService`。
- 調整設計：改由 `OrderService` 產生訂單編號後傳給 `OrderRepository`，`OrderRepository` 不再依賴 `OrderService`。
- 實作順序：`OrderRepository`、`OrderService`。

## Bad Example

### Example 1

- 同一情境中，`LegacyOrderDao` 在依賴它的 `OrderService` 改寫前就被刪除，`OrderService` 也排在它依賴的 `OrderRepository` 之前。

情境：

- `SqlOrderRepository` 實作 `OrderRepository`。
- `OrderService` 原本依賴 `LegacyOrderDao`，本次改為依賴 `OrderRepository`，並刪除 `LegacyOrderDao`。
- 實作順序：刪除 `LegacyOrderDao`、`OrderService`、`SqlOrderRepository`、`OrderRepository`。

### Example 2

- 同一情境中，`OrderService` 與 `OrderRepository` 互相依賴，卻直接排列成線性順序，沒有處理循環。

情境：

- `OrderService` 依賴 `OrderRepository`。
- `OrderRepository` 為了產生訂單編號而依賴 `OrderService`。
- 實作順序：`OrderService`、`OrderRepository`。
````

Rule 1～3 保留原文。

#### W4：`rules/類別圖輸出-格式規範.md` Rule 4

第一條列與表格改為下列巢狀條列，六組對應逐字不變；其餘兩條條列、Good Example 與 Bad Example 保留原文：

```markdown
- 已確定的類別關係必須使用下列對應的 Mermaid 符號：
  - 繼承：`<|--`
  - Interface 實作：`<|..`
  - Composition：`*--`
  - Aggregation：`o--`
  - Association：`-->` 或 `--`
  - Dependency：`..>`
```

Rule 1～3、5、6 保留原文。

## 7. 驗收情境

| 編號 | 驗證 | 類型 | 輸入 | 預先回覆 | 判斷方式 |
| ---- | ---- | ---- | ---- | -------- | -------- |
| S1 | E2–E7、E9 | 回歸 | 包含本次修改的專案複本，需求：為 `java-web-framework` 加入 middleware 鏈，可在 Handler 執行前後處理請求，並可以提前回應 | Phase 2 回覆「先不要實作」 | E3：提案檔位於 `specs/plan/04-<名稱>/class-diagram-proposal.md`，兩個頂層 Section 依序出現；E4：以 `mermaid@10.2.3` 解析通過，沒有 `classDef`／`style`，圖文名稱與變更類型一致；E5：每個類別恰有一個圖例中的類別標記，`<<modified>>` 類別至少有一個帶標記的成員；E6：被依賴者先於依賴者；E7：`git status` 只有新增的提案目錄；E9：子代理回報腳本命令與截斷、未解析引用的檢視結果 |
| S2 | E2、E8 | 回歸 | 包含本次修改的專案複本，需求：讓 `WebApplication` 可以註冊自訂的 404 Not Found 回應 | Phase 2 回覆「確認」 | 程式碼修改的順序與已確認提案的實作順序一致；實作的類別組織符合類別圖；回報 `mvn test` 結果 |
| S3 | E1、E2 | 本次 | 施工後的目標 Skill | 無 | 依三個 skill-form-* 的完成檢查清單逐條檢查，全部通過；以 GFM 渲染 `rules/類別圖輸出-格式規範.md`，六種關係的符號都完整出現；逐段比對修改前後的 diff，沒有任何行為約束的意義改變 |
| S4 | E2、E10 | 回歸 | 專案所有 skills 目錄中各 Skill 的 `description`，分別搭配修改前與修改後的目標 Skill `description`；六個請求：「幫 java-web-framework 加 middleware，先規劃類別再實作」「重構 Router，把路由比對抽成獨立類別」「Add a caching layer to UserService and plan the classes first」「修正 Route.java 註解的錯字」「說明 IoC 容器的原理」「幫我寫這次變更的 commit message」 | 無 | 不帶本次脈絡的子代理只依 `description` 判斷每個請求應使用的 Skill；修改前後的判斷結果相同，前三個使用本 Skill，後三個不使用 |

直接呼叫者：無，不需要呼叫者的回歸情境。

## 8. 驗收結果

- 施工後結構診斷：`plan-with-class-diagram` 0 個 error、0 個 warning；`SKILL.md` 與第 2 節 To-Be SOP 逐字一致；W3、W4 與工作項內容一致。W4 施工時多出的空行會讓整份清單渲染成鬆散清單，已移除（藍圖內容沒有這個空行）。
- 連結同步結果：Claude Code 已安裝；10 個 Skill 連結正常，沒有新建、移除、衝突、缺漏或移轉建議；`skill-creator` 在 `.agents/skills` 與 `.claude/skills` 並存（既有狀況，與本次無關）。
- 施工方式：W1 由 `skill-form-description` 施工，觸發演練與 S4 相同；W2 由 `skill-form-sop` 施工；W3、W4 由 `skill-form-rule` 施工，各自逐條通過完成檢查清單，沒有回報差異。
- 驗收方式：S1、S2 各自在包含本次未提交修改的暫存專案複本中執行（排除 `specs/skill-engineering`、`java-web-framework/target`、`upstreams`，執行前提交基準，`git status` 為乾淨），由不帶本次分析脈絡的子代理實際執行 Skill。S4 由兩個不帶脈絡的子代理分別只看修改前、修改後的 `description` 判斷。S3 為靜態檢查，由執行者逐條演練。準備複本時第一次的指令含 `rm -rf`，被使用者中斷；改用不刪除、目錄已存在就停止的做法後重新準備。
- S1 通過（E2–E7、E9）：
  - 需求「middleware 鏈」；新拆出的 P1-9 以獨立步驟執行，提案檔寫入 `specs/plan/04-middleware-chain/class-diagram-proposal.md`，兩個頂層 Section 依序出現（E3）。
  - 以 `mermaid@10.2.3` 解析通過，含 `classDef` 的反例會失敗；沒有 `classDef`／`style`；設計說明只使用圖中的類別名稱（E4）。
  - 9 個類別各有一個標記；`WebApplication`、`Router` 為 `<<modified>>` 並帶 `«new»`／`«changed»` 成員；連到新類別的關係沒有加標記（E5）。
  - 實作順序為 `Middleware` → `MiddlewareChain` → `Router` → `WebApplication` → 測試與 README（E6）。
  - 收到「先不要實作」後停止；`git status` 只有 `?? specs/plan/04-middleware-chain/`（E7）。
  - 腳本命令沒有 `--max-classes`；子代理檢視了 `truncated: false` 與 36 筆未解析引用（都是 JDK 型別）（E9）。
- S2 通過（E8）：
  - 需求「自訂 404 回應」；確認後依提案的實作順序修改 `Router` → `WebApplication` → 測試 → README，依據為提案檔的實作順序段落。
  - 類別組織與類別圖逐項一致，實作後重跑腳本多出 `Router -> Handler field`，與圖上標 `«new»` 的關聯一致。
  - `mvn -q test` 退出碼 0，15 個測試通過（`WebApplicationTest` 由 4 個增為 7 個）；執行者在複本重跑一次，結果相同。
- S3 通過（E1、E2）：三個 skill-form-* 的完成檢查清單逐條通過；GFM 渲染後六種關係符號完整；diff 中沒有任何規則強度或約束意義的改變。
- S4 通過（E2、E10）：修改前後的 `description` 對六個請求的判斷完全相同，前三個使用本 Skill，後兩個為「無」，commit message 使用 `git-commit-draft`。
- 觀察（既有問題，與本次修改無關）：S1、S2 的子代理都回報腳本抓不到只出現在方法本體或靜態呼叫中的相依（`LoggingHandler`），需要另外補讀；與根因報告第 8 節記錄的 04 觀察相同。
- 真實專案副作用：`git status` 只包含本次施工的 3 個 Skill 檔案與 08 紀錄目錄。
