# AGENTS.md

給在本專案中工作的 AI coding agent（Claude Code、Codex、Cursor 等）閱讀的共用指引。

## 規則

1. Always reply in ZH-TW

## 專案概覽

練習用專案，用來安裝與試用 Agent Skills。沒有建置、測試或執行流程。

## 目錄結構

```
.
├── AGENTS.md                  本檔，agent 共用指引
├── docs/                      學習筆記
│   └── conventional-commits.md
└── .claude/skills/            專案層級 Skills，只在本專案生效（目前沒有）
```

## Skills

- Skill 放在 `.claude/skills/<name>/SKILL.md`，每個 Skill 一個資料夾。
- 從外部 repo 安裝的 Skill 保持原樣，不直接修改內容；要更新時從上游重新複製。
