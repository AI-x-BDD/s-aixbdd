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
│   ├── conventional-commits.md
│   ├── 主幹式開發.md
│   └── 雙鑽石原則.md
└── .claude/skills/            專案層級 Skills，只在本專案生效
    ├── agent-reach/           外部安裝，來源 Panniantong/agent-reach（CLI 在 ~/.agent-reach-venv）
    ├── conventional-commits/  自建，依 docs/conventional-commits.md 撰寫
    ├── double-diamond/        自建，依 docs/雙鑽石原則.md 撰寫
    └── trunk-based-development/  自建，依 docs/主幹式開發.md 撰寫
```

## Skills

- Skill 放在 `.claude/skills/<name>/SKILL.md`，每個 Skill 一個資料夾。
- 從外部 repo 安裝的 Skill 保持原樣，不直接修改內容；要更新時從上游重新複製。
- 自建的 Skill（目前是 `conventional-commits`、`double-diamond`、`trunk-based-development`）可以直接修改；來源筆記更新時，一併同步 Skill 內容。
