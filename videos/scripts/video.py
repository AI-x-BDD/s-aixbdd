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
import socketserver
import subprocess
import sys
import tomllib


HOME = Path(__file__).resolve().parents[1]


def run(args, **kwargs):
    return subprocess.run([str(a) for a in args], check=True, **kwargs)


def ffmpeg(*args):
    run(["ffmpeg", "-y", "-hide_banner", "-loglevel", "error", "-xerror", *args])


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


def audio_path(materials, config):
    if config.get("audio_recipe"):
        return HOME / config["output"] / "中間產物" / config["audio"]
    return materials / config["audio"]


def prepare_audio(materials, config):
    """原始音檔唯讀，依已保存的剪接設定重建合成音檔。"""
    if not config.get("audio_recipe"):
        return
    recipe = json.loads((materials / config["audio_recipe"]).read_text())
    original, replacement = [materials / recipe[k] for k in ("original", "replacement")]
    for source in (original, replacement):
        expected = recipe["input_sha256"][source.name]
        if hashlib.sha256(source.read_bytes()).hexdigest() != expected:
            raise ValueError(f"原始配音已改動，請確認剪接設定：{source}")
    target = audio_path(materials, config)
    target.parent.mkdir(parents=True, exist_ok=True)
    start, end = float(recipe["cut_start"]), float(recipe["cut_end"])
    if not 0 <= start < end <= duration(original):
        raise ValueError("配音剪接時間超出原始音檔")
    filters = (f"[0:a]atrim=end={start},asetpts=PTS-STARTPTS[a];"
               "[1:a]asetpts=PTS-STARTPTS[b];"
               f"[0:a]atrim=start={end},asetpts=PTS-STARTPTS[c];"
               "[a][b][c]concat=n=3:v=0:a=1[out]")
    temporary = target.with_name(f".{target.stem}-{os.getpid()}.m4a")
    try:
        ffmpeg("-i", original, "-i", replacement, "-filter_complex", filters,
               "-map", "[out]", "-c:a", "aac", "-b:a", "192k", temporary)
        temporary.replace(target)
    finally:
        temporary.unlink(missing_ok=True)
    print(f"合成配音：{target}", flush=True)


def check(root, materials, content_path, data, out, config):
    if sys.platform != "darwin":
        raise RuntimeError("目前的臨時語音與 SVG 轉圖流程支援 macOS")
    missing = [tool for tool in (["ffmpeg", "ffprobe", "qlmanage"] + ([] if config.get("audio") else ["say"]))
               if not shutil.which(tool)]
    if missing:
        raise RuntimeError("缺少工具：" + ", ".join(missing))
    if config.get("audio"):
        audio, alignment_path = audio_path(materials, config), materials / config["alignment"]
        alignment = json.loads(alignment_path.read_text())
        if alignment["audio_sha256"] != hashlib.sha256(audio.read_bytes()).hexdigest():
            raise ValueError("音檔已改動，請重新對齊")
        if alignment["content_sha256"] != hashlib.sha256(content_path.read_bytes()).hexdigest():
            raise ValueError("製作內容已改動，請重新對齊")
        if [r["text"] for r in alignment["scenes"]] != [r["text"] for r in data["scenes"]]:
            raise ValueError("對齊資料與旁白不一致")
    else:
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


def recorded_timeline(data, materials, config):
    alignment = json.loads((materials / config["alignment"]).read_text())
    fps = data["fps"]
    length = math.ceil(duration(audio_path(materials, config))*fps)/fps
    starts = [0.0]
    for previous, current in zip(alignment["scenes"], alignment["scenes"][1:]):
        # 新畫面稍微領先發聲，但不提早切掉上一段尚在發聲的內容。
        desired = current["speech_start"]-.06
        if desired < previous["speech_end"]:
            desired = (previous["speech_end"]+current["speech_start"])/2
        starts.append(max(0, round(desired*fps)/fps))
    ends = starts[1:] + [length]
    rows = []
    for scene, aligned, start, end in zip(data["scenes"], alignment["scenes"], starts, ends):
        if end <= start:
            raise ValueError("場景時間不遞增，請檢查對齊資料")
        chars = aligned["characters"]
        if not all(start-.08 <= c["start"] <= c["end"] <= end+.08 for c in chars):
            raise ValueError(f"對齊時間超出場景：{scene['title']}")
        rows.append({**scene, "start": round(start,3), "end": round(end,3),
                     "voice_seconds": round(end-start,3), "characters": chars,
                     "last_voiced_end": aligned["speech_end"],
                     "trailing_silence_seconds": round(max(0,end-aligned["speech_end"]),3),
                     "artificial_padding_seconds": 0})
    if not data["min_seconds"] <= length <= data["max_seconds"]:
        raise ValueError(f"正式配音長度 {length:.2f} 秒超出設定範圍")
    return rows


