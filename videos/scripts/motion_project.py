"""Portable, profile-driven motion-video project workflow.

The command is intentionally a small project tool rather than a CH2 renderer.
Each film supplies its own profile, renderer entry point, state exporter output,
focus contract, audio and alignment.  The tool owns isolation, fingerprints,
subtitle muxing and evidence gates; it does not invent a film's scenes.

Examples::

    uv run --frozen python scripts/motion_project.py --config projects/demo.toml init
    uv run --frozen python scripts/motion_project.py --config projects/demo.toml prepare
    uv run --frozen python scripts/motion_project.py --config projects/demo.toml render
    uv run --frozen python scripts/motion_project.py --config projects/demo.toml review
    uv run --frozen python scripts/motion_project.py --config projects/demo.toml deliver
"""

from __future__ import annotations

import argparse
import contextlib
import fcntl
import hashlib
import html
import json
import math
import os
from pathlib import Path
import re
import shutil
import shlex
import subprocess
import sys
import tempfile
import time
from xml.sax.saxutils import escape as xml_escape
try:  # Python 3.11+ is the supported runtime; tomli keeps 3.10 tools readable.
    import tomllib
except ModuleNotFoundError:  # pragma: no cover - only used by older local launchers
    import tomli as tomllib  # type: ignore
from typing import Any, Iterable

import motion_checks as checks


TOOL_VERSION = "motion-project/0.1"
TEMPLATE = Path(__file__).resolve().parents[1] / "templates" / "motion-project"
TOOL_ROOT = Path(__file__).resolve().parents[1]


# A named exception is unnecessary here: the CLI catches the standard error
# directly, and keeping the workflow as functions over dictionaries makes the
# profile data easy for another agent to inspect and extend.
ProjectError = RuntimeError


def _run(command: list[str], *, cwd: Path | None = None, capture: bool = False) -> subprocess.CompletedProcess[str]:
    try:
        return subprocess.run(
            [str(value) for value in command],
            cwd=str(cwd) if cwd else None,
            check=True,
            text=True,
            capture_output=capture,
        )
    except FileNotFoundError as exc:
        raise ProjectError(f"缺少可執行工具：{command[0]}") from exc
    except subprocess.CalledProcessError as exc:
        detail = (exc.stderr or exc.stdout or "").strip()
        raise ProjectError(f"命令失敗（{shlex.join(command)}）：{detail[-1200:]}") from exc


def _command_output(command: list[str]) -> str:
    try:
        return subprocess.check_output(command, text=True, stderr=subprocess.STDOUT).strip()
    except (OSError, subprocess.CalledProcessError):
        return "未取得"


def _sha256(path: Path) -> str:
    return checks.sha256(path)


def _tree_sha(path: Path) -> str:
    if path.is_file():
        return _sha256(path)
    if not path.is_dir():
        raise ProjectError(f"找不到模型或來源：{path}")
    digest = hashlib.sha256()
    for child in sorted((p for p in path.rglob("*") if p.is_file()), key=lambda p: p.as_posix()):
        digest.update(child.relative_to(path).as_posix().encode())
        digest.update(_sha256(child).encode())
    return digest.hexdigest()


def _json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def _read_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ProjectError(f"無法讀取 JSON：{path}；{exc}") from exc


def _stamp(seconds: float, comma: bool = False) -> str:
    millis = round(seconds * 1000)
    hours, millis = divmod(millis, 3_600_000)
    minutes, millis = divmod(millis, 60_000)
    secs, millis = divmod(millis, 1000)
    return f"{hours:02}:{minutes:02}:{secs:02}{',' if comma else '.'}{millis:03}"


def _find_tool_root(config_path: Path) -> Path:
    for candidate in [config_path.parent, *config_path.parents]:
        if (candidate / "scripts" / "motion_project.py").is_file():
            return candidate
    return config_path.parent


def load_project(config_path: Path, source_root: Path | None = None, *, allow_missing: bool = False,
                 init_id: str | None = None) -> dict[str, Any]:
    """Resolve a profile into plain data; no chapter-specific defaults."""
    config_path = config_path.expanduser().resolve()
    if not config_path.is_file():
        if not allow_missing:
            raise ProjectError(f"找不到 profile：{config_path}")
        project_id = init_id or config_path.stem
        config_path.parent.mkdir(parents=True, exist_ok=True)
        config_path.write_text(
            f"id = {json.dumps(project_id, ensure_ascii=False)}\n"
            "source_root = " + json.dumps(os.path.relpath(config_path.parent, _find_tool_root(config_path))) + "\nmaterials = \"materials\"\n"
            "style_library_required = true\nstyle_library = \"style-library\"\nstyle_selection = \"style-selection.json\"\n"
            "content = \"content.json\"\naudio = \"voice.wav\"\n"
            "focus_contract = \"focus.json\"\nstate = \"state.json\"\n"
            "workspace = \"build/" + project_id + "/workspace\"\n"
            "output = \"build/" + project_id + "/output\"\n"
            "records = \"build/" + project_id + "/records\"\n"
            "width = 1280\nheight = 720\nfps = 30\ncomposition = \"Main\"\n"
            "entry = \"src/index.ts\"\n"
            "renderer = \"remotion\"\ncontent_safe_area = {left = 0, top = 0, right = 1280, bottom = 620}\n"
            "subtitle_area = {left = 0, top = 620, right = 1280, bottom = 720}\n"
            "opacity_threshold = 0.5\n",
            encoding="utf-8",
        )
    config = tomllib.loads(config_path.read_text(encoding="utf-8"))
    if isinstance(config.get("project"), dict):
        merged = dict(config)
        merged.update(config["project"])
        config = merged
    tool_root = _find_tool_root(config_path)
    configured_root = config.get("source_root")
    if source_root is not None:
        resolved_source_root = source_root.expanduser().resolve()
    elif configured_root:
        base = tool_root if not Path(str(configured_root)).is_absolute() else Path("/")
        resolved_source_root = (base / str(configured_root)).resolve()
    else:
        resolved_source_root = config_path.parent

    def source_path(value: Any) -> Path:
        path = Path(os.fspath(value)).expanduser()
        return path.resolve() if path.is_absolute() else (resolved_source_root / path).resolve()

    def derived_path(value: Any) -> Path:
        path = Path(os.fspath(value)).expanduser()
        if path.is_absolute():
            return path.resolve()
        return ((tool_root if path.parts and path.parts[0] == "build" else resolved_source_root) / path).resolve()

    project_id = str(config.get("id", config.get("name", config_path.stem)))
    width = int(config.get("width", config.get("video_width", 1280)))
    height = int(config.get("height", config.get("video_height", 720)))
    fps = float(config.get("fps", 30))
    if width <= 0 or height <= 0 or fps <= 0:
        raise ProjectError("profile 的 width、height、fps 必須是正數")
    return {
        "config_path": config_path,
        "config": config,
        "tool_root": tool_root,
        "source_root": resolved_source_root,
        "materials": source_path(config.get("materials", ".")),
        "project_id": project_id,
        "workspace": derived_path(config.get("workspace", f"build/{project_id}/workspace")),
        "output": derived_path(config.get("output", f"build/{project_id}/output")),
        "records": derived_path(config.get("records", f"build/{project_id}/records")),
        "width": width,
        "height": height,
        "fps": fps,
        "composition": str(config.get("composition", "Main")),
        "entry": str(config.get("entry", "src/index.ts")),
    }


def source(project: dict[str, Any], key: str, *, materials: bool = True, required: bool = True) -> Path | None:
    value = project["config"].get(key)
    if value in (None, ""):
        if required:
            raise ProjectError(f"profile 缺少 {key}")
        return None
    path = ((project["materials"] / str(value)).resolve() if materials and not Path(str(value)).is_absolute()
            else Path(os.fspath(value)).expanduser().resolve())
    if required and not path.is_file():
        raise ProjectError(f"profile 的 {key} 不存在：{path}")
    return path


def runtime_paths(project: dict[str, Any]) -> dict[str, Path]:
    workspace, public, build_out, records = project["workspace"], renderer_dir(project) / "public", project["workspace"] / "out", project["records"]
    return {"timeline": public / "timeline.json", "captions_srt": public / "captions.srt",
            "captions_vtt": public / "captions.vtt", "canonical_audio": public / "canonical-audio.m4a",
            "state": public / "state.json", "focus_contract": public / "focus-contract.json", "labels": public / "labels.json",
            "render_props": public / "render-props.json",
            "fingerprints": workspace / "source-fingerprints.json", "prepare": workspace / "prepare.json",
            "render": workspace / "render.json", "movie": build_out / "video.mp4",
            "review": records / "review.json", "subtitle_evidence": records / "subtitle-evidence.json"}


def style_selection_path(project: dict[str, Any]) -> Path:
    value = Path(str(project["config"]["style_selection"]))
    return value if value.is_absolute() else project["source_root"] / value


