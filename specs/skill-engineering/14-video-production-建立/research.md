# 影片製作 Skill 蒐證

日期：2026-10-18。模式：新建。僅寫本次設計紀錄；未建立 Skill、未改工具、未刪資料、未重製影片。

## 使用者已確認的基準

使用者：「這個過程和產生的結果可以當作地板完成度」「影片其實都已經交付出去了，成品也已經 OK」。因此 CH2 最後 M2 成片已獲使用者接受。這不表示 AI 曾直接聽看全片，也不表示新 Skill 已驗證。

正式成片：`videos/build/ch2-workflow-test/動態正式版/輸出/影片.mp4`。既有交付紀錄的 SHA-256：`a0f45efe3a37026fa19ab02de1bdbca43ed6d85d21cfd037b5b09953a43baa85`。本輪不重建、不播放或重新驗收該影片。

## 已讀材料與分類

| 材料 | 用途／結論 |
| --- | --- |
| `videos/WORKFLOW.md` | 內容→方向→分鏡→製作→評審的流程；須補成可獨立啟動、可恢復的 Skill |
| `videos/README.md`、`HANDOFF.md`、`motion/README.md` | 本機建置、工具依賴、字幕、舊基準與動態片區別 |
| `videos/projects/ch2-workflow-test/project.toml` 及 prepare/render/review/runtime/setup Python | 正式 M2 工具鏈，接受 profile 但不代表支援任意影片 |
| `videos/motion/src/Root.tsx`、`motion-state.ts`、`lib.tsx`、`Motion.tsx` 及 `scripts/export-state.cjs` | 實際動畫／字幕／共用狀態；CH2 構圖與語句不可當通用規格 |
| `videos/scripts/video.py`、`align.py`、`capability_probe.py`，`videos/tests/check_motion.py` | 素材、對齊、替代檢查與故障注入的重用邊界 |
| CH2 新流程測試之交付狀態、動態提案、全片分鏡、全片評審、聲畫能力與焦點稽核 | 正式成果、選版歷史、實際畫面缺陷與能力限制 |
| 根目錄 `.agents/skills`、`.claude/skills`、`skills`，`videos/.agents/skills` 的 name/description | 沒有負責從內容到成片交付的現成 Skill；新建編排 Skill 合適 |

## 既有 Skill 分工

| Skill／目錄 | 保留責任 | 新 Skill 責任 |
| --- | --- | --- |
| `videos/.agents/skills/storyboard` | 內容理解目標與製作 brief | 將媒體建議轉成可播放影片的逐幕設計 |
| `presentation-design-editorial` | 視覺設計、排印、層級 | 根據內容比較方向，與配音／時間整合 |
| `motion-art-direction` | 動態意圖、節奏、主從 | 對接真正 renderer 與逐段時間 |
| `presentation-design` | 診斷觀眾負荷與溝通效果（選用，須有可用授權證據） | 主代理依自建規範完成評審；外部診斷僅輔助 |
| 官方 Remotion Skill（固定版本快取） | 動畫實作方法 | 指定輸入、輸出及實際成片驗證 |
| `frontend-slides`、`impeccable` | HTML 簡報、介面設計 | 不當成 MP4 製作與影音驗收的替代品 |
| 根目錄 skill-engineering 系列 | Skill 工程 | 用來建立本 Skill，不在日常製片時反覆跑 Skill 工程 |
| course-transcript-notes 等個人工具 | 課程筆記與文字工作 | 需要時接收其產出，不把影片任務改成筆記任務 |

兩份 presentation-design 的 upstream name 相同，必須用依賴清單中的精確目錄載入。第三方原文不修改；Remotion Skill 原文無再散布授權，沿用固定版下載與雜湊方式，不複製進新 Skill。

## 必須通用化的工具缺口

