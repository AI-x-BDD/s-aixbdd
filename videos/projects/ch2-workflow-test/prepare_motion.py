"""依指定 profile 準備九幕 Remotion 輸入；不依賴任何既有成片。"""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import sys
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parents[1]/'scripts'))
import video
from burn_subtitles import wrap


def prepare(args):
    root,materials,content,data,out,config=video.load(args)
    video.prepare_audio(materials,config)
    video.check(root,materials,content,data,out,config)
    rows=video.recorded_timeline(data,materials,config)
    work=out/'中間產物';export=out/'輸出'
    for p in (work,export):p.mkdir(parents=True,exist_ok=True)
    cues=video.captions(rows,export)
    public=video.HOME/'motion/public';public.mkdir(parents=True,exist_ok=True)
    shutil.copy2(video.audio_path(materials,config),public/'正式旁白.m4a')
    segments={r['frame']:{'start':r['start'],'end':r['end'],'text':r['text'],
                'chars':[[c['offset'],c['start']] for c in r['characters']],
                'cues':[{'start':c['start'],'end':c['end'],'lines':wrap(c['text'])} for c in cues
                        if c['end']>r['start'] and c['start']<r['end']]}
              for r in rows}
    (public/'segments.json').write_text(json.dumps(segments,ensure_ascii=False,indent=1)+'\n')
    (work/'時間軸.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2)+'\n')
    source={'audio_sha256':hashlib.sha256(video.audio_path(materials,config).read_bytes()).hexdigest(),
            'content_sha256':hashlib.sha256(content.read_bytes()).hexdigest(),
            'alignment_sha256':hashlib.sha256((materials/config['alignment']).read_bytes()).hexdigest()}
    (public/'來源.json').write_text(json.dumps(source,ensure_ascii=False,indent=2)+'\n')
    print('已準備九幕：'+', '.join(f"{k} {v['start']}–{v['end']}" for k,v in segments.items()))
    return root,materials,content,data,out,config,rows

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--config',default='projects/ch2-workflow-test/project.toml')
    p.add_argument('--source-root')
    prepare(p.parse_args())
