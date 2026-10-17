"""驗證正式九幕語意聚焦、背景繪製順序與既有配音時間的相容性。"""
import argparse
import copy
import json
import sys
from pathlib import Path
import xml.etree.ElementTree as ET

HOME = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(HOME/'scripts'))
import video
import visual_motion

root, materials, content, data, out, config = video.load(argparse.Namespace(config='projects/ch2-skill-engineering/project.toml',source_root=None))
video.check(root, materials, content, data, out, config)
rows = video.recorded_timeline(data, materials, config)
spec = json.loads((materials/config['visuals']).read_text())
assert len(rows)==len(spec['frames'])==9
for row in rows:
    svg = ET.parse(materials/config['slides']/f"{row['frame']}.svg").getroot()
    events = visual_motion.timeline(video, row, spec['frames'][row['frame']],data['fps'])
    assert events[0]['start']==row['start'] and events[-1]['end']==row['end']
    assert all(a['end']==b['start'] for a,b in zip(events,events[1:]))
    for event in events:
        visual_motion.state_svg(svg,event['step'],spec['inactive_opacity'])
    # 改錯部位的名稱必須失敗，避免畫面未聚焦卻默默產出。
    if row['frame']=='03':
        try:
            visual_motion.state_svg(svg,{'active':['missing-node']},.7)
            raise AssertionError('未拒絕不存在的聚焦節點')
        except ValueError:
            pass
form = ET.parse(materials/config['slides']/'02.svg').getroot()
steps = spec['frames']['02']
expected = [('用途說明讓',0),('SOP 寫清楚',1),('規則附',2),('樣板提供',3),('腳本則',4)]
for phrase,active in expected:
    assert any(s.get('phrase')==phrase and s.get('primitive')==active for s in steps)
    svg = visual_motion.state_svg(form,{'primitive':active},.7)
    order=list(svg.iter());nodes={n.get('id'):n for n in order if n.get('id')}
    assert 'focus-bar' not in nodes
    assert nodes['focus-panel'].get('fill')=='#E7EDFF'
    assert nodes['focus-panel'].get('y')==nodes[f'form-{active}'].get('data-y')
    assert all(order.index(nodes['focus-panel'])<order.index(nodes[f'form-{j}']) for j in range(5))
    assert nodes[f'form-{active}'].get('opacity')=='1'
    assert all(n.get('fill')=='#315FF4' for n in nodes[f'form-{active}'] if n.tag.endswith('text'))
# 使用者發現的遮蓋問題：模擬把背景放到最後，建置應直接拒絕。
bad = copy.deepcopy(form)
parent = next(n for n in bad.iter() if any(c.get('id')=='focus-panel' for c in n))
panel=next(c for c in parent if c.get('id')=='focus-panel')
parent.remove(panel);parent.append(panel)
try:
    visual_motion.primitive_state(bad,0)
    raise RuntimeError('未阻擋背景遮住文字的退化')
except AssertionError as exc:
    assert '聚焦背景' in str(exc)
print('通過：九幕狀態時間連續、聚焦節點存在、五個 Form 完整、背景不遮字、錯誤圖層與節點受阻擋。')
# 四步光區必須逐一跟著當前步驟；不能永久停在 SOP，也不能蓋字。
workflow=ET.parse(materials/config['slides']/'03.svg').getroot()
for key in ('s0','s1','s2','s3'):
    svg=visual_motion.state_svg(workflow,{'active':[key]},spec['inactive_opacity'])
    panels=[n for n in svg.iter() if n.get('data-active-only')]
    assert len(panels)==4
    assert [n.get('data-active-only') for n in panels if n.get('opacity')=='1']==[key]
    group=next(n for n in svg.iter() if n.get('data-focus')==key)
    assert group[0].get('data-active-only')==key
    assert any(n.tag.endswith('text') and n.get('fill')=='#234DCB' for n in group)
# 新增的視覺標記必須被真正的語音狀態使用，而非永遠不會亮起的裝飾。
for row in rows:
    source=ET.parse(materials/config['slides']/f"{row['frame']}.svg").getroot()
    keys={n.get('data-active-only') for n in source.iter() if n.get('data-active-only')}
    states=[visual_motion.state_svg(source,s,spec['inactive_opacity']) for s in spec['frames'][row['frame']]]
    for key in keys:
        assert any(any(n.get('data-active-only')==key and n.get('opacity')=='1' for n in s.iter()) for s in states), (row['frame'],key)
print('通過：四步光區依序切換、當前標題顯著、背景先於文字、各幕光區確實可達。')
# Deriver 不能只降低左欄透明度：右欄背景、箭頭、目標部位必須同步。
for name,index,y in [('derive-rule',2,526),('derive-template',3,627),('derive-script',4,728)]:
    svg=visual_motion.state_svg(form,{'primitive':name},.58)
    nodes={n.get('id'):n for n in svg.iter() if n.get('id')}
    assert nodes['focus-panel'].get('opacity')=='0'
    assert nodes['derive-panel'].get('opacity')=='1'
    assert nodes['derive-panel'].get('y')==str(y)
    assert nodes['derive-panel'].get('height')=='100'
    assert nodes[f'part-{index}'].get('opacity')=='1'
    assert all(n.get('fill')=='#315FF4' for n in nodes[f'derive-{index}'] if n.tag.endswith('text'))
    assert all(nodes[f'derive-{j}'].get('opacity')==('1' if j==index else str(.58)) for j in range(2,5))
endcard=ET.parse(materials/config['slides']/'08.svg').getroot()
branch=next(n for n in endcard.iter() if n.get('id')=='output-branches')
import re
segments=re.findall(r'M(\d+) (\d+)([HV])(\d+)',branch.get('d'))
horizontal=[(min(int(x),int(end)), max(int(x),int(end)),int(y)) for x,y,axis,end in segments if axis=='H']
vertical=[(int(x),int(y),int(end)) for x,y,axis,end in segments if axis=='V']
assert len(horizontal)==1 and len(vertical)==3
left,right,bus_y=horizontal[0]
assert all(left<=x<=right and y==bus_y and end>bus_y for x,y,end in vertical)
assert len([1 for x,y,end in vertical if end==523])==3
print('通過：Deriver 三個背景／箭頭／目標同步，結尾三個分支均接上同一水平線。')
# 整頁依旁白覆蓋分組總覽、五項列舉、五項詳解及三項 Deriver；不能只驗證後半段。
expected_intro=[('先看兩種分工','overview'),('一組是格式把關','forms'),('用途說明、執行流程',0),('執行流程、規則',1),('規則、樣板',2),('樣板和腳本',3),('腳本。用途',4)]
assert [(s['phrase'],s['primitive']) for s in spec['frames']['02'][:7]]==expected_intro
for active,left,right in [('overview',True,True),('forms',True,False),('derivers',False,True),(0,True,False),('derive-rule',False,True)]:
    svg=visual_motion.state_svg(form,{'primitive':active},.58)
    order=list(svg.iter());nodes={n.get('id'):n for n in order if n.get('id')}
    for group,selected in [('form',left),('derive',right)]:
        assert nodes[f'{group}-title-panel'].get('opacity')==('1' if selected else '0')
        assert order.index(nodes[f'{group}-title-panel'])<order.index(nodes[f'{group}-heading'])
        if selected:
            assert all(nodes[f'{group}-{part}'].get('fill')=='#315FF4' for part in ('heading','count'))
print('通過：整頁旁白覆蓋分組標題與數量、開頭五項列舉、後段逐項解說；標題背景不遮字。')