| 實際位置 | 問題 | 藍圖處理 |
| --- | --- | --- |
| `motion/src/Root.tsx`、`scripts/export-state.cjs` | 2825 影格、25fps、1600×900 寫死 | 新影片各自擁有 Remotion workspace，從片設定與時間軸取規格 |
| `motion/src/motion-state.ts` | 固定 SCENES、B 色碼、片語及 BUILD 映射 | 保留為 CH2 個案；新片依分鏡撰寫自己的場景／狀態，不套舊主結構 |
| `prepare_motion.py` | 共用 `motion/public`，且沿用要求 SVG 的素材檢查 | 新影片 workspace 隔離；Remotion 檢查不要求無關 SVG／qlmanage |
| `motion_runtime.py` | MOTION 路徑固定，契約／名稱表取 CH2 所在目錄 | 新工具從明確 profile 解析，缺欄位直接失敗 |
| `review_motion.py` | 固定影格數／片長／尺寸／安全區、RECORDS、B-M2、交付頁 | 新工具讀本片規格、安全區與紀錄位置；交付頁只連本片 |
| `check_motion.py` | 匯入 CH2 模組、固定 p1／rule0 測試物件 | 新工具測試從獨立 fixture 與契約選取對象，保留舊測試 |
| `capability_probe.py` | 固定日期、課程辨識提示與能力宣告 | 新工具記實際日期、詞彙與當次能力證據；不憑程式推定 AI 模態 |
| `video.py` check | macOS、SVG／qlmanage、say 依賴與錄音分支耦合 | 新 Remotion 工具按使用模式檢查；初版支援仍明列 macOS，其他平台未驗證 |

不能只改名稱或提供一個新的 profile 就宣稱以上已解決。本輪只提出調整方案。

## 文件落差

`交付狀態.md`、WORKFLOW 開頭、全片評審末段及 build `驗證.json` 仍有「待使用者試看／驗收」文字。應新增本次使用者接受紀錄，保留 AI 未直接聽看的事實；歷史階段文字仍保留日期與當時意義。藍圖確認後才更新現行摘要，不改成「AI 已連續聽看」。

`聲畫能力與焦點稽核.md` 的 finish.py／SVG 敘述屬前一階段；動態提案的代表片段與部分舊鏡頭描述屬選版歷史。新 Skill 以最後分鏡、評審及最新使用者決定為準，舊紀錄不刪。

## 證據強度

- 已有個案證據：M2 九幕成片、原音封裝、燒錄字幕、逐段狀態、故障注入與抽幀修正；本次使用者接受為最低標準。
- 本輪實際完成：讀檔、Skill 盤點、Herdr 呼叫 Claude Code 討論、設計紀錄。
- 尚未完成：可重用 Skill、新通用工具、新主題實跑、無上下文代理驗收、其他機器／平台驗證。
- 不把既有影片驗證結果當新 Skill 的行為驗收。

## Herdr／Claude Code 討論

已實際執行 `herdr --skill`，確認在 Herdr 環境，並以既有 Claude Code agent `ch2-readme-review` 進行唯讀討論；沒有另開環境或讓對方修改檔案。

第一輪討論採納：新增流程編排 Skill、第三方按精確路徑載入、工具留在 videos、每片 workspace/public 隔離、數字與契約參數化、增加不同片長／幕數／配色與六類故障情境。

經主代理校正的建議：

- 對方提議「使用者已有聲試看」，但使用者只明確說接受成果；紀錄只寫接受，不推定觀看方式。
- 對方建議先 commit 快照；使用者明確禁止，本輪不做。後續以包含未提交內容的暫存複本及指紋比對保護。
- 固定標題、裁切線與換字先出後入是本片可用手法，不設為跨影片不可變規則。
- 未來可用工具若支援直接影音輸入，應實測後記錄；不能永遠禁止「已聽看」宣告。
- 授權資訊不完整的依賴須保留來源並查核，不憑缺少 LICENSE 檔就自行推定全部無授權，也不擴張成本輪清理工作。

工程藍圖交由同一 Claude Code 再做唯讀漏項檢查，提出四項缺口，已修訂：

1. 專案工具與文件工作不屬 Skill 部位施工，改列 A1／A2 關聯工作；A1 先通過再啟動 Skill 施工，不曲解 skill-form-* 的職責。
2. 授權不明的診斷 Skill 改為選用，不能加入可攜包；主代理以自建成片規範完成評審。必要第三方依賴補固定版本與經查核的授權資料。
3. 配音對齊明定使用 align.py 與明確指定的模型路徑／revision／雜湊；驗收環境預置，缺少時停止，不靠 CH2 快取或估時冒充。
4. 增加 init 建立本片 workspace、profile、public 與鎖定依賴安裝；新片與搬移情境都檢查初始化。

本輪設計檢查：五階段、43 步、18 驗收條件、20 約束、11 情境；本地文件連結與 diff 格式檢查通過，根目錄 Skills 未改且同步檢查一致。CH2 成片實際 SHA 與上述最終交付 SHA 相同。本輪仍不是新 Skill 行為驗收。

Claude Code 第二輪複查判定上述 B1–B4 已解除。其另指出 A1 不應依賴完整 Skill 情境才完成，已改為先獨立工具 fixture，再於 W10 跑完整 Skill 情境，避免循環前提。設計審查結論不代表已施工或實跑通過。
