"""核對動態敘事全片：逐影格共用狀態、成片解碼、原音與逐段抽幀。"""
import argparse
import html
import json
import math
from pathlib import Path
import shutil
import subprocess
import sys
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parents[1]/'scripts'))
import video
import motion_runtime as runtime
RECORDS='製作紀錄/設計/新流程測試'
LABELS=json.loads((HERE/'motion-labels.json').read_text())


def segments(rows,contract,focus=None):
    result=[]
    assert set(contract)=={r['frame'] for r in rows}
    if focus:assert set(focus)==set(contract)
    for row in rows:
        entries=contract[row['frame']]
        if focus:assert len(focus[row['frame']])==len(entries)
        assert all(row['text'].count(e['phrase'])==1 for e in entries)
        assert entries and row['text'].startswith(entries[0]['phrase'])
        offsets=[row['text'].index(e['phrase']) for e in entries]
        assert offsets==sorted(set(offsets))
        for i,e in enumerate(entries):
            end_offset=offsets[i+1] if i+1<len(entries) else len(row['text'])
            result.append(dict(scene=row['frame'],start=max(row['start'],video.text_time(row,offsets[i])-.04),
                end=video.text_time(row,end_offset)-.04 if i+1<len(entries) else row['end'],
                text=row['text'][offsets[i]:end_offset],targets=e['targets'],
                focus_targets=focus[row['frame']][i] if focus else e['targets'],hold_reason=e.get('hold_reason')))
    return result


def check_states(states,expected):
    """只檢查可見性／焦點與幾何資料；無法證明像素或聽感。"""
    assert len(states)==2825 and [s['frame'] for s in states]==list(range(2825))
    failures=[]
    for s in states:
        assert isinstance(s['active'],list) and isinstance(s['visible'],list)
        assert abs(s['t']-s['frame']/25)<1e-8
        assert len({o['id'] for o in s['visible']})==len(s['visible'])
        for o in s['visible']:
            assert all(math.isfinite(o[k]) for k in ('x','y','w','h','opacity')),o
            assert o['w']>=0 and o['h']>=0 and 0<=o['opacity']<=1,o
    for entry in expected:
        # 動作起頭一小段允許進場；中後段須保持對象，不容許提前失焦。
        samples=[s for s in states if s['scene']==entry['scene'] and
                 entry['start']+.24<=s['t']<entry['end']-.04]
        if not samples:samples=[s for s in states if s['scene']==entry['scene'] and entry['start']<=s['t']<entry['end']]
        assert samples,f'沒有核對到影格：{entry}'
        issues=[]
        for s in samples:
            visible={o['id']:o for o in s['visible'] if o.get('opacity',1)>=.45}
            missing=set(entry['targets'])-visible.keys()
            # 脈絡物件可保留低階強調；所有獨立列出的主焦點都必須實際強調或移動。
            unfocused=bool(entry['focus_targets']) and not set(entry['focus_targets'])<=set(s['active'])
            identity=[label for key in entry['focus_targets'] for label in LABELS.get(entry['scene'],{}).get(key,[])]
            missing_labels=[label for label in identity if label not in visible or not visible[label].get('text')]
            cropped=[]
            for key in [*entry['focus_targets'],*identity]:
                if key in visible:
                    o=visible[key].get('projected',visible[key])
                    if o['x'] < -1 or o['y'] < 214 or o['x']+o['w']>1601 or o['y']+o['h']>901:
                        cropped.append(key)
            if missing or unfocused or cropped or missing_labels:
                issues.append({'frame':s['frame'],'t':s['t'],'missing':sorted(missing),
                               'cropped':cropped,'missing_labels':missing_labels,'active':s['active']})
        if issues:failures.append({'scene':entry['scene'],'text':entry['text'],'issues':issues})
    return failures


