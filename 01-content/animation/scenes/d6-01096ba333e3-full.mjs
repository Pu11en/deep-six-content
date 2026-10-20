// Episode D6-01096ba333e3 (ensign wasp), full video: the lesson, then the approved Deep Six outro.
// Shot plan: episodes/D6-01096ba333e3/full/shot-list.json. Times are seconds in the full narration.
// Style C cut-paper storybook. Every frame is a pure function of time.
// New drawings: wasp-kit.mjs and home-world.mjs. Fire-ant files are only imported, never changed.
import { readFileSync, openSync, readSync, existsSync } from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { createCanvas, ImageData } from '@napi-rs/canvas';
import {
  W, H, C, clamp, lerp, eOut, eIn, eIO, eBack, hash, prog, wobble, shake, bell, cam, camAt, live,
  withCamera, fillScreen, makeFibres, createCaptions, cut, polyPath, ovalPath, smoothPath, bandPath, tornLine,
  puff, impactStar, Path2D,
} from './paper-kit.mjs';
import { questionMark } from './yard-world.mjs';
import * as K from './wasp-kit.mjs';
import { createSink, createMacro, createFloorTop, tracePath, flashlightBeam, SINK, MACRO_FLOOR } from './home-world.mjs';

const TAU = Math.PI * 2;
const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const EPISODE = path.join(root, 'episodes/D6-01096ba333e3/full');
const FLOOR = MACRO_FLOOR;

// ---------------------------------------------------------------- the approved outro, fitted to Chris
const OUTRO = JSON.parse(readFileSync(path.join(EPISODE, 'outro-retime.json'), 'utf8'));
const OUTRO_T0 = OUTRO.outro_start_frame / 30;
function createOutroFrames() {
  const file = path.join(EPISODE, 'dev', 'outro-frames.rgba');
  if (!existsSync(file)) throw Error('Outro frame cache missing: run episodes/D6-01096ba333e3/full/prep-outro.py');
  const fd = openSync(file, 'r');
  const size = W * H * 4;
  const buffer = Buffer.alloc(size);
  const canvas = createCanvas(W, H);
  const octx = canvas.getContext('2d');
  let loaded = -1;
  return k => {
    const i = clamp(k, 0, OUTRO.mapping.length - 1);
    if (i !== loaded) {
      readSync(fd, buffer, 0, size, i * size);
      octx.putImageData(new ImageData(new Uint8ClampedArray(buffer.buffer, buffer.byteOffset, size), W, H), 0, 0);
      loaded = i;
    }
    return canvas;
  };
}

// ---------------------------------------------------------------- small helpers
const ant = (t, s = 0, amp = 1) => [
  [0.08 * amp * Math.sin(t * 5.3 + s), 0.07 * amp * Math.sin(t * 4.1 + s), 0.05 * amp * Math.sin(t * 3.7 + s)],
  [0.07 * amp * Math.sin(t * 4.7 + s + 1), 0.06 * amp * Math.sin(t * 3.9 + s), 0.05 * amp * Math.sin(t * 3.1 + s)],
];
const flagBob = (t, s = 0) => -1.12 + 0.1 * Math.sin(t * 6.5 + s);
const caseY = L => FLOOR - 0.3 * L;
const toScreen = (c, x, y) => [W / 2 + (x - c.x) * c.zoom, H / 2 + (y - c.y) * c.zoom];
const cutEgg = (t, t0, d = 0.35) => 1 - eIO(prog(t, t0, t0 + d));

