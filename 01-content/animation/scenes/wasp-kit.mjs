// Ensign wasp, American cockroach and egg-case pieces in cut-paper style C.
// New drawings for episode D6-01096ba333e3; the fire-ant kit is used read-only.
// Anatomy follows science-notes.md (UF/IFAS IN319, TAMU City Bugs, UF/IFAS EENY-141, UMN Extension).
// Every function depends only on its inputs: same time in, same pixels out.
import {
  C, Path2D, clamp, lerp, eOut, eIO, eBack, hash, lerpColor,
  cut, polyPath, smoothPath, ovalPath, capsulePath,
} from './paper-kit.mjs';

const TAU = Math.PI * 2;
const PALE = '#EFE4C8';

// ------------------------------------------------------------------ shared helpers
// Two-bone leg: knee chosen on the side that points along `pref`.
function knee2(hip, foot, l1, l2, pref = [0, -1]) {
  const dx = foot[0] - hip[0];
  const dy = foot[1] - hip[1];
  const dist = Math.hypot(dx, dy) || 1;
  const d = clamp(dist, Math.abs(l1 - l2) + 0.5, l1 + l2 - 0.5);
  const ux = dx / dist;
  const uy = dy / dist;
  const a = (l1 * l1 - l2 * l2 + d * d) / (2 * d);
  const h = Math.sqrt(Math.max(0, l1 * l1 - a * a));
  const p1 = [hip[0] + ux * a - uy * h, hip[1] + uy * a + ux * h];
  const p2 = [hip[0] + ux * a + uy * h, hip[1] + uy * a - ux * h];
  const score = p => (p[0] - hip[0]) * pref[0] + (p[1] - hip[1]) * pref[1];
  const knee = score(p1) >= score(p2) ? p1 : p2;
  const end = dist <= l1 + l2 - 0.5 ? foot : [hip[0] + ux * d, hip[1] + uy * d];
  return { knee, foot: end };
}

// Tripod gait. phase advances by pi for each stance; returns [x, y, air].
function gaitFoot(base, group, phase, walk, stride, lift) {
  if (!walk) return [base[0], base[1], 0];
  let u = (phase + group * Math.PI) % TAU;
  if (u < 0) u += TAU;
  if (u < Math.PI) {
    const s = eIO(u / Math.PI);
    return [base[0] + walk * stride * (1 - 2 * s), base[1] - walk * lift * Math.sin(u), Math.sin(u)];
  }
  const s = (u - Math.PI) / Math.PI;
  return [base[0] + walk * stride * (-1 + 2 * s), base[1], 0];
}
export const gaitPhase = (distance, scale, stride) => distance * Math.PI / (2 * stride * scale);

const rot = (p, a) => [p[0] * Math.cos(a) - p[1] * Math.sin(a), p[0] * Math.sin(a) + p[1] * Math.cos(a)];
const add = (a, b) => [a[0] + b[0], a[1] + b[1]];
const lerp2 = (a, b, k) => [lerp(a[0], b[0], k), lerp(a[1], b[1], k)];

// A chain of capsules from `base`, each segment [length, angle offset]; returns the joint points.
function chain(base, angle, segments) {
  const pts = [base];
  let a = angle;
  let p = base;
  for (const [len, da] of segments) {
    a += da;
    p = [p[0] + Math.cos(a) * len, p[1] + Math.sin(a) * len];
    pts.push(p);
  }
  return pts;
}
function drawChain(ctx, texture, pts, r0, r1, color, depth = 2) {
  for (let i = 1; i < pts.length; i += 1) {
    const ra = lerp(r0, r1, (i - 1) / (pts.length - 1));
    const rb = lerp(r0, r1, i / (pts.length - 1));
    cut(ctx, capsulePath(pts[i - 1], pts[i], ra, rb), color, texture, depth);
  }
}

// ------------------------------------------------------------------ ensign wasp (Evania appendigaster)
// Side view, faces left, near feet on y = 160 in wasp space. About 560 px head to gaster at scale 1.
// All black. Gaster small, flattened and flag-like on a thin petiole set high on the propodeum.
// Long hind legs; mid and hind legs widely separated. Long slender antennae. Clear wings with dark veins.
export const WASP_FOOT_Y = 160;
const WP = {
  thorax: smoothPath([[-160, -60], [-142, -124], [-80, -172], [0, -178], [68, -152], [112, -110], [116, -60], [90, -22], [10, -4], [-90, -6], [-150, -26]]),
  thoraxHi: smoothPath([[-130, -120], [-78, -160], [-4, -168], [50, -150], [-6, -144], [-84, -130]]),
  scutum: smoothPath([[-60, -160], [10, -168], [62, -144], [32, -130], [-30, -136]]),
  neck: capsulePath([-172, -70], [-140, -66], 22, 24),
  head: ovalPath(-206, -78, 58, 64, -0.12),
  headHi: smoothPath([[-246, -118], [-212, -138], [-176, -124], [-202, -118], [-232, -106]]),
  eye: ovalPath(-214, -86, 34, 43, -0.18),
  eyeHi: ovalPath(-224, -102, 9, 13, -0.3),
  mandible: polyPath([[-242, -34], [-268, -24], [-258, -12], [-234, -18]]),
  coxaHind: ovalPath(84, -40, 24, 32, 0.3),
  coxaMid: ovalPath(-48, -18, 15, 18, 0),
};
// Gaster in petiole-tip space: x along the petiole, y to the insect's rear. Subtriangular blade.
const GASTER = smoothPath([[-12, -8], [12, -16], [62, -2], [88, 16], [92, 40], [76, 92], [56, 142], [38, 156], [20, 144], [-6, 76], [-16, 24]]);
const GASTER_HI = smoothPath([[0, -6], [24, -8], [66, 8], [76, 30], [44, 30], [10, 18]]);
const FOREWING = smoothPath([[0, -8], [110, -30], [250, -30], [348, -10], [374, 14], [334, 36], [196, 36], [60, 22], [0, 10]]);
const HINDWING = smoothPath([[0, -4], [100, -16], [230, -10], [262, 8], [220, 26], [90, 22], [0, 8]]);
// Legs: hip, foot rest position, femur and tibia lengths, knee preference, tarsus direction.
const WASP_LEGS = [
  { hip: [-126, -28], foot: [-206, 160], l1: 74, l2: 132, pref: [-0.4, -1], tar: -1, r: [7, 4.6], group: 0 },
  { hip: [-48, -12], foot: [-34, 160], l1: 88, l2: 118, pref: [0.5, -1], tar: 1, r: [7, 4.6], group: 1 },
  { hip: [88, -36], foot: [330, 160], l1: 165, l2: 250, pref: [0.1, -1], tar: 1, r: [10, 5], group: 0 },
];
const FOLDED = [
  [[-176, 20], [-112, 52]],
  [[-12, 54], [-90, 70]],
  [[170, 6], [24, 78]],
];

/**
 * pose: phase, walk (0..1), stride, lift, flag (petiole angle, radians; about -1.1 is held high),
 * antennae [[a0, a1, a2], [a0, a1, a2]] offsets, wing (0..1 lifts the wings), tint (0..1 pale),
 * fold (0..1 tucks legs, wings and antennae as in the pupa), bob (body offset), shadows.
 */
