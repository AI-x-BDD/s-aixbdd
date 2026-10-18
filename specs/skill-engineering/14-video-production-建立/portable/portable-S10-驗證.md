# Portable S10 驗證（v2）

- portable root：`/private/tmp/video-skill-s2-portable-plant-20261018/videos`
- profile：`projects/plant-watering/project.toml`
- `init`、`prepare`、`render`、`review`、`deliver`：均 pass。
- portable source fingerprint：`93f2bbe4125f7a3d1d8af7fcf82957dd4703f1cdcc302de0a5b8e18c110340a4`。
- portable 成片 SHA-256：`792751eb3cccb7939a4472793ded73d14944e7c4461578a6f6187d9aba05940d`；`輸出/影片.mp4` 同 SHA。
- required Skill 實體包含 `video-production`、`storyboard`、`presentation-design-editorial`、`motion-art-direction`；後三者均帶原文 `LICENSE`，`.agents` 與 `.claude` 逐檔固定版相同，來源與 hash 見 `.agents/skills/來源.json`、`required-skill-sources.json`。
- 已帶 renderer `LICENSE`、`package.json`／`package-lock.json`、template `LICENSE`／`package.json`／`package-lock.json`、Python `uv.lock`、model provenance JSON；`init` 實跑 `npm ci --ignore-scripts` pass。官方 Remotion Skill 原文未打包（上游未附授權）；帶 `scripts/install-official-remotion-skill.sh`、固定 revision `1441a11e95db35443bd76bb318386c0d3ca00053`、來源 JSON 與 291 檔 SHA-256 manifest，按需下載後驗 hash。
- portable 隔離測試：`subtitle_margin 18 → 19 → 18` 只改 portable；changed profile SHA `57bf6207d0ec989f6fe31b835e013b4a00eea2181670f38cfa3fe8555b491af0`，復原 SHA `3282f4a78df76db0c4684caea40b08d7842223983f3d3aaa453f073bdc19db75`，與 isolated profile `3282f4a78df76db0c4684caea40b08d7842223983f3d3aaa453f073bdc19db75` 相同；isolated 未寫入。
- 缺依賴測試：暫時移走 `renderer/node_modules`，render 以 exit `2` 明確報缺 Remotion；復原後 node_modules 在、影片 SHA 仍 `792751eb3cccb7939a4472793ded73d14944e7c4461578a6f6187d9aba05940d`。
- CH2 邊界：final portable 只有 `projects/plant-watering`；原本 portable 既有的 legacy `scripts/video.py`、`scripts/capability_probe.py`、重複測試檔已移出，詳見 `portable-package-cleanup.json`。本次未讀 specs 或舊 CH2 素材。
- 限制：shared model／host tools 是外部前置；encoded frame continuity 已查，user acceptance 仍 pending，未宣稱直接聽感聲畫同步。

完整機械資料見 `portable-s10-manifest.json`。
