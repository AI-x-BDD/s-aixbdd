# Rule 1 - 常見錯誤

- 「我們都從 main 開 branch，所以是 TBD」不成立：feature branch 活 2～3 週就不是 TBD。
- 一張 Story = 一個 branch = 一個 PR 不符合切小目的；一張 Story 可以拆成 refactor、API、UI、cleanup 多個 PR。
- 為了 merge 小而合併不能工作的 main 不符合 TBD；每一步都要保持可工作，用新舊並存處理跨層改動。
- PR 很小但等 review 三天時，效果跟三天 branch 一樣；branch 壽命要算入等 review 的時間。DORA 把重量級、非同步、耗時的 review 流程列為 TBD 常見阻礙。
- 多人在同一個 feature branch 開發、branch 一直不刪、接近 release 就 code freeze，都是官方 You're Doing It Wrong 列出的模式；main 變紅時先修 main 或立即 revert。

## Good Example

- review 等待三天時，回答把它視為 branch 壽命的一部分，並指出重量級 review 是整合阻礙。

## Bad Example

- 只因 PR 的程式碼很少，就說它符合 TBD，忽略 branch 已等待 review 三天。
