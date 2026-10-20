// Cut-paper kit for Deep Six shot-list videos (style C, the approved cut-paper storybook).
// Every function depends only on its inputs: no Math.random, no clock. Same time in, same pixels out.
// Shapes and colors of the worker ant come from the approved style C artwork (fire-ant-paper-motion.mjs).
import { createCanvas, Path2D, DOMMatrix } from '@napi-rs/canvas';
import {
  clamp, lerp, eOut, eIn, eIO, eBack, eElastic, noise1, rng, hash, pathOf, catmull, lerpColor,
} from '../vendor/claude-animation/core.mjs';

export { createCanvas, Path2D, clamp, lerp, eOut, eIn, eIO, eBack, eElastic, noise1, rng, hash, pathOf, catmull, lerpColor };

export const W = 1080;
export const H = 1920;

export const C = {
  cream: '#F0DDB2', paper: '#F6EFE2', ink: '#1E1B22', purple: '#3A3148', lime: '#A9D554', limeDark: '#8DA955',
  grass: '#789251', grassMid: '#93BD5C', grassDeep: '#5E7A3C', straw: '#CDB168', strawDark: '#A8894A', strawLight: '#E2CD8C',
  soil: '#B57553', soilLight: '#D5A273', soilPale: '#E4C79A', soilDark: '#9B674C', soilDeep: '#744C43',
  tunnel: '#4A3236', tunnelInner: '#5C4040', crust: '#D9B47E', crack: '#4B3532',
  sky: '#D9EBE1', hotSkyTop: '#F1BE5A', hotSkyLow: '#F8E2A0',
  sun: '#F7C548', sunHi: '#FCDC7E', sunRay: '#F2A93B', sunRay2: '#F6C04E', water: '#7FB8D6', white: '#FFF9EC',
};

// Colour mix that accepts '#rrggbb' or 'rgb(...)' and can be nested.
function parseColor(c) {
  if (c[0] === '#') return [1, 3, 5].map(i => parseInt(c.slice(i, i + 2), 16));
  return c.slice(c.indexOf('(') + 1, c.indexOf(')')).split(',').slice(0, 3).map(Number);
}
export function mix(a, b, k) {
  const A = parseColor(a);
  const B = parseColor(b);
  const f = clamp(k);
  return `rgb(${A.map((v, i) => Math.round(v + (B[i] - v) * f)).join(',')})`;
}

// ------------------------------------------------------------------ time
export const prog = (t, a, b) => clamp((t - a) / (b - a));
export const zoomTo = (z0, z1, k) => Math.exp(lerp(Math.log(z0), Math.log(z1), k));
// Damped wobble that starts at t0: 0 before, decays to 0 after.
export function wobble(t, t0, freq = 3, decay = 6) {
  if (t < t0) return 0;
  const u = t - t0;
  return Math.exp(-decay * u) * Math.sin(2 * Math.PI * freq * u);
}
export function shake(t, t0, duration, amplitude, seed = 0) {
  if (t < t0 || t > t0 + duration) return [0, 0];
  const fade = (1 - (t - t0) / duration) ** 2 * amplitude;
  return [fade * noise1(t * 57 + seed), fade * noise1(t * 57 + seed + 31.7)];
}

// ------------------------------------------------------------------ paper texture (approved fibres)
export function makeFibres(seed) {
  const canvas = createCanvas(384, 384);
  const ctx = canvas.getContext('2d');
  const random = randomSource(seed);
  for (let i = 0; i < 2300; i += 1) {
    const x = random() * 384;
    const y = random() * 384;
    const length = 1.5 + random() * 8;
    ctx.strokeStyle = i % 3 ? 'rgba(255,250,228,0.19)' : 'rgba(65,40,28,0.12)';
    ctx.lineWidth = 0.35 + random() * 0.8;
    ctx.beginPath();
    ctx.moveTo(x, y);
    ctx.quadraticCurveTo(x + length / 2, y - 0.8, x + length, y + random() * 2);
    ctx.stroke();
  }
  for (let i = 0; i < 1000; i += 1) {
    ctx.fillStyle = i % 2 ? 'rgba(255,255,246,0.12)' : 'rgba(52,35,29,0.08)';
    ctx.fillRect(random() * 384, random() * 384, 0.6 + random(), 0.6 + random());
  }
  return canvas;
}

function randomSource(seed) {
  let state = seed >>> 0;
  return () => {
    state += 0x6D2B79F5;
    let value = Math.imul(state ^ (state >>> 15), state | 1);
    value ^= value + Math.imul(value ^ (value >>> 7), value | 61);
    return ((value ^ (value >>> 14)) >>> 0) / 4294967296;
  };
}

