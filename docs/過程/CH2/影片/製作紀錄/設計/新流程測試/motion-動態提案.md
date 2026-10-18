# CH2 動態提案：連續焦點 vs. 動態敘事

日期：2026-10-18。狀態：**使用者已選 M2 動態敘事，九幕全片已實作；正式交付見 [交付狀態](交付狀態.md)**。以下為方向選擇前的代表片段比較紀錄，候選輸出另存；AI 未直接聽看。

## 為什麼要做

現行語意 SVG renderer 只有狀態切換。WORKFLOW 第 4 階段要求：設計需要物件移動、形變或鏡頭時，不能用輪流變色代替。`motion-art-direction` 只負責動態決策，不會產生畫面，所以這次接入 Remotion 實際渲染，在同一內容上比較「連續焦點」（M1）與「動態敘事」（M2）兩種動態語言，並以焦點直接切換的修訂後正式 B 作為精準焦點基準；三者差在動態，而不是換配色。

## 設計依據

- 共同限制：沿用正式 B 深色配色（#201D31／#373249／#F4F0FF／#C4BDD5，焦點 #D8EF8A）、原配音、片長、燒錄字幕帶（1422×800 內容框＋底部 100px）。所有動作以旁白字元對齊的片語起點為錨：多數在片語起點前 0.12 秒開始，經 0.2～1.1 秒緩動到位，到位通常晚於片語第一個字。
- 動態意圖（motion-art-direction 的主從與克制原則）：每個動作都要對應一個語意——焦點移動＝解說換到下一個對象；物件沿路徑移動＝工作交給下一個技能；形變＝同一份內容變成另一種形態（片段→獨立檔案、群組→標題列）；鏡頭推近＝要看細節，回全景＝回到整體關係。沒有裝飾循環。
- 換字不重疊：同一位置換文字一律先淡出再淡入（各 0.14 秒），避開正式 B 0.20 秒淡化曾出現的疊字。
- 官方 `remotion-best-practices`（固定 revision，見下方來源）採用：以 `useCurrentFrame()`＋`interpolate()` 驅動、不用 CSS 動畫、`@remotion/media` 的 `<Audio trimBefore>`、`@remotion/paths` 的 `interpolatePath`／`evolvePath`／`getPointAtLength`、`render`／`still` 指令。未採用 Studio 互動編輯用的 `Interactive.create()` 結構，因為四個合成由同一份模板程式產生，不需要逐一在 Studio 編輯。

## 兩段的具體設計

| 段落 | M1 連續焦點 | M2 動態敘事 |
| --- | --- | --- |
| scene02（11.16–38.80） | 「一組是格式把關」先出現五個虛線空位，唸到哪一項就填入哪一項；單一焦點色塊沿列舉、詳解、再下移到三種抽取連續滑動。焦點下的文字用裁切的深字層，移動途中壓到的部分是深字、其餘仍是淺字。 | 兩張群組卡片：Form 卡形變成標題列，部位從標題列落入空位；Deriver 卡退到右下待命。詳解時鏡頭推近 1.3 倍、說明框跟著當前部位移動；說到「另一組是部位抽取」回全景，Deriver 卡形變成標題列，流程步驟裡的規則／樣板／腳本片段依旁白沿曲線飛出、形變成 rules/、templates/、scripts/ 三份檔案，原位置留下虛線空位。 |
| scene07（53.04–70.44） | 版面同正式 B；焦點色塊 SOP → derive-rule → form-rule，說「再更新流程」時回接線依方向描回 SOP，焦點再滑回 SOP。 | 鏡頭從 SOP 文件第 3 步推近開始；「判斷規則」晶片沿路徑交到 derive-rule、再到 form-rule，形變成規則檔；回全景描出回接線，SOP 補上「讀取：何時讀、怎麼用」。「需要固定輸出或自動處理」時兩條虛線分支從 derive-rule 下方移出；「既有檔案只改內容」時鏡頭推向右側，既有檔案繞過抽取直接交給 form-rule。form-rule 在被呼叫時才出現。 |

## 實際畫格比較與推薦依據

畫格由 `motion_samples.py review` 從三版 MP4 同時間點擷取，位於 `videos/build/ch2-workflow-test/動態提案/scene02|scene07/{baseline,focus,motion}-總覽.png` 與 `畫格/`。

