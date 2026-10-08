# s-aixbdd

## 關於這個 repo

這個 repo 收錄我自己整理的 Skill 與開發過程，之後預計會再增加。

## 結構說明

| 路徑              | 內容                                                                               |
| ----------------- | ---------------------------------------------------------------------------------- |
| `.claude/skills/` | Claude Code 格式的 skills                                                          |
| `.agents/skills/` | Codex／.agents 格式的 skills（目前以 symlink 指向 `.claude/skills/` 的同名資料夾） |
| `VERSION`         | template 版本                                                                      |
| `docs/`           | Skill 的來源筆記、各章需求清單與過程紀錄                                           |
| `docs/ch1.md`     | ch1 的 Skill 說明與實作驗證                                                        |
| `src/`、`pom.xml` | String Calculator 實作與測試（Java 21、Maven、JUnit 5）                            |

## 各章內容

| 章節 | Skill | 說明 |
| ---- | ----- | ---- |
| ch1  | `double-diamond`、`trunk-based-development`、`conventional-commits` | [docs/ch1.md](docs/ch1.md) |

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
