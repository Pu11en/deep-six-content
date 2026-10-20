"""Open a verified D6 MP4 in a foreground Windows video window, paused."""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import subprocess


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('manifest', type=Path)
    args = parser.parse_args()
    manifest = args.manifest.resolve()
    spec = json.loads(manifest.read_text())
    review = json.loads((manifest.parent / spec['approval_file']).read_text())
    video = manifest.parent / review['candidate']
    digest = hashlib.sha256(video.read_bytes()).hexdigest()
    if digest != spec['video_sha256'] or digest != review['candidate_sha256']:
        raise SystemExit('Video fingerprint does not match its review.')
    powershell = shutil.which('powershell.exe')
    if not powershell or not shutil.which('wslpath'):
        raise SystemExit('Windows desktop integration is unavailable. Saved MP4: ' + str(video))
    source = subprocess.check_output(['wslpath', '-w', str(video)], text=True).strip()
    params = json.dumps({'source': source, 'fingerprint': digest, 'revision': spec['revision'],
                         'title': 'Deep Six Video Preview'})
    script = Path(__file__).with_name('open_d6_video.ps1').read_text()
    script = script.replace('__PARAMS__', "'" + params.replace("'", "''") + "'")
    result = subprocess.run([powershell, '-NoProfile', '-NonInteractive', '-Command', script],
                            capture_output=True, text=True, timeout=35)
    print(result.stdout.strip())
    if result.returncode:
        print(result.stderr.strip())
    else:
        details = json.loads(result.stdout.strip())
        details['video_sha256'] = digest
        details['browser_opened'] = False
        (manifest.parent.parent / 'playback-check.json').write_text(json.dumps(details, indent=2) + '\n')
    raise SystemExit(result.returncode)


if __name__ == '__main__':
    main()
