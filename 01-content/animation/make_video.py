#!/usr/bin/env python3
"""Deep Six MP3-to-MP4 runner: an approved narration MP3 in, a finished 9:16 video on Drew's Desktop out.

Design: AUTOMATION-DESIGN.md. Recipe and quality bar: VIDEO-FLOW.md. AI roles run through Claude Code
(Opus 5.5, max effort) and, when Claude is out of usage, Codex (GPT-6 Sol, then GPT-6 Astra). Subscription
logins only: no API keys, no paid calls. Videos are copied to the Windows Desktop; no player is ever opened.

When Drew approves an MP3, an agent records his start choice with one command:
  python3 make_video.py start   --episode ID --manifest ../audio/ID/RUN/comparison.json --when now|tonight|later
Then everything runs by itself in a background worker, one video at a time, in the order started:
  prepare, plan (Director), new drawings (Asset maker + Drew), segments (Animator, checks, Reviewer,
  pilot clip when risky), join with the approved outro, render, exact audio, file checks, whole-video
  Reviewer, Desktop copy and board entry. Then it waits for Drew.
Drew's answers, recorded in his words by an agent:
  python3 make_video.py verdict --run RUN --decision approve|notes --says "what Drew said"
Other commands:
  python3 make_video.py status  [--run RUN]     where every video stands; restarts the worker if needed
  python3 make_video.py go      --run RUN        start a "later" video, or retry a parked one
  python3 make_video.py stop    --run RUN        Drew drops a parked or waiting video
  python3 make_video.py full    --episode ID --run RUN [--start S --end E] [--model sol]   start now (old form)
  python3 make_video.py prepare --episode ID --manifest PATH                               word timing only
  python3 make_video.py segment --episode ID --name NAME --start S --end E [--model ...]   one-off model test
  python3 make_video.py render  --scene PATH                     detached render, next free revision
  python3 make_video.py deliver --mp4 PATH --title "Ensign Wasp" Desktop copy, checksum verified
"""
import argparse
import fcntl
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time
import traceback
from datetime import datetime, timedelta
from pathlib import Path

import video_finish as vf

ROOT = Path(__file__).resolve().parent              # 01-content/animation
PROJECT = ROOT.parents[1]                            # deep-six-content
D6_TOOL = PROJECT / 'tools' / 'd6'
CACHE = ROOT / '.cache'
LEARNED = ROOT / 'learned-rules.md'
PROBLEMS = ROOT / 'problems-seen.json'
VERDICTS = ROOT / 'verdicts.jsonl'
EPISODES = ROOT / 'episodes'

# Model ladder (AUTOMATION-DESIGN.md): Opus 5.5 max, then GPT-6 Sol xhigh, then GPT-6 Astra xhigh.
MODELS = {'opus': 'claude-opus-5-5', 'sol': 'gpt-6-sol', 'astra': 'gpt-6-astra', 'sonnet': 'claude-sonnet-5-5'}
PROVIDER = {'opus': 'claude', 'sonnet': 'claude', 'sol': 'codex', 'astra': 'codex'}
EFFORT = {'opus': 'max', 'sonnet': 'high', 'sol': 'xhigh', 'astra': 'xhigh'}
LADDER = ['opus', 'sol', 'astra']
AI_TIME_LIMIT, RENDER_TIME_LIMIT = 3 * 3600, 4 * 3600
TRIES = {'director': 3, 'animator': 3, 'asset': 3, 'render': 2}   # first try plus two retries; render crash: once more
FIX_ROUNDS = 2                                                      # checks/reviewer -> triage -> redo, then park
NIGHT_START_HOUR = 23

PROTECTED = ['scenes', 'vendor', 'fonts', 'tools', 'choreography', 'render-shots.mjs', 'render-frame.mjs', 'render-motion.mjs',
             'brand.json', 'package.json', 'package-lock.json', 'VIDEO-FLOW.md', 'KIT-API.md', 'make_video.py', 'video_finish.py',
             'science-notes.md', 'learned-rules.md', 'problems-seen.json', 'verdicts.jsonl', 'HARNESS-NOTES.md', 'AUTOMATION-DESIGN.md']
APPROVED_FRAMES = ['episodes/D6-01096ba333e3/full/renders/ensign-wasp-v3-keywords.png',
                   'episodes/D6-6c917b49743b/full/renders/full-v2-beats-1.png']
APPROVED_VIDEOS = {'fire-ants-v2': 'episodes/D6-6c917b49743b/full/renders/full-v2.mp4',
                   'ensign-wasp-v1': 'episodes/D6-01096ba333e3/full/renders/ensign-wasp-v3-final.mp4'}
REFERENCE_STRIPS = [('fire-ants-v2', 0), ('fire-ants-v2', 6), ('ensign-wasp-v1', 3)]
HOOK_SCENE = 'episodes/D6-6c917b49743b/hook'
HOOK_SHEETS_SHA256 = ['b7679f26aebe02877df441f9a1fcb3c63bf7a3b477dda447e1248956e2694ede',   # beat sheet of the approved
                      'ac7816be0c68707e166833318649e7a7152223d454c1c400f687388bb48512ea']   # hook, last kit change 19 Oct
STYLE_C = {'selection': 'episodes/D6-6c917b49743b/style-options/options.json', 'option': 'C',
           'sha256': '1497fedce35fb84d7334aaed44e5f129d6757940bf26d8341cab25b0ff666060'}

TOOLS = {  # Claude Code tools per role. Every job can view images; writers get a shell for the renderer.
    'director': 'Read Write Glob Grep Bash(node:*) Bash(ls:*)',
    'animator': 'Bash(node:*) Bash(ls:*) Bash(cat:*) Bash(sed:*) Bash(rg:*) Bash(head:*) Read Write Edit Glob Grep',
    'asset': 'Bash(node:*) Bash(ls:*) Bash(cat:*) Bash(rg:*) Bash(head:*) Read Write Edit Glob Grep WebSearch WebFetch',
    'reviewer': 'Read Glob Grep Bash(node:*) Bash(ls:*)',
    'triage': 'Read Glob Grep',
}
READ_ONLY = {'reviewer', 'triage'}
CLAUDE_LIMIT = re.compile(r'usage limit|hit your (?:\w+ )?limit|limit reached|out of (?:extra )?usage|credit balance is too low', re.I)
CODEX_LIMIT = re.compile(r'hit your usage limit[^"]*?try again at ([^".]+(?:\.\d+)?[^"]*?)(?:\."|")', re.I)
UNAVAILABLE = re.compile(r'not supported|model_not_found|not_found_error|overloaded|529|rate.?limit|429|quota|unavailable|'
                         r'connection (?:error|refused|reset)|could not resolve|network', re.I)


def obj(props, required=None):
    return {'type': 'object', 'additionalProperties': False, 'properties': props, 'required': required or list(props)}


S, N, I, B = {'type': 'string'}, {'type': 'number'}, {'type': 'integer'}, {'type': 'boolean'}
LIST = lambda item: {'type': 'array', 'items': item}
RESULT_SCHEMA = obj({'status': {'type': 'string', 'enum': ['done', 'blocked']}, 'files_written': LIST(S), 'shot_count': I,
                     'self_check_rounds': I, 'longest_still_seconds': N, 'picture_change_median': N,
                     'remaining_issues': LIST(S), 'summary': S})
PLAN_SCHEMA = obj({'status': {'type': 'string', 'enum': ['done', 'blocked']}, 'title': S, 'files_written': LIST(S),
                   'shot_count': I, 'segment_count': I, 'new_assets': LIST(S), 'summary': S})
REVIEW_SCHEMA = obj({'pass': B, 'notes': LIST(obj({'time': N, 'shot': S, 'problem': S, 'fix': S, 'problem_key': S})),
                     'summary': S})
TRIAGE_SCHEMA = obj({'actions': LIST(obj({
    'kind': {'type': 'string', 'enum': ['redo_segment', 'replan_segment', 'caption_timing', 'outro', 'music', 'ask_drew', 'none']},
    'segment': S, 'start': N, 'end': N, 'notes': S, 'problem_key': S, 'problem_title': S, 'rule': S,
    'question': S, 'options': LIST(S)})), 'summary': S})
REPLAN_SCHEMA = obj({'status': {'type': 'string', 'enum': ['done', 'blocked']}, 'summary': S})
ASSET_SCHEMA = obj({'status': {'type': 'string', 'enum': ['done', 'blocked']}, 'files_written': LIST(S), 'drawings': LIST(S),
                    'self_check_rounds': I, 'summary': S})


class Pause(Exception):
    """No model can run now (usage limits). The video waits and resumes by itself."""

    def __init__(self, until, why):
        super().__init__(why)
        self.until, self.why = until, why


class Park(Exception):
    """Retries are used up or something needs Drew. All work is kept; Drew decides."""


class WaitDrew(Exception):
    def __init__(self, what):
        super().__init__(what.get('ask', ''))
        self.what = what


class JobFailed(Exception):
    def __init__(self, model, why):
        super().__init__(why)
        self.model = model


# ---------------------------------------------------------------- small helpers
def now():
    return datetime.now().astimezone()


def stamp(t=None):
    return (t or now()).isoformat(timespec='seconds')


def atomic(path, text):
    path = Path(path)
    tmp = path.with_name(path.name + '.tmp')
    tmp.write_text(text)
    os.replace(tmp, path)


def wjson(path, data):
    atomic(path, json.dumps(data, indent=1) + '\n')


def rjson(path, default=None):
    path = Path(path)
    return json.loads(path.read_text()) if path.exists() else default


def rel(p):
    return os.path.relpath(Path(p).resolve(), ROOT)


def sha(path):
    return vf.sha(path)


def node(*args, timeout=3600):
    try:
        proc = subprocess.run(['node', *args], cwd=ROOT, capture_output=True, text=True, timeout=timeout)
    except subprocess.TimeoutExpired:
        return 'timeout', 'timed out'
    return proc.returncode, (proc.stdout + proc.stderr).strip()


def clean_env(provider):
    """Subscription logins only. Drop API keys so nothing is billed per call, and drop the calling session's markers."""
    env = dict(os.environ)
    for key in list(env):
        if key.startswith('ANTHROPIC_') or key.startswith('OPENAI_') or key == 'AI_AGENT' or (
                key.startswith('CLAUDE') and key != 'CLAUDE_CONFIG_DIR'):
            env.pop(key)
    return env


MONTHS = {m: i + 1 for i, m in enumerate('jan feb mar apr may jun jul aug sep oct nov dec'.split())}


def parse_reset(text, current=None):
    """Reset time from a usage-limit message, or None."""
    current = current or now()
    m = re.search(r'\|(\d{10})\b', text)
    if m:
        return datetime.fromtimestamp(int(m.group(1))).astimezone()
    m = re.search(r'(?:resets?|try again)(?: at)?\s+(?:([A-Za-z]{3,9})\.? (\d{1,2})(?:st|nd|rd|th)?,? (?:(\d{4}),? )?)?'
                  r'(\d{1,2})(?::(\d{2}))?\s*([ap])\.?m\.?', text, re.I)
    if not m:
        return None
    month, day, year, hh, mm, ap = m.groups()
    hour = int(hh) % 12 + (12 if ap.lower() == 'p' else 0)
    when = current.replace(hour=hour, minute=int(mm or 0), second=0, microsecond=0)
    if month and day and month[:3].lower() in MONTHS:
        when = when.replace(year=int(year) if year else when.year, month=MONTHS[month[:3].lower()], day=int(day))
    elif when <= current:
        when += timedelta(days=1)
    return when


def tonight(current=None):
    current = current or now()
    t = current.replace(hour=NIGHT_START_HOUR, minute=0, second=0, microsecond=0)
    return t if t > current else t + timedelta(days=1)


# ---------------------------------------------------------------- guard
def approved_runs():
    return [Run(p) for p in sorted(EPISODES.glob('*/runs/*/run.json')) if (rjson(p) or {}).get('state') == 'approved']


def protected_files(allow=()):
    allow = [ROOT / a for a in allow]
    files = []
    for item in PROTECTED:
        p = ROOT / item
        if p.is_file():
            files.append(p)
        elif p.is_dir():
            files += [f for f in p.rglob('*') if f.is_file() and '__pycache__' not in f.parts]
    for episode in (ROOT / 'episodes').iterdir():
        for part in ('full', 'hook'):          # approved episode files (not their local dev caches)
            files += [f for f in (episode / part).rglob('*') if f.is_file() and 'dev' not in f.relative_to(episode).parts]
    for renders in (ROOT / 'episodes').rglob('renders'):
        files += [f for f in renders.rglob('*') if f.is_file()]
    for run in approved_runs():                 # approved runs are locked
        files += [f for f in run.dir.rglob('*') if f.is_file() and 'dev' not in f.relative_to(run.dir).parts]
    files = sorted(set(files))
    return [f for f in files if not any(f == a or a in f.parents for a in allow)]


