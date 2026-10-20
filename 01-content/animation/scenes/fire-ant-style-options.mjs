import { createCanvas, Path2D } from '@napi-rs/canvas';

const W = 1080;
const H = 1920;
const DEFAULT_PALETTE = {
  cream: '#F0DDB2',
  paper: '#F6EFE2',
  ink: '#1E1B22',
  purple: '#3A3148',
  lime: '#A9D554',
};
const DEFAULT_LABELS = {
  eyebrow: 'DEEP SIX / FIRE ANT FIELD NOTES',
  title: 'The nursery moves.',
  footer: 'Workers carry their young as nest conditions change.',
  illustrationNote: 'Illustrative cutaway · not to scale',
};

function randomSource(seed) {
  let state = seed >>> 0;
  return () => {
    state += 0x6D2B79F5;
    let value = Math.imul(state ^ (state >>> 15), state | 1);
    value ^= value + Math.imul(value ^ (value >>> 7), value | 61);
    return ((value ^ (value >>> 14)) >>> 0) / 4294967296;
  };
}

function shape(ctx, d, fill, outline = null, width = 1) {
  const path = d instanceof Path2D ? d : new Path2D(d);
  if (fill) {
    ctx.fillStyle = fill;
    ctx.fill(path);
  }
  if (outline) {
    ctx.strokeStyle = outline;
    ctx.lineWidth = width;
    ctx.stroke(path);
  }
  return path;
}

function stroke(ctx, d, color, width) {
  return shape(ctx, d, null, color, width);
}

function polygonPath(points) {
  return `M${points.map(point => point.join(' ')).join(' L')} Z`;
}

function polygon(ctx, points, fill, outline = null, width = 1) {
  return shape(ctx, polygonPath(points), fill, outline, width);
}

function oval(ctx, x, y, rx, ry, fill, outline = null, width = 1, rotation = 0) {
  ctx.beginPath();
  ctx.ellipse(x, y, rx, ry, rotation, 0, Math.PI * 2);
  if (fill) {
    ctx.fillStyle = fill;
    ctx.fill();
  }
  if (outline) {
    ctx.strokeStyle = outline;
    ctx.lineWidth = width;
    ctx.stroke();
  }
}

function roundBox(ctx, x, y, width, height, radius, fill, outline = null, lineWidth = 1) {
  const r = Math.min(radius, width / 2, height / 2);
  return shape(ctx, `M${x + r} ${y} H${x + width - r}
    Q${x + width} ${y} ${x + width} ${y + r} V${y + height - r}
    Q${x + width} ${y + height} ${x + width - r} ${y + height}
    H${x + r} Q${x} ${y + height} ${x} ${y + height - r}
    V${y + r} Q${x} ${y} ${x + r} ${y} Z`, fill, outline, lineWidth);
}

function gradient(ctx, x0, y0, x1, y1, stops) {
  const result = ctx.createLinearGradient(x0, y0, x1, y1);
  for (const [offset, color] of stops) result.addColorStop(offset, color);
  return result;
}

