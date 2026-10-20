"""Drew-requested Opus creative direction through the existing subscription login."""
import datetime
import hashlib
import json
from pathlib import Path
import sys
import time

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT/'tools'))
from d6_models import invoke, failure_kind

PROD = ROOT/'01-content/outro/production'
RECEIPT = PROD/'opus-v2-focused-receipt.json'
OUTPUT = PROD/'OPUS-V2-CREATIVE.md'
assert not RECEIPT.exists() and not OUTPUT.exists(), 'Existing creative result preserved.'
code, raw, err = invoke(['claude', 'auth', 'status', '--json'], cwd=ROOT, timeout=20)
try:
    auth = json.loads(raw)
except ValueError:
    raise SystemExit('Could not verify subscription login. No model request sent.')
assert code == 0 and auth.get('loggedIn') and auth.get('authMethod') in ('claude.ai', 'oauth'), 'Subscription login required.'
prompt = (PROD/'opus-v2-focused-brief.md').read_text()
args = ['claude', '-p', '--safe-mode', '--strict-mcp-config', '--mcp-config', '{"mcpServers":{}}',
        '--model', 'claude-opus-5-5', '--effort', 'high', '--no-session-persistence',
        '--output-format', 'json', '--permission-mode', 'dontAsk', '--permission-prompts', 'none',
        '--tools', 'Read', '--allowedTools', 'Read', '--no-chrome',
        '--append-system-prompt', 'Read-only creative task explicitly requested by Drew. No writes, web, command execution, delegation or paid generation. Follow the supplied brief.']
r = {'started_utc': datetime.datetime.now(datetime.timezone.utc).isoformat(), 'status': 'running',
     'requested_model': 'claude-opus-5-5', 'effort': 'high', 'route': 'Claude Code subscription login',
     'api_key_route_disabled': True, 'automatic_fallback': False, 'tools': ['Read'],
     'brief_sha256': hashlib.sha256(prompt.encode()).hexdigest(), 'user_authorized_model': True}
with RECEIPT.open('x') as file:
    json.dump(r, file, indent=2); file.write('\n')
print(json.dumps({'status': 'started', 'model': r['requested_model'], 'route': r['route']}), flush=True)
start = time.monotonic()
try:
    code, out, err = invoke(args, cwd=ROOT, prompt=prompt, timeout=300)
    data = json.loads(out)
    if code or data.get('is_error') or not data.get('result'):
        raise RuntimeError(failure_kind(out + err))
    result = data['result']
    assert isinstance(result, str) and len(result) > 500
    with OUTPUT.open('x') as file:
        file.write(result.rstrip() + '\n')
    r.update({'status': 'complete', 'output': str(OUTPUT.relative_to(ROOT)),
              'output_sha256': hashlib.sha256(OUTPUT.read_bytes()).hexdigest(),
              'usage': data.get('usage', {}), 'model_usage': data.get('modelUsage', {}),
              'subscription_cost_equivalent_usd': data.get('total_cost_usd'),
              'cost_note': 'CLI cost-equivalent metadata is not evidence of an additional API charge.',
              'num_turns': data.get('num_turns'), 'permission_denials': data.get('permission_denials', [])})
except Exception as error:
    r.update({'status': 'failed_no_fallback', 'failure': type(error).__name__, 'failure_kind': getattr(error, 'kind', None)})
    if isinstance(error, RuntimeError):
        r['failure_kind'] = str(error)
finally:
    r['elapsed_seconds'] = round(time.monotonic()-start, 1)
    r['finished_utc'] = datetime.datetime.now(datetime.timezone.utc).isoformat()
    RECEIPT.write_text(json.dumps(r, indent=2)+'\n')
print(json.dumps({k: r[k] for k in ['status', 'output', 'elapsed_seconds', 'num_turns', 'failure_kind'] if k in r}))
if r['status'] != 'complete':
    raise SystemExit(1)
