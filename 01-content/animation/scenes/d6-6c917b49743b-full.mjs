// Episode D6-6c917b49743b, full video: the approved hook (0-8.98 s), then the rest of the narration.
// One caption track covers every word. Shot plan: episodes/D6-6c917b49743b/full/shot-list.json.
import { makeFibres, createCaptions } from './paper-kit.mjs';
import { createScene as createHook } from './hook-fire-ant-drought.mjs';
import { createBody } from './d6-6c917b49743b-body.mjs';

const HOOK_END = 8.98;

export function createScene(config, timing) {
  const hook = createHook({ ...config, duration_seconds: 8.8 }, timing);
  const texture = makeFibres((config.seed ?? 1) | 0);
  const body = createBody(texture);
  const captions = createCaptions(timing.words, timing.caption_groups, {
    texture, centerY: config.caption_center_y ?? 1420, endTime: config.duration_seconds + 10,
  });
  const drawWorld = (ctx, t) => (t < HOOK_END ? hook.drawWorld(ctx, t) : body.draw(ctx, t));
  return {
    duration: config.duration_seconds,
    blurWindows: [...hook.blurWindows, ...body.blurWindows],
    drawWorld,
    drawOverlay: captions,
    draw(ctx, t) {
      drawWorld(ctx, t);
      captions(ctx, t);
    },
  };
}
