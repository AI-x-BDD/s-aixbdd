"""獨立通用影片工具的 synthetic unit fixture。

它只驗證實際編碼、字幕封裝、證據閘門與六類故障；WAV 是靜音、對齊是
均分的人造資料、assessment 是 gate payload，不能當成模型對齊、有聲代表片
或實際視覺／聽看評審證據。
"""

from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
import wave


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "motion_project.py"


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def run_cli(config: Path, command: str, *extra: str, expect: int = 0) -> subprocess.CompletedProcess[str]:
    result = subprocess.run(
        [sys.executable, str(SCRIPT), "--config", str(config), command, *extra],
        text=True,
        capture_output=True,
    )
    if result.returncode != expect:
        raise AssertionError(f"{command} 預期 {expect}，實際 {result.returncode}\nstdout={result.stdout}\nstderr={result.stderr}")
    return result


def make_wav(path: Path, seconds: float = 2.0) -> None:
    # 低成本確實存在的旁白音訊；fixture 不把無聲檔當成「有聲影片」。
    frames = int(16_000 * seconds)
    with wave.open(str(path), "wb") as output:
        output.setnchannels(1)
        output.setsampwidth(2)
        output.setframerate(16_000)
        output.writeframes(b"\x00\x00" * frames)


def make_alignment(content: dict, audio: Path) -> dict:
    scenes = []
    bounds = [(0.0, 0.8), (1.0, 1.8)]
    for scene, (start, end) in zip(content["scenes"], bounds):
        step = (end - start) / len(scene["text"])
        characters = [{"offset": index, "start": round(start + index * step, 3),
                       "end": round(start + (index + 1) * step, 3)}
                      for index in range(len(scene["text"]))]
        scenes.append({"frame": scene["id"], "text": scene["text"], "characters": characters,
                       "speech_start": start, "speech_end": end})
    return {"method": "fixture-precomputed-model-output", "audio_sha256": digest(audio),
            "content_sha256": digest(Path(content["_path"])), "scenes": scenes}


def make_state() -> dict:
    frames = []
    for frame in range(20):
        second = frame / 10
        if second < 1:
            item = {"id": "request", "text": "request", "x": 40, "y": 50, "w": 240, "h": 80, "projected_bounds": {"x": 40, "y": 50, "w": 240, "h": 80}, "opacity": 1}
            active = ["request"]
            scene = "request"
        else:
            item = {"id": "refund", "text": "refund", "x": 40, "y": 50, "w": 240, "h": 80, "projected_bounds": {"x": 40, "y": 50, "w": 240, "h": 80}, "opacity": 1}
            active = ["refund"]
            scene = "refund"
        frames.append({"frame": frame, "t": second, "scene": scene, "active": active, "visible": [item]})
    return {"fps": 10, "frames": frames}


