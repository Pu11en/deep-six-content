#!/usr/bin/env python3
"""Build Deep Six's one animation canvas, then check its layout.

    python3 01-content/diagrams/animation-system.build.py

Writes animation-system.excalidraw (atomic replace) and animation-system.checks.json. Pictures come from
animation-system-images/ (frames taken from the approved and test videos with ffmpeg).
Change wording or layout here and re-run; do not hand-edit the drawing, or this file goes stale.
Checks replace screenshots (Drew's rule): unique IDs, two-way bindings, text inside its box, no overlapping
shapes, pictures or text, arrows that miss everything they do not connect, arrow ends on their shapes.
"""
import base64
import hashlib
import json
import math
import os
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
OUT = HERE / 'animation-system.excalidraw'
CHECKS = HERE / 'animation-system.checks.json'
IMG = HERE / 'animation-system-images'

CW, LH, FONT = 0.6, 1.25, 3   # Cascadia (font 3) advance is 0.586 em; 0.6 leaves a margin
EDGE = 3                       # arrow ends sit this far outside their shapes

# Colors: excalidraw-diagram skill, references/color-palette.md. Swatches show the real Deep Six colours.
FILL = {
    'code': ('#93c5fd', '#1e3a5f'), 'branch': ('#93c5fd', '#1e3a5f'), 'ai': ('#ddd6fe', '#6d28d9'),
    'drew': ('#fef3c7', '#b45309'), 'input': ('#fed7aa', '#c2410c'), 'done': ('#a7f3d0', '#047857'),
    'pause': ('#fee2e2', '#dc2626'), 'later': ('#dbeafe', '#1e40af'), 'evidence': ('#1e293b', '#1e293b'),
    'error': ('#fecaca', '#b91c1c'), 'zone': ('transparent', '#64748b'), 'aizone': ('transparent', '#6d28d9'),
    'drewzone': ('transparent', '#b45309'), 'warnzone': ('transparent', '#dc2626'), 'donezone': ('transparent', '#047857'),
    'sw_purple': ('#3A3148', '#1e293b'), 'sw_lime': ('#A9D554', '#1e293b'), 'sw_cream': ('#F0DDB2', '#1e293b'),
    'sw_paper': ('#F6EFE2', '#1e293b'), 'sw_ink': ('#1E1B22', '#1e293b'),
}
TITLE, SUB, BODY, ONLIGHT, ONDARK, GREEN, RED, SLATE, PURPLE = (
    '#1e40af', '#3b82f6', '#64748b', '#374151', '#ffffff', '#22c55e', '#dc2626', '#64748b', '#6d28d9')

ELS, BY, FILES = [], {}, {}


def seed(s):
    return int(hashlib.sha1(s.encode()).hexdigest()[:7], 16)


def add(el):
    if el['id'] in BY:
        sys.exit('duplicate id ' + el['id'])
    ELS.append(el)
    BY[el['id']] = el
    return el


def base(id, typ, x, y, w, h, stroke, bg='transparent', sw=2, ss='solid', group=None):
    return {'id': id, 'type': typ, 'x': round(x, 2), 'y': round(y, 2), 'width': round(w, 2), 'height': round(h, 2),
            'angle': 0, 'strokeColor': stroke, 'backgroundColor': bg, 'fillStyle': 'solid', 'strokeWidth': sw,
            'strokeStyle': ss, 'roughness': 0, 'opacity': 100, 'groupIds': [group] if group else [], 'frameId': None,
            'roundness': None, 'seed': seed(id), 'version': 1, 'versionNonce': seed(id + '#'), 'isDeleted': False,
            'boundElements': None, 'updated': 1, 'link': None, 'locked': False}


def measure(s, size):
    lines = s.split('\n')
    return max(len(l) for l in lines) * size * CW, len(lines) * size * LH


def text(id, x, y, s, size=16, color=BODY, align='left', group=None, container=None, inside=None):
    """Free text: x is the left edge, the center (align='center') or the right edge (align='right')."""
    w, h = measure(s, size)
    if container is None and align == 'center':
        x -= w / 2
    if container is None and align == 'right':
        x -= w
    el = base(id, 'text', x, y, w, h, color, group=group)
    el.update({'text': s, 'originalText': s, 'fontSize': size, 'fontFamily': FONT, 'textAlign': align,
               'verticalAlign': 'middle' if container else 'top', 'containerId': container, 'lineHeight': LH,
               'autoResize': True})
    if inside:
        el['customData'] = {'inside': inside}
    return add(el)


def shape(id, typ, x, y, w, h, kind, sw=2, ss='solid', group=None):
    fill, stroke = FILL[kind]
    el = base(id, typ, x, y, w, h, stroke, fill, sw, ss, group)
    if typ == 'rectangle':
        el['roundness'] = {'type': 3}
    el['customData'] = {'kind': kind}
    return add(el)


def image(id, name, x, y, w, h):
    data = (IMG / name).read_bytes()
    fid = hashlib.sha1(data).hexdigest()
    FILES[fid] = {'mimeType': 'image/jpeg', 'id': fid, 'created': 1760918400000, 'lastRetrieved': 1760918400000,
                  'dataURL': 'data:image/jpeg;base64,' + base64.b64encode(data).decode()}
    el = base(id, 'image', x, y, w, h, 'transparent', 'transparent', 1)
    el.update({'status': 'saved', 'fileId': fid, 'scale': [1, 1], 'crop': None, 'customData': {'kind': 'image'}})
    return add(el)


def bound(el, s, size, color):
    w, h = measure(s, size)
    cx, cy = el['x'] + el['width'] / 2, el['y'] + el['height'] / 2
    t = text(el['id'] + '_text', cx - w / 2, cy - h / 2, s, size, color, 'center', container=el['id'])
    el['boundElements'] = (el['boundElements'] or []) + [{'id': t['id'], 'type': 'text'}]
    return t


def box(id, x, y, w, h, kind, label, size=16, sw=2, ss='solid'):
    el = shape(id, 'rectangle', x, y, w, h, kind, sw, ss)
    bound(el, label, size, FILL[kind][1])
    return el


def diamond(id, cx, cy, w, h, kind, label, size=18, sw=2):
    el = shape(id, 'diamond', cx - w / 2, cy - h / 2, w, h, kind, sw)
    bound(el, label, size, FILL[kind][1])
    return el


def ellipse(id, cx, cy, w, h, kind, label, size=20, sw=2, ss='solid'):
    el = shape(id, 'ellipse', cx - w / 2, cy - h / 2, w, h, kind, sw, ss)
    bound(el, label, size, FILL[kind][1])
    return el


def stage(id, x, y, w, kind, tag, title, details, min_h=0, title_size=22, size=16, ss='solid', sw=2):
    """A step: rectangle plus title, role tag and details, grouped so they move together."""
    stroke = FILL[kind][1]
    _, th = measure(title, title_size)
    _, dh = measure(details, size)
    h = max(min_h, 16 + th + 10 + dh + 18)
    g = id + '_g'
    el = shape(id, 'rectangle', x, y, w, h, kind, sw, ss, g)
    text(id + '_title', x + 24, y + 16, title, title_size, stroke, group=g, inside=id)
    if tag:
        text(id + '_tag', x + w - 20, y + 20, tag, 13, stroke, 'right', group=g, inside=id)
    text(id + '_body', x + 24, y + 16 + th + 10, details, size, ONLIGHT, group=g, inside=id)
    return el


def evidence(id, x, y, w, title, body, size=14):
    _, th = measure(title, size)
    _, bh = measure(body, size)
    h = 14 + th + 8 + bh + 14
    g = id + '_g'
    el = shape(id, 'rectangle', x, y, w, h, 'evidence', 1, 'solid', g)
    text(id + '_title', x + 16, y + 14, title, size, ONDARK, group=g, inside=id)
    text(id + '_body', x + 16, y + 14 + th + 8, body, size, GREEN, group=g, inside=id)
    return el


def zone(id, x, y, w, h, kind='zone', ss='dashed', sw=1):
    el = shape(id, 'rectangle', x, y, w, h, kind, sw, ss)
    el['customData'] = {'kind': 'zone'}
    return el


def line(id, pts, color=SLATE, sw=1, ss='dashed'):
    x0, y0 = pts[0]
    rel = [[round(px - x0, 2), round(py - y0, 2)] for px, py in pts]
    xs, ys = [p[0] for p in rel], [p[1] for p in rel]
    el = base(id, 'line', x0, y0, max(xs) - min(xs), max(ys) - min(ys), color, sw=sw, ss=ss)
    el.update({'points': rel, 'lastCommittedPoint': None, 'startBinding': None, 'endBinding': None,
               'startArrowhead': None, 'endArrowhead': None})
    return add(el)


def arrow(id, pts, start=None, end=None, color=SLATE, sw=2, ss='solid', head='arrow', kind='flow'):
    x0, y0 = pts[0]
    rel = [[round(px - x0, 2), round(py - y0, 2)] for px, py in pts]
    xs, ys = [p[0] for p in rel], [p[1] for p in rel]
    el = base(id, 'arrow', x0, y0, max(xs) - min(xs), max(ys) - min(ys), color, sw=sw, ss=ss)
    el.update({'points': rel, 'lastCommittedPoint': None, 'startArrowhead': None, 'endArrowhead': head,
               'elbowed': False, 'startBinding': None, 'endBinding': None, 'customData': {'kind': kind}})
    for key, target in (('startBinding', start), ('endBinding', end)):
        if target:
            el[key] = {'elementId': target, 'focus': 0, 'gap': EDGE}
            t = BY[target]
            t['boundElements'] = (t['boundElements'] or []) + [{'id': id, 'type': 'arrow'}]
    return add(el)


def link(id, src, dst, y=None):
    """Dotted connector from a step's right edge to its example box."""
    s, d = BY[src], BY[dst]
    yy = y if y is not None else d['y'] + min(d['height'] / 2, 40)
    return arrow(id, [(s['x'] + s['width'] + EDGE, yy), (d['x'] - EDGE, yy)], src, dst, SLATE, 1, 'dotted', None, 'link')


# Edge helpers. For diamonds and ellipses, use only the four extreme points.
def left(i, y=None):
    e = BY[i]
    return (e['x'] - EDGE, e['y'] + e['height'] / 2 if y is None else y)


def right(i, y=None):
    e = BY[i]
    return (e['x'] + e['width'] + EDGE, e['y'] + e['height'] / 2 if y is None else y)


def top(i, x=None):
    e = BY[i]
    return (e['x'] + e['width'] / 2 if x is None else x, e['y'] - EDGE)


def bottom(i, x=None):
    e = BY[i]
    return (e['x'] + e['width'] / 2 if x is None else x, e['y'] + e['height'] + EDGE)


def ybot(i):
    return BY[i]['y'] + BY[i]['height']


def ymid(i):
    return BY[i]['y'] + BY[i]['height'] / 2


def band(id, y, title, sub=None):
    line(id + '_rule', [(40, y), (2840, y)], TITLE, 3, 'solid')
    text(id + '_title', 40, y + 18, title, 32, TITLE)
    if sub:
        text(id + '_sub', 40, y + 64, sub, 18, BODY)


def header(id, y, s, sub=None):
    text(id, 40, y, s, 22, TITLE)
    if sub:
        text(id + '_sub', 40, y + 32, sub, 15, BODY)


# ---------------------------------------------------------------- layout constants
X0, W = 700, 560          # main column of the automation
CX = X0 + W / 2           # 980
RX, RW = 1380, 640        # what worked by hand, real files and side branches
PX, PW = 2120, 720        # side panels
GAP = 70
LANE = {'a': 660, 'b': 630, 'c': 600, 'd': 570, 'e': 520, 'f': 490, 'g': 460}

