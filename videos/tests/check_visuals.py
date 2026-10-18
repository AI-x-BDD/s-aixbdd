"""依指定 profile 檢查所有語意狀態；B 版另核對完整旁白焦點契約。"""
import argparse
import json
from pathlib import Path
import sys
import xml.etree.ElementTree as ET
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
import video
import visual_motion
import review
parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('--config',default=review.DEFAULT)
parser.add_argument('--source-root')
args=parser.parse_args()
root,materials,path,data,out,config=video.load(args)
video.check(root,materials,path,data,out,config)
rows=video.recorded_timeline(data,materials,config)
spec=json.loads((materials/config['visuals']).read_text())
assert {r['frame'] for r in rows}==set(spec['frames'])
for row in rows:
 svg=ET.parse(materials/config['slides']/f"{row['frame']}.svg").getroot()
 events=visual_motion.timeline(video,row,spec['frames'][row['frame']],data['fps'])
 assert events[0]['start']==row['start'] and events[-1]['end']==row['end']
 assert all(a['end']==b['start'] for a,b in zip(events,events[1:]))
 for e in events:visual_motion.state_svg(svg,e['step'],spec['inactive_opacity'])
 if not any(n.get('id')=='form-0' for n in svg.iter()):
  try:visual_motion.state_svg(svg,{'active':['missing-node']},.7)
  except ValueError:pass
  else:raise AssertionError('未拒絕不存在的焦點')
if config.get('focus_contract'):
 contract=json.loads((video.HOME/config['focus_contract']).read_text())
 result=review.audit(data,rows,spec,contract)
 assert not any(e['issues'] for e in result),[e for e in result if e['issues']]
 print(f"通過：{args.config}，{len(rows)} 幕、{len(result)} 段講解焦點與時間連續性")
else:print(f"通過：{args.config}，語意狀態與時間連續性；未提供逐段焦點核對表")