function makeFibres(seed) {
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

function textureInPath(ctx, path, texture, opacity = 1) {
  ctx.save();
  ctx.clip(path);
  ctx.globalAlpha *= opacity;
  ctx.fillStyle = ctx.createPattern(texture, 'repeat');
  ctx.fillRect(-1600, -2200, 4400, 4800);
  ctx.restore();
}

function wrappedLines(ctx, text, width) {
  const lines = [];
  for (const paragraph of String(text).split('\n')) {
    let line = '';
    for (const word of paragraph.split(/\s+/).filter(Boolean)) {
      const candidate = line ? `${line} ${word}` : word;
      if (line && ctx.measureText(candidate).width > width) {
        lines.push(line);
        line = '';
      }
      if (ctx.measureText(word).width > width) {
        for (const character of word) {
          if (line && ctx.measureText(line + character).width > width) {
            lines.push(line);
            line = '';
          }
          line += character;
        }
      } else {
        line = line ? `${line} ${word}` : word;
      }
    }
    lines.push(line);
  }
  return lines;
}

function textBlock(ctx, text, options) {
  const {
    x, y, width, height, size, color, family = 'D6Sans',
    leading = 1.14, maxLines = 3, outline = null, weightStroke = 0,
  } = options;
  ctx.save();
  ctx.textAlign = 'left';
  ctx.textBaseline = 'top';
  ctx.lineJoin = 'round';
  let fittedSize = size;
  let lines;
  do {
    ctx.font = `normal ${fittedSize}px ${family}`;
    lines = wrappedLines(ctx, text, width - weightStroke * 2);
    if (lines.length <= maxLines && lines.length * fittedSize * leading <= height) break;
    fittedSize -= 1;
  } while (fittedSize > 8);
  ctx.fillStyle = color;
  lines.forEach((line, index) => {
    const top = y + index * fittedSize * leading;
    if (weightStroke) {
      ctx.strokeStyle = outline || color;
      ctx.lineWidth = weightStroke;
      ctx.strokeText(line, x, top);
    }
    ctx.fillText(line, x, top);
  });
  ctx.restore();
  return lines.length * fittedSize * leading;
}

function softShadow(ctx, x, y, rx, ry, opacity = 0.35) {
  ctx.save();
  ctx.translate(x, y);
  ctx.scale(rx, ry);
  const fill = ctx.createRadialGradient(0, 0, 0, 0, 0, 1);
  fill.addColorStop(0, `rgba(25,16,20,${opacity})`);
  fill.addColorStop(0.48, `rgba(25,16,20,${opacity * 0.6})`);
  fill.addColorStop(1, 'rgba(25,16,20,0)');
  oval(ctx, 0, 0, 1, 1, fill);
  ctx.restore();
}

// B: broad cel shapes, a rising ledge, and a worker seen from three quarters.
function cartoonHouse(ctx, p) {
  ctx.save();
  ctx.translate(835, 590);
  ctx.rotate(0.045);
  ctx.scale(0.78, 0.78);
  polygon(ctx, [[-75, -43], [66, -43], [76, 78], [-82, 78]], p.paper, p.ink, 7);
  polygon(ctx, [[66, -43], [109, -22], [114, 65], [76, 78]], p.cream, p.ink, 7);
  polygon(ctx, [[-102, -39], [-7, -124], [92, -42]], p.purple, p.ink, 8);
  polygon(ctx, [[-7, -124], [35, -119], [119, -25], [92, -42]], '#685770', p.ink, 6);
  roundBox(ctx, -11, 8, 43, 70, 8, p.lime, p.ink, 6);
  roundBox(ctx, -59, -15, 32, 34, 5, '#92B9A0', p.ink, 5);
  stroke(ctx, 'M-43 -14 V19', p.paper, 4);
  ctx.restore();
}

function cartoonLeg(ctx, points, p, far) {
  const d = `M${points.map(point => point.join(' ')).join(' L')}`;
  stroke(ctx, d, p.ink, far ? 20 : 25);
  stroke(ctx, d, far ? '#8E3E2C' : '#D46538', far ? 11 : 15);
  const knee = points[1];
  oval(ctx, knee[0], knee[1], far ? 8 : 10, far ? 8 : 10, far ? '#9E492D' : '#E77C43');
}

function cartoonAnt(ctx, p) {
  ctx.save();
  ctx.translate(180, 1132);
  ctx.rotate(-0.09);
  ctx.scale(1.04, 1.04);
  ctx.lineCap = 'round';
  ctx.lineJoin = 'round';
  const farLegs = [
    [[271, -25], [220, 54], [156, 142]],
    [[315, -30], [343, 55], [311, 143]],
    [[359, -35], [414, 48], [470, 140]],
  ];
  const nearLegs = [
    [[269, 8], [217, 88], [165, 160]],
    [[315, 10], [345, 91], [307, 160]],
    [[361, -2], [423, 78], [494, 160]],
  ];
  for (const [, , foot] of [...farLegs, ...nearLegs]) {
    oval(ctx, foot[0], foot[1] + 3, 23, 6, 'rgba(67,35,32,0.25)');
  }
  farLegs.forEach(points => cartoonLeg(ctx, points, p, true));
  stroke(ctx, 'M146 5 Q188 0 245 -17', p.ink, 23);
  stroke(ctx, 'M146 5 Q188 0 245 -17', '#AD482C', 13);
  shape(ctx, 'M-10 5 C-10 -45 39 -71 91 -62 C138 -59 165 -32 169 1 C174 43 136 75 81 76 C27 77 -9 49 -10 5 Z',
    '#9C392B', p.ink, 8);
  shape(ctx, 'M0 -9 C13 -44 56 -54 100 -43 C117 -39 130 -31 138 -19 C92 -31 42 -22 16 4 Z', '#CB5835');
  shape(ctx, 'M9 37 C54 59 122 54 157 19 C149 58 115 74 73 70 C42 69 18 57 9 37 Z', '#702B29');
  shape(ctx, 'M239 -46 C269 -78 345 -72 382 -42 C402 -18 379 19 347 24 L268 26 C236 23 219 -11 239 -46 Z',
    '#C6522F', p.ink, 8);
  shape(ctx, 'M247 -42 C277 -62 326 -58 353 -45 L339 -27 C303 -38 274 -33 242 -18 Z', '#EF8B47');
  shape(ctx, 'M247 10 C285 14 344 9 382 -15 C375 14 346 25 270 24 Z', '#963828');
  oval(ctx, 184, -1, 18, 20, '#D56735', p.ink, 7, -0.16);
  oval(ctx, 221, -11, 17, 20, '#E1783D', p.ink, 7, -0.18);
  stroke(ctx, 'M381 -38 L416 -54', p.ink, 30);
  stroke(ctx, 'M381 -38 L416 -54', '#AC432B', 19);
  nearLegs.forEach(points => cartoonLeg(ctx, points, p, false));
  shape(ctx, 'M409 -89 Q460 -121 510 -82 Q544 -41 511 1 Q481 30 432 6 Q388 -20 409 -89 Z',
    '#DA6137', p.ink, 8);
  shape(ctx, 'M414 -80 Q459 -108 496 -78 L483 -57 Q445 -76 409 -48 Z', '#F39751');
  shape(ctx, 'M429 -2 Q482 13 518 -33 Q525 1 486 13 Q454 20 429 -2 Z', '#B4432C');
  stroke(ctx, 'M484 -91 L524 -142 L580 -159', p.ink, 12);
  stroke(ctx, 'M441 -95 L441 -161 L481 -198', p.ink, 12);
  stroke(ctx, 'M484 -91 L524 -142 L580 -159', '#C95733', 6);
  stroke(ctx, 'M441 -95 L441 -161 L481 -198', '#E17A41', 6);
  oval(ctx, 581, -159, 13, 7, '#B7472E', p.ink, 4, -0.3);
  oval(ctx, 482, -199, 12, 7, '#C95D33', p.ink, 4, -0.65);
  oval(ctx, 492, -55, 10, 13, p.ink, null, 1, 0.15);
  oval(ctx, 489, -59, 2.6, 3.4, p.paper);
  const larva = shape(ctx, 'M545 -34 C592 -52 646 -18 653 26 C660 72 624 111 583 108 C550 105 528 82 535 55 C539 36 558 34 572 44 C556 54 557 73 576 80 C600 89 622 68 622 42 C622 16 598 -5 569 -5 C554 2 540 -13 545 -34 Z',
    p.cream, p.ink, 7);
  ctx.save();
  ctx.clip(larva);
  stroke(ctx, 'M549 -24 C601 -35 644 12 636 51 C630 84 605 100 575 96', '#D5B783', 12);
  stroke(ctx, 'M553 -29 Q565 -22 565 -6 M579 -34 Q581 -20 577 -7 M606 -24 Q601 -11 593 -3 M628 -3 Q617 5 610 7 M641 23 L622 28 M638 50 L620 45 M621 76 L608 62 M596 94 L590 79 M569 90 L576 77 M548 70 L562 66',
    '#B89A69', 2.7);
  ctx.restore();
  shape(ctx, 'M512 -29 Q535 -29 551 -15 L545 -3 Q527 -9 514 -11 L505 -19 Z',
    '#983C29', p.ink, 5);
  shape(ctx, 'M516 -7 Q532 7 551 1 L548 12 Q525 21 506 2 Z', '#C4512D', p.ink, 5);
  ctx.restore();
}

function drawCartoon(ctx, p, labels) {
  ctx.fillStyle = p.purple;
  ctx.fillRect(0, 0, W, H);
  shape(ctx, 'M889 -30 Q1028 117 1090 324 L1120 -30 Z', '#4B3E5B');
  shape(ctx, 'M-20 480 Q88 526 92 640 Q25 611 -20 620 Z', '#584663');
  polygon(ctx, [[69, 95], [907, 91], [930, 151], [75, 157]], p.lime);
  textBlock(ctx, labels.eyebrow, { x: 91, y: 111, width: 815, height: 38, size: 25, color: p.purple, maxLines: 1 });
  textBlock(ctx, labels.title, { x: 82, y: 202, width: 900, height: 252, size: 108, color: p.paper, weightStroke: 3.8, maxLines: 2 });
  shape(ctx, 'M-30 691 Q135 581 307 645 Q526 707 744 627 Q946 558 1110 664 L1110 831 L-30 824 Z', '#64855B', p.ink, 8);
  shape(ctx, 'M-30 737 Q169 649 357 719 Q606 782 800 686 Q947 645 1110 710 L1110 891 L-30 887 Z', p.lime, p.ink, 8);
  cartoonHouse(ctx, p);
  stroke(ctx, 'M731 674 Q705 639 711 618 M721 665 L687 647 M957 686 Q971 643 997 629', p.purple, 9);
  shape(ctx, 'M-30 774 Q174 713 379 783 Q629 829 819 735 Q965 699 1110 760 L1110 1570 L-30 1570 Z',
    '#BB7049', p.ink, 9);
  shape(ctx, 'M-30 818 Q166 757 378 827 Q610 877 842 775 Q1006 750 1110 803 L1110 882 Q951 838 815 861 Q561 940 337 871 Q132 817 -30 886 Z', '#E0A66B');
  shape(ctx, 'M-30 1040 C97 877 218 800 358 850 C461 747 690 793 827 843 C1017 849 1108 997 1100 1242 L1100 1450 L-30 1450 Z',
    '#684344', p.ink, 9);
  shape(ctx, 'M33 1074 C150 935 269 882 382 921 C492 826 669 864 802 925 C932 922 1011 1052 1050 1191 L1064 1397 L-20 1435 Z', '#BF8054');
  shape(ctx, 'M1110 887 Q980 886 928 963 L952 1036 Q1030 959 1110 978 Z', '#684344', p.ink, 7);
  stroke(ctx, 'M89 1005 Q200 897 313 910 M482 865 Q612 830 734 889', '#E3AB6B', 18);
  shape(ctx, 'M-20 1301 L1100 1196 L1100 1441 Q602 1506 -20 1473 Z', '#AF5D3D', p.ink, 9);
  shape(ctx, 'M-20 1283 Q415 1261 1100 1184 L1100 1254 Q510 1321 -20 1353 Z', '#E5AE6B', p.ink, 7);
  stroke(ctx, 'M18 1323 Q468 1285 1056 1224', '#F1CD86', 10);
  polygon(ctx, [[85, 1338], [103, 1315], [139, 1321], [152, 1341]], '#8D4F39', p.ink, 5);
  polygon(ctx, [[877, 1264], [903, 1239], [938, 1245], [951, 1271]], '#B9683D', p.ink, 5);
  cartoonAnt(ctx, p);
  stroke(ctx, 'M83 1091 L124 1100 M106 1045 L143 1063 M105 1152 L139 1149', p.cream, 8);
  shape(ctx, 'M-30 1490 Q217 1422 476 1469 Q778 1516 1110 1413 L1110 1950 L-30 1950 Z', p.lime, p.ink, 9);
  textBlock(ctx, labels.footer, { x: 86, y: 1525, width: 900, height: 118, size: 37, color: p.purple, weightStroke: 0.7, maxLines: 2 });
  textBlock(ctx, labels.illustrationNote, { x: 88, y: 1665, width: 900, height: 37, size: 23, color: p.purple, maxLines: 1 });
  shape(ctx, 'M896 1950 Q855 1810 1000 1750 Q984 1855 896 1950 Z', p.purple);
  shape(ctx, 'M904 1950 Q1023 1801 1110 1820 L1110 1950 Z', '#65875A');
  stroke(ctx, 'M884 1950 Q927 1845 997 1780', p.lime, 7);
}

// C: each silhouette is a separate paper piece with its own cast shadow.
function paperCut(ctx, d, color, texture, depth = 7) {
  ctx.save();
  ctx.shadowColor = 'rgba(57,35,27,0.24)';
  ctx.shadowBlur = depth * 0.65;
  ctx.shadowOffsetX = depth * 0.35;
  ctx.shadowOffsetY = depth;
  const path = shape(ctx, d, color);
  ctx.shadowColor = 'transparent';
  textureInPath(ctx, path, texture, 0.95);
  ctx.restore();
  return path;
}

function paperOval(ctx, x, y, rx, ry, color, texture, depth = 4, angle = 0) {
  const path = new Path2D();
  path.ellipse(x, y, rx, ry, angle, 0, Math.PI * 2);
  return paperCut(ctx, path, color, texture, depth);
}

function paperStrip(ctx, points, width, color, texture, depth = 3) {
  for (let i = 1; i < points.length; i += 1) {
    const [ax, ay] = points[i - 1];
    const [bx, by] = points[i];
    const length = Math.hypot(bx - ax, by - ay);
    const nx = -(by - ay) / length * width / 2;
    const ny = (bx - ax) / length * width / 2;
    paperCut(ctx, polygonPath([
      [ax + nx, ay + ny], [(ax + bx) / 2 + nx * 0.9, (ay + by) / 2 + ny],
      [bx + nx * 0.8, by + ny * 0.8], [bx - nx * 0.85, by - ny * 0.85],
      [(ax + bx) / 2 - nx * 1.05, (ay + by) / 2 - ny], [ax - nx, ay - ny],
    ]), color, texture, depth);
  }
  for (const [x, y] of points.slice(1, -1)) paperOval(ctx, x, y, width * 0.57, width * 0.52, color, texture, 2);
}

function paperHouse(ctx, p, texture) {
  ctx.save();
  ctx.translate(842, 630);
  ctx.rotate(-0.105);
  ctx.scale(0.85, 0.85);
  paperCut(ctx, 'M-73 -66 L55 -72 L62 35 L-78 39 L-75 -12 Z', p.paper, texture, 8);
  paperCut(ctx, 'M55 -72 L92 -51 L96 21 L62 35 Z', p.cream, texture, 5);
  paperCut(ctx, 'M-98 -61 L-15 -143 L10 -125 L82 -64 L61 -50 L-15 -111 L-77 -48 Z', p.purple, texture, 7);
  paperCut(ctx, 'M10 -125 L42 -125 L109 -50 L82 -64 Z', '#796882', texture, 4);
  paperCut(ctx, 'M2 -23 L34 -24 L37 36 L0 36 Z', p.lime, texture, 3);
  paperCut(ctx, 'M-57 -34 L-28 -36 L-26 -7 L-57 -6 Z', p.purple, texture, 2);
  ctx.restore();
}

function paperAnt(ctx, p, texture) {
  ctx.save();
  ctx.translate(570, 1110);
  ctx.rotate(-0.16);
  ctx.scale(1.04, 1.04);
  const farLegs = [
    [[-104, -30], [-137, 45], [-178, 140]],
    [[-49, -28], [-24, 56], [-61, 140]],
    [[8, -22], [103, 48], [150, 139]],
  ];
  const nearLegs = [
    [[-105, -3], [-156, 83], [-178, 164]],
    [[-49, 1], [-47, 84], [-75, 163]],
    [[12, -3], [104, 76], [146, 160]],
  ];
  for (const [, , foot] of [...farLegs, ...nearLegs]) {
    oval(ctx, foot[0] + 2, foot[1] + 4, 18, 5, 'rgba(77,49,30,0.16)');
  }
  farLegs.forEach(points => paperStrip(ctx, points, 13, '#743E32', texture, 3));
  paperStrip(ctx, [[25, -12], [112, 2], [148, 8]], 13, '#834635', texture, 2);
  paperCut(ctx, 'M130 -32 L154 -51 Q209 -76 259 -46 L284 -23 Q306 13 285 49 L267 67 Q213 93 164 61 L140 42 Q119 12 130 -32 Z',
    '#793B2D', texture, 9);
  paperCut(ctx, 'M148 -32 Q194 -58 242 -35 L263 -18 Q205 -32 162 -4 L140 14 Z', '#AA5639', texture, 3);
  paperCut(ctx, 'M-137 -45 L-117 -69 Q-68 -88 -16 -62 L17 -48 Q46 -27 29 4 L7 20 L-83 16 Q-126 13 -137 -13 Z',
    '#A94F32', texture, 7);
  paperCut(ctx, 'M-127 -47 L-107 -60 Q-64 -70 -23 -51 L-40 -34 L-103 -24 L-130 -26 Z', '#CB7646', texture, 3);
  paperOval(ctx, 61, -10, 17, 21, '#C17142', texture, 6, -0.2);
  paperOval(ctx, 100, 0, 16, 20, '#B25D38', texture, 6, -0.25);
  paperStrip(ctx, [[-128, -35], [-166, -42]], 24, '#89412F', texture, 3);
  nearLegs.forEach(points => paperStrip(ctx, points, 18, '#AE5735', texture, 5));
  paperCut(ctx, 'M-268 -65 L-249 -88 Q-213 -111 -178 -89 L-153 -66 Q-130 -30 -155 2 L-178 22 Q-218 36 -249 7 L-272 -20 Z',
    '#BE603A', texture, 8);
  paperCut(ctx, 'M-255 -63 L-238 -80 Q-207 -96 -182 -77 L-172 -62 Q-219 -68 -254 -41 Z', '#DC915A', texture, 3);
  paperStrip(ctx, [[-235, -76], [-278, -122], [-329, -117]], 7, '#7D3D2E', texture, 2);
  paperStrip(ctx, [[-194, -88], [-214, -150], [-272, -176]], 7, '#9E4C32', texture, 2);
  paperOval(ctx, -330, -117, 11, 5, '#7D3D2E', texture, 2, -0.1);
  paperOval(ctx, -273, -176, 11, 5, '#9E4C32', texture, 2, 0.43);
  paperOval(ctx, -243, -40, 6.7, 8.7, p.ink, texture, 1, -0.15);
  const larva = paperCut(ctx, 'M-296 -16 L-311 -17 Q-350 -5 -355 34 L-355 52 Q-352 91 -318 109 L-297 115 Q-268 114 -255 92 L-255 75 Q-262 63 -275 69 Q-282 91 -301 84 L-315 73 Q-332 51 -320 29 L-310 21 Q-289 20 -284 4 Z',
    p.cream, texture, 8);
  ctx.save();
  ctx.clip(larva);
  paperCut(ctx, 'M-345 17 Q-355 66 -321 93 Q-290 118 -263 88 L-256 109 L-310 126 L-362 77 L-361 25 Z', '#D4BA8D', texture, 2);
  stroke(ctx, 'M-322 -8 Q-319 5 -310 21 M-340 7 Q-331 16 -320 26 M-352 28 L-326 37 M-353 50 L-326 52 M-344 73 L-320 65 M-327 93 L-312 80 M-303 106 L-299 85 M-280 101 L-286 84',
    '#B59A73', 2.3);
  ctx.restore();
  paperCut(ctx, 'M-265 -14 L-285 -13 L-299 1 L-290 9 L-278 0 L-262 2 Z', '#85432F', texture, 3);
  paperCut(ctx, 'M-258 0 L-277 13 L-292 15 L-291 25 L-272 22 L-252 11 Z', '#9C4B30', texture, 3);
  ctx.restore();
}

function drawPaper(ctx, p, labels, texture) {
  ctx.fillStyle = p.paper;
  ctx.fillRect(0, 0, W, H);
  textureInPath(ctx, new Path2D(`M0 0 H${W} V${H} H0 Z`), texture, 0.8);
  textBlock(ctx, labels.eyebrow, { x: 90, y: 112, width: 900, height: 40, size: 24, color: p.purple, maxLines: 1 });
  ctx.save();
  ctx.translate(72, 190);
  ctx.rotate(-0.025);
  paperCut(ctx, 'M0 5 L278 0 L566 5 L907 0 L917 49 L899 99 L922 151 L909 240 L599 236 L304 243 L-5 234 L4 175 L-7 91 Z', p.purple, texture, 11);
  textBlock(ctx, labels.title, { x: 41, y: 26, width: 690, height: 219, size: 107, color: p.paper, family: 'D6Serif', leading: 0.98, maxLines: 2 });
  ctx.restore();
  paperCut(ctx, 'M955 454 L982 423 L973 394 L939 397 L925 429 L915 405 L887 402 L881 428 L907 458 L883 451 L860 465 L871 489 L914 486 L927 522 L943 516 Z', p.lime, texture, 6);
  paperStrip(ctx, [[929, 522], [921, 464], [954, 418]], 6, '#76904A', texture, 2);
  paperCut(ctx, 'M-35 865 L129 789 L297 767 L459 704 L639 679 L811 611 L1089 581 L1119 1507 L875 1510 L657 1454 L433 1484 L197 1437 L-33 1472 Z',
    '#744C43', texture, 15);
  paperCut(ctx, 'M-26 858 L147 795 L305 788 L474 727 L648 704 L820 643 L1100 614 L1102 1438 L861 1421 L653 1401 L432 1439 L189 1378 L-28 1419 Z',
    '#B57553', texture, 10);
  paperCut(ctx, 'M-20 905 L143 846 L319 840 L488 779 L663 758 L831 695 L1099 670 L1100 753 L847 760 L690 825 L507 843 L337 905 L144 908 L-20 966 Z',
    '#D5A273', texture, 7);
  paperCut(ctx, 'M-25 832 L137 769 L303 749 L467 687 L648 663 L813 594 L1100 566 L1100 618 L826 639 L660 707 L477 732 L314 793 L145 813 L-25 880 Z',
    '#789251', texture, 7);
  paperCut(ctx, 'M-25 817 L141 756 L304 735 L473 674 L646 650 L814 581 L1100 554 L1099 586 L821 615 L656 680 L478 705 L311 769 L144 787 L-25 851 Z',
    p.lime, texture, 6);
  paperHouse(ctx, p, texture);
  paperStrip(ctx, [[238, 807], [251, 884], [224, 943], [251, 997]], 15, p.cream, texture, 3);
  paperStrip(ctx, [[251, 885], [298, 913], [317, 960]], 8, p.cream, texture, 2);
  paperStrip(ctx, [[723, 711], [705, 797], [747, 850]], 13, '#DFC08D', texture, 3);
  paperStrip(ctx, [[705, 797], [657, 826], [649, 870]], 7, '#DFC08D', texture, 2);
  paperCut(ctx, 'M-30 1195 Q76 1161 123 1077 Q188 960 350 964 Q531 858 723 894 Q904 876 995 1030 L1017 1235 Q1011 1326 851 1350 L276 1443 Q125 1453 65 1374 L-30 1372 Z',
    '#5B4141', texture, 12);
  paperCut(ctx, 'M-25 1223 Q91 1181 151 1098 Q223 998 363 1002 Q549 898 725 933 Q885 913 956 1051 L984 1204 Q982 1291 836 1317 L285 1404 Q145 1427 94 1340 L-25 1344 Z',
    '#E0C09A', texture, 9);
  paperCut(ctx, 'M-15 1349 Q151 1384 329 1300 Q624 1162 981 1171 L1002 1248 Q686 1250 376 1385 L204 1434 L-15 1431 Z',
    '#C29A70', texture, 6);
  paperCut(ctx, 'M-15 1398 Q177 1425 368 1341 Q690 1205 1007 1214 L1007 1277 Q711 1282 395 1419 Q200 1500 -15 1450 Z',
    '#9B674C', texture, 7);
  paperAnt(ctx, p, texture);
  paperCut(ctx, 'M86 840 L72 787 L41 760 L25 773 L48 805 L59 858 Z', p.purple, texture, 5);
  paperCut(ctx, 'M78 829 L107 782 L143 768 L150 785 L116 810 L92 850 Z', p.purple, texture, 5);
  paperCut(ctx, 'M925 1378 L954 1321 L983 1308 L992 1326 L965 1356 L947 1391 Z', p.lime, texture, 5);
  paperCut(ctx, 'M73 1505 L294 1499 L513 1511 L749 1498 L1000 1507 L993 1624 L769 1633 L533 1624 L291 1636 L79 1626 Z', p.lime, texture, 7);
  textBlock(ctx, labels.footer, { x: 102, y: 1522, width: 862, height: 108, size: 42, color: p.purple, family: 'D6Serif', leading: 1.08, maxLines: 2 });
  textBlock(ctx, labels.illustrationNote, { x: 103, y: 1666, width: 875, height: 36, size: 22, color: p.ink, maxLines: 1 });
  paperCut(ctx, 'M-35 1835 L189 1776 L400 1801 L639 1762 L866 1800 L1110 1749 L1110 1950 L-35 1950 Z', p.cream, texture, 5);
}

// D: a physical cutaway block, matte rounded forms, and one warm key light.
function clayForm(ctx, d, bounds, colors, texture = null, depth = 8) {
  const [x, y, width, height] = bounds;
  const fill = gradient(ctx, x, y, x + width * 0.7, y + height, [
    [0, colors[0]], [0.32, colors[1]], [0.72, colors[2]], [1, colors[3]],
  ]);
  ctx.save();
  ctx.shadowColor = 'rgba(37,18,20,0.32)';
  ctx.shadowBlur = depth;
  ctx.shadowOffsetX = depth * 0.25;
  ctx.shadowOffsetY = depth * 0.6;
  const path = shape(ctx, d, fill);
  ctx.shadowColor = 'transparent';
  if (texture) textureInPath(ctx, path, texture, 0.17);
  ctx.restore();
  return path;
}

function clayOval(ctx, x, y, rx, ry, colors, texture, angle = 0, depth = 7) {
  const path = new Path2D();
  path.ellipse(x, y, rx, ry, angle, 0, Math.PI * 2);
  return clayForm(ctx, path, [x - rx, y - ry, rx * 2, ry * 2], colors, texture, depth);
}

function clayLeg(ctx, points, p, far) {
  const d = `M${points.map(point => point.join(' ')).join(' L')}`;
  const [start, knee, foot] = points;
  ctx.save();
  ctx.lineJoin = 'round';
  ctx.lineCap = 'round';
  ctx.shadowColor = 'rgba(30,18,18,0.32)';
  ctx.shadowBlur = 5;
  ctx.shadowOffsetY = 5;
  stroke(ctx, d, far ? '#69362B' : '#7B3727', far ? 13 : 19);
  ctx.shadowColor = 'transparent';
  const fill = gradient(ctx, start[0] - 8, start[1], foot[0] + 12, foot[1], [
    [0, far ? '#9F5940' : '#C77A4B'],
    [0.45, far ? '#824330' : '#AD5835'],
    [1, '#663125'],
  ]);
  stroke(ctx, d, fill, far ? 10 : 15);
  oval(ctx, knee[0] - 1, knee[1] - 1, far ? 5 : 7, far ? 5 : 7, far ? '#935036' : '#BC6941');
  stroke(ctx, `M${foot[0]} ${foot[1]} l${far ? -8 : 9} 1`, p.ink, far ? 4 : 5);
  ctx.restore();
}

function clayAnt(ctx, p, texture) {
  ctx.save();
  ctx.translate(212, 1120);
  ctx.rotate(-0.055);
  ctx.scale(1.02, 1.02);
  ctx.lineCap = 'round';
  ctx.lineJoin = 'round';
  const farLegs = [
    [[275, -68], [208, -7], [171, 80]],
    [[308, -73], [327, -1], [299, 79]],
    [[349, -73], [412, -14], [476, 77]],
  ];
  const nearLegs = [
    [[270, -45], [225, 48], [167, 128]],
    [[310, -43], [339, 49], [307, 129]],
    [[350, -56], [419, 36], [493, 124]],
  ];
  softShadow(ctx, 281, 102, 266, 44, 0.36);
  softShadow(ctx, 90, 78, 102, 26, 0.25);
  for (const [, , foot] of [...farLegs, ...nearLegs]) softShadow(ctx, foot[0], foot[1] + 3, 20, 7, 0.43);
  farLegs.forEach(points => clayLeg(ctx, points, p, true));
  stroke(ctx, 'M157 -24 L258 -55', '#603023', 16);
  stroke(ctx, 'M158 -28 L258 -59', '#AB5B35', 9);
  clayOval(ctx, 80, -22, 94, 66, ['#A76A49', '#81432F', '#5F3028', '#42252A'], texture, 0.17, 12);
  clayForm(ctx, 'M251 -86 C270 -115 331 -115 361 -92 C385 -75 367 -41 343 -32 C305 -18 271 -26 251 -44 Q239 -65 251 -86 Z',
    [245, -112, 133, 90], ['#CF8A56', '#AE603A', '#8A402C', '#673026'], texture, 9);
  clayOval(ctx, 193, -37, 17, 19, ['#D18A51', '#B2693C', '#8F462C', '#663022'], texture, -0.2, 5);
  clayOval(ctx, 231, -49, 17, 19, ['#D79258', '#B46A3E', '#90462C', '#673124'], texture, -0.2, 5);
  stroke(ctx, 'M358 -73 L393 -88', '#743624', 25);
  stroke(ctx, 'M359 -78 L394 -93', '#B4653A', 14);
  nearLegs.forEach(points => clayLeg(ctx, points, p, false));
  clayForm(ctx, 'M383 -124 C407 -154 456 -163 484 -139 C513 -119 521 -83 501 -53 C483 -23 441 -19 410 -39 C381 -56 366 -96 383 -124 Z',
    [374, -153, 141, 132], ['#E09B61', '#BD7144', '#98492F', '#6B3226'], texture, 10);
  stroke(ctx, 'M471 -126 L506 -178 L559 -192', '#723B2A', 9);
  stroke(ctx, 'M416 -139 L426 -192 L466 -222', '#8D482E', 9);
  stroke(ctx, 'M470 -128 L504 -180 L558 -194', '#C17B4C', 3.5);
  stroke(ctx, 'M415 -141 L424 -194 L465 -224', '#D08A55', 3.5);
  clayOval(ctx, 561, -193, 11, 6, ['#C17D4C', '#A25C38', '#7D3D2A', '#592C25'], texture, -0.3, 3);
  clayOval(ctx, 468, -224, 11, 6, ['#CF8B55', '#AE673E', '#87432B', '#633023'], texture, -0.55, 3);
  clayOval(ctx, 478, -93, 7, 10, ['#514039', '#302725', p.ink, p.ink], null, 0.2, 2);
  const larva = clayForm(ctx, 'M531 -49 C563 -63 600 -43 617 -16 C642 25 615 66 580 76 C550 84 518 62 515 36 C512 16 527 3 543 10 C529 22 536 42 555 46 C578 54 597 34 593 13 C588 -9 565 -20 543 -12 C529 -9 521 -32 531 -49 Z',
    [515, -58, 116, 139], [p.paper, p.cream, '#D5BD96', '#AC8C68'], texture, 8);
  ctx.save();
  ctx.clip(larva);
  stroke(ctx, 'M550 -51 Q553 -32 545 -14 M573 -48 Q570 -29 564 -18 M595 -35 Q581 -23 579 -13 M612 -15 Q596 -9 590 -3 M622 8 Q605 10 596 12 M617 34 Q602 29 590 28 M601 56 Q587 42 580 39 M578 71 Q573 55 568 47 M553 70 Q556 55 554 46 M531 53 Q544 46 542 37',
    'rgba(143,112,77,0.42)', 2.7);
  stroke(ctx, 'M539 -43 Q571 -52 595 -28', 'rgba(255,250,229,0.36)', 5);
  ctx.restore();
  clayForm(ctx, 'M494 -70 Q516 -66 540 -41 L538 -29 Q520 -39 501 -45 L490 -53 Z',
    [490, -70, 51, 44], ['#D18A53', '#AE6238', '#8A4028', '#633020'], texture, 4);
  clayForm(ctx, 'M493 -49 Q511 -28 539 -23 L540 -11 Q509 -10 488 -32 Z',
    [488, -49, 53, 39], ['#C87B47', '#A65731', '#7F3926', '#5D2B21'], texture, 4);
  ctx.restore();
}

function clayHouse(ctx, p, texture) {
  ctx.save();
  ctx.translate(777, 647);
  ctx.scale(0.85, 0.85);
  softShadow(ctx, 0, 65, 110, 30, 0.35);
  clayForm(ctx, 'M-73 -51 L38 -43 L38 78 L-74 59 Q-81 57 -81 45 V-42 Q-81 -52 -73 -51 Z',
    [-81, -52, 120, 130], [p.paper, p.cream, '#D6B992', '#AC8967'], texture, 8);
  clayForm(ctx, 'M38 -43 L93 -74 L95 42 Q95 49 87 54 L38 78 Z',
    [38, -74, 57, 152], ['#D5C39F', '#BAA17E', '#9C7C61', '#85634F'], texture, 5);
  clayForm(ctx, 'M-103 -48 Q-108 -54 -99 -62 L-28 -132 Q-22 -138 -14 -130 L60 -48 Q64 -41 54 -33 Z',
    [-106, -136, 169, 106], ['#80708A', '#62516E', p.purple, '#2B2336'], texture, 6);
  clayForm(ctx, 'M-22 -135 L30 -158 Q36 -160 42 -153 L115 -81 Q122 -73 113 -68 L57 -34 Z',
    [-22, -158, 145, 124], ['#968399', '#76657D', '#54445E', p.purple], texture, 4);
  roundBox(ctx, -12, 8, 29, 61, 5, '#628041');
  roundBox(ctx, -10, 10, 24, 57, 4, p.lime);
  roundBox(ctx, -62, -22, 29, 31, 5, '#695A58');
  roundBox(ctx, -59, -19, 23, 24, 4, '#B5CFBF');
  ctx.restore();
}

function drawMiniature(ctx, p, labels, texture) {
  ctx.fillStyle = gradient(ctx, 0, 0, 860, H, [[0, '#514357'], [0.48, p.purple], [1, '#27232F']]);
  ctx.fillRect(0, 0, W, H);
  const glow = ctx.createRadialGradient(245, 730, 20, 245, 730, 990);
  glow.addColorStop(0, 'rgba(238,194,134,0.18)');
  glow.addColorStop(0.6, 'rgba(219,170,115,0.05)');
  glow.addColorStop(1, 'rgba(219,170,115,0)');
  ctx.fillStyle = glow;
  ctx.fillRect(0, 0, W, H);
  textBlock(ctx, labels.eyebrow, { x: 85, y: 112, width: 910, height: 39, size: 24, color: p.paper, maxLines: 1 });
  textBlock(ctx, labels.title, { x: 81, y: 199, width: 900, height: 243, size: 104, color: p.lime, weightStroke: 1.8, maxLines: 2 });
  softShadow(ctx, 558, 1468, 459, 89, 0.55);
  softShadow(ctx, 561, 1454, 361, 35, 0.6);
  clayForm(ctx, 'M849 811 Q917 775 1003 730 L1011 1238 Q1015 1301 968 1336 L850 1431 L825 1069 Z',
    [825, 730, 190, 710], ['#AF7756', '#905D46', '#6B4339', '#503333'], texture, 17);
  clayForm(ctx, 'M137 780 Q172 757 225 772 L840 791 Q882 799 891 844 L893 1373 Q892 1430 841 1450 L192 1463 Q115 1459 104 1394 L94 867 Q94 805 137 780 Z',
    [94, 772, 801, 693], ['#DAA575', '#BD855C', '#986345', '#744737'], texture, 15);
  clayForm(ctx, 'M128 785 Q158 737 206 712 L743 602 Q780 595 815 616 L991 700 Q1024 717 997 742 L879 818 Q853 836 820 829 L174 812 Q137 811 128 785 Z',
    [128, 602, 886, 234], ['#D7B07D', '#B98958', '#986B46', '#785138'], texture, 10);
  clayForm(ctx, 'M141 774 Q169 738 212 720 L744 611 Q775 603 809 623 L984 705 Q1003 716 984 731 L870 801 Q850 814 817 807 L178 794 Q151 792 141 774 Z',
    [141, 611, 858, 205], ['#CCDE84', p.lime, '#85A749', '#627D3A'], texture, 7);
  clayHouse(ctx, p, texture);
  clayForm(ctx, 'M146 1036 C151 936 286 860 443 896 C580 848 771 887 832 989 Q871 1040 869 1148 L867 1281 Q862 1355 779 1380 L252 1403 Q155 1393 140 1317 Z',
    [140, 876, 733, 529], ['#D8A16E', '#B77B50', '#8C583C', '#6A4031'], texture, 5);
  const chamber = shape(ctx, 'M181 1040 C189 955 298 903 448 938 C589 893 738 925 797 1013 Q836 1062 831 1152 L832 1266 Q824 1327 763 1343 L267 1366 Q186 1359 176 1295 Z',
    gradient(ctx, 230, 923, 746, 1364, [[0, '#543A32'], [0.35, '#6A4837'], [0.7, '#956746'], [1, '#BA8A5C']]));
  ctx.save();
  ctx.clip(chamber);
  stroke(ctx, 'M168 1064 C177 947 301 889 448 925 C589 879 757 916 812 1010', 'rgba(36,24,25,0.32)', 29);
  shape(ctx, 'M155 1191 Q444 1159 852 1135 L875 1397 L156 1402 Z',
    gradient(ctx, 400, 1150, 520, 1385, [[0, '#C49866'], [0.48, '#B38556'], [1, '#8B5C3E']]));
  softShadow(ctx, 464, 1197, 298, 64, 0.24);
  textureInPath(ctx, chamber, texture, 0.16);
  ctx.restore();
  stroke(ctx, 'M153 1057 C158 940 290 869 443 905 C582 859 770 895 824 999',
    gradient(ctx, 150, 891, 824, 1070, [[0, '#E3B786'], [0.45, '#D29B68'], [1, '#A26B46']]), 23);
  clayOval(ctx, 955, 1068, 28, 65, ['#5D3E34', '#44302D', '#35272A', '#30252A'], texture, 0.06, 3);
  stroke(ctx, 'M943 1006 Q913 1065 939 1125', '#B07B54', 9);
  clayAnt(ctx, p, texture);
  clayForm(ctx, 'M177 1350 Q423 1323 763 1318 Q814 1316 849 1288 L851 1347 Q814 1387 764 1395 L259 1421 Q201 1417 178 1382 Z',
    [177, 1288, 675, 134], ['#D7A773', '#C19060', '#A6744B', '#865336'], texture, 7);
  clayForm(ctx, 'M241 1305 Q250 1292 269 1299 L282 1311 Q280 1320 263 1322 L245 1318 Z',
    [241, 1295, 42, 28], ['#D9B17C', '#BD9160', '#9B6C44', '#805034'], texture, 4);
  clayForm(ctx, 'M775 1237 Q787 1224 801 1234 L815 1246 Q814 1254 800 1255 L780 1250 Z',
    [775, 1225, 41, 31], ['#CFA371', '#B58959', '#91603D', '#744B32'], texture, 4);
  textBlock(ctx, labels.footer, { x: 86, y: 1531, width: 900, height: 115, size: 36, color: p.paper, leading: 1.2, maxLines: 2 });
  textBlock(ctx, labels.illustrationNote, { x: 87, y: 1666, width: 900, height: 36, size: 22, color: p.cream, maxLines: 1 });
  stroke(ctx, 'M89 1744 H246', p.lime, 5);
}

export function createScene(config = {}) {
  const width = config.width ?? W;
  const height = config.height ?? H;
  const style = config.style ?? 'cartoon';
  if (!Number.isFinite(width) || !Number.isFinite(height) || width <= 0 || height <= 0) {
    throw new RangeError('Scene dimensions must be positive finite numbers.');
  }
  if (!['cartoon', 'paper', 'miniature'].includes(style)) {
    throw new RangeError(`Unknown scene style: ${style}`);
  }
  const palette = { ...DEFAULT_PALETTE, ...config.palette };
  const labels = { ...DEFAULT_LABELS, ...config.labels };
  const frame = createCanvas(W, H);
  const ctx = frame.getContext('2d');
  ctx.lineCap = 'round';
  ctx.lineJoin = 'round';
  if (style === 'cartoon') {
    drawCartoon(ctx, palette, labels);
  } else {
    const texture = makeFibres((config.seed ?? 1) | 0);
    if (style === 'paper') drawPaper(ctx, palette, labels, texture);
    else drawMiniature(ctx, palette, labels, texture);
  }
  return {
    draw(target, timeSeconds = 0) {
      target.save();
      try {
        target.setTransform(1, 0, 0, 1, 0, 0);
        target.globalAlpha = 1;
        target.globalCompositeOperation = 'source-over';
        target.filter = 'none';
        target.shadowColor = 'transparent';
        target.shadowBlur = 0;
        target.shadowOffsetX = 0;
        target.shadowOffsetY = 0;
        target.imageSmoothingEnabled = true;
        target.imageSmoothingQuality = 'high';
        target.clearRect(0, 0, width, height);
        target.drawImage(frame, 0, 0, width, height);
      } finally {
        target.restore();
      }
    },
  };
}
