"""本機影片製作入口；素材唯讀，所有衍生檔寫入 videos/build/。"""

import argparse
import base64
from concurrent.futures import ThreadPoolExecutor
from functools import partial
import hashlib
import html
import http.server
import json
import math
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tomllib


HOME = Path(__file__).resolve().parents[1]


def run(args, **kwargs):
    return subprocess.run([str(a) for a in args], check=True, **kwargs)


def ffmpeg(*args):
    run(["ffmpeg", "-y", "-hide_banner", "-loglevel", "error", *args])


def duration(path):
    return float(subprocess.check_output([
        "ffprobe", "-v", "error", "-show_entries", "format=duration",
        "-of", "csv=p=0", str(path),
    ], text=True).strip())


def silence(path, minimum):
    result = run([
        "ffmpeg", "-hide_banner", "-i", path, "-vn", "-af",
        f"silencedetect=noise=-40dB:d={minimum}", "-f", "null", "-",
    ], capture_output=True, text=True)
    return [(k, float(v)) for k, v in re.findall(
        r"silence_(start|end): ([0-9.]+)", result.stderr
    )]


def load(args):
    config_path = Path(args.config).expanduser()
    if not config_path.is_absolute():
        config_path = HOME / config_path
    config = tomllib.loads(config_path.read_text())
    root = (Path(args.source_root).expanduser().resolve() if args.source_root
            else (HOME / config["source_root"]).resolve())
    materials = (root / config["materials"]).resolve()
    content_path = materials / config["content"]
    data = json.loads(content_path.read_text())
    out = (HOME / config["output"]).resolve()
    if not out.is_relative_to(HOME / "build"):
        raise ValueError("output 必須位於 videos/build/，避免覆寫素材")
    return root, materials, content_path, data, out, config


def check(root, materials, content_path, data, out, config):
    if sys.platform != "darwin":
        raise RuntimeError("目前的臨時語音與 SVG 轉圖流程支援 macOS")
    missing = [tool for tool in ["ffmpeg", "ffprobe", "say", "qlmanage"]
               if not shutil.which(tool)]
    if missing:
        raise RuntimeError("缺少工具：" + ", ".join(missing))
    voices = subprocess.check_output(["say", "-v", "?"], text=True)
    if not any(line.split()[0] == data["voice"] for line in voices.splitlines() if line):
        raise RuntimeError(f"macOS 尚未安裝語音 {data['voice']}")
    for scene in data["scenes"]:
        if not scene["text"].strip():
            raise ValueError("旁白不可為空")
        path = materials / config["slides"] / f"{scene['frame']}.svg"
        if not path.is_file():
            raise FileNotFoundError(path)
    for claim in data.get("claims", []):
        (root / claim["path"]).read_text()
    for focus in data.get("focus", []):
        scene = data["scenes"][focus["scene"]]
        positions = [scene["text"].index(phrase) for phrase, _ in focus["entries"]]
        if positions != sorted(positions):
            raise ValueError("畫面強調順序與旁白不一致")
    print(f"環境與素材檢查通過：{content_path}", flush=True)


def audio_timeline(data, work):
    rows, cursor = [], 0.0
    fps = data["fps"]
    for i, scene in enumerate(data["scenes"]):
        text_file, wav = work / f"voice-{i}.txt", work / f"voice-{i}.aiff"
        text_file.write_text(scene["text"])
        # 每次重建語音，避免語音或語速設定改動後誤用舊快取。
        run(["say", "-v", data["voice"], "-r", data["speech_rate"],
             "-f", text_file, "-o", wav])
        raw, voiced_end = duration(wav), None
        events = silence(wav, 0.08)
        if len(events) >= 2 and events[-1][0] == "end" and abs(events[-1][1] - raw) < .002:
            voiced_end = events[-2][1] if events[-2][0] == "start" else raw
        voiced_end = raw if voiced_end is None else voiced_end
        length = math.ceil((voiced_end + .12) * fps - 1e-8) / fps
        if length > raw:
            length = math.floor(raw * fps) / fps
        end = round(cursor + length, 3)
        rows.append({**scene, "start": cursor, "end": end, "voice_seconds": length,
                     "raw_voice_seconds": raw, "last_voiced_end": voiced_end,
                     "trailing_silence_seconds": round(length - voiced_end, 3),
                     "artificial_padding_seconds": 0})
        cursor = end
        print(f"{scene['title']}：{length:.2f} 秒", flush=True)
    if not data["min_seconds"] <= cursor <= data["max_seconds"]:
        raise ValueError(f"片長 {cursor:.2f} 秒超出設定範圍；請調整內容")
    return rows


def stamp(t, comma=False):
    ms = round(t * 1000)
    h, ms = divmod(ms, 3600000)
    m, ms = divmod(ms, 60000)
    s, ms = divmod(ms, 1000)
    return f"{h:02}:{m:02}:{s:02}{',' if comma else '.'}{ms:03}"


