// Episode D6-6c917b49743b, absolute narration 27.20–40.55.
// Cut-paper illustrations of brood, cold wet weather, and upper nest use.
import {
  W, H, C, Path2D, clamp, lerp, eOut, eIO, eBack, prog, makeFibres,
  cut, polyPath, smoothPath, ovalPath, capsulePath, bandPath, withCamera,
  placeAnt, walkPhase, drawLarva, drawPupa, drawEgg, createCaptions, tuft,
} from './paper-kit.mjs';
import { createNest } from './nest-world.mjs';

const TAU = Math.PI * 2;

function screen(ctx, texture, color = C.paper) {
  ctx.save();
  ctx.setTransform(1, 0, 0, 1, 0, 0);
  cut(ctx, polyPath([[0, 0], [W, 0], [W, H], [0, H]]), color, texture, 0);
  ctx.restore();
}

function dust(ctx, texture, t, count = 25, area = [0, 200, 1080, 1100]) {
  const [x0, y0, w, h] = area;
  for (let i = 0; i < count; i += 1) {
    const x = x0 + ((i * 317 + t * (30 + i % 5 * 14)) % w + w) % w;
    const y = y0 + ((i * 229 - t * (19 + i % 4 * 9)) % h + h) % h;
    cut(ctx, ovalPath(x, y, 2.5 + i % 3, 1.6 + i % 2), i % 3 ? '#E9D5B5' : '#F8E9CB', texture, 0);
  }
}

function nurse(ctx, texture, x, y, scale, t, faceRight = false, carry = null, walk = 0) {
  placeAnt(ctx, texture, x, y, scale, {
    phase: walkPhase(Math.max(0, t) * 85, scale) + x * 0.013,
    walk, carry,
    mand: 0.12 + 0.08 * Math.sin(t * 5),
    head: 0.05 * Math.sin(t * 4 + x),
    antennae: [[-0.12 + 0.13 * Math.sin(t * 8 + x), 0.07], [-0.08 + 0.12 * Math.sin(t * 7 + x * 0.4), 0.08]],
  }, { faceRight });
}

function chamber(ctx, texture, x, y, rx, ry, t, warm = 0) {
  cut(ctx, ovalPath(x, y + 12, rx + 18, ry + 20), '#714739', texture, 10);
  cut(ctx, ovalPath(x, y, rx, ry), '#51383A', texture, 2);
  cut(ctx, ovalPath(x, y + 23, rx * 0.94, ry * 0.86), '#654443', texture, 0);
  if (warm > 0) {
    ctx.save();
    ctx.globalAlpha = warm * (0.48 + 0.04 * Math.sin(t * 4));
    cut(ctx, ovalPath(x, y - 30, rx * 0.92, ry * 0.72), '#F4CA75', texture, 0);
    ctx.restore();
  }
}

function brood(ctx, texture, t, x = 410, y = 1030, scale = 1) {
  ctx.save();
  ctx.translate(x, y);
  ctx.scale(scale, scale);
  drawPupa(ctx, texture, -135, -60, 0.42, -0.11, 0.35);
  drawLarva(ctx, texture, 75, -92, 1.48, 0.38, Math.sin(t * 4.1));
  for (let i = 0; i < 7; i += 1) {
    const xx = 100 + (i % 4) * 20 + (Math.floor(i / 4) % 2) * 8;
    const yy = -16 - Math.floor(i / 4) * 16;
    drawEgg(ctx, texture, xx, yy, 15, 0.27 + i * 0.1);
  }
  ctx.restore();
}

