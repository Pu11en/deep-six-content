"""Offline tests for the MP3-to-MP4 runner. No AI calls, no renders, no Desktop writes.
Run from 01-content/animation:  python3 -m unittest tests.test_make_video -v"""
import argparse
import json
import os
import shutil
import sys
import tempfile
import unittest
from datetime import datetime, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import make_video as mv  # noqa: E402
import video_finish as vf  # noqa: E402

WASP = 'D6-01096ba333e3'
WASP_MANIFEST = ROOT / '../audio/D6-01096ba333e3/full-chris-01/comparison.json'
WASP_FULL = ROOT / 'episodes' / WASP / 'full'


class Temp(unittest.TestCase):
    """Every test gets its own episodes folder, learning files and Desktop; the real ones are never touched."""

    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix='mv-test-'))
        self.saved = {k: getattr(mv, k) for k in ('EPISODES', 'PROBLEMS', 'LEARNED', 'VERDICTS', 'ensure_worker', 'Guard', 'RUNNERS', 'D6_TOOL')}
        mv.EPISODES = self.tmp / 'episodes'
        mv.PROBLEMS, mv.LEARNED, mv.VERDICTS = self.tmp / 'problems.json', self.tmp / 'learned.md', self.tmp / 'verdicts.jsonl'
        mv.ensure_worker = lambda: None
        mv.Guard = FakeGuard
        self.desktop = self.tmp / 'Desktop'
        self.desktop.mkdir()
        self.saved_vf = {k: getattr(vf, k) for k in ('desktop', 'board')}
        vf.desktop = lambda: (self.desktop, 'C:\\Users\\test\\Desktop')
        vf.board = lambda path, caption: True

    def tearDown(self):
        for k, v in self.saved.items():
            setattr(mv, k, v)
        for k, v in self.saved_vf.items():
            setattr(vf, k, v)
        shutil.rmtree(self.tmp)

    def run_obj(self, when='later', name='zz-test'):
        return mv.new_run(WASP, name, WASP_MANIFEST, when, title='Test Wasp')

    def planned_run(self):
        """A run with the approved ensign-wasp words and lesson plan, split into four segments at sentence pauses."""
        r = self.run_obj()
        shutil.copyfile(WASP_FULL / 'words.json', r.dir / 'words.json')
        r.d.update(signoff=130, lesson_range=[0, 44.1333], video_range=[0, 48.352])
        plan = json.loads((WASP_FULL / 'shot-list.json').read_text())
        plan['shots'] = [s for s in plan['shots'] if s['id'] != 'O1']
        (r.dir / 'shot-list.json').write_text(json.dumps(plan))
        cuts = [0, 13.3, 24.8, 34.2, 44.1333]
        segs = [{'name': f'zz-test-seg{i + 1:02d}', 'start': a, 'end': b} for i, (a, b) in enumerate(zip(cuts, cuts[1:]))]
        (r.dir / 'segments.json').write_text(json.dumps(segs))
        words = json.loads((WASP_FULL / 'words.json').read_text())
        groups = [g['words'] for g in words['caption_groups'] if g['words'][0] < 130]
        (r.dir / 'caption-groups.json').write_text(json.dumps(groups))
        r.d['segments'] = segs
        r.save()
        return r


class FakeGuard:
    def __init__(self, *a, **k):
        pass

    def check(self):
        return []


def fake_runners(script):
    """script: model -> (result or None, meta overrides). Records the order models were tried."""
    tried = []

    def make(provider):
        def run(model, brief, job_dir, schema, role, images, timeout):
            tried.append(model)
            result, meta = script[model]
            base = {'model': mv.MODELS[model], 'effort': mv.EFFORT[model], 'exit': 0, 'elapsed_seconds': 0, 'usage': {},
                    'limit': False, 'reset': None, 'unavailable': False}
            base.update(meta)
            return result, base
        return run
    return {'claude': make('claude'), 'codex': make('codex')}, tried