export function drawWasp(ctx, texture, pose = {}) {
  const {
    phase = 0, walk = 0, stride = 26, lift = 18, flag = -1.1, antennae = [[0, 0, 0], [0, 0, 0]], wing = 0,
    tint = 0, fold = 0, bob = 0, shadows = true, sheen = 0, head = 0,
  } = pose;
  const col = tint > 0 ? c => lerpColor(c, PALE, tint) : c => c;
  const body = col('#2B2731');
  const bodyHi = col('#4E4862');
  const bodyHi2 = col('#5E6B86');
  const legNear = col('#25212B');
  const legFar = col('#141218');

  const legs = [];
  for (let side = 0; side < 2; side += 1) {
    WASP_LEGS.forEach((leg, i) => {
      const far = side === 0;
      const hip = add(leg.hip, far ? [14, -10] : [0, 0]);
      const restFoot = add(leg.foot, far ? [36, -20] : [0, 0]);
      const group = far ? 1 - leg.group : leg.group;
      const f = gaitFoot(restFoot, group, phase, walk, stride, lift);
      const solved = knee2([hip[0], hip[1] + bob], [f[0], f[1]], leg.l1, leg.l2, leg.pref);
      let knee = solved.knee;
      let foot = solved.foot;
      if (fold > 0) {
        knee = lerp2(knee, add(FOLDED[i][0], far ? [12, -8] : [0, 0]), eIO(fold));
        foot = lerp2(foot, add(FOLDED[i][1], far ? [12, -8] : [0, 0]), eIO(fold));
      }
      legs.push({ far, i, hip: [hip[0], hip[1] + bob], knee, foot, air: f[2], leg });
    });
  }

  if (shadows && fold < 0.5) {
    ctx.save();
    ctx.fillStyle = 'rgba(50,32,24,0.16)';
    ctx.fill(ovalPath(20, WASP_FOOT_Y + 6, 300, 14));
    for (const l of legs) {
      ctx.fillStyle = `rgba(50,32,24,${0.2 * (1 - l.air * 0.6)})`;
      ctx.fill(ovalPath(l.foot[0] + 4, (l.far ? WASP_FOOT_Y - 20 : WASP_FOOT_Y) + 4, 14, 4));
    }
    ctx.restore();
  }

  const drawLeg = (l, color, depth) => {
    const [r0, r1] = l.leg.r;
    const s = l.far ? 0.82 : 1;
    cut(ctx, capsulePath(l.hip, l.knee, r0 * s, (r0 + r1) * 0.5 * s), color, texture, depth);
    cut(ctx, capsulePath(l.knee, l.foot, (r0 + r1) * 0.5 * s * 0.8, r1 * s * 0.8), color, texture, depth);
    // Tarsus: a short jointed foot that lies along the ground.
    const tarsus = [l.foot[0] + l.leg.tar * 34 * (1 - fold), l.foot[1] - 2 + fold * 6];
    cut(ctx, capsulePath(l.foot, tarsus, r1 * s * 0.7, r1 * s * 0.55), color, texture, Math.max(1, depth - 1));
  };

  // Far legs and far wing sit behind the body.
  for (const l of legs.filter(l => l.far)) drawLeg(l, legFar, 2);
  const wingLift = wing * -0.55;
  const wingLen = lerp(1, 0.42, eIO(fold));
  const drawWing = (shape, anchor, angle, len, alpha, veins) => {
    ctx.save();
    ctx.translate(anchor[0], anchor[1] + bob);
    ctx.rotate(angle);
    ctx.scale(len, lerp(1, 0.8, fold));
    ctx.globalAlpha *= alpha;
    cut(ctx, shape, tint > 0.5 ? col('#E7ECE6') : 'rgba(226,236,236,0.62)', texture, 2, { shadow: 'rgba(40,30,40,0.12)', grain: 0.5 });
    ctx.globalAlpha /= alpha;
    if (veins && fold < 0.9) {
      ctx.lineCap = 'round';
      ctx.strokeStyle = col('#3A3442');
      ctx.lineWidth = 4.5;
      ctx.beginPath();
      ctx.moveTo(4, -6);
      ctx.quadraticCurveTo(120, -30, 214, -28);
      ctx.stroke();
      ctx.lineWidth = 2.2;
      ctx.beginPath();
      ctx.moveTo(10, 4);
      ctx.quadraticCurveTo(120, 4, 214, -22);
      ctx.moveTo(120, -22);
      ctx.lineTo(150, 22);
      ctx.moveTo(214, -24);
      ctx.quadraticCurveTo(250, 6, 236, 30);
      ctx.stroke();
      cut(ctx, ovalPath(206, -26, 18, 7, -0.05), col('#2E2935'), null, 0);
    }
    ctx.restore();
  };
  drawWing(HINDWING, [-10, -158], 0.16 + wingLift * 0.7, wingLen, 0.75, false);

  ctx.save();
  ctx.translate(0, bob);
  // Petiole and gaster: the "flag" on a thin stalk set high on the propodeum.
  const flagAngle = lerp(flag, 0.55, eIO(fold));
  const p0 = [98, -116];
  const petLen = 150;
  const tip = [p0[0] + Math.cos(flagAngle) * petLen, p0[1] + Math.sin(flagAngle) * petLen];
  cut(ctx, capsulePath(p0, tip, 7.5, 6), body, texture, 3);
  ctx.save();
  ctx.translate(tip[0], tip[1]);
  ctx.rotate(flagAngle);
  cut(ctx, GASTER, body, texture, 8);
  cut(ctx, GASTER_HI, bodyHi, texture, 2);
  ctx.restore();
  cut(ctx, WP.thorax, body, texture, 8);
  cut(ctx, WP.thoraxHi, bodyHi, texture, 3);
  cut(ctx, WP.scutum, bodyHi2, texture, 2, { grain: 0.6 });
  if (sheen > 0) {
    ctx.save();
    ctx.globalAlpha = sheen;
    ctx.clip(WP.thorax);
    ctx.fillStyle = 'rgba(190,210,255,0.55)';
    ctx.fillRect(-160 + sheen * 200, -170, 40, 200);
    ctx.restore();
  }
  ctx.restore();

  for (const l of legs.filter(l => !l.far)) {
    if (l.i === 1) cut(ctx, WP.coxaMid, legNear, texture, 2);
    if (l.i === 2) {
      ctx.save();
      ctx.translate(0, bob);
      cut(ctx, WP.coxaHind, legNear, texture, 3);
      ctx.restore();
    }
    drawLeg(l, legNear, 3);
  }

  ctx.save();
  ctx.translate(0, bob);
  cut(ctx, WP.neck, body, texture, 2);
  const pivot = [-150, -64];
  ctx.translate(pivot[0], pivot[1]);
  ctx.rotate(head);
  ctx.translate(-pivot[0], -pivot[1]);
  // Antennae: slender, many-segmented, set on the front of the head.
  const antBase = [[-246, -126], [-234, -132]];
  const rest = [[-2.72, 0.24, 0.26], [-2.5, 0.22, 0.24]];
  const folded = [[1.6, 0.55, 0.45], [1.75, 0.5, 0.42]];
  [1, 0].forEach(i => {
    const a = antennae[i] ?? [0, 0, 0];
    const r = rest[i].map((v, j) => lerp(v, folded[i][j], eIO(fold)) + a[j]);
    const pts = chain(antBase[i], r[0], [[46, 0], [140, r[1]], [140, r[2]]]);
    drawChain(ctx, texture, pts, 5, 3.4, i ? legFar : legNear, 2);
  });
  cut(ctx, WP.head, body, texture, 7);
  cut(ctx, WP.headHi, bodyHi, texture, 2);
  cut(ctx, WP.eye, col('#1B2230'), texture, 2);
  cut(ctx, WP.eyeHi, col('#6F8FB8'), null, 0);
  cut(ctx, WP.mandible, col('#1C1A20'), texture, 2);
  ctx.restore();

  // Near forewing over the body, translucent like tracing paper.
  drawWing(FOREWING, [-24, -162], 0.07 + wingLift, wingLen, 1, true);
}