function nursery(ctx, texture, t, shot) {
  screen(ctx, texture, '#B5805D');
  const u = prog(t, shot === 1 ? 27.2 : 37.48, shot === 1 ? 28.48 : 38.98);
  const pull = shot === 8 ? eIO(prog(t, 38.3, 38.82)) : 0;
  const cam = shot === 1
    ? { x: lerp(540, 590, u), y: lerp(880, 890, u), zoom: lerp(1.0, 1.18, u) }
    : { x: lerp(570, 540, u), y: lerp(880, 1020, pull), zoom: lerp(1.14, 0.81, pull) + 0.06 * u };
  withCamera(ctx, cam, () => {
    cut(ctx, bandPath(-600, 1700, 240, 2300, 8, 401), '#B77C59', texture, 8);
    cut(ctx, bandPath(-600, 1700, 1420, 2300, 8, 402), '#9E6B53', texture, 8);
    chamber(ctx, texture, 530, 835, 525, 345, t, shot === 8 ? 0.38 : 0.13);
    cut(ctx, ovalPath(530, 1090, 468, 45), '#8A5945', texture, 6);
    dust(ctx, texture, t, 33, [15, 560, 1050, 510]);
    brood(ctx, texture, t, 350, 1070, 1);
    const carrierK = eOut(prog(t, 37.62, 38.05));
    const youngK = eOut(prog(t, 27.88, 28.22));
    if (shot === 1) {
      nurse(ctx, texture, 740, 1070, 0.43, t, false, null, 0.1);
      if (youngK > 0) nurse(ctx, texture, lerp(1200, 940, youngK), 1080, 0.29, t, false, null, 1);
    } else {
      const x = lerp(910, 760, carrierK);
      nurse(ctx, texture, x, 1066, 0.43, t, false, t < 38.0 ? 'larva' : null, t < 38.0 ? 1 : 0.05);
      if (t >= 38.0) drawLarva(ctx, texture, 655, 1016, 0.78, 0.3, Math.sin(t * 5));
      ctx.save();
      ctx.globalAlpha = 0.82 * pull;
      cut(ctx, bandPath(-600, 1700, 1370, 2300, 6, 403), '#77A5BF', texture, 0);
      ctx.restore();
    }
  });
}

function sun(ctx, texture, x, y, r, t, amount) {
  if (amount <= 0.001) return;
  ctx.save();
  ctx.globalAlpha = amount;
  ctx.translate(x, y);
  ctx.rotate(t * 0.4);
  for (let i = 0; i < 12; i += 1) {
    const a = i * TAU / 12;
    const len = r * (1.55 + 0.06 * Math.sin(t * 6 + i));
    cut(ctx, polyPath([[Math.cos(a - 0.12) * r * 1.08, Math.sin(a - 0.12) * r * 1.08], [Math.cos(a) * len, Math.sin(a) * len], [Math.cos(a + 0.12) * r * 1.08, Math.sin(a + 0.12) * r * 1.08]]), i % 2 ? C.sunRay2 : C.sunRay, texture, 3);
  }
  ctx.restore();
  cut(ctx, ovalPath(x, y, r * amount, r * amount), C.sun, texture, 8);
  cut(ctx, ovalPath(x - r * 0.17, y - r * 0.2, r * 0.58 * amount, r * 0.55 * amount), C.sunHi, texture, 1);
}

function cloud(ctx, texture, x, y, s, color = '#A6AFB8') {
  ctx.save();
  ctx.translate(x, y);
  ctx.scale(s, s);
  const p = new Path2D();
  for (const [dx, dy, r] of [[-92, 18, 68], [-23, -24, 88], [60, -2, 73], [116, 22, 49]]) p.ellipse(dx, dy, r, r * 0.8, 0, 0, TAU);
  cut(ctx, p, color, texture, 8);
  ctx.restore();
}

