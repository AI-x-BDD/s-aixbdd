"""產生 CH2 的受控配色比較；不覆寫既有候選或重建影片。"""
from pathlib import Path
import importlib.util
import json
import math
import sys
import xml.etree.ElementTree as ET

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / 'videos/scripts'))
import video
from visual_motion import state_svg

spec = importlib.util.spec_from_file_location('ch2_design', HERE / 'design.py')
design = importlib.util.module_from_spec(spec)
spec.loader.exec_module(design)
OUT = ROOT / 'videos/build/ch2-workflow-test/預覽/適配比較'


def oklch(lightness, chroma, hue):
    """固定 OKLCH L/C 比較色相；轉成可用的 sRGB 色碼。"""
    a, b = chroma * math.cos(math.radians(hue)), chroma * math.sin(math.radians(hue))
    l = (lightness + .3963377774*a + .2158037573*b)**3
    m = (lightness - .1055613458*a - .0638541728*b)**3
    s = (lightness - .0894841775*a - 1.2914855480*b)**3
    linear = (4.0767416621*l - 3.3077115913*m + .2309699292*s,
              -1.2684380046*l + 2.6097574011*m - .3413193965*s,
              -.0041960863*l - .7034186147*m + 1.7076147010*s)
    assert all(0 <= v <= 1 for v in linear), linear
    rgb = [round(255*(12.92*v if v <= .0031308 else 1.055*v**(1/2.4)-.055)) for v in linear]
    return '#' + ''.join(f'{v:02X}' for v in rgb)


def luminance(color):
    rgb = [int(color[i:i+2], 16)/255 for i in (1, 3, 5)]
    rgb = [v/12.92 if v <= .04045 else ((v+.055)/1.055)**2.4 for v in rgb]
    return sum(v*w for v, w in zip(rgb, (.2126, .7152, .0722)))


def contrast(a, b):
    hi, lo = sorted((luminance(a), luminance(b)), reverse=True)
    return round((hi+.05)/(lo+.05), 2)


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    neutral = dict(bg='#F5F4F0', surface='#E5E6E4', ink='#252B31', muted='#48515A',
                   line='#9DA5AA', white='#FFFFFF', accent=design.PALETTES['a']['accent'])
    cases = [
        ('original', '原 A：紙色／深綠／陶土', design.PALETTES['a']),
        ('neutral', '中性底／陶土：只比較基底系統', neutral),
        ('blue', '中性底／藍：L .50、C .10、h 260', dict(neutral, accent=oklch(.50, .10, 260))),
        ('ochre', '中性底／赭黃：L .50、C .10、h 75', dict(neutral, accent=oklch(.50, .10, 75))),
        ('gray', '中性底／灰：L .50、C 0，無彩對照', dict(neutral, accent=oklch(.50, 0, 0))),
    ]
    states = [('02', ['forms-head', 'p0'], '密集資訊：用途說明'),
              ('04', ['after'], '規則拆分：新舊不靠紅綠'),
              ('07', ['step', 'write', 'back'], '回接：連線與讀取時機')]
    inventory = []
    for key, title, palette in cases:
        folder = OUT / key
        (folder / 'SVG').mkdir(parents=True, exist_ok=True)
        design.P = palette
        for frame, active, label in states:
            root = ET.fromstring(design.scene(frame, 'a'))
            svg = state_svg(root, {'active': active}, .85)
            ET.register_namespace('', 'http://www.w3.org/2000/svg')
            ET.ElementTree(svg).write(folder/'SVG'/f'{frame}.svg', encoding='unicode')
        video.frames(folder, {'slides': 'SVG'}, [{'frame': f} for f, _, _ in states], folder, folder)
        # 固定三張次序，讓每一行可直接對照同樣內容。
        args = []
        for frame, _, _ in states:
            args += ['-i', folder/'靜幀'/f'{frame}.png']
        video.ffmpeg(*args, '-filter_complex',
                     '[0:v]scale=640:360[a];[1:v]scale=640:360[b];[2:v]scale=640:360[c];[a][b][c]hstack=inputs=3',
                     '-frames:v', '1', folder/'三幕.png')
        checks = {f'{a}/{b}': contrast(palette[a], palette[b]) for a, b in
                  [('ink', 'bg'), ('ink', 'surface'), ('muted', 'bg'), ('muted', 'surface'),
                   ('accent', 'bg'), ('accent', 'surface'), ('white', 'accent')]}
        inventory.append(dict(key=key, title=title, palette=palette, contrast=checks))
    (OUT/'比較設定.json').write_text(json.dumps(inventory, ensure_ascii=False, indent=2)+'\n')
    print(OUT)


if __name__ == '__main__':
    main()
