# Motion project skeleton

這是每部影片各自使用的 Remotion workspace 骨架與通用檢查契約。它不包含任何章節的畫面、配色、幕數、旁白或物件名稱。`motion_project.py init` 只會在新的 workspace 建立骨架，已存在的檔案不覆寫。

工具把「原始素材」「實際繪圖狀態」「旁白焦點契約」分開保存：`state.json` 或 exporter 描述畫面實際畫了什麼，`focus.json` 描述旁白此時要求觀眾看什麼。焦點答案不會由 `active` 自動推導。影片作者仍須讓 renderer 與 exporter 共用同一套幾何、可見性與鏡頭後 bounds。

## 最小可執行專案

以下假設 profile 位於 repository 的 `videos/projects/demo-motion/project.toml`。`source_root` 是相對於工具根目錄 videos；若從其他位置執行，可用 CLI 的 `--source-root` 覆寫。`workspace`、`output`、`records` 以 `build/` 開頭時會放在專案根目錄，避免把建置產物寫回 `materials`。

```toml
id = "demo-motion"
source_root = "projects/demo-motion"
materials = "materials"
style_library_required = true
style_library = "style-library"
style_selection = "style-selection.json"

content = "content.json"
audio = "voice.wav"
alignment = "alignment.json"       # 已有對齊檔時使用；省略時改用 model_path
focus_contract = "focus.json"
labels = "labels.json"
state = "state.json"                # 或改用 state_exporter

workspace = "build/demo-motion/workspace"
output = "build/demo-motion/output"
records = "build/demo-motion/records"

width = 1280
height = 720
fps = 30
composition = "Main"
renderer = "remotion"
entry = "src/index.ts"
npm_install = true

require_audio = true
burn_subtitles = true
opacity_threshold = 0.5
content_safe_area = {left = 40, top = 30, right = 1240, bottom = 600}
subtitle_area = {left = 40, top = 620, right = 1240, bottom = 700}

# 這些是本片作者明列的設定，請依新片替換；不是工具固定配色。
background = "#000000"
foreground = "#ffffff"
focus = "#ffffff"
sample_interval = 1.0
```

建議目錄如下。`voice.wav` 必須是本片旁白；`alignment.json`、`state.json` 的內容必須與同一份音訊及稿件相符。

```text
videos/projects/demo-motion/
├── project.toml
├── style-selection.json
└── materials/
    ├── content.json
    ├── voice.wav
    ├── alignment.json
    ├── focus.json
    ├── labels.json
    └── state.json
```

若省略 `alignment`，profile 必須改列 `model_path`；工具會實際呼叫 `mlx_whisper` 與本專案的 `videos/scripts/align.py`，找不到模型或依賴時停止，不會用字數均分時間。模型來源、revision、檔案雜湊可再列 `model_source`、`model_revision`、`model_provenance`。

風格選用檔的格式與本機檢查見 [固定風格庫](../../style-library/README.md)。新片不得略過；缺欄位會失敗。歷史重建可在隔離設定明列 style_library_required=false 與 legacy_style_reason，理由會寫入 prepare 證據，不能用於新片。

## 素材格式

### `content.json`

最外層必須有非空 `scenes` 陣列，每幕必須有非空 `text`。`id` 與 `frame` 建議同時提供；若使用實際模型對齊而只有 `id`，工具會在送給 `align.py` 的副本補上 `frame`，不改原始稿件。

```json
{
  "title": "示範主題",
  "audience": "第一次接觸這個主題的觀眾",
  "scenes": [
    {"id": "problem", "frame": "problem", "text": "先看見問題與它造成的影響。"},
    {"id": "solution", "frame": "solution", "text": "接著展示解法如何逐步處理問題。"}
  ]
}
```

`text` 是旁白稿，也是對齊時的比對文字。不要在 prepare 後直接修改稿件；修改後必須重新 prepare、render、review，過期的 alignment、movie 與 assessment 都會被阻擋。

### `alignment.json`

