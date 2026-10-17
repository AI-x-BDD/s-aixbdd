# Rule 1 - 回答時區分規則來源與 branch 壽命

- 回答時必須區分規則來源：**TBD 官方**是 TrunkBasedDevelopment.com；**DORA** 是 Google DORA 的 DevOps 研究，標準通常比官方嚴格；**團隊規則**是 TBD 沒規定、由團隊自行決定的部分。
- 官方的短期 branch 通常為 1～2 天，DORA 以不到一天為目標；不要把「2 天」說成硬性標準。

## Good Example

- 同一個 branch 壽命問題同時呈現兩個來源的標準，並把團隊期限另列為團隊規則。

```text
TBD 官方：短期 branch 通常 1～2 天。
DORA：以不到一天為目標。
團隊規則：若團隊另定 2 天，這是團隊規則，不是 TBD 硬性上限。
```

## Bad Example

- 把 DORA 目標與官方常見範圍合併成單一硬性門檻。

```text
TBD 規定所有 branch 最多只能活 2 天。
```
