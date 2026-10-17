# 影片製作專案

這個目錄是可獨立複製的影片製作工具。目前由外層 `s-aixbdd` repo 管理版本；原始素材、旁白文字、圖稿與課程證據留在外層專案，工具唯讀載入。

## 環境

目前支援 macOS，使用 Python 3.11 以上、uv、FFmpeg（含 ffprobe）、macOS `say` 的 Meijia 語音與 `qlmanage`。一般建置只用 Python 標準函式庫；重新分析配音時另用選配的 `alignment` 套件；環境在 `.venv/`，uv 快取在 `.cache/uv/`，兩者均不進版控。系統執行檔仍由 macOS／套件管理器提供，無須複製進本目錄。

已安裝工具後，在本目錄執行：

```sh
make setup
make check
make render
make preview
```

預覽預設為 <http://127.0.0.1:60070/預覽.html>。`render` 重建影片，`preview` 只提供現有輸出的靜態伺服器。修改素材後先重新 render，再重新整理網頁。`Ctrl-C` 停止伺服器。

## CH2 的來源與輸出

- 設定：`projects/ch2-skill-engineering/project.toml`。
- 外部來源：`../docs/過程/CH2/影片/製作內容.json`（旁白、分鏡、重點框及證據引用）與同目錄的 `靜幀/*.svg`。
- 證據引用：依設定的 `source_root` 讀取外部專案 Skill 與前後比較文件。
- 生成輸出：`build/ch2-skill-engineering/`，包含預覽 HTML、MP4、旁白、字幕、時間軸、節奏檢查、可供瀏覽器使用的 PNG 及中間檔。

所有原始素材留在外層。`build/` 裡的 PNG、音訊和影片均為可重建的衍生檔，不是素材來源。現有外層預覽檔先保留，新的建置流程不再讀取它們，也不覆寫它們。

目前 SVG 輸入為 1600×900、PingFang TC 字體，採 Quick Look 轉圖；影片為 25 fps。CH2 目前使用外層 `正式配音/完整-03修正版.m4a` 與 `對齊.json`，依實際語音詞時間切畫面、字幕及 focus。音檔不做變速或刪減；自然停頓保留，不額外補時。對齊屬自動辨識結果，仍需聽看驗收。未設定 audio／alignment 的其他專案，維持系統語音與比例估時。

## 獨立複製

複製本目錄的已版控檔案即可建立另一個製作專案；`.venv/`、`.cache/`、`build/` 可省略並重新生成。素材仍需另行指定：

```sh
make setup
make check SOURCE_ROOT=/外部素材所在的大專案
make render SOURCE_ROOT=/外部素材所在的大專案
make preview SOURCE_ROOT=/外部素材所在的大專案 PORT=60071
```

`SOURCE_ROOT` 指向大專案根目錄；素材位置與證據路徑相對於此根目錄解析。也可直接調整 `project.toml`。工具不假設母目錄名稱，也不依賴母專案的 Python 環境。

增加 CH3、CH4 時，建立新的 project.toml，指向各章外部素材，再用 `make render PROJECT=projects/新影片/project.toml` 選擇。每個影片使用獨立的輸出目錄。

程式、模板、設定與鎖檔納入外層 Git；環境、快取和建置產物由本目錄的 `.gitignore` 排除。目前未設定 Git LFS，也未修改外層 Skill 或 CI。

## 正式配音與重新對齊

CH2 設定檔的 `audio`、`alignment` 路徑相對於外部素材目錄。一般 check/render 只讀取現有音檔及對齊資料，不需要載入辨識模型。若音檔或原始 JSON 改變，雜湊檢查會阻止使用舊時間軸，應先重新對齊：

```sh
UV_CACHE_DIR=.cache/uv uv run --frozen --extra alignment python scripts/align.py \
  --audio ../docs/過程/CH2/影片/正式配音/完整-03修正版.m4a \
  --content ../docs/過程/CH2/影片/製作內容.json \
  --output ../docs/過程/CH2/影片/正式配音/對齊.json
make check
make render
```

以上指令從 videos 執行。此分析使用本機 MLX Whisper 詞時間及原稿比對，繁簡字正規化只用於匹配，字幕保留原稿。少量辨識異字的時間由相鄰已匹配詞內插；它不是人工逐字校時，也不聲稱是音素強制對齊。參考 [MLX Whisper 官方文件](https://github.com/ml-explore/mlx-examples/blob/main/whisper/README.md)。

`alignment` 選配套件包括 mlx-whisper 與 OpenCC。模型與辨識快取分別留在本專案 `.cache/`、`build/alignment/`，均不進版控；模型約 1.5 GiB，套件另占空間。這次重用本機已有權重，複製到影片專案自己的忽略快取，沒有把其他專案路徑寫進設定或程式。也可用 `--model .cache/models/whisper-large-v3-turbo` 指定本機模型，未指定時首次會下載預設模型。

已保存的 `對齊.json` 含音檔／來源 JSON 雜湊、各原稿字元時間與辨識差異。獨立複製工具後，只要外部素材包含正式音檔和對齊資料，就能直接重建，不必重新辨識。

檢查正式音檔時間軸及過期資料阻擋：

```sh
uv run --frozen python tests/check_recorded.py
```
