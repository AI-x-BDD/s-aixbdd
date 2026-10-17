# 影片製作專案

這是可獨立複製的影片製作工具，目前由外層 s-aixbdd Git 管理。內容、圖稿與原始素材在外層章節目錄；環境、快取與建置產物留在 videos。

## 設計與製作流程

新影片、整體美術改版與設計評審依 [WORKFLOW](WORKFLOW.md) 執行：從說明材料推導主題適配的 color scheme、呈現方法、構圖、focus、節奏與聲音搭配，再由 AI 比較實際預覽、提出推薦，取得方向確認後製作。已以 CH2 深色 B 測試片實跑至獨立輸出與靜態複查；AI 未直接聽看全片，使用者最終驗收仍待完成。

Agent 從 [AGENTS.md](AGENTS.md)／[CLAUDE.md](CLAUDE.md) 進入。個案的內容與配色保存在各片來源的製作紀錄；CH2 的石墨黑、暖白、亮藍不作為其他主題預設。

目前新流程測試交付：[CH2 B 深色版](http://127.0.0.1:60071/預覽/交付.html)，獨立重建方式見 [測試專案](projects/ch2-workflow-test/README.md)。

## 既有影片重建與預覽

支援 macOS、Python 3.11 以上、uv、FFmpeg／ffprobe、qlmanage；系統預覽語音另需 macOS say 與 Meijia 語音。系統工具由電腦提供，不包含在 Python 環境中。

從本目錄執行：

```sh
make setup
make check
make render
make preview
```

預覽：<http://127.0.0.1:60070/預覽/預覽.html>。`render` 重建，`preview` 只提供靜態檔案；重建後重新整理網頁。用 Ctrl-C 停止伺服器，同一埠不必重複啟動。

## 來源與目錄規則

設定檔為 `projects/ch2-skill-engineering/project.toml`。`source_root` 相對 videos 解析，`materials` 相對 source_root，content／slides／alignment／audio_recipe 相對 materials。

CH2 來源位於 `../docs/過程/CH2/影片/`：

- `製作來源/內容/製作內容.json`：旁白、分鏡、紅框及課程證據引用，為修改入口。
- `製作來源/畫面/圖稿/`：1600×900 SVG，使用 PingFang TC。
- `製作來源/配音/稿件/`：完整旁白與九段 TXT。
- `製作來源/配音/剪接/`：可執行的剪接設定及原始音檔雜湊。
- `製作來源/配音/對齊/`：目前採用的字元時間與音檔、原稿雜湊。
- `製作紀錄/`：敘事、參考來源、檢查與修改紀錄，保留代表版本。
- `素材/配音/`：使用者提供的完整與第三段修正版 MP3。

CH3、CH4 沿用相同分類，需要時再建立錄影、圖片等素材子目錄。製作來源、時間對齊、Skills 與製作紀錄保留版控；原始素材改為 clone 後由使用者提供，CH2 的 `素材/` 除 README 外全部忽略。現有本機音檔仍保留。兩份既有音檔尚被 Git 追蹤：全域安全 hook 阻擋停止追蹤操作，須由使用者手動移出 Git index 並提交後，clone 才會完全不帶原始音檔；忽略規則已就位。舊 Git 歷史中的音檔不會因此消失。後續章節也應在影片目錄設定相同的素材忽略規則。

另一台 Mac 首次使用：安裝上述系統工具及 uv，clone 本 repo，再依 [CH2 素材清單](../docs/過程/CH2/影片/素材/README.md) 放入兩份原始 MP3，執行 `make setup`。最新 B 版含燒錄字幕的完整重建命令見 [測試專案](projects/ch2-workflow-test/README.md)；下方預設命令仍重建舊版 CH2。更換主題或素材還需產生對應內容、圖稿、剪接與對齊資料，依 WORKFLOW 執行，不能僅替換任意音檔。

可忽略的是 `.venv/`、`.cache/`（含模型）、`__pycache__/`、`build/`（成片、字幕、預覽、PNG、中間音檔）、本機 `.env` 與 `.DS_Store`。保留 `pyproject.toml`、`uv.lock`、所有 Python 原始碼、profile、SVG、視覺設定、剪接與對齊 JSON、素材來源說明及第三方 Skill 授權。不得全域忽略 PNG／SVG／JSON，其他目錄可能將它們作為正式來源或驗收證據。

所有衍生檔在 `build/ch2-skill-engineering/`，不納入版控：

| 子目錄 | 內容 |
| --- | --- |
| 預覽/ | 預覽.html、時間軸、節奏檢查、腳本與分鏡、證據對照 |
| 輸出/ | 影片.mp4、字幕.srt、字幕.vtt |
| 中間產物/ | 合成配音、PNG、SVG 轉圖、分段編碼 |

發布後可清理 build；不會自動刪除素材或成品。一般修改由 Git 保存，不為每次 render 複製完整來源快照。

## 配音剪接與對齊

CH2 的 `audio_recipe` 指向第三段替換設定。原始完整配音的 11.36–36.04 秒，由第三段修正版取代，其餘保持原樣、不變速。`make audio` 從兩份原始 MP3 重建 `build/ch2-skill-engineering/中間產物/完整-03修正版.m4a`；check／render 也會先重建並核對雜湊。

有 audio_recipe 時，audio 是建置中間產物的檔名。未設定 recipe 時，audio 仍是 materials 內的既有音檔路徑；未設定 audio 的影片使用系統預覽語音。

只搬移來源路徑不需要重新辨識。修改音檔或內容 JSON 後，舊對齊資料會被雜湊檢查阻擋；先確認剪接設定與原始音檔雜湊，再執行：

```sh
make audio
UV_CACHE_DIR=.cache/uv uv run --frozen --extra alignment python scripts/align.py \
  --audio build/ch2-skill-engineering/中間產物/完整-03修正版.m4a \
  --content ../docs/過程/CH2/影片/製作來源/內容/製作內容.json \
  --output ../docs/過程/CH2/影片/製作來源/配音/對齊/對齊.json \
  --model .cache/models/whisper-large-v3-turbo
make check
make render
uv run --frozen python tests/check_recorded.py
```

alignment 為選配依賴，包含 MLX Whisper 與 OpenCC。分析在本機進行；繁簡字正規化只用於比對，字幕保留原稿，少量異字時間採相鄰詞內插。這是語音詞時間與原稿匹配，仍需聽看確認，文字匹配率不代表對齊精準度。參考 [MLX Whisper 官方文件](https://github.com/ml-explore/mlx-examples/blob/main/whisper/README.md)。

模型約 1.5 GiB，位於 `.cache/models/`；辨識快取位於 `build/alignment/`。不指定 model 時首次會下載預設模型。一般 render 不用載入模型，只需既有對齊資料。

## 獨立複製與新增影片

複製 videos 已版控檔案即可，省略 `.venv/`、`.cache/`、`build/`，再指定外部來源：

```sh
make setup
make check SOURCE_ROOT=/外部大專案
make render SOURCE_ROOT=/外部大專案
make preview SOURCE_ROOT=/外部大專案 PORT=60071
```

工具不依賴母專案名稱或 Python 環境。複製工具不包含外部素材；外部來源也包含 claims 引用的課程證據文件。

新增影片建立獨立設定與輸出目錄，再以 `make render PROJECT=projects/新影片/project.toml` 選擇。環境、快取及 build 均由 videos/.gitignore 排除，不建立巢狀 Git，不自動更新 Skills 或外層 CI。

## CH2 美術樣稿

正式九幕已套用前次美術更新；使用者仍回報樣板感，尚未通過新 workflow 的美術驗收。現有成片使用原本的 `/預覽/預覽.html`。以下保留第 1、3、6 幕代表樣稿，以及第三幕 11.84 秒樣片，作為設計過程。`visual-samples` 只重建這組既有樣稿，不會產出新的候選設計方案。

```sh
make visual-samples
make preview
```

開啟 <http://127.0.0.1:60070/預覽/美術提案/>。SVG 原稿留在外層 `製作來源/畫面/美術提案/`，樣片頁面、MP4 與中間檔各自放在 build 原有三類目錄下的美術提案子目錄。網頁播放同一支已編碼 MP4，聚焦不依賴網頁額外效果。此命令只建立樣稿與短片，不覆寫正式九幕。

## 現行語意聚焦與設計 Skill

CH2 profile 的 `visuals` 指向外層 `製作來源/畫面/視覺設定.json`。該檔保存現行視覺分鏡、旁白定位片語與 SVG 語意節點；`scripts/visual_motion.py` 將其轉成狀態並編碼至 MP4。沒有 visuals 的 profile 保留原本的框線渲染流程。

完整預覽使用 `templates/preview_video.html` 直接播放同一 MP4。九幕、旁白文字與配音時間仍由製作內容及原對齊資料決定，不需因美術變更重做對齊；內容 JSON 舊的 visual/focus 為歷史相容資料，現行視覺以上述獨立檔為準。

```sh
uv run --frozen python tests/check_recorded.py
uv run --frozen python tests/check_visuals.py
```

設計 Skill 在 `.agents/skills/`，與影片工具一起管理，來源及內容雜湊見該目錄 `來源.json`。第三方原文保持原樣。一般 render 不會執行 Skill 的安裝器、引擎或下載；複製 videos 也不需要它們才能重建既有影片。

新增 `storyboard` 與 `presentation-design-editorial` 的分工、載入路徑和驗收方式以 WORKFLOW 為準；同名的兩份 presentation-design 必須依路徑區分。新增 Skill 尚未經完整影片實跑驗證。各 agent 的自動掃描範圍不同，執行時一律依 WORKFLOW 明確讀檔使用，不依賴自動發現。來源目錄內的 LICENSE 保留各自授權。

## 候選方案建置

以下在獲授權製作設計提案時使用，與正式來源及輸出隔離。現有工具不會自動設計候選圖稿，圖稿與設定由 agent 依 WORKFLOW 及對應 Skill 產出。

1. 原稿放在該片外部來源的 `製作來源/畫面/設計提案/方案id/`，包含 `圖稿/` 與需要的 `視覺設定.json`；同構圖的不同配色各有獨立方案 id。
2. 在 `videos/projects/影片id/proposals/方案id.toml` 建立獨立 profile，可複製該片既有 profile 後修改。`source_root` 仍相對 videos，`materials` 相對 source_root，`content`／`slides`／`visuals` 相對 materials；`output` 指向 `build/影片id/提案/方案id`。`slides` 與 `visuals` 指向候選原稿，不能覆寫正式圖稿或沿用正式 output。
3. 沿用正式聲音時，保留原 `content`、`audio_recipe` 與 `alignment`，在候選 output 重建衍生配音；直接音檔則沿用原 audio 路徑。完整音檔與對齊資料不可搭配自行刪減的 scenes。只要代表片段時，先建置獨立候選時間軸，再從候選 MP4 節錄，原音檔與正式成片不變。
4. 未配音的新片可建立獨立候選 content JSON，設定 scenes、voice、speech_rate、fps 與適合預覽的 min_seconds／max_seconds；不設 audio、audio_recipe、alignment，使用本機預覽語音。原內容需保留時，候選 content 另存於方案目錄。沒有語意狀態時可省略 visuals；若省略，需同步檢查 content 的舊 focus 是否適用。
5. 依下列指令建置與開啟候選，從實際 MP4 產生跨幕縮圖，將連結與具體時間點寫入 `視聽提案.md`。profile 與原稿保留版控，衍生檔仍在 build。需要現有 renderer 不支援的動態時，先依 WORKFLOW 提出能力落差與替代路徑。

```sh
make -C videos check PROJECT=projects/影片id/proposals/方案id.toml
make -C videos render PROJECT=projects/影片id/proposals/方案id.toml
make -C videos preview PROJECT=projects/影片id/proposals/方案id.toml PORT=60071
```

將指令中的影片id、方案id 換成實際名稱。從 repo 根目錄執行；候選預覽入口為 `http://127.0.0.1:60071/預覽/預覽.html`。埠號依當次服務狀態選擇；新片使用外部來源時可加 `SOURCE_ROOT=/外部大專案`。