export function placeWasp(ctx, texture, x, groundY, scale, pose = {}, options = {}) {
  ctx.save();
  ctx.translate(x, groundY);
  if (options.rotation) ctx.rotate(options.rotation);
  ctx.scale(options.faceRight ? -scale : scale, scale);
  ctx.translate(0, -WASP_FOOT_Y);
  drawWasp(ctx, texture, pose);
  ctx.restore();
}

// ------------------------------------------------------------------ wasp egg and larva
export function drawWaspEgg(ctx, texture, x, y, len, angle = 0, k = 1) {
  if (k <= 0.01) return;
  const s = eBack(clamp(k), 2);
  ctx.save();
  ctx.translate(x, y);
  ctx.rotate(angle);
  ctx.scale(s, s);
  const egg = cut(ctx, smoothPath([[-len / 2, 0], [-len * 0.38, -len * 0.16], [len * 0.3, -len * 0.15], [len / 2, 0], [len * 0.32, len * 0.15], [-len * 0.36, len * 0.14]]), '#FFFBF2', texture, 3);
  ctx.lineWidth = Math.max(1.5, len * 0.025);
  ctx.strokeStyle = 'rgba(150,120,90,0.55)';
  ctx.stroke(egg);
  ctx.fillStyle = 'rgba(255,255,255,0.9)';
  ctx.fill(ovalPath(-len * 0.12, -len * 0.06, len * 0.16, len * 0.04));
  ctx.restore();
}

// Toothed, sharply pointed mandible, pointing along -x from its base (first-instar larva, IN319).
function mandiblePath(size, teeth = 1) {
  const outer = [];
  const inner = [];
  const n = 14;
  for (let i = 0; i <= n; i += 1) {
    const s = i / n;
    const a = s * 1.0;
    const x = -size * s;
    const y = size * 0.42 * Math.sin(a * 1.3) * s;
    const w = size * 0.2 * (1 - s) + 0.6;
    outer.push([x, y - w]);
    const tooth = teeth > 0 && i > 2 && i < n - 1 && i % 2 === 0 ? size * 0.07 * teeth : 0;
    inner.push([x + tooth * 0.3, y + w + tooth]);
  }
  return polyPath([...outer, ...inner.reverse()]);
}

/**
 * Legless, pale, segmented wasp larva in side view, head on the left.
 * len: body length. curl bends it into a C. wig 0..1 wriggle amount, ph wriggle phase.
 * jaw 0..1 opens the mandibles. feed 0..1 tints the gut amber.
 */
export function drawGrub(ctx, texture, x, y, len, angle = 0, opts = {}) {
  const { curl = 0.25, wig = 0.5, ph = 0, jaw = 0, feed = 0, k = 1, look = 0 } = opts;
  if (k <= 0.01) return;
  const n = 11;
  const spine = [];
  for (let i = 0; i <= n; i += 1) {
    const s = i / n;
    const bend = curl * (s - 0.5) * (s - 0.5) * 2.2;
    const wave = wig * Math.sin(ph - s * 5) * 0.035;
    spine.push([(-0.5 + s) * len, (bend * 0.9 - curl * 0.25 + wave) * len]);
  }
  const radius = s => len * (0.035 + 0.115 * Math.pow(Math.sin(Math.PI * (0.12 + 0.82 * s)), 0.7));
  ctx.save();
  ctx.translate(x, y);
  ctx.rotate(angle);
  const sc = eBack(clamp(k), 2);
  ctx.scale(sc, sc);
  // Body segments from tail to head.
  for (let i = n; i >= 1; i -= 1) {
    const s = i / n;
    const [px, py] = spine[i];
    const r = radius(s);
    const color = i % 2 ? '#F2E8D0' : '#E9DCBC';
    cut(ctx, ovalPath(px, py, r * 0.78, r, 0), feed > 0 && i > 2 && i < n - 1 ? lerpColor(color, '#E4C58E', feed) : color, texture, 3);
  }
  // Head capsule and mandibles.
  const [hx, hy] = spine[0];
  const hr = len * 0.085;
  ctx.save();
  ctx.translate(hx + hr * 0.3, hy);
  ctx.rotate(look);
  cut(ctx, ovalPath(0, 0, hr * 1.05, hr, 0), '#E2C690', texture, 4);
  const msize = hr * 1.4;
  ctx.save();
  ctx.translate(-hr * 0.8, -hr * 0.12);
  ctx.rotate(-0.25 - jaw * 0.45);
  cut(ctx, mandiblePath(msize), '#7A4A24', texture, 2);
  ctx.restore();
  ctx.save();
  ctx.translate(-hr * 0.75, hr * 0.28);
  ctx.scale(1, -1);
  ctx.rotate(-0.15 - jaw * 0.45);
  cut(ctx, mandiblePath(msize * 0.9), '#5E3519', texture, 2);
  ctx.restore();
  ctx.restore();
  ctx.restore();
}

/** Front view of the young larva's head for the jaw close-up. size ~ head radius.
 * Two sharply pointed, sickle-shaped mandibles; a row of small teeth on each inner edge (IN319, first instar).
 * open 0..1 spreads the jaws; teethK 0..1 pops the teeth in one by one. */