def text_time(row, offset, end=False):
    chars = row.get("characters")
    if chars:
        selected = [c for c in chars if c["offset"] >= offset]
        return selected[0]["end" if end else "start"] if selected else row["end"]
    return row["start"] + row["voice_seconds"] * offset / len(row["text"])


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
        offset = 0
        for chunk in chunks:
            next_offset = offset + len(chunk)
            start = max(row["start"], text_time(row, offset)-.04) if row.get("characters") else text_time(row, offset)
            end = (min(row["end"], text_time(row, next_offset)-.04)
                   if next_offset < len(row["text"]) else row["end"])
            if end <= start:
                raise ValueError("字幕時間沒有前進，請檢查對齊資料")
            cues.append({"start": round(start, 3), "end": round(end, 3), "text": chunk})
            offset = next_offset
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
        times = [round(max(row["start"], text_time(row, row["text"].index(phrase))-.04), 3) for phrase, _ in entries]
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


def documents(root, data, rows, out, config):
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
    visual_descriptions = (json.loads((root / config["materials"] / config["visuals"]).read_text()).get("descriptions", {}) if config.get("visuals") else {})
    md = [f"# {data['title']} 腳本與分鏡\n", f"總長 {rows[-1]['end']:.2f} 秒。\n"]
    for r in rows:
        md += [f"## {r['start']:.2f}–{r['end']:.2f} 秒：{r['title']}\n",
               r["text"] + "\n", "畫面：" + visual_descriptions.get(r["frame"], r.get("visual", "")) + "\n",
               f"[畫面](../中間產物/靜幀/{r['frame']}.png)\n"]
    md.append(("字幕與視覺焦點依語音詞時間對齊；旁白使用 ElevenLabs 正式音檔，仍待聽看確認。\n"
               if config.get("audio") else "字幕與重點框依段內文字比例估時，尚未逐字校時；旁白使用 macOS 臨時系統語音。\n"))
    (out / "腳本與分鏡.md").write_text("\n".join(md))


def export_video(data, rows, focus, out, work, materials, config, visual_states=None):
    count = len(rows)
    if config.get("audio"):
        audio = work / "正式旁白.m4a"
        ffmpeg("-i", audio_path(materials, config), "-vn", "-c:a", "aac", "-b:a", "192k", audio)
    else:
        audio = work / "臨時旁白.mp3"
        args = []
        for i in range(count):
            args += ["-i", work / f"voice-{i}.aiff"]
        filters = [f"[{i}:a]atrim=duration={r['voice_seconds']},asetpts=PTS-STARTPTS[a{i}]" for i, r in enumerate(rows)]
        filters.append("".join(f"[a{i}]" for i in range(count)) + f"concat=n={count}:v=0:a=1[a]")
        ffmpeg(*args, "-filter_complex", ";".join(filters), "-map", "[a]", "-c:a", "libmp3lame",
               "-b:a", "96k", audio)

    def encode(item):
        i, row = item
        if visual_states is not None:
            import visual_motion
            visual_motion.encode(sys.modules[__name__], data, row, visual_states[0][i], visual_states[1], work, work / f"part{i}.mp4")
            return
        boxes = []
        for f in focus:
            if f["start"] >= row["start"] and f["end"] <= row["end"]:
                x, y, w, h = f["box"]
                boxes.append(f"drawbox=x={x}:y={y}:w={w}:h={h}:color=0xBA582D:t=3:enable='between(t,{f['start']-row['start']},{f['end']-row['start']})'")
        filters = ["-vf", ",".join(boxes)] if boxes else []
        ffmpeg("-loop", "1", "-framerate", data["fps"], "-i", work / "靜幀" / f"{row['frame']}.png",
               "-t", row["voice_seconds"], *filters, "-c:v", "libx264", "-preset", "veryfast",
               "-crf", "24", "-pix_fmt", "yuv420p", "-threads", "2", work / f"part{i}.mp4")
    with ThreadPoolExecutor(max_workers=2) as pool:
        list(pool.map(encode, enumerate(rows)))
    # 相對檔名避免跨目錄複製後 concat 清單仍指向舊位置。
    (work / "concat.txt").write_text("".join(f"file 'part{i}.mp4'\n" for i in range(count)))
    ffmpeg("-f", "concat", "-safe", "0", "-i", work / "concat.txt", "-i", audio,
           "-i", out / "字幕.srt", "-map", "0:v", "-map", "1:a", "-map", "2:s", "-c:v", "copy",
           "-c:a", "aac", "-b:a", "192k", "-c:s", "mov_text", "-metadata:s:s:0", "language=zho",
           "-disposition:s:0", "default", "-t", rows[-1]["end"], "-movflags", "+faststart", out / "影片.mp4")


