// Episode D6-6c917b49743b, hook (0.0-8.8 s of the approved Tyler narration).
// Shot plan: episodes/D6-6c917b49743b/hook/shot-list.json. Word times: episodes/D6-6c917b49743b/hook/words.json.
// Style C cut-paper storybook. Every draw is a pure function of time.
import {
  W, H, C, Path2D, createCanvas, clamp, lerp, eOut, eIn, eIO, eBack, noise1, rng, hash, pathOf, lerpColor,
  prog, zoomTo, wobble, shake, makeFibres, cut, polyPath, smoothPath, ovalPath, capsulePath, tornLine, bandPath,
  withCamera, placeAnt, walkPhase, blade, tuft, puff, impactStar, createCaptions, ANT_FOOT_Y,
} from './paper-kit.mjs';

const TAU = Math.PI * 2;

// ------------------------------------------------------------------ shared pieces
function fillScreen(ctx, color, texture) {
  ctx.save();
  ctx.setTransform(1, 0, 0, 1, 0, 0);
  cut(ctx, polyPath([[0, 0], [W, 0], [W, H], [0, H]]), color, texture, 0, { grain: 0.8 });
  ctx.restore();
}

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

function cloud(ctx, texture, x, y, s, alpha = 1) {
  if (s <= 0.02 || alpha <= 0.01) return;
  ctx.save();
  ctx.globalAlpha *= alpha;
  ctx.translate(x, y);
  ctx.scale(s, s);
  const path = new Path2D();
  for (const [ox, oy, r] of [[-95, 18, 62], [-30, -22, 82], [52, -6, 70], [110, 22, 50], [10, 30, 70]]) {
    path.ellipse(ox, oy, r, r * 0.82, 0, 0, TAU);
  }
  cut(ctx, path, C.white, texture, 7);
  ctx.restore();
}

// Underground tunnels and the ants that use them. Shared by the magnifier and the final reveal.
function createTunnels(texture, routes, chambers, ants, width) {
  const paths = routes.map(points => pathOf(points));
  const paint = (ctx, color, w, dy) => {
    ctx.save();
    ctx.translate(0, dy);
    ctx.strokeStyle = color;
    ctx.fillStyle = color;
    ctx.lineWidth = w;
    ctx.lineCap = 'round';
    ctx.lineJoin = 'round';
    for (const route of paths) {
      ctx.beginPath();
      route.points.forEach(([x, y], i) => (i ? ctx.lineTo(x, y) : ctx.moveTo(x, y)));
      ctx.stroke();
    }
    for (const [x, y, rx, ry] of chambers) ctx.fill(ovalPath(x, y, rx - (width - w) / 2, ry - (width - w) / 2));
    ctx.restore();
  };
  return {
    draw(ctx, t) {
      paint(ctx, 'rgba(40,24,22,0.35)', width + 10, 6);
      paint(ctx, C.tunnel, width, 0);
      paint(ctx, C.tunnelInner, width * 0.62, width * 0.14);
      for (const ant of ants) {
        const route = paths[ant.route];
        let u;
        if (ant.pace) {
          u = ant.u0 + ant.range * 0.5 * (1 - Math.cos((t * ant.pace + ant.offset) * TAU));
        } else {
          u = ((ant.u0 + t * ant.speed / route.length) % 1 + 1) % 1;
        }
        const ahead = clamp(u + 0.01, 0, 1);
        const behind = clamp(u - 0.01, 0, 1);
        const [x, y] = route.at(u);
        const a = route.at(ahead);
        const b = route.at(behind);
        let angle = Math.atan2(a[1] - b[1], a[0] - b[0]);
        const movingRight = ant.pace ? Math.sin((t * ant.pace + ant.offset) * TAU) > 0 : Math.cos(angle) > 0;
        const direction = ant.pace ? (movingRight ? 0 : Math.PI) : angle;
        const faceRight = Math.cos(direction) > 0;
        const tilt = faceRight ? direction : direction - Math.PI;
        placeAnt(ctx, texture, x, y + width * 0.3, ant.scale,
          { phase: t * 17 + ant.offset * 5, walk: 1, antennae: [[0.05 * Math.sin(t * 9 + ant.offset), 0], [0.05 * Math.sin(t * 8), 0]] },
          { faceRight, rotation: clamp(tilt, -0.7, 0.7) });
      }
    },
  };
}

// ------------------------------------------------------------------ S1: A fire ant colony (0.00-1.14)
function setupCrowd(texture) {
  const lanes = [
    { y: 640, color: '#EBDDBE', scale: 0.2, count: 9, speed: 52, seed: 11, tuftColors: ['#C2DD86', '#B0D06E'] },
    { y: 900, color: '#E3C99C', scale: 0.26, count: 8, speed: 68, seed: 12, tuftColors: ['#A9D554', '#93BD5C'] },
    { y: 1160, color: '#D3A877', scale: 0.34, count: 6, speed: 92, seed: 13, tuftColors: ['#93BD5C', '#789251'] },
    { y: 1440, color: '#BF8A5E', scale: 0.43, count: 5, speed: 118, seed: 14, tuftColors: ['#789251', '#5E7A3C'] },
  ];
  const span = 2000;
  for (const lane of lanes) {
    const random = rng(lane.seed);
    lane.band = bandPath(-900, 2000, lane.y, 3400, 4, lane.seed);
    lane.ants = Array.from({ length: lane.count }, (_, k) => ({
      x0: -400 + k * span / lane.count + (random() - 0.5) * 60,
      phase: random() * TAU,
    }));
    lane.tufts = [];
    for (let x = -880 + random() * 80; x < 1980; x += 120 + random() * 160) {
      lane.tufts.push({ x, size: lane.scale * (190 + random() * 120), seed: Math.floor(random() * 1000) });
    }
    lane.pebbles = Array.from({ length: 26 }, () => [
      -880 + random() * 2860, lane.y + 40 + random() * 200, (4 + random() * 10) * lane.scale * 3, random() * 3,
    ]);
  }
  const hero = lanes[2];
  hero.ants[0].x0 = 700;
  hero.ants[0].phase = 0;
  for (let k = 1; k < hero.count; k += 1) hero.ants[k].x0 = 700 + k * span / hero.count;
  for (const lane of [lanes[1], lanes[3]]) {
    for (const ant of lane.ants) {
      const x = ant.x0 - lane.speed * 0.36;
      if (Math.abs(x - heroX(0.36)) < 330) ant.x0 += x < heroX(0.36) ? -360 : 360;
    }
  }
  const hills = [
    smoothPath([[-900, 700], [-700, 560], [-420, 600], [-150, 520], [120, 585], [420, 500], [760, 570], [1040, 510], [1350, 580], [1700, 530], [2000, 600], [2000, 760], [-900, 760]], true),
    smoothPath([[-900, 720], [-600, 620], [-260, 650], [80, 600], [380, 660], [700, 600], [980, 650], [1300, 610], [1650, 650], [2000, 620], [2000, 780], [-900, 780]], true),
  ];
  const front = { band: bandPath(-900, 2000, 1735, 3400, 5, 15), tufts: [] };
  const random = rng(77);
  for (let x = -880; x < 1980; x += 90 + random() * 120) front.tufts.push({ x, size: 160 + random() * 110, seed: Math.floor(random() * 1000) });
  return { lanes, hills, front, span };
}

