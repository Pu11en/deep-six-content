// Backyard set and props for the closing segments, in cut-paper style C.
// Matches the hook's yard (same house, fence, lawn and mound spot) so the story returns to it.
import {
  W, H, C, Path2D, clamp, lerp, eOut, eIO, eBack, rng, hash, pathOf, mix,
  cut, polyPath, smoothPath, ovalPath, capsulePath, bandPath, tuft, puff,
} from './paper-kit.mjs';

const TAU = Math.PI * 2;
export const MOUND = { x: 520, base: 1065, width: 560, height: 265 };

function domePoints(cx, baseY, width, height, seed, n = 28) {
  const random = rng(seed);
  const points = [];
  for (let i = 0; i <= n; i += 1) {
    const a = Math.PI + (i / n) * Math.PI;
    const bump = i === 0 || i === n ? 0 : (random() - 0.5) * 0.09;
    const lift = Math.pow(Math.abs(Math.sin(a)), 0.85);
    points.push([cx + Math.cos(a) * width / 2 * (1 + bump * 0.4), baseY - lift * height * (1 + bump)]);
  }
  return points;
}

function cloud(ctx, texture, x, y, s, color = C.white) {
  ctx.save();
  ctx.translate(x, y);
  ctx.scale(s, s);
  const path = new Path2D();
  for (const [ox, oy, r] of [[-95, 18, 62], [-30, -22, 82], [52, -6, 70], [110, 22, 50], [10, 30, 70]]) path.ellipse(ox, oy, r, r * 0.82, 0, 0, TAU);
  cut(ctx, path, color, texture, 7);
  ctx.restore();
}

export function questionMark(ctx, texture, x, y, size, k, tilt = 0) {
  if (k <= 0.01) return;
  const s = eBack(clamp(k), 2.2);
  ctx.save();
  ctx.translate(x, y);
  ctx.rotate(tilt + 0.08 * Math.sin(k * 6));
  ctx.scale(s, s);
  cut(ctx, ovalPath(0, 0, size * 0.62, size * 0.62), C.paper, texture, 8);
  ctx.fillStyle = C.purple;
  ctx.font = `${size}px D6Caption`;
  ctx.textAlign = 'center';
  ctx.textBaseline = 'middle';
  ctx.fillText('?', 0, size * 0.05);
  ctx.restore();
}

export function bigX(ctx, texture, x, y, size, k) {
  if (k <= 0.01) return;
  const s = eBack(clamp(k), 2.4);
  ctx.save();
  ctx.translate(x, y);
  ctx.scale(s, s);
  ctx.rotate(-0.06);
  cut(ctx, capsulePath([-size, -size], [size, size], 46, 46), C.purple, texture, 12);
  cut(ctx, capsulePath([size, -size], [-size, size], 46, 46), C.purple, texture, 12);
  ctx.restore();
}

export function pushpin(ctx, texture, x, y, k) {
  if (k <= 0.01) return;
  const drop = 1 - eOut(clamp(k));
  ctx.save();
  ctx.translate(x, y - drop * 320);
  ctx.rotate(0.35);
  ctx.scale(1.7, 1.7);
  cut(ctx, capsulePath([0, 0], [0, 70], 6, 3), '#9AA0A6', texture, 3);
  cut(ctx, polyPath([[-26, -6], [26, -6], [18, -40], [-18, -40]]), C.lime, texture, 6);
  cut(ctx, ovalPath(0, -52, 46, 24), '#8DA955', texture, 8);
  cut(ctx, ovalPath(0, -58, 40, 20), C.lime, texture, 0);
  ctx.fillStyle = 'rgba(255,255,255,0.6)';
  ctx.fill(ovalPath(-14, -62, 12, 6));
  ctx.restore();
}

