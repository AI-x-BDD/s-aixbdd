"""建置已確認的 B 動態敘事全片，驗證後才更新交付入口。"""
import argparse
import fcntl
import json
from pathlib import Path
import subprocess
import sys
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parents[1]/'scripts'))
import video
from prepare_motion import prepare
import motion_runtime as runtime


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--config',default='projects/ch2-workflow-test/project.toml');p.add_argument('--source-root')
    p.add_argument('--prepare-only',action='store_true')
    args=p.parse_args()
    _,_,_,_,out,_=video.load(args)
    out.mkdir(parents=True,exist_ok=True)
    with (out/'.build.lock').open('w') as lock:
        try:fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
        except BlockingIOError:raise RuntimeError('動態正式版正在建置，請等待完成')
        root,materials,content,data,out,config,rows=prepare(args)
        if args.prepare_only:return
        executable=runtime.node();env=runtime.environment(executable)
        video.run([executable,runtime.MOTION/'node_modules/typescript/bin/tsc','--noEmit'],cwd=runtime.MOTION,env=env)
        before=runtime.fingerprints(materials,content,config,args)
        work=out/'中間產物';candidate=work/'待驗證影片.mp4';silent=work/'動態無聲.mp4'
        video.run([executable,runtime.MOTION/'node_modules/@remotion/cli/remotion-cli.js','render','src/index.ts',
                   'Full-Motion',silent,'--muted','--log=info'],cwd=runtime.MOTION,env=env)
        # 最後一次只封裝，不重新編碼原配音或已燒錄字幕的畫面。
        video.ffmpeg('-i',silent,'-i',video.audio_path(materials,config),'-map','0:v:0','-map','1:a:0',
                     '-c','copy','-t',rows[-1]['end'],'-movflags','+faststart',candidate)
        if before!=runtime.fingerprints(materials,content,config,args):raise RuntimeError('建置期間來源改動，停止交付')
        (out/'來源指紋.json').write_text(json.dumps(before,ensure_ascii=False,indent=2)+'\n')
        import review_motion
        evidence=review_motion.review(args,movie=candidate,capture=True)
        candidate.replace(out/'輸出/影片.mp4')
        review_motion.delivery(out,evidence,materials)
        print('動態正式片：'+str(out/'輸出/影片.mp4'),flush=True)

if __name__=='__main__':main()