# ================================================================= header
text('title', 40, 30, 'Deep Six animation: the whole system on one canvas', 40, TITLE)
text('subtitle', 40, 92, 'Approved narration MP3 in; finished 9:16 video out, in the style of the approved fire-ant video. 19 Oct 2026.\n'
     'A: the standard.  B: how we got here.  C: the automation (designed, not built).  D: problems, models, files, next.\n'
     'Far right: the whole thing in plain words, from the very beginning, with options and what-ifs for every step.',
     18, BODY)
zone('legend_zone', PX, 24, PW, 300)
text('legend_title', PX + 20, 36, 'LEGEND', 18, TITLE)
legend = [
    ('code', 'rect', 'Runner step: code, local, free'), ('ai', 'rect', 'AI step: Claude Code / Opus 5.5'),
    ('drew', 'diamond', 'Drew\'s gate: only Drew approves'), ('branch', 'diamond', 'Automatic branch'),
    ('input', 'ellipse', 'MP3 system (outside)'),
    ('back', 'arrow', 'Sent back to fix'), ('later', 'rect', 'Later piece, not built yet'),
    ('evidence', 'rect', 'Real file from 19 Oct'), ('done', 'ellipse', 'Approved, finished'),
    ('error', 'rect', 'Rejected or failed'),
]
for i, (kind, form, label) in enumerate(legend):
    col, row = divmod(i, 5)
    lx, ly = PX + 20 + col * 360, 76 + row * 48
    iid = f'legend_icon_{i}'
    if form == 'rect':
        shape(iid, 'rectangle', lx, ly, 44, 26, kind, 1 if kind == 'evidence' else 2, 'dashed' if kind == 'later' else 'solid')
    elif form == 'diamond':
        shape(iid, 'diamond', lx, ly - 4, 44, 34, kind, 2)
    elif form == 'ellipse':
        shape(iid, 'ellipse', lx, ly, 44, 26, kind, 2)
    else:
        arrow(iid, [(lx, ly + 13), (lx + 44, ly + 13)], color=RED, ss='dashed', kind='legend')
    text(f'legend_label_{i}', lx + 58, ly + 3, label, 15, ONLIGHT)

# ================================================================= A  the standard
A = 380
band('band_a', A, 'A  THE STANDARD: every video matches the approved fire-ant video')
image('img_approved', 'approved-full-v2.jpg', 40, A + 90, 1200, round(1200 * 480 / 1660, 2))
cy_ = ybot('img_approved') + 12
text('approved_caption', 40, cy_, 'Deep Six - Fire Ants Full v2.mp4, on Drew\'s Desktop: six moments from 0.9 s to 74 s.', 15, BODY)
text('approved_facts', 40, cy_ + 32,
     '79.2 s · 76 shots · 123 beats · 211 words · 3 sets: nest cutaway, nursery close-up, backyard\n'
     'Opus 5.5 made the lesson. Approved final: 88.10 s, including closing and 5.50 s outro.', 16, ONLIGHT)
stage('drew_said', 40, cy_ + 92, 1200, 'drew', 'DREW', 'What Drew said',
      'Hook v1: "It\'s really good ... I do like everything about it."\n'
      'Full v2: "very, very good ... the design, how it flows, how it does stuff is very, very good."\n'
      'His rule: keep this style for every video.')
text('bar_title', 1300, A + 90, 'THE QUALITY BAR', 22, TITLE)
text('bar_rules', 1300, A + 132,
     '1  One picture per 1 to 3 spoken words, landing on the word.\n'
     '2  New shot every 0.7-1.5 s in the hook, never over 2 s anywhere.\n'
     '   Something new appears about every 0.5 s.\n'
     '3  Constant motion: the camera pushes or drifts through every hold.\n'
     '4  Literal first: show the exact thing named. Symbols only for\n'
     '   absence or negation: dashed outline, purple X, question mark.\n'
     '5  Cut-paper style C: paper pieces, soft shadows, fibre grain,\n'
     '   natural insect and soil colours plus the Deep Six colours.\n'
     '6  Word-synced captions: torn paper strips near y 1420, lime tape\n'
     '   on the spoken word, 1 to 4 words per group.\n'
     '7  Three or four reusable sets per video. Move the camera inside\n'
     '   a set; cut hard on a new sentence or idea.\n'
     '8  Science limits: correct anatomy; no invented mechanisms,\n'
     '   depths, temperatures or treatment advice.\n'
     '9  9:16, 1080x1920, 30 fps. Key action between y 250 and 1250;\n'
     '   bottom 300 px and right 120 px kept clear.', 16, ONLIGHT)
text('targets_title', 2080, A + 90, 'TARGETS, MEASURED', 22, TITLE)
text('targets_table', 2080, A + 132,
     'CHECK                  TARGET          APPROVED\n'
     'Format                 1080x1920 30fps pass\n'
     'Audio and video        same length, 0  79.2 s each\n'
     'Longest nearly still   at most 0.35 s  0.33 s\n'
     'Change per half second at least 15%    17%\n'
     'Hook after kit changes pixel-identical pass', 15, ONLIGHT)
text('targets_note', 2080, A + 264, 'Reference shorts we liked: 4 to 62% change.\nThe rejected test: 0.1%.', 15, BODY)
text('palette_title', 2080, A + 330, 'DEEP SIX COLOURS', 18, TITLE)
for i, (kind, label) in enumerate([('sw_purple', 'purple\n#3A3148'), ('sw_lime', 'lime\n#A9D554'), ('sw_cream', 'cream\n#F0DDB2'),
                                   ('sw_paper', 'paper\n#F6EFE2'), ('sw_ink', 'ink\n#1E1B22')]):
    shape(f'swatch_{i}', 'rectangle', 2080 + i * 150, A + 366, 64, 44, kind, 1)
    text(f'swatch_label_{i}', 2080 + i * 150, A + 418, label, 13, ONLIGHT)

# ================================================================= B  how we got here
B = ybot('drew_said') + 90
band('band_b', B, 'B  HOW WE GOT HERE: 19 Oct 2026, one day of tests')
EVX = [140 + i * 256 for i in range(11)]
img_bottom = B + 92 + 362
image('img_styles', 'style-options.jpg', EVX[2] - 98, img_bottom - 360.74, 196, 360.74)
image('img_rejected', 'rejected-motion-test.jpg', EVX[3] - 141, img_bottom - 361.1, 282, 361.1)
image('img_models', 'model-test-opus-sol-astra.jpg', EVX[9] - 369, img_bottom - 211.88, 738, 211.88)
text('cap_styles', EVX[2], img_bottom + 10, 'Four looks; Drew chose C', 14, BODY, 'center')
text('cap_rejected', EVX[3], img_bottom + 10, 'Rejected: one still scene', 14, BODY, 'center')
for k, label in enumerate(['Opus: approved', 'Sol: "not bad"', 'Astra: "super bad"']):
    text(f'cap_model_{k}', EVX[9] - 369 + (k * 416 + 204) * 738 / 1240, img_bottom + 10, label, 14, BODY, 'center')
text('cap_models_note', EVX[9] - 369, img_bottom - 211.88 - 50,
     'Same 13 seconds, two moments each. Astra\'s\nbrood floats over an empty wall.', 14, BODY)
yl = img_bottom + 70
line('tl_line', [(100, yl), (2780, yl)], SLATE, 2, 'solid')
events = [
    ('code', 'Research', 'Compared code-drawn\nanimation kits; chose\na canvas kit and a\nlocal renderer.'),
    ('later', 'First frames', 'Science-book scene,\nthen Deep Six ad\ncolours (brand.json).'),
    ('drew', 'Style options', 'A, B, C, D drawn as\ncode. Drew chose C,\ncut-paper storybook.'),
    ('error', 'Motion test: REJECTED', 'One scene, one slow\nant. "Too little\nmotion, too few\nscenes"; captions off.'),
    ('code', 'Pacing research', '12 reference shorts.\nFastest: a new\npicture every\n0.6 to 0.7 s.'),
    ('code', 'Method rebuilt', 'Word timing by 3\nmodels; director and\nanimator prompts;\npaper kit.'),
    ('done', 'Hook v1: APPROVED', '8.8 s, 8 shots,\n25 beats. First try.\nOpus 5.5 at max.'),
    ('later', 'Full v1: not shown', 'Failed its own\nmotion check:\n1 s still, 14%.'),
    ('done', 'Full v2: APPROVED', '79.2 s, 76 shots.\n"Very, very good."\nAbout 65 min from\nDrew\'s go-ahead.'),
    ('error', 'Model test, same 13 s', 'Astra "super bad",\nSol "not bad".\nChecks passed both.'),
    ('drew', 'Drew\'s model rule', 'Claude Code;\nOpus 5.5 throughout.\nAstra/Sol: later\nprompting research.'),
]
for i, (kind, name, detail) in enumerate(events):
    shape(f'ev_dot_{i}', 'ellipse', EVX[i] - 12, yl - 12, 24, 24, kind, 2, 'dashed' if kind == 'later' else 'solid')
    text(f'ev_name_{i}', EVX[i], yl + 24, name, 15, FILL[kind][1], 'center')
    text(f'ev_text_{i}', EVX[i], yl + 48, detail, 14, ONLIGHT, 'center')
for i in (2, 3):
    line(f'ev_tick_{i}', [(EVX[i], img_bottom + 34), (EVX[i], yl - 16)], SLATE, 1, 'dotted')
line('ev_tick_9', [(EVX[9], img_bottom + 34), (EVX[9], yl - 16)], SLATE, 1, 'dotted')
ly_ = yl + 48 + 4 * 17.5 + 36
text('lesson_1', 40, ly_, 'Lesson: the rejected test was also style C. The method made the difference, not the art style.', 18, RED)
text('lesson_2', 40, ly_ + 32,
     'Lesson: stills and motion numbers ranked Astra first. Drew watched and called it "super bad". Watching is the gate.',
     18, RED)
text('dots_key', 1500, ly_, 'Dots: green approved · red rejected · amber Drew chose\n'
     'blue built or researched · pale blue replaced or never shown', 15, BODY)

# ================================================================= C  the automation
C = ybot('lesson_2') + 90
band('band_c', C, 'C  THE AUTOMATION: approved MP3 to finished MP4',
     'Designed from what worked on 19 Oct; not built yet. One video at a time. Only Drew approves.')
gy = C + 112
text('glance_title', 40, gy, 'AT A GLANCE', 15, BODY)
line('glance_line', [(100, gy + 64), (1960, gy + 64)], SLATE, 2, 'solid')
glance = [('input', 'Approved\nMP3'), ('drew', 'Drew picks\nstart time'), ('code', 'Time\nwords'), ('ai', 'Plan the\nvideo'), ('branch', 'New\ndrawings?'),
          ('ai', 'Make\nsegments'), ('code', 'Join and\nrender'), ('ai', 'Check and\nwatch'), ('code', 'Copy to\nDesktop'),
          ('drew', 'Drew\napproves'), ('done', 'Done')]
for i, (kind, label) in enumerate(glance):
    gx = 100 + i * (1860 / (len(glance) - 1))
    shape(f'glance_dot_{i}', 'ellipse', gx - 11, gy + 53, 22, 22, kind, 2)
    text(f'glance_label_{i}', gx, gy + 84, label, 15, ONLIGHT, 'center')

# input and scope
text('input_owner', CX, C + 262, 'MADE BY THE MP3 SYSTEM: another session, not part of this design', 15, BODY, 'center')
ellipse('input', CX, C + 362, 380, 120, 'input', 'Approved\nnarration MP3', 22)
evidence('ev_input', RX, C + 306, 460, 'WHAT ARRIVES',
         'narration.mp3, approved by Drew\nthe approved script, word for word\naudio fingerprint (sha256)\n'
         'science limits for this episode')
link('lk_input', 'input', 'ev_input', C + 362)
line('scope_line', [(40, C + 470), (2040, C + 470)], TITLE, 2, 'dashed')
text('scope_label', 40, C + 442, 'THIS DESIGN STARTS HERE', 15, TITLE)
text('right_header', RX, C + 482, 'RIGHT: what worked by hand on 19 Oct, and its real files', 15, TITLE)