const patternCache = new WeakMap();
function grainPattern(ctx, texture) {
  let byTexture = patternCache.get(ctx);
  if (!byTexture) { byTexture = new Map(); patternCache.set(ctx, byTexture); }
  let pattern = byTexture.get(texture);
  if (!pattern) { pattern = ctx.createPattern(texture, 'repeat'); byTexture.set(texture, pattern); }
  return pattern;
}

const scaleOf = ctx => { const m = ctx.getTransform(); return Math.hypot(m.a, m.b) || 1; };

// Fibre grain stays the same size on screen but travels and turns with the paper piece.
export function textureIn(ctx, path, texture, opacity = 0.95) {
  const m = ctx.getTransform();
  const s = Math.hypot(m.a, m.b) || 1;
  const c = m.a / s;
  const n = m.b / s;
  ctx.save();
  ctx.clip(path);
  ctx.setTransform(1, 0, 0, 1, 0, 0);
  ctx.globalAlpha *= opacity;
  const pattern = grainPattern(ctx, texture);
  pattern.setTransform(new DOMMatrix([c, n, -n, c, m.e, m.f]));
  ctx.fillStyle = pattern;
  ctx.fillRect(0, 0, 4096, 4096);
  ctx.restore();
}

// One paper piece: flat color, soft cast shadow that scales with the piece, fibre grain.
export function cut(ctx, d, color, texture, depth = 6, options = {}) {
  const path = d instanceof Path2D ? d : new Path2D(d);
  const k = clamp(scaleOf(ctx), 0.2, 1.6) * (options.lift ?? 1);
  ctx.save();
  if (depth > 0) {
    ctx.shadowColor = options.shadow ?? 'rgba(57,35,27,0.24)';
    ctx.shadowBlur = depth * 0.65 * k;
    ctx.shadowOffsetX = depth * 0.35 * k;
    ctx.shadowOffsetY = depth * k;
  }
  ctx.fillStyle = color;
  ctx.fill(path);
  ctx.shadowColor = 'transparent';
  if (texture) textureIn(ctx, path, texture, options.grain ?? 0.95);
  ctx.restore();
  return path;
}

// ------------------------------------------------------------------ paths
export function polyPath(points, close = true) {
  const path = new Path2D();
  points.forEach(([x, y], i) => (i ? path.lineTo(x, y) : path.moveTo(x, y)));
  if (close) path.closePath();
  return path;
}
export function smoothPath(points, close = true) {
  const n = points.length;
  const at = i => (close ? points[(i + n) % n] : points[clamp(i, 0, n - 1)]);
  const mid = (a, b) => [(a[0] + b[0]) / 2, (a[1] + b[1]) / 2];
  const path = new Path2D();
  const start = close ? mid(at(-1), at(0)) : at(0);
  path.moveTo(start[0], start[1]);
  for (let i = 0; i < (close ? n : n - 1); i += 1) {
    const a = at(i);
    const m = mid(a, at(i + 1));
    path.quadraticCurveTo(a[0], a[1], m[0], m[1]);
  }
  if (close) path.closePath();
  else path.lineTo(at(n - 1)[0], at(n - 1)[1]);
  return path;
}
export function ovalPath(x, y, rx, ry, rotation = 0) {
  const path = new Path2D();
  path.ellipse(x, y, Math.max(0.01, rx), Math.max(0.01, ry), rotation, 0, Math.PI * 2);
  return path;
}
// Rounded limb from a to b, radius r0 at a and r1 at b.
export function capsulePath(a, b, r0, r1 = r0) {
  const angle = Math.atan2(b[1] - a[1], b[0] - a[0]);
  const path = new Path2D();
  path.moveTo(a[0] + Math.cos(angle + Math.PI / 2) * r0, a[1] + Math.sin(angle + Math.PI / 2) * r0);
  path.lineTo(b[0] + Math.cos(angle + Math.PI / 2) * r1, b[1] + Math.sin(angle + Math.PI / 2) * r1);
  path.arc(b[0], b[1], r1, angle + Math.PI / 2, angle - Math.PI / 2, true);
  path.lineTo(a[0] + Math.cos(angle - Math.PI / 2) * r0, a[1] + Math.sin(angle - Math.PI / 2) * r0);
  path.arc(a[0], a[1], r0, angle - Math.PI / 2, angle + Math.PI / 2, true);
  path.closePath();
  return path;
}
// Torn edge: points from x0 to x1 around height y.
export function tornLine(x0, x1, y, amplitude, seed, step = 26) {
  const random = rng(seed * 7919 + 13);
  const points = [];
  for (let x = x0; x < x1; x += step * (0.6 + random() * 0.8)) points.push([x, y + (random() - 0.5) * 2 * amplitude]);
  points.push([x1, y + (random() - 0.5) * 2 * amplitude]);
  return points;
}
// A paper band with a torn top edge, reaching down to `bottom`.
export function bandPath(x0, x1, top, bottom, amplitude, seed, step = 26) {
  const edge = tornLine(x0, x1, top, amplitude, seed, step);
  return polyPath([...edge, [x1, bottom], [x0, bottom]]);
}
export function tornRect(x, y, width, height, amplitude, seed) {
  const random = rng(seed * 104729 + 7);
  const points = [];
  const jitter = () => (random() - 0.5) * 2 * amplitude;
  const n = Math.max(3, Math.round(width / 34));
  const m = Math.max(2, Math.round(height / 30));
  for (let i = 0; i <= n; i += 1) points.push([x + width * i / n, y + jitter()]);
  for (let i = 1; i <= m; i += 1) points.push([x + width + jitter() * 0.6, y + height * i / m]);
  for (let i = n - 1; i >= 0; i -= 1) points.push([x + width * i / n, y + height + jitter()]);
  for (let i = m - 1; i >= 1; i -= 1) points.push([x + jitter() * 0.6, y + height * i / m]);
  return points;
}

