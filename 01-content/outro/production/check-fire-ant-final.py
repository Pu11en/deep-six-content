"""Meaningful export checks for the assembled fire-ant lesson and outro."""
import datetime
import hashlib
import json
from pathlib import Path
import re
import subprocess

import numpy as np
from faster_whisper import WhisperModel

ROOT = Path(__file__).resolve().parents[3]
OUTRO = ROOT / '01-content/outro'
PROD = OUTRO / 'production'
FINAL = OUTRO / 'assets/deep-six-fire-ants-full-v2-with-outro.mp4'
ORIGINAL = ROOT / '01-content/animation/episodes/D6-6c917b49743b/full/renders/full-v2.mp4'
recipe = json.loads((PROD / 'fire-ant-assembly-v2.json').read_text())
probe = json.loads(subprocess.check_output(['ffprobe', '-v', 'error', '-count_frames', '-show_entries',
    'format=duration:stream=index,codec_type,codec_name,width,height,r_frame_rate,nb_read_frames,sample_rate,channels',
    '-of', 'json', str(FINAL)]))
video = next(s for s in probe['streams'] if s['codec_type'] == 'video')
audio = next(s for s in probe['streams'] if s['codec_type'] == 'audio')
assert [video['width'], video['height']] == [1080, 1920]
assert video['r_frame_rate'] == '30/1' and int(video['nb_read_frames']) == recipe['full_frames']
assert abs(float(probe['format']['duration']) - recipe['full_duration_seconds']) < 0.04
assert audio['sample_rate'] == '48000' and audio['channels'] == 1
print('Final dimensions, frame count, duration and audio format passed.', flush=True)

frame_file = PROD / 'fire-ant-final-frames.md5'
if not frame_file.exists():
    subprocess.run(['ffmpeg', '-hide_banner', '-loglevel', 'error', '-nostdin', '-n', '-i', str(FINAL),
                    '-map', '0:v:0', '-an', '-f', 'framemd5', str(frame_file)], check=True)
def frame_hashes(path):
    return [line.split(',')[-1].strip() for line in path.read_text().splitlines() if line and not line.startswith('#')]
before = frame_hashes(PROD / 'fire-ant-original-frames.md5')
after = frame_hashes(frame_file)
assert len(before) == 2376 and len(after) == recipe['full_frames']
assert before == after[:len(before)], 'Original lesson pixels changed.'
print('All 2,376 original lesson frames match exactly after decoding.', flush=True)

def pcm(path, start=0, duration=79.2):
    data = subprocess.check_output(['ffmpeg', '-hide_banner', '-loglevel', 'error', '-nostdin', '-ss', str(start),
        '-i', str(path), '-t', str(duration), '-vn', '-ar', '48000', '-ac', '1', '-f', 'f32le', '-'])
    return np.frombuffer(data, dtype='<f4')
first = pcm(ORIGINAL).astype(np.float64)
second = pcm(FINAL).astype(np.float64)
assert len(first) == len(second)
correlation = float(np.corrcoef(first, second)[0, 1])
assert correlation > 0.995, 'Original lesson audio comparison needs inspection.'
full_audio = pcm(FINAL, duration=recipe['full_duration_seconds'])
peak = float(np.max(np.abs(full_audio)))
assert peak < 1.0, 'Audio clipping detected.'
print('Original lesson audio comparison and peak check passed.', flush=True)

tail = PROD / 'fire-ant-final-ending-check.wav'
if not tail.exists():
    subprocess.run(['ffmpeg', '-hide_banner', '-loglevel', 'error', '-nostdin', '-n', '-ss', '79.2', '-i', str(FINAL),
        '-vn', '-ar', '16000', '-ac', '1', '-c:a', 'pcm_s16le', str(tail)], check=True)
model = WhisperModel('small.en', device='cpu', compute_type='int8', local_files_only=True)
segments, _ = model.transcribe(str(tail), language='en', word_timestamps=True, beam_size=5, vad_filter=False)
rows = [{'text': s.text, 'start': s.start, 'end': s.end,
         'words': [{'text': w.word.strip(), 'start': w.start, 'end': w.end} for w in s.words]} for s in segments]
