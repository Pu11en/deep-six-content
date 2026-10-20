// Local video composition. Actual official logo pixels; no paid calls.
import { readFile, writeFile, access } from 'node:fs/promises';
import { createHash } from 'node:crypto';
import { spawn } from 'node:child_process';
import { once } from 'node:events';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { createCanvas, loadImage, GlobalFonts } from '../../animation/node_modules/@napi-rs/canvas/index.js';
import { createCaptions, makeFibres } from '../../animation/scenes/paper-kit.mjs';

const prod = path.dirname(fileURLToPath(import.meta.url));
const assets = path.resolve(prod, '../assets');
const W = 1080, H = 1920, FPS = 30, frames = 165;
const entry = 0.3, voiceOffset = 0.55, releaseFrame = 73;
const release = releaseFrame / FPS, land = release + 0.60;
const track = JSON.parse(await readFile(path.join(prod, 'v2-lens-track-clean.json'), 'utf8'));
const voice = JSON.parse(await readFile(path.join(prod, 'v2-voice-check.json'), 'utf8'));
const logoPath = path.join(assets, 'deep-six-logo.png');
const logoBytes = await readFile(logoPath);
if (createHash('sha256').update(logoBytes).digest('hex') !== '135630619ad2fe7d263d27f2a380e9add1f8c733d1005e889d8b93f4b9560ee6') throw Error('Official logo identity changed.');
const logo = await loadImage(logoBytes);
GlobalFonts.registerFromPath(path.resolve(prod, '../../animation/fonts/InterDisplay-Black.otf'), 'D6Caption');
const captionWords = voice.segments[0].words.map(w => ({ text: w.word.trim(), start: w.start + voiceOffset, end: w.end + voiceOffset }));
const captions = createCaptions(captionWords, [{ words: [0, 1, 2, 3], fade_out_seconds: [2.37, 2.55] }], {
  family: 'D6Caption', centerY: 260, maxWidth: 910, maxSize: 58, minSize: 48,
  texture: makeFibres(6), endTime: 2.55,
});
const outputs = [path.join(assets, 'outro-animation-v2.mp4'), path.join(prod, 'v2-review-picture.mp4')];
for (const file of outputs) {
  try { await access(file); throw Error('Existing composed output preserved: ' + path.basename(file)); }
  catch (e) { if (e.code !== 'ENOENT') throw e; }
}

function encoder(file) {
  const process = spawn('ffmpeg', ['-hide_banner', '-loglevel', 'error', '-nostdin', '-n',
    '-f', 'rawvideo', '-pix_fmt', 'rgba', '-s', `${W}x${H}`, '-r', String(FPS), '-i', 'pipe:0',
    '-an', '-frames:v', String(frames), '-c:v', 'libx264', '-threads', '3', '-preset', 'fast',
    '-crf', '17', '-pix_fmt', 'yuv420p', '-movflags', '+faststart', file], { stdio: ['pipe', 'ignore', 'pipe'] });
  let stderr = '';
  process.stderr.on('data', x => stderr += x.toString());
  process.stdin.on('error', () => {});
  const complete = once(process, 'close').then(([code]) => { if (code) throw Error(stderr.slice(-1000)); });
  return { process, complete };
}

const a = encoder(outputs[0]), b = encoder(outputs[1]);
const canvas = createCanvas(W, H), ctx = canvas.getContext('2d');
const clamp = n => Math.max(0, Math.min(1, n));
const ease = u => 1 - (1 - clamp(u)) ** 3;
const smooth = u => { u = clamp(u); return u * u * (3 - 2 * u); };
const atRelease = track.frames[releaseFrame];
if (atRelease.missing) throw Error('Lens tracking unavailable at release.');
const launchWidth = atRelease.width * 0.82;
const final = { x: 540, y: 290, width: 520 };

