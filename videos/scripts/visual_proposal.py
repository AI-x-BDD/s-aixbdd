"""產生 CH2 三幕美術樣稿與正式配音短片；不改寫正式九幕。"""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import xml.etree.ElementTree as ET

import video


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--config', default='projects/ch2-skill-engineering/project.toml')
    parser.add_argument('--source-root')
    args = parser.parse_args()
    root, materials, content, data, out, config = video.load(args)
    artwork = materials / '製作來源/畫面/美術提案'
    work = out / '中間產物/美術提案'
    review = out / '預覽/美術提案'
    export = out / '輸出/美術提案'
    sources = [content, materials/config['alignment'], *sorted((materials/config['slides']).glob('*.svg'))]
    before = {str(p): hashlib.sha256(p.read_bytes()).hexdigest() for p in sources}
    for folder in (work, review, export, work/'轉圖', work/'SVG'):
        folder.mkdir(parents=True, exist_ok=True)
    if not video.audio_path(materials, config).exists():
        video.prepare_audio(materials, config)
    video.check(root, materials, content, data, out, config)
    for name in ('01', '03', '06'):
        shutil.copyfile(artwork/f'{name}.svg', work/'SVG'/f'{name}.svg')
    # 調整作用部位的字色、亮度與背景色塊，不加側邊標記，保留其餘部件的位置脈絡。
    ET.register_namespace('', 'http://www.w3.org/2000/svg')
    for active in range(5):
        tree = ET.parse(artwork/'03.svg')
        svg = tree.getroot()
        from visual_motion import primitive_state
        primitive_state(svg, active)
        tree.write(work/'SVG'/f'form-{active}.svg', encoding='unicode')
    names = ['01','03','06',*[f'form-{i}' for i in range(5)]]
    # 共用正式影片的 SVG 轉圖方式，PNG 只留在 build。
    video.frames(work, {'slides':'SVG'}, [{'frame':n} for n in names], work, work/'轉圖')
    rows = video.recorded_timeline(data, materials, config)
    group = next(g for g in data['focus'] if g['scene']==2)
    times = [video.text_time(rows[2],rows[2]['text'].index(phrase))-.04 for phrase,_ in group['entries']]
    start, end = times[1], times[-1]
    length = round(end-start,3)
    captions = video.captions(rows, work)
    clip_cues = [{**c,'start':max(c['start'],start)-start,'end':min(c['end'],end)-start}
                 for c in captions if c['end']>start and c['start']<end]
    (export/'字幕.srt').write_text('\n\n'.join(
        f"{i+1}\n{video.stamp(c['start'],True)} --> {video.stamp(c['end'],True)}\n{c['text']}"
        for i,c in enumerate(clip_cues))+'\n')
    inputs = []
    for i in range(5):
        inputs += ['-loop','1','-framerate','25','-t',str(length),'-i',str(work/'靜幀'/f'form-{i}.png')]
    inputs += ['-ss',str(start),'-t',str(length),'-i',str(video.audio_path(materials,config)),
               '-i',str(export/'字幕.srt')]
    filters = [f'[{i}:v]format=yuv420p,settb=AVTB,setpts=PTS-STARTPTS[v{i}]' for i in range(5)]
    previous = 'v0'
    for i in range(1,5):
        offset = round(times[i+1]-start,3)
        # 在原焦點時間到達新部位，過渡在前四影格完成，不延後旁白對應。
        filters.append(f'[{previous}][v{i}]xfade=transition=fade:duration=0.16:offset={offset-.16:.3f}[x{i}]')
        previous = f'x{i}'
    video.ffmpeg(*inputs,'-filter_complex_threads','1','-filter_complex',';'.join(filters),
                 '-map',f'[{previous}]','-map','5:a','-map','6:s',
                 '-c:v','libx264','-preset','veryfast','-crf','20','-pix_fmt','yuv420p','-threads','2',
                 '-c:a','aac','-b:a','192k','-c:s','mov_text','-metadata:s:s:0','language=zho',
                 '-t',str(length),'-movflags','+faststart',export/'聚焦樣片.mp4')
    page = (video.HOME/'templates/visual_proposal.html').read_text()
    revision = hashlib.sha256((export/'聚焦樣片.mp4').read_bytes()).hexdigest()[:12]
    page = page.replace('__CUES__',json.dumps(clip_cues,ensure_ascii=False)).replace('__LENGTH__',str(length)).replace('__REV__',revision)
    (review/'index.html').write_text(page)
    assert all(hashlib.sha256(Path(p).read_bytes()).hexdigest()==sha for p,sha in before.items())
    report = {'duration_seconds':video.duration(export/'聚焦樣片.mp4'),
              'source_clip_start':start,'source_clip_end':end,
              'focus_times_in_clip':[round(t-start,3) for t in times[1:-1]],
              'production_sources_unchanged':True,
              'note':'第三幕正式配音節錄；聚焦動畫已直接編碼於 MP4，網頁播放同一檔案。'}
    (review/'樣片檢查.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
    print(f'美術樣稿與 {length:.2f} 秒樣片：http://127.0.0.1:60070/預覽/美術提案/')


if __name__ == '__main__':
    main()
