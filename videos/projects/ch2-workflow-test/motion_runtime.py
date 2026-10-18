"""Remotion 執行環境與來源指紋；不改使用者全域 Node 設定。"""
import hashlib
import os
from pathlib import Path
import shutil
import subprocess
import video
MOTION=video.HOME/'motion'


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def node():
    candidates=[os.environ.get('NODE_BINARY'),shutil.which('node')]
    versions=Path.home()/'.nvm/versions/node'
    if versions.exists():
        candidates += [str(p/'bin/node') for p in sorted(versions.iterdir(),key=lambda p:tuple(int(v) for v in p.name.lstrip('v').split('.')),reverse=True)]
    for candidate in filter(None,candidates):
        try:
            version=subprocess.check_output([candidate,'--version'],stderr=subprocess.DEVNULL,text=True).strip()
            if int(version.lstrip('v').split('.')[0])>=22:return candidate
        except (OSError,ValueError,subprocess.CalledProcessError):pass
    raise RuntimeError('缺少可執行的 Node.js 22+；請 nvm use 24 或指定 NODE_BINARY')


def environment(executable):
    env=os.environ.copy();env['PATH']=str(Path(executable).parent)+os.pathsep+env.get('PATH','')
    return env


def fingerprints(materials,content,config,args):
    paths=[content,materials/config['alignment'],video.audio_path(materials,config),
           video.HOME/config['focus_contract'],Path(__file__).parent/'motion-focus.json',Path(__file__).parent/'motion-labels.json',MOTION/'public/segments.json',MOTION/'public/正式旁白.m4a',
           MOTION/'package.json',MOTION/'package-lock.json',MOTION/'remotion.config.ts',MOTION/'tsconfig.json']
    paths += list((MOTION/'src').glob('*.ts'))+list((MOTION/'src').glob('*.tsx'))+list((MOTION/'scripts').glob('*.cjs'))
    paths += list(Path(__file__).parent.glob('*motion*.py'))
    paths += [video.HOME/'scripts/video.py', Path(__file__).parent/'burn_subtitles.py']
    profile=Path(args.config)
    paths.append(profile if profile.is_absolute() else video.HOME/profile)
    return {str(p.resolve()):sha(p) for p in paths}


def audio_stream_hash(path):
    return subprocess.check_output(['ffmpeg','-v','error','-xerror','-i',str(path),'-map','0:a:0','-c:a','copy',
                                   '-f','hash','-hash','sha256','-'],text=True).strip()
