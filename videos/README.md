# 影片製作工具

已交付 CH2 的基準是 B 深色配色＋M2 動態敘事：九幕、113 秒、原配音、燒錄字幕；這些不是新片的固定規則。新片、改版與評審先讀 [WORKFLOW](WORKFLOW.md)；CH2 進度在 [交付狀態](../docs/過程/CH2/影片/製作紀錄/設計/新流程測試/交付狀態.md) 維護。

## 新章節與其他主題

完整製作使用 [video-production](../.agents/skills/video-production/SKILL.md)，不複製 CH2 專用 renderer。新的通用工具為 `scripts/motion_project.py`、`scripts/motion_checks.py`，空白 Remotion 骨架與完整設定說明見 [motion-project](templates/motion-project/README.md)。

從 `videos` 目錄執行，將設定換成本片：

```sh
uv sync --frozen --extra alignment
uv run --frozen python scripts/motion_project.py --help
uv run --frozen python scripts/motion_project.py --config projects/本片/project.toml init
uv run --frozen --extra alignment python scripts/motion_project.py --config projects/本片/project.toml prepare
uv run --frozen python scripts/motion_project.py --config projects/本片/project.toml render
uv run --frozen python scripts/motion_project.py --config projects/本片/project.toml review
```

候選／代表片段使用獨立 profile、workspace、records 與 output，執行相同 init→prepare→render→review，不覆寫正式輸出。新預覽語音可以只涵蓋代表內容，須重新取得該段實際對齊與契約；沿用已確認完整原音時，保留完整內容與對齊，從隔離的完整候選成片節錄，不刪原音或正式場景來湊片段。代表段的通過標準依 Skill 敘事規範執行。

新聲音須設定 `model_path` 或 `VIDEO_ALIGNMENT_MODEL`，並保存模型來源／固定版本與雜湊。既有素材、原音與對齊按本片設定讀取；缺模型、工具或輸入時停止，不使用估時計時。Remotion 依各工作區 lockfile 安裝，骨架不替代場景設計。

`review` 產生實際成片抽幀與技術結果；尚無綁定該片雜湊的視覺評審時會回傳失敗，這是交付守門。實際看過畫格、完成字幕及過渡檢查後，依工具說明填寫評審檔，再執行：

```sh
uv run --frozen python scripts/motion_project.py --config projects/本片/project.toml review --assessment 本片評審.json
uv run --frozen python scripts/motion_project.py --config projects/本片/project.toml deliver
```