diamond('g0', CX, C + 620, 460, 220, 'drew', 'DREW:\nstart now, tonight\nor later?', 20, 3)
arrow('a_input_g0', [bottom('input'), top('g0')], 'input', 'g0', FILL['input'][1])
text('g0_note', 1236, C + 566, 'Asked when the MP3 is approved.\nTonight: starts at 11 PM.\n'
     'Later: waits until Drew says go.\nHe answers in chat; an agent records it.', 15, ONLIGHT)

# 1 prepare
y = ybot('g0') + GAP
header('h_prepare', y, '1 PREPARE')
stage('s1', X0, y, W, 'code', 'RUNNER', 'Pick up the MP3, gather inputs',
      'One video at a time, in the order started.\nThe MP3 must match its approval fingerprint.\n'
      'Gathers science limits, Drew\'s past verdicts,\napproved frames, palette and science notes.\n'
      'Mismatch: park and tell Drew.')
arrow('a_g0_s1', [bottom('g0'), top('s1')], 'g0', 's1', FILL['drew'][1])
evidence('ev_gather', RX, y, RW, 'BY HAND, 19 OCT: inputs gathered first, about 15 minutes',
         'approved narration and its science limits\nMP3 manifest and its fingerprint\nDrew\'s rejection feedback, quoted\n'
         'approved style C frame and the brand palette\nscience-notes.md: anatomy, no mound opening\n'
         'pacing research, run by a cheaper helper')
link('lk_gather', 's1', 'ev_gather')

y = ybot('s1') + GAP
stage('s2', X0, y, W, 'code', 'RUNNER', 'Time every word',
      'Local and free: 3 offline speech models vote.\nEach start is snapped to measured silences.\n'
      'Flags words where the models disagree.\nCheck: every script word, in order.\nFails: park and tell Drew.')
arrow('a_s1_s2', [bottom('s1'), top('s2')], 's1', 's2', FILL['code'][1])
evidence('ev_words', RX, y, RW, 'BY HAND: 3 speech models voted on all 211 words · words.json',
         '{"audio_sha256": "a3e6c219...",\n "words": [\n  {"text": "fire", "start": 0.22, "end": 0.52},\n'
         '  {"text": "ant", "start": 0.52, "end": 0.71}],\n "caption_groups": [{"words": [0, 1, 2]}]}')
link('lk_words', 's2', 'ev_words')

# 2 plan
y = ybot('s2') + GAP
header('h_plan', y, '2 PLAN')
stage('s3', X0, y, W, 'ai', 'DIRECTOR · AI', 'Plan the whole video',
      'One picture per 1 to 3 words, on the word.\nProven sets and shot types first.\n'
      'Splits it into 6-15 s segments at pauses.\nLists any new drawings it needs.\nGives a short title for the file name.')
arrow('a_s2_s3', [bottom('s2'), top('s3')], 's2', 's3', FILL['code'][1])
evidence('ev_shot', RX, y, RW, 'BY HAND: 76 shots and 123 beats planned before drawing',
         '{"id": "S1", "start": 0.0, "end": 1.14,\n "words": "A fire ant colony",\n'
         ' "beats": [{"word": "colony", "at": 0.72,\n   "action": "Fast zoom-out reveals the crowd."}],\n'
         ' "camera": "Tracks the hero ant, then zooms out."}')
link('lk_shot', 's3', 'ev_shot')

y = ybot('s3') + GAP
stage('s4', X0, y, W, 'code', 'RUNNER · CHECK', 'Check the plan',
      'Every word captioned once, in order, 1-4 per group.\nEvery beat starts on a word.\n'
      'No shot over 2 s; hook shots 0.7-1.5 s.\nSegments 6-15 s, end to end, no gaps.\n'
      'Fails: back to the Director with the errors.')
arrow('a_s3_s4', [bottom('s3'), top('s4')], 's3', 's4', FILL['ai'][1])
arrow('loop_plan', [left('s4'), (LANE['a'], ymid('s4')), (LANE['a'], ybot('s3') - 34), left('s3', ybot('s3') - 34)],
      's4', 's3', RED, 2, 'dashed', kind='back')
evidence('ev_segments', RX, y, RW, 'EXAMPLE: two segments, cut at a sentence pause',
         '[{"name": "seg01",\n  "start": 57.6, "end": 67.8},\n'
         ' {"name": "seg02",\n  "start": 67.8, "end": 78.6}]')
link('lk_segments', 's4', 'ev_segments')

# 3 new drawings (only for a new pest or set)
y = ybot('s4') + GAP
header('h_draw', y, '3 NEW DRAWINGS', 'only for a new pest or set')
diamond('d5', CX, y + 75, 300, 150, 'branch', 'New drawings\nneeded?')
arrow('a_s4_d5', [bottom('s4'), top('d5')], 's4', 'd5', FILL['code'][1])
stage('s5', RX, ymid('d5') - 100, RW, 'ai', 'ASSET MAKER · AI', 'Make the new drawings',
      'Researched anatomy, same cut-paper style.\nNew files only; old drawings never change.\n'
      'Sheet beside the fire ant, plus a walk test,\non the Desktop and the board.\nAnatomy sources go in the source log.\n'
      '19 Oct: kit first, sets reused; no style drift.', min_h=200)
arrow('a_d5_s5', [right('d5'), left('s5', ymid('d5'))], 'd5', 's5', FILL['branch'][1])
text('l_d5_yes', (BY['d5']['x'] + BY['d5']['width'] + RX) / 2, ymid('d5') - 30, 'yes', 15, ONLIGHT, 'center')
diamond('g5', RX + RW / 2, ybot('s5') + GAP + 110, 400, 220, 'drew', 'DREW:\napprove the new\ndrawings?', 20, 3)
arrow('a_s5_g5', [bottom('s5'), top('g5')], 's5', 'g5', FILL['ai'][1])
arrow('loop_g5', [right('g5'), (2060, ymid('g5')), (2060, ybot('s5') - 40), right('s5', ybot('s5') - 40)],
      'g5', 's5', RED, 2, 'dashed', kind='back')
text('l_g5_notes', 1924, ymid('g5') + 10, 'notes', 15, RED)

# 4 make segments
y = ybot('g5') + 130
header('h_make', y - 40, '4 MAKE SEGMENTS')
stage('s6', X0, y, W, 'ai', 'ANIMATOR · AI', 'Make segment N',
      'Writes scene code for the planned shots.\nShots as data: camera keys plus set state.\nReads earlier segments for continuity.\n'
      'Sees frames from the approved video.\nLooks at its own frames until checks pass.', min_h=200)
arrow('a_d5_s6', [bottom('d5'), top('s6')], 'd5', 's6', FILL['branch'][1])
text('l_d5_no', CX + 14, ybot('d5') + 24, 'no: the kit has them', 15, ONLIGHT)
arrow('a_g5_s6', [bottom('g5'), (RX + RW / 2, y - 40), (CX + 70, y - 40), top('s6', CX + 70)], 'g5', 's6', FILL['drew'][1])
text('l_g5_ok', RX + RW / 2 + 14, ybot('g5') + 46, 'approve: they join the kit, protected', 15, ONLIGHT)

ly = y + 6
text('rl_title', RX, ly - 30, 'INSIDE THE ANIMATOR, as done by hand: up to 6 rounds', 15, TITLE)
rl = [('rl_write', RX, ly, 'Write or fix\nscene code'), ('rl_sheet', RX + 340, ly, 'Render one still\nper beat (--sheet)'),
      ('rl_look', RX + 340, ly + 110, 'Look at every tile;\nclose-ups with --at'),
      ('rl_motion', RX, ly + 110, 'Measure motion\n(--check-motion)')]
for rid, rx, ry, label in rl:
    box(rid, rx, ry, 300, 64, 'ai', label, 15, 1)
arrow('rl_1', [right('rl_write'), left('rl_sheet')], 'rl_write', 'rl_sheet', PURPLE, 1)
arrow('rl_2', [bottom('rl_sheet'), top('rl_look')], 'rl_sheet', 'rl_look', PURPLE, 1)
arrow('rl_3', [left('rl_look'), right('rl_motion')], 'rl_look', 'rl_motion', PURPLE, 1)
arrow('rl_4', [top('rl_motion'), bottom('rl_write')], 'rl_motion', 'rl_write', PURPLE, 1)
link('lk_rl', 's6', 'rl_write', ymid('rl_write'))

y = ybot('s6') + GAP
stage('s7', X0, y, W, 'code', 'RUNNER · CHECK', 'Check segment N',
      'Guard restores any protected file.\nCode loads; each frame renders the same.\n'
      'Still at most 0.35 s; change at least 15%.\nApproved hook still pixel-identical.\nFails: back to the Animator.')
arrow('a_s6_s7', [bottom('s6'), top('s7')], 's6', 's7', FILL['ai'][1])
evidence('ev_motion', RX, y + 10, RW, 'BY HAND: v1 failed (1 s still, 14%); v2 passed · --check-motion',
         '{"longest_still_seconds": 0.33,\n "picture_change_half_second_median": 0.17,\n'
         ' "targets": {"longest_still_seconds": "<= 0.35",\n   "picture_change_half_second_median": ">= 0.15"}}')
link('lk_motion', 's7', 'ev_motion')

y = ybot('s7') + GAP
stage('s8', X0, y, W, 'ai', 'REVIEWER · AI', 'Watch segment N',
      'Fresh session, never the one that made it.\n5-fps filmstrips beside the approved video\'s.\n'
      'Checks the 15 problems seen before.\nCan send work back; can never approve.\nFails: back to the Animator with notes.')
arrow('a_s7_s8', [bottom('s7'), top('s8')], 's7', 's8', FILL['code'][1])
evidence('ev_problems', RX, y - 6, RW, 'BY HAND: 15 problems the self-checks caught (examples)',
         'close-up cluttered by other ants\nants upside down on slopes\nempty sky in side views\n'
         'paper moves blurred into ghosts\nbrood too small to read\nprops overlapping characters\n'
         'holds going still for 1 s\n(full list with fixes: band D)')
link('lk_problems', 's8', 'ev_problems')
text('callout', RX, ybot('ev_problems') + 14,
     'Automatic checks passed Astra\'s "super bad" clip.\nChecks and the reviewer can only send work back.\n'
     'Only Drew approves.', 16, RED)

y = ybot('s8') + 90
diamond('d9', CX, y + 70, 280, 140, 'branch', 'Risky\nsegment?')
arrow('a_s8_d9', [bottom('s8'), top('d9')], 's8', 'd9', FILL['ai'][1])
text('l_s8_pass', CX + 14, ybot('s8') + 30, 'pass: saved as done in the ledger', 15, ONLIGHT)
diamond('g9', CX, ybot('d9') + GAP + 110, 400, 220, 'drew', 'DREW:\napprove this\nclip?', 20, 3)
arrow('a_d9_g9', [bottom('d9'), top('g9')], 'd9', 'g9', FILL['branch'][1])
text('l_d9_yes', CX + 14, ybot('d9') + 22, 'yes', 15, ONLIGHT)
diamond('d10', CX, ybot('g9') + GAP + 70, 280, 140, 'branch', 'More\nsegments?')
arrow('a_g9_d10', [bottom('g9'), top('d10')], 'g9', 'd10', FILL['drew'][1])
text('l_g9_ok', CX + 14, ybot('g9') + 22, 'approve', 15, ONLIGHT)
arrow('a_d9_bypass', [right('d9'), (1300, ymid('d9')), (1300, ymid('d10')), right('d10')], 'd9', 'd10', FILL['branch'][1])
text('l_d9_no', 1180, ymid('d9') - 30, 'no', 15, ONLIGHT)
text('risky_note', RX, ymid('d9') - 30,
     'Risky = the first segment with new drawings\nor a new pest or set.\n\n'
     'Drew watches the clip on the Desktop or board.\nHis notes go back to the Animator.\n\n'
     '19 Oct: Drew approved the hook first; then the\nfull video was made.\n\nDrew\'s choice, 19 Oct: risky runs only.', 16, ONLIGHT)