export function gauge(ctx, texture, x, groundY, scale, needle, k = 1) {
  if (k <= 0.01) return;
  const s = scale * eBack(clamp(k), 2);
  ctx.save();
  ctx.translate(x, groundY);
  ctx.scale(s, s);
  cut(ctx, capsulePath([0, 0], [0, -260], 13, 11), '#8A5A3C', texture, 6);
  cut(ctx, ovalPath(0, -330, 112, 112), C.ink, texture, 10);
  cut(ctx, ovalPath(0, -330, 96, 96), C.paper, texture, 0);
  ctx.save();
  ctx.translate(0, -330);
  ctx.strokeStyle = C.ink;
  ctx.lineCap = 'round';
  for (let i = 0; i <= 8; i += 1) {
    const a = Math.PI * (0.8 + i * 0.175);
    ctx.lineWidth = i % 4 === 0 ? 7 : 4;
    ctx.beginPath();
    ctx.moveTo(Math.cos(a) * 66, Math.sin(a) * 66);
    ctx.lineTo(Math.cos(a) * 84, Math.sin(a) * 84);
    ctx.stroke();
  }
  ctx.rotate(needle);
  cut(ctx, polyPath([[-8, 0], [0, -78], [8, 0]]), C.purple, texture, 3);
  ctx.restore();
  cut(ctx, ovalPath(0, -330, 16, 16), C.lime, texture, 2);
  ctx.restore();
}

// A homeowner in cut paper, side view. pose: walk (0..1 amount), phase, face (1 = right), arm ('down' | 'chin' | 'scratch' | 'hold'), look (head tilt).
export function person(ctx, texture, x, groundY, scale, pose = {}) {
  const { walk = 0, phase = 0, face = -1, arm = 'down', look = 0, armK = 1, scratch = 0 } = pose;
  const skin = '#E6AE86';
  const shirt = '#6E90B5';
  const shirtDark = '#5A7799';
  const pants = '#7E6A55';
  const swing = Math.sin(phase) * walk;
  const bob = -Math.abs(Math.cos(phase)) * 10 * walk;
  ctx.save();
  ctx.translate(x, groundY);
  ctx.scale(scale * face, scale);
  ctx.translate(0, bob);
  const leg = (hipX, a, color) => {
    const knee = [hipX + Math.sin(a) * 120, -330 + Math.cos(a) * 120];
    const foot = [knee[0] + Math.sin(a * 0.6) * 120, knee[1] + 120];
    cut(ctx, capsulePath([hipX, -440], knee, 30, 26), color, texture, 5);
    cut(ctx, capsulePath(knee, foot, 26, 22), color, texture, 5);
    cut(ctx, smoothPath([[foot[0] - 22, foot[1] - 14], [foot[0] + 48, foot[1] - 12], [foot[0] + 56, foot[1] + 10], [foot[0] - 26, foot[1] + 10]], true), '#3E2C2A', texture, 4);
  };
  leg(-6, -swing * 0.45, '#6B5947');
  const armPose = (back) => {
    const sh = [8, -760];
    if (!back && arm === 'scratch') return [sh, [70, -830 + 6 * scratch], [40 + 14 * scratch, -930 - 10 * scratch]];
    if (!back && arm === 'chin') return [sh, [90, -650], [70, -800]];
    if (!back && arm === 'hold') return [sh, [120, -680], [230, -660]];
    const a = (back ? 1 : -1) * swing * 0.5;
    return [sh, [sh[0] + Math.sin(a) * 140, sh[1] + Math.cos(a) * 140], [sh[0] + Math.sin(a * 1.3) * 270, sh[1] + Math.cos(a) * 270]];
  };
  const drawArm = (pts, color) => {
    cut(ctx, capsulePath(pts[0], pts[1], 26, 23), color, texture, 5);
    cut(ctx, capsulePath(pts[1], pts[2], 23, 20), skin, texture, 4);
    cut(ctx, ovalPath(pts[2][0], pts[2][1], 26, 28), skin, texture, 3);
  };
  drawArm(armPose(true), shirtDark);
  cut(ctx, smoothPath([[-70, -800], [70, -805], [92, -620], [80, -430], [-80, -430], [-92, -620]], true), shirt, texture, 9);
  cut(ctx, smoothPath([[-78, -470], [80, -470], [84, -410], [-84, -410]], true), pants, texture, 4);
  leg(10, swing * 0.45, pants);
  cut(ctx, capsulePath([0, -800], [0, -850], 26, 24), skin, texture, 3);
  ctx.save();
  ctx.translate(0, -905);
  ctx.rotate(look);
  cut(ctx, ovalPath(0, 0, 78, 84), skin, texture, 8);
  cut(ctx, smoothPath([[-84, -10], [-70, -70], [-10, -98], [60, -84], [86, -30], [40, -50], [-20, -46], [-60, -10]], true), '#4A3236', texture, 5);
  cut(ctx, ovalPath(-50, 6, 14, 20), '#D99A72', texture, 2);
  cut(ctx, ovalPath(42, -6, 7, 9), C.ink, texture, 1);
  cut(ctx, ovalPath(82, 14, 12, 10), '#D99A72', texture, 1);
  ctx.restore();
  if (armK > 0) drawArm(armPose(false), shirt);
  ctx.restore();
}

