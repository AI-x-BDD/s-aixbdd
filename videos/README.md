# 影片製作專案

這是可獨立複製的影片製作工具，目前由外層 s-aixbdd Git 管理。內容、圖稿與原始素材在外層章節目錄；環境、快取與建置產物留在 videos。

## 製作與預覽

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

CH3、CH4 沿用相同分類，需要時再建立錄影、圖片等素材子目錄。內容與製作過程保留版控，原始素材在交付確認後可清理；刪除前記錄來源與取得方式。刪除後如要重建，必須重新取得音檔，重新生成的聲音可能不同。刪除已追蹤素材不會清除 Git 歷史。

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
