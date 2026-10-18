"""從候選 MP4 擷取有聲片段與實際畫格，建立本輪評閱入口。"""
from pathlib import Path
import json
import math
import hashlib
import re
import subprocess
import sys
import xml.etree.ElementTree as ET

ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT/'videos/scripts'))
import video
from visual_motion import state_svg

BUILD=ROOT/'videos/build/ch2-workflow-test'
OUT=BUILD/'預覽'
OUT.mkdir(parents=True,exist_ok=True)
TIMES=[.8,9.5,22.5,51.5,62.5,80,90,100,110]


def run(*args):
    subprocess.run([str(a) for a in args],check=True)


def image_at(mp4,time,target):
    video.ffmpeg('-ss',time,'-i',mp4,'-frames:v','1','-update','1',target)


def export(candidate, folder=None):
    folder=folder or BUILD/'提案'/candidate
    mp4=folder/'輸出/影片.mp4'
    images=OUT/candidate
    images.mkdir(exist_ok=True)
    for pattern in ("state-*.png", "transition-*.png"):
        for stale in images.glob(pattern):stale.unlink()
    # 有聲節錄全部保留來源中的對應時間，不拼接或重配音。
    video.ffmpeg('-ss','53.04','-i',mp4,'-t','17.40','-c:v','libx264','-preset','fast','-crf','20','-c:a','aac','-b:a','192k','-movflags','+faststart',images/'節奏預覽.mp4')
    rows=json.loads((folder/'預覽/時間軸.json').read_text())
    for i,t in enumerate(TIMES):image_at(mp4,t,images/f'scene-{i:02}.png')
    video.ffmpeg('-framerate','1','-i',images/'scene-%02d.png','-vf','scale=480:270,tile=3x3:padding=6:margin=6:color=white','-frames:v','1','-update','1',images/'跨幕.png')
    states=json.loads((folder/'中間產物/視覺狀態/時間軸.json').read_text())
    inventory=[]
    for events in states:
        for event in events:
            # 從 MP4 取樣，避免只檢查未經編碼的 SVG。
            t=(event['start']+event['end'])/2
            name=f"state-{len(inventory):02}.png"
            image_at(mp4,t,images/name)
            inventory.append(dict(file=name,time=round(t,3),state=event['frame'],phrase=event['step'].get('phrase','開場狀態')))
    (images/'畫格索引.json').write_text(json.dumps(inventory,ensure_ascii=False,indent=2)+'\n')
    video.ffmpeg('-framerate','1','-i',images/'state-%02d.png','-vf',f'scale=400:225,tile=4x{math.ceil(len(inventory)/4)}:padding=4:margin=4:color=white','-frames:v','1','-update','1',images/'狀態總覽.png')
    # 淡化中點亦從成片抽查，不拿靜幀冒充過渡。
    transitions=[e for g in states for e in g[1:]]
    manifest=json.loads((folder/'來源指紋.json').read_text()) if (folder/'來源指紋.json').exists() else {}
    visual_paths=[Path(p) for p in manifest if p.endswith('視覺設定.json')]
    fade=json.loads(visual_paths[0].read_text()).get('transition_seconds',.2) if visual_paths else .2
    for i,e in enumerate(transitions):image_at(mp4,max(0,e['start']-fade/2),images/f'transition-{i:02}.png')
    video.ffmpeg('-framerate','1','-i',images/'transition-%02d.png','-vf',f'scale=400:225,tile=4x{max(1,math.ceil(len(transitions)/4))}:padding=4:margin=4:color=white','-frames:v','1','-update','1',images/'過渡總覽.png')
    video.ffmpeg('-i',mp4,'-f','null','-')
    return rows


def palette():
    folder=ROOT/'docs/過程/CH2/影片/製作來源/畫面/設計提案/workflow-test-a-color-b/圖稿'
    work=BUILD/'中間產物/配色對照'
    (work/'SVG').mkdir(parents=True,exist_ok=True)
    svg=state_svg(ET.parse(folder/'02.svg').getroot(),{'active':['forms-head','p0']},.85)
    ET.register_namespace('','http://www.w3.org/2000/svg')
    ET.ElementTree(svg).write(work/'SVG/02.svg',encoding='unicode')
    video.frames(work,{'slides':'SVG'},[{'frame':'02'}],work,work)
    run('cp',work/'靜幀/02.png',OUT/'同構圖-B配色.png')
    # A 的同一 p0 狀態，取實際編碼約 21 秒畫面。
    image_at(BUILD/'提案/a/輸出/影片.mp4',21.05,OUT/'同構圖-A配色.png')


