# 工程藍圖：plan-with-class-diagram－類別圖未標註新增修改刪除

- 模式：優化
- 紀錄目錄：`specs/skill-engineering/03-plan-with-class-diagram-類別圖未標註新增修改刪除/`
- 根因報告：同一紀錄目錄的 `rca-report.md`；使用者已確認 E1–E9 與 R1、R2，推定的 E4、E5 經使用者回覆需要，並選定方案 A（文字標記加顏色，未變更的既有類別明確標示 `<<existing>>`）
- 施工差異：W2 原寫「Rule 1、3、4 範例使用簡寫 `<<標記>> 類別名稱` 加 `cssClass`」，與 Rule 6「類別本體第一行」矛盾；2026-09-25 回報使用者，使用者選擇統一使用類別本體寫法，W2 內容已更新
- 確認紀錄：2026-09-25 使用者於 Phase 4 回覆「同意，開始執行」：同意三個刪除項目、全部施工工作項，以及關係標記只用於兩端皆為 `<<modified>>` 或 `<<existing>>` 的關係（C5）；預覽圖存於 `previews/`

## 1. 驗收條件

| 編號 | 驗收條件 | 來源 | 適用範圍 |
| ---- | -------- | ---- | -------- |
| E1 | 類別圖中每個類別在渲染後的圖上都帶有一個變更類型標記，且只有一個：新增、修改、刪除或未變更（只作為參考的既有類別）；標記與「相關程式碼現況」一致，目前原始碼中已存在的類別不得標為新增 | 本次 | 通用 |
| E2 | 標為修改的類別中，本次新增、修改或刪除的成員都在該成員行上各自帶有成員層級的標記；沒有標記的成員代表維持原樣 | 本次 | 通用 |
| E3 | 本次要刪除的類別仍出現在類別圖中，並帶有刪除標記；因刪除而移除的關係線在圖上也能辨識為已移除 | 本次 | 通用 |
| E4 | 提案檔中有圖例，說明每種類別標記與成員標記的意思 | 推定（已確認） | 通用 |
| E5 | 有類別或成員要刪除時，實作順序中有明確的移除步驟，並排在所有依賴者改寫完成之後 | 推定（已確認） | 通用 |
| E6 | 提案檔依序包含「類別圖」與「設計說明與實作順序」兩個頂層 Section，並寫入 `specs/plan/<NN>-<計畫名稱>/class-diagram-proposal.md` | 既有 | 通用 |
| E7 | 類別圖通過 Mermaid 語法檢查，且類別圖、設計說明與實作順序使用相同的類別名稱，描述的變更類型也一致 | 既有 | 通用 |
| E8 | 使用者明確確認提案前，不修改任何程式碼 | 既有 | 通用 |
| E9 | 使用者確認後，程式碼依已確認的類別圖與實作順序實作，並回報測試結果 | 既有 | 通用 |
| E10 | 提案檔的類別圖在 Mermaid 10.2.3（Neovim markdown-preview.nvim 內建）與最新版（12.0.0）都能渲染，且類別依樣式類別上色 | 本次（R3，使用者確認） | 通用 |

## 2. To-Be SOP

````markdown
---
name: plan-with-class-diagram
description: Before implementing a feature or refactor that introduces or changes classes, propose a Mermaid class diagram, obtain explicit user confirmation, then implement according to the approved diagram and dependency order.
---

# SOP

## Phase 1 -- 分析與提案

