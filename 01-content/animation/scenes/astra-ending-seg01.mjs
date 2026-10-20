// D6-6c917b49743b / 57.60–67.80. Implements director shots S01–S10.
// Absolute narration time; the interiors are illustrative crops, never depth maps.
import {
  W, H, C, Path2D, clamp, lerp, eOut, eIO, eBack, prog, rng,
  makeFibres, cut, polyPath, smoothPath, ovalPath, capsulePath, bandPath,
  withCamera, placeAnt, walkPhase, tuft, drawLarva, drawPupa, createCaptions,
} from './paper-kit.mjs';
import { createYard, MOUND } from './yard-world.mjs';
import { createNest, CHAMBERS } from './nest-world.mjs';

const SCREEN = polyPath([[0, 0], [W, 0], [W, H], [0, H]]);
// Start an action on its word frame, rather than spending that frame at zero.
const hit = (t, at, length = 0.12) => t < at ? 0 : eOut(prog(t + 1 / 30, at, at + length));
const antennae = (t, phase = 0, reach = 0) => [
  [reach + 0.11 * Math.sin(t * 8 + phase), 0.12 * Math.sin(t * 6 + phase)],
  [reach + 0.09 * Math.sin(t * 7 + phase + 1), 0.1 * Math.cos(t * 5 + phase)],
];

// A macro rendering of the existing C1 nursery and its adjoining branch.
// Its chamber oval and earthy paper layers retain the nest set's vocabulary;
// staging the kit insects separately prevents the wide-set brood/nurses colliding.
function setupInterior() {
  const random = rng(8173);
  const c = CHAMBERS.C1;
  const chamber = ovalPath(590, 840, c.rx * 5.1, c.ry * 7.5, -0.025);
  const inner = ovalPath(590, 850, c.rx * 4.93, c.ry * 7.1, -0.025);
  const strata = [
    [bandPath(-1600, 2700, -400, 2700, 12, 721), C.soil],
    [bandPath(-1600, 2700, 250, 2700, 18, 722), C.soilLight],
    [bandPath(-1600, 2700, 400, 2700, 13, 723), '#A66E50'],
    [bandPath(-1600, 2700, 1160, 2700, 18, 724), '#93604A'],
    [bandPath(-1600, 2700, 1530, 2700, 17, 725), C.soilDeep],
  ];
  const stones = Array.from({ length: 115 }, (_, i) => ({
    path: ovalPath(-700 + random() * 2500, 100 + random() * 2100,
      5 + random() * 19, 4 + random() * 11, random() * 3),
    color: [C.soilPale, '#C58A61', '#85553F', '#D5A273'][i % 4],
  }));
  const floor = bandPath(-1300, 2400, 1050, 1500, 14, 726);
  const farFloor = bandPath(-1300, 2400, 690, 742, 8, 727);
  const lip = smoothPath([[-900, 450], [50, 470], [160, 620], [110, 850], [180, 1190], [-900, 1280]]);
  const rightLip = smoothPath([[1010, 400], [1100, 490], [1020, 720], [1110, 980], [1020, 1180], [2100, 1250], [2100, 400]]);
  const rim = bandPath(-1300, 2400, 1140, 2500, 16, 728);
  const revealRim = bandPath(340, 950, 870, 1210, 9, 729);
  const shutter = bandPath(-1700, 1900, -300, 2700, 13, 730);
  const shelf = smoothPath([[560, 861], [750, 853], [1090, 858], [1250, 920], [720, 910], [590, 889]]);
  const pupaShelf = smoothPath([[665, 844], [900, 839], [1180, 851], [1200, 900], [730, 885]]);
  const upperShelf = bandPath(650, 1500, 694, 735, 7, 731);
  return { chamber, inner, strata, stones, floor, farFloor, lip, rightLip, rim, revealRim, shutter, shelf, pupaShelf, upperShelf };
}

