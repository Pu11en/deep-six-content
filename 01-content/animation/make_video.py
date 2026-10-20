#!/usr/bin/env python3
"""Deep Six MP3-to-MP4 video flow. Default agent: Opus 5.5 through Claude Code; backups: GPT-6 Sol, then GPT-6 Astra (Codex).

The agent follows VIDEO-FLOW.md and the choreography prompts, writes new scene code inside this
folder, renders its own frames and looks at them until the checks pass. This script prepares the
inputs, guards the approved files, validates what the agent wrote and renders the result.

  python3 make_video.py prepare  --episode ID --manifest ../audio/ID/RUN/comparison.json
  python3 make_video.py full     --episode ID --run NAME [--start S --end E] [--model opus|sol|astra] [--desktop-name "Deep Six - ....mp4"]
  python3 make_video.py segment  --episode ID --name NAME --start S --end E [--model opus|sol|astra] [--effort xhigh]
  python3 make_video.py render   --scene episodes/ID/.../scene.json
  python3 make_video.py deliver  --mp4 PATH --desktop-name "Deep Six - ....mp4"

Subscription models through Codex; no API keys, no paid calls. Videos are copied to Drew's Windows
Desktop; no player is ever opened.
"""
import argparse
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent
# Default (Drew, Oct 19): Opus 5.5 at max effort. When Claude credits run out, Sol, then Astra (Drew rated Sol higher).
# Codex models share one ChatGPT usage limit; Claude models use Drew's Claude plan.
MODELS = {'astra': 'gpt-6-astra', 'sol': 'gpt-6-sol', 'sonnet': 'claude-sonnet-5-5', 'opus': 'claude-opus-5-5'}
PROVIDER = {'astra': 'codex', 'sol': 'codex', 'sonnet': 'claude', 'opus': 'claude'}
PROTECTED = ['scenes', 'vendor', 'fonts', 'tools', 'choreography', 'render-shots.mjs', 'render-frame.mjs', 'render-motion.mjs',
             'brand.json', 'package.json', 'package-lock.json', 'VIDEO-FLOW.md', 'KIT-API.md', 'make_video.py', 'science-notes.md']
UNAVAILABLE = re.compile(r'not supported|usage limit|rate limit|429|quota|model_not_found|overloaded', re.I)
LIMIT = re.compile(r'hit your usage limit[^"]*?try again at ([^".]+(?:\.\d+)?[^"]*?)(?:\."|")', re.I)

RESULT_SCHEMA = {
    'type': 'object', 'additionalProperties': False,
    'required': ['status', 'files_written', 'shot_count', 'self_check_rounds', 'longest_still_seconds', 'picture_change_median', 'remaining_issues', 'summary'],
    'properties': {
        'status': {'type': 'string', 'enum': ['done', 'blocked']},
        'files_written': {'type': 'array', 'items': {'type': 'string'}},
        'shot_count': {'type': 'integer'},
        'self_check_rounds': {'type': 'integer'},
        'longest_still_seconds': {'type': 'number'},
        'picture_change_median': {'type': 'number'},
        'remaining_issues': {'type': 'array', 'items': {'type': 'string'}},
        'summary': {'type': 'string'},
    },
}


PLAN_SCHEMA = {
    'type': 'object', 'additionalProperties': False,
    'required': ['status', 'files_written', 'shot_count', 'segment_count', 'new_assets', 'summary'],
    'properties': {
        'status': {'type': 'string', 'enum': ['done', 'blocked']},
        'files_written': {'type': 'array', 'items': {'type': 'string'}},
        'shot_count': {'type': 'integer'},
        'segment_count': {'type': 'integer'},
        'new_assets': {'type': 'array', 'items': {'type': 'string'}},
        'summary': {'type': 'string'},
    },
}

