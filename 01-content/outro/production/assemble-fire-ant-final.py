"""Join the preserved lesson picture, new close and approved outro locally."""
import hashlib
import json
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[3]
OUTRO = ROOT / '01-content/outro'
PROD = OUTRO / 'production'
recipe = json.loads((PROD / 'fire-ant-assembly-v2.json').read_text())
original = ROOT / '01-content/animation/episodes/D6-6c917b49743b/full/renders/full-v2.mp4'
assert hashlib.sha256(original.read_bytes()).hexdigest() == 'c7ff2561764537bf68eef8b57a62ac3c5399e382f90baeec183e4620c825aa06'
output = OUTRO / 'assets/deep-six-fire-ants-full-v2-with-outro.mp4'
assert not output.exists(), 'Existing final output preserved.'
playlist = PROD / 'fire-ant-picture-concat.txt'
playlist.write_text("file 'fire-ant-original-picture-copy.mp4'\nfile 'fire-ant-ending-picture-v2.mp4'\n")
filters = (
    '[1:a]aresample=48000,aformat=sample_fmts=fltp:channel_layouts=mono,'
    'apad,atrim=duration=79.2,asetpts=PTS-STARTPTS[lesson];'
    '[2:a]aformat=sample_fmts=fltp:sample_rates=48000:channel_layouts=mono,'
    f'apad,atrim=duration={recipe["closing_duration_seconds"]},asetpts=PTS-STARTPTS[close];'
    '[3:a]aformat=sample_fmts=fltp:sample_rates=48000:channel_layouts=mono,'
    'adelay=550:all=1,apad,atrim=duration=5.5,asetpts=PTS-STARTPTS[outro];'
    '[lesson][close][outro]concat=n=3:v=0:a=1[audio]'
)
command = ['ffmpeg', '-hide_banner', '-loglevel', 'error', '-nostdin', '-n',
           '-f', 'concat', '-safe', '0', '-i', str(playlist),
           '-i', str(original), '-i', str(OUTRO / 'assets/fire-ant-closing-tyler-v1.wav'),
           '-i', str(OUTRO / 'assets/fire-ant-tyler-signoff-review-v2.wav'),
           '-filter_complex', filters, '-map', '0:v:0', '-map', '[audio]',
           '-c:v', 'copy', '-c:a', 'aac', '-b:a', '192k', '-ar', '48000', '-ac', '1',
           '-t', str(recipe['full_duration_seconds']), '-movflags', '+faststart', str(output)]
subprocess.run(command, check=True)
recipe.update(final_output=str(output.relative_to(ROOT)),
              final_sha256=hashlib.sha256(output.read_bytes()).hexdigest(),
              lesson_video_stream_copy=True,
              final_audio_processing='Original lesson audio decoded and resampled to 48 kHz, then joined to level-matched Tyler close and approved Tyler sign-off. One continuous AAC encode; speech not regenerated or retimed.',
              final_audio_sample_rate=48000, final_audio_channels=1,
              original_file_preserved=True)
(PROD / 'fire-ant-assembly-v2.json').write_text(json.dumps(recipe, indent=2) + '\n')
print(json.dumps({'output': str(output.relative_to(ROOT)), 'duration_seconds': recipe['full_duration_seconds'],
                  'original_lesson_picture_stream_copied': True, 'sha256': recipe['final_sha256']}))
