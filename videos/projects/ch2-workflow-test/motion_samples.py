"""CH2 動態候選：準備 Remotion 輸入、渲染代表片段、擷取基準並產生比較頁。

從 repo 根目錄執行：videos/.venv/bin/python videos/projects/ch2-workflow-test/motion_samples.py
只讀正式 B 成片、字幕、對齊與時間軸；輸出全在 videos/build/ch2-workflow-test/動態提案/。
"""
from pathlib import Path
from html import escape
import hashlib
import json
import re
import shutil
import subprocess
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
VIDEOS = ROOT/'videos'
MOTION = VIDEOS/'motion'
PUBLIC = MOTION/'public'
FORMAL = VIDEOS/'build/ch2-workflow-test/正式版'
OUT = VIDEOS/'build/ch2-workflow-test/動態提案'
ALIGN = ROOT/'docs/過程/CH2/影片/製作來源/配音/對齊/對齊.json'
# 原配音直接取自正式 B 成片的音訊流（copy）；若保留了修訂前原版，verify() 另核對兩者音訊流一致。
AUDIO_SOURCE = FORMAL/'輸出/影片.mp4'
ORIGINAL = VIDEOS/'build/ch2-workflow-test/參考/20261017-B原版/影片.mp4'
FPS = 25
SEGMENTS = {'02': (11.16, 38.80), '07': (53.04, 70.44)}
VARIANTS = {'focus': 'M1 連續焦點', 'motion': 'M2 動態敘事'}
sys.path.insert(0, str(HERE))
from burn_subtitles import seconds, wrap  # 與正式燒錄字幕相同的斷行規則


def run(*args, **kw):
    return subprocess.run([str(a) for a in args], check=True, **kw)


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def duration(path):
    return float(subprocess.check_output(['ffprobe', '-v', 'error', '-show_entries', 'format=duration',
                                          '-of', 'default=nw=1:nk=1', str(path)], text=True))


def prepare():
    """保留九幕輸入，避免重建歷史比較時破壞 Full-Motion 所需資料。"""
    from argparse import Namespace
    from prepare_motion import prepare as prepare_full
    prepare_full(Namespace(config='projects/ch2-workflow-test/project.toml', source_root=None))
    source = json.loads((PUBLIC/'來源.json').read_text())
    source.update(audio_source=str(AUDIO_SOURCE.relative_to(ROOT)),
                  audio_source_sha256=sha(AUDIO_SOURCE),
                  audio_stream_sha256=audio_stream_hash(PUBLIC/'正式旁白.m4a'),
                  subtitle_sha256=sha(FORMAL/'輸出/字幕.srt'))
    # 比較報告自己的來源，不改全片 public/來源.json。
    (OUT/'來源.json').parent.mkdir(parents=True, exist_ok=True)
    (OUT/'來源.json').write_text(json.dumps(source, ensure_ascii=False, indent=2)+'\n')
    return source


def audio_stream_hash(path):
    return subprocess.check_output(['ffmpeg', '-v', 'error', '-i', str(path), '-map', '0:a:0', '-c:a', 'copy',
                                    '-f', 'hash', '-hash', 'sha256', '-'], text=True).strip()


def render():
    from motion_runtime import node, environment
    binary = node()
    for frame in SEGMENTS:
        for variant in VARIANTS:
            target = OUT/f'scene{frame}'/f'{variant}.mp4'
            target.parent.mkdir(parents=True, exist_ok=True)
            run(binary, MOTION/'node_modules/@remotion/cli/remotion-cli.js', 'render', 'src/index.ts', f'S{frame}-{variant}', target, '--log=warn', cwd=MOTION, env=environment(binary))


def baseline():
    """從正式 B 成片節錄同秒數，作為現行「焦點直接切換」的精準焦點對照。"""
    for frame, (start, end) in SEGMENTS.items():
        run('ffmpeg', '-v', 'error', '-y', '-ss', f'{start}', '-to', f'{end}', '-i', FORMAL/'輸出/影片.mp4',
            '-c:v', 'libx264', '-crf', '18', '-pix_fmt', 'yuv420p', '-c:a', 'aac', '-b:a', '192k',
            '-movflags', '+faststart', OUT/f'scene{frame}'/'baseline.mp4')


