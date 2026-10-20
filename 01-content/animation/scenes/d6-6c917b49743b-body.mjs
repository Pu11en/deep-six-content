// Episode D6-6c917b49743b: everything after the hook (8.98 s to the end).
// Shot plan: episodes/D6-6c917b49743b/full/shot-list.json. Times are seconds in the full narration.
// Style C cut-paper storybook. Every frame is a pure function of time.
import {
  W, H, C, Path2D, clamp, lerp, eOut, eIn, eIO, eBack, rng, hash, mix,
  prog, zoomTo, wobble, shake, cut, polyPath, smoothPath, ovalPath, capsulePath, bandPath, tornLine,
  withCamera, placeAnt, walkPhase, drawEgg, drawLarva, drawPupa, ANT_FOOT_Y,
} from './paper-kit.mjs';
import { createNest, CHAMBERS, SURFACE } from './nest-world.mjs';
import { createYard, MOUND, questionMark, bigX, pushpin, gauge, person, thoughtBubble } from './yard-world.mjs';

const TAU = Math.PI * 2;
const bell = (t, t0, d) => { const k = prog(t, t0, t0 + d); return Math.sin(Math.PI * k); };

function fillScreen(ctx, color, texture) {
  ctx.save();
  ctx.setTransform(1, 0, 0, 1, 0, 0);
  cut(ctx, polyPath([[0, 0], [W, 0], [W, H], [0, H]]), color, texture, 0, { grain: 0.8 });
  ctx.restore();
}