def check_style_library(project: dict[str, Any]) -> None:
    """New profiles require a pinned library choice; historical profiles remain rebuildable."""
    config = project["config"]
    if "style_library_required" not in config:
        raise ProjectError("缺少 style_library_required；新片必須為 true，歷史重建須明列 false 與 legacy_style_reason")
    if config["style_library_required"] is not True:
        if config["style_library_required"] is not False or not str(config.get("legacy_style_reason", "")).strip():
            raise ProjectError("略過風格庫只限明列 legacy_style_reason 的歷史重建或隔離測試")
        return
    if not config.get("style_library") or not config.get("style_selection"):
        raise ProjectError("新影片必須指定 style_library 與 style_selection；不可用臨時風格取代固定庫")
    library = Path(str(config["style_library"]))
    if not library.is_absolute():
        library = TOOL_ROOT / library
    if library.resolve() != (TOOL_ROOT / "style-library").resolve():
        raise ProjectError("新片只可使用工具包內的固定 style-library，不可替換為臨時風格庫")
    selection = style_selection_path(project)
    _run([sys.executable, str(Path(__file__).with_name("style_library.py")), "check",
          "--library", str(library), "--selection", str(selection)])


def check_required(project: dict[str, Any]) -> None:
    check_style_library(project)
    for key in ("content", "focus_contract"):
        source(project, key)
    audio = source(project, "audio", required=project["config"].get("audio") not in (None, ""))
    if project["config"].get("require_audio", True) and audio is None:
        raise ProjectError("profile 必須提供 audio；若只是無聲草稿請明確設定 require_audio=false")
    state_configured = project["config"].get("state") not in (None, "")
    if state_configured:
        source(project, "state")
    if not state_configured and project["config"].get("state_exporter") is None:
        raise ProjectError("profile 必須提供 state 或 state_exporter；焦點不能由契約自動生成")
    if not state_configured and project["config"].get("state_exporter") and not project["config"].get("state_exporter_sources"):
        raise ProjectError("使用 state_exporter 時必須明列 state_exporter_sources，讓來源指紋可追溯")
    if project["config"].get("labels") in (None, ""):
        raise ProjectError("profile 必須提供 labels 名稱表；不能只記錄 labels 雜湊")
    renderer = str(project["config"].get("renderer", "remotion"))
    if renderer == "remotion" and not project["entry"].strip():
        raise ProjectError("renderer=remotion 必須明列 entry")
    if renderer == "remotion":
        entry_path = Path(project["entry"])
        entry_path = entry_path if entry_path.is_absolute() else renderer_dir(project) / entry_path
        if not entry_path.is_file():
            raise ProjectError(f"Remotion entry 不存在：{entry_path}；請先 init 或提供本片 renderer")
    if renderer in {"command", "custom"}:
        render_sources = project["config"].get("render_command_sources")
        if (render_sources in (None, "") or
                (isinstance(render_sources, (list, tuple)) and not render_sources)):
            raise ProjectError("renderer=command/custom 必須明列非空 render_command_sources；內建工具或外部腳本都要可追溯")
    for key in ("alignment", "labels", "subtitle_source", "subtitle_settings", "audio_recipe"):
        if project["config"].get(key) not in (None, ""):
            source(project, key)
    # These entries describe executable files used by a custom renderer or a
    # state exporter.  They are resolved from source_root rather than the
    # materials directory and are part of the source manifest.  A configured
    # but missing entry must stop the build instead of silently producing an
    # incomplete provenance record.
    for key in ("visuals", "slides", "render_command_sources", "state_exporter_sources", "model_provenance"):
        value = project["config"].get(key)
        if value in (None, ""):
            continue
        for path in _configured_paths(project, key):
            if not path.exists() or (path.is_file() and path.stat().st_size == 0):
                raise ProjectError(f"profile 的 {key} 不存在或為空：{path}")
    for key in ("content_safe_area", "subtitle_area"):
        value = project["config"].get(key)
        if not isinstance(value, dict):
            raise ProjectError(f"profile 必須明列 {key}，不能用畫布全區回退")
    try:
        opacity = float(project["config"].get("opacity_threshold"))
    except (TypeError, ValueError):
        raise ProjectError("profile 必須明列 opacity_threshold")
    if not 0 < opacity <= 1:
        raise ProjectError("opacity_threshold 必須介於 0 與 1 之間")
    if not bool(project["config"].get("burn_subtitles", True)):
        reason = str(project["config"].get("subtitle_override_reason", "")).strip()
        record = str(project["config"].get("subtitle_decision_record", "")).strip()
        if not reason and not record:
            raise ProjectError("burn_subtitles=false 必須明列 subtitle_override_reason 或 subtitle_decision_record")
    if project["fps"] < 1 or project["fps"] > 240:
        raise ProjectError("fps 超出可支援範圍 1–240")


def _tool_versions() -> dict[str, str]:
    return {
        "tool": TOOL_VERSION,
        "python": _command_output([sys.executable, "--version"]),
        "ffmpeg": _command_output(["ffmpeg", "-version"]).splitlines()[0] if shutil.which("ffmpeg") else "缺少",
        "ffprobe": _command_output(["ffprobe", "-version"]).splitlines()[0] if shutil.which("ffprobe") else "缺少",
        "node": _command_output(["node", "--version"]) if shutil.which("node") else "缺少",
        "npm": _command_output(["npm", "--version"]) if shutil.which("npm") else "缺少",
        "sips": _command_output(["sips", "--version"]) if shutil.which("sips") else "缺少（libass 可替代）",
    }


def _copy_template(destination: Path) -> None:
    if not TEMPLATE.is_dir():
        raise ProjectError(f"缺少通用 Remotion 骨架：{TEMPLATE}")
    destination.mkdir(parents=True, exist_ok=True)
    for source in TEMPLATE.rglob("*"):
        relative = source.relative_to(TEMPLATE)
        target = destination / relative
        if source.is_dir():
            target.mkdir(exist_ok=True)
        elif not target.exists():
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, target)


def renderer_dir(project: dict[str, Any]) -> Path:
    value = project["config"].get("renderer_dir")
    if not value:
        return project["workspace"] / "motion"
    path = Path(os.fspath(value)).expanduser()
    return path.resolve() if path.is_absolute() else (project["source_root"] / path).resolve()


def _configured_paths(project: dict[str, Any], key: str) -> list[Path]:
    """Resolve a repeatable profile source without guessing its location."""
    value = project["config"].get(key)
    if value in (None, ""):
        return []
    values = value if isinstance(value, list) else [value]
    base = project["source_root"] if key in {"visuals", "slides", "render_command_sources", "state_exporter_sources", "model_provenance"} else project["materials"]
    paths = []
    for entry in values:
        path = Path(os.fspath(entry)).expanduser()
        paths.append(path.resolve() if path.is_absolute() else (base / path).resolve())
    return paths


def _source_files(project: dict[str, Any]) -> list[tuple[str, Path]]:
    content_path = source(project, "content")
    focus_path = source(project, "focus_contract")
    files: list[tuple[str, Path]] = [("profile", project["config_path"]), ("content", content_path), ("focus_contract", focus_path)]
    if project["config"].get("style_library_required", False):
        library = Path(str(project["config"]["style_library"]))
        if not library.is_absolute():
            library = TOOL_ROOT / library
        files.extend([("style_selection", style_selection_path(project)),
                      ("style_catalog", library / "catalog.json"),
                      ("style_lock", library / "upstream-lock.json"),
                      ("tool:style_library", Path(__file__).with_name("style_library.py"))])
    for role, path in (("audio", source(project, "audio", required=False)),
                       ("alignment", source(project, "alignment", required=False)),
                       ("state", source(project, "state", required=False))):
        if path is not None:
            files.append((role, path))
    for key in ("audio_recipe", "visuals", "slides", "labels", "subtitle_source", "subtitle_settings",
                "render_command_sources", "state_exporter_sources", "model_provenance"):
        for path in _configured_paths(project, key):
            if path.is_file():
                files.append((key, path))
            elif path.is_dir():
                files.extend((f"{key}:{item.relative_to(path).as_posix()}", item) for item in sorted(path.rglob("*")) if item.is_file())
    source_dir = renderer_dir(project)
    if source_dir.exists():
        # Never fingerprint node_modules or generated public/out files.  The
        # package lock and author-owned source are enough to make a build
        # reproducible without hashing a dependency tree.
        excluded = {"node_modules", "public", "out", ".cache", "build"}
        files.extend((f"renderer:{item.relative_to(source_dir).as_posix()}", item)
                     for item in sorted(source_dir.rglob("*"))
                     if item.is_file() and not excluded.intersection(item.relative_to(source_dir).parts))
    # The executable contract itself is part of the evidence.  These are
    # project-tool sources, not a dependency-tree hash and therefore remain
    # cheap and portable to compare.
    for role, path in (("tool:motion_project", Path(__file__).resolve()),
                       ("tool:motion_checks", Path(__file__).with_name("motion_checks.py")),
                       ("tool:align", Path(__file__).with_name("align.py"))):
        if path.is_file():
            files.append((role, path))
    return files


def _fingerprints(project: dict[str, Any]) -> dict[str, Any]:
    files = []
    for role, path in _source_files(project):
        try:
            relative = path.relative_to(project["source_root"]).as_posix()
        except ValueError:
            relative = path.name
        files.append({"role": role, "path": str(path), "relative": relative,
                      "sha256": _sha256(path), "bytes": path.stat().st_size})
    return {"tool": TOOL_VERSION, "project_id": project["project_id"],
            "source_root": str(project["source_root"]), "files": files}