// ------------------------------------------------------------------ camera
// cam: { x, y } world point at screen centre, zoom, optional rot and screen offset dx, dy.
export function withCamera(ctx, cam, draw) {
  ctx.save();
  ctx.translate(W / 2 + (cam.dx ?? 0), H / 2 + (cam.dy ?? 0));
  if (cam.rot) ctx.rotate(cam.rot);
  ctx.scale(cam.zoom, cam.zoom);
  ctx.translate(-cam.x, -cam.y);
  draw();
  ctx.restore();
}

// Shot helpers (same as the approved video's). bell: 0 -> 1 -> 0 over d seconds from t0.
export const bell = (t, t0, d) => Math.sin(Math.PI * prog(t, t0, t0 + d));
export const cam = (x, y, zoom) => ({ x, y, zoom });
// Camera keyframes: [[time, cam(x, y, zoom), ease?], ...]. Zoom moves in log space; default ease eIO.
export function camAt(t, keys) {
  if (t <= keys[0][0]) return { ...keys[0][1] };
  for (let i = 1; i < keys.length; i += 1) {
    const [t1, b, ease = eIO] = keys[i];
    const [t0, a] = keys[i - 1];
    if (t <= t1) {
      const k = ease(clamp((t - t0) / Math.max(1e-6, t1 - t0)));
      return { x: lerp(a.x, b.x, k), y: lerp(a.y, b.y, k), zoom: zoomTo(a.zoom, b.zoom, k), rot: lerp(a.rot ?? 0, b.rot ?? 0, k) };
    }
  }
  return { ...keys[keys.length - 1][1] };
}
// The camera never fully stops: a slow breath and sway on top of a shot's own moves.
export const live = (c, t) => ({ ...c, x: c.x + 6 * Math.sin(t * 0.9), y: c.y + 5 * Math.sin(t * 1.13 + 1), zoom: c.zoom * (1 + 0.022 * Math.sin(t * 1.7)) });
export function fillScreen(ctx, color, texture) {
  ctx.save();
  ctx.setTransform(1, 0, 0, 1, 0, 0);
  cut(ctx, polyPath([[0, 0], [W, 0], [W, H], [0, H]]), color, texture, 0, { grain: 0.8 });
  ctx.restore();
}

// ------------------------------------------------------------------ the worker ant (approved style C shapes)
const LEG_FAR = [
  [[-104, -30], [-137, 45], [-178, 140]],
  [[-49, -28], [-24, 56], [-61, 140]],
  [[8, -22], [103, 48], [150, 139]],
];
const LEG_NEAR = [
  [[-105, -3], [-156, 83], [-178, 164]],
  [[-49, 1], [-47, 84], [-75, 163]],
  [[12, -3], [104, 76], [146, 160]],
];
const TRIPOD = [1, 0, 1, 0, 1, 0];
const ANTENNAE = [
  [[-235, -76], [-278, -122], [-329, -117]],
  [[-194, -88], [-214, -150], [-272, -176]],
];
const P = {
  waist: capsulePath([25, -12], [148, 8], 6.5, 6),
  gaster: new Path2D('M130 -32 L154 -51 Q209 -76 259 -46 L284 -23 Q306 13 285 49 L267 67 Q213 93 164 61 L140 42 Q119 12 130 -32 Z'),
  gasterHi: new Path2D('M148 -32 Q194 -58 242 -35 L263 -18 Q205 -32 162 -4 L140 14 Z'),
  thorax: new Path2D('M-137 -45 L-117 -69 Q-68 -88 -16 -62 L17 -48 Q46 -27 29 4 L7 20 L-83 16 Q-126 13 -137 -13 Z'),
  thoraxHi: new Path2D('M-127 -47 L-107 -60 Q-64 -70 -23 -51 L-40 -34 L-103 -24 L-130 -26 Z'),
  node1: ovalPath(61, -10, 17, 21, -0.2),
  node2: ovalPath(100, 0, 16, 20, -0.25),
  neck: capsulePath([-128, -35], [-166, -42], 12, 12),
  head: new Path2D('M-268 -65 L-249 -88 Q-213 -111 -178 -89 L-153 -66 Q-130 -30 -155 2 L-178 22 Q-218 36 -249 7 L-272 -20 Z'),
  headHi: new Path2D('M-255 -63 L-238 -80 Q-207 -96 -182 -77 L-172 -62 Q-219 -68 -254 -41 Z'),
  eye: ovalPath(-243, -40, 6.7, 8.7, -0.15),
  mandA: new Path2D('M-265 -14 L-285 -13 L-299 1 L-290 9 L-278 0 L-262 2 Z'),
  mandB: new Path2D('M-258 0 L-277 13 L-292 15 L-291 25 L-272 22 L-252 11 Z'),
};
export const ANT_FOOT_Y = 162; // near-side feet rest on y = 162 in ant space