// Camera keyframes: [[time, {x, y, zoom}, ease?], ...]. Zoom moves in log space.
function camAt(t, keys) {
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
const cam = (x, y, zoom) => ({ x, y, zoom });
const WIDE = cam(540, 1480, 0.62);
// The camera never fully stops: a slow breath and sway on top of every shot's own moves.
const live = (c, t) => ({ ...c, x: c.x + 6 * Math.sin(t * 0.9), y: c.y + 5 * Math.sin(t * 1.13 + 1), zoom: c.zoom * (1 + 0.022 * Math.sin(t * 1.7)) });

export function createBody(texture) {
  const nest = createNest(texture);
  const yard = createYard(texture);
  const NORMAL = { mound: 1, surfaceAnts: 0.6, traffic: 0.8 };

  function nestShot(ctx, t, camera, state, after) {
    fillScreen(ctx, C.paper, texture);
    withCamera(ctx, live(camera, t), () => {
      nest.draw(ctx, t, state);
      if (after) after(ctx);
    });
  }

  // Paper slide: the next scene arrives on a torn sheet. dir 1 = from the right, -1 = from below.
  function slide(ctx, t, t0, duration, drawPrev, drawNext, dir = 1) {
    const k = eOut(prog(t, t0, t0 + duration));
    if (k >= 1) { drawNext(ctx); return; }
    drawPrev(ctx);
    const edge = dir === 1
      ? polyPath([[18, -60], ...tornLine(-60, H + 60, 0, 12, 503, 36).map(([y, dx]) => [dx + 0, y]).map(([x, y]) => [x - 18 + 18 * Math.sin(y * 0.02), y]), [W + 60, H + 60], [W + 60, -60]])
      : bandPath(-50, W + 50, -18, H + 40, 12, 502);
    ctx.save();
    if (dir === 1) ctx.translate(W * (1 - k), 0); else ctx.translate(0, H * (1 - k));
    cut(ctx, edge, C.paper, texture, 22, { shadow: 'rgba(30,20,25,0.45)' });
    ctx.clip(edge);
    drawNext(ctx);
    ctx.restore();
  }

  // ---------------------------------------------------------------- nursery close-up set
  const FLOOR = 1150;
  const eggClump = [];
  for (const [n, row] of [[5, 0], [4, 1], [3, 2]]) {
    for (let k = 0; k < n; k += 1) eggClump.push([(k - (n - 1) / 2) * 36 + (row % 2) * 2, -24 - row * 30, 1.2 + hash(eggClump.length) * 0.5]);
  }
  const roomCrumbs = Array.from({ length: 30 }, (_, i) => [-80 + hash(i + 1) * 1240, FLOOR + 30 + hash(i + 7) * 200, 6 + hash(i + 3) * 14, hash(i + 9) * 3]);
  function nurseryRoom(ctx, t, camera, draw) {
    fillScreen(ctx, '#7E5242', texture);
    withCamera(ctx, live(camera, t), () => {
      cut(ctx, ovalPath(540, 880, 780, 620), C.tunnel, texture, 0);
      cut(ctx, ovalPath(540, 840, 700, 540), C.tunnelInner, texture, 0);
      const glow = ctx.createRadialGradient(540, 960, 60, 540, 960, 720);
      glow.addColorStop(0, 'rgba(255,214,120,0.32)');
      glow.addColorStop(1, 'rgba(255,214,120,0)');
      ctx.fillStyle = glow;
      ctx.fillRect(-400, 200, 1900, 1500);
      cut(ctx, smoothPath([[-400, FLOOR + 40], [100, FLOOR + 6], [540, FLOOR - 6], [980, FLOOR + 6], [1480, FLOOR + 40], [1480, 2200], [-400, 2200]], true), '#B9885F', texture, 10);
      cut(ctx, bandPath(-400, 1480, FLOOR + 110, 2200, 8, 77), '#9E6F4E', texture, 6);
      for (const [x, y, r, a] of roomCrumbs) cut(ctx, ovalPath(x, y, r, r * 0.6, a), '#8E5F44', null, 0);
      draw(ctx);
      // Warm dust motes drifting through the nursery.
      ctx.save();
      for (let i = 0; i < 26; i += 1) {
        const x = -100 + ((hash(i + 40) * 1300 + t * (14 + 10 * hash(i))) % 1300);
        const y = 1120 - ((hash(i + 70) * 700 + t * (22 + 18 * hash(i + 5))) % 700);
        ctx.globalAlpha = 0.25 + 0.35 * (0.5 + 0.5 * Math.sin(t * 3 + i));
        ctx.fillStyle = '#F6DFA8';
        ctx.beginPath();
        ctx.arc(x, y, 3 + 4 * hash(i + 9), 0, TAU);
        ctx.fill();
      }
      ctx.restore();
    });
  }
  const eggs = (ctx, x, y, s, k = 1) => {
    eggClump.forEach(([ex, ey, a], i) => {
      const pop = eBack(clamp(k * eggClump.length - i), 2);
      if (pop > 0) drawEgg(ctx, texture, x + ex * s, y + ey * s, 22 * s * pop, a);
    });
  };
  const larvae = (ctx, x, y, s, t, k = 1) => {
    [[-110, -0.35], [0, 0.25], [110, -0.1]].forEach(([dx, a], i) => {
      const pop = eBack(clamp(k * 3 - i), 2);
      if (pop > 0) drawLarva(ctx, texture, x + dx * s, y - 58 * s, s * pop, a, Math.sin(t * 4 + i * 2));
    });
  };
  const pupae = (ctx, x, y, s, k = 1) => {
    [[-140, false], [140, true]].forEach(([dx, flip], i) => {
      const pop = eBack(clamp(k * 2 - i), 2);
      if (pop <= 0) return;
      ctx.save();
      ctx.translate(x + dx * s, y - 42 * s);
      if (flip) ctx.scale(-1, 1);
      drawPupa(ctx, texture, 0, 0, 0.42 * s * pop, 0.04);
      ctx.restore();
    });
  };
  const lerp2 = (a, b, k) => [lerp(a[0], b[0], k), lerp(a[1], b[1], k), lerp(a[2], b[2], k)];

  function nurseryStages(ctx, t) {
    // Each stage lands on the floor as it is named; the camera whips to it, then pulls back.
    const camera = camAt(t, [
      [16.32, cam(320, 1075, 2.6)], [16.95, cam(320, 1075, 2.66)], [17.12, cam(560, 1075, 2.6)], [17.58, cam(560, 1075, 2.66)],
      [17.75, cam(800, 1075, 2.5)], [18.64, cam(810, 1080, 2.85)], [19.0, cam(540, 1060, 1.42)], [20.6, cam(540, 1060, 1.56)], [21.79, cam(540, 1095, 2.0)],
    ]);
    nurseryRoom(ctx, t, camera, () => {
      const gather = eIO(prog(t, 18.64, 19.06));
      const bounce = 1 + 0.08 * bell(t, 20.48, 0.28);
      const ex = lerp(320, 735, gather);
      const lx = lerp(560, 525, gather);
      const px = lerp(800, 315, gather);
      ctx.save();
      ctx.translate(530, FLOOR);
      ctx.scale(bounce, bounce);
      ctx.translate(-530, -FLOOR);
      if (t >= 17.76) pupae(ctx, px, FLOOR, lerp(0.8, 0.72, gather), prog(t, 17.76, 18.02));
      if (t >= 16.95) larvae(ctx, lx, FLOOR, lerp(0.85, 0.7, gather), t, prog(t, 16.95, 17.22));
      eggs(ctx, ex, FLOOR, lerp(1.25, 0.8, gather), prog(t, 16.32, 16.62));
      ctx.restore();
      // Nurses walk in from both sides.
      const walkIn = eOut(prog(t, 18.95, 19.6));
      if (t > 18.9) {
        const lxN = lerp(-260, 170, walkIn);
        const rxN = lerp(1340, 905, walkIn);
        const tap = [[-0.25 + 0.15 * Math.sin(t * 9), 0.15], [-0.2 + 0.15 * Math.sin(t * 8 + 1), 0.1]];
        placeAnt(ctx, texture, lxN, FLOOR + 4, 0.5, { phase: walkPhase(370 * walkIn, 0.5), walk: walkIn < 1 ? 1 : 0, head: 0.18, antennae: tap }, { faceRight: true });
        placeAnt(ctx, texture, rxN, FLOOR + 4, 0.5, { phase: walkPhase(370 * walkIn, 0.5) + 1, walk: walkIn < 1 ? 1 : 0, head: 0.18, antennae: tap });
      }
      // "brood": a lime loop wraps the whole pile.
      // A full turn of exactly 2*PI collapses to nothing in this canvas library; stop just short.
      const loop = Math.min(0.9995, eIO(prog(t, 20.16, 20.56)));
      if (loop > 0) {
        ctx.save();
        ctx.lineCap = 'round';
        ctx.strokeStyle = 'rgba(30,27,34,0.3)';
        ctx.lineWidth = 18;
        ctx.beginPath();
        ctx.ellipse(536, FLOOR - 44, 315, 130, -0.03, -Math.PI / 2, -Math.PI / 2 + TAU * loop);
        ctx.stroke();
        ctx.strokeStyle = C.lime;
        ctx.lineWidth = 14;
        ctx.beginPath();
        ctx.ellipse(530, FLOOR - 50, 315, 130, -0.03, -Math.PI / 2, -Math.PI / 2 + TAU * loop);
        ctx.stroke();
        ctx.restore();
      }
    });
  }

  function lifecycle(ctx, t) {
    const camera = camAt(t, [[21.79, cam(540, 1000, 1.0)], [22.68, cam(540, 990, 1.1)], [23.49, cam(540, 1000, 1.0)], [23.82, cam(540, 1000, 1.06)],
      [24.14, cam(540, 1010, 1.0)], [24.99, cam(540, 1030, 1.2)], [25.3, cam(540, 1000, 1.0)], [26.14, cam(560, 990, 1.12)], [27.29, cam(760, 1000, 1.04)]]);
    nurseryRoom(ctx, t, camera, () => {
      const cx = 540;
      // Egg: wobble, crack, split.
      const r = 215;
      const ey = FLOOR - r;
      if (t < 22.62) {
        const split = eOut(prog(t, 22.2, 22.6));
        const wob = 0.1 * Math.sin((t - 21.79) * TAU * 5) * Math.exp(-(t - 21.79) * 2) * (t < 22.2 ? 1 : 0);
        const crack = prog(t, 22.04, 22.18);
        const half = (top) => {
          ctx.save();
          ctx.globalAlpha = 1 - split;
          ctx.translate(cx + (top ? -120 : 100) * split, ey + (top ? -180 : 40) * split);
          ctx.rotate((top ? -0.6 : 0.5) * split + wob);
          ctx.translate(-cx, -ey);
          ctx.beginPath();
          if (top) ctx.rect(cx - 400, ey - 400, 800, 400); else ctx.rect(cx - 400, ey, 800, 400);
          ctx.clip();
          drawEgg(ctx, texture, cx, ey, r, 0);
          ctx.restore();
        };
        half(true);
        half(false);
        if (crack > 0 && split < 0.05) {
          ctx.save();
          ctx.translate(cx, ey);
          ctx.rotate(wob);
          ctx.strokeStyle = C.ink;
          ctx.lineWidth = 10;
          ctx.lineJoin = 'round';
          ctx.lineCap = 'round';
          ctx.beginPath();
          const pts = [[-158, 0], [-100, -26], [-52, 18], [0, -22], [50, 20], [100, -18], [158, 6]];
          const n = Math.max(1, Math.round(crack * (pts.length - 1)));
          pts.slice(0, n + 1).forEach(([x, y], i) => (i ? ctx.lineTo(x, y) : ctx.moveTo(x, y)));
          ctx.stroke();
          ctx.restore();
        }
      }
      // Larva: tiny on "hatch", grows on "larvae", flips into a pupa on "become".
      const flip1 = prog(t, 23.82, 24.14);
      const flip2 = prog(t, 24.99, 25.31);
      if (t >= 22.2 && flip1 < 0.5) {
        const grow = eBack(prog(t, 22.68, 23.06), 1.6);
        const s = lerp(0.6, 3.5, grow) * eBack(prog(t, 22.2, 22.4), 2);
        const squash = Math.abs(Math.cos(Math.PI * flip1));
        ctx.save();
        ctx.translate(cx, FLOOR);
        ctx.scale(squash, 1);
        ctx.translate(-cx, -FLOOR);
        drawLarva(ctx, texture, cx, FLOOR - 62 * s, s, 0.1, 1.6 * Math.sin(t * 6));
        ctx.restore();
      }
      if (flip1 >= 0.5 && flip2 < 0.5) {
        const squash = flip2 > 0 ? Math.abs(Math.cos(Math.PI * flip2)) : Math.abs(Math.cos(Math.PI * flip1));
        ctx.save();
        ctx.translate(cx, FLOOR);
        ctx.scale(squash, 1);
        ctx.rotate(0.02 * Math.sin(t * 3));
        ctx.translate(-cx, -FLOOR);
        drawPupa(ctx, texture, cx + 20, FLOOR - 112, 1.18, 0, eOut(prog(t, 24.14, 24.99)) * 0.6);
        ctx.restore();
      }
      if (flip2 >= 0.5) {
        const squash = flip2 < 1 ? Math.abs(Math.cos(Math.PI * flip2)) : 1;
        const darken = eIO(prog(t, 25.31, 26.1));
        const go = eIn(prog(t, 26.14, 27.1));
        const x = cx + 30 + 1100 * go;
        const look = bell(t, 25.52, 0.5);
        ctx.save();
        ctx.translate(cx, FLOOR);
        ctx.scale(squash, 1);
        ctx.translate(-cx, -FLOOR);
        placeAnt(ctx, texture, x, FLOOR + 6, 1.05, {
          tint: 1 - darken, phase: walkPhase(1100 * go, 1.05), walk: go > 0 ? 1 : 0,
          antennae: [[-0.35 * look + 0.05 * Math.sin(t * 7), 0.2 * look], [-0.3 * look, 0.15 * look]], mand: bell(t, 25.7, 0.3),
        }, { faceRight: true });
        ctx.restore();
      }
    });
  }

  // ---------------------------------------------------------------- tunnel close-up (Workers move the brood)
  const tunnelPebbles = Array.from({ length: 60 }, (_, i) => [-1400 + hash(i + 11) * 3200, 300 + hash(i + 23) * 1500, 6 + hash(i + 5) * 16, hash(i + 2) * 3]);
  const tunnelTop = smoothPath([[-1500, 760], ...tornLine(-1400, 1900, 0, 0, 404, 160).map(([x]) => [x, 720 + 50 * Math.sin(x * 0.004) + 20 * hash(Math.round(x))]), [1900, 760], [1900, 1240], [-1500, 1240]], true);
  function tunnelCloseUp(ctx, t) {
    const k = prog(t, 46.49, 47.64);
    const ax = lerp(980, 230, k);
    const camera = cam(lerp(800, 330, k), 1010, 1.35);
    fillScreen(ctx, '#9E6A4D', texture);
    withCamera(ctx, live(camera, t), () => {
      for (const [x, y, r, a] of tunnelPebbles) cut(ctx, ovalPath(x, y, r, r * 0.7, a), '#B07A58', texture, 2);
      cut(ctx, tunnelTop, C.tunnel, texture, 0);
      cut(ctx, bandPath(-1500, 1900, 800, 1240, 10, 405), C.tunnelInner, texture, 0);
      cut(ctx, smoothPath([[-1500, 1170], [-600, 1150], [200, 1165], [900, 1150], [1900, 1168], [1900, 1300], [-1500, 1300]], true), '#C29A70', texture, 8);
      cut(ctx, bandPath(-1500, 1900, 1240, 2000, 8, 406), '#9E6A4D', texture, 6);
      placeAnt(ctx, texture, ax, 1162, 0.8, { phase: walkPhase(750 * k, 0.8), walk: 1, carry: 'larva', antennae: [[0.05 * Math.sin(t * 9), 0], [0.05 * Math.sin(t * 8), 0]] });
      if (t > 47.2) {
        const bx = lerp(1700, 1020, eOut(prog(t, 47.2, 47.64)));
        placeAnt(ctx, texture, bx, 1162, 0.8, { phase: walkPhase(680 * prog(t, 47.2, 47.64), 0.8) + 1, walk: 1, carry: 'pupa' });
      }
    });
  }

  // ---------------------------------------------------------------- one fixed room (rather than...)
  const roomAnts = [[300, 0], [470, 1], [640, 0], [800, 1]];
  function fixedRoom(ctx, t) {
    const [sx, sy] = shake(t, 55.6, 0.25, 16, 2);
    const [xx, xy] = shake(t, 56.62, 0.3, 22, 5);
    const camera = { ...live(cam(540, 960, 1.0), t), dx: sx + xx, dy: sy + xy };
    const season = t < 56.24 ? 0 : Math.floor((t - 56.24) / 0.16) % 4;
    const skies = ['#CFE6E0', '#9AAAB8', '#F2C567', '#B8C4CF'];
    fillScreen(ctx, '#9E6A4D', texture);
    withCamera(ctx, camera, () => {
      ctx.fillStyle = skies[season];
      ctx.fillRect(-400, -400, 1900, 960);
      if (season === 0 || season === 2) {
        ctx.save();
        ctx.translate(540, 280);
        ctx.rotate(t * 0.8);
        for (let i = 0; i < 12; i += 1) {
          const a = i * TAU / 12;
          cut(ctx, polyPath([[Math.cos(a - 0.14) * 100, Math.sin(a - 0.14) * 100], [Math.cos(a) * 165, Math.sin(a) * 165], [Math.cos(a + 0.14) * 100, Math.sin(a + 0.14) * 100]]), season === 2 ? C.sunRay : C.sunRay2, texture, 4);
        }
        ctx.restore();
        cut(ctx, ovalPath(540, 280, 92, 92), C.sun, texture, 8);
      } else {
        const path = new Path2D();
        for (const [ox, oy, r] of [[-95, 18, 62], [-30, -22, 82], [52, -6, 70], [110, 22, 50], [10, 30, 70]]) path.ellipse(540 + ox * 1.4, 260 + oy * 1.4, r * 1.4, r * 1.1, 0, 0, TAU);
        cut(ctx, path, season === 1 ? '#8E99A6' : '#E6E9EC', texture, 8);
        if (season === 1) {
          ctx.save();
          ctx.strokeStyle = 'rgba(140,175,205,0.9)';
          ctx.lineWidth = 7;
          ctx.lineCap = 'round';
          for (let i = 0; i < 9; i += 1) {
            const x = 380 + i * 40;
            const y = 400 + ((t * 900 + i * 37) % 120);
            ctx.beginPath();
            ctx.moveTo(x, y);
            ctx.lineTo(x - 8, y + 34);
            ctx.stroke();
          }
          ctx.restore();
        }
      }
      cut(ctx, bandPath(-400, 1500, 548, 600, 4, 610), C.grass, texture, 5);
      cut(ctx, bandPath(-400, 1500, 540, 578, 4, 611), C.lime, texture, 5);
      cut(ctx, ovalPath(540, 1010, 400, 190), C.tunnel, texture, 0);
      cut(ctx, ovalPath(540, 990, 370, 160), C.tunnelInner, texture, 0);
      cut(ctx, smoothPath([[150, 1110], [540, 1090], [930, 1110], [930, 1200], [150, 1200]], true), '#C29A70', texture, 6);
      roomAnts.forEach(([x, face], i) => {
        const pop = eBack(prog(t, 54.12 + i * 0.07, 54.35 + i * 0.07), 2);
        if (pop <= 0) return;
        placeAnt(ctx, texture, x, 1102, 0.36 * pop, { antennae: [[0.04 * Math.sin(t * 6 + i), 0], [0.04 * Math.sin(t * 5 + i), 0]] }, { faceRight: face === 1 });
      });
      pushpin(ctx, texture, 540, 836, prog(t, 55.42, 55.6));
      bigX(ctx, texture, 540, 1000, 300, prog(t, 56.58, 56.76));
    });
  }

  // ---------------------------------------------------------------- yard shots
  const nestToYard = (ctx) => {
    const s = MOUND.width / 580;
    ctx.translate(MOUND.x - 540 * s, MOUND.base - SURFACE * s);
    ctx.scale(s, s);
  };
  function yardShot(ctx, t, camera, state, front) {
    fillScreen(ctx, C.sky, texture);
    withCamera(ctx, live(camera, t), () => {
      yard.drawBack(ctx, t, state);
      if (front) front(ctx);
      yard.drawFront(ctx, t, state);
    });
  }

  const shots = [];
  const add = (id, start, end, draw) => shots.push({ id, start, end, draw });

  // ---------------------------------------------------------------- 1. A colony has more going on ...
  const broodBase = { C1: 1, D1: 1, U2: 0.8 };
  add('S9', 8.98, 9.42, (ctx, t) => nestShot(ctx, t, cam(540, 1480, lerp(0.6, 0.62, prog(t, 8.98, 9.42))), {
    ...NORMAL, tunnelsDraw: eOut(prog(t, 8.98, 9.36)), traffic: 0.9 * eOut(prog(t, 9.1, 9.4)), surfaceAnts: 0.6 * prog(t, 9.1, 9.3), brood: broodBase,
  }));
  add('S10', 9.42, 10.52, (ctx, t) => nestShot(ctx, t, camAt(t, [[9.42, cam(540, 1480, 0.62)], [9.9, cam(560, 1350, 1.05)], [10.52, cam(560, 1330, 1.12)]]), {
    ...NORMAL, traffic: 0.9, brood: broodBase,
    busy: { C1: prog(t, 9.68, 9.9), C2: prog(t, 9.96, 10.18), U2: prog(t, 10.24, 10.45) },
    glow: { C1: bell(t, 9.68, 0.5), C2: bell(t, 9.96, 0.5), U2: bell(t, 10.24, 0.5) },
  }));
  add('S11', 10.52, 11.48, (ctx, t) => nestShot(ctx, t, camAt(t, [[10.52, cam(560, 1330, 1.12)], [10.72, cam(120, 700, 2.1)], [11.48, cam(60, 700, 2.2)]]), {
    ...NORMAL, traffic: 0.9, surfaceAnts: 1, surfaceScale: 1.5, brood: broodBase, busy: { C1: 1, C2: 1, U2: 1 },
  }));
  add('S12', 11.48, 12.99, (ctx, t) => nestShot(ctx, t, camAt(t, [[11.48, cam(60, 700, 2.2)], [11.95, cam(540, 780, 1.0), eOut], [12.99, cam(640, 800, 1.16)]]), {
    ...NORMAL, traffic: 0.9, surfaceAnts: 1, surfaceScale: lerp(1.5, 1.2, prog(t, 11.48, 11.9)), brood: broodBase, busy: { C1: 1, C2: 1, U2: 1 }, dimUnder: 0.4 * eOut(prog(t, 11.82, 12.1)),
  }));
  add('S13', 12.99, 13.98, (ctx, t) => nestShot(ctx, t, camAt(t, [[12.99, cam(600, 780, 1.05)], [13.25, cam(320, 1770, 1.25)], [13.98, cam(305, 1790, 1.4)]]), {
    ...NORMAL, traffic: 0.9, brood: { C1: 1, U2: 0.8 }, busy: { C1: 1 },
  }));
  add('S14', 13.98, 15.0, (ctx, t) => nestShot(ctx, t, camAt(t, [[13.98, cam(305, 1790, 1.4)], [14.4, cam(285, 1800, 2.6)], [15.0, cam(282, 1802, 3.0)]]), {
    ...NORMAL, traffic: 0.7, brood: { C1: 1, U2: 0.8, D1: eOut(prog(t, 13.98, 14.36)) }, glow: { D1: eOut(prog(t, 14.38, 14.62)) },
  }));
  add('S15', 15.0, 16.32, (ctx, t) => nestShot(ctx, t, camAt(t, [[15.0, cam(282, 1802, 3.0)], [15.42, cam(540, 1480, 0.62), eOut], [16.32, cam(420, 1600, 0.78)]]), {
    ...NORMAL, traffic: 0.7, brood: { C1: 1, U2: 0.8, D1: 1 }, glow: { D1: 0.7 }, ring: { D1: eOut(prog(t, 15.28, 15.52)) },
  }));

  // ---------------------------------------------------------------- 2-3. eggs, larvae, pupae; brood; life cycle
  add('S16', 16.32, 21.79, nurseryStages);
  add('S21', 21.79, 27.29, lifecycle);

  // ---------------------------------------------------------------- 4. Those young ants ... nest conditions matter.
  const broodMid = { C1: 1, U2: 1, D1: 1 };
  add('S26', 27.29, 28.26, (ctx, t) => nestShot(ctx, t, camAt(t, [[27.29, cam(380, 1240, 2.05)], [28.26, cam(380, 1240, 2.2)]]), {
    ...NORMAL, brood: broodMid, ring: { C1: eOut(prog(t, 27.54, 27.78)) },
  }));
  add('S27', 28.26, 29.28, (ctx, t) => nestShot(ctx, t, camAt(t, [[28.26, cam(380, 1240, 2.2)], [28.62, WIDE, eOut], [29.28, cam(540, 1470, 0.63)]]), {
    ...NORMAL, brood: broodMid, ring: { C1: 1, U2: eOut(prog(t, 28.48, 28.7)), D1: eOut(prog(t, 28.98, 29.2)) },
  }));
  add('S28', 29.28, 30.08, (ctx, t) => {
    const toSun = prog(t, 29.6, 29.72);
    nestShot(ctx, t, cam(540, 1400, 0.64), {
      ...NORMAL, brood: broodMid, ring: { C1: 1, U2: 1, D1: 1 },
      rain: eOut(prog(t, 29.28, 29.44)) * (1 - toSun), rainFall: 1 - toSun, cold: 0.6 * (1 - toSun), water: 0.12 * (1 - toSun),
      sun: eBack(prog(t, 29.62, 29.8), 1.6), sunX: 860, sunY: 220, heat: 0.85 * toSun, heatSoil: 0.6 * toSun, cool: 0.5 * toSun,
    });
  });
  add('S29', 30.08, 31.15, (ctx, t) => {
    const back = 1 - prog(t, 30.08, 30.6);
    nestShot(ctx, t, camAt(t, [[30.08, cam(540, 1400, 0.64)], [30.3, cam(380, 1250, 2.4), eOut], [31.15, cam(380, 1245, 2.5)]]), {
      ...NORMAL, brood: broodMid, ring: { C1: 1 }, glow: { C1: 0.4 + 0.5 * bell(t, 30.2, 0.6) },
      sun: back, sunX: 860, sunY: 220, heat: 0.85 * back, heatSoil: 0.6 * back,
    });
  });

  // ---------------------------------------------------------------- 5. cold, wet weather: brood moves up
  const coldWet = t => ({ ...NORMAL, cold: eOut(prog(t, 31.25, 31.6)), wind: 0.8 * eOut(prog(t, 31.3, 31.7)), surfaceAnts: 0 });
  add('S30', 31.15, 32.06, (ctx, t) => nestShot(ctx, t, camAt(t, [[31.15, cam(540, 560, 1.12)], [32.06, cam(540, 590, 1.2)]]), {
    ...coldWet(t), traffic: 0.6, brood: { C1: 1, D1: 1 },
  }));
  add('S31', 32.06, 32.99, (ctx, t) => nestShot(ctx, t, camAt(t, [[32.06, cam(540, 590, 1.2)], [32.5, cam(540, 1300, 0.7), eOut], [32.99, cam(540, 1300, 0.7)]]), {
    ...coldWet(t), traffic: 0.6, brood: { C1: 1, D1: 1 }, rain: eOut(prog(t, 32.06, 32.36)), rainFall: prog(t, 32.2, 32.5),
  }));
  const upperFill = t => ({
    M1: eOut(prog(t, 34.18, 34.46)), M2: eOut(prog(t, 34.3, 34.58)), M3: eOut(prog(t, 34.42, 34.7)), U1: eOut(prog(t, 34.52, 34.8)), U2: eOut(prog(t, 34.62, 34.9)),
  });
  add('S32', 32.99, 34.18, (ctx, t) => nestShot(ctx, t, camAt(t, [[32.99, cam(540, 1300, 0.7)], [34.18, cam(540, 880, 1.05)]]), {
    ...coldWet(t), rain: 1, traffic: 1, flow: -1, carry: true, speed: 1.3,
    brood: { C1: 1 - prog(t, 33.2, 33.9), D1: 1 - prog(t, 33.0, 33.7) }, water: 0.08,
  }));
  add('S33', 34.18, 35.9, (ctx, t) => nestShot(ctx, t, camAt(t, [[34.18, cam(540, 880, 1.05)], [34.5, cam(540, 760, 1.3)], [35.9, cam(540, 740, 1.38)]]), {
    ...coldWet(t), rain: 1, traffic: 1, flow: -1, carry: true, speed: 1.3, water: 0.1,
    brood: upperFill(t), ring: { M1: eOut(prog(t, 34.64, 34.9)) },
  }));
  add('S34', 35.9, 37.02, (ctx, t) => nestShot(ctx, t, camAt(t, [[35.9, cam(540, 740, 1.38)], [36.2, cam(560, 560, 0.95)], [37.02, cam(560, 560, 0.98)]]), {
    ...coldWet(t), rain: 1, rainFall: 1 - prog(t, 36.1, 36.5), cloudsPart: eIO(prog(t, 36.24, 36.8)), traffic: 0.8, flow: -1, carry: true, water: 0.1,
    sun: eOut(prog(t, 36.42, 36.8)), sunPale: 0.45, sunX: 820, sunY: 210, sunR: 110, brood: upperFill(40), ring: { M1: 1 - prog(t, 35.9, 36.2) },
  }));
  add('S35', 37.02, 37.62, (ctx, t) => nestShot(ctx, t, camAt(t, [[37.02, cam(560, 560, 0.98)], [37.62, cam(560, 570, 1.05)]]), {
    ...coldWet(t), rain: 1, rainFall: 0, cloudsPart: 1, traffic: 0.8, flow: -1, carry: true, water: 0.1,
    sun: 1, sunPale: 0.45, sunX: 820, sunY: 210, sunR: 110, beam: eOut(prog(t, 37.02, 37.24)), brood: upperFill(40),
    glow: { M1: eOut(prog(t, 37.1, 37.36)), M2: eOut(prog(t, 37.16, 37.42)), M3: eOut(prog(t, 37.22, 37.48)) },
  }));
  const warmTop = { M1: 1, M2: 1, M3: 1 };
  add('S36', 37.62, 38.3, (ctx, t) => nestShot(ctx, t, camAt(t, [[37.62, cam(520, 720, 2.0)], [38.3, cam(525, 715, 2.12)]]), {
    ...coldWet(t), rain: 1, rainFall: 0, cloudsPart: 1, traffic: 1, flow: -1, carry: true, speed: 0.8, water: 0.1,
    sun: 1, sunPale: 0.45, sunX: 820, sunY: 210, sunR: 110, beam: 1, brood: upperFill(40), glow: warmTop,
  }));
  add('S37', 38.3, 38.98, (ctx, t) => nestShot(ctx, t, camAt(t, [[38.3, cam(525, 715, 2.12)], [38.56, cam(540, 2050, 0.95)], [38.98, cam(540, 2000, 0.9)]]), {
    ...coldWet(t), rain: 1, rainFall: 0, cloudsPart: 1, traffic: 0.5, water: 0.1, sun: 1, sunPale: 0.45, sunX: 820, sunY: 210, sunR: 110, beam: 1, brood: upperFill(40), glow: warmTop,
  }));
  add('S38', 38.98, 40.64, (ctx, t) => nestShot(ctx, t, camAt(t, [[38.98, cam(540, 2000, 0.9)], [40.64, cam(540, 1880, 0.96)]]), {
    ...coldWet(t), rain: 1, rainFall: 0, cloudsPart: 1, traffic: 0.35, water: 0.1 + 0.68 * eIO(prog(t, 38.98, 39.9)), sun: 1, sunPale: 0.45, sunX: 820, sunY: 210, sunR: 110, beam: 1, brood: upperFill(40), glow: warmTop,
  }));

  // ---------------------------------------------------------------- 6. hot, dry weather: brood moves down
  const hotDry = t => ({ ...NORMAL, surfaceAnts: 0, heat: eOut(prog(t, 40.7, 41.0)), sun: eBack(prog(t, 40.82, 41.06), 1.8), sunX: 540, sunY: 210, sunR: 150 });
  const upperAll = { M1: 1, M2: 1, M3: 1, U1: 1, U2: 1 };
  add('S39', 40.64, 41.42, (ctx, t) => nestShot(ctx, t, camAt(t, [[40.64, cam(540, 1350, 0.66)], [41.42, cam(540, 1330, 0.68)]]), {
    ...hotDry(t), traffic: 0.6, brood: upperAll,
  }));
  add('S40', 41.42, 42.39, (ctx, t) => nestShot(ctx, t, camAt(t, [[41.42, cam(540, 640, 1.35)], [42.39, cam(540, 650, 1.45)]]), {
    ...hotDry(t), traffic: 0.6, brood: upperAll, moundCracks: eOut(prog(t, 41.42, 41.8)), heatSoil: eOut(prog(t, 41.5, 41.95)),
  }));
  add('S41', 42.39, 43.36, (ctx, t) => nestShot(ctx, t, camAt(t, [[42.39, cam(540, 650, 1.45)], [42.62, cam(520, 2060, 1.05)], [43.36, cam(520, 2080, 1.12)]]), {
    ...hotDry(t), traffic: 0.6, brood: upperAll, moundCracks: 1, heatSoil: 1, cool: eOut(prog(t, 42.5, 42.85)), moist: eOut(prog(t, 43.0, 43.2)),
  }));
  add('S42', 43.36, 44.64, (ctx, t) => nestShot(ctx, t, camAt(t, [[43.36, cam(520, 2080, 1.12)], [44.26, cam(520, 2000, 1.0)], [44.64, WIDE, eOut]]), {
    ...hotDry(t), traffic: 0.6, brood: upperAll, moundCracks: 1, heatSoil: 1, cool: 1, moist: 1,
    glow: { D1: eOut(prog(t, 43.36, 43.6)), D2: eOut(prog(t, 43.5, 43.74)), D3: eOut(prog(t, 43.64, 43.88)) }, glowColor: { D1: 'cool', D2: 'cool', D3: 'cool' },
  }));
  add('S43', 44.64, 46.49, (ctx, t) => {
    const up = ['M1', 'M2', 'M3', 'U1', 'U2'];
    const brood = {};
    up.forEach((id, i) => { brood[id] = 1 - prog(t, 44.7 + i * 0.1, 45.3 + i * 0.1); });
    ['D1', 'D2', 'D3'].forEach((id, i) => { brood[id] = eOut(prog(t, 44.96 + i * 0.15, 45.4 + i * 0.15)); });
    nestShot(ctx, t, camAt(t, [[44.64, WIDE], [46.49, cam(540, 1720, 0.8)]]), {
      ...hotDry(t), traffic: 1, flow: 1, carry: true, speed: 1.3, moundCracks: 1, heatSoil: 1, cool: 1, moist: 1, brood,
      glow: { D1: 0.6, D2: 0.6, D3: 0.6 }, glowColor: { D1: 'cool', D2: 'cool', D3: 'cool' },
    });
  });

  // ---------------------------------------------------------------- 7. Workers move the brood ... nursery shifting ... not one fixed room
  add('S44', 46.49, 47.64, tunnelCloseUp);
  const broodMove = { C1: 1, U2: 1, D1: 1 };
  add('S45', 47.64, 48.4, (ctx, t) => nestShot(ctx, t, camAt(t, [[47.64, WIDE], [48.4, cam(540, 1470, 0.64)]]), {
    ...NORMAL, traffic: 1, carry: true, brood: broodMove,
  }));
  add('S46', 48.4, 49.02, (ctx, t) => nestShot(ctx, t, cam(540, 1460, 0.65), {
    ...NORMAL, traffic: 1, carry: true, flow: -1, brood: broodMove, rain: eOut(prog(t, 48.42, 48.6)), rainFall: prog(t, 48.5, 48.7), cold: 0.6, wind: 0.4, surfaceAnts: 0,
  }));
  add('S47', 49.02, 50.26, (ctx, t) => {
    const sw = prog(t, 49.02, 49.16);
    nestShot(ctx, t, camAt(t, [[49.02, cam(540, 1460, 0.65)], [50.26, cam(600, 1260, 0.86)]]), {
      ...NORMAL, traffic: 1, carry: true, flow: 1, brood: broodMove, rain: 1 - sw, rainFall: 1 - sw, cold: 0.6 * (1 - sw), surfaceAnts: 0,
      sun: eBack(prog(t, 49.02, 49.22), 1.8), sunX: 860, sunY: 220, heat: 0.85 * sw, heatSoil: 0.6 * sw, cool: 0.6 * sw,
    });
  });
  const hop = (t, path) => {
    // path: [[time, chamberId], ...]; returns frame position and the brood amounts.
    let from = path[0][1];
    let to = path[0][1];
    let k = 1;
    for (let i = 1; i < path.length; i += 1) {
      if (t >= path[i][0]) { from = path[i][1]; to = path[i][1]; k = 1; }
      if (t >= path[i][0] && t < path[i][0] + 0.26) { from = path[i - 1][1]; to = path[i][1]; k = eIO(prog(t, path[i][0], path[i][0] + 0.26)); }
    }
    const a = CHAMBERS[from];
    const b = CHAMBERS[to];
    const lift = Math.sin(Math.PI * k) * 60;
    const frame = { x: lerp(a.x, b.x, k), y: lerp(a.y, b.y, k) - 8 - lift, w: lerp(a.rx, b.rx, k) * 2.7, h: lerp(a.ry, b.ry, k) * 3.6, k: 1 };
    const brood = { [from]: 1 - k };
    brood[to] = Math.max(brood[to] ?? 0, k);
    return { frame, brood };
  };
  add('S48', 50.26, 51.06, (ctx, t) => {
    const c = CHAMBERS.U2;
    nestShot(ctx, t, camAt(t, [[50.26, cam(c.x - 40, c.y, 1.9)], [51.06, cam(c.x - 40, c.y, 2.02)]]), {
      ...NORMAL, traffic: 0.6, brood: { U2: 1 }, frame: { x: c.x, y: c.y - 8, w: c.rx * 2.7, h: c.ry * 3.6, k: eOut(prog(t, 50.26, 50.46)) },
    });
  });
  add('S49', 51.06, 51.94, (ctx, t) => {
    const { frame, brood } = hop(t, [[50, 'U2'], [51.06, 'C2']]);
    nestShot(ctx, t, camAt(t, [[51.06, cam(CHAMBERS.U2.x - 40, CHAMBERS.U2.y, 2.02)], [51.5, cam(700, 1240, 1.3)], [51.94, cam(700, 1300, 1.25)]]), {
      ...NORMAL, traffic: 0.8, carry: true, flow: 1, brood, frame,
    });
  });
  add('S50', 51.94, 53.32, (ctx, t) => {
    const { frame, brood } = hop(t, [[50, 'C2'], [51.94, 'D1'], [52.3, 'M1'], [52.88, 'D2']]);
    nestShot(ctx, t, camAt(t, [[51.94, cam(700, 1300, 1.25)], [52.2, WIDE, eOut], [53.32, cam(540, 1470, 0.64)]]), {
      ...NORMAL, traffic: 0.9, carry: true, brood, frame,
    });
  });
  add('S51', 53.32, 57.69, (ctx, t) => {
    slide(ctx, t, 53.32, 0.2, c => {
      const { frame, brood } = hop(53.32, [[50, 'C2'], [51.94, 'D1'], [52.3, 'M1'], [52.88, 'D2']]);
      nestShot(c, t, cam(540, 1470, 0.64), { ...NORMAL, traffic: 0.9, carry: true, brood, frame });
    }, c => fixedRoom(c, t), 1);
  });

  // ---------------------------------------------------------------- 8. the nest you see above ground ... surface looks quiet
  add('S55', 57.69, 60.66, (ctx, t) => {
    const camera = camAt(t, [[57.69, cam(540, 960, 1.0)], [58.56, cam(520, 990, 1.14)], [59.47, cam(520, 940, 1.32)], [60.66, cam(520, 975, 1.22)]]);
    const lensK = eBack(prog(t, 60.22, 60.5), 1.3);
    const lens = t >= 60.22 ? {
      x: lerp(1400, MOUND.x, lensK), y: lerp(700, 960, lensK), r: 230, angle: lerp(0.7, -0.16, eOut(prog(t, 60.22, 60.5))),
      xray: (c) => {
        c.save();
        nestToYard(c);
        nest.draw(c, t, { mound: 1, traffic: 0.6, surfaceAnts: 0, brood: { D2: 1 } });
        c.restore();
      },
    } : null;
    yardShot(ctx, t, camera, {
      mound: prog(t, 57.96, 58.2), trace: prog(t, 58.56, 58.95), lens,
    }, (c) => questionMark(c, texture, MOUND.x, 700, 160, prog(t, 59.47, 59.68) * (1 - prog(t, 60.3, 60.5))));
  });
  add('S59', 60.66, 61.74, (ctx, t) => nestShot(ctx, t, camAt(t, [[60.66, cam(540, 690, 1.35)], [61.02, cam(740, 2030, 1.45)], [61.74, cam(760, 2050, 1.6)]]), {
    ...NORMAL, surfaceAnts: 0, traffic: 0.7, brood: { D2: 1 }, ring: { D2: eOut(prog(t, 61.08, 61.3)) },
  }));
  add('S60', 61.74, 62.73, (ctx, t) => nestShot(ctx, t, camAt(t, [[61.74, cam(772, 2060, 2.15)], [62.73, cam(772, 2060, 2.3)]]), {
    ...NORMAL, surfaceAnts: 0, traffic: 0.7, brood: { D2: 1 }, ring: { D2: 1 - prog(t, 62.2, 62.6) }, glow: { D2: 0.6 },
  }));
  const busyAll = { C1: 1, C2: 1, U1: 1, D1: 1, D3: 1 };
  const quiet = { mound: 0, surfaceAnts: 0, traffic: 1, speed: 1.6, busy: busyAll, brood: { D2: 1, C1: 0.7 } };
  add('S61', 62.73, 65.82, (ctx, t) => nestShot(ctx, t, camAt(t, [[62.73, cam(560, 1300, 1.0)], [64.26, cam(560, 1290, 1.08)], [65.06, cam(560, 1280, 1.0)], [65.82, cam(560, 1280, 0.98)]]), {
    ...quiet, cover: eIO(prog(t, 65.06, 65.46)),
  }));
  add('S64', 65.82, 68.11, (ctx, t) => nestShot(ctx, t, camAt(t, [[65.82, cam(560, 1280, 0.98)], [66.3, cam(540, 650, 1.2)], [68.11, cam(560, 610, 1.5)]]), {
    ...quiet, cover: 1, fairClouds: 1,
  }));

  // ---------------------------------------------------------------- 9. For a homeowner ... developing young.
  add('S66', 68.11, 75.64, (ctx, t) => {
    const camera = camAt(t, [[68.11, cam(540, 960, 1.0)], [69.01, cam(600, 920, 1.08)], [70.58, cam(560, 820, 1.22)], [71.64, cam(560, 840, 1.3)],
      [72.0, cam(560, 980, 1.12)], [73.56, cam(540, 1010, 1.22)], [74.25, cam(480, 1040, 1.2)], [75.64, cam(420, 1060, 1.32)]]);
    const walkIn = eOut(prog(t, 68.11, 68.9));
    const px = lerp(1380, 790, walkIn);
    const arm = t >= 72.6 ? 'chin' : t >= 70.62 ? 'scratch' : 'down';
    const lensOn = t >= 72.6;
    const lensK = eOut(prog(t, 72.6, 72.8));
    const xrayK = prog(t, 73.56, 73.8);
    const lens = lensOn ? {
      x: lerp(-300, MOUND.x + 30, lensK), y: lerp(1300, 1040, lensK), r: 200, angle: -0.16,
      xray: xrayK > 0 ? (c) => {
        c.save();
        c.globalAlpha = xrayK;
        c.beginPath();
        c.rect(-400, MOUND.base - 20, 2000, 1500);
        c.clip();
        nestToYard(c);
        nest.draw(c, t, { mound: 0, traffic: 1, surfaceAnts: 0, brood: { C1: 1 }, busy: { U1: 1, U2: 1 } });
        c.restore();
      } : null,
    } : null;
    const needle = t < 74.9 ? -0.9 : t < 75.4 ? 1.3 * Math.sin((t - 74.9) * 28) : 1.3 * Math.sin(0.5 * 28) * Math.exp(-(t - 75.4) * 8);
    yardShot(ctx, t, camera, { mound: 0, dashed: prog(t, 72.74, 73.0), lens }, (c) => {
      gauge(c, texture, 190, 1330, 0.85, needle, prog(t, 74.48, 74.72));
      questionMark(c, texture, 190, 940, 96, prog(t, 75.3, 75.5));
      person(c, texture, px, 1300, 0.55, {
        walk: walkIn < 1 ? 1 : 0, phase: 590 * walkIn / 60, face: -1, arm, scratch: Math.sin(t * 14),
        look: t > 69.0 && t < 72.6 ? -0.12 : 0.08,
      });
      // Thought bubble: a mound, which turns into a dashed outline, then a question mark; the picture blows away.
      const bubbleK = prog(t, 69.01, 69.28) * (1 - prog(t, 72.3, 72.5));
      thoughtBubble(c, texture, 520, 520, 440, 300, bubbleK, (b) => {
        const fly = eIn(prog(t, 71.8, 72.4));
        b.save();
        b.translate(-260 * fly, -260 * fly);
        b.rotate(-1.2 * fly);
        b.scale(1 - 0.5 * fly, 1 - 0.5 * fly);
        const solid = prog(t, 69.94, 70.1) * (1 - prog(t, 70.3, 70.45));
        const dash = prog(t, 70.3, 70.5);
        if (solid > 0) {
          b.save();
          b.globalAlpha = solid;
          b.translate(0, 70);
          b.scale(0.42 * eBack(prog(t, 69.94, 70.14), 2), 0.42 * eBack(prog(t, 69.94, 70.14), 2));
          b.translate(-MOUND.x, -MOUND.base);
          cut(b, smoothPath([...yard.outline.points.filter((_, i) => i % 3 === 0), [MOUND.x + 290, MOUND.base], [MOUND.x - 290, MOUND.base]], true), '#B57553', texture, 6);
          b.restore();
        }
        if (dash > 0) {
          b.save();
          b.translate(0, 70);
          b.scale(0.42, 0.42);
          b.translate(-MOUND.x, -MOUND.base);
          b.setLineDash([30, 22]);
          b.lineWidth = 16;
          b.lineCap = 'round';
          b.strokeStyle = C.purple;
          b.beginPath();
          yard.outline.slice(dash).forEach(([x, y], i) => (i ? b.lineTo(x, y) : b.moveTo(x, y)));
          b.stroke();
          b.restore();
        }
        b.restore();
        questionMark(b, texture, 120, -40, 110, prog(t, 70.58, 70.8) * (1 - prog(t, 71.8, 72.0)));
      });
    });
  });
  const endState = { mound: 0, surfaceAnts: 0, traffic: 1, busy: { U1: 1, C2: 1, D1: 1, D3: 1 }, brood: { C1: 1, D2: 1 } };
  add('S75', 75.64, 80, (ctx, t) => nestShot(ctx, t, camAt(t, [[75.64, WIDE], [77.14, cam(540, 1440, 0.67)], [77.6, cam(400, 1210, 2.05)], [79.3, cam(395, 1215, 2.3)]]), endState, (c) => {
    questionMark(c, texture, 540, 1360, 230, prog(t, 76.46, 76.7) * (1 - prog(t, 77.2, 77.4)));
    questionMark(c, texture, 545, 1120, 90, prog(t, 77.98, 78.2));
  }));

  shots.sort((a, b) => a.start - b.start);
  return {
    shots,
    blurWindows: [[10.52, 10.72], [12.99, 13.25], [15.0, 15.36], [30.08, 30.3], [38.3, 38.56], [42.39, 42.62], [44.26, 44.64], [60.66, 61.02], [77.14, 77.6]].map(w => [...w, 9, 1 / 60]),
    draw(ctx, t) {
      const shot = shots.findLast(s => t >= s.start) ?? shots[0];
      shot.draw(ctx, t);
    },
  };
}
