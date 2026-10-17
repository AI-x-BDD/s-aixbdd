"""CH2 新流程測試的候選圖稿；從 repo 根目錄以 videos/.venv/bin/python 執行。"""
from pathlib import Path
from html import escape
import json

ROOT = Path(__file__).resolve().parents[3]
MAT = ROOT / 'docs/過程/CH2/影片'
BASE = MAT / '製作來源/畫面/設計提案'
PROFILES = Path(__file__).parent / 'proposals'
PALETTES = {
    'a': dict(bg='#F4F0E6', surface='#E5E9DF', ink='#173F35', muted='#43574C', accent='#9B452C', white='#FFFFFF', line='#9CA99A'),
    'b': dict(bg='#201D31', surface='#373249', ink='#F4F0FF', muted='#C4BDD5', accent='#D8EF8A', white='#201D31', line='#847B97'),
    'c': dict(bg='#F5F4F0', surface='#E5E6E4', ink='#252B31', muted='#48515A', accent='#40639C', white='#FFFFFF', line='#9DA5AA'),
}


def text(x, y, value, size=32, color=None, weight=400, face='PingFang TC', **attrs):
    extra = ' '.join(f'{k.replace("_", "-")}="{v}"' for k, v in attrs.items())
    return f'<text x="{x}" y="{y}" font-family="{face}" font-size="{size}" font-weight="{weight}" fill="{color or P["ink"]}" {extra}>{escape(value)}</text>'


def rect(x, y, w, h, fill=None, stroke='none', **attrs):
    extra = ' '.join(f'{k.replace("_", "-")}="{v}"' for k, v in attrs.items())
    return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{fill or P["surface"]}" stroke="{stroke}" {extra}/>'


def line(x1, y1, x2, y2, color=None, width=2):
    return f'<path d="M{x1} {y1} L{x2} {y2}" fill="none" stroke="{color or P["line"]}" stroke-width="{width}"/>'


def path(d, color=None, width=3):
    return f'<path d="{d}" fill="none" stroke="{color or P["accent"]}" stroke-width="{width}"/>'


def group(key, body, only=False):
    if only:
        return f'<g data-focus="{key}"/><g data-active-only="{key}">{body}</g>'
    return f'<g data-focus="{key}">{body}</g>'


def focus_text(x,y,label,size=48):
    return text(x,y,label,size,weight=600,data_active_fill=P['accent'])


def tag(x, y, w, label, key, h=86):
    return group(key, rect(x,y,w,h, data_active_fill=P['accent']) + text(x+25,y+h/2+12,label,34,weight=600,data_active_fill=P['white']))


def page(x, y, w, h, label, lines):
    s = rect(x,y,w,h,P['bg'],P['line']) + text(x+25,y+50,label,29,weight=600)
    for i, v in enumerate(lines):
        s += line(x+25,y+80+i*65,x+w-25,y+80+i*65) + text(x+25,y+123+i*65,v,28)
    return s


def header(title, eyebrow):
    # 不把共用頁首當成主角；開場、結語另作整頁構圖。
    return text(90,85,eyebrow,24,P['muted'],600,letter_spacing=3) + text(90,168,title,58,weight=600) + line(90,205,1510,205)


def wrap(body):
    return '<svg xmlns="http://www.w3.org/2000/svg" width="1600" height="900" viewBox="0 0 1600 900"><g font-family="PingFang TC">' + rect(0,0,1600,900,P['bg']) + body + '</g></svg>\n'


