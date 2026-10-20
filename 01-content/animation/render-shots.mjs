// Render a shot-list scene (captions + approved narration) to a 9:16 MP4.
// Usage:
//   node render-shots.mjs <scene.json>                 full candidate: MP4, manifest, checks, contact sheet
//   node render-shots.mjs <scene.json> --sheet         key-frame contact sheet only (fast self-check)
//   node render-shots.mjs <scene.json> --at 0.5,2.6    single frames as PNGs (development)
import { createHash } from 'node:crypto';
import { readFile, writeFile, mkdir, access, rename } from 'node:fs/promises';
import path from 'node:path';
import { fileURLToPath, pathToFileURL } from 'node:url';
import { spawn, execFile } from 'node:child_process';
import { promisify } from 'node:util';
import { createCanvas, GlobalFonts } from '@napi-rs/canvas';

const root = path.dirname(fileURLToPath(import.meta.url));
const json = async file => JSON.parse(await readFile(file, 'utf8'));
const sha = bytes => createHash('sha256').update(bytes).digest('hex');
const exists = async file => { try { await access(file); return true; } catch { return false; } };
const run = promisify(execFile);

async function load(configPath) {
  const config = await json(configPath);
  if (config.schema_version !== 1 || config.width !== 1080 || config.height !== 1920 || !Number.isInteger(config.fps)
      || !/^[a-zA-Z0-9_-]+$/.test(config.revision) || !/^scenes\/[a-z0-9-]+\.mjs$/.test(config.module)) {
    throw Error('Unsupported scene settings. Videos must be 1080x1920 (9:16).');
  }
  const start = config.audio_excerpt_start_seconds;
  const end = config.audio_excerpt_end_seconds;
  if (!(start >= 0 && end > start && Math.abs(config.duration_seconds - (end - start)) < 1e-6)) throw Error('Invalid excerpt.');
  const folder = path.dirname(configPath);
  const timing = await json(path.resolve(folder, config.timing));
  // words.json times count from the start of the full MP3. With "absolute_time": true the scene,
  // shot list and captions keep those times and frames are drawn at start + i / fps. Otherwise
  // everything counts from the start of this segment.
  config.time_offset = config.absolute_time ? start : 0;
  if (!config.absolute_time) timing.words = timing.words.map(w => ({ ...w, start: w.start - start, end: w.end - start }));

  // Approved style C and approved narration must be unchanged.
  const selectionPath = path.resolve(root, config.approved_style.selection);
  const selection = await json(selectionPath);
  const candidate = selection.candidates.find(c => c.key === config.approved_style.option);
  if (selection.selected_option !== config.approved_style.option || !candidate) throw Error('Style is not the selected one.');
  const styleReview = await json(path.resolve(path.dirname(selectionPath), candidate.review));
  const styleBytes = await readFile(path.resolve(path.dirname(selectionPath), candidate.image));
  if (styleReview.decision !== 'approved' || sha(styleBytes) !== config.approved_style.sha256) throw Error('Approved style changed.');
  const manifestPath = path.resolve(root, config.approved_audio.manifest);
  const audioManifest = await json(manifestPath);
  const variant = audioManifest.variants.find(v => v.name === audioManifest.audio_review?.approved_variant);
  if (audioManifest.audio_review?.status !== 'approved' || !variant || end > variant.duration_seconds) throw Error('Approved narration unavailable.');
  const audioPath = path.resolve(path.dirname(manifestPath), variant.audio_file);
  const audioHash = sha(await readFile(audioPath));
  if (audioHash !== config.approved_audio.sha256 || audioHash !== timing.audio_sha256) throw Error('Approved audio fingerprint changed.');
  const spoken = (await readFile(path.join(path.dirname(manifestPath), 'original.txt'), 'utf8')).replace(/\s+/g, ' ');
  if (!spoken.includes(timing.excerpt.replace(/’/g, "'")) && !spoken.replace(/’/g, "'").includes(timing.excerpt)) {
    throw Error('Excerpt is not approved wording.');
  }
  const brand = await json(path.resolve(root, config.brand_profile));
  config.palette = brand.palette;

  for (const [file, alias] of [['EBGaramond12-Regular.ttf', 'D6Serif'], ['DejaVuSans.ttf', 'D6Sans'], ['InterDisplay-Black.otf', 'D6Caption']]) {
    if (!GlobalFonts.registerFromPath(path.join(root, 'fonts', file), alias)) throw Error(`Missing bundled font ${file}.`);
  }
  const { createScene } = await import(pathToFileURL(path.join(root, config.module)).href);
  const scene = createScene(config, timing);
  return { config, timing, scene, folder, audioPath, audioHash, styleBytes };
}