可由工具的實際模型對齊產生，也可以提供已經驗證過的檔案。`audio_sha256` 必須是目前 audio 檔案的 SHA-256，`content_sha256` 必須是目前 content 檔案的 SHA-256；每幕文字及數量必須一致，`characters` 不可為空。

```json
{
  "method": "whisper-word-timestamps-and-transcript-matching",
  "audio_sha256": "<目前 voice.wav 的 sha256>",
  "content_sha256": "<目前 content.json 的 sha256>",
  "scenes": [
    {
      "frame": "problem",
      "text": "先看見問題與它造成的影響。",
      "speech_start": 0.12,
      "speech_end": 1.86,
      "characters": [
        {"offset": 0, "start": 0.12, "end": 0.24},
        {"offset": 1, "start": 0.24, "end": 0.36}
      ]
    }
  ]
}
```

實際檔案要列出每個字元的時間，不可只保留上面的兩筆示意資料。

### `labels.json`

labels 是必填來源，讓檢查器能在物件移動、形變與鏡頭過渡時核對名稱仍可辨識。可用 id→名稱物件：

```json
{
  "problem": "問題",
  "solution": "解法"
}
```

也可用陣列：

```json
{
  "labels": [
    {"id": "problem", "name": "問題"},
    {"id": "solution", "label": "解法"}
  ]
}
```

### `focus.json`

最外層必須有非空 `segments`。區間採半開表示 `[start, end)`：剛好在交棒時間的 frame 屬於下一段。區間必須從 0 開始、連續覆蓋所有 state frame，不能重疊或留空；每段都必須明列 `required_active`，不能從 state 反推答案。

```json
{
  "segments": [
    {
      "id": "problem-focus",
      "start": 0.0,
      "end": 1.9,
      "targets": [
        {"id": "problem", "name": "問題", "min_opacity": 0.5}
      ],
      "required_active": ["problem"],
      "forbidden_active": []
    },
    {
      "id": "solution-focus",
      "start": 1.9,
      "end": 4.2,
      "targets": [
        {"id": "solution", "name": "解法"}
      ],
      "required_active": ["solution"],
      "forbidden_active": []
    }
  ]
}
```

`targets` 也可寫成 id 字串，但建議使用物件並明列 `name`。沒有 `min_opacity` 時使用 profile 的 `opacity_threshold`。只有在確實有理解目的時才使用 `grace_start`、`grace_end`，而且兩者不能覆蓋整段，並必須加 `hold_reason` 或 `transition_reason`。若允許同時有其他 active，必須設定 `allow_extra_active = true` 並提供 `extra_active_reason`；否則 active 必須精確等於 `required_active`。

### `state.json` 或 state exporter 輸出

根物件必須有 `frames` 陣列，且要為實際影片的每一個 encoded frame 提供 state。`frame` 從 0 連續遞增，`t` 通常是 `frame / fps`。`active` 是實際畫面使用的焦點狀態，不能只是額外欄位；renderer 必須由同一狀態繪製可見的粗體、框線、填色或其他焦點表現。

```json
{
  "fps": 30,
  "frames": [
    {
      "frame": 0,
      "t": 0.0,
      "scene": "problem",
      "active": ["problem"],
      "visible": [
        {
          "id": "problem",
          "text": "問題",
          "opacity": 1,
          "x": 80,
          "y": 160,
          "w": 520,
          "h": 180,
          "projected_bounds": {"x": 80, "y": 160, "w": 520, "h": 180}
        }
      ]
    }
  ]
}
```

實際 state 必須有 `frame = 0` 到最後一格的完整陣列，不能只保留一格示意資料。`visible` 也可使用 `items` 別名。每個 focus target 在所有非 grace frame 都必須可見、opacity 達門檻、`text` 包含 contract 或 labels 要求的名稱，並提供鏡頭後、裁切前的 `projected_bounds`。bounds 不能超出 `content_safe_area`、不能與 `subtitle_area` 重疊；若提供 `text_bounds` 與 `paths`，工具也會檢查路徑是否蓋住文字。

使用 exporter 時，profile 例如：

```toml
state_exporter = ["node", "/absolute/path/to/export-state.cjs", "{state}"]
state_exporter_sources = ["/absolute/path/to/export-state.cjs"]
```

