"""Submit saved crawler actions sequentially with receipts and recovery state."""
import json
from pathlib import Path
import subprocess
import sys
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parent
ALLOWED_DOMAINS = ('citybugs.tamu.edu', 'fireant.tamu.edu', 'extensionentomology.tamu.edu', 'agrilifeextension.tamu.edu', 'npic.orst.edu', 'epa.gov', 'ars.usda.gov', 'extension.msstate.edu', 'pmc.ncbi.nlm.nih.gov', 'academic.oup.com', 'extension.okstate.edu', 'fireants.tennessee.edu')


def save(name, value):
    (ROOT / name).write_text(json.dumps(value, indent=2, ensure_ascii=False) + '\n')


def call(method, endpoint, payload, output):
    subprocess.run([sys.executable, str(ROOT / 'crawler-client.py'), method,
                    endpoint, payload, output], check=True)
    return json.loads((ROOT / output).read_text())


checkpoint = json.loads((ROOT / 'checkpoint.json').read_text())
job = json.loads((ROOT / 'job-opened.json').read_text())['state']['id']
checkpoint['crawler_job_id'] = job
state = call('GET', f'/research/agent/jobs/{job}?client_id=imac-research', '-', 'live-job.json')['state']
if checkpoint.get('pending_action'):
    raise SystemExit('An action is pending. Reconcile its saved payload and live receipts before continuing.')
for action in json.loads((ROOT / sys.argv[1]).read_text()):
    if action['tool'] == 'read':
        url = urlsplit(action['url'])
        if (url.scheme != 'https' or url.username or url.password
                or not any(url.hostname == domain or (url.hostname or '').endswith('.' + domain)
                           for domain in ALLOWED_DOMAINS)):
            raise SystemExit('Read is outside the approved source domains; no action submitted.')
    number = state['agent_revision'] + 1
    name = f'receipts/{number:03d}-{action["tool"]}'
    payload = {'client_id': 'imac-research', 'expected_revision': state['agent_revision'],
               'idempotency_key': f'research-488991e51202-a{number}', 'action': action}
    save(name + '-request.json', payload)
    checkpoint.update(status='researching', pending_action=name + '-request.json')
    save('checkpoint.json', checkpoint)
    result = call('POST', f'/research/agent/jobs/{job}/actions', name + '-request.json', name + '.json')
    state = result['state']
    save('live-job.json', result)
    checkpoint.update(pending_action=None, agent_revision=state['agent_revision'],
                      usage=state['usage'], active_seconds=state['active_seconds'],
                      crawler_status=state['status'])
    save('checkpoint.json', checkpoint)
    print(json.dumps({'receipt': name, 'tool': action['tool'],
                      'status': state['status'], 'usage': state['usage'],
                      'active_seconds': state['active_seconds'],
                      'outcome': result.get('receipt', {}).get('outcome')},
                     ensure_ascii=False), flush=True)
    if action['tool'] not in ('read', 'search') and result.get('receipt', {}).get('outcome') != 'applied':
        raise SystemExit('Research record was not applied; inspect this receipt before continuing.')