class Ladder(Temp):
    def job(self, script, **kw):
        mv.RUNNERS, tried = fake_runners(script)
        return mv.agent_job('animator', 'brief', self.tmp / 'job', mv.RESULT_SCHEMA, **kw), tried

    def test_opus_first(self):
        (result, model), tried = self.job({'opus': ({'status': 'done'}, {})})
        self.assertEqual((model, tried), ('opus', ['opus']))

    def test_claude_limit_moves_to_sol(self):
        (result, model), tried = self.job({'opus': (None, {'limit': True, 'reset': '2026-10-21T01:00:00-05:00'}),
                                           'sol': ({'status': 'done'}, {})})
        self.assertEqual((model, tried), ('sol', ['opus', 'sol']))

    def test_sol_unavailable_moves_to_astra(self):
        (result, model), tried = self.job({'opus': (None, {'limit': True}), 'sol': (None, {'unavailable': True}),
                                           'astra': ({'status': 'done'}, {})})
        self.assertEqual((model, tried), ('astra', ['opus', 'sol', 'astra']))

    def test_codex_limit_blocks_astra_and_pauses_until_first_reset(self):
        with self.assertRaises(mv.Pause) as caught:
            self.job({'opus': (None, {'limit': True, 'reset': '2026-10-21T03:00:00-05:00'}),
                      'sol': (None, {'limit': True, 'reset': '2026-10-21T01:30:00-05:00'}),
                      'astra': ({'status': 'done'}, {})})
        self.assertEqual(caught.exception.until.isoformat(), '2026-10-21T01:30:00-05:00')

    def test_quality_failure_never_switches_model(self):
        mv.RUNNERS, tried = fake_runners({'opus': (None, {'exit': 1}), 'sol': ({'status': 'done'}, {})})
        with self.assertRaises(mv.JobFailed) as caught:
            mv.agent_job('animator', 'brief', self.tmp / 'job', mv.RESULT_SCHEMA)
        self.assertEqual((caught.exception.model, tried), ('opus', ['opus']))

    def test_retry_keeps_the_same_model(self):
        (result, model), tried = self.job({'opus': ({'status': 'done'}, {}), 'sol': ({'status': 'done'}, {})}, start_at='sol')
        self.assertEqual(tried, ['sol'])


class Resets(unittest.TestCase):
    def test_parse(self):
        base = datetime(2026, 10, 20, 15, 0).astimezone()
        self.assertEqual(mv.parse_reset('Claude AI usage limit reached|1761012000').timestamp(), 1761012000)
        self.assertEqual(mv.parse_reset("You've hit your limit · resets 5pm (America/Chicago)", base).hour, 17)
        self.assertEqual(mv.parse_reset('resets 9am', base).day, 21)
        t = mv.parse_reset('try again at Oct 21st, 2026 9:41 PM', base)
        self.assertEqual((t.month, t.day, t.hour, t.minute), (10, 21, 21, 41))
        self.assertIsNone(mv.parse_reset('something else'))


class Plan(Temp):
    def test_approved_wasp_plan_passes(self):
        self.assertEqual(mv.check_plan(self.planned_run()), [])

    def test_broken_plan_is_sent_back(self):
        r = self.planned_run()
        plan = json.loads((r.dir / 'shot-list.json').read_text())
        plan['shots'][5]['end'] += 1.0
        plan['shots'][6]['start'] += 1.0
        plan['shots'][7]['beats'][0]['at'] += 0.3
        (r.dir / 'shot-list.json').write_text(json.dumps(plan))
        segs = json.loads((r.dir / 'segments.json').read_text())
        segs[0]['end'] = segs[1]['start'] = 12.0
        (r.dir / 'segments.json').write_text(json.dumps(segs))
        groups = json.loads((r.dir / 'caption-groups.json').read_text())
        (r.dir / 'caption-groups.json').write_text(json.dumps(groups[1:]))
        text = ' | '.join(mv.check_plan(r))
        for expected in ('Caption groups', 'not in a pause', 'no shot over 2 s', 'not on a word start'):
            self.assertIn(expected, text)


