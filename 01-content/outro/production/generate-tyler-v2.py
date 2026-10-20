"""One episode-specific Tyler review. No retries, top-ups, or universal narration."""
import datetime
import hashlib
import json
import os
from pathlib import Path
import shlex
import urllib.error
import urllib.request

ROOT = Path(__file__).resolve().parents[3]
OUTRO = ROOT / '01-content/outro'
PROD = OUTRO / 'production'
receipt_path = PROD / 'v2-voice-generation.json'
destination = OUTRO / 'assets/fire-ant-tyler-signoff-source-v2.mp3'
assert not receipt_path.exists() and not destination.exists(), 'Existing request preserved; no retry.'
approval = json.loads((PROD / 'v2-production-approval.json').read_text())
assert approval['approved'] and approval['limits']['voice']['max_usd_per_call'] == 0.10
verified = json.loads((PROD / 'v2-voice-provider-check.json').read_text())
assert verified['model'][0]['model_id'] == 'eleven_v4' and verified['model'][0]['token_cost_factor'] == 1.0
assert verified['voice_sharing']['rate'] == 1.0
voice = json.loads((PROD / 'fire-ant-voice-reference.json').read_text())
spoken = (OUTRO / 'outro-spoken.txt').read_text().strip()
assert spoken == 'Helping you understand pests. Deep Six Pest Control.'
text = '[warm, clear, conversational] ' + spoken
bound = len(text) * 0.10 / 1000
assert bound < 0.10
spent = approval['prior_estimated_production_spend_usd']
for path in PROD.glob('v2-*-generation.json'):
    r = json.loads(path.read_text())
    spent += r.get('estimated_api_cost_usd', r['conservative_token_cost_bound_usd'])
assert spent + 0.10 <= 3.0
key = os.environ.get('ELEVENLABS_API_KEY')
if not key:
    for entry in (Path.home() / '.config/allwork/keys.env').read_text().splitlines():
        if entry.startswith('ELEVENLABS_API_KEY='):
            key = shlex.split(entry.split('=', 1)[1])[0]
assert key, 'ElevenLabs credential unavailable.'

def request(path, payload=None):
    headers = {'xi-api-key': key}
    data = None
    if payload is not None:
        headers['Content-Type'] = 'application/json'
        data = json.dumps(payload).encode()
    try:
        with urllib.request.urlopen(urllib.request.Request('https://api.elevenlabs.io' + path,
                data=data, headers=headers), timeout=180) as response:
            return response.read(), {k: response.headers.get(k) for k in ['request-id', 'character-cost']}
    except urllib.error.HTTPError as error:
        raise RuntimeError('ElevenLabs HTTP status ' + str(error.code)) from None
    except Exception:
        raise RuntimeError('ElevenLabs request interrupted; no automatic retry.') from None

sub = json.loads(request('/v1/user/subscription')[0])
available = sub['character_limit'] - sub['character_count']
assert available >= len(text), 'Insufficient existing credits; no top-up.'
assert sub['tier'] == 'payg' and not sub['can_extend_character_limit']
payload = {'text': text, 'model_id': voice['model_id'], 'seed': voice['seed'],
           'voice_settings': voice['voice_settings']}
receipt = {'started_utc': datetime.datetime.now(datetime.timezone.utc).isoformat(),
           'status': 'request_started', 'phase': 'replacement_v2', 'category': 'voice',
           'generation_requests': 1, 'automatic_retry': False,
           'approval_file': '01-content/outro/production/v2-production-approval.json',
           'voice_id': voice['voice_id'], 'voice_name': 'Tyler', 'model_id': voice['model_id'],
           'seed': voice['seed'], 'voice_settings': voice['voice_settings'],
           'output_format': voice['output_format'], 'spoken_text': spoken, 'direction_tag': '[warm, clear, conversational]',
           'characters_including_direction': len(text), 'available_credits_before': available,
           'credit_multiplier': 1.0, 'usd_per_1000_characters': 0.10,
           'conservative_token_cost_bound_usd': round(bound, 8), 'approved_cap_usd': 0.10,
           'pricing_url': 'https://elevenlabs.io/pricing/api',
           'same_pricing_v4_source': 'https://elevenlabs.io/v4', 'cost_is_invoice_confirmed': False,
           'scope': 'Fire-ant outro review only. Future videos generate whole narration in their own voice.'}
with receipt_path.open('x') as file:
    json.dump(receipt, file, indent=2)
    file.write('\n')
print(json.dumps({'preflight_passed': True, 'voice': 'Tyler', 'characters': len(text), 'bound_usd': bound}), flush=True)
try:
    data, headers = request('/v1/text-to-speech/' + voice['voice_id'] + '?output_format=' + voice['output_format'], payload)
    with destination.open('xb') as file:
        file.write(data)
    receipt.update(status='generated_pending_review', output=str(destination.relative_to(ROOT)),
                   sha256=hashlib.sha256(data).hexdigest(), bytes=len(data),
                   estimated_api_cost_usd=round(bound, 8), response_headers=headers)
except Exception as error:
    receipt.update(status='failed_or_incomplete_no_retry', error=str(error).replace(key, '[redacted]')[:160])
finally:
    receipt['finished_utc'] = datetime.datetime.now(datetime.timezone.utc).isoformat()
    receipt_path.write_text(json.dumps(receipt, indent=2) + '\n')
print(json.dumps({k: receipt[k] for k in ['status', 'output', 'bytes', 'estimated_api_cost_usd', 'error'] if k in receipt}))
if receipt['status'] != 'generated_pending_review':
    raise SystemExit(1)
