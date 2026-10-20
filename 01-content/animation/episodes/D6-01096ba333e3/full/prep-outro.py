"""Fit the approved outro animation to Chris's sign-off in D6-01096ba333e3.

Only the mascot's opening scan (source frames 10-43) is shortened, by dropping its 24-to-30 fps
duplicate frames and two scan frames spread evenly. The wipe (0-9) and everything from the
anticipation on (44+: dip, jump, robe flare, swing, logo reveal and landing) play at designed speed.
Writes outro-retime.json (tracked) and dev/outro-frames.rgba (local cache, 1080x1920 RGBA)."""
import hashlib
import json
import subprocess
from pathlib import Path

import numpy as np

here = Path(__file__).parent
root = here.parents[2]  # 01-content/animation
src = (root / '../outro/assets/outro-animation-v2.mp4').resolve()
W, H, FPS = 1080, 1920, 30
words = json.loads((here / 'words.json').read_text())['words']
lesson_end_frame = 1324            # 44.133 s: first frame after "roaches." ends (44.13 s)
last_word_end = words[137]['end']  # "Control." ends
end_frame = round((last_word_end + 1.0) * FPS)  # hold the settled logo about 1 s

small = subprocess.run(['ffmpeg', '-v', 'error', '-i', str(src), '-vf', 'scale=108:192', '-pix_fmt', 'gray', '-f', 'rawvideo', '-'],
                       capture_output=True, check=True).stdout
g = np.frombuffer(small, np.uint8).reshape(-1, 192, 108).astype(float)
dup = {i for i in range(1, len(g)) if np.abs(g[i] - g[i - 1]).mean() < 0.15}
SCAN = (10, 43)
TRIM = 9
real = [i for i in range(SCAN[0], SCAN[1] + 1) if i not in dup]
n_out = (SCAN[1] - SCAN[0] + 1) - TRIM
picked = [real[round(j * (len(real) - 1) / (n_out - 1))] for j in range(n_out)]
mapping = list(range(0, SCAN[0])) + picked + list(range(SCAN[1] + 1, len(g)))
used = mapping[:end_frame - lesson_end_frame]
assert used == sorted(used) and len(set(used)) == len(used)

out_of = {s: i for i, s in enumerate(mapping)}
t0 = lesson_end_frame / FPS
release, landed = out_of[73], out_of[91]
info = {
    'source': '01-content/outro/assets/outro-animation-v2.mp4',
    'source_sha256': hashlib.sha256(src.read_bytes()).hexdigest(),
    'source_frames': len(g), 'fps': FPS,
    'outro_start_frame': lesson_end_frame, 'outro_start_seconds': round(t0, 4),
    'end_frame': end_frame, 'video_seconds': round(end_frame / FPS, 4),
    'scan_source_frames': list(SCAN), 'scan_duplicates_dropped': sorted(d for d in dup if SCAN[0] <= d <= SCAN[1]),
    'scan_frames_dropped': sorted(set(real) - set(picked)), 'frames_trimmed': TRIM, 'seconds_trimmed': round(TRIM / FPS, 4),
    'designed_speed_from_source_frame': SCAN[1] + 1,
    'logo_release_seconds': round(t0 + release / FPS, 4), 'logo_landed_seconds': round(t0 + landed / FPS, 4),
    'deep_starts_seconds': words[134]['start'], 'helping_starts_seconds': words[130]['start'],
    'last_word_ends_seconds': last_word_end, 'hold_after_last_word_seconds': round(end_frame / FPS - last_word_end, 3),
    'wipe_frames': [0, 8],
    'mapping': used,
}
assert info['logo_landed_seconds'] <= info['deep_starts_seconds'], 'logo must land at or before "Deep"'
(here / 'outro-retime.json').write_text(json.dumps(info, indent=1) + '\n')

cache = here / 'dev' / 'outro-frames.rgba'
cache.parent.mkdir(exist_ok=True)
proc = subprocess.Popen(['ffmpeg', '-v', 'error', '-i', str(src), '-pix_fmt', 'rgba', '-f', 'rawvideo', '-'], stdout=subprocess.PIPE)
need = set(used)
size = W * H * 4
with open(cache, 'wb') as f:
    for i in range(len(g)):
        frame = proc.stdout.read(size)
        if len(frame) < size:
            break
        if i in need:
            f.write(frame)
proc.wait()
assert cache.stat().st_size == size * len(used)
print(json.dumps({k: v for k, v in info.items() if k != 'mapping'}, indent=1))
