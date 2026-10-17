"""將語音詞時間對應到 SVG 語意部位，供完整影片與樣片共用。"""
import copy
import json
from pathlib import Path
import xml.etree.ElementTree as ET


def primitive_state(svg, active, dim=.70):
    nodes = {n.get('id'): n for n in svg.iter() if n.get('id')}
    order = list(svg.iter())
    assert all(order.index(nodes['focus-panel']) < order.index(nodes[f'form-{i}']) for i in range(5)), '聚焦背景必須先於所有 Form 文字繪製'
    accent, ink = svg.get('data-accent'), svg.get('data-ink')
    individual = isinstance(active, int)
    derive_index = {'derive-rule':2, 'derive-template':3, 'derive-script':4}.get(active)
    deriving = active == 'derivers' or derive_index is not None
    # 分組介紹的標題與數量也有可見焦點，不能只讓下方欄位變淡。
    for group, focused in (
        ('form', active in ('overview', 'forms') or individual),
        ('derive', active == 'overview' or deriving),
    ):
        if f'{group}-title-panel' in nodes:
            nodes[f'{group}-title-panel'].set('opacity', '1' if focused else '0')
            for suffix in ('heading', 'count'):
                node = nodes[f'{group}-{suffix}']
                node.set('fill', accent if focused else ink)
                node.set('opacity', '1' if focused or active is None else str(dim))
    for i in range(5):
        selected = individual and active == i
        opacity = '1' if selected or active in (None, 'forms') else str(dim)
        nodes[f'form-{i}'].set('opacity', opacity)
        for node in nodes[f'form-{i}']:
            if node.tag.endswith('text'):
                node.set('fill', accent if selected else ink)
        nodes[f'link-{i}'].set('stroke', accent if selected else '#CFD6DF')
        nodes[f'link-{i}'].set('stroke-width', '3' if selected else '2')
        nodes[f'dot-{i}'].set('fill', accent if selected else '#CFD6DF')
        part = nodes[f'part-{i}']
        part_selected = selected or derive_index == i
        part.set('opacity', '1' if part_selected or (active == 'derivers' and i >= 2) else opacity)
        for node in part:
            if node.get('data-part-fill'):
                node.set('fill', accent if part_selected else ('#EDF0F4' if i < 2 else '#FFFFFF'))
                if i >= 2:
                    node.set('stroke', accent if part_selected else '#CFD6DF')
            if node.tag.endswith('text'):
                node.set('fill', '#FFFFFF' if part_selected else ink)
    nodes['derivers'].set('opacity', '1' if active is None or deriving else str(dim))
    if 'derive-panel' in nodes:
        panel = nodes['derive-panel']
        panel.set('opacity', '1' if deriving else '0')
        panel.set('y', str(526 + (derive_index-2)*101) if derive_index is not None else '526')
        panel.set('height', '100' if derive_index is not None else '306')
        for i in range(2,5):
            selected = active == 'derivers' or derive_index == i
            nodes[f'derive-{i}'].set('opacity', '1' if selected or active is None else str(dim))
            for child in nodes[f'derive-{i}']:
                if child.tag.endswith('text'):
                    child.set('fill', accent if selected else ink)
                elif child.tag.endswith('path'):
                    child.set('stroke', accent if selected else '#626D7A')
                    child.set('stroke-width', '3' if selected else '2')
    nodes['focus-panel'].set('opacity', '1' if individual else '0')
    if individual:
        nodes['focus-panel'].set('y', nodes[f'form-{active}'].get('data-y'))


def state_svg(root, step, dim):
    svg = copy.deepcopy(root)
    if any(n.get('id') == 'form-0' for n in svg.iter()):
        primitive_state(svg, step.get('primitive'), dim)
    else:
        active = set(step.get('active', []))
        available = {key for node in svg.iter() for key in node.get('data-focus', '').split()}
        if active - available:
            raise ValueError(f'圖稿缺少聚焦部位：{active - available}')
        for node in svg.iter():
            keys = set(node.get('data-focus', '').split())
            if keys:
                node.set('opacity', '1' if not active or keys & active else str(dim))
                selected = bool(keys & active)
                for child in node.iter():
                    for attr in ('fill', 'stroke'):
                        value = child.get(f'data-active-{attr}')
                        if selected and value:
                            child.set(attr, value)
            only = set(node.get('data-active-only', '').split())
            if only:
                node.set('opacity', '1' if only & active else '0')
    return svg


def timeline(video, row, steps, fps):
    events = [{'start': row['start'], 'step': {}}]
    last_offset = -1
    for step in steps:
        offset = row['text'].index(step['phrase'])
        if offset <= last_offset:
            raise ValueError('視覺聚焦必須依旁白順序，且每個起點只能有一個狀態')
        last_offset = offset
        start = max(row['start'], video.text_time(row, offset) - .04)
        start = min(row['end'] - 1/fps, round(start*fps)/fps)
        event = {'start': round(start, 3), 'step': step}
        if start <= events[-1]['start'] + .001:
            events[-1] = event
        else:
            events.append(event)
    for i, event in enumerate(events):
        event['end'] = events[i+1]['start'] if i+1 < len(events) else row['end']
        if event['end'] <= event['start']:
            raise ValueError('視覺狀態時間沒有前進')
    return events


def prepare(video, materials, config, data, rows, work):
    spec = json.loads((materials/config['visuals']).read_text())
    source, raster = work/'視覺狀態/SVG', work/'視覺狀態/轉圖'
    for folder in (source, raster):
        folder.mkdir(parents=True, exist_ok=True)
    ET.register_namespace('', 'http://www.w3.org/2000/svg')
    result = []
    for row in rows:
        root = ET.parse(materials/config['slides']/f"{row['frame']}.svg").getroot()
        events = timeline(video, row, spec['frames'][row['frame']], data['fps'])
        for i, event in enumerate(events):
            name = f"{row['frame']}-{i:02}"
            event['frame'] = name
            svg = state_svg(root, event['step'], spec['inactive_opacity'])
            ET.ElementTree(svg).write(source/f'{name}.svg', encoding='unicode')
        result.append(events)
    video.frames(work/'視覺狀態', {'slides':'SVG'}, [e for group in result for e in group], work/'視覺狀態', raster)
    (work/'視覺狀態/時間軸.json').write_text(json.dumps(result, ensure_ascii=False, indent=2)+'\n')
    return result, spec


def encode(video, data, row, events, spec, work, target):
    length = row['voice_seconds']
    inputs = []
    for event in events:
        inputs += ['-loop','1','-framerate',str(data['fps']),'-t',str(length),'-i',str(work/'視覺狀態/靜幀'/f"{event['frame']}.png")]
    filters = [f'[{i}:v]format=yuv420p,settb=AVTB,setpts=PTS-STARTPTS[v{i}]' for i in range(len(events))]
    previous = 'v0'
    for i in range(1, len(events)):
        offset = events[i]['start']-row['start']
        transition = min(spec['transition_seconds'], (events[i]['start']-events[i-1]['start'])/2)
        filters.append(f'[{previous}][v{i}]xfade=transition=fade:duration={transition:.6f}:offset={offset-transition:.6f}[x{i}]')
        previous = f'x{i}'
    video.ffmpeg(*inputs,'-filter_complex_threads','1','-filter_complex',';'.join(filters),'-map',f'[{previous}]',
                 '-t',str(length),'-r',str(data['fps']),'-c:v','libx264','-preset','veryfast',
                 '-crf','20','-pix_fmt','yuv420p','-threads','2',target)
