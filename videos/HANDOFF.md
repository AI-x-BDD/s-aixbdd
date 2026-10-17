# s-aixbdd 影片製作交接

更新日期：2026-10-17。這份交接由 side conversation 完成，供主對話接續 CH2 影片內容修改。影片已在新環境重新產製，尚未完成正式配音與最終內容驗收。

## 接續位置

- 專案根目錄：`/Volumes/data/Projects-practice/s-aixbdd`。
- 新預覽：<http://127.0.0.1:60070/預覽.html>。
- 新 MP4：`videos/build/ch2-skill-engineering/計時預覽.mp4`，116.28 秒。
- 操作說明：`videos/README.md`。
- 原始旁白、分鏡與畫面設定：`docs/過程/CH2/影片/製作內容.json`。
- 原始圖稿：`docs/過程/CH2/影片/靜幀/00.svg` 至 `08.svg`；場景順序以 JSON 為準。

請從上述新預覽接續；原先 60069 的伺服器若仍存在，提供的是外層目錄中的既有預覽，不是新製作環境的輸出。本次未停止或操作原伺服器。

## 使用者已確認的目錄分工

1. `s-aixbdd` 的主要目的仍是打造 Skill，`docs/過程/CH2/影片/` 是持續累積的素材來源。CH3、CH4 也會有自己的素材；這些不是「舊目錄」，不搬進 videos，也不改成入口連結。
2. `videos/` 是有自身環境的影片製作專案，目前共用外層 Git repo，未建立巢狀 Git repo。原始素材放在外層；影片工具唯讀載入，衍生輸出寫入自己的 build。
3. `videos/` 未來可複製出去獨立運作；外部素材位置透過設定或 `SOURCE_ROOT` 指定。複製工具不包含外部素材。
4. 製作流程以大專案內的素材與程式為來源，執行時不再依賴 `/tmp`。既有 temp 檔未刪除，但無須保留它們才能重建目前影片。

## 本次完成

- 建立 `videos/pyproject.toml`、`uv.lock`、`.python-version`、`.gitignore`、Makefile、README。
- 建立 `videos/scripts/video.py`：環境檢查、系統語音、時間軸、字幕、SVG 轉 PNG、重點框、MP4、預覽及靜態伺服器。
- 建立 `videos/templates/preview.html`。模板不包含原始圖稿或旁白。
- 建立 `videos/projects/ch2-skill-engineering/project.toml`，設定外層來源、素材路徑與輸出路徑。
- 在外層素材目錄新增 `製作內容.json`，從現有旁白、分鏡與製作設定整理而來；最初只整理現有內容；後續已依下節重新改寫旁白與圖稿。
- 將原先臨時程式中的影片內容與通用製作工具分開。原始 SVG、既有外層輸出保留，新的 render 不再讀取既有 MP4／MP3／HTML，也不覆寫它們。
- 環境、uv 快取與輸出分別在 `videos/.venv/`、`.cache/uv/`、`build/`，均已忽略。

目前 Python 無第三方套件，使用本機 Python 3.11.14。外部工具為 FFmpeg／ffprobe、macOS say（Meijia）與 qlmanage；系統執行檔由電腦提供，未打包進 videos。目前流程限定 macOS，不宣稱跨作業系統支援。

## 最新敘事改寫

- 使用者要求搜尋簡報專家方法，改善開場拗口與整體敘事。已參考 Reynolds、Duarte 與 Assertion-Evidence，來源與採用方式見 `docs/過程/CH2/影片/簡報敘事調整.md`。
- 新開場「技能越改越難維護？」實際 1.64 秒，接自己做出的解法。全片九段、116.28 秒，沒有補時。
- 結構為問題 → 解法 → 兩組 primitives → 根因及藍圖 → 完整委派 → 三支技能前後對照 → 整體成果。五支 Form 與三支 Deriver 納入同一套分工。
- 改寫前 JSON 與六張 SVG 保存在外層素材的 `版本/20261017-敘事改寫前/`。最新仍為暫時系統語音，待使用者檢視。

## 已確認的節奏參考

2026-10-17，使用者肯定目前 116.28 秒版本的節奏與旁白展示方式，要求保留作後續參考。來源快照、九張 SVG、時間軸與節奏檢查位於 `docs/過程/CH2/影片/版本/20261017-節奏與旁白參考/`；方法與網路來源見 `docs/過程/CH2/影片/簡報敘事調整.md`。後續改寫先對照此版，不覆寫該參考快照。這不等同全片最終驗收。

## 初版確認與下一階段

使用者已確認目前長度、文字、聲音、畫面切換與紅框 focus 基本 OK，整體定位為影片草稿。後續工作聚焦正式配音對齊，以及美術／配色／視覺呈現。

