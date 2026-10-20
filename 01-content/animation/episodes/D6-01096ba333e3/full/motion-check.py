"""Motion numbers measured on the encoded MP4, same measures as render-shots.mjs --check-motion.
Reports the lesson (before the outro wipe) and the whole video separately: the approved outro ends on a still logo hold.
Usage: python3 motion-check.py <mp4> [lesson_end_seconds]"""
import json
import subprocess
import sys

import numpy as np

mp4 = sys.argv[1]
lesson_end = float(sys.argv[2]) if len(sys.argv) > 2 else 1324 / 30
raw = subprocess.run(['ffmpeg', '-v', 'error', '-i', mp4, '-vf', 'scale=54:96:flags=area', '-pix_fmt', 'rgb24', '-f', 'rawvideo', '-'],
                     capture_output=True, check=True).stdout
f = np.frombuffer(raw, np.uint8).reshape(-1, 96, 54, 3).astype(np.int16)
fps = 30

def measure(frames):
    d = np.abs(frames[1:] - frames[:-1]).mean(axis=(1, 2, 3))
    still = longest = 0
    for x in d:
        still = still + 1 if x < 0.6 else 0
        longest = max(longest, still)
    half = fps // 2
    change = (np.abs(frames[half:] - frames[:-half]).max(axis=3) > 40).mean(axis=(1, 2))
    return {'longest_still_seconds': round(longest / fps, 3), 'picture_change_half_second_median': round(float(np.median(change)), 3),
            'stretches_over_0_35s': int(sum(1 for _ in [0]) if longest / fps > 0.35 else 0)}

cut = int(round(lesson_end * fps))
out = {'frames': len(f), 'lesson_seconds': [0, round(lesson_end, 3)], 'lesson': measure(f[:cut]), 'whole': measure(f),
       'targets': {'longest_still_seconds': '<= 0.35', 'picture_change_half_second_median': '>= 0.15'}}
# Where the lesson goes still, if anywhere: list stretches longer than 0.2 s.
d = np.abs(f[1:cut] - f[:cut - 1]).mean(axis=(1, 2, 3))
runs, start = [], None
for i, x in enumerate(d):
    if x < 0.6 and start is None:
        start = i
    if (x >= 0.6 or i == len(d) - 1) and start is not None:
        if (i - start) / fps > 0.2:
            runs.append([round(start / fps, 2), round(i / fps, 2)])
        start = None
out['lesson_still_stretches_over_0_2s'] = runs
print(json.dumps(out, indent=2))
