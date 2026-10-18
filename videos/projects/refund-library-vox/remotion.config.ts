import {Config} from '@remotion/cli/config';

Config.setCodec('h264');
Config.setPixelFormat('yuv420p');
// 固定版 4.0.536 已移除 setImageFormat；本片工作區改用分開的設定，通用骨架不動。
Config.setStillImageFormat('png');
Config.setVideoImageFormat('png');
// 本機 runtime 設定（僅本片、本機）：複製來的 node_modules/.remotion 瀏覽器在此機無法載入 root，
// 改用同版 Remotion 新下載且已實測可渲染的 headless shell。不是 Skill 或工具的固定路徑。
Config.setBrowserExecutable('/private/tmp/.remotion/chrome-headless-shell/mac-arm64/chrome-headless-shell-mac-arm64/chrome-headless-shell');