def scene(frame, layout):
    b = ''
    if frame == '00':
        b += text(90,280,'技能越改',112,weight=700) + text(90,430,'越難維護？',112,weight=700)
        b += line(95,500,670,500,P['ink'],4)
        b += page(1000,155,450,575,'SKILL.md',['流程','規則','範例','例外','輸出格式'])
    elif frame == '01':
        b += header('把修改工作交給對的技能','SKILL ENGINEERING')
        if layout == 'a':
            b += text(100,335,'建立／優化',40) + text(100,448,'需求',78,weight=600)
            b += line(440,415,590,415)
            b += group('eng',rect(590,305,520,220)+text(625,385,'Skill Engineering',42,weight=600)+focus_text(625,460,'安排工作',56))
            b += line(1110,415,1200,415)
            b += group('parts',text(1200,390,'基礎技能',44,weight=600)+text(1200,450,'分工完成',34))
            b += text(1280,510,'↓',32)+text(1160,570,'新的／改寫後 Skill',27,P['muted'])
            b += group('out',focus_text(590,710,'接下來：分工方式 × 三支案例',45),True)
        else:
            b += text(100,350,'輸入',30,P['muted'])+text(100,420,'建立／優化需求',48,weight=600)
            b += group('eng',tag(640,285,760,'Skill Engineering：安排工作','eng',120))
            b += group('parts',tag(640,455,760,'Form ＋ Deriver：分工完成','parts',120))
            b += text(640,650,'產出新的／改寫後的 Skill',36,weight=600)
            b += group('out',line(640,705,1400,705)+focus_text(640,780,'接下來：分工方式 × 三支案例',38))
            b += path('M530 395 V345 H640 M1020 410 V450 M1020 580 V610',P['line'])
            b += text(1030,437,'↓',32)+text(1030,607,'↓',32)
    elif frame == '02':
        b += header('兩種分工，處理不同問題','FORM × 5  /  DERIVER × 3')
        labels=['用途說明','執行流程','規則','樣板','腳本']
        details=['何時使用這支 Skill？','實際執行哪些步驟？','判斷依據與正反例','輸出骨架與完成範例','輸入、輸出與執行方式']
        if layout == 'a':
            b += group('forms-head',text(90,315,'格式把關',56,weight=600)+text(90,375,'五個部位，各有責任',32,P['muted']),True)
            b += group('overview',text(90,345,'格式把關 × 5',57,weight=600)+text(90,475,'部位抽取 × 3',57,weight=600)+text(90,565,'兩組技能，兩種工作',34,P['muted']),True)
            for i,(label,detail) in enumerate(zip(labels,details)):
                y=260+i*98
                b += tag(790,y,265,label,f'p{i}',82)+text(1085,y+52,detail,28)
                b += group(f'p{i}',text(90,510,label,76,P['accent'],600)+text(95,585,detail,36),True)
            b += group('derive',text(90,315,'部位抽取',56,P['accent'],600)+text(90,375,'三種工作，從步驟分出部位',32,P['muted'])+rect(90,435,630,235)+text(125,510,'從流程步驟分出：',32)+text(125,600,'規則 ／ 樣板 ／ 腳本',42,weight=600),True)
            b += text(790,830,'Form 把關內容格式；Deriver 拆出並接回流程',28,P['muted'])
        else:
            b += '<g data-focus="forms-head"/>'
            b += text(90,290,'FORM：把關各部位格式',36,weight=600)
            b += group('overview',text(90,545,'格式把關 × 5　／　部位抽取 × 3',52,weight=600),True)
            for i,label in enumerate(labels):
                x=90+i*290
                b += tag(x,330,260,label,f'p{i}',112)
                b += group(f'p{i}',text(100,545,label+'：'+details[i],56,P['accent'],600),True)
            b += group('derive',text(90,540,'DERIVER：從流程分出部位',48,P['accent'],600)+tag(90,610,400,'規則抽取','derive')+tag(585,610,400,'樣板抽取','derive')+tag(1080,610,400,'腳本抽取','derive'),True)
            b += text(90,805,'五個格式責任，三種抽取工作；兩組不是同一套分類。',32,P['muted'])
    elif frame == '03':
        b += header('先找原因，再決定怎麼改','OPTIMIZATION / 先確認，再施工')
        entries=[('預期','哪裡不滿意？'),('根因','差異怎麼來？'),('修改計畫','確認後才動手'),('整理 SOP','逐步判斷部位')]
        for i,(label,detail) in enumerate(entries):
            x=90+i*370; y=390 if layout=='a' else 280+i*110
            if layout=='a':
                b += group(f'v{i}',group(f's{i}',focus_text(x,y-35,f'0{i+1}',80)+focus_text(x,y+55,label,47)+text(x,y+112,detail,29)),True)
                if i<3:b += line(x+280,y+35,x+330,y+35)
            else:
                b += group(f'v{i}',group(f's{i}',rect(450,y,1000,95)+focus_text(490,y+62,f'0{i+1}   {label}',40)+text(900,y+62,detail,31,P['muted'])),True)
        b += text(90,810,'根因與修改計畫確認，是開始施工的前提。',32,P['muted'])
    elif frame == '07':
        b += header('拆出規則，也要接回讀取時機','EXTRACTION / 產出檔案只是其中一步')
        if layout == 'a':
            b += group('step',page(90,275,470,365,'SOP',['步驟：需要更多判斷規則']))
            b += group('extract',focus_text(690,325,'規則抽取',43)+text(690,380,'derive-rule',29,P['muted'])+line(560,350,660,350)+text(635,360,'›',40))
            b += group('write',page(1100,275,410,235,'規則檔',['form-rule 寫好規則'])+line(1000,350,1090,350)+text(1060,360,'›',40),True)
            b += group('back',path('M1300 530 V665 H325 V610',width=7)+path('M313 630 L325 610 L337 630',width=5)+text(680,625,'form-sop 接回流程',37,P['accent'],600)+text(680,705,'交代載入時機與使用方式',31)+text(115,455,'讀取：何時讀、怎麼用',28),True)
        else:
            b += group('step',tag(90,290,410,'SOP：需要更多規則','step',115))
            b += line(500,350,590,350)+group('extract',tag(590,290,390,'derive-rule','extract',115))
            b += group('write',line(980,350,1070,350)+tag(1070,290,440,'form-rule 寫規則','write',115),True)
            b += group('back',path('M1290 405 V625 H295 V405',width=7)+path('M283 425 L295 405 L307 425',width=5)+rect(590,535,580,120)+text(625,610,'form-sop：接回讀取時機',38,P['accent'],600),True)
        b += group('branches',text(90,795,'需要固定輸出 → 抽取樣板　／　需要自動處理 → 抽取腳本',30,P['muted']),True)
        b += group('existing',text(90,850,'既有檔案只改內容 → 直接交給 Form',30,P['accent'],600),True)
    elif frame == '04':
        b += header('慣例式提交：依決策分開規則','CASE 01 / 主檔帶流程，規則按需讀取')
        if layout=='a':
            b += group('before',page(90,275,450,440,'原本：主檔混寫',['分類','訊息格式','範例']))
            b += group('after',text(690,300,'SOP',54,weight=600)+line(730,335,730,745),True)
            for i,label in enumerate(['變更分類','提交訊息','歷史處理']):
                y=355+i*135
                b += group('after',line(730,y+43,850,y+43)+rect(850,y,660,86)+text(885,y+56,label,40,weight=600)+(text(1220,y+56,'需要時',28,P['muted']) if i==2 else ''),True)
        else:
            b += group('before',rect(90,280,310,460)+text(120,345,'原本混寫',40,weight=600)+text(120,435,'分類',40)+text(120,510,'訊息格式',40)+text(120,585,'範例',40))
            b += group('after',text(500,335,'現在：在對的決策點讀取',45,weight=600),True)
            for i,label in enumerate(['變更分類','提交訊息','歷史處理']):
                x=500+i*340
                b += group('after',line(x,455,x+240,455)+text(x,550,label,40,weight=600)+text(x,620,'需要時讀取' if i==2 else '獨立規則檔',28,P['muted']),True)
    elif frame == '05':
        b += header('主幹式開發：共通先讀，再依任務分流','CASE 02 / 共通判準 ＋ 任務規則')
        if layout=='a':
            b += group('common',rect(90,330,620,280)+text(125,405,'先讀',32,P['muted'])+text(125,490,'共通 TBD 判準',55,weight=600))
            b += group('task',path('M710 470 H830 M830 350 V650 M830 350 H970 M830 650 H970')+tag(970,295,540,'規劃 → 變更規劃','task',110)+rect(970,565,540,180,P['accent'])+text(995,610,'審查',34,P['white'],600)+text(995,670,'變更規劃',38,P['white'],600)+text(995,720,'＋工作流程評估',34,P['white']),True)
        else:
            b += group('common',tag(420,280,760,'每次先讀：共通 TBD 判準','common',120))
            b += group('task',path('M800 410 V495 M370 495 H1230 M370 495 V570 M1230 495 V570')+tag(90,570,560,'規劃：變更規劃','task',125)+rect(950,570,560,180,P['accent'])+text(980,620,'審查：變更規劃',38,P['white'],600)+text(980,685,'＋工作流程評估',38,P['white']),True)
    elif frame == '06':
        b += header('雙鑽石：流程與三類判斷各有位置','CASE 03 / 分開的是規則責任')
        if layout=='a':
            b += group('sop',focus_text(90,330,'主檔負責帶流程',64))
            b += text(1000,330,'判斷回到各自的規則檔',32,P['muted'])
            for i,(label,detail) in enumerate([('模型判準','理解雙鑽石'),('任務分流','判斷走哪條路'),('需求分析','分析與產出')]):
                x=90+i*510
                b += group('rules',line(x,470,x+400,470)+focus_text(x,565,label,53)+text(x,635,detail,33,P['muted'])+line(x,710,x+400,710))
        else:
            b += group('sop',focus_text(90,355,'SOP',95)+text(90,420,'主檔帶流程',36))
            for i,label in enumerate(['模型判準','任務分流','需求分析']):
                x=600+i*300
                b += group('rules',rect(x,280,270,410)+line(x+25,360,x+245,360)+focus_text(x+25,465,label,39)+text(x+25,625,'獨立規則',29,P['muted']))
        b += text(90,825,'這是檔案責任的分離；不是把雙鑽石模型改成固定階段。',29,P['muted'])
    elif frame=='08':
        b += text(90,160,'各自的用途，同一套整理方法',65,weight=600)
        for i,(label,detail,key) in enumerate([('Engineering','安排工作','flow0'),('Form ＋ Deriver','分工完成','flow1'),('SOP','在對的時機使用規則','flow2')]):
            y=290+i*160
            b += group(f'v{i}',group(key,text(90,y,label,52,weight=600)+line(650,y-15,760,y-15)+focus_text(800,y,detail,50)),True)
        b += line(90,735,1510,735)+text(90,810,'慣例式提交　／　主幹式開發　／　雙鑽石',36,P['muted'])
    return wrap(b)


