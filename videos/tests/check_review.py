"""以實際旁白對齊與焦點核對表，測試漏焦點、提前結束及父群組染色的回歸。"""
import argparse
import copy
import json
from pathlib import Path
import sys
import xml.etree.ElementTree as ET
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
import review
import video
import visual_motion
args=argparse.Namespace(config=review.DEFAULT,source_root=None)
root,materials,path,data,out,config=video.load(args)
rows=video.recorded_timeline(data,materials,config)
spec=json.loads((materials/config['visuals']).read_text())
contract=json.loads((video.HOME/config['focus_contract']).read_text())
assert not any(e['issues'] for e in review.audit(data,rows,spec,contract))
# 重現五項列舉漏焦點：移掉 p0 狀態後，群組標題仍存在、時間仍連續，但必須被拒絕。
broken=copy.deepcopy(spec)
broken['frames']['02']=[s for s in broken['frames']['02'] if s['phrase']!='用途說明、執行流程']
assert any(e['issues'] for e in review.audit(data,rows,broken,contract))
# 提前切到下一個物件，即使所有事件仍存在也必須被抓出。
broken=copy.deepcopy(spec)
next(s for s in broken['frames']['02'] if s['phrase']=='用途說明讓')['active']=['forms-head','p1']
assert any(e['issues'] for e in review.audit(data,rows,broken,contract))
# 延後兩個字才開始聚焦也要失敗，不能用長過渡容錯掩蓋短漏焦點。
broken=copy.deepcopy(spec)
next(s for s in broken['frames']['02'] if s['phrase']=='用途說明讓')['phrase']='讓 AI 知道'
assert any(e['issues'] for e in review.audit(data,rows,broken,contract))
# 缺少場景與無理由的空焦點都不可默默通過。
for change in ['missing','empty','ambiguous']:
 bad=copy.deepcopy(contract)
 if change=='missing':bad.pop('08')
 elif change=='empty':bad['01'][0]['targets']=[]
 else:bad['02'][4]['phrase']='規則'
 try:review.audit(data,rows,spec,bad)
 except ValueError:pass
 else:raise AssertionError(change)
svg=ET.parse(materials/config['slides']/'04.svg').getroot()
state=visual_motion.state_svg(svg,{'active':['before','before-class']},.85)
texts={n.get('data-focus'):n for n in state.iter() if n.tag.endswith('text') and n.get('data-focus')}
assert texts['before-class'].get('fill')=='#D8EF8A'
assert texts['before-message'].get('fill')!='#D8EF8A'
print('通過：49 段焦點對照、漏列舉／錯對象／缺場景／空焦點阻擋、父群組不覆蓋細部焦點')
