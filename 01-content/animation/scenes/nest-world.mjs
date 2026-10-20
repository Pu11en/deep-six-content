// Fire-ant nest cutaway in cut-paper style C: mound, chambers, tunnels, ants, brood and weather.
// The segment code passes a state object for each frame; the world draws itself from that state.
// Illustrative only: no depths, temperatures or measured nest layout.
import {
  C, Path2D, clamp, lerp, eOut, eIO, eBack, rng, hash, pathOf, mix as lerpColor,
  cut, polyPath, smoothPath, ovalPath, capsulePath, bandPath, tornLine,
  placeAnt, walkPhase, tuft, blade, puff, drawBroodPile, createBroodPile,
} from './paper-kit.mjs';

const TAU = Math.PI * 2;
export const SURFACE = 760;

export const CHAMBERS = {
  M1: { x: 540, y: 612, rx: 62, ry: 26 },
  M2: { x: 425, y: 694, rx: 58, ry: 24 },
  M3: { x: 657, y: 700, rx: 60, ry: 24 },
  U1: { x: 262, y: 902, rx: 96, ry: 36 },
  U2: { x: 812, y: 952, rx: 96, ry: 36 },
  C1: { x: 372, y: 1232, rx: 116, ry: 42 },
  C2: { x: 772, y: 1432, rx: 112, ry: 42 },
  D1: { x: 292, y: 1802, rx: 122, ry: 46 },
  D2: { x: 772, y: 2062, rx: 126, ry: 48 },
  D3: { x: 440, y: 2424, rx: 118, ry: 45 },
};
export const UPPER = ['M1', 'M2', 'M3', 'U1', 'U2'];
export const DEEP = ['D1', 'D2', 'D3'];

const SPINE = [[540, 600], [532, 700], [545, 800], [555, 900], [540, 1000], [500, 1150], [540, 1300], [590, 1400],
  [560, 1550], [470, 1700], [430, 1760], [520, 1880], [620, 2000], [580, 2180], [500, 2320], [440, 2424]];
const BRANCHES = {
  M2: [[532, 694], [480, 694], [425, 694]],
  M3: [[534, 700], [600, 702], [657, 700]],
  U1: [[552, 870], [400, 890], [262, 902]],
  U2: [[555, 905], [690, 935], [812, 952]],
  C1: [[500, 1150], [440, 1200], [372, 1232]],
  C2: [[590, 1400], [690, 1420], [772, 1432]],
  D1: [[430, 1760], [360, 1790], [292, 1802]],
  D2: [[620, 2000], [700, 2040], [772, 2062]],
};
// Surface tunnels that open beside the mound (fire-ant mounds have no central opening).
const EXITS = [[[545, 800], [420, 818], [285, 806], [165, 766]], [[548, 820], [680, 832], [805, 808], [925, 766]]];

function moundPoints(seed) {
  const random = rng(seed);
  const pts = [];
  const n = 30;
  for (let i = 0; i <= n; i += 1) {
    const a = Math.PI + (i / n) * Math.PI;
    const bump = i === 0 || i === n ? 0 : (random() - 0.5) * 0.1;
    const lift = Math.pow(Math.abs(Math.sin(a)), 0.8);
    pts.push([540 + Math.cos(a) * 290 * (1 + bump * 0.3), SURFACE + 4 - lift * 238 * (1 + bump)]);
  }
  return pts;
}

