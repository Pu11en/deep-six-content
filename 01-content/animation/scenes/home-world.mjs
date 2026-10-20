// Home sets for episode D6-01096ba333e3, cut-paper style C.
//  createSink: the cabinet under a kitchen sink, front view. Cracks, small gaps, a warm supply line,
//              a dripping trap and a damp floor. World units match a 1080 x 1920 frame at zoom 1.
//  createMacro: the same cabinet floor seen very close, where an egg case lies near a crack.
//  createFloorTop: the cabinet floor seen from above, for the cockroach portrait.
// Every frame is a pure function of time. The fire-ant sets are not used or changed.
import {
  C, Path2D, clamp, lerp, eOut, eIO, eBack, hash, mix,
  cut, polyPath, smoothPath, ovalPath, capsulePath, bandPath, tornLine, puff,
} from './paper-kit.mjs';

const TAU = Math.PI * 2;
export const SINK = {
  floor: 1060, // where the back wall meets the cabinet floor
  front: 1360, // front lip of the cabinet floor
  crack: [[268, 1074], [292, 1118], [276, 1160], [312, 1206], [300, 1250], [338, 1300], [326, 1352]],
  gap: { x0: 760, x1: 1010, y: 1056 }, // slit under the back wall
  pipeGap: { x: 830, y: 700, r: 58 }, // gap around the drain arm where it enters the wall
  hot: { x: 250, y: 880 },
  cold: { x: 830, y: 900 },
  trapNut: { x: 560, y: 610 },
  drip: { x: 548, y: 1150 },
};
const W0 = -320;
const W1 = 1400;

function jag(points, amp, seed) {
  return points.map(([x, y], i) => [x + (hash(seed + i * 3.1) - 0.5) * amp, y + (hash(seed + i * 5.7) - 0.5) * amp]);
}

