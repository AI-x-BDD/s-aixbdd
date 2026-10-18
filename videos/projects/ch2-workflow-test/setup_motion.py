"""用可執行的 Node 安裝鎖定的 Remotion 依賴，不改全域設定。"""
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[2]/'scripts'))
import video
import motion_runtime as runtime
executable=runtime.node()
npm=Path(executable).parent.parent/'lib/node_modules/npm/bin/npm-cli.js'
if not npm.exists():raise RuntimeError('選定的 Node 缺少 npm，請確認 Node 安裝')
video.run([executable,npm,'ci'],cwd=runtime.MOTION,env=runtime.environment(executable))
