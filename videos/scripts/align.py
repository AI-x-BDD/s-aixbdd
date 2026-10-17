"""以本機 MLX Whisper 的詞時間對齊既有旁白稿，保留原稿文字。"""
import argparse
from difflib import SequenceMatcher
import hashlib
import json
import os
from pathlib import Path
import unicodedata
from opencc import OpenCC

CONVERTER = OpenCC("t2s")


def normalized(text):
    return ''.join(c for c in CONVERTER.convert(unicodedata.normalize('NFKC', text)).lower() if c.isalnum())


def align(content, raw):
    expected = ''.join(normalized(s['text']) for s in content['scenes'])
    observed, times = '', []
    for segment in raw['segments']:
        for word in segment.get('words', []):
            text = normalized(word['word'])
            for i, char in enumerate(text):
                observed += char
                times.append((word['start'] + (word['end']-word['start'])*i/len(text),
                              word['start'] + (word['end']-word['start'])*(i+1)/len(text)))
    matcher = SequenceMatcher(None, expected, observed, autojunk=False)
    anchors = {}
    for block in matcher.get_matching_blocks():
        for i in range(block.size):
            anchors[block.a+i] = times[block.b+i]
    if not anchors or len(anchors)/len(expected) < .8:
        raise ValueError('辨識文字與原稿差異過大，請檢查音檔與辨識結果')
    # 少數辨識異字以相鄰已匹配詞時間內插；不改寫顯示文字。
    keys = sorted(anchors)
    mapped = []
    for i in range(len(expected)):
        if i in anchors:
            mapped.append(anchors[i]); continue
        left = max((k for k in keys if k < i), default=None)
        right = min((k for k in keys if k > i), default=None)
        start = anchors[left][1] if left is not None else 0
        end = anchors[right][0] if right is not None else times[-1][1]
        count = (right if right is not None else len(expected)) - (left if left is not None else -1) - 1
        offset = i - (left if left is not None else -1) - 1
        mapped.append((start+(end-start)*offset/count, start+(end-start)*(offset+1)/count))
    scenes, cursor = [], 0
    for scene in content['scenes']:
        chars = []
        for pos, char in enumerate(scene['text']):
            for _ in normalized(char):
                start, end = mapped[cursor]
                chars.append({'offset': pos, 'start': round(start, 3), 'end': round(end, 3)})
                cursor += 1
        scenes.append({'frame': scene['frame'], 'text': scene['text'], 'characters': chars,
                       'speech_start': chars[0]['start'], 'speech_end': chars[-1]['end']})
    return {'method': 'whisper-word-timestamps-and-transcript-matching',
            'matched_character_ratio': round(len(anchors)/len(expected), 4),
            'unmatched_ranges': [{'text': expected[a:b], 'recognized': observed[c:d]}
                                 for tag,a,b,c,d in matcher.get_opcodes() if tag != 'equal'],
            'scenes': scenes}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--audio', required=True)
    parser.add_argument('--content', required=True)
    parser.add_argument('--output', required=True)
    parser.add_argument('--model', default='mlx-community/whisper-large-v3-turbo')
    args = parser.parse_args()
    audio, content_path, output = map(Path, [args.audio, args.content, args.output])
    content = json.loads(content_path.read_text())
    digest = hashlib.sha256(audio.read_bytes()).hexdigest()
    cache = Path(__file__).resolve().parents[1]/'build/alignment'/f'{digest}.json'
    cache.parent.mkdir(parents=True, exist_ok=True)
    if cache.exists():
        raw = json.loads(cache.read_text())
    else:
        os.environ.setdefault("HF_HOME", str(Path(__file__).resolve().parents[1]/".cache/huggingface"))
        import mlx_whisper
        raw = mlx_whisper.transcribe(str(audio), path_or_hf_repo=args.model,
                                    language='zh', word_timestamps=True, verbose=None,
                                    initial_prompt='繁體中文。Skill Engineering、AI、SOP、Form、Deriver。',
                                    condition_on_previous_text=False, temperature=0.0)
        cache.write_text(json.dumps(raw, ensure_ascii=False, indent=2)+'\n')
    result = align(content, raw)
    result.update(audio_sha256=digest, content_sha256=hashlib.sha256(content_path.read_bytes()).hexdigest())
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, ensure_ascii=False, indent=2)+'\n')
    print(json.dumps({k:v for k,v in result.items() if k != 'scenes'}, ensure_ascii=False), flush=True)


if __name__ == '__main__':
    main()