def _runtime_hashes(project: dict[str, Any]) -> dict[str, str]:
    paths = runtime_paths(project)
    values = {name: path for name, path in {
        "timeline": paths["timeline"], "state": paths["state"], "focus_contract": paths["focus_contract"],
        "captions_srt": paths["captions_srt"], "captions_vtt": paths["captions_vtt"],
        "canonical_audio": paths["canonical_audio"],
        "render_props": runtime_paths(project)["render_props"],
    }.items()}
    generated = project["workspace"] / "alignment.generated.json"
    if generated.is_file():
        values["generated_alignment"] = generated
    labels = paths["labels"]
    if labels.is_file():
        values["labels"] = labels
    missing = [f"{name}:{path}" for name, path in values.items() if not path.is_file()]
    if missing:
        raise ProjectError("runtime 來源缺失，停止繼續：" + ", ".join(missing))
    return {name: _sha256(path) for name, path in values.items()}


def _labels(project: dict[str, Any]) -> dict[str, str]:
    path = source(project, "labels", required=False)
    if path is None:
        return {}
    value = _read_json(path)
    raw = value.get("labels", value) if isinstance(value, dict) else value
    if isinstance(raw, dict):
        return {str(key): str(item) for key, item in raw.items()}
    if isinstance(raw, list):
        return {str(item["id"]): str(item.get("name", item.get("label", "")))
                for item in raw if isinstance(item, dict) and item.get("id")}
    raise ProjectError("labels 必須是 id→name 物件或 labels 陣列")


def _verify_fingerprints(project: dict[str, Any]) -> list[dict[str, Any]]:
    return checks.check_fingerprints(runtime_paths(project)["fingerprints"])


def _content(project: dict[str, Any]) -> dict[str, Any]:
    value = _read_json(source(project, "content"))
    if not isinstance(value, dict) or not isinstance(value.get("scenes"), list) or not value["scenes"]:
        raise ProjectError("content 必須包含非空 scenes 陣列")
    for index, scene in enumerate(value["scenes"]):
        if not isinstance(scene, dict) or not str(scene.get("text", "")).strip():
            raise ProjectError(f"content scenes[{index}] 缺少旁白 text")
    return value


def _model_fingerprint(project: dict[str, Any], model: Path) -> dict[str, Any]:
    revision = None
    config = model / "config.json" if model.is_dir() else None
    if config and config.is_file():
        try:
            raw = _read_json(config)
            revision = raw.get("_commit_hash", raw.get("revision"))
        except ProjectError:
            pass
    provenance_path = project["config"].get("model_provenance")
    provenance: dict[str, Any] = {}
    if provenance_path:
        candidate = Path(os.fspath(provenance_path)).expanduser()
        if not candidate.is_absolute():
            candidate = (project["source_root"] / candidate).resolve()
        if not candidate.is_file():
            raise ProjectError(f"model_provenance 不存在：{candidate}")
        value = _read_json(candidate)
        if isinstance(value, dict):
            provenance = value
    return {
        "path": str(model),
        "source": project["config"].get("model_source", provenance.get("source")),
        "revision": project["config"].get("model_revision", provenance.get("revision", revision or model.name)),
        "sha256": _tree_sha(model),
        "provenance": provenance,
    }


def _new_alignment(project: dict[str, Any], audio: Path, content: dict[str, Any]) -> dict[str, Any]:
    model_value = project["config"].get("model_path") or os.environ.get("VIDEO_ALIGNMENT_MODEL")
    if not model_value:
        raise ProjectError("缺少 model_path；沒有模型時停止對齊，不使用估計時間")
    model = Path(str(model_value)).expanduser()
    if not model.is_absolute():
        model = (project["source_root"] / model).resolve()
    if not model.exists():
        raise ProjectError(f"指定的 model_path 不存在：{model}")
    scripts = str(TOOL_ROOT / "scripts")
    if scripts not in sys.path:
        sys.path.insert(0, scripts)
    try:
        import mlx_whisper  # type: ignore
        import align as align_module  # type: ignore
    except ImportError as exc:
        raise ProjectError("缺少 mlx-whisper 或 align.py 依賴；無法執行實際模型對齊，請安裝 videos 的 alignment extra") from exc
    raw = mlx_whisper.transcribe(
        str(audio), path_or_hf_repo=str(model), language=str(project["config"].get("language", "zh")),
        word_timestamps=True, verbose=None, condition_on_previous_text=False,
        temperature=0.0,
    )
    # align.py's public function uses the generic ``frame`` field as its
    # stable scene identifier.  New projects may call it ``id``; normalize a
    # copy so the source content bytes and wording remain untouched.
    alignment_content = {**content, "scenes": [
        {**scene, "frame": scene.get("frame", scene.get("id", str(index)))}
        for index, scene in enumerate(content["scenes"])
    ]}
    result = align_module.align(alignment_content, raw)
    result.update(audio_sha256=_sha256(audio), content_sha256=_sha256(source(project, "content")),
                  model=_model_fingerprint(project, model), source="mlx_whisper + videos/scripts/align.py")
    return result


def _validate_alignment(project: dict[str, Any], alignment: dict[str, Any], audio: Path, content: dict[str, Any]) -> None:
    if not alignment.get("audio_sha256") or alignment["audio_sha256"] != _sha256(audio):
        raise ProjectError("對齊資料的 audio_sha256 過期，請重新對齊")
    if not alignment.get("content_sha256") or alignment["content_sha256"] != _sha256(source(project, "content")):
        raise ProjectError("對齊資料的 content_sha256 過期，請重新對齊")
    rows = alignment.get("scenes")
    if not isinstance(rows, list) or len(rows) != len(content["scenes"]):
        raise ProjectError("對齊資料的 scenes 與 content 數量不同")
    for expected, actual in zip(content["scenes"], rows):
        if expected.get("text") != actual.get("text"):
            raise ProjectError("對齊資料與 content 旁白文字不同")
        if not actual.get("characters"):
            raise ProjectError("對齊資料缺少 characters；不能以估計時間取代實際模型對齊")


def _audio_duration(path: Path) -> float:
    try:
        value = subprocess.check_output([
            "ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(path),
        ], text=True).strip()
        return float(value)
    except (OSError, subprocess.CalledProcessError, ValueError) as exc:
        raise ProjectError(f"無法讀取音訊長度：{path}") from exc


def _canonical_audio(project: dict[str, Any], audio: Path) -> tuple[Path, dict[str, Any]]:
    destination = runtime_paths(project)["canonical_audio"]
    destination.parent.mkdir(parents=True, exist_ok=True)
    probe = _read_probe(audio)
    codec = next((stream.get("codec_name") for stream in probe.get("streams", []) if stream.get("codec_type") == "audio"), None)
    original_sha = _sha256(audio)
    if codec == "aac" and audio.suffix.lower() in {".m4a", ".mp4", ".mov"}:
        shutil.copy2(audio, destination)
        method = "copy-aac"
    else:
        temporary = destination.with_suffix(f".{os.getpid()}.m4a")
        _run(["ffmpeg", "-y", "-hide_banner", "-loglevel", "error", "-xerror", "-i", str(audio), "-vn",
              "-c:a", "aac", "-b:a", str(project["config"].get("audio_bitrate", "192k")), str(temporary)])
        temporary.replace(destination)
        method = "canonical-aac-transcode"
    return destination, {"source": str(audio), "source_sha256": original_sha,
                         "canonical": str(destination), "canonical_sha256": _sha256(destination),
                         "method": method, "codec_before": codec}


def _read_probe(path: Path) -> dict[str, Any]:
    try:
        return json.loads(subprocess.check_output([
            "ffprobe", "-v", "error", "-of", "json", "-show_streams", "-show_format", str(path),
        ], text=True))
    except (OSError, subprocess.CalledProcessError, json.JSONDecodeError) as exc:
        raise ProjectError(f"無法讀取媒體：{path}") from exc


def _stream_hash(path: Path, selector: str) -> str:
    """Hash encoded packets for one stream, preserving the actual bytes."""
    try:
        output = subprocess.check_output(
            ["ffmpeg", "-v", "error", "-xerror", "-i", str(path), "-map", selector,
             "-c", "copy", "-f", "hash", "-hash", "sha256", "-"],
            text=True,
        ).strip()
    except (OSError, subprocess.CalledProcessError) as exc:
        raise ProjectError(f"無法計算媒體 stream 雜湊：{path} ({selector})") from exc
    if "=" not in output:
        raise ProjectError(f"媒體 stream 雜湊格式無效：{path} ({selector})")
    return output.split("=", 1)[1]


def _decode_movie(path: Path, require_audio: bool) -> None:
    """Decode the complete candidate, rather than checking metadata only."""
    audio_map = "0:a:0" if require_audio else "0:a:0?"
    _run(["ffmpeg", "-v", "error", "-xerror", "-i", str(path), "-map", "0:v:0",
          "-map", audio_map, "-f", "null", "-"])


def _char_time(row: dict[str, Any], offset: int, *, end: bool = False) -> float:
    chars = row.get("characters", [])
    if end:
        selected = [char for char in chars if int(char.get("offset", -1)) < offset]
        if selected:
            return float(selected[-1].get("end", row.get("last_voiced_end", row.get("end", 0))))
        return float(row.get("start", 0))
    selected = [char for char in chars if int(char.get("offset", -1)) >= offset]
    if selected:
        return float(selected[0].get("start", row.get("last_voiced_end", row.get("end", 0))))
    return float(row.get("last_voiced_end", row.get("end", 0)))