s6 = BY['s6']
arrow('loop_s7', [left('s7'), (LANE['a'], ymid('s7')), (LANE['a'], s6['y'] + 170), left('s6', s6['y'] + 170)],
      's7', 's6', RED, 2, 'dashed', kind='back')
arrow('loop_s8', [left('s8'), (LANE['b'], ymid('s8')), (LANE['b'], s6['y'] + 140), left('s6', s6['y'] + 140)],
      's8', 's6', RED, 2, 'dashed', kind='back')
arrow('loop_g9', [left('g9'), (LANE['c'], ymid('g9')), (LANE['c'], s6['y'] + 110), left('s6', s6['y'] + 110)],
      'g9', 's6', RED, 2, 'dashed', kind='back')
text('l_g9_notes', 700, ymid('g9') - 28, 'notes', 15, RED)
arrow('loop_next', [left('d10'), (LANE['d'], ymid('d10')), (LANE['d'], s6['y'] + 80), left('s6', s6['y'] + 80)],
      'd10', 's6', FILL['branch'][1], 2, 'solid')
text('l_next', 610, ymid('d10') - 28, 'yes: next segment', 15, ONLIGHT)

zone('seg_zone', 545, s6['y'] - 76, 1340 - 545, ybot('d10') + 40 - (s6['y'] - 76))
text('seg_zone_title', 562, s6['y'] - 64, 'REPEAT FOR EACH SEGMENT, IN ORDER', 18, BODY)

# 5 finish
y = ybot('seg_zone') + 70
header('h_finish', y, '5 FINISH')
stage('s11', X0, y, W, 'code', 'RUNNER', 'Join and render',
      'Joins the lesson, closing thought and approved outro.\nOne voice and caption track for the whole video.\nRenders the MP4: about 17 min per 80 s.')
arrow('a_d10_s11', [bottom('d10'), top('s11')], 'd10', 's11', FILL['branch'][1])
text('l_d10_no', CX + 14, ybot('seg_zone') + 14, 'no: all segments done', 15, ONLIGHT)
fy = y - 10
box('f1', RX + 60, fy, 420, 74, 'done', 'This episode: closing thought\nReuse the approved paper wipe', 16)
box('f2', RX + 60, fy + 124, 420, 92, 'done', 'REUSE: approved Deep Six outro\nSilent animation; this episode\nsupplies voice and captions', 16)
box('f3', RX + 60, fy + 266, 420, 74, 'later', 'LATER: music under\nthe narration', 16, 2, 'dashed')
arrow('a_s11_f1', [right('s11', ymid('f1')), left('f1')], 's11', 'f1', FILL['done'][1])
arrow('a_f1_f2', [bottom('f1'), top('f2')], 'f1', 'f2', FILL['done'][1])
arrow('a_f2_f3', [bottom('f2'), top('f3')], 'f2', 'f3', FILL['later'][1], 2, 'dashed')

y = ybot('f3') + 60
header('h_check', y, '6 CHECK AND WATCH')
stage('s13', X0, y, W, 'code', 'RUNNER · CHECK', 'Check the finished file',
      '1080x1920, 30 fps, 9:16.\nAudio and video start at 0, same length.\n'
      'Lesson: still at most 0.35 s, change 15%+.\nOutro: preserve approved action and final hold.\nFrames on key words and at every joint.\nFails: to Triage.')
arrow('a_s11_s13', [bottom('s11'), top('s13')], 's11', 's13', FILL['code'][1])
text('l_today', CX + 14, ybot('s11') + 40, 'includes approved outro', 15, ONLIGHT)
arrow('a_f3_s13', [left('f3'), (CX + 150, ymid('f3')), top('s13', CX + 150)], 'f3', 's13', FILL['later'][1], 2, 'dashed')
evidence('ev_final', RX, y + 40, RW, 'BY HAND: the encoded file, measured (approved video)',
         '{"width": 1080, "height": 1920, "fps": "30/1",\n "audio_seconds": 79.2, "video_seconds": 79.2,\n'
         ' "longest_still_seconds": 0.33,\n "picture_change_half_second_median": 0.17}')
link('lk_final', 's13', 'ev_final')

y = ybot('s13') + GAP
stage('s14', X0, y, W, 'ai', 'REVIEWER · AI', 'Watch the whole video',
      'Whole-video filmstrips beside the approved video.\nSets and characters match across segments.\n'
      'Captions on time; flagged words first.\nScience limits: no invented numbers or claims.\nFails: to Triage.')
arrow('a_s13_s14', [bottom('s13'), top('s14')], 's13', 's14', FILL['code'][1])
evidence('ev_review', RX, y, RW, 'reviewer verdict (example, from a past test)',
         '{"pass": false, "segment": "seg03",\n "notes": [{"shot": "S24",\n'
         '   "problem": "brood floating over an empty wall",\n   "fix": "keep the brood on the chamber floor"}]}')
link('lk_review', 's14', 'ev_review')

ty = BY['s13']['y'] + 40
stage('s_triage', 60, ty, 480, 'ai', 'TRIAGE · AI', 'Sort the fixes',
      'Maps each failed check or note to\na stage and a time range.\n\nShot problem: redo those segments.\n'
      'Plan problem: re-plan that stretch.\nCaption timing: re-time those words.\nUnclear note: ask Drew (multiple choice).\n'
      'Outro timing: fix the join, voice or captions.\nMusic note: saved for later.\nUntouched segments stay pixel-identical.\n'
      'Then join, render, check, deliver v2.', min_h=ymid('s14') + 70 - ty)
arrow('a_s13_tri', [left('s13', ymid('s13') + 20), right('s_triage', ymid('s13') + 20)], 's13', 's_triage', RED, 2, 'dashed', kind='back')
arrow('a_s14_tri', [left('s14'), right('s_triage', ymid('s14'))], 's14', 's_triage', RED, 2, 'dashed', kind='back')
tri = BY['s_triage']
arrow('tri_s2', [(LANE['g'], tri['y'] - EDGE), (LANE['g'], BY['s2']['y'] + 40), left('s2', BY['s2']['y'] + 40)],
      's_triage', 's2', RED, 2, 'dashed', kind='back')
text('l_tri_s2', 690, BY['s2']['y'] + 14, 're-time words', 15, RED, 'right')
arrow('tri_s3', [(LANE['f'], tri['y'] - EDGE), (LANE['f'], BY['s3']['y'] + 40), left('s3', BY['s3']['y'] + 40)],
      's_triage', 's3', RED, 2, 'dashed', kind='back')
text('l_tri_s3', 690, BY['s3']['y'] + 14, 're-plan a stretch', 15, RED, 'right')
arrow('tri_s6', [(LANE['e'], tri['y'] - EDGE), (LANE['e'], s6['y'] + 40), left('s6', s6['y'] + 40)],
      's_triage', 's6', RED, 2, 'dashed', kind='back')
text('l_tri_s6', 690, s6['y'] + 14, 'redo segments', 15, RED, 'right')

# 7 deliver and approve
y = ybot('s14') + GAP
stage('s15', X0, y, W, 'code', 'RUNNER', 'Deliver',
      'Copy to the Windows Desktop:\n  "Deep Six - <title> v1.mp4"\nNever overwrite; verify the copy; never open a player.\n'
      'Board entry: moving preview and beat sheets.\nDelivery note: which model made each segment.')
arrow('a_s14_s15', [bottom('s14'), top('s15')], 's14', 's15', FILL['ai'][1])
evidence('ev_desktop', RX, y, RW, 'BY HAND: copied and verified, no player opened',
         '{"status": "copied_and_verified",\n "bytes": 67496747,\n "sha256": "c7ff2561...",\n "player_opened": false}')
link('lk_desktop', 's15', 'ev_desktop')

y = ybot('s15') + GAP
header('h_approve', y, '7 DREW APPROVES')
diamond('g16', CX, y + 130, 480, 260, 'drew', 'DREW\nwatches it:\napprove?', 22, 3)
arrow('a_s15_g16', [bottom('s15'), top('g16')], 's15', 'g16', FILL['code'][1])
arrow('a_g16_tri', [left('g16'), (500, ymid('g16')), (500, ybot('s_triage') + EDGE)], 'g16', 's_triage', RED, 2, 'dashed', kind='back')
text('l_g16_notes', 520, ymid('g16') - 28, 'notes', 15, RED)
evidence('ev_verdict', RX, y + 40, RW, 'verdicts.jsonl (example; a real complaint from 19 Oct)',
         '{"video": "v1", "verdict": "notes",\n "said": "subtitle timing did not match speech",\n'
         ' "fix": "re-time words 40-62, re-render"}')
link('lk_verdict', 'g16', 'ev_verdict', ymid('g16'))
text('verdict_note', RX, ybot('ev_verdict') + 14,
     'Drew gives his verdict in chat. An agent records it\nwith one command; the runner then continues.', 15, BODY)

y = ybot('g16') + 80
ellipse('done', CX, y + 60, 380, 120, 'done', 'Finished MP4,\napproved', 22)
arrow('a_g16_done', [bottom('g16'), top('done')], 'g16', 'done', FILL['drew'][1])
text('l_g16_ok', CX + 14, ybot('g16') + 26, 'approve', 15, ONLIGHT)
oy = ybot('done') + 90
stage('o1', 240, oy, 400, 'code', 'RUNNER', 'Lock the run', 'Its files join the protected list.')
ellipse('o2', CX, oy + 60, 380, 120, 'input', 'MP3 system marks\nthis episode\'s\nsources as used', 16, 2, 'dashed')
stage('o3', 1320, oy, 400, 'code', 'RUNNER', 'Start the next MP3', 'Back to the top of the queue.')
arrow('a_done_o1', [left('done'), (440, ymid('done')), top('o1', 440)], 'done', 'o1', FILL['done'][1])
arrow('a_done_o2', [bottom('done'), top('o2')], 'done', 'o2', FILL['done'][1], 2, 'dashed')
arrow('a_done_o3', [right('done'), (1520, ymid('done')), top('o3', 1520)], 'done', 'o3', FILL['done'][1])

# side panels
py = C + 300
zone('router_zone', PX, py, PW, 10, 'aizone', 'solid', 2)
text('router_title', PX + 24, py + 18, 'MAIN FLOW: CLAUDE CODE', 24, PURPLE)
text('router_sub', PX + 24, py + 52, 'Every AI role uses Opus 5.5. Local tools do the rest.', 15, BODY)
ladder = [('r1', 'ai', '1  Opus 5.5, max effort', 'Claude Code on Drew\'s Claude plan'),
          ('r4', 'pause', 'Pause and wait', 'Save finished work. Resume with Claude Code\nwhen available; keep the same approved choices.')]
why = ['Claude usage limit, or Opus unavailable']
ry = py + 96
for i, (rid, kind, name, detail) in enumerate(ladder):
    stage(rid, PX + 30 + i * 30, ry, 560, kind, '', name, detail, title_size=20, size=15)
    if i:
        prev = ladder[i - 1][0]
        ax = BY[prev]['x'] + 60
        arrow(f'a_{prev}_{rid}', [(ax, ybot(prev) + EDGE), (ax, ry - EDGE)], prev, rid, FILL['ai'][1] if i < 3 else RED)
        text(f'l_{rid}', ax + 14, ybot(prev) + 22, why[i - 1], 15, ONLIGHT)
    ry = ybot(rid) + GAP
rules = ('Quality failure: Opus retries with notes.\nAvailability failure: pause and save progress.\n'
         'Every job gets a shell, file writing and image viewing.\nEvery job sees frames from the approved video.\n'
         'Use the Claude subscription; no paid API calls.\nAstra/Sol prompting research stays outside this flow.')
