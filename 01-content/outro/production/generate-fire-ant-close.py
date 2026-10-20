"""One short Tyler closing sentence within the existing $3 production cap."""
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
receipt_path = PROD / 'fire-ant-close-generation-v1.json'
output = OUTRO / 'assets/fire-ant-closing-tyler-source-v1.mp3'
assert not receipt_path.exists() and not output.exists(), 'Existing request preserved. No retry.'
approval = json.loads((PROD / 'finished-outro-approval-v2.json').read_text())
plan = json.loads((PROD / 'fire-ant-ending-plan.json').read_text())
assert approval['finished_outro_approved'] and approval['fire_ant_closing_and_join_authorized']
assert approval['production_cap_remains_usd'] == plan['existing_cumulative_production_cap_usd'] == 3.0
assert plan['production_estimate_before_usd'] + plan['new_voice_conservative_ceiling_usd'] <= 3.0
for name, expected in approval['approved_assets'].items():
    assert hashlib.sha256((OUTRO / name).read_bytes()).hexdigest() == expected
voice = json.loads((PROD / 'fire-ant-voice-reference.json').read_text())
spoken = (OUTRO / 'fire-ant-closing-spoken.txt').read_text().strip()
assert spoken == plan['closing_spoken_text']
text = '[warm, clear, conversational] ' + spoken
previous = (ROOT / '01-content/audio/D6-6c917b49743b/full-original-tyler-01/original.txt').read_text().strip().split('\n\n')[-1]
following = (OUTRO / 'outro-spoken.txt').read_text().strip()
# Reserve even the context at the published character rate; no billable retry.
context_inclusive_estimate = (len(text) + len(previous) + len(following)) * 0.10 / 1000
assert context_inclusive_estimate <= plan['new_voice_conservative_ceiling_usd']
key = os.environ.get('ELEVENLABS_API_KEY')
if not key:
    for line in (Path.home() / '.config/allwork/keys.env').read_text().splitlines():
        if line.startswith('ELEVENLABS_API_KEY='):
            key = shlex.split(line.split('=', 1)[1])[0]
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
            return response.read(), {name: response.headers.get(name) for name in ['request-id', 'character-cost']}
    except urllib.error.HTTPError as error:
        raise RuntimeError('ElevenLabs HTTP status ' + str(error.code)) from None
    except Exception:
        raise RuntimeError('Provider request interrupted; no automatic retry.') from None

sub = json.loads(request('/v1/user/subscription')[0])
live_voice = json.loads(request('/v1/voices/' + voice['voice_id'])[0])
models = json.loads(request('/v1/models')[0])
model = next(m for m in models if m['model_id'] == voice['model_id'])
assert model['can_do_text_to_speech'] and model['token_cost_factor'] == 1.0
assert live_voice['sharing']['rate'] == 1.0
available = sub['character_limit'] - sub['character_count']
assert available >= len(text) + len(previous) + len(following)
assert sub['tier'] == 'payg' and not sub['can_extend_character_limit']
payload = {'text': text, 'model_id': voice['model_id'], 'seed': voice['seed'],
           'voice_settings': voice['voice_settings'], 'previous_text': previous, 'next_text': following}
receipt = {'started_utc': datetime.datetime.now(datetime.timezone.utc).isoformat(),
           'status': 'request_started', 'phase': 'approved_fire_ant_finishing', 'category': 'voice',
           'generation_requests': 1, 'automatic_retry': False,
           'authorization': 'Approved next step after finished outro; remains inside previously approved $3 production cap.',
           'approval_file': 'production/finished-outro-approval-v2.json',
           'plan_file': 'production/fire-ant-ending-plan.json',
           'voice_id': voice['voice_id'], 'voice_name': 'Tyler', 'model_id': voice['model_id'],
           'seed': voice['seed'], 'voice_settings': voice['voice_settings'], 'spoken_text': spoken,
           'direction': '[warm, clear, conversational]', 'spoken_input_characters_with_tag': len(text),
           'previous_text_context': previous, 'next_text_context': following,
           'context_fields_are_not_spoken': True, 'existing_available_credits': available,
           'voice_credit_multiplier': 1.0, 'model_credit_multiplier': 1.0,
           'usd_per_1000_characters': 0.10, 'conservative_cost_bound_usd': round(context_inclusive_estimate, 8),
           'reserved_ceiling_usd': plan['new_voice_conservative_ceiling_usd'],
           'estimated_api_cost_usd': round(len(text) * 0.10 / 1000, 8),
           'pricing_url': 'https://elevenlabs.io/pricing/api', 'cost_is_invoice_confirmed': False}
with receipt_path.open('x') as file:
    json.dump(receipt, file, indent=2)
    file.write('\n')
print(json.dumps({'preflight_passed': True, 'voice': 'Tyler', 'estimated_usd': receipt['estimated_api_cost_usd'],
                  'context_inclusive_bound_usd': receipt['conservative_cost_bound_usd']}), flush=True)
try:
    data, headers = request('/v1/text-to-speech/' + voice['voice_id'] + '?output_format=' + voice['output_format'], payload)
    with output.open('xb') as file:
        file.write(data)
    receipt.update(status='generated_pending_review', output=str(output.relative_to(ROOT)),
                   bytes=len(data), sha256=hashlib.sha256(data).hexdigest(), response_headers=headers)
except Exception as error:
    receipt.update(status='failed_or_incomplete_no_retry', error=str(error).replace(key, '[redacted]')[:180])
finally:
    receipt['finished_utc'] = datetime.datetime.now(datetime.timezone.utc).isoformat()
    receipt_path.write_text(json.dumps(receipt, indent=2) + '\n')
print(json.dumps({k: receipt[k] for k in ['status', 'output', 'bytes', 'estimated_api_cost_usd', 'error'] if k in receipt}))
if receipt['status'] != 'generated_pending_review':
    raise SystemExit(1)
