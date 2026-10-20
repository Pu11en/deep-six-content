"""End-to-end runner test on the approved ensign-wasp episode (D6-01096ba333e3), without overwriting anything.

The Director and Animator steps are taken from the hand-made, approved work of October 20: its shot list and its lesson code
(scenes/d6-01096ba333e3-full.mjs, wrapped as one segment that draws the lesson only). Everything after that is the runner's own
work: verify the MP3, fit the approved outro, join, detached render, exact audio, file checks, key-word frames, the whole-video
Reviewer (one real Opus call), Desktop copy and board entry. The new run folder is
episodes/D6-01096ba333e3/runs/d6-01096ba333e3-replay; the approved files are only read.

  python3 tests/replay_wasp.py setup     # create the run, waiting for "go"
  python3 make_video.py go --run d6-01096ba333e3-replay
  python3 tests/replay_wasp.py compare   # after delivery: frame-by-frame and audio comparison with the approved MP4
"""
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import make_video as mv  # noqa: E402
import video_finish as vf  # noqa: E402

EP = 'D6-01096ba333e3'
RUN = 'd6-01096ba333e3-replay'
FULL = ROOT / 'episodes' / EP / 'full'
APPROVED_PICTURE = FULL / 'renders' / 'full-v3.mp4'
APPROVED_FINAL = FULL / 'renders' / 'ensign-wasp-v3-final.mp4'

WRAPPER = """// Runner test only (tests/replay_wasp.py): the approved ensign-wasp lesson, hand-made by Opus on 20 Oct 2026, as one
// segment. It draws the lesson shots only; the runner adds the caption track and the approved outro itself.
import { createScene as approved } from './d6-01096ba333e3-full.mjs';

export function createScene(config, timing) {
  const s = approved(config, timing);
  const drawWorld = (ctx, t) => (s.shots.findLast(x => t >= x.start) ?? s.shots[0]).draw(ctx, t);
  return { duration: config.duration_seconds, blurWindows: s.blurWindows, drawWorld, drawOverlay: () => {},
    draw(ctx, t) { drawWorld(ctx, t); } };
}
"""


def setup():
    r = mv.new_run(EP, RUN, ROOT / '../audio/D6-01096ba333e3/full-chris-01/comparison.json', 'later', title='Runner Test Ensign Wasp')
    words = json.loads((FULL / 'words.json').read_text())
    plan = json.loads((FULL / 'shot-list.json').read_text())
    (r.dir / 'shot-list.json').write_text(json.dumps(plan, indent=1) + '\n')
    lesson_end = vf.outro_start_frame(words['words']) / vf.FPS
    segs = [{'name': f'{RUN}-seg01', 'start': 0, 'end': round(lesson_end, 4)}]
    (r.dir / 'segments.json').write_text(json.dumps(segs, indent=1) + '\n')
    (r.dir / 'caption-groups.json').write_text(json.dumps([g['words'] for g in words['caption_groups'] if g['words'][0] < 130]) + '\n')
    module = ROOT / 'scenes' / f'{RUN}-seg01.mjs'
    module.write_text(WRAPPER)
    r.d.update(steps_done=['plan', 'assets'], segments=segs, segments_done=[segs[0]['name']], new_assets=[],
               made_by={'plan': 'opus', segs[0]['name']: 'opus'}, segment_sha256={segs[0]['name']: mv.sha(module)},
               fix_rounds_allowed=0, test='Replay of the approved, hand-made ensign-wasp lesson; agent steps not re-run.')
    r.event('test setup: plan and lesson taken from the approved hand-made video of 20 Oct')
    r.save()
    print(f'Run {RUN} is waiting. Start it with: python3 make_video.py go --run {RUN}')


def frame_stream(mp4):
    return subprocess.Popen(['ffmpeg', '-v', 'error', '-nostdin', '-i', str(mp4), '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-'],
                            stdout=subprocess.PIPE)


def compare():
    """Byte and frame comparison of the runner's finished MP4 with the approved one Drew watched."""
    import numpy as np
    r = mv.find_run(RUN)
    final, picture = ROOT / r.d['final'], ROOT / r.d['picture']
    out = {'replay_final': mv.rel(final), 'approved_final': mv.rel(APPROVED_FINAL),
           'final_sha256_identical': vf.sha(final) == vf.sha(APPROVED_FINAL),
           'picture_sha256_identical': vf.sha(picture) == vf.sha(APPROVED_PICTURE)}
    size = 1080 * 1920 * 3
    a, b = frame_stream(final), frame_stream(APPROVED_FINAL)
    n = same = worst = 0
    while True:
        x, y = a.stdout.read(size), b.stdout.read(size)
        if len(x) < size or len(y) < size:
            out['frames_left_over'] = [len(x) // size, len(y) // size]
            break
        d = int(np.abs(np.frombuffer(x, np.uint8).astype(np.int16) - np.frombuffer(y, np.uint8)).max())
        n, same, worst = n + 1, same + (d == 0), max(worst, d)
    out.update(frames_compared=n, decoded_frames_identical=same, largest_pixel_difference=worst)
    pa, pb = vf.pcm(final), vf.pcm(APPROVED_FINAL)
    out['audio_samples_identical'] = bool(len(pa) == len(pb) and np.array_equal(pa, pb))
    (r.dir / 'replay-compare.json').write_text(json.dumps(out, indent=1) + '\n')
    print(json.dumps(out, indent=1))


if __name__ == '__main__':
    {'setup': setup, 'compare': compare}[sys.argv[1]]()
