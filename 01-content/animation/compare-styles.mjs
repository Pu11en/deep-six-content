import { readFile, writeFile } from 'node:fs/promises';
import { createHash } from 'node:crypto';
import { fileURLToPath } from 'node:url';
import path from 'node:path';
import { createCanvas, GlobalFonts, loadImage } from '@napi-rs/canvas';

const root = path.dirname(fileURLToPath(import.meta.url));
const folder = path.join(root, 'episodes/D6-6c917b49743b/style-options');
const sha = bytes => createHash('sha256').update(bytes).digest('hex');
const options = JSON.parse(await readFile(path.join(folder, 'options.json'), 'utf8'));
const brand = JSON.parse(await readFile(path.join(root, 'brand.json'), 'utf8'));
if (!GlobalFonts.registerFromPath(path.join(root, 'fonts/DejaVuSans.ttf'), 'D6Sans')) throw new Error('Missing comparison font.');
const board = createCanvas(1092, 2008), ctx = board.getContext('2d');
ctx.fillStyle = brand.palette.paper; ctx.fillRect(0, 0, 1092, 2008);
ctx.fillStyle = brand.palette.purple; ctx.font = '36px D6Sans';
ctx.fillText('Four different looks', 40, 54);
ctx.font = '20px D6Sans'; ctx.fillText('Same lesson. Same Deep Six colors.', 40, 86);
const checked = [];
for (const [i, candidate] of options.candidates.entries()) {
  const bytes = await readFile(path.join(folder, candidate.image));
  const manifest = JSON.parse(await readFile(path.join(folder, candidate.manifest), 'utf8'));
  const hash = sha(bytes);
  if (hash !== manifest.png_sha256) throw new Error(`Candidate ${candidate.key} changed.`);
  const img = await loadImage(bytes);
  if (img.width !== 1080 || img.height !== 1920) throw new Error(`Candidate ${candidate.key} has wrong dimensions.`);
  const x = 40 + (i % 2) * 526;
  const y = 112 + Math.floor(i / 2) * 948;
  ctx.fillStyle = brand.palette.lime; ctx.fillRect(x, y + 7, 34, 34);
  ctx.fillStyle = brand.palette.ink; ctx.font = '24px D6Sans'; ctx.fillText(candidate.key, x + 8, y + 32);
  ctx.font = '25px D6Sans'; ctx.fillText(candidate.name, x + 46, y + 32);
  ctx.drawImage(img, x, y + 52, 486, 864);
  checked.push({ key: candidate.key, image: candidate.image, sha256: hash, width: img.width, height: img.height });
}
const png = board.toBuffer('image/png');
const target = path.join(folder, 'comparison.png');
await writeFile(target, png, { flag: 'wx' });
await writeFile(path.join(folder, 'comparison-manifest.json'), JSON.stringify({
  status: 'awaiting_style_selection', episode_id: options.episode_id,
  png_sha256: sha(png), width: 1092, height: 2008, candidates: checked,
  note: 'Scaled full-frame previews, with no cropping or recoloring. Individual full-resolution files are retained.',
}, null, 2) + '\n', { flag: 'wx' });
console.log(JSON.stringify({ status: 'comparison_ready', path: path.relative(root, target), candidates: checked.length }));