// Thought bubble above a point; the content callback draws inside, clipped, in bubble space (0, 0 at centre).
export function thoughtBubble(ctx, texture, x, y, w, h, k, content) {
  if (k <= 0.01) return;
  const s = eBack(clamp(k), 2);
  const shape = new Path2D();
  const bumps = 11;
  for (let i = 0; i <= bumps; i += 1) {
    const a = (i / bumps) * TAU;
    const px = Math.cos(a) * w / 2;
    const py = Math.sin(a) * h / 2;
    if (i === 0) shape.moveTo(px, py);
    const a2 = ((i + 0.5) / bumps) * TAU;
    shape.quadraticCurveTo(Math.cos(a2) * w / 2 * 1.22, Math.sin(a2) * h / 2 * 1.22, Math.cos((i + 1) / bumps * TAU) * w / 2, Math.sin((i + 1) / bumps * TAU) * h / 2);
  }
  shape.closePath();
  ctx.save();
  ctx.translate(x, y);
  ctx.scale(s, s);
  cut(ctx, ovalPath(w * 0.18, h * 0.62, 26, 22), C.paper, texture, 5);
  cut(ctx, ovalPath(w * 0.26, h * 0.8, 15, 13), C.paper, texture, 4);
  cut(ctx, shape, C.paper, texture, 10);
  ctx.save();
  ctx.clip(shape);
  if (content) content(ctx);
  ctx.restore();
  ctx.restore();
}

