# Codex 的選用 Jev 路由

這是製作、複習與修改 Skill 時使用的 Codex 工作環境設定，不是課程產出的 Skill。
不修改 `.agents/skills/` 或 `.claude/skills/`，也不讓那些 Skill 依賴 Jev。

## 目前行為

- 預設關閉，關閉時不呼叫 Jev。
- 開啟後，`UserPromptSubmit` 將本輪 `prompt` 送到 TypeSafe 分流。開啟表示同意這項外部傳送。
- 只有明確的找路徑、列出項目、計數與文字格式轉換，才可能交給 `jev_light`。
- `jev_light` 使用 `gpt-6-luna`／`high`；模型是否可用取決於帳號權限。
- 寫檔、修改 Skill、課程審查、根因分析、設計及含糊的「繼續」留給原本的主代理。
- Jev 的機率與 confidence 均須至少 0.9 才提出輕量派工指示。這是未校準的試驗門檻，不代表正確率。
- 主代理仍須對照完整上下文、既有授權與 Skill 規範，才能派工。Hook 沒有切換主模型，也不保證代理一定服從指示。
- Hook 不傳送對話歷史、專案名稱或自行讀取的檔案；但本輪 prompt 中貼入的資料也屬於傳送內容。
- 偵測到部分常見憑證格式、輸入過長、子代理事件、金鑰缺漏、低信心、API 錯誤或逾時時，沒有路由指示，交回原流程。憑證偵測不是完整的敏感資料防護；有私人內容時先關閉。
- 不記錄 prompt、金鑰或遠端錯誤。網路請求逾時設定為 4 秒，整個 Hook 逾時為 10 秒。
- 這個 Hook 只處理輸入時的分流，不檢查中途產生的改善提案。

## 使用

在專案根目錄操作。需要 Python 3.9 以上，只使用標準函式庫，不安裝套件。

1. 提供 Jev 金鑰：優先使用 `TYPESAFE_API_KEY`；macOS 另支援目前使用者 Keychain 中 service 為 `codex-jev-router` 的 generic password。金鑰不放進 repo。使用 Keychain 不必重啟既有 Codex；使用環境變數則須在啟動 Codex 的終端設定，既有程序不會自動繼承後來設定的值。
2. 啟動 Codex，透過 `/hooks` 檢查並信任專案的 Hook。不要手動改寫信任雜湊，也不需要繞過 Hook 信任。
3. 在終端手動開啟：

   ```sh
   python3 .codex/hooks/jev_router.py on
   ```

4. 查詢或關閉：

   ```sh
   python3 .codex/hooks/jev_router.py status
   python3 .codex/hooks/jev_router.py off
   ```

開關只寫入被 Git 忽略的 `.codex/jev-router/enabled`，不存放金鑰。
也可在啟動 Codex 前設定 `JEV_ROUTER_DISABLE=1`，強制停用路由。

`status` 只表示狀態檔及目前程序能否從環境變數或 Keychain 取得金鑰；不代表 Hook 已信任、金鑰有效或模型可用。
可在 Codex 內以假設的找檔任務觀察是否派給 `jev_light`，並用代理切換畫面確認實際執行模型。
比較開／關時的品質、整輪用量與等待時間，不能只把 Jev 回覆時間當作整體節省。

## 驗證範圍

```sh
PYTHONDONTWRITEBYTECODE=1 python3 .codex/tests/test_jev_router.py
```

本機檢查驗證開關、敏感內容與缺欄位攔截、API 請求格式、答案驗證、例外回退與關閉狀態。
使用 mock，不呼叫外部 API。前次八題假設案例的實測只驗證限制判斷，不是這個模型路由題的準確率證據。
本機已完成 Hook 信任、實際派工與輕量模型可用性驗證；新電腦仍須重新驗證。
實際品質與成本節省尚未驗證。

2026-10-15 啟用紀錄：已透過 Codex `/hooks` 信任專案 Hook，並開啟路由。
已確認 Keychain 可讀取金鑰，Jev API 可回傳模型層級選項。
後續在隔離專案以真實 Jev 完成自動派工驗收：父 session 有 `spawn_agent(agent_type="jev_light")`，
子 session 使用 `gpt-6-luna`／`high` 並回覆正確結果。
`codex exec --json` 未呈現建立事件，不能只用該串流判定沒有派工。
換機安裝請依 [使用指南](../docs/codex-jev/codex-jev使用指南.md)操作，安裝來源集中在 `docs/codex-jev/`。

## 官方依據

- [Codex Hooks](https://learn.chatgpt.com/docs/hooks)：設定、信任、`UserPromptSubmit` 與 `additionalContext`。
- [Codex 子代理](https://learn.chatgpt.com/docs/agent-configuration/subagents)：`.codex/agents/*.toml` 與模型設定。
- [TypeSafe API](https://docs.typesafe.ai/api.md)：`state`、`questions` 與 Choice 答案。
