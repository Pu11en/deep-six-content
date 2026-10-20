"""Deterministic finishing steps for make_video.py. No AI, no network, no paid service.

Built from the hand-made scripts of the approved ensign-wasp video (episodes/D6-01096ba333e3/full/):
prep-outro.py, finish.py, motion-check.py, keyword-frames.py and filmstrip.sh, generalised so any
episode whose narration ends with the approved sign-off gets the same treatment.
"""
import hashlib
import json
import math
import os
import re
import shutil
import signal
import subprocess
import tempfile
import time
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent            # 01-content/animation
PROJECT = ROOT.parents[1]                          # deep-six-content
CACHE = ROOT / '.cache'                            # git-ignored, rebuilt on demand
FPS, W, H = 30, 1080, 1920

# ---------------------------------------------------------------- the approved outro
OUTRO_SOURCE = ROOT.parent / 'outro' / 'assets' / 'outro-animation-v2.mp4'
OUTRO_SHA256 = '201c8cf62c61b415574ae0fdf3676fbc258f5a7dc1685cd34e7a4a650472569e'
# Designed moments, as source frames at 30 fps (measured for the ensign-wasp fit; see outro/production/v2-composition-timing.json).
OUTRO_WIPE = (0, 8)        # cream-paper entry over the last teaching picture (0.30 s)
OUTRO_SCAN = (10, 43)      # the reaper's opening scan: the only part that may be shortened
OUTRO_RELEASE = 73         # logo leaves the lens (2.433 s)
OUTRO_LANDED = 91          # logo settled in its spot (3.033 s)
SIGNOFF = 'Helping you understand pests. Deep Six Pest Control.'
HOLD_AFTER_LAST_WORD = 1.0
CAPTION_FADE = (-0.03, 0.13)   # top caption fades out around the logo release (approved: 46.24 to 46.40 s)


class FinishError(Exception):
    pass


def sha(path):
    digest = hashlib.sha256()
    with open(path, 'rb') as handle:
        for block in iter(lambda: handle.read(1 << 20), b''):
            digest.update(block)
    return digest.hexdigest()


def norm(word):
    return re.sub(r"[^a-z0-9']", '', word.lower().replace('’', "'"))


def find_signoff(words):
    """Index of the sign-off's first word ("Helping") when the narration ends with it, else None."""
    target = [norm(w) for w in SIGNOFF.split()]
    tail = [norm(w['text']) for w in words[-len(target):]]
    return len(words) - len(target) if tail == target else None


def outro_start_frame(words):
    """The cream wipe starts on the first frame after the last lesson word (the word before "Helping")."""
    return math.ceil(words[find_signoff(words) - 1]['end'] * FPS - 1e-6)


def probe(path):
    out = subprocess.run(['ffprobe', '-v', 'error', '-show_streams', '-show_format', '-of', 'json', str(path)],
                         capture_output=True, text=True, check=True).stdout
    return json.loads(out)


def outro_cache():
    """All 165 source frames of the approved outro as raw 1080x1920 RGBA, shared by every run (1.4 GB, git-ignored)."""
    path = CACHE / 'outro-animation-v2.rgba'
    meta = CACHE / 'outro-animation-v2.json'
    if path.exists() and meta.exists() and json.loads(meta.read_text()).get('source_sha256') == OUTRO_SHA256:
        return path
    if sha(OUTRO_SOURCE) != OUTRO_SHA256:
        raise FinishError('The approved outro animation changed; it must match its approval fingerprint.')
    CACHE.mkdir(exist_ok=True)
    tmp = path.with_suffix('.partial')
    with open(tmp, 'wb') as out:
        subprocess.run(['ffmpeg', '-v', 'error', '-nostdin', '-i', str(OUTRO_SOURCE), '-pix_fmt', 'rgba', '-f', 'rawvideo', '-'],
                       stdout=out, check=True)
    frames = tmp.stat().st_size // (W * H * 4)
    os.replace(tmp, path)
    meta.write_text(json.dumps({'source': str(OUTRO_SOURCE.relative_to(PROJECT)), 'source_sha256': OUTRO_SHA256,
                                'frames': frames, 'width': W, 'height': H, 'format': 'rgba'}, indent=1) + '\n')
    return path