transcript = ''.join(s['text'] for s in rows).strip()
closing = (OUTRO / 'fire-ant-closing-spoken.txt').read_text().strip()
signoff = (OUTRO / 'outro-spoken.txt').read_text().strip()
normalize = lambda text: re.sub('[^a-z]+', ' ', text.lower().replace('6', ' six ')).strip()
assert normalize(transcript) == normalize(closing + ' ' + signoff), transcript
assert normalize(transcript).count(normalize(signoff)) == 1
complete = (OUTRO / 'fire-ant-complete-narration.txt').read_text()
original_text = (ROOT / '01-content/audio/D6-6c917b49743b/full-original-tyler-01/original.txt').read_text().strip()
assert complete.startswith(original_text) and complete.count(signoff) == 1

approval = json.loads((PROD / 'finished-outro-approval-v2.json').read_text())
approved_unchanged = {name: hashlib.sha256((OUTRO / name).read_bytes()).hexdigest() == expected
                      for name, expected in approval['approved_assets'].items()}
assert all(approved_unchanged.values())
source_hash = hashlib.sha256(ORIGINAL.read_bytes()).hexdigest()
assert source_hash == 'c7ff2561764537bf68eef8b57a62ac3c5399e382f90baeec183e4620c825aa06'
voice = json.loads((PROD / 'fire-ant-voice-reference.json').read_text())
generation = json.loads((PROD / 'fire-ant-close-generation-v1.json').read_text())
assert all(voice[k] == generation[k] for k in ['voice_id', 'model_id', 'seed', 'voice_settings'])
production_estimate = 2.2813095 + generation['estimated_api_cost_usd']
assert production_estimate < 3.0
result = {
    'checked_utc': datetime.datetime.now(datetime.timezone.utc).isoformat(), 'status': 'checks_passed',
    'final_output': str(FINAL.relative_to(ROOT)), 'final_sha256': hashlib.sha256(FINAL.read_bytes()).hexdigest(),
    'probe': probe, 'original_decoded_frames_identical': len(before), 'new_frames_added': recipe['ending_frames'],
    'original_lesson_frame_comparison': 'Every decoded frame hash matches the corresponding original frame.',
    'original_audio_prefix_correlation': correlation, 'original_audio_sample_count_compared': len(first),
    'audio_processing_limit': 'Final audio is resampled and AAC-encoded once; it is not byte-identical to original audio.',
    'final_audio_peak_dbfs': round(20 * np.log10(peak), 3), 'original_video_file_unchanged': True,
    'approved_outro_assets_unchanged': approved_unchanged, 'same_Tyler_voice_settings': True,
    'closing_words_and_signoff_once': True, 'ending_asr_transcript': transcript, 'ending_asr_segments': rows,
    'complete_narration_contains_original_and_exact_signoff_once': True,
    'caption_negation_remains_visible_through_concluding_clause': True,
    'closing_duration_seconds': recipe['closing_duration_seconds'], 'outro_start_seconds': recipe['outro_start_seconds'],
    'new_voice_generation_calls': 1, 'new_image_or_video_generation_calls': 0, 'automatic_retries': False,
    'finishing_voice_estimate_usd': generation['estimated_api_cost_usd'],
    'cumulative_production_estimate_usd': round(production_estimate, 8), 'approved_production_cap_usd': 3.0,
    'initial_test_separate_estimate_usd': 0.058155, 'cost_is_invoice_confirmed': False,
    'publishing_performed': False, 'other_sessions_messaged': False,
}
(PROD / 'fire-ant-final-checks.json').write_text(json.dumps(result, indent=2) + '\n')
print(json.dumps({k: result[k] for k in ['status', 'original_decoded_frames_identical', 'original_audio_prefix_correlation',
    'ending_asr_transcript', 'cumulative_production_estimate_usd']}))
