"""Render layout sketches and silent timing previews from existing artwork only."""
import base64
import hashlib
import html
import json
from pathlib import Path
import shutil
import subprocess
import textwrap

import cairosvg

ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
MASCOT = ROOT / '01-content/outro/assets/hybrid-still-v1.jpg'
BRAND = ROOT / '01-content/brand/fun-fact-friday-spider.png'
FONT = '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
CHOICES = [
    {'id': 1, 'title': 'Simple brand credit', 'seconds': 5,
     'spoken': 'Brought to you by Deep Six Pest Control.',
     'screen': ['Brought to you by'],
     'action': 'Small friendly nod; hold the logo.'},
    {'id': 2, 'title': 'Educational sign-off', 'seconds': 5,
     'spoken': 'Helping you understand pests. Deep Six Pest Control.',
     'screen': ['Helping you', 'understand pests.'],
     'action': 'Paper wipe, then one small nod.'},
    {'id': 3, 'title': 'A closer look', 'seconds': 6,
     'spoken': 'A closer look at pests, from Deep Six Pest Control.',
     'screen': ['A closer look at pests'],
     'action': 'A soft flashlight sweep across the logo.'},
]


def data_uri(path, mime):
    return 'data:' + mime + ';base64,' + base64.b64encode(path.read_bytes()).decode()


mascot_uri = data_uri(MASCOT, 'image/jpeg')
brand_uri = data_uri(BRAND, 'image/png')


def text(x, y, content, size=25, color='#3A3148', weight=600, anchor='middle'):
    return f'<text x="{x}" y="{y}" font-family="DejaVu Sans,sans-serif" font-size="{size}" font-weight="{weight}" fill="{color}" text-anchor="{anchor}">{html.escape(content)}</text>'


def scene(choice):
    # SVG viewports display unchanged source pixels; these are layout sketches.
    # The actual logo is a crop from the supplied ad, not a new wordmark.
    parts = [f'<image href="{mascot_uri}" x="0" y="0" width="540" height="960" preserveAspectRatio="xMidYMid slice"/>']
    parts.append('<rect x="28" y="28" width="484" height="40" rx="8" fill="#3A3148"/>')
    parts.append(text(270,55,f"OPTION {choice['id']}  |  {choice['seconds']} seconds",17,'#F6EFE2'))
    if choice['id'] == 1:
        parts.append(text(270,132,choice['screen'][0],26))
        logo_y = 166
    elif choice['id'] == 2:
        logo_y = 117
        parts.extend([text(270,362,choice['screen'][0],29), text(270,400,choice['screen'][1],29)])
    else:
        parts.append(text(270,137,choice['screen'][0],27))
        logo_y = 180
        parts.append('<path d="M 114 157 L 426 157" stroke="#A9D554" stroke-width="7" stroke-linecap="round"/>')
    parts.append(f'<svg x="85" y="{logo_y}" width="370" height="205" viewBox="180 25 470 260" overflow="hidden"><image href="{brand_uri}" x="0" y="0" width="1254" height="1254"/></svg>')
    parts.append('<rect x="28" y="878" width="484" height="63" rx="9" fill="#F6EFE2" fill-opacity="0.96"/>')
    parts.append(text(270,902,'SILENT LAYOUT SKETCH',15))
    parts.append(text(270,924,'Draft mascot + original logo crop',13,weight=400))
    return ''.join(parts)


def svg_document(content, width, height):
    return f'<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="{width}" height="{height}" viewBox="0 0 {width} {height}">{content}</svg>'


def run(args):
    result = subprocess.run(args, capture_output=True, text=True)
    if result.returncode:
        raise RuntimeError(result.stderr[-1800:])