def _timeline(project: dict[str, Any], content: dict[str, Any], alignment: dict[str, Any], audio: Path) -> list[dict[str, Any]]:
    aligned = alignment["scenes"]
    if len(aligned) != len(content["scenes"]):
        raise ProjectError("alignment scenes 與 content scenes 數量不同")
    duration = _audio_duration(audio)
    # Round upward to the next frame so the final AAC packet is not silently
    # clipped to make the video duration look tidy.
    total = max(1, math.ceil(duration * project["fps"] - 1e-9)) / project["fps"]
    lead = float(project["config"].get("transition_lead_seconds", 0.0))
    starts = [0.0]
    for previous, current in zip(aligned, aligned[1:]):
        desired = float(current.get("speech_start", 0)) - lead
        prior_end = float(previous.get("speech_end", 0))
        if desired < prior_end:
            desired = (prior_end + float(current.get("speech_start", 0))) / 2
        starts.append(max(starts[-1], round(desired * project["fps"]) / project["fps"]))
    ends = starts[1:] + [total]
    rows = []
    for scene, aligned_row, start, end in zip(content["scenes"], aligned, starts, ends):
        if end <= start:
            raise ProjectError(f"場景時間不遞增：{scene.get('id', scene.get('frame', len(rows)))}")
        rows.append({**scene, "start": round(start, 3), "end": round(end, 3),
                     "voice_seconds": round(end - start, 3),
                     "characters": aligned_row.get("characters", []),
                     "last_voiced_end": aligned_row.get("speech_end"),
                     "trailing_silence_seconds": round(end - float(aligned_row.get("speech_end", end)), 3)})
    return rows


def _caption_chunks(row: dict[str, Any], max_chars: int) -> list[tuple[int, int, str]]:
    text = str(row["text"])
    if len(text) <= max_chars:
        return [(0, len(text), text)]
    chunks: list[tuple[int, int, str]] = []
    start = 0
    while start < len(text):
        end = min(len(text), start + max_chars)
        if end < len(text):
            split = max(text.rfind(mark, start, end) for mark in "，、；。 ")
            if split > start:
                end = split + 1
        chunks.append((start, end, text[start:end]))
        start = end
    return chunks


def _captions(project: dict[str, Any], rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    result = []
    max_chars = int(project["config"].get("subtitle_max_chars", 37))
    for row in rows:
        for start_offset, end_offset, text in _caption_chunks(row, max_chars):
            start = max(float(row["start"]), _char_time(row, start_offset) - float(project["config"].get("subtitle_lead_seconds", 0.0)))
            end = min(float(row["end"]), _char_time(row, end_offset, end=True))
            if end <= start:
                raise ProjectError(f"字幕時間沒有前進：{text}")
            result.append({"start": round(start, 3), "end": round(end, 3), "text": text})
    return result


def _write_captions(project: dict[str, Any], captions: list[dict[str, Any]]) -> None:
    paths = runtime_paths(project)
    paths["captions_vtt"].write_text("WEBVTT\n\n" + "\n\n".join(
        f"{_stamp(item['start'])} --> {_stamp(item['end'])}\n{item['text']}" for item in captions
    ) + "\n", encoding="utf-8")
    paths["captions_srt"].write_text("\n\n".join(
        f"{index}\n{_stamp(item['start'], True)} --> {_stamp(item['end'], True)}\n{item['text']}"
        for index, item in enumerate(captions, 1)
    ) + "\n", encoding="utf-8")


def _copy_runtime_sources(project: dict[str, Any]) -> None:
    paths = runtime_paths(project)
    public = paths["state"].parent
    public.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source(project, "focus_contract"), paths["focus_contract"])
    labels_path = source(project, "labels", required=False)
    if labels_path is not None:
        shutil.copy2(labels_path, paths["labels"])
    state_path = source(project, "state", required=False)
    if state_path is not None:
        shutil.copy2(state_path, paths["state"])
    else:
        exporter = project["config"].get("state_exporter")
        if not exporter:
            raise ProjectError("缺少 state 或 state_exporter")
        command = _expand_command(exporter, project, output=paths["state"])
        _run(command, cwd=project["workspace"])
        if not paths["state"].is_file():
            raise ProjectError(f"state_exporter 沒有產生 {paths['state']}")


def _expand_command(template: Any, project: dict[str, Any], *, output: Path | None = None,
                    duration: float | None = None) -> list[str]:
    if isinstance(template, str):
        values = shlex.split(template)
    elif isinstance(template, list):
        values = [str(value) for value in template]
    else:
        raise ProjectError("render_command/state_exporter 必須是字串或字串陣列")
    duration = duration if duration is not None else float(project["config"].get("duration", 0))
    replacements = {
        "{output}": str(output or project["workspace"] / "out" / "raw.mp4"), "{workspace}": str(project["workspace"]),
        "{public}": str(runtime_paths(project)["state"].parent), "{composition}": project["composition"],
        "{width}": str(project["width"]), "{height}": str(project["height"]),
        "{fps}": str(project["fps"]), "{duration}": str(duration), "{state}": str(runtime_paths(project)["state"]),
    }
    expanded = []
    for text in values:
        for token, value in replacements.items():
            text = text.replace(token, value)
        expanded.append(text)
    return expanded


