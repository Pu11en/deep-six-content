import { createHash } from 'node:crypto';
import { readFile, writeFile, mkdir, access, rename } from 'node:fs/promises';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { spawn, execFile } from 'node:child_process';
import { promisify } from 'node:util';
import { createCanvas, GlobalFonts } from '@napi-rs/canvas';

const root = path.dirname(fileURLToPath(import.meta.url));
const json = async file => JSON.parse(await readFile(file, 'utf8'));
const sha = bytes => createHash('sha256').update(bytes).digest('hex');
const exists = async file => { try { await access(file); return true; } catch { return false; } };
const run = promisify(execFile);

async function main() {
  if (process.argv.length !== 3) throw Error('Usage: node render-motion.mjs episode/motion/scene.json');
  const configPath = path.resolve(root, process.argv[2]);
  const config = await json(configPath);
  if (config.schema_version !== 1 || config.scene_id !== 'fire-ant-paper-motion' || config.style !== 'paper'
      || config.width !== 1080 || config.height !== 1920 || config.fps !== 24
      || !Number.isInteger(config.seed) || !/^[a-zA-Z0-9_-]+$/.test(config.revision)) {
    throw Error('Unsupported motion settings.');
  }
  const start = config.audio_excerpt_start_seconds, end = config.audio_excerpt_end_seconds;
  const duration = end - start;
  if (!Number.isFinite(start) || !Number.isFinite(end) || !Number.isFinite(config.duration_seconds)
      || start < 0 || duration < 8 || duration > 18
      || Math.abs(config.duration_seconds - duration) > 0.000001) throw Error('Invalid measured excerpt.');
  for (const key of ['eyebrow', 'title', 'footer', 'illustrationNote']) {
    if (typeof config.labels?.[key] !== 'string' || config.labels[key].length > 160) throw Error('Invalid label.');
  }
  const selectionPath = path.resolve(root, config.approved_style.selection);
  const selection = await json(selectionPath);
  const candidate = selection.candidates.find(c => c.key === 'C');
  if (selection.episode_id !== config.episode_id || selection.selected_option !== 'C' || !candidate) {
    throw Error('Cut-paper style is not selected for this episode.');
  }
  const styleReview = await json(path.resolve(path.dirname(selectionPath), candidate.review));
  const styleBytes = await readFile(path.resolve(path.dirname(selectionPath), candidate.image));
  if (styleReview.decision !== 'approved' || sha(styleBytes) !== styleReview.candidate_sha256
      || sha(styleBytes) !== config.approved_style.sha256) throw Error('Approved illustration changed.');
  const audioManifestPath = path.resolve(root, config.approved_audio.manifest);
  const audio = await json(audioManifestPath);
  const variant = audio.variants.find(v => v.name === audio.audio_review?.approved_variant);
  if (audio.approved_narration_id !== config.episode_id || audio.audio_review?.status !== 'approved'
      || variant?.status !== 'complete' || end > variant.duration_seconds) throw Error('Approved narration is unavailable.');
  const audioPath = path.resolve(path.dirname(audioManifestPath), variant.audio_file);
  const audioHash = sha(await readFile(audioPath));
  if (audioHash !== variant.audio_sha256 || audioHash !== config.approved_audio.sha256) throw Error('Approved audio fingerprint changed.');
  const spoken = await readFile(path.join(path.dirname(audioManifestPath), 'original.txt'), 'utf8');
  if (!spoken.replace(/\s+/g, ' ').includes(config.narration_excerpt.replace(/\s+/g, ' '))) throw Error('Excerpt is not approved wording.');
  const brandPath = path.resolve(root, config.brand_profile);
  const brand = await json(brandPath);
  for (const key of ['cream', 'paper', 'ink', 'purple', 'lime']) {
    if (!/^#[0-9a-f]{6}$/i.test(brand.palette?.[key] ?? '')) throw Error('Invalid brand palette.');
  }
  if (sha(await readFile(path.resolve(root, brand.reference_image))) !== brand.reference_sha256) throw Error('Brand reference changed.');
  config.palette = brand.palette;
  const files = ['render-motion.mjs', 'scenes/fire-ant-paper-motion.mjs', 'package-lock.json',
    'fonts/EBGaramond12-Regular.ttf', 'fonts/DejaVuSans.ttf'];
  const inputs = { config: sha(await readFile(configPath)), approved_audio: audioHash,
    approved_style: sha(styleBytes), brand: sha(await readFile(brandPath)), brand_reference: brand.reference_sha256 };
  for (const file of files) inputs[file] = sha(await readFile(path.join(root, file)));
  const encoderVersion = (await run('ffmpeg', ['-version'])).stdout.split('\n')[0];
  const identity = sha(JSON.stringify({ inputs, node: process.version, platform: process.platform, arch: process.arch, encoderVersion }));
  const folder = path.join(path.dirname(configPath), 'renders');
  const stem = `motion-${config.revision}`;
  const videoPath = path.join(folder, `${stem}.mp4`);
  const partialPath = path.join(folder, `${stem}.partial.mp4`);
  const manifestPath = path.join(folder, `${stem}.json`);
  const reviewPath = path.join(folder, `${stem}.review.json`);
  if (await exists(manifestPath)) {
    const saved = await json(manifestPath), review = await json(reviewPath);
    if (saved.input_identity !== identity) throw Error('Changed inputs require a new motion revision.');
    if (sha(await readFile(videoPath)) !== saved.video_sha256 || review.candidate_sha256 !== saved.video_sha256
        || review.candidate !== path.basename(videoPath)) throw Error('Saved video or review changed.');
    for (const frame of saved.sample_frames) {
      if (sha(await readFile(path.join(folder, frame.file))) !== frame.sha256) throw Error('Saved sample frame changed.');
    }
    console.log(JSON.stringify({ status: 'existing_video_reused', video: path.relative(root, videoPath) }));
    return;
  }
  // The encoder rounds a duration to the nearest whole frame at this rate.
  const frameCount = Math.round(duration * config.fps);
  const sampleIndices = [...new Set([0, 0.25, 0.5, 0.75, 1].map(t => Math.round(t * (frameCount - 1))))];
  for (const file of [videoPath, partialPath, reviewPath, ...sampleIndices.map(i => path.join(folder, `${stem}-frame-${i}.png`))]) {
    if (await exists(file)) throw Error('An unfinished candidate exists. Use a new revision; no outputs were overwritten.');
  }
  for (const [file, alias] of [['EBGaramond12-Regular.ttf', 'D6Serif'], ['DejaVuSans.ttf', 'D6Sans']]) {
    if (!GlobalFonts.registerFromPath(path.join(root, 'fonts', file), alias)) throw Error('Missing bundled font.');
  }
  const { createScene } = await import('./scenes/fire-ant-paper-motion.mjs');
  const scene = createScene(config), canvas = createCanvas(config.width, config.height);
  const ctx = canvas.getContext('2d');
  await mkdir(folder, { recursive: true });
  const args = ['-hide_banner', '-loglevel', 'error', '-n', '-f', 'rawvideo', '-pixel_format', 'rgba',
    '-video_size', `${config.width}x${config.height}`, '-framerate', String(config.fps), '-i', 'pipe:0',
    '-ss', String(start), '-t', String(duration), '-i', audioPath, '-map', '0:v:0', '-map', '1:a:0',
    '-c:v', 'libx264', '-preset', 'fast', '-crf', '20', '-pix_fmt', 'yuv420p',
    '-c:a', 'aac', '-b:a', '192k', '-ar', '44100', '-t', String(duration), '-movflags', '+faststart', partialPath];
  const ffmpeg = spawn('ffmpeg', args, { stdio: ['pipe', 'ignore', 'pipe'] });
  let errorText = '';
  ffmpeg.stderr.on('data', chunk => { errorText = (errorText + chunk).slice(-4000); });
  ffmpeg.stdin.on('error', () => {});
  const completion = new Promise(resolve => {
    ffmpeg.on('error', error => resolve({ error }));
    ffmpeg.on('close', code => resolve({ code }));
  });
  const started = performance.now(), samples = [];
  try {
    for (let i = 0; i < frameCount; i++) {
      scene.draw(ctx, i / config.fps);
      if (sampleIndices.includes(i)) {
        const bytes = canvas.toBuffer('image/png');
        const file = `${stem}-frame-${i}.png`;
        await writeFile(path.join(folder, file), bytes, { flag: 'wx' });
        samples.push({ frame: i, time_seconds: i / config.fps, file, sha256: sha(bytes) });
      }
      await new Promise((resolve, reject) => ffmpeg.stdin.write(canvas.data(), error => error ? reject(error) : resolve()));
      if (i % 48 === 0) console.log(JSON.stringify({ rendered_frames: i + 1, total_frames: frameCount }));
    }
    ffmpeg.stdin.end();
    const result = await completion;
    if (result.error || result.code !== 0) throw Error(`Encoder failed: ${result.error?.message ?? errorText}`);
  } catch (error) {
    ffmpeg.kill('SIGTERM');
    await completion;
    throw error;
  }
  const probe = JSON.parse((await run('ffprobe', ['-v', 'error', '-show_streams', '-show_format', '-of', 'json', partialPath])).stdout);
  const video = probe.streams.find(s => s.codec_type === 'video'), sound = probe.streams.find(s => s.codec_type === 'audio');
  if (video?.codec_name !== 'h264' || video.width !== 1080 || video.height !== 1920 || video.pix_fmt !== 'yuv420p'
      || video.r_frame_rate !== '24/1' || Number(video.nb_frames) !== frameCount
      || sound?.codec_name !== 'aac' || Math.abs(Number(probe.format.duration) - duration) > 0.1
      || Math.abs(Number(sound.duration) - duration) > 0.1) throw Error('Encoded output failed format checks.');
  await rename(partialPath, videoPath);
  const hash = sha(await readFile(videoPath));
  const author = await json(path.join(root, 'motion-paper-authoring.json'));
  const manifest = { schema_version: 1, episode_id: config.episode_id, scene_id: config.scene_id,
    revision: config.revision, status: 'awaiting_motion_review', input_identity: identity, inputs,
    video_sha256: hash, width: 1080, height: 1920, fps: 24, frame_count: frameCount,
    duration_seconds: Number(probe.format.duration), audio_excerpt_start_seconds: start, audio_excerpt_end_seconds: end,
    audio_alignment_method: 'Offline word timestamps matched to the exact approved excerpt; see excerpt-timing.json.',
    sample_frames: samples, encoder: encoderVersion, render_milliseconds: Math.round(performance.now() - started),
    author_model: author.model, author_effort: author.reasoning_effort, approval_file: path.basename(reviewPath),
    limitations: ['Short movement test only; full video and final captions are not produced.', 'Motion needs Drew’s review.'] };
  const review = { schema_version: 1, episode_id: config.episode_id, candidate: path.basename(videoPath),
    candidate_sha256: hash, stage: 'motion_review', decision: 'pending', feedback: [], approved_by: null, approved_at: null };
  await writeFile(reviewPath, JSON.stringify(review, null, 2) + '\n', { flag: 'wx' });
  await writeFile(manifestPath, JSON.stringify(manifest, null, 2) + '\n', { flag: 'wx' });
  console.log(JSON.stringify({ status: manifest.status, video: path.relative(root, videoPath), seconds: manifest.duration_seconds, sha256: hash }));
}

main().catch(error => { console.error(error.message); process.exitCode = 1; });