def fit_outro(words, out_json, audio_seconds):
    """Fit the approved outro to this narrator's sign-off and write the frame plan used by scenes/outro.mjs.

    The cream wipe starts on the first frame after the last lesson word. Only the reaper's opening scan
    is shortened: first its duplicate frames (24-to-30 fps repeats), then scan frames thinned evenly, until
    the logo has settled for one whole frame before "Deep" starts. The jump, swing and reveal keep their
    designed speed. The settled logo holds about 1 s after the last word. The top caption fades out
    around the logo release, before the logo flies into its spot.
    """
    i0 = find_signoff(words)
    if i0 is None:
        raise FinishError('The narration does not end with the approved sign-off.')
    lesson_end = words[i0 - 1]['end']
    start_frame = outro_start_frame(words)
    deep = words[i0 + 4]['start']
    last_end = words[-1]['end']
    end_frame = max(round((last_end + HOLD_AFTER_LAST_WORD) * FPS), math.ceil(audio_seconds * FPS - 1e-6))

    small = subprocess.run(['ffmpeg', '-v', 'error', '-nostdin', '-i', str(OUTRO_SOURCE), '-vf', 'scale=108:192',
                            '-pix_fmt', 'gray', '-f', 'rawvideo', '-'], capture_output=True, check=True).stdout
    g = np.frombuffer(small, np.uint8).reshape(-1, 192, 108).astype(float)
    total = len(g)
    dup = sorted(i for i in range(1, total) if np.abs(g[i] - g[i - 1]).mean() < 0.15)
    scan = list(range(OUTRO_SCAN[0], OUTRO_SCAN[1] + 1))
    scan_dups = [i for i in scan if i in dup]
    real = [i for i in scan if i not in dup]

    # Smallest trim that lets the landed frame finish before "Deep" begins.
    trim = max(0, math.ceil(start_frame + OUTRO_LANDED + 1 - deep * FPS - 1e-6))
    max_trim = len(scan_dups) + len(real) // 2
    if trim > max_trim:
        raise FinishError(f'The narrator reaches "Deep" {(trim - max_trim) / FPS:.2f} s too soon for the approved outro, '
                          'even with half the opening scan removed. The narration needs a natural pause before the sign-off.')
    if trim <= len(scan_dups):
        drop = {scan_dups[round(j * (len(scan_dups) - 1) / max(1, trim - 1))] for j in range(trim)} if trim else set()
        kept_scan = [i for i in scan if i not in drop]
    else:
        n_out = len(scan) - trim
        kept_scan = [real[round(j * (len(real) - 1) / (n_out - 1))] for j in range(n_out)]
    mapping = list(range(0, OUTRO_SCAN[0])) + kept_scan + list(range(OUTRO_SCAN[1] + 1, total))
    used = mapping[:end_frame - start_frame]
    if used != sorted(set(used)):
        raise FinishError('Outro frame plan is not strictly increasing.')
    position = {s: i for i, s in enumerate(mapping)}
    t0 = start_frame / FPS
    release = t0 + position[OUTRO_RELEASE] / FPS
    landed = t0 + position[OUTRO_LANDED] / FPS
    fade = [round(release + CAPTION_FADE[0], 2), round(release + CAPTION_FADE[1], 2)]
    info = {
        'source': str(OUTRO_SOURCE.relative_to(PROJECT)), 'source_sha256': OUTRO_SHA256,
        'frames_cache': str(outro_cache().relative_to(ROOT)), 'cache_holds': 'every source frame; mapping gives source frame numbers',
        'source_frames': total, 'fps': FPS,
        'outro_start_frame': start_frame, 'outro_start_seconds': round(t0, 4),
        'end_frame': end_frame, 'video_seconds': round(end_frame / FPS, 4),
        'scan_source_frames': list(OUTRO_SCAN), 'scan_duplicates_dropped': sorted(set(scan_dups) - set(kept_scan)),
        'scan_frames_dropped': sorted(set(real) - set(kept_scan)), 'frames_trimmed': trim, 'seconds_trimmed': round(trim / FPS, 4),
        'designed_speed_from_source_frame': OUTRO_SCAN[1] + 1,
        'logo_release_seconds': round(release, 4), 'logo_landed_seconds': round(landed, 4),
        'deep_starts_seconds': deep, 'helping_starts_seconds': words[i0]['start'],
        'lesson_last_word_ends_seconds': lesson_end,
        'last_word_ends_seconds': last_end, 'hold_after_last_word_seconds': round(end_frame / FPS - last_end, 3),
        'signoff_first_word': i0, 'caption_words': [i0, i0 + 1, i0 + 2, i0 + 3], 'caption_fade_seconds': fade,
        'wipe_frames': list(OUTRO_WIPE), 'wipe_seconds': 0.3,
        'mapping': used,
    }
    if landed + 1 / FPS > deep + 1e-9:
        raise FinishError('Logo would land after "Deep".')
    Path(out_json).write_text(json.dumps(info, indent=1) + '\n')
    return info


