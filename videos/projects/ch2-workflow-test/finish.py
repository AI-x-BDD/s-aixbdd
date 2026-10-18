"""匯出已選定 B 的交付頁、實際畫格與可追溯檢查；不重新編輯配音。"""
import argparse
from pathlib import Path
import hashlib
import importlib.util
import json
import shutil
import subprocess
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(HERE))
from burn_subtitles import burn
spec = importlib.util.spec_from_file_location('ch2_preview', HERE/'preview.py')
preview = importlib.util.module_from_spec(spec)
spec.loader.exec_module(preview)
FINAL = preview.BUILD/'正式版'
RECORDS = ROOT/'docs/過程/CH2/影片/製作紀錄/設計/新流程測試'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def delivery(evidence, entry="基準.html"):
    version = evidence['video_sha256'][:12]
    target = preview.OUT/'製作歷程'
    target.mkdir(exist_ok=True)
    for source in RECORDS.glob('*.md'):
        shutil.copy2(source, target/source.name)
    comparison = ' · <a href="index.html">查看原候選與配色比較</a>' if (preview.OUT/'index.html').exists() else ''
    motion_comparison = '<p><a href="../動態提案/index.html">有聲動態比較：目前 B／連續焦點／動態敘事</a></p>' if (preview.BUILD/'動態提案/index.html').exists() else ''
    body = f'''<!doctype html><html lang="zh-Hant"><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1"><title>CH2｜B 深色版測試影片</title>
<style>body{{background:#201D31;color:#F4F0FF;font:18px/1.7 system-ui,"PingFang TC",sans-serif;margin:0}}main{{max-width:1080px;margin:auto;padding:30px 24px}}h1{{line-height:1.3}}a{{color:#D8EF8A}}video,img{{width:100%;display:block}}.status{{background:#373249;padding:16px 22px;border-left:4px solid #D8EF8A}}small{{color:#C4BDD5}}li{{margin:12px 0}}details{{margin:28px 0}}</style>
<main><h1>CH2｜B 固定構圖焦點基準</h1><p>此頁保存先前版本；<a href="交付.html">最新動態敘事交付</a>以另一頁為準。</p>
<p class="status">已依選定深色方向完成逐段焦點修訂，片長 1 分 53 秒，字幕已燒錄。<br>畫格、來源與檔案檢查已執行；AI 未直接聽審聲音或連續觀看全片，聽感與觀看舒適度待你試看確認。</p>
<video controls preload="metadata" poster="正式版/scene-02.png?v={version}" src="../正式版/輸出/影片.mp4?v={version}"></video>
<p><a href="../正式版/輸出/影片.mp4?v={version}" download="CH2-B深色版.mp4">下載完整影片</a>{comparison}</p>
<h2>這次實際經過的流程</h2><ol>
<li>先確認內容與限制：保留九幕、原配音與 113 秒時間。</li>
<li>逐段核對 49 段旁白的預期焦點，修正列舉漏項、錯時焦點與淡化疊字。</li>
<li>本基準以明確指定 focus-baseline.toml 重建；自動燒錄字幕並驗證來源、音檔與片長。</li>
<li>完整解碼、逐段中點／尾端抽幀與本機全片語音辨識，分開記錄能力與未驗證範圍。</li>
<li>實作有旁白的連續移動、形變與二維鏡頭候選；使用者後續已選 M2 全片，詳見最新交付頁。</li></ol>{motion_comparison}
<p><a href="../正式版/預覽/聲畫稽核/index.html">全片逐段旁白與焦點稽核</a></p><h2>九幕總覽</h2><a href="正式版/跨幕.png"><img src="正式版/跨幕.png?v={version}" alt="B 深色版九幕實際影片畫格"></a>
<details><summary>檢查範圍與製作紀錄</summary>
<p>字幕已燒錄在下方獨立字幕帶，無須開啟字幕軌；{evidence['duration']:.2f} 秒、1600×900、25fps。圖解等比縮小保留全部內容，避免字幕遮住圖解。音檔雜湊與版控的對齊資料一致，完整解碼通過。</p>
<p>檢查 {evidence['states']} 個語意狀態及 {evidence['transitions']} 個過渡中點；畫面以逐項聚焦與直接切換呈現，已取消容易疊字的淡化；連續物件動態另有候選比較。AI 未直接聽看全片，不能宣稱整體聲畫或使用者驗收通過。</p>
<p><a href="正式版/狀態總覽.png">狀態總覽</a> · <a href="正式版/過渡總覽.png">過渡總覽</a> · <a href="製作歷程/分鏡.md">逐幕分鏡</a> · <a href="製作歷程/B定版評審.md">原版評審（歷史）</a> · <a href="製作歷程/交付狀態.md">交付狀態</a></p></details>
<p><small>方向選擇已完成；目前待完整影片的使用者驗收，不是再次確認是否製作。</small></p></main></html>'''
    (preview.OUT/entry).write_text(body)