function legFrame(points) {
  const [hip, knee, foot] = points;
  const l1 = Math.hypot(knee[0] - hip[0], knee[1] - hip[1]) * 1.08;
  const l2 = Math.hypot(foot[0] - knee[0], foot[1] - knee[1]) * 1.08;
  const side = Math.sign((foot[0] - hip[0]) * (knee[1] - hip[1]) - (foot[1] - hip[1]) * (knee[0] - hip[0])) || 1;
  return { hip, foot, l1, l2, side };
}
const LEGS = [...LEG_FAR, ...LEG_NEAR].map(legFrame);

function solveKnee(hip, foot, l1, l2, side) {
  const dx = foot[0] - hip[0];
  const dy = foot[1] - hip[1];
  const d = clamp(Math.hypot(dx, dy), Math.abs(l1 - l2) + 0.5, l1 + l2 - 0.5);
  const ux = dx / (Math.hypot(dx, dy) || 1);
  const uy = dy / (Math.hypot(dx, dy) || 1);
  const along = (l1 * l1 - l2 * l2 + d * d) / (2 * d);
  const bend = Math.sqrt(Math.max(0, l1 * l1 - along * along));
  // Insect knees ride above the hip-to-foot line; `side` only breaks a perfectly vertical tie.
  const up = -ux || side * 1e-6;
  const across = bend * Math.sign(up);
  const knee = [hip[0] + ux * along - uy * across, hip[1] + uy * along + ux * across];
  // Keep the true foot when reachable; otherwise the limb extends straight toward it.
  const reachable = Math.hypot(dx, dy) <= l1 + l2 - 0.5;
  return { knee, foot: reachable ? foot : [hip[0] + ux * d, hip[1] + uy * d] };
}

function rotateAbout(point, pivot, angle) {
  const c = Math.cos(angle);
  const s = Math.sin(angle);
  const x = point[0] - pivot[0];
  const y = point[1] - pivot[1];
  return [pivot[0] + c * x - s * y, pivot[1] + s * x + c * y];
}

// Foot position for walking. phase advances by pi for every stance of one tripod.
function footAt(base, group, phase, walk, stride, lift) {
  if (!walk) return [base[0], base[1], 0];
  let u = (phase + group * Math.PI) % (Math.PI * 2);
  if (u < 0) u += Math.PI * 2;
  if (u < Math.PI) {
    const s = eIO(u / Math.PI);
    return [base[0] + walk * stride * (1 - 2 * s), base[1] - walk * lift * Math.sin(u), Math.sin(u)];
  }
  const s = (u - Math.PI) / Math.PI;
  return [base[0] + walk * stride * (-1 + 2 * s), base[1], 0];
}

// Phase that keeps planted feet still while the body travels `distance` world px at ant scale `scale`.
export const walkPhase = (distance, scale, stride = 24) => distance * Math.PI / (2 * stride * scale);

/**
 * Draw one worker in ant space (faces left, near feet at y = 162). The caller places it with
 * translate/rotate/scale; use scale(-1, 1) to face right.
 * pose: phase, walk (0..1), stride, lift, mand (0..1 open), antennae [[proximal, distal], ...] radians,
 * head (tilt radians), bob (body offset, ant units; negative lifts the body), shadows (floor shadows).
 */