# ---------------------------------------------------------------- renders
def next_revision(renders, stem):
    """First vN with no finished file, partial file, manifest or review: a crashed render never blocks the next try."""
    n = 1
    while any((Path(renders) / f'{stem}-v{n}{ext}').exists() for ext in ('.mp4', '.partial.mp4', '.json', '.review.json')):
        n += 1
    return f'v{n}'


def start_render(scene_path, log_path):
    """Start a render in its own session, so closing the chat or the runner cannot stop it."""
    log = open(log_path, 'a')
    proc = subprocess.Popen(['node', 'render-shots.mjs', str(Path(scene_path).resolve().relative_to(ROOT))], cwd=ROOT,
                            stdin=subprocess.DEVNULL, stdout=log, stderr=subprocess.STDOUT, start_new_session=True)
    return proc.pid


def alive(pid, needle=None):
    try:
        os.waitpid(pid, os.WNOHANG)             # reap our own finished child, if it is one
    except (ChildProcessError, OSError):
        pass
    try:
        os.kill(pid, 0)
        cmd = Path(f'/proc/{pid}/cmdline').read_bytes().replace(b'\0', b' ').decode(errors='replace')
        state = Path(f'/proc/{pid}/stat').read_text().split(') ', 1)[1].split()[0]
    except (OSError, IndexError):
        return False
    return state != 'Z' and (needle is None or needle in cmd)


def stop(pid):
    try:
        os.killpg(pid, signal.SIGTERM)
    except OSError:
        pass


# ---------------------------------------------------------------- exact audio
def audio_graph(video_seconds, music=None):
    """Audio for the finished file: the approved MP3 unchanged, padded with silence to the end of the picture.

    MUSIC GOES HERE (later; owned by the music session in 01-content/music/). A chosen bed would be a second
    ffmpeg input mixed under the narration in this graph. Keep check_audio() measuring the narration against
    the approved MP3, for example by mixing from a separately kept narration-only file.
    """
    if music:
        raise FinishError('Music is not chosen yet. The music session decides how a bed is mixed here.')
    return f'apad=whole_dur={video_seconds:.6f}'


def pcm(path):
    raw = subprocess.run(['ffmpeg', '-v', 'error', '-nostdin', '-i', str(path), '-map', '0:a:0', '-ac', '1', '-ar', '44100',
                          '-f', 'f32le', '-'], capture_output=True, check=True).stdout
    return np.frombuffer(raw, np.float32)