text('router_rules', PX + 30, ry - 30, rules, 16, ONLIGHT)
ry = ry - 30 + measure(rules, 16)[1] + 24
evidence('ev_router', PX + 30, ry, PW - 60, 'Claude Code call (no --bare, no API key)',
         'claude -p --model claude-opus-5-5 --effort max\n  --output-format json --json-schema <schema>\n\n'
         'Canvas decision: Claude-only main flow.\nExisting runner defaults still need a separate update.')
BY['router_zone']['height'] = round(ybot('ev_router') + 24 - py, 2)

py = ybot('router_zone') + 80
zone('guard_zone', PX, py, PW, 10, 'zone', 'solid', 1)
text('guard_title', PX + 24, py + 18, 'GUARD', 24, TITLE)
text('guard_sub', PX + 24, py + 52, 'Wraps every AI job.', 15, BODY)
steps = ['Snapshot protected files: kit, sets, renderer,\ntools, prompts and approved videos.',
         'The AI adds new files only: its module and job folder.',
         'After the job, restore anything changed, and log it.',
         'Re-render the approved hook\'s beat sheet:\nit must match pixel for pixel.']
gy2, dots = py + 96, []
for i, s in enumerate(steps):
    shape(f'guard_dot_{i}', 'ellipse', PX + 34, gy2 + 4, 14, 14, 'code', 1)
    text(f'guard_step_{i}', PX + 64, gy2, s, 16, ONLIGHT)
    dots.append(gy2 + 11)
    gy2 += measure(s, 16)[1] + 22
line('guard_line', [(PX + 41, dots[0] + 8), (PX + 41, dots[-1] - 8)], SLATE, 1, 'solid')
BY['guard_zone']['height'] = round(gy2 + 4 - py, 2)

py = ybot('guard_zone') + 80
zone('ledger_zone', PX, py, PW, 10, 'zone', 'solid', 1)
text('ledger_title', PX + 24, py + 18, 'RUN LEDGER', 24, TITLE)
text('ledger_sub', PX + 24, py + 52, 'Stop and resume anywhere.', 15, BODY)
ledger = ('Each step saves its files, then marks itself done.\nRe-running the same command resumes; finished work is kept.\n'
          'A half-finished AI job restarts its segment.\nWaits on: its start time, Drew\'s verdict, a usage\n'
          'reset (automatic), or a parked failure (Drew decides).')
text('ledger_text', PX + 30, py + 90, ledger, 16, ONLIGHT)
evidence('ev_ledger', PX + 30, py + 90 + measure(ledger, 16)[1] + 24, PW - 60, 'run.json (example)',
         '{"run": "d6-6c917b49743b-opus",\n "step": "segments",\n "segments_done": ["seg01", "seg02"],\n'
         ' "made_by": {"seg01": "opus", "seg02": "opus"},\n "attempts": {"seg03": 2},\n'
         ' "waiting_for": "usage reset 21:40"}')
BY['ledger_zone']['height'] = round(ybot('ev_ledger') + 24 - py, 2)

py = ybot('ledger_zone') + 80
zone('retry_zone', PX, py, PW, 10, 'zone', 'solid', 1)
text('retry_title', PX + 24, py + 18, 'RETRIES AND STOPS', 24, TITLE)
retry = ('Plan fails its check: the Director retries twice\nwith the errors.\n\n'
         'Segment fails a check or review: the Animator\nretries twice with notes; the best try is kept.\n\n'
         'Render or encoder crash: retry once.\n\n'
         'Still failing: park. Stop this video, keep all work,\nand write the reason in the status note.\n\n'
         'Time limits: AI job 3 h, render 4 h.\nA timeout counts as a failure.\n\nNothing pops up on Drew\'s screen.')
text('retry_text', PX + 30, py + 64, retry, 16, ONLIGHT)
BY['retry_zone']['height'] = round(64 + measure(retry, 16)[1] + 24, 2)

py = BY['g16']['y'] - 20
zone('learn_zone', PX, py, PW, 10, 'zone', 'solid', 1)
text('learn_title', PX + 24, py + 18, 'RECORDS AND LEARNING', 24, TITLE)
cy0 = py + 76
cyc = [('c1', PX + 30, cy0, 'Drew\'s verdict saved,\nin his words'), ('c2', PX + 390, cy0, 'Problem seen twice?\nIt becomes a rule'),
       ('c3', PX + 390, cy0 + 130, 'Every AI brief reads\nlearned-rules.md'), ('c4', PX + 30, cy0 + 130, 'Next video')]
for cid, cx_, cyy, label in cyc:
    box(cid, cx_, cyy, 300, 64, 'code' if cid != 'c4' else 'done', label, 15, 1)
arrow('c_12', [right('c1'), left('c2')], 'c1', 'c2', SLATE, 1)
arrow('c_23', [bottom('c2'), top('c3')], 'c2', 'c3', SLATE, 1)
arrow('c_34', [left('c3'), right('c4')], 'c3', 'c4', SLATE, 1)
arrow('c_41', [top('c4'), bottom('c1')], 'c4', 'c1', SLATE, 1)
link('lk_learn', 'ev_verdict', 'c1', ymid('c1'))
records = ('Per job: brief, event log, result, guard report, usage.\n'
           'Per video: ledger, delivery note, board entry,\nDesktop copy record.')
text('learn_text', PX + 30, cy0 + 230, records, 16, ONLIGHT)
BY['learn_zone']['height'] = round(cy0 + 230 + measure(records, 16)[1] + 24 - py, 2)


# ================================================================= the whole thing in plain words, far right, from the top
HX, HW = 2960, 680
HC = HX + HW / 2
NX, NW = 3720, 720          # options and what-ifs, level with each step
text('plain_title', HX, 30, 'THE WHOLE THING, IN PLAIN WORDS', 32, TITLE)
text('plain_sub', HX, 76, 'From the first search for a topic to the finished video. Think of a\n'
     'small film crew: you\'re the producer, and nothing is done until you say so.', 18, BODY)
zone('cast_zone', HX, 150, 740, 10, 'zone', 'solid', 1)
text('cast_title', HX + 24, 166, 'WHO\'S WHO', 20, TITLE)
cy2 = 206
for cid, kind, chip, desc in [('cast_you', 'drew', 'YOU', 'You choose, approve and give notes.'),
                              ('cast_pc', 'code', 'COMPUTER', 'Timing, checks, joining, copying, and the voice\nrecording. Only the voice costs money.'),
                              ('cast_ai', 'ai', 'AI CREW', 'Researcher, writer, director, animator, reviewers.\nClaude Code with Opus 5.5 for every AI role.')]:
    box(cid, HX + 24, cy2, 140, 40, kind, chip, 16)
    text(cid + '_desc', HX + 184, cy2 + 8, desc, 18, ONLIGHT)
    cy2 += max(40, measure(desc, 18)[1]) + 18
BY['cast_zone']['height'] = round(cy2 + 6 - 150, 2)
jobs = ('1  Pick the sources you like.\n2  Pick one of five hooks.\n3  Pick one of five scripts.\n'
        '4  OK the cost of the voice recording.\n5  Listen and approve the recording.\n6  Pick when the video starts.\n'
        '7  New bug only: approve its drawing.\n8  Risky runs only: watch the first piece.\n'
        '9  Watch the video: approve or give notes.\n\n'
        'At any choice you can pick, say no and why,\nor stop. Silence never counts as a yes.')
zone('side_jobs', NX, 150, NW, 10, 'drewzone', 'solid', 2)
text('side_jobs_title', NX + 24, 168, 'WHERE YOU COME IN', 20, FILL['drewzone'][1])
text('side_jobs_body', NX + 24, 206, jobs, 19, ONLIGHT)
BY['side_jobs']['height'] = round(56 + measure(jobs, 19)[1] + 24, 2)

py_ = max(ybot('cast_zone'), ybot('side_jobs')) + 50
text('part1_title', HX, py_, 'PART 1: THE STORY AND THE VOICE', 26, TITLE)
text('part1_sub', HX, py_ + 38, 'Built by the writing side, another session. Summarized here.', 15, BODY)
text('notes_title', NX, py_, 'OPTIONS AND WHAT-IFS, STEP BY STEP', 22, TITLE)
text('notes_sub', NX, py_ + 38, 'Yellow: your choices. Red: what happens if something goes wrong.', 15, BODY)
py_ += 80
prev_ = None


def note(sid, num, blocks, y):
    zid = sid + '_note'
    zone(zid, NX, y, NW, 10, 'zone', 'solid', 1)
    yy = y + 14
    for k, (head, body) in enumerate(blocks):
        text(f'{zid}_h{k}', NX + 18, yy, f'{num} · {head}', 15, FILL['drew'][1] if head == 'YOUR OPTIONS' else RED)
        yy += 15 * LH + 6
        text(f'{zid}_b{k}', NX + 18, yy, body, 16, ONLIGHT)
        yy += measure(body, 16)[1] + 12
    BY[zid]['height'] = round(yy + 2 - y, 2)
    return ybot(zid)


def plain(id, kind, title, body, notes=(), ss='solid', sw=2, gap=56):
    global py_, prev_
    stage(id, HX, py_, HW, kind, '', title, body, title_size=26, size=19, ss=ss, sw=sw)
    if prev_:
        arrow(f'pa_{prev_}_{id}', [bottom(prev_), top(id)], prev_, id, FILL[BY[prev_]['customData']['kind']][1])
    row = ybot(id)
    if notes:
        row = max(row, note(id, title.split()[0], notes, py_))
    prev_ = id
    py_ = row + gap


OPT, WHAT = 'YOUR OPTIONS', 'WHAT IF'
plain('p1', 'ai', '1  The research helper finds sources',
      'Claude gives Ultimate Crawler search words.\nCrawler uses Parallel web search for links.\nClaude picks links; crawler reads those pages.\nClaude checks them and prepares five choices.',
      [(WHAT, '• Fewer than five good sources turn up: it says so.\n  It never makes one up.\n'
              '• The research tool is down: your saved sources stay safe,\n  and it reports what\'s missing.\n'
              '• The same article shows up under another name: it\'s caught.\n'
              '• Every pest already has three saved sources: research\n  pauses until some get used.'),
       ('CURRENT SOURCES', 'Texas A&M, NPIC and EPA public articles.\n'
              'Social/video ingestion is not connected to this route.\n'
              'Search returns titles, links and snippets; page reads\n'
              'return text and access details. Claude judges the lesson.')])
plain('p2', 'drew', '2  You pick the sources you like',
      'Keep every one you like. The first one gets used;\nthe rest wait their turn for later videos.',
      [(OPT, '• Pick one or more. The first is used; the rest wait in line.\n'
             '• Say no to all, and why: five fresh ones for the same pest.\n'
             '• Save for later, or stop. Nothing runs without you.'),
       (WHAT, '• An article changed while it waited: it\'s read again.\n  Changed facts stop the writing until checked.\n'
              '• Skipping one doesn\'t count as disliking it.\n'
              '• Sources you were already shown don\'t come back next time.')])
plain('p3', 'drew', '3  You pick one of five hooks', 'The AI writes five opening lines from your\nsource, and you choose the one you like.',
      [(OPT, '• Pick one. You can save a second favourite for later.\n'
             '• Say no to all: five new hooks from the same source.\n'
             '• Change your mind about the source: back to step 2.'),
       (WHAT, '• The source is too thin for a real lesson: it stops and\n  offers a better source or a narrower lesson.')])
plain('p4', 'ai', '4  The AI checks the science', 'It researches the details your hook needs,\nso every fact in the video holds up.',
      [(WHAT, '• The facts don\'t back up your hook: it stops and asks you.\n  It never quietly rewrites your hook.\n'
              '• A source can\'t be read anymore: that fact waits until\n  it\'s backed up again.\n'
              '• A wording-only redo reuses the facts already checked.')])
