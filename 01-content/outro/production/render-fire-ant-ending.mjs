// Extend the existing paper scene, then use the approved outro frames unchanged
// except for replacing its neutral entry plate with the outgoing teaching scene.
import { readFile, writeFile, access } from 'node:fs/promises';
import { spawn } from 'node:child_process';
import { once } from 'node:events';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { createCanvas, GlobalFonts, loadImage } from '../../animation/node_modules/@napi-rs/canvas/index.js';
import { C, cut, polyPath, makeFibres, createCaptions, withCamera, eIO, prog, lerp, zoomTo } from '../../animation/scenes/paper-kit.mjs';
import { createNest } from '../../animation/scenes/nest-world.mjs';
import { questionMark } from '../../animation/scenes/yard-world.mjs';

const prod = path.dirname(fileURLToPath(import.meta.url));
const W = 1080, H = 1920, fps = 30, originalDuration = 79.2;
const voice = JSON.parse(await readFile(path.join(prod, 'fire-ant-closing-voice-check-v1.json'), 'utf8'));
const words = voice.segments.flatMap(s => s.words).map(w => ({ text: w.text, start: w.start, end: w.end }));
if (words.length !== 10 || !voice.exact_words_once) throw Error('Closing words need review.');
const closingFrames = Math.ceil(Math.max(Number(voice.probe.format.duration), words.at(-1).end + 0.25) * fps);
const closingDuration = closingFrames / fps, outroFrames = 165, totalFrames = closingFrames + outroFrames;
const output = path.join(prod, 'fire-ant-ending-picture-v2.mp4');
try { await access(output); throw Error('Existing output preserved.'); } catch (e) { if (e.code !== 'ENOENT') throw e; }
for (const [file, alias] of [['InterDisplay-Black.otf', 'D6Caption'], ['DejaVuSans.ttf', 'D6Sans']]) {
  if (!GlobalFonts.registerFromPath(path.resolve(prod, '../../animation/fonts', file), alias)) throw Error('Font unavailable.');
}
const texture = makeFibres(20261019), nest = createNest(texture);
const captions = createCaptions(words, [{ words: [0, 1, 2, 3] }, { words: [4, 5, 6, 7, 8, 9] }], {
  texture, centerY: 1420, minSize: 44, endTime: closingDuration + 0.3,
});
const state = { mound: 0, surfaceAnts: 0, traffic: 1,
  busy: { U1: 1, C2: 1, D1: 1, D3: 1 }, brood: { C1: 1, D2: 1 } };
const canvas = createCanvas(W, H), ctx = canvas.getContext('2d');

function world(local) {
  const t = originalDuration + local;
  const originalK = eIO(prog(t, 77.6, 79.3));
  const start = { x: lerp(400, 395, originalK), y: lerp(1210, 1215, originalK), zoom: zoomTo(2.05, 2.3, originalK) };
  const pull = eIO(prog(local, 0.15, 2.05));
  const camera = {
    x: lerp(start.x, 540, pull) + 6 * Math.sin(t * 0.9),
    y: lerp(start.y, 1480, pull) + 5 * Math.sin(t * 1.13 + 1),
    zoom: zoomTo(start.zoom, 0.64, pull) * (1 + 0.022 * Math.sin(t * 1.7)),
  };
  ctx.save(); ctx.setTransform(1, 0, 0, 1, 0, 0);
  cut(ctx, polyPath([[0, 0], [W, 0], [W, H], [0, H]]), C.paper, texture, 0, { grain: 0.8 });
  ctx.restore();
  withCamera(ctx, camera, () => {
    nest.draw(ctx, t, state);
    // The previous shot's question mark clears as the concluding view opens.
    const amount = 1 - eIO(prog(local, 0.1, 0.65));
    if (amount > 0) questionMark(ctx, texture, 545, 1120, 90, amount);
  });
}

