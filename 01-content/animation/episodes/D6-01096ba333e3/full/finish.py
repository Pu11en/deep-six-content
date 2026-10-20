"""Finish D6-01096ba333e3: put the approved MP3 under the rendered picture unchanged, then check it.

The renderer's MP4 fades the last 80 ms of its audio. This step replaces that track with the approved MP3
decoded as-is (no fade, no gain, no retiming), padded with silence to the end of the picture.
Usage: python3 finish.py <revision>   e.g. v1"""
import hashlib
import json
import subprocess
import sys
from pathlib import Path

import numpy as np

here = Path(__file__).parent
rev = sys.argv[1]
render = here / 'renders' / f'full-{rev}.mp4'
mp3 = (here / '../../../../audio/D6-01096ba333e3/full-chris-01/ensign-wasp-chris.mp3').resolve()
out = here / 'renders' / f'ensign-wasp-{rev}-final.mp4'
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()
assert sha(mp3) == '48b3cd7ce950a65f51603f320868072966b0ce0e3532909df93b5878070b5710', 'approved MP3 changed'
assert not out.exists(), f'{out.name} exists; nothing overwritten'

probe = lambda p: json.loads(subprocess.run(['ffprobe', '-v', 'error', '-show_streams', '-show_format', '-of', 'json', str(p)],
                                            capture_output=True, text=True, check=True).stdout)
v = next(s for s in probe(render)['streams'] if s['codec_type'] == 'video')
video_seconds = int(v['nb_frames']) / 30
subprocess.run(['ffmpeg', '-hide_banner', '-loglevel', 'error', '-nostdin', '-n', '-i', str(render), '-i', str(mp3),
                '-map', '0:v:0', '-map', '1:a:0', '-c:v', 'copy', '-af', f'apad=whole_dur={video_seconds:.6f}',
                '-c:a', 'aac', '-b:a', '192k', '-ar', '44100', '-ac', '1', '-t', f'{video_seconds:.6f}',
                '-movflags', '+faststart', str(out)], check=True)

info = probe(out)
vs = next(s for s in info['streams'] if s['codec_type'] == 'video')
aus = next(s for s in info['streams'] if s['codec_type'] == 'audio')

def pcm(path):
    raw = subprocess.run(['ffmpeg', '-v', 'error', '-i', str(path), '-map', '0:a:0', '-ac', '1', '-ar', '44100', '-f', 'f32le', '-'],
                         capture_output=True, check=True).stdout
    return np.frombuffer(raw, np.float32)

a = pcm(mp3)
b = pcm(out)
n = min(len(a), len(b))
# Alignment: best lag within +-20 ms.
seg = slice(44100 * 2, 44100 * 40)
lags = range(-882, 883, 1)
best = max(lags, key=lambda L: float(np.dot(a[seg], b[seg.start + L:seg.stop + L])))
corr = float(np.corrcoef(a[:n], b[:n])[0, 1])
rms = lambda x: float(np.sqrt(np.mean(np.square(x)))) if len(x) else 0.0
level_db = 20 * np.log10(rms(b[:n]) / rms(a[:n]))
tail = b[len(a):]
checks = {
    'output': str(out.relative_to(here)), 'sha256': sha(out), 'bytes': out.stat().st_size,
    'width': vs['width'], 'height': vs['height'], 'fps': vs['r_frame_rate'], 'frames': int(vs['nb_frames']),
    'video_seconds': float(vs['duration']), 'audio_seconds': float(aus['duration']), 'container_seconds': float(info['format']['duration']),
    'video_start': float(vs.get('start_time', 0)), 'audio_start': float(aus.get('start_time', 0)),
    'audio_codec': aus['codec_name'], 'audio_sample_rate': aus['sample_rate'],
    'approved_mp3_sha256': sha(mp3), 'approved_mp3_seconds': len(a) / 44100,
    'audio_vs_mp3': {'best_lag_ms': round(best / 44.1, 2), 'correlation': round(corr, 5), 'level_change_db': round(float(level_db), 3),
                     'padding_after_mp3_seconds': round(len(tail) / 44100, 3), 'padding_peak': float(np.max(np.abs(tail))) if len(tail) else 0.0},
    'picture_stream_copied_from': str(render.relative_to(here)), 'picture_sha256_source': sha(render),
}
ok = (checks['width'], checks['height'], checks['fps']) == (1080, 1920, '30/1') and abs(checks['video_seconds'] - checks['audio_seconds']) < 0.05 \
    and abs(best) <= 1 and corr > 0.99 and abs(level_db) < 0.2
checks['pass'] = bool(ok)
(here / 'renders' / f'ensign-wasp-{rev}-final.checks.json').write_text(json.dumps(checks, indent=2) + '\n')
print(json.dumps(checks, indent=2))