export function drawJawFace(ctx, texture, x, y, size, open = 0, teethK = 1, boost = 0, lime = 0) {
  const out = { tips: [], edges: [] };
  ctx.save();
  ctx.translate(x, y);
  // Body rings behind the head, curving away from the viewer.
  cut(ctx, ovalPath(0, -size * 0.62, size * 1.28, size * 0.9), '#EADCBB', texture, 6);
  cut(ctx, ovalPath(0, -size * 0.34, size * 1.16, size * 0.9), '#F3E9D3', texture, 6);
  cut(ctx, ovalPath(0, 0, size, size * 0.92), '#E5C994', texture, 10);
  cut(ctx, smoothPath([[-size * 0.72, -size * 0.5], [-size * 0.25, -size * 0.84], [size * 0.38, -size * 0.8], [size * 0.08, -size * 0.6], [-size * 0.45, -size * 0.42]]), '#F0D9AA', texture, 2);
  cut(ctx, ovalPath(0, size * 0.5, size * 0.3, size * 0.15), '#6E4430', texture, 1);
  const L = size * 0.95;
  const B = [0, 0];
  const Cp = [0.25 * L, 0.55 * L];
  const T = [-0.5 * L, 0.85 * L];
  const at = u => [
    (1 - u) * (1 - u) * B[0] + 2 * (1 - u) * u * Cp[0] + u * u * T[0],
    (1 - u) * (1 - u) * B[1] + 2 * (1 - u) * u * Cp[1] + u * u * T[1],
  ];
  const dir = u => {
    const d = [2 * (1 - u) * (Cp[0] - B[0]) + 2 * u * (T[0] - Cp[0]), 2 * (1 - u) * (Cp[1] - B[1]) + 2 * u * (T[1] - Cp[1])];
    const n = Math.hypot(d[0], d[1]) || 1;
    return [d[0] / n, d[1] / n];
  };
  const n = 20;
  const centre = [-0.35 * L, 0.25 * L];
  for (const side of [-1, 1]) {
    ctx.save();
    ctx.translate(side * size * 0.38, size * 0.3);
    ctx.scale(side, 1);
    ctx.rotate(-open * 0.6);
    const toWorld = p => {
      const r = [p[0] * Math.cos(-open * 0.6) - p[1] * Math.sin(-open * 0.6), p[0] * Math.sin(-open * 0.6) + p[1] * Math.cos(-open * 0.6)];
      return [x + side * size * 0.38 + side * r[0], y + size * 0.3 + r[1]];
    };
    const a = [];
    const b = [];
    const innerSide = [];
    for (let i = 0; i <= n; i += 1) {
      const u = i / n;
      const p = at(u);
      const d = dir(u);
      const nn = [-d[1], d[0]];
      const w = L * 0.17 * Math.pow(1 - u, 0.8) + 1;
      const pa = [p[0] + nn[0] * w, p[1] + nn[1] * w];
      const pb = [p[0] - nn[0] * w, p[1] - nn[1] * w];
      a.push(pa);
      b.push(pb);
      const da = Math.hypot(pa[0] - centre[0], pa[1] - centre[1]);
      const db = Math.hypot(pb[0] - centre[0], pb[1] - centre[1]);
      innerSide.push(da < db ? [pa, nn, 1] : [pb, nn, -1]);
    }
    if (lime > 0.01) {
      // Lime marker along the row of teeth, under the jaw so the teeth stand out against it.
      const row = innerSide.slice(4, n - 1).map(([p, nn, sgn]) => [p[0] + nn[0] * sgn * L * 0.05, p[1] + nn[1] * sgn * L * 0.05]);
      const upto = Math.max(2, Math.ceil(row.length * clamp(lime)));
      ctx.save();
      ctx.lineCap = 'round';
      ctx.lineJoin = 'round';
      ctx.strokeStyle = C.lime;
      ctx.lineWidth = L * 0.16;
      ctx.beginPath();
      row.slice(0, upto).forEach(([px, py], i) => (i ? ctx.lineTo(px, py) : ctx.moveTo(px, py)));
      ctx.stroke();
      ctx.restore();
    }
    cut(ctx, polyPath([...a, ...b.reverse()]), '#7C4B22', texture, 7);
    // Lighter ridge along the outer curve.
    const ridge = [];
    for (let i = 0; i <= 10; i += 1) {
      const p = at(i / 14);
      const d = dir(i / 14);
      ridge.push([p[0] + d[1] * L * 0.06, p[1] - d[0] * L * 0.06]);
    }
    ctx.save();
    ctx.lineWidth = L * 0.05;
    ctx.lineCap = 'round';
    ctx.strokeStyle = 'rgba(205,150,90,0.55)';
    ctx.beginPath();
    ridge.forEach(([px, py], i) => (i ? ctx.lineTo(px, py) : ctx.moveTo(px, py)));
    ctx.stroke();
    ctx.restore();
    // A row of small teeth along the inner edge.
    for (let i = 5, j = 0; i < n - 2; i += 2, j += 1) {
      const pop = eBack(clamp(teethK * 7 - j), 2.4);
      if (pop <= 0.01) continue;
      const [p, nn, sgn] = innerSide[i];
      const d = dir(i / n);
      const ts = L * 0.075 * pop * (1 + 0.7 * boost * Math.sin(Math.PI * clamp(boost * 6 - j * 0.6)));
      const out = [nn[0] * sgn, nn[1] * sgn];
      cut(ctx, polyPath([[p[0] - d[0] * ts * 0.7, p[1] - d[1] * ts * 0.7], [p[0] + out[0] * ts * 1.3, p[1] + out[1] * ts * 1.3], [p[0] + d[0] * ts * 0.7, p[1] + d[1] * ts * 0.7]]), '#5A3216', texture, 1);
    }
    // Dark, sharp point.
    const tipBase = at(0.86);
    const d = dir(0.86);
    const nn = [-d[1], d[0]];
    const w = L * 0.17 * Math.pow(0.14, 0.8) + 1;
    cut(ctx, polyPath([[tipBase[0] + nn[0] * w, tipBase[1] + nn[1] * w], [T[0] + d[0] * L * 0.04, T[1] + d[1] * L * 0.04], [tipBase[0] - nn[0] * w, tipBase[1] - nn[1] * w]]), '#3A1F0E', texture, 1);
    out.tips.push(toWorld([T[0] + d[0] * L * 0.04, T[1] + d[1] * L * 0.04]));
    out.edges.push(innerSide.slice(4, n - 1).map(([p]) => toWorld(p)));
    ctx.restore();
  }
  ctx.restore();
  return out;
}

// ------------------------------------------------------------------ cockroach egg case (ootheca)
// Hardened, purse-shaped case about 8 x 5 mm, brown when laid, soon dark; a ridged seam (keel)
// along the top; 16 eggs in two rows of eight (UF/IFAS EENY-141; Lander Univ.). Shape in units of L.
const CASE_PTS = [[-0.5, 0.02], [-0.47, -0.19], [-0.38, -0.285], [-0.2, -0.315], [0, -0.32], [0.2, -0.315], [0.38, -0.285], [0.47, -0.19], [0.5, 0.02], [0.47, 0.2], [0.36, 0.285], [0.15, 0.31], [-0.15, 0.31], [-0.36, 0.285], [-0.47, 0.2]];
const scalePts = (pts, L, s = 1) => pts.map(([a, b]) => [a * L * s, b * L * s]);
export const CASE_H = 0.63; // height as a share of length
export const CASE_HOLE = { x: 0.3, y: 0.05, r: 0.085 };

function keelPath(L) {
  const top = [];
  const n = 26;
  for (let i = 0; i <= n; i += 1) {
    const s = i / n;
    const x = (-0.4 + 0.8 * s) * L;
    const base = -0.31 * L - 0.018 * L * Math.sin(Math.PI * s);
    top.push([x, base - (i % 2 ? 0.034 : 0.018) * L]);
  }
  return polyPath([[-0.42 * L, -0.27 * L], ...top, [0.42 * L, -0.27 * L], [0, -0.28 * L]]);
}

const CASE_COLORS = { base: '#5B3424', top: '#7B4733', keel: '#3F2419', ridge: 'rgba(38,20,12,0.5)', light: 'rgba(255,214,170,0.16)' };

/**
 * Exterior of an egg case, centred on (x, y), length L. Options: angle, fresh (0..1, brown to dark),
 * hole: { cut: 0..1 chewed arc, open: 0..1 hole opened }.
 */
export function drawEggCase(ctx, texture, x, y, L, opts = {}) {
  const { angle = 0, hole = null, glow = 0, k = 1 } = opts;
  if (k <= 0.01) return;
  const s = eBack(clamp(k), 2);
  ctx.save();
  ctx.translate(x, y);
  ctx.rotate(angle);
  ctx.scale(s, s);
  const outline = smoothPath(scalePts(CASE_PTS, L));
  cut(ctx, keelPath(L), CASE_COLORS.keel, texture, 4);
  cut(ctx, outline, CASE_COLORS.base, texture, 10);
  ctx.save();
  ctx.clip(outline);
  cut(ctx, smoothPath([[-0.55 * L, -0.4 * L], [0.55 * L, -0.4 * L], [0.5 * L, -0.12 * L], [0, -0.06 * L], [-0.5 * L, -0.12 * L]]), CASE_COLORS.top, texture, 2);
  // Ridges between the egg compartments.
  ctx.strokeStyle = CASE_COLORS.ridge;
  ctx.lineWidth = Math.max(2, L * 0.012);
  ctx.lineCap = 'round';
  for (let i = 1; i < 8; i += 1) {
    const rx = (-0.5 + i / 8) * L * 0.96;
    ctx.beginPath();
    ctx.moveTo(rx - L * 0.01, -0.3 * L);
    ctx.quadraticCurveTo(rx + L * 0.03, 0, rx - L * 0.005, 0.31 * L);
    ctx.stroke();
  }
  ctx.strokeStyle = CASE_COLORS.light;
  ctx.lineWidth = Math.max(1.5, L * 0.008);
  for (let i = 1; i < 8; i += 1) {
    const rx = (-0.5 + i / 8) * L * 0.96 + L * 0.016;
    ctx.beginPath();
    ctx.moveTo(rx - L * 0.01, -0.26 * L);
    ctx.quadraticCurveTo(rx + L * 0.03, 0, rx - L * 0.005, 0.27 * L);
    ctx.stroke();
  }
  if (glow > 0) {
    ctx.fillStyle = `rgba(255,236,200,${0.3 * glow})`;
    ctx.fillRect(-L, -L, 2 * L, 2 * L);
  }
  ctx.restore();
  if (hole) drawCaseHole(ctx, texture, L, hole);
  ctx.restore();
}