def _lock(project: dict[str, Any]):
    project["workspace"].mkdir(parents=True, exist_ok=True)
    handle = (project["workspace"] / ".build.lock").open("a+")
    try:
        fcntl.flock(handle, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except BlockingIOError as exc:
        handle.close()
        raise ProjectError(f"工作區正在建置：{project['workspace']}") from exc
    return handle


def command_init(project: dict[str, Any]) -> dict[str, Any]:
    # init is the workspace boundary, before content, audio, focus or state
    # exists.  Full input validation intentionally belongs to prepare.
    if not project["project_id"].strip():
        raise ProjectError("profile id 不可為空")
    project["workspace"].mkdir(parents=True, exist_ok=True)
    renderer = renderer_dir(project)
    renderer.mkdir(parents=True, exist_ok=True)
    runtime_paths(project)["state"].parent.mkdir(parents=True, exist_ok=True)
    (project["workspace"] / "out").mkdir(parents=True, exist_ok=True)
    project["records"].mkdir(parents=True, exist_ok=True)
    _copy_template(renderer)
    profile_copy = project["workspace"] / "profile.toml"
    if not profile_copy.exists():
        shutil.copy2(project["config_path"], profile_copy)
    install = bool(project["config"].get("npm_install", project["config"].get("renderer", "remotion") == "remotion"))
    npm_result = {"status": "skipped", "reason": "profile npm_install=false"}
    if install:
        package = renderer / "package.json"
        lock = renderer / "package-lock.json"
        if not package.is_file() or not lock.is_file():
            raise ProjectError("Remotion workspace 缺少 package.json 或 package-lock.json")
        if not shutil.which("npm"):
            raise ProjectError("缺少 npm；無法執行鎖定依賴的 npm ci")
        _run(["npm", "ci", "--ignore-scripts"], cwd=renderer)
        npm_result = {"status": "pass", "command": "npm ci --ignore-scripts"}
    missing_inputs = []
    for key in ("content", "audio", "focus_contract", "state"):
        candidate = source(project, key, required=False)
        if project["config"].get(key) and (candidate is None or not candidate.is_file()):
            missing_inputs.append(key)
    result = {"tool": TOOL_VERSION, "project_id": project["project_id"],
              "workspace": str(project["workspace"]), "renderer": str(renderer),
              "public": str(runtime_paths(project)["state"].parent),
              "output": str(project["output"]), "records": str(project["records"]),
              "npm": npm_result, "pending_inputs": missing_inputs, "tools": _tool_versions()}
    _json(project["workspace"] / "init.json", result)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return result


def command_prepare(project: dict[str, Any]) -> dict[str, Any]:
    check_required(project)
    project["workspace"].mkdir(parents=True, exist_ok=True)
    renderer_dir(project).mkdir(parents=True, exist_ok=True)
    runtime_paths(project)["state"].parent.mkdir(parents=True, exist_ok=True)
    (project["workspace"] / "out").mkdir(parents=True, exist_ok=True)
    project["records"].mkdir(parents=True, exist_ok=True)
    content = _content(project)
    audio = source(project, "audio", required=False)
    if audio is None:
        raise ProjectError("目前的通用流程需要 audio 才能產生實際旁白時間；請明確提供音訊")
    alignment_path = source(project, "alignment", required=False)
    generated_alignment = project["workspace"] / "alignment.generated.json"
    if alignment_path is not None:
        alignment = _read_json(alignment_path)
        _validate_alignment(project, alignment, audio, content)
        alignment_info = {"source": str(alignment_path), "method": alignment.get("method", "provided"),
                          "model": alignment.get("model")}
    elif generated_alignment.is_file():
        candidate = _read_json(generated_alignment)
        try:
            _validate_alignment(project, candidate, audio, content)
            alignment = candidate
            alignment_info = {"source": str(generated_alignment), "method": "reused-verified-generated-alignment",
                              "model": candidate.get("model")}
        except ProjectError:
            alignment = _new_alignment(project, audio, content)
            _json(generated_alignment, alignment)
            alignment_info = {"source": str(generated_alignment), "method": alignment.get("source"), "model": alignment.get("model")}
    else:
        alignment = _new_alignment(project, audio, content)
        alignment_info = {"source": "generated", "method": alignment.get("source"), "model": alignment.get("model")}
        _json(generated_alignment, alignment)
    canonical_audio, audio_info = _canonical_audio(project, audio)
    rows = _timeline(project, content, alignment, canonical_audio)
    captions = _captions(project, rows)
    _write_captions(project, captions)
    _copy_runtime_sources(project)
    fingerprint = _fingerprints(project)
    paths = runtime_paths(project)
    _json(paths["fingerprints"], fingerprint)
    _json(paths["timeline"], {
        "project_id": project["project_id"], "width": project["width"], "height": project["height"],
        "fps": project["fps"], "duration": rows[-1]["end"], "frame_count": round(rows[-1]["end"] * project["fps"]),
        "scenes": rows, "captions": captions,
    })
    _json(paths["render_props"], {
        "composition": project["composition"], "width": project["width"], "height": project["height"],
        "fps": project["fps"], "frameCount": round(rows[-1]["end"] * project["fps"]),
        "background": project["config"].get("background", "#000000"),
        "foreground": project["config"].get("foreground", "#ffffff"),
        "focus": project["config"].get("focus", "currentColor"),
    })
    runtime_hashes = _runtime_hashes(project)
    fingerprint_sha = _sha256(paths["fingerprints"])
    result = {"tool": TOOL_VERSION, "project_id": project["project_id"], "timeline": str(paths["timeline"]),
              "duration": rows[-1]["end"], "frame_count": round(rows[-1]["end"] * project["fps"]),
              "alignment": alignment_info, "audio": audio_info, "source": fingerprint,
              "fingerprint_sha256": fingerprint_sha, "runtime_hashes": runtime_hashes,
              "tools": _tool_versions(), "style_library_required": project["config"].get("style_library_required"),
              "legacy_style_reason": project["config"].get("legacy_style_reason")}
    _json(paths["prepare"], result)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return result


def _ensure_prepared(project: dict[str, Any], *, require_current_render: bool = False) -> tuple[dict[str, Any], dict[str, Path]]:
    check_style_library(project)
    paths = runtime_paths(project)
    if not paths["prepare"].is_file() or not paths["timeline"].is_file():
        raise ProjectError("尚未 prepare；先執行 prepare 取得實際時間軸與來源指紋")
    stale = _verify_fingerprints(project)
    if stale:
        raise ProjectError("來源已改動，請重新 prepare；" + json.dumps(stale[:3], ensure_ascii=False))
    timeline = _read_json(paths["timeline"])
    if not paths["canonical_audio"].is_file():
        raise ProjectError("缺少 canonical audio；請重新 prepare")
    prepared = _read_json(paths["prepare"])
    current_fingerprint_sha = _sha256(paths["fingerprints"])
    if prepared.get("fingerprint_sha256") != current_fingerprint_sha:
        raise ProjectError("prepare 證據與目前來源指紋不同；請重新 prepare")
    current_runtime = _runtime_hashes(project)
    if prepared.get("runtime_hashes") != current_runtime:
        raise ProjectError("prepare runtime 來源已改動；請重新 prepare")
    render_manifest = paths["render"]
    if require_current_render and not render_manifest.is_file():
        raise ProjectError("缺少 render 證據；請先 render")
    if require_current_render and render_manifest.is_file():
        rendered = _read_json(render_manifest)
        if (rendered.get("prepare_fingerprint_sha256") != current_fingerprint_sha or
                rendered.get("prepare_runtime_hashes") != current_runtime):
            raise ProjectError("render 使用的 prepare 證據已過期；請重新 render")
        if not paths["movie"].is_file():
            raise ProjectError("render 證據存在但成片不存在；請重新 render")
        current_movie_sha = _sha256(paths["movie"])
        if rendered.get("movie_sha256") != current_movie_sha:
            raise ProjectError("目前 MP4 SHA 與 render.json 不一致；請重新 render")
    return timeline, paths


def _subtitle_lines(text: str, max_chars: int, max_lines: int) -> list[str]:
    lines: list[str] = []
    current = ""
    for char in text.strip():
        if char in "\\n\\r":
            if current:
                lines.append(current)
                current = ""
            continue
        if len(current) >= max_chars:
            lines.append(current)
            current = ""
        current += char
    if current:
        lines.append(current)
    if len(lines) > max_lines:
        raise ProjectError(f"字幕超過設定的 {max_lines} 行：{text}")
    return lines or [""]


def _has_ffmpeg_filter(name: str) -> bool:
    if not shutil.which("ffmpeg"):
        return False
    try:
        output = subprocess.check_output(["ffmpeg", "-hide_banner", "-filters"], text=True, stderr=subprocess.STDOUT)
    except (OSError, subprocess.CalledProcessError):
        return False
    return any(len(parts) >= 2 and parts[1] == name for parts in (line.split() for line in output.splitlines()))


def _burn_subtitles_with_images(project: dict[str, Any], source: Path, destination: Path,
                                captions: list[dict[str, Any]], duration: float) -> None:
    """Burn subtitles without assuming libass/drawtext in the local ffmpeg.

    macOS sips preserves SVG transparency and the requested non-square canvas.
    Quick Look thumbnails flatten transparency onto white and must not be used.
    The generated PNGs are only build artefacts inside the isolated
    workspace; they are never added to the source manifest.
    """
    rasterizer = shutil.which("sips")
    if not rasterizer:
        raise ProjectError("目前 ffmpeg 沒有 subtitles filter，且缺少 macOS sips；無法燒錄字幕")
    width, height = project["width"], project["height"]
    subtitle_area = project["config"].get("subtitle_area")
    if not isinstance(subtitle_area, dict):
        raise ProjectError("profile 缺少 subtitle_area；無法決定燒錄字幕區")
    left = float(subtitle_area.get("left", 0))
    top = float(subtitle_area.get("top", 0))
    right = float(subtitle_area.get("right", width))
    bottom = float(subtitle_area.get("bottom", height))
    area_height = max(1.0, bottom - top)
    font_size = float(project["config"].get("subtitle_font_size", max(16, round(area_height * 0.38))))
    max_chars = int(project["config"].get("subtitle_max_chars", max(8, round((right - left) / max(font_size * 0.62, 1)))))
    max_lines = int(project["config"].get("subtitle_max_lines", 2))
    font = xml_escape(str(project["config"].get("subtitle_font", "Arial")), {"'": "&apos;", '"': "&quot;"})
    color = str(project["config"].get("subtitle_color", "#FFFFFF"))
    background = str(project["config"].get("subtitle_background", "#000000"))
    background_opacity = float(project["config"].get("subtitle_background_opacity", 0.65))
    margin = float(project["config"].get("subtitle_margin", max(4, font_size * 0.35)))
    canvas = max(width, height)
    centre_x = (left + right) / 2
    line_gap = font_size * 1.2
    unique: dict[str, Path] = {}
    intervals: list[tuple[float, float, str]] = []
    cursor = 0.0
    for caption in sorted(captions, key=lambda item: float(item["start"])):
        start, end = float(caption["start"]), float(caption["end"])
        if start < cursor - 0.001 or end <= start:
            raise ProjectError("字幕時間重疊或沒有前進，無法燒錄")
        if start > cursor:
            intervals.append((cursor, start, ""))
        text = str(caption["text"])
        intervals.append((start, min(end, duration), text))
        cursor = min(end, duration)
    if cursor < duration - 0.001:
        intervals.append((cursor, duration, ""))
    if not intervals:
        intervals = [(0.0, duration, "")]
    with tempfile.TemporaryDirectory(prefix="subtitle-burn-", dir=str(project["workspace"])) as temporary:
        root = Path(temporary)
        svg_dir, png_dir = root / "svg", root / "png"
        svg_dir.mkdir()
        png_dir.mkdir()
        for index, text in enumerate(dict.fromkeys(text for _, _, text in intervals)):
            lines = _subtitle_lines(text, max_chars, max_lines) if text else [""]
            body = []
            if text:
                body.append(f"<rect x='{left:g}' y='{top:g}' width='{right-left:g}' height='{bottom-top:g}' fill='{xml_escape(background)}' fill-opacity='{background_opacity:g}'/>")
                first_baseline = (top + bottom - (len(lines) - 1) * line_gap) / 2 + font_size * 0.35
                for line_index, line in enumerate(lines):
                    baseline = first_baseline + line_index * line_gap
                    body.append(f"<text x='{centre_x:g}' y='{baseline:g}' text-anchor='middle' font-family='{font}' font-size='{font_size:g}' fill='{xml_escape(color)}'>{xml_escape(line)}</text>")
            svg = svg_dir / f"cue-{index:04}.svg"
            svg.write_text(f"<svg xmlns='http://www.w3.org/2000/svg' width='{width}' height='{height}' viewBox='0 0 {width} {height}'><rect width='{canvas}' height='{canvas}' fill='none'/>{''.join(body)}</svg>\n", encoding="utf-8")
            raster = png_dir / f"cue-{index:04}.png"
            _run([rasterizer, "-s", "format", "png", str(svg), "--out", str(raster)])
            if not raster.is_file():
                raise ProjectError(f"sips 沒有產生字幕畫格：{raster}")
            raster_info = _read_probe(raster)
            raster_video = next((stream for stream in raster_info.get("streams", []) if stream.get("codec_type") == "video"), {})
            if raster_video.get("width") != width or raster_video.get("height") != height or "a" not in str(raster_video.get("pix_fmt", "")):
                raise ProjectError("字幕轉圖未保留指定尺寸及 alpha；停止燒錄")
            unique[text] = raster
        listing = root / "subtitles.txt"
        listing.write_text("\n".join(
            [f"file '{unique[text].as_posix()}'\nduration {end - start:.6f}" for start, end, text in intervals]
            + [f"file '{unique[intervals[-1][2]].as_posix()}'"]
        ) + "\n", encoding="utf-8")
        filter_graph = f"[1:v]fps={project['fps']},format=rgba[sub];[0:v][sub]overlay=0:0:shortest=1:format=auto[v]"
        _run(["ffmpeg", "-y", "-hide_banner", "-loglevel", "error", "-xerror", "-i", str(source),
              "-f", "concat", "-safe", "0", "-i", str(listing), "-filter_complex", filter_graph,
              "-map", "[v]", "-an", "-t", str(duration), "-c:v", "libx264", "-crf", "18",
              "-pix_fmt", "yuv420p", str(destination)])


def _burn_subtitles(project: dict[str, Any], source: Path, destination: Path,
                    captions: list[dict[str, Any]], duration: float) -> None:
    srt = runtime_paths(project)["captions_srt"]
    # Prefer libass when it is actually present; otherwise use the portable
    # image overlay path above.  A missing filter is a capability limitation,
    # never silently treated as a burned-subtitle success.
    if _has_ffmpeg_filter("subtitles"):
        escaped = str(srt).replace("\\", "\\\\").replace(":", "\\:").replace("'", "\\'")
        style = str(project["config"].get("subtitle_force_style", "FontName=Arial,FontSize=20,PrimaryColour=&H00FFFFFF,OutlineColour=&H00000000,BorderStyle=1,Outline=2,Alignment=2,MarginV=24"))
        _run(["ffmpeg", "-y", "-hide_banner", "-loglevel", "error", "-xerror", "-i", str(source),
              "-vf", f"subtitles=filename='{escaped}':force_style='{style}'", "-an", "-c:v", "libx264", "-crf", "18",
              "-pix_fmt", "yuv420p", str(destination)])
        return
    _burn_subtitles_with_images(project, source, destination, captions, duration)


def _extract_subtitle_evidence(project: dict[str, Any], movie: Path, captions: list[dict[str, Any]],
                               duration: float) -> dict[str, Any]:
    evidence_dir = project["records"] / "subtitle-frames"
    evidence_dir.mkdir(parents=True, exist_ok=True)
    movie_sha = _sha256(movie)
    frames = []
    for index, caption in enumerate(captions):
        requested_time = (float(caption["start"]) + float(caption["end"])) / 2
        frame = evidence_dir / f"caption-{index:04}.png"
        frame_index, actual_time = _extract_frame(project, movie, requested_time, duration, frame)
        frames.append({"frame": frame_index, "time": actual_time, "requested_time": requested_time,
                       "text": caption["text"], "path": str(frame),
                       "sha256": _sha256(frame), "visible_text_review": "pending"})
    value = {"method": "encoded-frame-check", "movie_sha256": movie_sha,
             "frames": frames, "note": "frame images require visual confirmation; extraction alone is not direct listening"}
    _json(runtime_paths(project)["subtitle_evidence"], value)
    return value


def command_render(project: dict[str, Any]) -> dict[str, Any]:
    timeline, paths = _ensure_prepared(project)
    project["workspace"].mkdir(parents=True, exist_ok=True)
    lock = _lock(project)
    try:
        before = _read_json(paths["fingerprints"])
        raw = project["workspace"] / "out" / f"raw-{os.getpid()}.mp4"
        renderer = str(project["config"].get("renderer", "remotion"))
        if renderer == "remotion":
            package_dir = renderer_dir(project)
            executable = package_dir / "node_modules" / ".bin" / "remotion"
            if not executable.is_file():
                raise ProjectError(f"缺少 Remotion 依賴：{executable}；先執行 init 並 npm ci")
            # Resolve generated props from the renderer working directory.
            props_path = paths["render_props"].relative_to(package_dir).as_posix()
            _run([str(executable), "render", project["entry"], project["composition"], str(raw),
                  "--props", props_path, "--log=error"], cwd=package_dir)
            command = [str(executable), "render", project["entry"], project["composition"], str(raw)]
        elif renderer in {"command", "custom"}:
            template = project["config"].get("render_command")
            if not template:
                raise ProjectError("renderer=command 必須提供 render_command")
            command = _expand_command(template, project, output=raw, duration=float(timeline["duration"]))
            _run(command, cwd=project["workspace"])
        elif renderer == "ffmpeg":
            command = ["ffmpeg", "-y", "-hide_banner", "-loglevel", "error", "-f", "lavfi",
                       "-i", f"color=c={project['config'].get('background', 'black')}:s={project['width']}x{project['height']}:r={project['fps']}",
                       "-t", str(timeline["duration"]), "-c:v", "libx264", "-pix_fmt", "yuv420p", str(raw)]
            _run(command)
        else:
            raise ProjectError(f"不支援 renderer：{renderer}")
        if not raw.is_file() or raw.stat().st_size == 0:
            raise ProjectError("renderer 沒有產生影片")
        rendered = raw
        burned = bool(project["config"].get("burn_subtitles", True))
        captions = timeline.get("captions", [])
        if burned:
            rendered = project["workspace"] / "out" / f"burned-{os.getpid()}.mp4"
            _burn_subtitles(project, raw, rendered, captions, float(timeline["duration"]))
        final_tmp = project["workspace"] / "out" / f"video-{os.getpid()}.tmp.mp4"
        _run(["ffmpeg", "-y", "-hide_banner", "-loglevel", "error", "-xerror", "-i", str(rendered),
              "-i", str(paths["canonical_audio"]), "-map", "0:v:0", "-map", "1:a:0", "-c:v", "copy", "-c:a", "copy",
              "-t", str(timeline["duration"]), "-movflags", "+faststart", str(final_tmp)])
        final_tmp.replace(paths["movie"])
        canonical_audio_sha = _stream_hash(paths["canonical_audio"], "0:a:0")
        movie_audio_sha = _stream_hash(paths["movie"], "0:a:0")
        if canonical_audio_sha != movie_audio_sha:
            paths["movie"].unlink(missing_ok=True)
            raise ProjectError("封裝後音訊 stream 雜湊與 canonical AAC 不一致，停止交付")
        after = _verify_fingerprints(project)
        if after:
            paths["movie"].unlink(missing_ok=True)
            raise ProjectError("建置期間來源改動，停止交付；" + json.dumps(after[:3], ensure_ascii=False))
        subtitle_evidence = _extract_subtitle_evidence(project, paths["movie"], captions,
                                                       float(timeline["duration"])) if burned else None
        result = {"tool": TOOL_VERSION, "project_id": project["project_id"], "movie": str(paths["movie"]),
                  "movie_sha256": _sha256(paths["movie"]), "renderer": renderer, "render_command": command,
                  "burned_subtitles": burned, "subtitle_evidence": str(runtime_paths(project)["subtitle_evidence"]) if subtitle_evidence else None,
                  "canonical_audio_stream_sha256": canonical_audio_sha,
                  "movie_audio_stream_sha256": movie_audio_sha,
                  "prepare_fingerprint_sha256": _sha256(paths["fingerprints"]),
                  "prepare_runtime_hashes": _runtime_hashes(project),
                  "source_fingerprints": before, "tools": _tool_versions()}
        _json(paths["render"], result)
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return result
    finally:
        with contextlib.suppress(OSError):
            fcntl.flock(lock, fcntl.LOCK_UN)
        lock.close()


def _extract_frame(project: dict[str, Any], movie: Path, requested_time: float,
                   duration: float, destination: Path) -> tuple[int, float]:
    """Extract a legal encoded frame without seeking past the final PTS."""
    fps = project["fps"]
    frame_count = max(1, math.ceil(duration * fps - 1e-9))
    frame_index = min(frame_count - 1, max(0, math.floor(requested_time * fps + 1e-9)))
    actual_time = frame_index / fps
    # Seek just before the frame boundary.  The previous implementation
    # rounded 29/30 to 0.967, which is after the last 30-fps frame at 0.9666.
    seek_time = max(0.0, actual_time - min(0.001, 0.25 / fps))
    _run(["ffmpeg", "-y", "-hide_banner", "-loglevel", "error", "-ss", f"{seek_time:.9f}",
          "-i", str(movie), "-frames:v", "1", str(destination)])
    if not destination.is_file() or destination.stat().st_size == 0:
        raise ProjectError(f"無法抽取成片影格：requested={requested_time} frame={frame_index} time={actual_time}")
    return frame_index, actual_time


def _capture_frames(project: dict[str, Any], movie: Path, contracts: list[dict[str, Any]], duration: float) -> list[dict[str, Any]]:
    directory = project["records"] / "movie-frames"
    directory.mkdir(parents=True, exist_ok=True)
    point_reasons: dict[int, set[str]] = {}

    def add_point(value: Any, reason: str) -> None:
        try:
            point = float(value)
        except (TypeError, ValueError):
            raise ProjectError(f"成片檢查時間不是數字：{value}")
        if not math.isfinite(point) or point < 0:
            raise ProjectError(f"成片檢查時間無效：{value}")
        frame_count = max(1, math.ceil(duration * project["fps"] - 1e-9))
        frame_index = min(frame_count - 1, max(0, math.floor(point * project["fps"] + 1e-9)))
        point_reasons.setdefault(frame_index, set()).add(reason)

    sample_interval = project["config"].get("sample_interval", 1.0)
    try:
        sample_interval = float(sample_interval)
    except (TypeError, ValueError) as exc:
        raise ProjectError("sample_interval 必須是正數") from exc
    if not math.isfinite(sample_interval) or sample_interval <= 0:
        raise ProjectError("sample_interval 必須是正數")
    sample = 0.0
    while sample < duration:
        add_point(sample, "periodic")
        sample += sample_interval
    add_point(max(0.0, duration - 1 / project["fps"]), "full-clip-end")
    for contract in contracts:
        add_point(contract["start"], f"contract:{contract['id']}:start")
        add_point((contract["start"] + contract["end"]) / 2, f"contract:{contract['id']}:middle")
        add_point(max(contract["start"], contract["end"] - 1 / project["fps"]), f"contract:{contract['id']}:end")
        if contract.get("grace_start"):
            add_point(contract["start"] + contract["grace_start"], f"contract:{contract['id']}:grace-start-end")
        if contract.get("grace_end"):
            add_point(contract["end"] - contract["grace_end"], f"contract:{contract['id']}:grace-end-start")

    for key, reason in (("review_times", "profile-review-time"), ("transition_times", "profile-transition")):
        values = project["config"].get(key, [])
        if values in (None, ""):
            continue
        if not isinstance(values, list):
            raise ProjectError(f"{key} 必須是時間數字陣列")
        for value in values:
            if isinstance(value, dict):
                add_point(value.get("time"), str(value.get("reason", reason)))
            else:
                add_point(value, reason)
    frames = []
    for index, frame_index in enumerate(sorted(point_reasons)):
        requested_time = frame_index / project["fps"]
        frame = directory / f"frame-{index:04}.png"
        _, actual_time = _extract_frame(project, movie, requested_time, duration, frame)
        frames.append({"frame": frame_index, "time": actual_time, "path": str(frame), "sha256": _sha256(frame),
                       "reasons": sorted(point_reasons[frame_index])})
    return frames


def _assessment_frame_evidence(value: dict[str, Any], key: str, expected: list[dict[str, Any]],
                               *, kind: str, require_text: bool = False) -> list[dict[str, Any]]:
    """Bind every assessment observation to an extracted frame from this run.

    The reviewer may add prose, but cannot replace the current frame hash/time
    with a claim about an unrecorded image.  A frame is only accepted when its
    source file is still present and its current bytes match the render record.
    """
    issues: list[dict[str, Any]] = []
    supplied = value.get(key)
    if not isinstance(supplied, list) or not supplied:
        return [{"code": f"assessment-{kind}-frames-missing", "actual": supplied}]
    if not expected:
        return [{"code": f"assessment-{kind}-frames-unexpected", "message": "本次沒有可綁定的實際畫格"}]

    expected_keys: list[tuple[float, str, str | None]] = []
    expected_by_key: dict[tuple[float, str, str | None], dict[str, Any]] = {}
    for frame in expected:
        if not isinstance(frame, dict):
            issues.append({"code": f"{kind}-evidence-invalid-source", "frame": frame})
            continue
        path_value = frame.get("path")
        path = Path(path_value) if path_value else None
        expected_sha = frame.get("sha256")
        timestamp = checks._number(frame.get("time"))
        text_value = str(frame.get("text")) if require_text and frame.get("text") is not None else None
        if timestamp is None or not math.isfinite(timestamp) or not expected_sha or path is None or not path.is_file():
            issues.append({"code": f"{kind}-evidence-invalid-source", "frame": frame})
            continue
        if path.stat().st_size == 0 or checks.sha256(path) != expected_sha:
            issues.append({"code": f"{kind}-evidence-source-stale", "path": str(path),
                           "expected": expected_sha,
                           "actual": checks.sha256(path) if path.is_file() and path.stat().st_size else None})
            continue
        identity = (round(timestamp, 3), str(expected_sha), text_value)
        expected_keys.append(identity)
        expected_by_key[identity] = frame

    supplied_keys: list[tuple[float, str, str | None]] = []
    for index, frame in enumerate(supplied):
        if not isinstance(frame, dict):
            issues.append({"code": f"assessment-{kind}-frame-invalid", "index": index, "frame": frame})
            continue
        if frame.get("status") != "pass":
            issues.append({"code": f"assessment-{kind}-frame-not-passed", "index": index,
                           "actual": frame.get("status")})
        observation = str(frame.get("observation", "")).strip()
        if not observation:
            issues.append({"code": f"assessment-{kind}-observation-missing", "index": index})
        timestamp = checks._number(frame.get("time"))
        frame_sha = str(frame.get("sha256", "")).strip()
        text_value = str(frame.get("text")) if require_text and frame.get("text") is not None else None
        if timestamp is None or not math.isfinite(timestamp) or not frame_sha:
            issues.append({"code": f"assessment-{kind}-identity-invalid", "index": index})
            continue
        identity = (round(timestamp, 3), frame_sha, text_value)
        supplied_keys.append(identity)
        expected_frame = expected_by_key.get(identity)
        if expected_frame is None:
            issues.append({"code": f"assessment-{kind}-frame-stale-or-fake", "index": index,
                           "time": timestamp, "sha256": frame_sha})
        elif frame.get("path"):
            supplied_path = Path(os.fspath(frame["path"])).expanduser().resolve()
            expected_path = Path(os.fspath(expected_frame["path"])).expanduser().resolve()
            if supplied_path != expected_path:
                issues.append({"code": f"assessment-{kind}-path-mismatch", "index": index,
                               "expected": str(expected_path), "actual": str(supplied_path)})

    if len(supplied) != len(expected):
        issues.append({"code": f"assessment-{kind}-frame-count", "expected": len(expected),
                       "actual": len(supplied)})
    if sorted(supplied_keys) != sorted(expected_keys):
        issues.append({"code": f"assessment-{kind}-frame-set", "expected": sorted(expected_keys),
                       "actual": sorted(supplied_keys)})
    return issues


def _read_assessment(project: dict[str, Any], assessment_path: Path | None, movie_sha: str,
                     captured_frames: list[dict[str, Any]],
                     subtitle_evidence: dict[str, Any] | None) -> dict[str, Any]:
    if assessment_path is None:
        return {"status": "missing", "issues": [{"code": "missing-assessment",
                                                    "message": "需要綁定影片與來源 SHA 的實際視覺評審紀錄"}]}
    if not assessment_path.is_file():
        return {"status": "fail", "issues": [{"code": "assessment-missing", "path": str(assessment_path)}]}
    value = _read_json(assessment_path)
    if not isinstance(value, dict):
        return {"status": "fail", "issues": [{"code": "assessment-invalid", "message": "assessment 必須是 JSON object"}]}
    issues = []
    if value.get("movie_sha256") != movie_sha:
        issues.append({"code": "assessment-movie-stale", "expected": movie_sha, "actual": value.get("movie_sha256")})
    fingerprint_path = runtime_paths(project)["fingerprints"]
    if value.get("source_fingerprints_sha256") != _sha256(fingerprint_path):
        issues.append({"code": "assessment-source-stale", "expected": _sha256(fingerprint_path),
                       "actual": value.get("source_fingerprints_sha256")})
    issues.extend(_assessment_frame_evidence(value, "captured_frames", captured_frames, kind="captured"))
    visual = value.get("static_visual", value.get("visual", {}))
    if not isinstance(visual, dict) or visual.get("status") != "pass":
        issues.append({"code": "visual-assessment-not-passed", "actual": visual})
    subtitles = value.get("subtitle_visibility", value.get("subtitles", {}))
    allowed_subtitle_statuses = {"pass"}
    if not bool(project["config"].get("burn_subtitles", True)):
        allowed_subtitle_statuses.add("overridden")
    if not isinstance(subtitles, dict) or subtitles.get("status") not in allowed_subtitle_statuses:
        issues.append({"code": "subtitle-assessment-not-passed", "actual": subtitles})
    elif bool(project["config"].get("burn_subtitles", True)):
        expected_subtitle_frames = []
        if isinstance(subtitle_evidence, dict):
            expected_subtitle_frames = subtitle_evidence.get("frames", [])
        issues.extend(_assessment_frame_evidence(value, "subtitle_frames", expected_subtitle_frames,
                                                 kind="subtitle", require_text=True))
    return {"status": "pass" if not issues else "fail", "issues": issues, "value": value}


def command_review(project: dict[str, Any], assessment_path: Path | None = None) -> dict[str, Any]:
    timeline, paths = _ensure_prepared(project, require_current_render=True)
    movie = paths["movie"]
    if not movie.is_file():
        raise ProjectError("尚未 render；找不到候選成片")
    movie_sha = _sha256(movie)
    render_manifest = _read_json(paths["render"])
    contracts = checks.normalize_contract(_read_json(paths["focus_contract"]))
    state_result = checks.review_state_files(
        state_path=paths["state"], contract_path=paths["focus_contract"], width=project["width"],
        height=project["height"], fps=project["fps"], frame_count=int(timeline["frame_count"]),
        safe_area=project["config"].get("content_safe_area"),
        subtitle_area=project["config"].get("subtitle_area"),
        opacity_threshold=float(project["config"]["opacity_threshold"]),
        labels=_labels(project),
    )
    probe = checks.probe_movie(movie, width=project["width"], height=project["height"], fps=project["fps"],
                               duration=float(timeline["duration"]), require_audio=bool(project["config"].get("require_audio", True)))
    decode_issues: list[dict[str, Any]] = []
    audio_hashes: dict[str, str] = {}
    try:
        _decode_movie(movie, bool(project["config"].get("require_audio", True)))
        if project["config"].get("require_audio", True):
            audio_hashes = {
                "canonical_audio_stream_sha256": _stream_hash(paths["canonical_audio"], "0:a:0"),
                "movie_audio_stream_sha256": _stream_hash(movie, "0:a:0"),
            }
            if audio_hashes["canonical_audio_stream_sha256"] != audio_hashes["movie_audio_stream_sha256"]:
                decode_issues.append({"code": "audio-stream-hash-mismatch", **audio_hashes})
    except ProjectError as exc:
        decode_issues.append({"code": "full-decode-failed", "error": str(exc)})
    stale = _verify_fingerprints(project)
    subtitle_issues = checks.check_subtitle_evidence(paths["subtitle_evidence"], movie_sha) if bool(project["config"].get("burn_subtitles", True)) else []
    frames = _capture_frames(project, movie, contracts, float(timeline["duration"]))
    subtitle_evidence = None
    if bool(project["config"].get("burn_subtitles", True)) and paths["subtitle_evidence"].is_file():
        subtitle_evidence = _read_json(paths["subtitle_evidence"])
    assessment = _read_assessment(project, assessment_path, movie_sha, frames, subtitle_evidence)
    technical = []
    technical.extend(stale)
    technical.extend(state_result["issues"])
    technical.extend(probe.get("issues", []))
    technical.extend(decode_issues)
    technical.extend(subtitle_issues)
    statuses = {
        "automated_state": {"status": "pass" if not state_result["issues"] else "fail", "method": "motion_checks.check_focus", "issues": state_result["issues"]},
        "technical": {"status": "pass" if not technical else "fail", "method": "ffprobe+source-fingerprint+encoded-frame-extraction", "issues": technical},
        "static_visual": {"status": "unverified", "method": "manual/AI frame review required", "frames": frames},
        "subtitle_visibility": {"status": "unverified" if bool(project["config"].get("burn_subtitles", True)) else "overridden",
                                "method": "encoded subtitle-frame evidence plus visual review required" if bool(project["config"].get("burn_subtitles", True)) else "profile subtitle override",
                                "reason": project["config"].get("subtitle_override_reason")},
        "audio_analysis": {"status": "pass" if probe.get("status") == "pass" and not decode_issues else "fail",
                           "method": "ffprobe + full decode + encoded AAC stream hash; not direct listening"},
        "user_acceptance": {"status": "pending", "method": "user decision required"},
    }
    if assessment.get("status") == "pass":
        value = assessment.get("value", {})
        statuses["static_visual"] = {"status": "pass", "method": "bound encoded-frame assessment", "assessment": value.get("static_visual", value.get("visual"))}
        subtitle_value = value.get("subtitle_visibility", value.get("subtitles"))
        statuses["subtitle_visibility"] = {"status": subtitle_value.get("status"), "method": "bound encoded-frame subtitle assessment", "assessment": subtitle_value}
        if isinstance(value.get("audio_analysis"), dict):
            statuses["audio_analysis"] = value["audio_analysis"]
    else:
        technical.append({"code": "assessment-required", "details": assessment.get("issues", [])})
    if technical:
        statuses["technical"]["status"] = "fail"
        statuses["technical"]["issues"] = technical
    fingerprint_sha = _sha256(paths["fingerprints"])
    result = {"tool": TOOL_VERSION, "project_id": project["project_id"], "movie": str(movie),
              "movie_sha256": movie_sha, "source_fingerprints_sha256": fingerprint_sha,
              "render_movie_sha256": render_manifest.get("movie_sha256"),
              "verdict": "pass" if not technical else "fail",
              "statuses": statuses, "assessment": assessment,
              "audio_stream_hashes": audio_hashes,
              "source_fingerprints": _read_json(paths["fingerprints"]),
              "captured_frames": frames, "reviewed_at": time.strftime("%Y-%m-%dT%H:%M:%S%z")}
    _json(paths["review"], result)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    if result["verdict"] != "pass":
        raise ProjectError("成片 review 未通過；請見 records/review.json")
    return result


def command_deliver(project: dict[str, Any], acceptance: str = "pending") -> dict[str, Any]:
    _, paths = _ensure_prepared(project, require_current_render=True)
    if not paths["review"].is_file() or not paths["movie"].is_file():
        raise ProjectError("deliver 需要先完成 render 與 review")
    review = _read_json(paths["review"])
    movie_sha = _sha256(paths["movie"])
    render_manifest = _read_json(paths["render"])
    visual_status = review.get("statuses", {}).get("static_visual", {}).get("status")
    subtitle_status = review.get("statuses", {}).get("subtitle_visibility", {}).get("status")
    subtitle_allowed = {"pass"} if bool(project["config"].get("burn_subtitles", True)) else {"overridden"}
    if (review.get("verdict") != "pass" or visual_status != "pass" or
            subtitle_status not in subtitle_allowed or
            review.get("movie_sha256") != movie_sha or
            render_manifest.get("movie_sha256") != movie_sha or
            review.get("source_fingerprints_sha256") != _sha256(paths["fingerprints"])):
        raise ProjectError("review 與目前成片 SHA 不一致或未通過，停止發布")
    stale = _verify_fingerprints(project)
    if stale:
        raise ProjectError("來源已改動，review 過期，停止發布")
    project["output"].mkdir(parents=True, exist_ok=True)
    destination = project["output"] / str(project["config"].get("filename", "video.mp4"))
    caption_paths = [paths["captions_srt"], paths["captions_vtt"]]
    for source_path in caption_paths:
        if not source_path.is_file() or source_path.stat().st_size == 0:
            raise ProjectError(f"缺少可修改字幕來源：{source_path}")
    temporary = destination.with_name(f".{destination.name}.{os.getpid()}.tmp")
    shutil.copy2(paths["movie"], temporary)
    if _sha256(temporary) != movie_sha:
        temporary.unlink(missing_ok=True)
        raise ProjectError("交付複製後 SHA 不一致")
    temporary.replace(destination)
    subtitle_sources = []
    for source_name, source_path in zip(("captions.srt", "captions.vtt"), caption_paths):
        copied = project["output"] / source_name
        shutil.copy2(source_path, copied)
        subtitle_sources.append(str(copied))
    html_path = project["output"] / "delivery.html"
    html_path.write_text(
        "<!doctype html><meta charset='utf-8'><title>影片交付</title>"
        f"<video controls preload='metadata' src='{html.escape(destination.name)}'></video>"
        f"<p><a download href='{html.escape(destination.name)}'>下載成片</a></p>"
        f"<p>字幕來源：<a href='{html.escape(Path(subtitle_sources[0]).name)}'>SRT</a> · "
        f"<a href='{html.escape(Path(subtitle_sources[1]).name)}'>VTT</a></p>\n",
        encoding="utf-8",
    )
    result = {"tool": TOOL_VERSION, "project_id": project["project_id"], "movie": str(destination),
              "movie_sha256": movie_sha, "review": str(paths["review"]),
              "render_movie_sha256": render_manifest.get("movie_sha256"),
              "statuses": review.get("statuses", {}), "user_acceptance": acceptance,
              "delivery_html": str(html_path), "subtitle_sources": subtitle_sources,
              "rebuild_command": f"uv run --frozen python scripts/motion_project.py --config {project['config_path']} render",
              "delivered_at": time.strftime("%Y-%m-%dT%H:%M:%S%z")}
    _json(project["output"] / "delivery.json", result)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return result


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", required=True, type=Path, help="本片 profile.toml")
    parser.add_argument("--source-root", type=Path, help="覆寫 profile source_root，供搬移後建置")
    parser.add_argument("--version", action="version", version=TOOL_VERSION)
    parser.add_argument("command", choices=["init", "prepare", "render", "review", "deliver"])
    parser.add_argument("--user-acceptance", choices=["pending", "accepted", "rejected"], default="pending")
    parser.add_argument("--assessment", type=Path,
                        help="review 用的實際成片評審 JSON，須綁定 movie/source SHA 且 static_visual=pass")
    parser.add_argument("--init-id", help="config 尚不存在時，init 建立的 profile id")
    args = parser.parse_args(argv)
    try:
        project = load_project(args.config, args.source_root, allow_missing=args.command == "init", init_id=args.init_id)
        if args.command == "init":
            command_init(project)
        elif args.command == "prepare":
            command_prepare(project)
        elif args.command == "render":
            command_render(project)
        elif args.command == "review":
            assessment = args.assessment.expanduser().resolve() if args.assessment else None
            command_review(project, assessment)
        else:
            command_deliver(project, args.user_acceptance)
    except ProjectError as exc:
        print(f"motion-project: {exc}", file=sys.stderr)
        return 2
    except (OSError, ValueError, KeyError) as exc:
        print(f"motion-project: 輸入或建置失敗：{exc}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