// Draw one frame. Fast camera moves get sub-frame motion blur (captions stay sharp).
function makeFrameDrawer(scene, config) {
  const { samples = 5, shutter_seconds: shutter = 1 / 60 } = config.motion_blur ?? {};
  const accum = createCanvas(config.width, config.height);
  const actx = accum.getContext('2d');
  return (ctx, t) => {
    // A window may carry its own sample count and shutter: [start, end, samples, shutter].
    const window = scene.blurWindows?.find(([a, b]) => t >= a && t <= b);
    const n = window?.[2] ?? samples;
    const open = window?.[3] ?? shutter;
    if (!window || n < 2) {
      scene.drawWorld(ctx, t);
    } else {
      for (let i = 0; i < n; i += 1) {
        const ts = Math.max(0, t + (i / (n - 1) - 0.5) * open);
        actx.save();
        actx.setTransform(1, 0, 0, 1, 0, 0);
        actx.globalAlpha = 1;
        scene.drawWorld(actx, ts);
        actx.restore();
        ctx.save();
        ctx.setTransform(1, 0, 0, 1, 0, 0);
        ctx.globalAlpha = 1 / (i + 1);
        ctx.drawImage(accum, 0, 0);
        ctx.restore();
      }
    }
    scene.drawOverlay(ctx, t);
  };
}

async function contactSheet(drawFrame, config, shotList, outFile, range = [0, Infinity]) {
  const all = shotList.shots.flatMap(shot => shot.beats.map(beat => ({ ...beat, shot: shot.id })))
    .filter(b => b.at >= range[0] && b.at < range[1]);
  const pages = [];
  for (let i = 0; i < all.length; i += 24) pages.push(all.slice(i, i + 24));
  const files = [];
  for (const [pi, beats] of pages.entries()) {
    const file = pages.length > 1 ? outFile.replace(/\.png$/, `-${pi + 1}.png`) : outFile;
    await contactPage(drawFrame, config, beats, file);
    files.push(file);
  }
  return files;
}

async function contactPage(drawFrame, config, beats, outFile) {
  const end = config.time_offset + config.duration_seconds + (config.tail_seconds ?? 0);
  const times = beats.map(b => Math.min(end - 0.01, b.at + 0.12));
  const tileW = 216;
  const tileH = 384;
  const cols = 6;
  const rows = Math.ceil(times.length / cols);
  const sheet = createCanvas(cols * tileW, rows * (tileH + 44));
  const sctx = sheet.getContext('2d');
  sctx.fillStyle = '#F6EFE2';
  sctx.fillRect(0, 0, sheet.width, sheet.height);
  const frame = createCanvas(config.width, config.height);
  const fctx = frame.getContext('2d');
  for (const [i, t] of times.entries()) {
    drawFrame(fctx, t);
    const x = (i % cols) * tileW;
    const y = Math.floor(i / cols) * (tileH + 44);
    sctx.drawImage(frame, x + 4, y + 40, tileW - 8, tileH - 8);
    sctx.fillStyle = '#1E1B22';
    sctx.font = '19px D6Sans';
    sctx.fillText(`${beats[i].shot} ${t.toFixed(2)}s`, x + 6, y + 18);
    sctx.font = '16px D6Sans';
    sctx.fillText(beats[i].word.slice(0, 22), x + 6, y + 36);
  }
  await writeFile(outFile, sheet.toBuffer('image/png'));
}

