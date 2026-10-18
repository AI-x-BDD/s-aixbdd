#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""固定風格庫的離線檢查、目錄與預覽建置；不搜尋、不更新上游。

check/list/gallery 僅需標準庫。render 需以已裝 playwright 的 Python 執行，
以及 ffmpeg、ffprobe、Playwright Chromium。只在 macOS 實跑。
"""
from __future__ import annotations

import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
import hashlib
import html
import json
import os
from pathlib import Path
import subprocess
import sys


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def write(path: Path, data) -> None:
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def safe(root: Path, name: str) -> Path:
    path = (root / name).resolve()
    if not path.is_relative_to(root.resolve()):
        raise ValueError(f"路徑超出工具包：{name}")
    return path


def check(library: Path, selection: Path | None = None) -> dict:
    data = read(library / "catalog.json")
    lock = read(library / "upstream-lock.json")
    videos = library.parent
    upstream = safe(videos, str(Path("style-library") / lock["root"]))
    issues = []
    if data.get("upstream_revision") != lock["revision"]:
        issues.append("目錄與來源鎖定版本不同")
    actual = {p.relative_to(upstream).as_posix() for p in upstream.rglob("*") if p.is_file()}
    for name in sorted(actual - set(lock["files"])):
        issues.append(f"上游出現未鎖定檔案：{name}")
    for name, expected in lock["files"].items():
        path = safe(upstream, name)
        if not path.is_file() or digest(path) != expected:
            issues.append(f"上游檔案缺失或改動：{name}")
    ids = [e["id"] for e in data["entries"]]
    if len(ids) != len(set(ids)):
        issues.append("風格 ID 重複")
    for entry in data["entries"]:
        for key in ("card", "implementation"):
            if not safe(videos, entry[key]).is_file():
                issues.append(f"{entry['id']} 缺少 {key}")
        if entry["source_revision"] != lock["revision"]:
            issues.append(f"{entry['id']} 來源版本不符")
        blocked = entry.get("status") == "blocked-needs-assets" and not entry.get("selectable") and entry.get("blocked_reason")
        for key in (() if blocked else ("preview", "poster")):
            path = safe(library, entry[key])
            if not path.is_file() or digest(path) != entry.get(key + "_sha256"):
                issues.append(f"{entry['id']} 缺少或使用過期 {key}")
        if not blocked and entry.get("status") != "preview-rendered":
            issues.append(f"{entry['id']} 尚未完成預覽建置")
        if entry.get("render_mode") == "spec" and not blocked and not entry.get("spec_sha256"):
            issues.append(f"{entry['id']} 缺少預覽 spec 來源雜湊")
        if entry.get("spec_sha256"):
            path = safe(library, entry["spec"])
            if not path.is_file() or digest(path) != entry["spec_sha256"]:
                issues.append(f"{entry['id']} 預覽 spec 已過期")
    # 固定庫的已承諾覆蓋範圍；研究卡不計入這個數量。
    counts = {k: sum(e["category"] == k for e in data["entries"]) for k in ("explainer", "art")}
    selectable_counts = {k: sum(e["category"] == k and bool(e.get("selectable")) for e in data["entries"]) for k in counts}
    if selectable_counts["explainer"] < 7 or selectable_counts["art"] < 34:
        issues.append("固定風格庫可選覆蓋不足：應有至少 7 種解說形式、34 種藝術方向")
    if selection is not None:
        selected = read(selection)
        if not isinstance(selected, dict):
            raise ValueError("選用紀錄必須是 JSON object")
        if selected.get("catalog_sha256") != digest(library / "catalog.json"):
            issues.append("風格選用紀錄的目錄版本過期")
        known = {e["id"]: e for e in data["entries"]}
        chosen = selected.get("choices", [])
        reuse = selected.get("reuse")
        if not isinstance(chosen, list) or any(not isinstance(item, dict) for item in chosen):
            raise ValueError("choices 必須是 object 陣列")
        if reuse:
            if not isinstance(reuse, dict) or chosen:
                raise ValueError("reuse 必須是 object，且不得和 choices 混用")
            evidence = safe(selection.parent, reuse.get("evidence", ""))
            if not evidence.is_file() or digest(evidence) != reuse.get("sha256"):
                issues.append("沿用方向缺少有效的原始確認證據")
            if not str(reuse.get("adaptation", "")).strip():
                issues.append("沿用方向缺少本片適配方法")
        if not chosen and not reuse:
            issues.append("未選定風格庫項目")
        for item in chosen:
            entry = known.get(item.get("id"))
            if entry is None or not entry.get("selectable"):
                issues.append(f"不可選用的風格：{item.get('id')}")
            if not str(item.get("content_reason", "")).strip() or not str(item.get("adaptation", "")).strip():
                issues.append("選用項目缺少內容依據或新題材改編方法")
    result = {"status": "fail" if issues else "pass", "revision": lock["revision"],
              "catalog_sha256": digest(library / "catalog.json"), "counts": counts,
              "selectable_counts": selectable_counts,
              "selectable": sum(e["selectable"] for e in data["entries"]), "issues": issues}
    return result


def render_one(library: Path, entry: dict, art_seconds: float) -> dict:
    videos = library.parent
    upstream = (library / read(library / "upstream-lock.json")["root"]).resolve()
    renderer = upstream / "scripts/engine/render.py"
    preview = library / entry["preview"]
    preview.parent.mkdir(exist_ok=True)
    command = [sys.executable, str(renderer)]
    if entry["render_mode"] == "solo":
        command += ["--film", "gallery", "--solo", entry["id"], "--from", "0", "--to", str(art_seconds),
                    "--fps", "30", "--no-counter"]
    else:
        spec = read(upstream / "scripts/engine/examples" / (entry["id"] + ".json"))
        # 使用上游原範例，僅將素材路徑轉成庫內相對路徑，保留可重建來源。
        spec_path = library / entry["spec"]
        spec_path.parent.mkdir(exist_ok=True)
        def paths(node):
            if isinstance(node, dict):
                for key, value in list(node.items()):
                    if key == "image" and isinstance(value, str) and not value.startswith(("http:", "https:")):
                        node[key] = os.path.relpath(upstream / "scripts/engine/examples" / value, spec_path.parent)
                    else:
                        paths(value)
            elif isinstance(node, list):
                for item in node:
                    paths(item)
        paths(spec)
        write(spec_path, spec)
        command += ["--spec", str(spec_path)]
    command += ["--out", str(preview)]
    logs = library / "render-logs"
    logs.mkdir(exist_ok=True)
    with (logs / (entry["id"] + ".log")).open("w", encoding="utf-8") as log:
        subprocess.run(command, stdout=log, stderr=subprocess.STDOUT, check=True, timeout=300,
                       env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"})
    probe = json.loads(subprocess.check_output(["ffprobe", "-v", "error", "-show_streams", "-show_format", "-of", "json", str(preview)]))
    stream = next(s for s in probe["streams"] if s["codec_type"] == "video")
    duration = float(probe["format"]["duration"])
    subprocess.run(["ffmpeg", "-v", "error", "-i", str(preview), "-f", "null", "-"], check=True, timeout=60)
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-ss", str(min(duration * .6, duration - .1)),
                    "-i", str(preview), "-frames:v", "1", str(library / entry["poster"])], check=True, timeout=60)
    return {**entry, **({"spec_sha256": digest(library / entry["spec"])} if entry.get("spec") else {}),
            "status": "preview-rendered", "preview_sha256": digest(preview),
            "poster_sha256": digest(library / entry["poster"]), "duration": duration,
            "width": stream["width"], "height": stream["height"], "frames": int(stream["nb_frames"]),
            "validation": "實際渲染、完整解碼及規格確認；風格示範，非新題材內容驗收"}


def gallery(library: Path) -> None:
    data = read(library / "catalog.json")
    esc = html.escape
    cards = []
    for e in sorted(data["entries"], key=lambda e: (e["category"] != "explainer", e["id"])):
        label = "解說形式" if e["category"] == "explainer" else "藝術風格"
        player = (f'<p><strong>不可使用：{esc(e["blocked_reason"])}</strong></p>' if e.get("status") == "blocked-needs-assets" else
                  f'<video controls preload="none" poster="{esc(e["poster"])}" src="{esc(e["preview"])}"></video>')
        cards.append(f'''<article data-category="{e['category']}"><h2>{esc(e['name'])}</h2>
<p class="tag">{label} · {esc(e['id'])} · {'可作候選' if e['selectable'] else '不可選用（見限制）'}</p>
{player}
<p><b>適用：</b>{esc(e['fit'])}</p><p><b>用法：</b>{esc(e.get('adaptation_kind', '依規範製作新內容'))}</p><p><b>特徵（來源原文）：</b>{esc(e['features'])}</p>
<details><summary>限制與來源</summary><p>{esc(e['limits'])}</p>
<p>{esc(e.get('validation', '尚未完成預覽'))}</p><p>上游評價：{esc(e.get('source_quality', '未評星'))}；不是本專案品質驗收。</p>
<a href="../{esc(e['card'])}">原始風格規範</a> · <a download href="{esc(e['preview'])}">下載示範 MP4</a></details></article>''')
    page = '''<!doctype html><html lang="zh-Hant"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>影片固定風格庫</title><style>:root{color-scheme:light}body{margin:0;background:#f5f2eb;color:#252825;font:16px/1.65 system-ui}header,main{max-width:1400px;margin:auto;padding:24px}h1{font-size:36px;margin:0}header p{max-width:1000px}.controls{display:flex;gap:12px;flex-wrap:wrap}input,select{font:inherit;padding:10px;border:1px solid #a9ada5;border-radius:6px}main{display:grid;grid-template-columns:repeat(auto-fit,minmax(min(100%,350px),1fr));gap:22px}article{background:#fff;padding:20px;border:1px solid #d7d9d2;border-radius:10px}article[hidden]{display:none}h2{font-size:23px;margin:0}.tag{color:#586456;font-size:14px}video{width:100%;aspect-ratio:16/9;background:#222}a{color:#275b41}details{border-top:1px solid #ddd;padding-top:12px}summary{cursor:pointer}small{color:#596056}</style>
<header><h1>影片固定風格庫</h1><p><strong>7 種可用解說形式＋35 種藝術風格預覽。</strong>先按內容篩選，再用新題材製作代表片段；不是每次上網找風格。共 43 個目錄項，42 個有影片；角色故事缺素材，保留限制說明。研究配方未列入可選庫。</p>
<p>以下是原庫的無聲示範，藝術片段 3 秒；用來比較視覺語言，不是正式影片。配音、字幕與新題材適配仍依製作流程驗證。角色僅限上游示範，不得搬入新片。來源固定版本保留在專案內。</p>
<div class="controls"><input type="search" id="search" placeholder="搜尋名稱、特徵或適用內容" aria-label="搜尋風格"><select id="category" aria-label="風格分類"><option value="all">全部</option><option value="explainer">解說形式（7 可用＋1 缺素材）</option><option value="art">藝術風格（35）</option></select></div><p id="count"></p><small>來源：huashu-art-motion · 固定 revision ''' + esc(data["upstream_revision"][:12]) + ''' · <a href="README.md">範圍、授權與重建說明</a></small></header><main>''' + "\n".join(cards) + '''</main><script>
const search=document.querySelector('#search'),category=document.querySelector('#category'),cards=[...document.querySelectorAll('article')];
function filter(){let n=0;for(const c of cards){c.hidden=!(category.value==='all'||c.dataset.category===category.value)||!c.textContent.toLowerCase().includes(search.value.toLowerCase());if(!c.hidden)n++}document.querySelector('#count').textContent=`顯示 ${n} / ${cards.length} 項`}
search.addEventListener('input',filter);category.addEventListener('change',filter);filter();
document.querySelectorAll('video').forEach(v=>v.addEventListener('play',()=>document.querySelectorAll('video').forEach(o=>{if(o!==v)o.pause()})));
</script></html>'''
    (library / "index.html").write_text(page, encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("check", "list", "gallery", "render"))
    parser.add_argument("--library", type=Path, required=True)
    parser.add_argument("--selection", type=Path, help="本片選用紀錄 JSON，check 時核對")
    parser.add_argument("--ids", nargs="*", help="render 指定項目，省略為全部")
    parser.add_argument("--workers", type=int, default=2)
    parser.add_argument("--art-seconds", type=float, default=3)
    args = parser.parse_args()
    library = args.library.resolve()
    try:
        data = read(library / "catalog.json")
        if args.command == "check":
            result = check(library, args.selection)
            print(json.dumps(result, ensure_ascii=False, indent=2))
            return int(result["status"] != "pass")
        if args.command == "list":
            print(json.dumps(data, ensure_ascii=False, indent=2))
        elif args.command == "render":
            if not 1 <= args.workers <= 4 or args.art_seconds <= 0:
                raise ValueError("workers 必須為 1–4，片段秒數必須大於零")
            entries = [e for e in data["entries"] if (args.ids is None and e.get("status") != "blocked-needs-assets")
                       or (args.ids is not None and e["id"] in args.ids)]
            if args.ids is not None and (set(args.ids) != {e["id"] for e in entries}
                                        or any(e.get("status") == "blocked-needs-assets" for e in entries)):
                raise ValueError("指定了不存在或缺少素材而停用的風格 ID")
            failures = []
            with ThreadPoolExecutor(max_workers=args.workers) as pool:
                futures = {pool.submit(render_one, library, e, args.art_seconds): e for e in entries}
                for future in as_completed(futures):
                    entry = futures[future]
                    try:
                        result = future.result()
                        data["entries"][data["entries"].index(entry)] = result
                        print("rendered " + entry["id"], flush=True)
                    except Exception as exc:
                        failures.append(f"{entry['id']}: {exc}")
                        entry["status"] = "render-failed"
                        print(failures[-1], file=sys.stderr, flush=True)
                    write(library / "catalog.json", data)
            gallery(library)
            if failures:
                return 1
        else:
            gallery(library)
        return 0
    except (OSError, ValueError, KeyError, subprocess.SubprocessError) as exc:
        print(f"style-library: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
