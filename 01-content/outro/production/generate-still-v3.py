"""Execute Drew's approved Google still correction; never retry automatically."""
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
PRODUCTION = OUTRO / 'production'
MODEL = 'gemini-nano-banana-2.1'
API = 'https://generativelanguage.googleapis.com/v1beta/models/' + MODEL
CAP = 0.15
OUTPUT_LIMIT = 4096
INPUT_RATE = 1.50 / 1_000_000
IMAGE_RATE = 30.00 / 1_000_000
TEXT_RATE = 7.50 / 1_000_000
RECEIPT = PRODUCTION / 'image-correction-v3.json'
REFERENCES = [
    ROOT / '01-content/brand/fun-fact-friday-spider.png',
]

if RECEIPT.exists():
    raise SystemExit('This test already has a receipt. No duplicate request or retry sent.')

approval = json.loads((PRODUCTION / 'production-approval.json').read_text())
assert approval['approved'] and approval['maximum_additional_usd'] == 2.0
assert approval['limits']['image']['max_usd_per_call'] == CAP
credential = None
for entry in (Path.home() / '.config/allwork/keys.env').read_text().splitlines():
    if entry.startswith('DEEPSIX_GOOGLE_API_KEY='):
        credential = shlex.split(entry.split('=', 1)[1])[0]
        break
if not credential:
    raise SystemExit('Project Google credential is unavailable. No request sent.')


def request(suffix, body):
    req = urllib.request.Request(
        API + suffix, data=json.dumps(body).encode(),
        headers={'x-goog-api-key': credential, 'Content-Type': 'application/json'},
    )
    try:
        with urllib.request.urlopen(req, timeout=300) as response:
            return json.load(response)
    except urllib.error.HTTPError as error:
        raise RuntimeError('Google HTTP status ' + str(error.code)) from None
    except Exception:
        raise RuntimeError('Google request failed; no automatic retry was sent.') from None


prompt = (PRODUCTION / 'still-source-v3-prompt.txt').read_text()
parts = [{'inlineData': {'mimeType': 'image/png' if p.suffix == '.png' else 'image/jpeg', 'data': base64.b64encode(p.read_bytes()).decode()}} for p in REFERENCES]
parts.append({'text': prompt})
contents = [{'role': 'user', 'parts': parts}]
config = {
    'candidateCount': 1,
    'responseModalities': ['IMAGE'],
    'maxOutputTokens': OUTPUT_LIMIT,
    'thinkingConfig': {'thinkingLevel': 'MINIMAL'},
    'imageConfig': {'aspectRatio': '9:16', 'imageSize': '2K'},
}

tokens = request(':countTokens', {'contents': contents})['totalTokens']
input_bound = max(tokens, len(prompt.encode()) + 4096 * len(REFERENCES))
upper_bound = input_bound * INPUT_RATE + OUTPUT_LIMIT * max(IMAGE_RATE, TEXT_RATE)
if upper_bound > CAP:
    raise SystemExit('The request cannot fit the approved ceiling. No generation request sent.')

receipt = {
    'started_utc': datetime.datetime.now(datetime.timezone.utc).isoformat(),
    'status': 'request_started',
    'provider': 'Google Gemini API',
    'model': MODEL,
    'generation_requests': 1,
    'approval_file': str((PRODUCTION / 'production-approval.json').relative_to(ROOT)),
    'approved_cap_usd': CAP,
    'generation_config': config,
    'prompt_sha256': hashlib.sha256(prompt.encode()).hexdigest(),
    'references': {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest() for p in REFERENCES},
    'preflight_input_tokens': tokens,
    'conservative_input_token_allowance': input_bound,
    'phase': 'additional_2_usd',
    'category': 'image',
    'conservative_token_cost_bound_usd': round(upper_bound, 8),
    'pricing_url': 'https://ai.google.dev/gemini-api/docs/pricing',
    'pricing_checked_date': '2026-10-19',
    'rate_usd_per_million_tokens': {'input': 1.5, 'output_image': 30, 'output_text_and_thinking': 7.5},
    'automatic_retry': False,
}
with RECEIPT.open('x') as file:
    json.dump(receipt, file, indent=2)
    file.write('\n')
print(json.dumps({'preflight_passed': True, 'input_tokens': tokens, 'conservative_bound_usd': round(upper_bound, 8), 'approved_cap_usd': CAP}), flush=True)

try:
    response = request(':generateContent', {'contents': contents, 'generationConfig': config})
    receipt['usage'] = response.get('usageMetadata', {})
    receipt['model_version'] = response.get('modelVersion')
    receipt['finish_reasons'] = [c.get('finishReason') for c in response.get('candidates', [])]
    images = [p['inlineData'] for c in response.get('candidates', [])
              for p in c.get('content', {}).get('parts', [])
              if 'inlineData' in p and not p.get('thought') and p['inlineData'].get('mimeType', '').startswith('image/')]
    if len(images) != 1:
        raise RuntimeError('Expected exactly one final image; no retry sent.')
    image = images[0]
    suffix = {'image/png': '.png', 'image/jpeg': '.jpg', 'image/webp': '.webp'}.get(image['mimeType'])
    if suffix is None:
        raise RuntimeError('Unexpected image format; no retry sent.')
    data = base64.b64decode(image['data'])
    with Image.open(io.BytesIO(data)) as loaded:
        dimensions = list(loaded.size)
        loaded.verify()
    destination = OUTRO / 'assets' / ('hybrid-still-v3' + suffix)
    destination.parent.mkdir(exist_ok=True)
    with destination.open('xb') as file:
        file.write(data)
    receipt.update({'status': 'generated_pending_visual_review', 'output': str(destination.relative_to(ROOT)),
                    'dimensions': dimensions, 'sha256': hashlib.sha256(data).hexdigest()})
    usage = receipt['usage']
    details = usage.get('candidatesTokensDetails', [])
    image_tokens = sum(d.get('tokenCount', 0) for d in details if d.get('modality') == 'IMAGE')
    if not image_tokens:
        image_tokens = 1680
        receipt['image_token_count_basis'] = 'Published per-image 2K token quantity; modality breakdown unavailable'
    else:
        receipt['image_token_count_basis'] = 'API usage modality breakdown'
    text_tokens = max(0, usage.get('candidatesTokenCount', image_tokens) - image_tokens)
    thought_tokens = usage.get('thoughtsTokenCount', 0)
    estimate = usage.get('promptTokenCount', tokens) * INPUT_RATE + image_tokens * IMAGE_RATE + (text_tokens + thought_tokens) * TEXT_RATE
    receipt['estimated_api_cost_usd'] = round(estimate, 8)
    receipt['cost_is_invoice_confirmed'] = False
except Exception as error:
    receipt['status'] = 'failed_or_incomplete_no_retry'
    receipt['error'] = str(error).replace(credential, '[redacted]')[:200]
finally:
    receipt['finished_utc'] = datetime.datetime.now(datetime.timezone.utc).isoformat()
    RECEIPT.write_text(json.dumps(receipt, indent=2) + '\n')

print(json.dumps({k: receipt[k] for k in ['status', 'output', 'dimensions', 'estimated_api_cost_usd', 'error'] if k in receipt}))
if receipt['status'] == 'failed_or_incomplete_no_retry':
    raise SystemExit(1)