export function createSink(texture) {
  const planks = [];
  for (let x = W0; x < W1; x += 170) planks.push(x);
  const grain = Array.from({ length: 60 }, (_, i) => [W0 + hash(i + 3) * (W1 - W0), 60 + hash(i + 9) * 950, 40 + hash(i + 5) * 120, hash(i + 1)]);
  const floorBits = Array.from({ length: 34 }, (_, i) => [W0 + hash(i + 50) * (W1 - W0), SINK.floor + 30 + hash(i + 70) * 270, 3 + hash(i + 80) * 6, hash(i + 90) * 3]);
  const crackPath = SINK.crack;

  function back(ctx, t, s = {}) {
    // Back wall: warm wood panels.
    cut(ctx, polyPath([[W0, -400], [W1, -400], [W1, SINK.floor + 10], [W0, SINK.floor + 10]]), '#B98A5C', texture, 0);
    ctx.save();
    for (const x of planks) {
      ctx.fillStyle = 'rgba(70,40,24,0.28)';
      ctx.fillRect(x, -400, 6, SINK.floor + 410);
      ctx.fillStyle = 'rgba(255,230,190,0.12)';
      ctx.fillRect(x + 6, -400, 4, SINK.floor + 410);
    }
    ctx.strokeStyle = 'rgba(90,55,32,0.18)';
    ctx.lineWidth = 3;
    ctx.lineCap = 'round';
    for (const [x, y, l, k] of grain) {
      ctx.beginPath();
      ctx.moveTo(x, y);
      ctx.bezierCurveTo(x + 6 * (k - 0.5), y + l * 0.3, x - 6 * (k - 0.5), y + l * 0.7, x + 3, y + l);
      ctx.stroke();
    }
    // Shadow under the sink.
    const shade = ctx.createLinearGradient(0, -100, 0, 700);
    shade.addColorStop(0, 'rgba(40,24,18,0.5)');
    shade.addColorStop(1, 'rgba(40,24,18,0)');
    ctx.fillStyle = shade;
    ctx.fillRect(W0, -400, W1 - W0, 1100);
    ctx.restore();
    // Baseboard strip with the small gap beneath its right end.
    cut(ctx, polyPath([[W0, SINK.floor - 70], [W1, SINK.floor - 70], [W1, SINK.floor], [W0, SINK.floor]]), '#A9784D', texture, 5);
    const g = SINK.gap;
    cut(ctx, polyPath(jag([[g.x0, g.y - 4], [g.x0 + 60, g.y - 12], [g.x0 + 140, g.y - 16], [g.x1 - 60, g.y - 13], [g.x1, g.y - 6], [g.x1, g.y + 6], [g.x0, g.y + 6]], 3, 11)), '#1F130E', null, 0);
    // Cabinet floor plane, seen from slightly above.
    cut(ctx, polyPath([[W0, SINK.floor], [W1, SINK.floor], [W1 + 120, SINK.front], [W0 - 120, SINK.front]]), '#C89C6A', texture, 4);
    ctx.save();
    ctx.strokeStyle = 'rgba(90,55,32,0.2)';
    ctx.lineWidth = 3;
    for (let i = 0; i < 9; i += 1) {
      const x = W0 + i * 210;
      ctx.beginPath();
      ctx.moveTo(x, SINK.floor);
      ctx.lineTo(x + (x - 540) * 0.16, SINK.front);
      ctx.stroke();
    }
    ctx.restore();
    for (const [x, y, r, a] of floorBits) cut(ctx, ovalPath(x, y, r, r * 0.6, a), '#A47A50', null, 0);
    // Damp patch spreading on the floor under the drip.
    const damp = s.damp ?? 0;
    if (damp > 0.01) {
      const d = eOut(damp);
      ctx.save();
      ctx.globalAlpha = 0.85;
      cut(ctx, smoothPath(jag([[SINK.drip.x - 210 * d, SINK.drip.y + 6], [SINK.drip.x - 120 * d, SINK.drip.y - 30 * d], [SINK.drip.x + 40 * d, SINK.drip.y - 38 * d], [SINK.drip.x + 200 * d, SINK.drip.y - 10 * d], [SINK.drip.x + 170 * d, SINK.drip.y + 40 * d], [SINK.drip.x - 20 * d, SINK.drip.y + 56 * d], [SINK.drip.x - 180 * d, SINK.drip.y + 40 * d]], 10 * d, 21)), '#8E6440', texture, 0);
      ctx.fillStyle = `rgba(200,230,240,${0.35 * d})`;
      ctx.fill(ovalPath(SINK.drip.x - 40 * d, SINK.drip.y - 4, 90 * d, 12 * d, -0.05));
      ctx.restore();
    }
    // Crack running across the floor boards.
    const crackK = s.crack ?? 1;
    ctx.save();
    ctx.lineJoin = 'round';
    ctx.lineCap = 'round';
    ctx.strokeStyle = '#22150F';
    ctx.lineWidth = 15;
    ctx.beginPath();
    crackPath.forEach(([x, y], i) => (i ? ctx.lineTo(x, y) : ctx.moveTo(x, y)));
    ctx.stroke();
    ctx.strokeStyle = 'rgba(255,225,180,0.25)';
    ctx.lineWidth = 3;
    ctx.beginPath();
    crackPath.forEach(([x, y], i) => (i ? ctx.lineTo(x + 9, y + 2) : ctx.moveTo(x + 9, y + 2)));
    ctx.stroke();
    ctx.restore();
    if (crackK < 1) return;
  }

  // Sink bowl, drain, trap, supply lines.
  function plumbing(ctx, t, s = {}) {
    // Counter edge and bowl underside.
    cut(ctx, polyPath([[W0, -420], [W1, -420], [W1, -150], [W0, -150]]), '#6E4A33', texture, 10);
    cut(ctx, smoothPath([[110, -170], [970, -170], [930, 120], [820, 300], [540, 360], [260, 300], [150, 120]]), '#E4DED2', texture, 14);
    cut(ctx, smoothPath([[200, -150], [520, -150], [380, 100], [270, 220], [210, 80]]), '#F2EEE6', texture, 2);
    const pipe = '#DCD9CF';
    const pipeHi = '#F4F2EC';
    const pipeDark = '#B9B5A8';
    // Supply lines and shutoff valves.
    const warm = s.warm ?? 0;
    for (const [v, handle, hi] of [[SINK.hot, '#C8553D', warm], [SINK.cold, '#5D7FA3', 0]]) {
      if (hi > 0.01) {
        const glow = ctx.createRadialGradient(v.x, v.y - 200, 20, v.x, v.y - 200, 420);
        glow.addColorStop(0, `rgba(255,170,80,${0.55 * hi})`);
        glow.addColorStop(1, 'rgba(255,170,80,0)');
        ctx.fillStyle = glow;
        ctx.fillRect(v.x - 460, v.y - 660, 920, 920);
      }
      cut(ctx, ovalPath(v.x, v.y, 46, 46), '#C9C4B8', texture, 4);
      cut(ctx, capsulePath([v.x, v.y], [v.x, v.y - 70], 18, 18), '#C7C2B6', texture, 4);
      cut(ctx, smoothPath([[v.x - 34, v.y - 60], [v.x + 34, v.y - 60], [v.x + 30, v.y - 120], [v.x - 30, v.y - 120]]), '#BDB8AC', texture, 6);
      cut(ctx, ovalPath(v.x + 46, v.y - 92, 34, 22, 0.1), handle, texture, 5);
      // Flexible line up to the faucet.
      ctx.save();
      ctx.lineCap = 'round';
      ctx.lineWidth = 22;
      ctx.strokeStyle = hi > 0.01 ? mix('#B8B2A5', '#E69A5A', hi * 0.6) : '#B8B2A5';
      ctx.beginPath();
      ctx.moveTo(v.x, v.y - 120);
      ctx.bezierCurveTo(v.x, v.y - 360, v.x + (v === SINK.hot ? 120 : -120), v.y - 470, v.x + (v === SINK.hot ? 160 : -160), 310);
      ctx.stroke();
      ctx.strokeStyle = 'rgba(255,255,255,0.35)';
      ctx.lineWidth = 5;
      ctx.setLineDash([10, 12]);
      ctx.stroke();
      ctx.restore();
    }
    // Heat ripples rising off the warm line.
    if (warm > 0.01) {
      ctx.save();
      ctx.lineCap = 'round';
      for (let i = 0; i < 4; i += 1) {
        const k = ((t * 0.7 + i / 4) % 1);
        const y0 = SINK.hot.y - 160 - k * 380;
        ctx.globalAlpha = warm * Math.sin(Math.PI * k) * 0.9;
        ctx.strokeStyle = i % 2 ? '#F2A93B' : '#F7C548';
        ctx.lineWidth = 12;
        ctx.beginPath();
        for (let j = 0; j <= 12; j += 1) {
          const y = y0 - j * 12;
          const x = SINK.hot.x - 120 + i * 70 + Math.sin(j * 0.9 + t * 6 + i) * 14;
          if (j) ctx.lineTo(x, y); else ctx.moveTo(x, y);
        }
        ctx.stroke();
      }
      ctx.restore();
    }
    // Drain tailpiece, slip nut and trap.
    cut(ctx, polyPath([[514, 330], [586, 330], [586, 760], [514, 760]]), pipe, texture, 8);
    cut(ctx, polyPath([[524, 330], [540, 330], [540, 760], [524, 760]]), pipeHi, texture, 0);
    cut(ctx, polyPath([[498, SINK.trapNut.y - 24], [602, SINK.trapNut.y - 24], [602, SINK.trapNut.y + 24], [498, SINK.trapNut.y + 24]]), pipeDark, texture, 6);
    ctx.save();
    ctx.lineCap = 'butt';
    ctx.strokeStyle = 'rgba(57,35,27,0.22)';
    ctx.lineWidth = 76;
    ctx.beginPath();
    ctx.moveTo(556, 760);
    ctx.bezierCurveTo(556, 930, 760, 930, 760, 760);
    ctx.lineTo(760, 720);
    ctx.lineTo(SINK.pipeGap.x - 20, 720);
    ctx.stroke();
    ctx.strokeStyle = pipe;
    ctx.lineWidth = 72;
    ctx.beginPath();
    ctx.moveTo(550, 756);
    ctx.bezierCurveTo(550, 920, 754, 920, 754, 756);
    ctx.lineTo(754, 712);
    ctx.lineTo(SINK.pipeGap.x - 20, 712);
    ctx.stroke();
    ctx.strokeStyle = pipeHi;
    ctx.lineWidth = 14;
    ctx.beginPath();
    ctx.moveTo(530, 760);
    ctx.bezierCurveTo(530, 880, 640, 905, 700, 880);
    ctx.stroke();
    ctx.restore();
    cut(ctx, polyPath([[500, 744], [600, 744], [600, 784], [500, 784]]), pipeDark, texture, 5);
    // Where the arm enters the wall: an escutcheon pulled away, leaving a dark gap ring.
    const g = SINK.pipeGap;
    cut(ctx, ovalPath(g.x + 6, g.y + 10, g.r + 12, g.r + 12), '#1F130E', null, 0);
    cut(ctx, ovalPath(g.x + 22, g.y + 24, g.r + 4, g.r - 4, 0.3), '#D2CEC4', texture, 6);
    cut(ctx, ovalPath(g.x + 22, g.y + 24, g.r - 26, g.r - 30, 0.3), '#2C1C14', null, 0);
    cut(ctx, polyPath([[g.x - 120, 676], [g.x + 18, 676], [g.x + 30, 748], [g.x - 120, 748]]), pipe, texture, 6);
    cut(ctx, polyPath([[g.x - 120, 680], [g.x + 10, 680], [g.x + 12, 694], [g.x - 120, 694]]), pipeHi, texture, 0);
    // Drops forming on the slip nut and falling to the floor.
    const drip = s.drip ?? 0;
    if (drip > 0.01) {
      ctx.save();
      ctx.globalAlpha = drip;
      for (let i = 0; i < 3; i += 1) {
        const k = ((t * 1.25 + i / 3) % 1);
        const fall = eIO(clamp((k - 0.35) / 0.5));
        const y = lerp(SINK.trapNut.y + 30, SINK.drip.y - 6, fall);
        const r = 14 * (k < 0.35 ? k / 0.35 : 1);
        if (k < 0.86) cut(ctx, smoothPath([[SINK.drip.x, y - r * 1.9], [SINK.drip.x + r, y], [SINK.drip.x, y + r], [SINK.drip.x - r, y]]), '#9FD0E6', texture, 2);
        else {
          const sp = (k - 0.86) / 0.14;
          for (const dx of [-1, 1]) cut(ctx, ovalPath(SINK.drip.x + dx * 40 * sp, SINK.drip.y - 30 * Math.sin(Math.PI * sp), 7, 5), '#9FD0E6', null, 0);
        }
      }
      cut(ctx, ovalPath(SINK.trapNut.x - 6, SINK.trapNut.y + 26, 12, 9), '#9FD0E6', texture, 1);
      ctx.restore();
    }
  }

  function frame(ctx) {
    // Side panels and the cabinet face frame at the edges.
    cut(ctx, polyPath([[W0 - 400, -500], [W0 + 40, -500], [W0 + 40, SINK.floor], [W0 - 80, SINK.front + 200], [W0 - 400, SINK.front + 200]]), '#8E6442', texture, 10);
    cut(ctx, polyPath([[W1 - 40, -500], [W1 + 400, -500], [W1 + 400, SINK.front + 200], [W1 + 80, SINK.front + 200], [W1 - 40, SINK.floor]]), '#8E6442', texture, 10);
    cut(ctx, bandPath(W0 - 500, W1 + 500, SINK.front, SINK.front + 900, 0, 4), '#7A5236', texture, 12);
    cut(ctx, polyPath([[W0 - 500, SINK.front], [W1 + 500, SINK.front], [W1 + 500, SINK.front + 26], [W0 - 500, SINK.front + 26]]), '#94683F', texture, 2);
  }

  return {
    draw(ctx, t, s = {}) {
      back(ctx, t, s);
      plumbing(ctx, t, s);
      if (s.extra) s.extra(ctx);
      frame(ctx);
    },
    back, plumbing, frame,
  };
}