1. `READ` 使用者需求、專案規範、Java 原始碼路徑（若有），以及專案根目錄下既有的 `specs/plan/` 計畫目錄（若存在），建立「專案輸入」。
2. `THINK` 若「專案輸入」顯示本次需求涉及 Java 原始碼，依需求與原始碼路徑選定完整名稱的入口類別及最多輸出類別數（預設 30）。
3. `DELEGATE` 若已選定 Java 入口類別，在本 Skill 目錄執行 `uv run --script scripts/inspect_java_classes.py --project-root <專案根目錄絕對路徑> --entry <完整類別名稱> --max-classes <最多類別數>`，從標準輸出取得 JSON 類別結構摘要；若缺少 `uv`，依 https://docs.astral.sh/uv/getting-started/installation/ 的目前平台安裝說明安裝後重試，安裝失敗時回報原因並停止此步驟。
4. `CHECK` 執行腳本時確認退出狀態為零、JSON 包含入口類別、輸出類別數未超過上限，並檢視未解析引用及截斷狀態；失敗時依標準錯誤輸出修正入口並重試，仍失敗時回報原因。
5. `READ` 已取得類別結構摘要時依摘要選擇相關原始碼深入閱讀；未取得摘要時直接閱讀相關程式碼，建立「相關程式碼現況」。
6. `READ` 設計類別時，讀取 `rules/類別設計-格式規範.md` 的所有 Rule，建立類別設計檢查清單。
7. `THINK` 依「相關程式碼現況」與已載入的類別設計檢查清單，設計必要的類別、責任、關係、相依性與開發順序；並決定本次計畫名稱及下一個可用的兩位數編號 `<NN>`（從既有最大編號加一，沒有既有計畫時從 `01` 開始）。
8. `CHECK` 逐條驗證類別設計檢查清單；未通過時修正設計。
9. `READ` 產生類別圖時，讀取 `rules/類別圖輸出-格式規範.md` 的所有 Rule，建立類別圖輸出檢查清單。
10. `READ` `templates/class-diagram-proposal.md` 與 `templates/class-diagram-proposal.example.md`，載入骨架與範例，命名載入結果為「類別圖提案樣板組」。
11. `WRITE` 依已載入的類別圖輸出檢查清單與「類別圖提案樣板組」，建立計畫目錄，將完整 Markdown 類別圖提案檔寫入專案根目錄下的 `specs/plan/<NN>-<本次計畫名稱>/class-diagram-proposal.md`。
12. `CHECK` 逐條驗證類別圖輸出檢查清單，並確認提案檔位於指定路徑且涵蓋需求。

完成條件：類別設計與類別圖輸出檢查清單均已通過，完整 Markdown 類別圖提案檔可供使用者評估，且程式碼尚未修改。

## Phase 2 -- 確認提案

1. `WRITE` 向使用者展示完整 Markdown 類別圖提案檔，並請求明確確認。
2. `CHECK` 使用者回覆；要求修改時返回 Phase 1，未明確確認時停止執行。

完成條件：使用者已明確確認目前版本的 Markdown 類別圖提案檔與實作順序。

## Phase 3 -- 按圖開發與驗證

1. `READ` 已確認的 Markdown 類別圖提案檔、最新的相關程式碼與專案規範。
2. `THINK` 依已確認的 Markdown 類別圖提案檔中的類別圖與類別相依性確定實作順序；實際狀態需要改變類別圖時，返回 Phase 1 修訂並重新取得確認。
3. `WRITE` 依已確認的 Markdown 類別圖提案檔與實作順序修改程式碼。
4. `CHECK` 類別組織符合已確認的 Markdown 類別圖提案檔中的類別圖，並執行適用的測試、型別檢查與 lint。

完成條件：程式碼符合已確認的 Markdown 類別圖提案檔中的類別圖，且所有適用驗證結果已回報。
````

## 3. 差異表

### 刪除

| 元素 | 位置 | 理由 |
| ---- | ---- | ---- |
| 「；第一個頂層 Section 放置 Mermaid 類別圖，第二個頂層 Section 放置設計說明與實作順序」 | P1-11 內文 | 無法追溯：E6 已由類別圖提案樣板組保證（C9） |
| 「兩個頂層 Section 結構、Mermaid 類別圖、設計說明與實作順序彼此一致」 | P1-12 內文 | 無法追溯：E6 由樣板組保證（C9），E7 由 `rules/類別圖輸出-格式規範.md` Rule 1、5 保證（C7），P1-12 已逐條驗證該檢查清單 |
| 「（第一個頂層 Section 為 Mermaid 類別圖，第二個頂層 Section 為設計說明與實作順序）」 | P2-1 內文 | 無法追溯：展示的就是依樣板組產生的提案檔（C9） |

### 修改、合併、改換存放位置與新增

