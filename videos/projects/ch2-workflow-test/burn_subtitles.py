"""用既有 SVG／Quick Look 工具燒錄字幕，無需安裝 libass。"""
from pathlib import Path
from html import escape
import json
import re
import shutil
import subprocess
import sys
import unicodedata

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT/'videos/scripts'))
import video


def seconds(value):
    h, m, rest = value.split(':')
    s, ms = rest.split(',')
    return int(h)*3600 + int(m)*60 + int(s) + int(ms)/1000


def wrap(text):
    lines, current, width = [], '', 0
    tokens = re.findall(r'[A-Za-z0-9]+(?:[-_][A-Za-z0-9]+)*|.', text)
    for token in tokens:
        size = sum(1 if unicodedata.east_asian_width(c) in 'WF' else .62 for c in token)
        if current and width+size > 37 and token not in '，。；：、？！）》」』':
            lines.append(current.strip())
            current, width = '', 0
        current += token
        width += size
    if current.strip():
        lines.append(current.strip())
    assert len(lines) <= 2, f'字幕超過兩行，需重新斷句：{text}'
    return lines


def burn(folder):
    output = folder/'輸出/影片.mp4'
    source = folder/'中間產物/未燒字幕.mp4'
    work = folder/'中間產物/燒錄字幕'
    (work/'SVG').mkdir(parents=True, exist_ok=True)
    (work/'字幕帶').mkdir(exist_ok=True)
    # render 會重新產生含字幕軌的來源；重跑 finish 時則沿用保存的未燒錄來源。
    streams = json.loads(subprocess.check_output(['ffprobe','-v','quiet','-show_streams','-of','json',str(output)]))['streams']
    if any(s['codec_type']=='subtitle' for s in streams):
        shutil.copy2(output, source)
    assert source.exists(), '缺少未燒字幕來源；請先 render'
    cues = []
    for block in (folder/'輸出/字幕.srt').read_text().strip().split('\n\n'):
        parts = block.splitlines()
        start, end = parts[1].split(' --> ')
        cues.append((seconds(start), seconds(end), ''.join(parts[2:])))
    total = video.duration(source)
    intervals = []
    cursor = 0
    for start, end, text in cues:
        assert start >= cursor-0.001 and end > start, '字幕重疊或時間無效'
        if start > cursor:
            intervals.append((cursor, start, ''))
        intervals.append((start, end, text))
        cursor = end
    if cursor < total:
        intervals.append((cursor, total, ''))
    unique = list(dict.fromkeys(text for _, _, text in intervals))
    keys = {text: f'{i:03}' for i, text in enumerate(unique)}
    for text, key in keys.items():
        lines = wrap(text) if text else []
        baselines = [865] if len(lines)==1 else [840, 884]
        body = ''.join(f'<text x="800" y="{y}" text-anchor="middle" font-size="36" font-weight="500" fill="#F4F0FF">{escape(line)}</text>' for line, y in zip(lines, baselines))
        (work/'SVG'/f'{key}.svg').write_text('<svg xmlns="http://www.w3.org/2000/svg" width="1600" height="900" viewBox="0 0 1600 900"><g font-family="PingFang TC"><rect width="1600" height="900" fill="#201D31"/>'+body+'</g></svg>')
    video.frames(work, {'slides':'SVG'}, [{'frame':key} for key in keys.values()], work, work)
    for key in keys.values():
        video.ffmpeg('-i', work/'靜幀'/f'{key}.png', '-vf', 'crop=1600:100:0:800', '-frames:v', '1', work/'字幕帶'/f'{key}.png')
    listing = []
    for start, end, text in intervals:
        listing += [f"file '字幕帶/{keys[text]}.png'", f'duration {end-start:.6f}']
    listing.append(f"file '字幕帶/{keys[intervals[-1][2]]}.png'")
    (work/'字幕帶.txt').write_text('\n'.join(listing)+'\n')
    target = folder/'輸出/影片-燒錄中.mp4'
    # 圖解等比縮至800px高，完整保留內容；底部100px專供字幕。
    video.ffmpeg('-i', source, '-f', 'concat', '-safe', '0', '-i', work/'字幕帶.txt',
                 '-filter_complex', '[0:v]scale=1422:800:flags=lanczos,pad=1600:900:89:0:color=0x201D31[base];[1:v]fps=25[subs];[base][subs]overlay=0:800:eof_action=repeat[v]',
                 '-map', '[v]', '-map', '0:a:0', '-sn', '-c:v', 'libx264', '-preset', 'fast', '-crf', '18',
                 '-pix_fmt', 'yuv420p', '-r', '25', '-c:a', 'copy', '-t', total, '-movflags', '+faststart', target)
    def audio_hash(path):
        return subprocess.check_output(['ffmpeg','-v','error','-i',str(path),'-map','0:a:0',
                                        '-c:a','copy','-f','hash','-hash','sha256','-'],text=True).strip()
    assert audio_hash(source)==audio_hash(target), '燒錄字幕不得改動音訊內容'
    target.replace(output)
    (folder/'字幕燒錄.json').write_text(json.dumps({'mode':'burned','cues':len(cues),'duration':total,'canvas':[1600,900],'content_box':[89,0,1422,800],'subtitle_box':[0,800,1600,100],'font':'PingFang TC','font_size':36,'max_lines':2,'audio':'copy'},ensure_ascii=False,indent=2)+'\n')
    return output