class Outro(unittest.TestCase):
    def test_fit_reproduces_the_approved_ensign_wasp_ending(self):
        words = json.loads((WASP_FULL / 'words.json').read_text())['words']
        with tempfile.TemporaryDirectory() as tmp:
            info = vf.fit_outro(words, Path(tmp) / 'plan.json', 48.352653)
        approved = json.loads((WASP_FULL / 'outro-retime.json').read_text())
        self.assertEqual(info['mapping'], approved['mapping'])
        self.assertEqual(info['caption_fade_seconds'], [46.24, 46.4])        # the values Drew approved in the hand-made module
        for k in ('outro_start_frame', 'end_frame', 'frames_trimmed', 'logo_landed_seconds', 'hold_after_last_word_seconds'):
            self.assertEqual(info[k], approved[k])

    def test_slower_narrator_needs_no_trim_and_faster_one_parks(self):
        words = json.loads((WASP_FULL / 'words.json').read_text())['words']
        slow = [dict(w) for w in words]
        for w in slow[134:]:
            w['start'] += 0.5
            w['end'] += 0.5
        with tempfile.TemporaryDirectory() as tmp:
            self.assertEqual(vf.fit_outro(slow, Path(tmp) / 'p.json', 48.9)['frames_trimmed'], 0)
            fast = [dict(w) for w in words]
            for w in fast[134:]:
                w['start'] -= 1.0
                w['end'] -= 1.0
            with self.assertRaises(vf.FinishError):
                vf.fit_outro(fast, Path(tmp) / 'p.json', 47.4)


class Files(Temp):
    def test_next_revision_skips_partial_files(self):
        renders = self.tmp / 'renders'
        renders.mkdir()
        (renders / 'full-v1.mp4').write_text('x')
        (renders / 'full-v2.partial.mp4').write_text('crashed')
        self.assertEqual(vf.next_revision(renders, 'full'), 'v3')

    def test_desktop_name_clash_takes_next_number(self):
        src = self.tmp / 'a.mp4'
        src.write_bytes(b'video')
        (self.desktop / 'Deep Six - Test Wasp v1.mp4').write_bytes(b'older')
        rec = vf.deliver(src, 'Test Wasp', 1)
        self.assertEqual((rec['name'], rec['player_opened']), ('Deep Six - Test Wasp v2.mp4', False))
        self.assertEqual((self.desktop / 'Deep Six - Test Wasp v1.mp4').read_bytes(), b'older')
        self.assertEqual(rec['sha256'], vf.sha(self.desktop / rec['name']))

    def test_guard_restores_changed_files(self):
        target = self.tmp / 'kit.mjs'
        target.write_text('approved')
        saved = mv.protected_files
        mv.protected_files = lambda allow=(): []
        try:
            mv.Guard = self.saved['Guard']
            old_root = mv.ROOT
            mv.ROOT = self.tmp
            g = mv.Guard(self.tmp / 'job', protect=[target])
            target.write_text('changed by an agent')
            self.assertEqual(g.check(), ['kit.mjs'])
            self.assertEqual(target.read_text(), 'approved')
        finally:
            mv.ROOT = old_root
            mv.protected_files = saved


class Ledger(Temp):
    def test_start_choices(self):
        self.assertEqual(self.run_obj('now', 'zz-now').state, 'queued')
        later = self.run_obj('later', 'zz-later')
        self.assertEqual((later.state, later.d['waiting_for']), ('waiting', "Drew's go"))
        night = self.run_obj('tonight', 'zz-night')
        t = datetime.fromisoformat(night.d['not_before'])
        self.assertEqual((night.state, t.hour, t.minute), ('waiting', 23, 0))
        runs = mv.all_runs()
        self.assertEqual([r.name for r in mv.due(runs)], ['zz-now'])
        self.assertIn('zz-night', [r.name for r in mv.due(runs, t + timedelta(minutes=1))])
        self.assertTrue((night.dir / 'STATUS.md').exists())

    def test_order_started_and_crash_recovery(self):
        a, b = self.run_obj('now', 'zz-a'), self.run_obj('now', 'zz-b')
        a.set('running', worker_pid=999999)
        mv.recover(mv.all_runs())
        self.assertEqual([r.name for r in mv.due(mv.all_runs())], ['zz-a', 'zz-b'])

    def test_rejects_an_unapproved_or_changed_mp3(self):
        bad = self.tmp / 'comparison.json'
        spec = json.loads(WASP_MANIFEST.read_text())
        spec['status'] = 'waiting_audio_review'
        bad.write_text(json.dumps(spec))
        with self.assertRaises(SystemExit):
            mv.new_run(WASP, 'zz-bad', bad, 'now')


