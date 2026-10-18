"""逐段核對旁白與焦點；成片抽幀、辨識與人類聽看分開記錄。"""
import argparse
import hashlib
import html
import json
from pathlib import Path
import sys
import video
import visual_motion

DEFAULT = 'projects/ch2-workflow-test/project.toml'


def audit(data, rows, spec, contract):
    result = []
    if set(contract) != {r['frame'] for r in rows}:
        raise ValueError('焦點核對表必須覆蓋所有場景')
    for row in rows:
        entries = contract[row['frame']]
        if not entries or not row['text'].startswith(entries[0]['phrase']):
            raise ValueError(f"{row['frame']} 核對表未從第一句開始")
        if any(row['text'].count(e['phrase']) != 1 for e in entries):
            raise ValueError('核對片語必須在場景旁白中恰好出現一次')
        offsets = [row['text'].index(e['phrase']) for e in entries]
        if offsets != sorted(set(offsets)):
            raise ValueError('核對片語必須唯一且依旁白順序')
        events = visual_motion.timeline(video, row, spec['frames'][row['frame']], data['fps'])
        for i, (entry, offset) in enumerate(zip(entries, offsets)):
            end_offset = offsets[i+1] if i+1 < len(offsets) else len(row['text'])
            start = max(row['start'], video.text_time(row, offset)-.04)
            end = video.text_time(row, end_offset)-.04 if i+1 < len(offsets) else row['end']
            targets = set(entry['targets'])
            if not targets and not entry.get('hold_reason'):
                raise ValueError('靜止段必須記錄觀看對象與停留理由')
            failures = []
            # 僅容許一影格的詞時間量化誤差；其餘解說區間必須保留預期對象。
            for event in events:
                left, right = max(start+1/data['fps'], event['start']), min(end-.04, event['end'])
                if left < right and not targets <= set(event['step'].get('active', [])):
                    failures.append({'start':round(left,3),'end':round(right,3),
                                     'expected':sorted(targets),'actual':event['step'].get('active',[])})
            result.append(dict(frame=row['frame'],start=round(start,3),end=round(end,3),
                               text=row['text'][offset:end_offset],targets=sorted(targets),
                               hold_reason=entry.get('hold_reason'),issues=failures))
    return result


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--config',default=DEFAULT)
    parser.add_argument('--source-root')
    parser.add_argument('--capture',action='store_true',help='從實際 MP4 擷取每段中點與尾端，不宣稱連續觀看')
    args=parser.parse_args()
    root,materials,content,data,out,config=video.load(args)
    if config.get('review_script'):
        video.run([sys.executable,video.HOME/config['review_script'],'--config',args.config,
                   *(['--source-root',args.source_root] if args.source_root else []),
                   *(['--capture'] if args.capture else [])])
        return
    video.check(root,materials,content,data,out,config)
    contract_path=video.HOME/config['focus_contract']
    spec=json.loads((materials/config['visuals']).read_text())
    rows=video.recorded_timeline(data,materials,config)
    result=audit(data,rows,spec,json.loads(contract_path.read_text()))
    target=out/'預覽/聲畫稽核'
    target.mkdir(parents=True,exist_ok=True)
    mp4=out/'輸出/影片.mp4'
    if args.capture:
        manifest=json.loads((out/'來源指紋.json').read_text())
        if any(not Path(p).is_file() or hashlib.sha256(Path(p).read_bytes()).hexdigest()!=digest for p,digest in manifest.items()):
            raise ValueError('成片來源指紋已過期，請先重新 render')
        video.ffmpeg('-i',mp4,'-f','null','-')
        for i,entry in enumerate(result):
            for label,t in [('mid',(entry['start']+entry['end'])/2),('end',max(entry['start'],entry['end']-.12))]:
                video.ffmpeg('-ss',t,'-i',mp4,'-frames:v','1','-update','1',target/f'{i:03}-{label}.png')
    evidence={'config':args.config,'contract_sha256':hashlib.sha256(contract_path.read_bytes()).hexdigest(),
              'visuals_sha256':hashlib.sha256((materials/config['visuals']).read_bytes()).hexdigest(),
              'video_sha256':hashlib.sha256(mp4.read_bytes()).hexdigest() if mp4.exists() else None,
              'segments':len(result),'failed_segments':sum(bool(e['issues']) for e in result),
              'scope':'來源焦點時序與逐段預期對照；抽幀不等於連續聽看',
              'listening':'未直接聽審','continuous_viewing':'未連續觀看','entries':result}
    (target/'稽核.json').write_text(json.dumps(evidence,ensure_ascii=False,indent=2)+'\n')
    table=[]
    for i,e in enumerate(result):
        pictures=''.join(f'<a href="{i:03}-{k}.png"><img width="400" src="{i:03}-{k}.png" alt="{k}"></a>' for k in ['mid','end']) if args.capture else '未抽幀'
        status='不通過' if e['issues'] else '來源時序通過；畫面待檢視'
        table.append(f'<tr><td><a href="../../輸出/影片.mp4#t={e["start"]},{e["end"]}">{e["start"]}–{e["end"]}</a></td><td>{html.escape(e["text"])}</td><td>{html.escape(", ".join(e["targets"]) or e["hold_reason"])}</td><td>{status}<pre>{html.escape(json.dumps(e["issues"],ensure_ascii=False))}</pre></td><td>{pictures}</td></tr>')
    (target/'index.html').write_text('<!doctype html><html lang="zh-Hant"><meta charset="utf-8"><title>全片逐段聲畫稽核</title><style>body{background:#201D31;color:#F4F0FF;font:17px system-ui}a{color:#D8EF8A}td{border:1px solid #847B97;padding:12px;vertical-align:top}table{border-collapse:collapse}img{max-width:30vw}</style><h1>全片逐段聲畫稽核</h1><p>來源時序檢查與成片中點／尾端抽幀；不是連續聽看，也未判定聲音自然度。</p><table><tr><th>秒</th><th>旁白</th><th>預期觀看對象</th><th>時序結果</th><th>成片</th></tr>'+''.join(table)+'</table></html>')
    print(json.dumps({k:v for k,v in evidence.items() if k!='entries'},ensure_ascii=False))
    if evidence['failed_segments']:
        raise SystemExit(1)


if __name__=='__main__':main()
