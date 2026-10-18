import {Config} from '@remotion/cli/config';

Config.setCodec('h264');
Config.setPixelFormat('yuv420p');
Config.setStillImageFormat('png');
Config.setVideoImageFormat('png');

// 本次本機 runtime；既有 headless shell 載入逾時，改用已實測成功的瀏覽器。跨機器需重測路徑。
Config.setBrowserExecutable('/private/tmp/.remotion/chrome-headless-shell/mac-arm64/chrome-headless-shell-mac-arm64/chrome-headless-shell');