// Lime outline traced along a path; k 0..1 draws it from the start.
export function tracePath(ctx, points, k, width = 12) {
  if (k <= 0.01) return;
  const total = points.slice(1).reduce((a, p, i) => a + Math.hypot(p[0] - points[i][0], p[1] - points[i][1]), 0);
  let left = total * clamp(k);
  ctx.save();
  ctx.lineCap = 'round';
  ctx.lineJoin = 'round';
  for (const [color, w, d] of [['rgba(30,27,34,0.3)', width + 4, 4], [C.lime, width, 0]]) {
    let rem = left;
    ctx.strokeStyle = color;
    ctx.lineWidth = w;
    ctx.beginPath();
    ctx.moveTo(points[0][0] + d, points[0][1] + d);
    for (let i = 1; i < points.length && rem > 0; i += 1) {
      const seg = Math.hypot(points[i][0] - points[i - 1][0], points[i][1] - points[i - 1][1]);
      const f = Math.min(1, rem / seg);
      ctx.lineTo(lerp(points[i - 1][0], points[i][0], f) + d, lerp(points[i - 1][1], points[i][1], f) + d);
      rem -= seg;
    }
    ctx.stroke();
  }
  ctx.restore();
}

// ------------------------------------------------------------------ macro: the cabinet floor up close
export const MACRO_FLOOR = 1150;
export function createMacro(texture) {
  const crumbs = Array.from({ length: 40 }, (_, i) => [-900 + hash(i + 11) * 2900, MACRO_FLOOR + 40 + hash(i + 23) * 700, 6 + hash(i + 5) * 16, hash(i + 2) * 3]);
  const grain = Array.from({ length: 40 }, (_, i) => [-900 + hash(i + 31) * 2900, MACRO_FLOOR + 30 + hash(i + 41) * 700, 120 + hash(i + 51) * 260]);
  const crackTop = tornLine(-900, 2000, MACRO_FLOOR + 330, 26, 77, 60);
  const crackBottom = tornLine(-900, 2000, MACRO_FLOOR + 380, 20, 78, 60).reverse();
  return {
    draw(ctx, t, s = {}) {
      // Far back wall in deep shadow, huge planks, the dark gap under the baseboard.
      cut(ctx, polyPath([[-1400, -900], [2500, -900], [2500, MACRO_FLOOR], [-1400, MACRO_FLOOR]]), '#8C6242', texture, 0);
      ctx.save();
      for (let x = -1400; x < 2500; x += 520) {
        ctx.fillStyle = 'rgba(50,30,20,0.3)';
        ctx.fillRect(x, -900, 16, MACRO_FLOOR + 900);
      }
      const warmth = ctx.createRadialGradient(300, 500, 60, 300, 500, 1100);
      warmth.addColorStop(0, 'rgba(255,205,140,0.3)');
      warmth.addColorStop(1, 'rgba(255,205,140,0)');
      ctx.fillStyle = warmth;
      ctx.fillRect(-1400, -900, 3900, 2100);
      ctx.restore();
      cut(ctx, polyPath([[-1400, MACRO_FLOOR - 260], [2500, MACRO_FLOOR - 260], [2500, MACRO_FLOOR - 40], [-1400, MACRO_FLOOR - 40]]), '#9C6E48', texture, 8);
      cut(ctx, polyPath([[-1400, MACRO_FLOOR - 40], [2500, MACRO_FLOOR - 40], [2500, MACRO_FLOOR], [-1400, MACRO_FLOOR]]), '#20140F', null, 0);
      // Floor board top.
      cut(ctx, bandPath(-1400, 2500, MACRO_FLOOR, MACRO_FLOOR + 1400, 0, 9), '#C49766', texture, 6);
      ctx.save();
      ctx.strokeStyle = 'rgba(110,70,40,0.22)';
      ctx.lineWidth = 5;
      ctx.lineCap = 'round';
      for (const [x, y, l] of grain) {
        ctx.beginPath();
        ctx.moveTo(x, y);
        ctx.quadraticCurveTo(x + l * 0.5, y - 8, x + l, y + 4);
        ctx.stroke();
      }
      ctx.restore();
      for (const [x, y, r, a] of crumbs) cut(ctx, ovalPath(x, y, r, r * 0.55, a), '#A87C52', texture, 2);
      // A crack in the board, the kind of place egg cases are left.
      if (s.crack !== 0) {
        cut(ctx, polyPath([...crackTop, ...crackBottom]), '#22150F', null, 0);
        ctx.save();
        ctx.strokeStyle = 'rgba(255,225,180,0.25)';
        ctx.lineWidth = 4;
        ctx.beginPath();
        crackBottom.forEach(([x, y], i) => (i ? ctx.lineTo(x, y + 3) : ctx.moveTo(x, y + 3)));
        ctx.stroke();
        ctx.restore();
      }
      // Dust motes drifting in the warm air.
      ctx.save();
      for (let i = 0; i < 22; i += 1) {
        const x = -400 + ((hash(i + 40) * 2200 + t * (16 + 12 * hash(i))) % 2200);
        const y = MACRO_FLOOR - 60 - ((hash(i + 70) * 1300 + t * (20 + 16 * hash(i + 5))) % 1300);
        ctx.globalAlpha = 0.2 + 0.3 * (0.5 + 0.5 * Math.sin(t * 3 + i));
        ctx.fillStyle = '#F6DFA8';
        ctx.beginPath();
        ctx.arc(x, y, 3 + 5 * hash(i + 9), 0, TAU);
        ctx.fill();
      }
      ctx.restore();
    },
  };
}

