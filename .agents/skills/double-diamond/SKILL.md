---
name: double-diamond
description: 依雙鑽石原則（Double Diamond：Discover → Define → Develop → Deliver，兩次發散 → 收斂）釐清需求、定義問題與比較解法。用在：收到需求／ticket／老闆或 PM 指定的做法（例如「加 Excel 匯出」「換 Redis」「加 Google Login」「加 AI Chatbot」）時判斷它是問題還是已經是解法、拆解真正要解的問題、撰寫 Problem Statement／Design Brief／Success Criteria、判斷目前卡在哪個階段與下一步該做什麼、展開多個方案並挑選最便宜的驗證方式、判斷研究是否已經夠了、判斷某個變更需不需要跑完整流程（小修正、緊急事故、法規要求），以及說明 Double Diamond 與 Design Thinking、Agile 的關係。
---

# 雙鑽石原則（Double Diamond）

雙鑽石要防兩件事：太早認定問題、太早愛上某個解法。

```text
第一鑽石  Problem Space   找對事情（Design the right thing）
  Discover  發散：挑戰「我們以為的問題」
  Define    收斂：根據證據決定真正要解什麼
第二鑽石  Solution Space  把事情做好（Design the thing right）
  Develop   發散：展開多個方案，做便宜的驗證
  Deliver   收斂：用測試與證據留下有效方案
```

注意兩個常見誤解：Develop 不是「開始寫 code」，是發展多種可能方案（sketch、prototype、技術 spike、小型 PoC）；Deliver 不是「deploy」，是驗證、淘汰、改善後找到真的可行的方案。

回答時區分說法來源，不要把實務判斷說成官方規定：

- **官方定義／官方原則**：Design Council（Framework for Innovation、The Double Diamond、History）。
- **業界慣例**：NN/g、IDEO 等，例如 Desirable／Viable／Feasible、Decision Gate。
- **實務判斷**：例如「研究何時算夠」。

Double Diamond 是描述設計流程的模型，不是規格或逐步 SOP。不存在「沒做五次訪談所以違反 Double Diamond」這種說法。流程不是線性的，任何階段都可以因為新的學習回到前面。

官方四個 Design Principles：Put people first、Communicate visually and inclusively、Collaborate and co-create、Iterate, iterate, iterate。

## 先判斷不確定性在哪

不先問「現在在哪一階段」，先問「現在還有什麼不知道」：

```text
收到需求
│
├─ 問題、原因、解法、驗證方式都已明確？
│   └─ Yes → 直接做／壓縮流程（見「不需要完整流程」）
│
├─ 不知道真正問題？                 → Discover
├─ 有很多問題，不知道先做哪個？       → Define
├─ 問題清楚，不知道怎麼解？           → Develop
└─ 已有解法，不知道是否有效？         → Deliver / Test
```

## 日常四問

碰到需求先用這四題檢查，不用每次畫兩顆鑽石：

1. **Problem**：我現在講的是問題，還是其實已經是解法？（「需要加 Tab」是解法）
2. **Evidence**：這是證據，還是某個人猜的？（「老闆覺得大家不會用」是 Hypothesis）
3. **Alternatives**：是不是只考慮一個方案？是的話，第二鑽石沒有展開。
4. **Validation**：拿什麼證明這個方案成功？答案是「大家覺得不錯」代表 Deliver 還沒完成。

## 各階段做法

### Step 0：收到需求

不要直接開 Jira 切 component。先列出已知與未知：

```text
已知：<需求原文>
未知：為什麼？哪些人？現在遇到什麼困難？多常發生？目前怎麼繞過？成功長什麼樣？
```

### Discover（發散）

目標是拆掉「我們以為的問題」。看四類資料：

- **使用者**：訪談、觀察、support ticket、customer／sales feedback。
- **行為**：analytics、funnel、error log、search log、session replay。
- **Business**：revenue、conversion、retention、人工作業成本、法規。
- **Technology**：API 限制、performance、legacy system、security、資料品質。

NN/g 的三面向可當檢查：Desirable（使用者想要）、Viable（商業可行）、Feasible（技術可行）。

何時算夠（實務判斷，非官方規定）：不看訪談人數，看「最大的未知是否已經小到足以做決策」。繼續研究不太可能改變決策時就收斂。