// Jagged round exit hole near one end of a long side (IN319). cut: chewing arc 0..1, open: hole 0..1.
function holePoints(cx, cy, r, seed = 3) {
  const pts = [];
  for (let i = 0; i < 22; i += 1) {
    const a = (i / 22) * TAU;
    const rr = r * (1 + (hash(seed + i * 1.7) - 0.5) * 0.18);
    pts.push([cx + Math.cos(a) * rr, cy + Math.sin(a) * rr]);
  }
  return pts;
}
export function drawCaseHole(ctx, texture, L, hole) {
  const cx = CASE_HOLE.x * L;
  const cy = CASE_HOLE.y * L;
  const r = CASE_HOLE.r * L;
  const open = clamp(hole.open ?? 0);
  if (open > 0) {
    cut(ctx, polyPath(holePoints(cx, cy, r * (0.8 + 0.2 * eOut(open)))), '#1A0F0B', texture, 0);
    ctx.save();
    ctx.strokeStyle = 'rgba(160,110,80,0.6)';
    ctx.lineWidth = Math.max(2, L * 0.008);
    ctx.stroke(polyPath(holePoints(cx, cy, r * 1.04, 9)));
    ctx.restore();
  }
  const k = clamp(hole.cut ?? 0);
  if (k > 0 && open < 1) {
    ctx.save();
    ctx.strokeStyle = '#1E1210';
    ctx.lineWidth = Math.max(3, L * 0.016);
    ctx.lineCap = 'round';
    ctx.lineJoin = 'round';
    ctx.beginPath();
    const steps = Math.max(2, Math.round(40 * Math.min(0.999, k)));
    for (let i = 0; i <= steps; i += 1) {
      const a = -Math.PI / 2 + (i / 40) * TAU;
      const rr = r * (1 + (i % 2 ? 0.07 : -0.05));
      const px = cx + Math.cos(a) * rr;
      const py = cy + Math.sin(a) * rr;
      if (i) ctx.lineTo(px, py); else ctx.moveTo(px, py);
    }
    ctx.stroke();
    ctx.restore();
  }
}
// The chewed-out disc, drawn by the scene where it falls.
export function drawCaseDisc(ctx, texture, x, y, r, angle = 0) {
  ctx.save();
  ctx.translate(x, y);
  ctx.rotate(angle);
  cut(ctx, polyPath(holePoints(0, 0, r, 5)), CASE_COLORS.base, texture, 4);
  cut(ctx, polyPath(holePoints(-r * 0.15, -r * 0.2, r * 0.45, 8)), CASE_COLORS.top, texture, 0);
  ctx.restore();
}

/**
 * Egg case cut open, centred on (x, y), length L. state:
 *  eggs: array of 16 values 0..1 (1 whole, 0 eaten, empty shell), order front row 0..7 then back row.
 *  waspEgg 0..1 (shows the wasp's single white egg), drawInside(ctx, L) draws extra pieces inside.
 */
export function drawCaseCutaway(ctx, texture, x, y, L, state = {}) {
  const { angle = 0, eggs = null, waspEgg = 0, drawInside = null, t = 0, wall = 1 } = state;
  ctx.save();
  ctx.translate(x, y);
  ctx.rotate(angle);
  const outline = smoothPath(scalePts(CASE_PTS, L));
  const inner = smoothPath(scalePts(CASE_PTS, L, 0.9));
  cut(ctx, keelPath(L), CASE_COLORS.keel, texture, 4);
  cut(ctx, outline, CASE_COLORS.base, texture, 12);
  // Cut edge of the wall.
  ctx.save();
  ctx.lineWidth = L * 0.012;
  ctx.strokeStyle = '#B07A58';
  ctx.stroke(inner);
  ctx.restore();
  cut(ctx, inner, '#6A3F28', texture, 0);
  ctx.save();
  ctx.clip(inner);
  const glow = ctx.createRadialGradient(0, -0.05 * L, L * 0.05, 0, 0, L * 0.6);
  glow.addColorStop(0, 'rgba(255,200,130,0.42)');
  glow.addColorStop(1, 'rgba(255,200,130,0.04)');
  ctx.fillStyle = glow;
  ctx.fillRect(-L, -L, 2 * L, 2 * L);
  const values = eggs ?? new Array(16).fill(1);
  const { bounce = 0, highlight = null } = state;
  // Back row, offset half an egg and darker, then the front row.
  for (let idx = 8; idx < 16; idx += 1) {
    const g = caseEgg(L, idx);
    drawRoachEgg(ctx, texture, g.x, g.y, g.rx * 2, g.ry * 2, values[idx] ?? 1, true, idx, t, bounce);
  }
  for (let idx = 0; idx < 8; idx += 1) {
    const g = caseEgg(L, idx);
    drawRoachEgg(ctx, texture, g.x, g.y, g.rx * 2, g.ry * 2, values[idx] ?? 1, false, idx, t, bounce);
  }
  if (highlight) {
    ctx.save();
    ctx.lineCap = 'round';
    for (let idx = 0; idx < 16; idx += 1) {
      const k = clamp(highlight[idx] ?? 0);
      if (k <= 0.01) continue;
      const g = caseEgg(L, idx);
      const s = eBack(k, 2.4);
      ctx.globalAlpha = Math.min(1, k * 2);
      ctx.strokeStyle = C.lime;
      ctx.lineWidth = L * 0.012;
      ctx.beginPath();
      ctx.ellipse(g.x, g.y, g.rx * 1.12 * s, g.ry * 1.06 * s, 0, 0, TAU * 0.9995);
      ctx.stroke();
    }
    ctx.restore();
  }
  if (waspEgg > 0) drawWaspEgg(ctx, texture, 0.02 * L, -0.255 * L, 0.15 * L, -0.06, waspEgg);
  if (drawInside) drawInside(ctx, L);
  ctx.restore();
  // Rim highlight on the cut wall.
  if (wall > 0) {
    ctx.save();
    ctx.globalAlpha = 0.55;
    ctx.lineWidth = L * 0.006;
    ctx.strokeStyle = '#B07A5C';
    ctx.stroke(outline);
    ctx.restore();
  }
  ctx.restore();
}

// Egg geometry inside a cutaway of length L, case-local coordinates. 0..7 front row, 8..15 back row.
export function caseEgg(L, i) {
  const spacing = 0.86 * L / 8;
  if (i < 8) return { x: (-0.43 + (i + 0.5) / 8 * 0.86) * L, y: 0.035 * L, rx: spacing * 0.46, ry: 0.25 * L };
  const j = i - 8;
  return { x: (-0.43 + (j + 1) / 8 * 0.86) * L - spacing * 0.08, y: -0.045 * L, rx: spacing * 0.46, ry: 0.24 * L };
}