plain('p5', 'drew', '5  You pick one of five scripts', 'Each starts with your hook, then tells the\nwhole lesson in natural speech.',
      [(OPT, '• Pick one.\n• Say no to all, and why: five new scripts, same hook.\n'
             '• Go back and change the hook or the source.'),
       (WHAT, '• A script needs more depth: only the missing part\n  gets researched.')])
plain('p6', 'code', '6  A voice reads it aloud',
      'Voices take turns: Tyler, then Chris, then Liam.\nIt costs money, so it needs your OK first.',
      [(OPT, '• OK the cost, or wait.\n• Try a short sample first when the voice or delivery is new.'),
       (WHAT, '• Not enough credits: it stops and asks. It never spends\n  without your OK.\n'
              '• The recording breaks midway: it never pays twice. It checks\n  the bill first.\n'
              '• The words changed since you approved them: it stops.')])
plain('p7', 'drew', '7  You listen and approve',
      'Wrong word or tone? It gets fixed and recorded\nagain. Your OK is saved with that exact file.',
      [(OPT, '• Approve.\n• A wrong word: fix just that word, then a short test.\n'
             '• Flat delivery: a short sample with the same voice.\n'
             '• Don\'t like the voice: short samples of other voices.\n'
             '• Content problem: back to the script, step 5.'),
       (WHAT, '• You can\'t find the file: it\'s copied to your Desktop.\n'
              '• Liking a voice sample isn\'t approving the full recording.')], gap=130)
rb = py_ - 130
line('part_divider', [(HX, rb + 22), (HX + HW, rb + 22)], TITLE, 2, 'dashed')
text('part2_title', HX, rb + 40, 'PART 2: THE VIDEO', 26, TITLE)
text('part2_sub', HC + 16, rb + 42, 'Designed on this canvas;\nnot built yet.', 15, BODY)
plain('p8', 'drew', '8  You pick when the video starts', 'Now, tonight at 11 PM, or later when you say go.',
      [(OPT, '• Now.\n• Tonight at 11 PM.\n• Later, when you say go.'),
       (WHAT, '• Two videos are ready to start: they go one at a time.\n'
              '• The recording changed after you approved it: the video stops.\n'
              '  Nothing is made from audio you didn\'t approve.')])
plain('p9', 'code', '9  The computer times every word', 'It finds the exact moment each word is spoken,\nso pictures and captions land right on it.',
      [(WHAT, '• The three speech models disagree on a word: that word\n  gets an extra check at the end.\n'
              '• A word can\'t be timed at all: the video stops and tells you.')])
plain('p10', 'ai', '10  The AI director plans every picture',
      'One picture for every 1 to 3 words. It cuts the video\ninto short pieces, called segments, of 6 to 15 seconds.',
      [(WHAT, '• The plan breaks a rule, like a shot over 2 seconds or a word\n'
              '  with no picture: it\'s sent back with the exact problems,\n  up to two more times.\n'
              '• The plan needs a new bug or place: step 11 comes first.')])
plain('p11', 'ai', '11  New bug? It gets drawn first',
      'Only when the video needs a new bug or place.\nThe AI draws it in the same paper style;\nyou approve it once, then every video reuses it.',
      [(OPT, '• Approve the drawing: it joins the kit for good.\n• Give notes: it gets redrawn.'),
       (WHAT, '• The anatomy is wrong: you or the checks send it back.\n'
              '• Old drawings never change, so finished videos stay the same.')], ss='dashed')
piece_top = py_
py_ += 52
plain('p12', 'ai', '12  The AI animator makes one piece', 'It draws the piece, looks at its own frames,\nfixes what\'s wrong and repeats.',
      [(WHAT, '• Claude runs out midway: save the work and wait.\n'
              '• Claude is available again: continue from the saved work.\n'
              '• It touches a file it shouldn\'t: the file is put back.\n'
              '• A piece takes over 3 hours: that counts as a failed try.\n'
              '• The computer restarts: finished pieces are kept, and it\n  picks up from the last one.')])
plain('p13', 'ai', '13  A second AI watches the piece',
      'The computer measures the motion. Then a reviewer\nAI watches it beside the fire-ant video.\nNot good enough? It goes back to step 12.',
      [(WHAT, '• A piece fails three times: the video stops and waits for\n  you, with the evidence.\n'
              '• The numbers pass but it looks bad: the reviewer can still\n  send it back.\n'
              '• The reviewer can only say no. Only you say yes.')])
plain('p14', 'drew', '14  Sometimes, you watch the first piece',
      'When there is a new bug, set or drawing.\nThe rest waits for your OK.\nNotes? That piece goes back to step 12.',
      [(OPT, '• Approve: the rest gets made.\n• Give notes: that piece is redone.\n• Stop: everything made so far is kept.')],
      ss='dashed', gap=80)
zone('piece_zone', HX - 20, piece_top, HW + 30, ybot('p14') + 24 - piece_top)
text('piece_zone_title', HX - 4, piece_top + 12, 'REPEATS FOR EVERY PIECE', 18, BODY)
plain('p15', 'code', '15  The computer joins the pieces', 'Lesson, closing thought and approved outro.\nThe same narrator speaks the whole video.\nReuse the outro animation; fit voice and captions.',
      [(WHAT, '• The render crashes: it tries once more, then stops and\n  tells you.\n'
              '• Outro and transition: approved; reuse the saved assets.\n'
              '• Music remains later work.')])
plain('p16', 'ai', '16  Final check',
      'The computer checks size, sound sync and motion.\nA reviewer AI watches the whole video.\nProblems get fixed before you see anything.',
      [(WHAT, '• Sound and picture don\'t line up, or a key frame is wrong:\n'
              '  the right part is fixed before you see anything.\n'
              '• Two pieces don\'t match where they join: they\'re redone.')])
plain('p17', 'code', '17  It lands on your Desktop', 'Named "Deep Six - <title> v1.mp4". No player\npops up. It also goes on the board.',
      [(WHAT, '• A file with that name is already there: it\'s never\n  overwritten. You get the next version number.\n'
              '• The copy doesn\'t match the original: it\'s copied again.')])
plain('p18', 'drew', '18  You watch it', 'Approve it, or say what to change.',
      [(OPT, '• Approve.\n• Give notes: only those parts are redone, and version 2\n  lands on your Desktop.\n'
             '• An unclear note: you get one multiple-choice question.\n'
             '• Outro timing: fix the join, voice or captions.\n'
             '• Music: saved for later.'),
       (WHAT, '• You don\'t answer: it waits. Silence never counts as a yes.')], sw=3)
plain('p19', 'done', '19  Approved: done',
      'The video is saved and locked. Its sources and\nscript are used up, so no later video repeats\nthem. The next recording can start.',
      [(WHAT, '• Its sources, hook and script can never start another video.\n'
              '• A problem in your notes twice becomes a rule the AI follows.')])
text('pl_approve', HC + 14, ybot('p18') + 18, 'approve', 15, ONLIGHT)
arrow('pa_loop_p13', [right('p13'), (3680, ymid('p13')), (3680, ybot('p12') - 26), right('p12', ybot('p12') - 26)],
      'p13', 'p12', RED, 2, 'dashed', kind='back')
arrow('pa_notes_p18', [right('p18'), (3700, ymid('p18')), (3700, BY['p12']['y'] + 30), right('p12', BY['p12']['y'] + 30)],
      'p18', 'p12', RED, 2, 'dashed', kind='back')

by_ = py_ + 24
for sid, kind, x, w, title, body in [
        ('side_wrong', 'warnzone', HX, HW, 'WHEN SOMETHING GOES WRONG',
         'A paid recording never repeats by itself.\n'
         'A check fails: the AI fixes it and tries\nagain, up to two more times.\n'
         'Still failing: the video stops and waits for\nyou. Nothing is lost.\n'
         'Claude runs out: save progress and wait.\nResume with Claude when available.\n'
         'It picks up where it left off; finished\npieces are kept.\nNothing ever pops up on your screen.'),
        ('side_learn', 'donezone', NX, NW, 'IT LEARNS FROM YOU',
         'Your notes and reasons are saved in your\nown words. The same problem twice becomes\na rule the AI always follows.')]:
    zone(sid, x, by_, w, 10, kind, 'solid', 2)
    text(sid + '_title', x + 24, by_ + 18, title, 20, FILL[kind][1])
    text(sid + '_body', x + 24, by_ + 56, body, 19, ONLIGHT)
    BY[sid]['height'] = round(56 + measure(body, 19)[1] + 24, 2)
line('plain_divider', [(2900, 30), (2900, ybot('side_wrong') + 20)], SLATE, 1, 'dashed')

# ================================================================= D  reference
D = max(ybot('o2'), ybot('learn_zone'), ybot('side_wrong')) + 100
band('band_d', D, 'D  REFERENCE: problems, models, files, what\'s next')
cols = [40, 750, 1460, 2170]
CWID = 670
ref = [
    ('ref_problems', 'PROBLEMS THE SELF-CHECKS CAUGHT', 'The reviewer checks every one.',
     'Hero ant close-up cluttered by other ants\n  Keep neighbours out of the close-up window.\n'
     'Mound too small; magnifier hidden by captions\n  Enlarge; key action above y 1250; props last.\n'
     'Path2D.addPath drew tunnels as one big triangle\n  Round-capped strokes; build paths by hand.\n'
     'Characters overlapping after a pull-back\n  Space them, or walk them in during the move.\n'
     'Ants upside down on slopes\n  Rotation = path angle; facing from direction.\n'
     'Empty sky in side views\n  Zoom until the subject fills the frame width.\n'
     'Motion blur made paper slides look ghostly\n  Blur only big zooms and whips.\n'
     'Brood and life cycle too small to read\n  Close-ups: items fill a third of the frame.\n'
     'A full lime loop vanished\n  An arc of exactly 2*PI draws nothing; stop short.\n'
     'Magnifier never appeared\n  Check each beat\'s named element is visible.\n'
     'Gauge overlapping the homeowner\n  Check props against characters at the beat.\n'
     'Tunnel ant above a quiet, mound-less lawn\n  Hide everything above ground when the mound is off.\n'
     'Holds went still for up to 1 s\n  Keep the camera breathing (live); push through holds.\n'
     'Drifting clouds off-screen during their shot\n  Check drifting props at the shot\'s actual time.\n'
     'Heat tint leaked into the sky\n  Clip effects to the region they describe.'),
    ('ref_models', 'PAST MODEL TESTS', 'Outside the main flow; future prompting research.',
     'MODEL        TIME   SHOTS  STILL   CHANGE  DREW\n'
     'Opus 5.5     n/a    13     0.33 s  17%     approved\n'
     'GPT-6 Astra  9 min  15     0 s     22%     "super bad"\n'
     'GPT-6 Sol    8 min  9      0 s     16%     "not bad"\n'
     '(Opus figures are for the whole approved video.)\n\n'
     'Astra invented compositions that failed in motion:\n'
     'brood in midair over an empty wall, a jumpy camera,\nnear-static weather shots.\n'
     'Sol stayed in the proven nest set and read clearly.\n'
     'Automatic checks passed both.\n\n'
     'Agent mode (shell plus image viewer) beat one-shot\nruns, which gave the rejected single scene.\n\n'
     'A segment job: 2 to 4 million input tokens, mostly\ncached, and 15,000 to 25,000 output tokens.\n'
     'Astra and Sol share one ChatGPT Codex usage limit;\nthe tests used it up on 19 Oct (back that evening).\n\n'
     'GPT-6.1 Sol: not available to Codex on Drew\'s\nChatGPT account.\n'
     'claude -p works on Drew\'s Claude plan; never use\n--bare, which switches to API billing.\n'
     'Sonnet backup: wired and probed once, opt-in only.\n\n'
     'Prompting guides: OpenAI\'s Codex prompting and\nbest-practice pages. Third-party GPT-6 notes are\nunverified.'),
    ('ref_files', 'BUILDING BLOCKS AND FILES', 'In 01-content/animation/',
     'VIDEO-FLOW.md          the recipe and quality bar\n'
     'HARNESS-NOTES.md       what worked; requirements\n'
     'KIT-API.md             what the kit and sets draw\n'
     'choreography/          director and animator prompts\n'
     'scenes/\n'
     '  paper-kit.mjs        paper pieces, fire-ant worker,\n'
     '                       brood, captions, camera, effects\n'
     '  nest-world.mjs       nest cutaway: weather, water,\n'
     '                       heat, brood, ants\n'
     '  yard-world.mjs       yard, homeowner, magnifier,\n'
     '                       gauge, pushpin, X, question mark\n'
     '  hook, body and full  the approved video\'s modules\n'
     'render-shots.mjs       --sheet, --at, --check-motion,\n'
     '                       full MP4 render\n'
     'tools/align_words.py   word timing, 3 local models\n'
     'make_video.py          runner: prepare, full, segment,\n'
     '                       render, deliver\n'
     'science-notes.md       anatomy and science limits\n'
     'brand.json             the Deep Six palette\n'
     'episodes/D6-6c917b49743b/\n'
     '  full/                approved v2 and its records\n'
     '  hook/                approved hook v1\n'
     '  model-test/          Opus, Sol and Astra tests\n'
     '  runs/astra-ending/   Astra\'s half-done full run\n\n'
     'Times everywhere are seconds from the start of\nthe approved MP3.'),
    ('ref_next', 'NOW, LATER, OPEN', 'State on 19 Oct 2026.',
     'NOW\n'
     'Fire-ant video done; its style is the standard.\n'
     'Today\'s runner works when started by hand:\n'
     '  make_video.py prepare, then full.\n'
     'Opus through the runner: probed, not yet run on a\n'
     'full job. The approved video was made directly.\n\n'
     'OUTRO STATUS\n'
     'Outro and fire-ant closing: approved, complete.\n'
     'Final fire-ant video: 88.10 s, approved by Drew.\n\n'
     'LATER PIECES (not built)\n'
     'Wire reusable outro into the future automatic runner.\n'
     'Music.\n'
     'New pests need researched drawings first, such\n'
     'as a cockroach and a kitchen set.\n\n'
     'DREW DECIDED, 19 OCT\n'
     'Pilot clip only on risky runs.\n'
     'Drew picks now, tonight or later when each\nMP3 is approved.\n\n'
     'OPEN, FOR DREW\n'
     'Usage across many videos on the Claude plan.\n\n'
     'DECIDED IN THIS DESIGN\n'
     'Claude Code with Opus 5.5 for every AI role.\n'
     'Astra/Sol prompting research: separate, later.\n'
     'Ideas adopted: show the target, proven shot types,\n'
     'watch then judge, pilot when risky, learn from\n'
     'verdicts. Not adopted: best of two (double usage;\n'
     'Astra was "super bad").\n\n'
     'STILL UNKNOWN\n'
     'Whether GPT-6.1 Sol becomes reachable.\n'
     'Whether Astra at ultra beats xhigh.\n'
     'Word times are machine-aligned, not checked by ear.'),
]
for k, (rid, title, sub, body) in enumerate(ref):
    x = cols[k]
    zone(rid + '_zone', x, D + 90, CWID, 10, 'zone', 'solid', 1)
    text(rid + '_title', x + 24, D + 108, title, 22, TITLE)
    text(rid + '_sub', x + 24, D + 142, sub, 15, BODY)
    text(rid + '_body', x + 24, D + 178, body, 14, ONLIGHT)