交付前仍會核對來源、編碼版本及評審證據。播放與下載指向同一檔案，保留 SRT/VTT；各項實際檢查與使用者驗收分別記錄。第三方授權見 [來源清單](.agents/skills/來源.json) 與 [Remotion 說明](motion/README.md#官方-skill-與授權)。

## 建置與預覽

支援 macOS、Python 3.11+、uv、可執行的 Node.js 22+、FFmpeg／ffprobe、qlmanage 與 PingFang TC。未提供正式音檔時的預覽另需 macOS say／Meijia。從 repo 根目錄執行：

```sh
make -C videos setup
make -C videos check test
make -C videos render
make -C videos preview
```

預覽：<http://127.0.0.1:60071/預覽/交付.html>。`setup` 安裝 Python 與鎖定版 Remotion 依賴；執行時會選可用的 Node.js（可用 `NODE_BINARY` 指定）。`render` 自動重建原配音、準備九幕輸入、渲染 Remotion `Full-Motion`（畫面含字幕）、直接複製原 AAC 音訊、核對 2825 影格焦點並抽幀，全部通過才替換交付影片與頁面。`preview` 只提供靜態檔案，重建後重新整理；有既存服務時不重複啟動。

預設設定為 `projects/ch2-workflow-test/project.toml`；輸出在 `build/ch2-workflow-test/動態正式版/`。交付頁與歷史比較放在其上一層 `build/ch2-workflow-test/`。使用者已選 M2；原本固定構圖的 B 焦點基準保留於 `正式版/`，其重建 profile 為 `projects/ch2-workflow-test/focus-baseline.toml`。

## 全片聲畫核對

```sh
make -C videos review
make -C videos test
```

`review` 依 49 段旁白契約與獨立的 `motion-focus.json` 主焦點表與 `motion-labels.json` 移動物件名稱表，核對實際繪圖共用的逐影格狀態：主焦點、可見性、字幕帶以上的邊界；另檢查完整解碼、113 秒規格與原 AAC 音訊流相同，從同一成片擷取 49 段中點與尾端及每秒畫格。入口為 `動態正式版/預覽/聲畫稽核/index.html`。圖稿或對齊資料改動後，必須先 render；過期來源指紋會阻擋抽幀。

焦點自動核對允許各段起點後 0.24 秒進場，核對到終點前 0.04 秒；全片 2825 影格皆計算狀態，進場／交棒的實際可讀性另看成片抽幀。

`tests/check_recorded.py`、`check_visuals.py` 接受 `--config`／`--source-root`，預設均檢查 B 版；`check_review.py` 專門重現漏列舉、錯對象與父群組誤染色。`check_motion.py` 另故意注入消失、錯焦點、裁切與空白焦點檔案，確認檢查會阻擋。這些自動檢查不能證明畫面可讀、語音自然或動態舒適，仍須逐段檢視成片。

### 能力實測

```sh
# 模型須已存在；此工具不下載模型，不上傳素材。
cd videos
uv sync --frozen --extra alignment
uv run --frozen --extra alignment python scripts/capability_probe.py --transcribe
```

結果放在目前 profile 輸出的 `預覽/能力實測/`：全片每秒畫格、全片本機辨識及能力說明。安裝 alignment 依賴需網路；辨識使用本機 `.cache/models/whisper-large-v3-turbo`。本對話沒有直接音訊輸入工具；辨識與抽幀是替代檢查，不可宣稱 AI 已連續聽看。具體範圍見個案的 `聲畫能力與焦點稽核.md`。聲音自然度與整體觀看舒適度仍須人工聽看或另行接入並實測可處理影音的服務。

## 來源、素材與建置產物

`source_root` 相對 videos；`materials` 相對 source_root；`content`／`slides`／`visuals`／`alignment`／`audio_recipe` 相對 materials。`focus_contract`、`postprocess`、`renderer_script`、`review_script`、`setup_script`、`preview_root` 相對 videos。

CH2 位於 `../docs/過程/CH2/影片/`：

| 類別 | 位置與用途 |
| --- | --- |
| 內容 | `製作來源/內容/製作內容.json`：正式旁白、順序與內容證據 |
| 正式動態畫面 | `videos/motion/src/`：九幕 TSX 與實際繪圖共用的動態狀態；`製作來源/畫面/新流程測試定版/` 保留 B SVG 焦點基準 |
| 配音稿 | `製作來源/配音/稿件/`：完整與分段 TXT |
| 剪接與對齊 | `製作來源/配音/剪接/`、`製作來源/配音/對齊/` |
| 製作紀錄 | `製作紀錄/設計/新流程測試/`：分鏡、評審、交付、聲畫稽核及動態候選 |
| 原始素材 | `素材/配音/`：使用者提供的兩份 MP3，清單見 [素材 README](../docs/過程/CH2/影片/素材/README.md) |

原始素材和正式來源在建置期間唯讀；來源與對齊資料保留雜湊檢查。B 選定方向清單保留原始與焦點修訂後的來源雜湊，不把修訂冒充昨天原版。

`build/` 的 `預覽/`、`輸出/`、`中間產物/` 都是衍生檔，不納入版控。環境、模型、快取、`.env` 也忽略。內容、SVG、設定、契約、來源說明、程式與第三方授權保留版控；不得全域忽略 PNG／SVG／JSON。原始素材不自動刪除；兩份歷史音檔仍被 Git 追蹤，停止追蹤及歷史容量限制見素材 README。

## 配音剪接與重新對齊

現有 `audio_recipe` 將原完整配音 11.36–36.04 秒替換為第三段修正版，其餘不變速、不補時。`make -C videos audio` 從兩份原始 MP3 重建中間音檔並核對雜湊。

只改畫面不需重新對齊。更改音檔或內容 JSON 時，先確認剪接設定與原檔雜湊，再執行：

```sh
make -C videos audio
cd videos
uv run --frozen --extra alignment python scripts/align.py \
  --audio build/ch2-workflow-test/動態正式版/中間產物/完整-03修正版.m4a \
  --content ../docs/過程/CH2/影片/製作來源/內容/製作內容.json \
  --output ../docs/過程/CH2/影片/製作來源/配音/對齊/對齊.json \
  --model .cache/models/whisper-large-v3-turbo
make check test
make render
```

模型需事先取得，約 1.5 GiB；不指定 model 時 align.py 首次可能下載預設模型。一般 render 只使用既有對齊資料。辨識異字可能採相鄰時間內插，文字匹配率不等於對齊精準度。

## 獨立複製與新影片

複製 videos 的版控檔案，省略環境、快取、build，另提供外部來源與原始素材。外部來源也需包含內容引用的課程證據。

```sh
make -C videos setup
make -C videos check SOURCE_ROOT=/外部大專案
make -C videos render SOURCE_ROOT=/外部大專案
make -C videos preview SOURCE_ROOT=/外部大專案 PORT=60071
```

以上 `make`／`PROJECT` 介面用於既有影片的重建；新章節使用本文「新章節與其他主題」的 `motion_project.py` 介面。CH2 的後處理與契約不可直接套到新片。

## CH2 動態方案與歷史候選隔離

動態能力、實際比較與重建見 [motion](motion/README.md)。最新正式片使用 Remotion 逐影格動態敘事；原 SVG renderer 保留給焦點基準與歷史片。不能把 Skill 安裝成功當成動畫已實作，或把網頁 CSS 動畫當成已編碼 MP4。

通用候選原稿放外部來源的 `製作來源/畫面/設計提案/方案id/`；profile 放 `projects/影片id/proposals/`，output 必須獨立，不能覆寫正式來源。沿用完整配音及對齊時，不可自行刪減 scenes；代表片段從獨立候選成片節錄。新片可用暫定旁白。至少比較兩種實際呈現方式，記錄理解目的、取捨與未驗證範圍，再請使用者確認。

## CH2 舊版 SVG 候選建置

本節僅保留既有 CH2／舊版 SVG 候選的重建方式。新片代表段依本文「新章節與其他主題」使用獨立 `motion_project.py` profile；[motion 的重建指令](motion/README.md#重建) 是 CH2 專用。歷史 SVG 候選操作如下：

1. 在外部來源的 `製作來源/畫面/設計提案/方案id/` 建立 `圖稿/` 與 `視覺設定.json`，依 WORKFLOW 產生設計，不覆寫正式來源。
2. 複製該片 profile 到 `videos/projects/影片id/proposals/方案id.toml`。修改 `slides`、`visuals` 指向候選，`output` 設為 `build/影片id/提案/方案id`；來源路徑仍依上方的相對路徑規則。
3. 沿用正式聲音時，保留原 `content`、`audio`、`audio_recipe`、`alignment`，保留完整 scenes，再從候選成片節錄代表片段。不要拿完整配音搭配刪減的 scenes。
4. 複製 B profile 時，移除其 `postprocess`、`renderer_script`、`review_script`、`setup_script`、`renderer`、`preview_root`、`preview_entry`，避免執行只接受已選定來源的 B 交付器或跳回正式預覽；`focus_contract` 必須換成候選自己的核對表，沒有時移除並明列「逐段焦點未驗證」。需要燒錄字幕時，提供候選專用後處理；一般未燒錄候選不得當成正式交付。
5. 依下列指令建置，檢視實際 MP4，將時間點、比較、取捨與未驗證範圍寫入該片的 `視聽提案.md`。候選原稿與 profile 保留版控，衍生檔留在 build。

```sh
make -C videos check PROJECT=projects/影片id/proposals/方案id.toml
make -C videos render PROJECT=projects/影片id/proposals/方案id.toml
make -C videos preview PROJECT=projects/影片id/proposals/方案id.toml PORT=60072
```

將影片id／方案id 換成實際名稱。未設定自訂 preview_root／preview_entry 時，入口為 `http://127.0.0.1:60072/預覽/預覽.html`；埠號依實際服務狀態選擇，外部來源可加 `SOURCE_ROOT=/外部大專案`。上例是沿用正式音檔與對齊資料的候選；尚未配音的新片可省略 audio／audio_recipe／alignment，改用本機預覽語音，素材檢查用 `cd videos` 後執行 `uv run --frozen python scripts/video.py --config projects/影片id/proposals/方案id.toml check`；錄音專用測試不適用。

## 歷史版本

舊 CH2 重建必須明確指定：

```sh
make -C videos render PROJECT=projects/ch2-skill-engineering/project.toml
make -C videos preview PROJECT=projects/ch2-skill-engineering/project.toml PORT=60070
```

此版本不是目前交付基準。`make -C videos visual-samples PROJECT=projects/ch2-skill-engineering/project.toml` 只重建早期 1／3／6 幕樣稿。歷史專屬幾何檢查為 `videos/tests/check_legacy_visuals.py`，不作最新 B 版驗收。

### 固定風格庫（新片必要依賴）

先讀 [固定風格庫](style-library/README.md)，開啟 [可播放目錄](style-library/index.html)。它隨工具包提供 7 種可用解說形式與 35 種藝術示範，不在每次製作時臨時搜尋。新片 init 設定預設啟用 style_library_required，選用紀錄綁定當次 catalog SHA；原庫示範不替代新題材有聲、燒錄字幕候選。歷史 CH2 建置不強制改版。
