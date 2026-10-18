# 網購退款：新手操作說明｜B 俯視桌面插畫 評審與交付

## 版本與證據

- 候選版本識別：`refund-s1-style-b`
- profile：`videos/projects/refund-s1/style-b/project.toml`
- encoded MP4：`videos/build/refund-s1-style-b/output/refund-flow-style-b.mp4`
- MP4 SHA-256：`da92851c9c17607b2050bbea2bc378270e44d4f8666c7225f8ebeea39edff7a0`
- source fingerprints SHA-256：`84e3729d250c011616eef2bf1a1c427a95c16cc1360eb013f96b5efe5b7e506b`
- review：`videos/build/refund-s1-style-b/records/review.json`
- subtitle evidence：`videos/build/refund-s1-style-b/records/subtitle-evidence.json`
- motion checks：`videos/build/refund-s1-style-b/records/motion-checks.json`
- playback/download：`videos/build/refund-s1-style-b/output/delivery.html`（播放器與下載連結指向同一 MP4）
- review verdict：`pass`；`automated_state`、`technical`、`static_visual`、`subtitle_visibility`、`audio_analysis` 均為 `pass`。

## 分項結果

| 項目 | 結果 | 實際證據 |
| --- | --- | --- |
| 1280×720／30 fps／24.433333 秒 | 通過 | `capability-probe.json`、`review.json` 的 encoded probe |
| 完整 24 秒原音與 AAC stream | 技術通過 | `review.json` 的 canonical/movie AAC stream hash；未宣稱直接聽感 |
| 733 frames／11 段 focus contract | 通過 | `records/motion-checks.json`（state／contract 逐影格） |
| 燒錄字幕 | 通過 | `records/subtitle-evidence.json`、6 個 `subtitle-frames/caption-*.png` |
| 靜態視覺與 label | 通過 | 本輪 encoded review frames 與切點序列；`assessment.json` 綁定當前 MP4 SHA |
| 連續聲畫 | 未驗證 | `continuous_av=unverified`，工具沒有直接連續聽看輸入 |

## 美術方向與實片符合性

- 美術方向：以有邊界的桌墊、便箋、手部、人物、橡皮章、撕下退款單與開放帳本承擔操作關係。
- 實片符合性：encoded 畫格將審核人變成桌面人物、將核准變成實體蓋章、將回接變成把退款單放回帳本；圖像語言與 A 的流程軌道有實質差異。
- 取捨：桌面物件與角色較多，情境更強但小畫面閱讀負荷較高；適合想要操作感的版本。
- 方向狀態：AI 畫格評審通過，真人方向待確認。

## 問題、修正與複查

初版只像紙卡加網格，已重做為桌面場景，讓人物／手／印章／帳本承擔敘事；最後同樣將退款單置於帳本左側，保留完整標籤。

複查以最後一次 render 後的 `review.json`、`assessment.json` 和現行 output MP4 為準；沒有沿用被遮擋的舊序列作為最終通過證據。`records/visual-review/cut-1-final.png`、`cut-2-final.png`、`scene-3-final.png`；`subtitle-frames/caption-0004.png` 顯示撕下退款單的「退款單」完整且與付款紀錄分離。

## 核心、節奏與切點序列複查

- 7.20 秒「交給審核人」：`cut-1-final.png` 是本輪 MP4 6.83–7.50 秒的連續畫格；review transition frames：frame-0207 (6.90s)、frame-0210 (7.00s)、frame-0213 (7.10s)、frame-0216 (7.20s)、frame-0219 (7.30s)、frame-0222 (7.40s)、frame-0457 (15.23s)、frame-0460 (15.33s)、frame-0463 (15.43s)、frame-0466 (15.53s)、frame-0469 (15.63s)、frame-0472 (15.73s)、frame-0475 (15.83s)。確認交接物件在切點前後可追蹤。
- 12.72 秒「申請轉退款單」：以 `review.json` 約 12.7–14.13 秒的 transition／contract frames 複查；先退場再落定，沒有「退款申請」與「退款單」重影。
- 15.56 秒「回接付款紀錄」：`cut-2-final.png` 是本輪 MP4 15.17–16.00 秒的連續畫格；`scene-3-final.png` 展示穩定段。退款單與付款紀錄的名稱均完整可見。
- 約 17.8 秒 label：`subtitle-frames/caption-0004.png` 實看，旁白字幕完整，物件 label「退款單」完整，未被付款紀錄框遮擋。

## 交付與重建

- 交付頁：`videos/build/refund-s1-style-b/output/delivery.html`
- 同一 MP4 下載：`videos/build/refund-s1-style-b/output/refund-flow-style-b.mp4`
- 可修改字幕：`captions.srt`、`captions.vtt`
- 重建：`uv run --frozen python scripts/motion_project.py --config videos/projects/refund-s1/style-b/project.toml render`
- `delivery.json` 已綁定 review、render 與 MP4 SHA；目前 `user_acceptance` 保持 `pending`。

## 使用者驗收

- 狀態：`pending`
- 測試回覆：`測試接受推薦`（測試來源，完成比較頁展示後的測試字串，不是真人確認）
- 真人美術方向：待確認
- 真人全片／連續聲畫：待確認；目前 `continuous_av=unverified`
