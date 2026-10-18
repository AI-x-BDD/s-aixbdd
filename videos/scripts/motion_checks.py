"""Generic, data-driven checks for a rendered motion video.

This module deliberately knows nothing about a particular chapter, scene count,
colour palette, or duration.  A film supplies an independent focus contract and
the renderer supplies the actual per-frame state.  The two are compared here;
the expected focus is never derived from ``active`` state.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
from pathlib import Path
import subprocess
from typing import Any, Iterable


TOOL_VERSION = "motion-checks/0.1"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _number(value: Any, default: float | None = None) -> float | None:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _path(value: Any) -> Path:
    return Path(os.fspath(value)).expanduser().resolve()


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def normalize_contract(value: Any) -> list[dict[str, Any]]:
    """Return a list of independently checkable focus intervals.

    The public format accepts either ``{"segments": [...]}`` or a bare list.
    A target may be a string or ``{"id": ..., "name": ...}``.  ``name`` is
    checked against the visible item's text while the id is checked against the
    renderer state.
    """

    raw = value.get("segments", value) if isinstance(value, dict) else value
    if not isinstance(raw, list) or not raw:
        raise ValueError("focus contract 必須包含非空 segments 陣列")
    result: list[dict[str, Any]] = []
    for index, item in enumerate(raw):
        if not isinstance(item, dict):
            raise ValueError(f"focus contract 第 {index + 1} 段不是物件")
        start = _number(item.get("start"))
        end = _number(item.get("end"))
        if (start is None or end is None or not math.isfinite(start) or not math.isfinite(end)
                or start < 0 or end <= start):
            raise ValueError(f"focus contract 第 {index + 1} 段時間無效")
        targets = item.get("targets", item.get("required_visible", []))
        if not isinstance(targets, list) or not targets:
            raise ValueError(f"focus contract 第 {index + 1} 段必須列出 targets")
        if "required_active" not in item:
            raise ValueError(f"focus contract 第 {index + 1} 段必須明列 required_active；不能從實際 active 反推焦點")
        if not isinstance(item.get("required_active"), list):
            raise ValueError(f"focus contract 第 {index + 1} 段 required_active 必須是陣列")
        if "forbidden_active" in item and not isinstance(item.get("forbidden_active"), list):
            raise ValueError(f"focus contract 第 {index + 1} 段 forbidden_active 必須是陣列")
        if item.get("allow_extra_active") and not item.get("extra_active_reason"):
            raise ValueError(f"focus contract 第 {index + 1} 段允許額外 active 時必須說明理由")
        target_specs: list[dict[str, Any]] = []
        for target in targets:
            if isinstance(target, str):
                target_specs.append({"id": target})
            elif isinstance(target, dict) and target.get("id"):
                target_specs.append({"id": str(target["id"]), **target})
            else:
                raise ValueError(f"focus contract 第 {index + 1} 段有無效 target")
        grace_start = _number(item.get("grace_start"), 0.0)
        grace_end = _number(item.get("grace_end"), 0.0)
        length = end - start
        if grace_start is None or grace_end is None or not math.isfinite(grace_start) or not math.isfinite(grace_end):
            raise ValueError(f"focus contract 第 {index + 1} 段 grace 必須是有限數字")
        if grace_start < 0 or grace_end < 0 or grace_start + grace_end >= length:
            raise ValueError(f"focus contract 第 {index + 1} 段 grace 不能覆蓋整段或為負數")
        if (grace_start or grace_end) and not (item.get("hold_reason") or item.get("transition_reason")):
            raise ValueError(f"focus contract 第 {index + 1} 段 grace 必須說明觀看目的")
        result.append({
            **item,
            "id": str(item.get("id", item.get("scene", f"segment-{index + 1}"))),
            "start": start,
            "end": end,
            "targets": target_specs,
            "required_active": list(item.get("required_active", [])),
            "forbidden_active": list(item.get("forbidden_active", [])),
            "grace_start": grace_start,
            "grace_end": grace_end,
        })
    result.sort(key=lambda item: (item["start"], item["end"], item["id"]))
    return result


def normalize_states(value: Any) -> list[dict[str, Any]]:
    raw = value.get("frames", value) if isinstance(value, dict) else value
    if not isinstance(raw, list) or not raw:
        raise ValueError("state exporter 必須產生非空 frames 陣列")
    states = []
    for index, state in enumerate(raw):
        if not isinstance(state, dict):
            raise ValueError(f"state 第 {index} 筆不是物件")
        if "frame" not in state or "t" not in state:
            raise ValueError(f"state 第 {index} 筆缺少 frame 或 t")
        states.append(state)
    return sorted(states, key=lambda item: int(item["frame"]))


def _visible_by_id(state: dict[str, Any]) -> dict[str, dict[str, Any]]:
    values = state.get("visible", state.get("items", []))
    result = {}
    if not isinstance(values, list):
        return result
    for item in values:
        if isinstance(item, dict) and item.get("id"):
            result[str(item["id"])] = item
    return result


def _bounds(item: dict[str, Any]) -> tuple[float, float, float, float] | None:
    value = item.get("projected_bounds", item.get("bounds"))
    if isinstance(value, dict):
        values = (value.get("x"), value.get("y"), value.get("w"), value.get("h"))
    elif isinstance(value, (list, tuple)) and len(value) == 4:
        values = tuple(value)
    else:
        values = (item.get("x"), item.get("y"), item.get("w"), item.get("h"))
    if any(v is None for v in values):
        return None
    try:
        return tuple(float(v) for v in values)  # type: ignore[return-value]
    except (TypeError, ValueError):
        return None


def _within(bounds: tuple[float, float, float, float], width: float, height: float,
            safe: dict[str, Any]) -> bool:
    x, y, w, h = bounds
    left = float(safe.get("left", 0))
    top = float(safe.get("top", 0))
    right = float(safe.get("right", width))
    bottom = float(safe.get("bottom", height))
    return (all(math.isfinite(value) for value in bounds)
            and w > 0 and h > 0
            and x >= left and y >= top and x + w <= right and y + h <= bottom)


def _overlap(a: tuple[float, float, float, float], b: tuple[float, float, float, float]) -> bool:
    ax, ay, aw, ah = a
    bx, by, bw, bh = b
    return ax < bx + bw and bx < ax + aw and ay < by + bh and by < ay + ah


def _contract_at(contracts: list[dict[str, Any]], t: float) -> dict[str, Any] | None:
    for item in contracts:
        # Half-open intervals make a hand-off belong to the next focus target;
        # otherwise a frame exactly at a scene boundary can silently validate
        # against the previous object.
        if item["start"] <= t < item["end"]:
            return item
    return None


def _projected_bounds(item: dict[str, Any]) -> tuple[float, float, float, float] | None:
    value = item.get("projected_bounds")
    if isinstance(value, dict):
        values = (value.get("x"), value.get("y"), value.get("w"), value.get("h"))
    elif isinstance(value, (list, tuple)) and len(value) == 4:
        values = tuple(value)
    else:
        return None
    if any(v is None for v in values):
        return None
    try:
        return tuple(float(v) for v in values)  # type: ignore[return-value]
    except (TypeError, ValueError):
        return None


def check_state_shape(states: list[dict[str, Any]], fps: float, frame_count: int) -> list[dict[str, Any]]:
    issues: list[dict[str, Any]] = []
    expected = list(range(frame_count))
    actual = [int(state["frame"]) for state in states]
    if actual != expected:
        issues.append({"code": "state-frame-sequence", "expected": [0, frame_count - 1], "actual": actual[:5] + actual[-5:]})
    for index, state in enumerate(states):
        frame = int(state["frame"])
        t = _number(state.get("t"))
        expected_t = frame / fps
        if t is None or abs(t - expected_t) > max(1 / fps, 0.01):
            issues.append({"code": "state-time-mismatch", "frame": frame, "expected": expected_t, "actual": t})
        if index and frame <= int(states[index - 1]["frame"]):
            issues.append({"code": "state-frame-order", "frame": frame})
    return issues


def check_focus(states: list[dict[str, Any]], contracts: list[dict[str, Any]], *,
                width: int, height: int, safe_area: dict[str, Any] | None = None,
                subtitle_area: dict[str, Any] | None = None,
                opacity_threshold: float | None = None,
                labels: dict[str, str] | None = None,
                require_bounds: bool = True) -> list[dict[str, Any]]:
    """Compare every encoded-time state with an independent focus contract."""

    safe = safe_area or {}
    issues: list[dict[str, Any]] = []
    if not contracts:
        return [{"code": "empty-focus-contract"}]
    first = contracts[0]["start"]
    last = max(item["end"] for item in contracts)
    if first > 0.001:
        issues.append({"code": "focus-gap", "start": 0.0, "end": first})
    for previous, current in zip(contracts, contracts[1:]):
        if current["start"] > previous["end"] + 0.001:
            issues.append({"code": "focus-gap", "start": previous["end"], "end": current["start"]})
        if current["start"] < previous["end"] - 0.001:
            issues.append({"code": "focus-overlap", "first": previous["id"], "second": current["id"]})
    if any(last < state["t"] - 1 / max(1, len(states)) for state in states):
        issues.append({"code": "focus-does-not-cover-end", "end": last})

    for state in states:
        t = float(state["t"])
        contract = _contract_at(contracts, t)
        if contract is None:
            issues.append({"code": "focus-uncovered-frame", "frame": state["frame"], "t": t})
            continue
        in_grace = (t < contract["start"] + contract["grace_start"] or
                    t >= contract["end"] - contract["grace_end"])
        visible = _visible_by_id(state)
        active = {str(value) for value in state.get("active", [])}
        required_active = {str(value) for value in contract.get("required_active", [])}
        forbidden = {str(value) for value in contract.get("forbidden_active", [])}
        if not in_grace and not required_active.issubset(active):
            issues.append({"code": "focus-not-active", "frame": state["frame"], "t": t,
                           "segment": contract["id"], "expected": sorted(required_active),
                           "actual": sorted(active)})
        if not in_grace and not contract.get("allow_extra_active", False) and active != required_active:
            issues.append({"code": "wrong-focus", "frame": state["frame"], "t": t,
                           "segment": contract["id"], "expected_exact": sorted(required_active),
                           "actual": sorted(active)})
        if contract.get("allow_extra_active") and not contract.get("extra_active_reason"):
            issues.append({"code": "extra-focus-without-reason", "frame": state["frame"], "segment": contract["id"]})
        if forbidden.intersection(active):
            issues.append({"code": "wrong-focus", "frame": state["frame"], "t": t,
                           "segment": contract["id"], "forbidden": sorted(forbidden.intersection(active))})
        for target in contract["targets"]:
            target_id = str(target["id"])
            item = visible.get(target_id)
            target_threshold = target.get("min_opacity", contract.get("opacity_threshold", opacity_threshold))
            try:
                threshold_value = float(target_threshold)
            except (TypeError, ValueError):
                threshold_value = float("nan")
            if not math.isfinite(threshold_value) or not 0 < threshold_value <= 1:
                issues.append({"code": "opacity-threshold-missing", "frame": state["frame"], "target": target_id})
                continue
            if item is None or float(item.get("opacity", 0)) < threshold_value:
                if not in_grace:
                    issues.append({"code": "focus-not-visible", "frame": state["frame"], "t": t,
                                   "segment": contract["id"], "target": target_id})
                continue
            expected_name = target.get("name", target.get("label")) or (labels or {}).get(target_id)
            if expected_name is not None and str(expected_name) not in str(item.get("text", "")):
                issues.append({"code": "label-missing", "frame": state["frame"], "t": t,
                               "segment": contract["id"], "target": target_id,
                               "expected_name": expected_name, "actual": item.get("text", "")})
            elif not str(item.get("text", "")).strip():
                issues.append({"code": "label-empty", "frame": state["frame"], "t": t,
                               "segment": contract["id"], "target": target_id})
            bounds = _projected_bounds(item)
            if require_bounds and bounds is None:
                issues.append({"code": "projected-bounds-missing", "frame": state["frame"], "target": target_id})
            elif bounds is not None and not _within(bounds, width, height, safe):
                issues.append({"code": "cropped-focus", "frame": state["frame"], "t": t,
                               "segment": contract["id"], "target": target_id, "bounds": bounds})
            if bounds is not None and subtitle_area is not None:
                subtitle_bounds = _bounds({"bounds": subtitle_area})
                if subtitle_bounds is not None and _overlap(bounds, subtitle_bounds):
                    issues.append({"code": "focus-overlaps-subtitle-area", "frame": state["frame"], "target": target_id})
            # A state exporter may provide text bounds and path bounds.  When it
            # does, check the contract's route-avoidance promise as well.
            text_bounds = item.get("text_bounds")
            paths = state.get("paths", [])
            if isinstance(text_bounds, dict) and isinstance(paths, list):
                tb = _bounds({"bounds": text_bounds})
                if tb is not None:
                    for path in paths:
                        pb = _bounds(path) if isinstance(path, dict) else None
                        if pb is not None and _overlap(tb, pb):
                            issues.append({"code": "path-covers-text", "frame": state["frame"], "target": target_id})
    return issues


def check_labels(states: list[dict[str, Any]], contracts: list[dict[str, Any]], labels: dict[str, str] | None = None) -> list[dict[str, Any]]:
    """Check names during movement, including interpolated frames."""

    issues: list[dict[str, Any]] = []
    for state in states:
        contract = _contract_at(contracts, float(state["t"]))
        if not contract:
            continue
        visible = _visible_by_id(state)
        for target in contract["targets"]:
            expected = target.get("name", target.get("label")) or (labels or {}).get(str(target["id"]))
            if expected is None:
                continue
            item = visible.get(str(target["id"]))
            if item is None or not str(item.get("text", "")).strip() or str(expected) not in str(item.get("text", "")):
                issues.append({"code": "moving-name-missing", "frame": state["frame"], "t": state["t"],
                               "target": target["id"], "expected": expected})
    return issues


def probe_movie(path: Path, *, width: int, height: int, fps: float, duration: float,
                require_audio: bool = True) -> dict[str, Any]:
    """Read encoded metadata, without treating it as a visual or hearing review."""

    command = ["ffprobe", "-v", "error", "-of", "json", "-show_streams", "-show_format", str(path)]
    try:
        payload = json.loads(subprocess.check_output(command, text=True))
    except (OSError, subprocess.CalledProcessError, json.JSONDecodeError) as exc:
        return {"status": "fail", "issues": [{"code": "ffprobe-failed", "error": str(exc)}]}
    streams = payload.get("streams", [])
    video = next((item for item in streams if item.get("codec_type") == "video"), None)
    audio = next((item for item in streams if item.get("codec_type") == "audio"), None)
    issues = []
    if video is None:
        issues.append({"code": "missing-video-stream"})
    else:
        if int(video.get("width", 0)) != width or int(video.get("height", 0)) != height:
            issues.append({"code": "video-size", "expected": [width, height], "actual": [video.get("width"), video.get("height")]})
        rate = video.get("r_frame_rate", "0/1").split("/")
        actual_fps = float(rate[0]) / float(rate[1]) if len(rate) == 2 and float(rate[1]) else 0
        if abs(actual_fps - fps) > 0.01:
            issues.append({"code": "video-fps", "expected": fps, "actual": actual_fps})
    if require_audio and audio is None:
        issues.append({"code": "missing-audio-stream"})
    actual_duration = _number(payload.get("format", {}).get("duration"))
    if actual_duration is None or abs(actual_duration - duration) > max(2 / max(fps, 1), 0.08):
        issues.append({"code": "video-duration", "expected": duration, "actual": actual_duration})
    return {"status": "pass" if not issues else "fail", "issues": issues,
            "format": payload.get("format", {}), "streams": streams}


def check_subtitle_evidence(path: Path, movie_sha: str) -> list[dict[str, Any]]:
    if not path.is_file():
        return [{"code": "missing-subtitle-evidence", "path": str(path)}]
    try:
        value = load_json(path)
    except (OSError, ValueError) as exc:
        return [{"code": "invalid-subtitle-evidence", "error": str(exc)}]
    issues = []
    if value.get("movie_sha256") != movie_sha:
        issues.append({"code": "subtitle-evidence-stale", "expected": movie_sha, "actual": value.get("movie_sha256")})
    if value.get("method") != "encoded-frame-check":
        issues.append({"code": "subtitle-evidence-method", "actual": value.get("method")})
    frames = value.get("frames", [])
    if not frames:
        issues.append({"code": "subtitle-evidence-empty"})
    for frame in frames:
        if not isinstance(frame, dict):
            issues.append({"code": "subtitle-frame-invalid", "frame": frame})
            continue
        timestamp = _number(frame.get("time"))
        if timestamp is None or not math.isfinite(timestamp) or timestamp < 0:
            issues.append({"code": "subtitle-frame-time-invalid", "frame": frame})
        if not frame.get("path") or not Path(frame["path"]).is_file():
            issues.append({"code": "subtitle-frame-missing", "frame": frame})
            continue
        path = Path(frame["path"])
        if path.stat().st_size == 0:
            issues.append({"code": "subtitle-frame-empty", "path": frame["path"]})
            continue
        actual = sha256(path)
        if frame.get("sha256") != actual:
            issues.append({"code": "subtitle-frame-stale", "path": frame["path"],
                           "expected": frame.get("sha256"), "actual": actual})
    return issues


def check_fingerprints(manifest: Path) -> list[dict[str, Any]]:
    if not manifest.is_file():
        return [{"code": "missing-source-fingerprints", "path": str(manifest)}]
    try:
        value = load_json(manifest)
    except (OSError, ValueError) as exc:
        return [{"code": "invalid-source-fingerprints", "path": str(manifest), "error": str(exc)}]
    issues = []
    if not isinstance(value, dict) or not isinstance(value.get("files"), list) or not value["files"]:
        return [{"code": "empty-source-fingerprints", "path": str(manifest)}]
    for item in value["files"]:
        if not isinstance(item, dict) or not item.get("path") or not item.get("sha256"):
            issues.append({"code": "invalid-source-fingerprint-entry", "entry": item})
            continue
        path = Path(item["path"])
        if not path.is_file():
            issues.append({"code": "source-missing", "path": str(path), "role": item.get("role")})
            continue
        if path.stat().st_size == 0:
            issues.append({"code": "source-empty", "path": str(path), "role": item.get("role")})
            continue
        current = sha256(path)
        if current != item.get("sha256"):
            issues.append({"code": "source-changed", "path": str(path), "role": item.get("role"),
                           "expected": item.get("sha256"), "actual": current})
    return issues


def review_state_files(*, state_path: Path, contract_path: Path, width: int, height: int,
                       fps: float, frame_count: int, safe_area: dict[str, Any] | None = None,
                       subtitle_area: dict[str, Any] | None = None,
                       opacity_threshold: float | None = None,
                       labels: dict[str, str] | None = None) -> dict[str, Any]:
    contracts = normalize_contract(load_json(contract_path))
    states = normalize_states(load_json(state_path))
    issues = check_state_shape(states, fps, frame_count)
    issues.extend(check_focus(states, contracts, width=width, height=height, safe_area=safe_area,
                              subtitle_area=subtitle_area, opacity_threshold=opacity_threshold, labels=labels))
    issues.extend(check_labels(states, contracts, labels))
    return {"status": "pass" if not issues else "fail", "issues": issues,
            "frame_count": len(states), "contract_count": len(contracts)}


def _cli() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--state", required=True, type=Path)
    parser.add_argument("--contract", required=True, type=Path)
    parser.add_argument("--width", required=True, type=int)
    parser.add_argument("--height", required=True, type=int)
    parser.add_argument("--fps", required=True, type=float)
    parser.add_argument("--frames", required=True, type=int)
    parser.add_argument("--opacity-threshold", required=True, type=float,
                        help="可見焦點的最低 opacity，不能從 active 狀態推導")
    parser.add_argument("--safe-area", type=Path, help="內容安全區 JSON（可選；project profile 應明列）")
    parser.add_argument("--subtitle-area", type=Path, help="字幕區 JSON（可選；project profile 應明列）")
    parser.add_argument("--labels", type=Path, help="id→name JSON（可選；project profile 應明列）")
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    try:
        safe_area = load_json(args.safe_area) if args.safe_area else None
        subtitle_area = load_json(args.subtitle_area) if args.subtitle_area else None
        labels = load_json(args.labels) if args.labels else None
        if isinstance(labels, dict) and isinstance(labels.get("labels"), (dict, list)):
            labels = labels["labels"]
        if isinstance(labels, list):
            labels = {str(item["id"]): str(item.get("name", item.get("label", "")))
                      for item in labels if isinstance(item, dict) and item.get("id")}
        result = review_state_files(state_path=args.state, contract_path=args.contract,
                                    width=args.width, height=args.height, fps=args.fps,
                                    frame_count=args.frames, safe_area=safe_area,
                                    subtitle_area=subtitle_area,
                                    opacity_threshold=args.opacity_threshold, labels=labels)
    except (OSError, ValueError, KeyError) as exc:
        result = {"status": "fail", "issues": [{"code": "invalid-input", "error": str(exc)}]}
    write_json(args.output, {"tool": TOOL_VERSION, **result})
    print(json.dumps(result, ensure_ascii=False))
    return 0 if result["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(_cli())