class Verdicts(Temp):
    def delivered(self):
        r = self.planned_run()
        mp4 = self.tmp / 'final.mp4'
        shutil.copyfile(ROOT / 'episodes' / WASP / 'full' / 'renders' / 'ensign-wasp-v3-final.mp4', mp4)
        r.d['deliveries'] = [{'version': 1, 'name': 'Deep Six - Test Wasp v1.mp4', 'source': str(mp4)}]
        r.set('waiting_drew', waiting_for={'kind': 'video', 'version': 1, 'mp4': str(mp4), 'ask': 'Watch it.'})
        return r

    def test_silence_is_not_approval(self):
        r = self.delivered()
        with self.assertRaises(SystemExit):
            mv.cmd_verdict(argparse.Namespace(run=r.name, decision='approve', says='  '))
        self.assertEqual(mv.find_run(r.name).state, 'waiting_drew')

    def test_approval_records_the_final_video_and_locks_the_run(self):
        r = self.delivered()
        log = self.tmp / 'd6-calls.txt'
        fake = self.tmp / 'd6'
        fake.write_text(f'#!/bin/sh\necho "$@" >> {log}\n')
        fake.chmod(0o755)
        mv.D6_TOOL = fake
        mv.cmd_verdict(argparse.Namespace(run=r.name, decision='approve', says='yes good i like it'))
        r = mv.find_run(r.name)
        self.assertEqual((r.state, r.d['locked']), ('approved', True))
        call = log.read_text().split()
        self.assertEqual(call[:2], ['complete-video', WASP])
        self.assertEqual(call[-1], '--final')
        line = json.loads(mv.VERDICTS.read_text().splitlines()[-1])
        self.assertEqual((line['by'], line['decision'], line['said']), ('Drew', 'approve', 'yes good i like it'))
        self.assertIn(r.dir / 'run.json', mv.protected_files())

    def test_notes_go_to_triage_and_only_affected_segments_are_redone(self):
        r = self.delivered()
        r.d['steps_done'] = [s for s, _ in mv.STEPS]
        r.d['segments_done'] = [s['name'] for s in r.d['segments']]
        r.save()
        mv.cmd_verdict(argparse.Namespace(run=r.name, decision='notes', says='the roach looks tiny at 31 seconds'))
        r = mv.find_run(r.name)
        self.assertEqual((r.state, r.d['pending_notes']['drew']), ('queued', 'the roach looks tiny at 31 seconds'))
        saved = mv.agent_job
        mv.agent_job = lambda *a, **k: ({'summary': 'one shot', 'actions': [{
            'kind': 'redo_segment', 'segment': 'zz-test-seg03', 'start': 30.5, 'end': 32.0, 'notes': 'Push in on the roach.',
            'problem_key': 'subject-too-small', 'problem_title': 'Small subjects too small to read', 'rule': 'Close-ups.',
            'question': '', 'options': []}]}, 'opus')
        try:
            mv.triage(r, **r.d.pop('pending_notes'))
        finally:
            mv.agent_job = saved
        self.assertEqual(r.d['steps_done'], ['prepare', 'plan', 'assets'])
        self.assertEqual(r.d['segments_done'], ['zz-test-seg01', 'zz-test-seg02', 'zz-test-seg04'])
        self.assertEqual(r.d['notes']['zz-test-seg03'], ['Push in on the roach.'])

    def test_unclear_note_becomes_a_multiple_choice_question(self):
        r = self.delivered()
        saved = mv.agent_job
        mv.agent_job = lambda *a, **k: ({'summary': '', 'actions': [{
            'kind': 'ask_drew', 'segment': '', 'start': 0, 'end': 0, 'notes': '', 'problem_key': '', 'problem_title': '', 'rule': '',
            'question': 'Which part felt slow?', 'options': ['The egg case', 'The sink']}]}, 'opus')
        try:
            with self.assertRaises(mv.WaitDrew) as caught:
                mv.triage(r, drew='it drags', item='video v1')
        finally:
            mv.agent_job = saved
        self.assertIn('A) The egg case', caught.exception.what['ask'])