| 元素 | 動作 | 內容 | 追溯 |
| ---- | ---- | ---- | ---- |
| `rules/類別圖輸出-格式規範.md` Rule 6 | 新增 | 新 Rule「類別圖必須標示本次的變更類型」：類別標記、合併 annotation、成員標記、關係標記 | R1、E1、E2、E3（C1、C2、C3、C5） |
| `rules/類別圖輸出-格式規範.md` Rule 2 | 修改 | 第 1 條改為「新增、修改或刪除的類別」都必須出現在圖中；正反範例補上變更標記，並加入一個刪除類別 | R1、E3（C4） |
| `rules/類別圖輸出-格式規範.md` Rule 5 | 修改 | 第 1 條改為新增、修改或刪除的類別都要在設計說明中註明變更類型，並與圖中標記一致；正反範例補上標記 | E7（C7） |
| `rules/類別圖輸出-格式規範.md` Rule 1、3、4 的範例 | 修改 | 範例中的 Mermaid 補上符合 Rule 6 的變更標記，條列不變 | 範例不得與 Rule 6 矛盾（約束分配 Rule 1） |
| `rules/類別設計-格式規範.md` Rule 4 | 修改 | 第 2 條改為涵蓋「新增、修改或刪除」的類別；新增一條：刪除類別或成員的步驟必須排在所有依賴者改寫之後；Good Example 加入刪除步驟 | R2、E5（C8） |
| `templates/class-diagram-proposal.md` | 修改 | 在 Mermaid 區塊的 `{{CLASS_DIAGRAM_BODY}}` 後加入四行固定的 `classDef`；在 Mermaid 區塊後加入固定的圖例表 | E1、E4（C6） |
| `templates/class-diagram-proposal.example.md` | 修改 | 情境改為「新增取消訂單，並把資料存取從 `LegacyOrderDao` 改為 `OrderRepository`」，示範新增、修改、刪除、未變更四種類別標記，以及成員與關係標記；設計說明註明變更類型，實作順序最後刪除 `LegacyOrderDao` | E1–E5、E7，範例與 C1–C8 一致 |
| P1-11、P1-12、P2-1 | 修改 | 刪除上表所列的重複描述，其餘文字保留原文 | C7、C9 |

### 保留

| 元素 | 追溯 |
| ---- | ---- |
| frontmatter（`name` 與 `description`） | E8、E9：description 已說明先確認提案再實作；變更標示不影響觸發情境 |
| 三個 Phase 的完成條件 | Phase 1：E6、E7、E8；Phase 2：E8；Phase 3：E9 |
| P1-1～P1-5（讀取輸入、執行類別結構腳本、閱讀相關程式碼） | E1：判定新增、修改、刪除或未變更需要「相關程式碼現況」 |
| P1-6～P1-8（類別設計檢查清單的載入、設計與驗證） | E5、E7 |
| P1-9、P1-10（載入類別圖輸出檢查清單與類別圖提案樣板組） | E1–E4、E6、E7 |
| P2-2 | E8 |
| Phase 3 -- 按圖開發與驗證（P3-1～P3-4） | E9 |
| `rules/類別設計-格式規範.md` Rule 1～3 | E7、E9：類別可追溯、責任邊界與關係語意，支撐可確認且可實作的設計 |
| `rules/類別設計-格式規範.md` Rule 3 的 Mermaid 範例 | 用來說明關係語意，不是提案檔的輸出，不需要套用 Rule 6 的變更標記 |
| `rules/類別圖輸出-格式規範.md` Rule 1、3、4 的條列 | E7：Mermaid 結構、設計層級成員與關係符號 |
| `scripts/inspect_java_classes.py` | E1：提供既有類別結構，用來判定變更類型 |

## 4. 淨增減

| 項目 | As-Is | To-Be | 增減 |
| ---- | ----- | ----- | ---- |
| Phase | 3 | 3 | 0 |
| 步驟 | 18 | 18 | 0 |
| RuleFile | 2 | 2 | 0 |
| Rule | 9 | 10 | +1 |
| 樣板組 | 1 | 1 | 0 |
| 腳本 | 1 | 1 | 0 |

- Rule +1（`rules/類別圖輸出-格式規範.md` Rule 6）：R1 的缺陷類型為缺失。依序考慮其他做法：
  - 刪除：沒有表達變更標記的既有內容可以刪除。
  - 改寫：Rule 2 的目的是「類別完整、名稱一致」。若把類別、成員、關係三層標記與 annotation 合併方式都塞進 Rule 2，Rule 2 會同時負責兩件事，正反範例也無法聚焦。因此只把「刪除的類別也要出現在圖中」這一條併入 Rule 2。
  - 改換存放位置：標記詞彙與顏色已經放進樣板骨架（C6），但「每個類別標哪一種」需要依設計語意判斷，樣板無法逐一保證，必須放在 RuleFile。
- 內容減少：刪除三個步驟中重複描述兩個頂層 Section 與一致性的文字。

## 5. 約束分配表

