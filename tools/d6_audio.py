"""Explicitly requested audio comparisons; credentials stay in the environment."""
import argparse
import fcntl
import hashlib
import json
import math
import os
from pathlib import Path
import re
import shutil
import subprocess
from contextlib import contextmanager
from uuid import uuid4
from urllib.error import HTTPError
from urllib.request import Request, urlopen

from d6_harness import atomic_text, now


class AudioError(Exception):
    pass


def fingerprint(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(',', ':'),
                                     ensure_ascii=False).encode()).hexdigest()


def audio_root(spec_path):
    """All manifests in the project's audio tree share locks and request receipts."""
    path = Path(spec_path).resolve()
    for parent in path.parents:
        if parent.name == 'audio' and parent.parent.name == '01-content':
            return parent
    return path.parent


@contextmanager
def episode_lock(spec_path):
    path = Path(spec_path).resolve()
    spec = json.loads(path.read_text())
    episode = spec.get('approved_narration_id')
    if not isinstance(episode, str) or not re.fullmatch(r'[A-Za-z0-9_-]+', episode):
        raise AudioError('A valid approved narration ID is required.')
    directory = audio_root(path) / '.locks'
    directory.mkdir(exist_ok=True)
    with (directory / (episode + '.lock')).open('a') as lock:
        try:
            fcntl.flock(lock.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            raise AudioError('Another audio operation for this episode is active.') from None
        # Always reread mutable state after acquiring the shared episode lock.
        current = json.loads(path.read_text())
        if current.get('approved_narration_id') != episode:
            raise AudioError('The episode changed while acquiring its lock. Reload the job.')
        yield current


def canonical_script(spec_path, spec):
    if spec.get('approved_script_file'):
        path = (Path(spec_path).parent / spec['approved_script_file']).resolve()
    else:
        path = audio_root(spec_path).parent / 'approved-narrations' / (spec['approved_narration_id'] + '.md')
    if not path.is_file():
        raise AudioError('The canonical approved script file is missing.')
    text = path.read_text().strip()
    if path.suffix == '.md':
        heading = '# Approved narration ' + spec['approved_narration_id']
        if not text.startswith(heading + '\n') or '\n---\n' not in text:
            raise AudioError('The approved narration document does not match this episode.')
        text = text[len(heading):].split('\n---\n', 1)[0].strip()
    if not text:
        raise AudioError('The canonical approved script is empty.')
    state_path = audio_root(spec_path).parent / 'harness' / 'runtime' / 'state.json'
    if state_path.is_file():
        state = json.loads(state_path.read_text())
        approved = [item for item in state.get('approved', [])
                    if item.get('id') == spec['approved_narration_id']]
        if len(approved) != 1 or normalize_words(approved[0]['text']) != normalize_words(text):
            raise AudioError('The canonical script differs from the saved human-approved narration.')
    return text


def normalize_words(text):
    return ' '.join(text.split())


def request_identity(spec_path, spec, variant):
    text = (Path(spec_path).parent / variant['text_file']).read_text().rstrip('\n')
    approved = canonical_script(spec_path, spec)
    spoken = normalize_words(re.sub(r'\[[^\]\n]*\]', '', text))
    canonical = normalize_words(approved)
    kind = spec.get('kind')
    if kind == 'full_narration' and spoken != canonical:
        raise AudioError('Full render words differ from the canonical approved script. Reapprove the script first.')
    if kind == 'audition' and (not spoken or spoken not in canonical):
        raise AudioError('An audition must use an unchanged excerpt of the approved script.')
    if kind not in ('full_narration', 'audition'):
        raise AudioError('Specify kind: full_narration or audition before a new request.')
    identity = {'approved_narration_id': spec['approved_narration_id'], 'kind': kind,
                'script_sha256': hashlib.sha256(canonical.encode()).hexdigest(),
                'text_sha256': hashlib.sha256(text.encode()).hexdigest(),
                'voice_id': variant.get('voice_id') or spec.get('voice_id'),
                'model_id': spec['model_id'], 'seed': spec['seed'],
                'voice_settings': spec['voice_settings'], 'output_format': spec['output_format']}
    if not identity['voice_id'] or not text.strip():
        raise AudioError('A voice and nonempty render text are required.')
    if not str(identity['output_format']).startswith('mp3_'):
        raise AudioError('This audio workflow requires an MP3 output format.')
    return text, identity, fingerprint(identity)


def prepare_identities(spec_path, spec):
    if not 1 <= len(spec['variants']) <= 3:
        raise AudioError('This audio review requires one to three variants.')
    names = [v['name'] for v in spec['variants']]
    paths = [(Path(spec_path).parent / v['audio_file']).resolve() for v in spec['variants']]
    if len(set(names)) != len(names) or len(set(paths)) != len(paths):
        raise AudioError('Variant names and output paths must be unique; no request was sent.')
    if spec.get('voice_rotation_file'):
        if len(spec['variants']) != 1 or spec.get('kind') != 'full_narration':
            raise AudioError('Voice rotation applies to one full narration, not auditions.')
        voice = reserve_voice(Path(spec_path).parent / spec['voice_rotation_file'], spec['approved_narration_id'])
        current = spec.get('voice_id')
        if spec['variants'][0]['status'] != 'prepared' and (
                current != voice['voice_id'] or spec['variants'][0].get('voice_id') != voice['voice_id']):
            raise AudioError('The recorded voice differs from this episode assignment.')
        spec.update(voice_id=voice['voice_id'], voice_name=voice['name'])
        spec['variants'][0]['voice_id'] = voice['voice_id']
    items = [(variant, *request_identity(spec_path, spec, variant)) for variant in spec['variants']]
    if len({item[3] for item in items}) != len(items):
        raise AudioError('Identical requests cannot appear twice in one job.')
    return items


def authorize(spec_path, evidence, max_requests, max_characters):
    """Record actual user authorization supplied by the operator; never implies consent."""
    if not evidence.strip():
        raise AudioError('Record the user instruction that authorized this bounded request.')
    spec_path = Path(spec_path).resolve()
    with episode_lock(spec_path) as spec:
        items = prepare_identities(spec_path, spec)
        if len(items) > max_requests or sum(len(item[1]) for item in items) > max_characters:
            raise AudioError('The requested outputs exceed the stated authorization limits.')
        spec['authorization'] = {'approved': True, 'approved_at': now(), 'evidence': evidence,
                                 'max_requests': max_requests, 'max_characters': max_characters,
                                 'request_sha256': [item[3] for item in items]}
        atomic_text(spec_path, json.dumps(spec, indent=2) + '\n')
        return spec


def request(path, payload=None):
    key = os.environ.get('ELEVENLABS_API_KEY') or os.environ.get('ELEVEN_API_KEY')
    if not key:
        raise AudioError('An ElevenLabs key must be supplied through the environment.')
    headers = {'xi-api-key': key}
    data = None
    if payload is not None:
        headers['Content-Type'] = 'application/json'
        data = json.dumps(payload).encode()
    try:
        with urlopen(Request('https://api.elevenlabs.io' + path, data=data, headers=headers), timeout=180) as response:
            body = response.read()
            return body, response.headers.get('request-id')
    except HTTPError as error:
        # Never log a provider response or authenticated request headers.
        raise AudioError(f'ElevenLabs returned HTTP {error.code}; no automatic retry.') from None
    except (OSError, TimeoutError):
        raise AudioError('ElevenLabs request interrupted; check provider history before retrying.') from None


def remaining():
    body, _ = request('/v1/user/subscription')
    data = json.loads(body)
    return max(0, data['character_limit'] - data['character_count'])


def probe(path):
    result = subprocess.run(['ffprobe', '-v', 'error', '-show_entries',
                             'format=duration:stream=codec_name,sample_rate,channels',
                             '-of', 'json', str(path)], capture_output=True, text=True, check=True, timeout=30)
    data = json.loads(result.stdout)
    if not data.get('streams') or data['streams'][0]['codec_name'] != 'mp3':
        raise AudioError('Generated file did not validate as MP3.')
    duration = float(data['format']['duration'])
    if not math.isfinite(duration) or duration <= 1:
        raise AudioError('Generated audio was unexpectedly short.')
    return {'duration_seconds': duration, **data['streams'][0]}


def reserve_voice(rotation_path, narration_id):
    """Assign one rotating voice per approved script, including across retries."""
    rotation_path = Path(rotation_path)
    with rotation_path.with_suffix('.lock').open('a') as lock:
        fcntl.flock(lock.fileno(), fcntl.LOCK_EX)
        rotation = json.loads(rotation_path.read_text())
        assignments = rotation.setdefault('assignments', {})
        if narration_id not in assignments:
            index = rotation['next_index']
            assignments[narration_id] = rotation['voices'][index]
            rotation['next_index'] = (index + 1) % len(rotation['voices'])
            atomic_text(rotation_path, json.dumps(rotation, indent=2) + '\n')
        return assignments[narration_id]


def generate(spec_path):
    spec_path = Path(spec_path).resolve()
    with episode_lock(spec_path) as spec:
        return _generate_locked(spec_path, spec)


def _generate_locked(spec_path, spec):
    folder = spec_path.parent
    items = prepare_identities(spec_path, spec)
    pending = []
    for variant, text, identity, request_hash in items:
        digest = identity['text_sha256']
        if variant['status'] == 'complete':
            audio_path = folder / variant['audio_file']
            if (variant.get('request_sha256') != request_hash or
                    variant.get('text_sha256') != digest or not audio_path.exists() or
                    variant.get('audio_sha256') != hashlib.sha256(audio_path.read_bytes()).hexdigest()):
                raise AudioError('Completed audio, words or request settings changed, or this is a legacy job. Verify/deliver the saved recording; do not regenerate silently.')
            continue
        if variant['status'] != 'prepared':
            raise AudioError('A previous request may have been billed. Check provider history before retrying.')
        if (folder / variant['audio_file']).exists():
            raise AudioError('An audio file already exists; refusing to overwrite it.')
        if not (folder / variant['audio_file']).parent.is_dir():
            raise AudioError('The output directory is missing; no request was sent.')
        pending.append((variant, text, identity, request_hash))
    if not pending:
        if spec.get('status') not in ('audio_approved', 'audio_rejected') and not spec.get('review_id'):
            # Recover a crash after saving the last MP3 but before creating review.
            spec.update(status='waiting_audio_review', review_id='AUD-' + uuid4().hex[:12])
            atomic_text(spec_path, json.dumps(spec, indent=2) + '\n')
        return spec
    authorization = spec.get('authorization')
    if (not isinstance(authorization, dict) or authorization.get('approved') is not True or
            not authorization.get('evidence') or not authorization.get('approved_at') or
            authorization.get('request_sha256') != [item[3] for item in items] or
            authorization.get('max_requests', 0) < len(items) or
            authorization.get('max_characters', 0) < sum(len(item[1]) for item in items)):
        raise AudioError('This exact job lacks bounded recorded authorization; no request was sent.')
    if not shutil.which('ffprobe'):
        raise AudioError('ffprobe is unavailable; no paid request was sent.')
    receipts = audio_root(spec_path) / '.requests'
    receipts.mkdir(exist_ok=True)
    for _, _, _, request_hash in pending:
        receipt = receipts / (request_hash + '.json')
        if receipt.exists():
            raise AudioError('This exact request already has a receipt. Recover its saved result or reconcile provider history; do not pay again.')
    available = remaining()
    needed = sum(len(text) for _, text, _, _ in pending)
    # This comparison uses a verified standard-rate voice and one-credit model.
    if available < needed:
        raise AudioError(f'Need {needed} available characters; {available} remain. No top-up was attempted.')
    spec['available_characters_before'] = available
    for variant, text, identity, request_hash in pending:
        variant.update(status='request_started', text_sha256=identity['text_sha256'],
                       script_sha256=identity['script_sha256'], request_sha256=request_hash,
                       characters=len(text), started_at=now())
        spec.pop('audio_review', None)
        spec.pop('review_id', None)
        atomic_text(spec_path, json.dumps(spec, indent=2) + '\n')
        receipt = receipts / (request_hash + '.json')
        record = {'status': 'request_started', 'manifest': str(spec_path), 'variant': variant['name'],
                  'request_sha256': request_hash, 'started_at': now()}
        # Shared episode lock + persistent receipt protects calls across manifests.
        with receipt.open('x') as output:
            output.write(json.dumps(record, indent=2) + '\n')
        payload = {'text': text, 'model_id': spec['model_id'], 'seed': spec['seed'],
                   'voice_settings': spec['voice_settings']}
        body, request_id = request('/v1/text-to-speech/' + variant.get('voice_id', spec['voice_id']) +
                                   '?output_format=' + spec['output_format'], payload)
        audio_path = folder / variant['audio_file']
        # Exclusive creation avoids overwriting a prior paid result.
        with audio_path.open('xb') as output:
            output.write(body)
        variant.update(status='received', request_id=request_id,
                       audio_sha256=hashlib.sha256(body).hexdigest(), bytes=len(body))
        atomic_text(spec_path, json.dumps(spec, indent=2) + '\n')
        variant.update(probe(audio_path), status='complete', completed_at=now())
        atomic_text(spec_path, json.dumps(spec, indent=2) + '\n')
        record.update(status='complete', path=str(audio_path), audio_sha256=variant['audio_sha256'])
        atomic_text(receipt, json.dumps(record, indent=2) + '\n')
        print(variant['name'], 'MP3 saved:', round(variant['duration_seconds'], 1), 'seconds', flush=True)
    spec['status'] = 'waiting_audio_review'
    spec['review_id'] = 'AUD-' + uuid4().hex[:12]
    atomic_text(spec_path, json.dumps(spec, indent=2) + '\n')
    return spec


def checked_recording(spec_path, spec, variant_name, allow_legacy=False):
    variants = [item for item in spec['variants'] if item['name'] == variant_name]
    if len(variants) != 1 or variants[0]['status'] != 'complete':
        raise AudioError('Choose one complete recording from this review.')
    variant = variants[0]
    legacy = not variant.get('request_sha256')
    if legacy and not allow_legacy:
        raise AudioError('This legacy recording needs explicit verification before a new review.')
    if spec.get('kind') == 'audition':
        raise AudioError('An audition cannot be approved as the full MP3.')
    checked_spec = dict(spec, kind='full_narration')
    _, identity, request_hash = request_identity(spec_path, checked_spec, variant)
    if (variant.get('text_sha256') != identity['text_sha256'] or
            (not legacy and variant['request_sha256'] != request_hash)):
        raise AudioError('The recording no longer matches its approved words or request settings.')
    path = (Path(spec_path).parent / variant['audio_file']).resolve()
    if not path.is_file() or hashlib.sha256(path.read_bytes()).hexdigest() != variant.get('audio_sha256'):
        raise AudioError('The recording file is missing or changed.')
    measured = probe(path)
    return {'path': str(path), 'duration_seconds': measured['duration_seconds'],
            'audio_sha256': variant['audio_sha256'],
            'approved_narration_id': spec['approved_narration_id'],
            'request_sha256': request_hash, 'script_sha256': identity['script_sha256'],
            'legacy_approval': legacy}


def review_audio(spec_path, decision, review_id, variant_name, feedback):
    if decision not in ('approve', 'reject') or not feedback.strip():
        raise AudioError('Record an explicit approve/reject decision and the user feedback.')
    spec_path = Path(spec_path).resolve()
    with episode_lock(spec_path) as spec:
        if not review_id or spec.get('review_id') != review_id or spec.get('status') != 'waiting_audio_review':
            raise AudioError('That audio review is stale or already answered.')
        recording = checked_recording(spec_path, spec, variant_name)
        spec['audio_review'] = dict(recording, status='approved' if decision == 'approve' else 'rejected',
                                    feedback=feedback, reviewed_at=now(), review_id=review_id,
                                    approved_variant=variant_name if decision == 'approve' else None,
                                    reviewed_variant=variant_name)
        spec['status'] = 'audio_approved' if decision == 'approve' else 'audio_rejected'
        atomic_text(spec_path, json.dumps(spec, indent=2) + '\n')
        return spec


def verify_approved_audio(spec_path):
    """Read-only verification for the final-MP4 receipt; legacy approvals are flagged."""
    spec_path = Path(spec_path).resolve()
    spec = json.loads(spec_path.read_text())
    review = spec.get('audio_review', {})
    if spec.get('status') != 'audio_approved' or review.get('status') != 'approved':
        raise AudioError('A full recording needs explicit audio approval first.')
    recording = checked_recording(spec_path, spec, review.get('approved_variant'), allow_legacy=True)
    if not recording['legacy_approval']:
        for key in ('audio_sha256', 'request_sha256', 'script_sha256', 'approved_narration_id'):
            if review.get(key) != recording[key]:
                raise AudioError('The audio approval no longer matches this recording.')
    return recording


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Generate an authorized script or voice MP3 comparison.')
    parser.add_argument('comparison', type=Path)
    parser.add_argument('--action', choices=('generate', 'authorize', 'approve', 'reject', 'verify'), default='generate')
    parser.add_argument('--evidence', default='', help='Actual user instruction or review feedback; never credentials.')
    parser.add_argument('--max-requests', type=int, default=0)
    parser.add_argument('--max-characters', type=int, default=0)
    parser.add_argument('--review-id')
    parser.add_argument('--variant')
    args = parser.parse_args()
    try:
        if args.action == 'authorize':
            authorize(args.comparison, args.evidence, args.max_requests, args.max_characters)
            print('Exact request authorization saved; no generation was started.')
        elif args.action in ('approve', 'reject'):
            review_audio(args.comparison, args.action, args.review_id, args.variant, args.evidence)
            print('Audio decision saved.')
        elif args.action == 'verify':
            print(json.dumps(verify_approved_audio(args.comparison), indent=2))
        else:
            result = generate(args.comparison)
            for variant in result['variants']:
                print('MP3:', (args.comparison.resolve().parent / variant['audio_file']).resolve())
            print('Review:', result.get('review_id', 'existing recording'))
    except (AudioError, subprocess.SubprocessError, OSError, ValueError, KeyError) as error:
        raise SystemExit(str(error)) from None