function wide(ctx, texture, nest, t, mode) {
  screen(ctx, texture, '#D8E7D9');
  let start, end, cx, cy, z0, z1;
  if (mode === 2) { start = 28.48; end = 29.62; cx = 540; cy = 980; z0 = 1.68; z1 = 0.94; }
  else if (mode === 3) { start = 29.62; end = 31.15; cx = 540; cy = 1040; z0 = 1.0; z1 = 1.19; }
  else if (mode === 4) { start = 31.15; end = 32.99; cx = 540; cy = 930; z0 = 0.97; z1 = 1.22; }
  else { start = 38.98; end = 40.55; cx = 540; cy = 1050; z0 = 0.89; z1 = 1.08; }
  const u = prog(t, start, end);
  const cam = { x: cx + Math.sin(u * 2.2) * 55, y: cy - u * 58, zoom: lerp(z0, z1, eIO(u)) };
  let s;
  if (mode === 2) s = { brood: { U1: 1, U2: 1 }, traffic: 0.55, glow: { U1: 0.15 }, ring: { U1: prog(t, 28.98, 29.15) * 0.7 }, surfaceAnts: 0.3, sun: 0.5, fairClouds: 0.4 };
  else if (mode === 3) s = { brood: { U1: 1, U2: 1, M2: 0.7 }, traffic: 0.7, glow: { U1: 0.6, U2: 0.5 }, ring: { U1: 0.85, U2: prog(t, 30.08, 30.3) * 0.75 }, cool: 0.35, sun: 0.78, beam: 0.4, surfaceAnts: 0.35 };
  else if (mode === 4) {
    const cold = eOut(prog(t, 31.34, 31.75));
    const wet = eOut(prog(t, 32.06, 32.35));
    s = { brood: { U1: 1, U2: 1 }, traffic: 0.62, cold, rain: Math.max(0.3, cold), rainFall: wet, rainDark: 0.75, cool: wet * 0.45, surfaceAnts: 0.23, sun: 0.35 * (1 - cold) };
  } else {
    const water = 0.72 + 0.28 * eOut(prog(t, 38.98, 39.54));
    s = { brood: { U1: 1, U2: 1, M2: 1 }, traffic: 0.7, busy: { U1: 0.45 }, cold: 0.66, rain: 0.65, rainFall: 0.65, water, cool: 0.8, glow: { U1: 0.6, U2: 0.6 }, ring: { U1: 0.75, U2: 0.7 }, sun: 0.3, beam: 0.2 };
  }
  withCamera(ctx, cam, () => nest.draw(ctx, t, s));
}

function corridor(ctx, texture, t) {
  screen(ctx, texture, '#A87352');
  const u = prog(t, 32.99, 35.9);
  withCamera(ctx, { x: lerp(510, 630, u), y: lerp(950, 750, u), zoom: lerp(1.03, 1.23, u) }, () => {
    cut(ctx, bandPath(-500, 1700, 170, 2300, 8, 501), '#B77B56', texture, 8);
    cut(ctx, bandPath(-500, 1700, 1140, 2300, 9, 502), '#A16C50', texture, 8);
    cut(ctx, bandPath(-500, 1700, 1480, 2300, 9, 503), '#8B5A48', texture, 8);
    const p = new Path2D();
    p.moveTo(-200, 1320);
    p.bezierCurveTo(270, 1150, 430, 990, 1030, 560);
    ctx.save();
    ctx.lineCap = 'round';
    ctx.strokeStyle = '#6A453D'; ctx.lineWidth = 290; ctx.stroke(p);
    ctx.strokeStyle = '#4A3236'; ctx.lineWidth = 260; ctx.stroke(p);
    ctx.strokeStyle = '#614142'; ctx.lineWidth = 225; ctx.stroke(p);
    ctx.restore();
    chamber(ctx, texture, 930, 570, 275, 185, t, 0.24);
    dust(ctx, texture, t, 30, [20, 420, 1050, 700]);
    const k = eIO(prog(t, 33.8, 35.3));
    const antPositions = [
      { x: lerp(440, 820, k), y: lerp(1060, 650, k), scale: 0.34, carry: t >= 33.38 && t < 35.24 ? 'larva' : null },
      { x: lerp(70, 480, k), y: lerp(1250, 1015, k), scale: 0.29, carry: null },
      { x: lerp(-310, 85, k), y: lerp(1370, 1245, k), scale: 0.28, carry: null },
    ];
    antPositions.forEach((a, i) => {
      if (i === 2 && t < 33.8) return;
      placeAnt(ctx, texture, a.x, a.y, a.scale, {
        phase: walkPhase(k * 540, a.scale) + i * 2, walk: 1, carry: a.carry,
        antennae: [[0.08 * Math.sin(t * 9 + i), 0.08], [0.08 * Math.sin(t * 8 + i), 0.05]],
      }, { faceRight: true, rotation: -0.56 });
    });
    if (t >= 35.24) drawLarva(ctx, texture, 890, 690, 0.88, 0.22, Math.sin(t * 4));
    if (t >= 34.64) drawEgg(ctx, texture, 970, 715, 20, 0.25);
  });
}