height = max(178 + measure(body, 14)[1] + 28 for (_, _, _, body) in ref)
for rid, *_ in ref:
    BY[rid + '_zone']['height'] = round(height, 2)

# Refinement beside the existing flows. These are design decisions, not implemented automation.
FX, FW, FC = 4620, 760, 5000
SX, SW = 5620, 820
text('research_design_title', FX, 30, 'RESEARCH: START TO CHECKED EVIDENCE', 32, TITLE)
text('research_design_sub', FX, 84,
     '20 Oct: refine and prove this flow first. This section ends before narration writing.\n'
     'Claude Code / Opus 5.5 directs the research; Ultimate Crawler searches and reads.', 18, BODY)
stage('rd_start', FX, 170, FW, 'input', '', '1  Start or resume the episode',
      'Continue an unfinished episode at its saved step.\n'
      'Only a new episode starts the pest-selection route.')
stage('rd_pest', FX, 390, FW, 'code', '', '2  Choose the next episode pest',
      'Use the episode pest rotation unless Drew chooses another.\n'
      'Research stocking has its own order; keep the two separate.')
arrow('rd_a_start_pest', [bottom('rd_start'), top('rd_pest')], 'rd_start', 'rd_pest')
diamond('rd_queue', FC, 720, 460, 220, 'branch', 'Liked, unused source\nfor this pest?', 18)
arrow('rd_a_pest_queue', [bottom('rd_pest'), top('rd_queue')], 'rd_pest', 'rd_queue')
stage('rd_saved', FX, 940, FW, 'code', '', '3A  Use that pest\'s saved source',
      'Pick its next liked article; recheck access and facts.\n'
      'Keep the other liked articles for the next visits to this pest.')
arrow('rd_a_queue_saved', [bottom('rd_queue'), top('rd_saved')], 'rd_queue', 'rd_saved')
text('rd_yes', FC + 14, 870, 'yes: use the saved shelf', 15, ONLIGHT)
stage('rd_search', SX, 640, SW, 'ai', '', '3B  Find new sources when needed',
      'Claude sends the pest, audience, exclusions and search words.\n'
      'Ultimate Crawler uses Parallel search: titles, links, excerpts.\n'
      'Use search history to choose a different promising route.\n'
      'Change questions, species terms, publishers or cited studies.')
arrow('rd_a_queue_search', [right('rd_queue'), (5520, 720), (5520, ymid('rd_search')),
                           left('rd_search')], 'rd_queue', 'rd_search')
text('rd_no', 5400, 678, 'no', 15, ONLIGHT)
text('rd_fresh', SX, 580, 'Also available when Drew explicitly asks for fresh choices.', 15, BODY)
stage('rd_read', SX, 910, SW, 'ai', '', '4  Read, check and compare lessons',
      'Claude chooses pages; crawler returns their original text.\n'
      'Check facts, species, Texas relevance, depth and duplicate use.\n'
      'Reject copied lessons and claims the evidence does not support.\n'
      'Keep valid candidates between searches; do not restart from zero.')
arrow('rd_a_search_read', [bottom('rd_search'), top('rd_read')], 'rd_search', 'rd_read')
stage('rd_review', SX, 1190, SW, 'drew', '', '5  Drew reviews short source previews',
      'Aim for five strong choices; explain any shortage honestly.\n'
      'Save every liked source under this pest. Pick one for now.\n'
      'Reject all is enough: Claude chooses a different search route.\n'
      'No explanation required; do not ask Drew to diagnose the batch.')
arrow('rd_a_read_review', [bottom('rd_read'), top('rd_review')], 'rd_read', 'rd_review')
stage('rd_selected', FX, 1210, FW, 'code', '', '6  Reserve the selected article',
      'One main article belongs to this episode.\n'
      'Its other liked sources stay queued for this pest.')
arrow('rd_a_saved_selected', [bottom('rd_saved'), top('rd_selected')], 'rd_saved', 'rd_selected')
arrow('rd_a_review_selected', [left('rd_review', ymid('rd_selected')), right('rd_selected')],
      'rd_review', 'rd_selected', FILL['drew'][1])
arrow('rd_reject_loop', [right('rd_review'), (6540, ymid('rd_review')),
                         (6540, ymid('rd_search')), right('rd_search')],
      'rd_review', 'rd_search', RED, 2, 'dashed', kind='back')
text('rd_reject_label', 6580, 880,
     'Reject all:\nkeep the pest,\nrecord the choice,\nchange the route.\n\nClaude decides how.\nNo explanation\nneeded from Drew.\nKeep search history.', 16, RED)
stage('rd_hook', FX, 1480, FW, 'drew', '', '7  Choose the hook',
      'Five hooks from the chosen article\'s supported lesson.\n'
      'Drew picks one. Keep the chosen words and promise.')
arrow('rd_a_selected_hook', [bottom('rd_selected'), top('rd_hook')], 'rd_selected', 'rd_hook')
stage('rd_support', FX, 1720, FW, 'ai', '', '8  Second crawler pass: explain the hook',
      'Send the exact hook, checked facts and unanswered questions.\n'
      'Find supporting science for how, why and useful limits.\n'
      'Keep the same episode, pest, main source and chosen hook.\n'
      'On retries, reuse adequate evidence; research only real gaps.')
arrow('rd_a_hook_support', [bottom('rd_hook'), top('rd_support')], 'rd_hook', 'rd_support')
stage('rd_packet', FX, 2010, FW, 'code', '', '9  Pass checked evidence to narration',
      'Chosen hook, main source, supporting facts and limits.\n'
      'Every essential claim has support; note what remains uncertain.\n'
      'Contradiction or missing proof: return to research or hook choice.\n'
      'A changed hook needs Drew\'s approval before writing.')
arrow('rd_a_support_packet', [bottom('rd_support'), top('rd_packet')], 'rd_support', 'rd_packet')
ellipse('rd_end', FC, 2350, 520, 140, 'done', 'Ready for narration writing\nThis section ends here.', 18)
arrow('rd_a_packet_end', [bottom('rd_packet'), top('rd_end')], 'rd_packet', 'rd_end')
stage('rd_history', SX, 1550, SW, 'code', '', 'ONE SOURCE HISTORY, SEPARATE STATES',
      'Shown / rejected / liked and queued / reserved / used.\n'
      'Compare links, publisher + title and matching page text.\n'
      'Unchosen is not disliked or permanently used.\n'
      'Same-episode edits can keep their evidence.\n'
      'A finished episode consumes main and supporting publications.\n'
      'Keep lesson history too: a new article can repeat an old lesson.')
stage('rd_broader', SX, 1900, SW, 'later', '', 'PROPOSED: broader discovery sources',
      'Search beyond a fixed list; admit sources by checked evidence.\n'
      'UF/IFAS, UC IPM, Mississippi State, Oklahoma State, USDA ARS.\n'
      'Follow useful studies, their authors and their original references.\n'
      'Expert articles/videos: verify author, content and factual support.\n'
      'Social questions can suggest topics; they do not prove facts.', ss='dashed')
stage('rd_status', SX, 2250, SW, 'later', '', 'WHAT EXISTS / WHAT STILL NEEDS BUILDING',
      'Built: saved sources by pest, duplicate checks, rejection feedback,\n'
      'and a separate crawler request after hook selection.\n'
      'Still needed: episode rotation and the research rules below.\n'
      'Proposed: wider discovery and persistent partial batches.\n'
      'Current importer stops unless exactly five pass.', ss='dashed')

# Explicit failure routes keep the overview legible; detailed rules sit below it.
arrow('rd_hook_retry', [left('rd_hook'), (4520, ymid('rd_hook')),
                        (4520, BY['rd_hook']['y'] - 45), top('rd_hook')],
      'rd_hook', 'rd_hook', RED, 2, 'dashed', kind='back')
text('rd_hook_retry_label', FX, 1420, 'Reject hooks: new openings, same source.', 15, RED)
arrow('rd_evidence_revisit', [left('rd_packet'), (4550, ymid('rd_packet')),
                             (4550, ymid('rd_support')), left('rd_support')],
      'rd_packet', 'rd_support', RED, 2, 'dashed', kind='back')
text('rd_rules_title', FX, 2580, 'RESEARCH RULES TO ADD AND PROVE', 26, TITLE)
text('rd_rules_sub', FX, 2628,
     'Proposed safeguards. Existing code covers parts of these; the complete loop needs a real trial.', 17, BODY)