PLAN_BRIEF = """You are the Deep Six video director. Your working root is the folder `01-content/animation`.
Plan a whole pest-education short for episode {episode}, narration time {start:.2f} to {end:.2f} seconds, in the approved
cut-paper style C. Match the pace and quality bar in VIDEO-FLOW.md. You plan pictures; you do not write scene code.

Narration words with their index in words.json and start time in seconds:
{word_lines}

Read these first: VIDEO-FLOW.md, choreography/director-prompt.md, KIT-API.md (what the kit and finished sets already draw),
science-notes.md. Episode limits: {limits}
{exclusions}
Write exactly these three files:
1. {shot_list}: every shot, in the director prompt's JSON shape, with absolute times. Every phrase gets a visible action
   landing on its word. Add a top-level "new_assets" list naming any drawing the kit and sets do not have yet.
2. {segments}: a JSON list of {{"name", "start", "end"}} segments named {run}-seg01, {run}-seg02 and so on. They must be
   contiguous, cover {start:.2f} to {end:.2f} exactly, cut only in pauses between sentences, and last 6 to 15 seconds each.
3. {groups}: a JSON list of caption groups; each group is a list of word indexes from the list above. Cover every word once,
   in order, one to four words per group, broken at natural phrases.

Never modify existing files. When finished, reply with the JSON summary the output schema asks for.
"""

PLANNED_SEGMENT_NOTE = """
The director already planned this segment. Its shots are in {shot_list} (copied from the whole-video plan {plan}).
Implement those shots faithfully; refine details only to fix problems you see in your checks. Do not rewrite {shot_list}.
Earlier segments in this video, for continuity: {previous}
"""


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def protected_files():
    files = []
    for item in PROTECTED:
        p = ROOT / item
        if p.is_file():
            files.append(p)
        elif p.is_dir():
            files += [f for f in p.rglob('*') if f.is_file() and '__pycache__' not in f.parts]
    for renders in (ROOT / 'episodes').rglob('renders'):
        files += [f for f in renders.rglob('*') if f.is_file()]
    return files


class Guard:
    """Snapshot protected files before an agent runs; restore anything it changed or deleted."""

    def __init__(self, job_dir):
        self.backup = job_dir / 'protected-backup'
        self.hashes = {}
        self.unrestorable = set()
        for f in protected_files():
            rel = f.relative_to(ROOT)
            self.hashes[str(rel)] = sha(f)
            if f.stat().st_size > 5_000_000:
                self.unrestorable.add(str(rel))  # large videos: detect changes, do not copy
                continue
            dest = self.backup / rel
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(f, dest)

    def check(self):
        restored = []
        for rel, digest in self.hashes.items():
            f = ROOT / rel
            if not f.exists() or sha(f) != digest:
                if rel in self.unrestorable:
                    restored.append(rel + ' (CHANGED, large file not restorable)')
                    continue
                f.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(self.backup / rel, f)
                restored.append(rel)
        shutil.rmtree(self.backup)
        return restored


def run_codex(model, effort, brief, job_dir, timeout, schema_obj=None):
    """One Codex agent run in this folder with a workspace-write sandbox. Returns (ok, result, meta)."""
    schema = job_dir / 'result-schema.json'
    schema.write_text(json.dumps(schema_obj or RESULT_SCHEMA, indent=1))
    final = job_dir / f'final-{model}.json'
    events = job_dir / f'events-{model}.jsonl'
    cmd = ['codex', 'exec', '--ignore-user-config', '--skip-git-repo-check', '-m', MODELS[model],
           '-c', f'model_reasoning_effort="{effort}"', '-c', 'approval_policy="never"',
           '-s', 'workspace-write', '-C', str(ROOT), '--json', '--output-schema', str(schema), '-o', str(final), '-']
    env = {k: v for k, v in os.environ.items() if not k.startswith('OPENAI_')}
    started = time.time()
    with events.open('w') as out, (job_dir / f'stderr-{model}.log').open('w') as err:
        try:
            proc = subprocess.run(cmd, input=brief, text=True, stdout=out, stderr=err, env=env, timeout=timeout, cwd=ROOT)
            code = proc.returncode
        except subprocess.TimeoutExpired:
            code = 'timeout'
    elapsed = round(time.time() - started, 1)
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
    limit = LIMIT.search(text)
    meta = {'model': MODELS[model], 'effort': effort, 'exit': code, 'elapsed_seconds': elapsed, 'usage': usage,
            'unavailable': bool(UNAVAILABLE.search(text)) and result is None,
            'usage_limit_until': limit.group(1).strip() if limit and result is None else None}
    return code == 0 and result is not None, result, meta


