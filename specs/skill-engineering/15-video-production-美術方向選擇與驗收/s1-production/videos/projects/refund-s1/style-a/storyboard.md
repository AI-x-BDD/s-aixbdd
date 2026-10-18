# 網購退款：新手操作說明｜A 紙面流程軌道 分鏡與焦點

## 場景與理解目標

本案沿用同一份 `content.json`、`alignment.json`、`voice.m4a`，完整 24.433 秒時間軸、1280×720／30 fps、燒錄字幕。觀眾是第一次申請退款的網購使用者；三段旁白的理解順序是「找原訂單／交給審核／回接付款紀錄」。

固定水平流程軌道與編輯式紙面層級。三段內容使用同一條視線路徑，文件卡、審核人、退款單與付款紀錄依語意節點交接。

| 時間／旁白段 | 畫面與動作 | 理解焦點 |
| --- | --- | --- |
| 0.00–7.20／「先找到原訂單……送出申請」 | `01` 軌道展開；原訂單卡固定在左側，商品與退款原因依序亮起，送出申請按鈕在尾端被強調。 | 先定位哪一張單，再核對兩個欄位，最後送出。 |
| 7.20–15.56／「申請會交給審核人……轉成退款單」 | `02` 節點交給退款申請卡與審核人；條件符合章落下。12.72 秒開始，申請／審核物件先淡出，退款單獨立落定，避免「退款申請」與「退款單」殘字重疊。 | 身份從申請轉成退款單，轉換有明確先後。 |
| 15.56–24.433／「最後，把退款單回接付款紀錄……」 | `03` 退款單保持在付款紀錄左側，付款紀錄框從右側接入，金額、方式、進度依序亮起。17.8 秒退款單完整顯示「退款單」，不被付款紀錄框遮住。 | 退款單仍是同一個對象，回接後讀取三項資訊並追蹤。 |


## 動態與可讀性設計

- 每個語意物件使用固定中文 label；label 只出現在承擔該關係的物件上，避免旁白段落變更時身份混用。
- 12.72 秒的身份變換採「舊物件先淡出、退款單再落定」；不讓「退款申請」與「退款單」同時以高可見度重疊。
- 15.56 秒之後退款單與付款紀錄保持分離；17.8 秒 encoded caption 畫格確認兩者名稱完整可讀。
- 字幕固定在底部安全區；底部只放旁白結論，沒有把內部製作規則當成觀眾文字。

## 核心與動靜節奏

- 0–7.2 秒以節點逐步亮起，語音每個動詞都有一個可見回應。
- 7.2 秒是「交給審核人」切點；取樣 `records/visual-review/cut-1-final.png`，包含 6.83–7.50 秒連續畫格。
- 12.72 秒是身份變換；以 review 的 `frame-0037` 起始序列核對淡出／落定，確保標籤不殘留。
- 15.56 秒是「回接付款紀錄」切點；取樣 `records/visual-review/cut-2-final.png`，包含 15.17–16.00 秒連續畫格；`scene-3-final.png` 和 `subtitle-frames/caption-0004.png` 核對退款單與付款紀錄的分離與可讀性。


## 獨立焦點契約

| 區間 | `required_active` | 內容目的 |
| --- | --- | --- |
| 0.00–2.24 | `order-card` 原訂單 | 先找到原訂單 |
| 2.24–4.98 | `product-check` 商品、`reason-check` 退款原因 | 核對申請條件 |
| 4.98–7.20 | `submit-button` 送出申請 | 完成送出 |
| 7.20–9.48 | `application-card` 退款申請、`reviewer` 審核人 | 把申請交給審核人 |
| 9.48–11.70 | `reviewer` 審核人 | 審核條件 |
| 11.70–12.72 | `approval-stamp` 條件符合 | 明確表示通過 |
| 12.72–15.56 | `refund-ticket` 退款單 | 申請轉成退款單 |
| 15.56–19.04 | `refund-ticket` 退款單、`payment-ledger` 付款紀錄 | 將退款單回接紀錄 |
| 19.04–20.20 | `amount` 金額 | 讀取金額 |
| 20.20–21.76 | `method` 方式 | 讀取方式 |
| 21.76–24.433 | `progress` 進度、`trace-line` 追蹤款項 | 追蹤款項 |


兩案 contract、state、labels 完全相同；差異只在 render source、空間與動作語言。完整 contract 來源是 `videos/build/refund-s1-style-a/workspace/motion/public/focus-contract.json`，逐影格檢查在 `videos/build/refund-s1-style-a/records/motion-checks.json`。

## 檢查區間與過渡取樣

- 交接切點：`records/visual-review/cut-1-final.png`，以 6.83–7.50 秒的連續 encoded frame 檢查 7.20 秒前後的物件交接。
- 回接切點：`records/visual-review/cut-2-final.png`，以 15.17–16.00 秒的連續 encoded frame 檢查 15.56 秒前後的付款紀錄接入。
- 身份轉換與 label：`records/review.json` 的 12.7 秒左右 transition frames，以及 `records/subtitle-frames/caption-0004.png`（約 17.8 秒）實看；結果記錄在 `review.md`。

## 供工具讀取的資料位置

- profile：`videos/projects/refund-s1/style-a/project.toml`
- source materials：`videos/projects/refund-s1/style-a/materials/`
- Remotion source：`videos/build/refund-s1-style-a/workspace/motion/src/Root.tsx`
- encoded movie：`videos/build/refund-s1-style-a/output/refund-flow-style-a.mp4`
- delivery player：`videos/build/refund-s1-style-a/output/delivery.html`
- review：`videos/build/refund-s1-style-a/records/review.json`、`subtitle-evidence.json`
