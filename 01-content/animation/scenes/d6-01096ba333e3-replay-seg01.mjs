// Runner test only (tests/replay_wasp.py): the approved ensign-wasp lesson, hand-made by Opus on 20 Oct 2026, as one
// segment. It draws the lesson shots only; the runner adds the caption track and the approved outro itself.
import { createScene as approved } from './d6-01096ba333e3-full.mjs';

export function createScene(config, timing) {
  const s = approved(config, timing);
  const drawWorld = (ctx, t) => (s.shots.findLast(x => t >= x.start) ?? s.shots[0]).draw(ctx, t);
  return { duration: config.duration_seconds, blurWindows: s.blurWindows, drawWorld, drawOverlay: () => {},
    draw(ctx, t) { drawWorld(ctx, t); } };
}