class Animator(Temp):
    """The segment loop: runner checks, then the Reviewer; the same model retries with notes; the best try is kept."""

    def setUp(self):
        super().setUp()
        self.fake_root = self.tmp / 'root'
        (self.fake_root / 'scenes').mkdir(parents=True)
        self.saved_more = {k: getattr(mv, k) for k in ('ROOT', 'agent_job', 'runner_checks', 'render_frames', 'review')}
        self.saved_strips = vf.frame_strips
        vf.frame_strips = lambda frames, prefix: []
        mv.render_frames = lambda scene, times: ['frame.png']
        self.calls = []

    def tearDown(self):
        for k, v in self.saved_more.items():
            setattr(mv, k, v)
        vf.frame_strips = self.saved_strips
        super().tearDown()

    def script(self, outcomes):
        """outcomes: per try, (checks problems, reviewer pass)."""
        tries = iter(outcomes)
        state = {}

        def job(role, brief, job_dir, schema, images=(), allow=(), ladder=None, start_at=None, **k):
            n = len(self.calls) + 1
            self.calls.append({'start_at': start_at, 'brief': brief})
            (self.fake_root / allow[0]).write_text(f'// try {n}\n')
            state['now'] = next(tries)
            return {'status': 'done', 'summary': ''}, start_at or 'sol'

        mv.agent_job = job
        mv.runner_checks = lambda r, seg, seg_dir: (state['now'][0], None)
        mv.review = lambda *a, **k: {'pass': state['now'][1], 'notes': [] if state['now'][1] else [
            {'time': 2.0, 'shot': 'H2', 'problem': 'Roach too small.', 'fix': 'Push in.', 'problem_key': 'subject-too-small'}],
            'summary': ''}

    def test_retries_with_notes_on_the_same_model(self):
        r = self.planned_run()
        mv.ROOT = self.fake_root
        self.script([(['Picture goes still for 0.6 s.'], False), ([], False), ([], True)])
        mv.make_segment(r, r.d['segments'][0], [])
        self.assertEqual([c['start_at'] for c in self.calls], [None, 'sol', 'sol'])
        self.assertIn('Picture goes still', self.calls[1]['brief'])
        self.assertIn('Roach too small', self.calls[2]['brief'])
        self.assertEqual((r.d['attempts']['zz-test-seg01'], r.d['made_by']['zz-test-seg01']), (3, 'sol'))

    def test_parks_after_three_tries_and_keeps_the_best(self):
        r = self.planned_run()
        mv.ROOT = self.fake_root
        self.script([(['Does not load.'], False), ([], False), (['Still for 1 s.'], False)])
        with self.assertRaises(mv.Park) as caught:
            mv.make_segment(r, r.d['segments'][0], [])
        self.assertIn('Best try kept (try 2)', str(caught.exception))
        self.assertEqual((self.fake_root / 'scenes' / 'zz-test-seg01.mjs').read_text(), '// try 2\n')


class Learning(Temp):
    def test_problem_seen_twice_becomes_a_rule(self):
        mv.record_problem('pale-on-dark-misread', 'Pale shapes read as teeth', 'Outline pale eggs.', 'run-a seg02', 'eggs look like teeth')
        self.assertFalse(mv.LEARNED.exists())
        mv.record_problem('pale-on-dark-misread', 'Pale shapes read as teeth', '', 'run-a seg02', 'same place again')
        self.assertFalse(mv.LEARNED.exists())
        mv.record_problem('pale-on-dark-misread', 'Pale shapes read as teeth', '', 'run-b seg01', 'eggs look like teeth again')
        self.assertIn('Outline pale eggs.', mv.LEARNED.read_text())

    def test_pilot_gate_only_for_risky_segments(self):
        r = self.planned_run()
        r.d['made_by'] = {'zz-test-seg01': 'opus', 'zz-test-seg02': 'sol', 'zz-test-seg03': 'sol'}
        self.assertEqual(mv.pilot_reasons(r, 'zz-test-seg01'), [])
        self.assertEqual(mv.pilot_reasons(r, 'zz-test-seg02'), ['codex'])
        r.d['pilot']['approved'] = ['codex']
        self.assertEqual(mv.pilot_reasons(r, 'zz-test-seg03'), [])
        r.d['new_assets'] = ['American cockroach']
        r.d['made_by']['zz-test-seg01'] = 'opus'
        self.assertEqual(mv.pilot_reasons(r, mv.first_new_drawing_segment(r)), ['new_drawings'])


if __name__ == '__main__':
    unittest.main()
