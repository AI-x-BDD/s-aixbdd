# 影片製作流程入口

新章節、新主題、整體改版或聲畫焦點修正，使用 [video-production Skill](../.agents/skills/video-production/SKILL.md)。**通用流程與品質判準以該 Skill 及其按需載入部位為準**；本頁只保留入口摘要。只重建已定版影片時讀 [README](README.md)。

驗證狀態：先前通過的是工程與部分情境測試，未證明美術選擇及 CH2 品質下限。美術方向流程已依確認的 [修改藍圖](../specs/skill-engineering/15-video-production-美術方向選擇與驗收/blueprint.md) 修改並完成限定情境補驗（[結果與限制](../specs/skill-engineering/15-video-production-美術方向選擇與驗收/acceptance.md)）；使用者實際驗證仍為「未驗證」。既有 CH2 影片的接受紀錄另列，不混為 Skill 已驗收。

## 從素材到交付

1. 理解內容、觀眾、理解目標、來源與製作授權，查核當次實際工具能力。
2. 先檢查本機固定風格庫，再依內容從庫內 ID 選出方向、說明推薦與取捨，製作同內容有聲候選供確認；已有方向時沿用並檢驗本片適配。
3. 依實際配音對齊旁白、逐幕動態與獨立焦點契約。
4. 製作、燒錄字幕及技術守門；依實際成片檢查中途、尾端與過渡，修正後重建複查。
5. 交付同一影片的播放／下載、製作來源、檢查結果及限制，另記使用者驗收。

工具與命令見 [README](README.md#新章節與其他主題)。新影片使用獨立工作區及設定；歷史 CH2 建置入口保留。Skill 本身不包含編碼環境，搬移時需要工具包、鎖定依賴、合法第三方與新素材；平台及當次能力由實測確定。

## 既有能力分工

| 需求 | 精確入口 |
| --- | --- |
| 整體影片流程 | [video-production](../.agents/skills/video-production/SKILL.md) |
| 固定風格庫與可播放預覽 | [42 個風格預覽](style-library/index.html)、[範圍與選用檢查](style-library/README.md)；7 可用解說＋35 藝術，研究及弱項不算正式候選 |
| 內容理解與分鏡 brief | [storyboard](.agents/skills/storyboard/SKILL.md) |
| 構圖與排印 | [editorial presentation-design](.agents/skills/presentation-design-editorial/SKILL.md) |
| 動態意圖與主從 | [motion-art-direction](.agents/skills/motion-art-direction/SKILL.md) |
| 連續動態實作 | [固定版 Remotion 與授權說明](motion/README.md#官方-skill-與授權) |
| 選用診斷輔助 | [presentation-design](.agents/skills/presentation-design/SKILL.md)，取得可用授權證據後才使用；基本流程由主代理依自建規範評審 |

第三方原文保持原樣；固定版、雜湊及授權見 [.agents/skills/來源.json](.agents/skills/來源.json) 與 [motion/來源.json](motion/來源.json)。兩份 presentation-design 同名，按表中精確路徑載入。

## CH2 基準與歷史

使用者已接受 CH2 最後 B 深色＋M2 動態敘事影片及製作過程，作為最低完成標準；深色、幕數與片長屬於該個案。現行狀態見 [CH2 交付狀態](../docs/過程/CH2/影片/製作紀錄/設計/新流程測試/交付狀態.md)。

流程演進證據保留於 CH2 製作紀錄；本次整理前的流程全文另存 [工程紀錄](../specs/skill-engineering/14-video-production-建立/construction/WORKFLOW.before.md)，只作歷史參考。

## 固定風格庫守門

新片先執行 `python3 scripts/style_library.py check --library style-library`，在本片設定啟用 `style_library_required = true` 並記錄 style_selection；缺庫、來源變動、預覽過期、未知 ID 或過期選用紀錄會阻擋建置及交付。原庫無聲示範只用於選型，本片仍須製作有配音與燒錄字幕的代表片。[整合與驗收紀錄](../specs/skill-engineering/16-video-production-固定風格庫整合/acceptance.md)。