def finish_audio(render, mp3, mp3_sha256, out, music=None):
    """Replace the renderer's audio (it fades the last 80 ms) with the approved MP3 decoded as-is, then check it."""
    render, mp3, out = Path(render), Path(mp3), Path(out)
    if sha(mp3) != mp3_sha256:
        raise FinishError('The approved MP3 changed.')
    if out.exists():
        raise FinishError(f'{out.name} exists; nothing overwritten.')
    v = next(s for s in probe(render)['streams'] if s['codec_type'] == 'video')
    video_seconds = int(v['nb_frames']) / FPS
    partial = out.with_name(out.stem + '.partial.mp4')
    partial.unlink(missing_ok=True)
    subprocess.run(['ffmpeg', '-hide_banner', '-loglevel', 'error', '-nostdin', '-n', '-i', str(render), '-i', str(mp3),
                    '-map', '0:v:0', '-map', '1:a:0', '-c:v', 'copy', '-af', audio_graph(video_seconds, music),
                    '-c:a', 'aac', '-b:a', '192k', '-ar', '44100', '-ac', '1', '-t', f'{video_seconds:.6f}',
                    '-movflags', '+faststart', str(partial)], check=True)
    os.replace(partial, out)
    return check_audio(out, mp3, render)


def check_audio(final, mp3, render=None):
    info = probe(final)
    vs = next(s for s in info['streams'] if s['codec_type'] == 'video')
    aus = next(s for s in info['streams'] if s['codec_type'] == 'audio')
    a, b = pcm(mp3), pcm(final)
    n = min(len(a), len(b))
    seg = slice(44100 * 2, max(44100 * 3, min(44100 * 40, n - 44100 * 2)))
    lags = range(-882, 883)
    best = max(lags, key=lambda L: float(np.dot(a[seg], b[seg.start + L:seg.stop + L])))
    corr = float(np.corrcoef(a[:n], b[:n])[0, 1])
    rms = lambda x: float(np.sqrt(np.mean(np.square(x)))) if len(x) else 0.0
    level_db = 20 * np.log10(rms(b[:n]) / rms(a[:n]))
    tail = b[len(a):]
    checks = {
        'output': final.name, 'sha256': sha(final), 'bytes': final.stat().st_size,
        'width': vs['width'], 'height': vs['height'], 'fps': vs['r_frame_rate'], 'frames': int(vs['nb_frames']),
        'video_seconds': float(vs['duration']), 'audio_seconds': float(aus['duration']),
        'container_seconds': float(info['format']['duration']),
        'video_start': float(vs.get('start_time', 0)), 'audio_start': float(aus.get('start_time', 0)),
        'audio_codec': aus['codec_name'], 'audio_sample_rate': aus['sample_rate'],
        'approved_mp3_sha256': sha(mp3), 'approved_mp3_seconds': round(len(a) / 44100, 3),
        'audio_vs_mp3': {'best_lag_ms': round(best / 44.1, 2), 'correlation': round(corr, 5),
                         'level_change_db': round(float(level_db), 3), 'padding_after_mp3_seconds': round(len(tail) / 44100, 3),
                         'padding_peak': float(np.max(np.abs(tail))) if len(tail) else 0.0},
        'music': None,
    }
    if render:
        checks['picture_stream_copied_from'] = Path(render).name
        checks['picture_sha256_source'] = sha(render)
    checks['pass'] = bool((checks['width'], checks['height'], checks['fps']) == (1080, 1920, '30/1')
                          and abs(checks['video_seconds'] - checks['audio_seconds']) < 0.05
                          and checks['video_start'] == 0 and checks['audio_start'] == 0
                          and abs(best) <= 1 and corr > 0.99 and abs(level_db) < 0.2)
    return checks


