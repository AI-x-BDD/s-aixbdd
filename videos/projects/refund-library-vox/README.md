# 退款流程編輯式證據桌面候選（B）

以 video-production Skill 製作的比較用候選。固定風格 ID：`y2_vox`（編輯式資訊拼貼），選用紀錄見 `style-selection.json`。旁白、語音與對齊沿用原退款三段（24.433 秒），只換畫面方向；未經使用者確認，不取代 A-r2。

## 來源

| 檔案 | 用途 |
| --- | --- |
| `project.toml` | 本片設定：風格庫守門、內容安全區（y<570）與字幕區、取樣時間 |
| `style-selection.json` | 綁定 catalog SHA 的庫內選用、內容理由與改編方法 |
| `materials/content.json`、`voice.m4a`、`alignment.json`、`model-provenance-reference.json` | 從 A-r2 素材原樣複製；雜湊與原件相同 |
| `materials/focus.json` | 依實際字元時間手寫的旁白焦點契約，17 段、半開區間、無寬限；不從繪圖狀態推導 |
| `materials/labels.json` | 焦點物件 id 與名稱 |
| `scene_state.py` | 唯一幾何來源：桌面紙件、鏡頭落點、12fps 步進的標記進度與畫面 active；輸出 `materials/state.json` |
| `materials/state.json` | 逐幀狀態；renderer 只依此繪製（可由 `scene_state.py` 逐位元重現） |
| `src/Root.tsx`、`src/index.ts`、`remotion.config.ts` | 繪圖程式來源；複製進建置工作區使用 |

`scene_state.py` 與上述繪圖程式以 profile 的 `visuals` 納入來源指紋，改動後舊 state、成片與評審即過期。

## 畫面設計摘要

- 一張桌面世界：原訂單、退款申請、審核人、退款條件、付款紀錄都是自繪紙件，名稱以黑底撕邊標籤印在紙上，隨物件移動。
- 揭示動作輪換：紅底線、手畫圈、螢光筆、蓋章、紅線、打勾、撕線；每拍只標一項，標記進度以 12fps 步進，鏡頭 30fps 平滑。
- 鏡頭依當下要讀的物件反算落點；交棒沿紅線追蹤，「通過後，」句讀處硬切回原訂單。
- 退款單是原訂單下緣的撕線聯：先寫上名稱並畫撕線，再撕下到空白桌面，表達由訂單產生退款單。
- 焦點物件與其所屬單據維持清楚，其他紙件覆一層桌面色降階；已講過的標記轉為低彩度。
- 桌面鏡頭只在 y<570 的內容視窗內呈現，其下為乾淨的字幕保留區。
- 訂單、條件與付款紀錄的細節都是灰色佔位條，沒有杜撰商品、條件或金額。

## 狀態與限制

- 交付、評審與比較頁由 root 負責；目前紀錄見 `videos/build/refund-library-vox/records/` 與 `output/`。
- `remotion.config.ts` 的 `setBrowserExecutable` 指向本機 `/private/tmp/.remotion/...` 的 headless shell，是本機 runtime 設定，不是 Skill 或工具的固定路徑；重建方式見 `重建.md`。
- 本次檢查方法：實際編碼畫格、逐幀狀態與焦點契約、音訊解碼與封裝分析。
- 使用者已選擇本次 B「編輯式證據桌面」方向，版本與範圍見 `方向確認.json`；未擴張為全流程驗收。
- 只在 macOS 實跑；其他平台未驗證。
