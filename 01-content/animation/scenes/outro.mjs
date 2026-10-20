// The approved Deep Six outro for runner-made videos (same picture as the approved ensign-wasp ending).
// make_video.py fits it to each narrator with video_finish.fit_outro, which writes the frame plan named in
// config.outro.plan: when the cream-paper wipe starts, which source frame shows on each video frame, and when
// the top caption fades. Frames come from the shared cache of 01-content/outro/assets/outro-animation-v2.mp4.
import { readFileSync, openSync, readSync, existsSync } from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { createCanvas, ImageData } from '@napi-rs/canvas';
import { W, H, clamp, makeFibres, createCaptions } from './paper-kit.mjs';

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');

export function createOutro(config, timing) {
  const plan = JSON.parse(readFileSync(path.resolve(root, config.outro.plan), 'utf8'));
  const file = path.resolve(root, plan.frames_cache);
  if (!existsSync(file)) throw Error(`Outro frame cache missing (${plan.frames_cache}). Re-run make_video.py; it rebuilds the cache.`);
  const fd = openSync(file, 'r');
  const size = W * H * 4;
  const buffer = Buffer.alloc(size);
  const canvas = createCanvas(W, H);
  const octx = canvas.getContext('2d');
  let loaded = -1;
  const frame = k => {
    const source = plan.mapping[clamp(k, 0, plan.mapping.length - 1)];
    if (source !== loaded) {
      readSync(fd, buffer, 0, size, source * size);
      octx.putImageData(new ImageData(new Uint8ClampedArray(buffer.buffer, buffer.byteOffset, size), W, H), 0, 0);
      loaded = source;
    }
    return canvas;
  };
  const index = t => Math.round(t * 30 - plan.outro_start_frame);
  // The outro's own top caption for "Helping you understand pests.", faded before the logo flies to its spot.
  const caption = createCaptions(timing.words, [{ words: plan.caption_words, fade_out_seconds: plan.caption_fade_seconds }], {
    family: 'D6Caption', centerY: 260, maxWidth: 910, maxSize: 58, minSize: 48, texture: makeFibres(6), endTime: plan.caption_fade_seconds[1],
  });
  return {
    start: plan.outro_start_frame / 30,
    firstWord: plan.signoff_first_word,
    // Before the outro: the lesson. During the wipe: the last teaching picture and its caption under the cream paper.
    drawWorld(ctx, t, lessonWorld, lessonCaptions) {
      const k = index(t);
      if (k < 0) { lessonWorld(ctx, t); return; }
      ctx.save();
      ctx.setTransform(1, 0, 0, 1, 0, 0);
      if (k <= plan.wipe_frames[1]) {
        lessonWorld(ctx, t);
        lessonCaptions(ctx, t);
        ctx.save();
        ctx.beginPath();
        ctx.rect(0, 0, W, H * (k / 30) / plan.wipe_seconds);
        ctx.clip();
        ctx.drawImage(frame(k), 0, 0);
        ctx.restore();
      } else {
        ctx.drawImage(frame(k), 0, 0);
      }
      ctx.restore();
    },
    drawOverlay(ctx, t, lessonCaptions) {
      if (index(t) < 0) lessonCaptions(ctx, t);
      else caption(ctx, t);
    },
  };
}