function drawLogo(cx, cy, width, alpha = 1) {
  const height = width * logo.height / logo.width;
  ctx.save(); ctx.globalAlpha = alpha;
  ctx.drawImage(logo, cx - width / 2, cy - height / 2, width, height);
  ctx.restore();
}

function branding(frame) {
  const t = frame / FPS;
  if (t < 2.05) return;
  if (frame < releaseFrame) {
    const lens = track.frames[frame];
    if (lens.missing) throw Error('Missing lens position during reveal.');
    const alpha = smooth((t - 2.05) / 0.17);
    ctx.save();
    ctx.beginPath();
    ctx.ellipse(lens.x, lens.y, lens.width * 0.485, lens.height * 0.485, lens.angle * Math.PI / 180, 0, Math.PI * 2);
    ctx.clip();
    drawLogo(lens.x, lens.y, lens.width * 0.82, alpha);
    ctx.restore();
  } else if (t < land) {
    const u = clamp((t - release) / 0.45), p = ease(u);
    const x = atRelease.x + (final.x - atRelease.x) * p;
    const y = atRelease.y + (final.y - atRelease.y) * p - Math.sin(Math.PI * p) * 80;
    let width = launchWidth + (final.width * 1.03 - launchWidth) * p;
    if (u >= 1) width = final.width * (1.03 - 0.03 * smooth((t - release - 0.45) / 0.15));
    drawLogo(x, y, width);
  } else drawLogo(final.x, final.y, final.width);
}

async function send(encoder, bytes) {
  if (!encoder.process.stdin.write(bytes)) await once(encoder.process.stdin, 'drain');
}

for (let frame = 0; frame < frames; frame++) {
  const source = await loadImage(path.join(prod, 'v2-source-frames', `${String(frame + 1).padStart(4, '0')}.png`));
  ctx.clearRect(0, 0, W, H); ctx.drawImage(source, 0, 0);
  branding(frame);
  await send(a, Buffer.from(ctx.getImageData(0, 0, W, H).data));
  captions(ctx, frame / FPS);
  await send(b, Buffer.from(ctx.getImageData(0, 0, W, H).data));
  if (frame % 30 === 0) console.log(JSON.stringify({ composed_frames: frame + 1, total: frames }));
}
a.process.stdin.end(); b.process.stdin.end();
await Promise.all([a.complete, b.complete]);
await writeFile(path.join(prod, 'v2-composition-timing.json'), JSON.stringify({
  fps: FPS, frames, duration_seconds: frames / FPS, dimensions: [W, H],
  source_dimensions: [720, 1280], source_fps: 24, resolution_note: '1080p delivery is a scale-up of a native 720p AI source.',
  source_in_seconds: 0, source_out_seconds: 5.2, entry_seconds: entry,
  character_action_reviewed: 'Anticipation, jump, robe flare, wide arm swing, recoil and settle. Continuous generated motion retained.',
  source_motion_retimed: false, source_audio_used: false,
  logo_reveal_seconds: [2.05, release], logo_release_seconds: release,
  logo_landed_seconds: land, logo_final_center: [final.x, final.y], logo_final_width: final.width,
  logo_source: 'assets/deep-six-logo.png', logo_sha256: createHash('sha256').update(logoBytes).digest('hex'),
  logo_source_dimensions: [logo.width, logo.height], logo_generated_by_ai: false,
  voice_start_seconds: voiceOffset, company_name_start_seconds: 3.18, company_name_timing_basis: 'ASR on final muxed review; approximate word boundary',
  final_spoken_word_end_seconds: 4.24, final_brand_hold_after_speech_seconds: 1.26,
  review_caption: 'HELPING YOU UNDERSTAND PESTS.', caption_end_seconds: 2.55,
  reusable_master_has_audio: false, reusable_master_has_captions: false,
  no_fire_ant_footage_in_review: true, finished_media_approved: false,
}, null, 2) + '\n');
console.log(JSON.stringify({ status: 'composed', outputs }));