export function drawAnt(ctx, texture, pose = {}) {
  const {
    phase = 0, walk = 0, stride = 24, lift = 16, mand = 0, antennae = [[0, 0], [0, 0]],
    head = 0, bob = 0, shadows = true, groundY = ANT_FOOT_Y, tint = 0, carry = null,
  } = pose;
  // tint 0 keeps the approved colours exactly; tint 1 is the pale colour of a newly emerged adult.
  const col = tint > 0 ? c => lerpColor(c, '#EFE2C2', tint) : c => c;
  const feet = LEGS.map((leg, i) => footAt(leg.foot, TRIPOD[i], phase, walk, stride, lift));
  const legs = LEGS.map((leg, i) => {
    const hip = [leg.hip[0], leg.hip[1] + bob];
    const solved = solveKnee(hip, [feet[i][0], feet[i][1]], leg.l1, leg.l2, leg.side);
    return [hip, solved.knee, solved.foot];
  });

  if (shadows) {
    ctx.save();
    for (let i = 0; i < 6; i += 1) {
      const air = feet[i][2];
      ctx.fillStyle = `rgba(77,49,30,${0.16 * (1 - air * 0.6)})`;
      ctx.fill(ovalPath(feet[i][0] + 2, groundY + 4 - (i < 3 ? 22 : 0), 17 * (1 - air * 0.3), 5));
    }
    ctx.fillStyle = 'rgba(60,38,26,0.13)';
    ctx.fill(ovalPath(10, groundY + 6, 250, 16));
    ctx.restore();
  }

  const limb = (points, r0, r1, color, depth) => {
    const [hip, knee, foot] = points;
    cut(ctx, capsulePath(hip, knee, r0, (r0 + r1) / 2), color, texture, depth);
    cut(ctx, capsulePath(knee, foot, (r0 + r1) / 2, r1), color, texture, depth);
    cut(ctx, ovalPath(knee[0], knee[1], r0 * 0.95, r0 * 0.88), color, texture, 2);
  };
  for (let i = 0; i < 3; i += 1) limb(legs[i], 6.5, 4.6, col('#743E32'), 3);

  ctx.save();
  ctx.translate(0, bob);
  cut(ctx, P.waist, col('#834635'), texture, 2);
  cut(ctx, P.gaster, col('#793B2D'), texture, 9);
  cut(ctx, P.gasterHi, col('#AA5639'), texture, 3);
  cut(ctx, P.thorax, col('#A94F32'), texture, 7);
  cut(ctx, P.thoraxHi, col('#CB7646'), texture, 3);
  cut(ctx, P.node1, col('#C17142'), texture, 6);
  cut(ctx, P.node2, col('#B25D38'), texture, 6);
  ctx.restore();

  for (let i = 3; i < 6; i += 1) limb(legs[i], 9, 6.2, col('#AE5735'), 5);

  ctx.save();
  ctx.translate(0, bob);
  cut(ctx, P.neck, col('#89412F'), texture, 3);
  const pivot = [-150, -45];
  ctx.translate(pivot[0], pivot[1]);
  ctx.rotate(head);
  ctx.translate(-pivot[0], -pivot[1]);
  cut(ctx, P.head, col('#BE603A'), texture, 8);
  cut(ctx, P.headHi, col('#DC915A'), texture, 3);
  ANTENNAE.forEach((base, i) => {
    const [proximal, distal] = antennae[i] ?? [0, 0];
    const elbow = rotateAbout(base[1], base[0], proximal);
    const tipOffset = rotateAbout([base[2][0] - base[1][0], base[2][1] - base[1][1]], [0, 0], proximal + distal);
    const tip = [elbow[0] + tipOffset[0], elbow[1] + tipOffset[1]];
    const color = col(i ? '#9E4C32' : '#7D3D2E');
    cut(ctx, capsulePath(base[0], elbow, 4, 3.6), color, texture, 2);
    cut(ctx, capsulePath(elbow, tip, 3.6, 3.2), color, texture, 2);
    cut(ctx, ovalPath(tip[0], tip[1], 11, 5, Math.atan2(tipOffset[1], tipOffset[0])), color, texture, 2);
  });
  cut(ctx, P.eye, tint > 0 ? lerpColor(C.ink, '#B89C78', tint * 0.7) : C.ink, texture, 1);
  if (carry === 'larva') larvaInPlace(ctx, texture);
  else if (carry === 'pupa') drawPupa(ctx, texture, -345, 52, 0.3, -0.5);
  else if (carry === 'egg') drawEgg(ctx, texture, -296, 22, 15, 0.3);
  ctx.save();
  ctx.translate(-262, -8);
  ctx.rotate(mand * 0.42);
  ctx.translate(262, 8);
  cut(ctx, P.mandA, col('#85432F'), texture, 3);
  ctx.restore();
  ctx.save();
  ctx.translate(-254, 8);
  ctx.rotate(-mand * 0.5);
  ctx.translate(254, -8);
  cut(ctx, P.mandB, col('#9C4B30'), texture, 3);
  ctx.restore();
  ctx.restore();
}

