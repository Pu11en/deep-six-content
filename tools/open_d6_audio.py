"""Open a self-contained comparison player on Drew's Windows desktop from WSL."""
import argparse
import base64
import html
import json
from pathlib import Path
import shutil
import subprocess

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('comparison', type=Path)
parser.add_argument('--focus-only', action='store_true')
args = parser.parse_args()
folder = args.comparison.resolve().parent
spec = json.loads(args.comparison.read_text())
window_title = spec.get('player_title', 'D6 Audio Review')
cards = []
for variant in spec['variants']:
    path = folder / variant['audio_file']
    if variant['status'] != 'complete' or not path.is_file():
        raise SystemExit('All requested MP3s must be complete before opening the player.')
    encoded = base64.b64encode(path.read_bytes()).decode('ascii')
    original = variant['name'] == 'original'
    title = html.escape(variant.get('label', 'Original narration' if original else 'Refined for AI voice'))
    detail = html.escape(variant.get('description', 'Exactly the script you chose.' if original else 'Same hook and facts. Wording adjusted for speech.'))
    seconds = round(variant['duration_seconds'])
    duration = f'{seconds//60}:{seconds%60:02d}'
    cards.append(f'<section><h2>{title}</h2><p>{detail}</p><p class="time">{duration}</p>'
                 f'<audio controls preload="metadata" aria-label="{title}" src="data:audio/mpeg;base64,{encoded}"></audio></section>')
page = '''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>D6 Audio Review</title><style>
body{font-family:system-ui,sans-serif;background:#f2f4f7;color:#17212b;margin:0;padding:36px 24px}
main{max-width:850px;margin:auto}h1{font-size:30px;margin-bottom:8px}.intro{color:#465565;line-height:1.6}
section{background:white;padding:24px;border-radius:14px;border:1px solid #dce2e8;margin:20px 0}
h2{margin-top:0;font-size:22px}p{line-height:1.5}.time{color:#465565}audio{display:block;width:100%;margin-top:18px}
footer{color:#465565;font-size:14px}button{padding:10px 16px;font:inherit;border:1px solid #bbc5cf;background:white;border-radius:8px;cursor:pointer}
</style><main><h1>D6 Audio Review</h1><p class="intro">Narration 2: how fire ants move their developing young.<br>Press the triangular Play button below each version.</p>'''
page = page.replace('D6 Audio Review', html.escape(window_title))
page = page.replace('Narration 2: how fire ants move their developing young.', html.escape(spec.get('player_intro', 'Narration 2: how fire ants move their developing young.')))
page += ''.join(cards)
page += '<button id="stop">Pause audio</button><footer><p>Voice: '+html.escape(spec.get('player_footer', spec['voice_name']+'. Same voice and settings for both versions.'))+'<br>Return to Zed and tell me which version you prefer.</p></footer></main>'
page += '''<script>const players=[...document.querySelectorAll('audio')];players.forEach(p=>p.addEventListener('play',()=>players.forEach(other=>{if(other!==p)other.pause()})));document.querySelector('#stop').onclick=()=>players.forEach(p=>p.pause());</script></html>'''
player = folder/'listen.html'
player.write_text(page)
source = subprocess.check_output(['wslpath','-w',str(player)],text=True).strip()
params = json.dumps({'source':source,'run':spec.get('comparison_id',spec['approved_narration_id']),'title':window_title,'focus_only':args.focus_only})
script = r'''
$ErrorActionPreference='Stop'
$p=__PARAMS__ | ConvertFrom-Json
$folder=Join-Path ([System.IO.Path]::GetTempPath()) ('D6Audio-' + $p.run)
New-Item -ItemType Directory -Force -Path $folder | Out-Null
$target=Join-Path $folder 'listen.html'
Copy-Item -LiteralPath $p.source -Destination $target -Force
$url=([System.Uri]$target).AbsoluteUri
$edge=@((Join-Path ${env:ProgramFiles(x86)} 'Microsoft\Edge\Application\msedge.exe'),(Join-Path $env:ProgramFiles 'Microsoft\Edge\Application\msedge.exe')) | Where-Object {Test-Path $_} | Select-Object -First 1
if (-not $edge) {throw 'Microsoft Edge executable not found.'}
if(-not $p.focus_only) {Start-Process -FilePath $edge -ArgumentList @('--new-window',('--app='+$url))}
Add-Type @'
using System;
using System.Text;
using System.Runtime.InteropServices;
public class D6PlayerWindow {
 public delegate bool Callback(IntPtr w,IntPtr p);
 [DllImport("user32.dll")] public static extern bool EnumWindows(Callback cb,IntPtr p);
 [DllImport("user32.dll")] public static extern bool IsWindowVisible(IntPtr w);
 [DllImport("user32.dll",CharSet=CharSet.Unicode)] public static extern int GetWindowText(IntPtr w,StringBuilder s,int n);
 [DllImport("user32.dll")] public static extern bool SetForegroundWindow(IntPtr w);
 [DllImport("user32.dll")] public static extern bool ShowWindow(IntPtr w,int cmd);
 [DllImport("user32.dll")] public static extern IntPtr GetForegroundWindow();
 [DllImport("user32.dll")] public static extern void keybd_event(byte key,byte scan,uint flags,UIntPtr info);
 public static bool Focus(string expectedTitle) {
  bool found=false;
  EnumWindows((w,p)=>{var s=new StringBuilder(1024);GetWindowText(w,s,1024);
   if(IsWindowVisible(w)&&s.ToString().Contains(expectedTitle)) {
    ShowWindow(w,9);
    if(GetForegroundWindow()!=w){keybd_event(0x12,0,0,UIntPtr.Zero);keybd_event(0x12,0,2,UIntPtr.Zero);}
    SetForegroundWindow(w);found=GetForegroundWindow()==w;return false;
   }return true;},IntPtr.Zero);return found;
 }
}
'@
$focused=$false
for($i=0;$i -lt 30;$i++) {
 Start-Sleep -Milliseconds 300
 if([D6PlayerWindow]::Focus($p.title)) {$focused=$true;break}
}
if(-not $focused){throw 'Player launched, but its foreground window could not be confirmed.'}
Write-Output ('Confirmed: ' + $p.title + ' is the foreground Windows window.')
'''.replace('__PARAMS__', "'"+params.replace("'","''")+"'")
result = subprocess.run([shutil.which('powershell.exe'),'-NoProfile','-NonInteractive','-Command',script],capture_output=True,text=True,timeout=30)
print(result.stdout.strip())
if result.returncode:
    print(result.stderr.strip())
raise SystemExit(result.returncode)
