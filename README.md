# s-aixbdd

## 關於這個 repo

這個 repo 收錄我自己整理的 Skill 與開發過程，之後預計會再增加。

## 結構說明

| 路徑              | 內容                                                                               |
| ----------------- | ---------------------------------------------------------------------------------- |
| `.claude/skills/` | Claude Code 格式的 skills                                                          |
| `.agents/skills/` | Codex／.agents 格式的 skills（與 `.claude/skills/` 實體相同，用 `scripts/sync-skills.sh` 同步） |
| `VERSION`         | template 版本                                                                      |
| `docs/`           | Skill 的來源筆記、各章需求清單與過程紀錄                                           |
| `docs/ch1.md`     | ch1 的 Skill 說明與實作驗證                                                        |
| `src/`、`pom.xml` | String Calculator 實作與測試（Java 21、Maven、JUnit 5）                            |
| `specs/`          | 第二份作業的紀錄：`skill-engineering/` 為 Skill 建立與優化的藍圖和根因報告，`plan/` 為類別圖提案 |
| `java-web-framework/` | 第二份作業以 `plan-with-class-diagram` 規劃實作的 Java Web 框架（Java 17、Maven、JUnit 5） |
| `assets/`         | Skill 資源目錄結構示意圖                                                           |
| `skills/`、`upstreams/`、`scripts/install.sh`、`scripts/sync-upstreams.sh`、`skills-lock.json` | 來自 [stevecyj/skills](https://github.com/stevecyj/skills) 的個人 Skill、上游 submodule 與安裝腳本，見下方「個人 Skill 與安裝腳本」 |
| `LICENSE`         | MIT 授權原文（來自 [stevecyj/skills](https://github.com/stevecyj/skills)）與本 repo 的授權範圍，見下方「授權」 |

## 各章內容

| 章節 | Skill | 說明 |
| ---- | ----- | ---- |
| ch1  | `double-diamond`、`trunk-based-development`、`conventional-commits` | [docs/ch1.md](docs/ch1.md) |
| 第二份作業 | `skill-engineering`、`skill-form-*`（description、sop、rule、template、script）、`skill-derive-*`（rule、template、script）、`plan-with-class-diagram`；另收錄外部的 `skill-creator` | [specs/](specs/)、[java-web-framework/](java-web-framework/) |

## 個人 Skill 與安裝腳本

第二份作業原本放在 [stevecyj/skills](https://github.com/stevecyj/skills)，以保留雙方 Git 歷史的 merge 整合進本 repo。根目錄的 `skills/`、`upstreams/`、`scripts/install.sh` 與 `scripts/sync-upstreams.sh` 是個人跨專案使用的 Skill 與安裝工具，和課程平台讀取的 `.claude/skills/`、`.agents/skills/` 分開；`install.sh` 會在家目錄建立 symlink，只影響個人環境。

以下保留原 repo README 的內容，其中的 clone 網址與 `~/src/skills` 路徑仍以原 repo 為準。

Personal agent skills for Codex CLI and Claude Code.

`skills/` contains skills maintained here. `upstreams/` contains third-party skills as Git submodules, so their history and release updates stay with the original authors.

### Install

```bash
git clone --recurse-submodules https://github.com/stevecyj/skills.git ~/src/skills
~/src/skills/scripts/install.sh
```

The installer creates a symbolic link for every managed skill in both locations:

- Codex CLI: `~/.agents/skills/<skill>`
- Claude Code: `~/.claude/skills/<skill>`

It preserves a non-symlinked skill with the same name and reports the conflict instead of overwriting it.

#### Important: `--recurse-submodules`

The `--recurse-submodules` flag is **required** to clone upstream skills (no-ai-slop, shuorenhua, etc.). Without it, the `upstreams/` directory will be empty and those skills won't be available.

**If you already cloned without `--recurse-submodules`:**

```bash
cd ~/src/skills
git submodule update --init --recursive
~/src/skills/scripts/install.sh
```

#### Verify installation

After running `install.sh`, confirm all 7 skills are linked:

```bash
ls -la ~/.claude/skills/ | grep -E "transcript|commit|article|slop|shuorenhua|ste100"
# Should show symlinks to all 7 skills
```

### Update

Update this repository and its pinned upstream versions:

```bash
git pull --ff-only
git submodule update --init --recursive
./scripts/install.sh
```

To review and adopt the newest upstream versions, run:

```bash
./scripts/sync-upstreams.sh
git diff --submodule=log
git commit -am "chore: update upstream skills"
git push
```

The sync script never commits or pushes. Review the submodule revisions before committing them.

### Managed upstreams

| Skill | Source |
| --- | --- |
| `asd-ste100-skill` | [`danyuchn/asd-ste100-skill`](https://github.com/danyuchn/asd-ste100-skill) (MIT) |
| `no-ai-slop` | [`petergyang/no-ai-slop`](https://github.com/petergyang/no-ai-slop) (MIT) |
| `shuorenhua` | [`MrGeDiao/shuorenhua`](https://github.com/MrGeDiao/shuorenhua) (MIT) |

Third-party files remain in their own repositories; this repo records only the upstream commit to use.

## 授權

完整範圍以 [LICENSE](LICENSE) 為準，摘要如下：

- **MIT**：我擁有權利的自建程式與 Skill，包括第一份作業的 `src/`、`pom.xml`、`scripts/sync-skills.sh` 與 `conventional-commits`、`double-diamond`、`trunk-based-development`，以及第二份作業的 `skill-engineering`、`skill-form-*`、`skill-derive-*`、`plan-with-class-diagram`。
- **沿用原狀**：原 stevecyj/skills 的其他內容（`skills/`、`java-web-framework/`、`specs/`、`assets/`、`scripts/install.sh`、`scripts/sync-upstreams.sh`、`skills-lock.json`）維持該 repo 原本的授權狀態。
- **第三方與課程內容，保留各自授權**：
  - `skill-creator`：來自 [anthropics/skills](https://github.com/anthropics/skills)，Apache License 2.0，見 `skill-creator/LICENSE.txt`
  - `upstreams/` 的 submodule：依各自 repo 的授權
  - 水球軟體學院課程官方文字及素材：文末官方區塊、`CLAUDE.md`／`AGENTS.md` 的「課程產出規範」、兩個 `skills/README.md`、`VERSION`
- **未宣告**：`docs/` 的學習筆記與過程紀錄。

## 交流

使用上的問題或改進建議，歡迎開 issue 討論。

---

## 官方宣告（以下區塊請保留）

本 repo 為[水球軟體學院](https://world.waterballsa.tw)《AI x
BDD：規格驅動全自動化開發術》課程的學員產出，用於公告課程中道館作業的展示，並依[官方 Template](https://github.com/AI-x-BDD/aixbdd-skill-homework-template)
建立。

《AI x BDD：規格驅動全自動化開發術》課程四大特色：

1. **【軟工方法論＋結果導向】** 只談 AI
   coding 不談軟工方法論，是不學無術！課程中強調結果導向的開發方法：只要訂好驗收標準，就可以 One-Shot 開發到位！
2. **【最完整的 SDD 概念與實作】**
   市面上最完整的 SDD 課程，一次教你 Skills、SDD、TDD、BDD 的知識與實踐，輕鬆實踐高效可靠全自動開發。
3. **【企業級實戰導入】** 用企業級實踐導入高規格，不只學會工具，更知道如何舉一反三完全客製化企業專案需求。
4. **【課程教學方式與物超所值】**
   這是一堂理論、實務跟實戰三者兼具的 SDD 線上課程，用工作坊級別的學習體驗，不是只是教概念，而是直接帶著做！

[了解更多課程內容說明](https://waterballs.tw/Ghl6O)

## 開源專案：AI x BDD

水球老師把這套 AI x BDD 的方法論做成開源 pipeline skill：把產品迭代寫成 Gherkin，再一路帶到 RED → GREEN → REFACTOR。

覺得有幫助，歡迎給它一顆 Star：

[![Star Waterball-Software-Academy/aixbdd](https://img.shields.io/github/stars/Waterball-Software-Academy/aixbdd?style=social)](https://github.com/Waterball-Software-Academy/aixbdd)

## 相關問題洽詢管道

1. [水球軟體學院 LINE 官方帳號](https://lin.ee/STIsOLZ)
2. 客服信箱：[support@waterballsa.tw](mailto:support@waterballsa.tw)
3. [水球軟體學院（社群）Discord](https://discord.gg/Ymjz7NmZXn)

---

© 2026 水球球特務有限公司版權所有，侵害必究。