def review(args,movie=None,capture=False):
    root,materials,content,data,out,config=video.load(args)
    movie=Path(movie) if movie else out/'輸出/影片.mp4'
    manifest=json.loads((out/'來源指紋.json').read_text())
    if manifest!=runtime.fingerprints(materials,content,config,args):
        raise RuntimeError('來源指紋已過期，請先重建動態正式片')
    rows=video.recorded_timeline(data,materials,config)
    contract=json.loads((video.HOME/config['focus_contract']).read_text())
    focus=json.loads((HERE/'motion-focus.json').read_text())
    expected=segments(rows,contract,focus)
    target=out/'預覽/聲畫稽核';target.mkdir(parents=True,exist_ok=True)
    state_file=target/'逐影格狀態.json'
    executable=runtime.node()
    video.run([executable,runtime.MOTION/'scripts/export-state.cjs',state_file],cwd=runtime.MOTION,
              env=runtime.environment(executable))
    states=json.loads(state_file.read_text())
    failures=check_states(states,expected)
    if failures:
        (target/'失敗.json').write_text(json.dumps(failures,ensure_ascii=False,indent=2)+'\n')
        raise ValueError(f'動態逐段核對不通過：{len(failures)} 段，見 {target}/失敗.json')
    (target/'失敗.json').unlink(missing_ok=True)
    video.ffmpeg('-i',movie,'-f','null','-')
    info=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_streams','-show_format','-of','json',str(movie)]))
    assert {s['codec_type'] for s in info['streams']}=={'video','audio'}
    v=next(s for s in info['streams'] if s['codec_type']=='video')
    assert (v['width'],v['height'],v['r_frame_rate'])==(1600,900,'25/1')
    assert int(v['nb_frames'])==2825 and abs(float(info['format']['duration'])-113)<.04
    original=runtime.audio_stream_hash(video.audio_path(materials,config))
    assert runtime.audio_stream_hash(movie)==original,'動態片音訊流與原配音不同'
    if capture:
        for i,e in enumerate(expected):
            for label,t in [('mid',(e['start']+e['end'])/2),('end',max(e['start'],e['end']-.12))]:
                video.ffmpeg('-ss',t,'-i',movie,'-frames:v','1','-update','1',target/f'{i:03}-{label}.png')
        # 每秒一幀總覽可補看各段之間的動作，仍不是連續觀看。
        video.ffmpeg('-i',movie,'-vf','fps=1,scale=640:360','-start_number',0,target/'second-%03d.png')
        for start in range(0,113,9):
            video.ffmpeg('-framerate','1','-start_number',start,'-i',target/'second-%03d.png',
                         '-frames:v','1','-vf','tile=3x3:nb_frames=9:padding=6:margin=6:color=0x201D31',target/f'總覽-{start//9:02}.png')
    evidence={'renderer':'remotion','direction':'B-M2','duration':float(info['format']['duration']),
              'frames':2825,'scenes':len(rows),'segments':len(expected),'failed_segments':0,
              'focus_window':{'intro_grace_seconds':.24,'end_margin_seconds':.04,'note':'每段起點後0.24秒至終點前0.04秒逐影格核對；過短段回退為全段'},
              'video_sha256':runtime.sha(movie),'audio_stream_sha256':original,'subtitles':'burned',
              'review':'逐影格狀態與抽幀；非直接連續聽看','listening':'未直接聽審','continuous_viewing':'未連續觀看全片',
              'acceptance':'待使用者','entries':expected}
    previous=out/'驗證.json'
    if previous.exists():
        old=json.loads(previous.read_text())
        if old.get('video_sha256')==evidence['video_sha256'] and old.get('static_review'):
            evidence['static_review']=old['static_review']
    previous.write_text(json.dumps(evidence,ensure_ascii=False,indent=2)+'\n')
    table=[]
    for i,e in enumerate(expected):
        pictures=''.join(f'<a href="{i:03}-{k}.png"><img src="{i:03}-{k}.png"></a>' for k in ['mid','end']) if capture else '未重抽幀'
        table.append(f'<tr><td>{e["start"]:.2f}–{e["end"]:.2f}</td><td>{html.escape(e["text"])}</td><td>{html.escape(", ".join(e["targets"]) or e["hold_reason"])}</td><td>{pictures}</td></tr>')
    (target/'index.html').write_text('<!doctype html><html lang="zh-Hant"><meta charset="utf-8"><title>動態全片逐段核對</title><style>body{background:#201D31;color:#F4F0FF;font:17px system-ui}a{color:#D8EF8A}td{border:1px solid #847B97;padding:12px}img{width:380px}table{border-collapse:collapse}</style><h1>動態全片逐段核對</h1><p>共用動畫狀態檢查及成片抽幀分開記錄。狀態通過不代表畫格可讀或已連續聽看。</p><table>'+''.join(table)+'</table></html>')
    print(f'通過：9幕、2825影格、{len(expected)}段狀態、原音copy、113秒與完整解碼',flush=True)
    return evidence


def delivery(out,evidence,materials=None):
    build=out.parent;preview=build/'預覽';preview.mkdir(exist_ok=True)
    rev=evidence['video_sha256'][:12]
    records=preview/'製作歷程';records.mkdir(exist_ok=True)
    if materials is None:
        _,materials,_,_,_,_=video.load(argparse.Namespace(config='projects/ch2-workflow-test/project.toml',source_root=None))
    checked='已完成技術、逐影格焦點與成片抽幀複查' if evidence.get('static_review') else '技術與逐影格焦點檢查通過；已產生抽幀，視覺複查中'
    for p in (materials/RECORDS).glob('*.md'):shutil.copy2(p,records/p.name)
    (preview/'交付.html').write_text(f'''<!doctype html><html lang="zh-Hant"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>CH2 B 動態敘事全片</title><style>body{{background:#201D31;color:#F4F0FF;font:18px/1.7 system-ui;margin:0}}main{{max-width:1080px;margin:auto;padding:28px}}a{{color:#D8EF8A}}video{{width:100%}}.status{{padding:16px;background:#373249;border-left:4px solid #D8EF8A}}</style><main><h1>CH2｜B 深色動態敘事</h1><p class="status">已依你選定的 M2 動態敘事完成九幕，113 秒，保留原旁白與配音，字幕已燒錄。<br>{checked}；AI 未直接連續聽看，聲畫感受待你試看。</p><video controls preload="metadata" src="../動態正式版/輸出/影片.mp4?v={rev}"></video><p><a href="../動態正式版/輸出/影片.mp4?v={rev}" download="CH2-B動態敘事.mp4">下載完整動態片</a> · <a href="../動態正式版/預覽/聲畫稽核/index.html">逐段核對</a></p><p><a href="../正式版/輸出/影片.mp4">先前 B 焦點版</a> · <a href="../動態提案/index.html">代表片段比較</a> · <a href="製作歷程/交付狀態.md">製作狀態</a></p><p>技能與流程關係以揭露、拆分、交棒、路徑移動及回接呈現；鏡頭服務當下講解，標題與字幕帶固定。開場與結尾保留閱讀時間。</p></main></html>''')

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--config',default='projects/ch2-workflow-test/project.toml');p.add_argument('--source-root');p.add_argument('--capture',action='store_true')
    args=p.parse_args();evidence=review(args,capture=args.capture);_,materials,_,_,out,_=video.load(args);delivery(out,evidence,materials)