async function main() {
  const args = process.argv.slice(2);
  if (!args[0]) throw Error('Usage: node render-shots.mjs <scene.json> [--sheet | --at t1,t2]');
  const configPath = path.resolve(root, args[0]);
  const { config, timing, scene, folder, audioPath, audioHash, styleBytes } = await load(configPath);
  const shotList = await json(path.resolve(folder, config.shot_list));
  const drawFrame = makeFrameDrawer(scene, config);
  const devFolder = path.join(folder, 'dev');

  if (args[1] === '--at') {
    await mkdir(devFolder, { recursive: true });
    const canvas = createCanvas(config.width, config.height);
    const ctx = canvas.getContext('2d');
    for (const value of args[2].split(',')) {
      const t = Number(value);
      const started = performance.now();
      drawFrame(ctx, t);
      const file = path.join(devFolder, `frame-${t.toFixed(2)}.png`);
      await writeFile(file, canvas.toBuffer('image/png'));
      console.log(JSON.stringify({ t, file: path.relative(root, file), ms: Math.round(performance.now() - started) }));
    }
    return;
  }
  if (args[1] === '--check-motion') {
    const fps = config.fps;
    const total = config.duration_seconds + (config.tail_seconds ?? 0);
    const canvas = createCanvas(config.width, config.height);
    const ctx = canvas.getContext('2d');
    const small = createCanvas(54, 96);
    const sctx = small.getContext('2d');
    const frames = [];
    let still = 0;
    let longest = 0;
    let prev = null;
    for (let i = 0; i < Math.round(total * fps); i += 1) {
      drawFrame(ctx, config.time_offset + i / fps);
      sctx.drawImage(canvas, 0, 0, 54, 96);
      const px = Uint8ClampedArray.from(sctx.getImageData(0, 0, 54, 96).data);
      if (prev) {
        let d = 0;
        for (let p = 0; p < px.length; p += 4) d += Math.abs(px[p] - prev[p]) + Math.abs(px[p + 1] - prev[p + 1]) + Math.abs(px[p + 2] - prev[p + 2]);
        still = d / (54 * 96 * 3) < 0.6 ? still + 1 : 0;
        longest = Math.max(longest, still);
      }
      prev = px;
      frames.push(px);
    }
    const half = Math.round(fps / 2);
    const change = [];
    for (let i = half; i < frames.length; i += 1) {
      let c = 0;
      for (let p = 0; p < frames[i].length; p += 4) {
        if (Math.max(Math.abs(frames[i][p] - frames[i - half][p]), Math.abs(frames[i][p + 1] - frames[i - half][p + 1]), Math.abs(frames[i][p + 2] - frames[i - half][p + 2])) > 40) c += 1;
      }
      change.push(c / (54 * 96));
    }
    change.sort((x, y) => x - y);
    console.log(JSON.stringify({ longest_still_seconds: Number((longest / fps).toFixed(3)), picture_change_half_second_median: Number(change[Math.floor(change.length / 2)].toFixed(3)), targets: { longest_still_seconds: '<= 0.35', picture_change_half_second_median: '>= 0.15' } }));
    return;
  }
  if (args[1] === '--sheet') {
    await mkdir(devFolder, { recursive: true });
    const range = args[2] ? args[2].split('-').map(Number) : [config.time_offset, config.time_offset + config.duration_seconds + (config.tail_seconds ?? 0)];
    const files = await contactSheet(drawFrame, config, shotList, path.join(devFolder, 'beats-sheet.png'), range);
    console.log(JSON.stringify({ sheets: files.map(f => path.relative(root, f)) }));
    return;
  }

  // Full candidate. Never overwrite a reviewed revision.
  const renders = path.join(folder, 'renders');
  const stem = `${config.output_stem ?? 'hook'}-${config.revision}`;
  const videoPath = path.join(renders, `${stem}.mp4`);
  const partialPath = path.join(renders, `${stem}.partial.mp4`);
  const manifestPath = path.join(renders, `${stem}.json`);
  for (const file of [videoPath, partialPath, manifestPath, path.join(renders, `${stem}.review.json`)]) {
    if (await exists(file)) throw Error(`${path.basename(file)} exists. Use a new revision; nothing was overwritten.`);
  }
  await mkdir(renders, { recursive: true });
  const fps = config.fps;
  const duration = config.duration_seconds;
  const total = duration + (config.tail_seconds ?? 0);
  const frameCount = Math.round(total * fps);
  const fadeStart = (duration - 0.08).toFixed(3);
  const ffmpegArgs = ['-hide_banner', '-loglevel', 'error', '-n', '-f', 'rawvideo', '-pixel_format', 'rgba',
    '-video_size', `${config.width}x${config.height}`, '-framerate', String(fps), '-i', 'pipe:0',
    '-ss', String(config.audio_excerpt_start_seconds), '-t', String(duration), '-i', audioPath,
    '-map', '0:v:0', '-map', '1:a:0', '-af', `afade=t=out:st=${fadeStart}:d=0.08,apad=whole_dur=${total}`,
    '-c:v', 'libx264', '-preset', 'medium', '-crf', '18', '-pix_fmt', 'yuv420p', '-r', String(fps),
    '-c:a', 'aac', '-b:a', '192k', '-ar', '44100', '-t', String(total), '-movflags', '+faststart', partialPath];
  const ffmpeg = spawn('ffmpeg', ffmpegArgs, { stdio: ['pipe', 'ignore', 'pipe'] });
  let errorText = '';
  ffmpeg.stderr.on('data', chunk => { errorText = (errorText + chunk).slice(-4000); });
  const finished = new Promise(resolve => ffmpeg.on('close', code => resolve(code)));
  const canvas = createCanvas(config.width, config.height);
  const ctx = canvas.getContext('2d');
  const small = createCanvas(54, 96);
  const sctx = small.getContext('2d');
  let previous = null;
  const motion = [];
  const history = [];
  const halfSecond = Math.round(fps / 2);
  const change = [];
  const started = performance.now();
  for (let i = 0; i < frameCount; i += 1) {
    drawFrame(ctx, config.time_offset + i / fps);
    sctx.drawImage(canvas, 0, 0, 54, 96);
    const pixels = sctx.getImageData(0, 0, 54, 96).data;
    if (previous) {
      let diff = 0;
      for (let p = 0; p < pixels.length; p += 4) diff += Math.abs(pixels[p] - previous[p]) + Math.abs(pixels[p + 1] - previous[p + 1]) + Math.abs(pixels[p + 2] - previous[p + 2]);
      motion.push(diff / (54 * 96 * 3));
    }
    previous = Uint8ClampedArray.from(pixels);
    history.push(previous);
    if (history.length > halfSecond) {
      // Share of the picture that changes within half a second (same measure as the pacing research).
      const old = history.shift();
      let changed = 0;
      for (let p = 0; p < previous.length; p += 4) {
        if (Math.max(Math.abs(previous[p] - old[p]), Math.abs(previous[p + 1] - old[p + 1]), Math.abs(previous[p + 2] - old[p + 2])) > 40) changed += 1;
      }
      change.push(changed / (54 * 96));
    }
    await new Promise((resolve, reject) => ffmpeg.stdin.write(canvas.data(), e => (e ? reject(e) : resolve())));
    if (i % 60 === 0) console.log(JSON.stringify({ rendered_frames: i + 1, total_frames: frameCount }));
  }
  ffmpeg.stdin.end();
  const code = await finished;
  if (code !== 0) throw Error(`ffmpeg failed: ${errorText}`);
  const renderSeconds = (performance.now() - started) / 1000;
  await rename(partialPath, videoPath);

  // Checks: format, duration, and the longest stretch without visible change.
  const probe = JSON.parse((await run('ffprobe', ['-v', 'error', '-show_streams', '-show_format', '-of', 'json', videoPath])).stdout);
  const video = probe.streams.find(s => s.codec_type === 'video');
  const audio = probe.streams.find(s => s.codec_type === 'audio');
  let longestStill = 0;
  let run0 = 0;
  for (const m of motion) { run0 = m < 0.6 ? run0 + 1 : 0; longestStill = Math.max(longestStill, run0); }
  const sheetFiles = await contactSheet(drawFrame, config, shotList, path.join(renders, `${stem}-beats.png`),
    [config.time_offset, config.time_offset + total]);
  const bytes = await readFile(videoPath);
  const reviewPath = path.join(renders, `${stem}.review.json`);
  const manifest = {
    candidate: path.basename(videoPath),
    revision: config.revision,
    video_sha256: sha(bytes),
    approval_file: path.basename(reviewPath),
    created_with: { scene: config.module, kit: 'scenes/paper-kit.mjs', renderer: 'render-shots.mjs', node: process.version },
    inputs: {
      config_sha256: sha(await readFile(configPath)),
      scene_sha256: sha(await readFile(path.join(root, config.module))),
      kit_sha256: sha(await readFile(path.join(root, 'scenes/paper-kit.mjs'))),
      timing_sha256: sha(await readFile(path.resolve(folder, config.timing))),
      shot_list_sha256: sha(await readFile(path.resolve(folder, config.shot_list))),
      approved_audio_sha256: audioHash,
      approved_style_sha256: sha(styleBytes),
    },
    checks: {
      width: video.width, height: video.height, aspect: `${video.width}:${video.height}`,
      fps: video.r_frame_rate, frames: Number(video.nb_frames), video_seconds: Number(video.duration),
      audio_seconds: Number(audio.duration), container_seconds: Number(probe.format.duration),
      longest_still_seconds: Number((longestStill / fps).toFixed(3)),
      mean_motion: Number((motion.reduce((a, b) => a + b, 0) / motion.length).toFixed(3)),
      picture_change_half_second_median: Number([...change].sort((a, b) => a - b)[Math.floor(change.length / 2)].toFixed(3)),
      render_seconds: Number(renderSeconds.toFixed(1)),
    },
    contact_sheets: sheetFiles.map(f => path.basename(f)),
  };
  const review = { episode_id: config.episode_id, stage: 'hook_motion_review', candidate: manifest.candidate,
    candidate_sha256: manifest.video_sha256, decision: 'pending', feedback: [], approved_by: null, approved_at: null };
  await writeFile(reviewPath, JSON.stringify(review, null, 2) + '\n', { flag: 'wx' });
  await writeFile(manifestPath, JSON.stringify(manifest, null, 2) + '\n', { flag: 'wx' });
  console.log(JSON.stringify({ video: path.relative(root, videoPath), ...manifest.checks }));
}

main().catch(error => { console.error(error.message); process.exit(1); });