export function createScene(config, timing) {
  const texture = makeFibres((config.seed ?? 1) | 0);
  const tex = texture;
  const sink = createSink(tex);
  const macro = createMacro(tex);
  const floorTop = createFloorTop(tex);
  const outroFrame = createOutroFrames();
  const lessonGroups = timing.caption_groups.filter(g => g.words[0] < 130);
  const captions = createCaptions(timing.words, lessonGroups, { texture, centerY: config.caption_center_y ?? 1420, endTime: OUTRO_T0 + 0.4 });
  // The approved outro's own top caption for the first sentence of the sign-off.
  const outroCaption = createCaptions(timing.words, [{ words: [130, 131, 132, 133], fade_out_seconds: [46.24, 46.4] }], {
    family: 'D6Caption', centerY: 260, maxWidth: 910, maxSize: 58, minSize: 48, texture: makeFibres(6), endTime: 46.4,
  });

  function inMacro(ctx, t, camera, draw, dxdy = [0, 0]) {
    fillScreen(ctx, '#8C6242', tex);
    const c = live(camera, t);
    withCamera(ctx, { ...c, dx: dxdy[0], dy: dxdy[1] }, () => { macro.draw(ctx, t); draw(ctx, c); });
  }
  function inSink(ctx, t, camera, state, extra, overlay) {
    fillScreen(ctx, '#7A5236', tex);
    const c = live(camera, t);
    withCamera(ctx, c, () => sink.draw(ctx, t, { ...state, extra }));
    if (overlay) overlay(ctx, c);
  }
  function inTop(ctx, t, camera, draw) {
    fillScreen(ctx, '#C29464', tex);
    const c = live(camera, t);
    withCamera(ctx, c, () => { floorTop.draw(ctx, t, { crackY: 1560 }); draw(ctx); });
  }
  // Paper slide: the next scene arrives on a torn sheet from the right.
  function slide(ctx, t, t0, d, drawPrev, drawNext) {
    const k = eOut(prog(t, t0, t0 + d));
    if (k >= 1) { drawNext(ctx); return; }
    drawPrev(ctx);
    const edge = polyPath([...tornLine(-60, H + 60, 0, 12, 503, 36).map(([y, dx]) => [dx - 18 + 18 * Math.sin(y * 0.02), y]), [W + 60, H + 60], [W + 60, -60]]);
    ctx.save();
    ctx.translate(W * (1 - k), 0);
    cut(ctx, edge, C.paper, tex, 22, { shadow: 'rgba(30,20,25,0.45)' });
    ctx.clip(edge);
    ctx.translate(-W * (1 - k), 0);
    drawNext(ctx);
    ctx.restore();
  }
  // See-through circle on the egg case: the cutaway shows inside it.
  function xray(ctx, cx, cy, r, drawInside, ringAlpha = 1) {
    if (r <= 1) return;
    ctx.save();
    const p = new Path2D();
    p.arc(cx, cy, r, 0, TAU * 0.9999);
    ctx.clip(p);
    drawInside(ctx);
    ctx.restore();
    if (ringAlpha > 0.01) {
      ctx.save();
      ctx.globalAlpha = ringAlpha;
      ctx.lineWidth = Math.max(8, r * 0.07);
      ctx.strokeStyle = 'rgba(30,27,34,0.3)';
      ctx.beginPath();
      ctx.arc(cx + 4, cy + 5, r, 0, TAU * 0.9999);
      ctx.stroke();
      ctx.strokeStyle = C.lime;
      ctx.beginPath();
      ctx.arc(cx, cy, r, 0, TAU * 0.9999);
      ctx.stroke();
      ctx.restore();
    }
  }

  const shots = [];
  const add = (id, start, end, draw) => shots.push({ id, start, end, draw });

  // ================================================================ hook (0 - 4.46)
  // H1 "Why would a": the wasp walks the cabinet floor; a question mark pops.
  add('H1', 0, 0.92, (ctx, t) => {
    const k = eOut(prog(t, -0.45, 0.42));
    const x = lerp(900, 560, k);
    const flick = bell(t, 0.42, 0.34);
    inMacro(ctx, t, camAt(t, [[0, cam(600, 900, 1.02)], [0.92, cam(560, 880, 1.12)]]), () => {
      questionMark(ctx, tex, 320, 600, 150, prog(t, 0.02, 0.22), -0.08);
      K.placeWasp(ctx, tex, x, FLOOR, 0.95, {
        phase: K.gaitPhase(900 - x, 0.95, 26), walk: 1 - prog(t, 0.34, 0.46), flag: flagBob(t) - 0.45 * flick, antennae: ant(t),
      });
    });
  });

  // H2 "wasp lay its egg inside": the wasp stands on an egg case; its egg goes inside.
  const CASE = { x: 560, L: 560 };
  CASE.y = caseY(CASE.L);
  const CASE_TOP = CASE.y - 0.315 * CASE.L;
  const EGG_SPOT = [CASE.x + 0.02 * CASE.L, CASE.y - 0.255 * CASE.L];
  const layingFlag = (t, t0, t1) => {
    const down = eIO(prog(t, t0, t0 + 0.14)) * (1 - eIO(prog(t, t1, t1 + 0.18)));
    return lerp(flagBob(t), 0.85 + 0.08 * Math.sin(t * 31), down);
  };
  function caseWithEgg(ctx, t, r, cx, cy, eggK, ringAlpha, eggs) {
    K.drawEggCase(ctx, tex, CASE.x, CASE.y, CASE.L);
    xray(ctx, cx, cy, r, c => K.drawCaseCutaway(c, tex, CASE.x, CASE.y, CASE.L, { waspEgg: eggK, t, eggs }), ringAlpha);
  }
  function h2(ctx, t) {
    const r = Math.max(0.2 * CASE.L * eBack(prog(t, 1.66, 1.84), 1.6), 0.8 * CASE.L * eIO(prog(t, 1.88, 2.2)));
    const grow = eIO(prog(t, 1.88, 2.2));
    const cx = lerp(EGG_SPOT[0], CASE.x, grow);
    const cy = lerp(EGG_SPOT[1], CASE.y, grow);
    inMacro(ctx, t, camAt(t, [[0.92, cam(530, 760, 2.0)], [1.12, cam(560, 900, 1.2), eOut], [1.86, cam(560, 900, 1.3)], [2.2, cam(575, 900, 1.62)], [2.4, cam(578, 900, 1.68)]]), () => {
      caseWithEgg(ctx, t, r, cx, cy, prog(t, 1.68, 1.86), 1 - prog(r, 0.32 * CASE.L, 0.7 * CASE.L));
      K.placeWasp(ctx, tex, 520, CASE_TOP + 4, 0.62, { flag: layingFlag(t, 1.3, 9), antennae: ant(t, 1, 1.3), bob: 3 * Math.sin(t * 9) });
    });
  }
  add('H2', 0.92, 2.4, h2);

  // H3 "a cockroach's egg": paper slide to an American cockroach carrying its egg case.
  const ROACH_S = 1.1;
  const roachX = t => lerp(1260, 700, eOut(prog(t, 2.2, 3.0)));
  const roachTail = x => [x + 545 * ROACH_S / 1.1, FLOOR - 181 * ROACH_S];
  function h3(ctx, t) {
    const x = roachX(t);
    const [tx, ty] = roachTail(x);
    inMacro(ctx, t, camAt(t, [[2.4, cam(700, 880, 0.72)], [3.06, cam(760, 900, 0.8)], [3.24, cam(1160, 940, 1.5), eOut], [3.32, cam(1170, 940, 1.56)]]), () => {
      K.placeRoach(ctx, tex, x, FLOOR, ROACH_S, {
        phase: K.gaitPhase(1260 - x, ROACH_S, 34), walk: 1 - prog(t, 2.9, 3.05), ootheca: 1, t, ant: 0.3 * Math.sin(t * 2),
      });
      K.limeRing(ctx, tx, ty, 110, 82, prog(t, 3.06, 3.3));
    });
  }
  add('H3', 2.4, 3.32, (ctx, t) => slide(ctx, t, 2.4, 0.16, c => h2(c, t), c => h3(c, t)));

  // H4 "case?": the egg case drops to the floor; a question mark beside it.
  add('H4', 3.32, 4.46, (ctx, t) => {
    const L = 420;
    const y0 = caseY(L);
    const fall = eIn(prog(t, 3.32, 3.5));
    const land = t > 3.5 ? 70 * Math.abs(Math.sin((t - 3.5) * 9)) * Math.exp(-(t - 3.5) * 7) : 0;
    const hop = 26 * bell(t, 3.9, 0.22);
    const y = lerp(y0 - 420, y0, fall) - land - hop;
    inMacro(ctx, t, camAt(t, [[3.32, cam(600, 900, 1.15)], [4.46, cam(590, 930, 1.34)]]), () => {
      for (let i = 0; i < 5; i += 1) {
        const k = prog(t, 3.5, 3.95);
        if (k > 0 && k < 1) puff(ctx, tex, 560 + (i - 2) * 90 * (0.6 + k), FLOOR - 20 - 50 * k * (i % 2 ? 1 : 0.6), 24 * (1 - k) + 6, '#E2C9A2', 1 - k);
      }
      K.drawEggCase(ctx, tex, 560, y, L, { angle: 0.05 * Math.sin((t - 3.5) * 9) * Math.exp(-(t - 3.5) * 5) * (t > 3.5 ? 1 : 0), glow: 0.5 * bell(t, 4.05, 0.4) });
      questionMark(ctx, tex, 850, 660, 240, prog(t, 3.42, 3.62), 0.1 + 0.12 * wobble(t, 4.2, 2.5, 4));
    });
  });

  // ================================================================ A small wasp called an ensign wasp puts one egg inside.
  // A1 "A small wasp": tight on the wasp, then a fast pull back shows the huge cockroach beside it.
  add('A1', 4.46, 5.48, (ctx, t) => {
    inMacro(ctx, t, camAt(t, [[4.46, cam(170, 1070, 2.6)], [4.58, cam(172, 1068, 2.7)], [4.86, cam(700, 860, 0.6), eOut], [5.48, cam(680, 880, 0.65)]]), () => {
      K.drawEggCase(ctx, tex, 430, caseY(200), 200);
      K.placeRoach(ctx, tex, 1060, FLOOR, 1.25, { t, ant: 0.25 * Math.sin(t * 1.7) });
      K.placeWasp(ctx, tex, 170, FLOOR, 0.29, { flag: flagBob(t) - 0.35 * bell(t, 4.9, 0.3), antennae: ant(t, 2) }, { faceRight: true });
      K.limeRing(ctx, 168, 1086, 140, 100, prog(t, 4.9, 5.15), -0.05, 18);
    });
  });

  // A2 "called an ensign wasp": a pennant (ensign = flag) waves beside the flag-like abdomen.
  add('A2', 5.48, 6.99, (ctx, t) => {
    const w = Math.sin((t - 5.93) * TAU * 1.6);
    const synced = t >= 5.93 && t < 6.36 ? 0.2 * w * prog(t, 5.93, 6.05) : 0;
    const big = t >= 6.36 ? -0.42 * Math.sin((t - 6.36) * TAU * 2.2) * Math.exp(-(t - 6.36) * 1.1) : 0;
    const flagK = prog(t, 5.93, 6.13) * (1 - eIn(prog(t, 6.36, 6.56)));
    inMacro(ctx, t, camAt(t, [[5.48, cam(520, 900, 1.08)], [6.36, cam(560, 860, 1.14)], [6.99, cam(640, 800, 1.3)]]), () => {
      K.ensignFlag(ctx, tex, 800 + 120 * eIn(prog(t, 6.36, 6.56)), FLOOR - 30, 220, flagK, w, t);
      K.placeWasp(ctx, tex, 440, FLOOR, 1.0, { flag: -1.1 + synced + big, antennae: ant(t, 3, 1.4) });
      K.limeRing(ctx, 686, 736, 112, 124, prog(t, 5.95, 6.2) * (1 - prog(t, 6.36, 6.5)), 0.2, 14);
    });
  });

  // A3 "puts one egg inside.": abdomen into the case wall; one white egg; it settles among the roach eggs.
  add('A3', 6.99, 8.87, (ctx, t) => {
    const r = Math.max(0.2 * CASE.L * eBack(prog(t, 7.14, 7.32), 1.6), 0.8 * CASE.L * eIO(prog(t, 7.8, 8.1)));
    const grow = eIO(prog(t, 7.8, 8.1));
    const walkK = prog(t, 8.06, 8.87);
    const wx = 520 - 160 * walkK;
    inMacro(ctx, t, camAt(t, [[6.99, cam(560, 880, 1.25)], [7.8, cam(565, 880, 1.42)], [8.1, cam(560, 900, 1.3)], [8.87, cam(540, 900, 1.38)]]), () => {
      caseWithEgg(ctx, t, r, lerp(EGG_SPOT[0], CASE.x, grow), lerp(EGG_SPOT[1], CASE.y, grow), prog(t, 7.16, 7.36), 1 - prog(r, 0.32 * CASE.L, 0.7 * CASE.L));
      K.limeRing(ctx, EGG_SPOT[0], EGG_SPOT[1], 62, 34, prog(t, 7.2, 7.42) * (1 - prog(t, 7.8, 7.95)), 0, 9);
      impactStar(ctx, tex, EGG_SPOT[0] + 30, EGG_SPOT[1] - 14, 40, eBack(prog(t, 7.52, 7.62), 2), 1 - prog(t, 7.66, 7.86), 0.3);
      K.placeWasp(ctx, tex, wx, CASE_TOP + 4, 0.62, {
        flag: layingFlag(t, 6.99, 7.82), antennae: ant(t, 4, 1.2), phase: K.gaitPhase(160 * walkK, 0.62, 26), walk: walkK > 0 && walkK < 1 ? 1 : 0,
      });
    });
  });

  // ================================================================ inside the egg case (cutaway set)
  const CUT = { x: 540, L: 1000 };
  CUT.y = caseY(CUT.L);
  const eggW = i => { const g = K.caseEgg(CUT.L, i); return { x: CUT.x + g.x, y: CUT.y + g.y, rx: g.rx, ry: g.ry, top: CUT.y + g.y - g.ry }; };
  const WE = [CUT.x + 0.02 * CUT.L, CUT.y - 0.255 * CUT.L]; // the wasp egg
  // Which cockroach eggs have been eaten, and when (seconds), for the whole sequence.
  const EATEN = { 4: 17.8, 5: 18.45, 3: 18.94, 2: 19.26, 6: 19.32, 11: 19.38, 12: 19.44, 13: 19.5,
    0: 20.46, 1: 20.52, 7: 20.6, 8: 20.68, 9: 20.76, 10: 20.84, 14: 20.92, 15: 21.0 };
  const eggsAt = t => Array.from({ length: 16 }, (_, i) => (EATEN[i] === undefined ? 1 : cutEgg(t, EATEN[i])));
  function inCase(ctx, t, camera, state, draw, dxdy) {
    inMacro(ctx, t, camera, () => {
      K.drawCaseCutaway(ctx, tex, CUT.x, CUT.y, CUT.L, { t, eggs: eggsAt(t), ...state });
      if (draw) draw(ctx);
    }, dxdy);
  }
  const grub = (ctx, t, x, y, len, angle = 0, o = {}) => K.drawGrub(ctx, tex, x, y, len, angle, { wig: 0.8, ph: t * 8, jaw: 0.4 + 0.4 * Math.sin(t * 9), curl: 0.3, ...o });
  // Ink cut across one egg's shell; k grows it from the top down.
  function shellCut(ctx, i, k, fade = 1) {
    if (k <= 0.01 || fade <= 0.01) return;
    const e = eggW(i);
    ctx.save();
    ctx.globalAlpha = fade;
    ctx.strokeStyle = C.ink;
    ctx.lineWidth = 7;
    ctx.lineJoin = 'round';
    ctx.lineCap = 'round';
    ctx.beginPath();
    const n = 9;
    for (let j = 0; j <= n * k; j += 1) {
      const y = e.top + 12 + j * (e.ry * 1.5 / n);
      const x = e.x + (j % 2 ? 10 : -10);
      if (j) ctx.lineTo(x, y); else ctx.moveTo(x, y);
    }
    ctx.stroke();
    ctx.restore();
  }

  // B1 "When it hatches,": the wasp egg wobbles, splits, and a tiny larva wriggles out.
  add('B1', 8.87, 9.92, (ctx, t) => {
    inCase(ctx, t, camAt(t, [[8.87, cam(560, 610, 2.5)], [9.92, cam(560, 604, 3.05)]]), {}, () => {
      const wob = 0.14 * Math.sin((t - 8.87) * 22) * Math.exp(-(t - 8.87) * 2.2) * (t < 9.22 ? 1 : 0);
      const split = eOut(prog(t, 9.22, 9.45));
      if (split < 1) {
        for (const side of [-1, 1]) {
          ctx.save();
          ctx.globalAlpha = 1 - split;
          ctx.translate(WE[0] + side * 60 * split, WE[1] - 30 * split);
          ctx.rotate(wob + side * 0.6 * split);
          ctx.beginPath();
          ctx.rect(side < 0 ? -200 : 0, -200, 200, 400);
          ctx.clip();
          K.drawWaspEgg(ctx, tex, 0, 0, 0.15 * CUT.L, -0.06, 1);
          ctx.restore();
        }
        const crack = prog(t, 9.14, 9.22);
        if (crack > 0 && split < 0.05) {
          ctx.save();
          ctx.translate(WE[0], WE[1]);
          ctx.rotate(wob);
          ctx.strokeStyle = C.ink;
          ctx.lineWidth = 4;
          ctx.beginPath();
          const pts = [[0, -24], [-6, -10], [5, 0], [-4, 12], [3, 24]];
          pts.slice(0, Math.max(2, Math.round(crack * 5))).forEach(([x, y], i) => (i ? ctx.lineTo(x, y) : ctx.moveTo(x, y)));
          ctx.stroke();
          ctx.restore();
        }
      }
      if (t >= 9.22) grub(ctx, t, WE[0], WE[1] + 2, 110 * eBack(prog(t, 9.22, 9.42), 2), 0, { wig: 1 });
    });
  });

  // B2 "the young wasp": close on the larva; a lime ring.
  add('B2', 9.92, 10.72, (ctx, t) => {
    inCase(ctx, t, camAt(t, [[9.92, cam(560, 604, 3.05)], [10.72, cam(560, 600, 3.6)]]), {}, () => {
      grub(ctx, t, WE[0], WE[1] + 2, 110, 0, { wig: 1 + bell(t, 10.04, 0.3) });
      K.limeRing(ctx, WE[0], WE[1] + 2, 84, 46, prog(t, 10.26, 10.5), 0, 8);
    });
  });

  // B3 "has a dozen or more": pull back; eggs light up one by one.
  const lightAt = i => (i < 12 ? 11.02 + i * 0.03 : 11.4 + (i - 12) * 0.05);
  add('B3', 10.72, 11.76, (ctx, t) => {
    const highlight = Array.from({ length: 16 }, (_, i) => prog(t, lightAt(i), lightAt(i) + 0.12));
    inCase(ctx, t, camAt(t, [[10.72, cam(560, 600, 3.6)], [10.95, cam(540, 840, 0.95), eOut], [11.76, cam(540, 830, 1.03)]]), { highlight, bounce: 0.5 * bell(t, 11.4, 0.25) }, () => {
      grub(ctx, t, WE[0], WE[1] + 2, 110);
    });
  });

  // B4 "cockroach eggs to feed on.": pan along the eggs; the larva turns to an egg and bites.
  add('B4', 11.76, 13.68, (ctx, t) => {
    const fadeHi = 1 - prog(t, 11.76, 11.95);
    const highlight = Array.from({ length: 16 }, () => fadeHi);
    const turn = eIO(prog(t, 12.68, 12.86));
    const chomp = t >= 12.88 ? Math.abs(Math.sin((t - 12.88) * 14)) * Math.exp(-(t - 12.88) * 1.2) : 0.85 * turn;
    const [sx, sy] = shake(t, 12.88, 0.9, 7, 11);
    inCase(ctx, t, camAt(t, [[11.76, cam(300, 860, 1.7)], [12.28, cam(780, 860, 1.7)], [12.5, cam(575, 640, 2.9)], [13.68, cam(560, 628, 3.45)]]), { highlight, bounce: bell(t, 12.28, 0.32) }, () => {
      grub(ctx, t, WE[0], WE[1] + 2, 115, -0.55 * turn, { jaw: t >= 12.68 ? chomp : 0.3 + 0.3 * Math.sin(t * 9) });
      for (let i = 0; i < 4; i += 1) {
        const k = prog(t, 12.9 + i * 0.12, 13.3 + i * 0.12);
        if (k > 0 && k < 1) puff(ctx, tex, WE[0] - 50 + i * 12, WE[1] + 40 + 30 * k, 8 * (1 - k) + 2, '#F3E6C8', 1 - k);
      }
    }, [sx, sy]);
  });

  // ================================================================ pointed jaws with tiny teeth
  // C1 "The young wasp uses": the larva crawls across the egg tops and lifts its head.
  add('C1', 13.68, 14.86, (ctx, t) => {
    const x = lerp(430, 640, eIO(prog(t, 13.68, 14.4)));
    const look = -0.45 * eOut(prog(t, 14.42, 14.6));
    inCase(ctx, t, camAt(t, [[13.68, cam(470, 618, 3.0)], [14.4, cam(660, 618, 3.0)], [14.86, cam(600, 600, 3.6)]]), {}, () => {
      grub(ctx, t, x, 598, 130, -0.15 * eOut(prog(t, 14.42, 14.6)), { look, wig: 1.2 });
    });
  });

  // Jaw close-up set: inside the case, out-of-focus eggs behind the larva's head.
  function insideBack(ctx, t, c) {
    fillScreen(ctx, '#3A241B', tex);
    withCamera(ctx, c, () => {
      for (let i = 0; i < 6; i += 1) {
        ctx.save();
        ctx.globalAlpha = 0.28;
        cut(ctx, ovalPath(-200 + i * 300, 980 + (i % 2) * 120, 140, 420), '#E8D8B4', null, 0);
        ctx.restore();
      }
      const glow = ctx.createRadialGradient(540, 780, 50, 540, 780, 800);
      glow.addColorStop(0, 'rgba(255,205,140,0.35)');
      glow.addColorStop(1, 'rgba(255,205,140,0)');
      ctx.fillStyle = glow;
      ctx.fillRect(-600, -300, 2300, 2400);
    });
  }
  function jaws(ctx, t, camera, open, boost = 0, lime = 0) {
    const c = live(camera, t);
    insideBack(ctx, t, c);
    withCamera(ctx, c, () => {
      const pts = K.drawJawFace(ctx, tex, 540, 800, 290, open, 1, boost, lime);
      jaws.tips = pts.tips;
    });
  }
  // C2 "pointed jaws with": jaws snap open (points glint), chomp, slide toward one jaw.
  add('C2', 14.86, 15.98, (ctx, t) => {
    let open = 0.85 * eBack(prog(t, 14.86, 15.0), 2);
    if (t >= 15.18) open = lerp(0.85, 0, eIn(prog(t, 15.18, 15.24)));
    if (t >= 15.24) open = 0.45 * eOut(prog(t, 15.3, 15.5)) + 0.04 * Math.sin(t * 5);
    const [sx, sy] = shake(t, 15.24, 0.22, 16, 3);
    const camera = camAt(t, [[14.86, cam(540, 900, 0.95)], [15.58, cam(540, 920, 1.04)], [15.98, cam(560, 1000, 1.5)]]);
    jaws(ctx, t, { ...camera, x: camera.x - sx, y: camera.y - sy }, open);
    const c = live(camera, t);
    withCamera(ctx, c, () => {
      for (const [x, y] of jaws.tips ?? []) impactStar(ctx, tex, x, y, 46, eBack(prog(t, 14.9, 15.02), 2), 1 - prog(t, 15.06, 15.2), 0.4);
    });
  });
  // C3 "tiny teeth to": the row of small teeth pops up, a lime line underneath; jaws open wide.
  add('C3', 15.98, 17.18, (ctx, t) => {
    const open = 0.45 + 0.04 * Math.sin(t * 5) + 0.5 * eBack(prog(t, 16.7, 16.9), 1.6);
    jaws(ctx, t, camAt(t, [[15.98, cam(560, 1000, 1.9)], [16.7, cam(550, 1000, 2.08)], [17.18, cam(560, 980, 1.8)]]), open, prog(t, 16.32, 16.66), prog(t, 16.32, 16.6) * (1 - prog(t, 16.75, 16.95)));
  });

  // C4 "cut through the shells": the larva bites one egg; a cut runs down it; the shell collapses.
  add('C4', 17.18, 18.4, (ctx, t) => {
    const e = eggW(4);
    const bite = t < 17.18 ? 0.8 : t < 17.26 ? lerp(0.8, 0, prog(t, 17.18, 17.24)) : 0.25 + 0.35 * Math.abs(Math.sin((t - 17.26) * 10));
    const [sx, sy] = shake(t, 17.18, 0.18, 10, 7);
    inCase(ctx, t, camAt(t, [[17.18, cam(610, 720, 2.1)], [18.4, cam(612, 745, 2.32)]]), {}, () => {
      shellCut(ctx, 4, t < 17.44 ? 0.18 * prog(t, 17.18, 17.24) : lerp(0.18, 1, eOut(prog(t, 17.44, 17.7))), 1 - prog(t, 17.8, 18.0));
      grub(ctx, t, e.x + 66, e.top - 60, 150, -1.0, { jaw: bite });
      impactStar(ctx, tex, e.x, e.top + 10, 34, eBack(prog(t, 17.18, 17.26), 2), 1 - prog(t, 17.28, 17.4));
    }, [sx, sy]);
  });

  // C5 "individual eggs around it.": egg after egg empties, then the eggs around the larva.
  add('C5', 18.4, 20.2, (ctx, t) => {
    const at5 = eggW(5);
    const at3 = eggW(3);
    const camera = camAt(t, [[18.4, cam(700, 720, 2.1)], [18.88, cam(700, 724, 2.16)], [18.9, cam(490, 720, 2.1)], [19.22, cam(490, 722, 2.16)], [19.48, cam(540, 820, 1.15), eOut], [20.2, cam(540, 812, 1.22)]]);
    const highlight = Array.from({ length: 16 }, (_, i) => (EATEN[i] && EATEN[i] < 20 ? bell(t, EATEN[i] - 0.06, 0.3) : 0));
    inCase(ctx, t, camera, { highlight }, () => {
      if (t < 18.9) {
        shellCut(ctx, 5, eOut(prog(t, 18.4, 18.5)), 1 - prog(t, 18.45, 18.6));
        grub(ctx, t, at5.x + 66, at5.top - 60, 150, -1.0, { jaw: 0.2 + 0.5 * Math.abs(Math.sin(t * 12)) });
      } else if (t < 19.24) {
        shellCut(ctx, 3, eOut(prog(t, 18.9, 19.0)), 1 - prog(t, 18.94, 19.1));
        grub(ctx, t, at3.x + 66, at3.top - 60, 155, -1.0, { jaw: 0.2 + 0.5 * Math.abs(Math.sin(t * 12)) });
      } else {
        grub(ctx, t, 560, 600, 170, 0.05 * Math.sin(t * 3), { wig: 1 + bell(t, 19.56, 0.35) });
      }
    });
  });

  // ================================================================ After feeding and growing, it changes into an adult inside that same case.
  // D1: fast chomping, the last eggs empty, then the larva swells.
  add('D1', 20.2, 21.73, (ctx, t) => {
    const g = eBack(prog(t, 21.02, 21.4), 1.4);
    const len = lerp(170, 640, g);
    inCase(ctx, t, camAt(t, [[20.2, cam(540, 790, 1.22)], [21.02, cam(540, 790, 1.3)], [21.73, cam(540, 800, 1.2)]]), {}, () => {
      grub(ctx, t, lerp(560, 540, g), lerp(600, 720, g), len, 0, {
        jaw: t > 20.44 && t < 21.02 ? Math.abs(Math.sin((t - 20.44) * 14)) : 0.3, feed: prog(t, 20.44, 21.2), curl: lerp(0.3, 0.55, g), wig: 0.7,
      });
    });
  });

  // The pupa and adult lie inside the case. Body centre about (540, 730).
  const ADULT = { x: 563, gy: 994, s: 1.15 };
  // D2 "it changes into an adult": squash-flip from larva to pale pupa; it darkens to a black adult.
  add('D2', 21.73, 23.14, (ctx, t) => {
    const k1 = prog(t, 21.84, 21.96);
    const k2 = prog(t, 21.96, 22.1);
    const tint = t < 22.22 ? 1 : t < 22.62 ? lerp(1, 0.55, eIO(prog(t, 22.22, 22.6))) : lerp(0.55, 0, eOut(prog(t, 22.62, 22.74)));
    inCase(ctx, t, camAt(t, [[21.73, cam(540, 780, 1.3)], [23.14, cam(540, 760, 1.46)]]), {}, () => {
      if (t < 21.96) {
        ctx.save();
        ctx.translate(540, 720);
        ctx.scale(Math.max(0.02, Math.cos(k1 * Math.PI / 2)), 1);
        ctx.translate(-540, -720);
        grub(ctx, t, 540, 720, 640, 0, { curl: 0.55, wig: 0.5, feed: 1 });
        ctx.restore();
      } else {
        impactStar(ctx, tex, 560, 720, 210, eBack(prog(t, 22.62, 22.74), 2), 1 - prog(t, 22.76, 22.92), 0.2);
        ctx.save();
        ctx.translate(540, 720);
        ctx.scale(Math.max(0.02, Math.sin(k2 * Math.PI / 2)), 1);
        ctx.translate(-540, -720);
        K.placeWasp(ctx, tex, ADULT.x, ADULT.gy, ADULT.s, { fold: 1, tint, shadows: false, antennae: ant(t, 5, 0.3) });
        ctx.restore();
      }
    });
  });

  // D3 "inside that same case.": pull back; the cut-open side closes; lime ring round the case.
  add('D3', 23.14, 25.05, (ctx, t) => {
    const close = eIO(prog(t, 23.72, 24.0));
    const wob = 0.012 * Math.sin((t - 24.6) * 30) * bell(t, 24.6, 0.3);
    inMacro(ctx, t, camAt(t, [[23.14, cam(540, 760, 1.46)], [23.4, cam(540, 860, 0.82), eOut], [25.05, cam(540, 860, 0.93)]]), () => {
      ctx.save();
      ctx.translate(CUT.x, CUT.y + 0.31 * CUT.L);
      ctx.rotate(wob);
      ctx.translate(-CUT.x, -(CUT.y + 0.31 * CUT.L));
      K.drawCaseCutaway(ctx, tex, CUT.x, CUT.y, CUT.L, { t, eggs: eggsAt(t) });
      K.placeWasp(ctx, tex, ADULT.x, ADULT.gy, ADULT.s, { fold: 1, shadows: false, antennae: ant(t, 5, 0.3) });
      if (close > 0) {
        ctx.save();
        ctx.beginPath();
        ctx.rect(CUT.x - 0.62 * CUT.L, CUT.y - CUT.L, 1.24 * CUT.L * close, 2 * CUT.L);
        ctx.clip();
        K.drawEggCase(ctx, tex, CUT.x, CUT.y, CUT.L);
        ctx.restore();
      }
      ctx.restore();
      K.limeRing(ctx, CUT.x, CUT.y - 10, 620, 410, prog(t, 24.08, 24.42), -0.04, 18);
    });
  });

  // ================================================================ Once that change is complete, the adult cuts a small, round hole ...
  // E1 "Once that change is complete,": inside, the adult stirs; legs and antennae unfold; a shine sweeps it.
  add('E1', 25.05, 26.16, (ctx, t) => {
    const fold = lerp(1, 0.55, eOut(prog(t, 25.42, 25.72)));
    const eye = [ADULT.x - 214 * ADULT.s, ADULT.gy + (-86 - 160) * ADULT.s];
    inCase(ctx, t, camAt(t, [[25.05, cam(540, 740, 1.5)], [26.16, cam(520, 740, 1.66)]]), {}, () => {
      K.placeWasp(ctx, tex, ADULT.x, ADULT.gy, ADULT.s, {
        fold, shadows: false, sheen: prog(t, 25.78, 26.1) * (1 - prog(t, 26.08, 26.16)), antennae: ant(t, 6, 0.6 + 2 * bell(t, 25.42, 0.4)),
      });
      impactStar(ctx, tex, eye[0] - 10, eye[1] - 20, 40, eBack(prog(t, 25.8, 25.9), 2), 1 - prog(t, 25.95, 26.12));
    });
  });

  // Exit hole on the outside of the case (near the end of a long side).
  const HOLE = { x: CASE.x + 0.3 * CASE.L, y: CASE.y + 0.05 * CASE.L, r: 0.085 * CASE.L };
  const chew = t => (t < 26.88 ? 0 : t < 27.14 ? 0.42 * prog(t, 26.88, 27.14) : lerp(0.42, 1, eIO(prog(t, 27.14, 28.0))));
  function crumbs(ctx, t, t0, t1) {
    for (let i = 0; i < 8; i += 1) {
      const born = t0 + (i / 8) * (t1 - t0);
      const k = prog(t, born, born + 0.3);
      if (k <= 0 || k >= 1) continue;
      const a = -Math.PI / 2 + chew(born) * TAU;
      const x = HOLE.x + Math.cos(a) * HOLE.r * (1 + k * 0.8);
      const y = HOLE.y + Math.sin(a) * HOLE.r * (1 + k * 0.4) + 80 * k * k;
      cut(ctx, ovalPath(x, y, 4, 3, i), '#4A2A1C', null, 0);
    }
  }
  // E2 "the adult cuts": the case trembles; a chewed line starts round a small circle.
  add('E2', 26.16, 27.14, (ctx, t) => {
    const tremble = 4 * Math.sin(t * 70) * bell(t, 26.64, 0.3);
    inMacro(ctx, t, camAt(t, [[26.16, cam(690, 980, 1.7)], [27.14, cam(705, 990, 1.88)]]), () => {
      K.drawEggCase(ctx, tex, CASE.x + tremble, CASE.y, CASE.L, { hole: { cut: chew(t), open: 0 } });
      crumbs(ctx, t, 26.9, 27.14);
    });
  });
  // E3 "a small, round hole": lime ring shows how small; the circle closes; the disc pops out.
  add('E3', 27.14, 28.52, (ctx, t) => {
    const pop = prog(t, 28.14, 28.5);
    inMacro(ctx, t, camAt(t, [[27.14, cam(HOLE.x, HOLE.y, 2.6)], [28.52, cam(HOLE.x, HOLE.y + 6, 2.88)]]), () => {
      K.drawEggCase(ctx, tex, CASE.x, CASE.y, CASE.L, { hole: { cut: chew(t), open: prog(t, 28.14, 28.2) } });
      crumbs(ctx, t, 27.14, 28.0);
      const ringR = HOLE.r * lerp(2.3, 1.4, eOut(prog(t, 27.32, 27.56)));
      K.limeRing(ctx, HOLE.x, HOLE.y, ringR, ringR, prog(t, 27.32, 27.5) * (1 - prog(t, 27.72, 27.9)), 0, 7);
      if (pop > 0 && pop < 1) K.drawCaseDisc(ctx, tex, HOLE.x + 40 * pop, HOLE.y + 150 * eIn(pop), HOLE.r * 0.95, 3 * pop);
      impactStar(ctx, tex, HOLE.x, HOLE.y, 50, eBack(prog(t, 28.14, 28.22), 2), 1 - prog(t, 28.26, 28.4), 0.2);
    });
  });
  // E4 "through the case and comes out.": head pokes through, the wasp pulls free and lands outside.
  add('E4', 28.52, 30.46, (ctx, t) => {
    const s = 0.42;
    const out = eIO(prog(t, 29.22, 29.48));
    const poke = eOut(prog(t, 28.52, 28.8));
    const X = HOLE.x + 34 - 206 * s - 70 * (1 - poke) + 300 * out;
    const drop = eIn(prog(t, 29.48, 29.62));
    const gY = lerp(HOLE.y + 238 * s * 0.92, FLOOR + 24, drop) - 30 * bell(t, 29.62, 0.18) * 0;
    const free = t >= 29.48;
    inMacro(ctx, t, camAt(t, [[28.52, cam(HOLE.x, HOLE.y + 6, 2.88)], [28.9, cam(700, 1000, 1.5), eOut], [29.24, cam(720, 1000, 1.5)], [29.62, cam(870, 1020, 1.62)], [30.46, cam(880, 1020, 1.72)]]), () => {
      K.drawEggCase(ctx, tex, CASE.x, CASE.y, CASE.L, { hole: { cut: 1, open: 1 } });
      K.drawCaseDisc(ctx, tex, HOLE.x + 40, FLOOR - 8, HOLE.r * 0.95, 3);
      ctx.save();
      if (!free) {
        const p = new Path2D();
        p.moveTo(HOLE.x + HOLE.r, HOLE.y);
        p.arc(HOLE.x, HOLE.y, HOLE.r, 0, TAU * 0.9999);
        p.closePath();
        p.rect(HOLE.x, HOLE.y - 800, 1600, 1600);
        ctx.clip(p);
      }
      K.placeWasp(ctx, tex, X, gY, s, {
        flag: t < 29.7 ? -1.0 : flagBob(t) - 0.45 * bell(t, 29.7, 0.34), wing: bell(t, 29.72, 0.36), antennae: ant(t, 7, 1.5),
        phase: K.gaitPhase(300 * out, s, 26), walk: out > 0 && out < 1 ? 1 : 0, shadows: free,
      }, { faceRight: true });
      ctx.restore();
    });
  });

  // ================================================================ American cockroach egg cases are one of this wasp's targets.
  const TOP = { s: 0.85, a: Math.atan2(-590, 700) };
  const topPoint = (cx, cy, lx, ly) => [cx + lx * Math.cos(TOP.a) - ly * Math.sin(TOP.a), cy + lx * Math.sin(TOP.a) + ly * Math.cos(TOP.a)];
  const roachTopAt = t => {
    if (t < 31.62) {
      const k = eOut(prog(t, 30.3, 30.92));
      return [lerp(1150, 560, k), lerp(1750, 1050, k), Math.hypot(590, 700) * k, 1 - prog(t, 30.85, 30.95)];
    }
    const k = eIn(prog(t, 31.62, 31.96));
    return [560 - 640 * k * 0.645, 1050 - 640 * k * 0.765, 920 + 640 * k, 1];
  };
  const PRONOTUM = topPoint(560, 1050, 0, -300 * TOP.s);
  const CASE_TOP_POS = topPoint(560, 1050, 0, 450 * TOP.s);
  function topShot(ctx, t, camera) {
    const [x, y, dist, walk] = roachTopAt(t);
    inTop(ctx, t, camera, () => {
      if (t >= 31.62) K.drawEggCaseTop(ctx, tex, CASE_TOP_POS[0], CASE_TOP_POS[1], 150 * TOP.s, TOP.a + Math.PI / 2);
      K.drawRoachTop(ctx, tex, x, y, TOP.s, TOP.a, { phase: dist * 0.03, walk, t, ootheca: t >= 31.62 ? 0 : prog(t, 31.44, 31.6) });
    });
  }
  // F1 "American cockroach": seen from above, it scurries in; punch in on its pale-rimmed shield.
  add('F1', 30.46, 31.44, (ctx, t) => topShot(ctx, t, camAt(t, [[30.46, cam(720, 1250, 0.85)], [30.92, cam(640, 1100, 0.96)], [31.1, cam(PRONOTUM[0], PRONOTUM[1] + 40, 1.7), eOut], [31.44, cam(PRONOTUM[0], PRONOTUM[1] + 40, 1.8)]])));
  // F2 "egg cases": pan to its tail; the egg case is left on the floor as it scurries off.
  add('F2', 31.44, 31.96, (ctx, t) => topShot(ctx, t, camAt(t, [[31.44, cam(PRONOTUM[0], PRONOTUM[1] + 40, 1.8)], [31.58, cam(CASE_TOP_POS[0] - 20, CASE_TOP_POS[1] - 60, 1.5), eOut], [31.96, cam(CASE_TOP_POS[0] - 30, CASE_TOP_POS[1] - 70, 1.42)]])));

  // F3 "are one of this wasp's": side view; the wasp walks up to the case and taps it with its antennae.
  const T_CASE = { x: 640, L: 420 };
  T_CASE.y = caseY(T_CASE.L);
  function targetShot(ctx, t, camera, extra) {
    const k = eOut(prog(t, 31.96, 32.46));
    const x = lerp(-80, 330, k);
    const tap = prog(t, 32.76, 32.9);
    const antennae = ant(t, 8, 1).map(a => [a[0] - 0.55 * tap + 0.12 * tap * Math.sin(t * 17), a[1] + 0.2 * tap, a[2]]);
    inMacro(ctx, t, camera, () => {
      K.drawEggCase(ctx, tex, T_CASE.x, T_CASE.y, T_CASE.L);
      K.placeWasp(ctx, tex, x, FLOOR, 0.5, {
        phase: K.gaitPhase(410 * k, 0.5, 26), walk: k < 1 ? 1 - prog(t, 32.36, 32.46) : 0, antennae,
        flag: flagBob(t) - 0.3 * bell(t, 32.76, 0.3) - 0.3 * bell(t, 33.36, 0.3), head: 0.15 * tap,
      }, { faceRight: true });
      if (extra) extra(ctx);
    });
  }
  add('F3', 31.96, 33.36, (ctx, t) => targetShot(ctx, t, camAt(t, [[31.96, cam(470, 960, 1.12)], [33.36, cam(490, 965, 1.24)]]), c => {
    K.limeRing(c, T_CASE.x, T_CASE.y, 270, 178, prog(t, 32.24, 32.5), -0.04, 14);
  }));
  // F4 "targets.": a lime target snaps onto the case.
  add('F4', 33.36, 34.38, (ctx, t) => targetShot(ctx, t, camAt(t, [[33.36, cam(510, 980, 1.28)], [34.38, cam(560, 995, 1.44)]]), c => {
    K.limeRing(c, T_CASE.x, T_CASE.y, 270, 178, 1 - prog(t, 33.36, 33.5), -0.04, 14);
    impactStar(c, tex, T_CASE.x, T_CASE.y - 160, 90, eBack(prog(t, 33.36, 33.46), 2), 1 - prog(t, 33.48, 33.64), 0.1);
    K.targetMark(c, tex, T_CASE.x, T_CASE.y, 230, prog(t, 33.36, 33.56), t);
  }));

  // ================================================================ under the sink
  const RA = { s: 0.4 };
  const STOP_X = 302 + 545 * RA.s - 6;
  // Roach A: walks in, leaves its case at the crack, then heads back toward the warm line.
  const roachA = t => {
    if (t < 35.4) {
      const k = eOut(prog(t, 34.2, 34.9));
      return { x: lerp(-260, STOP_X, k), y: 1200, face: true, walk: 1 - prog(t, 34.82, 34.92), dist: (STOP_X + 260) * k };
    }
    const k = eIO(prog(t, 35.45, 38.4));
    return { x: lerp(STOP_X, 470, k), y: lerp(1200, 1118, k), face: false, walk: k > 0 && k < 1 ? 1 : 0, dist: 140 * k };
  };
  const CRACK_CASE = [302, 1206];
  const GAP_CASE = [800, 1050];
  function drawRoachA(ctx, t) {
    const a = roachA(t);
    K.placeRoach(ctx, tex, a.x, a.y, RA.s, { phase: K.gaitPhase(a.dist, RA.s, 34), walk: a.walk, t, ootheca: t < 35.32 ? prog(t, 34.9, 35.08) : 0, ant: 0.6 * bell(t, 37.88, 0.6) }, { faceRight: a.face });
  }
  // The egg case at the crack: dropped at the tail, slides in and wedges.
  function crackCase(ctx, t) {
    if (t < 35.32) return;
    const k = eIO(prog(t, 35.32, 35.62));
    const tail = [STOP_X - 545 * RA.s, 1200 - 181 * RA.s];
    const x = lerp(tail[0], CRACK_CASE[0], k);
    const y = lerp(tail[1], CRACK_CASE[1], k);
    K.drawEggCase(ctx, tex, x, y, 70, { angle: lerp(-0.15, 1.05, k) });
    if (k > 0.5) {
      // Crack edge drawn over the bottom of the case so it sits down inside.
      ctx.save();
      ctx.globalAlpha = prog(k, 0.5, 1);
      ctx.strokeStyle = '#22150F';
      ctx.lineWidth = 9;
      ctx.lineCap = 'round';
      ctx.beginPath();
      ctx.moveTo(CRACK_CASE[0] - 20, CRACK_CASE[1] + 14);
      ctx.lineTo(CRACK_CASE[0] + 6, CRACK_CASE[1] + 30);
      ctx.stroke();
      ctx.restore();
    }
  }
  function gapCase(ctx, t) {
    if (t < 36.54) return;
    const k = eOut(prog(t, 36.54, 36.74));
    K.drawEggCase(ctx, tex, GAP_CASE[0] + 60 * (1 - k), GAP_CASE[1] - 4, 66 * eBack(clamp(k * 1.5), 2));
  }
  // Roach B: hides in the gap around the drain pipe; peeks out; later steps out into the light.
  function drawRoachB(ctx, t) {
    let x = 990;
    if (t > 34.5 && t < 35.4) x = lerp(990, 905, eOut(prog(t, 34.56, 34.76))) + 100 * eIn(prog(t, 35.05, 35.35));
    if (t > 43.2) x = lerp(990, 760, eOut(prog(t, 43.32, 43.7)));
    if (x >= 985) return;
    ctx.save();
    ctx.beginPath();
    ctx.rect(-400, -400, SINK.pipeGap.x + 6 + 400, 2400);
    ctx.clip();
    const walking = (t > 43.32 && t < 43.7) || (t > 34.56 && t < 34.76) || (t > 35.05 && t < 35.35);
    K.placeRoach(ctx, tex, x, 678, 0.3, { t, walk: walking ? 1 - prog(t, 43.6, 43.72) : 0, phase: K.gaitPhase(990 - x, 0.24, 34), ant: 0.4 * Math.sin(t * 7) });
    ctx.restore();
  }
  const sinkBase = (t, s = {}) => (ctx) => {
    crackCase(ctx, t);
    gapCase(ctx, t);
    drawRoachB(ctx, t);
    drawRoachA(ctx, t);
    if (s.extra) s.extra(ctx);
  };
  const WIDE = cam(540, 960, 0.95);
  // G1 "Those roaches leave their": a roach scurries in; another peeks from the pipe gap; a case shows at its tail.
  add('G1', 34.38, 35.32, (ctx, t) => inSink(ctx, t, camAt(t, [[34.38, cam(560, 980, 1.12)], [35.32, cam(500, 1010, 1.22)]]), {}, sinkBase(t)));
  // G2 "cases in cracks": push in; the case slides into the crack; lime traces the crack.
  add('G2', 35.32, 36.28, (ctx, t) => inSink(ctx, t, camAt(t, [[35.32, cam(500, 1010, 1.22)], [35.52, cam(330, 1160, 2.3), eOut], [36.28, cam(325, 1162, 2.45)]]), {}, sinkBase(t, {
    extra: c => tracePath(c, SINK.crack, prog(t, 35.86, 36.12), 12),
  })));
  // G3 "and small gaps,": whip to the back wall; a case in the gap under the wall; lime marks both gaps.
  add('G3', 36.28, 37.65, (ctx, t) => inSink(ctx, t, camAt(t, [[36.28, cam(325, 1162, 2.45)], [36.44, cam(845, 903, 1.9), eOut], [37.65, cam(825, 908, 2.2)]]), {}, sinkBase(t, {
    extra: c => {
      tracePath(c, [[SINK.gap.x0, SINK.gap.y + 2], [SINK.gap.x1, SINK.gap.y + 2]], prog(t, 36.88, 37.1), 10);
      K.limeRing(c, SINK.pipeGap.x + 10, SINK.pipeGap.y + 14, 96, 96, prog(t, 36.98, 37.25), 0, 12);
    },
  })));
  // G4 "and they favor warm,": to the hot line; the roach comes near; warm glow and ripples.
  add('G4', 37.65, 38.78, (ctx, t) => inSink(ctx, t, camAt(t, [[37.65, cam(825, 908, 2.2)], [37.84, cam(350, 960, 1.45), eOut], [38.78, cam(330, 948, 1.62)]]), { warm: eOut(prog(t, 38.16, 38.42)) }, sinkBase(t)));
  // G5 "damp places.": drops fall from the trap, a damp patch spreads; pull back; lime ring round the spot.
  add('G5', 38.78, 40.16, (ctx, t) => inSink(ctx, t, camAt(t, [[38.78, cam(330, 948, 1.62)], [38.94, cam(560, 960, 1.3), eOut], [39.02, cam(560, 960, 1.31)], [39.36, cam(520, 1000, 1.06), eOut], [40.16, cam(500, 1010, 1.2)]]), {
    warm: 1, drip: prog(t, 38.78, 38.86), damp: prog(t, 38.8, 39.3),
  }, sinkBase(t, { extra: c => K.limeRing(c, 420, 930, 380, 330, prog(t, 39.12, 39.48), -0.08, 16) })));

  // ================================================================ When you inspect those areas, look for egg cases as well as live roaches.
  const beamTarget = t => {
    const keys = [[40.5, [560, 700]], [40.66, [560, 700]], [40.85, [300, 1200]], [40.88, [300, 1200]], [41.15, [850, 1056]], [41.2, [850, 1056]], [41.5, [260, 870]],
      [41.6, [260, 870]], [41.85, CRACK_CASE], [42.18, CRACK_CASE], [42.45, GAP_CASE], [42.62, GAP_CASE], [42.9, [800, 690]], [44.5, [790, 690]]];
    if (t <= keys[0][0]) return keys[0][1];
    for (let i = 1; i < keys.length; i += 1) {
      if (t <= keys[i][0]) {
        const k = eIO(prog(t, keys[i - 1][0], keys[i][0]));
        return [lerp(keys[i - 1][1][0], keys[i][1][0], k), lerp(keys[i - 1][1][1], keys[i][1][1], k)];
      }
    }
    return keys[keys.length - 1][1];
  };
  function inspect(ctx, t, camera, extra) {
    const dim = prog(t, 40.16, 40.32);
    const on = t >= 40.5 ? 1 : 0;
    const slideIn = eOut(prog(t, 40.36, 40.56));
    inSink(ctx, t, camera, { warm: 1, drip: 1, damp: 1 }, sinkBase(t, { extra }), (c2, c) => {
      const grip = [lerp(1300, 940, slideIn), lerp(2000, 1720, slideIn)];
      const bt = beamTarget(t);
      const [tx, ty] = toScreen(c, bt[0] + 7 * Math.sin(t * 7.3), bt[1] + 6 * Math.sin(t * 9.1));
      const a = Math.atan2(ty - grip[1], tx - grip[0]);
      const lens = [grip[0] + Math.cos(a) * 262 * 0.62, grip[1] + Math.sin(a) * 262 * 0.62];
      flashlightBeam(c2, lens[0], lens[1], tx, ty, 0.16, on, dim);
      if (slideIn > 0) K.flashlightHand(c2, tex, grip[0], grip[1], a, 0.62, on);
    });
  }
  // I1 "When you inspect those areas,": the cabinet dims; a flashlight sweeps the crack, the gap, the warm line.
  add('I1', 40.16, 41.6, (ctx, t) => inspect(ctx, t, camAt(t, [[40.16, cam(500, 1010, 1.2)], [41.6, cam(530, 1005, 1.24)]])));
  // I2 "look for egg cases": the beam finds the case in the crack, then the one in the gap.
  add('I2', 41.6, 42.62, (ctx, t) => inspect(ctx, t, camAt(t, [[41.6, cam(530, 1005, 1.24)], [41.85, cam(560, 1090, 1.45), eOut], [42.62, cam(580, 1080, 1.62)]]), c => {
    impactStar(c, tex, CRACK_CASE[0] + 10, CRACK_CASE[1] - 16, 34, eBack(prog(t, 41.92, 42.02), 2), 1 - prog(t, 42.06, 42.2), 0.3);
    K.limeRing(c, CRACK_CASE[0], CRACK_CASE[1] - 4, 74, 56, prog(t, 42.18, 42.36), 0, 9);
    K.limeRing(c, GAP_CASE[0], GAP_CASE[1] - 6, 70, 50, prog(t, 42.3, 42.48), 0, 9);
  }));
  // I3 "as well as live roaches.": the beam reaches the pipe gap; a live roach steps out; lime ring.
  add('I3', 42.62, 44.6, (ctx, t) => inspect(ctx, t, camAt(t, [[42.62, cam(580, 1080, 1.62)], [42.9, cam(790, 740, 2.0), eOut], [44.6, cam(780, 745, 2.2)]]), c => {
    K.limeRing(c, 790, 640, 175, 96, prog(t, 43.56, 43.82), 0, 10);
  }));

  shots.sort((a, b) => a.start - b.start);
  const lessonWorld = (ctx, t) => (shots.findLast(s => t >= s.start) ?? shots[0]).draw(ctx, t);
  const outroIndex = t => Math.round(t * 30 - OUTRO.outro_start_frame);
  function drawWorld(ctx, t) {
    if (outroIndex(t) < 0) { lessonWorld(ctx, t); return; }
    const k = outroIndex(t);
    ctx.save();
    ctx.setTransform(1, 0, 0, 1, 0, 0);
    if (k <= OUTRO.wipe_frames[1]) {
      // Approved cream-paper entry: the outgoing teaching scene stays under the wipe.
      lessonWorld(ctx, t);
      captions(ctx, t);
      ctx.save();
      ctx.beginPath();
      ctx.rect(0, 0, W, H * (k / 30) / 0.3);
      ctx.clip();
      ctx.drawImage(outroFrame(k), 0, 0);
      ctx.restore();
    } else {
      ctx.drawImage(outroFrame(k), 0, 0);
    }
    ctx.restore();
  }
  const drawOverlay = (ctx, t) => (outroIndex(t) < 0 ? captions(ctx, t) : outroCaption(ctx, t));
  const blur = [[0.92, 1.1], [4.58, 4.8], [10.72, 10.92], [19.24, 19.44], [23.14, 23.36], [28.9, 29.06], [31.44, 31.58], [35.32, 35.5], [36.28, 36.42], [39.02, 39.3], [41.6, 41.8], [42.62, 42.86]];
  return {
    duration: config.duration_seconds,
    blurWindows: blur.map(w => [...w, 7, 1 / 60]),
    drawWorld,
    drawOverlay,
    shots,
    draw(ctx, t) { drawWorld(ctx, t); drawOverlay(ctx, t); },
  };
}
