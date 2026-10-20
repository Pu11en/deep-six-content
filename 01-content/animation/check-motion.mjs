import { readFile, writeFile } from 'node:fs/promises';
import { createHash } from 'node:crypto';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { createCanvas, GlobalFonts } from '@napi-rs/canvas';
import { createScene } from './scenes/fire-ant-paper-motion.mjs';

const root = path.dirname(fileURLToPath(import.meta.url));
const json = async p => JSON.parse(await readFile(p, 'utf8'));
const sha = b => createHash('sha256').update(b).digest('hex');
if (process.argv.length !== 3) throw Error('Usage: node check-motion.mjs path/to/scene.json');
const configPath = path.resolve(root, process.argv[2]);
const config = await json(configPath);
config.palette = (await json(path.resolve(root, config.brand_profile))).palette;
for (const [file, alias] of [['EBGaramond12-Regular.ttf', 'D6Serif'], ['DejaVuSans.ttf', 'D6Sans']]) {
  if (!GlobalFonts.registerFromPath(path.join(root, 'fonts', file), alias)) throw Error('Missing font.');
}
const scene = createScene(config);
const render = (s, t) => { const c = createCanvas(1080, 1920); s.draw(c.getContext('2d'), t); return c; };
const fractions = [0, 0.2, 0.4, 0.6, 0.8, 1];
const started = performance.now();
const frames = fractions.map(t => render(scene, t * config.duration_seconds));
const hashes = frames.map(c => sha(c.toBuffer('image/png')));
const repeated = render(scene, config.duration_seconds * 0.4);
const fresh = render(createScene(config), config.duration_seconds * 0.4);
const regionHash = (c, y, height) => sha(c.getContext('2d').getImageData(0, y, 1080, height).data);
const opaque = c => { const data = c.data(); for (let i = 3; i < data.length; i += 4) if (data[i] !== 255) return false; return true; };
const author = await json(path.join(root, 'motion-paper-authoring.json'));
const checks = {
  out_of_order_repeat_matches: sha(repeated.toBuffer('image/png')) === hashes[2],
  fresh_scene_matches: sha(fresh.toBuffer('image/png')) === hashes[2],
  visible_motion_exists: new Set(hashes).size >= 4,
  all_frames_opaque: frames.every(opaque),
  header_stays_fixed: frames.every(c => regionHash(c, 0, 790) === regionHash(frames[0], 0, 790)),
  footer_stays_fixed: frames.every(c => regionHash(c, 1490, 430) === regionHash(frames[0], 1490, 430)),
  original_paper_source_unchanged: sha(await readFile(path.join(root, author.source_input))) === author.source_input_sha256,
};
const firstFrameMatches = hashes[0] === config.approved_style.sha256;
const sheet = createCanvas(1080, 1380), ctx = sheet.getContext('2d');
ctx.fillStyle = config.palette.paper; ctx.fillRect(0, 0, 1080, 1380);
for (let i = 0; i < frames.length; i++) {
  const x = (i % 3) * 360, y = Math.floor(i / 3) * 690;
  ctx.fillStyle = config.palette.purple; ctx.font = '22px D6Sans';
  ctx.fillText(`${(fractions[i] * config.duration_seconds).toFixed(2)} sec`, x + 16, y + 30);
  ctx.drawImage(frames[i], x + 10, y + 45, 340, 604);
}
const folder = path.dirname(configPath);
await writeFile(path.join(folder, 'motion-contact-sheet.png'), sheet.toBuffer('image/png'), { flag: 'wx' });
const result = { status: Object.values(checks).every(Boolean) ? 'passed' : 'needs_review', checks,
  first_frame_exactly_matches_approved_png: firstFrameMatches,
  sample_frame_sha256: hashes, sampled_times_seconds: fractions.map(t => t * config.duration_seconds),
  total_check_milliseconds: Math.round(performance.now() - started),
  limits: ['Frame checks do not approve movement quality.', 'Contact sheet is visual inspection evidence, not a video playback test.'] };
await writeFile(path.join(folder, 'motion-checks.json'), JSON.stringify(result, null, 2) + '\n', { flag: 'wx' });
console.log(JSON.stringify(result));
if (result.status !== 'passed') process.exitCode = 1;
