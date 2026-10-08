---
name: plan-with-class-diagram
description: 實作或重構會新增或變更類別的功能前，必須使用此 Skill；先提出 Mermaid 類別圖提案並取得使用者明確確認，再依已確認的類別圖與相依順序實作。使用者要求先規劃類別或先畫類別圖（class diagram）再實作時使用。
---

# SOP

## Phase 1 -- 分析與提案

1. `READ` 使用者需求、專案規範、Java 原始碼路徑（若有），以及專案根目錄下既有的 `specs/plan/` 計畫目錄（若存在），建立「專案輸入」。
2. `THINK` 若「專案輸入」顯示本次需求涉及 Java 原始碼，依需求與原始碼路徑選定完整名稱的入口類別。
3. `DELEGATE` 若已選定 Java 入口類別，在本 Skill 目錄執行 `uv run --script scripts/inspect_java_classes.py --project-root <專案根目錄絕對路徑> --entry <完整類別名稱>`，從標準輸出取得 JSON 類別結構摘要；若缺少 `uv`，依 https://docs.astral.sh/uv/getting-started/installation/ 的目前平台安裝說明安裝後重試，安裝失敗時回報原因並停止此步驟。
4. `CHECK` 執行腳本時確認退出狀態為零且標準輸出為可解析的 JSON，並檢視未解析引用、方法本體引用及截斷狀態；失敗時依標準錯誤輸出修正入口並重試，仍失敗時回報原因。
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