# ---------------------------------------------------------------- picture checks on the encoded file
def frames_small(mp4, w=54, h=96, start=None, end=None):
    cmd = ['ffmpeg', '-v', 'error', '-nostdin']
    if start is not None:
        cmd += ['-ss', f'{start:.3f}']
    cmd += ['-i', str(mp4)]
    if end is not None:
        cmd += ['-t', f'{end - (start or 0):.3f}']
    cmd += ['-vf', f'scale={w}:{h}:flags=area', '-pix_fmt', 'rgb24', '-f', 'rawvideo', '-']
    raw = subprocess.run(cmd, capture_output=True, check=True).stdout
    return np.frombuffer(raw, np.uint8).reshape(-1, h, w, 3).astype(np.int16)


def _measure(frames):
    d = np.abs(frames[1:] - frames[:-1]).mean(axis=(1, 2, 3))
    still = longest = 0
    for x in d:
        still = still + 1 if x < 0.6 else 0
        longest = max(longest, still)
    half = FPS // 2
    change = (np.abs(frames[half:] - frames[:-half]).max(axis=3) > 40).mean(axis=(1, 2))
    return {'longest_still_seconds': round(longest / FPS, 3),
            'picture_change_half_second_median': round(float(np.median(change)), 3)}


def motion_check(mp4, lesson_end=None):
    """Motion measured on the encoded MP4, same measures as render-shots.mjs --check-motion.
    The lesson is scored on its own: the approved outro ends on a designed still logo hold."""
    f = frames_small(mp4)
    cut = int(round(lesson_end * FPS)) if lesson_end else len(f)
    lesson = _measure(f[:cut])
    d = np.abs(f[1:cut] - f[:cut - 1]).mean(axis=(1, 2, 3))
    runs, start = [], None
    for i, x in enumerate(d):
        if x < 0.6 and start is None:
            start = i
        if (x >= 0.6 or i == len(d) - 1) and start is not None:
            if (i - start) / FPS > 0.2:
                runs.append([round(start / FPS, 2), round(i / FPS, 2)])
            start = None
    return {'frames': len(f), 'lesson_seconds': [0, round(cut / FPS, 3)], 'lesson': lesson, 'whole': _measure(f),
            'lesson_still_stretches_over_0_2s': runs,
            'targets': {'longest_still_seconds': '<= 0.35', 'picture_change_half_second_median': '>= 0.15'},
            'pass': lesson['longest_still_seconds'] <= 0.35 and lesson['picture_change_half_second_median'] >= 0.15}


