# CH2 動態敘事（Remotion）

本目錄保留 CH2 個案與固定版官方 Skill 取得方式。新章節使用 [video-production](../../.agents/skills/video-production/SKILL.md) 及 [通用工作區骨架](../templates/motion-project/README.md)，不直接套用下方 CH2 的場景程式與數字。

使用者於 2026-10-18 選定 M2 動態敘事套用九幕，維持 B 深色配色、113 秒、原旁白與燒錄字幕。以物件展開、拆出、委派、分流、回接及局部鏡頭帶領注意力。最新完成與評審狀態見 [交付狀態](../../docs/過程/CH2/影片/製作紀錄/設計/新流程測試/交付狀態.md)。

## 重建

需 macOS、Python 3.11+、uv、FFmpeg、PingFang TC 與可執行的 Node.js 22+。runtime 優先 `NODE_BINARY`、PATH，再找 nvm；同機曾有預設 node 報 Bad CPU type，因此不只檢查路徑存在。原始音檔放置方式見 [素材 README](../../docs/過程/CH2/影片/素材/README.md)。

從 repo 根目錄：

```sh
make -C videos setup
make -C videos check test
make -C videos render
make -C videos preview
```

預設 profile `projects/ch2-workflow-test/project.toml`；`Full-Motion` 為 1600×900、25fps、2825 影格。準備程式直接讀原始配音與對齊，不依賴舊 MP4。原音訊流直接複製至正式影片。輸出 `videos/build/ch2-workflow-test/動態正式版/`，入口 <http://127.0.0.1:60071/預覽/交付.html>。

開發時在本目錄執行 `npx remotion studio`（先確認 node 可用）；九幕時間、字幕及片語時間由 `public/segments.json` 供應，準備步驟自動產生。`src/motion-state.ts` 提供實際繪圖共用的位置、可見性與焦點；`scripts/export-state.cjs` 匯出全片狀態，供 Python 以獨立旁白主焦點表檢查。來源修改後須重建，禁止用舊抽幀當新影片評審。

## 代表片段比較歷程

原選版比較保留：scene02（11.16–38.80 秒）與 scene07（53.04–70.44 秒），各有固定構圖 B、M1 連續焦點與 M2 動態敘事。使用者已選 M2，不再等待選版。

若要重建比較，需原固定構圖 B 位於 `build/ch2-workflow-test/正式版/`，且正式建置沒有正在執行：

```sh
videos/.venv/bin/python videos/projects/ch2-workflow-test/motion_samples.py prepare
videos/.venv/bin/python videos/projects/ch2-workflow-test/motion_samples.py render review
```

此 `prepare` 同樣保留九幕輸入，不會改成只剩兩幕。輸出 `build/ch2-workflow-test/動態提案/index.html`。代表片段的設計與觀察見 [motion-動態提案](../../docs/過程/CH2/影片/製作紀錄/設計/新流程測試/motion-動態提案.md)。

## 官方 Skill 與授權

| 項目 | 來源與固定版本 | 授權 | 本 repo 收錄方式 |
| --- | --- | --- | --- |
| Remotion 引擎 | [remotion-dev/remotion](https://github.com/remotion-dev/remotion)，npm 4.0.536（tag commit `d16a341`），版本鎖在 `package-lock.json` | Remotion License：個人、3 人以下營利組織、非營利免費；其他營利組織需 Company License。**不是 MIT** | 只透過 npm 安裝，不收錄原始碼 |
| 官方 Agent Skill | [remotion-dev/skills](https://github.com/remotion-dev/skills) `remotion-best-practices`，revision `1441a11`（skill 版本 4.0.536） | repo 未附授權檔 | **不收錄原文**；`scripts/install-official-skills.sh` 下載到 `videos/.cache/official-skills/`（已忽略），以 `official-skills.sha256` 逐檔核對 |

官方安裝指令是 `npx skills add remotion-dev/skills`；這裡改用固定 revision 下載（`videos/motion/scripts/install-official-skills.sh`，已存在時只核對雜湊），以便重建時取得同一份內容。使用時直接讀 `videos/.cache/official-skills/remotion-dev-skills/1441a11e95db35443bd76bb318386c0d3ca00053/skills/remotion-best-practices/SKILL.md`。詳細來源、星數與查核日期見 [來源.json](來源.json)。

本目錄自寫的程式（`src/`、`scripts/`、設定檔）依根目錄 [LICENSE](../../LICENSE) 的範圍處理；`package.json` 以 `SEE LICENSE IN ../../LICENSE` 指向它。Remotion 引擎本身仍受 Remotion License 約束。

本專案渲染時不傳 `licenseKey`；依 4.0.536 原始碼，此時不會送出使用事件。首次渲染會下載 Chrome Headless Shell（Remotion 自動處理）。

## 檢查範圍

`make review` 核對完整解碼、規格、原 AAC 音訊流、來源指紋及 49 段共 2825 影格的實際繪圖狀態，另確認短句移動物件的識別文字持續可見（各段起點後 0.24 秒至終點前 0.04 秒為核對區間，進場／交棒另看實際抽幀），擷取每段中點／尾端與全片每秒畫格。`make test` 故意注入消失、錯焦點、裁切與空白焦點檔案，確認檢查能阻擋。

AI 未直接聽看全片，音訊辨識與抽幀不代表聽感、連續節奏或舒適度已驗證；另一台電腦重建亦未驗證。技術及靜態視覺評審結果以個案交付狀態與成片證據為準。