// One cockroach egg centred on (x, y): pale, elongated. whole 1 = intact; 0 = an empty, collapsed shell.
export function drawRoachEgg(ctx, texture, x, y, w, h, whole = 1, back = false, i = 0, t = 0, bounce = 0) {
  const k = clamp(whole);
  const base = back ? '#DCC392' : '#F2E2B8';
  if (k > 0.02) {
    const ry = h / 2 * (0.55 + 0.45 * k) * (1 + 0.1 * bounce);
    const rx = w / 2 * (0.8 + 0.2 * k) * (1 - 0.04 * bounce);
    const breathe = 1 + 0.015 * Math.sin(t * 2.2 + i * 1.3);
    const cy = y + h / 2 - ry;
    const r = rx * breathe;
    const body = cut(ctx, capsulePath([x, cy - ry + r], [x, cy + ry - r], r, r), k < 1 ? lerpColor('#C9B48A', base, k) : base, texture, back ? 2 : 4);
    ctx.save();
    ctx.lineWidth = Math.max(2, rx * 0.09);
    ctx.strokeStyle = back ? 'rgba(150,115,70,0.6)' : 'rgba(176,140,92,0.75)';
    ctx.stroke(body);
    if (!back) {
      ctx.fillStyle = `rgba(255,255,255,${0.5 * k})`;
      ctx.fill(capsulePath([x - rx * 0.42, cy - ry * 0.7], [x - rx * 0.42, cy - ry * 0.05], rx * 0.14, rx * 0.1));
    }
    ctx.restore();
  }
  if (k < 0.98) {
    // Empty shell: crumpled, see-through outline.
    const e = 1 - k;
    ctx.save();
    ctx.globalAlpha = 0.75 * e;
    const pts = [];
    for (let j = 0; j < 16; j += 1) {
      const a = (j / 16) * TAU;
      const wr = 1 + (hash(i * 31 + j) - 0.5) * 0.16;
      const sag = Math.sin(a) > 0 ? 1 : 0.55;
      pts.push([x + Math.cos(a) * w * 0.46 * wr, y + h * 0.4 + Math.sin(a) * h * 0.09 * wr * sag]);
    }
    const p = polyPath(pts);
    ctx.fillStyle = 'rgba(232,214,178,0.35)';
    ctx.fill(p);
    ctx.lineWidth = Math.max(2, w * 0.05);
    ctx.lineJoin = 'round';
    ctx.strokeStyle = 'rgba(214,190,150,0.9)';
    ctx.stroke(p);
    ctx.restore();
  }
}

// ------------------------------------------------------------------ American cockroach (Periplaneta americana)
// Reddish brown, pale-yellow band around the pronotum edge, long wings over the abdomen,
// long whip-like antennae, strong spiny legs, a pair of cerci (UF/IFAS EENY-141; UMN Extension).
const R = {
  rim: '#E2B866', pronotum: '#9A4A2A', blotch: '#5A2414', wing: '#8E3B21', wingHi: '#B35D38', wingDark: '#6B2A17',
  head: '#6A2C1B', leg: '#A4552F', legFar: '#7A3B22', spine: '#4A2214', belly: '#5A2716',
};

// Top view, head toward -y at angle 0. About 820 px long at scale 1, plus antennae.
const TOP_LEGS = [
  { hip: [-70, -150], knee: [-190, -230], foot: [-250, -330], group: 0 },
  { hip: [-80, -70], knee: [-230, -40], foot: [-300, 40], group: 1 },
  { hip: [-70, 10], knee: [-200, 140], foot: [-250, 320], group: 0 },
];
export function drawRoachTop(ctx, texture, x, y, scale, angle = 0, pose = {}) {
  const { phase = 0, walk = 0, ant = 0, t = 0, ootheca = 0 } = pose;
  ctx.save();
  ctx.translate(x, y);
  ctx.rotate(angle);
  ctx.scale(scale, scale);
  // Soft floor shadow.
  ctx.save();
  ctx.fillStyle = 'rgba(40,24,16,0.13)';
  ctx.fill(ovalPath(14, 30, 170, 400, 0));
  ctx.restore();
  // Legs, mirrored left and right; tripod swing driven by phase.
  for (const side of [-1, 1]) {
    TOP_LEGS.forEach((leg, i) => {
      const group = side < 0 ? leg.group : 1 - leg.group;
      let u = (phase + group * Math.PI) % TAU;
      if (u < 0) u += TAU;
      const swing = walk * (u < Math.PI ? Math.cos(u) : -Math.cos(u)) * (i === 1 ? 0.22 : 0.28);
      const hip = [leg.hip[0] * side, leg.hip[1]];
      const knee = add(hip, rot([(leg.knee[0] - leg.hip[0]) * side, leg.knee[1] - leg.hip[1]], swing * side * -1));
      const foot = add(hip, rot([(leg.foot[0] - leg.hip[0]) * side, leg.foot[1] - leg.hip[1]], swing * side * -1.15));
      cut(ctx, capsulePath(hip, knee, 17, 13), R.leg, texture, 4);
      cut(ctx, capsulePath(knee, foot, 11, 6), R.leg, texture, 4);
      // Spines along the tibia.
      for (let s = 1; s <= 5; s += 1) {
        const p = lerp2(knee, foot, s / 6.2);
        const d = [foot[0] - knee[0], foot[1] - knee[1]];
        const n = Math.hypot(d[0], d[1]) || 1;
        const o = [-d[1] / n * side, d[0] / n * side];
        cut(ctx, polyPath([[p[0] + o[0] * 6, p[1] + o[1] * 6], [p[0] + o[0] * 26 + d[0] / n * 14, p[1] + o[1] * 26 + d[1] / n * 14], [p[0] + d[0] / n * 12, p[1] + d[1] / n * 12]]), R.spine, null, 0);
      }
      const tarsus = add(foot, [(i === 0 ? -20 : i === 2 ? -10 : -30) * side, i === 0 ? -40 : 40]);
      cut(ctx, capsulePath(foot, tarsus, 6, 4), R.legFar, texture, 2);
    });
  }
  // Antennae: long, thin, sweeping back along the sides.
  for (const side of [-1, 1]) {
    const wave = Math.sin(t * 3.1 + side) * 0.14 + ant * side * 0.2;
    const pts = chain([side * 26, -400], -Math.PI / 2 + side * 0.32 + wave, [[110, side * 0.12], [150, side * 0.14 + wave * 0.5], [160, side * 0.16], [160, side * 0.18 + wave], [140, side * 0.2]]);
    drawChain(ctx, texture, pts, 6, 3, '#8A4428', 2);
  }
  // Cerci at the tail.
  for (const side of [-1, 1]) cut(ctx, capsulePath([side * 40, 330], [side * 70, 430], 9, 4), R.legFar, texture, 3);
  if (ootheca > 0.01) {
    const k = eBack(clamp(ootheca), 1.6);
    ctx.save();
    ctx.translate(0, 410);
    ctx.scale(k, k);
    drawEggCaseTop(ctx, texture, 0, 40, 150);
    ctx.restore();
  }
  // Abdomen edge peeking out, then the two wings.
  cut(ctx, smoothPath([[-120, -170], [-150, 40], [-120, 330], [0, 400], [120, 330], [150, 40], [120, -170]]), R.belly, texture, 8);
  cut(ctx, smoothPath([[4, -210], [-128, -190], [-160, 60], [-120, 340], [-20, 430], [10, 420]]), R.wing, texture, 6);
  cut(ctx, smoothPath([[-4, -210], [128, -190], [160, 60], [120, 340], [30, 430], [-20, 410], [-6, 120]]), R.wingDark, texture, 5);
  cut(ctx, smoothPath([[-30, -190], [-110, -170], [-128, 40], [-90, 240], [-60, 120], [-40, -60]]), R.wingHi, texture, 2, { grain: 0.7 });
  ctx.save();
  ctx.strokeStyle = 'rgba(60,20,10,0.35)';
  ctx.lineWidth = 3;
  for (let i = 0; i < 9; i += 1) {
    ctx.beginPath();
    ctx.moveTo(-20 - i * 4, -120 + i * 50);
    ctx.lineTo(-120 + i * 2, -60 + i * 50);
    ctx.moveTo(30 + i * 3, -100 + i * 52);
    ctx.lineTo(130 - i * 2, -40 + i * 52);
    ctx.stroke();
  }
  ctx.restore();
  // Head peeking out ahead of the pronotum.
  cut(ctx, ovalPath(0, -395, 52, 46), R.head, texture, 4);
  cut(ctx, ovalPath(-30, -400, 13, 20, 0.3), '#2A1510', null, 0);
  cut(ctx, ovalPath(30, -400, 13, 20, -0.3), '#2A1510', null, 0);
  // Pronotum: rounded shield, pale-yellow rim, darker paired markings.
  cut(ctx, smoothPath([[-150, -250], [-130, -350], [-60, -400], [60, -400], [130, -350], [150, -250], [90, -205], [-90, -205]]), R.rim, texture, 7);
  cut(ctx, smoothPath([[-118, -258], [-102, -335], [-50, -372], [50, -372], [102, -335], [118, -258], [70, -226], [-70, -226]]), R.pronotum, texture, 3);
  cut(ctx, smoothPath([[-96, -256], [-84, -322], [-40, -352], [0, -334], [40, -352], [84, -322], [96, -256], [40, -236], [0, -256], [-40, -236]]), R.blotch, texture, 1);
  cut(ctx, smoothPath([[-50, -300], [-30, -330], [0, -318], [30, -330], [50, -300], [0, -284]]), '#7A3420', texture, 0);
  ctx.restore();
}