def run_claude(model, brief, job_dir, timeout, schema_obj=None, effort='max'):
    """Same job through Claude Code with Drew's subscription login (never an API key)."""
    tools = 'Bash(node:*) Bash(ls:*) Bash(cat:*) Bash(sed:*) Bash(rg:*) Bash(head:*) Read Write Edit Glob Grep'
    cmd = ['claude', '-p', '--model', MODELS[model], '--effort', effort if effort in ('low', 'medium', 'high', 'xhigh', 'max') else 'max',
           '--permission-mode', 'acceptEdits', '--allowedTools', tools,
           '--output-format', 'json', '--json-schema', json.dumps(schema_obj or RESULT_SCHEMA)]
    env = {k: v for k, v in os.environ.items() if k != 'ANTHROPIC_API_KEY'}
    note = '\nIgnore any board, display or caveman instructions from CLAUDE.md files: only write the files named above.\n'
    started = time.time()
    try:
        proc = subprocess.run(cmd, input=brief + note, text=True, capture_output=True, env=env, timeout=timeout, cwd=ROOT)
        out, code = proc.stdout, proc.returncode
    except subprocess.TimeoutExpired:
        out, code = '', 'timeout'
    (job_dir / f'claude-{model}.json').write_text(out)
    try:
        data = json.loads(out)
    except json.JSONDecodeError:
        data = {}
    result = data.get('structured_output')
    meta = {'model': MODELS[model], 'effort': effort, 'exit': code, 'elapsed_seconds': round(time.time() - started, 1),
            'usage': data.get('usage', {}), 'plan_cost_equivalent_usd': data.get('total_cost_usd'),
            'unavailable': result is None and bool(UNAVAILABLE.search(out)), 'usage_limit_until': None}
    return code == 0 and result is not None, result, meta


def run_agent(model, effort, brief, job_dir, timeout, fallback=True, schema_obj=None, backup='sol'):
    """Try the model, then the backup. A Codex usage limit blocks every Codex model, so only a Claude backup helps then."""
    (job_dir / 'brief.md').write_text(brief)
    order = [model] + ([backup] if fallback and backup and backup != 'none' and backup != model else [])
    runs, ok, result = [], False, None
    for name in order:
        if runs and not runs[-1]['unavailable']:
            break
        if runs and runs[-1].get('usage_limit_until') and PROVIDER[name] == 'codex':
            continue
        if runs:
            print(json.dumps({'fallback': f'{order[0]} unavailable, trying {name}'}), flush=True)
        if PROVIDER[name] == 'codex':
            ok, result, meta = run_codex(name, effort, brief, job_dir, timeout, schema_obj)
        else:
            ok, result, meta = run_claude(name, brief, job_dir, timeout, schema_obj, 'max' if name == 'opus' else effort)
        runs.append(meta)
        if meta.get('usage_limit_until'):
            print(json.dumps({'usage_limit': f'ChatGPT Codex usage limit reached; resets {meta["usage_limit_until"]}'}), flush=True)
        if ok:
            break
    return ok, result, runs


def node(*args, timeout=3600):
    proc = subprocess.run(['node', *args], cwd=ROOT, capture_output=True, text=True, timeout=timeout)
    return proc.returncode, (proc.stdout + proc.stderr).strip()


def base_scene(episode):
    """Copy the approved audio and style references from the episode's existing scene settings."""
    for candidate in [ROOT / 'episodes' / episode / 'full' / 'scene.json', ROOT / 'episodes' / episode / 'hook' / 'scene.json']:
        if candidate.exists():
            return json.loads(candidate.read_text())
    sys.exit('No scene settings with approved audio and style for this episode. Run prepare first.')


def cmd_prepare(args):
    out = ROOT / 'episodes' / args.episode / 'full' / 'words.json'
    if out.exists() and not args.force:
        print(json.dumps({'words': str(out.relative_to(ROOT)), 'status': 'exists'}))
        return
    proc = subprocess.run([sys.executable, str(ROOT / 'tools' / 'align_words.py'), '--manifest', args.manifest, '--out', str(out)], cwd=ROOT)
    if proc.returncode:
        sys.exit('Word timing failed.')