exporter 會在 workspace 目錄執行，必須把符合上述 schema 的 JSON 寫到 `{state}`。可用的替換值有 `{output}`、`{workspace}`、`{public}`、`{composition}`、`{width}`、`{height}`、`{fps}`、`{duration}`、`{state}`。`state_exporter_sources` 的檔案會進入來源指紋；不能只列指令名稱而不列實際腳本。上例的絕對路徑請換成實際腳本；若使用相對路徑，必須確認它是從 workspace 執行時可解析的路徑。prepare 呼叫 exporter 時，`{duration}` 使用 profile 的 `duration` 值，未明列時是 0；它不會自動帶入 audio timeline，因此 exporter 必須自行產生完整 frame 數，或直接使用已產生的 state 檔。若 exporter 與 renderer 使用不同的幾何或可見性模型，state 檢查不能證明實際畫面正確，不能宣稱完成。

## Renderer 與 profile 欄位

- `renderer = "remotion"`：`init` 會把本骨架複製到 `workspace/motion`，以該 workspace 的 `package-lock.json` 執行 `npm ci --ignore-scripts`；`entry` 預設為 `src/index.ts`。
- `renderer = "command"` 或 `"custom"`：必須提供 `render_command` 與非空 `render_command_sources`。command 可使用與 exporter 相同的替換值，並必須將影片寫到 `{output}`。
- `renderer = "ffmpeg"`：使用工具內建的純色技術 smoke renderer；它不是動態敘事成片。背景色可由 profile 的 `background` 指定。
- `renderer_dir` 若未指定就是 `workspace/motion`；不要把新的 profile 指向既有章節的 `node_modules`。

profile 也可指定 `subtitle_font`、`subtitle_font_size`、`subtitle_color`、`subtitle_background`、`subtitle_max_chars`、`subtitle_max_lines` 等字幕設定，以及 `review_times`、`transition_times` 供額外畫格取樣。這些值都屬於個案設定，不應從其他影片複製成固定規則。

## CLI

在 repository 根目錄執行：

```bash
uv run --frozen python videos/scripts/motion_project.py \
  --config videos/projects/demo-motion/project.toml init

uv run --frozen python videos/scripts/motion_project.py \
  --config videos/projects/demo-motion/project.toml prepare

uv run --frozen python videos/scripts/motion_project.py \
  --config videos/projects/demo-motion/project.toml render

uv run --frozen python videos/scripts/motion_project.py \
  --config videos/projects/demo-motion/project.toml review \
  --assessment videos/projects/demo-motion/assessment.json

uv run --frozen python videos/scripts/motion_project.py \
  --config videos/projects/demo-motion/project.toml deliver \
  --user-acceptance accepted
```

各階段責任如下：

1. `init` 可以從尚無素材的 profile 建立 workspace；若 profile 尚不存在，可使用 `--init-id demo-motion`。它會列出 `pending_inputs`，不會宣稱影片已完成。
2. `prepare` 驗證素材、模型或 alignment、labels、state、安全區，依實際 audio 建立 canonical AAC、逐字字幕、timeline、runtime 檔案與來源指紋。
3. `render` 使用本片 renderer，燒錄字幕、合併 canonical audio，並寫入 `workspace/render.json`。建置期間來源改動或 audio stream hash 不一致會停止。
4. `review` 會檢查實際 encoded MP4 的 metadata、完整解碼、音訊 stream hash、state／focus contract、字幕畫格與週期／起中尾畫格。第一次不帶 assessment 執行時會產生畫格證據但以失敗結束，不能把抽幀或 ASR 當成直接連續聽看。
5. `deliver` 只接受目前 MP4 SHA 與 `render.json`、review、source fingerprint 全部一致且評審通過的結果，交付 MP4、SRT、VTT、`delivery.html` 與 `delivery.json`。

可用的全域選項：

```text
--config <profile.toml>       必填
--source-root <path>          覆寫 profile 的 source_root
--version                     顯示工具版本
--assessment <json>            review 使用的評審紀錄
--user-acceptance <state>      deliver 使用 pending/accepted/rejected
--init-id <id>                 profile 不存在時給 init 的 project id
```