// Egg case seen from above: long rounded body with the ridged seam down the middle.
export function drawEggCaseTop(ctx, texture, x, y, L, angle = 0) {
  ctx.save();
  ctx.translate(x, y);
  ctx.rotate(angle);
  cut(ctx, smoothPath([[-0.5 * L, 0], [-0.44 * L, -0.2 * L], [0, -0.24 * L], [0.44 * L, -0.2 * L], [0.5 * L, 0], [0.44 * L, 0.2 * L], [0, 0.24 * L], [-0.44 * L, 0.2 * L]]), CASE_COLORS.base, texture, 6);
  cut(ctx, polyPath(Array.from({ length: 21 }, (_, i) => [(-0.42 + 0.84 * i / 20) * L, (i % 2 ? -0.05 : -0.02) * L]).concat([[0.42 * L, 0.03 * L], [-0.42 * L, 0.03 * L]])), CASE_COLORS.keel, texture, 2);
  ctx.strokeStyle = CASE_COLORS.ridge;
  ctx.lineWidth = Math.max(2, L * 0.012);
  for (let i = 1; i < 8; i += 1) {
    const rx = (-0.5 + i / 8) * L;
    ctx.beginPath();
    ctx.moveTo(rx, -0.2 * L);
    ctx.lineTo(rx, 0.2 * L);
    ctx.stroke();
  }
  ctx.restore();
}

// Side view, faces left, feet on y = 150. About 860 px nose to wing tip at scale 1.
export const ROACH_FOOT_Y = 150;
const RS = {
  belly: smoothPath([[-250, -36], [-100, -20], [150, -18], [380, -40], [420, -62], [300, -70], [0, -70], [-230, -70]]),
  wing: smoothPath([[-250, -120], [-120, -148], [120, -142], [330, -112], [448, -76], [430, -50], [300, -44], [60, -42], [-200, -50], [-262, -78]]),
  wingHi: smoothPath([[-220, -128], [-100, -146], [120, -138], [300, -112], [120, -122], [-100, -126]]),
  pronotum: smoothPath([[-372, -84], [-350, -140], [-292, -168], [-226, -156], [-200, -112], [-214, -66], [-300, -56], [-360, -60]]),
  pronotumIn: smoothPath([[-350, -92], [-330, -136], [-288, -154], [-238, -144], [-218, -110], [-230, -76], [-300, -68]]),
  head: ovalPath(-372, -40, 40, 52, 0.4),
};
const SIDE_LEGS = [
  { hip: [-280, -50], foot: [-420, 150], l1: 120, l2: 150, pref: [-0.3, -1], group: 0 },
  { hip: [-170, -44], foot: [-160, 150], l1: 130, l2: 165, pref: [0.6, -1], group: 1 },
  { hip: [-60, -44], foot: [190, 150], l1: 175, l2: 210, pref: [0.4, -1], group: 0 },
];
export function drawRoachSide(ctx, texture, pose = {}) {
  const { phase = 0, walk = 0, stride = 34, lift = 22, ant = 0, t = 0, ootheca = 0, shadows = true } = pose;
  const legs = [];
  for (let side = 0; side < 2; side += 1) {
    SIDE_LEGS.forEach((leg, i) => {
      const far = side === 0;
      const hip = add(leg.hip, far ? [16, -8] : [0, 0]);
      const rest = add(leg.foot, far ? [40, -24] : [0, 0]);
      const f = gaitFoot(rest, far ? 1 - leg.group : leg.group, phase, walk, stride, lift);
      const s = knee2(hip, [f[0], f[1]], leg.l1, leg.l2, leg.pref);
      legs.push({ far, i, hip, knee: s.knee, foot: s.foot, air: f[2] });
    });
  }
  if (shadows) {
    ctx.save();
    ctx.fillStyle = 'rgba(40,24,16,0.2)';
    ctx.fill(ovalPath(20, ROACH_FOOT_Y + 6, 420, 16));
    ctx.restore();
  }
  const drawLeg = (l, color) => {
    cut(ctx, capsulePath(l.hip, l.knee, l.far ? 12 : 15, l.far ? 10 : 12), color, texture, 3);
    cut(ctx, capsulePath(l.knee, l.foot, l.far ? 8 : 10, 5), color, texture, 3);
    const d = [l.foot[0] - l.knee[0], l.foot[1] - l.knee[1]];
    const n = Math.hypot(d[0], d[1]) || 1;
    for (let s = 1; s <= 5; s += 1) {
      const p = lerp2(l.knee, l.foot, s / 6.2);
      const o = [d[1] / n, -d[0] / n];
      const side = l.i === 0 ? -1 : 1;
      cut(ctx, polyPath([[p[0] + o[0] * 4 * side, p[1] + o[1] * 4 * side], [p[0] + o[0] * 22 * side + d[0] / n * 12, p[1] + o[1] * 22 * side + d[1] / n * 12], [p[0] + d[0] / n * 12, p[1] + d[1] / n * 12]]), R.spine, null, 0);
    }
    const tar = [l.foot[0] + (l.i === 0 ? -34 : 34), l.foot[1] - 2];
    cut(ctx, capsulePath(l.foot, tar, 5, 3.5), color, texture, 2);
  };
  legs.filter(l => l.far).forEach(l => drawLeg(l, R.legFar));
  // Far antenna and cerci.
  const antenna = (side, color) => {
    const wave = Math.sin(t * 3 + side * 1.7) * 0.12 + ant * 0.25;
    const pts = chain([-404, -66], -2.6 + side * 0.25 + wave, [[120, 0.18], [150, 0.2 + wave * 0.6], [150, 0.22], [150, 0.26 + wave], [140, 0.3]]);
    drawChain(ctx, texture, pts, 5, 2.6, color, 2);
  };
  antenna(1, '#6E3220');
  cut(ctx, capsulePath([410, -66], [500, -96], 8, 3), R.legFar, texture, 2);
  cut(ctx, RS.belly, R.belly, texture, 6);
  ctx.save();
  ctx.strokeStyle = 'rgba(30,10,4,0.4)';
  ctx.lineWidth = 3;
  for (let i = 0; i < 6; i += 1) {
    ctx.beginPath();
    ctx.moveTo(-60 + i * 70, -66);
    ctx.lineTo(-50 + i * 70, -24);
    ctx.stroke();
  }
  ctx.restore();
  if (ootheca > 0.01) {
    const k = eBack(clamp(ootheca), 1.6);
    ctx.save();
    ctx.translate(436, -40);
    ctx.rotate(0.15);
    ctx.scale(k, k);
    drawEggCase(ctx, texture, 60, 0, 120, { angle: 0 });
    ctx.restore();
  }
  cut(ctx, RS.wing, R.wing, texture, 8);
  cut(ctx, RS.wingHi, R.wingHi, texture, 2, { grain: 0.7 });
  ctx.save();
  ctx.strokeStyle = 'rgba(60,20,10,0.32)';
  ctx.lineWidth = 3;
  for (let i = 0; i < 7; i += 1) {
    ctx.beginPath();
    ctx.moveTo(-150 + i * 80, -136 + i * 3);
    ctx.lineTo(-90 + i * 80, -60);
    ctx.stroke();
  }
  ctx.restore();
  cut(ctx, RS.head, R.head, texture, 4);
  cut(ctx, ovalPath(-378, -54, 12, 18, 0.4), '#2A1510', null, 0);
  cut(ctx, capsulePath([-392, -6], [-410, 20], 5, 3), R.legFar, texture, 1);
  cut(ctx, RS.pronotum, R.rim, texture, 6);
  cut(ctx, RS.pronotumIn, R.pronotum, texture, 2);
  cut(ctx, smoothPath([[-330, -120], [-290, -146], [-252, -136], [-284, -118]]), R.blotch, texture, 1);
  legs.filter(l => !l.far).forEach(l => drawLeg(l, R.leg));
  cut(ctx, capsulePath([404, -70], [496, -112], 9, 3.5), R.leg, texture, 2);
  antenna(-1, '#8A4428');
}

