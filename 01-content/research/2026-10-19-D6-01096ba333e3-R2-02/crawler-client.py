"""Run this trial's crawler requests; credentials remain in process memory."""
import json
from pathlib import Path
import socket
import subprocess
import sys
import time
from urllib.error import HTTPError
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parent
CLIENT = 'imac-research'
REMOTE = 'drewp@100.80.131.62'


def save(path, value):
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + '\n')


def main():
    method, endpoint, payload_name, output_name = sys.argv[1:]
    payload = None if payload_name == '-' else json.loads((ROOT / payload_name).read_text())
    remote_code = (
        'import json,sys; '
        'from pathlib import Path; '
        'd=json.loads(Path("/Users/drewp/ultimate-crawler-agent/config/clients.json").read_text()); '
        'v=d["imac-research"]; '
        'sys.stdout.write(v if isinstance(v,str) else v["token"])'
    )
    import shlex
    login = subprocess.run(
        ['ssh', '-o', 'BatchMode=yes', '-o', 'ConnectTimeout=10', REMOTE,
         'python3 -c ' + shlex.quote(remote_code)],
        capture_output=True, text=True, timeout=20,
    )
    if login.returncode or not login.stdout.strip():
        raise RuntimeError('Existing crawler login unavailable; no request sent.')
    token = login.stdout.strip()
    del login
    with socket.socket() as listener:
        listener.bind(('127.0.0.1', 0))
        port = listener.getsockname()[1]
    tunnel = subprocess.Popen(
        ['ssh', '-N', '-o', 'BatchMode=yes', '-o', 'ConnectTimeout=10',
         '-o', 'ExitOnForwardFailure=yes', '-L',
         f'127.0.0.1:{port}:127.0.0.1:8766', REMOTE],
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
    )
    try:
        for _ in range(50):
            if tunnel.poll() is not None:
                raise RuntimeError('Crawler tunnel failed; no request sent.')
            try:
                with socket.create_connection(('127.0.0.1', port), timeout=0.2):
                    break
            except OSError:
                time.sleep(0.1)
        else:
            raise RuntimeError('Crawler tunnel unavailable; no request sent.')
        request = Request(
            f'http://127.0.0.1:{port}' + endpoint,
            data=None if payload is None else json.dumps(payload).encode(),
            headers={'Authorization': 'Bearer ' + token, 'Content-Type': 'application/json'},
            method=method,
        )
        try:
            with urlopen(request, timeout=55) as response:
                result = json.loads(response.read())
        except HTTPError as error:
            # Do not log raw authenticated errors or request headers.
            print(json.dumps({'http_status': error.code, 'saved': False}))
            return 1

        def scrub(value):
            if isinstance(value, dict):
                return {key: ('[redacted]' if key.lower() in
                        {'token', 'access_token', 'api_key', 'password', 'authorization'}
                        else scrub(item)) for key, item in value.items()}
            if isinstance(value, list):
                return [scrub(item) for item in value]
            if isinstance(value, str):
                return value.replace(token, '[redacted]')
            return value

        result = scrub(result)
        save(ROOT / output_name, result)
        print(json.dumps({'saved': output_name, 'keys': list(result) if isinstance(result, dict) else [],
                          'status': result.get('status') if isinstance(result, dict) else None}))
        return 0
    finally:
        token = None
        tunnel.terminate()
        try:
            tunnel.wait(timeout=3)
        except subprocess.TimeoutExpired:
            tunnel.kill()
            tunnel.wait()


if __name__ == '__main__':
    try:
        raise SystemExit(main())
    except Exception as error:
        print(json.dumps({'error_type': type(error).__name__, 'saved': False,
                          'action': 'Reconcile existing state before retrying a mutation.'}))
        raise SystemExit(1)
