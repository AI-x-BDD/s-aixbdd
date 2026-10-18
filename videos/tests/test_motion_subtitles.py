"""實際解碼字幕 fallback，防止透明圖被白底蓋住、字幕跑出非正方形畫布。"""
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import motion_project


@unittest.skipUnless(shutil.which("sips") and shutil.which("ffmpeg"), "macOS sips/FFmpeg required")
class SubtitleRasterTests(unittest.TestCase):
    def test_background_survives_and_caption_is_visible(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            source, movie = root / "source.mp4", root / "burned.mp4"
            subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "lavfi", "-i",
                            "color=c=0x2060a0:s=640x360:r=10", "-t", "1", "-c:v", "libx264", str(source)], check=True)
            project = {"width": 640, "height": 360, "fps": 10, "workspace": root,
                       "config": {"subtitle_area": {"left": 30, "top": 290, "right": 610, "bottom": 350}}}
            motion_project._burn_subtitles_with_images(
                project, source, movie, [{"start": 0, "end": 1, "text": "字幕確實可見"}], 1)
            pixels = subprocess.check_output(["ffmpeg", "-v", "error", "-ss", "0.4", "-i", str(movie),
                                               "-frames:v", "1", "-f", "rawvideo", "-pix_fmt", "rgb24", "-"])
            # 畫面上方保留原藍底；白底或不透明黑底都必須失敗。
            original = subprocess.check_output(["ffmpeg", "-v", "error", "-ss", "0.4", "-i", str(source),
                                                 "-frames:v", "1", "-f", "rawvideo", "-pix_fmt", "rgb24", "-"])
            self.assertLess(max(abs(a - b) for a, b in zip(pixels[:640 * 250 * 3], original[:640 * 250 * 3])), 10)
            # 亮字必須位於預留字幕帶，不能只有一張透明圖。
            band = pixels[640 * 290 * 3:640 * 350 * 3]
            self.assertGreater(sum(channel > 200 for channel in band), 300)


if __name__ == "__main__":
    unittest.main()