def segment_words(full_words, start, end):
    """Keep every word (the renderer checks the full approved wording); keep only this segment's caption groups."""
    seg = dict(full_words)
    seg['caption_groups'] = [g for g in full_words['caption_groups']
                             if start - 0.05 <= full_words['words'][g['words'][0]]['start'] < end]
    return seg


SEGMENT_BRIEF = """You are the Deep Six video animator. Your working root is the folder `01-content/animation`.
Make one segment of a pest-education short in the approved cut-paper style C. It must match the quality, pace and look of the
approved reference video described in VIDEO-FLOW.md.

Segment: episode {episode}, absolute narration time {start:.2f} to {end:.2f} seconds.
Narration words in this segment, with start times in seconds:
{word_lines}

Read these first, in order:
1. VIDEO-FLOW.md: the recipe and the quality bar.
2. choreography/director-prompt.md, then choreography/animator-prompt.md.
3. KIT-API.md: everything the kit and the finished sets can draw. Open scenes/paper-kit.mjs, scenes/nest-world.mjs or
   scenes/yard-world.mjs only to check one specific function.
4. scenes/hook-fire-ant-drought.mjs: a complete approved example. Skim it for structure.
5. science-notes.md. Episode limits: {limits}
{exclusions}
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
- Never modify, rename or delete existing files. Create only the files named above. Put any kit additions inside your module.
- No network and no installs. Keep every frame a pure function of t.
- No on-screen words except the kit's captions. A question mark or X is allowed only where the narration questions or negates.

When finished, reply with the JSON summary the output schema asks for.
"""


def cmd_segment(args):
    episode_dir = ROOT / 'episodes' / args.episode
    words_path = Path(getattr(args, 'words', None) or episode_dir / 'full' / 'words.json')
    full_words = json.loads(words_path.read_text())
    seg_dir = episode_dir / args.folder / args.name
    seg_dir.mkdir(parents=True, exist_ok=True)
    (seg_dir / 'words.json').write_text(json.dumps(segment_words(full_words, args.start, args.end), indent=1) + '\n')
    scene = base_scene(args.episode)
    module = f'scenes/{args.name}.mjs'
    scene.update({'scene_id': args.name, 'module': module, 'revision': 'v1', 'output_stem': 'segment', 'timing': 'words.json',
                  'shot_list': 'shot-list.json', 'audio_excerpt_start_seconds': args.start, 'audio_excerpt_end_seconds': args.end,
                  'duration_seconds': round(args.end - args.start, 3), 'absolute_time': True})
    scene.pop('tail_seconds', None)
    scene_path = seg_dir / 'scene.json'
    scene_path.write_text(json.dumps(scene, indent=2) + '\n')
    words = [w for w in full_words['words'] if args.start - 0.05 <= w['start'] < args.end]
    word_lines = '\n'.join(f"  {w['start']:6.2f}  {w['text']}" for w in words)
    exclusions = ''.join(f'- Do not open {x}. It is withheld for this test.\n' for x in args.exclude)
    if exclusions:
        exclusions = '\nWithheld files:\n' + exclusions
    rel = lambda p: str(p.relative_to(ROOT))
    brief = SEGMENT_BRIEF.format(episode=args.episode, start=args.start, end=args.end, word_lines=word_lines,
                                 limits=args.limits, exclusions=exclusions, shot_list=rel(seg_dir / 'shot-list.json'),
                                 module=module, scene_json=rel(scene_path), dev_dir=rel(seg_dir / 'dev'))
    plan = getattr(args, 'plan', None)
    if plan:
        brief = brief.replace(f"- {rel(seg_dir / 'shot-list.json')}: your shot list for this segment, absolute times, in the director prompt's JSON shape.\n", '')
        brief += PLANNED_SEGMENT_NOTE.format(shot_list=rel(seg_dir / 'shot-list.json'), plan=plan, previous=getattr(args, 'previous', 'none'))
    job_dir = seg_dir / 'job'
    job_dir.mkdir(exist_ok=True)
    guard = Guard(job_dir)
    print(json.dumps({'job': rel(job_dir), 'model': MODELS[args.model], 'effort': args.effort}), flush=True)
    ok, result, runs = run_agent(args.model, args.effort, brief, job_dir, args.timeout, fallback=not args.no_fallback,
                                 backup=getattr(args, 'backup', 'sol'))
    restored = guard.check()
    report = {'ok': ok, 'agent_result': result, 'runs': runs, 'protected_files_restored': restored}
    # Independent checks by the runner.
    code, out = node('--check', module)
    report['module_syntax'] = 'ok' if code == 0 else out[-800:]
    if code == 0 and (seg_dir / 'shot-list.json').exists():
        code, out = node('render-shots.mjs', rel(scene_path), '--check-motion', timeout=7200)
        report['motion'] = json.loads(out.splitlines()[-1]) if code == 0 else out[-800:]
    (job_dir / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps({k: report[k] for k in ('ok', 'protected_files_restored', 'module_syntax')} | {'motion': report.get('motion')}))
    return report



