"""Pull frames from the finished MP4 just after key words and tile them, to check picture and highlighted word.
Usage: python3 keyword-frames.py <mp4> <out.png>"""
import json
import subprocess
import sys
import tempfile
from pathlib import Path

mp4, out = sys.argv[1], sys.argv[2]
words = json.loads((Path(__file__).parent / 'words.json').read_text())['words']
keys = [3, 7, 9, 13, 17, 20, 25, 31, 43, 47, 52, 62, 67, 71, 79, 83, 89, 90, 99, 106, 109, 113, 114, 118, 124, 129, 130, 134]
with tempfile.TemporaryDirectory() as tmp:
    files = []
    for n, i in enumerate(keys):
        t = words[i]['start'] + 0.15
        f = Path(tmp) / f'{n:02d}.png'
        label = f"{words[i]['text']}  {t:.2f}s"
        subprocess.run(['ffmpeg', '-v', 'error', '-y', '-ss', f'{t:.3f}', '-i', mp4, '-frames:v', '1', '-vf',
                        f"scale=270:480,pad=270:510:0:30:white,drawtext=text='{label}':x=6:y=6:fontsize=20:fontcolor=black", str(f)], check=True)
        files.append(str(f))
    subprocess.run(['montage', *files, '-tile', '7x', '-geometry', '+4+4', out], check=True)
print(out)