// ------------------------------------------------------------------ the cabinet floor from above
export function createFloorTop(texture) {
  const boards = [];
  for (let y = -1200; y < 3200; y += 300) boards.push(y);
  const knots = Array.from({ length: 12 }, (_, i) => [-600 + hash(i + 3) * 2300, -1200 + hash(i + 7) * 4400, 30 + hash(i + 1) * 40]);
  return {
    draw(ctx, t, s = {}) {
      cut(ctx, polyPath([[-1400, -1400], [2600, -1400], [2600, 3400], [-1400, 3400]]), '#C29464', texture, 0);
      ctx.save();
      boards.forEach((y, i) => {
        ctx.fillStyle = i % 2 ? 'rgba(120,80,45,0.08)' : 'rgba(255,230,190,0.06)';
        ctx.fillRect(-1400, y, 4000, 300);
        ctx.fillStyle = 'rgba(70,40,24,0.35)';
        ctx.fillRect(-1400, y, 4000, 8);
        const off = (i * 730) % 1600 - 800;
        ctx.fillRect(off, y, 8, 300);
        ctx.fillRect(off + 1500, y, 8, 300);
      });
      ctx.strokeStyle = 'rgba(110,70,40,0.2)';
      ctx.lineWidth = 4;
      for (let i = 0; i < 60; i += 1) {
        const y = -1200 + hash(i + 200) * 4400;
        const x = -1200 + hash(i + 300) * 3600;
        ctx.beginPath();
        ctx.moveTo(x, y);
        ctx.quadraticCurveTo(x + 200, y - 10, x + 420, y + 6);
        ctx.stroke();
      }
      for (const [x, y, r] of knots) {
        ctx.strokeStyle = 'rgba(110,70,40,0.25)';
        ctx.beginPath();
        ctx.ellipse(x, y, r * 2, r * 0.8, 0, 0, TAU);
        ctx.stroke();
      }
      ctx.restore();
      // The crack: a dark split between two boards.
      const crack = tornLine(-1400, 2600, s.crackY ?? 1500, 14, 91, 50);
      const crack2 = tornLine(-1400, 2600, (s.crackY ?? 1500) + 34, 10, 92, 50).reverse();
      cut(ctx, polyPath([...crack, ...crack2]), '#22150F', null, 0);
    },
  };
}