def assemble(run_dir, run, segments, scene_base, words, start, end):
    imports = '\n'.join(f"import {{ createScene as seg{i + 1:02d} }} from './{seg['name']}.mjs';" for i, seg in enumerate(segments))
    table = ',\n  '.join(f"{{ start: {seg['start']}, end: {seg['end']}, create: seg{i + 1:02d} }}" for i, seg in enumerate(segments))
    module = f"""// Generated by make_video.py: joins the segments of run {run} and draws one caption track.
import {{ makeFibres, createCaptions }} from './paper-kit.mjs';
{imports}

const SEGMENTS = [
  {table},
];

export function createScene(config, timing) {{
  const made = SEGMENTS.map(s => ({{ ...s, scene: s.create(config, timing) }}));
  const texture = makeFibres((config.seed ?? 1) | 0);
  const captions = createCaptions(timing.words, timing.caption_groups, {{
    texture, centerY: config.caption_center_y ?? 1420, endTime: (config.time_offset ?? 0) + config.duration_seconds + 10,
  }});
  const pick = t => made.findLast(s => t >= s.start) ?? made[0];
  const drawWorld = (ctx, t) => pick(t).scene.drawWorld(ctx, t);
  return {{
    duration: config.duration_seconds,
    blurWindows: made.flatMap(s => s.scene.blurWindows ?? []),
    drawWorld,
    drawOverlay: captions,
    draw(ctx, t) {{ drawWorld(ctx, t); captions(ctx, t); }},
  }};
}}
"""
    path = ROOT / 'scenes' / f'{run}-full.mjs'
    path.write_text(module)
    scene = dict(scene_base)
    scene.update({'scene_id': f'{run}-full', 'module': f'scenes/{run}-full.mjs', 'revision': 'v1', 'output_stem': run,
                  'timing': 'words.json', 'shot_list': 'shot-list.json', 'audio_excerpt_start_seconds': start,
                  'audio_excerpt_end_seconds': end, 'duration_seconds': round(end - start, 3), 'absolute_time': True})
    scene.pop('tail_seconds', None)
    (run_dir / 'scene.json').write_text(json.dumps(scene, indent=2) + '\n')
    return path


