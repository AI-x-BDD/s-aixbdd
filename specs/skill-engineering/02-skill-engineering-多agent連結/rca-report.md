# 根因報告：skill-engineering－多agent連結

- 紀錄目錄：`specs/skill-engineering/02-skill-engineering-多agent連結/`
- 問題證據：本次對話上下文（使用者訊息「我可能會用 Codex CLI 或 Claude Code，不一定每次都會用同一個 agent 來做 Skill engineering」「之前 9 個 skill 是用 Codex 建立的」「用了 Skill 還要等你來發問，那我為什麼要建立 Skill」）；Claude Code 官方文件「Choose where skills load」表格；Codex 原始碼 `codex-rs/ext/skills/src/host_roots.rs`（讀取專案 `.agents/skills` 並跟隨 symlink）；vercel-labs/skills 原始碼 `src/agents.ts`（以 `~/.claude` 是否存在偵測 Claude Code）；本次 session 的可用 Skill 清單在建立 symlink 前後的差異

## 1. 使用者回報的問題

使用者輪流以 Codex CLI 與 Claude Code 執行 skill engineering。以 skill-engineering 建好或修改 Skill 後，Skill 只存在 `.agents/skills`，Claude Code 看不到；需要使用者自己發現並手動建立 `.claude/skills` 的 symlink。使用者希望 skill-engineering 能自行判斷是否需要 symlink，而且過程中不詢問使用者：來源一律放在 `.agents/skills`，並依主流工具的做法，以這台電腦是否安裝 Claude Code 決定是否建立 symlink。

## 2. 驗收條件

| 編號 | 驗收條件 | 來源 | 適用範圍 | 驗收情境 |
| ---- | -------- | ---- | -------- | -------- |
| E1 | 不論執行的 agent 為何，新建 Skill 的來源一律寫在專案的 `.agents/skills/<name>/`，不寫入 `.claude/skills` | 本次 | 通用 | S1 |
| E2 | 這台電腦安裝了 Claude Code（`CLAUDE_CONFIG_DIR` 或 `~/.claude` 存在）時，施工後 `.agents/skills` 中每個 Skill 在專案的 `.claude/skills/` 都有同名、以相對路徑指向來源的 symlink，`.claude/skills/` 不存在時自動建立；沒有安裝時，不建立任何目錄或 symlink；兩種情況都不詢問使用者 | 本次 | 通用 | S1、S2 |
| E3 | `.claude/skills/` 中與來源同名的實體目錄，或指向其他位置的 symlink，保持不變並回報給使用者 | 本次（使用者同意的提案） | 通用 | S1 |
| E4 | 指向 `.agents/skills`、但來源已不存在的 symlink 會被移除 | 本次（使用者同意的提案） | 通用 | S1 |
| E5 | `.claude/skills/` 中只存在於該處、採模組化格式的實體目錄 Skill，只回報「建議移到 `.agents/skills` 並改用 symlink」，不自動搬移 | 本次（使用者同意的提案） | 通用 | S1 |
| E6 | 可以在不修改任何檔案的情況下檢查 symlink 是否齊全，有缺漏或失效時以非零狀態結束 | 本次（使用者同意的提案） | 通用 | S2 |
| E7 | 先定義驗收條件、優化時先取得根因確認、確認藍圖後才施工、施工後以子代理實跑驗收的既有流程維持不變 | 既有 | 通用 | S1 |

## 3. 落差

| 驗收條件 | 預期 | 實際 | 證據 |
| -------- | ---- | ---- | ---- |
| E1 | SOP 規定來源目錄 | SOP 只要求「確定目標 Skill 所在的 skills 目錄」，沒有規定來源必須是 `.agents/skills` | 觀察：`skill-engineering/SKILL.md` Phase 1 步驟 2 |
| E2 | 施工後 Claude Code 可使用新 Skill | 建立 skill-engineering 與 skill-form-description 後，本 session 的可用 Skill 清單沒有這兩個 Skill；建立 symlink 後才出現 | 觀察：本次 session 的可用 Skill 清單在建立 symlink 前後的差異 |
| E3–E6 | 有處理衝突、失效連結、移轉建議與檢查模式的步驟 | Phase 5 沒有任何與 symlink 相關的步驟 | 觀察：`skill-engineering/SKILL.md` Phase 5 步驟 1–12 |

## 4. 演練表

`skill-engineering`（以本專案新建 Skill 的流程演練；這台電腦安裝了 Claude Code）：

