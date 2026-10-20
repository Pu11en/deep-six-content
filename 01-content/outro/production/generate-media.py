"""One bounded, explicitly approved Google media request. Never auto-retry."""
import argparse
import base64
import datetime
import hashlib
import json
from pathlib import Path
import shlex
import urllib.error
import urllib.request

ROOT = Path(__file__).resolve().parents[3]
OUTRO = ROOT / '01-content/outro'
PROD = OUTRO / 'production'
if (PROD / 'v1-rejection.json').exists():
    raise SystemExit('Drew rejected v1. This historical generation path is closed; no request sent. Use the corrected per-episode voice and approved replacement plan.')
parser = argparse.ArgumentParser()
parser.add_argument('kind', choices=['voice', 'video'])
parser.add_argument('--version', type=int, default=1)
args = parser.parse_args()
approval = json.loads((PROD / 'production-approval.json').read_text())
assert approval['approved'] and approval['maximum_additional_usd'] == 2.0
limit = approval['limits'][args.kind]
receipt_path = PROD / f'{args.kind}-generation-v{args.version}.json'
assert not receipt_path.exists(), 'Existing receipt: no duplicate request sent.'
existing = [json.loads(p.read_text()) for p in PROD.glob('*-generation-v*.json')]
assert sum(r.get('category') == args.kind for r in existing) < limit['max_calls']
credential = None
for entry in (Path.home() / '.config/allwork/keys.env').read_text().splitlines():
    if entry.startswith('DEEPSIX_GOOGLE_API_KEY='):
        credential = shlex.split(entry.split('=', 1)[1])[0]
        break
assert credential, 'Project Google credential unavailable.'

def sha(data):
    return hashlib.sha256(data).hexdigest()

def now():
    return datetime.datetime.now(datetime.timezone.utc).isoformat()

references = {}
if args.kind == 'voice':
    assert args.version in [1, 2]
    model = 'gemini-3.8-flash-tts'
    spoken = (OUTRO / 'outro-spoken.txt').read_text().strip()
    assert spoken == 'Helping you understand pests. Deep Six Pest Control.'
    direction_file = PROD / ('voice-prompt.txt' if args.version == 1 else 'voice-prompt-v2.txt')
    direction = direction_file.read_text().split('Speak only')[0].strip()
    input_data = [{'type': 'user_input', 'content': [{
        'type': 'text', 'text': spoken,
        'annotations': [{'type': 'speech_metadata', 'style': direction}],
    }]}]
    response_format = {'type': 'audio', 'mime_type': 'audio/wav', 'sample_rate': 24000}
    output_limit = 2048
    generation = {'max_output_tokens': output_limit, 'speech_config': [{'voice': 'Sulafat'}]}
    input_bound = len((spoken + direction).encode()) + 1024
    input_rate, max_output_rate = 0.50, 9.0
    prompt = direction + '\n' + spoken
    extension = '.wav'
    destination = OUTRO / 'assets' / f'outro-voice-raw-v{args.version}{extension}'
else:
    assert args.version == 1
    model = 'gemini-omni-1.1-flash'
    reference = OUTRO / 'assets/hybrid-still-v3.jpg'
    review = json.loads((PROD / 'still-v3-review.json').read_text())
    assert review['accepted_for_motion_test'] and review['sha256'] == sha(reference.read_bytes())
    prompt = '[# Sources <FIRST_FRAME>@Image1]\n' + (PROD / 'video-prompt.txt').read_text()
    input_data = [
        {'type': 'image', 'mime_type': 'image/jpeg', 'data': base64.b64encode(reference.read_bytes()).decode()},
        {'type': 'text', 'text': prompt},
    ]
    references[str(reference.relative_to(ROOT))] = sha(reference.read_bytes())
    response_format = {'type': 'video', 'aspect_ratio': '9:16', 'resolution': '720p'}
    output_limit = 65536
    generation = {'max_output_tokens': output_limit}
    input_bound = len(prompt.encode()) + 8192
    input_rate, max_output_rate = 1.50, 17.50
    extension = '.mp4'
    destination = OUTRO / 'assets/mascot-motion-source-v1.mp4'