def cmd_full(args):
    episode_dir = ROOT / 'episodes' / args.episode
    words = json.loads((episode_dir / 'full' / 'words.json').read_text())
    end = args.end if args.end is not None else words['excerpt_end_seconds']
    run_dir = episode_dir / 'runs' / args.run
    run_dir.mkdir(parents=True, exist_ok=True)
    rel = lambda p: str(p.relative_to(ROOT))
    progress = run_dir / 'progress.json'
    state = json.loads(progress.read_text()) if progress.exists() else {'segments_done': []}
    in_range = [(i, w) for i, w in enumerate(words['words']) if args.start - 0.05 <= w['start'] < end]
    exclusions = ''.join(f'- Do not open {x}. It is withheld for this run.\n' for x in args.exclude)
    if exclusions:
        exclusions = '\nWithheld files:\n' + exclusions

    # 1. Director: whole-video plan, segment cuts and caption groups.
    plan, segs_file, groups_file = run_dir / 'shot-list.json', run_dir / 'segments.json', run_dir / 'caption-groups.json'
    if not (plan.exists() and segs_file.exists() and groups_file.exists()):
        job = run_dir / 'plan-job'
        job.mkdir(exist_ok=True)
        guard = Guard(job)
        brief = PLAN_BRIEF.format(episode=args.episode, start=args.start, end=end, limits=args.limits, exclusions=exclusions,
                                  word_lines='\n'.join(f'  [{i}] {w["start"]:6.2f}  {w["text"]}' for i, w in in_range),
                                  shot_list=rel(plan), segments=rel(segs_file), groups=rel(groups_file), run=args.run)
        print(json.dumps({'step': 'plan', 'model': MODELS[args.model]}), flush=True)
        ok, result, runs = run_agent(args.model, args.effort, brief, job, args.timeout, schema_obj=PLAN_SCHEMA, backup=args.backup)
        restored = guard.check()
        (job / 'report.json').write_text(json.dumps({'ok': ok, 'result': result, 'runs': runs, 'restored': restored}, indent=2) + '\n')
        if not ok:
            sys.exit('Planning failed; see ' + rel(job))
    segments = json.loads(segs_file.read_text())
    groups = json.loads(groups_file.read_text())
    covered = [i for g in groups for i in g]
    if covered != [i for i, _ in in_range] or any(not 1 <= len(g) <= 4 for g in groups):
        sys.exit('Caption groups must cover every word once, in order, one to four words each.')
    if abs(segments[0]['start'] - args.start) > 0.3 or abs(segments[-1]['end'] - end) > 0.3 or any(
            abs(a['end'] - b['start']) > 1e-6 for a, b in zip(segments, segments[1:])):
        sys.exit('Segments must be contiguous and cover the whole range.')
    run_words = dict(words)
    keep = [g for g in words['caption_groups'] if not (args.start - 0.05 <= words['words'][g['words'][0]]['start'] < end)]
    run_words['caption_groups'] = sorted(keep + [{'words': g} for g in groups], key=lambda g: g['words'][0])
    (run_dir / 'words.json').write_text(json.dumps(run_words, indent=1) + '\n')
    full_plan = json.loads(plan.read_text())

    # 2. Animator: one job per segment, in order.
    previous = []
    for seg in segments:
        seg_dir = run_dir / seg['name']
        seg_dir.mkdir(exist_ok=True)
        subset = dict(full_plan)
        subset['shots'] = [sh for sh in full_plan['shots'] if seg['start'] - 0.05 <= sh['start'] < seg['end']]
        (seg_dir / 'shot-list.json').write_text(json.dumps(subset, indent=1) + '\n')
        if seg['name'] not in state['segments_done']:
            seg_args = argparse.Namespace(episode=args.episode, name=seg['name'], start=seg['start'], end=seg['end'],
                                          folder=f"runs/{args.run}", model=args.model, effort=args.effort, limits=args.limits,
                                          exclude=args.exclude, timeout=args.timeout, no_fallback=False, plan=rel(plan), backup=args.backup,
                                          words=str(run_dir / 'words.json'),
                                          previous=', '.join(previous) or 'none')
            print(json.dumps({'step': 'segment', 'name': seg['name'], 'start': seg['start'], 'end': seg['end']}), flush=True)
            report = cmd_segment(seg_args)
            if report['module_syntax'] != 'ok' or not report['ok']:
                limit = next((r['usage_limit_until'] for r in report['runs'] if r.get('usage_limit_until')), None)
                if limit:
                    sys.exit(f"Paused at {seg['name']}: the ChatGPT Codex usage limit resets {limit}. Run the same command again then; finished work is kept.")
                sys.exit(f"Segment {seg['name']} failed; see its job folder.")
            state['segments_done'].append(seg['name'])
            progress.write_text(json.dumps(state, indent=1) + '\n')
        previous.append(f"scenes/{seg['name']}.mjs")

    # 3. Assemble, render, deliver.
    assemble(run_dir, args.run, segments, base_scene(args.episode), run_words, args.start, end)
    print(json.dumps({'step': 'render', 'scene': rel(run_dir / 'scene.json')}), flush=True)
    code, out = node('render-shots.mjs', rel(run_dir / 'scene.json'), timeout=4 * 3600)
    print(out.splitlines()[-1] if out else '')
    if code:
        sys.exit('Render failed.')
    if args.desktop_name:
        cmd_deliver(argparse.Namespace(mp4=str(run_dir / 'renders' / f'{args.run}-v1.mp4'), desktop_name=args.desktop_name))

