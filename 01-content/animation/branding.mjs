import { createCanvas, Path2D, grainCanvas } from './vendor/claude-animation/core.mjs';

function linesFor(ctx, text, width, size, maxLines = 2) {
  let lines;
  for (; size >= 18; size--) {
    ctx.font = `${size}px D6Serif`;
    lines = [];
    let line = '';
    for (const word of text.trim().split(/\s+/)) {
      const next = line ? `${line} ${word}` : word;
      if (line && ctx.measureText(next).width > width) { lines.push(line); line = word; }
      else line = next;
    }
    if (line) lines.push(line);
    if (lines.length <= maxLines && lines.every(line => ctx.measureText(line).width <= width)) return { lines, size };
  }
  throw new Error('Brand text is too long for this frame.');
}

// A reusable color treatment, independent of the pest drawing.
// The original scene keeps its anatomy, natural colors and time-driven artwork.
export function withBrand(scene, config) {
  const { palette: p, labels } = config;
  const overlay = createCanvas(1080, 1920);
  const c = overlay.getContext('2d');
  c.lineJoin = 'round'; c.lineCap = 'round';
  const header = new Path2D('M 0 0 H 1080 V 337 C 805 324 606 345 389 337 C 230 331 110 346 0 336 Z');
  c.fillStyle = p.purple; c.fill(header);
  c.save(); c.clip(header);
  c.globalCompositeOperation = 'multiply'; c.globalAlpha = .16;
  c.fillStyle = c.createPattern(grainCanvas(256, 45, config.seed), 'repeat');
  c.fillRect(0, 0, 1080, 360); c.restore();
  c.strokeStyle = p.lime; c.lineWidth = 5;
  c.stroke(new Path2D('M 0 336 C 110 346 230 331 389 337 C 606 345 805 324 1080 337'));

  c.font = '24px D6Sans'; c.fillStyle = p.paper;
  c.fillText(labels.eyebrow, 84, 128, 850);
  c.fillStyle = p.lime; c.fillRect(84, 151, 88, 5);
  const title = linesFor(c, labels.title, 858, 91);
  c.font = `${title.size}px D6Serif`;
  c.fillStyle = p.lime; c.strokeStyle = p.ink; c.lineWidth = 2;
  const titleY = title.lines.length > 1 ? 226 : 267;
  title.lines.forEach((line, i) => {
    const y = titleY + i * title.size * 1.02;
    c.strokeText(line, 80, y); c.fillText(line, 80, y);
  });

  const footer = linesFor(c, labels.footer, 790, 36);
  const box = new Path2D('M 82 1588 H 932 Q 950 1588 950 1606 V 1698 Q 950 1716 932 1716 H 82 Q 64 1716 64 1698 V 1606 Q 64 1588 82 1588 Z');
  c.fillStyle = p.purple; c.fill(box);
  c.strokeStyle = p.ink; c.lineWidth = 2; c.stroke(box);
  c.fillStyle = p.lime; c.fillRect(84, 1610, 6, 82);
  c.font = `${footer.size}px D6Serif`; c.fillStyle = p.paper;
  footer.lines.forEach((line, i) => c.fillText(line, 116, (footer.lines.length > 1 ? 1642 : 1664) + i * 40));

  return {
    draw(ctx, time) {
      scene.draw(ctx, time);
      ctx.save(); ctx.setTransform(config.width / 1080, 0, 0, config.height / 1920, 0, 0);
      ctx.globalAlpha = 1; ctx.globalCompositeOperation = 'source-over';
      ctx.drawImage(overlay, 0, 0); ctx.restore();
    },
  };
}
