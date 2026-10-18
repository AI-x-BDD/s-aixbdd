# 使用者要求逐項核對

本表逐條回到使用者原提示與本輪補充；技術通過、代理觀察與使用者驗收不互換。情境結果與版本以 acceptance.md 為準。

| 使用者要求 | 具體處理位置／證據 |
| --- | --- |
| 使用專案 skill-engineering，先藍圖確認才施工 | blueprint.md 確認紀錄、construction/ W1–W9、施工紀錄 |
| Herdr 問功能並找 Claude Code 討論 | implementation.md、claude-rhythm-review.txt；唯讀檢視不冒充看片 |
| 最新 CH2 動態敘事為品質地板，正式／歷史／未驗證分清 | research.md、WORKFLOW／README／HANDOFF／motion README、當前交付摘要 |
| 內容、觀眾、來源、限制 | 製作計畫樣板、輸入與能力 Rule 1、S1/S2 |
| 查當次動畫、配音、音訊與影片理解能力 | 輸入與能力規範、能力實測；直接連續聽看本次未驗證 |
| 實際視聽方向、理由取捨；既定方向沿用 | 敘事 Rule 1；退款兩候選／植物既定淺綠原音；S1/S2/S3 |
| 旁白、逐幕分鏡、實際語音時間 | 分鏡與焦點樣板、最終 timeline／對齊、S9 |
| 代表片修正後才依授權製作 | Phase 2/4 確認閘門；S3 兩候選與正式 sentinel 保護；S1 測試預設回覆有註明 |
| 渲染、燒錄字幕、規格與來源一致 | motion_project CLI、實際字幕 encode/decode 回歸、S1/S2/S7/S9 |
| 全片焦點、列舉逐項、停留有觀看對象 | 獨立焦點契約、敘事 Rule 2/3、S5 及退款逐項修正 |
| 動作有語意、身份保留、路徑不壓字、鏡頭不裁重點 | 敘事 Rule 2/4、S6/S8 實片修前修後證據 |
| 字幕預設燒錄且可改 | 可改 SRT/VTT 來源；長字幕與未燒錄的實片負例 S9 |
| 技術／畫格／音訊／直接聽看／使用者分開 | 評審 Rule 3、評審樣板五列、兩新主題實際評審 |
| 不以抽幀、ASR、播放、音訊 hash 冒充直接聽看 | 輸入能力及成片評審限制；browser-check.json 只證可播下載 |
| 實際編碼片中途、尾端、移動過渡；改後重建 | 成片 Rule 1/2、S7、S8/S9、S12 新成片與序列 SHA |
| 不固定深色／九幕／113 秒／49 段／CH2 名稱或本機路徑 | 新白暖退款三幕約24秒、淺綠植物四幕13.5秒；通用 profile／空白骨架 |
| 區分 Skill、第三方能力、工具、素材；不靠舊成片／本對話 | Skill 只有規則樣板與流程；專案工具／本片素材另置；S1/S2 無本次分析脈絡的代理、S10 搬移 |
| 不把 CH2 專用工具改名冒充通用 | 新 motion_project／motion_checks／空白 Remotion 骨架；兩主題實跑，舊 CH2 程式保留歷史重建 |
| 第三方原文、來源、版本、授權 | videos/.agents/skills/來源.json；motion-art-direction 補同 revision LICENSE，不改原文；官方 Remotion Skill 固定版按需取得 |
| 結構檢查與兩側實體同步 | audit-agents/claude.json；scripts/sync-skills.sh --check；template-check.json |
| 故障要能發現並阻擋、工具缺失不說完成 | S4–S9；18工具測試；實際故障編碼與修復，未混寫測試層級 |
| 播放下載同片、來源與檢查紀錄、使用者驗收 | deliver 的相同 MP4/SRT/VTT 與 HTML；原 CH2 已接受／新 Skill 使用者未驗證分開 |
| 不刪歷史、不重製 CH2、不 commit/push | baseline.json／preservation.json、CH2 MP4 SHA／Git HEAD 保護；失敗測試版本保留 |
| 新補充：有核心、變動與靜止有輕重，落定時突出重點 | 敘事 Rule 2；分鏡新增核心詞／動作起訖／穩定區間，S12 植物修正與退款回歸 |
| 新補充：不能移動途中無理由硬切，不能流水帳套版 | 最終 timeline 倒推，逐切點連續幀／位置／落定／停留核對；一幀標題物件錯幕也需修正；主觀連續節奏維持未驗證 |
| 再次提醒：認真讀提示，不能有提示卻未處理 | 本表對應原提示與後續補充；rhythm-addendum.md 記失敗、修法、Claude 複查與實片重驗，不能只加一句注意節奏 |
