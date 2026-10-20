"""One approved replacement request, with durable receipt and no retries."""
import argparse
import base64
import datetime
import hashlib
import io
import json
from pathlib import Path
import shlex
import urllib.error
import urllib.request

from PIL import Image

ROOT = Path(__file__).resolve().parents[3]
OUTRO = ROOT / '01-content/outro'
PROD = OUTRO / 'production'
parser = argparse.ArgumentParser()
parser.add_argument('kind', choices=['start', 'end', 'video'])
args = parser.parse_args()
approval = json.loads((PROD / 'v2-production-approval.json').read_text())
assert approval['approved'] and approval['total_production_cap_usd'] == 3.0
receipt_path = PROD / f'v2-{args.kind}-generation.json'
assert not receipt_path.exists(), 'Existing receipt: no duplicate or retry sent.'

def sha(data):
    return hashlib.sha256(data).hexdigest()

def now():
    return datetime.datetime.now(datetime.timezone.utc).isoformat()

credential = None
for entry in (Path.home() / '.config/allwork/keys.env').read_text().splitlines():
    if entry.startswith('DEEPSIX_GOOGLE_API_KEY='):
        credential = shlex.split(entry.split('=', 1)[1])[0]
        break
assert credential, 'Project Google credential unavailable.'

def request(url, body, timeout=900):
    req = urllib.request.Request(url, data=json.dumps(body).encode(),
        headers={'x-goog-api-key': credential, 'Content-Type': 'application/json'})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as response:
            return json.load(response)
    except urllib.error.HTTPError as error:
        raise RuntimeError('Google HTTP status ' + str(error.code)) from None
    except Exception:
        raise RuntimeError('Google request interrupted; no automatic retry sent.') from None

def accepted_frame(kind):
    review = json.loads((PROD / f'v2-{kind}-review.json').read_text())
    path = ROOT / review['output']
    assert review['accepted_for_motion'] and review['sha256'] == sha(path.read_bytes())
    return path

if args.kind == 'start':
    refs = [ROOT / '01-content/brand/fun-fact-friday-spider.png',
            OUTRO / 'assets/v2-paper-style-reference.png']
elif args.kind == 'end':
    refs = [accepted_frame('start')]
else:
    refs = [accepted_frame('start'), accepted_frame('end')]

def mime(path):
    return 'image/png' if path.suffix == '.png' else 'image/jpeg'

prompt = (PROD / f'v2-{args.kind}-frame-prompt.txt').read_text() if args.kind != 'video' else (
    '[# Sources <FIRST_FRAME>@Image1 <LAST_FRAME>@Image2]\n' + (PROD / 'v2-video-prompt.txt').read_text())
input_bound = len(prompt.encode()) + (8192 if args.kind == 'video' else 4096) * len(refs)
if args.kind != 'video':
    model = 'gemini-nano-banana-2.1'
    url = 'https://generativelanguage.googleapis.com/v1beta/models/' + model
    parts = [{'inlineData': {'mimeType': mime(p), 'data': base64.b64encode(p.read_bytes()).decode()}} for p in refs]
    parts.append({'text': prompt})
    contents = [{'role': 'user', 'parts': parts}]
    counted = request(url + ':countTokens', {'contents': contents}, timeout=90).get('totalTokens', 0)
    input_bound = max(counted, input_bound)
    config = {'candidateCount': 1, 'responseModalities': ['IMAGE'], 'maxOutputTokens': 4096,
              'thinkingConfig': {'thinkingLevel': 'MINIMAL'},
              'imageConfig': {'aspectRatio': '9:16', 'imageSize': '2K'}}
    payload = {'contents': contents, 'generationConfig': config}
    url += ':generateContent'
    bound = input_bound * 1.5e-6 + 4096 * 30e-6
    cap = 0.15
    destination_stem = OUTRO / 'assets' / f'outro-v2-{args.kind}'
else:
    model = 'gemini-omni-1.1-flash'
    url = 'https://generativelanguage.googleapis.com/v1beta/interactions'
    inputs = [{'type': 'image', 'mime_type': mime(p), 'data': base64.b64encode(p.read_bytes()).decode()} for p in refs]
    inputs.append({'type': 'text', 'text': prompt})
    config = {'max_output_tokens': 65536}
    payload = {'model': model, 'input': inputs,
               'response_format': {'type': 'video', 'aspect_ratio': '9:16', 'resolution': '720p'},
               'generation_config': config, 'store': False, 'stream': False, 'background': False}
    bound = input_bound * 1.5e-6 + 65536 * 17.5e-6
    cap = 1.25
    destination_stem = OUTRO / 'assets/mascot-motion-source-v2'
