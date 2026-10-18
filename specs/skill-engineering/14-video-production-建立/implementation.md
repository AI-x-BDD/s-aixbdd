# video-production 施工與驗收紀錄

2026-10-18 使用者回覆「確認」，授權依工程藍圖施工，包括 E3 兩個方向候選及 A1／A2 關聯工作。代理工程與情境驗收已完成；使用者實際驗證、直接連續聽看與主觀節奏仍未驗證。

## 執行前保護

- 基準清單：本目錄的 `baseline.json`，包含原 Git HEAD/status 及 CH2 素材／紀錄／正式片雜湊。
- 不刪歷史、不重製已交付 CH2、不 commit/push。
- A1 專案工具先完成獨立測試，通過後才執行 W1–W9；A2 文件整合後執行 W10。

## 當次能力

- 實際查詢當次可呼叫工具：有本機命令、圖片檢視、瀏覽器操作；沒有直接連續音訊／影片理解工具。
- 後續可用 ASR 對齊、逐影格狀態、編碼成片抽幀作替代檢查；不宣稱 AI 直接聽看。
- 動畫、音訊與模型能力須由新主題實跑證據補齊；不得沿用 CH2 通過當新流程結果。

## Claude Code 協作

- 已執行 `herdr --skill`，驗證 Herdr 環境後使用既有 `ch2-readme-review` Claude Code 代理。
- 本輪唯讀查核第三方原文與授權：storyboard／editorial 既有固定版與 MIT 證據相符；motion-art-direction 原文與 `3c129f769d90a1328c209c386492333c9ac62312` 相符，已由 A2 補 LICENSE 與清單；Remotion 官方 Skill 留固定版下載與逐檔雜湊，不再散布原文。
- 主代理另實際下載 motion-art-direction 同一 revision 的 LICENSE 與三份原文比對，全部相符；原文不修改。

## 情境結果

A1：主代理重新執行 7 項工具測試與 10 項獨立焦點契約測試，全數通過。含 30fps 尾幀實際擷取。真實 say＋MLX 對齊／燒錄 smoke 僅驗證技術，黑畫面未評審、交付維持阻擋。

W1–W9：依施工順序完成；各階段 SKILL 快照見 construction/，最終 SOP 與已確認 To-Be 相符。

A2：已更新 WORKFLOW、README、HANDOFF、motion README 與當前交付狀態；補 motion-art-direction 固定 revision／MIT 證據，不改第三方原文。

W10 初次檢查（歷史狀態）：結構 audit 0 error、1 warning（P2 可略過，P3 仍須載入敘事規範，故保留兩處 READ）；sync --from agents／--check 均成功。S1、S2/S10 及 S3–S9 已啟動隔離複本驗收，尚未宣稱通過。

## 介面文件複查

Claude Code 指出舊 README 的 CH2 候選指令可能誤導新片，已明標歷史／既有重建，新片統一指向 motion_project。工具骨架 README 補完整 profile、資料與 assessment JSON schema。已將這兩份介面文件補入隔離環境，這是測試環境修正，不提供分析脈絡。

Claude Code 複查結論：最後三項程式交付阻擋（逐張評審綁定、外部 renderer 來源清單、MP4 替換偵測）及兩項文件缺漏均已解除。其結論屬唯讀程式／文件審查，不冒充影片觀看或動態效果驗收。

## 實片字幕缺陷與修復

S1/S2 首輪實片抽查發現：raw 動畫正常，燒錄後全白。macOS Quick Look 將透明 SVG 鋪成白底且縮放非正方形畫布，遮住原片；改以 sips 保留正確尺寸與 alpha。另實測 sips 的 SVG stroke／paint-order 會吞掉文字，改為在有底色字幕帶上繪製填色字。新增 test_motion_subtitles.py：實際編碼解碼後核對畫面上方保留原色、字幕區確實有亮字；先失敗後通過。已實際看修後 smoke 畫格。證據在 videos/build/video-production-acceptance/subtitle-regression/。

此為原工具實作缺陷，未變更已確認 Skill 流程／約束／驗收標準。修後工具同步隔離環境，要求舊來源與成片證據失效並重建複查。

S8 已完成三種實際缺陷及修復：連線壓字、移動形變無名、旁白期間無觀看對象。六支 3 秒有聲燒錄字幕 fixture，每支 0.2/1.4/2.8 秒從 MP4 重新抽幀；代理實際看圖，主代理另看三組風險畫格。修前不通過、修後通過；旁白未裁切、成對原音與 SRT 相同。獨立環境 results：`videos/build/video-production-acceptance/isolated-q7q_evgg/acceptance/s8/results.md`。

S9 視覺附加驗收亦完成：超大字幕遮內容、SRT 存在但成片未燒錄，均由實際 MP4 畫格判缺陷並重編修正。結果在同環境 `acceptance/s8/s9/results.md`。均不冒充完整 Skill 製片或直接聽看。

S1 首輪評審發現付款紀錄名稱被欄位卡遮住、列舉契約把多項合併。已按既有 Rule 要求移開遮擋，並從語音字詞拆逐項契約；正式交付尚未放行。

字幕修復後工具回歸：`videos/.venv/bin/python -m unittest videos/tests/test_motion_project.py videos/tests/check_motion_contracts.py videos/tests/test_motion_subtitles.py`，18 tests／13.226s／OK。字幕回歸改用非黑藍色來源，逐像素比對上方保留原色，可同時抓白底及黑底遮蓋。Claude Code 唯讀複查字幕修法未見阻擋；測試強度建議已採用。

## 使用者實看否定與本輪補正

使用者發現植物片動作未完就硬切、沒有重點與動靜節奏；原先代理判定不足，已撤回 S2 通過。根因與修改見 [節奏補充](rhythm-addendum.md)，新規則由 Claude Code 兩次唯讀複查，並以使用者再次提醒逐條核對提示。不得把這次問題當初步預覽而免驗。

最終工具 f22e93f…：18 tests／10.057s／OK；絕對 props 白片假設無法重現，移除因果註解（只有相對路徑選擇保留）。工具、動畫修改均使原證據失效，要求重建。

## W10／W13 最終收尾

兩個新主題皆實際製片，退款包含兩個不同方向候選；植物依使用者回饋修正動作收束、穩定理解與逐幀切點。最終三支成片、render 與來源指紋一致，見 final-verification.json。18 項工具測試通過；兩側 audit 各 0 error／1 可解釋 warning，實體同步通過。同機搬移包的兩側 Skill 與三個 required 第三方 Skill 逐檔比對一致；S10 最終證據另存 portable/。

原 CH2 成片未變；123 個保護檔沒有遺失，僅允許的目前交付狀態摘要變更；HEAD 不變。未刪歷史、未 commit/push。情境的實跑與 fixture 層級、外部模型及主機工具限制依 acceptance.md，不能合併為真人聽看驗收。
