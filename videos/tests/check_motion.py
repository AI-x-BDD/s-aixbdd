"""用實際動畫狀態檢查49段，刻意移除／切錯焦點／裁切時必須失敗。"""
import argparse
import copy
import json
from pathlib import Path
import subprocess
import sys
HERE=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(HERE/'scripts'))
sys.path.insert(0,str(HERE/'projects/ch2-workflow-test'))
import video
from prepare_motion import prepare
import review_motion
import motion_runtime as runtime
p=argparse.ArgumentParser(description=__doc__)
p.add_argument('--config',default='projects/ch2-workflow-test/project.toml');p.add_argument('--source-root')
args=p.parse_args()
_,_,_,_,_,config=video.load(args)
if config.get('renderer')!='remotion':
    print('非Remotion profile，動態狀態檢查不適用');sys.exit(0)
video.run([sys.executable,HERE/'projects/ch2-workflow-test/render_motion.py','--config',args.config,
           *(['--source-root',args.source_root] if args.source_root else []),'--prepare-only'])
_,materials,_,data,out,config=video.load(args)
rows=video.recorded_timeline(data,materials,config)
expected=review_motion.segments(rows,json.loads((HERE/config['focus_contract']).read_text()),
                               json.loads((runtime.MOTION.parent/'projects/ch2-workflow-test/motion-focus.json').read_text()))
executable=runtime.node();statefile=out/'中間產物/測試狀態.json'
video.run([executable,runtime.MOTION/'scripts/export-state.cjs',statefile],cwd=runtime.MOTION,env=runtime.environment(executable))
states=json.loads(statefile.read_text())
issues=review_motion.check_states(states,expected)
if issues:
    (out/'中間產物/測試失敗.json').write_text(json.dumps(issues,ensure_ascii=False,indent=2)+'\n')
    raise AssertionError(f'{len(issues)}段不符；見中間產物/測試失敗.json')
entry=next(e for e in expected if e['scene']=='02' and e['focus_targets']==['p1'])
sample=next(s for s in states if s['scene']=='02' and entry['start']+.24<=s['t']<entry['end']-.04)
for defect in ['missing','wrong-focus','cropped']:
    broken=copy.deepcopy(states);s=broken[sample['frame']]
    if defect=='missing':s['visible']=[o for o in s['visible'] if o['id']!='p1']
    elif defect=='wrong-focus':s['active']=[x for x in s['active'] if x!='p1']
    else:
        o=next(o for o in s['visible'] if o['id']=='p1')
        o.get('projected',o)['x']=-100
    assert review_motion.check_states(broken,expected),defect
label_entry=next(e for e in expected if e['scene']=='06' and e['focus_targets']==['rule0'])
label_sample=next(s for s in states if s['scene']=='06' and label_entry['start']+.24<=s['t']<label_entry['end']-.04)
broken=copy.deepcopy(states)
broken[label_sample['frame']]['visible']=[o for o in broken[label_sample['frame']]['visible'] if o['id']!='rule0-label']
assert review_motion.check_states(broken,expected),'missing-label'
print('通過：九幕2825影格、49段真正焦點／可見性／裁切，故意漏項／錯焦點／裁切／空白焦點檔案均被阻擋')