| 步驟 | 應載入 | 實際載入 | 應產出 | 實際產出 | 判定 |
| ---- | ------ | -------- | ------ | -------- | ---- |
| P1-1 | 無 | 無 | 使用者需求 | 觀察：已讀取 | 一致 |
| P1-2 | 無 | 無 | 目標 Skill 的來源目錄固定為 `.agents/skills` | 觀察：SOP 只要求「確定」目錄，沒有判斷依據；S1、S3 驗收時使用者需求恰好指定 `.agents/skills`，所以放對位置 | 偏離 |
| P1-3～P1-12 | 依各步驟 | 觀察：依各步驟 | 驗收條件等 | 觀察：與消費端無關 | 一致 |
| P2～P4 | 依各步驟 | 觀察：依各步驟 | 根因報告、工程藍圖 | 觀察：藍圖的驗收條件與工作項沒有涵蓋消費端 | 一致 |
| P5-1～P5-4 | 施工委派檢查清單 | 觀察：已使用 | Skill 部位寫入來源目錄 | 觀察：只寫入 `.agents/skills` | 一致 |
| P5-5～P5-12 | 無 | 無 | 在 Claude Code 可使用新 Skill | 觀察：沒有任何步驟建立 symlink，新 Skill 不在 Claude Code 的可用清單中 | 偏離 |

第一個偏離點：P1-2（`THINK` 確定目標 Skill 所在的 skills 目錄）。後段的 P5 偏離源自同一個缺口：整份 Skill 都沒有表達「Skill 要給哪些 agent 使用」這個預期。

## 5. 根因

| 編號 | 位置 | 缺陷類型 | 說明與證據 | 反事實檢驗 |
| ---- | ---- | -------- | ---------- | ---------- |
| R1 | `skill-engineering`／`SKILL.md`／Phase 1 步驟 2 與 Phase 5 | 缺失 | 觀察：Phase 1 步驟 2 沒有規定來源目錄；Phase 5 沒有依消費端建立或檢查 symlink 的步驟；五個 RuleFile 與兩組樣板都沒有提及消費端 agent。觀察：官方文件列出的 Skill 位置只有 `.claude/skills` 系列，不含 `.agents/skills`。推論：只要執行者或使用者需求沒有特別指定，Skill 的來源位置與 Claude Code 能否使用都無法保證（依據上列三項觀察）。 | 假設 P1-2 固定來源為 `.agents/skills`，且 Phase 5 依這台電腦是否安裝 Claude Code 自動同步 symlink：新 Skill 會在 Claude Code 出現（觀察：手動建立 symlink 後即出現），E1、E2 滿足；同步時若也處理衝突、失效連結與移轉建議，E3–E6 滿足；前四個 Phase 的流程不受影響，E7 滿足。 |

## 6. 被排除的假設

| 假設 | 缺陷類型 | 排除依據 |
| ---- | -------- | -------- |
| H2：description 寫法讓 Claude Code 沒有觸發 Skill | 觸發缺陷 | 觀察：建立 symlink 後，同一份 description 立即出現在可用清單中；問題在載入位置，而不是觸發 |
| H3：Claude Code 不支援 `.agents/skills`，屬於環境限制，Skill 無從處理 | 非 Skill 問題 | 觀察：官方文件支援在 `.claude/skills` 放指向其他目錄的 symlink；推論：這個限制穩定且已知，Skill 可以用確定的方式處理（依據該項觀察），因此缺口在 Skill |
| H4：`skill-form-description` 建立 Skill 目錄時選錯位置 | 交接缺陷 | 觀察：`skill-form-description` Phase 2 步驟 1 只建立呼叫者指定的「目標 Skill 目錄」；位置由 skill-engineering 決定 |

## 7. 影響範圍

無：沒有其他 Skill 委派 `skill-engineering`（結構診斷的呼叫關係中 `callers` 為空）。

## 8. 待確認事項

1. 第 2 節的驗收條件是否正確、完整？（E2 已依使用者確認的「偵測是否安裝 Claude Code、自動處理、不詢問」規則改寫）
2. `.agents/skills` 中的每個 Skill 是否都要連結到 Claude Code，或只連結模組化格式的 Skill？（使用者回覆：全部都連；已反映於 E2 的「每個 Skill」）
3. `.claude/skills/skill-creator` 是實體目錄；依 E3 保持不變並在每次同步時回報為「並存」，是否符合預期？
4. 是否同意第 5 節的根因 R1？

使用者回覆（2026-09-25）：同意 R1。E2 依使用者要求改為「偵測是否安裝 Claude Code、自動處理、不詢問」；`.agents/skills` 中的每個 Skill 都連結；同名實體目錄保持不變，同步報告以一行回報「並存」。