class MotionProjectFixtureTest(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory(prefix="motion-project-")
        self.root = Path(self.temp.name)
        materials = self.root / "materials"
        materials.mkdir()
        content = {"title": "Refund", "scenes": [
            {"id": "request", "text": "Submit request"},
            {"id": "refund", "text": "Refund issued"},
        ]}
        content["_path"] = str(materials / "content.json")
        (materials / "content.json").write_text(json.dumps(content), encoding="utf-8")
        content.pop("_path")
        audio = materials / "voice.wav"
        make_wav(audio)
        content_for_hash = materials / "content.json"
        alignment = make_alignment({**content, "_path": str(content_for_hash)}, audio)
        (materials / "alignment.json").write_text(json.dumps(alignment), encoding="utf-8")
        focus = {"segments": [
            {"id": "request-focus", "start": 0, "end": 1, "required_active": ["request"], "targets": [{"id": "request", "name": "request"}]},
            {"id": "refund-focus", "start": 1, "end": 2, "required_active": ["refund"], "targets": [{"id": "refund", "name": "refund"}]},
        ]}
        (materials / "focus.json").write_text(json.dumps(focus), encoding="utf-8")
        (materials / "labels.json").write_text(json.dumps({"request": "request", "refund": "refund"}), encoding="utf-8")
        (materials / "state.json").write_text(json.dumps(make_state()), encoding="utf-8")
        self.config = self.root / "project.toml"
        self.config.write_text(
            """id = \"refund-fixture\"\nstyle_library_required = false\nlegacy_style_reason = \"isolated synthetic gate fixture; no style selection\"\nsource_root = \".\"\nmaterials = \"materials\"\ncontent = \"content.json\"\naudio = \"voice.wav\"\nalignment = \"alignment.json\"\nfocus_contract = \"focus.json\"\nlabels = \"labels.json\"\nstate = \"state.json\"\nworkspace = \"build/refund-fixture/workspace\"\noutput = \"build/refund-fixture/output\"\nrecords = \"build/refund-fixture/records\"\nwidth = 320\nheight = 180\nfps = 10\ncomposition = \"Main\"\nrenderer = \"command\"\nrender_command_sources = [\"project.toml\"]\nnpm_install = false\nburn_subtitles = true\nrequire_audio = true\nopacity_threshold = 0.5\ncontent_safe_area = {left = 0, top = 0, right = 320, bottom = 150}\nsubtitle_area = {left = 0, top = 150, right = 320, bottom = 180}\nrender_command = [\"ffmpeg\", \"-y\", \"-hide_banner\", \"-loglevel\", \"error\", \"-f\", \"lavfi\", \"-i\", \"color=c=black:s={width}x{height}:r={fps}\", \"-t\", \"{duration}\", \"-c:v\", \"libx264\", \"-pix_fmt\", \"yuv420p\", \"{output}\"]\n""",
            encoding="utf-8",
        )

    def tearDown(self) -> None:
        self.temp.cleanup()

    def prepare_render(self) -> Path:
        run_cli(self.config, "init")
        run_cli(self.config, "prepare")
        run_cli(self.config, "render")
        return self.root / "build/refund-fixture/workspace"

    def assessment(self, workspace: Path) -> Path:
        movie = workspace / "out/video.mp4"
        fingerprints = workspace / "source-fingerprints.json"
        review = json.loads((workspace / "../records/review.json").read_text(encoding="utf-8"))
        subtitle_evidence = json.loads((workspace / "../records/subtitle-evidence.json").read_text(encoding="utf-8"))
        path = self.root / "assessment.json"
        path.write_text(json.dumps({
            "movie_sha256": digest(movie),
            "source_fingerprints_sha256": digest(fingerprints),
            "captured_frames": [
                {"time": frame["time"], "sha256": frame["sha256"], "status": "pass",
                 "observation": "synthetic gate payload; no visual inspection"}
                for frame in review["captured_frames"]
            ],
            "subtitle_frames": [
                {"time": frame["time"], "text": frame["text"], "sha256": frame["sha256"],
                 "status": "pass", "observation": "synthetic gate payload; no visual inspection"}
                for frame in subtitle_evidence["frames"]
            ],
            "static_visual": {"status": "pass", "method": "synthetic gate payload; no visual inspection"},
            "subtitle_visibility": {"status": "pass", "method": "synthetic gate payload; no visual inspection"},
            "audio_analysis": {"status": "pass", "method": "synthetic gate payload; no direct listening"},
            "continuous_av": {"status": "unverified", "reason": "fixture has no direct AV listener"},
        }), encoding="utf-8")
        return path

    def test_actual_encoding_burned_subtitles_review_delivery(self) -> None:
        workspace = self.prepare_render()
        # Without an assessment, review must stop instead of treating technical
        # green as a complete visual review.
        run_cli(self.config, "review", expect=2)
        assessment = self.assessment(workspace)
        run_cli(self.config, "review", "--assessment", str(assessment))
        run_cli(self.config, "deliver", "--user-acceptance", "accepted")
        output = self.root / "build/refund-fixture/output"
        self.assertTrue((output / "video.mp4").is_file())
        self.assertTrue((output / "captions.srt").is_file())
        self.assertTrue((output / "captions.vtt").is_file())
        html = (output / "delivery.html").read_text(encoding="utf-8")
        self.assertIn("<video", html)
        self.assertIn("download", html)
        self.assertIn("video.mp4", html)

    def test_assessment_must_bind_every_extracted_frame(self) -> None:
        workspace = self.prepare_render()
        run_cli(self.config, "review", expect=2)
        assessment = self.assessment(workspace)
        original = json.loads(assessment.read_text(encoding="utf-8"))
        for mutation in ("missing", "fake-hash", "empty-observation", "missing-subtitle"):
            value = copy.deepcopy(original)
            if mutation == "missing":
                value["captured_frames"] = value["captured_frames"][:-1]
            elif mutation == "fake-hash":
                value["captured_frames"][0]["sha256"] = "0" * 64
            elif mutation == "empty-observation":
                value["captured_frames"][0]["observation"] = ""
            else:
                value["subtitle_frames"] = value["subtitle_frames"][:-1]
            assessment.write_text(json.dumps(value), encoding="utf-8")
            run_cli(self.config, "review", "--assessment", str(assessment), expect=2)
        assessment.write_text(json.dumps(original), encoding="utf-8")

    def test_review_rejects_mp4_changed_after_render(self) -> None:
        workspace = self.prepare_render()
        render_manifest = workspace / "render.json"
        value = json.loads(render_manifest.read_text(encoding="utf-8"))
        value["movie_sha256"] = "0" * 64
        render_manifest.write_text(json.dumps(value), encoding="utf-8")
        run_cli(self.config, "review", expect=2)

    def test_six_faults_are_blocked(self) -> None:
        workspace = self.prepare_render()
        state_path = workspace / "motion/public/state.json"
        original = json.loads(state_path.read_text(encoding="utf-8"))
        for name in ("missing-enumeration", "premature-focus", "wrong-target", "missing-name", "cropped", "stale-evidence"):
            state = copy.deepcopy(original)
            if name == "missing-enumeration":
                state["frames"][3]["visible"] = []
            elif name == "premature-focus":
                state["frames"][5]["visible"] = []
                state["frames"][5]["active"] = []
            elif name == "wrong-target":
                state["frames"][3]["active"] = ["refund"]
            elif name == "missing-name":
                state["frames"][3]["visible"][0]["text"] = ""
            elif name == "cropped":
                state["frames"][3]["visible"][0]["x"] = -20
            elif name == "stale-evidence":
                content = self.root / "materials/content.json"
                content.write_text(content.read_text(encoding="utf-8") + " ", encoding="utf-8")
            if name != "stale-evidence":
                state_path.write_text(json.dumps(state), encoding="utf-8")
            run_cli(self.config, "review", expect=2)
            if name != "stale-evidence":
                state_path.write_text(json.dumps(original), encoding="utf-8")
            else:
                content = self.root / "materials/content.json"
                content.write_text(content.read_text(encoding="utf-8").rstrip(), encoding="utf-8")

    def test_missing_model_stops_when_alignment_is_needed(self) -> None:
        self.config.write_text(self.config.read_text(encoding="utf-8").replace('alignment = "alignment.json"\n', '').replace('model_path =', 'model_path ='), encoding="utf-8")
        # Keep a malformed explicit model path so the workflow cannot silently
        # estimate timing or reuse a CH2 cache.
        with self.config.open("a", encoding="utf-8") as output:
            output.write('model_path = "missing-model"\n')
        run_cli(self.config, "init")
        run_cli(self.config, "prepare", expect=2)

    def test_command_renderer_requires_source_provenance(self) -> None:
        self.config.write_text(self.config.read_text(encoding="utf-8").replace(
            'render_command_sources = ["project.toml"]\n', ''), encoding="utf-8")
        run_cli(self.config, "init")
        run_cli(self.config, "prepare", expect=2)

    def test_disabling_burned_subtitles_requires_explicit_decision(self) -> None:
        self.config.write_text(self.config.read_text(encoding="utf-8").replace(
            "burn_subtitles = true", "burn_subtitles = false"), encoding="utf-8")
        run_cli(self.config, "init")
        run_cli(self.config, "prepare", expect=2)
        with self.config.open("a", encoding="utf-8") as output:
            output.write('subtitle_override_reason = "此片由外部播放器提供字幕，保留 SRT/VTT"\n')
        run_cli(self.config, "prepare")


if __name__ == "__main__":
    unittest.main()