const heroX = t => 700 - 92 * t;

function crowdCamera(t) {
  const startX = heroX(0.72) - 10;
  if (t <= 0.72) return { x: heroX(t) - 10, y: 1104, zoom: lerp(3.95, 3.75, t / 0.72) };
  const k = eOut(prog(t, 0.72, 1.06));
  const drift = Math.max(0, t - 1.06);
  return { x: lerp(startX, 560, k), y: lerp(1104, 1150, k), zoom: zoomTo(3.75, 0.9, k) * (1 - drift * 0.03) };
}

function drawCrowd(ctx, texture, world, t) {
  fillScreen(ctx, C.paper, texture);
  withCamera(ctx, crowdCamera(t), () => {
    cloud(ctx, texture, 150 + t * 14, 300, 0.9);
    cloud(ctx, texture, 900 + t * 10, 220, 0.7);
    cut(ctx, world.hills[0], '#D7E6AE', texture, 4);
    cut(ctx, world.hills[1], '#C5DB92', texture, 5);
    world.lanes.forEach((lane, li) => {
      cut(ctx, lane.band, lane.color, texture, 9);
      for (const [x, y, r, a] of lane.pebbles) cut(ctx, ovalPath(x, y, r, r * 0.7, a), '#00000014', null, 0);
      for (const tf of lane.tufts) {
        tuft(ctx, texture, tf.x, lane.y + 3, tf.size, tf.seed, lane.tuftColors, 0.05 * Math.sin(t * 2.6 + tf.x * 0.01));
      }
      for (const [k, ant] of lane.ants.entries()) {
        let x = ant.x0 - lane.speed * t;
        x = ((x + 900) % world.span + world.span) % world.span - 900;
        const isHero = li === 2 && k === 0;
        let pose = { phase: walkPhase(lane.speed * t, lane.scale) + ant.phase, walk: 1 };
        if (isHero) {
          const flick = Math.sin(Math.PI * prog(t, 0.2, 0.46));
          const chomp = Math.sin(Math.PI * prog(t, 0.5, 0.68));
          pose = {
            ...pose,
            mand: chomp,
            antennae: [[-0.34 * flick + 0.05 * Math.sin(t * 11), 0.22 * flick], [-0.28 * flick + 0.05 * Math.sin(t * 9 + 1), 0.18 * flick]],
            head: -0.06 * chomp,
          };
        } else {
          pose.antennae = [[0.06 * Math.sin(t * 7 + k), 0], [0.06 * Math.sin(t * 6 + k * 2), 0]];
        }
        placeAnt(ctx, texture, x, lane.y, lane.scale, pose);
      }
    });
    cut(ctx, world.front.band, '#A06C49', texture, 12);
    for (const tf of world.front.tufts) tuft(ctx, texture, tf.x, 1738, tf.size, tf.seed, ['#789251', '#5E7A3C', '#6B8A46'], 0.06 * Math.sin(t * 3 + tf.x));
  });
}

// ------------------------------------------------------------------ S2 + S3: the yard (1.14-4.19)
const MOUND = { x: 520, base: 1065, width: 560, height: 265 };
const LENS = { x: 515, y: 1170, r: 238 };

function setupYard(texture) {
  const random = rng(404);
  const dome = domePoints(MOUND.x, MOUND.base, MOUND.width, MOUND.height, 9);
  const flare = [[MOUND.x - MOUND.width / 2 - 40, MOUND.base + 6], ...dome, [MOUND.x + MOUND.width / 2 + 40, MOUND.base + 6]];
  const moundPath = smoothPath([...flare, [MOUND.x, MOUND.base + 12]], true);
  const sx = MOUND.width / 480;
  const sy = MOUND.height / 230;
  const shadowPath = smoothPath([
    [30, -0.98 * 230], [150, -0.75 * 230], [236, -40], [270, 6], [60, 10], [90, -90],
  ].map(([x, y]) => [MOUND.x + x * sx, MOUND.base + y * sy]), true);
  const highlightPath = smoothPath([
    [-190, -60], [-120, -170], [-20, -212], [40, -200], [-60, -150], [-150, -40],
  ].map(([x, y]) => [MOUND.x + x * sx, MOUND.base + y * sy]), true);
  const crumbs = [];
  while (crumbs.length < 34) {
    const x = MOUND.x + (random() - 0.5) * MOUND.width * 0.92;
    const y = MOUND.base - random() * MOUND.height;
    const nx = (x - MOUND.x) / (MOUND.width / 2);
    const ny = (MOUND.base - y) / MOUND.height;
    if (nx * nx + ny * ny < 0.86) crumbs.push([x, y, 7 + random() * 11, random() * 3, ['#D9AE80', '#A86F4E', '#8E5A3F', '#C88B60'][crumbs.length % 4]]);
  }
  const outline = pathOf(dome);
  const fencePickets = [];
  for (let x = -40; x < 690; x += 58) fencePickets.push(polyPath([[x, 905], [x, 790], [x + 23, 762], [x + 46, 790], [x + 46, 905]]));
  const bushes = Array.from({ length: 16 }, (_, i) => [-60 + i * 78 + (random() - 0.5) * 30, 860 + (random() - 0.5) * 30, 62 + random() * 48, i % 2 ? '#7DA650' : '#8DB55A']);
  const lawnStripes = [];
  let y = 990;
  for (let i = 0; i < 9; i += 1) {
    const h = 26 * Math.pow(1.33, i);
    if (i % 2 === 0) lawnStripes.push(bandPath(-200, 1300, y, y + h, 3, 30 + i));
    y += h;
  }
  const lawnTufts = Array.from({ length: 22 }, (_, i) => ({ x: -40 + i * 54 + random() * 30, size: 70 + random() * 40, seed: i + 3 }));
  const frontTufts = Array.from({ length: 13 }, (_, i) => ({ x: -60 + i * 95 + random() * 40, size: 210 + random() * 120, seed: i + 50 }));
  const nearSpot = Array.from({ length: 7 }, (_, i) => ({ x: MOUND.x - 270 + i * 90 + random() * 20, size: 80 + random() * 30, seed: i + 90 }));
  const up = MOUND.base - 1150;
  const underground = createTunnels(texture, [
    [[515, 1150], [500, 1205], [530, 1262], [505, 1330], [450, 1385], [395, 1430]],
    [[530, 1262], [600, 1290], [655, 1350], [690, 1420]],
    [[500, 1205], [430, 1225], [372, 1262]],
  ].map(route => route.map(([x, y]) => [x, y + up])), [[395, 1440 + up, 92, 38], [690, 1430 + up, 84, 36], [365, 1268 + up, 58, 28]], [
    { route: 0, u0: 0.1, speed: 70, scale: 0.12, offset: 0.1 },
    { route: 0, u0: 0.6, speed: 60, scale: 0.12, offset: 0.5 },
    { route: 1, u0: 0.2, speed: 64, scale: 0.12, offset: 0.3 },
    { route: 2, u0: 0.3, pace: 0.8, range: 0.5, scale: 0.11, offset: 0.2 },
    { route: 1, u0: 0.75, pace: 0.6, range: 0.22, scale: 0.12, offset: 0.7 },
  ], 36);
  const moundAnts = [0.24, 0.5, 0.76].map((u, i) => ({ u, offset: i * 1.7 }));
  return { dome, moundPath, shadowPath, highlightPath, crumbs, outline, fencePickets, bushes, lawnStripes, lawnTufts, frontTufts, nearSpot, underground, moundAnts };
}