// ------------------------------------------------------------------ brood (eggs, larvae, pupae)
// The larva is the approved style C larva, in the coordinates where a worker holds it.
const LARVA = {
  body: new Path2D('M-296 -16 L-311 -17 Q-350 -5 -355 34 L-355 52 Q-352 91 -318 109 L-297 115 Q-268 114 -255 92 L-255 75 Q-262 63 -275 69 Q-282 91 -301 84 L-315 73 Q-332 51 -320 29 L-310 21 Q-289 20 -284 4 Z'),
  shade: new Path2D('M-345 17 Q-355 66 -321 93 Q-290 118 -263 88 L-256 109 L-310 126 L-362 77 L-361 25 Z'),
  lines: new Path2D('M-322 -8 Q-319 5 -310 21 M-340 7 Q-331 16 -320 26 M-352 28 L-326 37 M-353 50 L-326 52 M-344 73 L-320 65 M-327 93 L-312 80 M-303 106 L-299 85 M-280 101 L-286 84'),
};
function larvaInPlace(ctx, texture) {
  const body = cut(ctx, LARVA.body, C.cream, texture, 8);
  ctx.save();
  ctx.clip(body);
  cut(ctx, LARVA.shade, '#D4BA8D', texture, 2);
  ctx.strokeStyle = '#B59A73';
  ctx.lineWidth = 2.3;
  ctx.lineCap = 'round';
  ctx.stroke(LARVA.lines);
  ctx.restore();
}
// A larva centred on (x, y); about 100 x 130 px at scale 1. wiggle in -1..1 bends it.
export function drawLarva(ctx, texture, x, y, scale = 1, angle = 0, wiggle = 0) {
  ctx.save();
  ctx.translate(x, y);
  ctx.rotate(angle + wiggle * 0.1);
  ctx.scale(scale * (1 + wiggle * 0.04), scale * (1 - wiggle * 0.04));
  ctx.translate(305, -49);
  larvaInPlace(ctx, texture);
  ctx.restore();
}
export function drawEgg(ctx, texture, x, y, r, angle = 0) {
  cut(ctx, ovalPath(x, y, r * 0.74, r, angle), '#F6EEDB', texture, Math.max(1, r * 0.25));
  ctx.save();
  ctx.fillStyle = 'rgba(255,255,255,0.75)';
  ctx.fill(ovalPath(x - r * 0.22, y - r * 0.35, r * 0.2, r * 0.3, angle));
  ctx.restore();
}
// Exposed pupa: the adult's body shape, pale, with legs and antennae folded against it.
// Ant space (faces left). mature 0..1 darkens the eyes as it develops.
const PUPA_LEGS = [
  [[-104, -30], [-80, 24], [-128, 52]], [[-49, -28], [-20, 30], [-62, 60]], [[8, -22], [40, 26], [-6, 62]],
  [[-105, -3], [-84, 44], [-140, 66]], [[-49, 1], [-24, 52], [-78, 74]], [[12, -3], [44, 44], [-4, 80]],
];
export function drawPupa(ctx, texture, x, y, scale = 1, angle = 0, mature = 0) {
  const pale = '#F1E5C8';
  const mid = '#E3D0A8';
  ctx.save();
  ctx.translate(x, y);
  ctx.rotate(angle);
  ctx.scale(scale, scale);
  ctx.translate(0, 10);
  const leg = (pts, r, color) => {
    cut(ctx, capsulePath(pts[0], pts[1], r, r * 0.85), color, texture, 2);
    cut(ctx, capsulePath(pts[1], pts[2], r * 0.85, r * 0.7), color, texture, 2);
  };
  for (let i = 0; i < 3; i += 1) leg(PUPA_LEGS[i], 7, mid);
  cut(ctx, P.waist, mid, texture, 2);
  cut(ctx, P.gaster, pale, texture, 8);
  cut(ctx, P.gasterHi, '#FBF4E2', texture, 2);
  cut(ctx, P.thorax, pale, texture, 6);
  cut(ctx, P.node1, mid, texture, 4);
  cut(ctx, P.node2, mid, texture, 4);
  for (let i = 3; i < 6; i += 1) leg(PUPA_LEGS[i], 9, '#EADBB8');
  cut(ctx, P.neck, mid, texture, 2);
  cut(ctx, P.head, pale, texture, 7);
  cut(ctx, P.headHi, '#FBF4E2', texture, 2);
  cut(ctx, capsulePath([-235, -76], [-266, -16], 4.5, 4), mid, texture, 2);
  cut(ctx, capsulePath([-266, -16], [-248, 46], 4, 3.6), mid, texture, 2);
  cut(ctx, ovalPath(-243, -40, 7, 9, -0.15), lerpColor('#D9C4A0', '#3A2A26', mature), texture, 1);
  ctx.restore();
}
// A brood pile: an egg clump, larvae and pupae resting on a chamber floor centred at (x, y).
// amount 0..1 reveals the pile item by item. size scales the whole pile.
export function createBroodPile(seed, counts = { eggs: 9, larvae: 3, pupae: 2 }) {
  const random = rng(seed * 977 + 3);
  const items = [];
  // Resting on the floor (y = 0 is the floor): pupae at the back left, larvae in the middle, an egg clump on the right.
  for (let i = 0; i < counts.pupae; i += 1) items.push({ kind: 'pupa', x: -150 + i * 62, y: -22, a: (random() - 0.5) * 0.15, flip: i % 2 === 1 });
  for (let i = 0; i < counts.larvae; i += 1) items.push({ kind: 'larva', x: -10 + i * 48, y: -27, a: (i % 2 ? 0.35 : -0.25) + (random() - 0.5) * 0.2, ph: random() * 6 });
  const rows = [[4, -8], [3, -21], [2, -34], [1, -46]];
  let placed = 0;
  for (const [n, y] of rows) {
    for (let k = 0; k < n && placed < counts.eggs; k += 1, placed += 1) {
      items.push({ kind: 'egg', x: 165 + (k - (n - 1) / 2) * 16 + (random() - 0.5) * 3, y, a: 1.3 + (random() - 0.5) * 0.6 });
    }
  }
  return items;
}
export function drawBroodPile(ctx, texture, items, x, y, size, amount, t = 0) {
  if (amount <= 0.001) return;
  const n = items.length;
  ctx.save();
  ctx.translate(x, y);
  ctx.scale(size, size);
  items.forEach((item, i) => {
    const k = clamp(amount * n - i);
    if (k <= 0) return;
    const pop = eBack(k, 2);
    if (item.kind === 'pupa') {
      ctx.save();
      ctx.translate(item.x, item.y);
      if (item.flip) ctx.scale(-1, 1);
      drawPupa(ctx, texture, 0, 0, 0.2 * pop, item.a);
      ctx.restore();
    } else if (item.kind === 'larva') {
      drawLarva(ctx, texture, item.x, item.y, 0.42 * pop, item.a, Math.sin(t * 3 + item.ph));
    } else {
      drawEgg(ctx, texture, item.x, item.y, 8 * pop, item.a);
    }
  });
  ctx.restore();
}