### Assessment 格式

`review --assessment` 必須綁定本次 render 的成片與來源指紋。`movie_sha256` 取自 `workspace/render.json`；`source_fingerprints_sha256` 是 `workspace/source-fingerprints.json` 的 SHA-256。`captured_frames` 可從第一次失敗 review 產生的 `records/review.json` 取得，`subtitle_frames` 可從 `records/subtitle-evidence.json` 取得。每一筆都必須使用目前檔案的 `time`、`sha256`，並填寫非空 `observation` 與 `status = "pass"`。

```json
{
  "movie_sha256": "<workspace/render.json 的 movie_sha256>",
  "source_fingerprints_sha256": "<source-fingerprints.json 的 sha256>",
  "captured_frames": [
    {
      "time": 0.0,
      "sha256": "<records/review.json 對應畫格 sha256>",
      "status": "pass",
      "observation": "此格實際看到主標題與目前焦點，未被字幕遮住。"
    }
  ],
  "subtitle_frames": [
    {
      "time": 0.5,
      "text": "目前字幕文字",
      "sha256": "<records/subtitle-evidence.json 對應畫格 sha256>",
      "status": "pass",
      "observation": "字幕文字完整可讀，沒有被畫面物件遮住。"
    }
  ],
  "static_visual": {
    "status": "pass",
    "method": "以本次 encoded MP4 的所有 captured frames 實際檢查"
  },
  "subtitle_visibility": {
    "status": "pass",
    "method": "以本次 encoded MP4 的 subtitle frames 實際檢查"
  },
  "audio_analysis": {
    "status": "pass",
    "method": "ffprobe、完整解碼與 AAC stream hash；不是直接聽看"
  },
  "continuous_av": {
    "status": "unverified",
    "reason": "目前工具沒有直接連續聽看輸入"
  }
}
```

工具會拒絕缺畫格、重複或假 hash、過期來源、空 observation、任一筆非 `pass`，以及未綁定當前 MP4 的 assessment。`burn_subtitles = false` 且 profile 已提供 `subtitle_override_reason` 或 `subtitle_decision_record` 時，`subtitle_visibility.status` 可用 `overridden`，此時不要求 `subtitle_frames`；仍須保留可修改的 SRT/VTT。

## 獨立 state／contract 檢查 CLI

若只要檢查 state 與 focus contract，不代表已檢查 encoded MP4，可直接執行：

```bash
uv run --frozen python videos/scripts/motion_checks.py \
  --state build/demo-motion/workspace/motion/public/state.json \
  --contract build/demo-motion/workspace/motion/public/focus-contract.json \
  --labels build/demo-motion/workspace/motion/public/labels.json \
  --width 1280 --height 720 --fps 30 --frames <frame_count> \
  --opacity-threshold 0.5 \
  --output build/demo-motion/records/state-review.json
```

`--safe-area`、`--subtitle-area` 可另外接 JSON 檔；命令回傳 0 代表 state／contract 檢查通過，回傳 1 代表失敗。這個命令不會宣稱看過影片，也不會取代 `motion_project.py review`。

## 產物與能力限制

主要產物位於 profile 的 workspace、records、output：`timeline.json`、`captions.srt`、`captions.vtt`、`canonical-audio.m4a`、`source-fingerprints.json`、`prepare.json`、`render.json`、`review.json`、字幕畫格、成片畫格，以及最後的 `video.mp4`、字幕來源與播放／下載 HTML。

字幕預設燒錄。FFmpeg 有 `subtitles` filter 時使用 libass；目前 macOS 若沒有該 filter，會使用 `sips` 將 SVG 字幕畫格轉成 PNG 再 overlay，因此替代路徑需要 macOS sips，未宣稱跨平台。

抽幀、ASR、播放指令、metadata 與 audio hash 都是獨立證據，不能冒充直接連續聽看。工具會如實把無法驗證的 continuous AV 或未提供的視覺 assessment 標成未驗證，並阻擋交付。