- 製作過程：`docs/過程/CH2/影片/製作流程紀錄.md`。
- ElevenLabs 文字：`docs/過程/CH2/影片/正式配音/完整旁白.txt` 及九份分段 TXT，對應表見同目錄 README。
- 現有程式尚未支援匯入正式配音。收到音檔後需接入並重新計時，字幕與 focus 需重新對齊。
- 美術尚待提案與製作；保留目前已確認的內容與節奏作基準。

## 下一輪怎麼修改

在專案根目錄修改來源：

- 旁白與場景順序：`docs/過程/CH2/影片/製作內容.json` 的 scenes。
- 圖中文字與配置：同目錄 `靜幀/*.svg`。目前圖稿為 1600×900，使用 PingFang TC。
- 畫面強調：JSON 的 focus；其 phrase 必須存在於對應旁白，且順序一致。修改旁白時一併檢查這些定位字串。
- 證據引用：JSON 的 claims，路徑相對於設定的 source_root。
- 工具與預覽介面：`videos/scripts/video.py`、`videos/templates/preview.html`。

接著在 `videos/` 執行：

```sh
make check
make render
make preview
```

預覽伺服器若仍在執行，只需 render 後重新整理網頁，不要重複啟動同埠。此次預覽的 exec session 為 `1700`，啟動時 PID 為 `84428`；接手時用 `lsof -nP -iTCP:60070 -sTCP:LISTEN` 重新確認，不假設進程永久存在。

工具複製到另一處後，使用：

```sh
make setup
make check SOURCE_ROOT=/外部素材所在的大專案
make render SOURCE_ROOT=/外部素材所在的大專案
```

生成的 `腳本與分鏡.md`、`時間軸.json`、字幕與影片位於 build；修改內容應回到外層 `製作內容.json`，避免直接修改產物後被覆蓋。素材目錄裡原有同名產物保留作紀錄，目前不會跟隨新建置更新。

## 已驗證與界線

- `make setup`、`make check`、完整 `make render` 通過。
- 將工具複製到 `videos/build/portability-tool/`，不帶環境、快取或既有輸出，指定原外部來源後，成功建立新環境並完成 check、render。
- 工具獨立性驗證使用改寫前版本：原位置與複製位置都輸出 104.68 秒；六張生成 PNG 的 SHA-256 均一致。此紀錄不代表新版九張圖的雜湊。驗證紀錄為 `videos/build/環境驗證.json`。
- 新影片的靜音檢測在 -40 dB 門檻下，沒有長達 0.5 秒的靜音區間；無補時靜音，各段最後發聲至切換最大 0.157 秒（新版 116.28 秒）。
- 建置前後原始 JSON、SVG 雜湊相同。
- Chrome 已開啟新預覽，驗證播放能前進、字幕與畫面會切換；不能把這些檢查描述成使用者已驗收或正式配音完成。
- 執行碼、模板、專案設定不包含 `/tmp` 或目前電腦的絕對路徑。外層來源預設為相對路徑 `..`，可覆寫。
- `git diff --check` 無輸出；沒有修改既有已追蹤檔案。Git 當時顯示 `docs/過程/CH2/影片/` 與 `videos/` 為未追蹤。未 stage、commit、push，未修改 Skills、AGENTS、CI、根目錄 Maven 設定，也未安裝 Git LFS。
- 字幕與重點框仍為比例估時，未逐字校時；聲音為本機臨時語音。影片內容與視覺敘事仍待使用者繼續修改。

## 影片內容必須延續的決定

- 90–120 秒，上限 120 秒；主軸是 Skill Engineering、primitives 調度，以及三支 Skill 的前後差異。
- 描述完整實作時為五支 Form、三支 Deriver，共八支 primitives。Form Description 當成整體分工介紹，新版由「用途說明讓 AI 知道何時該用」表達；不要改回「另外增加／自行擴充」。課程題目指定七支與實作八支的差別，先前已向使用者說明，無須在片中插入這段沿革。
- 移除的左上角「道館二 / SKILL ENGINEERING」、左下角「stevecyj / s-aixbdd」不要重新加回。
- 腳本分支使用「可交給腳本自動處理」，不使用「適合機械操作」。
- DD 聚焦 SOP、判準、任務分流與需求分析的分工；不放「八題核心前後通過」等施工驗證過程。
- 節奏依實際旁白切換；不以預覽稿為由補數秒靜音。不要把 Conventional Commits 個別修正歷程當主軸，也不要讓測試細節搶走 Engineering 調度的篇幅。

## 交接方式

本 side conversation 無直接回填主對話訊息的工具。請在主對話貼上本交接檔路徑並要求先閱讀；檔案已存在共用工作目錄，可直接接續，無需重新建立環境。