export function createScene(config, timing) {
  const texture = makeFibres(config.seed ?? 20261019);
  const yard = createYard(texture);
  const nest = createNest(texture, 7);
  const room = setupInterior();
  const captions = createCaptions(timing.words, timing.caption_groups, {
    texture, centerY: config.caption_center_y ?? 1420,
    maxWidth: 760, maxSize: 86, minSize: 52, lead: 0,
  });
  const grassColors = [C.grass, C.grassDeep, C.limeDark];
  const soilShoulders = [
    smoothPath([[248, 1056], [328, 954], [458, 969], [564, 1067], [420, 1090]]),
    smoothPath([[432, 1041], [534, 916], [661, 955], [797, 1066], [622, 1080]]),
    smoothPath([[300, 1072], [396, 1007], [520, 1033], [645, 1071], [450, 1100]]),
  ];
  const turf = bandPath(-1500, 2600, 760, 788, 5, 840);
  const moundMask = new Path2D();
  moundMask.rect(-2000, -1400, 5000, 2159);
  const undergroundClip = new Path2D();
  undergroundClip.rect(-2000, 778, 5000, 274);
  const lowerCover = bandPath(-2000, 3000, 1052, 3600, 9, 841);
  const skyEdge = bandPath(-2000, 3000, -2000, 372, 0, 842);
  const highTurf = bandPath(-1500, 2600, 372, 407, 6, 850);

  function base(ctx, color) { cut(ctx, SCREEN, color, texture, 0); }
  function soil(ctx) {
    for (const [path, color] of room.strata) cut(ctx, path, color, texture, 9);
    for (const p of room.stones) cut(ctx, p.path, p.color, texture, 3);
  }
  function interiorBack(ctx, lanes = false) {
    soil(ctx);
    // Round-capped branch strokes, never Path2D.addPath unions.
    ctx.save();
    ctx.lineCap = 'round';
    for (const [width, color] of [[244, C.tunnel], [204, C.tunnelInner]]) {
      ctx.strokeStyle = color; ctx.lineWidth = width;
      ctx.beginPath(); ctx.moveTo(-1200, 880); ctx.quadraticCurveTo(100, 830, 420, 870); ctx.stroke();
      if (lanes) {
        ctx.beginPath(); ctx.moveTo(-1200, 620); ctx.bezierCurveTo(100, 610, 790, 540, 1800, 620); ctx.stroke();
      }
    }
    ctx.restore();
    cut(ctx, room.chamber, C.tunnel, texture, 13);
    cut(ctx, room.inner, C.tunnelInner, texture, 2);
    ctx.save(); ctx.clip(room.inner);
    cut(ctx, room.floor, '#B68560', texture, 8);
    if (lanes) {
      cut(ctx, room.farFloor, '#A67554', texture, 6);
      cut(ctx, room.shelf, '#A67554', texture, 7);
    }
    ctx.restore();
  }
  function nearRim(ctx, t, origin, amount = 1, leftOffset = 0) {
    ctx.save(); ctx.translate(leftOffset - 65 * (t - origin), 0);
    cut(ctx, room.lip, '#9B674C', texture, 16);
    ctx.restore();
    ctx.save(); ctx.translate(-110 * (t - origin), 0);
    cut(ctx, room.rightLip, '#AC7855', texture, 14);
    ctx.restore();
    ctx.save(); ctx.translate(-100 * (t - origin), 20 * amount);
    cut(ctx, room.rim, '#B57553', texture, 15);
    ctx.restore();
  }
  function worker(ctx, x, y, scale, distance, t, faceRight, extras = {}) {
    placeAnt(ctx, texture, x, y, scale, {
      walk: 1, phase: walkPhase(distance, scale), antennae: antennae(t, x * 0.01), ...extras,
    }, { faceRight });
  }
  function restingBrood(ctx, t, mode = 0) {
    if (mode === 0) {
      drawLarva(ctx, texture, 490, 985, 1.05, -0.2, Math.sin(t * 3));
      drawLarva(ctx, texture, 620, 984, 1.00, 0.28, Math.sin(t * 3.2 + 2));
    } else {
      drawLarva(ctx, texture, 663, 1000, 0.73, -0.2, Math.sin(t * 3));
      drawLarva(ctx, texture, 766, 1004, 0.68, 0.2, Math.sin(t * 3 + 2));
    }
  }
  function slideCover(ctx, edge, top = 320, fromRight = false) {
    // Opaque torn paper. Occlusion changes visibility only, never the ant state.
    const teeth = [];
    for (let y = top; y <= 2400; y += 35) teeth.push([edge + 9 * Math.sin(y * 0.041), y]);
    const side = fromRight ? 2400 : -1800;
    const path = polyPath([[side, top], ...teeth, [side, 2400]]);
    cut(ctx, path, '#A66E50', texture, 18);
    ctx.save(); ctx.clip(path);
    for (const p of room.stones) cut(ctx, p.path, p.color, texture, 3);
    ctx.restore();
  }

  function yardShot(ctx, t, shot) {
    const first = shot === 1;
    const wide = shot === 10;
    const start = first ? 57.60 : wide ? 66.64 : 65.82;
    const length = first ? 0.96 : wide ? 1.16 : 0.82;
    const p = prog(t, start, start + length);
    const cam = first
      ? { x: 542 + 45 * p, y: 980 - 7 * hit(t, 57.96), zoom: 1.17 + 0.058 * p }
      : wide
        ? { x: 551 + 60 * p, y: 1080 - 12 * p, zoom: 1.13 - 0.0565 * p }
        : { x: 550 + 65 * p, y: 997 - 10 * p, zoom: 1.28 + 0.04 * p };
    base(ctx, C.sky);
    withCamera(ctx, cam, () => {
      // A local time keeps the kit's drifting clouds in this composition.
      yard.drawBack(ctx, 8 + (t - 57.6) * 1.6, { mound: 1 });
      if (first || !wide) {
        const drift = 28 * p + (first ? 12 * hit(t, 57.69) + 8 * hit(t, 57.96) : 10 * hit(t, 66.26));
        soilShoulders.forEach((path, i) => {
          ctx.save(); ctx.translate(-drift * (0.3 + i * 0.3), 0);
          cut(ctx, path, ['#C58B60', '#9B674C', '#B57553'][i], texture, 6 + i * 2);
          ctx.restore();
        });
      }
      // Near grass passes across the lower action area, ahead of the lawn.
      for (let i = 0; i < 6; i += 1) {
        const x = -30 + i * 220 - 125 * p;
        tuft(ctx, texture, x, 1210, 112 + (i % 3) * 28, 900 + i, grassColors,
          0.09 * Math.sin(t * 3 + i));
      }
      if (first && t >= 58.36) {
        const k = hit(t, 58.36, 0.14);
        const lx = lerp(295, 420, k), ly = lerp(912, 898, k);
        // Reuse the set's complete magnifier. Its callback draws enlarged
        // surface material only: no tunnel, worker, or brood can appear here.
        yard.drawFront(ctx, t, { lens: {
          x: lx, y: ly, r: 120, angle: -0.2,
          xray(c) {
            c.save(); c.translate(lx, ly); c.scale(1.8, 1.8); c.translate(-lx, -ly);
            yard.drawBack(c, 8 + (t - 57.6) * 1.6, { mound: 1 }); c.restore();
          },
        } });
      }
    });
  }

  function surfaceSection(ctx, t, covered) {
    const start = covered ? 59.47 : 58.56;
    const p = prog(t, start, covered ? 60.22 : 59.47);
    base(ctx, C.sky);
    const cam = covered
      ? { x: 552 + 90 * p, y: 902 + 12 * p, zoom: 1.18 + 0.047 * p }
      : { x: 537 + 68 * p, y: 909 - 16 * p, zoom: 1.13 + 0.035 * p };
    withCamera(ctx, cam, () => {
      nest.draw(ctx, t, { traffic: 0, surfaceAnts: 0, fairClouds: 1, cover: covered ? hit(t, 59.47, 0.12) : 0 });
      // Above the turf, keep the mound opaque. The open illustration starts
      // below the surface, and cannot be mistaken for a central mound hole.
      ctx.save(); ctx.clip(moundMask);
      nest.draw(ctx, t, { traffic: 0, surfaceAnts: 0, tunnelsDraw: -1, fairClouds: 1 });
      ctx.restore();
      ctx.save(); ctx.clip(undergroundClip);
      if (!covered) {
        // The lateral crop exposes the second branch during the hold.
        const edge = 720 + 160 * hit(t, 59.24, 0.13);
        ctx.save(); ctx.translate(edge + 1700, 0);
        cut(ctx, room.shutter, '#A66E50', texture, 14); ctx.restore();
      }
      ctx.restore();
      cut(ctx, lowerCover, '#A66E50', texture, 10);
      cut(ctx, turf, C.grass, texture, 6);
      tuft(ctx, texture, 140 - p * 85, 771, 118, 905, grassColors, 0.10 * Math.sin(t * 3));
      tuft(ctx, texture, 920 - p * 65, 771, 130, 906, grassColors, 0.08 * Math.sin(t * 3 + 2));
    });
  }

  function nurseryReveal(ctx, t) {
    const p = prog(t, 60.22, 61.42);
    base(ctx, C.soil);
    withCamera(ctx, { x: 520 + 46 * p, y: 966 - 76 * p, zoom: 0.91 + 0.073 * p }, () => {
      interiorBack(ctx);
      restingBrood(ctx, t);
      // The pupa is behind its own small paper rim until the word 'ants'.
      drawPupa(ctx, texture, 805, 1020, 0.36, -0.05);
      const reveal = hit(t, 60.66, 0.12);
      ctx.save(); ctx.translate(0, 420 * reveal);
      cut(ctx, room.revealRim, '#B68560', texture, 12); ctx.restore();
      if (t < 61.08) {
        cut(ctx, smoothPath([[680, 760], [1100, 760], [1100, 1145], [720, 1145]]), '#9B674C', texture, 10);
      } else {
        const move = hit(t, 61.08, 0.13);
        ctx.save(); ctx.translate(430 * move, 0);
        cut(ctx, smoothPath([[680, 760], [1100, 760], [1100, 1145], [720, 1145]]), '#9B674C', texture, 10);
        ctx.restore();
        const d = 70 * move;
        worker(ctx, 186 + d, 1045, 0.52, d, t, true, { walk: move < 1 ? 1 : 0, head: 0.03 });
      }
      nearRim(ctx, t, 60.22);
      // Reveal the covered diagram from its left edge within 0.12 s.
      const open = hit(t, 60.22, 0.12);
      if (open < 1) slideCover(ctx, 1200 - 2400 * open, -500);
    });
  }

  function nurseryTending(ctx, t) {
    const p = prog(t, 61.42, 62.73);
    base(ctx, C.soil);
    withCamera(ctx, { x: 505 + 36 * p, y: 989 - 70 * p, zoom: 0.98 + 0.049 * p }, () => {
      interiorBack(ctx);
      ctx.save(); ctx.clip(room.inner);
      cut(ctx, room.pupaShelf, '#A67554', texture, 7);
      cut(ctx, room.upperShelf, '#A67554', texture, 6);
      ctx.restore();
      restingBrood(ctx, t, 1);
      drawPupa(ctx, texture, 795, 815, 0.29, 0.02);
      // 61.58 anticipation lowers the held larva; contact/release is 61.74.
      const arrival = eOut(prog(t, 61.42, 61.70));
      const x = 250 + 50 * arrival;
      const lower = eIO(prog(t, 61.58, 61.74));
      const recover = hit(t, 61.74, 0.25);
      const liftHead = hit(t, 62.14, 0.15);
      const bob = 55 * lower * (1 - recover);
      worker(ctx, x, 1050, 0.72, 50 * arrival, t, true, {
        walk: t < 61.70 ? 1 : 0,
        bob, head: -0.10 * liftHead + 0.02 * Math.sin(t * 4) * liftHead,
        mand: t >= 61.74 ? 0.6 * (1 - liftHead * 0.6) : 0,
        carry: t < 61.74 ? 'larva' : null,
        antennae: antennae(t, 2, -0.13 * liftHead),
      });
      if (t >= 61.74) {
        // Exact carried-larva centre at the release frame, with grounded flex.
        ctx.save(); ctx.translate(519.6, 1008.24); ctx.scale(-1, 1);
        drawLarva(ctx, texture, 0, 0, 0.72, 0, Math.sin((t - 61.74) * 3) * 0.45);
        ctx.restore();
      }
      if (t >= 62.54) {
        const d = 50 * hit(t, 62.54, 0.15);
        worker(ctx, 815 - d, 693, 0.36, d, t, false);
      }
      nearRim(ctx, t, 61.42, 1, -180);
    });
  }

  function colonyActors(ctx, t, shot) {
    if (shot === 6) {
      const u = t - 62.73;
      worker(ctx, 620 + u * 94, 1060, 0.43, u * 94, t, true);
      if (t >= 62.84) {
        const d = 115 * (t - 62.84);
        worker(ctx, 190 + d, 1060, 0.40, d, t, true);
      }
      worker(ctx, 790, 860, 0.34, 0, t, false, { walk: 0, head: 0.09 * Math.sin(t * 4) });
      drawLarva(ctx, texture, 640, 822, 0.58, -0.16, Math.sin(t * 3));
      if (t >= 63.32) {
        const d = 95 * (t - 63.32);
        worker(ctx, 430 + d, 691, 0.35, d, t, true);
      }
    } else {
      const u = t - 63.76;
      worker(ctx, 310 + 158 * u, 1060, 0.51, 158 * u, t, true);
      worker(ctx, 785, 860, 0.37, 0, t, false, {
        walk: 0, head: 0.16 * hit(t, 63.76, 0.12) + 0.055 * Math.sin(t * 5),
        antennae: antennae(t, 1, -0.11),
      });
      drawLarva(ctx, texture, 611, 817, 0.57, -0.2, Math.sin(t * 3.2));
      if (t >= 64.26) {
        const d = 120 * (t - 64.26);
        worker(ctx, 540 - d, 691, 0.36, d, t, false);
      }
    }
  }
  function colony(ctx, t, shot) {
    const start = shot === 6 ? 62.73 : shot === 7 ? 63.76 : 65.06;
    const end = shot === 6 ? 63.76 : shot === 7 ? 65.06 : 65.82;
    const p = prog(t, start, end);
    const cam = shot === 6
      ? { x: 485 + 64 * p, y: 988 - 85 * p, zoom: 0.89 + 0.036 * p }
      : shot === 7
        ? { x: 510 + 114 * p, y: 1000 - 90 * p, zoom: 1.04 + 0.04 * p }
        : { x: 575 + 36 * p, y: 1010 - 95 * p, zoom: 0.91 + 0.03 * p };
    base(ctx, C.soil);
    withCamera(ctx, cam, () => {
      interiorBack(ctx, true);
      colonyActors(ctx, t, shot);
      nearRim(ctx, t, start);
      if (shot === 8) {
        // Successive occlusions on out / of / sight. No fades or frozen ants.
        let edge;
        if (t < 65.36) edge = lerp(730, 530, hit(t, 65.06, 0.30));
        else if (t < 65.52) edge = lerp(530, 290, hit(t, 65.36, 0.16));
        else edge = -1600;
        slideCover(ctx, edge, 390, true);
        cut(ctx, skyEdge, C.sky, texture, 0);
        cut(ctx, highTurf, C.grass, texture, 7);
        for (const x of [150, 590, 940]) tuft(ctx, texture, x, 375, 70, x, grassColors, 0.06 * Math.sin(t * 3));
      }
    });
  }

  function drawWorld(ctx, t) {
    if (t < 58.56) yardShot(ctx, t, 1);
    else if (t < 59.47) surfaceSection(ctx, t, false);
    else if (t < 60.22) surfaceSection(ctx, t, true);
    else if (t < 61.42) nurseryReveal(ctx, t);
    else if (t < 62.73) nurseryTending(ctx, t);
    else if (t < 63.76) colony(ctx, t, 6);
    else if (t < 65.06) colony(ctx, t, 7);
    else if (t < 65.82) colony(ctx, t, 8);
    else if (t < 66.64) yardShot(ctx, t, 9);
    else yardShot(ctx, t, 10);
  }
  function drawOverlay(ctx, t) {
    ctx.save(); ctx.translate(-40, 0); captions(ctx, t); ctx.restore();
  }
  return {
    duration: config.duration_seconds, blurWindows: [], drawWorld, drawOverlay,
    draw(ctx, t) { drawWorld(ctx, t); drawOverlay(ctx, t); },
  };
}
