import { createCanvas, Path2D, rng, grainCanvas, smooth, ellipse, line, lerp } from '../vendor/claude-animation/core.mjs';
import { fibrePaper } from '../vendor/claude-animation/textures.mjs';
import { roots } from '../vendor/claude-animation/colony.mjs';

// Original fire-ant artwork. Reference coordinates: 1080 x 1920.
// All raster materials belong to this scene; draw() never creates a texture.
const TAU = Math.PI * 2;
const REF_W = 1080, REF_H = 1920;
const HERO = { x: 566, y: 1110, scale: 1.08 };

function seedOf(value) {
  const s = String(value == null ? 37 : value);
  let h = 2166136261;
  for (let i = 0; i < s.length; i++) h = Math.imul(h ^ s.charCodeAt(i), 16777619);
  return (h >>> 0) % 2147483646 + 1;
}
function path(d) { return new Path2D(d); }
function wash(ctx, x, y, radius, color) {
  const g = ctx.createRadialGradient(x, y, 0, x, y, radius);
  g.addColorStop(0, color); g.addColorStop(1, 'rgba(190,155,104,0)');
  ctx.fillStyle = g; ctx.fillRect(x - radius, y - radius, radius * 2, radius * 2);
}
function inkPath(ctx, p, color, width) {
  ctx.strokeStyle = color; ctx.lineWidth = width; ctx.stroke(p);
}
function specks(ctx, random, count, box, colors, alpha, maxRadius) {
  ctx.save();
  for (let i = 0; i < count; i++) {
    const x = lerp(box[0], box[2], random()), y = lerp(box[1], box[3], random());
    const r = .35 + random() * maxRadius;
    ctx.globalAlpha = alpha * (.2 + random() * .8);
    ctx.fillStyle = colors[i % colors.length];
    ellipse(ctx, x, y, r, r * (.45 + random() * .45), random() * Math.PI);
    ctx.fill();
  }
  ctx.restore();
}
function pebble(ctx, x, y, size, rotation, color) {
  ctx.save(); ctx.translate(x, y); ctx.rotate(rotation);
  const p = path('M -18 2 C -21 -5 -10 -13 0 -12 C 12 -12 23 -3 20 4 C 17 13 -10 13 -18 2 Z');
  ctx.scale(size / 20, size / 20);
  ctx.fillStyle = color; ctx.fill(p);
  inkPath(ctx, p, 'rgba(58,41,29,.36)', 1.2);
  inkPath(ctx, path('M -12 -4 Q -2 -11 11 -5'), 'rgba(244,220,183,.4)', 1.4);
  ctx.restore();
}

// A continuous, tapered, legless grub, with a small head at its narrow end.
function makeGrub() {
  const A = [-213, 6], B = [-299, -20], C = [-301, 100], D = [-232, 110];
  const at = t => {
    const u = 1 - t;
    const x = u*u*u*A[0] + 3*u*u*t*B[0] + 3*u*t*t*C[0] + t*t*t*D[0];
    const y = u*u*u*A[1] + 3*u*u*t*B[1] + 3*u*t*t*C[1] + t*t*t*D[1];
    const dx = 3*u*u*(B[0]-A[0]) + 6*u*t*(C[0]-B[0]) + 3*t*t*(D[0]-C[0]);
    const dy = 3*u*u*(B[1]-A[1]) + 6*u*t*(C[1]-B[1]) + 3*t*t*(D[1]-C[1]);
    const length = Math.hypot(dx, dy);
    const tx = dx / length, ty = dy / length;
    return { x, y, tx, ty, nx: -ty, ny: tx, r: 9 + 15 * Math.sin(Math.PI * (.2 + .8*t)) };
  };
  const samples = Array.from({ length: 65 }, (_, i) => at(i / 64));
  const outline = new Path2D(), points = [];
  samples.forEach((p, i) => {
    const x = p.x + p.nx*p.r, y = p.y + p.ny*p.r;
    if (i) outline.lineTo(x, y); else outline.moveTo(x, y);
    points.push([x, y]);
  });
  const cap = (p, start) => {
    for (let k = 1; k <= 16; k++) {
      const a = start - Math.PI * k / 16;
      const q = [p.x + Math.cos(a)*p.r, p.y + Math.sin(a)*p.r];
      outline.lineTo(...q); points.push(q);
    }
  };
  const end = samples[samples.length - 1], first = samples[0];
  cap(end, Math.atan2(end.ny, end.nx));
  for (let i = samples.length - 2; i >= 0; i--) {
    const p = samples[i], q = [p.x - p.nx*p.r, p.y - p.ny*p.r];
    outline.lineTo(...q); points.push(q);
  }
  cap(first, Math.atan2(first.ny, first.nx) + Math.PI);
  outline.closePath();
  return { outline, at, samples, points };
}

