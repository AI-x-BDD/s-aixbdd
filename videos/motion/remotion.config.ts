import {Config} from '@remotion/cli/config';

// 與 CH2 正式片一致：1600×900、25fps、H.264；PNG 擷取避免深色漸層產生 JPEG 色塊。
Config.setVideoImageFormat('png');
Config.setCodec('h264');
Config.setPixelFormat('yuv420p');
Config.setCrf(18);