def captions(rows, out):
    cues = []
    for row in rows:
        chunks = []
        for phrase in filter(None, re.split(r"(?<=[。；])", row["text"])):
            if len(phrase) <= 37:
                chunks.append(phrase)
                continue
            buf = ""
            for item in filter(None, re.split(r"(?<=[，、])", phrase)):
                if len(buf + item) > 37 and buf:
                    chunks.append(buf)
                    buf = ""
                buf += item
            if buf:
                chunks.append(buf)
        total, t = sum(map(len, chunks)), row["start"]
        for chunk in chunks:
            end = t + row["voice_seconds"] * len(chunk) / total
            cues.append({"start": round(t, 3), "end": round(end, 3), "text": chunk})
            t = end
    (out / "字幕.vtt").write_text("WEBVTT\n\n" + "\n\n".join(
        f"{stamp(c['start'])} --> {stamp(c['end'])}\n{c['text']}" for c in cues) + "\n")
    (out / "字幕.srt").write_text("\n\n".join(
        f"{i+1}\n{stamp(c['start'], True)} --> {stamp(c['end'], True)}\n{c['text']}"
        for i, c in enumerate(cues)) + "\n")
    return cues


def focus_timeline(data, rows):
    cues = []
    for group in data.get("focus", []):
        row = rows[group["scene"]]
        entries = group["entries"]
        times = [round(row["start"] + row["voice_seconds"] * row["text"].index(phrase)
                       / len(row["text"]), 3) for phrase, _ in entries]
        for i, (_, box) in enumerate(entries):
            cues.append({"start": times[i], "end": times[i+1] if i+1 < len(times)
                         else row["end"], "box": box})
    return cues


def frames(materials, config, rows, out, work):
    (out / "靜幀").mkdir(exist_ok=True)
    for frame in sorted({r["frame"] for r in rows}):
        source = materials / config["slides"] / f"{frame}.svg"
        # Quick Look 先用正方形畫布，避免其縮圖裁切 16:9 SVG。
        svg = source.read_text().replace('height="900" viewBox="0 0 1600 900"',
                                         'height="1600" viewBox="0 0 1600 1600"')
        svg = svg.replace('<g font-family=', '<g transform="translate(0,350)"><g font-family=', 1)
        svg = svg.replace("</svg>", "</g></svg>")
        wrapper = work / f"frame{frame}.svg"
        wrapper.write_text(svg)
        run(["qlmanage", "-t", "-s", "1600", "-o", work, wrapper], stdout=subprocess.DEVNULL)
        ffmpeg("-i", str(wrapper) + ".png", "-vf", "crop=1600:900:0:350",
               "-frames:v", "1", out / "靜幀" / f"{frame}.png")


def documents(root, data, rows, out):
    evidence = ["# 影片證據對照\n"]
    for claim in data.get("claims", []):
        path = root / claim["path"]
        lines = path.read_text().splitlines()
        start = next((i+1 for i, line in enumerate(lines) if claim["start"] in line), 1) if claim["start"] else 1
        end = next((i for i, line in enumerate(lines[start:], start) if claim["end"] in line), len(lines)) if claim["end"] else len(lines)
        evidence.append(f"- **{claim['id']}**：{claim['claim']}。[來源]({os.path.relpath(path, out)})，第 {start}–{end} 行。")
    evidence += ["\n| 時間 | 場景 | 來源 |", "| --- | --- | --- |"]
    evidence += [f"| {r['start']:.2f}–{r['end']:.2f} 秒 | {r['title']} | {r.get('evidence', '')} |" for r in rows]
    (out / "證據對照.md").write_text("\n".join(evidence) + "\n")
    md = [f"# {data['title']} 腳本與分鏡\n", f"總長 {rows[-1]['end']:.2f} 秒。\n"]
    for r in rows:
        md += [f"## {r['start']:.2f}–{r['end']:.2f} 秒：{r['title']}\n",
               r["text"] + "\n", "畫面：" + r.get("visual", "") + "\n",
               f"[畫面](靜幀/{r['frame']}.png)\n"]
    md.append("字幕與重點框依段內文字比例估時，尚未逐字校時；旁白使用 macOS 臨時系統語音。\n")
    (out / "腳本與分鏡.md").write_text("\n".join(md))