def audio_residual(a, b):
    """兩段解碼音訊相減後的 RMS（dB）；越低代表聲音越一致。"""
    out = subprocess.run(['ffmpeg', '-v', 'info', '-i', str(a), '-i', str(b), '-filter_complex',
                          '[0:a]aresample=44100,pan=mono|c0=c0[x];[1:a]aresample=44100,pan=mono|c0=c0,volume=-1[y];'
                          '[x][y]amix=inputs=2:normalize=0,astats=measure_overall=RMS_level:measure_perchannel=none',
                          '-f', 'null', '-'], capture_output=True, text=True).stderr
    levels = re.findall(r'RMS level dB: (\S+)', out)
    if not levels:
        raise RuntimeError(f'無法取得音訊殘差：{a} / {b}')
    # 完全相同時 FFmpeg 報 -inf，代表殘差為零；其他非數值一律視為錯誤。
    if levels[-1] == '-inf':
        return float('-inf')
    return float(levels[-1])


def frames():
    """依旁白事件擷取實際畫格：每段取同一組時間點，三種版本並排。
    含動作途中的時間點（卡片形變、鏡頭回全景、片段飛出、晶片沿路徑、回接描線），這些是刻意的過程狀態，不是靜止閱讀畫面。"""
    picks = {'02': [12.2, 13.1, 16.5, 21.5, 30.6, 32.7, 35.8, 38.0],
             '07': [54.5, 56.3, 59.4, 60.6, 62.6, 64.6, 67.6, 70.2]}
    for frame, times in picks.items():
        start = SEGMENTS[frame][0]
        for variant in ['baseline', *VARIANTS]:
            folder = OUT/f'scene{frame}'/'畫格'/variant
            folder.mkdir(parents=True, exist_ok=True)
            for t in times:
                run('ffmpeg', '-v', 'error', '-y', '-ss', f'{t-start:.3f}', '-i', OUT/f'scene{frame}'/f'{variant}.mp4',
                    '-frames:v', '1', folder/f'{t:05.1f}.png')
            run('ffmpeg', '-v', 'error', '-y', '-framerate', '1', '-pattern_type', 'glob', '-i', f'{folder}/*.png',
                '-vf', 'scale=400:225,tile=4x2:padding=6:margin=6:color=0x201D31', '-frames:v', '1',
                OUT/f'scene{frame}'/f'{variant}-總覽.png')
    return picks


def verify():
    source = json.loads((OUT/'來源.json').read_text())
    formal = FORMAL/'輸出/影片.mp4'
    source['formal_movie_sha256'] = sha(formal)
    source['formal_audio_stream_sha256'] = audio_stream_hash(formal)
    assert source['formal_audio_stream_sha256'] == source['audio_stream_sha256'], '準備後正式成片的音訊流已改變，請重新 prepare'
    if ORIGINAL.exists():
        source['original_audio_stream_sha256'] = audio_stream_hash(ORIGINAL)
        assert source['original_audio_stream_sha256'] == source['formal_audio_stream_sha256'], '修訂前後正式 B 的音訊流不同'
    report = {'source': source, 'segments': {}}
    for frame, (start, end) in SEGMENTS.items():
        expected = end-start
        rows = {}
        for variant in ['baseline', *VARIANTS]:
            path = OUT/f'scene{frame}'/f'{variant}.mp4'
            streams = json.loads(subprocess.check_output(['ffprobe', '-v', 'error', '-show_streams', '-of', 'json', str(path)]))['streams']
            video = next(s for s in streams if s['codec_type'] == 'video')
            run('ffmpeg', '-v', 'error', '-xerror', '-i', path, '-f', 'null', '-')  # 全段解碼，遇錯即中止
            rows[variant] = {'duration': round(duration(path), 3), 'size': [video['width'], video['height']],
                             'fps': video['r_frame_rate'], 'has_audio': any(s['codec_type'] == 'audio' for s in streams),
                             'sha256': sha(path)}
            if variant != 'baseline':
                residual = audio_residual(OUT/f'scene{frame}'/'baseline.mp4', path)
                # 僅記錄觀察值；尚未校準錯段／偏移門檻，不以殘差宣稱聲畫通過。
                rows[variant]['audio_residual_vs_baseline_db'] = round(residual, 1)
        for row in rows.values():
            assert abs(row['duration']-expected) < 0.08, f'{frame} 片長不符 {row}'
            assert row['size'] == [1600, 900] and row['has_audio'] and row['fps'] == '25/1'
        report['segments'][frame] = {'start': start, 'end': end, 'expected': round(expected, 3), 'files': rows}
    (OUT/'驗證.json').write_text(json.dumps(report, ensure_ascii=False, indent=2)+'\n')
    return report