export function placeRoach(ctx, texture, x, groundY, scale, pose = {}, options = {}) {
  ctx.save();
  ctx.translate(x, groundY);
  if (options.rotation) ctx.rotate(options.rotation);
  ctx.scale(options.faceRight ? -scale : scale, scale);
  ctx.translate(0, -ROACH_FOOT_Y);
  drawRoachSide(ctx, texture, pose);
  ctx.restore();
}

// ------------------------------------------------------------------ props and symbols
// "Ensign" means flag: a small paper pennant on a pole that waves in time with the gaster.
export function ensignFlag(ctx, texture, x, y, size, k, wave = 0, t = 0) {
  if (k <= 0.01) return;
  const s = eBack(clamp(k), 2.2);
  ctx.save();
  ctx.translate(x, y);
  ctx.scale(s, s);
  ctx.rotate(wave * 0.25);
  cut(ctx, capsulePath([0, 0], [0, -size * 1.5], size * 0.05, size * 0.04), '#8B6B4A', texture, 4);
  cut(ctx, ovalPath(0, -size * 1.52, size * 0.08, size * 0.08), C.lime, texture, 2);
  const pts = [];
  const n = 10;
  for (let i = 0; i <= n; i += 1) {
    const u = i / n;
    pts.push([u * size * 1.1, -size * 1.45 + Math.sin(t * 7 - u * 4) * size * 0.06 * u]);
  }
  const bottom = [];
  for (let i = n; i >= 0; i -= 1) {
    const u = i / n;
    const notch = u > 0.85 ? (u - 0.85) * 2.2 : 0;
    bottom.push([u * size * 1.1 - notch * size * 0.5, -size * 0.85 + Math.sin(t * 7 - u * 4) * size * 0.06 * u - (u > 0.85 ? 0 : 0)]);
  }
  cut(ctx, polyPath([...pts, [size * 0.86, -size * 1.15], ...bottom]), C.purple, texture, 5);
  cut(ctx, polyPath([[0, -size * 1.2], [size * 0.7, -size * 1.2 + Math.sin(t * 7 - 2.5) * size * 0.04], [size * 0.7, -size * 1.08 + Math.sin(t * 7 - 2.5) * size * 0.04], [0, -size * 1.08]]), C.lime, texture, 1);
  ctx.restore();
}

// Lime ring drawn on like a marker; k 0..1 draws it, stops short of a full turn.
export function limeRing(ctx, x, y, rx, ry, k, rot0 = -0.05, width = 14) {
  const loop = Math.min(0.9995, eIO(clamp(k)));
  if (loop <= 0.001) return;
  ctx.save();
  ctx.lineCap = 'round';
  ctx.strokeStyle = 'rgba(30,27,34,0.3)';
  ctx.lineWidth = width + 4;
  ctx.beginPath();
  ctx.ellipse(x + 5, y + 6, rx, ry, rot0, -Math.PI / 2, -Math.PI / 2 + TAU * loop);
  ctx.stroke();
  ctx.strokeStyle = C.lime;
  ctx.lineWidth = width;
  ctx.beginPath();
  ctx.ellipse(x, y, rx, ry, rot0, -Math.PI / 2, -Math.PI / 2 + TAU * loop);
  ctx.stroke();
  ctx.restore();
}

// Lime target: ring plus four ticks that snap in and turn.
export function targetMark(ctx, texture, x, y, r, k, t = 0) {
  if (k <= 0.01) return;
  const s = lerp(1.8, 1, eOut(clamp(k)));
  ctx.save();
  ctx.translate(x, y);
  ctx.rotate(0.6 * (1 - eOut(clamp(k))) + 0.05 * Math.sin(t * 2));
  ctx.scale(s, s);
  ctx.globalAlpha *= clamp(k * 3);
  ctx.lineCap = 'round';
  for (const [w, c, dx] of [[r * 0.13, 'rgba(30,27,34,0.3)', 5], [r * 0.1, C.lime, 0]]) {
    ctx.strokeStyle = c;
    ctx.lineWidth = w;
    ctx.beginPath();
    ctx.arc(dx, dx, r, 0, TAU * 0.9995);
    ctx.stroke();
    for (let i = 0; i < 4; i += 1) {
      const a = i * Math.PI / 2;
      ctx.beginPath();
      ctx.moveTo(dx + Math.cos(a) * r * 0.72, dx + Math.sin(a) * r * 0.72);
      ctx.lineTo(dx + Math.cos(a) * r * 1.32, dx + Math.sin(a) * r * 1.32);
      ctx.stroke();
    }
  }
  ctx.restore();
}

// A hand holding a flashlight, pointing along +x from the grip at (0, 0). on 0..1 lights the lens.
export function flashlightHand(ctx, texture, x, y, angle, scale, on = 1) {
  ctx.save();
  ctx.translate(x, y);
  ctx.rotate(angle);
  ctx.scale(scale, scale);
  // Sleeve behind the hand.
  cut(ctx, polyPath([[-420, -110], [-150, -92], [-130, 96], [-420, 120]]), C.purple, texture, 8);
  cut(ctx, polyPath([[-170, -96], [-130, -92], [-112, 92], [-150, 96]]), C.lime, texture, 2);
  // Flashlight body and head.
  cut(ctx, capsulePath([-120, 0], [170, 0], 46, 46), '#2F2A36', texture, 8);
  cut(ctx, polyPath([[160, -50], [250, -78], [262, -78], [262, 78], [250, 78], [160, 50]]), '#3A3442', texture, 8);
  cut(ctx, polyPath([[40, -46], [70, -46], [70, 46], [40, 46]]), C.lime, texture, 2);
  cut(ctx, ovalPath(262, 0, 16, 74), on > 0.5 ? '#FFF6CF' : '#BFB9A8', texture, 3);
  // Hand: palm wrapped round the body, four fingers and a thumb.
  cut(ctx, smoothPath([[-120, -70], [-20, -76], [40, -54], [40, 60], [-30, 84], [-120, 72]]), '#E6AE88', texture, 7);
  for (let i = 0; i < 4; i += 1) cut(ctx, ovalPath(-70 + i * 34, 52 + (i % 2) * 4, 22, 30, 0.1), i % 2 ? '#DDA27C' : '#E6AE88', texture, 3);
  cut(ctx, capsulePath([-60, -60], [30, -66], 22, 18), '#EDB894', texture, 4);
  ctx.restore();
}
