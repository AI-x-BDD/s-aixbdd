"""匯出已選定 B 的交付頁、實際畫格與可追溯檢查；不重新編輯配音。"""
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


def delivery(evidence):
    version = evidence['video_sha256'][:12]
    target = preview.OUT/'製作歷程'
    target.mkdir(exist_ok=True)
    for source in RECORDS.glob('*.md'):
        shutil.copy2(source, target/source.name)
    comparison = ' · <a href="index.html">查看原候選與配色比較</a>' if (preview.OUT/'index.html').exists() else ''
    body = f'''<!doctype html><html lang="zh-Hant"><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1"><title>CH2｜B 深色版測試影片</title>
<style>body{{background:#201D31;color:#F4F0FF;font:18px/1.7 system-ui,"PingFang TC",sans-serif;margin:0}}main{{max-width:1080px;margin:auto;padding:30px 24px}}h1{{line-height:1.3}}a{{color:#D8EF8A}}video,img{{width:100%;display:block}}.status{{background:#373249;padding:16px 22px;border-left:4px solid #D8EF8A}}small{{color:#C4BDD5}}li{{margin:12px 0}}details{{margin:28px 0}}</style>
<main><h1>CH2｜B 深色系統路由</h1>
<p class="status">已依你選定的深色方向輸出測試片，片長 1 分 53 秒，字幕已燒錄。<br>畫格、來源與檔案檢查已執行；AI 未直接聽審聲音或連續觀看全片，聽感與觀看舒適度待你試看確認。</p>
<video controls preload="metadata" poster="正式版/scene-02.png?v={version}" src="../正式版/輸出/影片.mp4?v={version}"></video>
<p><a href="../正式版/輸出/影片.mp4?v={version}" download="CH2-B深色版.mp4">下載完整影片</a>{comparison}</p>
<h2>這次實際經過的流程</h2><ol>
<li>先確認內容與限制：保留九幕、原配音與 113 秒時間。</li>
<li>製作 A／B 候選，發現配色判斷證據不足後退回；修改流程、補比較與 C 候選。</li>
<li>你選定深色 B；凍結來源與逐幕分鏡，產生獨立正式測試輸出。</li>
<li>檢查完整檔案，從正式 MP4 擷取九幕、所有語意狀態與過渡，記錄結果與限制。</li>
<li>現在請看完整片，回覆是否達到你想測的品質；有問題可附時間點，我會依回饋修正。</li></ol>
<h2>九幕總覽</h2><a href="正式版/跨幕.png"><img src="正式版/跨幕.png?v={version}" alt="B 深色版九幕實際影片畫格"></a>
<details><summary>檢查範圍與製作紀錄</summary>
<p>字幕已燒錄在下方獨立字幕帶，無須開啟字幕軌；{evidence['duration']:.2f} 秒、1600×900、25fps。圖解等比縮小保留全部內容，避免字幕遮住圖解。音檔雜湊與版控的對齊資料一致，完整解碼通過。</p>
<p>檢查 {evidence['states']} 個語意狀態及 {evidence['transitions']} 個過渡中點；畫面以揭露與 0.20 秒淡化呈現，過渡會短暫疊字，沒有物件連續移動。AI 未直接聽看全片，不能宣稱整體聲畫或使用者驗收通過。</p>
<p><a href="正式版/狀態總覽.png">狀態總覽</a> · <a href="正式版/過渡總覽.png">過渡總覽</a> · <a href="製作歷程/分鏡.md">逐幕分鏡</a> · <a href="製作歷程/B定版評審.md">本次評審</a> · <a href="製作歷程/交付狀態.md">交付狀態</a></p></details>
<p><small>方向選擇已完成；目前待完整影片的使用者驗收，不是再次確認是否製作。</small></p></main></html>'''
    (preview.OUT/'交付.html').write_text(body)


def main():
    selected = json.loads((HERE/'選定方向.json').read_text())
    assert selected['direction'] == 'b', '目前交付器只適用已確認的 B 方向'
    burn(FINAL)
    preview.export('正式版', FINAL)
    alignment = json.loads((ROOT/'docs/過程/CH2/影片/製作來源/配音/對齊/對齊.json').read_text())
    audio = FINAL/'中間產物/完整-03修正版.m4a'
    assert alignment['audio_sha256'] == sha(audio), '正式配音與已確認對齊資料不一致'
    mp4 = FINAL/'輸出/影片.mp4'
    info = json.loads(subprocess.check_output(['ffprobe','-v','quiet','-show_format','-show_streams','-of','json',str(mp4)]))
    duration = float(info['format']['duration'])
    assert abs(duration-113) < .04, '片長與確認範圍不符'
    assert {s['codec_type'] for s in info['streams']} == {'video','audio'}
    video = next(s for s in info['streams'] if s['codec_type']=='video')
    assert (video['width'], video['height'], video['r_frame_rate']) == (1600,900,'25/1')
    sources = ROOT/'docs/過程/CH2/影片/製作來源/畫面'
    after = sources/'新流程測試定版'
    hashes = {str(path.relative_to(after)): sha(path)
              for path in [*after.glob('圖稿/*.svg'), after/'視覺設定.json']}
    assert hashes == selected['source_sha256'], '正式來源與選定 B 的來源清單不一致'
    evidence = dict(direction='b', duration=duration, states=len(list((preview.OUT/'正式版').glob('state-*.png'))),
                    transitions=len(list((preview.OUT/'正式版').glob('transition-*.png'))),
                    audio_sha256=sha(audio), video_sha256=sha(mp4), sources=hashes, subtitles='burned',
                    listening='未直接聽審', continuous_viewing='未連續觀看全片', acceptance='待使用者')
    assert evidence['states']==36 and evidence['transitions']==27
    (FINAL/'驗證.json').write_text(json.dumps(evidence,ensure_ascii=False,indent=2)+'\n')
    delivery(evidence)
    print(preview.OUT/'交付.html')


if __name__=='__main__':
    main()