STEPS={
 '00':[],
 '01':[('Skill Engineering',['eng']),('分派給對應的基礎技能',['eng','parts']),('接下來',['out'])],
 '02':[('先看兩種分工',['overview']),('一組是格式把關',['forms-head']),('用途說明讓',['forms-head','p0']),('SOP 寫清楚',['forms-head','p1']),('規則附',['forms-head','p2']),('樣板提供',['forms-head','p3']),('腳本則',['forms-head','p4']),('另一組是部位抽取',['derive'])],
 '03':[('收到優化需求',['v0','s0']),('再找出差異',['v0','v1','s1']),('根因和修改計畫',['v0','v1','v2','s2']),('接著整理',['v0','v1','v2','v3','s3'])],
 '07':[('例如',['step','extract']),('它請格式技能',['step','extract','write']),('再更新流程',['step','write','back']),('需要固定輸出',['step','write','back','branches']),('既有檔案只改內容',['step','write','back','existing'])],
 '04':[('這次三支技能',['before']),('現在拆成',['after'])],
 '05':[('主幹式開發',['common']),('先讀共通判準',['common']),('再依規劃',['common','task'])],
 '06':[('雙鑽石',['sop']),('主檔負責帶流程',['sop']),('各類判斷',['rules'])],
 '08':[('三支技能保留',['v0','v1','v2']),('技能工程安排工作',['v0','v1','v2','flow0']),('基礎技能分工完成',['v0','v1','v2','flow1']),('流程負責',['v0','v1','v2','flow2'])],
}