| 編號 | 約束 | 所屬步驟 | 存放位置 | 理由 |
| ---- | ---- | -------- | -------- | ---- |
| C1 | 每個類別在類別本體第一行，以圖例中四種類別標記之一標示，並套用對應的樣式類別；標記依「相關程式碼現況」判定，已存在的類別不得標為 `<<new>>` | P1-11 | `rules/類別圖輸出-格式規範.md` Rule 6 | 判定變更類型需要設計語意，腳本無法判斷；骨架以區塊填位符號產生類別，樣板無法逐類別保證；需要正反例；屬於類別圖輸出主題 |
| C2 | 類別已有 `<<interface>>` 等 annotation 時合併成單一 annotation，例如 `<<interface · new>>` | P1-11 | `rules/類別圖輸出-格式規範.md` Rule 6 | Mermaid 只顯示第一個 annotation（已實測）。需要正反例說明失效寫法；腳本與樣板都無法逐類別保證 |
| C3 | `<<modified>>` 類別列出本次新增、修改或移除的設計層級成員，並在行尾加上 `«new»`、`«changed»` 或 `«removed»`；每個 `<<modified>>` 類別至少有一個帶標記的成員 | P1-11 | `rules/類別圖輸出-格式規範.md` Rule 6 | 需要判斷哪些成員屬於本次變更；需要正反例 |
| C4 | 預計刪除的類別必須出現在類別圖中 | P1-11 | `rules/類別圖輸出-格式規範.md` Rule 2 | 與既有的「類別必須完整」屬於同一條約束，擴充該條列即可 |
| C5 | 兩端都是 `<<modified>>` 或 `<<existing>>` 的關係，若是本次新增或移除，須在標籤結尾加上 `«new»` 或 `«removed»`，並保留原本的 Mermaid 符號；連到 `<<new>>` 或 `<<deleted>>` 類別的關係，變更已由類別標記表達，不加關係標記 | P1-11 | `rules/類別圖輸出-格式規範.md` Rule 6 | 需要判斷關係是否為本次變更；需要正反例說明「改箭頭種類」的錯誤寫法 |
| C6 | 標記詞彙、意義與顏色：四種類別標記對應 `added`、`changed`、`removed`、`kept` 四個樣式類別的固定 `classDef`，以及三種成員或關係標記；提案檔包含說明這些標記的圖例 | P1-11 | 類別圖提案樣板組（骨架固定內容） | 約束的是每份提案檔都相同的固定內容，屬於產出檔的整體結構；不需要逐類別判斷，因此不放 RuleFile |
| C7 | 設計說明中每個新增、修改或刪除的類別都註明變更類型，且與圖中標記一致 | P1-11 | `rules/類別圖輸出-格式規範.md` Rule 5 | 擴充既有的「圖與文字對應」條列；需要判斷語意是否一致 |
| C8 | 實作順序涵蓋刪除的類別或成員，刪除步驟排在所有依賴者改寫之後 | P1-7 | `rules/類別設計-格式規範.md` Rule 4 | 擴充既有的相依順序 Rule；需要判斷依賴關係與正反例 |
| C9 | 提案檔依序包含兩個頂層 Section | P1-11 | 類別圖提案樣板組 | 既有；約束的是整份提案檔的結構 |
| C10 | 使用者明確確認前不修改程式碼 | P2-2 | SOP 流程 | 既有；屬於使用者確認閘門 |

## 6. 施工工作項

| 順序 | 工作項 | 執行者 | 目標 | 內容 | 約束 | 狀態 |
| ---- | ------ | ------ | ---- | ---- | ---- | ---- |
| 1 | W1 | `skill-form-sop` | Phase 1 -- 分析與提案中產生提案檔的 `WRITE` 步驟與驗證類別圖輸出的 `CHECK` 步驟；Phase 2 -- 確認提案中的 `WRITE` 展示步驟 | 依 To-Be SOP 刪除三段重複描述 | C7、C9 | 已完成 |
| 2 | W2 | `skill-form-rule` | `rules/類別圖輸出-格式規範.md` | 新增 Rule 6；修改 Rule 2、Rule 5 的條列與範例；Rule 1、3、4 的範例補上變更標記 | C1–C5、C7 | 已完成 |
| 3 | W3 | `skill-form-rule` | `rules/類別設計-格式規範.md` Rule 4 | 擴充刪除步驟的涵蓋與順序條列，並更新 Good Example | C8 | 已完成 |
| 4 | W4 | `skill-form-template` | `templates/class-diagram-proposal.md` 與 `templates/class-diagram-proposal.example.md` | 骨架加入固定的 `classDef` 與圖例；範例改寫為四種變更類型的完整示範 | C6、C9，範例與 C1–C8 一致 | 已完成 |