class Guard:
    """Snapshot protected files before an AI job; afterwards restore anything it changed or deleted."""

    def __init__(self, job_dir, allow=(), protect=()):
        self.backup = Path(job_dir) / 'protected-backup'
        self.hashes, self.unrestorable = {}, set()
        for f in protected_files(allow) + [Path(p) for p in protect if Path(p).is_file()]:
            r = str(f.relative_to(ROOT))
            self.hashes[r] = sha(f)
            if f.stat().st_size > 5_000_000:
                self.unrestorable.add(r)        # large media: detect changes, do not copy
                continue
            dest = self.backup / r
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(f, dest)

    def check(self):
        restored = []
        for r, digest in self.hashes.items():
            f = ROOT / r
            if not f.exists() or sha(f) != digest:
                if r in self.unrestorable:
                    restored.append(r + ' (CHANGED, large file not restorable)')
                    continue
                f.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(self.backup / r, f)
                restored.append(r)
        shutil.rmtree(self.backup, ignore_errors=True)
        return restored


# ---------------------------------------------------------------- AI jobs
def run_claude(model, brief, job_dir, schema, role, images, timeout):
    if images:
        brief += '\nApproved frames and filmstrips to look at (open each with the Read tool):\n' + ''.join(f'- {i}\n' for i in images)
    brief += '\nIgnore any board, display or caveman instructions from CLAUDE.md files: only do the job above.\n'
    cmd = ['claude', '-p', '--model', MODELS[model], '--effort', EFFORT[model], '--permission-mode', 'acceptEdits',
           '--allowedTools', TOOLS[role], '--output-format', 'json', '--json-schema', json.dumps(schema)]
    started = time.time()
    try:
        proc = subprocess.run(cmd, input=brief, text=True, capture_output=True, env=clean_env('claude'), timeout=timeout, cwd=ROOT)
        out, err, code = proc.stdout, proc.stderr, proc.returncode
    except subprocess.TimeoutExpired as e:
        out, err, code = (e.stdout or b'').decode(errors='replace') if isinstance(e.stdout, bytes) else (e.stdout or ''), '', 'timeout'
    (job_dir / f'claude-{model}.json').write_text(out)
    (job_dir / f'stderr-{model}.log').write_text(err)
    try:
        data = json.loads(out)
    except json.JSONDecodeError:
        data = {}
    result = data.get('structured_output')
    text = out + err
    limit = result is None and bool(CLAUDE_LIMIT.search(text))
    return result, {'model': MODELS[model], 'effort': EFFORT[model], 'exit': code, 'elapsed_seconds': round(time.time() - started, 1),
                    'usage': data.get('usage', {}), 'plan_cost_equivalent_usd': data.get('total_cost_usd'),
                    'limit': limit, 'reset': stamp(parse_reset(text)) if limit and parse_reset(text) else None,
                    'unavailable': result is None and not limit and code != 'timeout' and bool(UNAVAILABLE.search(text))}


def run_codex(model, brief, job_dir, schema, role, images, timeout):
    schema_file = job_dir / 'result-schema.json'
    schema_file.write_text(json.dumps(schema, indent=1))
    final = job_dir / f'final-{model}.json'
    events = job_dir / f'events-{model}.jsonl'
    cmd = ['codex', 'exec', '--ignore-user-config', '--skip-git-repo-check', '-m', MODELS[model],
           '-c', f'model_reasoning_effort="{EFFORT[model]}"', '-c', 'approval_policy="never"',
           '-s', 'read-only' if role in READ_ONLY else 'workspace-write', '-C', str(ROOT)]
    for image in images:
        cmd += ['-i', str(ROOT / image)]
    cmd += ['--json', '--output-schema', str(schema_file), '-o', str(final), '-']
    started = time.time()
    with events.open('w') as out, (job_dir / f'stderr-{model}.log').open('w') as err:
        try:
            code = subprocess.run(cmd, input=brief, text=True, stdout=out, stderr=err, env=clean_env('codex'),
                                  timeout=timeout, cwd=ROOT).returncode
        except subprocess.TimeoutExpired:
            code = 'timeout'
    text = events.read_text(errors='replace') + (job_dir / f'stderr-{model}.log').read_text(errors='replace')
    usage = {}
    for line in events.read_text(errors='replace').splitlines():
        if '"usage"' in line:
            try:
                usage = json.loads(line).get('usage', usage) or usage
            except json.JSONDecodeError:
                pass
    result = None
    if final.exists():
        try:
            result = json.loads(final.read_text())
        except json.JSONDecodeError:
            result = None
    m = CODEX_LIMIT.search(text) if result is None else None
    reset = parse_reset('try again at ' + m.group(1)) if m else None
    return result, {'model': MODELS[model], 'effort': EFFORT[model], 'exit': code, 'elapsed_seconds': round(time.time() - started, 1),
                    'usage': usage, 'limit': bool(m), 'reset': stamp(reset) if reset else None,
                    'limit_text': m.group(1).strip() if m else None,
                    'unavailable': result is None and not m and code != 'timeout' and bool(UNAVAILABLE.search(text))}


RUNNERS = {'claude': run_claude, 'codex': run_codex}


def agent_job(role, brief, job_dir, schema, images=(), allow=(), ladder=None, start_at=None, timeout=AI_TIME_LIMIT, protect=()):
    """One AI job up the model ladder. Returns (result, model). A Claude limit or an unavailable model moves down
    the ladder; a Codex limit blocks Sol and Astra together, so the job raises Pause until the first known reset.
    A quality failure (no usable result, timeout, crash) raises JobFailed: the caller retries with the same model."""
    job_dir = Path(job_dir)
    job_dir.mkdir(parents=True, exist_ok=True)
    (job_dir / 'brief.md').write_text(brief)
    ladder = ladder or LADDER
    order = ladder[ladder.index(start_at):] if start_at in ladder else ladder
    guard = Guard(job_dir, allow, protect)
    runs, resets, outcome = [], {}, None
    try:
        for model in order:
            provider = PROVIDER[model]
            if provider in resets:
                continue
            print(json.dumps({'job': rel(job_dir), 'role': role, 'model': MODELS[model], 'at': stamp()}), flush=True)
            result, meta = RUNNERS[provider](model, brief, job_dir, schema, role, list(images), timeout)
            runs.append(meta)
            if result is not None:
                outcome = (result, model)
                return outcome
            if meta['limit']:
                resets[provider] = meta['reset']
                continue
            if meta['unavailable']:
                continue
            raise JobFailed(model, f"{MODELS[model]} gave no usable result (exit {meta['exit']}).")
        known = sorted(r for r in resets.values() if r)
        until = datetime.fromisoformat(known[0]) if known else now() + timedelta(hours=1)
        why = 'No model available: ' + ', '.join(f"{m['model']} {'usage limit' if m['limit'] else 'unavailable'}" for m in runs)
        raise Pause(until, why)
    finally:
        restored = guard.check()
        wjson(job_dir / 'report.json', {'role': role, 'ok': outcome is not None, 'model': outcome[1] if outcome else None,
                                        'result': outcome[0] if outcome else None, 'runs': runs,
                                        'protected_files_restored': restored})


# ---------------------------------------------------------------- the run ledger
class Run:
    """run.json: every step saves its files, then marks itself done. Re-running resumes; finished work is kept."""

    def __init__(self, path):
        self.path = Path(path)
        self.dir = self.path.parent
        self.d = rjson(self.path)

    @property
    def name(self):
        return self.d['run']

    @property
    def state(self):
        return self.d['state']

    def save(self):
        wjson(self.path, self.d)
        atomic(self.dir / 'STATUS.md', status_note(self))

    def event(self, text, **extra):
        self.d.setdefault('history', []).append({'at': stamp(), 'event': text, **extra})
        print(json.dumps({'run': self.name, 'event': text, **extra}), flush=True)

    def set(self, state, **fields):
        self.d['state'] = state
        for key in ('waiting_for', 'reason', 'not_before'):
            self.d[key] = fields.pop(key, None)
        self.d.update(fields)
        self.event(f'state: {state}', **{k: v for k, v in (('waiting_for', self.d['waiting_for']), ('reason', self.d['reason'])) if v})
        self.save()


def all_runs():
    return [Run(p) for p in sorted(EPISODES.glob('*/runs/*/run.json'))]


def find_run(name):
    found = [r for r in all_runs() if r.name == name]
    if not found:
        sys.exit(f'No run named {name}. See: python3 make_video.py status')
    return found[0]


def new_run(episode, run, manifest, when, title=None, start=0.0, end=None, limits='', exclude=(), ladder=None):
    from_tools = str(PROJECT / 'tools')
    if from_tools not in sys.path:
        sys.path.insert(0, from_tools)
    from d6_audio import AudioError, verify_approved_audio
    manifest = Path(manifest).resolve()
    try:
        audio = verify_approved_audio(manifest)
    except (AudioError, OSError, ValueError, KeyError) as error:
        sys.exit(f'The MP3 is not approved or no longer matches its approval: {error}')
    if audio['approved_narration_id'] != episode:
        sys.exit('That approved MP3 belongs to another episode.')
    if not re.fullmatch(r'[a-z0-9-]+', run):
        sys.exit('Run names use lowercase letters, numbers and hyphens.')
    folder = EPISODES / episode / 'runs' / run
    if (folder / 'run.json').exists():
        sys.exit(f'Run {run} exists. Use: python3 make_video.py status --run {run}')
    folder.mkdir(parents=True, exist_ok=True)
    created = now()
    r = Run(folder / 'run.json')
    r.d = {'episode': episode, 'run': run, 'manifest': os.path.relpath(manifest, ROOT), 'mp3': os.path.relpath(audio['path'], ROOT),
           'audio_sha256': audio['audio_sha256'], 'audio_seconds': audio['duration_seconds'], 'title': title,
           'when': when, 'created_at': stamp(created), 'queued_at': stamp(created), 'seed': int(created.strftime('%Y%m%d')),
           'range': [start, end], 'limits': limits, 'exclude': list(exclude), 'ladder': ladder or LADDER,
           'state': None, 'step': None, 'steps_done': [], 'segments': [], 'segments_done': [], 'made_by': {}, 'attempts': {},
           'notes': {}, 'seg_model': {}, 'pilot': {'approved': []}, 'renders': [], 'deliveries': [], 'version': 1,
           'fix_rounds': 0, 'fix_rounds_allowed': FIX_ROUNDS, 'history': []}
    if when == 'now':
        r.set('queued')
    elif when == 'tonight':
        t = tonight(created)
        r.set('waiting', not_before=stamp(t), waiting_for=f'start time {t:%a %H:%M}')
    else:
        r.set('waiting', waiting_for="Drew's go")
    return r


# ---------------------------------------------------------------- the worker
LOCK = CACHE / 'worker.lock'


