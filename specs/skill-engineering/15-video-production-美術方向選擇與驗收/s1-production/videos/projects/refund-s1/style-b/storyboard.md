# 網購退款：新手操作說明｜B 俯視桌面插畫 分鏡與焦點

## 場景與理解目標

本案沿用同一份 `content.json`、`alignment.json`、`voice.m4a`，完整 24.433 秒時間軸、1280×720／30 fps、燒錄字幕。觀眾是第一次申請退款的網購使用者；三段旁白的理解順序是「找原訂單／交給審核／回接付款紀錄」。

以一張有邊界的桌墊作為空間場景。便箋、手部、人物、實體印章、撕下的退款單與打開的帳本承擔操作與關係，畫面語言與 A 的抽象流程軌道不同。

| 時間／旁白段 | 畫面與動作 | 理解焦點 |
| --- | --- | --- |
| 0.00–7.20／「先找到原訂單……送出申請」 | 桌墊上的原訂單置中；商品／退款原因是兩張便箋，手部與藍色申請章在尾端完成動作。 | 觀眾看到實際桌面操作：找到單、核對便箋，再按下申請。 |
| 7.20–15.56／「申請會交給審核人……轉成退款單」 | 退款申請紙卡沿弧形線交給桌面人物；人物接手並以橡皮章表示條件符合，12.72 秒後紙卡變成帶齒邊的退款單。 | 人物承擔審核關係，手、線與印章把交接和核准具體化；變身時舊紙卡先退場。 |
| 15.56–24.433／「最後，把退款單回接付款紀錄……」 | 撕下的退款單保持在左側，開放帳本從右側攤開並以藍線回接；金額、方式、進度便籤依序貼上。 | 退款單和帳本是兩個可辨識物件，回接後能逐項查看並追蹤。 |


## 動態與可讀性設計

- 每個語意物件使用固定中文 label；label 只出現在承擔該關係的物件上，避免旁白段落變更時身份混用。
- 12.72 秒的身份變換採「舊物件先淡出、退款單再落定」；不讓「退款申請」與「退款單」同時以高可見度重疊。
- 15.56 秒之後退款單與付款紀錄保持分離；17.8 秒 encoded caption 畫格確認兩者名稱完整可讀。
- 字幕固定在底部安全區；底部只放旁白結論，沒有把內部製作規則當成觀眾文字。

## 核心與動靜節奏

- 0–7.2 秒以桌面物件的位移、按章與手部完成申請，節奏由靜到動。
- 7.2 秒交接以人物接紙與弧形線完成；取樣 `records/visual-review/cut-1-final.png`，包含 6.83–7.50 秒連續畫格。
- 12.72 秒身份變換先讓申請紙卡退場，再落下帶齒邊退款單；review 的 `frame-0037` 起始序列核對標籤唯一性。
- 15.56 秒帳本從右側攤開；取樣 `records/visual-review/cut-2-final.png`，包含 15.17–16.00 秒連續畫格；`scene-3-final.png`、`subtitle-frames/caption-0004.png` 核對完整退款單文字與帳本無遮擋。


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


兩案 contract、state、labels 完全相同；差異只在 render source、空間與動作語言。完整 contract 來源是 `videos/build/refund-s1-style-b/workspace/motion/public/focus-contract.json`，逐影格檢查在 `videos/build/refund-s1-style-b/records/motion-checks.json`。

## 檢查區間與過渡取樣

- 交接切點：`records/visual-review/cut-1-final.png`，以 6.83–7.50 秒的連續 encoded frame 檢查 7.20 秒前後的物件交接。
- 回接切點：`records/visual-review/cut-2-final.png`，以 15.17–16.00 秒的連續 encoded frame 檢查 15.56 秒前後的付款紀錄接入。
- 身份轉換與 label：`records/review.json` 的 12.7 秒左右 transition frames，以及 `records/subtitle-frames/caption-0004.png`（約 17.8 秒）實看；結果記錄在 `review.md`。

## 供工具讀取的資料位置

- profile：`videos/projects/refund-s1/style-b/project.toml`
- source materials：`videos/projects/refund-s1/style-b/materials/`
- Remotion source：`videos/build/refund-s1-style-b/workspace/motion/src/Root.tsx`
- encoded movie：`videos/build/refund-s1-style-b/output/refund-flow-style-b.mp4`
- delivery player：`videos/build/refund-s1-style-b/output/delivery.html`
- review：`videos/build/refund-s1-style-b/records/review.json`、`subtitle-evidence.json`