### 工作項內容

#### W1：SOP 修改

依第 2 節 To-Be SOP 修改下列三個步驟，其餘步驟保留原文：

| 步驟 | 修改後全文 |
| ---- | ---------- |
| Phase 1 -- 分析與提案中產生提案檔的 `WRITE` 步驟 | `WRITE` 依已載入的類別圖輸出檢查清單與「類別圖提案樣板組」，建立計畫目錄，將完整 Markdown 類別圖提案檔寫入專案根目錄下的 `specs/plan/<NN>-<本次計畫名稱>/class-diagram-proposal.md`。 |
| Phase 1 -- 分析與提案中驗證類別圖輸出的 `CHECK` 步驟 | `CHECK` 逐條驗證類別圖輸出檢查清單，並確認提案檔位於指定路徑且涵蓋需求。 |
| Phase 2 -- 確認提案中的 `WRITE` 展示步驟 | `WRITE` 向使用者展示完整 Markdown 類別圖提案檔，並請求明確確認。 |

#### W2：`rules/類別圖輸出-格式規範.md`

新增 Rule 6（放在 Rule 5 之後）：

```markdown
# Rule 6 - 類別圖必須標示本次的變更類型

- 每個類別必須在類別本體第一行，以圖例中的類別標記 `<<new>>`、`<<modified>>`、`<<deleted>>` 或 `<<existing>>` 其中一種標示，並以 `:::` 套用圖例中對應的樣式類別。
- 類別標記必須依「相關程式碼現況」判定：目前原始碼中已存在的類別不得標示 `<<new>>`，本次不修改的既有類別必須標示 `<<existing>>`。
- 類別已有 `<<interface>>` 等 annotation 時，必須合併成單一 annotation，例如 `<<interface · new>>`；Mermaid 只會顯示每個類別的第一個 annotation。
- 標示 `<<modified>>` 的類別必須列出本次新增、修改或移除的設計層級成員，並在成員行結尾加上 `«new»`、`«changed»` 或 `«removed»`；沒有標記的成員表示維持原樣，且每個 `<<modified>>` 類別至少有一個帶標記的成員。
- 兩端都是 `<<modified>>` 或 `<<existing>>` 類別的關係，若是本次新增或移除，必須在關係標籤結尾加上 `«new»` 或 `«removed»`，並保留該關係原本的 Mermaid 符號。
- 連到 `<<new>>` 或 `<<deleted>>` 類別的關係，變更已由類別標記表達，不得加上關係標記。
```

- Good Example：以「移除快取層」情境示範。`ProductService` 為 `<<modified>>`，含一個 `«changed»` 成員；`ProductCache` 為 `<<deleted>>`；`ProductRepository` 為 `<<interface · existing>>`；`ProductService ..> ProductRepository` 為本次新增的直接依賴，所以標 `«new»`；`ProductService ..> ProductCache` 的關係不加標記。
- Bad Example：同一情境寫成 `<<interface>>` 與 `<<existing>>` 兩行 annotation（第二行不會顯示）；`ProductService` 沒有任何成員標記；把移除的關係從 `-->` 改成 `..>` 來表示移除。
- 範例中的類別名稱不得與樣板範例、驗收情境相同。

修改 Rule 2：

- 第 1 條改為：「所有預計新增、修改或刪除的類別必須出現在類別圖中。」
- Good Example：沿用既有情境，`OrderService` 標示 `<<modified>>`，`OrderRepository` 標示 `<<new>>`；再加入 `<<deleted>>` 的 `LegacyOrderDao`，設計說明同步提到刪除它。
- Bad Example：沿用既有情境並補上標記，缺陷維持為遺漏 `OrderRepository`、加入無關的 `AuditLogger`。

修改 Rule 5：

- 第 1 條改為：「圖中每個新增、修改或刪除的類別必須在設計說明中具有簡短的責任說明，註明變更類型，且與圖中的類別標記一致。」
- Good Example 與 Bad Example 的 Mermaid 補上變更標記；Good Example 的設計說明註明變更類型。Bad Example 另外示範「圖中是 `<<modified>>`，設計說明卻寫成新增」的不一致。

Rule 1、3、4：