### Define（收斂）

把資料轉成決策：Evidence → Pattern → Insight → Problem → Priority。

產出 Problem Statement，至少回答五件事：

```text
誰：<對象>
遇到什麼問題：<具體情境>
為什麼重要：<影響、數據>
什麼叫成功：<可量測的目標>
限制：<不能違反的條件>
```

例：客服人員尋找會員時經常得到大量相似結果，平均 45 秒才找到正確會員；目標降到 15 秒；限制是不能增加個資曝光。這比「新增 Advanced Search」好，因為有對象、數字目標與限制。

沒有回答「所以到底要解什麼」，Define 就沒完成，不管整理了多少便利貼。

### Develop（發散）

先增加選項，不要第一個方案直接做。列出至少數個方向不同的方案，再用便宜的方式驗證：wireframe、prototype、SQL query、技術 spike、mock API、fake door、小規模 PoC。

選方案不問「哪個最漂亮」，問「哪個方案可以最便宜地驗證最大的風險」。Prototype 只要能回答一個還不知道的問題，不需要像正式產品。

### Deliver（收斂）

對剩下的候選方案測試：使用者能不能完成任務、改善多少、錯誤率、效能、開發成本、維護成本。淘汰不能工作的方案，改善後選定。

Deliver 之後不是結束：Production → Measure → Learn → 必要時重新 Discover／Define／Develop。

### Decision Gate（業界慣例，非官方強制）

```text
Discover → Define   有足夠證據了嗎？
Define   → Develop  問題清楚嗎？
Develop  → Deliver  方案有證據支持嗎？
Deliver  → Launch   風險可接受嗎？
```

## 適用與例外

特別適合：問題不明確（例如留存降低）、利害關係人多、解法成本高（重寫系統、支付流程、大型改版）、需求本身很可能只是解法（例如「新增 AI Chatbot」）。

不需要完整流程：

- **問題、原因、解法、驗證都已知**（padding 寫錯、timeout 5 秒改 10 秒）：直接修。為了看起來有流程而跑 workshop 是 process theatre。
- **緊急事故**（production 全掛、SQL injection）：先 contain → patch → deploy → verify，事後再 incident review，那時才進入 Discover root cause。
- **法規要求**：第一鑽石可以很短，第二鑽石（UI 怎麼放、怎麼減少摩擦）仍有價值。
- **成熟問題、團隊領域知識充足**：壓縮流程，而不是完全拿掉（NN/g 觀點）。

## 常見錯誤

1. **把需求當問題**：PM 說「做 Excel export」就開工。應先問為什麼需要 export。
2. **Discover 無止境**：研究的目的是降低足以影響決策的不確定性，不是越多越好。
3. **Define 只是整理便利貼**：100 張 Post-it 拍照就結束。
4. **Develop 只有一個方案**：設計畫一版、工程開發，實際上沒有第二鑽石。
5. **Prototype 做太完整**：用最簡單能測試想法的原型。
6. **把四階段當 Waterfall**：官方直接否定「做完不能回頭」。

## 與其他方法的關係

- **Design Thinking**：較大的思考哲學；Double Diamond 是把設計流程視覺化的一種方法。IDEO 的 Creating choices → Making choices 就是發散 → 收斂。
- **Agile**：Double Diamond 回答「應該做什麼」，Agile 回答「怎麼快速、持續把東西做好」。接法：Discover／Define → Product Backlog → Develop／Deliver → Sprint → Feedback → 重新 Discover。

## 輸出格式

分析一個需求時用這個格式：

```text
需求原文：<...>
判斷：這是問題／已經是解法
目前最大的不確定性：<...> → 所在階段：<Discover／Define／Develop／Deliver／不需完整流程>
Problem Statement：誰／問題／為什麼重要／成功指標／限制（證據不足的欄位標「待驗證」）
候選方案：A … B … C …（至少三個方向不同的方案；問題未定義時先不列）
最便宜的驗證：<用什麼方式驗證哪個最大風險>
下一步：<具體行動>
```

證據與假設要分開寫，不要把 stakeholder 的說法當成已驗證的 fact。

完整案例（Excel 匯出、搜尋不好用、Google Login、換 Redis、SQL Injection、進階篩選）見 [references/cases.md](references/cases.md)。
