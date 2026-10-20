#!/usr/bin/env python3
"""Mix a music bed under a finished Deep Six MP4 without touching its picture.

Usage: mix_preview.py VIDEO.mp4 MUSIC.mp3 OUT.mp4 [--under 10] [--target -14] [--start 0]

- Without --target the narration level stays exactly as in the input video.
- With --target the narration alone is first brought to that integrated loudness
  (two-pass loudnorm on the voice only), so pauses and music are not lifted.
- Music is evened out over long windows, set UNDER LU below the narration,
  gently ducked by the narration, and faded out at the end.
  With --steady the music keeps one constant level: no leveler, no ducking.
- A final limiter keeps true peak under --tp. Video stream is copied, never re-encoded.
"""
import argparse, json, re, subprocess, sys

def run(cmd):
    return subprocess.run(cmd, capture_output=True, text=True, check=True)

def duration(path):
    return float(run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', path]).stdout)

def loudness(inputs, graph, label):
    err = run(['ffmpeg', '-hide_banner', '-nostats', '-nostdin', *inputs, '-filter_complex',
               f'{graph};[{label}]ebur128=peak=true[z]', '-map', '[z]', '-f', 'null', '-']).stderr
    summary = err[err.rfind('Summary:'):]
    return (float(re.search(r'I:\s+(-?[\d.]+) LUFS', summary).group(1)),
            float(re.search(r'Peak:\s+(-?[\d.]+) dBFS', summary).group(1)))

ap = argparse.ArgumentParser()
ap.add_argument('video'); ap.add_argument('music'); ap.add_argument('out')
ap.add_argument('--under', type=float, default=15.0, help='music bed this many LU below narration')
ap.add_argument('--target', type=float, default=None, help='narration loudness, LUFS (e.g. -14)')
ap.add_argument('--tp', type=float, default=-1.5, help='true peak ceiling, dBTP (AAC adds about 0.5 dB)')
ap.add_argument('--start', type=float, default=0.0, help='start offset into the music track, seconds')
ap.add_argument('--duck-below', type=float, default=11.5,
                help='ducking starts when the voice is louder than (narration LUFS minus this), dB')
ap.add_argument('--steady', action='store_true',
                help='constant music level: no leveler, no ducking (Drew heard ducked mixes as unstable)')
ap.add_argument('--level', action='store_true', help='with --steady: keep the slow leveler, still no ducking')
ap.add_argument('--fade', type=float, default=1.2, help='fade-out length at the end, seconds')
a = ap.parse_args()

total = duration(a.video)
if duration(a.music) - a.start < total:
    sys.exit('Music track shorter than video; looping not built yet.')
inputs = ['-i', a.video, '-i', a.music]
chans = int(run(['ffprobe', '-v', 'error', '-select_streams', 'a:0', '-show_entries', 'stream=channels',
                 '-of', 'csv=p=0', a.video]).stdout.strip())
# Dual-mono stereo plays like the mono file but reads 3 LU higher, so measure after the pan.
voice = 'aresample=48000,' + ('pan=stereo|c0=c0|c1=c0' if chans == 1 else 'anull')

if a.target is not None:
    ln = f'loudnorm=I={a.target}:TP={a.tp}:LRA=11'
    err = run(['ffmpeg', '-hide_banner', '-nostats', '-nostdin', *inputs, '-filter_complex',
               f'[0:a]{voice},{ln}:print_format=json[o]', '-map', '[o]', '-f', 'null', '-']).stderr
    m = json.loads(err[err.rfind('{'):err.rfind('}') + 1])
    voice += (f',{ln}:measured_I={m["input_i"]}:measured_TP={m["input_tp"]}:measured_LRA={m["input_lra"]}'
              f':measured_thresh={m["input_thresh"]}:offset={m["target_offset"]}:linear=true'
              f',aresample=48000,atrim=end={total:.3f}')
voice_i, voice_peak = loudness(inputs, f'[0:a]{voice}[v]', 'v')

bed = f'atrim={a.start}:{a.start + total},asetpts=PTS-STARTPTS,aresample=48000'
if not a.steady or a.level:
    bed += ',dynaudnorm=f=500:g=31:p=0.9:m=10'
music_i, _ = loudness(inputs, f'[1:a]{bed}[m]', 'm')
gain = (voice_i - a.under) - music_i
limit = 10 ** (a.tp / 20)
# Tie the ducking threshold to the narration level so a louder voice does not duck harder.
duck = 10 ** ((voice_i - a.duck_below) / 20)

graph = (
    f'[1:a]{bed},volume={gain:.2f}dB[m0];'
    + (f'[0:a]{voice}[v];[m0]anull[md];' if a.steady else
       f'[0:a]{voice},asplit=2[v][vsc];'
       f'[m0][vsc]sidechaincompress=threshold={duck:.4f}:ratio=3:attack=30:release=500[md];')
    + f'[md]afade=t=in:d=0.3,afade=t=out:st={total - a.fade:.3f}:d={a.fade}[mf];'
    f'[v][mf]amix=inputs=2:normalize=0:duration=first,alimiter=limit={limit:.4f}:level=disabled[mix]'
)
run(['ffmpeg', '-hide_banner', '-loglevel', 'error', '-nostdin', '-y', *inputs,
     '-filter_complex', graph, '-map', '0:v', '-map', '[mix]', '-c:v', 'copy',
     '-c:a', 'aac', '-b:a', '192k', '-ar', '48000', '-movflags', '+faststart', a.out])

out_i, out_peak = loudness(['-i', a.out], '[0:a]anull[x]', 'x')
print(json.dumps({'video': a.video, 'music': a.music, 'out': a.out, 'seconds': round(total, 3),
                  'narration_lufs': voice_i, 'narration_peak_dbfs': voice_peak,
                  'music_bed_target_lufs': round(voice_i - a.under, 1), 'music_gain_db': round(gain, 2),
                  'mix_lufs': out_i, 'mix_peak_dbfs': out_peak, 'out_seconds': round(duration(a.out), 3)}))