def worker_running():
    CACHE.mkdir(exist_ok=True)
    with open(LOCK, 'a+') as f:
        try:
            fcntl.flock(f, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            return True
        fcntl.flock(f, fcntl.LOCK_UN)
    return False


def ensure_worker():
    """Start the background worker in its own session, so a closed chat cannot stop it."""
    if worker_running():
        return None
    CACHE.mkdir(exist_ok=True)
    log = open(CACHE / 'worker.log', 'a')
    proc = subprocess.Popen([sys.executable, str(ROOT / 'make_video.py'), 'work'], cwd=ROOT, stdin=subprocess.DEVNULL,
                            stdout=log, stderr=subprocess.STDOUT, start_new_session=True)
    return proc.pid


def due(runs, current=None):
    current = current or now()
    ready = [r for r in runs if r.state == 'queued' or (
        r.state in ('waiting', 'paused') and r.d.get('not_before') and datetime.fromisoformat(r.d['not_before']) <= current)]
    return sorted(ready, key=lambda r: r.d['queued_at'])


def recover(runs):
    """A video left 'running' by a dead worker resumes from its last finished piece."""
    for r in runs:
        if r.state == 'running' and r.d.get('worker_pid') != os.getpid() and not vf.alive(r.d.get('worker_pid') or 0, 'make_video.py'):
            r.set('queued')
            r.event('resumed after the worker stopped (crash, restart or closed session)')
            r.save()


def cmd_work(args):
    CACHE.mkdir(exist_ok=True)
    lock = open(LOCK, 'a+')
    try:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except BlockingIOError:
        print('Another worker is running.')
        return
    print(json.dumps({'worker': os.getpid(), 'started': stamp()}), flush=True)
    while True:
        runs = all_runs()
        recover(runs)
        ready = due(runs)
        if ready:
            run_one(ready[0])
            continue
        later = [datetime.fromisoformat(r.d['not_before']) for r in runs if r.state in ('waiting', 'paused') and r.d.get('not_before')]
        if not later:
            print(json.dumps({'worker': os.getpid(), 'idle': stamp()}), flush=True)
            return
        time.sleep(max(1, min(60, (min(later) - now()).total_seconds())))


def run_one(r):
    r.set('running', worker_pid=os.getpid())
    try:
        advance(r)
        last = r.d['deliveries'][-1]
        r.set('waiting_drew', waiting_for={'kind': 'video', 'version': last['version'], 'desktop': last['name'], 'mp4': last['source'],
                                           'ask': f"Watch '{last['name']}' on the Desktop: approve, or give notes."})
    except Pause as p:
        r.d['seg_model'] = {}                    # after a usage reset every job starts at Opus again
        r.set('paused', not_before=stamp(p.until), waiting_for=f'usage reset {p.until:%a %H:%M}', reason=p.why)
    except Park as p:
        r.set('parked', reason=str(p), waiting_for='Drew decides: go (try again) or stop')
    except WaitDrew as w:
        r.set('waiting_drew', waiting_for=w.what)
    except Exception as e:  # anything unexpected parks the video with its reason; work is kept
        (r.dir / 'last-error.txt').write_text(traceback.format_exc())
        r.set('parked', reason=f'Runner error: {type(e).__name__}: {e}'[:600], waiting_for='Drew decides: go (try again) or stop')


# ---------------------------------------------------------------- inputs
def learned_rules():
    return LEARNED.read_text() if LEARNED.exists() else ''


def past_verdicts(limit=12):
    if not VERDICTS.exists():
        return 'none yet'
    lines = [json.loads(x) for x in VERDICTS.read_text().splitlines() if x.strip()]
    drew = [v for v in lines if v.get('by') == 'Drew'][-limit:]
    return '\n'.join(f"  - {v['at'][:10]} {v['episode']} {v.get('item', '')}: {v['decision']}: \"{v['said']}\"" for v in drew) or 'none yet'


def problem_list():
    probs = rjson(PROBLEMS, {})
    return '\n'.join(f'  - {k}: {p["title"]}' for k, p in probs.items())


def narration_limits(episode):
    md = PROJECT / '01-content' / 'approved-narrations' / f'{episode}.md'
    if md.exists():
        m = re.search(r'^Limits: (.+)$', md.read_text(), re.M)
        if m:
            return m.group(1).strip()
    return 'see science-notes.md.'


def reference_strips():
    """5-fps strips of the approved videos, made once (git-ignored)."""
    out = []
    for name, index in REFERENCE_STRIPS:
        f = CACHE / 'reference' / f'{name}-{index:02d}.png'
        if not f.exists():
            f.parent.mkdir(parents=True, exist_ok=True)
            vf.filmstrips(ROOT / APPROVED_VIDEOS[name], f.parent / name)
        out.append(rel(f))
    return out


def scene_settings(r):
    return {'schema_version': 1, 'episode_id': r.d['episode'], 'width': 1080, 'height': 1920, 'fps': 30, 'seed': r.d['seed'],
            'timing': 'words.json', 'shot_list': 'shot-list.json',
            'approved_audio': {'manifest': r.d['manifest'], 'sha256': r.d['audio_sha256']},
            'brand_profile': 'brand.json', 'approved_style': dict(STYLE_C), 'caption_center_y': 1420,
            'motion_blur': {'samples': 5, 'shutter_seconds': 0.0125}}


def audio_end(r):
    return int(r.d['audio_seconds'] * 1000) / 1000     # the renderer refuses an end past the MP3


def words_of(r):
    return rjson(r.dir / 'words.json')


def lesson_words(r):
    w = words_of(r)['words']
    a, b = r.d['lesson_range']
    return [(i, x) for i, x in enumerate(w) if a - 0.05 <= x['start'] < b]


# ---------------------------------------------------------------- briefs
PLAN_BRIEF = """You are the Deep Six video director. Your working root is the folder `01-content/animation`.
Plan the lesson of a pest-education short for episode {episode}, narration time {start:.2f} to {end:.2f} seconds, in the approved
cut-paper style C. Match the pace and quality bar in VIDEO-FLOW.md. You plan pictures; you do not write scene code.
{outro_note}
Narration words with their index in words.json and start time in seconds:
{word_lines}

Read these first: VIDEO-FLOW.md, choreography/director-prompt.md, KIT-API.md (what the kit and finished sets already draw),
science-notes.md and learned-rules.md (rules learned from Drew's verdicts; follow every one). Episode limits: {limits}
Drew's past verdicts, in his words:
{verdicts}
Prefer the proven sets and shot types of the approved videos; invent a new composition only when the narration needs one.
{exclusions}{errors}
Write exactly these three files:
1. {shot_list}: every shot, in the director prompt's JSON shape, with absolute times. Every phrase gets a visible action
   landing on its word (each beat's "at" is the start time of its word). Shots cover {start:.2f} to {end:.2f} with no gaps, none
   longer than 2 seconds; shots in the first sentence last 0.7 to 1.5 seconds. Add a top-level "new_assets" list naming any
   drawing the kit and sets do not have yet (empty when the kit has everything).
2. {segments}: a JSON list of {{"name", "start", "end"}} segments named {run}-seg01, {run}-seg02 and so on. They must be
   contiguous, cover {start:.2f} to {end:.2f} exactly, cut only in pauses between sentences, and last 6 to 15 seconds each.
3. {groups}: a JSON list of caption groups; each group is a list of word indexes from the list above. Cover every word once,
   in order, one to four words per group, broken at natural phrases.

Never modify existing files. When finished, reply with the JSON summary the output schema asks for. "title" is a short title for
the video's file name, 2 to 4 plain words such as "Ensign Wasp" or "Fire Ants Drought".
"""

OUTRO_NOTE = """The narration ends with the Deep Six sign-off ("Helping you understand pests. Deep Six Pest Control.") from {outro:.2f} s.
The approved outro animation covers it automatically: plan no shots and no captions for it. The last lesson picture stays on
screen until {outro:.2f} s, when a cream-paper wipe starts, so keep the final teaching shot alive and readable until then.
"""

SEGMENT_BRIEF = """You are the Deep Six video animator. Your working root is the folder `01-content/animation`.
Make one segment of a pest-education short in the approved cut-paper style C. It must match the quality, pace and look of the
approved reference videos described in VIDEO-FLOW.md.

Segment: episode {episode}, absolute narration time {start:.2f} to {end:.2f} seconds.
Narration words in this segment, with start times in seconds:
{word_lines}

Read these first, in order:
1. VIDEO-FLOW.md: the recipe and the quality bar.
2. choreography/director-prompt.md, then choreography/animator-prompt.md.
3. KIT-API.md: everything the kit and the finished sets can draw. Open a scene file only to check one specific function.
4. scenes/hook-fire-ant-drought.mjs: a complete approved example. Skim it for structure.
5. science-notes.md and learned-rules.md (rules learned from Drew's verdicts; follow every one). Episode limits: {limits}
{assets}{exclusions}
Write exactly these files:
- {shot_list}: your shot list for this segment, absolute times, in the director prompt's JSON shape.
- {module}: the scene module. Export createScene(config, timing) returning
  {{ duration, blurWindows, drawWorld(ctx, t), drawOverlay(ctx, t), draw(ctx, t) }}. t is absolute narration time.
  Build captions with createCaptions(timing.words, timing.caption_groups, {{ texture, centerY: config.caption_center_y ?? 1420 }}).
The scene settings already exist at {scene_json}; do not edit them. Scratch files may go in {dev_dir}.

Self-check loop. Required; repeat until every check passes, at most 6 rounds:
1. Run `node render-shots.mjs {scene_json} --sheet`, then open every sheet with your image viewing tool. Each tile must show
   the words printed under it; nothing important cut off or under the caption; no overlapping characters; correct anatomy.
2. Run `node render-shots.mjs {scene_json} --at <seconds,...>` for transitions and holds, and view those frames.
3. Run `node render-shots.mjs {scene_json} --check-motion`. Targets: longest_still_seconds at most 0.35;
   picture_change_half_second_median at least 0.15.

Keep usage low: view each sheet once per round, use --at for single-frame checks, and do not re-read files you have read.

Rules:
- Never modify, rename or delete existing files, except your own files named above. Put any kit additions inside your module.
- No network and no installs. Keep every frame a pure function of t.
- No on-screen words except the kit's captions. A question mark or X is allowed only where the narration questions or negates.

When finished, reply with the JSON summary the output schema asks for.
"""

PLANNED_SEGMENT_NOTE = """
The director already planned this segment. Its shots are in {shot_list} (from the whole-video plan {plan}).
Implement those shots faithfully; refine details only to fix problems you see in your checks. Do not rewrite {shot_list}.
Earlier segments in this video, for continuity (same sets, characters and camera language): {previous}
"""

RETRY_NOTE = """
This is try {attempt} for this segment. Your previous try is in {module}; you may edit it. Fix every problem below first,
then run the whole self-check loop again:
{notes}
"""

REVIEW_BRIEF = """You are the Deep Six video reviewer: a fresh pair of eyes. You did not make this video. You can send work back;
you can never approve it. Only Drew approves.

Watch {what}, narration {start:.2f} to {end:.2f} s. Its filmstrips show 5 frames per second, left to right, top row then bottom
row, 6 seconds per strip, starting at {start:.2f} s:
{strips}
The approved Deep Six videos' strips show what good looks like:
{refs}
Shot plan: {shot_list}. Narration words and start times:
{word_lines}
Words the timing models disagreed on (check their captions first): {flagged}

Check, in this order:
1. Every problem caught before (problems-seen.json) and every rule in learned-rules.md.
2. Each planned beat is visible on its word; the caption shows the spoken words and the highlighted word is the one being said.
3. Constant motion: something moves in every frame; holds keep drifting; no jumpy camera; cuts land on new sentences or ideas.
4. Composition: the subject fills the frame; small things shown in close-up; nothing important below y 1250, under the caption
   or cut off; no overlapping characters or props.
5. Anatomy and science: science-notes.md; episode limits: {limits}. No invented numbers, mechanisms, depths, temperatures or
   treatment advice.
{extra}
To look closer, render single frames: node render-shots.mjs {scene_json} --at <seconds,...> and open them.
Do not write or change any file except those frame renders. Reply with the JSON the output schema asks for: "pass" is true only
when nothing needs fixing; each note gives the time in seconds, the shot id, the problem, the fix, and a problem_key (reuse a
key from problems-seen.json for the same problem, otherwise a new short kebab-case key).
"""

TRIAGE_BRIEF = """You are the Deep Six triage editor for episode {episode}. Map each problem below to the stage that fixes it and the
time range it affects. Do not fix anything yourself and do not write any file.

Problems, from {source}:
{problems}

The video's parts (absolute narration seconds):
{parts}
Shot plan: {shot_list}. Word timings: {words}. Known problem keys (problems-seen.json):
{keys}

Action kinds:
- redo_segment: a shot problem. The Animator redoes that segment with your notes; untouched segments stay as they are.
- replan_segment: a plan problem (wrong picture for the words, missing idea). The Director re-plans that segment's shots first.
- caption_timing: captions or word timing are off.
- outro: the outro, its timing or its top caption.
- music: any note about music. It is saved for later; there is no music yet.
- ask_drew: the note is unclear. Give one multiple-choice question with 2 to 4 options.
- none: nothing to change; say why in notes.
Give one action per problem and segment. For each: kind, segment (a segment name, or "" when none), start and end seconds,
notes (exact fix instructions for the Animator or Director), problem_key (reuse a known key for the same problem), problem_title
(a short plain description), rule (one sentence a future animator should follow to avoid it), question and options (ask_drew
only, otherwise "" and []).
"""

REPLAN_BRIEF = """You are the Deep Six video director. Your working root is the folder `01-content/animation`. Re-plan the shots of
one segment of episode {episode}, {start:.2f} to {end:.2f} seconds, because of these notes:
{notes}
The current whole-video plan is {plan}; keep the other segments' shots and the sets they use in mind for continuity.
Narration words in this segment with start times:
{word_lines}
Read choreography/director-prompt.md, KIT-API.md, science-notes.md and learned-rules.md. Episode limits: {limits}
Write exactly one new file, {out}: {{"shots": [...]}} with this segment's shots in the director prompt's JSON shape, absolute
times, covering {start:.2f} to {end:.2f} with no gaps, each beat's "at" on its word's start time, no shot over 2 seconds.
Never modify existing files. Reply with the JSON the output schema asks for.
"""

ASSET_BRIEF = """You are the Deep Six asset maker. Your working root is the folder `01-content/animation`. Before any shot uses
them, draw these new pieces for episode {episode} in the approved cut-paper style C:
{needed}

Read first: KIT-API.md (style and kit), scenes/wasp-kit.mjs and scenes/home-world.mjs (the newest researched pieces, built the
same way), science-notes.md, learned-rules.md, and the approved narration with its sources: {narration}.
Check anatomy against reliable sources (university extension services, museum collections): shape, colour, proportions, number
and placement of legs, wings and antennae. Scale and poses may be illustrative; anatomy may not.
{notes}
Write exactly these new files:
1. scenes/{run}-assets.mjs: one exported drawing function per piece, built from paper pieces with cut(), shadows and grain.
2. scenes/{run}-asset-sheet.mjs: a test scene (module contract in KIT-API.md) for 0 to 12 seconds: each new piece large and
   alone for about 1.5 s, beside a fire ant from the kit at the same scale; then a walk or movement test for the last 3 s.
   drawOverlay draws nothing.
3. {assets_dir}/shot-list.json: {{"shots": [{{"id", "start", "end", "words", "beats": [{{"word", "at", "action"}}]}}]}} with one beat
   per piece at the time it shows, so `--sheet` shows one tile per piece. "word" is the piece's name.
4. {assets_dir}/API.md: a short reference for the animator: each exported function, its parameters, its size at scale 1.
5. {assets_dir}/sources.json: [{{"url", "title", "used_for"}}] for every source you used.
6. {assets_dir}/science-notes.md: the facts and limits behind these drawings, with links, a few lines each.
The scene settings exist at {scene_json}. Check your work: node render-shots.mjs {scene_json} --sheet, view every tile, fix,
repeat, at most 6 rounds. Never modify existing files except your own files above. Reply with the JSON the schema asks for.
"""


def word_lines(words, a, b, index=False):
    return '\n'.join(f"  {'[%d] ' % i if index else ''}{w['start']:6.2f}  {w['text']}" for i, w in enumerate(words) if a - 0.05 <= w['start'] < b)


def exclusions(r):
    x = ''.join(f'- Do not open {e}. It is withheld for this run.\n' for e in r.d.get('exclude', []))
    return '\nWithheld files:\n' + x if x else ''


# ---------------------------------------------------------------- steps
def step_prepare(r):
    tools = str(PROJECT / 'tools')
    if tools not in sys.path:
        sys.path.insert(0, tools)
    from d6_audio import AudioError, verify_approved_audio
    try:
        audio = verify_approved_audio(ROOT / r.d['manifest'])
    except (AudioError, OSError, ValueError, KeyError) as error:
        raise Park(f'The MP3 no longer matches its approval: {error}')
    if audio['audio_sha256'] != r.d['audio_sha256']:
        raise Park('The MP3 changed after the video was started; its fingerprint no longer matches.')
    words_file = r.dir / 'words.json'
    if not words_file.exists():
        approved = ROOT / 'episodes' / r.d['episode'] / 'full' / 'words.json'
        if approved.exists() and (rjson(approved) or {}).get('audio_sha256') == r.d['audio_sha256']:
            shutil.copyfile(approved, words_file)
            r.event('word timing reused from the episode folder (same MP3 fingerprint)')
        else:
            proc = subprocess.run([sys.executable, str(ROOT / 'tools' / 'align_words.py'), '--manifest', str(ROOT / r.d['manifest']),
                                   '--out', str(words_file)], cwd=ROOT, capture_output=True, text=True, timeout=3600)
            (r.dir / 'align.log').write_text(proc.stdout + proc.stderr)
            if proc.returncode or not words_file.exists():
                raise Park('Word timing failed; see align.log.')
    words = rjson(words_file)
    if words.get('audio_sha256') != r.d['audio_sha256']:
        raise Park('words.json belongs to a different MP3.')
    w = words['words']
    i0 = vf.find_signoff(w)
    start, end = r.d['range']
    end = audio_end(r) if end is None else end
    if i0 is not None and end >= w[i0]['start']:
        outro = vf.outro_start_frame(w) / vf.FPS     # first frame after the last lesson word
        r.d.update(signoff=i0, lesson_range=[start, round(outro, 4)], video_range=[start, audio_end(r)])
    elif r.d['range'][1] is None:
        raise Park('The narration does not end with the approved sign-off ("Helping you understand pests. Deep Six Pest Control."). '
                   'Every full narration needs it once.')
    else:
        r.d.update(signoff=None, lesson_range=[start, end], video_range=[start, end])
    r.d['limits'] = (r.d.get('limits') or narration_limits(r.d['episode'])).rstrip('. ')
    r.d['flagged_words'] = words.get('low_confidence_words', [])
    reference_strips()


def check_plan(r):
    """Errors in the Director's plan (sent back to the Director), or [] when it passes."""
    errors = []
    paths = {k: r.dir / f for k, f in (('shots', 'shot-list.json'), ('segments', 'segments.json'), ('groups', 'caption-groups.json'))}
    try:
        plan, segs, groups = (json.loads(paths[k].read_text()) for k in ('shots', 'segments', 'groups'))
    except (OSError, json.JSONDecodeError) as e:
        return [f'Plan files missing or not valid JSON: {e}']
    w = words_of(r)['words']
    a, b = r.d['lesson_range']
    in_range = [i for i, x in lesson_words(r)]
    if [i for g in groups for i in g] != in_range or any(not 1 <= len(g) <= 4 for g in groups):
        errors.append('Caption groups must cover every lesson word once, in order, one to four words each.')
    if not segs or abs(segs[0]['start'] - a) > 0.3 or abs(segs[-1]['end'] - b) > 0.3 or any(
            abs(x['end'] - y['start']) > 1e-6 for x, y in zip(segs, segs[1:])):
        errors.append(f'Segments must be contiguous and cover {a:.2f} to {b:.2f} s.')
    for n, s in enumerate(segs, 1):
        if s.get('name') != f"{r.name}-seg{n:02d}":
            errors.append(f"Segment {n} must be named {r.name}-seg{n:02d}.")
        length = s['end'] - s['start']
        if (b - a) >= 6 and not 6 - 0.01 <= length <= 15 + 0.01:
            errors.append(f"Segment {s.get('name')} lasts {length:.2f} s; segments last 6 to 15 s.")
    for x, y in zip(segs, segs[1:]):
        cut = x['end']
        ok = any(w[i]['text'].rstrip('"”’)').endswith(('.', '?', '!')) and w[i]['end'] - 0.15 <= cut <= w[i + 1]['start'] + 0.15
                 for i in range(len(w) - 1))
        if not ok:
            errors.append(f'Segment cut at {cut:.2f} s is not in a pause between sentences.')
    shots = plan.get('shots', []) if isinstance(plan, dict) else []
    if not shots:
        errors.append('The shot list has no shots.')
        return errors
    starts = [x['start'] for x in w]
    first_sentence_end = next((x['end'] for x in w if x['start'] >= a and x['text'].endswith(('.', '?', '!'))), a)
    if shots[0]['start'] > a + 0.05 or shots[-1]['end'] < b - 0.05:
        errors.append(f'Shots must cover {a:.2f} to {b:.2f} s.')
    for s, t in zip(shots, shots[1:]):
        if t['start'] < s['end'] - 0.02 or t['start'] - s['end'] > 0.25:
            errors.append(f"Shots {s['id']} and {t['id']} overlap or leave a gap.")
    for s in shots:
        length = s['end'] - s['start']
        if length > 2.1:
            errors.append(f"Shot {s['id']} lasts {length:.2f} s; no shot over 2 s.")
        if s['start'] < first_sentence_end - 0.05 and length > 1.6:
            errors.append(f"Hook shot {s['id']} lasts {length:.2f} s; hook shots last 0.7 to 1.5 s.")
        if not s.get('beats'):
            errors.append(f"Shot {s['id']} has no beats.")
        for beat in s.get('beats', []):
            if not str(beat.get('word', '')).startswith('(') and min(abs(beat['at'] - x) for x in starts) > 0.021:
                errors.append(f"Shot {s['id']} beat '{beat.get('word')}' at {beat['at']} is not on a word start.")
    return errors[:25]


def step_plan(r):
    files = [r.dir / 'shot-list.json', r.dir / 'segments.json', r.dir / 'caption-groups.json']
    a, b = r.d['lesson_range']
    w = words_of(r)['words']
    errors, model = [], r.d['seg_model'].get('plan')
    while True:
        if all(f.exists() for f in files):
            errors = check_plan(r)
            if not errors and r.d.get('title'):
                break
        tries = r.d['attempts'].get('plan', 0)
        if tries >= TRIES['director']:
            raise Park('The Director\'s plan failed its checks 3 times: ' + '; '.join(errors[:5]))
        if any(f.exists() for f in files):          # keep the failed try as evidence, out of the Director's way
            keep = r.dir / f'plan-try-{tries}'
            keep.mkdir(exist_ok=True)
            for f in files:
                if f.exists():
                    f.rename(keep / f.name)
        err = ('\nYour previous plan failed these checks; fix every one:\n' + ''.join(f'- {e}\n' for e in errors)) if errors else ''
        brief = PLAN_BRIEF.format(episode=r.d['episode'], start=a, end=b, word_lines=word_lines(w, a, b, index=True),
                                  outro_note=OUTRO_NOTE.format(outro=b) if r.d.get('signoff') is not None else '',
                                  limits=r.d['limits'], verdicts=past_verdicts(), exclusions=exclusions(r), errors=err,
                                  shot_list=rel(files[0]), segments=rel(files[1]), groups=rel(files[2]), run=r.name)
        try:
            result, model = agent_job('director', brief, r.dir / f'plan-job-{tries + 1}', PLAN_SCHEMA, APPROVED_FRAMES,
                                      ladder=r.d['ladder'], start_at=model)
        except JobFailed as e:
            result, model = {'status': 'blocked', 'summary': str(e), 'title': '', 'new_assets': []}, e.model
        r.d['attempts']['plan'] = tries + 1
        r.d['seg_model']['plan'] = model
        r.d['made_by']['plan'] = model
        r.save()
        if result.get('status') != 'done':
            errors = [f"The Director reported it could not finish: {result.get('summary', '')}"]
            continue
        title = re.sub(r'[^A-Za-z0-9 -]', '', result.get('title', '')).strip()
        if not 2 <= len(title) <= 40:
            errors = check_plan(r) + ['Give a short title of 2 to 4 plain words.']
            continue
        r.d['title'] = r.d.get('title') or title
        r.d['new_assets'] = result.get('new_assets') or (rjson(files[0], {}) or {}).get('new_assets', [])
    segs = json.loads(files[1].read_text())
    segs[0]['start'], segs[-1]['end'] = a, b
    r.d['segments'] = segs
    groups = json.loads(files[2].read_text())
    words = words_of(r)
    keep = [g for g in words['caption_groups'] if not (a - 0.05 <= words['words'][g['words'][0]]['start'] < b)]
    if r.d.get('signoff') is not None:
        keep = [g for g in keep if g['words'][0] >= r.d['signoff']]
    words['caption_groups'] = sorted(keep + [{'words': g} for g in groups], key=lambda g: g['words'][0])
    wjson(r.dir / 'words.json', words)
    r.event('plan checked', shots=len(json.loads(files[0].read_text())['shots']), segments=len(segs), title=r.d['title'])


def step_assets(r):
    needed = r.d.get('new_assets') or []
    a = r.d.setdefault('assets', {})
    if not needed or a.get('status') == 'approved':
        return
    adir = r.dir / 'assets'
    adir.mkdir(exist_ok=True)
    module, sheet = f'scenes/{r.name}-assets.mjs', f'scenes/{r.name}-asset-sheet.mjs'
    scene = scene_settings(r)
    scene.update({'scene_id': f'{r.name}-asset-sheet', 'module': sheet, 'revision': 'v1', 'output_stem': 'new-drawings',
                  'timing': '../words.json', 'audio_excerpt_start_seconds': 0, 'duration_seconds': min(12, audio_end(r)),
                  'audio_excerpt_end_seconds': min(12, audio_end(r)), 'absolute_time': True})
    wjson(adir / 'scene.json', scene)
    model = r.d['seg_model'].get('assets')
    while True:
        tries = a.get('tries', 0)
        if tries >= TRIES['asset']:
            raise Park('The new drawings failed their checks 3 times. ' + '; '.join(a.get('problems', [])[:4]))
        notes = a.get('notes', []) + a.get('problems', [])
        brief = ASSET_BRIEF.format(episode=r.d['episode'], needed=''.join(f'- {x}\n' for x in needed), run=r.name,
                                   narration=f"../approved-narrations/{r.d['episode']}.md", assets_dir=rel(adir),
                                   scene_json=rel(adir / 'scene.json'),
                                   notes=('\nThis is a redo. Fix these notes first (your previous files are in place; you may edit them):\n'
                                          + ''.join(f'- {n}\n' for n in notes)) if notes else '')
        try:
            result, model = agent_job('asset', brief, adir / f'job-{tries + 1}', ASSET_SCHEMA, APPROVED_FRAMES, ladder=r.d['ladder'],
                                      start_at=model, allow=[module, sheet, rel(adir)])
        except JobFailed as e:
            result, model = {'status': 'blocked', 'summary': str(e)}, e.model
        a['tries'] = tries + 1
        r.d['seg_model']['assets'] = r.d['made_by']['assets'] = model
        problems = [] if result.get('status') == 'done' else [f"Asset maker blocked: {result.get('summary', '')}"]
        for m in (module, sheet):
            code, out = node('--check', m)
            if code != 0:
                problems.append(f'{m} does not load: {out[-300:]}')
        if not problems:
            code, out = node('render-shots.mjs', rel(adir / 'scene.json'), '--sheet', timeout=1800)
            if code != 0:
                problems.append(f'The asset sheet does not render: {out[-300:]}')
        a['problems'] = problems
        r.save()
        if not problems:
            break
    # Show Drew: the sheet and a short movement test, on the Desktop and the board. Drew approves before any shot uses them.
    sheets = sorted((adir / 'dev').glob('beats-sheet*.png'))
    mp4 = render_and_wait(r, adir / 'scene.json', label='new drawings')
    rec = vf.deliver(mp4, r.d['title'], a.get('version', 1), kind='new drawings')
    a['version'] = rec['version'] + 1
    a['delivered'] = rec
    for s in sheets:
        vf.board(s, f"{r.d['title']}: new drawings to approve ({s.stem})")
    vf.board(mp4, f"{r.d['title']}: new drawings, movement test. On your Desktop: {rec['name'][:-4]}")
    a['status'] = 'waiting'
    r.save()
    raise WaitDrew({'kind': 'assets', 'desktop': rec['name'], 'files': [module, sheet],
                    'ask': f"Approve the new drawings ('{rec['name']}' and the sheet on the board), or give notes."})


def segment_files(r, seg):
    """Write the segment's words, scene settings and shot list from the whole-video plan."""
    seg_dir = r.dir / seg['name']
    seg_dir.mkdir(exist_ok=True)
    words = words_of(r)
    seg_words = dict(words)
    seg_words['caption_groups'] = [g for g in words['caption_groups'] if seg['start'] - 0.05 <= words['words'][g['words'][0]]['start'] < seg['end']]
    wjson(seg_dir / 'words.json', seg_words)
    scene = scene_settings(r)
    scene.update({'scene_id': seg['name'], 'module': f"scenes/{seg['name']}.mjs", 'revision': 'v1', 'output_stem': 'segment',
                  'audio_excerpt_start_seconds': seg['start'], 'audio_excerpt_end_seconds': seg['end'],
                  'duration_seconds': round(seg['end'] - seg['start'], 3), 'absolute_time': True})
    wjson(seg_dir / 'scene.json', scene)
    plan = rjson(r.dir / 'shot-list.json')
    subset = dict(plan)
    subset['shots'] = [s for s in plan['shots'] if seg['start'] - 0.05 <= s['start'] < seg['end']]
    wjson(seg_dir / 'shot-list.json', subset)
    return seg_dir


def hook_regression():
    """The approved hook's beat sheet must still be pixel-identical (the kit is shared by every video)."""
    with tempfile.TemporaryDirectory() as tmp:
        for f in ('scene.json', 'words.json', 'shot-list.json'):
            shutil.copyfile(ROOT / HOOK_SCENE / f, Path(tmp) / f)
        code, out = node('render-shots.mjs', str(Path(tmp) / 'scene.json'), '--sheet', timeout=900)
        got = [sha(p) for p in sorted((Path(tmp) / 'dev').glob('beats-sheet-*.png'))]
    return code == 0 and got == HOOK_SHEETS_SHA256


def runner_checks(r, seg, seg_dir):
    """Independent checks after an Animator try: code loads, every beat renders, motion targets, approved hook unchanged."""
    module = f"scenes/{seg['name']}.mjs"
    scene = rel(seg_dir / 'scene.json')
    problems, motion = [], None
    code, out = node('--check', module)
    if code != 0:
        return [f'The module does not load: {out[-400:]}'], None
    code, out = node('render-shots.mjs', scene, '--sheet', timeout=1800)
    if code != 0:
        return [f'The beat sheet does not render: {out[-400:]}'], None
    code, out = node('render-shots.mjs', scene, '--check-motion', timeout=AI_TIME_LIMIT)
    if code != 0:
        return [f'The motion check crashed: {out[-400:]}'], None
    motion = json.loads(out.splitlines()[-1])
    if motion['longest_still_seconds'] > 0.35:
        problems.append(f"The picture goes still for {motion['longest_still_seconds']} s (at most 0.35 s): keep the camera drifting "
                        'and something moving through every hold.')
    if motion['picture_change_half_second_median'] < 0.15:
        problems.append(f"Only {motion['picture_change_half_second_median']:.0%} of the picture changes per half second (at least 15%): "
                        'more new pieces and camera moves.')
    if not hook_regression():
        problems.append('The approved hook no longer renders pixel-identical: a shared kit file changed.')
    return problems, motion


def render_frames(scene_json, times):
    """Render frames at the given times with render-shots --at; returns the PNG paths."""
    code, out = node('render-shots.mjs', rel(scene_json), '--at', ','.join(f'{t:.2f}' for t in times), timeout=3600)
    if code != 0:
        raise Park(f'Frames for review would not render: {out[-300:]}')
    return [str(ROOT / json.loads(line)['file']) for line in out.splitlines() if line.startswith('{')]


def review(r, what, a, b, strips, scene_json, shot_list, job_dir, extra=''):
    """A fresh AI session watches the filmstrips beside the approved videos. It can send work back, never approve."""
    w = words_of(r)['words']
    brief = REVIEW_BRIEF.format(what=what, start=a, end=b, strips=''.join(f'- {rel(s)}\n' for s in strips),
                                refs=''.join(f'- {x}\n' for x in reference_strips()), shot_list=rel(shot_list),
                                word_lines=word_lines(w, a, b), flagged=', '.join(r.d.get('flagged_words') or []) or 'none',
                                limits=r.d['limits'], extra=extra, scene_json=rel(scene_json))
    images = [rel(s) for s in strips] + reference_strips()
    try:
        result, model = agent_job('reviewer', brief, job_dir, REVIEW_SCHEMA, images, ladder=r.d['ladder'])
    except JobFailed as e:
        result, model = {'pass': False, 'notes': [], 'summary': f'Reviewer gave no usable answer: {e}'}, e.model
    for n in result.get('notes', []):
        record_verdict(r, item=what, decision='notes', said=f"{n['problem']} Fix: {n['fix']}", by=f'reviewer ({MODELS[model]})',
                       problem_key=n.get('problem_key'), where=f"{what} at {n.get('time', 0):.1f} s")
    if not result.get('notes'):
        record_verdict(r, item=what, decision='pass' if result.get('pass') else 'notes', said=result.get('summary', ''),
                       by=f'reviewer ({MODELS[model]})')
    return result


def make_segment(r, seg, previous):
    name = seg['name']
    module = f'scenes/{name}.mjs'
    seg_dir = segment_files(r, seg)
    tries_dir = seg_dir / 'attempts'
    tries_dir.mkdir(exist_ok=True)
    record = rjson(tries_dir / 'attempts.json', [])
    model = r.d['seg_model'].get(name)
    notes = r.d['notes'].get(name, [])
    w = words_of(r)['words']
    assets = ''
    if (r.d.get('assets') or {}).get('status') == 'approved':
        assets = (f"\nNew drawings made and approved for this episode: scenes/{r.name}-assets.mjs. "
                  f"Their reference: {rel(r.dir / 'assets' / 'API.md')}. Import them; do not redraw them.\n")
    while True:
        tries = r.d['attempts'].get(name, 0)
        if tries >= TRIES['animator']:
            this_round = record[-tries:] if tries else []
            best = max(this_round, key=lambda x: (x['checks_pass'], x['review_pass'], -len(x['problems']))) if this_round else None
            if best and (tries_dir / f"try-{best['try']}.mjs").exists():
                shutil.copyfile(tries_dir / f"try-{best['try']}.mjs", ROOT / module)
            raise Park(f"Segment {name} failed its checks or review {tries} times. Best try kept (try {best['try'] if best else '-'}). "
                       f"Last problems: " + '; '.join((record[-1]['problems'] if record else notes)[:4]))
        brief = SEGMENT_BRIEF.format(episode=r.d['episode'], start=seg['start'], end=seg['end'], word_lines=word_lines(w, seg['start'], seg['end']),
                                     limits=r.d['limits'], assets=assets, exclusions=exclusions(r), shot_list=rel(seg_dir / 'shot-list.json'),
                                     module=module, scene_json=rel(seg_dir / 'scene.json'), dev_dir=rel(seg_dir / 'dev'))
        brief = brief.replace(f"- {rel(seg_dir / 'shot-list.json')}: your shot list for this segment, absolute times, in the director prompt's JSON shape.\n", '')
        brief += PLANNED_SEGMENT_NOTE.format(shot_list=rel(seg_dir / 'shot-list.json'), plan=rel(r.dir / 'shot-list.json'),
                                             previous=', '.join(previous) or 'none (this is the first)')
        if notes and (ROOT / module).exists():
            brief += RETRY_NOTE.format(attempt=tries + 1, module=module, notes=''.join(f'- {n}\n' for n in notes))
        elif notes:
            brief += '\nNotes for this segment; follow them:\n' + ''.join(f'- {n}\n' for n in notes)
        rules = learned_rules()
        n = len(record) + 1                     # numbered across rounds, so a redo never overwrites earlier evidence
        try:
            result, model = agent_job('animator', brief, seg_dir / f'job-{n}', RESULT_SCHEMA, APPROVED_FRAMES,
                                      allow=[module, rel(seg_dir)], ladder=r.d['ladder'], start_at=model)
        except JobFailed as e:
            result, model = {'status': 'blocked', 'summary': str(e)}, e.model
        tries += 1
        r.d['attempts'][name] = tries
        r.d['seg_model'][name] = model
        r.save()
        problems, motion = ([f"The Animator could not finish: {result.get('summary', '')}"], None) if result.get('status') != 'done' else ([], None)
        if not problems:
            problems, motion = runner_checks(r, seg, seg_dir)
        checks_pass = not problems
        review_pass = False
        if checks_pass:
            times = [round(seg['start'] + i * 0.2, 2) for i in range(int((seg['end'] - seg['start']) / 0.2) + 1)]
            frames = render_frames(seg_dir / 'scene.json', [t for t in times if t < seg['end']])
            (seg_dir / 'review').mkdir(exist_ok=True)
            strips = vf.frame_strips(frames, seg_dir / 'review' / f'try-{n}-strip') if frames else []
            verdict = review(r, f'segment {name}', seg['start'], seg['end'], [Path(s) for s in strips], seg_dir / 'scene.json',
                             seg_dir / 'shot-list.json', seg_dir / f'review-job-{n}',
                             extra=f'6. Continuity with the earlier segments ({", ".join(previous) or "none"}).\n')
            review_pass = bool(verdict.get('pass'))
            if not review_pass:
                problems = [f"{n.get('time', 0):.2f} s, shot {n.get('shot', '?')}: {n['problem']} Fix: {n['fix']}" for n in verdict.get('notes', [])] \
                    or [f"Reviewer: {verdict.get('summary', 'not good enough')}"]
        if (ROOT / module).exists():
            shutil.copyfile(ROOT / module, tries_dir / f'try-{n}.mjs')
        record.append({'try': n, 'round_try': tries, 'model': model, 'at': stamp(), 'checks_pass': checks_pass, 'review_pass': review_pass,
                       'motion': motion, 'problems': problems, 'rules_read': len(rules.splitlines())})
        wjson(tries_dir / 'attempts.json', record)
        if checks_pass and review_pass:
            r.d['made_by'][name] = model
            r.d['notes'].pop(name, None)
            r.d.setdefault('segment_sha256', {})[name] = sha(ROOT / module)
            r.event(f'segment {name} done', model=MODELS[model], tries=tries)
            return
        notes = problems                        # the same model retries with these notes


def first_new_drawing_segment(r):
    names = [n.lower() for n in r.d.get('new_assets') or []]
    if not names:
        return None
    plan = rjson(r.dir / 'shot-list.json')
    for seg in r.d['segments']:
        text = json.dumps([s for s in plan['shots'] if seg['start'] - 0.05 <= s['start'] < seg['end']]).lower()
        if any(n in text for n in names):
            return seg['name']
    return r.d['segments'][0]['name']


def pilot_reasons(r, name):
    """Pilot clip gate, risky segments only (Drew, 19 Oct): the first segment Sol or Astra makes, or the first with new drawings."""
    ok = r.d['pilot']['approved']
    reasons = []
    if PROVIDER[r.d['made_by'][name]] == 'codex' and 'codex' not in ok:
        reasons.append('codex')
    if name == first_new_drawing_segment(r) and 'new_drawings' not in ok:
        reasons.append('new_drawings')
    return reasons


def step_segments(r):
    previous = []
    for seg in r.d['segments']:
        name = seg['name']
        if name not in r.d['segments_done']:
            make_segment(r, seg, previous)
            r.d['segments_done'].append(name)
            r.save()
            reasons = pilot_reasons(r, name)
            if reasons:
                seg_dir = r.dir / name
                mp4 = render_and_wait(r, seg_dir / 'scene.json', label=f'pilot clip {name}')
                rec = vf.deliver(mp4, r.d['title'], r.d['pilot'].get('version', 1), kind='pilot clip')
                r.d['pilot']['version'] = rec['version'] + 1
                vf.board(mp4, f"{r.d['title']}: pilot clip {name}. On your Desktop: {rec['name'][:-4]}")
                r.save()
                why = {'codex': f"made by {MODELS[r.d['made_by'][name]]}", 'new_drawings': 'first segment with the new drawings'}
                raise WaitDrew({'kind': 'pilot', 'segment': name, 'reasons': reasons, 'desktop': rec['name'], 'mp4': rec['source'],
                                'ask': f"Pilot clip ({', '.join(why[x] for x in reasons)}): watch '{rec['name']}', approve or give notes."})
        previous.append(f'scenes/{name}.mjs')


def assemble(r):
    segs = r.d['segments']
    imports = '\n'.join(f"import {{ createScene as seg{i + 1:02d} }} from './{s['name']}.mjs';" for i, s in enumerate(segs))
    table = ',\n  '.join(f"{{ start: {s['start']}, end: {s['end']}, create: seg{i + 1:02d} }}" for i, s in enumerate(segs))
    module = f"""// Generated by make_video.py: joins the segments of run {r.name}, one caption track, then the approved outro.
import {{ makeFibres, createCaptions }} from './paper-kit.mjs';
import {{ createOutro }} from './outro.mjs';
{imports}

const SEGMENTS = [
  {table},
];

export function createScene(config, timing) {{
  const made = SEGMENTS.map(s => ({{ ...s, scene: s.create(config, timing) }}));
  const texture = makeFibres((config.seed ?? 1) | 0);
  const outro = config.outro ? createOutro(config, timing) : null;
  const groups = outro ? timing.caption_groups.filter(g => g.words[0] < outro.firstWord) : timing.caption_groups;
  const captions = createCaptions(timing.words, groups, {{
    texture, centerY: config.caption_center_y ?? 1420,
    endTime: outro ? outro.start + 0.4 : (config.time_offset ?? 0) + config.duration_seconds + 10,
  }});
  const pick = t => made.findLast(s => t >= s.start) ?? made[0];
  const lessonWorld = (ctx, t) => pick(t).scene.drawWorld(ctx, t);
  const drawWorld = outro ? (ctx, t) => outro.drawWorld(ctx, t, lessonWorld, captions) : lessonWorld;
  const drawOverlay = outro ? (ctx, t) => outro.drawOverlay(ctx, t, captions) : captions;
  return {{
    duration: config.duration_seconds,
    blurWindows: made.flatMap(s => s.scene.blurWindows ?? []),
    drawWorld,
    drawOverlay,
    draw(ctx, t) {{ drawWorld(ctx, t); drawOverlay(ctx, t); }},
  }};
}}
"""
    path = ROOT / 'scenes' / f'{r.name}-full.mjs'
    path.write_text(module)
    return path


def step_join(r):
    """Fit the approved outro to this narrator, then join the segments into one module and one scene."""
    changed = [s for s, digest in r.d.get('segment_sha256', {}).items()
               if (ROOT / 'scenes' / f'{s}.mjs').exists() and sha(ROOT / 'scenes' / f'{s}.mjs') != digest]
    if changed:
        raise Park('Finished segments changed after their checks: ' + ', '.join(changed))
    a, b = r.d['video_range']
    scene = scene_settings(r)
    scene.update({'scene_id': f'{r.name}-full', 'module': f'scenes/{r.name}-full.mjs', 'revision': 'v1', 'output_stem': r.name,
                  'audio_excerpt_start_seconds': a, 'audio_excerpt_end_seconds': b, 'duration_seconds': round(b - a, 3),
                  'absolute_time': True})
    if r.d.get('signoff') is not None:
        try:
            plan = vf.fit_outro(words_of(r)['words'], r.dir / 'outro-retime.json', r.d['audio_seconds'])
        except vf.FinishError as e:
            raise Park(f'Outro fit: {e}')
        scene['outro'] = {'plan': rel(r.dir / 'outro-retime.json')}
        scene['tail_seconds'] = round(plan['end_frame'] / 30 - scene['duration_seconds'], 6)
        r.event('outro fitted', trimmed_frames=plan['frames_trimmed'], logo_landed=plan['logo_landed_seconds'],
                deep=plan['deep_starts_seconds'], hold=plan['hold_after_last_word_seconds'])
    old = rjson(r.dir / 'scene.json')
    if old:
        scene['revision'] = old.get('revision', 'v1')
    wjson(r.dir / 'scene.json', scene)
    assemble(r)
    code, out = node('--check', f'scenes/{r.name}-full.mjs')
    if code != 0:
        raise Park(f'The joined module does not load: {out[-300:]}')


def render_and_wait(r, scene_json, label='video'):
    """Detached render with crash safety: a render that dies is retried once on the next free revision; a leftover partial
    file never blocks. Returns the finished MP4. Time limit 4 h."""
    scene_json = Path(scene_json)
    key = rel(scene_json)
    renders = scene_json.parent / 'renders'
    while True:
        cur = next((x for x in reversed(r.d['renders']) if x['scene'] == key and x['status'] == 'running'), None)
        if cur is None:
            failures = sum(1 for x in r.d['renders'] if x['scene'] == key and x['status'] == 'failed' and not x.get('cleared'))
            if failures >= TRIES['render']:
                raise Park(f'The {label} render failed {failures} times; see its log in {rel(renders)}.')
            scene = rjson(scene_json)
            scene['revision'] = vf.next_revision(renders, scene.get('output_stem', 'hook'))
            wjson(scene_json, scene)
            renders.mkdir(exist_ok=True)
            log = renders / f"render-{scene['revision']}.log"
            pid = vf.start_render(scene_json, log)
            cur = {'scene': key, 'revision': scene['revision'], 'pid': pid, 'status': 'running', 'started_at': stamp(), 'label': label,
                   'mp4': rel(renders / f"{scene.get('output_stem', 'hook')}-{scene['revision']}.mp4"), 'log': rel(log)}
            r.d['renders'].append(cur)
            r.event(f'render started: {label} {scene["revision"]}', pid=pid)
            r.save()
        started = datetime.fromisoformat(cur['started_at'])
        while vf.alive(cur['pid'], 'render-shots.mjs'):
            if (now() - started).total_seconds() > RENDER_TIME_LIMIT:
                vf.stop(cur['pid'])
                time.sleep(5)
                break
            time.sleep(10)
        mp4 = ROOT / cur['mp4']
        manifest = mp4.with_suffix('.json')
        if mp4.exists() and manifest.exists():
            cur.update(status='done', ended_at=stamp())
            r.event(f'render finished: {label} {cur["revision"]}')
            r.save()
            return mp4
        lines = (ROOT / cur['log']).read_text(errors='replace').splitlines() if (ROOT / cur['log']).exists() else []
        progress = [json.loads(x) for x in lines if x.startswith('{"rendered_frames"')]
        errors = ' '.join(x for x in lines if not x.startswith('{'))[-200:]
        error = (f"stopped near frame {progress[-1]['rendered_frames']} of {progress[-1]['total_frames']}" if progress
                 else 'stopped before the first frame') + (f': {errors}' if errors else '')
        cur.update(status='failed', ended_at=stamp(), error=error)
        r.event(f'render failed: {label} {cur["revision"]}; the next try takes the next revision')
        r.save()


def step_render(r):
    mp4 = render_and_wait(r, r.dir / 'scene.json', label='video')
    r.d['picture'] = rel(mp4)


def step_finish(r):
    """The approved MP3 under the picture, unchanged and padded with silence; then the audio checks."""
    picture = ROOT / r.d['picture']
    final = picture.with_name(picture.stem + '-final.mp4')
    if not final.exists():
        try:
            checks = vf.finish_audio(picture, ROOT / r.d['mp3'], r.d['audio_sha256'], final, music=r.d.get('music'))
        except vf.FinishError as e:
            raise Park(f'Finish: {e}')
    else:
        checks = vf.check_audio(final, ROOT / r.d['mp3'], picture)
    wjson(final.with_name(final.stem + '.checks.json'), checks)
    if not checks['pass']:
        raise Park(f"The finished file failed its format or audio checks: {final.with_name(final.stem + '.checks.json').name}")
    r.d['final'] = rel(final)


def keyword_items(r):
    plan = rjson(r.dir / 'shot-list.json')
    items = []
    for s in plan['shots']:
        if s.get('beats') and (r.d.get('signoff') is None or s['beats'][0]['at'] < r.d['lesson_range'][1]):
            b = s['beats'][0]
            items.append((b['at'] + 0.15, f"{s['id']} {b['word']}"))
    for s in r.d['segments'][1:]:
        items += [(s['start'] - 0.05, 'joint before'), (s['start'] + 0.05, 'joint after')]
    out = rjson(r.dir / 'outro-retime.json')
    if out:
        items += [(out['outro_start_seconds'] + 0.15, 'wipe'), (out['logo_landed_seconds'] + 0.02, 'logo landed'),
                  (out['video_seconds'] - 0.05, 'last frame')]
    return sorted(items)


def step_check(r):
    """The encoded file: format, streams, lesson motion, outro frames, and frames pulled on key words and every joint."""
    final = ROOT / r.d['final']
    stem = final.with_suffix('')
    checks = rjson(Path(str(stem) + '.checks.json'))
    out = rjson(r.dir / 'outro-retime.json') if r.d.get('signoff') is not None else None
    motion = vf.motion_check(final, out['outro_start_seconds'] if out else None)
    wjson(Path(str(stem) + '.motion.json'), motion)
    outro = vf.outro_check(final, out) if out else None
    sheet = Path(str(stem) + '-keywords.png')
    vf.keyword_sheet(final, keyword_items(r), sheet)
    r.d['keywords'] = rel(sheet)
    problems = []
    if abs(checks['video_seconds'] - checks['audio_seconds']) > 0.05 or checks['video_start'] or checks['audio_start']:
        problems.append('Audio and video do not start together or differ in length.')
    if not motion['pass']:
        stretches = ', '.join(f'{x[0]}-{x[1]} s' for x in motion['lesson_still_stretches_over_0_2s']) or 'none listed'
        problems.append(f"Lesson motion misses its targets: still {motion['lesson']['longest_still_seconds']} s, change "
                        f"{motion['lesson']['picture_change_half_second_median']:.0%}; still stretches: {stretches}.")
    if outro is not None:
        wjson(Path(str(stem) + '.outro-check.json'), outro)
        if not outro['pass']:
            problems.append(f"The outro differs from the approved animation (difference {outro['worst_mean_difference']}).")
    r.d['file_checks'] = {'motion': motion['lesson'], 'outro': outro, 'audio_pass': checks['pass'], 'problems': problems}
    if problems:
        return fix(r, problems, 'the runner\'s checks of the finished file')


def step_review(r):
    final = ROOT / r.d['final']
    stem = final.with_suffix('')
    strips = vf.filmstrips(final, Path(str(stem) + '-strip'))
    joints = ', '.join(f"{s['start']:.2f}" for s in r.d['segments'][1:])
    a, b = r.d['video_range']
    rounds = r.d.get('fix_rounds', 0)
    verdict = review(r, f'the whole video ({final.name})', a, b, [Path(s) for s in strips], r.dir / 'scene.json', r.dir / 'shot-list.json',
                     r.dir / f'review-job-{len(r.d["renders"])}-{rounds}',
                     extra=('6. Whole video: sets and characters match across segments'
                            + (f'; joints at {joints} s are clean.\n' if joints else '.\n')
                            + '7. The ending: the last teaching picture stays readable through its last word, then the approved cream-paper '
                            'wipe and outro play; the logo has landed before "Deep".\n'))
    r.d['review'] = {'pass': verdict.get('pass'), 'summary': verdict.get('summary'), 'notes': len(verdict.get('notes', []))}
    if not verdict.get('pass'):
        notes = [f"{n.get('time', 0):.2f} s, shot {n.get('shot', '?')}: {n['problem']} Fix: {n['fix']}" for n in verdict.get('notes', [])]
        return fix(r, notes or [verdict.get('summary', '')], 'the whole-video reviewer')


def step_deliver(r):
    final = ROOT / r.d['final']
    rec = vf.deliver(final, r.d['title'], r.d.get('version', 1))
    rec['revision'] = final.stem
    rec['made_by'] = {s['name']: MODELS[r.d['made_by'][s['name']]] for s in r.d['segments'] if s['name'] in r.d['made_by']}
    r.d['deliveries'].append(rec)
    r.d['version'] = rec['version'] + 1
    r.save()
    seconds = rjson(final.with_name(final.stem + '.checks.json'))['video_seconds']
    vf.board(final, f"{r.d['title']} v{rec['version']} ({seconds:.0f} s). On your Desktop: {rec['name'][:-4]}")
    if r.d.get('keywords'):
        vf.board(ROOT / r.d['keywords'], f"{r.d['title']} v{rec['version']}: key moments, with the spoken word highlighted")


STEPS = [('prepare', step_prepare), ('plan', step_plan), ('assets', step_assets), ('segments', step_segments), ('join', step_join),
         ('render', step_render), ('finish', step_finish), ('check', step_check), ('review', step_review), ('deliver', step_deliver)]
REDO_FROM = ['segments', 'join', 'render', 'finish', 'check', 'review', 'deliver']


def advance(r):
    while True:
        if r.d.get('pending_notes'):
            triage(r, **r.d.pop('pending_notes'))
            r.save()
        pending = [(n, f) for n, f in STEPS if n not in r.d['steps_done']]
        if not pending:
            return
        name, fn = pending[0]
        r.d['step'] = name
        r.save()
        if fn(r) is False:                      # the step sent work back (triage reset earlier steps)
            continue
        r.d['steps_done'].append(name)
        r.event(f'{name} done')
        r.save()


# ---------------------------------------------------------------- fixes, verdicts and learning
def fix(r, problems, source):
    """Checks or the reviewer failed the finished video: triage, then redo only what is affected (at most FIX_ROUNDS times)."""
    r.d['fix_rounds'] = r.d.get('fix_rounds', 0) + 1
    if r.d['fix_rounds'] > r.d.get('fix_rounds_allowed', FIX_ROUNDS):
        raise Park(f'Still failing after {r.d["fix_rounds"] - 1} fix rounds ({source}): ' + '; '.join(problems[:4]))
    triage(r, problems=problems, source=source)
    return False


def triage(r, problems=(), source='', drew=None, item=None):
    parts = '\n'.join(f"- {s['name']}: {s['start']:.2f} to {s['end']:.2f} s" for s in r.d['segments'])
    out = rjson(r.dir / 'outro-retime.json')
    if out:
        parts += f"\n- outro: {out['outro_start_seconds']:.2f} to {out['video_seconds']:.2f} s (approved animation, fitted by the runner)"
    text = '\n'.join(f'- {p}' for p in problems) if problems else f'Drew said about {item}: "{drew}"'
    brief = TRIAGE_BRIEF.format(episode=r.d['episode'], source=source or 'Drew', problems=text, parts=parts,
                                shot_list=rel(r.dir / 'shot-list.json'), words=rel(r.dir / 'words.json'), keys=problem_list())
    job = r.dir / f"triage-{len(list(r.dir.glob('triage-*'))) + 1}"
    try:
        result, model = agent_job('triage', brief, job, TRIAGE_SCHEMA, ladder=r.d['ladder'])
    except JobFailed as e:
        raise Park(f'Triage gave no usable answer: {e}')
    redo, park, questions = set(), [], []
    names = {s['name'] for s in r.d['segments']}
    for act in result.get('actions', []):
        kind, seg = act['kind'], act.get('segment', '')
        if act.get('problem_key') and kind not in ('none', 'music', 'ask_drew'):
            record_problem(act['problem_key'], act.get('problem_title') or act['notes'][:80], act.get('rule', ''),
                           where=f"{r.name} {seg or 'video'} {act.get('start', 0):.1f}-{act.get('end', 0):.1f} s",
                           said=drew or act['notes'])
        if kind in ('redo_segment', 'replan_segment') and seg in names:
            r.d['notes'].setdefault(seg, []).append(act['notes'])
            if kind == 'replan_segment':
                r.d.setdefault('replan', {})[seg] = act['notes']
            redo.add(seg)
        elif kind in ('caption_timing', 'outro'):
            park.append(f"{kind.replace('_', ' ')}: {act['notes']}")
        elif kind == 'music':
            record_verdict(r, item=item or 'video', decision='music note', said=act['notes'], by='triage')
        elif kind == 'ask_drew':
            questions.append(act)
    r.event('triage', source=source or 'Drew', redo=sorted(redo), parked=park, questions=len(questions))
    if questions:
        q = questions[0]
        r.save()
        raise WaitDrew({'kind': 'question', 'item': item, 'question': q['question'], 'options': q.get('options', []),
                        'ask': q['question'] + ' ' + ' / '.join(f'{chr(65 + i)}) {o}' for i, o in enumerate(q.get('options', [])))})
    if park:
        raise Park('Needs a hand fix outside the AI roles: ' + '; '.join(park))
    if not redo:
        raise Park(f"Triage found nothing to redo ({result.get('summary', '')[:200]}) for: " + ('; '.join(problems[:3]) or drew))
    for seg in sorted(redo):
        if seg in r.d.get('replan', {}):
            replan(r, next(s for s in r.d['segments'] if s['name'] == seg), r.d['replan'].pop(seg))
        r.d['attempts'][seg] = 0
        if seg in r.d['segments_done']:
            r.d['segments_done'].remove(seg)
        r.d.get('segment_sha256', {}).pop(seg, None)
    r.d['steps_done'] = [s for s in r.d['steps_done'] if s not in REDO_FROM]
    r.save()


def replan(r, seg, notes):
    w = words_of(r)['words']
    out = r.dir / f"replan-{seg['name']}-{stamp()[:19].replace(':', '')}.json"
    brief = REPLAN_BRIEF.format(episode=r.d['episode'], start=seg['start'], end=seg['end'], notes=notes, plan=rel(r.dir / 'shot-list.json'),
                                word_lines=word_lines(w, seg['start'], seg['end']), limits=r.d['limits'], out=rel(out))
    try:
        result, model = agent_job('director', brief, r.dir / f'{out.stem}-job', REPLAN_SCHEMA, APPROVED_FRAMES, ladder=r.d['ladder'])
    except JobFailed as e:
        raise Park(f'Re-planning {seg["name"]} failed: {e}')
    new = rjson(out, {}).get('shots') if out.exists() else None
    if result.get('status') != 'done' or not new:
        raise Park(f'Re-planning {seg["name"]} gave no shots.')
    plan = rjson(r.dir / 'shot-list.json')
    shutil.copyfile(r.dir / 'shot-list.json', r.dir / f'shot-list.before-{out.stem}.json')
    plan['shots'] = sorted([s for s in plan['shots'] if not seg['start'] - 0.05 <= s['start'] < seg['end']] + new, key=lambda s: s['start'])
    wjson(r.dir / 'shot-list.json', plan)
    errors = [e for e in check_plan(r) if 'Segment' not in e and 'Caption' not in e]
    if errors:
        shutil.copyfile(r.dir / f'shot-list.before-{out.stem}.json', r.dir / 'shot-list.json')
        raise Park(f'Re-planned shots for {seg["name"]} failed the plan checks: ' + '; '.join(errors[:4]))


def record_verdict(r, item, decision, said, by='Drew', **extra):
    line = {'at': stamp(), 'episode': r.d['episode'], 'run': r.name, 'item': item, 'decision': decision, 'said': said, 'by': by, **extra}
    with open(VERDICTS, 'a') as f:
        f.write(json.dumps(line) + '\n')
    if extra.get('problem_key') and decision == 'notes':
        record_problem(extra['problem_key'], said[:80], '', where=f"{r.name} {extra.get('where', item)}", said=said, by=by)


def record_problem(key, title, rule, where, said, by='triage'):
    """A problem seen twice becomes a rule in learned-rules.md, which every brief tells the AI to read."""
    key = re.sub(r'[^a-z0-9-]', '-', key.lower()).strip('-')[:60] or 'unnamed'
    probs = rjson(PROBLEMS, {})
    p = probs.setdefault(key, {'title': title, 'rule': rule, 'seen': [], 'rule_added': False})
    if rule and not p.get('rule'):
        p['rule'] = rule
    if not any(s['where'] == where for s in p['seen']):
        p['seen'].append({'at': stamp(), 'where': where, 'said': said[:300], 'by': by})
    if len(p['seen']) >= 2 and not p['rule_added'] and p.get('rule'):
        with open(LEARNED, 'a') as f:
            f.write(f"- **{p['title'].rstrip('.')}.** {p['rule']} (Seen {len(p['seen'])} times; key `{key}`.)\n")
        p['rule_added'] = True
    wjson(PROBLEMS, probs)


def approve_video(r, says):
    what = r.d['waiting_for']
    mp4 = ROOT / what['mp4']
    cmd = [str(D6_TOOL), 'complete-video', r.d['episode'], str(mp4), '--audio-manifest', str((ROOT / r.d['manifest']).resolve()), '--final']
    proc = subprocess.run(cmd, cwd=PROJECT, capture_output=True, text=True)
    r.d['complete_video'] = {'command': ' '.join(cmd[1:]), 'exit': proc.returncode, 'output': (proc.stdout + proc.stderr).strip()[-600:]}
    if proc.returncode:
        r.save()
        sys.exit('Approval saved in verdicts.jsonl, but recording the finished video failed:\n' + r.d['complete_video']['output'])
    review = mp4.with_name(mp4.name[:-len('-final.mp4')] + '.review.json')
    if mp4.name.endswith('-final.mp4') and review.exists():   # the renderer's review file for this picture
        data = rjson(review)
        data.update(decision='approved', approved_by='Drew', approved_at=stamp(), final_mp4=mp4.name,
                    feedback=data.get('feedback', []) + [{'at': stamp(), 'user_text': says}])
        wjson(review, data)
    r.d['locked'] = True
    r.set('approved')
    r.event('approved by Drew; run locked; sources marked used by tools/d6 complete-video')
    r.save()


def cmd_verdict(args):
    r = find_run(args.run)
    if r.state != 'waiting_drew':
        sys.exit(f'{r.name} is not waiting for Drew (state: {r.state}).')
    says = args.says.strip()
    if not says:
        sys.exit("Record Drew's own words with --says. Silence never counts as approval.")
    what = r.d['waiting_for']
    kind = what['kind']
    item = {'video': f"video v{what.get('version')}", 'pilot': f"pilot clip {what.get('segment')}", 'assets': 'new drawings',
            'question': 'question'}[kind]
    record_verdict(r, item=item, decision=args.decision, said=says, by='Drew')
    if args.decision == 'approve' and kind == 'video':
        approve_video(r, says)
        print(f'{r.name}: approved and locked. The finished video is recorded with tools/d6 complete-video.')
        ensure_worker() if due(all_runs()) else None
        return
    if args.decision == 'approve' and kind == 'pilot':
        r.d['pilot']['approved'] += what.get('reasons', [])
    elif args.decision == 'approve' and kind == 'assets':
        assets_approved(r)
    elif kind == 'pilot':
        seg = what['segment']
        r.d['notes'].setdefault(seg, []).append(f'Drew watched the pilot clip and said: "{says}"')
        r.d['segments_done'].remove(seg)
        r.d['attempts'][seg] = 0
    elif kind == 'assets':
        r.d['assets'].update(status=None, tries=0, notes=r.d['assets'].get('notes', []) + [f'Drew said: "{says}"'])
    elif kind == 'question':
        r.d['pending_notes'] = {'drew': f"{what.get('question')} Drew answered: {says}", 'item': what.get('item') or 'video'}
    else:                                       # notes on the delivered video: triage maps them, redo, re-deliver as the next version
        r.d['pending_notes'] = {'drew': says, 'item': item}
        r.d['fix_rounds'] = 0
    r.set('queued')
    pid = ensure_worker()
    print(f'{r.name}: verdict saved; the video continues in the background' + (f' (worker {pid}).' if pid else '.'))


def assets_approved(r):
    """Drew approved the new drawings: they join the protected kit; their sources go in the source log and science notes."""
    a = r.d['assets']
    a['status'] = 'approved'
    adir = r.dir / 'assets'
    sources = rjson(adir / 'sources.json', [])
    log = PROJECT / '01-content' / 'source-log.md'
    if sources and log.exists():
        rows = ''.join(f"| [{s.get('title', s['url'])}]({s['url']}) | {s.get('used_for', '')} | {r.d['episode']} |\n" for s in sources)
        with open(log, 'a') as f:
            f.write(f"\n## Drawing anatomy checks: {r.d['episode']} ({stamp()[:10]}, run {r.name})\n\n"
                    '| Source | Used for | Episode |\n|---|---|---|\n' + rows)
    notes = adir / 'science-notes.md'
    if notes.exists():
        with open(ROOT / 'science-notes.md', 'a') as f:
            f.write(f"\n## New drawings for {r.d['episode']} ({stamp()[:10]}, run {r.name})\n\n{notes.read_text().strip()}\n")
    kit = ROOT / 'KIT-API.md'
    api = adir / 'API.md'
    if api.exists():
        with open(kit, 'a') as f:
            f.write(f"\n## `scenes/{r.name}-assets.mjs`: new drawings for {r.d['episode']}\n\n{api.read_text().strip()}\n")


def cmd_go(args):
    r = find_run(args.run)
    if r.state == 'waiting' and not r.d.get('not_before'):
        r.d['queued_at'] = stamp()
    elif r.state == 'parked':
        for key in list(r.d['attempts']):         # a fresh set of tries for the step that parked
            if key not in r.d['segments_done']:
                r.d['attempts'][key] = 0
        r.d.get('assets', {}).update(tries=0) if r.d.get('assets') else None
        r.d['fix_rounds'] = 0
        for x in r.d['renders']:
            x['cleared'] = True
    elif r.state not in ('waiting', 'paused'):
        sys.exit(f'{r.name} is {r.state}; nothing to start.')
    r.set('queued')
    pid = ensure_worker()
    print(f'{r.name}: queued' + (f'; worker {pid} started.' if pid else '; the running worker picks it up.'))


def cmd_stop(args):
    r = find_run(args.run)
    if r.state in ('running', 'approved'):
        sys.exit(f'{r.name} is {r.state}; it cannot be stopped here.')
    r.set('stopped', reason=args.reason or 'Drew stopped it.')
    print(f'{r.name}: stopped. All its files are kept.')


# ---------------------------------------------------------------- status
STATE_WORDS = {'waiting': 'Waiting to start', 'queued': 'Queued', 'running': 'Being made now', 'paused': 'Paused for a usage reset',
               'parked': 'Parked: needs Drew', 'waiting_drew': 'Waiting for Drew', 'approved': 'Approved and locked', 'stopped': 'Stopped'}


def status_note(r):
    d = r.d
    title = d.get('title') or d['episode']
    w = d.get('waiting_for')
    ask = w.get('ask') if isinstance(w, dict) else w
    lines = [f'# {title} video ({d["run"]}): {STATE_WORDS.get(d["state"], d["state"])}', '']
    if d['state'] == 'waiting_drew':
        lines.append(f'**{ask}**')
    elif d['state'] == 'parked':
        lines.append(f'**{d.get("reason")}** Drew decides: try again (`go`) or drop it (`stop`).')
    elif d['state'] in ('waiting', 'paused'):
        lines.append(f'**Waiting for {ask}.**' + (f' {d.get("reason")}' if d.get('reason') else ''))
    else:
        lines.append(f'**Step: {d.get("step") or "not started"}.**')
    lines += ['', f'- Episode {d["episode"]}; MP3 `{d["mp3"]}` ({d["audio_seconds"]:.1f} s); start: {d["when"]}, recorded {d["created_at"][:16]}.']
    if d.get('segments'):
        segs = []
        for s in d['segments']:
            n = s['name']
            model = MODELS.get(d['made_by'].get(n) or d['seg_model'].get(n, ''), '')
            state = 'done' if n in d['segments_done'] else (f"try {d['attempts'].get(n, 0)}" if d['attempts'].get(n) else 'to do')
            segs.append(f"{n.rsplit('-', 1)[-1]} {s['start']:.1f}-{s['end']:.1f} s {state}{' by ' + model if model else ''}")
        lines.append('- Segments: ' + '; '.join(segs) + '.')
    for x in d.get('renders', [])[-4:]:
        lines.append(f"- Render {x['label']} {x['revision']}: {x['status']}{' (' + x['error'][-120:] + ')' if x.get('error') else ''}.")
    for x in d.get('deliveries', []):
        lines.append(f"- Delivered v{x['version']}: Desktop `{x['name']}`, checksum verified, no player opened. Made by: "
                     + ', '.join(f"{k.rsplit('-', 1)[-1]} {v}" for k, v in x.get('made_by', {}).items()) + '.')
    fc = d.get('file_checks')
    if fc:
        lines.append(f"- File checks: lesson still {fc['motion']['longest_still_seconds']} s, change {fc['motion']['picture_change_half_second_median']:.0%}"
                     + (f", outro difference {fc['outro']['worst_mean_difference']}" if fc.get('outro') else '') + f", audio {'pass' if fc['audio_pass'] else 'FAIL'}.")
    if d.get('review'):
        lines.append(f"- Whole-video reviewer: {'no problems found' if d['review']['pass'] else f"{d['review']['notes']} note(s) sent back"}. {d['review'].get('summary') or ''}")
    lines += ['', 'Commands (from `01-content/animation`):', '']
    if d['state'] == 'waiting_drew':
        lines.append(f'    python3 make_video.py verdict --run {d["run"]} --decision approve|notes --says "Drew\'s words"')
    if d['state'] in ('waiting', 'parked'):
        lines.append(f'    python3 make_video.py go --run {d["run"]}')
    lines.append(f'    python3 make_video.py status --run {d["run"]}')
    return '\n'.join(lines) + '\n'


def cmd_status(args):
    runs = all_runs()
    if any(r.state == 'running' for r in runs) or due(runs) or any(r.state in ('waiting', 'paused') and r.d.get('not_before') for r in runs):
        if not worker_running():
            recover(runs)
            pid = ensure_worker()
            print(f'(worker restarted: {pid})')
            runs = all_runs()
    for r in runs if not args.run else [find_run(args.run)]:
        if args.run:
            print(status_note(r))
        else:
            w = r.d.get('waiting_for')
            print(f"{r.name:34} {STATE_WORDS.get(r.state, r.state):26} {r.d.get('step') or '':9} "
                  f"{(w.get('ask') if isinstance(w, dict) else w) or r.d.get('reason') or ''}"[:220])
    if not runs:
        print('No videos started yet.')


# ---------------------------------------------------------------- commands
def cmd_start(args):
    run = args.run or args.episode.lower()
    r = new_run(args.episode, run, args.manifest, args.when, title=args.title, start=args.start, end=args.end,
                limits=args.limits, exclude=args.exclude, ladder=args.ladder.split(',') if args.ladder else None)
    pid = ensure_worker() if args.when != 'later' else None
    print(f"{run}: {STATE_WORDS[r.state].lower()}" + (f" until {r.d['not_before'][11:16]}" if r.d.get('not_before') else '')
          + (f'; worker {pid} started.' if pid else '.') + f' Status note: {rel(r.dir / "STATUS.md")}')


def cmd_full(args):
    """Old form, kept for the saved resume commands: start now (or continue an existing run)."""
    folder = ROOT / 'episodes' / args.episode / 'runs' / args.run
    if (folder / 'run.json').exists():
        return cmd_go(argparse.Namespace(run=args.run)) if Run(folder / 'run.json').state in ('waiting', 'parked', 'paused') else cmd_status(argparse.Namespace(run=args.run))
    manifest = args.manifest or next((rjson(p)['approved_audio']['manifest'] for p in (ROOT / 'episodes' / args.episode).glob('*/scene.json')), None)
    if not manifest:
        sys.exit('Give --manifest for the approved MP3.')
    title = args.title or (re.sub(r'^Deep Six - |\.mp4$|\s+v\d+$', '', args.desktop_name) if args.desktop_name else None)
    ladder = [args.model] + [m for m in LADDER if m != args.model] if args.model != 'opus' else None
    r = new_run(args.episode, args.run, ROOT / manifest, 'now', title=title, start=args.start, end=args.end, limits=args.limits,
                exclude=args.exclude, ladder=ladder)
    old = rjson(folder / 'progress.json')
    if old and (folder / 'segments.json').exists():   # a run started by the October 19 runner: keep its plan and finished segments
        r.d.update(steps_done=['plan'], segments=rjson(folder / 'segments.json'), segments_done=old.get('segments_done', []),
                   made_by={s: args.model for s in old.get('segments_done', [])}, title=r.d.get('title') or args.run, new_assets=[])
        r.save()
    pid = ensure_worker()
    print(f'{args.run}: queued' + (f'; worker {pid} started.' if pid else '.') + f' Status: {rel(r.dir / "STATUS.md")}')


def cmd_prepare(args):
    out = ROOT / 'episodes' / args.episode / 'full' / 'words.json'
    if out.exists() and not args.force:
        print(json.dumps({'words': rel(out), 'status': 'exists'}))
        return
    out.parent.mkdir(parents=True, exist_ok=True)
    proc = subprocess.run([sys.executable, str(ROOT / 'tools' / 'align_words.py'), '--manifest', args.manifest, '--out', str(out)], cwd=ROOT)
    if proc.returncode:
        sys.exit('Word timing failed.')


def cmd_segment(args):
    """One-off model test: one Animator job on one segment, no retries or review (used for the October 19 model tests)."""
    episode_dir = ROOT / 'episodes' / args.episode
    full_words = rjson(episode_dir / 'full' / 'words.json')
    seg_dir = episode_dir / args.folder / args.name
    seg_dir.mkdir(parents=True, exist_ok=True)
    seg_words = dict(full_words)
    seg_words['caption_groups'] = [g for g in full_words['caption_groups'] if args.start - 0.05 <= full_words['words'][g['words'][0]]['start'] < args.end]
    wjson(seg_dir / 'words.json', seg_words)
    scene = rjson(episode_dir / 'full' / 'scene.json') or rjson(episode_dir / 'hook' / 'scene.json')
    module = f'scenes/{args.name}.mjs'
    scene.update({'scene_id': args.name, 'module': module, 'revision': 'v1', 'output_stem': 'segment', 'timing': 'words.json',
                  'shot_list': 'shot-list.json', 'audio_excerpt_start_seconds': args.start, 'audio_excerpt_end_seconds': args.end,
                  'duration_seconds': round(args.end - args.start, 3), 'absolute_time': True})
    scene.pop('tail_seconds', None)
    wjson(seg_dir / 'scene.json', scene)
    x = ''.join(f'- Do not open {e}. It is withheld for this test.\n' for e in args.exclude)
    brief = SEGMENT_BRIEF.format(episode=args.episode, start=args.start, end=args.end, word_lines=word_lines(full_words['words'], args.start, args.end),
                                 limits=args.limits, assets='', exclusions=('\nWithheld files:\n' + x) if x else '',
                                 shot_list=rel(seg_dir / 'shot-list.json'), module=module, scene_json=rel(seg_dir / 'scene.json'),
                                 dev_dir=rel(seg_dir / 'dev'))
    ladder = [args.model] if args.no_fallback else [args.model] + [m for m in LADDER if m != args.model]
    try:
        result, model = agent_job('animator', brief, seg_dir / 'job', RESULT_SCHEMA, APPROVED_FRAMES, allow=[module, rel(seg_dir)], ladder=ladder)
    except (JobFailed, Pause) as e:
        sys.exit(f'Segment job did not finish: {e}')
    code, out = node('render-shots.mjs', rel(seg_dir / 'scene.json'), '--check-motion', timeout=7200)
    print(json.dumps({'model': MODELS[model], 'status': result.get('status'), 'motion': out.splitlines()[-1] if code == 0 else out[-400:]}))


def cmd_render(args):
    """Detached render on the next free revision; waits and prints the result. Closing the chat does not stop the render."""
    scene = Path(args.scene)
    scene = scene if scene.is_absolute() else ROOT / scene
    data = rjson(scene)
    data['revision'] = vf.next_revision(scene.parent / 'renders', data.get('output_stem', 'hook'))
    wjson(scene, data)
    (scene.parent / 'renders').mkdir(exist_ok=True)
    log = scene.parent / 'renders' / f"render-{data['revision']}.log"
    pid = vf.start_render(scene, log)
    print(json.dumps({'render': data['revision'], 'pid': pid, 'log': rel(log)}), flush=True)
    while vf.alive(pid, 'render-shots.mjs'):
        time.sleep(5)
    print(log.read_text().strip().splitlines()[-1] if log.exists() else '')


def cmd_deliver(args):
    title = args.title or re.sub(r'^Deep Six - |\.mp4$|\s+v\d+$', '', args.desktop_name or Path(args.mp4).stem)
    print(json.dumps(vf.deliver(Path(args.mp4).resolve(), title, args.version)))


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest='command', required=True)
    p = sub.add_parser('start', help='record Drew\'s start choice for an approved MP3')
    p.add_argument('--episode', required=True)
    p.add_argument('--manifest', required=True)
    p.add_argument('--when', required=True, choices=['now', 'tonight', 'later'])
    p.add_argument('--run')
    p.add_argument('--title')
    p.add_argument('--start', type=float, default=0.0)
    p.add_argument('--end', type=float)
    p.add_argument('--limits', default='')
    p.add_argument('--exclude', action='append', default=[])
    p.add_argument('--ladder', help='comma list, default opus,sol,astra')
    p = sub.add_parser('verdict', help="record Drew's verdict in his words")
    p.add_argument('--run', required=True)
    p.add_argument('--decision', required=True, choices=['approve', 'notes'])
    p.add_argument('--says', required=True)
    for name in ('go', 'stop'):
        p = sub.add_parser(name)
        p.add_argument('--run', required=True)
        if name == 'stop':
            p.add_argument('--reason', default='')
    p = sub.add_parser('status')
    p.add_argument('--run')
    sub.add_parser('work', help='the background worker (started automatically)')
    p = sub.add_parser('full', help='old form: start a run now')
    p.add_argument('--episode', required=True)
    p.add_argument('--run', required=True)
    p.add_argument('--manifest')
    p.add_argument('--title')
    p.add_argument('--start', type=float, default=0.0)
    p.add_argument('--end', type=float)
    p.add_argument('--model', choices=LADDER, default='opus')
    p.add_argument('--effort', help='ignored: each model has its fixed effort')
    p.add_argument('--backup', help='ignored: the ladder is opus, sol, astra')
    p.add_argument('--limits', default='')
    p.add_argument('--exclude', action='append', default=[])
    p.add_argument('--timeout', type=int, help='ignored: AI jobs are limited to 3 h')
    p.add_argument('--desktop-name')
    p = sub.add_parser('prepare')
    p.add_argument('--episode', required=True)
    p.add_argument('--manifest', required=True)
    p.add_argument('--force', action='store_true')
    p = sub.add_parser('segment')
    p.add_argument('--episode', required=True)
    p.add_argument('--name', required=True)
    p.add_argument('--start', type=float, required=True)
    p.add_argument('--end', type=float, required=True)
    p.add_argument('--folder', default='segments')
    p.add_argument('--model', choices=list(MODELS), default='opus')
    p.add_argument('--limits', default='see the approved narration file for this episode.')
    p.add_argument('--exclude', action='append', default=[])
    p.add_argument('--no-fallback', action='store_true')
    p = sub.add_parser('render')
    p.add_argument('--scene', required=True)
    p = sub.add_parser('deliver')
    p.add_argument('--mp4', required=True)
    p.add_argument('--title')
    p.add_argument('--desktop-name')
    p.add_argument('--version', type=int, default=1)
    args = parser.parse_args()
    {'start': cmd_start, 'verdict': cmd_verdict, 'go': cmd_go, 'stop': cmd_stop, 'status': cmd_status, 'work': cmd_work,
     'full': cmd_full, 'prepare': cmd_prepare, 'segment': cmd_segment, 'render': cmd_render, 'deliver': cmd_deliver}[args.command](args)


if __name__ == '__main__':
    main()