assert bound <= cap, 'Request exceeds approved per-call cap.'
spent = approval['prior_estimated_production_spend_usd']
for p in PROD.glob('v2-*-generation.json'):
    r = json.loads(p.read_text())
    spent += r.get('estimated_api_cost_usd', r['conservative_token_cost_bound_usd'])
assert spent + bound <= approval['total_production_cap_usd'], 'Request exceeds cumulative cap.'
assert not list(destination_stem.parent.glob(destination_stem.name + '.*')), 'Existing output preserved.'
receipt = {'started_utc': now(), 'status': 'request_started', 'phase': 'replacement_v2',
           'category': args.kind, 'model': model, 'generation_requests': 1, 'automatic_retry': False,
           'approval_file': str((PROD / 'v2-production-approval.json').relative_to(ROOT)),
           'approved_cap_usd': cap, 'conservative_token_cost_bound_usd': round(bound, 8),
           'prior_estimated_or_reserved_production_usd': round(spent, 8),
           'input_token_allowance': input_bound, 'generation_config': config,
           'prompt_sha256': sha(prompt.encode()),
           'references': {str(p.relative_to(ROOT)): sha(p.read_bytes()) for p in refs},
           'pricing_url': 'https://ai.google.dev/gemini-api/docs/pricing',
           'rates_checked_date': '2026-10-19', 'cost_is_invoice_confirmed': False}
with receipt_path.open('x') as file:
    json.dump(receipt, file, indent=2)
    file.write('\n')
print(json.dumps({'preflight_passed': True, 'kind': args.kind, 'bound_usd': round(bound, 8)}), flush=True)
try:
    response = request(url, payload)
    if args.kind != 'video':
        usage = response.get('usageMetadata', {})
        receipt['model_version'] = response.get('modelVersion')
        blocks = [p['inlineData'] for c in response.get('candidates', [])
                  for p in c.get('content', {}).get('parts', [])
                  if not p.get('thought') and p.get('inlineData', {}).get('mimeType', '').startswith('image/')]
        assert len(blocks) == 1, 'Expected one image; no retry sent.'
        block = blocks[0]
        suffix = {'image/png': '.png', 'image/jpeg': '.jpg', 'image/webp': '.webp'}[block['mimeType']]
        data = base64.b64decode(block['data'])
        with Image.open(io.BytesIO(data)) as loaded:
            receipt['dimensions'] = list(loaded.size)
            loaded.verify()
        image_tokens = sum(d.get('tokenCount', 0) for d in usage.get('candidatesTokensDetails', []) if d.get('modality') == 'IMAGE') or 1680
        other = max(0, usage.get('candidatesTokenCount', image_tokens) - image_tokens) + usage.get('thoughtsTokenCount', 0)
        estimate = usage.get('promptTokenCount', input_bound) * 1.5e-6 + image_tokens * 30e-6 + other * 7.5e-6
        receipt['image_output_tokens'] = image_tokens
    else:
        usage = response.get('usage', {})
        receipt['provider_status'] = response.get('status')
        receipt['interaction_id'] = response.get('id')
        blocks = [c for s in response.get('steps', []) if s.get('type') == 'model_output'
                  for c in s.get('content', []) if c.get('type') == 'video']
        assert len(blocks) == 1 and blocks[0].get('data'), 'Expected one inline video; no retry sent.'
        suffix = '.mp4'
        data = base64.b64decode(blocks[0]['data'])
        assert data[4:8] == b'ftyp', 'Expected MP4 container.'
        estimate = usage.get('total_input_tokens', input_bound) * 1.5e-6 + usage.get('total_output_tokens', 65536) * 17.5e-6 + usage.get('total_thought_tokens', 0) * 9e-6
    destination = destination_stem.with_suffix(suffix)
    with destination.open('xb') as file:
        file.write(data)
    receipt.update(status='generated_pending_review', output=str(destination.relative_to(ROOT)),
                   sha256=sha(data), bytes=len(data), usage=usage, estimated_api_cost_usd=round(estimate, 8))
except Exception as error:
    receipt.update(status='failed_or_incomplete_no_retry', error=str(error).replace(credential, '[redacted]')[:200])
finally:
    receipt['finished_utc'] = now()
    receipt_path.write_text(json.dumps(receipt, indent=2) + '\n')
print(json.dumps({k: receipt[k] for k in ['status', 'output', 'dimensions', 'estimated_api_cost_usd', 'usage', 'error'] if k in receipt}))
if receipt['status'] != 'generated_pending_review':
    raise SystemExit(1)
