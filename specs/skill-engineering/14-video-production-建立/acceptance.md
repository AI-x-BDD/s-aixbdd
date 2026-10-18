# video-production 驗收

本頁記錄實際執行結果；代理實跑不等於使用者驗收，直接連續聽看仍未驗證。

| 情境 | 狀態 | 證據與範圍 |
| --- | --- | --- |
| S1 新主題完整流程 | 通過（代理實跑） | 暖白退款三幕、24.433秒；兩個實質方向有聲燒錄預覽，修後均綁新版本評審；正式 paper-flow 成片 `c5605a4c…`；使用者 pending |
| S2 既定方向及原音 | 修後代理檢查通過，使用者待驗收 | 淺綠四幕13.5秒，原音SHA不變；原 pass 撤回後修動靜與一幀錯幕；新片 `792751eb…`，S12序列複查 |
| S3 提案授權邊界 | 通過 | 兩支隔離短候選實際編碼抽幀；正式 sentinel SHA 不變；沒有正式 delivery。授權由 Skill 閘門判斷，非 CLI 自動判授權 |
| S4 缺工具／無直接影音能力 | 通過 | 缺 FFmpeg prepare exit 2，修復後可編碼；直接連續聽看維持未驗證 |
| S5 漏項／提早失焦／錯對象 | 通過 | 每類獨立 CLI exit 1，修復同契約 exit 0，未以 stale source 代替指定缺陷 |
| S6 形變失名／裁切 | 通過 | 每類獨立阻擋後修復；實際過渡圖另由 S8 覆蓋 |
| S7 證據過期 | 通過 | 改來源、渲染中變更、替換 MP4、修改 runtime 均 exit 2；修復後重建 |
| S8 三類視覺缺陷 | 通過 | 六支真實有聲／燒錄 MP4，修前 fail、修後 pass；從編碼片抽風險、中途與尾端畫格實看 |
| S9 對齊及字幕 | 通過 | 改稿未對齊阻擋；缺燒錄與長字幕遮內容以實際畫格判 fail，修後重輸出看圖 |
| S10 搬移與雙 profile | 通過（同機搬移） | 已補兩側 Skill、三個 required MIT Skills、來源及授權；固定版 Remotion 下載／291 檔 hash 清單。init/npm ci/prepare/render/review/deliver、profile 隔離及缺依賴 exit 2 均實跑 |
| S11 工程與來源保護 | 通過 | 最終 audit 0 error、1 可解釋 warning；實體同步與三組樣板核對一致；18 工具測試通過；123 基準檔無遺失，僅交付狀態摘要依授權改動，HEAD 不變 |

| S12 核心與動靜節奏 | 原片 fail → 可觀察缺陷修後通過；主觀節奏未驗證 | 植物原52352…保留；手指落定後2.2秒、第二幕靜止、澆水落定後約1.67秒、排水結尾約1.2秒；三切點與收束逐幀序列；退款亦逐節拍回歸 |

## 詳細紀錄

- [故障及授權環境](../../../videos/build/video-production-acceptance/isolated-8j6e2god/acceptance/results.md)：S3–S7、S9；S3 為依預先回覆執行的 Skill 授權閘門，實際候選與 sentinel 核對。
- [視覺故障環境](../../../videos/build/video-production-acceptance/isolated-q7q_evgg/acceptance/s8/results.md)：S8，短 fixture，非完整 Skill 製片。
- [附加字幕視覺環境](../../../videos/build/video-production-acceptance/isolated-q7q_evgg/acceptance/s8/s9/results.md)：S9，四支修前修後短片。
- [工具測試](tool-tests.json)、[來源保護](preservation.json)、[施工及修復紀錄](implementation.md)。

建置產物位於忽略版控的 `videos/build/`，本次保留；重新執行不依賴舊影片。

- [原始提示及補充逐項核對](request-checklist.md)、[節奏根因與補正](rhythm-addendum.md)、[Claude Code 複查摘要](claude-rhythm-review.txt)。

## 新主題最終版本

- [退款製作計畫](../../../videos/build/video-production-acceptance/isolated-pmq66uoq/videos/projects/refund/製作計畫.md)、[兩案比較](../../../videos/build/video-production-acceptance/isolated-pmq66uoq/videos/projects/refund/候選方向評審.md)、[逐幕與節拍](../../../videos/build/video-production-acceptance/isolated-pmq66uoq/videos/projects/refund/分鏡與焦點.md)、[評審與交付](../../../videos/build/video-production-acceptance/isolated-pmq66uoq/videos/projects/refund/評審與交付.md)。正式 SHA `c5605a4ce6884651346a0792214ec0eef647919a6f2764ab179e73a8989baf4d`；另一候選 `fdf25aee81e9122fa8c0fc3f9b5bf6b14a93f1d78ca815de4a08a86d8f51816a`。兩案最終 review pass，continuous_av unverified／使用者 pending。
- [植物分鏡](../../../videos/build/video-production-acceptance/isolated-smozlqqm/videos/build/plant-watering/records/分鏡與焦點.md)、[植物評審與節奏複查](../../../videos/build/video-production-acceptance/isolated-smozlqqm/videos/build/plant-watering/records/評審與交付.md)。正式 SHA `792751eb3cccb7939a4472793ded73d14944e7c4461578a6f6187d9aba05940d`；三個切點整數幀對齊，v4 編碼序列重新擷取。原音 SHA `e06d8988892b915ad2709b2e732a3ac5df082536ce4ad87f8dfcd052c7065d9f`，未裁語音。
- [瀏覽器驗證](browser-check.json)：新版13.5秒720p實際播放進度前進、無media error，下載SHA與植物新成片相同；這只驗證播放下載，不代表AI直接聽看。

本輪新主題測試不是首次無人介入即成功：首次字幕輸出、列舉契約、遮擋與節奏均曾失敗並修正。無本次分析脈絡的代理成功從新素材啟動；修正與補驗過程及使用者否定紀錄全部保留。

## S10 最終證據與範圍

[搬移紀錄](portable/portable-S10-驗證.md)、[完整清單](portable/portable-s10-manifest.json)、[profile 隔離](portable/portable-isolation-v2.json)、[缺依賴](portable/portable-missing-dependency-v2.json) 已從暫存目錄保存至本紀錄。搬移不依賴 CH2 素材或本次對話；仍使用同機唯讀模型與已安裝的 Python/uv、Node/npm、FFmpeg、sips，未宣稱跨主機零安裝。無授權的 Remotion Skill 原文未打包，保留固定 revision 取得及逐檔驗 hash 做法。

[最終一致性檢查](final-verification.json) 確認植物、退款兩方向的 MP4、render 與來源證據相符，搬移包兩側 Skill 與第三方原文逐檔一致。使用者實際驗證仍未驗證。

## 使用者檢視後的驗證範圍更正

使用者指出測試片簡陋、與 CH2 差距明顯，並確認美術方向選擇未向真人展示確認。原 S1／S2 通過只涵蓋所列工程、動態及隔離情境，不代表美術探索充分、真人已選方向或 CH2 最低完成度已達標。植物「淺綠植物風」是測試預設，相關紀錄中的「使用者已確認」不是本次真人確認；退款的紙卡／路徑比較也未證明美術語言探索充分。原完成聲明不可再作為這些能力已驗證的證據。後續優化與新驗收另見 [15 號工程案](../15-video-production-美術方向選擇與驗收/blueprint.md)；保留原測試事實與歷史檔案。
