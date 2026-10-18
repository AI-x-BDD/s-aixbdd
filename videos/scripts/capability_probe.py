"""實測本機成片抽幀與音訊辨識；不把辨識文字當成直接聽審。"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import sys
import time
import video


def main():
 p=argparse.ArgumentParser(description=__doc__)
 p.add_argument('--config',default='projects/ch2-workflow-test/project.toml')
 p.add_argument('--source-root')
 p.add_argument('--transcribe',action='store_true',help='以已存在的本機模型辨識全片，不下載模型')
 args=p.parse_args()
 _,materials,_,data,out,config=video.load(args)
 mp4=out/'輸出/影片.mp4';target=out/'預覽/能力實測';target.mkdir(parents=True,exist_ok=True)
 digest=hashlib.sha256(mp4.read_bytes()).hexdigest();length=video.duration(mp4)
 video.ffmpeg('-i',mp4,'-f','null','-')
 for stale in target.glob('frame-*.jpg'):stale.unlink()
 video.ffmpeg('-i',mp4,'-vf','fps=1,scale=800:450','-start_number',0,target/'frame-%03d.jpg')
 report={'video_sha256':digest,'duration':length,'frames':len(list(target.glob('frame-*.jpg'))),
         'visual_input':'已從全片每秒擷取一幀；可用 view_image 讀取，未逐影格觀看',
         'native_audio_input':'本對話未提供直接音訊輸入工具',
         'continuous_audiovisual_review':'未建立；不可宣稱已連續聽看',
         'transcription':'未執行','audio_naturalness':'未驗證','tool_probe_date':'2026-10-18'}
 if args.transcribe:
  model=video.HOME/'.cache/models/whisper-large-v3-turbo'
  if not (model/'config.json').exists():raise RuntimeError('缺少本機模型；不自動下載')
  import mlx_whisper
  start=time.monotonic()
  raw=mlx_whisper.transcribe(str(mp4),path_or_hf_repo=str(model),language='zh',word_timestamps=True,
       verbose=None,condition_on_previous_text=False,temperature=0.0,
       initial_prompt='繁體中文。Skill Engineering、AI、SOP、Form、Deriver。')
  (target/'全片辨識.json').write_text(json.dumps(raw,ensure_ascii=False,indent=2)+'\n')
  report.update(transcription='全片音訊本機辨識完成；非聽感評審',transcription_seconds=round(time.monotonic()-start,2),
                recognized_segments=len(raw['segments']),recognized_last_end=raw['segments'][-1]['end'])
 if hashlib.sha256(mp4.read_bytes()).hexdigest()!=digest:raise RuntimeError('實測期間影片已變更，證據失效')
 (target/'能力實測.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
 print(json.dumps(report,ensure_ascii=False))


if __name__=='__main__':main()