PAGE = '''<!doctype html><html lang="zh-Hant"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>CH2 動態提案比較</title><style>
:root{color-scheme:dark;--bg:#201D31;--panel:#2A263D;--ink:#F4F0FF;--muted:#C4BDD5;--focus:#D8EF8A}
body{margin:0;background:var(--bg);color:var(--ink);font:16px/1.6 "PingFang TC",system-ui,sans-serif}
main{max-width:1500px;margin:auto;padding:28px 20px 60px}h1{font-size:30px;margin:0 0 8px}h2{margin:40px 0 6px}
.status{background:var(--panel);border-left:4px solid var(--focus);padding:12px 16px;color:var(--muted)}
.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(420px,1fr));gap:18px}article{background:var(--panel);padding:14px;border-radius:6px}
video,img{width:100%;display:block;border-radius:4px}h3{margin:0 0 4px;font-size:19px}p{margin:6px 0;color:var(--muted)}
table{border-collapse:collapse;width:100%;margin-top:10px}td,th{border-bottom:1px solid #373249;padding:6px 8px;text-align:left;vertical-align:top}
code{color:var(--focus)}</style><main>
<h1>CH2 動態提案：連續焦點 vs. 動態敘事</h1>
<p class="status"><strong>代表片段比較，尚未套用全片。</strong>三版共用正式 B 的深色配色、旁白、原配音與燒錄字幕版面；差別只在畫面如何隨解說移動。AI 檢查了畫格、片長、解碼與音訊殘差；<strong>沒有直接聽看，聲音自然度與聲畫節奏未驗證</strong>，請開聲音試看後選擇方向。畫格包含動作途中的時間點，那些是刻意的過程狀態。</p>
__BODY__
</main></html>'''

NOTES = {
    'baseline': '正式 B 現況：固定版面，焦點依旁白直接切換（無淡化、無移動）。',
    'focus': '同一版面；焦點是一個會沿解說連續滑動的框，五項依旁白逐詞揭露，回接線依方向描出。無鏡頭、無形變。',
    'motion': '二維鏡頭推近當下部位、說到另一組時回全景；物件沿路徑移動、SVG 由流程片段形變成獨立檔案。',
}
SCENES = {
    '02': ('scene02｜兩組技能，分別把關與抽取（11.16–38.80 秒）',
           '檢查：五項是否在唸到時逐一出現；Form 與 Deriver 是否分開；部位抽取是否看得出「從流程步驟分出」。'),
    '07': ('scene07｜檔案拆出去，流程也要接回來（53.04–70.44 秒）',
           '檢查：規則需求是否被看見從 SOP 出發、經抽取到寫規則；「再更新流程」時是否看得出回到 SOP 的方向。'),
}


def page(report, picks):
    body = ''
    for frame, (title, check) in SCENES.items():
        body += f'<h2>{escape(title)}</h2><p>{escape(check)}</p><div class="grid">'
        for variant, label in [('baseline', '基準：正式 B'), *VARIANTS.items()]:
            rev = report['segments'][frame]['files'][variant]['sha256'][:10]
            body += (f'<article><h3>{escape(label)}</h3><p>{escape(NOTES[variant])}</p>'
                     f'<video controls preload="metadata" src="scene{frame}/{variant}.mp4?v={rev}"></video>'
                     f'<p>畫格（{", ".join(f"{t:g}" for t in picks[frame])} 秒）</p>'
                     f'<a href="scene{frame}/{variant}-總覽.png?v={rev}"><img src="scene{frame}/{variant}-總覽.png?v={rev}" alt="{escape(label)}畫格"></a></article>')
        body += '</div>'
    rows = ''.join(f'<tr><td>scene{f}</td><td>{v}</td><td>{r["duration"]} 秒</td><td>{r.get("audio_residual_vs_baseline_db", "—")}</td></tr>'
                   for f, seg in report['segments'].items() for v, r in seg['files'].items())
    body += ('<h2>技術檢查</h2><p>片長、尺寸、全段解碼；音訊殘差為候選與基準節錄（兩者皆經重新編碼）解碼後相減的 RMS（dB），可協助發現可能錯段或偏移；門檻未校準，不作通過判準，也不代表聽感已驗證。詳見 <code>驗證.json</code>。</p>'
             f'<table><tr><th>段落</th><th>版本</th><th>片長</th><th>音訊殘差 dB</th></tr>{rows}</table>')
    (OUT/'index.html').write_text(PAGE.replace('__BODY__', body))


def main():
    # prepare：產生 Remotion 輸入；render：渲染兩段×兩版；review：節錄正式 B、擷取畫格、驗證並建比較頁。
    # 正式 B 重建中不可執行 prepare／review，因為兩者會讀取正式輸出。
    steps = sys.argv[1:] or ['prepare', 'render', 'review']
    if 'prepare' in steps:
        prepare()
    if 'render' in steps:
        render()
    if 'review' in steps:
        baseline()
        picks = frames()
        page(verify(), picks)
        print(OUT/'index.html')


if __name__ == '__main__':
    main()
