"""Local edit only. Uses approved-generation outputs; no network or API calls."""
import json
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[3]
ASSETS = ROOT / '01-content/outro/assets'
PROD = ROOT / '01-content/outro/production'

def ffmpeg(arguments):
    subprocess.run(['ffmpeg', '-hide_banner', '-loglevel', 'error', '-nostdin', '-n',
                    '-filter_complex_threads', '2'] + arguments, check=True)

# The provider introduced blinking and white pupils after its initial clean frames.
# Reuse only source frames 0..31, then reverse the same brief motion to return to pose.
# This makes a tiny acknowledgement; no changed-eye frame enters the master.
motion = ASSETS / 'mascot-motion-clean-v1.mp4'
if not motion.exists():
    filters = (
        '[0:v]trim=start_frame=0:end_frame=32,setpts=PTS-STARTPTS,split=3[a][b][c];'
        '[a]select=eq(n\\,0),loop=loop=41:size=1:start=0,setpts=N/(30*TB)[hold1];'
        '[b]setpts=PTS*0.3,fps=30,trim=end_frame=12,setpts=N/(30*TB),split[fwd][back];'
        '[back]reverse,setpts=N/(30*TB)[rev];'
        '[c]select=eq(n\\,0),loop=loop=68:size=1:start=0,setpts=N/(30*TB)[hold2];'
        '[hold1][fwd][rev][hold2]concat=n=4:v=1:a=0,fps=30,format=yuv420p[v]'
    )
    ffmpeg(['-i', str(ASSETS/'mascot-motion-source-v1.mp4'), '-filter_complex', filters,
            '-map', '[v]', '-an', '-frames:v', '135', '-c:v', 'libx264', '-preset', 'slow',
            '-crf', '16', '-movflags', '+faststart', str(motion)])

master = ASSETS / 'outro-master-v1.mp4'
if not master.exists():
    filters = (
        '[0:v]scale=960:1706:flags=lanczos,setsar=1[art];'
        '[1:v][art]overlay=x=40:y=48:shortest=1[paper];'
        '[paper][2:v]overlay=0:0:format=auto,format=yuv420p[v]'
    )
    ffmpeg(['-i', str(motion), '-f', 'lavfi', '-i', 'color=c=0xF6EFE2:s=1080x1920:r=30:d=4.5',
            '-loop', '1', '-framerate', '30', '-i', str(ASSETS/'outro-wording-overlay-v1.png'),
            '-i', str(ASSETS/'outro-audio-v1.wav'), '-filter_complex', filters,
            '-map', '[v]', '-map', '3:a', '-frames:v', '135', '-t', '4.5',
            '-c:v', 'libx264', '-preset', 'slow', '-crf', '18', '-pix_fmt', 'yuv420p',
            '-c:a', 'aac', '-b:a', '192k', '-ar', '48000', '-movflags', '+faststart', str(master)])

# Standalone review uses a neutral cream entry. The episode's final teaching
# frame replaces this neutral plate only after Drew approves the finished outro.
review = ASSETS / 'outro-review-v1.mp4'
if not review.exists():
    filters = (
        '[0:v]tpad=start_mode=clone:start_duration=0.5,setpts=PTS-STARTPTS,split[base][reveal];'
        '[base]drawbox=x=0:y=0:w=iw:h=ih:color=0xF6EFE2:t=fill[cream];'
        "[cream][reveal]blend=all_expr='if(lt(T,0.2),A,if(lt(T,0.5),if(lt(X,W*(T-0.2)/0.3),B,A),B))'[v];"
        '[0:a]adelay=500:all=1,apad,atrim=duration=5[a]'
    )
    ffmpeg(['-i', str(master), '-filter_complex', filters, '-map', '[v]', '-map', '[a]',
            '-frames:v', '150', '-t', '5', '-c:v', 'libx264', '-preset', 'slow', '-crf', '18',
            '-pix_fmt', 'yuv420p', '-c:a', 'aac', '-b:a', '192k', '-ar', '48000',
            '-movflags', '+faststart', str(review)])

recipe = {
    'output_fps': 30, 'dimensions': [1080, 1920], 'master_frames': 135,
    'review_frames': 150, 'master_duration_seconds': 4.5, 'review_duration_seconds': 5,
    'source_video': '01-content/outro/assets/mascot-motion-source-v1.mp4',
    'source_clean_frames_inclusive': [0, 31], 'source_fps': 24,
    'motion_edit': '42-frame hold; 12-frame forward acknowledgement from clean source; 12-frame reverse; 69-frame hold.',
    'motion_window_master_seconds': [1.4, 2.2],
    'source_audio_used': False,
    'voice': {'source': 'outro-voice-raw-v1.wav', 'trim_start_seconds': 0.16,
              'gain_db': -0.7, 'speed_change': False, 'padded_duration_seconds': 4.5},
    'logo_source': 'https://www.deepsixpest.com/wp-content/uploads/2026/02/Header_Logo.png',
    'review_entry': 'Neutral cream for 0.2 seconds, then left-to-right cream reveal for 0.3 seconds.',
    'episode_join_pending': 'Replace neutral plate with the episode final image and apply the same 9-frame wipe after its last audible word plus 6 frames. Requires finished-outro approval first.',
    'no_fire_ant_footage_used': True,
}
(PROD/'assembly-v1.json').write_text(json.dumps(recipe, indent=2)+'\n')
print(json.dumps({'master': str(master.relative_to(ROOT)), 'review': str(review.relative_to(ROOT))}))