export function createNest(texture, seed = 7) {
  const random = rng(seed * 131 + 9);
  const spine = pathOf(SPINE);
  const branches = Object.fromEntries(Object.entries(BRANCHES).map(([k, v]) => [k, pathOf(v)]));
  const exits = EXITS.map(pts => pathOf(pts));
  const dome = moundPoints(seed + 1);
  const moundShape = smoothPath([[230, SURFACE + 8], ...dome, [850, SURFACE + 8]], true);
  const moundOutline = pathOf(dome);
  const layers = [
    { path: bandPath(-900, 2000, SURFACE - 6, 3600, 5, 201), color: '#B57553' },
    { path: bandPath(-900, 2000, 1110, 3600, 9, 202), color: '#A66E50' },
    { path: bandPath(-900, 2000, 1580, 3600, 10, 203), color: '#93604A' },
    { path: bandPath(-900, 2000, 2150, 3600, 10, 204), color: '#7E5242' },
  ];
  const pebbles = Array.from({ length: 140 }, () => [-700 + random() * 2500, SURFACE + 40 + random() * 2100, 5 + random() * 15, random() * 3,
    ['#C98E66', '#9A6447', '#D9AE80', '#7F503B', '#B9805C'][Math.floor(random() * 5)]]);
  const roots = [
    [[150, SURFACE], [170, 860], [140, 960], [175, 1040]], [[170, 860], [230, 890], [250, 950]],
    [[930, SURFACE], [910, 870], [950, 990]], [[910, 870], [860, 905]],
  ];
  const grass = Array.from({ length: 34 }, (_, i) => ({ x: -620 + i * 70 + random() * 30, size: 60 + random() * 40, seed: i + 300 }));
  const piles = Object.fromEntries(Object.keys(CHAMBERS).map((k, i) => [k, createBroodPile(40 + i)]));
  const sparkles = Array.from({ length: 46 }, () => [-300 + random() * 1700, 1550 + random() * 1150, random() * 3, random()]);
  const rainDrops = Array.from({ length: 90 }, () => [random() * 1900 - 400, random(), 0.7 + random() * 0.6]);
  const puddles = [[160, 70], [330, 46], [900, 80], [1040, 52], [-120, 60]];
  const chamberPath = id => { const c = CHAMBERS[id]; return ovalPath(c.x, c.y, c.rx, c.ry); };
  const allChambers = new Path2D();
  const tunnelStroke = (ctx, color, width, dy = 0) => {
    ctx.save();
    ctx.translate(0, dy);
    ctx.strokeStyle = color;
    ctx.lineCap = 'round';
    ctx.lineJoin = 'round';
    const draw = (route, w) => {
      ctx.lineWidth = w;
      ctx.beginPath();
      route.points.forEach(([x, y], i) => (i ? ctx.lineTo(x, y) : ctx.moveTo(x, y)));
      ctx.stroke();
    };
    draw(spine, width);
    for (const b of Object.values(branches)) draw(b, width * 0.88);
    for (const e of exits) draw(e, width * 0.8);
    ctx.fillStyle = color;
    for (const id of Object.keys(CHAMBERS)) {
      const c = CHAMBERS[id];
      ctx.fill(ovalPath(c.x, c.y, c.rx + (width - 34) / 2, c.ry + (width - 34) / 2));
    }
    ctx.restore();
  };

  // Ants: traffic on the spine, nurses in chambers, walkers on the surface.
  const traffic = Array.from({ length: 14 }, (_, i) => ({ u0: i / 14 + random() * 0.03, speed: 95 + random() * 40, dir: i % 2 ? 1 : -1, seed: i }));
  const surfaceAnts = Array.from({ length: 14 }, (_, i) => ({ x0: -500 + i * 190 + random() * 60, speed: 70 + random() * 40, dir: i % 2 ? 1 : -1, scale: 0.15 + random() * 0.03 }));

  function antOnRoute(ctx, route, u, forward, scale, pose) {
    const [x, y] = route.at(clamp(u));
    const a = route.at(clamp(u + 0.004));
    const b = route.at(clamp(u - 0.004));
    let angle = Math.atan2(a[1] - b[1], a[0] - b[0]);
    if (!forward) angle += Math.PI;
    const faceRight = Math.cos(angle) > 0;
    const tilt = faceRight ? angle : angle - Math.PI;
    placeAnt(ctx, texture, x, y + 15, scale, pose, { faceRight, rotation: clamp(tilt, -0.75, 0.75) });
  }

  function drawSky(ctx, s, t) {
    const hot = s.heat ?? 0;
    const cold = s.cold ?? 0;
    const top = lerpColor(lerpColor('#CFE6E0', '#F2C567', hot), '#9AAAB8', cold);
    const low = lerpColor(lerpColor('#EAF3E6', '#F8E2A0', hot), '#C4CDD3', cold);
    const g = ctx.createLinearGradient(0, -900, 0, SURFACE);
    g.addColorStop(0, top);
    g.addColorStop(1, low);
    ctx.fillStyle = g;
    ctx.fillRect(-1200, -1800, 3600, SURFACE + 1800);
  }

  function drawSun(ctx, s, t) {
    const k = s.sun ?? 0;
    if (k <= 0.01) return;
    const x = s.sunX ?? 860;
    const y = s.sunY ?? 230;
    const r = (s.sunR ?? 120) * k;
    const pale = s.sunPale ?? 0;
    ctx.save();
    const glow = ctx.createRadialGradient(x, y, r * 0.6, x, y, r * 3.2);
    glow.addColorStop(0, `rgba(255,244,196,${0.6 * k})`);
    glow.addColorStop(1, 'rgba(255,244,196,0)');
    ctx.fillStyle = glow;
    ctx.fillRect(x - r * 3.4, y - r * 3.4, r * 6.8, r * 6.8);
    ctx.translate(x, y);
    ctx.rotate(t * 0.7);
    const rays = 14;
    for (let i = 0; i < rays; i += 1) {
      const a = i * TAU / rays;
      const len = (i % 2 ? 1.55 : 1.8) * r * (1 + 0.05 * Math.sin(t * 8 + i));
      cut(ctx, polyPath([[Math.cos(a - 0.13) * r * 1.08, Math.sin(a - 0.13) * r * 1.08], [Math.cos(a) * len, Math.sin(a) * len],
        [Math.cos(a + 0.13) * r * 1.08, Math.sin(a + 0.13) * r * 1.08]]), lerpColor(i % 2 ? C.sunRay2 : C.sunRay, '#F3E7B8', pale), texture, 4);
    }
    ctx.restore();
    cut(ctx, ovalPath(x, y, r, r), lerpColor(C.sun, '#F7EBC0', pale), texture, 8);
    cut(ctx, ovalPath(x - r * 0.15, y - r * 0.15, r * 0.68, r * 0.64, 0.3), lerpColor(C.sunHi, '#FBF3D8', pale), texture, 0);
  }

  function drawClouds(ctx, s, t) {
    const fair = s.fairClouds ?? 0;
    if (fair > 0.01) {
      // Placed so they cross the frame during the quiet-lawn shot.
      for (const [x0, y, sc, sp] of [[508, 300, 1.0, 26], [1494, 430, 0.75, 18], [1076, 540, 0.6, 22]]) {
        const x = ((x0 + t * sp + 600) % 1900) - 600;
        ctx.save();
        ctx.globalAlpha = fair;
        ctx.translate(x, y);
        ctx.scale(sc, sc);
        const path = new Path2D();
        for (const [ox, oy, r] of [[-95, 18, 62], [-30, -22, 82], [52, -6, 70], [110, 22, 50], [10, 30, 70]]) path.ellipse(ox, oy, r, r * 0.82, 0, 0, TAU);
        cut(ctx, path, C.white, texture, 7);
        ctx.restore();
      }
    }
    const k = s.rain ?? 0;
    const part = s.cloudsPart ?? 0;
    if (k <= 0.01) return;
    const color = lerpColor('#E6E9EC', '#8E99A6', s.rainDark ?? 0.6);
    const shapes = [[-60, 150, 1.3], [300, 110, 1.6], [700, 160, 1.4], [1050, 120, 1.3]];
    shapes.forEach(([x, y, sc], i) => {
      const side = x < 520 ? -1 : 1;
      const dx = side * part * 700 + Math.sin(t * 0.6 + i) * 12;
      const enter = eOut(clamp(k * 1.4 - i * 0.1));
      const yy = lerp(y - 520, y, enter);
      ctx.save();
      ctx.translate(x + dx, yy);
      ctx.scale(sc, sc);
      const path = new Path2D();
      for (const [ox, oy, r] of [[-95, 18, 62], [-30, -22, 82], [52, -6, 70], [110, 22, 50], [10, 30, 70]]) path.ellipse(ox, oy, r, r * 0.8, 0, 0, TAU);
      cut(ctx, path, color, texture, 8);
      ctx.restore();
    });
    const fall = s.rainFall ?? k;
    if (fall > 0.02) {
      ctx.save();
      ctx.strokeStyle = 'rgba(140,175,205,0.85)';
      ctx.lineWidth = 6;
      ctx.lineCap = 'round';
      for (const [x0, phase, sp] of rainDrops) {
        const cycle = (t * 1.6 * sp + phase) % 1;
        const y = lerp(260, SURFACE, cycle);
        const x = x0 - (y - 260) * 0.25;
        if ((x0 + 600) / 2100 > fall) continue;
        ctx.globalAlpha = fall;
        ctx.beginPath();
        ctx.moveTo(x, y);
        ctx.lineTo(x - 9, y + 38);
        ctx.stroke();
      }
      ctx.restore();
      for (const [x, w] of puddles) {
        const p = eOut(clamp(fall * 1.5 - 0.3));
        if (p > 0) cut(ctx, ovalPath(x, SURFACE + 2, w * p, 9 * p), 'rgba(120,165,200,0.85)', texture, 0);
      }
    }
  }

  function drawWind(ctx, s, t) {
    const k = s.wind ?? 0;
    if (k <= 0.01) return;
    ctx.save();
    ctx.strokeStyle = 'rgba(255,255,255,0.8)';
    ctx.lineWidth = 7;
    ctx.lineCap = 'round';
    for (let i = 0; i < 5; i += 1) {
      const x = ((t * 520 + i * 410) % 1900) - 500;
      const y = 300 + i * 85;
      ctx.globalAlpha = k * 0.8;
      ctx.beginPath();
      ctx.moveTo(x, y);
      ctx.bezierCurveTo(x + 90, y - 30, x + 160, y + 20, x + 210, y - 8);
      ctx.arc(x + 210, y - 32, 24, Math.PI / 2, -Math.PI * 0.9, true);
      ctx.stroke();
    }
    ctx.restore();
  }

  function drawMound(ctx, s, t) {
    const k = s.mound ?? 1;
    if (k <= 0.01) return;
    ctx.save();
    ctx.translate(540, SURFACE);
    ctx.scale(1, k);
    ctx.translate(-540, -SURFACE);
    const hot = s.heat ?? 0;
    cut(ctx, moundShape, lerpColor('#B97A56', '#C98B5E', hot * 0.5), texture, 12);
    ctx.save();
    ctx.clip(moundShape);
    cut(ctx, smoothPath([[600, 540], [720, 600], [800, 700], [840, 780], [620, 790], [650, 660]], true), 'rgba(120,70,45,0.28)', null, 0);
    cut(ctx, smoothPath([[330, 700], [400, 600], [500, 545], [560, 548], [440, 620], [370, 720]], true), 'rgba(235,190,140,0.35)', null, 0);
    ctx.restore();
    if ((s.moundCracks ?? 0) > 0.01) {
      ctx.save();
      ctx.strokeStyle = C.crack;
      ctx.lineCap = 'round';
      ctx.lineWidth = 6;
      const c = s.moundCracks;
      for (const [x0, y0, x1, y1] of [[420, 560, 455, 620], [600, 548, 575, 600], [700, 610, 740, 650], [340, 650, 380, 690]]) {
        ctx.beginPath();
        ctx.moveTo(x0, y0);
        ctx.lineTo(lerp(x0, x1, c), lerp(y0, y1, c));
        ctx.stroke();
      }
      ctx.restore();
    }
    ctx.restore();
  }

  function drawSurface(ctx, s, t) {
    const hot = s.heat ?? 0;
    const cold = s.cold ?? 0;
    const green = lerpColor(lerpColor(C.lime, '#D3B86D', hot), '#8FAE7A', cold * 0.6);
    const deep = lerpColor(lerpColor(C.grass, '#B39555', hot), '#6E8C66', cold * 0.6);
    // Lawn strip on both sides; under the mound the dome itself is the surface.
    const spans = (s.mound ?? 1) > 0.5 ? [[-900, 268], [812, 2000]] : [[-900, 2000]];
    for (const [a, b] of spans) {
      cut(ctx, bandPath(a, b, SURFACE - 20, SURFACE + 22, 4, 210), deep, texture, 5);
      cut(ctx, bandPath(a, b, SURFACE - 28, SURFACE + 2, 4, 211), green, texture, 5);
    }
    const sway = (s.wind ?? 0) * 0.35;
    for (const g of grass) {
      if (Math.abs(g.x - 540) < 300 && (s.mound ?? 1) > 0.5) continue;
      tuft(ctx, texture, g.x, SURFACE - 22, g.size, g.seed, [green, deep], 0.05 * Math.sin(t * 2.4 + g.x) + sway, hot * 0.9);
    }
  }

  function drawUnderground(ctx, s, t) {
    for (const layer of layers) cut(ctx, layer.path, layer.color, texture, 10);
    for (const [x, y, r, a, color] of pebbles) cut(ctx, ovalPath(x, y, r, r * 0.7, a), color, texture, 2);
    ctx.save();
    ctx.strokeStyle = '#E2C79C';
    ctx.lineCap = 'round';
    for (const r of roots) {
      ctx.lineWidth = 10;
      ctx.beginPath();
      r.forEach(([x, y], i) => (i ? ctx.lineTo(x, y) : ctx.moveTo(x, y)));
      ctx.stroke();
    }
    ctx.restore();
  }

  function drawTunnels(ctx, s, t) {
    const reveal = s.tunnelsDraw ?? 1;
    ctx.save();
    if ((s.mound ?? 1) < 0.5) {
      // No mound: nothing of the nest shows above the ground line.
      ctx.beginPath();
      ctx.rect(-900, SURFACE + 6, 3000, 3000);
      ctx.clip();
    }
    if (reveal < 1) {
      ctx.beginPath();
      ctx.rect(-900, -900, 3000, SURFACE - 120 + reveal * 2000 + 900);
      ctx.clip();
    }
    tunnelStroke(ctx, 'rgba(40,24,22,0.35)', 46, 6);
    tunnelStroke(ctx, C.tunnel, 36, 0);
    tunnelStroke(ctx, C.tunnelInner, 22, 5);
    ctx.restore();
  }

  function drawChamberFx(ctx, s, t) {
    for (const [id, k] of Object.entries(s.glow ?? {})) {
      if (k <= 0.01) continue;
      const c = CHAMBERS[id];
      const warm = s.glowColor?.[id] ?? 'warm';
      const rgb = warm === 'cool' ? '150,210,235' : '255,214,120';
      const g = ctx.createRadialGradient(c.x, c.y, 4, c.x, c.y, c.rx * 1.9);
      g.addColorStop(0, `rgba(${rgb},${0.75 * k})`);
      g.addColorStop(1, `rgba(${rgb},0)`);
      ctx.fillStyle = g;
      ctx.fillRect(c.x - c.rx * 2, c.y - c.rx * 2, c.rx * 4, c.rx * 4);
    }
  }

  function drawBrood(ctx, s, t) {
    for (const [id, amount] of Object.entries(s.brood ?? {})) {
      if (amount <= 0.01) continue;
      const c = CHAMBERS[id];
      drawBroodPile(ctx, texture, piles[id], c.x - 10, c.y + c.ry * 0.62, c.rx / 270, amount, t);
    }
  }

  function drawRings(ctx, s, t) {
    for (const [id, k] of Object.entries(s.ring ?? {})) {
      if (k <= 0.01) continue;
      const c = CHAMBERS[id];
      const pulse = 1 + 0.05 * Math.sin(t * 7);
      ctx.save();
      ctx.globalAlpha = clamp(k * 2);
      ctx.strokeStyle = 'rgba(30,27,34,0.3)';
      ctx.lineWidth = 16;
      ctx.beginPath();
      ctx.ellipse(c.x + 3, c.y + 6, c.rx * 1.32 * pulse * eBack(k, 2), c.ry * 1.9 * pulse * eBack(k, 2), 0, 0, TAU);
      ctx.stroke();
      ctx.strokeStyle = C.lime;
      ctx.lineWidth = 12;
      ctx.beginPath();
      ctx.ellipse(c.x, c.y, c.rx * 1.32 * pulse * eBack(k, 2), c.ry * 1.9 * pulse * eBack(k, 2), 0, 0, TAU);
      ctx.stroke();
      ctx.restore();
    }
  }

  function drawAnts(ctx, s, t) {
    const n = s.traffic ?? 0.6;
    const dir = s.flow ?? 0;
    traffic.forEach((ant, i) => {
      if (i / traffic.length >= n) return;
      const forward = dir === 0 ? ant.dir > 0 : dir > 0;
      const sign = forward ? 1 : -1;
      const speed = ant.speed * (s.speed ?? 1);
      const u = ((ant.u0 + sign * t * speed / spine.length) % 1 + 1) % 1;
      // Without a mound, nothing walks above the ground line.
      if ((s.mound ?? 1) < 0.5 && spine.at(u)[1] < SURFACE + 40) return;
      const carry = s.carry ? (i % 3 === 0 ? 'pupa' : 'larva') : null;
      antOnRoute(ctx, spine, u, !forward, 0.15,
        { phase: walkPhase(t * speed, 0.15) + ant.seed, walk: 1, carry, antennae: [[0.05 * Math.sin(t * 9 + i), 0], [0.05 * Math.sin(t * 8 + i), 0]] });
    });
    // Nurses tend brood in occupied chambers.
    for (const [id, amount] of Object.entries(s.brood ?? {})) {
      if (amount < 0.3) continue;
      const c = CHAMBERS[id];
      const k = hash(c.x);
      const x = c.x + Math.sin(t * 1.3 + k * 6) * c.rx * 0.35 + c.rx * 0.2;
      placeAnt(ctx, texture, x, c.y + c.ry * 0.62, 0.14,
        { phase: t * 8 + k * 9, walk: 0.5, head: 0.12 + 0.06 * Math.sin(t * 5 + k), antennae: [[-0.2 + 0.1 * Math.sin(t * 9), 0.1], [-0.15, 0.1]] },
        { faceRight: Math.cos(t * 1.3 + k * 6) > 0 });
    }
    for (const [id, k] of Object.entries(s.busy ?? {})) {
      if (k <= 0.01) continue;
      const c = CHAMBERS[id];
      for (let j = 0; j < 2; j += 1) {
        const phase = t * 1.8 + j * 3 + hash(c.y);
        const x = c.x + Math.sin(phase) * c.rx * 0.55;
        placeAnt(ctx, texture, x, c.y + c.ry * 0.62, 0.13 * eBack(clamp(k * 1.5 - j * 0.3), 2),
          { phase: walkPhase(Math.abs(Math.sin(phase)) * 200, 0.13) + j, walk: 1 }, { faceRight: Math.cos(phase) > 0 });
      }
    }
    const surface = s.surfaceAnts ?? 0;
    surfaceAnts.forEach((ant, i) => {
      if (i / surfaceAnts.length >= surface) return;
      const span = 2600;
      let x = ant.x0 + ant.dir * t * ant.speed;
      x = ((x + 900) % span + span) % span - 900;
      const onMound = Math.abs(x - 540) < 280 && (s.mound ?? 1) > 0.5;
      let y = SURFACE - 22;
      let rotation = 0;
      if (onMound) {
        const u = clamp((x - 250) / 580);
        const [mx, my, ang] = moundOutline.at(u);
        y = my;
        rotation = ang;
      }
      const size = ant.scale * (s.surfaceScale ?? 1);
      placeAnt(ctx, texture, x, y, size, { phase: walkPhase(t * ant.speed, size), walk: 1, antennae: [[0.06 * Math.sin(t * 9 + i), 0], [0.06 * Math.sin(t * 8 + i), 0]] },
        { faceRight: ant.dir > 0, rotation });
    });
  }

  function drawWeatherUnder(ctx, s, t) {
    const heat = s.heatSoil ?? 0;
    if (heat > 0.01) {
      // Only the mound and the top soil warm up; the sky keeps its own colour.
      ctx.save();
      const zone = new Path2D(moundShape);
      zone.rect(-900, SURFACE - 8, 3000, 700);
      ctx.clip(zone);
      const g = ctx.createLinearGradient(0, 520, 0, 1250);
      g.addColorStop(0, `rgba(240,120,50,${0.42 * heat})`);
      g.addColorStop(1, 'rgba(240,120,50,0)');
      ctx.fillStyle = g;
      ctx.fillRect(-900, 480, 3000, 770);
      ctx.restore();
    }
    const cool = s.cool ?? 0;
    if (cool > 0.01) {
      const g = ctx.createLinearGradient(0, 1350, 0, 2200);
      g.addColorStop(0, 'rgba(110,190,210,0)');
      g.addColorStop(1, `rgba(110,190,210,${0.42 * cool})`);
      ctx.fillStyle = g;
      ctx.fillRect(-900, 1350, 3000, 2400);
      ctx.save();
      const moist = s.moist ?? cool;
      for (const [x, y, ph, sz] of sparkles) {
        const tw = 0.5 + 0.5 * Math.sin(t * 4 + ph * 3);
        ctx.globalAlpha = moist * tw;
        ctx.fillStyle = sz > 0.6 ? '#E8FBFF' : '#9FD8E8';
        const r = 5 + sz * 7;
        ctx.beginPath();
        ctx.moveTo(x, y - r * 1.6);
        ctx.lineTo(x + r * 0.5, y);
        ctx.lineTo(x, y + r * 1.6);
        ctx.lineTo(x - r * 0.5, y);
        ctx.closePath();
        ctx.fill();
      }
      ctx.restore();
    }
    const dim = s.dimUnder ?? 0;
    if (dim > 0.01) {
      ctx.fillStyle = `rgba(30,20,25,${dim})`;
      ctx.fillRect(-900, SURFACE + 16, 3000, 3000);
    }
    const water = s.water ?? 0;
    if (water > 0.005) {
      const level = lerp(2850, 1500, water);
      const pts = tornLine(-900, 2000, level, 0, 5, 40).map(([x], i) => [x, level + 10 * Math.sin(x * 0.012 + t * 3)]);
      const path = polyPath([...pts, [2000, 3600], [-900, 3600]]);
      ctx.save();
      ctx.globalAlpha = 0.55;
      cut(ctx, path, '#5E9CC7', null, 0);
      ctx.restore();
      ctx.save();
      ctx.strokeStyle = 'rgba(210,235,250,0.9)';
      ctx.lineWidth = 8;
      ctx.beginPath();
      pts.forEach(([x, y], i) => (i ? ctx.lineTo(x, y) : ctx.moveTo(x, y)));
      ctx.stroke();
      for (let i = 0; i < 14; i += 1) {
        const by = level + 60 + ((t * 140 + i * 97) % 700);
        const bx = 200 + (i * 173) % 700 + 10 * Math.sin(t * 5 + i);
        ctx.globalAlpha = 0.7;
        ctx.beginPath();
        ctx.arc(bx, by, 6 + (i % 3) * 3, 0, TAU);
        ctx.stroke();
      }
      ctx.restore();
    }
  }

  function drawHeatAbove(ctx, s, t) {
    const heat = s.heat ?? 0;
    if (heat <= 0.05) return;
    ctx.save();
    ctx.strokeStyle = 'rgba(255,250,232,0.55)';
    ctx.lineWidth = 7;
    ctx.lineCap = 'round';
    for (let i = 0; i < 7; i += 1) {
      const x0 = -40 + i * 190;
      ctx.globalAlpha = heat * 0.75;
      ctx.beginPath();
      for (let k = 0; k <= 14; k += 1) {
        const y = SURFACE - 40 - k * 24 - ((t * 220 + i * 60) % 80);
        const x = x0 + 11 * Math.sin(k * 0.8 + t * 11 + i);
        if (k === 0) ctx.moveTo(x, y); else ctx.lineTo(x, y);
      }
      ctx.stroke();
    }
    ctx.restore();
  }

  function drawBeam(ctx, s, t) {
    const k = s.beam ?? 0;
    if (k <= 0.01) return;
    const x = s.sunX ?? 860;
    const y = s.sunY ?? 230;
    ctx.save();
    ctx.globalAlpha = 0.38 * k;
    const g = ctx.createLinearGradient(x, y, 540, 620);
    g.addColorStop(0, 'rgba(255,240,170,1)');
    g.addColorStop(1, 'rgba(255,240,170,0.2)');
    ctx.fillStyle = g;
    ctx.beginPath();
    ctx.moveTo(x - 40, y);
    ctx.lineTo(x + 40, y);
    ctx.lineTo(760, 700);
    ctx.lineTo(330, 680);
    ctx.closePath();
    ctx.fill();
    ctx.restore();
  }

  function drawFrame(ctx, s, t) {
    const f = s.frame;
    if (!f || f.k <= 0.01) return;
    const k = eBack(clamp(f.k), 2);
    const w = f.w * k;
    const h = f.h * k;
    // Built by hand: Path2D.addPath joins pieces in this canvas library.
    const frame = new Path2D();
    frame.rect(f.x - w / 2 - 22, f.y - h / 2 - 22, w + 44, h + 44);
    frame.rect(f.x - w / 2, f.y - h / 2, w, h);
    ctx.save();
    ctx.translate(f.x, f.y);
    ctx.rotate(f.tilt ?? -0.03);
    ctx.translate(-f.x, -f.y);
    ctx.shadowColor = 'rgba(30,20,25,0.35)';
    ctx.shadowBlur = 8;
    ctx.shadowOffsetY = 8;
    ctx.fillStyle = C.lime;
    ctx.fill(frame, 'evenodd');
    ctx.restore();
  }

  function drawCover(ctx, s, t) {
    const k = s.cover ?? 0;
    if (k <= 0.01) return;
    const edge = lerp(-420, 1600, eIO(k));
    const pts = tornLine(SURFACE + 18, 3600, 0, 0, 9, 40).map(([y]) => [edge + 18 * Math.sin(y * 0.03), y]);
    const path = polyPath([[-1000, SURFACE + 18], ...pts.map(([x, y]) => [x, y]), [-1000, 3600]]);
    cut(ctx, path, '#A66E50', texture, 16, { shadow: 'rgba(30,20,25,0.4)' });
    ctx.save();
    ctx.clip(path);
    for (const [x, y, r, a, color] of pebbles) cut(ctx, ovalPath(x, y, r, r * 0.7, a), color, texture, 2);
    ctx.restore();
  }

  return {
    chambers: CHAMBERS,
    spine,
    moundOutline,
    draw(ctx, t, s = {}) {
      drawSky(ctx, s, t);
      drawSun(ctx, s, t);
      drawClouds(ctx, s, t);
      drawWind(ctx, s, t);
      drawBeam(ctx, s, t);
      drawHeatAbove(ctx, s, t);
      drawUnderground(ctx, s, t);
      drawMound(ctx, s, t);
      drawSurface(ctx, s, t);
      drawTunnels(ctx, s, t);
      drawChamberFx(ctx, s, t);
      drawBrood(ctx, s, t);
      drawAnts(ctx, s, t);
      drawWeatherUnder(ctx, s, t);
      drawRings(ctx, s, t);
      drawFrame(ctx, s, t);
      drawCover(ctx, s, t);
      if (s.extra) s.extra(ctx, t);
    },
  };
}
