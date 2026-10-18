# 固定影片風格庫

這是 video-production 的必要本機依賴；新片先在此選用，不在每次製作時臨時上網找風格。

- 7 種可用參數化解說形式：3Blue1Brown 式推導、Keynote UI、財經圖表、Kurzgesagt 式資訊圖解、Vox 式註解、白板、動態文字。名稱表示上游參考，不表示品牌背書。
- 35 種 Canvas 藝術風格預覽；其中 Rembrandt 為上游一星弱項，展示但禁止作正式候選。因此目前有 41 個可選 ID，並非 41 個已通過新題材成片驗收的模板。
- 17 份研究配方、需另備素材的 presenter-led 與另一個 SVG 示範不計入可選庫。
- [可播放目錄](index.html) 的藝術片段為 3 秒原庫示範；7 種解說示範依原範例長度，均無旁白、無燒錄字幕。這些不代替本片的同內容有聲候選。

## 本機使用與檢查

在 videos 目錄執行，check/list/gallery 只需 Python 3.11 以上標準庫，沒有網路請求：

```sh
python3 scripts/style_library.py check --library style-library
python3 scripts/style_library.py list --library style-library
python3 scripts/style_library.py gallery --library style-library
python3 -m http.server 60083 --bind 127.0.0.1
```

瀏覽 http://127.0.0.1:60083/style-library/ 。正式新片設定：

```toml
style_library_required = true
style_library = "style-library" # 相對 videos 工具根目錄
style_selection = "projects/my-film/style-selection.json" # 相對 source_root
```

選用檔範例（SHA 必須取當前 catalog.json；不得複製占位值）：

```json
{"catalog_sha256":"當前目錄 SHA256","choices":[{"id":"y3_whiteboard","content_reason":"逐步揭示責任交接，適合首次操作觀眾","adaptation":"改為本片訂單、審核者與付款紀錄；依旁白安排揭示與穩定閱讀"}]}
```

check 加上 `--selection 本片選用檔.json` 可驗證；motion_project.py 的 prepare/render/review/deliver 均呼叫此檢查，且指紋綁定目錄、選用檔及鎖檔。缺少欄位會報錯；歷史重建或隔離工程測試須在隔離設定明列 style_library_required=false 與 legacy_style_reason，不修改原歷史資料，也不能把豁免當成新片範本。

## 來源與重建

固定原文在 `../.agents/skills/huashu-art-motion/`；上游 https://github.com/alchaincyf/huashu-art-motion ，revision `8a0d7d72ca65fcce6f8ba82c4a6c8dfe35b8422c`。upstream-lock.json 記錄逐檔 SHA，catalog.json 記錄預覽 SHA、來源卡與實作。不得執行上游自動更新；擴充、改版須單獨重建並重驗選用證據。

預覽重建另需 ffmpeg/ffprobe、Playwright 1.64.0 與相符 Chromium；首次安裝瀏覽器需下載，此後可離線重建。macOS 實跑，其他平台未實跑。

```sh
uv run --with playwright==1.64.0 python -m playwright install chromium
uv run --with playwright==1.64.0 --script scripts/style_library.py render --library style-library --workers 2
```

每個原範例 spec 保存在 specs/，藝術風格由固定引擎及 ID 重建；render-logs/ 保存實際命令輸出。建置會完整解碼各 MP4、取得規格並產生海報與雜湊。它不自動判定審美或新題材適配通過。

## 授權與搬移

保留上游 LICENSE、README 及所有附帶聲明。程式與文件 MIT；字體依各自 OFL；筆順資料依 Arphic 授權（本包不收錄該參考整片）。原作者角色、Clawd 及部分原示範圖像保留權利，只展示上游示範，禁止搬入新片。新片使用自身合法素材，不以本專案 MIT 概括第三方資產。

搬移時必須帶齊主 Skill、videos 工具包、此目錄與固定上游目錄；不能只複製 SKILL.md。字型、模型、配音環境另依當次工具檢查。固定庫缺失或改動、預覽缺失／過期、未知／弱項 ID、過期選用紀錄都阻擋新片建置。

角色故事 y4_storytime 因上游只附角色圖片占位路徑，目前不可選、無預覽；待專案具備合法角色素材並補足預覽後才可啟用。原庫 8 種解說形式不等於本機可用 8 種。

已確認的舊方向可沿用，選用檔改以 `reuse: {"evidence":"確認紀錄.md","sha256":"該實檔雜湊","adaptation":"本片適配方法"}` 取代 choices，檔案必須隨本片攜帶；不偽造庫內 ID。

本機採必要檔案子集：保留 295 檔原文，排除 214 個不供目前渲染使用的展示／角色資產與參考整片。`upstream-lock.json` 保留被排除路徑、原 SHA 與理由；不是修改第三方原文。上游 README 中被排除素材的連結僅作來源說明，不是本包可用資產。

藝術方向需依原始規範製作新場景，不是 34 個換字即用的影片模板；7 種解說形式則有可參數化 cues 實作。兩者皆須按新內容檢驗，不能只套用原示範構圖。