stage('rd_adapt', FX, 2700, FW, 'later', '', 'A  Claude chooses the next search strategy',
      'Drew can reject with no explanation. Claude changes approach.\n'
      'Use search history, source quality and variety to choose how.\n'
      'Try new questions, mechanisms, species, authors or publishers.\n'
      'Use past likes as clues, without inventing a rejection reason.\n'
      'Judge the next results; do not repeat the same failed batch.', ss='dashed')
stage('rd_memory', SX, 2700, SW, 'later', '', 'B  Keep a research memory for each pest',
      'Save queries, publications, dates, useful leads and failure reasons.\n'
      'Carry good unfinished candidates into the next search batch.\n'
      'Revisit promising authors and publications as the queue needs stock.\n'
      'Old but unused evidence can still support a new lesson.\n'
      'Keep source approval separate from discovering a candidate.', ss='dashed')
stage('rd_scarcity', FX, 3030, FW, 'later', '', 'C  Handle shortages without weak filler',
      'A search outage is different from finding no good sources.\n'
      'Unreadable page: try its original accessible version.\n'
      'Keep good results; widen the next bounded search when useful.\n'
      'No progress: report the gap; offer fewer choices or pause.\n'
      'Keep quality and no-reuse rules. Fresh sources are not endless.', ss='dashed')
stage('rd_facts', SX, 3030, SW, 'later', '', 'D  Check meaning and independence',
      'A matching quote does not prove the claim drawn from it.\n'
      'Check that each fact supports the hook or explanation.\n'
      'Five sites copying one study are one evidence origin.\n'
      'Keep species, location, dates and uncertainties attached.\n'
      'Do not choose only evidence that agrees with the hook.', ss='dashed')
stage('rd_recovery', FX, 3360, FW, 'later', '', 'E  Handle stale sources and changed choices',
      'Changed or unreadable saved source: hold it for recheck.\n'
      'Do not erase the other liked sources or restart the whole queue.\n'
      'Changed pest/source/hook: invalidate dependent work only.\n'
      'Late results for the old choice must not enter the new episode.\n'
      'Resume saved work after interruption; check active reservations.', ss='dashed')
stage('rd_ready', SX, 3360, SW, 'later', '', 'F  Define evidence ready to write',
      'The chosen hook and its main source agree.\n'
      'Necessary how/why questions have supported answers.\n'
      'Every planned factual claim has a checked source and limits.\n'
      'No unresolved contradiction essential to the lesson remains.\n'
      'Pass this package to writing; narration review comes after drafts.', ss='dashed')

# zones render underneath everything else
ELS.sort(key=lambda e: 0 if (e.get('customData') or {}).get('kind') == 'zone' else 1)


# ================================================================= checks
def bbox(e):
    if e['type'] in ('arrow', 'line'):
        pts = abs_points(e)
        return (min(p[0] for p in pts), min(p[1] for p in pts), max(p[0] for p in pts), max(p[1] for p in pts))
    return (e['x'], e['y'], e['x'] + e['width'], e['y'] + e['height'])


def inner(e):
    x0, y0, x1, y1 = bbox(e)
    w, h = e['width'], e['height']
    if e['type'] == 'diamond':
        return (x0 + w / 4 + 5, y0 + h / 4 + 5, x1 - w / 4 - 5, y1 - h / 4 - 5)
    if e['type'] == 'ellipse':
        k = (1 - 1 / math.sqrt(2)) / 2
        return (x0 + w * k + 5, y0 + h * k + 5, x1 - w * k - 5, y1 - h * k - 5)
    return (x0 + 5, y0 + 5, x1 - 5, y1 - 5)


def within(a, b, tol=0.6):
    return a[0] >= b[0] - tol and a[1] >= b[1] - tol and a[2] <= b[2] + tol and a[3] <= b[3] + tol


def overlap(a, b, m=0.0):
    return a[0] < b[2] + m and b[0] < a[2] + m and a[1] < b[3] + m and b[1] < a[3] + m


def seg_hits(p, q, b, shrink=1.0):
    """Liang-Barsky: does segment p-q pass through box b (shrunk slightly)?"""
    x0, y0, x1, y1 = b[0] + shrink, b[1] + shrink, b[2] - shrink, b[3] - shrink
    dx, dy = q[0] - p[0], q[1] - p[1]
    t0, t1 = 0.0, 1.0
    for pp, qq in ((-dx, p[0] - x0), (dx, x1 - p[0]), (-dy, p[1] - y0), (dy, y1 - p[1])):
        if pp == 0:
            if qq < 0:
                return False
        else:
            t = qq / pp
            if pp < 0:
                t0 = max(t0, t)
            else:
                t1 = min(t1, t)
    return t0 < t1


def abs_points(e):
    return [(e['x'] + px, e['y'] + py) for px, py in e['points']]


def boundary_distance(pt, e):
    x, y = pt
    x0, y0, x1, y1 = bbox(e)
    cx, cy, w, h = (x0 + x1) / 2, (y0 + y1) / 2, e['width'], e['height']
    if e['type'] == 'diamond':
        v = abs(x - cx) / (w / 2) + abs(y - cy) / (h / 2)
        return abs(v - 1) * min(w, h) / 2
    if e['type'] == 'ellipse':
        v = math.hypot((x - cx) / (w / 2), (y - cy) / (h / 2))
        return abs(v - 1) * min(w, h) / 2
    dx = max(x0 - x, 0, x - x1)
    dy = max(y0 - y, 0, y - y1)
    if dx or dy:
        return math.hypot(dx, dy)
    return min(x - x0, x1 - x, y - y0, y1 - y)


errors, warnings = [], []
ids = [e['id'] for e in ELS]
if len(ids) != len(set(ids)):
    errors.append('duplicate ids')
shapes = [e for e in ELS if e['type'] in ('rectangle', 'diamond', 'ellipse', 'image')]
zones = [e for e in shapes if (e.get('customData') or {}).get('kind') == 'zone']
solids = [e for e in shapes if e not in zones]
texts = [e for e in ELS if e['type'] == 'text']
free = [t for t in texts if not t['containerId']]
arrows = [e for e in ELS if e['type'] == 'arrow']

for e in ELS:   # two-way bindings
    for ref_ in e.get('boundElements') or []:
        other = BY.get(ref_['id'])
        if not other:
            errors.append(f'{e["id"]} lists missing {ref_["id"]}')
        elif ref_['type'] == 'text' and other.get('containerId') != e['id']:
            errors.append(f'{ref_["id"]} does not point back to {e["id"]}')
        elif ref_['type'] == 'arrow' and e['id'] not in ((other.get('startBinding') or {}).get('elementId'),
                                                          (other.get('endBinding') or {}).get('elementId')):
            errors.append(f'{ref_["id"]} does not bind back to {e["id"]}')
for e in ELS:
    if e['type'] == 'image' and e['fileId'] not in FILES:
        errors.append(f'{e["id"]}: picture data missing')
for t in texts:
    if t['containerId']:
        c = BY.get(t['containerId'])
        if not c or {'id': t['id'], 'type': 'text'} not in (c.get('boundElements') or []):
            errors.append(f'{t["id"]}: container missing or not reciprocal')
        elif not within(bbox(t), inner(c)):
            errors.append(f'{t["id"]}: text does not fit inside {c["id"]}')
    w, h = measure(t['text'], t['fontSize'])
    if t['width'] + 0.01 < w or t['height'] + 0.01 < h:
        errors.append(f'{t["id"]}: declared size smaller than its text')
for t in free:   # free text inside its own box, clear of every other box, picture and text
    host = (t.get('customData') or {}).get('inside')
    if host:
        hx0, hy0, hx1, hy1 = bbox(BY[host])
        if not within(bbox(t), (hx0 + 8, hy0 + 8, hx1 - 8, hy1 - 8)):
            errors.append(f'{t["id"]}: spills out of {host}')
    for s in solids:
        if s['id'] != host and overlap(bbox(t), bbox(s), 4):
            errors.append(f'{t["id"]} overlaps {s["id"]}')
    for z in zones:
        if overlap(bbox(t), bbox(z)) and not within(bbox(t), bbox(z), -6):
            errors.append(f'{t["id"]} straddles zone {z["id"]}')
for i, a in enumerate(free):
    for b in free[i + 1:]:
        if overlap(bbox(a), bbox(b), 3):
            errors.append(f'texts overlap: {a["id"]} / {b["id"]}')
for i, a in enumerate(solids):
    for b in solids[i + 1:]:
        if overlap(bbox(a), bbox(b), 10):
            errors.append(f'shapes too close or overlapping: {a["id"]} / {b["id"]}')
for z in zones:
    for s in solids:
        if overlap(bbox(s), bbox(z)) and not within(bbox(s), bbox(z), -8):
            errors.append(f'shape {s["id"]} straddles zone {z["id"]}')
segments = []
for a in arrows:
    pts = abs_points(a)
    ends = {(a.get('startBinding') or {}).get('elementId'), (a.get('endBinding') or {}).get('elementId')} - {None}
    for key, pt in (('startBinding', pts[0]), ('endBinding', pts[-1])):
        b = a.get(key)
        if b and boundary_distance(pt, BY[b['elementId']]) > 8:
            errors.append(f'{a["id"]}: {key} end is {boundary_distance(pt, BY[b["elementId"]]):.0f}px from {b["elementId"]}')
    for p, q in zip(pts, pts[1:]):
        segments.append((a['id'], p, q))
        for s in solids:
            if s['id'] not in ends and seg_hits(p, q, bbox(s)):
                errors.append(f'{a["id"]} crosses {s["id"]}')
        for t in free:
            if seg_hits(p, q, bbox(t), -2):
                errors.append(f'{a["id"]} crosses text {t["id"]}')
for i, (ida, p1, q1) in enumerate(segments):   # crossings between connectors
    for idb, p2, q2 in segments[i + 1:]:
        if ida == idb:
            continue
        h1, h2 = p1[1] == q1[1], p2[1] == q2[1]
        if h1 != h2:
            hp, hq, vp, vq = (p1, q1, p2, q2) if h1 else (p2, q2, p1, q1)
            x, y = vp[0], hp[1]
            if min(hp[0], hq[0]) < x < max(hp[0], hq[0]) and min(vp[1], vq[1]) < y < max(vp[1], vq[1]):
                warnings.append(f'connectors cross: {ida} / {idb} at ({x:.0f}, {y:.0f})')

boxes = [bbox(e) for e in ELS]
report = {
    'drawing': OUT.name, 'elements': len(ELS), 'shapes': len(solids), 'pictures': len(FILES), 'zones': len(zones),
    'texts': len(texts), 'arrows': len(arrows),
    'canvas': [round(min(b[0] for b in boxes)), round(min(b[1] for b in boxes)),
               round(max(b[2] for b in boxes)), round(max(b[3] for b in boxes))],
    'checks': ['unique ids', 'two-way bindings', 'picture data present', 'bound text fits its shape',
               'free text inside its own box', 'no text, picture or shape overlaps',
               'arrows miss shapes, pictures and text they do not connect', 'arrow ends on their shapes',
               'connector crossings listed'],
    'errors': errors, 'warnings': warnings, 'screenshots': 'none (Drew\'s rule)',
}

scene = {'type': 'excalidraw', 'version': 2, 'source': 'https://excalidraw.com', 'elements': ELS,
         'appState': {'viewBackgroundColor': '#ffffff', 'gridSize': 20}, 'files': FILES}
fd, tmp = tempfile.mkstemp(dir=HERE, prefix='.tmp-', suffix='.excalidraw')
with os.fdopen(fd, 'w') as f:
    json.dump(scene, f, indent=1)
json.loads(Path(tmp).read_text())
os.chmod(tmp, 0o644)
os.replace(tmp, OUT)
CHECKS.write_text(json.dumps(report, indent=1) + '\n')
print(json.dumps({k: report[k] for k in ('elements', 'shapes', 'pictures', 'texts', 'arrows', 'canvas')}))
print(f'{len(errors)} errors, {len(warnings)} warnings')
for e in errors + warnings:
    print(' -', e)
sys.exit(1 if errors else 0)
