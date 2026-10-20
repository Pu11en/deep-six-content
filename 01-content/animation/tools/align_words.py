#!/usr/bin/env python3
"""Word timings for an approved narration MP3: step 1 of the MP3-to-MP4 video flow.

Three offline faster-whisper models (small.en, medium.en, large-v3-turbo) each transcribe the MP3
with word timestamps. Each transcript is aligned to the approved script; the median start per
script word is kept and then snapped to measured silences. Caption groups of one to four words
are built automatically. No network, no paid service.

Usage:
  python3 tools/align_words.py --manifest ../audio/<id>/<run>/comparison.json --out episodes/<id>/full/words.json
"""
import argparse
import difflib
import hashlib
import json
import re
import statistics
import subprocess
import sys
import tempfile
from pathlib import Path

MODELS = ['small.en', 'medium.en', 'mobiuslabsgmbh/faster-whisper-large-v3-turbo']
FUNCTION_WORDS = {'a', 'an', 'the', 'of', 'to', 'in', 'and', 'or', 'for', 'its', 'their', 'your', 'from', 'at', 'on', 'by', 'with', 'as'}


def norm(word):
    return re.sub(r"[^a-z0-9']", '', word.lower().replace('’', "'"))


def transcribe(wav, name):
    from faster_whisper import WhisperModel
    model = WhisperModel(name, device='cpu', compute_type='int8', local_files_only=True)
    segments, _ = model.transcribe(str(wav), language='en', word_timestamps=True, beam_size=5, vad_filter=False)
    words = []
    for segment in segments:
        for w in segment.words:
            parts = [p for p in re.split(r'[\s\-]+', w.word.strip()) if norm(p)]
            step = (w.end - w.start) / max(1, len(parts))
            for i, part in enumerate(parts):
                words.append((w.start + i * step, w.start + (i + 1) * step, part))
    return words


def silences(wav):
    out = subprocess.run(['ffmpeg', '-hide_banner', '-i', str(wav), '-af', 'silencedetect=noise=-38dB:d=0.12', '-f', 'null', '-'],
                         capture_output=True, text=True).stderr
    values = [float(v) for v in re.findall(r'silence_(?:start|end): ([0-9.]+)', out)]
    return list(zip(values[0::2], values[1::2]))


STARTERS = {'and', 'or', 'but', 'than', 'for', 'to', 'of', 'in', 'where', 'while', 'as', 'rather', 'not', 'what', 'that',
            'from', 'during', 'into', 'become', 'are', 'is', 'can', 'doesn\'t', 'between', 'within', 'about', 'below', 'above'}


def caption_groups(words):
    """One to four words per group. Break after punctuation and pauses, before linking words,
    and at about 22 characters; never end a group on a short function word."""
    groups, current = [], []
    for i, w in enumerate(words):
        if current:
            prev = words[current[-1]]
            text = ' '.join(words[j]['text'] for j in current + [i])
            hard = re.search(r'[.,:;!?]$', prev['text']) or w['start'] - prev['end'] > 0.25
            soft = norm(w['text']) in STARTERS and len(current) >= 2
            full = len(current) >= 4 or len(text) > 22
            if hard or soft or full:
                if not hard and len(current) > 2 and norm(words[current[-1]]['text']) in FUNCTION_WORDS:
                    groups.append(current[:-1])
                    current = [current[-1]]
                else:
                    groups.append(current)
                    current = []
        current.append(i)
    if current:
        groups.append(current)
    return [{'words': g} for g in groups]


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('--manifest', required=True, type=Path, help='approved audio comparison.json')
    parser.add_argument('--out', required=True, type=Path)
    args = parser.parse_args()

    manifest = json.loads(args.manifest.read_text())
    if manifest.get('audio_review', {}).get('status') != 'approved':
        sys.exit('The narration audio is not approved.')
    variant = next(v for v in manifest['variants'] if v['name'] == manifest['audio_review']['approved_variant'])
    audio = args.manifest.parent / variant['audio_file']
    digest = hashlib.sha256(audio.read_bytes()).hexdigest()
    if digest != variant['audio_sha256']:
        sys.exit('Approved audio fingerprint changed.')
    script = (args.manifest.parent / 'original.txt').read_text().replace('’', "'")
    tokens = script.split()
    target = [norm(t) for t in tokens]

    with tempfile.TemporaryDirectory() as tmp:
        wav = Path(tmp) / 'audio16k.wav'
        subprocess.run(['ffmpeg', '-hide_banner', '-loglevel', 'error', '-y', '-i', str(audio), '-ac', '1', '-ar', '16000', str(wav)], check=True)
        quiet = silences(wav)
        starts = [[] for _ in tokens]
        ends = [[] for _ in tokens]
        votes = {}
        for name in MODELS:
            heard = transcribe(wav, name)
            matcher = difflib.SequenceMatcher(a=target, b=[norm(h[2]) for h in heard], autojunk=False)
            matched = 0
            for block in matcher.get_matching_blocks():
                for k in range(block.size):
                    starts[block.a + k].append(heard[block.b + k][0])
                    ends[block.a + k].append(heard[block.b + k][1])
                    matched += 1
            votes[name] = matched
            print(json.dumps({'model': name, 'matched': matched, 'of': len(tokens)}), flush=True)

    words = []
    for i, token in enumerate(tokens):
        words.append({'text': token, 'start': statistics.median(starts[i]) if starts[i] else None,
                      'end': statistics.median(ends[i]) if ends[i] else None, 'votes': len(starts[i])})
    for i, w in enumerate(words):
        if w['start'] is None:
            w['start'] = next((words[j]['end'] for j in range(i - 1, -1, -1) if words[j]['end'] is not None), 0.0)
            w['end'] = next((words[j]['start'] for j in range(i + 1, len(words)) if words[j]['start'] is not None), w['start'] + 0.2)
    for s0, s1 in quiet:
        for i in range(len(words) - 1):
            a, b = words[i], words[i + 1]
            if abs(s0 - a['end']) < 0.3 and abs(s1 - b['start']) < 0.35 and a['end'] - 0.25 <= s0 <= b['start'] + 0.25:
                a['end'] = s0
                b['start'] = s1 - 0.01
    for i in range(len(words) - 1):
        if words[i]['end'] > words[i + 1]['start']:
            words[i]['end'] = words[i + 1]['start']
        if words[i]['end'] <= words[i]['start']:
            words[i]['end'] = words[i]['start'] + 0.05
    clean = [{'text': w['text'], 'start': round(w['start'], 2), 'end': round(w['end'], 2)} for w in words]
    low = [w['text'] for w in words if w['votes'] < 2]
    out = {
        'audio': str(Path('..') / '..' / '..' / '..' / 'audio' / Path(*args.manifest.parent.parts[-2:]) / variant['audio_file']),
        'audio_sha256': digest,
        'excerpt': ' '.join(tokens),
        'excerpt_start_seconds': 0,
        'excerpt_end_seconds': round(variant['duration_seconds'], 3),
        'method': 'Median word start of three offline faster-whisper models aligned to the approved script, snapped to ffmpeg silencedetect (-38 dB, 0.12 s). Machine alignment, not a human listening check.',
        'model_votes': votes,
        'low_confidence_words': low,
        'silences_seconds': [[round(a, 3), round(b, 3)] for a, b in quiet],
        'words': clean,
        'caption_groups': caption_groups(clean),
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(out, indent=1) + '\n')
    print(json.dumps({'words': len(clean), 'caption_groups': len(out['caption_groups']), 'low_confidence': low, 'out': str(args.out)}))


if __name__ == '__main__':
    main()
