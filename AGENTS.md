# CLAUDE.md

給在本專案中工作的 AI coding agent（Claude Code、Codex、Cursor 等）閱讀的共用指引。

本 repo 依水球軟體學院《AI x BDD》課程的[官方 Template](https://github.com/AI-x-BDD/aixbdd-skill-homework-template)（`VERSION`：`2026.09-v1`）整理。下方「課程產出規範」取自官方 Template 的 `CLAUDE.md`。

## 規則

1. Always reply in ZH-TW

## 專案概覽

練習用專案，用來建立與試用 Agent Skills。

- 第一份作業（tag `homework-01`）：以 [Coding Dojo](https://codingdojo.org/) 的 String Calculator 題目（Java 21、Maven、JUnit 5）實際驗證三個自建 Skill。
- 第二份作業：由 [stevecyj/skills](https://github.com/stevecyj/skills) 以保留雙方 Git 歷史的 merge 整合進來，包含 `skill-engineering` 系列 Skill、`plan-with-class-diagram`，以及用它規劃實作的 `java-web-framework/`（Java 17、Maven、JUnit 5）。

- 測試：根目錄 `mvn test`（String Calculator）；`mvn test -f java-web-framework/pom.xml`（第二份作業）
- CI：`.github/workflows/ci.yml`，push 或 PR 到 `main` 時執行 `scripts/sync-skills.sh --check`、`mvn -B test` 與 `mvn -B test -f java-web-framework/pom.xml`

## 目錄結構

```
.
├── AGENTS.md                  與 CLAUDE.md 內容相同的實體檔，給讀 AGENTS.md 的 agent
├── CLAUDE.md                  本檔，agent 共用指引與課程產出規範
├── README.md                  repo 介紹，文末保留官方區塊
├── VERSION                    Template 版本
├── pom.xml                    Maven 設定
├── LICENSE                    MIT 授權原文（來自 stevecyj/skills）與授權範圍；第三方與課程內容為例外
├── skills-lock.json           外部 Skill（skill-creator）的來源與雜湊
├── scripts/
│   ├── sync-skills.sh         同步兩邊的 skills 與 CLAUDE.md／AGENTS.md
│   ├── install.sh             個人工具：把 skills/ 與 upstreams/ 的 Skill 以 symlink 裝到家目錄
│   └── sync-upstreams.sh      個人工具：更新 upstreams/ 的 submodule 版本
├── src/                       String Calculator 程式碼與測試
├── java-web-framework/        第二份作業的 Java Web 框架（獨立的 Maven 專案）
├── specs/                     第二份作業的紀錄
│   ├── skill-engineering/     skill-engineering 各次建立與優化的藍圖、根因報告
│   └── plan/                  plan-with-class-diagram 產出的類別圖提案
├── assets/                    Skill 資源目錄結構示意圖
├── skills/                    個人跨專案使用的 Skill，由 install.sh 安裝，不是課程平台讀取的路徑
├── upstreams/                 第三方 Skill 的 Git submodule，由 install.sh 安裝
├── docs/                      學習筆記
│   ├── ch1.md                 ch1 的 Skill 說明與實作驗證
│   ├── conventional-commits.md
│   ├── 主幹式開發.md
│   ├── 雙鑽石原則.md
│   ├── 需求清單.md            String Calculator 的 8 個開發步驟
│   └── 過程/                  各 Step 的過程紀錄與實作觀察
├── .claude/skills/            專案層級 Skills，只在本專案生效
│   ├── conventional-commits/  自建，依 docs/conventional-commits.md 撰寫
│   ├── double-diamond/        自建，依 docs/雙鑽石原則.md 撰寫
│   ├── trunk-based-development/  自建，依 docs/主幹式開發.md 撰寫
│   ├── skill-engineering/     自建，編排 Skill 的建立與優化
│   ├── skill-form-*/          自建，撰寫 Skill 單一部位（description、sop、rule、template、script）
│   ├── skill-derive-*/        自建，為 SOP 步驟抽出部位（rule、template、script）
│   ├── plan-with-class-diagram/  自建，實作前先提出類別圖
│   └── skill-creator/         外部，來源見 skills-lock.json，授權見 skill-creator/LICENSE.txt
└── .agents/skills/            Codex 等讀 .agents 的 agent 讀這裡；各 Skill 是 .claude/skills/ 的實體複製
```

## Skills

- Skill 放在 `.claude/skills/<name>/SKILL.md`，每個 Skill 一個資料夾。
- `.agents/skills/` 的內容須與 `.claude/skills/` 實體相同，不使用 symlink（課程平台與 Windows 不一定會跟著 symlink 讀取）。兩個 `skills/README.md` 刻意寫給不同 agent，不需要相同。
- 在任一邊建立、修改或刪除 Skill，或修改 `CLAUDE.md`／`AGENTS.md` 之後，從自己編輯的那一邊執行同步：
  - 改的是 `.claude/skills/` 或 `CLAUDE.md`：`scripts/sync-skills.sh --from claude`
  - 改的是 `.agents/skills/` 或 `AGENTS.md`：`scripts/sync-skills.sh --from agents`
  - 刪除 Skill 時，腳本不會刪除另一邊的同名資料夾，要手動刪掉兩邊。
  - 同步後用 `scripts/sync-skills.sh --check` 確認兩邊一致；CI 也會執行這項檢查。
- 從外部 repo 安裝的 Skill 保持原樣，不直接修改內容；要更新時從上游重新複製。
- 自建的 Skill（第一份作業的 `conventional-commits`、`double-diamond`、`trunk-based-development`，以及第二份作業的 `skill-engineering`、`skill-form-*`、`skill-derive-*`、`plan-with-class-diagram`）可以直接修改；來源筆記更新時，一併同步 Skill 內容。外部的 `skill-creator` 與它的 `LICENSE.txt` 保持原樣。
- `skill-engineering` 施工後在專案根目錄執行 `scripts/sync-skills.sh --from <寫入的一側>` 與 `--check`，以實體目錄同步兩邊，不建立 symlink。
- 授權範圍以根目錄 `LICENSE` 為準：自建程式與 Skill 採 MIT；`skill-creator`、`upstreams/`、課程官方文字及素材保留各自授權。不要更動既有的版權與授權聲明。
- 根目錄的 `skills/`、`upstreams/`、`scripts/install.sh`、`scripts/sync-upstreams.sh` 是個人工具，與課程產出無關：不要為了本專案執行 `install.sh`（會改動家目錄），也不要自行更新 submodule 版本。

## 課程產出規範

本 repo 是水球軟體學院「AI x BDD」課程的學員產出 repo（由官方 template 產生），可能是道館作業，也可能是學員想分享的 skill 群——定位由學員決定。
你（AI agent）在此 repo 的所有產出必須遵守本規範。

### 語言

- 與學員互動、文件內容一律使用繁體中文。
- 程式碼、識別字、指令、技術術語維持原文，不翻譯。

### 結構錨點不可動（最重要）

課程平台依固定路徑**自動抓取並展示 skills**，以下一律不得更名、搬移、刪除：

- 根目錄 `.claude/skills/`、`.agents/skills/` 路徑
- 根目錄 `VERSION` 檔
- 根目錄 `README.md` 文末的官方區塊：「官方宣告」「開源專案：AI x BDD」「相關問題洽詢管道」與版權宣告

### skills 就是產出

- 若本 repo 是道館作業：要繳交的 skill 清單以**課程平台道館頁列出的題目為準**——不多做、不漏做。
- skill 放進學員所用 agent 對應的目錄（`.claude/skills/` 或 `.agents/skills/`）。
- 每個 skill 必須可獨立運作：用途、觸發時機、步驟齊備，不依賴當次對話的上下文。
- 未經學員實際驗證的 skill，要在說明中標明「未驗證」，不得寫成已驗證。

### 宣傳自由 vs 規範界線

- 文末官方區塊以外，README 與 repo 內容**隨學員自由發揮**——這個 repo 同時是學員的開源作品集，鼓勵個人風格與對外宣傳。
- 不要主動把 README 改造成制式表單；學員要展示什麼、怎麼展示，由學員決定。

### 提交前守門（僅當學員把本 repo 當道館作業繳交）

學員表示要繳交時，逐項核對、缺漏明確列出、不默默略過：

1. 道館頁列出的 skills 是否都已就位（路徑正確、可獨立運作）。
2. demo 影片（3 分鐘內）是否已備妥。
3. 提醒學員：回課程平台貼上本 repo 連結＋影片連結，缺一不可。
4. 非繳交條件（不得列為缺漏）：可提醒學員，若這套方法論有幫助，歡迎到開源專案 https://github.com/Waterball-Software-Academy/aixbdd 按 Star 支持。
