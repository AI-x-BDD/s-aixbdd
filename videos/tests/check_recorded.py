"""檢查正式配音時間軸、詞時間定位，以及過期對齊資料的阻擋。"""
import argparse
import importlib.util
import json
from pathlib import Path
import tempfile

HOME = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('video', HOME/'scripts/video.py')
video = importlib.util.module_from_spec(spec)
spec.loader.exec_module(video)

parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('--config',default='projects/ch2-workflow-test/project.toml')
parser.add_argument('--source-root')
args=parser.parse_args()

# 後半句實際講得較慢，字幕與 focus 必須依詞時間定位，而非字數比例。
row = {'text':'甲乙。丙丁。', 'start':0, 'end':8, 'voice_seconds':8,
       'characters':[{'offset':0,'start':.2,'end':.5}, {'offset':1,'start':.5,'end':1},
                     {'offset':3,'start':3,'end':5}, {'offset':4,'start':5,'end':7}]}
assert video.text_time(row,3) == 3
focus = video.focus_timeline({'focus':[{'scene':0,'entries':[['丙',[0,0,10,10]]]}]}, [row])
assert focus[0]['start'] == 2.96
(HOME/'build').mkdir(exist_ok=True)
with tempfile.TemporaryDirectory(dir=HOME/'build') as folder:
    folder = Path(folder)
    cues = video.captions([row], folder)
    assert cues[0]['end'] == cues[1]['start'] == 2.96
    assert cues[-1]['end'] == 8
    # 音檔換了卻沿用舊對齊資料，必須在呼叫 FFmpeg 前拒絕建置。
    (folder/'audio.mp3').write_bytes(b'new audio')
    (folder/'alignment.json').write_text(json.dumps({'audio_sha256':'old'}))
    try:
        video.check(folder,folder,folder/'content.json',{},folder,
                    {'audio':'audio.mp3','alignment':'alignment.json'})
        raise AssertionError('未拒絕過期對齊資料')
    except ValueError as exc:
        assert '音檔已改動' in str(exc)
    # 素材中的九幕必須連續、不切掉音訊，且每一幕和每個字幕區間都向前。
    root,materials,path,data,out,config = video.load(args)
    rows = video.recorded_timeline(data,materials,config)
    assert rows[0]['start']==0
    assert all(a['end']==b['start'] for a,b in zip(rows,rows[1:]))
    assert abs(rows[-1]['end']-video.duration(video.audio_path(materials,config))) < 1/data['fps']
    cues = video.captions(rows,folder)
    assert all(c['end']>c['start'] for c in cues)
    assert all(a['end']<=b['start']+.002 for a,b in zip(cues,cues[1:]))
    focus = video.focus_timeline(data,rows)
    assert all(c['end']>c['start'] for c in focus)
print('通過：變速旁白定位、字幕接續、過期對齊阻擋、九幕完整連續、focus 時間有效')