const encoder = spawn('ffmpeg', ['-hide_banner', '-loglevel', 'error', '-nostdin', '-n',
  '-f', 'rawvideo', '-pix_fmt', 'rgba', '-s', `${W}x${H}`, '-r', String(fps), '-i', 'pipe:0',
  '-an', '-frames:v', String(totalFrames), '-c:v', 'libx264', '-profile:v', 'high', '-level:v', '4.0',
  '-threads', '4', '-preset', 'fast', '-crf', '17', '-pix_fmt', 'yuv420p', '-video_track_timescale', '15360',
  '-movflags', '+faststart', output], { stdio: ['pipe', 'ignore', 'pipe'] });
let errors = '';
encoder.stderr.on('data', x => errors += x.toString());
encoder.stdin.on('error', () => {});
const done = once(encoder, 'close').then(([code]) => { if (code) throw Error(errors.slice(-1200)); });
const samples = new Set([0, 30, 60, 95, closingFrames + 3, closingFrames + 9, closingFrames + 90]);
for (let frame = 0; frame < totalFrames; frame++) {
  const local = frame / fps;
  ctx.clearRect(0, 0, W, H);
  if (frame < closingFrames) {
    world(local); captions(ctx, local);
  } else {
    const outroFrame = frame - closingFrames, outroTime = outroFrame / fps;
    const picture = await loadImage(path.join(prod, 'fire-ant-outro-frames', `${String(outroFrame + 1).padStart(4, '0')}.png`));
    if (outroFrame < 9) {
      world(local); captions(ctx, local);
      // Match the approved top-to-bottom paper reveal, replacing only cream
      // outside the reveal with the outgoing moving teaching scene.
      ctx.save(); ctx.beginPath(); ctx.rect(0, 0, W, H * outroTime / 0.3); ctx.clip();
      ctx.drawImage(picture, 0, 0); ctx.restore();
    } else ctx.drawImage(picture, 0, 0);
  }
  if (samples.has(frame)) await writeFile(path.join(prod, `fire-ant-ending-v2-frame-${String(frame).padStart(3, '0')}.png`), canvas.toBuffer('image/png'));
  if (!encoder.stdin.write(Buffer.from(ctx.getImageData(0, 0, W, H).data))) await once(encoder.stdin, 'drain');
  if (frame % 30 === 0) console.log(JSON.stringify({ rendered_frames: frame + 1, total: totalFrames }));
}
encoder.stdin.end(); await done;
const recipe = {
  original_video_seconds: originalDuration, original_video_frames: 2376,
  closing_duration_seconds: closingDuration, closing_frames: closingFrames,
  closing_spoken_text: voice.spoken_text, closing_word_count: words.length,
  closing_caption_groups: ['So a missing mound', "doesn't mean the colony is gone."],
  caption_meaning_check: 'The negation remains visible through the entire concluding clause.',
  closing_gain_db: voice.matching_gain_db, closing_speech_speed_changed: false,
  outro_duration_seconds: 5.5, outro_frames: outroFrames, outro_start_seconds: originalDuration + closingDuration,
  outro_entry_modified_frames: [0, 8], outro_modification: 'Replace neutral cream below entry wipe with outgoing moving teaching scene. All later approved frames used as supplied.',
  approved_outro_speech_start_seconds: 0.55, approved_outro_audio_reused: true,
  ending_frames: totalFrames, ending_seconds: totalFrames / fps,
  full_frames: 2376 + totalFrames, full_duration_seconds: originalDuration + totalFrames / fps,
  fps, dimensions: [W, H], output, source_art_modules_used_read_only: ['nest-world.mjs', 'paper-kit.mjs', 'yard-world.mjs'],
  source_scene_seed: 20261019, lesson_rendered_again: false, publication: false,
};
await writeFile(path.join(prod, 'fire-ant-assembly-v2.json'), JSON.stringify(recipe, null, 2) + '\n');
console.log(JSON.stringify({ status: 'ending_picture_ready', frames: totalFrames, final_duration_seconds: recipe.full_duration_seconds }));
