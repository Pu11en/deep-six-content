#!/usr/bin/env python3
"""Score music tracks for use as a steady bed under narration. Drew heard earlier tracks as 'random'.

Usage: score_steadiness.py OUT.json TRACK...   (system python3 with numpy and faster_whisper)

Per track, over 3 s to 90 s:
- level_spread_db: momentary loudness p90 minus p10 (lower is steadier)
- big_jumps: count of loudness changes over 3 dB within 0.4 s (drum hits count too)
- short_term_spread_db: 3 s loudness p95 minus p5 (beats smoothed out; lower is steadier)
- section_changes: 2 s blocks whose sound differs sharply from the previous block
- voice_room_db: integrated loudness minus the 1 to 4 kHz speech band (higher leaves more room)
- pulse_strength: how regular the hits are (0 to 1). Beats and ticking score high; Drew finds them annoying
- hit_rate: sharp attacks per second in the 2 to 12 kHz band (ticks, hi-hats, clicks)
- percussive_ratio: share of energy in short hits after a median-filter split of sustained and percussive sound (drums and ticks raise it)
- speech_segments: segments an offline speech model hears as words (0 wanted)
"""
import json, re, subprocess, sys
import numpy as np

def ffmpeg_err(args):
    return subprocess.run(['ffmpeg', '-hide_banner', '-nostats', *args], capture_output=True, text=True).stderr

def pcm(path, sr=22050):
    raw = subprocess.run(['ffmpeg', '-v', 'error', '-ss', '3', '-t', '87', '-i', path, '-ac', '1', '-ar', str(sr),
                          '-f', 'f32le', '-'], capture_output=True).stdout
    return np.frombuffer(raw, dtype=np.float32), sr

def integrated(path, extra=''):
    err = ffmpeg_err(['-ss', '3', '-t', '87', '-i', path, '-af', extra + 'ebur128', '-f', 'null', '-'])
    return float(re.findall(r'I:\s+(-?[\d.]+) LUFS', err)[-1])

def loudness_series(path, key):
    err = subprocess.run(['ffmpeg', '-hide_banner', '-nostats', '-v', 'verbose', '-ss', '3', '-t', '87', '-i', path,
                          '-af', 'ebur128=framelog=verbose', '-f', 'null', '-'], capture_output=True, text=True).stderr
    m = np.array([float(x) for x in re.findall(r'Parsed_ebur128.*?' + key + r':\s*(-?[\d.]+)', err)])
    return m[m > -70]

def percussiveness(x, sr):
    hop = 256
    fr = x[: len(x) // hop * hop].reshape(-1, hop)
    e = np.log1p(1000 * (fr ** 2).sum(1))
    on = np.maximum(np.diff(e), 0); on -= on.mean()
    ac = np.correlate(on, on, 'full')[len(on) - 1:]
    lags = np.arange(len(ac)) / (sr / hop)
    ok = (lags > 60 / 180) & (lags < 60 / 50)
    pulse = float(ac[ok].max() / ac[0])
    spec = np.fft.rfft(x)
    f = np.fft.rfftfreq(len(x), 1 / sr)
    hi = np.fft.irfft(spec * ((f > 2000) & (f < 12000)), len(x))
    he = np.log1p(1e4 * (hi[: len(hi) // hop * hop].reshape(-1, hop) ** 2).sum(1))
    d = np.diff(he)
    hits = int((d > np.median(np.abs(d)) * 8 + 0.5).sum())
    return round(pulse, 2), round(hits / (len(x) / sr), 2)

def percussive_ratio(x, sr):
    from scipy.ndimage import median_filter
    n, hop = 2048, 512
    frames = np.lib.stride_tricks.sliding_window_view(x, n)[::hop] * np.hanning(n)
    S = np.abs(np.fft.rfft(frames, axis=1)).T  # freq x time
    H = median_filter(S, size=(1, 31))
    P = median_filter(S, size=(31, 1))
    mask_p = P ** 2 / (H ** 2 + P ** 2 + 1e-12)
    return round(float((mask_p * S ** 2).sum() / ((S ** 2).sum() + 1e-12)), 3)

def section_changes(x, sr):
    block = 2 * sr
    feats = []
    for i in range(0, len(x) - block, block):
        spec = np.abs(np.fft.rfft(x[i:i + block] * np.hanning(block)))
        bands = np.array_split(spec[: len(spec) // 2], 24)
        feats.append(np.log1p([b.mean() for b in bands]))
    f = np.array(feats)
    f = f - f.mean(1, keepdims=True)
    d = 1 - np.sum(f[1:] * f[:-1], 1) / (np.linalg.norm(f[1:], axis=1) * np.linalg.norm(f[:-1], axis=1) + 1e-9)
    return int((d > max(0.15, np.median(d) * 4)).sum()), round(float(d.max()), 3)

out, tracks = sys.argv[1], sys.argv[2:]
from faster_whisper import WhisperModel
asr = WhisperModel('small.en', device='cpu', compute_type='int8', local_files_only=True)
rows = []
for t in tracks:
    m = loudness_series(t, 'M')
    st = loudness_series(t, 'S')[30:]  # 3 s windows; skip the first 3 s while the window fills
    jumps = np.abs(np.diff(m[::4]))
    x, sr = pcm(t)
    changes, worst = section_changes(x, sr)
    pulse, hit_rate = percussiveness(x, sr)
    perc = percussive_ratio(x[: sr * 40], sr)  # first 40 s is enough and keeps memory low
    segs, _ = asr.transcribe(t, language='en', vad_filter=True, beam_size=1, clip_timestamps=[0, 95])
    words = [s.text.strip() for s in segs if s.no_speech_prob < 0.5 and s.text.strip().lower() not in ('music', '[music]')]
    i_all = integrated(t)
    row = {'track': t.split('/')[-1], 'level_spread_db': round(float(np.percentile(m, 90) - np.percentile(m, 10)), 1),
           'big_jumps': int((jumps > 3).sum()),
           'short_term_spread_db': round(float(np.percentile(st, 95) - np.percentile(st, 5)), 1), 'section_changes': changes, 'worst_change': worst,
           'voice_room_db': round(i_all - integrated(t, 'highpass=f=1000,lowpass=f=4000,'), 1),
           'pulse_strength': pulse, 'hit_rate': hit_rate, 'percussive_ratio': perc,
           'speech_segments': len(words), 'heard': ' '.join(words)[:80], 'lufs': i_all}
    rows.append(row)
    print(json.dumps(row), flush=True)
json.dump(rows, open(out, 'w'), indent=1)