// Place an ant with its near feet on the ground point (x, groundY).
export function placeAnt(ctx, texture, x, groundY, scale, pose = {}, options = {}) {
  ctx.save();
  ctx.translate(x, groundY);
  if (options.rotation) ctx.rotate(options.rotation);
  ctx.scale(options.faceRight ? -scale : scale, scale);
  ctx.translate(0, -ANT_FOOT_Y);
  drawAnt(ctx, texture, pose);
  ctx.restore();
}

// ------------------------------------------------------------------ plants and effects
// One paper grass blade rooted at (x, y): lean tilts it, bend curls the tip (positive = toward +x).
export function blade(ctx, texture, x, y, height, width, lean, bend, color, depth = 3) {
  const left = [];
  const right = [];
  let px = x;
  let py = y;
  const steps = 7;
  for (let i = 0; i <= steps; i += 1) {
    const s = i / steps;
    const angle = -Math.PI / 2 + lean + bend * s * s;
    const half = width * 0.5 * (1 - s * 0.94);
    const nx = -Math.sin(angle);
    const ny = Math.cos(angle);
    left.push([px - nx * half, py - ny * half]);
    right.push([px + nx * half, py + ny * half]);
    px += Math.cos(angle) * height / steps;
    py += Math.sin(angle) * height / steps;
  }
  return cut(ctx, polyPath([...left, ...right.reverse()]), color, texture, depth);
}

export function tuft(ctx, texture, x, y, size, seed, colors, sway = 0, droop = 0) {
  const random = rng(seed * 31 + 5);
  const count = 4 + Math.floor(random() * 3);
  for (let i = 0; i < count; i += 1) {
    const offset = (i - (count - 1) / 2) * size * 0.16;
    const lean = (i - (count - 1) / 2) * 0.16 + (random() - 0.5) * 0.2 + sway;
    const height = size * (0.55 + random() * 0.55);
    blade(ctx, texture, x + offset, y + 2, height, size * 0.17, lean, droop * Math.sign(lean || 1) + sway * 0.6,
      colors[i % colors.length], 3);
  }
}

export function puff(ctx, texture, x, y, radius, color, alpha = 1) {
  if (radius <= 0.5 || alpha <= 0.01) return;
  ctx.save();
  ctx.globalAlpha *= alpha;
  cut(ctx, ovalPath(x, y, radius, radius * 0.86), color, texture, 2);
  ctx.restore();
}

