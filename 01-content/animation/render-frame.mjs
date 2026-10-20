import { createHash } from 'node:crypto';
import { readFile, writeFile, mkdir, access } from 'node:fs/promises';
import path from 'node:path';
import { fileURLToPath, pathToFileURL } from 'node:url';
import { createCanvas, GlobalFonts } from '@napi-rs/canvas';
import { withBrand } from './branding.mjs';

const root = path.dirname(fileURLToPath(import.meta.url));
const defaultConfig = 'episodes/D6-6c917b49743b/scene.json';
const scenes = {
  'fire-ant-brood': { module: 'scenes/fire-ant-brood.mjs', author: 'authoring-record.json', branding: 'overlay' },
  'fire-ant-style-options': { module: 'scenes/fire-ant-style-options.mjs', author: 'style-options-authoring.json', branding: 'scene' },
};
const sha = bytes => createHash('sha256').update(bytes).digest('hex');
const exists = async file => { try { await access(file); return true; } catch { return false; } };
const json = async file => JSON.parse(await readFile(file, 'utf8'));

async function main() {
  if (process.argv.length > 3) throw new Error('Usage: node render-frame.mjs [scene.json]');
  const configPath = path.resolve(root, process.argv[2] ?? defaultConfig);
  const config = await json(configPath);
  const definition = Object.hasOwn(scenes, config.scene_id) ? scenes[config.scene_id] : null;
  if (config.schema_version !== 1 || !definition) {
    throw new Error('Unsupported scene configuration.');
  }
  if (config.scene_id === 'fire-ant-style-options' && !['cartoon', 'paper', 'miniature'].includes(config.style)) {
    throw new Error('Unsupported visual style.');
  }
  if (config.width !== 1080 || config.height !== 1920) {
    throw new Error('This scene requires 1080×1920.');
  }
  if (!/^[a-zA-Z0-9_-]+$/.test(config.revision)) throw new Error('Invalid revision.');
  if (!Number.isInteger(config.seed) || !Number.isFinite(config.frame_time_seconds)
      || config.frame_time_seconds < 0 || config.frame_time_seconds > 600) {
    throw new Error('Invalid seed or frame time.');
  }
  for (const key of ['eyebrow', 'title', 'footer', 'illustrationNote']) {
    if (typeof config.labels?.[key] !== 'string' || config.labels[key].length > 160) {
      throw new Error(`Missing or excessive label: ${key}`);
    }
  }
  let brandReferenceHash = null;
  if (config.brand_profile) {
    const brand = await json(path.resolve(root, config.brand_profile));
    for (const key of ['cream', 'paper', 'ink', 'purple', 'lime']) {
      if (!/^#[0-9a-f]{6}$/i.test(brand.palette?.[key] ?? '')) throw new Error(`Invalid brand color: ${key}`);
    }
    brandReferenceHash = sha(await readFile(path.resolve(root, brand.reference_image)));
    if (brandReferenceHash !== brand.reference_sha256) throw new Error('The brand reference image changed. Review the palette first.');
    config.palette = brand.palette;
  }

  // Rendering never calls a model or a voice service. Verify the existing approval.
  const audioManifestPath = path.resolve(root, config.approved_audio.manifest);
  const audio = await json(audioManifestPath);
  if (audio.approved_narration_id !== config.episode_id || audio.audio_review?.status !== 'approved') {
    throw new Error('The episode has no matching approved narration.');
  }
  const approvedVariant = audio.variants.find(v => v.name === audio.audio_review.approved_variant);
  if (!approvedVariant || approvedVariant.status !== 'complete') throw new Error('Approved audio is incomplete.');
  const audioPath = path.resolve(path.dirname(audioManifestPath), approvedVariant.audio_file);
  const audioHash = sha(await readFile(audioPath));
  if (audioHash !== config.approved_audio.sha256 || audioHash !== approvedVariant.audio_sha256) {
    throw new Error('Approved audio fingerprint changed. Review the input before rendering.');
  }
  const spokenOriginal = await readFile(path.join(path.dirname(audioManifestPath), 'original.txt'), 'utf8');
  if (!spokenOriginal.replace(/\s+/g, ' ').includes(config.narration_excerpt.replace(/\s+/g, ' '))) {
    throw new Error('The selected excerpt is absent from the approved original narration.');
  }

  const files = [
    'render-frame.mjs', 'branding.mjs', definition.module, 'package-lock.json',
    'vendor/claude-animation/core.mjs', 'vendor/claude-animation/textures.mjs',
    'vendor/claude-animation/colony.mjs', 'vendor/claude-animation/provenance.json',
    'fonts/EBGaramond12-Regular.ttf', 'fonts/DejaVuSans.ttf',
  ];
  if (config.brand_profile) files.push(config.brand_profile);
  const fingerprints = { config: sha(await readFile(configPath)), approved_audio: audioHash };
  if (brandReferenceHash) fingerprints.brand_reference_image = brandReferenceHash;
  for (const file of files) fingerprints[file] = sha(await readFile(path.join(root, file)));
  const identity = sha(JSON.stringify({ fingerprints, node: process.version, platform: process.platform, arch: process.arch }));
  const outputDir = path.join(path.dirname(configPath), 'renders');
  const stem = `frame-${config.revision}`;
  const pngPath = path.join(outputDir, `${stem}.png`);
  const manifestPath = path.join(outputDir, `${stem}.json`);
  const reviewPath = path.join(outputDir, `${stem}.review.json`);

  if (await exists(manifestPath)) {
    const previous = await json(manifestPath);
    if (previous.input_identity !== identity) {
      throw new Error('This revision already has different inputs. Choose a new revision to preserve the reviewed candidate.');
    }
    if (!await exists(pngPath) || sha(await readFile(pngPath)) !== previous.png_sha256 || !await exists(reviewPath)) {
      throw new Error('The saved candidate is incomplete or changed. Review it before continuing.');
    }
    const savedReview = await json(reviewPath);
    if (savedReview.candidate_sha256 !== previous.png_sha256 || savedReview.candidate !== path.basename(pngPath)) {
      throw new Error('The review record does not match this frame.');
    }
    console.log(JSON.stringify({ status: 'existing_frame_reused', frame: path.relative(root, pngPath), png_sha256: previous.png_sha256 }));
    return;
  }
  if (await exists(pngPath) || await exists(reviewPath)) {
    throw new Error('An incomplete candidate already exists. Choose a new revision; no files were overwritten.');
  }

  for (const [file, alias] of [['EBGaramond12-Regular.ttf', 'D6Serif'], ['DejaVuSans.ttf', 'D6Sans']]) {
    if (!GlobalFonts.registerFromPath(path.join(root, 'fonts', file), alias)) throw new Error(`Cannot load font: ${file}`);
  }
  const { createScene } = await import(pathToFileURL(path.join(root, definition.module)));
  const started = performance.now();
  const applyOverlay = config.brand_profile && definition.branding === 'overlay';
  const baseConfig = applyOverlay
    ? { ...config, labels: { ...config.labels, eyebrow: '', title: '', footer: '' } }
    : config;
  const baseScene = createScene(baseConfig);
  const scene = applyOverlay ? withBrand(baseScene, config) : baseScene;
  const canvas = createCanvas(config.width, config.height);
  const ctx = canvas.getContext('2d');
  scene.draw(ctx, config.frame_time_seconds);
  const bytes = canvas.toBuffer('image/png');
  const pngHash = sha(bytes);
  const authoring = await json(path.join(root, definition.author));
  const manifest = {
    schema_version: 1, episode_id: config.episode_id, scene_id: config.scene_id,
    style: config.style ?? null,
    revision: config.revision, status: 'awaiting_style_review',
    width: config.width, height: config.height, frame_time_seconds: config.frame_time_seconds,
    input_identity: identity, inputs: fingerprints, png_sha256: pngHash,
    render_milliseconds: Math.round(performance.now() - started),
    node: process.version, platform: process.platform, architecture: process.arch,
    author_model: authoring.model, author_effort: authoring.reasoning_effort,
    brand_profile: config.brand_profile ?? null,
    local_revision: applyOverlay ? 'Deep Six ad colors applied as a reusable overlay; original Astra artwork preserved.' : null,
    approval_file: path.basename(reviewPath),
    audio_excerpt_aligned: false, animation_rendered: false,
  };
  const review = {
    schema_version: 1, episode_id: config.episode_id, scene_id: config.scene_id,
    style: config.style ?? null,
    candidate: path.basename(pngPath), candidate_sha256: pngHash,
    stage: 'style_review', decision: 'pending', feedback: [],
    approved_by: null, approved_at: null,
    next_step_after_approval: 'Measure the approved audio excerpt, then render the short moving test.',
  };
  await mkdir(outputDir, { recursive: true });
  await writeFile(pngPath, bytes, { flag: 'wx' });
  await writeFile(reviewPath, JSON.stringify(review, null, 2) + '\n', { flag: 'wx' });
  await writeFile(manifestPath, JSON.stringify(manifest, null, 2) + '\n', { flag: 'wx' });
  console.log(JSON.stringify({ status: manifest.status, frame: path.relative(root, pngPath), png_sha256: pngHash, render_milliseconds: manifest.render_milliseconds }));
}

main().catch(error => { console.error(error.message); process.exitCode = 1; });