| 觀察（看過的畫格） | 基準／M1 | M2 |
| --- | --- | --- |
| scene07 59.4、60.6、62.6 秒 | 方框與回接線表達「有回接」，但規則檔本身沒有出現 | 晶片形變成規則檔、回接線從規則檔出發、SOP 多一行讀取時機：「產出檔案只是其中一步」有畫面上的因果 |
| scene07 64.6 秒 | 樣板／腳本只有一行灰字 | 兩條虛線分支在 derive-rule 下方，看得出「相同方式分派」 |
| scene07 67.6、70.2 秒 | 一行綠字說明 | 既有檔案的箭頭繞過 derive-rule 直接接到 form-rule |
| scene02 35.8、38.0 秒 | 三個抽取方塊並列 | 片段離開「流程步驟」、留下空位並成為獨立檔案，對應旁白「從流程步驟中分出來」 |
| scene02 16.5、21.5 秒 | M1 的空位＋逐項填入能數出「五個」；基準一開始五項均已可見 | 推近後部位與說明更大，但兩側部位被鏡頭切到邊緣 |

推薦（AI 依畫格判斷，未聽看）：

- **關係與流程轉換的段落用 M2**：scene07 全段、scene02 的 Deriver 部分。M2 把基準裡只靠文字說的關係（抽出、交棒、接回、繞過）變成看得到的動作，這是內容上的差異，不只是更花。
- **列舉與逐項說明用 M1**：scene02 的 Form 五項。逐項填入與連續焦點已足以跟上旁白；M2 的推近在這段收益小，還會讓兩側部位只剩邊緣。
- 若使用者偏好一致的動態語言，可全片用 M1（風險最低）；不建議全片都用 M2 的鏡頭推近。

以上需要使用者開聲音試看確認：動作速度是否跟得上語速、鏡頭移動是否造成不適，AI 無法判斷。

## 修正紀錄

首輪渲染後，AI 與 Codex 看畫格發現並修正：M2 推近時標題被裁（標題移到鏡頭外固定，鏡頭內容裁在標題線下）；scene07 開場右緣只剩 form-rule 窄條（改為被呼叫時才出現）；收尾推近切掉 form-rule 名稱（調整鏡頭中心與縮放）；FORM 標題列在鏡頭平移時被切（文字跟隨可見左緣）；晶片停在 derive-rule 名稱上（改停在節點下方）；SOP 第 3 步交出後深字壓在淡焦點上對比不足（改為框線＋淺字）；M1 移動中焦點蓋到淺字（改為裁切深字層）；M1 說明文字與 M2 檔名換字時重疊（改為先出後入）。

## 驗證

已驗證（`驗證.json`）：

- 四支候選與兩支基準皆 1600×900、25fps、有音訊，全段解碼（`-xerror`）無錯；候選片長 27.648／17.408 秒，與基準 27.64／17.40 秒相差一影格內。
- 原配音取自正式 B 成片（sha256 `912daad0…`）的音訊流 copy；正式 B 修訂前後音訊流雜湊相同（`1b19bb5a…`）。
- 候選與基準節錄解碼相減的殘差約 -54 dB。兩者都經重新編碼，這個數值僅供觀察可能錯段或偏移，門檻未校準，不作通過判準，也不代表聽感或差異來源已驗證。
- AI 看過兩段三版共 48 張同時間點畫格（含動作途中）及 M1 焦點滑動途中的靜幀。

未驗證：聲音自然度、聲畫節奏、動態舒適度（AI 未聽看）；全片套用；另一台電腦重建。

## 來源查核（2026-10-18）

| 項目 | URL 與固定版本 | GitHub 星數 | 授權 |
| --- | --- | --- | --- |
| Remotion 引擎 | https://github.com/remotion-dev/remotion ，npm 4.0.536，tag commit `d16a341948f8948a69ba260dd9a8b24732aa8f52` | 64,775 | Remotion License：個人、3 人以下營利組織、非營利免費，其他需 Company License；不是 MIT |
| 官方 Agent Skill | https://github.com/remotion-dev/skills ，revision `1441a11e95db35443bd76bb318386c0d3ca00053`（skill 4.0.536）；官方安裝指令 `npx skills add remotion-dev/skills` | 5,293 | repo 未附授權檔；原文不收錄，只下載到忽略的快取並保存逐檔雜湊 |

星數只代表關注度與社群規模，不是畫面品質或教學成效的證據。本次沒有找到針對這組 Skill 或以 Remotion 動畫改善說明影片理解度的公開成效研究；推薦依據只有上面的實際畫格比較。

## 重跑

見 [videos/motion/README.md](../../../../../../../videos/motion/README.md)。從 repo 根目錄：

```sh
nvm use 24
npm ci --prefix videos/motion
videos/.venv/bin/python videos/projects/ch2-workflow-test/motion_samples.py prepare
npm run typecheck --prefix videos/motion
videos/.venv/bin/python videos/projects/ch2-workflow-test/motion_samples.py render review
videos/motion/scripts/install-official-skills.sh   # 需要讀官方 Skill 時
```

比較頁：<http://127.0.0.1:60071/動態提案/index.html>（需先以 README 指令啟動本機服務）。