def cmd_render(args):
    code, out = node('render-shots.mjs', args.scene, timeout=10800)
    print(out.splitlines()[-1] if out else '')
    sys.exit(code)


def cmd_deliver(args):
    src = Path(args.mp4).resolve()
    win_desktop = subprocess.run(['powershell.exe', '-NoProfile', '-Command', '[Environment]::GetFolderPath("Desktop")'],
                                 capture_output=True, text=True).stdout.strip()
    desktop = Path(subprocess.run(['wslpath', win_desktop], capture_output=True, text=True).stdout.strip())
    dest = desktop / args.desktop_name
    if dest.exists():
        sys.exit(f'{dest.name} already exists on the Desktop; nothing was overwritten.')
    shutil.copy2(src, dest)
    same = sha(src) == sha(dest)
    print(json.dumps({'desktop_copy': args.desktop_name, 'verified': same, 'player_opened': False}))
    sys.exit(0 if same else 1)


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest='command', required=True)
    p = sub.add_parser('prepare')
    p.add_argument('--episode', required=True)
    p.add_argument('--manifest', required=True)
    p.add_argument('--force', action='store_true')
    p = sub.add_parser('segment')
    p.add_argument('--episode', required=True)
    p.add_argument('--name', required=True, help='module and folder name, e.g. d6-xxxx-seg03')
    p.add_argument('--start', type=float, required=True)
    p.add_argument('--end', type=float, required=True)
    p.add_argument('--folder', default='segments')
    p.add_argument('--model', choices=list(MODELS), default='opus', help='default Opus 5.5 (max effort); use sol or astra when Claude credits are out')
    p.add_argument('--backup', choices=list(MODELS) + ['none'], default='sol', help='used if the model is unavailable')
    p.add_argument('--effort', default='xhigh', choices=['low', 'medium', 'high', 'xhigh', 'max', 'ultra'])
    p.add_argument('--limits', default='see the approved narration file for this episode.')
    p.add_argument('--exclude', action='append', default=[])
    p.add_argument('--timeout', type=int, default=3 * 3600)
    p.add_argument('--no-fallback', action='store_true')
    p = sub.add_parser('full', help='plan, make every segment, join, render and copy to the Desktop')
    p.add_argument('--episode', required=True)
    p.add_argument('--run', required=True, help='name for this run, e.g. d6-xxxx-astra')
    p.add_argument('--start', type=float, default=0.0)
    p.add_argument('--end', type=float)
    p.add_argument('--model', choices=list(MODELS), default='opus', help='default Opus 5.5 (max effort); use sol or astra when Claude credits are out')
    p.add_argument('--backup', choices=list(MODELS) + ['none'], default='sol', help='used if the model is unavailable')
    p.add_argument('--effort', default='xhigh', choices=['low', 'medium', 'high', 'xhigh', 'max', 'ultra'])
    p.add_argument('--limits', default='see the approved narration file for this episode.')
    p.add_argument('--exclude', action='append', default=[])
    p.add_argument('--timeout', type=int, default=3 * 3600)
    p.add_argument('--desktop-name')
    p = sub.add_parser('render')
    p.add_argument('--scene', required=True)
    p = sub.add_parser('deliver')
    p.add_argument('--mp4', required=True)
    p.add_argument('--desktop-name', required=True)
    args = parser.parse_args()
    {'prepare': cmd_prepare, 'segment': cmd_segment, 'full': cmd_full, 'render': cmd_render, 'deliver': cmd_deliver}[args.command](args)


if __name__ == '__main__':
    main()