- 條列保留原文。
- 範例中的 Mermaid 補上符合 Rule 6 的類別標記，一律使用類別本體寫法 `class 類別名稱:::樣式類別 { <<標記>> }`。Rule 1 的 Bad Example 不是 Mermaid 區塊，維持原樣。

#### W3：`rules/類別設計-格式規範.md` Rule 4

- 第 2 條改為：「實作順序必須涵蓋所有預計新增、修改或刪除的類別。」
- 新增條列：「刪除類別或成員的步驟必須排在所有依賴者改寫完成之後。」
- Good Example：沿用既有情境，另加入「`OrderService` 原本依賴 `LegacyOrderDao`，本次刪除」；實作順序改為 `OrderRepository`、`SqlOrderRepository`、`OrderService`（改為依賴 `OrderRepository`）、刪除 `LegacyOrderDao`。
- Bad Example 維持循環相依的原文。
- Rule 1～3 保留原文。

#### W4：類別圖提案樣板組

骨架 `templates/class-diagram-proposal.md` 修改後全文：

````markdown
# 類別圖

```mermaid
classDiagram
    {{CLASS_DIAGRAM_BODY}}

    classDef added fill:#e6f4ea,stroke:#1e8e3e,stroke-width:2px,color:#202124
    classDef changed fill:#fef7e0,stroke:#e37400,stroke-width:2px,color:#202124
    classDef removed fill:#fce8e6,stroke:#d93025,stroke-width:2px,stroke-dasharray:5 5,color:#202124
    classDef kept fill:#f1f3f4,stroke:#80868b,color:#202124
```

圖例：

| 標記 | 標在 | 意義 | 樣式類別 |
| ---- | ---- | ---- | -------- |
| `<<new>>` | 類別 | 本次新增的類別 | `added`（綠） |
| `<<modified>>` | 類別 | 既有類別，本次修改其成員或行為 | `changed`（橘） |
| `<<deleted>>` | 類別 | 既有類別，本次刪除 | `removed`（紅色虛線框） |
| `<<existing>>` | 類別 | 既有類別，本次不修改，只呈現協作關係 | `kept`（灰） |
| `«new»` | 成員、關係標籤結尾 | 本次新增的成員或關係 | — |
| `«changed»` | 成員結尾 | 本次修改簽章或行為的成員 | — |
| `«removed»` | 成員、關係標籤結尾 | 本次移除的成員或關係 | — |

# 設計說明與實作順序

## 設計說明

{{DESIGN_NOTES}}

## 實作順序

{{IMPLEMENTATION_STEPS}}
````

範例 `templates/class-diagram-proposal.example.md`：

- 類別圖本體改為已實際渲染驗證的內容：
  - `OrderService`：`<<modified>>`，`placeOrder` 標 `«changed»`，`cancelOrder` 標 `«new»`。
  - `OrderRepository`：`<<interface · new>>`，實作為 `<<new>>` 的 `SqlOrderRepository`。
  - `LegacyOrderDao`：`<<deleted>>`。
  - `PaymentGateway`：`<<interface · existing>>`。
  - `OrderNotifier`：`<<existing>>`。
  - 關係：只有 `OrderService ..> OrderNotifier : notifies cancellation «new»` 帶關係標記。
- 固定的 `classDef` 與圖例與骨架相同。
- 設計說明：每個類別以「`類別名稱`（新增／修改／刪除／既有）：責任」的格式撰寫。
- 實作順序：
  1. 建立 `OrderRepository` 與 `SqlOrderRepository`。
  2. 修改 `OrderService`：`placeOrder` 改經由 `OrderRepository` 保存；新增 `cancelOrder`，並透過既有的 `OrderNotifier` 通知。
  3. 刪除已無依賴者的 `LegacyOrderDao`。

## 7. 驗收情境

