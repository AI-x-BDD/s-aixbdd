# 雙鑽石實戰案例

## 目錄

- Excel 匯出：需求偷偷包含解法
- 進階篩選：從需求到 Problem Statement
- 搜尋不好用：簡單案例
- Google Login：PM 提的是 Solution
- 換 Redis：最容易判斷錯
- SQL Injection：不跑完整流程
- 參考資料

## Excel 匯出：需求偷偷包含解法

PM：「會員列表加一個 Excel 匯出按鈕。」

不要理解成「需求 = 做 Excel 按鈕」。先問：

```text
為什麼需要匯出？誰需要？拿去做什麼？多久做一次？
真正問題是資料無法整理？報表功能不足？還是財務系統需要資料？
```

可能發現：

```text
真正問題：會計每月底要統計會員方案。（第一鑽石）

解法 A：Excel          （第二鑽石）
解法 B：直接提供月報
解法 C：自動寄報表
解法 D：Accounting API
```

## 進階篩選：從需求到 Problem Statement

需求：「搜尋頁要新增進階篩選。」

Step 0 列未知：為什麼？哪些人？現在遇到什麼困難？多常發生？目前怎麼繞過？成功長什麼樣？

Discover：70% support ticket 不是抱怨搜尋條件少，而是搜尋結果太多，使用者分不出資料差在哪。

Define：原本「新增 20 個搜尋條件」重新定義為「幫助客服快速找到最可能符合條件的會員」。

```text
客服人員
在尋找會員時，經常得到大量相似搜尋結果，
因此平均需要 45 秒找到正確會員。
目標：降到 15 秒。
限制：不能增加會員個資曝光。
```

Develop：

```text
A 精準篩選  B 搜尋排名  C 顯示更多識別資訊
D 最近查詢  E autocomplete  F fuzzy search
```

用 wireframe、SQL query、技術 spike 做便宜驗證。

Deliver：剩下 A 搜尋排名、B 精準篩選，測試使用者能否找到人、速度改善、錯誤率、效能、開發與維護成本後選定。

## 搜尋不好用：簡單案例

使用者說：「搜尋不好用。」

- Discover：看搜尋 log、客服 ticket、使用者操作。問題不在演算法，而是很多人不知道會員編號在哪。
- Define：使用者不知道可搜尋哪些資訊。
- Develop：A placeholder、B examples、C autocomplete、D 搜尋提示。
- Deliver：快速 prototype 測試，autocomplete 效果最好。

## Google Login：PM 提的是 Solution

PM：「註冊流程新增 Google Login。」

- Discover：查 abandonment 在哪。大部分使用者卡在 email verification 信太晚收到。
- Define：Email verification friction 太高；登入方式太少不是主因。
- Develop：A Google Login、B 改寄信流程、C resend、D magic link、E verification 延後。
- Deliver：先改善寄信 + resend，成本可能遠低於導入 OAuth。

## 換 Redis：最容易判斷錯

老闆：「系統太慢，要換 Redis。」錯誤做法是直接開工。

- Discover：先量 frontend、network、backend、DB、3rd-party API。瓶頸是 SQL N+1 query。
- Define：DB query 次數爆炸。
- Develop：A eager loading、B batch query、C cache、D schema／index。
- Deliver：可能根本不需要 Redis。

## SQL Injection：不跑完整流程

Production API 有 SQL Injection 漏洞。不要先開 workshop：

```text
Contain → Patch → Deploy → Verify
```

之後才進入 Problem Discovery：為什麼 code review 沒抓到？為什麼測試沒抓到？為什麼架構允許？

## 參考資料

- [Design Council：Framework for Innovation](https://www.designcouncil.org.uk/resources/framework-for-innovation/)：四階段、兩次發散收斂、非線性、四個 Design Principles。
- [Design Council：The Double Diamond](https://www.designcouncil.org.uk/resources/the-double-diamond/)：它是描述流程的模型，不是逐步操作說明書。
- [Design Council：History of the Double Diamond](https://www.designcouncil.org.uk/resources/the-double-diamond/history-of-the-double-diamond/)：Design the right thing／Design the thing right、design brief。
- [NN/g：Discovery: Definition](https://www.nngroup.com/articles/discovery-phase/)：Discovery 如何研究使用者、商業與技術未知數。
- [IDEO：Design Thinking Process](https://designthinking.ideo.com/process)：Creating choices → Making choices。