def export_video(data, rows, focus, out, work):
    count = len(rows)
    args = []
    for i in range(count):
        args += ["-i", work / f"voice-{i}.aiff"]
    filters = [f"[{i}:a]atrim=duration={r['voice_seconds']},asetpts=PTS-STARTPTS[a{i}]" for i, r in enumerate(rows)]
    filters.append("".join(f"[a{i}]" for i in range(count)) + f"concat=n={count}:v=0:a=1[a]")
    ffmpeg(*args, "-filter_complex", ";".join(filters), "-map", "[a]", "-c:a", "libmp3lame",
           "-b:a", "96k", out / "臨時旁白.mp3")

    def encode(item):
        i, row = item
        boxes = []
        for f in focus:
            if f["start"] >= row["start"] and f["end"] <= row["end"]:
                x, y, w, h = f["box"]
                boxes.append(f"drawbox=x={x}:y={y}:w={w}:h={h}:color=0xBA582D:t=3:enable='between(t,{f['start']-row['start']},{f['end']-row['start']})'")
        filters = ["-vf", ",".join(boxes)] if boxes else []
        ffmpeg("-loop", "1", "-framerate", data["fps"], "-i", out / "靜幀" / f"{row['frame']}.png",
               "-t", row["voice_seconds"], *filters, "-c:v", "libx264", "-preset", "veryfast",
               "-crf", "24", "-pix_fmt", "yuv420p", "-threads", "2", work / f"part{i}.mp4")
    with ThreadPoolExecutor(max_workers=2) as pool:
        list(pool.map(encode, enumerate(rows)))
    # 相對檔名避免跨目錄複製後 concat 清單仍指向舊位置。
    (work / "concat.txt").write_text("".join(f"file 'part{i}.mp4'\n" for i in range(count)))
    ffmpeg("-f", "concat", "-safe", "0", "-i", work / "concat.txt", "-i", out / "臨時旁白.mp3",
           "-i", out / "字幕.srt", "-map", "0:v", "-map", "1:a", "-map", "2:s", "-c:v", "copy",
           "-c:a", "aac", "-b:a", "96k", "-c:s", "mov_text", "-metadata:s:s:0", "language=zho",
           "-disposition:s:0", "default", "-t", rows[-1]["end"], "-movflags", "+faststart", out / "計時預覽.mp4")


def preview(data, rows, cues, focus, out):
    page = (HOME / "templates/preview.html").read_text()
    gallery = "".join(f'<figure><a href="靜幀/{r["frame"]}.png"><img src="靜幀/{r["frame"]}.png" alt="{html.escape(r["title"])}"></a><figcaption>{html.escape(r["title"])}</figcaption></figure>'
                      for i, r in enumerate(rows) if r["frame"] not in {v["frame"] for v in rows[:i]})
    length = rows[-1]["end"]
    replacements = {"__TITLE__": html.escape(data["title"]), "__DURATION__": str(round(length)),
                    "__TOTAL__": str(length), "__CLOCK__": f"{int(length)//60}:{int(length)%60:02}",
                    "__GALLERY__": gallery, "__ROWS__": json.dumps(rows, ensure_ascii=False),
                    "__CUES__": json.dumps(cues, ensure_ascii=False), "__FOCUS__": json.dumps(focus)}
    for key, value in replacements.items():
        page = page.replace(key, value)
    page = page.replace('src="臨時旁白.mp3"', 'src="data:audio/mpeg;base64,' + base64.b64encode((out / "臨時旁白.mp3").read_bytes()).decode() + '"')
    (out / "預覽.html").write_text(page)


def render(root, materials, content_path, data, out, config):
    check(root, materials, content_path, data, out, config)
    work = out / "work"
    work.mkdir(parents=True, exist_ok=True)
    inputs = [content_path] + sorted((materials / config["slides"]).glob("*.svg"))
    before = {str(p): hashlib.sha256(p.read_bytes()).hexdigest() for p in inputs}
    rows = audio_timeline(data, work)
    (out / "時間軸.json").write_text(json.dumps(rows, ensure_ascii=False, indent=2) + "\n")
    cues, focus = captions(rows, out), focus_timeline(data, rows)
    frames(materials, config, rows, out, work)
    documents(root, data, rows, out)
    export_video(data, rows, focus, out, work)
    preview(data, rows, cues, focus, out)
    length = duration(out / "計時預覽.mp4")
    events = silence(out / "計時預覽.mp4", .5)
    if not data["min_seconds"] <= length <= data["max_seconds"]:
        raise ValueError(f"輸出片長不符：{length}")
    if any(before[str(p)] != hashlib.sha256(p.read_bytes()).hexdigest() for p in inputs):
        raise RuntimeError("來源素材在製作期間發生變動")
    report = {"duration_seconds": length, "added_padding_seconds": 0,
              "silences_at_least_half_second": events,
              "maximum_scene_trailing_silence_seconds": max(r["trailing_silence_seconds"] for r in rows),
              "source_files_unchanged": True, "subtitle_alignment": "estimated"}
    (out / "節奏檢查.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n")
    print(f"輸出完成：{out / '計時預覽.mp4'}（{length:.2f} 秒）", flush=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", default="projects/ch2-skill-engineering/project.toml")
    parser.add_argument("--source-root", help="外部素材所在的大專案根目錄")
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("check", help="檢查環境與素材")
    commands.add_parser("render", help="重新製作旁白、字幕、預覽與 MP4")
    serve = commands.add_parser("serve", help="啟動本機預覽，不重新製作影片")
    serve.add_argument("--port", type=int, default=60070)
    args = parser.parse_args()
    state = load(args)
    if args.command == "check":
        check(*state)
    elif args.command == "render":
        render(*state)
    else:
        out = state[4]
        if not (out / "預覽.html").is_file():
            parser.error("請先執行 render")
        handler = partial(http.server.SimpleHTTPRequestHandler, directory=str(out))
        server = http.server.ThreadingHTTPServer(("127.0.0.1", args.port), handler)
        print(f"預覽：http://127.0.0.1:{server.server_port}/預覽.html", flush=True)
        server.serve_forever()


if __name__ == "__main__":
    main()