for choice in CHOICES:
    stem = f"option-{choice['id']:02d}-v1"
    doc = svg_document(scene(choice), 540, 960)
    svg = HERE / (stem + '.svg')
    png = HERE / (stem + '.png')
    mp4 = HERE / (stem + '.mp4')
    if mp4.exists():
        raise SystemExit('Versioned preview already exists; no overwrite performed.')
    svg.write_text(doc)
    cairosvg.svg2png(bytestring=doc.encode(), write_to=str(png))
    filters = 'fade=t=in:st=0:d=0.25:color=0xF6EFE2,format=yuv420p'
    run(['ffmpeg','-hide_banner','-loglevel','error','-n','-loop','1','-framerate','30','-i',str(png),
         '-vf',filters,'-t',str(choice['seconds']),'-an','-c:v','libx264','-preset','fast','-crf','19','-pix_fmt','yuv420p',
         '-movflags','+faststart',str(mp4)])
    choice['preview'] = str(mp4.relative_to(ROOT))
    print('Rendered ' + mp4.name, flush=True)

# One exported comparison graphic. This is a native SVG layout, not an AI image.
board = ['<rect width="1260" height="1110" fill="#F6EFE2"/>',
         text(48,52,'Three ways to end a Deep Six lesson',32,anchor='start'),
         text(48,87,'Same brand. Different wording and feel. Silent sketches, with draft artwork.',18,weight=400,anchor='start')]
for index, choice in enumerate(CHOICES):
    x = 48 + index * 405
    board.append(text(x,133,f"{choice['id']}. {choice['title']}",23,anchor='start'))
    board.append(f'<g transform="translate({x},154) scale(0.67)">{scene(choice)}</g>')
    board.append(text(x,835,'NARRATOR SAYS',14,weight=700,anchor='start'))
    for n, line in enumerate(textwrap.wrap(choice['spoken'], 31)):
        board.append(text(x,866+n*28,line,20,weight=500,anchor='start'))
    for n, line in enumerate(textwrap.wrap(choice['action'], 34)):
        board.append(text(x,978+n*24,line,16,weight=400,anchor='start'))
board.append(text(48,1072,'The finished version will use corrected mascot art, a clean original logo, voice and subtle animation.',16,weight=400,anchor='start'))
comparison = svg_document(''.join(board),1260,1110)
(HERE/'outro-options-v1.svg').write_text(comparison)
cairosvg.svg2png(bytestring=comparison.encode(),write_to=str(HERE/'outro-options-v1.png'))

concat = HERE/'options-v1.concat.txt'
concat.write_text(''.join("file '" + f"option-{c['id']:02d}-v1.mp4" + "'\n" for c in CHOICES))
combined = HERE/'outro-options-v1.mp4'
run(['ffmpeg','-hide_banner','-loglevel','error','-n','-f','concat','-safe','0','-i',str(concat),
     '-c','copy','-movflags','+faststart',str(combined)])

desktop = Path('/mnt/c/Users/drewp/Desktop')
copy = desktop/'Deep Six - Outro Options v1.mp4'
if desktop.is_dir():
    if copy.exists():
        raise SystemExit('Desktop copy already exists; no overwrite performed.')
    shutil.copy2(combined,copy)

manifest = {'type':'silent_layout_and_pacing_sketches','ai_generation_calls':0,'additional_spend_usd':0,
            'mascot_status':'Existing unapproved draft reused as a placeholder; no character animation rendered',
            'logo_status':'Unchanged pixels displayed from original ad crop; clean logo preparation pending',
            'voice_status':'Exact spoken copy displayed as text; no synthesized audio',
            'choices':CHOICES,'comparison_graphic':'01-content/outro/previews/outro-options-v1.png',
            'combined_preview':str(combined.relative_to(ROOT)),
            'desktop_copy':str(copy) if copy.exists() else None,
            'source_hashes':{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in [MASCOT,BRAND]},
            'player_opened':False,'browser_opened':False}
(HERE/'options-v1.json').write_text(json.dumps(manifest,indent=2)+'\n')
print(json.dumps({'combined':str(combined.relative_to(ROOT)),'desktop_copy':manifest['desktop_copy'],'additional_spend_usd':0}))