def main():
    global P
    data=json.loads((MAT/'製作來源/內容/製作內容.json').read_text())
    for candidate,layout,palette in [('a','a','a'),('b','b','b'),('a-color-b','a','b'),('c','a','c')]:
        P=PALETTES[palette]
        folder=BASE/('workflow-test-'+candidate)
        (folder/'圖稿').mkdir(parents=True,exist_ok=True)
        for row in data['scenes']:
            (folder/'圖稿'/f"{row['frame']}.svg").write_text(scene(row['frame'],layout))
        frames={key:[{'phrase':phrase,'active':active} for phrase,active in steps] for key,steps in STEPS.items()}
        # overview 是不改色、不顯示細節的總覽狀態，仍需語意節點存在。
        target=folder/'圖稿/02.svg'
        target.write_text(target.read_text().replace('</svg>','<g data-focus="overview"/></svg>'))
        (folder/'視覺設定.json').write_text(json.dumps({'transition_seconds':.20,'inactive_opacity':.85,'frames':frames},ensure_ascii=False,indent=2)+'\n')
        config=(ROOT/'videos/projects/ch2-skill-engineering/project.toml').read_text()
        relative=folder.relative_to(MAT).as_posix()
        config=config.replace('slides = "製作來源/畫面/圖稿"',f'slides = "{relative}/圖稿"')
        config=config.replace('output = "build/ch2-skill-engineering"',f'output = "build/ch2-workflow-test/提案/{candidate}"')
        config=config.replace('visuals = "製作來源/畫面/視覺設定.json"',f'visuals = "{relative}/視覺設定.json"')
        (PROFILES/f'{candidate}.toml').write_text(config)
    print('A／B 九幕候選、同構圖配色對照與 C 中性底修訂候選原稿已建立。')


if __name__=='__main__':
    main()