bound = (input_bound * input_rate + output_limit * max_output_rate) / 1_000_000
assert bound <= limit['max_usd_per_call'], 'Request exceeds per-call ceiling.'
phase_receipts = [json.loads(p.read_text()) for p in PROD.glob('*.json')]
reserved = sum(r.get('estimated_api_cost_usd', r.get('conservative_token_cost_bound_usd', 0))
               for r in phase_receipts if isinstance(r, dict) and r.get('phase') == 'additional_2_usd')
assert reserved + bound <= approval['maximum_additional_usd'], 'Request exceeds total approval.'
assert not destination.exists(), 'Existing output preserved.'
payload = {'model': model, 'input': input_data, 'response_format': response_format,
           'generation_config': generation, 'store': False, 'stream': False, 'background': False}
receipt = {
    'started_utc': now(), 'status': 'request_started', 'phase': 'additional_2_usd',
    'category': args.kind, 'model': model, 'generation_requests': 1,
    'approved_cap_usd': limit['max_usd_per_call'], 'automatic_retry': False,
    'approval_file': '01-content/outro/production/production-approval.json',
    'conservative_input_token_allowance': input_bound,
    'conservative_token_cost_bound_usd': round(bound, 8),
    'already_estimated_or_reserved_usd': round(reserved, 8),
    'generation_config': generation, 'response_format': response_format,
    'prompt_sha256': sha(prompt.encode()), 'references': references,
    'pricing_url': 'https://ai.google.dev/gemini-api/docs/pricing',
    'pricing_checked_date': '2026-10-19',
    'rate_usd_per_million_tokens': {'input': input_rate, 'maximum_output': max_output_rate},
}
with receipt_path.open('x') as file:
    json.dump(receipt, file, indent=2); file.write('\n')
print(json.dumps({'kind': args.kind, 'preflight_passed': True,
                  'conservative_bound_usd': round(bound, 8), 'cap_usd': limit['max_usd_per_call']}), flush=True)
try:
    request = urllib.request.Request('https://generativelanguage.googleapis.com/v1beta/interactions',
        data=json.dumps(payload).encode(), headers={'x-goog-api-key': credential, 'Content-Type': 'application/json'})
    with urllib.request.urlopen(request, timeout=900) as response:
        result = json.load(response)
    receipt['provider_status'] = result.get('status')
    receipt['interaction_id'] = result.get('id')
    receipt['usage'] = result.get('usage', {})
    blocks = [content for step in result.get('steps', []) if step.get('type') == 'model_output'
              for content in step.get('content', []) if content.get('type') == ('audio' if args.kind == 'voice' else 'video')]
    assert len(blocks) == 1, 'Expected exactly one generated media block; no retry sent.'
    media = blocks[0]
    assert media.get('data'), 'Inline output missing; no duplicate request sent.'
    data = base64.b64decode(media['data'])
    if args.kind == 'voice':
        assert data[:4] == b'RIFF' and data[8:12] == b'WAVE', 'Expected WAV container.'
    else:
        assert data[4:8] == b'ftyp', 'Expected MP4 container.'
    with destination.open('xb') as file:
        file.write(data)
    receipt.update({'status': 'generated_pending_review', 'output': str(destination.relative_to(ROOT)),
                    'sha256': sha(data), 'bytes': len(data), 'mime_type': media.get('mime_type')})
    # Preserve the provider's usage schema for an explicit cost calculation after review.
    receipt['cost_is_invoice_confirmed'] = False
except urllib.error.HTTPError as error:
    receipt.update({'status': 'failed_no_retry', 'http_status': error.code})
    try:
        error_obj = json.loads(error.read())
        message = error_obj.get('error', {}).get('message', '')
        receipt['error'] = message.replace(credential, '[redacted]')[:600]
    except Exception:
        receipt['error'] = 'Provider error; no automatic retry sent.'
except Exception as error:
    receipt.update({'status': 'failed_or_incomplete_no_retry',
                    'error': str(error).replace(credential, '[redacted]')[:200]})
finally:
    receipt['finished_utc'] = now()
    receipt_path.write_text(json.dumps(receipt, indent=2) + '\n')
print(json.dumps({k: receipt[k] for k in ['status', 'output', 'bytes', 'usage', 'http_status', 'error'] if k in receipt}))
if receipt['status'] != 'generated_pending_review':
    raise SystemExit(1)