// Dim the frame and light a flashlight cone from (x0, y0) toward (x1, y1), in screen space.
// beam 0..1 lights the cone; dim 0..1 darkens everything outside it.
export function flashlightBeam(ctx, x0, y0, x1, y1, spread, beam, dim = 0) {
  if (beam <= 0.01 && dim <= 0.01) return;
  const a = Math.atan2(y1 - y0, x1 - x0);
  const len = Math.hypot(x1 - x0, y1 - y0) * 1.5;
  const r0 = 46;
  const r1 = len * Math.tan(spread);
  const p = [
    [x0 + Math.cos(a + Math.PI / 2) * r0, y0 + Math.sin(a + Math.PI / 2) * r0],
    [x0 + Math.cos(a) * len + Math.cos(a + Math.PI / 2) * r1, y0 + Math.sin(a) * len + Math.sin(a + Math.PI / 2) * r1],
    [x0 + Math.cos(a) * len + Math.cos(a - Math.PI / 2) * r1, y0 + Math.sin(a) * len + Math.sin(a - Math.PI / 2) * r1],
    [x0 + Math.cos(a - Math.PI / 2) * r0, y0 + Math.sin(a - Math.PI / 2) * r0],
  ];
  ctx.save();
  ctx.setTransform(1, 0, 0, 1, 0, 0);
  const shade = new Path2D();
  shade.rect(-50, -50, 1180, 2020);
  if (beam > 0.01) {
    shade.moveTo(p[0][0], p[0][1]);
    p.slice(1).forEach(([x, y]) => shade.lineTo(x, y));
    shade.closePath();
  }
  ctx.fillStyle = `rgba(22,14,18,${0.62 * dim})`;
  ctx.fill(shade, 'evenodd');
  if (beam > 0.01) {
    const g = ctx.createLinearGradient(x0, y0, x0 + Math.cos(a) * len, y0 + Math.sin(a) * len);
    g.addColorStop(0, `rgba(255,246,205,${0.5 * beam})`);
    g.addColorStop(0.6, `rgba(255,246,205,${0.18 * beam})`);
    g.addColorStop(1, `rgba(255,246,205,${0.06 * beam})`);
    ctx.fillStyle = g;
    ctx.fill(polyPath(p));
  }
  ctx.restore();
}
