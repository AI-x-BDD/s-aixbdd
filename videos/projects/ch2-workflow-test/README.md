# CH2 新流程測試

使用者已選 B 深色配色，並於 2026-10-18 選定 M2 動態敘事套用九幕。維持 113 秒、原旁白與音訊；字幕直接繪進畫面。最新完成範圍與限制只看 [交付狀態](../../../docs/過程/CH2/影片/製作紀錄/設計/新流程測試/交付狀態.md)。交付頁：<http://127.0.0.1:60071/預覽/交付.html>。

從 repo 根目錄重建（先依 [素材說明](../../../docs/過程/CH2/影片/素材/README.md) 提供原始 MP3）：

```sh
make -C videos setup
make -C videos check test
make -C videos render
make -C videos preview
```

預設 `project.toml` 使用 Remotion `Full-Motion`，輸出 `build/ch2-workflow-test/動態正式版/`。`prepare_motion.py` 從原始來源準備九幕配音、字幕與字元時間，不需舊成片。`render_motion.py` 渲染含字幕的無聲畫面，再複製原 AAC 音訊；`review_motion.py` 核對 2825 影格與 49 段主焦點、來源指紋、完整解碼、音訊流並擷取實際成片。通過後才更新交付頁。

動態程式、官方 Skill、版本與授權見 [motion](../../motion/README.md)。原固定構圖 B 保留在 `正式版/`，重建須明確指定 `PROJECT=projects/ch2-workflow-test/focus-baseline.toml`（使用 `finish.py` 燒錄字幕及舊 SVG 稽核）；此基準重建只更新 `預覽/基準.html`，不覆寫最新動態交付頁。`選定方向.json` 保留 B 舊來源與動態決策，不將後來改版冒充昨天原版。

技術、逐影格狀態與靜態抽幀檢查不等於 AI 直接聽看；直接聽感、連續觀看的節奏與舒適度仍需使用者試看。

以下保留候選重建方式與歷程。

個案紀錄：[新流程測試](../../../docs/過程/CH2/影片/製作紀錄/設計/新流程測試/交付狀態.md)。旁白、原始音檔剪接與字元時間沿用 CH2，維持 113 秒。舊來源及原成片不覆寫。

從 repo 根目錄重建：

```sh
# 沒有 render 正在讀取候選來源時，才重新生成圖稿。
videos/.venv/bin/python videos/projects/ch2-workflow-test/design.py
make -C videos render PROJECT=projects/ch2-workflow-test/proposals/a.toml
make -C videos render PROJECT=projects/ch2-workflow-test/proposals/b.toml
make -C videos render PROJECT=projects/ch2-workflow-test/proposals/c.toml
videos/.venv/bin/python videos/projects/ch2-workflow-test/compare.py
videos/.venv/bin/python videos/projects/ch2-workflow-test/preview.py
videos/.venv/bin/python -m http.server 60071 --bind 127.0.0.1 --directory videos/build/ch2-workflow-test
```

比較入口：<http://127.0.0.1:60071/預覽/index.html>。有既存服務時不要重複啟動。

`design.py` 產生候選 SVG、語意狀態與獨立 profile；`preview.py` 從已編碼 MP4 擷取 17.4 秒有聲片段、九幕畫格、每個語意狀態與過渡中點、生成配色對照並做全片解碼。配色對照使用同一構圖與 focus，B 配色圖為渲染靜幀，跨幕圖與節奏片則來自 MP4。

現有轉圖器要求原稿有根層 `<g font-family="…">`。本輪候選遵循該介面；勿刪掉後只憑 render 成功判斷轉圖正確。一般旁白、內容與證據讀取同 `ch2-skill-engineering`，個案視覺以候選的 `視覺設定.json` 和新流程設計紀錄為準，原內容 JSON 的舊 visual 描述不是新版視覺定版。

AI 尚未直接聽審，聲音自然度及聲畫舒適度留待使用者試看。技術及畫格通過不等於正式美術驗收。

重建平台與限制：目前支援 macOS（含 PingFang TC、qlmanage）、Python 3.11+、uv、FFmpeg／ffprobe；本次驗證使用 FFmpeg 9.0.1。Linux／Windows 尚不支援。原始音檔以剪接設定內的 SHA-256 檢查；重新生成的同稿配音不能直接代用。不同 FFmpeg 版本若導致合成音檔雜湊不同，需先確認音訊差異，再依 videos README 重新對齊，不得跳過檢查。

2026-10-17 重建檢查：以版控預定檔案建立隔離目錄，排除 build、.venv、.cache 及原始素材，再只補入上述兩份 MP3；從零建立環境、render 與 finish 通過。產出 113 秒燒錄字幕影片，36 個語意狀態及 27 個過渡、來源／音訊雜湊與交付頁連結檢查通過，未建置任何 A／B／C 候選。這是本機隔離重建檢查，尚未在另一台實體電腦驗證。