export function createYard(texture) {
  const random = rng(404);
  const dome = domePoints(MOUND.x, MOUND.base, MOUND.width, MOUND.height, 9);
  const flare = [[MOUND.x - MOUND.width / 2 - 40, MOUND.base + 6], ...dome, [MOUND.x + MOUND.width / 2 + 40, MOUND.base + 6]];
  const moundPath = smoothPath([...flare, [MOUND.x, MOUND.base + 12]], true);
  const sx = MOUND.width / 480;
  const sy = MOUND.height / 230;
  const shadowPath = smoothPath([[30, -0.98 * 230], [150, -0.75 * 230], [236, -40], [270, 6], [60, 10], [90, -90]].map(([x, y]) => [MOUND.x + x * sx, MOUND.base + y * sy]), true);
  const highlightPath = smoothPath([[-190, -60], [-120, -170], [-20, -212], [40, -200], [-60, -150], [-150, -40]].map(([x, y]) => [MOUND.x + x * sx, MOUND.base + y * sy]), true);
  const crumbs = [];
  while (crumbs.length < 34) {
    const x = MOUND.x + (random() - 0.5) * MOUND.width * 0.92;
    const y = MOUND.base - random() * MOUND.height;
    const nx = (x - MOUND.x) / (MOUND.width / 2);
    const ny = (MOUND.base - y) / MOUND.height;
    if (nx * nx + ny * ny < 0.86) crumbs.push([x, y, 7 + random() * 11, random() * 3, ['#D9AE80', '#A86F4E', '#8E5A3F', '#C88B60'][crumbs.length % 4]]);
  }
  const outline = pathOf(dome);
  const fence = [];
  for (let x = -40; x < 690; x += 58) fence.push(polyPath([[x, 905], [x, 790], [x + 23, 762], [x + 46, 790], [x + 46, 905]]));
  const bushes = Array.from({ length: 16 }, (_, i) => [-60 + i * 78 + (random() - 0.5) * 30, 860 + (random() - 0.5) * 30, 62 + random() * 48, i % 2 ? '#7DA650' : '#8DB55A']);
  const stripes = [];
  let y = 990;
  for (let i = 0; i < 9; i += 1) {
    const h = 26 * Math.pow(1.33, i);
    if (i % 2 === 0) stripes.push(bandPath(-200, 1300, y, y + h, 3, 30 + i));
    y += h;
  }
  const tufts = Array.from({ length: 22 }, (_, i) => ({ x: -40 + i * 54 + random() * 30, size: 70 + random() * 40, seed: i + 3 }));
  const front = Array.from({ length: 13 }, (_, i) => ({ x: -60 + i * 95 + random() * 40, size: 210 + random() * 120, seed: i + 50 }));

  function house(ctx) {
    ctx.save();
    ctx.translate(845, 848);
    ctx.rotate(-0.03);
    ctx.scale(1.55, 1.55);
    cut(ctx, 'M-73 -66 L55 -72 L62 35 L-78 39 L-75 -12 Z', C.paper, texture, 8);
    cut(ctx, 'M55 -72 L92 -51 L96 21 L62 35 Z', C.cream, texture, 5);
    cut(ctx, 'M-98 -61 L-15 -143 L10 -125 L82 -64 L61 -50 L-15 -111 L-77 -48 Z', C.purple, texture, 7);
    cut(ctx, 'M10 -125 L42 -125 L109 -50 L82 -64 Z', '#796882', texture, 4);
    cut(ctx, 'M2 -23 L34 -24 L37 36 L0 36 Z', C.lime, texture, 3);
    cut(ctx, 'M-57 -34 L-28 -36 L-26 -7 L-57 -6 Z', C.purple, texture, 2);
    ctx.restore();
  }

  function mound(ctx, k) {
    if (k <= 0.01) return;
    ctx.save();
    ctx.translate(MOUND.x, MOUND.base);
    ctx.scale(1, eBack(clamp(k), 2));
    ctx.translate(-MOUND.x, -MOUND.base);
    cut(ctx, moundPath, '#B57553', texture, 10);
    ctx.save();
    ctx.clip(moundPath);
    cut(ctx, shadowPath, '#94603F', texture, 0);
    cut(ctx, highlightPath, '#CD966A', texture, 0);
    for (const [x, yy, r, a, color] of crumbs) cut(ctx, ovalPath(x, yy, r, r * 0.72, a), color, texture, 2);
    ctx.restore();
    ctx.restore();
  }

  function dashed(ctx, k, color = C.purple) {
    if (k <= 0.01) return;
    const pts = outline.slice(eIO(clamp(k)));
    ctx.save();
    ctx.setLineDash([30, 20]);
    ctx.lineCap = 'round';
    ctx.lineWidth = 11;
    ctx.strokeStyle = 'rgba(30,27,34,0.25)';
    ctx.beginPath();
    pts.forEach(([x, yy], i) => (i ? ctx.lineTo(x + 3, yy + 6) : ctx.moveTo(x + 3, yy + 6)));
    ctx.stroke();
    ctx.strokeStyle = color;
    ctx.beginPath();
    pts.forEach(([x, yy], i) => (i ? ctx.lineTo(x, yy) : ctx.moveTo(x, yy)));
    ctx.stroke();
    ctx.restore();
  }

  function trace(ctx, k) {
    if (k <= 0.01) return;
    const pts = outline.slice(eIO(clamp(k)));
    ctx.save();
    ctx.lineCap = 'round';
    ctx.lineJoin = 'round';
    ctx.lineWidth = 22;
    ctx.strokeStyle = 'rgba(30,27,34,0.3)';
    ctx.beginPath();
    pts.forEach(([x, yy], i) => (i ? ctx.lineTo(x + 3, yy - 2) : ctx.moveTo(x + 3, yy - 2)));
    ctx.stroke();
    ctx.lineWidth = 20;
    ctx.strokeStyle = C.lime;
    ctx.beginPath();
    pts.forEach(([x, yy], i) => (i ? ctx.lineTo(x, yy - 8) : ctx.moveTo(x, yy - 8)));
    ctx.stroke();
    ctx.restore();
  }

  function magnifier(ctx, lens, t, xray) {
    const r = lens.r ?? 238;
    ctx.save();
    const glass = ovalPath(lens.x, lens.y, r, r);
    ctx.save();
    ctx.clip(glass);
    if (xray) xray(ctx);
    ctx.fillStyle = 'rgba(255,255,255,0.08)';
    ctx.fill(glass);
    ctx.restore();
    ctx.translate(lens.x, lens.y);
    ctx.rotate(lens.angle ?? -0.16);
    ctx.save();
    ctx.rotate(Math.PI / 4);
    cut(ctx, capsulePath([r + 6, 0], [r + 330, 0], 36, 40), C.purple, texture, 12);
    cut(ctx, polyPath([[r + 40, -38], [r + 70, -38], [r + 70, 38], [r + 40, 38]]), C.lime, texture, 2);
    ctx.restore();
    const ring = new Path2D();
    ring.ellipse(0, 0, r + 30, r + 30, 0, 0, TAU);
    ring.ellipse(0, 0, r, r, 0, 0, TAU);
    ctx.save();
    ctx.fillStyle = C.ink;
    ctx.shadowColor = 'rgba(30,20,25,0.35)';
    ctx.shadowBlur = 10;
    ctx.shadowOffsetX = 5;
    ctx.shadowOffsetY = 12;
    ctx.fill(ring, 'evenodd');
    ctx.restore();
    ctx.strokeStyle = C.lime;
    ctx.lineWidth = 6;
    ctx.beginPath();
    ctx.ellipse(0, 0, r + 11, r + 11, 0, 0, TAU);
    ctx.stroke();
    ctx.save();
    ctx.beginPath();
    ctx.ellipse(0, 0, r, r, 0, 0, TAU);
    ctx.clip();
    ctx.strokeStyle = 'rgba(255,255,255,0.55)';
    ctx.lineWidth = 14;
    ctx.beginPath();
    ctx.arc(0, 0, r - 34, Math.PI * 1.08, Math.PI * 1.42);
    ctx.stroke();
    ctx.restore();
    ctx.restore();
  }

  return {
    outline,
    // s: mound (0..1 pop), dashed (0..1 draw), trace (0..1), lens {x, y, r, angle, xray(ctx)}, front (bool)
    drawBack(ctx, t, s = {}) {
      ctx.fillStyle = C.sky;
      ctx.fillRect(-1200, -1200, 3600, 2400);
      cloud(ctx, texture, ((190 + t * 18) % 1700) - 250, 330, 1.0);
      cloud(ctx, texture, ((820 + t * 12) % 1700) - 250, 480, 0.7);
      for (const [x, yy, r, color] of bushes) cut(ctx, ovalPath(x, yy, r, r * 0.85), color, texture, 6);
      house(ctx);
      for (const p of fence) cut(ctx, p, C.paper, texture, 6);
      cut(ctx, polyPath([[-40, 812], [700, 806], [700, 826], [-40, 832]]), C.cream, texture, 4);
      cut(ctx, polyPath([[-40, 868], [700, 864], [700, 884], [-40, 888]]), C.cream, texture, 4);
      cut(ctx, bandPath(-600, 1700, 902, 2800, 4, 21), C.grassMid, texture, 8);
      cut(ctx, bandPath(-600, 1700, 952, 2800, 5, 22), C.lime, texture, 9);
      for (const stripe of stripes) cut(ctx, stripe, '#A0CB4C', null, 0);
      for (const tf of tufts) tuft(ctx, texture, tf.x, 955, tf.size, tf.seed, ['#93BD5C', '#7FA84E'], 0.05 * Math.sin(t * 2.4 + tf.x * 0.02));
      mound(ctx, s.mound ?? 0);
      trace(ctx, s.trace ?? 0);
      dashed(ctx, s.dashed ?? 0);
    },
    drawFront(ctx, t, s = {}) {
      for (const tf of front) tuft(ctx, texture, tf.x, 1760, tf.size, tf.seed, ['#789251', '#5E7A3C', '#6B8A46'], 0.05 * Math.sin(t * 2 + tf.x));
      if (s.lens) magnifier(ctx, s.lens, t, s.lens.xray);
    },
  };
}
