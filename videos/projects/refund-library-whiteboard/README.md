# 退款流程白板候選

以 video-production Skill 重跑。固定風格 ID：y3_whiteboard；旁白與內容沿用原退款三段，供比較視覺方向，未標記使用者確認。

設定：project.toml。原始旁白、語音、對齊、字幕檢查所需契約：materials/。實際繪圖使用 state.json 每幀位置及幾何資料，與獨立 focus.json 逐項比對。src/ 保存本次繪圖程式副本；原始建置工作區與來源 SHA 在 records 中。

重建：由專案根目錄執行 motion_project.py 的 init；將 src/ 複製到本片 workspace/motion/src/，remotion.config.ts 使用 setStillImageFormat 和 setVideoImageFormat；安裝鎖定 package-lock.json 的依賴，再 prepare、render、review、deliver。完整命令與輸出見 videos/README.md。

本機已完成 Python、FFmpeg、Node、Remotion 實際編碼；旁白沿用已生成的預覽配音，未新增配音服務。