def page(rows):
    styles='''body{margin:0;background:#f5f3ee;color:#1c342d;font-family:system-ui,"PingFang TC",sans-serif;line-height:1.7}main{max-width:1200px;margin:auto;padding:32px 24px}h1{font-size:36px;line-height:1.3}h2{margin-top:48px}p{max-width:900px}.status{background:#e5ebdf;padding:18px 24px;border-left:5px solid #8b452c}.grid{display:grid;grid-template-columns:1fr 1fr;gap:24px}img,video{display:block;width:100%;height:auto;background:#211d31}figure{margin:0}figcaption{padding:10px 0;font-weight:600}.note{font-size:15px;color:#52645a}a{color:#7f3822}section{scroll-margin-top:20px}.frames{display:grid;grid-template-columns:repeat(3,1fr);gap:12px}.frames figcaption{font-size:14px}nav a{margin-right:22px}@media(max-width:760px){.grid,.frames{grid-template-columns:1fr}h1{font-size:28px}}'''
    body='''<h1>CH2 新流程測試：先比較實際方向</h1><p class="status"><strong>目前：已補適配比較，C 修訂候選可確認視覺方向。</strong><br>這裡的影片是獨立測試建置，尚未定版。補做 15 張配色比較及靜態評審後，推薦 C「中性文件圖解」。藍與赭黃皆可成立，色相屬美術裁量。請比較實際影片後確認 C 視覺方向或說明調整；確認後依既有授權繼續定版。</p><nav><a href="#experience">製作歷程</a><a href="#directions">候選有聲預覽</a><a href="#colors">單獨比較配色</a><a href="#shots">跨幕構圖</a></nav>
    <section id="experience"><h2>你會經歷什麼</h2><ol><li><strong>AI 先讀內容：</strong>確認理解目標與限制。本次維持原旁白、113 秒和既有配音。</li><li><strong>你看具體提案（現在）：</strong>比較配色、構圖與有聲片段，AI 提推薦；你只要說偏好或哪裡不對。</li><li><strong>AI 完成逐幕製作：</strong>依確認方向定版九幕，核對焦點及配音時間，自行處理設計細節。</li><li><strong>AI 複查，你驗收成片：</strong>交付完整片、修正紀錄與未驗證範圍；你評估是否改善樣板感。</li></ol><p class="note">已讀取四支設計 Skill；本輪已補配色與結構的比較評審。聲音與連續動態未直接聽看，0.20 秒淡化有短暫疊字；不能視為完整聲畫驗收。能力限制：目前為逐步揭露與淡化，沒有連續物件變形；AI 未直接聽審，聲音自然度與聲畫舒適度請試看片段判斷。</p></section>
    <section id="directions"><h2>同一段內容，C 修訂與 A／B 原候選</h2><p>53.04–70.44 秒：「檔案拆出去，流程也要接回來」。同一正式配音、17.40 秒，請開聲音觀看。回接線在旁白說到更新流程時揭露。</p><div class="grid">'''
    for key,title,desc in [('c','C｜中性文件圖解・本輪推薦','保留 A 的文件、分流與索引結構；中性底與文字，藍色只標示當下解說。這是比較後的美術取捨，不宣稱藍色是內容唯一正解。'),('a','A｜原編輯式工程圖解','紙色 × 深綠 × 陶土色。文件層次、責任分開與回接關係；保留供追溯比較。'),('b','B｜深色系統路由','深紫 × 淡紫 × 黃綠。橫向路徑、模組與分岔；委派感更強，整體較像系統面板。')]:
        body+=f'<article><h3>{title}</h3><p>{desc}</p><video controls preload="metadata" poster="{key}/scene-04.png" src="{key}/節奏預覽.mp4"></video><p><a href="../提案/{key}/輸出/影片.mp4">全長候選 113 秒（尚未定版）</a></p></article>'
    body+='''</div></section><section id="colors"><h2>這次怎麼選配色</h2><p>內容要求的是辨識文件責任、拆分與回接，來源沒有指定綠、紫或藍。先固定構圖比較基底，再固定中性底比較焦點色。藍與赭黃的 OKLCH 明度、彩度相同；灰色是無彩對照。這些是渲染靜幀，並非全部另做影片。</p><p>每列依序為密集 Form、規則拆分、流程回接。灰焦點的文字與次文字較接近；有彩焦點多一個辨識線索。藍與赭黃皆可用，C 的藍色是美術選擇，沒有客觀勝過赭黃的證據。規則拆分圖仍依位置及標籤辨識新舊，沒有用紅綠編碼新增刪除。</p>'''
    for item in json.loads((OUT/'適配比較/比較設定.json').read_text()):
        body+=f'<figure><a href="適配比較/{item["key"]}/三幕.png"><img src="適配比較/{item["key"]}/三幕.png" alt="{item["title"]}三段代表內容"></a><figcaption>{item["title"]}</figcaption></figure>'
    body+='''<details><summary>舊 A/B 整套配色對照及限制</summary><p>此對照同時換明暗和色相，只能比較整套效果，不能單獨證明某個色相較好。</p><div class="grid"><figure><img src="同構圖-A配色.png" alt="A 構圖與 A 配色"><figcaption>紙色、深綠、陶土色</figcaption></figure><figure><img src="同構圖-B配色.png" alt="同一構圖改用 B 配色"><figcaption>深紫、淡紫、黃綠</figcaption></figure></div></details></section><section id="shots"><h2>看跨幕，而不只看漂亮的單張</h2><p>三個案例分別呈現規則分層、任務分岔、責任索引。下圖全部從實際候選 MP4 擷取；點圖看原尺寸。</p>'''
    for key,name in [('c','C：中性文件圖解'),('a','A：原文件結構與閱讀層次'),('b','B：路由、模組與分支')]:
        body+=f'<h3>{name}</h3><a href="{key}/跨幕.png"><img src="{key}/跨幕.png" alt="{name}九幕總覽"></a><details><summary>逐幕看實際畫面</summary><div class="frames">'
        for i,row in enumerate(rows):body+=f'<figure><a href="{key}/scene-{i:02}.png"><img loading="lazy" src="{key}/scene-{i:02}.png" alt="{row["title"]}"></a><figcaption>{i+1}. {row["title"]}</figcaption></figure>'
        body+='</div></details>'
    body+='''</section><h2>現在確認視覺方向</h2><p class="status">推薦 C 的文件結構與中性底／藍色焦點。請回到對話回覆「採用 C」，或描述想調整的地方；也可選相同結構的赭黃焦點。這次只確認視覺方向，聲音與連續動態尚未直接聽看，正式全片仍待定版。確認後依既有授權繼續，不再問是否開始。</p><p class="note">技術檢查與 AI 視覺檢查的範圍，另記於來源目錄「製作紀錄／設計／新流程測試／美術評審.md」。使用者最終驗收尚未完成。</p>'''
    selected=Path(__file__).parent/'選定方向.json'
    if selected.exists():
        body=body.replace('C｜中性文件圖解・本輪推薦','C｜中性文件圖解・先前推薦').replace('你看具體提案（現在）：','你看具體提案：')
        status='<p class="status"><strong>已選定 B「深色系統路由」。</strong><br>使用者已確認深色方向。<a href="交付.html">開啟 B 版完整影片與檢查結果</a>。以下 A／B／C 與配色比較保留為製作歷程，不再要求選版。</p>'
        body=re.sub(r'<p class="status">.*?</p>',status,body,count=1,flags=re.S)
        body=re.sub(r'<h2>現在確認視覺方向</h2><p class="status">.*?</p>','<h2>方向已確認</h2>'+status,body,flags=re.S)
    revision=hashlib.sha256(b''.join((BUILD/f'提案/{k}/輸出/影片.mp4').read_bytes() for k in ['a','b','c'])).hexdigest()[:10]
    body=re.sub(r'(src|poster)="([^"]+)"',lambda m:f'{m[1]}="{m[2]}?v={revision}"',body)
    (OUT/'index.html').write_text('<!doctype html><html lang="zh-Hant"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>CH2 新流程測試</title><style>'+styles+'.grid article p:first-of-type{min-height:58px}</style><main>'+body+'</main></html>')


if __name__=='__main__':
    rows=export('a')
    export('b')
    export('c')
    palette()
    page(rows)
    print(OUT/'index.html')