def preview(data, rows, cues, focus, out, config):
    if config.get("visuals"):
        page = (HOME / "templates/preview_video.html").read_text()
        movie = out.parent / "輸出/影片.mp4"
        revision = hashlib.sha256(movie.read_bytes() + page.encode()).hexdigest()[:12]
        gallery = "".join(f'<figure><img src="../中間產物/靜幀/{r["frame"]}.png?v={revision}" alt="{html.escape(r["title"])}"><figcaption>{i+1}. {html.escape(r["title"])}</figcaption></figure>' for i,r in enumerate(rows))
        values = {"__TITLE__": html.escape(data['title']), "__DURATION__":str(round(rows[-1]['end'])), "__TOTAL__":str(rows[-1]['end']), "__REV__":revision,
                  "__ROWS__":json.dumps(rows,ensure_ascii=False), "__CUES__":json.dumps(cues,ensure_ascii=False), "__GALLERY__":gallery}
        for key,value in values.items():
            page = page.replace(key,value)
        (out/'預覽.html').write_text(page)
        return
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
    audio = out.parent / "中間產物" / ("正式旁白.m4a" if config.get("audio") else "臨時旁白.mp3")
    mime = "audio/mp4" if config.get("audio") else "audio/mpeg"
    page = page.replace('src="臨時旁白.mp3"', f'src="data:{mime};base64,' + base64.b64encode(audio.read_bytes()).decode() + '"')
    if config.get("audio"):
        page = page.replace("靜幀＋臨時系統語音", "ElevenLabs 正式配音・對齊預覽")
        page = page.replace("聲音為本機 Meijia 臨時語音；字幕為段內估時稿。", "使用正式配音；字幕與重點框依語音詞時間對齊，待聽看確認。")
    page = page.replace('靜幀/', '../中間產物/靜幀/')
    page = page.replace('href="計時預覽.mp4"', 'href="../輸出/影片.mp4"')
    (out / "預覽.html").write_text(page)