function drawHouse(ctx, texture) {
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

function moundScale(t) {
  if (t < 1.22) return [1, 0];
  if (t < 1.74) return [1, eBack(prog(t, 1.22, 1.46), 2.2)];
  if (t < 1.8) { const k = eOut(prog(t, 1.74, 1.8)); return [1 - 0.06 * k, 1 + 0.1 * k]; }
  const k = eIn(prog(t, 1.8, 1.96));
  return [lerp(0.94, 1.28, k), lerp(1.1, 0, k)];
}

function yardCamera(t) {
  if (t < 2.38) {
    const k = eIO(prog(t, 1.14, 2.38));
    return { x: 540, y: lerp(990, 1010, k), zoom: lerp(1, 1.05, k) };
  }
  const k = eIO(prog(t, 2.38, 4.19));
  return { x: lerp(540, 520, k), y: lerp(1010, 1050, k), zoom: lerp(1.05, 1.17, k) };
}

function lensPose(t) {
  const k = prog(t, 2.8, 3.2);
  const e = eBack(k, 1.25);
  const p0 = [1420, 820];
  const p1 = [1060, 1560];
  const p2 = [LENS.x, LENS.y];
  const u = e;
  const x = (1 - u) * (1 - u) * p0[0] + 2 * (1 - u) * u * p1[0] + u * u * p2[0];
  const y = (1 - u) * (1 - u) * p0[1] + 2 * (1 - u) * u * p1[1] + u * u * p2[1];
  const idle = Math.max(0, t - 3.2);
  return { x: x + 4 * Math.sin(idle * 4.2), y: y + 6 * Math.sin(idle * 5.1), angle: lerp(0.75, -0.16, eOut(k)) + 0.025 * Math.sin(idle * 3.3), visible: t >= 2.8 };
}

function drawYard(ctx, texture, yard, t) {
  fillScreen(ctx, C.sky, texture);
  withCamera(ctx, yardCamera(t), () => {
    cloud(ctx, texture, 190 + t * 18, 330, 1.0);
    cloud(ctx, texture, 820 + t * 12, 480, 0.7);
    for (const [x, y, r, color] of yard.bushes) cut(ctx, ovalPath(x, y, r, r * 0.85), color, texture, 6);
    drawHouse(ctx, texture);
    for (const picket of yard.fencePickets) cut(ctx, picket, C.paper, texture, 6);
    cut(ctx, polyPath([[-40, 812], [700, 806], [700, 826], [-40, 832]]), C.cream, texture, 4);
    cut(ctx, polyPath([[-40, 868], [700, 864], [700, 884], [-40, 888]]), C.cream, texture, 4);
    cut(ctx, bandPath(-300, 1400, 902, 2600, 4, 21), C.grassMid, texture, 8);
    cut(ctx, bandPath(-300, 1400, 952, 2600, 5, 22), C.lime, texture, 9);
    for (const stripe of yard.lawnStripes) cut(ctx, stripe, '#A0CB4C', null, 0);
    for (const tf of yard.lawnTufts) tuft(ctx, texture, tf.x, 955, tf.size, tf.seed, ['#93BD5C', '#7FA84E'], 0.05 * Math.sin(t * 2.4 + tf.x * 0.02));

    // The mound: pops up on "doesn't", squashes into the lawn on "always".
    const [sx, sy] = moundScale(t);
    if (sy > 0.01) {
      ctx.save();
      ctx.translate(MOUND.x, MOUND.base);
      ctx.scale(sx, sy);
      ctx.translate(-MOUND.x, -MOUND.base);
      cut(ctx, yard.moundPath, '#B57553', texture, 10);
      ctx.save();
      ctx.clip(yard.moundPath);
      cut(ctx, yard.shadowPath, '#94603F', texture, 0);
      cut(ctx, yard.highlightPath, '#CD966A', texture, 0);
      for (const [x, y, r, a, color] of yard.crumbs) cut(ctx, ovalPath(x, y, r, r * 0.72, a), color, texture, 2);
      ctx.restore();
      for (const ant of yard.moundAnts) {
        const [x, y, angle] = yard.outline.at(ant.u + 0.03 * Math.sin(t * 2 + ant.offset));
        placeAnt(ctx, texture, x, y + 2, 0.12, { phase: t * 18 + ant.offset, walk: 1 }, { rotation: angle, faceRight: false });
      }
      ctx.restore();
    }
    // Dust puff where the mound went.
    const dust = prog(t, 1.9, 2.36);
    if (dust > 0 && dust < 1) {
      for (let i = 0; i < 11; i += 1) {
        const side = (i / 10 - 0.5) * 2;
        const r = (26 + 30 * hash(i)) * (0.6 + eOut(dust));
        puff(ctx, texture, MOUND.x + side * (120 + 190 * eOut(dust)), MOUND.base - 20 - 70 * eOut(dust) * (1 - Math.abs(side) * 0.5) - 30 * hash(i + 3),
          r, '#D9B88C', 1 - dust);
      }
    }
    // Grass springs back over the empty spot on "have".
    for (const tf of yard.nearSpot) {
      const spring = t < 1.96 ? 0 : 0.3 * wobble(t, 1.96, 2.6, 4.5);
      if (t >= 1.96) tuft(ctx, texture, tf.x, MOUND.base + 4, tf.size * eBack(prog(t, 1.96, 2.2), 2), tf.seed, ['#93BD5C', '#7FA84E', '#A9D554'], spring);
    }

    for (const tf of yard.frontTufts) tuft(ctx, texture, tf.x, 1760, tf.size, tf.seed, ['#789251', '#5E7A3C', '#6B8A46'], 0.05 * Math.sin(t * 2 + tf.x));
    const lens = lensPose(t);
    if (lens.visible) {
      // X-ray view: the colony is still there under the flat lawn.
      ctx.save();
      const glass = ovalPath(lens.x, lens.y, LENS.r, LENS.r);
      ctx.clip(glass);
      ctx.fillStyle = 'rgba(255,255,255,0.10)';
      ctx.fill(glass);
      ctx.beginPath();
      ctx.rect(-400, MOUND.base, 2000, 1200);
      ctx.clip();
      cut(ctx, polyPath([[-400, MOUND.base], [1600, MOUND.base], [1600, 2600], [-400, 2600]]), '#A06A4C', texture, 0);
      for (let i = 0; i < 4; i += 1) {
        cut(ctx, bandPath(-400, 1600, MOUND.base + 70 + i * 95, MOUND.base + 80 + i * 95, 6, 60 + i), i % 2 ? '#8E5B42' : '#B07A58', null, 0);
      }
      yard.underground.draw(ctx, t);
      cut(ctx, bandPath(-400, 1600, MOUND.base - 6, MOUND.base + 14, 3, 61), C.lime, texture, 3);
      ctx.restore();
    }
    // Dashed outline of the missing mound.
    const draw = eIO(prog(t, 2.56, 2.84));
    if (draw > 0) {
      const pts = yard.outline.slice(draw);
      ctx.save();
      ctx.setLineDash([30, 20]);
      ctx.lineCap = 'round';
      ctx.lineWidth = 11;
      ctx.strokeStyle = 'rgba(30,27,34,0.25)';
      ctx.beginPath();
      pts.forEach(([x, y], i) => (i ? ctx.lineTo(x + 3, y + 6) : ctx.moveTo(x + 3, y + 6)));
      ctx.stroke();
      ctx.strokeStyle = C.purple;
      ctx.beginPath();
      pts.forEach(([x, y], i) => (i ? ctx.lineTo(x, y) : ctx.moveTo(x, y)));
      ctx.stroke();
      ctx.restore();
    }
    if (lens.visible) drawMagnifier(ctx, texture, lens, t);
  });
}

function drawMagnifier(ctx, texture, lens, t) {
  ctx.save();
  ctx.translate(lens.x, lens.y);
  ctx.rotate(lens.angle);
  const r = LENS.r;
  // Handle first, then the rim over it.
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
  // Glare, and a glint sweep on "see".
  ctx.save();
  ctx.beginPath();
  ctx.ellipse(0, 0, r, r, 0, 0, TAU);
  ctx.clip();
  ctx.strokeStyle = 'rgba(255,255,255,0.55)';
  ctx.lineWidth = 14;
  ctx.beginPath();
  ctx.arc(0, 0, r - 34, Math.PI * 1.08, Math.PI * 1.42);
  ctx.stroke();
  const glint = prog(t, 3.13, 3.42);
  if (glint > 0 && glint < 1) {
    ctx.rotate(-0.7);
    ctx.fillStyle = 'rgba(255,255,255,0.45)';
    ctx.fillRect(lerp(-r * 1.6, r * 1.6, eIO(glint)) - 40, -r * 1.5, 80, r * 3);
  }
  ctx.restore();
  ctx.restore();
}

// ------------------------------------------------------------------ S4: In a drought (4.19-4.98)
function setupDrought() {
  const random = rng(808);
  const back = Array.from({ length: 30 }, (_, i) => ({ x: -40 + i * 40 + random() * 20, h: 120 + random() * 90, w: 36 + random() * 12, lean: (random() - 0.5) * 0.4, c: random() }));
  const front = Array.from({ length: 22 }, (_, i) => ({ x: -50 + i * 55 + random() * 25, h: 190 + random() * 130, w: 50 + random() * 18, lean: (random() - 0.5) * 0.45, c: random() }));
  return { back, front };
}

function drawDrought(ctx, texture, drought, t) {
  const sky = ctx.createLinearGradient(0, 0, 0, 1300);
  sky.addColorStop(0, C.hotSkyTop);
  sky.addColorStop(1, C.hotSkyLow);
  fillScreen(ctx, '#F4CF7A', texture);
  ctx.save();
  ctx.fillStyle = sky;
  ctx.globalAlpha = 0.85;
  ctx.fillRect(0, 0, W, H);
  ctx.restore();
  const zoom = lerp(1, 1.05, prog(t, 4.19, 4.98));
  withCamera(ctx, { x: 540, y: 960, zoom }, () => {
    const drop = eBack(prog(t, 4.19, 4.42), 1.7);
    const sunY = lerp(-320, 540, drop);
    const glow = ctx.createRadialGradient(540, sunY, 120, 540, sunY, 640);
    glow.addColorStop(0, 'rgba(255,246,200,0.85)');
    glow.addColorStop(1, 'rgba(255,246,200,0)');
    ctx.fillStyle = glow;
    ctx.fillRect(-200, sunY - 700, 1500, 1400);
    ctx.save();
    ctx.translate(540, sunY);
    ctx.rotate(t * 0.9);
    for (let i = 0; i < 16; i += 1) {
      const a = i * TAU / 16;
      const long = i % 2 ? 300 : 360;
      const pulse = 1 + 0.05 * Math.sin(t * 9 + i);
      const tip = [Math.cos(a) * long * pulse, Math.sin(a) * long * pulse];
      const l = [Math.cos(a - 0.11) * 205, Math.sin(a - 0.11) * 205];
      const r = [Math.cos(a + 0.11) * 205, Math.sin(a + 0.11) * 205];
      cut(ctx, polyPath([l, tip, r]), i % 2 ? C.sunRay2 : C.sunRay, texture, 5);
    }
    ctx.restore();
    cut(ctx, ovalPath(540, sunY, 200, 200), C.sun, texture, 10);
    cut(ctx, ovalPath(515, sunY - 26, 140, 132, 0.3), C.sunHi, texture, 0);

    // The last rain cloud dries up on "drought".
    const gone = eIn(prog(t, 4.46, 4.7));
    cloud(ctx, texture, 220 + 20 * gone, 300 - 40 * gone, 1.05 * (1 - gone), 1);
    for (let i = 0; i < 4; i += 1) {
      const k = prog(t, 4.52 + i * 0.03, 4.9);
      if (k > 0 && k < 1) puff(ctx, texture, 160 + i * 45, 300 - 160 * k, 18 * (1 - k), C.white, 1 - k);
    }

    // Heat shimmer.
    ctx.save();
    ctx.strokeStyle = 'rgba(255,250,232,0.5)';
    ctx.lineWidth = 7;
    ctx.lineCap = 'round';
    const heat = prog(t, 4.3, 4.6);
    for (let i = 0; i < 6; i += 1) {
      const x0 = 110 + i * 175;
      ctx.globalAlpha = heat * 0.8;
      ctx.beginPath();
      for (let s = 0; s <= 20; s += 1) {
        const y = 1150 - s * 22 - ((t * 260 + i * 70) % 90);
        const x = x0 + 12 * Math.sin(s * 0.8 + t * 12 + i);
        if (s === 0) ctx.moveTo(x, y); else ctx.lineTo(x, y);
      }
      ctx.stroke();
    }
    ctx.restore();

    // Grass wilts and fades to straw, left to right.
    const wilt = x => eIO(prog(t, 4.44 + x / 1100 * 0.2, 4.44 + x / 1100 * 0.2 + 0.28));
    const avg = eIO(prog(t, 4.44, 4.92));
    cut(ctx, bandPath(-300, 1400, 1205, 2600, 6, 81), lerpColor('#8DB55A', '#CDB168', avg), texture, 8);
    for (const b of drought.back) {
      const k = wilt(b.x);
      blade(ctx, texture, b.x, 1215, b.h * (1 - 0.15 * k), b.w, b.lean + 0.03 * Math.sin(t * 5 + b.x), (b.lean >= 0 ? 1 : -1) * 1.1 * k,
        lerpColor(b.c > 0.5 ? '#93BD5C' : '#7FA84E', b.c > 0.5 ? '#D8C07C' : '#C4A65E', k), 3);
    }
    cut(ctx, bandPath(-300, 1400, 1290, 2600, 6, 82), lerpColor('#789251', '#BFA05A', avg), texture, 9);
    for (const b of drought.front) {
      const k = wilt(b.x);
      blade(ctx, texture, b.x, 1300, b.h * (1 - 0.18 * k), b.w, b.lean + 0.04 * Math.sin(t * 4 + b.x), (b.lean >= 0 ? 1 : -1) * 1.35 * k,
        lerpColor(b.c > 0.5 ? '#789251' : '#A9D554', b.c > 0.5 ? '#B89A55' : '#D2B86F', k), 4);
    }
  });
}

// ------------------------------------------------------------------ S5: the ground itself (4.98-5.88)
function clipHalf(poly, s, o) {
  const mx = (s[0] + o[0]) / 2;
  const my = (s[1] + o[1]) / 2;
  const nx = o[0] - s[0];
  const ny = o[1] - s[1];
  const f = p => (p[0] - mx) * nx + (p[1] - my) * ny;
  const out = [];
  for (let i = 0; i < poly.length; i += 1) {
    const a = poly[i];
    const b = poly[(i + 1) % poly.length];
    const fa = f(a);
    const fb = f(b);
    if (fa <= 0) out.push(a);
    if ((fa <= 0) !== (fb <= 0)) {
      const k = fa / (fa - fb);
      out.push([a[0] + (b[0] - a[0]) * k, a[1] + (b[1] - a[1]) * k]);
    }
  }
  return out;
}

function setupCracks() {
  const random = rng(2026);
  const sites = [];
  const cell = 150;
  for (let y = -380; y < 2300; y += cell) {
    for (let x = -380; x < 1460; x += cell) sites.push([x + random() * cell, y + random() * cell]);
  }
  const origin = [540, 880];
  const plates = sites.map((site, i) => {
    let poly = [[-500, -500], [1580, -500], [1580, 2420], [-500, 2420]];
    for (let j = 0; j < sites.length; j += 1) {
      if (j === i) continue;
      const other = sites[j];
      if (Math.abs(other[0] - site[0]) > 420 || Math.abs(other[1] - site[1]) > 420) continue;
      poly = clipHalf(poly, site, other);
      if (poly.length < 3) break;
    }
    const cx = poly.reduce((s, p) => s + p[0], 0) / poly.length;
    const cy = poly.reduce((s, p) => s + p[1], 0) / poly.length;
    let area = 0;
    for (let k = 0; k < poly.length; k += 1) {
      const a = poly[k];
      const b = poly[(k + 1) % poly.length];
      area += a[0] * b[1] - b[0] * a[1];
    }
    const radius = Math.sqrt(Math.abs(area / 2) / Math.PI);
    return {
      poly, cx, cy, radius,
      delay: Math.hypot(cx - origin[0], cy - origin[1]) / 2300,
      color: ['#C9A271', '#DDBB88', '#C49A68', '#D8B582', '#CFA877'][i % 5],
      curl: (random() - 0.5) * 0.08,
    };
  });
  const stubs = Array.from({ length: 22 }, () => [random() * 1080, random() * 1920, random() * TAU, 30 + random() * 40]);
  return { plates, stubs };
}

function drawCracks(ctx, texture, ground, t) {
  fillScreen(ctx, C.crack, texture);
  const k = prog(t, 4.98, 5.88);
  withCamera(ctx, { x: 540, y: 900, zoom: lerp(1.04, 1.16, eIO(k)), rot: lerp(-0.02, 0.07, eIO(k)) }, () => {
    for (const plate of ground.plates) {
      const open = eOut(prog(t, 5.12 + plate.delay, 5.12 + plate.delay + 0.2));
      const widen = eOut(prog(t, 5.42 + plate.delay * 0.6, 5.42 + plate.delay * 0.6 + 0.3));
      const gap = 13 * open + 11 * widen;
      const s = Math.max(0.4, 1 - gap / Math.max(30, plate.radius * 1.7));
      ctx.save();
      ctx.translate(plate.cx, plate.cy);
      ctx.rotate(plate.curl * widen);
      ctx.scale(s, s);
      ctx.translate(-plate.cx, -plate.cy);
      cut(ctx, polyPath(plate.poly), lerpColor('#D2AE7C', plate.color, open), texture, 1 + 6 * open + 4 * widen);
      ctx.restore();
    }
    for (const [x, y, a, h] of ground.stubs) {
      blade(ctx, texture, x, y, h, 9, a, 0.6, '#B89A55', 2);
    }
  });
}

// ------------------------------------------------------------------ S6-S8: hard, dry, cannot build (5.88-8.8)
const GROUND = 1000;
const HERO_SCALE = 0.62;

function setupCrust(texture) {
  const random = rng(5150);
  const crustTop = tornLine(-700, 1800, GROUND, 3, 71, 30);
  const crustBottom = tornLine(-700, 1800, GROUND + 95, 8, 72, 40);
  const crust = polyPath([...crustTop, ...crustBottom.reverse()]);
  const layers = [
    { path: bandPath(-700, 1800, GROUND + 90, 3600, 8, 73), color: '#B57553' },
    { path: bandPath(-700, 1800, GROUND + 400, 3600, 10, 74), color: '#9E6A4D' },
    { path: bandPath(-700, 1800, GROUND + 820, 3600, 10, 75), color: '#86563F' },
    { path: bandPath(-700, 1800, GROUND + 1300, 3600, 10, 76), color: '#744C43' },
  ];
  const notches = [[-120, 70, 18], [150, 62, 20], [330, 86, 24], [452, 74, 22], [700, 90, 26], [905, 66, 20], [1150, 80, 22]];
  const pebbles = Array.from({ length: 70 }, () => [-600 + random() * 2300, GROUND + 120 + random() * 1700, 6 + random() * 16, random() * 3,
    ['#C98E66', '#9A6447', '#D9AE80', '#7F503B'][Math.floor(random() * 4)]]);
  const crumbs = Array.from({ length: 50 }, () => [-600 + random() * 2300, GROUND + 15 + random() * 70, 3 + random() * 7, random() * 3]);
  const grassBack = Array.from({ length: 30 }, (_, i) => ({ x: -620 + i * 85 + random() * 40, h: 70 + random() * 90, lean: (random() - 0.5) * 0.6 }));
  const tunnels = createTunnels(texture, [
    [[452, GROUND + 60], [440, GROUND + 230], [490, GROUND + 420], [470, GROUND + 520]],
    [[470, GROUND + 520], [600, GROUND + 600], [720, GROUND + 720], [760, GROUND + 760]],
    [[700, GROUND + 790], [600, GROUND + 880], [470, GROUND + 940], [380, GROUND + 960]],
    [[380, GROUND + 990], [330, GROUND + 1110], [300, GROUND + 1200]],
    [[330, GROUND + 520], [230, GROUND + 560], [160, GROUND + 640]],
  ], [
    [470, GROUND + 540, 120, 50], [770, GROUND + 770, 135, 55], [370, GROUND + 970, 140, 55], [300, GROUND + 1215, 115, 46], [155, GROUND + 650, 90, 40],
  ], [
    { route: 0, u0: 0.2, speed: 120, scale: 0.2, offset: 0.1 },
    { route: 1, u0: 0.1, speed: 110, scale: 0.2, offset: 0.4 },
    { route: 1, u0: 0.6, speed: 100, scale: 0.2, offset: 0.8 },
    { route: 2, u0: 0.3, speed: 115, scale: 0.2, offset: 0.2 },
    { route: 3, u0: 0.5, pace: 0.7, range: 0.45, scale: 0.19, offset: 0.6 },
    { route: 4, u0: 0.2, pace: 0.6, range: 0.6, scale: 0.18, offset: 0.9 },
    { route: 2, u0: 0.75, speed: 90, scale: 0.2, offset: 0.5 },
  ], 52);
  const ghost = domePoints(540, GROUND, 720, 340, 31, 60);
  const ghostPath = pathOf(ghost);
  const dashCount = 22;
  const dashes = Array.from({ length: dashCount }, (_, i) => {
    const u0 = i / dashCount;
    const u1 = u0 + 0.6 / dashCount;
    return { u0, u1, a: ghostPath.at(u0), b: ghostPath.at(u1), spin: (hash(i + 4) - 0.5) * 12, drift: (hash(i + 9) - 0.5) * 260, delay: Math.abs(i - (dashCount - 1) / 2) * 0.006 };
  });
  return { crust, layers, notches, pebbles, crumbs, grassBack, tunnels, ghostPath, dashes };
}

// Hero ant motion: walk in, rear back, strike the crust, recoil, look up.
function heroState(t) {
  const walkK = eOut(prog(t, 5.88, 6.32));
  let x = lerp(1310, 600, walkK);
  const travelled = 710 * walkK;
  const rear = eOut(prog(t, 6.34, 6.56));
  const strike = eIn(prog(t, 6.56, 6.62));
  const recover = eOut(prog(t, 6.64, 6.95));
  x += 40 * recover;
  let pitch = 0.13 * rear * (1 - strike);
  let bob = -14 * rear * (1 - strike) + 58 * strike * (1 - recover);
  let head = 0.3 * rear * (1 - strike) - 0.62 * strike * (1 - recover);
  let mand = rear * (1 - strike) + 0.4 * strike * (1 - recover);
  pitch += 0.06 * wobble(t, 6.66, 3.2, 5);
  head += 0.16 * wobble(t, 7.0, 4.5, 3.5);
  const lookUp = eOut(prog(t, 7.68, 7.9));
  head += 0.16 * lookUp;
  const antennaLift = -0.38 * Math.max(rear * (1 - strike), lookUp);
  return {
    x, pitch, recoil: recover,
    pose: {
      phase: walkPhase(travelled, HERO_SCALE), walk: t < 6.34 ? 1 : 0, mand, head, bob,
      antennae: [[antennaLift + 0.06 * Math.sin(t * 10), 0.2 * lookUp], [antennaLift * 0.9 + 0.06 * Math.sin(t * 8 + 1), 0.15 * lookUp]],
    },
  };
}

// World position of an ant-space point for the hero (same transforms as drawHero).
function heroPoint(state, local) {
  const pivot = [146, ANT_FOOT_Y];
  const c = Math.cos(state.pitch);
  const s = Math.sin(state.pitch);
  const lx = local[0] - pivot[0];
  const ly = local[1] - pivot[1];
  const rx = pivot[0] + c * lx - s * ly;
  const ry = pivot[1] + s * lx + c * ly;
  return [state.x + rx * HERO_SCALE, GROUND + (ry - ANT_FOOT_Y) * HERO_SCALE];
}

// Pitch turns the body about the hind foot so the front lifts when it rears back.
function drawHero(ctx, texture, state) {
  ctx.save();
  ctx.translate(state.x, GROUND);
  ctx.scale(HERO_SCALE, HERO_SCALE);
  ctx.translate(146, 0);
  ctx.rotate(state.pitch);
  ctx.translate(-146, 0);
  placeAnt(ctx, texture, 0, 0, 1, state.pose);
  ctx.restore();
}

function crustCamera(t) {
  let cam;
  if (t < 7.0) {
    const k = eIO(prog(t, 5.88, 6.6));
    cam = { x: lerp(640, 560, k), y: 900, zoom: lerp(1.9, 2.0, k) };
  } else if (t < 7.48) {
    const k = eIO(prog(t, 7.0, 7.48));
    cam = { x: lerp(560, 530, k), y: lerp(900, 905, k), zoom: lerp(2.0, 2.1, k) };
  } else if (t < 8.38) {
    const k = eIO(prog(t, 7.48, 7.78));
    cam = { x: lerp(530, 560, k), y: lerp(905, 940, k), zoom: zoomTo(2.1, 0.9, k) * (1 - 0.02 * prog(t, 7.78, 8.38)) };
  } else {
    const k = eIO(prog(t, 8.38, 8.8));
    cam = { x: 560, y: lerp(940, 1560, k), zoom: lerp(0.9 * 0.98, 0.84, k) };
  }
  const [dx, dy] = shake(t, 6.61, 0.3, 20, 3);
  return { ...cam, dx, dy };
}

function drawCrust(ctx, texture, crust, t) {
  const sky = ctx.createLinearGradient(0, 0, 0, H);
  sky.addColorStop(0, '#F3CC72');
  sky.addColorStop(0.6, '#F8E3A8');
  fillScreen(ctx, '#F6DB95', texture);
  ctx.save();
  ctx.fillStyle = sky;
  ctx.globalAlpha = 0.8;
  ctx.fillRect(0, 0, W, H);
  ctx.restore();
  const hero = heroState(t);
  const strikePoint = heroPoint({ ...heroState(6.62) }, [-286, 18]);
  withCamera(ctx, crustCamera(t), () => {
    // Sun stays in the corner for continuity.
    ctx.save();
    ctx.translate(960, 300);
    ctx.rotate(t * 0.8);
    for (let i = 0; i < 12; i += 1) {
      const a = i * TAU / 12;
      cut(ctx, polyPath([[Math.cos(a - 0.15) * 125, Math.sin(a - 0.15) * 125], [Math.cos(a) * 205, Math.sin(a) * 205], [Math.cos(a + 0.15) * 125, Math.sin(a + 0.15) * 125]]), i % 2 ? C.sunRay2 : C.sunRay, texture, 4);
    }
    ctx.restore();
    cut(ctx, ovalPath(960, 300, 120, 120), C.sun, texture, 8);
    for (const g of crust.grassBack) blade(ctx, texture, g.x, GROUND + 4, g.h, 26, g.lean + 0.04 * Math.sin(t * 4 + g.x), 0.9 * Math.sign(g.lean || 1), '#CDB168', 3);

    for (const layer of crust.layers) cut(ctx, layer.path, layer.color, texture, 10);
    for (const [x, y, r, a, color] of crust.pebbles) cut(ctx, ovalPath(x, y, r, r * 0.72, a), color, texture, 2);
    crust.tunnels.draw(ctx, t);
    cut(ctx, crust.crust, C.crust, texture, 9);
    for (const [x, y, r, a] of crust.crumbs) cut(ctx, ovalPath(x, y, r, r * 0.6, a), '#C59D69', null, 0);
    const widen = eOut(prog(t, 7.18, 7.42));
    for (const [x, depth, width] of crust.notches) {
      const w = width * (1 + 0.9 * widen);
      cut(ctx, polyPath([[x - w / 2, GROUND - 1], [x + w / 2, GROUND - 1], [x + w * 0.12, GROUND + depth * (1 + 0.25 * widen)], [x - w * 0.1, GROUND + depth * 0.7]]), C.crack, null, 0);
    }

    // A last drop of moisture shrinks away on "dry".
    const drop = eBack(prog(t, 6.9, 7.02), 2) * (1 - eIn(prog(t, 7.22, 7.42)));
    if (drop > 0.01) {
      ctx.save();
      ctx.translate(335, GROUND - 2);
      ctx.scale(drop, drop);
      cut(ctx, 'M0 0 C-26 0 -30 -26 -16 -40 L0 -66 L16 -40 C30 -26 26 0 0 0 Z', C.water, texture, 4);
      cut(ctx, ovalPath(-7, -30, 6, 10, 0.4), 'rgba(255,255,255,0.7)', null, 0);
      ctx.restore();
    }
    const steam = prog(t, 7.3, 7.6);
    if (steam > 0 && steam < 1) {
      ctx.save();
      ctx.globalAlpha = 1 - steam;
      ctx.strokeStyle = C.white;
      ctx.lineWidth = 9;
      ctx.lineCap = 'round';
      ctx.beginPath();
      for (let s = 0; s <= 10; s += 1) {
        const y = GROUND - 40 - s * 14 - steam * 80;
        const x = 335 + 14 * Math.sin(s * 0.9 + steam * 8);
        if (s === 0) ctx.moveTo(x, y); else ctx.lineTo(x, y);
      }
      ctx.stroke();
      ctx.restore();
    }

    // Two more workers come into view when the camera pulls back.
    const look = eOut(prog(t, 7.74, 7.94));
    const arrive = eOut(prog(t, 7.4, 7.8));
    const leftX = lerp(-300, 160, arrive);
    const rightX = lerp(1420, 990, arrive);
    const helperPose = (distance, scale, seed) => ({
      phase: walkPhase(distance, scale) + seed, walk: arrive < 1 ? 1 : 0, head: 0.14 * look,
      antennae: [[-0.4 * look + 0.05 * Math.sin(t * 9 + seed), 0.2 * look], [-0.35 * look + 0.05 * Math.sin(t * 7), 0.15 * look]],
    });
    if (t > 7.38) {
      placeAnt(ctx, texture, leftX, GROUND, 0.46, helperPose(460 * arrive, 0.46, 0), { faceRight: true });
      placeAnt(ctx, texture, rightX, GROUND, 0.46, helperPose(430 * arrive, 0.46, 2));
    }
    drawHero(ctx, texture, hero);

    // Strike: impact star on "hard".
    const pop = eBack(prog(t, 6.61, 6.72), 2.2);
    const fade = 1 - prog(t, 6.8, 6.98);
    impactStar(ctx, texture, strikePoint[0], strikePoint[1] - 10, 150, pop, fade, 0.2);

    // Dust gust on "and", dust puff on "dry".
    for (let i = 0; i < 46; i += 1) {
      const start = 6.98 + hash(i) * 0.26;
      const k = (t - start) / 0.55;
      if (k <= 0 || k >= 1) continue;
      const x = -120 + k * (1400 + 500 * hash(i + 1));
      const y = GROUND - 10 - 170 * hash(i + 2) + 26 * Math.sin(k * 7 + i);
      ctx.save();
      ctx.translate(x, y);
      ctx.rotate(k * 9 * (hash(i + 3) - 0.5));
      const r = 5 + 9 * hash(i + 4);
      cut(ctx, polyPath([[-r, -r * 0.4], [r, -r * 0.6], [r * 0.7, r * 0.5], [-r * 0.8, r * 0.4]]), ['#E6CFA0', '#D9B47E', '#C9A271'][i % 3], texture, 2);
      ctx.restore();
    }
    const cloudK = prog(t, 7.2, 7.75);
    if (cloudK > 0 && cloudK < 1) {
      for (let i = 0; i < 8; i += 1) {
        const a = -Math.PI / 2 + (i / 7 - 0.5) * 2.6;
        const d = 30 + 110 * eOut(cloudK);
        puff(ctx, texture, strikePoint[0] + Math.cos(a) * d * 1.4, strikePoint[1] - 20 + Math.sin(a) * d, (34 + 26 * hash(i + 20)) * (0.5 + eOut(cloudK)), '#E3CDA2', 1 - cloudK);
      }
    }

    // Ghost mound draws on "build", falls apart on "one".
    const drawK = eIO(prog(t, 7.98, 8.2));
    for (const dash of crust.dashes) {
      if (drawK <= dash.u0) continue;
      const fallStart = 8.2 + dash.delay;
      const f = Math.max(0, t - fallStart);
      const kick = f > 0 ? -60 * Math.exp(-f * 18) * Math.min(1, f * 40) : 0;
      const partial = clamp((drawK - dash.u0) / (dash.u1 - dash.u0));
      const b = partial < 1 ? crust.ghostPath.at(dash.u0 + (dash.u1 - dash.u0) * partial) : dash.b;
      const mx = (dash.a[0] + b[0]) / 2;
      const my = (dash.a[1] + b[1]) / 2;
      const fallY = Math.min(GROUND - 10 - my, 0.5 * 6500 * f * f + kick);
      const alpha = 1 - prog(t, fallStart + 0.2, fallStart + 0.36);
      if (alpha <= 0) continue;
      ctx.save();
      ctx.globalAlpha = alpha;
      ctx.translate(mx + dash.drift * f, my + fallY);
      ctx.rotate(dash.spin * f);
      ctx.translate(-mx, -my);
      cut(ctx, capsulePath(dash.a, b, 7, 7), C.purple, texture, 4);
      ctx.restore();
    }
  });
}

// ------------------------------------------------------------------ assembly
export function createScene(config, timing) {
  const texture = makeFibres((config.seed ?? 1) | 0);
  const crowd = setupCrowd(texture);
  const yard = setupYard(texture);
  const drought = setupDrought();
  const ground = setupCracks();
  const crust = setupCrust(texture);
  const duration = config.duration_seconds;
  const captions = createCaptions(timing.words, timing.caption_groups, {
    texture, centerY: config.caption_center_y ?? 1420, endTime: duration + 1,
  });

  function drawWorld(ctx, t) {
    if (t < 1.14) {
      drawCrowd(ctx, texture, crowd, t);
    } else if (t < 1.3) {
      drawCrowd(ctx, texture, crowd, t);
      const k = eOut(prog(t, 1.14, 1.3));
      const offset = H * (1 - k);
      const edge = bandPath(-50, W + 50, -18, H + 40, 12, 501);
      ctx.save();
      ctx.translate(0, offset);
      cut(ctx, edge, C.paper, texture, 22, { shadow: 'rgba(30,20,25,0.45)' });
      ctx.clip(edge);
      drawYard(ctx, texture, yard, t);
      ctx.restore();
    } else if (t < 4.19) {
      drawYard(ctx, texture, yard, t);
    } else if (t < 4.98) {
      drawDrought(ctx, texture, drought, t);
    } else if (t < 5.14) {
      const k = eIO(prog(t, 4.98, 5.14));
      ctx.save();
      ctx.translate(0, -H * k);
      drawDrought(ctx, texture, drought, t);
      ctx.restore();
      ctx.save();
      ctx.translate(0, H * (1 - k));
      const edge = bandPath(-50, W + 50, -14, H + 40, 12, 502);
      cut(ctx, edge, C.crack, texture, 20, { shadow: 'rgba(30,20,25,0.45)' });
      ctx.clip(edge);
      drawCracks(ctx, texture, ground, t);
      ctx.restore();
    } else if (t < 5.88) {
      drawCracks(ctx, texture, ground, t);
    } else {
      drawCrust(ctx, texture, crust, t);
    }
  }

  return {
    duration,
    // Windows with fast camera moves get sub-frame motion blur from the renderer.
    // Paper slides and whips stay crisp, like stop-motion cutouts.
    blurWindows: [[0.74, 1.02], [2.82, 3.08], [7.48, 7.74]],
    drawWorld,
    drawOverlay: captions,
    draw(ctx, t) {
      drawWorld(ctx, t);
      captions(ctx, t);
    },
  };
}