def outro_check(mp4, plan):
    """The outro in the finished file must be the approved animation, frame for frame, after the wipe.
    The top caption region is ignored until the caption has faded."""
    cache = ROOT / plan['frames_cache']
    src = np.memmap(cache, np.uint8, 'r', shape=(cache.stat().st_size // (W * H * 4), H, W, 4))
    first = plan['outro_start_frame'] + plan['wipe_frames'][1] + 1
    end = plan['end_frame']
    got = frames_small(mp4, 108, 192, start=first / FPS, end=end / FPS)
    worst, n = 0.0, 0
    fade_end = plan['caption_fade_seconds'][1]
    for j, frame in enumerate(got):
        k = first + j - plan['outro_start_frame']
        s = plan['mapping'][min(k, len(plan['mapping']) - 1)]
        ref = np.asarray(src[s, :, :, :3], np.float32).reshape(192, 10, 108, 10, 3).mean(axis=(1, 3))
        diff = np.abs(frame - ref).mean(axis=2)
        if (first + j) / FPS < fade_end + 0.05:
            diff = diff[45:]                       # caption strip near y 260 still on screen
        worst = max(worst, float(diff.mean()))
        n += 1
    return {'frames_compared': n, 'worst_mean_difference': round(worst, 2), 'pass': n > 0 and worst < 6.0,
            'note': 'Mean absolute difference per pixel (0-255) against the approved outro frames, 108x192.'}


def keyword_sheet(mp4, items, out_png, cols=7):
    """Frames pulled from the finished MP4 at given times, tiled with their labels."""
    with tempfile.TemporaryDirectory() as tmp:
        files = []
        for n, (t, label) in enumerate(items):
            f = Path(tmp) / f'{n:03d}.png'
            safe = re.sub(r"[^A-Za-z0-9 .,!?-]", '', label)[:28]
            subprocess.run(['ffmpeg', '-v', 'error', '-nostdin', '-y', '-ss', f'{t:.3f}', '-i', str(mp4), '-frames:v', '1', '-vf',
                            f"scale=270:480,pad=270:510:0:30:white,drawtext=text='{safe}  {t:.2f}s':x=6:y=6:fontsize=18:fontcolor=black",
                            str(f)], check=True)
            files.append(str(f))
        subprocess.run(['montage', *files, '-tile', f'{cols}x', '-geometry', '+4+4', str(out_png)], check=True)
    return str(out_png)


def filmstrips(mp4, out_prefix, start=0.0, end=None, every=6.0):
    """5-frames-per-second strips, one per 6 seconds (15x2 tiles), for watching motion as stills."""
    end = end if end is not None else float(probe(mp4)['format']['duration'])
    files = []
    t = start
    while t < end - 0.05:
        f = Path(f'{out_prefix}-{len(files):02d}.png')
        subprocess.run(['ffmpeg', '-v', 'error', '-nostdin', '-y', '-ss', f'{t:.3f}', '-t', f'{min(every, end - t):.3f}', '-i', str(mp4),
                        '-vf', 'fps=5,scale=144:-1,tile=15x2', '-frames:v', '1', str(f)], check=True)
        files.append(str(f))
        t += every
    return files


def frame_strips(frame_files, out_prefix, per_strip=30):
    """Tile already-rendered PNG frames (5 per second) into strips like filmstrips()."""
    files = []
    for i in range(0, len(frame_files), per_strip):
        f = Path(f'{out_prefix}-{len(files):02d}.png')
        subprocess.run(['montage', *frame_files[i:i + per_strip], '-tile', '15x2', '-geometry', '144x256+0+0', str(f)], check=True)
        files.append(str(f))
    return files


# ---------------------------------------------------------------- delivery
def desktop():
    win = subprocess.run(['powershell.exe', '-NoProfile', '-NonInteractive', '-Command', '[Environment]::GetFolderPath("Desktop")'],
                         capture_output=True, text=True, timeout=60).stdout.strip()
    if not win:
        raise FinishError('Could not find the Windows Desktop.')
    return Path(subprocess.run(['wslpath', win], capture_output=True, text=True, check=True).stdout.strip()), win


def deliver(src, title, version=1, kind=''):
    """Copy to Drew's Windows Desktop as "Deep Six - <title> [kind ]v<N>.mp4". Never overwrites (a clash takes the
    next number), verifies the copy by checksum and copies again once on a mismatch. Never opens a player."""
    folder, win = desktop()
    label = f'{title} {kind} '.replace('  ', ' ') if kind else f'{title} '
    n = version
    while (folder / f'Deep Six - {label}v{n}.mp4').exists():
        n += 1
    dest = folder / f'Deep Six - {label}v{n}.mp4'
    want = sha(src)
    for _ in range(2):
        shutil.copyfile(src, dest)
        if sha(dest) == want:
            return {'status': 'copied_and_verified', 'destination': win.rstrip('\\') + '\\' + dest.name, 'name': dest.name,
                    'version': n, 'source': os.path.relpath(Path(src).resolve(), ROOT), 'bytes': Path(src).stat().st_size,
                    'sha256': want, 'player_opened': False}
    raise FinishError('The Desktop copy failed its checksum twice.')


def board(path, caption):
    """Put a picture or video on BOARD.md with tools/show (videos get a moving preview)."""
    out = subprocess.run([str(PROJECT / 'tools' / 'show'), str(path), caption], capture_output=True, text=True)
    return out.returncode == 0
