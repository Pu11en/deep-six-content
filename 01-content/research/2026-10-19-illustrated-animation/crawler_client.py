"""Research-run helper. Uses the existing remote credential in memory only."""
import hashlib
import json
from pathlib import Path
import socket
import subprocess
import sys
import time
import urllib.error
import urllib.request

ROOT = Path(__file__).resolve().parent
CLIENT = 'imac-research'
HOST = 'drewp@100.80.131.62'
SSH = ['ssh', '-o', 'BatchMode=yes', '-o', 'ConnectTimeout=8',
       '-o', 'ConnectionAttempts=1', '-o', 'StrictHostKeyChecking=yes']


def save(name, data):
    p = ROOT / name
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(data, indent=2, ensure_ascii=False) + '\n')


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, *args, **kwargs):
        return None


def main(command):
    code = "import json; from pathlib import Path; print(json.dumps({'token':json.loads(Path('/Users/drewp/ultimate-crawler-agent/config/clients.json').read_text())['imac-research']}))"
    proc = subprocess.run(SSH + [HOST, 'python3 -'], input=code,
                          capture_output=True, text=True, timeout=15)
    if proc.returncode:
        raise RuntimeError('Existing crawler credential unavailable over SSH')
    token = json.loads(proc.stdout)['token']
    del proc
    with socket.socket() as sock:
        sock.bind(('127.0.0.1', 0))
        port = sock.getsockname()[1]
    tunnel = subprocess.Popen(SSH + ['-N', '-T', '-o', 'ExitOnForwardFailure=yes',
        '-L', f'127.0.0.1:{port}:127.0.0.1:8766', HOST],
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    try:
        deadline = time.monotonic() + 10
        while time.monotonic() < deadline:
            if tunnel.poll() is not None:
                raise RuntimeError('SSH tunnel failed')
            try:
                with socket.create_connection(('127.0.0.1', port), timeout=.2):
                    break
            except OSError:
                time.sleep(.1)
        else:
            raise RuntimeError('SSH tunnel readiness timed out')
        opener = urllib.request.build_opener(urllib.request.ProxyHandler({}), NoRedirect())

        def call(method, path, data=None):
            body = None if data is None else json.dumps(data).encode()
            request = urllib.request.Request(f'http://127.0.0.1:{port}' + path,
                data=body, method=method, headers={'Authorization': 'Bearer ' + token,
                'Accept': 'application/json', 'Content-Type': 'application/json'})
            try:
                with opener.open(request, timeout=55) as response:
                    return json.loads(response.read(8_000_000))
            except urllib.error.HTTPError as error:
                raise RuntimeError(f'Crawler HTTP {error.code}; request not retried') from None

        caps = call('GET', '/research/agent/capabilities?client_id=' + CLIENT)
        if caps.get('authentication') != 'per_client_bearer' or caps.get('paid_fallback'):
            raise RuntimeError('Unexpected authentication or paid-fallback configuration')
        save('capabilities.json', caps)
        if command['op'] == 'init':
            if (ROOT / 'session.json').exists():
                raise RuntimeError('Existing session: resume instead of creating another')
            created = call('POST', '/planning/sessions', command['session'])
            save('session.json', created)
            approved = call('POST', f"/planning/sessions/{created['id']}/approve",
                {'client_id': CLIENT, 'expected_revision': created['revision']})
            save('approved-plan.json', approved)
            queued = call('POST', f"/planning/sessions/{created['id']}/start",
                {'client_id': CLIENT, 'expected_revision': created['revision'],
                 'idempotency_key': 'd6-illustrated-animation-' + created['id']})
            save('request.json', queued)
            opened = call('POST', f"/research/agent/requests/{queued['id']}", {'client_id': CLIENT})
            save('job.json', opened)
            state = opened['state']
            print(json.dumps({'job_id': state['id'], 'status': state['status'], 'limits': state['limits']}), flush=True)
            return
        state = json.loads((ROOT / 'job.json').read_text())['state']
        live = call('GET', f"/research/agent/jobs/{state['id']}?client_id={CLIENT}")
        save('job.json', live)
        state = live['state']
        for action in command.get('actions', []):
            revision = state['agent_revision']
            digest = hashlib.sha256(json.dumps(action, sort_keys=True).encode()).hexdigest()[:16]
            payload = {'client_id': CLIENT, 'expected_revision': revision,
                'idempotency_key': f'd6-{revision}-{digest}', 'action': action}
            save(f'actions/{revision:03d}-request.json', payload)
            response = call('POST', f"/research/agent/jobs/{state['id']}/actions", payload)
            save('job.json', response)
            save(f'actions/{revision:03d}-receipt.json', response['receipt'])
            state = response['state']
            for source in state['sources']:
                save(f"sources/{source['id']}.json", source)
            info = {'tool': action['tool'], 'revision': state['agent_revision'],
                    'outcome': response['receipt']['outcome'], 'usage': state['usage']}
            if action['tool'] == 'read' and state['sources']:
                source = state['sources'][-1]
                info['latest_source'] = {'id': source['id'], 'url': source['final_url'], 'chars': len(source['text'])}
            if action['tool'] == 'search':
                info['search'] = state['queries'][-1:] if state.get('queries') else []
                info['gaps'] = state['gaps'][-2:]
            if action['tool'] == 'evidence':
                info['evidence'] = state['evidence'][-1:]
            print(json.dumps(info, ensure_ascii=False), flush=True)
    finally:
        token = None
        tunnel.terminate()
        try:
            tunnel.wait(timeout=5)
        except subprocess.TimeoutExpired:
            tunnel.kill()
            tunnel.wait()


if __name__ == '__main__':
    try:
        main(json.load(sys.stdin))
    except Exception as error:
        print(f'Research helper stopped: {type(error).__name__}. No automatic retry.', file=sys.stderr)
        raise SystemExit(1)