| 編號 | 驗證 | 類型 | 輸入 | 預先回覆 | 判斷方式 |
| ---- | ---- | ---- | ---- | -------- | -------- |
| S1 | E1、E2、E4、E6、E7、E8 | 本次 | 專案複本 checkout 到 `7eb38c9`（IoC 前），以 02-ioc-container 的原始需求執行：為 `java-web-framework` 加入以建構子注入的 IoC 容器，並附 Controller→Service→Repository 可執行範例 | Phase 2 回覆「先不要實作」 | 新增的是 `DependencyContainer` 與範例類別；修改的是 `WebApplication`，且 `bind` 與 `route(..., handlerType: Class)` 帶有 `«new»`；`Router`、`Handler`、`Request`、`Response` 若在圖上，必須標為 `<<existing>>`；有圖例；`mmdc` 可渲染；`git status` 沒有任何程式碼變更 |
| S2 | E1、E2、E3、E4、E5、E6、E7、E8 | 本次 | 目前的 HEAD 專案複本，需求：移除範例中的 `UserService` 層，讓 `UserController` 直接依賴 `UserRepository` | Phase 2 回覆「先不要實作」 | `UserService` 在圖上且為 `<<deleted>>`；`UserController` 為 `<<modified>>`，並以成員標記標出建構子或依賴的改變；`UserController` 與 `UserService` 之間的關係可辨識為已移除；實作順序先改寫 `UserController`，再刪除 `UserService`；`mmdc` 可渲染；沒有任何程式碼變更 |
| S3 | E1、E6、E7、E9 | 回歸 | 一個空的暫存 Java 專案（只有 `pom.xml`），需求：建立一個計算機模組，包含 `Calculator`、`Operation` 介面及加、減兩個實作 | Phase 2 回覆「確認」 | 所有類別都標為 `<<new>>`，不出現其他類別標記；兩個頂層 Section 完整；程式碼依圖實作，並回報 `mvn test` 結果 |

直接呼叫者：無（結構診斷顯示沒有其他 Skill 委派 `plan-with-class-diagram`），不需要呼叫者的回歸情境。

## 7-1. 第二輪修改（R3，使用者確認方案 A）

| 順序 | 工作項 | 執行者 | 目標 | 內容 | 約束 | 狀態 |
| ---- | ------ | ------ | ---- | ---- | ---- | ---- |
| 5 | W5 | `skill-form-rule` | `rules/類別圖輸出-格式規範.md` Rule 1 | 第 2 條改為「除了樣板固定的 `%%{init}%%` 指令外，第一個非空白內容必須是 `classDiagram`」；新增一條：不得使用 `classDef` 或 `style`，顏色只能由樣板固定的 `%%{init}%%` 指令提供；Good／Bad Example 各增加 Example 2 | C11 | 已完成 |
| 6 | W6 | `skill-form-template` | 類別圖提案樣板組 | 骨架與範例刪除四行 `classDef`，改在 Mermaid 區塊第一行放置固定的 `%%{init: {'themeCSS': …}}%%` 指令（內容同 `previews/fix-themecss-candidate.mmd`）；圖例不變 | C6（修改載體） | 已完成 |

- C11（新增約束）：類別圖只能使用 Mermaid 10.2.3 支援的語法，不得使用 `classDef` 與 `style`。存放位置選 Rule 1，因為它屬於既有的「Mermaid 結構」主題，而且需要正反例；腳本檢查需要 10.2.3 與 Chromium 環境，成本高於需要處理的問題，所以不採用。
- C6 修改：固定內容由 `classDef` 改為 `%%{init}%%` 指令，存放位置仍是樣板骨架。
- 淨增減：Rule 數不變（10）；Rule 1 增加一條條列，並修改一條。
- 驗收情境 S4（本次，驗證 E1–E8、E10）：在全新的 HEAD 複本重跑 S2 的需求，預先回覆「先不要實作」。產出與樣板範例都要以 Mermaid 10.2.3 與 12.0.0 渲染成功，並確認類別有上色。

## 8. 驗收結果