def render(root, materials, content_path, data, out, config):
    prepare_audio(materials, config)
    check(root, materials, content_path, data, out, config)
    work, review, export = out / "中間產物", out / "預覽", out / "輸出"
    raster = work / "轉圖"
    for folder in (work, review, export, raster):
        folder.mkdir(parents=True, exist_ok=True)
    inputs = [content_path] + sorted((materials / config["slides"]).glob("*.svg"))
    if config.get("audio"):
        inputs += [audio_path(materials, config), materials / config["alignment"]]
        if config.get("audio_recipe"):
            recipe = json.loads((materials / config["audio_recipe"]).read_text())
            inputs += [materials / config["audio_recipe"], materials / recipe["original"], materials / recipe["replacement"]]
    if config.get("visuals"):
        inputs.append(materials / config["visuals"])
    before = {str(p): hashlib.sha256(p.read_bytes()).hexdigest() for p in inputs}
    rows = recorded_timeline(data, materials, config) if config.get("audio") else audio_timeline(data, work)
    (review / "時間軸.json").write_text(json.dumps(rows, ensure_ascii=False, indent=2) + "\n")
    cues, focus = captions(rows, export), focus_timeline(data, rows)
    frames(materials, config, rows, work, raster)
    documents(root, data, rows, review, config)
    visual_states = None
    if config.get("visuals"):
        import visual_motion
        visual_states = visual_motion.prepare(sys.modules[__name__], materials, config, data, rows, work)
    export_video(data, rows, focus, export, work, materials, config, visual_states)
    preview(data, rows, cues, focus, review, config)
    length = duration(export / "影片.mp4")
    events = silence(export / "影片.mp4", .5)
    if not data["min_seconds"] <= length <= data["max_seconds"]:
        raise ValueError(f"輸出片長不符：{length}")
    if any(before[str(p)] != hashlib.sha256(p.read_bytes()).hexdigest() for p in inputs):
        raise RuntimeError("來源素材在製作期間發生變動")
    report = {"duration_seconds": length, "added_padding_seconds": 0,
              "silences_at_least_half_second": events,
              "maximum_scene_trailing_silence_seconds": max(r["trailing_silence_seconds"] for r in rows),
              "source_files_unchanged": True,
              "audio_source": config.get("audio", "macOS say"),
              "subtitle_alignment": "whisper-word-timestamps" if config.get("audio") else "estimated",
              "visual_renderer": "semantic-svg-states" if config.get("visuals") else "legacy-focus-box",
              "preview_matches_export": bool(config.get("visuals"))}
    (review / "節奏檢查.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n")
    (out / "來源指紋.json").write_text(json.dumps(before, ensure_ascii=False, indent=2)+"\n")
    print(f"輸出完成：{export / '影片.mp4'}（{length:.2f} 秒）", flush=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", default="projects/ch2-workflow-test/project.toml")
    parser.add_argument("--source-root", help="外部素材所在的大專案根目錄")
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("check", help="檢查環境與素材")
    commands.add_parser("setup", help="安裝 profile 指定的渲染依賴")
    commands.add_parser("prepare-audio", help="從原始音檔重建剪接配音")
    commands.add_parser("render", help="重新製作旁白、字幕、預覽與 MP4")
    serve = commands.add_parser("serve", help="啟動本機預覽，不重新製作影片")
    serve.add_argument("--port", type=int, default=60071)
    args = parser.parse_args()
    state = load(args)
    if args.command == "setup":
        if state[5].get("setup_script"):
            run([sys.executable, HOME/state[5]["setup_script"]])
    elif args.command == "prepare-audio":
        prepare_audio(state[1], state[5])
    elif args.command == "check":
        check(*state)
    elif args.command == "render":
        if state[5].get("renderer_script"):
            run([sys.executable, HOME/state[5]["renderer_script"], "--config", args.config,
                 *(["--source-root", args.source_root] if args.source_root else [])])
        else:
            render(*state)
            if state[5].get("postprocess"):
                run([sys.executable, HOME/state[5]["postprocess"], "--config", args.config,
                     *(["--source-root", args.source_root] if args.source_root else [])])
    else:
        out = HOME/state[5]["preview_root"] if state[5].get("preview_root") else state[4]
        entry = state[5].get("preview_entry", "預覽/預覽.html")
        if not (out / entry).is_file():
            parser.error("請先執行 render")
        handler = partial(http.server.SimpleHTTPRequestHandler, directory=str(out))
        # 本機固定 IP 不需反查主機名稱，避免 macOS DNS 延遲阻塞預覽啟動。
        with http.server.ThreadingHTTPServer(("127.0.0.1", args.port), handler,
                                             bind_and_activate=False) as server:
            socketserver.TCPServer.server_bind(server)
            server.server_name, server.server_port = server.server_address
            server.server_activate()
            print(f"預覽：http://127.0.0.1:{server.server_port}/{entry}", flush=True)
            server.serve_forever()


if __name__ == "__main__":
    main()
