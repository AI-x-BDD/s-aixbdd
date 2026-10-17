# Rule 1 - 規則分級

- **核心規則**（違反就不算 TBD）：沒有長期開發分支；頻繁整合 main，DORA 至少每天一次、一天多次更好；main 保持可工作，CI 紅了先修 main，不繼續開發新功能，DORA 建議立即修或立即 revert，不是「晚上再看」。
- **強烈建議**：branch 非常短命（官方約 1～2 天，DORA < 1 天）；active branches 盡量少；不靠 code freeze 解決整合問題；merge 後刪 branch。
- **團隊自行決定**（不要說成 TBD 的要求）：squash、merge commit、rebase merge、同步 main 用 merge 還是 rebase、branch 命名、reviewer 人數、GitHub 或 GitLab、是否禁止 direct push。

## Good Example

- 回答把 main 維持可工作列為核心規則，並把 squash 方式列為團隊選項。

## Bad Example

- 把團隊選擇的 squash merge 寫成違反 TBD 的核心規則。