def main():
    global FINAL, RECORDS
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--config',default='projects/ch2-workflow-test/project.toml')
    parser.add_argument('--source-root')
    args=parser.parse_args()
    root, materials, content, data, FINAL, config=preview.video.load(args)
    RECORDS=materials/'製作紀錄/設計/新流程測試'
    preview.BUILD=FINAL.parent
    preview.OUT=preview.BUILD/'預覽'
    preview.OUT.mkdir(parents=True,exist_ok=True)
    selected = json.loads((HERE/'選定方向.json').read_text())
    assert selected['direction'] == 'b', '目前交付器只適用已確認的 B 方向'
    burn(FINAL)
    preview.export('正式版', FINAL)
    alignment = json.loads((materials/config['alignment']).read_text())
    audio = FINAL/'中間產物/完整-03修正版.m4a'
    assert alignment['audio_sha256'] == sha(audio), '正式配音與已確認對齊資料不一致'
    mp4 = FINAL/'輸出/影片.mp4'
    info = json.loads(subprocess.check_output(['ffprobe','-v','quiet','-show_format','-show_streams','-of','json',str(mp4)]))
    duration = float(info['format']['duration'])
    assert abs(duration-113) < .04, '片長與確認範圍不符'
    assert {s['codec_type'] for s in info['streams']} == {'video','audio'}
    video = next(s for s in info['streams'] if s['codec_type']=='video')
    assert (video['width'], video['height'], video['r_frame_rate']) == (1600,900,'25/1')
    sources = materials/'製作來源/畫面'
    after = sources/'新流程測試定版'
    hashes = {str(path.relative_to(after)): sha(path)
              for path in [*after.glob('圖稿/*.svg'), after/'視覺設定.json']}
    assert hashes == selected['source_sha256'], '正式來源與選定 B 的來源清單不一致'
    evidence = dict(direction='b', duration=duration, states=len(list((preview.OUT/'正式版').glob('state-*.png'))),
                    transitions=len(list((preview.OUT/'正式版').glob('transition-*.png'))),
                    audio_sha256=sha(audio), video_sha256=sha(mp4), sources=hashes, subtitles='burned',
                    listening='未直接聽審', continuous_viewing='未連續觀看全片', acceptance='待使用者')
    events=json.loads((FINAL/'中間產物/視覺狀態/時間軸.json').read_text())
    assert evidence['states']==sum(map(len,events)) and evidence['transitions']==sum(len(g)-1 for g in events)
    if config.get('focus_contract'):
        preview.video.run([sys.executable,ROOT/'videos/scripts/review.py','--config',args.config,
                           *(['--source-root',args.source_root] if args.source_root else []),'--capture'])
    (FINAL/'驗證.json').write_text(json.dumps(evidence,ensure_ascii=False,indent=2)+'\n')
    entry=Path(config.get('preview_entry','預覽/基準.html')).name
    delivery(evidence,entry)
    print(preview.OUT/entry)


if __name__=='__main__':
    main()