function tracked(ctx, text, x, y, size, spacing, maxWidth, color) {
  if (!text) return;
  const chars = Array.from(text);
  ctx.font = '500 ' + size + 'px D6Sans';
  let total = chars.reduce((n, c) => n + ctx.measureText(c).width, 0) + spacing * Math.max(0, chars.length - 1);
  if (total > maxWidth) {
    const ratio = maxWidth / total;
    size *= ratio; spacing *= ratio;
    ctx.font = '500 ' + size + 'px D6Sans';
  }
  ctx.fillStyle = color;
  for (const c of chars) { ctx.fillText(c, x, y); x += ctx.measureText(c).width + spacing; }
}
function fitLines(ctx, text, maxWidth, startSize, family, maxLines = 2) {
  const clean = String(text).trim();
  if (!clean) return { lines: [], size: startSize };
  const hard = clean.split(/\n+/);
  let size = startSize, lines = [];
  for (;;) {
    ctx.font = '400 ' + size + 'px ' + family;
    lines = [];
    for (const paragraph of hard) {
      const words = paragraph.trim().split(/\s+/);
      let row = '';
      for (const word of words) {
        const candidate = row ? row + ' ' + word : word;
        if (row && ctx.measureText(candidate).width > maxWidth) { lines.push(row); row = word; }
        else row = candidate;
      }
      if (row) lines.push(row);
    }
    if (lines.length <= maxLines && lines.every(s => ctx.measureText(s).width <= maxWidth)) break;
    if (size <= 8) break;
    size -= 1;
  }
  // Balance a two-line editorial title without changing the supplied words.
  if (family === 'D6Serif' && hard.length === 1 && lines.length === 2) {
    const words = clean.split(/\s+/);
    let best = lines, score = Infinity;
    for (let i = 1; i < words.length; i++) {
      const a = words.slice(0, i).join(' '), b = words.slice(i).join(' ');
      const wa = ctx.measureText(a).width, wb = ctx.measureText(b).width;
      if (Math.max(wa, wb) <= maxWidth && Math.abs(wa - wb) < score) {
        best = [a, b]; score = Math.abs(wa - wb);
      }
    }
    lines = best;
  }
  return { lines, size };
}

