# Contributing

這個 repo 由 Steve Tsao 維護。問題與建議請開 [issue](https://github.com/AI-x-BDD/s-aixbdd/issues)。

文件用繁體中文。程式碼、識別字、指令與技術術語維持原文。

## 改 Skill

Skill 有兩份實體副本：`.claude/skills/` 與 `.agents/skills/`。改其中一邊，再從那一邊同步，並確認一致：

```bash
scripts/sync-skills.sh --from claude   # 改的是 .claude/skills/ 或 CLAUDE.md
scripts/sync-skills.sh --from agents   # 改的是 .agents/skills/ 或 AGENTS.md
scripts/sync-skills.sh --check
```

刪除 Skill 時，腳本不會刪掉另一邊的同名資料夾，要兩邊都手動刪除。

`skill-creator` 來自上游，保持原樣，連同它的 `LICENSE.txt`。要更新時從上游重新複製。

## 測試

需要 Java 21 與 Maven。

```bash
mvn test
mvn test -f java-web-framework/pom.xml
```

## 不要動

- `README.md` 從 `## 官方宣告（以下區塊請保留）` 到檔案結尾。
- `VERSION`。
- 既有的版權與授權聲明。授權範圍以 `LICENSE` 為準。
- `upstreams/` 的 submodule 版本。不要為了這個 repo 執行 `scripts/install.sh`，它會改家目錄。

docs/ 下的筆記與過程紀錄供個人推進作業使用，保留所有權利，不適用 MIT 授權。改這些檔案前請先開 issue 討論。