// Paper impact star with ink burst lines. k: 0..1 pop, fade: 1..0.
export function impactStar(ctx, texture, x, y, radius, k, fade = 1, rotation = 0) {
  if (k <= 0 || fade <= 0) return;
  const star = (outer, inner, points) => {
    const pts = [];
    for (let i = 0; i < points * 2; i += 1) {
      const angle = rotation + i * Math.PI / points - Math.PI / 2;
      const r = i % 2 ? inner : outer;
      pts.push([x + Math.cos(angle) * r, y + Math.sin(angle) * r]);
    }
    return polyPath(pts);
  };
  ctx.save();
  ctx.globalAlpha *= fade;
  const r = radius * k;
  cut(ctx, star(r, r * 0.48, 9), C.white, texture, 6);
  cut(ctx, star(r * 0.56, r * 0.27, 9), C.lime, texture, 3);
  ctx.strokeStyle = C.ink;
  ctx.lineCap = 'round';
  ctx.lineWidth = Math.max(2, radius * 0.05);
  for (let i = 0; i < 9; i += 1) {
    const angle = rotation + 0.17 + i * Math.PI * 2 / 9;
    ctx.beginPath();
    ctx.moveTo(x + Math.cos(angle) * r * 1.15, y + Math.sin(angle) * r * 1.15);
    ctx.lineTo(x + Math.cos(angle) * r * 1.55, y + Math.sin(angle) * r * 1.55);
    ctx.stroke();
  }
  ctx.restore();
}

// ------------------------------------------------------------------ captions
// Word-synced captions on torn paper strips. The spoken word gets a lime tape highlight.
export function createCaptions(words, groups, options = {}) {
  const {
    family = 'D6Caption', centerY = 1390, maxWidth = 900, maxSize = 92, minSize = 62,
    lead = 0.03, texture = null, endTime = Infinity,
  } = options;
  const measure = createCanvas(16, 16).getContext('2d');
  const layouts = groups.map((group, gi) => {
    const items = group.words.map(i => ({ ...words[i], label: words[i].text.toUpperCase() }));
    let size = maxSize;
    let widths;
    let space;
    let total;
    do {
      measure.font = `${size}px ${family}`;
      widths = items.map(item => measure.measureText(item.label).width);
      space = size * 0.26;
      total = widths.reduce((a, b) => a + b, 0) + space * (items.length - 1);
      if (total <= maxWidth) break;
      size -= 2;
    } while (size > minSize);
    let x = -total / 2;
    items.forEach((item, i) => { item.x = x; item.width = widths[i]; x += widths[i] + space; });
    const padX = size * 0.42;
    const padY = size * 0.3;
    const strip = tornRect(-total / 2 - padX, -size * 0.62 - padY, total + padX * 2, size * 1.24 + padY * 2, 5, gi + 3);
    return {
      items, size, start: items[0].start, total,
      strip: polyPath(strip),
      tilt: (gi % 2 ? 1 : -1) * 0.022,
      fade: group.fade_out_seconds ?? null,
    };
  });
  layouts.forEach((layout, i) => { layout.until = i + 1 < layouts.length ? layouts[i + 1].start : endTime; });

  return function drawCaptions(ctx, t) {
    const layout = layouts.findLast(l => t >= l.start - lead);
    if (!layout || t >= layout.until - lead) return;
    let alpha = 1;
    if (layout.fade) alpha = 1 - prog(t, layout.fade[0], layout.fade[1]);
    if (alpha <= 0) return;
    const enter = prog(t, layout.start - lead, layout.start - lead + 0.13);
    const scale = lerp(0.82, 1, eBack(enter, 2.4));
    ctx.save();
    ctx.globalAlpha = alpha * clamp(enter * 4);
    ctx.translate(W / 2, centerY);
    ctx.rotate(layout.tilt);
    ctx.scale(scale, scale);
    cut(ctx, layout.strip, C.paper, texture, 10, { shadow: 'rgba(30,20,25,0.32)' });
    const active = layout.items.findLast(item => t >= item.start - lead);
    if (active) {
      const slap = eOut(prog(t, active.start - lead, active.start - lead + 0.08));
      const padX = layout.size * 0.12;
      const tape = tornRect(active.x - padX, -layout.size * 0.5, active.width + padX * 2, layout.size * 1.0, 3,
        Math.round(active.start * 100));
      ctx.save();
      ctx.translate(active.x + active.width / 2, 0);
      ctx.scale(lerp(0.35, 1, slap), 1);
      ctx.translate(-(active.x + active.width / 2), 0);
      cut(ctx, polyPath(tape), C.lime, texture, 3);
      ctx.restore();
    }
    ctx.font = `${layout.size}px ${family}`;
    ctx.textBaseline = 'middle';
    ctx.textAlign = 'left';
    for (const item of layout.items) {
      const spoken = t >= item.start - lead;
      ctx.fillStyle = spoken ? C.ink : 'rgba(30,27,34,0.38)';
      ctx.fillText(item.label, item.x, layout.size * 0.04);
    }
    ctx.restore();
  };
}