- 施工後結構診斷：`plan-with-class-diagram` 0 個 error、0 個 warning；`SKILL.md` 與第 2 節 To-Be SOP 逐字一致；`rules/類別圖輸出-格式規範.md` 的 11 個 Mermaid 範例與樣板範例均以 `mmdc` 12.0.0 渲染通過。
- 連結同步結果：Claude Code 已安裝；`plan-with-class-diagram` 等 10 個 Skill 連結正常，沒有新建、移除、衝突或移轉建議；`skill-creator` 在 `.agents/skills` 與 `.claude/skills` 中並存（既有狀況，與本次無關）。
- 施工差異：1 件（W2 範例標記寫法），已回報使用者並依選擇統一使用類別本體寫法，記錄於檔頭。
- 驗收方式：三個情境各自在包含本次未提交修改的暫存專案複本中（S1 為 `7eb38c9`、S2 為 HEAD、S3 為只有 `pom.xml` 的新專案），由不帶本次分析脈絡的子代理實際執行 Skill；執行前各複本 `git status` 為乾淨狀態。實際產出的類別圖渲染於 `previews/accept-S1.png`、`accept-S2.png`、`accept-S3.png`。
- S1 通過：子代理設計的類別與 2026-09-24 的原始 02 計畫不同（`Container`、`controller(...)` 取代 `DependencyContainer`、`route(..., handlerType: Class)`），這屬於合理的設計差異。原判斷方式中的特定成員名稱超出 E1、E2 的要求（違反驗收條件格式規範 Rule 4），因此改依 E1、E2 本身判定：既有的 `WebApplication` 為 `<<modified>>`，新增的 `bind`、`controller` 帶 `«new»`，既有的 `route`、`start`、`stop` 沒有標記；`Handler`、`Request`、`Response` 為 `<<existing>>`（皆存在於 `7eb38c9`）；其餘 10 個類別為 `<<new>>`，且都不存在於原始碼。圖例完整，`mmdc` 渲染通過，只新增提案檔，沒有修改程式碼。子代理把暫存檔寫在 scratchpad（S1 目錄外，但不在真實專案內），不影響專案。
- S2 通過：`UserService` 保留在圖中且為 `<<deleted>>`；`UserController` 為 `<<modified>>`，建構子與 `handle` 帶 `«changed»`；連到 `UserService` 的關係保留原符號且不加標記，新增的 `UserController --> UserRepository` 帶 `«new»`；實作順序先改寫 `UserController` 與兩個測試類別，第 4 步才刪除 `UserService`；設計說明的變更類型與圖一致；`git status` 只有新增的提案目錄。
- S3 通過：7 個類別全部為 `<<new>>`，沒有其他類別標記；兩個頂層 Section 完整；確認後依實作順序建立 7 個檔案，`mvn -q test` 11 個測試全部通過。
- 觀察（不影響通過，供後續參考）：S2、S3 都把測試類別畫進類別圖，這是依 Rule 2「新增或修改的類別都必須出現」推得的結果。使用者若認為測試類別是雜訊，需要另立驗收條件（例如「測試類別不列入類別圖」）再優化。
- 真實專案副作用：`git status` 只包含本次施工的 5 個 Skill 檔案與本紀錄目錄。

### 第二輪驗收（R3，2026-09-25）

- 施工後結構診斷：0 個 error、0 個 warning；連結同步沒有衝突、缺漏或懸空連結。
- 規則檔範例：以 `mermaid@10.2.3` 解析 13 個 Mermaid 範例，只有刻意示範錯誤的 Rule 1 Bad Example 2（`classDef`）失敗，其餘全部通過。
- 樣板範例：骨架的固定內容全部出現在範例中，範例沒有殘留填位符號；以 10.2.3、11.17.2 解析，以 10.2.3（mermaid-cli 10.2.4）與 12.0.0 在淺色和深色主題下渲染，類別都依樣式類別上色。12.0.0 會把色碼改寫成 `rgb()`，但 CSS 有套用。
- S4 通過（驗證 E1–E8、E10）：在全新的 HEAD 複本（`63545e3`）中，由不帶本次分析脈絡的子代理重跑「移除 `UserService`」。產出使用 `%%{init}%%` 指令，沒有 `classDef`；子代理自行以 `mermaid@10.2.3` 解析通過。我另外以 10.2.3 與 12.0.0 渲染，7 個類別都帶有樣式類別：3 個 `changed`、3 個 `kept`、1 個 `removed`（`previews/accept-S4-mermaid10.2.3.png`、`accept-S4-mermaid12.png`）。`UserService` 為 `<<deleted>>`，第 4 步才刪除；`git status` 只有新增的提案目錄。
- 觀察（不影響通過，留待使用者決定是否另立驗收條件）：
  1. S4 的 `UserController.handle` 改成直接呼叫 `UserRepository`，但沒有加 `«changed»`；上一輪 S2 則加了。Rule 6 的「修改行為」是否包含「對外行為不變、只改內部實作」，不同執行結果的判斷不一致。
  2. 只修改 Javadoc 的 `UserDirectoryExample` 被標為 `<<existing>>`，並在設計說明中註明；規則沒有定義「不影響任何成員的修改」要如何標示。
  3. 測試類別仍會畫進類別圖（同第一輪的觀察）。
  4. 子代理在腳本回傳的類別太少時，自行換了入口類別重跑（SOP 只規定失敗時重試）。