export function createScene(config) {
  const W = Number(config.width == null ? REF_W : config.width);
  const H = Number(config.height == null ? REF_H : config.height);
  if (!(W > 0 && H > 0 && Number.isFinite(W) && Number.isFinite(H))) throw new RangeError('Invalid scene dimensions');
  const seed = seedOf(config.seed);
  const P = Object.assign({
    cream: '#F5EEDD', paper: '#EEE3CD', ink: '#30271F', purple: '#62506F', lime: '#BBC86B'
  }, config.palette || {});
  const labels = {};
  for (const key of ['eyebrow', 'title', 'footer', 'illustrationNote']) {
    labels[key] = String((config.labels || {})[key] || '');
  }
  // Default is the still submitted for review. A later caller can opt into
  // quiet articulation without changing the art or releasing any planted foot.
  const motion = Math.max(0, Math.min(1, Number(config.motion) || 0));
  const grain = grainCanvas(256, 62, seed);
  const grub = makeGrub();
  const anatomy = {
    neck: path('M -99 -7 Q -78 -12 -62 -5 L -59 13 Q -80 20 -98 15 Z'),
    thorax: path('M -69 -3 C -63 -21 -47 -31 -32 -27 C -18 -26 -11 -13 2 -11 C 14 -15 26 -13 34 -6 C 46 -6 58 4 57 17 C 59 31 45 37 32 32 C 16 30 11 27 -2 29 C -25 29 -47 25 -60 17 C -69 12 -73 6 -69 -3 Z'),
    head: path('M -91 -45 C -100 -69 -119 -86 -146 -83 C -170 -83 -187 -63 -188 -39 C -191 -18 -180 9 -167 21 C -151 36 -123 34 -106 20 C -91 10 -82 -14 -91 -45 Z'),
    petiole: path('M 62 22 C 66 15 64 7 69 -1 C 73 -10 83 -9 87 0 C 92 10 85 18 91 25 C 83 31 70 29 62 26 Z'),
    postpetiole: path('M 99 24 C 99 12 104 6 114 7 C 125 7 132 17 129 27 C 121 36 109 35 99 30 Z'),
    gaster: path('M 133 14 C 146 -11 177 -39 219 -37 C 258 -36 283 -12 286 22 C 290 55 266 80 232 84 C 194 89 158 72 141 49 C 130 36 127 24 133 14 Z'),
    farJaw: path('M -177 -9 C -190 -9 -202 1 -208 13 L -205 24 L -199 24 C -198 11 -186 7 -176 9 Z'),
    nearJaw: path('M -176 17 C -185 23 -195 24 -204 19 L -211 16 C -213 24 -209 30 -202 33 C -190 37 -180 30 -171 25 Z')
  };
  const shellPatternCanvas = grainCanvas(128, 46, seed + 19);

  function shell(ctx, p, top, bottom, box, width = 1.8) {
    const g = ctx.createLinearGradient(box[0], box[1], box[2], box[3]);
    g.addColorStop(0, top); g.addColorStop(1, bottom);
    ctx.fillStyle = g; ctx.fill(p);
    ctx.save(); ctx.clip(p);
    ctx.globalCompositeOperation = 'multiply'; ctx.globalAlpha = .28;
    ctx.fillStyle = ctx.createPattern(shellPatternCanvas, 'repeat');
    ctx.fillRect(-330, -210, 680, 450); ctx.restore();
    inkPath(ctx, p, '#482D22', width);
  }
  function drawGrub(ctx) {
    const g = ctx.createLinearGradient(-285, 5, -237, 122);
    g.addColorStop(0, '#F7EDD4'); g.addColorStop(.48, '#EEE1C0'); g.addColorStop(1, '#D4C19A');
    ctx.fillStyle = g; ctx.fill(grub.outline);
    ctx.save(); ctx.clip(grub.outline);
    ctx.globalCompositeOperation = 'multiply'; ctx.globalAlpha = .15;
    ctx.fillStyle = ctx.createPattern(shellPatternCanvas, 'repeat');
    ctx.fillRect(-320, -30, 140, 170); ctx.restore();
    for (let i = 1; i <= 9; i++) {
      const p = grub.at(i / 10);
      ctx.beginPath();
      ctx.moveTo(p.x + p.nx*p.r*.82, p.y + p.ny*p.r*.82);
      ctx.quadraticCurveTo(p.x + p.tx*3.2, p.y + p.ty*3.2,
        p.x - p.nx*p.r*.86, p.y - p.ny*p.r*.86);
      ctx.strokeStyle = 'rgba(135,112,76,.32)'; ctx.lineWidth = 1.05; ctx.stroke();
    }
    inkPath(ctx, grub.outline, '#9A825C', 1.45);
    // The small ochre head belongs to the larva, not an eye or limb.
    ellipse(ctx, -228.5, 110.5, 7, 6.2, .14);
    ctx.fillStyle = '#C8B187'; ctx.fill();
    ctx.strokeStyle = '#A18A63'; ctx.lineWidth = .8; ctx.stroke();
    line(ctx, [[-223.8, 109.6], [-222.5, 111.7]], .8, '#806846');
    // Very sparse fine larval setae.
    for (const t of [.23, .39, .58, .76]) {
      const p = grub.at(t);
      line(ctx, [[p.x + p.nx*p.r, p.y + p.ny*p.r],
        [p.x + p.nx*(p.r+2.3), p.y + p.ny*(p.r+2.3)]], .55, 'rgba(126,105,71,.44)');
    }
  }

  const ground = path('M -30 516 C 77 490 161 516 264 502 C 388 486 467 516 607 505 C 751 495 883 486 1110 510 L 1110 1950 L -30 1950 Z');
  const rooms = [
    path('M 126 694 C 150 651 238 647 316 666 C 377 679 428 710 416 745 C 405 783 344 795 283 793 C 223 801 166 781 136 763 C 107 745 106 721 126 694 Z'),
    path('M 112 1002 C 122 938 204 895 292 897 C 356 898 380 866 448 851 C 550 822 655 851 753 873 C 848 895 942 873 979 950 C 1018 1030 1001 1159 967 1234 C 946 1289 884 1313 789 1315 C 681 1322 566 1320 465 1317 C 394 1312 340 1321 285 1323 C 203 1328 148 1306 130 1266 C 109 1224 116 1170 101 1117 C 89 1075 91 1040 112 1002 Z'),
    path('M 406 1430 C 449 1391 533 1398 600 1392 C 687 1379 764 1398 791 1441 C 822 1492 773 1539 705 1550 C 633 1563 563 1553 497 1547 C 443 1542 406 1522 401 1484 C 396 1461 399 1444 406 1430 Z')
  ];
  // Draw all cavities into ONE alpha mask. Room/tunnel junctions have no seams.
  const mask = createCanvas(REF_W, REF_H), mc = mask.getContext('2d');
  mc.fillStyle = '#FFFFFF'; mc.strokeStyle = '#FFFFFF'; mc.lineCap = 'round'; mc.lineJoin = 'round';
  for (const r of rooms) mc.fill(r);
  for (const [d, w] of [
    ['M -35 565 C 31 577 72 620 103 651 C 129 678 150 704 180 722', 43],
    ['M 352 746 C 370 786 442 796 447 831 C 452 860 420 887 404 918', 78],
    ['M 908 1245 C 930 1320 861 1369 788 1407 C 744 1430 720 1448 696 1473', 84]
  ]) {
    mc.lineWidth = w; mc.stroke(path(d));
  }

  function edgeBand(dx, dy, color) {
    const c = createCanvas(REF_W, REF_H), x = c.getContext('2d');
    x.drawImage(mask, 0, 0);
    x.globalCompositeOperation = 'source-in'; x.fillStyle = color; x.fillRect(0, 0, REF_W, REF_H);
    x.globalCompositeOperation = 'destination-out'; x.drawImage(mask, dx, dy);
    x.globalCompositeOperation = 'source-over';
    return c;
  }

  const background = fibrePaper(REF_W, REF_H, P.cream);
  const b = background.getContext('2d');
  b.lineCap = 'round'; b.lineJoin = 'round';

  // Quiet, distant domestic context; the dry surface has no central mound.
  b.save(); b.globalAlpha = .62;
  const house = path('M 789 431 L 848 390 L 914 431 L 914 493 L 789 493 Z');
  b.fillStyle = P.paper; b.fill(house);
  inkPath(b, house, '#A7977F', 1.4);
  b.fillStyle = '#C9BDA6'; b.fill(path('M 776 433 L 847 381 L 929 432 L 913 433 L 848 396 L 790 437 Z'));
  inkPath(b, path('M 776 433 L 847 381 L 929 432'), '#958874', 1.6);
  b.fillStyle = '#C3B79F'; b.fillRect(844, 451, 19, 42);
  b.strokeStyle = '#ADA18B'; b.lineWidth = 1.2; b.strokeRect(805, 450, 18, 19); b.strokeRect(881, 450, 18, 19);
  line(b, [[814,450],[814,469]], .8, '#ADA18B');
  line(b, [[890,450],[890,469]], .8, '#ADA18B');
  line(b, [[773,494],[944,494]], 1.1, '#A99A80');
  b.restore();

  b.save(); b.clip(ground);
  const earth = b.createLinearGradient(0, 490, 0, REF_H);
  earth.addColorStop(0, '#B59A76'); earth.addColorStop(.22, '#9B7955');
  earth.addColorStop(.56, '#8A6749'); earth.addColorStop(1, '#70513D');
  b.fillStyle = earth; b.fillRect(0, 480, REF_W, REF_H);
  const soilRandom = rng(seed + 71);
  // Broad irregular mineral stains, not a uniform hatch.
  for (let i = 0; i < 105; i++) {
    const x = soilRandom()*REF_W, y = 525 + soilRandom()*1400;
    const rx = 35 + soilRandom()*165, ry = 12 + soilRandom()*58;
    const points = [];
    for (let j = 0; j < 10; j++) {
      const a = j/10*TAU, rr = .72 + soilRandom()*.32;
      points.push([x + Math.cos(a)*rx*rr, y + Math.sin(a)*ry*rr]);
    }
    smooth(b, points); b.globalAlpha = .035 + soilRandom()*.055;
    b.fillStyle = i % 3 ? '#E0C49B' : '#533B2B'; b.fill();
  }
  b.globalAlpha = 1;
  const strata = [
    ['M -40 566 C 160 614 270 556 459 582 S 813 609 1130 564', 30, 'rgba(224,198,154,.16)'],
    ['M -40 798 C 147 748 277 822 472 793 S 873 764 1120 802', 17, 'rgba(75,48,31,.08)'],
    ['M -40 1378 C 159 1351 258 1418 442 1387 S 840 1344 1120 1385', 29, 'rgba(215,178,130,.09)'],
    ['M -20 1587 C 230 1640 364 1570 572 1597 S 856 1642 1110 1590', 34, 'rgba(211,174,125,.07)']
  ];
  for (const [d, w, color] of strata) inkPath(b, path(d), color, w);
  specks(b, soilRandom, 7800, [0, 510, REF_W, REF_H],
    ['#E6CEAA', '#4D3627', '#C5A57C', '#62432E'], .3, 1.55);
  // Short broken sediment marks occur in clusters, leaving large quiet areas.
  for (let i = 0; i < 360; i++) {
    const x = soilRandom()*REF_W, y = 540 + soilRandom()*1320;
    if (Math.sin(x*.011 + y*.007) < .25) continue;
    const length = 3 + soilRandom()*14;
    line(b, [[x,y],[x+length,y-1.4]], .7, 'rgba(60,40,26,.2)');
  }
  b.globalCompositeOperation = 'multiply'; b.globalAlpha = .23;
  b.fillStyle = b.createPattern(grain, 'repeat'); b.fillRect(0, 490, REF_W, 1430);
  b.globalCompositeOperation = 'source-over'; b.globalAlpha = 1;

  // Roots and stones precede the opaque cavity layer: none cross empty space.
  b.save(); b.globalAlpha = .48;
  roots(b, 72, 507, 515, seed + 11, 2.8);
  roots(b, 956, 500, 362, seed + 29, 3.3);
  roots(b, 565, 506, 186, seed + 47, 2);
  b.restore();
  for (const p of [
    [477,665,13,.3,'#B7A486'], [807,724,22,-.2,'#9A927F'],
    [86,860,12,.7,'#C1AD8D'], [236,1415,20,.3,'#AC9679'],
    [957,1435,16,-.6,'#9E8B72'], [834,1578,13,.2,'#B8A083'],
    [121,1729,18,-.3,'#927E68'], [1039,1158,21,.8,'#B29D7C']
  ]) pebble(b, ...p);
  const depth = b.createLinearGradient(0, 1460, 0, REF_H);
  depth.addColorStop(0, 'rgba(49,32,24,0)'); depth.addColorStop(.47, 'rgba(49,32,24,.22)');
  depth.addColorStop(1, 'rgba(49,32,24,.28)');
  b.fillStyle = depth; b.fillRect(0, 1460, REF_W, 460);

  const interior = createCanvas(REF_W, REF_H), ic = interior.getContext('2d');
  const cavityColor = ic.createLinearGradient(0, 640, 0, 1570);
  cavityColor.addColorStop(0, '#CDB38D'); cavityColor.addColorStop(.34, '#E2CCA6');
  cavityColor.addColorStop(.65, '#D9BD93'); cavityColor.addColorStop(1, '#B89A75');
  ic.fillStyle = cavityColor; ic.fillRect(0, 0, REF_W, REF_H);
  wash(ic, 365, 1008, 459, 'rgba(255,242,207,.38)');
  wash(ic, 875, 1180, 345, 'rgba(153,111,70,.12)');
  specks(ic, rng(seed + 81), 3800, [0, 550, REF_W, 1580],
    ['#FFF1D2', '#816241', '#B49569'], .15, 1.15);
  ic.globalCompositeOperation = 'multiply'; ic.globalAlpha = .14;
  ic.fillStyle = ic.createPattern(grain, 'repeat'); ic.fillRect(0, 500, REF_W, 1100);
  ic.globalCompositeOperation = 'source-over'; ic.globalAlpha = 1;
  // Sloping floor planes, clipped together with the rooms and passages.
  const floor = ic.createLinearGradient(0, 1257, 0, 1330);
  floor.addColorStop(0, 'rgba(146,108,70,0)');
  floor.addColorStop(.45, 'rgba(155,117,78,.24)');
  floor.addColorStop(1, 'rgba(116,80,48,.35)');
  ic.fillStyle = floor;
  ic.fill(path('M 70 1282 C 220 1256 354 1278 474 1279 C 650 1280 833 1290 1004 1246 L 1040 1363 L 60 1363 Z'));
  inkPath(ic, path('M 144 769 C 232 786 317 787 392 764'), 'rgba(118,86,51,.26)', 3);
  inkPath(ic, path('M 426 1514 C 514 1535 653 1538 749 1520'), 'rgba(105,76,48,.22)', 2.5);
  ic.globalCompositeOperation = 'destination-in'; ic.drawImage(mask, 0, 0);
  ic.globalCompositeOperation = 'source-over';

  // A soft outside rim and two continuous interior edge bands.
  b.save(); b.shadowColor = 'rgba(56,36,22,.44)'; b.shadowBlur = 19; b.shadowOffsetY = 3;
  b.drawImage(interior, 0, 0); b.restore();
  b.drawImage(edgeBand(0, 12, 'rgba(92,63,37,.22)'), 0, 0);
  b.drawImage(edgeBand(0, 3, 'rgba(74,50,29,.28)'), 0, 0);
  b.drawImage(edgeBand(0, -3, 'rgba(241,214,167,.31)'), 0, 0);

  // A few resting larvae are subordinate to the single carried larva.
  for (const [x, s, a, floorY] of [[484,.24,-.6,1525], [528,.28,.56,1531], [569,.22,-.18,1527]]) {
    const lowest = Math.max(...grub.points.map(p => ((p[0]+250)*Math.sin(a) + (p[1]-60)*Math.cos(a))*s));
    const y = floorY - lowest;
    ellipse(b, x, floorY, 19, 3); b.fillStyle = 'rgba(77,52,30,.14)'; b.fill();
    b.save(); b.translate(x,y); b.rotate(a); b.scale(s,s); b.translate(250,-60);
    drawGrub(b); b.restore();
  }
  pebble(b, 334,1296,7,.2,'#BCA179');
  pebble(b, 884,1299,8,-.3,'#B29972');
  b.restore();

  // Broken surface contour and sparse dry blades.
  inkPath(b, path('M -10 513 C 86 493 169 514 264 502 C 388 486 467 516 607 505 C 751 495 883 486 1090 508'), 'rgba(83,63,42,.62)', 2);
  const tufts = [[29,507,34],[156,507,20],[399,500,28],[663,501,19],[1003,501,38]];
  for (let n = 0; n < tufts.length; n++) {
    const [x,y,h] = tufts[n];
    for (let j = 0; j < 5; j++) {
      const lean = (j-2)*7, height = h*(.65 + (j%3)*.15);
      b.beginPath(); b.moveTo(x+(j-2)*2,y);
      b.quadraticCurveTo(x+lean*.5,y-height*.65,x+lean,y-height);
      b.strokeStyle = j === 2 && n === 3 ? P.lime : ['#9B8A5D','#B6A574','#8E805B'][j%3];
      b.lineWidth = 1.25; b.stroke();
    }
  }
  line(b, [[274,500],[294,495],[306,496]], 1.3, '#A69471');
  line(b, [[714,498],[733,489],[747,490]], 1.2, '#A99877');

  // The supplied copy is the only display copy.
  b.textAlign = 'left'; b.textBaseline = 'alphabetic';
  tracked(b, labels.eyebrow, 84, 129, 17.5, 2.65, 850, P.purple);
  if (labels.eyebrow || labels.title) {
    line(b, [[84,157],[116,157]], 3, P.purple);
    line(b, [[124,157],[155,157]], 3, P.lime);
  }
  const title = fitLines(b, labels.title, 858, 91, 'D6Serif');
  b.font = '400 ' + title.size + 'px D6Serif'; b.fillStyle = P.ink;
  const titleY = title.lines.length > 1 ? 237 : 265;
  title.lines.forEach((s, i) => b.fillText(s, 80, titleY + i*title.size*1.02));
  const footer = fitLines(b, labels.footer, 846, 32, 'D6Serif');
  b.font = '400 ' + footer.size + 'px D6Serif'; b.fillStyle = P.cream;
  if (footer.lines.length) line(b, [[84,1606],[120,1606]], 2.5, P.lime);
  footer.lines.forEach((s, i) => b.fillText(s, 84, (footer.lines.length > 1 ? 1648 : 1668) + i*40));
  const note = fitLines(b, labels.illustrationNote.replace(/\s+/g, ' '), 846, 17, 'D6Sans', 1);
  b.font = '400 ' + note.size + 'px D6Sans'; b.fillStyle = P.paper;
  b.save(); b.globalAlpha = .79;
  note.lines.forEach(s => b.fillText(s, 84, 1814)); b.restore();

  // Six legs: three far and three near. Every hip lies on the mesosoma.
  const farLegs = [
    [[-48,8],[-62,26],[-111,68],[-155,143],[-173,156],[-187,157]],
    [[-12,15],[3,40],[72,62],[103,141],[122,157],[139,158]],
    [[32,20],[55,37],[153,66],[199,138],[218,151],[233,153]]
  ];
  const nearLegs = [
    [[-48,19],[-67,39],[-104,72],[-130,156],[-147,176],[-162,179]],
    [[-8,24],[-6,46],[40,80],[11,160],[-7,178],[-24,180]],
    [[34,25],[45,44],[113,87],[152,164],[179,180],[196,180]]
  ];
  function drawLeg(ctx, pts, far) {
    const edge = far ? '#73563D' : '#55331F', color = far ? '#A07D54' : '#A66C40';
    const widths = far ? [6.1,5.6,4.0,2.8,2.0] : [7.2,6.8,4.7,3.1,2.2];
    for (let i = 0; i < pts.length - 1; i++) {
      line(ctx, [pts[i],pts[i+1]], widths[i]+1.9, edge);
      line(ctx, [pts[i],pts[i+1]], widths[i], color);
    }
    for (const i of [1,2,3]) {
      ellipse(ctx, pts[i][0],pts[i][1],far?2.3:2.8,far?2.1:2.4);
      ctx.fillStyle = color; ctx.fill();
    }
    // Fine divisions in the tarsus; small paired claws touch the floor.
    const a = pts[3], z = pts[5];
    for (const u of [.35,.6,.81]) {
      const x = lerp(a[0],z[0],u), y = lerp(a[1],z[1],u);
      line(ctx, [[x-1,y-1.5],[x+1,y+1.3]], .7, edge);
    }
    const foot = pts[5], direction = Math.sign(foot[0] - pts[4][0]) || 1;
    line(ctx, [[foot[0],foot[1]],[foot[0]+direction*5,foot[1]+.5],[foot[0]+direction*6,foot[1]-1.3]], 1.1, edge);
    line(ctx, [[foot[0]-1,foot[1]],[foot[0]+direction*3,foot[1]+2]], .9, edge);
  }
  function antenna(ctx, base, elbow, distal, far, swing) {
    ctx.save(); ctx.translate(base[0],base[1]); ctx.rotate(swing); ctx.translate(-base[0],-base[1]);
    const edge = far ? '#76533B' : '#593420', color = far ? '#B08B61' : '#B07749';
    // One long scape, followed by nine funicular segments = ten total.
    line(ctx, [base,elbow], far?5.3:5.8, edge);
    line(ctx, [base,elbow], far?3.1:3.5, color);
    let last = elbow;
    for (let i = 0; i < distal.length; i++) {
      const next = distal[i], club = i >= 7;
      const w = club ? (i === 8 ? 5.6 : 4.8) : 2.7;
      const a = [lerp(last[0],next[0],.065),lerp(last[1],next[1],.065)];
      const z = [lerp(last[0],next[0],.94),lerp(last[1],next[1],.94)];
      line(ctx, [a,z], w+1.35, edge); line(ctx, [a,z], w, color);
      last = next;
    }
    ctx.restore();
  }
  function drawWorker(ctx, time) {
    const phase = Number.isFinite(time) ? time - 4.5 : 0;
    const feeler = Math.sin(phase*.8)*.018*motion;
    ctx.save(); ctx.translate(HERO.x,HERO.y); ctx.scale(HERO.scale,HERO.scale);
    ctx.lineCap = 'round'; ctx.lineJoin = 'round';
    // Grounding shadow plus individual contacts for the two depth planes.
    const shadow = ctx.createRadialGradient(30,174,2,30,174,282);
    shadow.addColorStop(0,'rgba(77,48,25,.15)'); shadow.addColorStop(1,'rgba(77,48,25,0)');
    ctx.save(); ctx.translate(0,174); ctx.scale(1,.065); ctx.translate(0,-174);
    ctx.fillStyle = shadow; ctx.fillRect(-270,-110,600,570); ctx.restore();
    for (const pts of farLegs.concat(nearLegs)) {
      const p = pts[5]; ellipse(ctx,p[0],p[1]+1,9,2.1);
      ctx.fillStyle = 'rgba(72,46,25,.18)'; ctx.fill();
    }
    for (const leg of farLegs) drawLeg(ctx,leg,true);
    antenna(ctx,[-131,-68],[-144,-142],
      [[-151,-147],[-159,-152],[-167,-156],[-175,-160],[-183,-164],[-191,-167],[-198,-170],[-208,-174],[-220,-174]],true,-feeler);
    // The dark abdomen, narrow connecting stalk and TWO individually outlined nodes.
    line(ctx,[[46,24],[141,30]],8,'#71462C');
    shell(ctx,anatomy.gaster,'#755244','#392A23',[171,-35,229,85],2);
    ctx.save(); ctx.clip(anatomy.gaster);
    for (const [d,w,c] of [
      ['M 177 -28 C 156 7 167 54 193 77',1.1,'rgba(218,175,127,.27)'],
      ['M 233 -34 C 257 1 258 47 238 80',1.05,'rgba(26,19,16,.43)'],
      ['M 265 -18 C 281 14 273 46 262 61',.9,'rgba(214,167,121,.18)'],
      ['M 177 -17 C 193 -28 217 -26 234 -18',2.1,'rgba(217,167,124,.21)']
    ]) inkPath(ctx,path(d),c,w);
    ctx.restore();
    shell(ctx,anatomy.petiole,'#AE6944','#75412A',[71,-9,80,30],1.5);
    shell(ctx,anatomy.postpetiole,'#AC6743','#73402A',[105,6,120,35],1.5);
    shell(ctx,anatomy.neck,'#995633','#6D3B25',[-93,-8,-71,20],1.4);
    shell(ctx,anatomy.thorax,'#B6754C','#864528',[-41,-29,21,35],1.9);
    inkPath(ctx,path('M -24 -21 Q -16 -4 -21 19'), 'rgba(83,44,26,.45)',1.1);
    inkPath(ctx,path('M 20 -10 Q 14 8 24 28'), 'rgba(83,44,26,.36)',1);
    inkPath(ctx,path('M -59 -8 Q -49 -22 -34 -20'), 'rgba(241,191,130,.37)',1.5);
    // Near legs overlay the lower thorax, keeping the three origins readable.
    for (const leg of nearLegs) drawLeg(ctx,leg,false);
    for (const p of [[-48,19],[-8,24],[34,25]]) {
      ellipse(ctx,p[0],p[1],6.2,4.5,.2); ctx.fillStyle = '#965635'; ctx.fill();
      ctx.strokeStyle = '#683B25'; ctx.lineWidth = 1; ctx.stroke();
    }
    shell(ctx,anatomy.farJaw,'#9B6540','#633B24',[-202,0,-178,24],1.1);
    drawGrub(ctx);
    shell(ctx,anatomy.head,'#B56E49','#874429',[-150,-78,-119,29],2);
    // Small matte compound eye: no white, pupil or cartoon highlight.
    ellipse(ctx,-148,-35,6.4,8.1,-.25); ctx.fillStyle = '#402C23'; ctx.fill();
    ellipse(ctx,-149,-36,4.4,5.9,-.25); ctx.fillStyle = '#4C3527'; ctx.fill();
    inkPath(ctx,path('M -170 -17 Q -158 -14 -151 -3'), 'rgba(89,47,29,.42)',1);
    inkPath(ctx,path('M -172 -52 Q -162 -70 -143 -72'), 'rgba(237,178,119,.4)',1.5);
    inkPath(ctx,path('M -127 -67 Q -106 -48 -105 -23'), 'rgba(228,168,111,.2)',1.1);
    // This near mandible overlaps the grub at (-204, 19): there is no gap.
    shell(ctx,anatomy.nearJaw,'#AC754A','#714324',[-199,17,-183,34],1.25);
    inkPath(ctx,path('M -199 28 Q -190 31 -180 24'), 'rgba(225,174,109,.4)',.8);
    antenna(ctx,[-151,-61],[-200,-113],
      [[-209,-116],[-218,-120],[-227,-125],[-235,-131],[-242,-138],[-248,-145],[-253,-152],[-256,-163],[-255,-176]],false,feeler);
    // A few engraved setae, kept subordinate to the silhouette.
    for (const p of [[-126,-78,-127,-83],[-112,-70,-110,-75],[-155,29,-156,34],
      [-52,-25,-54,-30],[0,-10,0,-15],[44,-3,46,-7],[206,-36,207,-41],
      [253,-26,256,-30],[278,49,282,51],[227,84,228,89]]) {
      line(ctx,[[p[0],p[1]],[p[2],p[3]]],.65,'rgba(74,47,31,.65)');
    }
    ctx.restore();
  }

  return {
    draw(ctx, timeSeconds = 4.5) {
      ctx.save();
      ctx.setTransform(1,0,0,1,0,0);
      ctx.globalAlpha = 1; ctx.globalCompositeOperation = 'source-over';
      ctx.shadowColor = 'rgba(0,0,0,0)'; ctx.shadowBlur = 0;
      ctx.shadowOffsetX = 0; ctx.shadowOffsetY = 0; ctx.filter = 'none';
      ctx.setLineDash([]);
      ctx.clearRect(0,0,W,H); ctx.scale(W/REF_W,H/REF_H);
      ctx.drawImage(background,0,0);
      drawWorker(ctx, Number(timeSeconds));
      ctx.restore();
    }
  };
}