function upper(ctx, texture, t) {
  screen(ctx, texture, '#D7E9E0');
  const u = prog(t, 35.9, 37.48);
  withCamera(ctx, { x: lerp(550, 570, u), y: lerp(850, 900, u), zoom: lerp(0.98, 1.19, u) }, () => {
    cut(ctx, bandPath(-500, 1700, 625, 2300, 8, 601), '#B97B57', texture, 8);
    cut(ctx, bandPath(-500, 1700, 1235, 2300, 8, 602), '#A36A4E', texture, 8);
    const mound = smoothPath([[190, 635], [250, 565], [390, 470], [550, 435], [710, 485], [855, 565], [910, 635], [190, 650]], true);
    cut(ctx, mound, '#BE855C', texture, 12);
    cut(ctx, ovalPath(520, 980, 466, 250), '#71463E', texture, 12);
    chamber(ctx, texture, 520, 950, 445, 225, t, eOut(prog(t, 37.02, 37.3)) * 0.55);
    const part = eOut(prog(t, 36.24, 36.75));
    cloud(ctx, texture, 280 - 370 * part + t * 12, 260, 0.78, '#AAB4BC');
    cloud(ctx, texture, 800 + 380 * part + t * 10, 300, 0.8, '#B7BEC4');
    sun(ctx, texture, 780, 280, 112, t, eOut(prog(t, 37.02, 37.23)));
    if (t >= 37.02) {
      ctx.save(); ctx.globalAlpha = 0.32 * eOut(prog(t, 37.02, 37.34));
      cut(ctx, polyPath([[690, 335], [860, 335], [870, 925], [420, 930]]), '#F6D889', texture, 0);
      ctx.restore();
    }
    brood(ctx, texture, t, 390, 1060, 0.82);
    nurse(ctx, texture, 790, 1060, 0.37, t, false, null, 0.12);
    for (let i = 0; i < 5; i += 1) tuft(ctx, texture, 110 + i * 195, 635, 50, i + 90, [C.grass, C.lime], 0.06 * Math.sin(t * 3 + i));
  });
}

export function createScene(config, timing) {
  const texture = makeFibres((config.seed ?? 1) | 0);
  const nest = createNest(texture, 37);
  const captions = createCaptions(timing.words, timing.caption_groups, { texture, centerY: config.caption_center_y ?? 1420, endTime: 40.55 });
  function drawWorld(ctx, t) {
    if (t < 28.48) nursery(ctx, texture, t, 1);
    else if (t < 29.62) wide(ctx, texture, nest, t, 2);
    else if (t < 31.15) wide(ctx, texture, nest, t, 3);
    else if (t < 32.99) wide(ctx, texture, nest, t, 4);
    else if (t < 35.9) corridor(ctx, texture, t);
    else if (t < 37.48) upper(ctx, texture, t);
    else if (t < 38.98) nursery(ctx, texture, t, 8);
    else wide(ctx, texture, nest, t, 9);
  }
  return {
    duration: config.duration_seconds,
    blurWindows: [[34.18, 34.5]],
    drawWorld,
    drawOverlay: captions,
    draw(ctx, t) { drawWorld(ctx, t); captions(ctx, t); },
  };
}
