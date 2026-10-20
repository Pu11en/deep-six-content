"""Offline crawler checkpoints, publication lifecycle and safe return paths."""
import copy
import hashlib
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
from d6_harness import Harness, FlowError
from d6_lifecycle import reservations
from d6_sources import validate_cards
from test_d6_harness import FakeWriter, card, fetch


class RecoveryTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        folder = self.root / '01-content/harness'
        folder.mkdir(parents=True)
        config = {'active_provider': 'codex', 'research_backend': 'subscription',
                  'trusted_domains': ['citybugs.tamu.edu'], 'writing_enabled': True,
                  'board_updates_enabled': False, 'pest_rotation': ['ants', 'cockroaches'],
                  'sources_per_pest': 3}
        (folder / 'config.json').write_text(json.dumps(config))
        (self.root / '01-content/writing-harness-prompts.md').write_text('Fixture instructions.')
        (self.root / '01-content/narration-style.md').write_text('Fixture narration style.')
        self.writer = FakeWriter()
        self.flow = Harness(self.root, self.writer, fetch)

    def crawler(self):
        self.flow.config['research_backend'] = 'crawler'
        (self.flow.folder / 'config.json').write_text(json.dumps(self.flow.config))

    def seed_queue(self):
        self.flow.start()
        self.flow.save_sources(self.flow.state['current']['review_id'], [1, 2, 4], first=2)

    def envelope(self, cards, unresolved=None):
        expected = self.flow.state['current']['research_request']
        folder = self.root / '01-content/research/fixture'
        folder.mkdir(parents=True, exist_ok=True)
        evidence = folder / 'evidence.json'
        evidence.write_text(json.dumps({'job_id': 'fixture-job', 'evidence': 'Fixture crawler material'}))
        data = {k: expected[k] for k in ('run_id', 'request_id', 'stage', 'client_id')}
        data.update(crawler_job_id='fixture-job', evidence_file=str(evidence.relative_to(self.root)), result={'cards': cards})
        if expected['stage'] == 'support':
            data['result']['unresolved'] = unresolved or []
        path = folder / 'result.json'
        path.write_text(json.dumps(data))
        return path

    def import_sources(self):
        path = self.envelope([card(n) for n in range(30, 35)])
        self.flow.import_research(path)
        return path

    def choose_source_hook(self):
        self.flow.choose(self.flow.state['current']['review_id'], 1)
        self.flow.choose(self.flow.state['current']['review_id'], 2)

    def approved(self):
        self.flow.start()
        self.choose_source_hook()
        self.flow.choose(self.flow.state['current']['review_id'], 1)
        return self.flow.state['approved'][-1]

    def test_fresh_request_leaves_saved_queue_and_priority_untouched(self):
        self.seed_queue()
        before = copy.deepcopy(self.flow.state['source_queue'])
        first = self.flow.state['next_source_id']
        self.crawler()
        calls = list(self.writer.calls)
        self.flow.start(fresh=True)
        self.assertEqual(self.flow.state['current']['pest'], 'cockroaches')
        self.assertEqual(self.flow.state['current']['status'], 'waiting_research')
        self.assertEqual(self.flow.state['source_queue'], before)
        self.assertEqual(self.flow.state['next_source_id'], first)
        self.assertEqual(self.writer.calls, calls)
        self.assertTrue((self.root / self.flow.state['current']['research_request']['file']).is_file())

    def test_crawler_source_hook_support_narration_flow_and_provenance(self):
        self.seed_queue()
        queued = copy.deepcopy(self.flow.state['source_queue'])
        first = self.flow.state['next_source_id']
        self.crawler()
        self.flow.start(fresh=True)
        self.import_sources()
        self.choose_source_hook()
        self.assertEqual(self.flow.state['current']['status'], 'waiting_research')
        self.assertEqual(self.flow.state['current']['research_request']['stage'], 'support')
        hook = self.flow.state['current']['selected_hook']['text']
        self.flow.import_research(self.envelope([card(910)]))
        current = self.flow.state['current']
        self.assertEqual(current['status'], 'waiting_narrations')
        self.assertTrue(all(s['text'].split('\n\n')[0] == hook for s in current['scripts']))
        self.flow.choose(current['review_id'], 1)
        self.assertEqual(len(self.flow.state['approved'][0]['crawler_research']), 2)
        self.assertEqual(self.writer.calls.count('research'), 1)  # Queue seeding only.
        self.assertNotIn('support_research', self.writer.calls)
        self.assertEqual(self.flow.state['source_queue'][:3], queued)
        self.assertEqual(self.flow.state['next_source_id'], first)
        self.assertEqual(self.flow.state['source_queue'][-1]['status'], 'awaiting_video')

    def test_stale_import_cannot_mutate_pending_request(self):
        self.crawler()
        self.flow.start(fresh=True)
        path = self.envelope([card(n) for n in range(30, 35)])
        data = json.loads(path.read_text()); data['request_id'] = 'another-request'
        path.write_text(json.dumps(data))
        before = copy.deepcopy(self.flow.state)
        with self.assertRaisesRegex(FlowError, 'another request'):
            self.flow.import_research(path)
        self.assertEqual(self.flow.state, before)
        self.assertEqual(self.writer.calls, [])

    def test_source_import_survives_export_failure_without_stale_request(self):
        self.crawler()
        self.flow.start(fresh=True)
        path = self.envelope([card(n) for n in range(30, 35)])
        with patch.object(self.flow, 'sync_outputs', side_effect=OSError('Fixture interrupted export')):
            with self.assertRaises(OSError):
                self.flow.import_research(path)
        self.flow = Harness(self.root, self.writer, fetch)
        self.assertEqual(self.flow.state['current']['status'], 'waiting_sources')
        self.assertNotIn('research_request', self.flow.state['current'])
        self.assertEqual(len(self.flow.state['current']['crawler_research']), 1)
        self.choose_source_hook()
        self.assertEqual(self.flow.state['current']['research_request']['stage'], 'support')

    def test_support_import_crash_resumes_writer_without_research(self):
        self.crawler(); self.flow.start(fresh=True); self.import_sources(); self.choose_source_hook()
        path = self.envelope([card(920)])
        with patch.object(self.flow, 'advance', side_effect=KeyboardInterrupt):
            with self.assertRaises(KeyboardInterrupt):
                self.flow.import_research(path)
        self.flow = Harness(self.root, self.writer, fetch)
        self.assertEqual(self.flow.state['current']['status'], 'generating')
        self.assertNotIn('research_request', self.flow.state['current'])
        self.flow.retry()
        self.assertEqual(self.flow.state['current']['status'], 'waiting_narrations')
        self.assertNotIn('support_research', self.writer.calls)

    def test_missing_evidence_stops_import_and_preserves_pending_request(self):
        self.crawler(); self.flow.start(fresh=True)
        path = self.envelope([card(n) for n in range(30, 35)])
        data = json.loads(path.read_text()); data['evidence_file'] = '../outside-project.json'
        path.write_text(json.dumps(data))
        with self.assertRaisesRegex(FlowError, 'research folder'):
            self.flow.import_research(path)
        self.assertEqual(self.flow.state['current']['status'], 'waiting_research')

    def test_support_publication_is_reserved_across_episodes(self):
        approved = self.approved()
        support = approved['supporting_sources'][0]
        checked, failures = validate_cards([card(int(support['url'].rsplit('-', 1)[1]))],
                                           ['citybugs.tamu.edu'], reservations(self.flow.state), '', fetch)
        self.assertEqual(checked, [])
        self.assertEqual(len(failures), 1)

    def test_legacy_status_migration_preserves_queue_and_history(self):
        self.seed_queue()
        queued = copy.deepcopy(self.flow.state['source_queue'])
        approved = self.approved()
        self.flow.state['source_queue'][-1]['status'] = 'used'
        self.flow.save()
        history = copy.deepcopy(self.flow.state['approved'])
        self.assertEqual(self.flow.migrate_lifecycle(), 1)
        self.assertEqual(self.flow.state['source_queue'][:3], queued)
        self.assertEqual(self.flow.state['approved'], history)
        self.assertEqual(self.flow.state['source_queue'][-1]['status'], 'awaiting_video')
        self.assertEqual(self.flow.migrate_lifecycle(), 0)

    def test_final_receipt_consumes_once_and_blocks_a_different_completion(self):
        approved = self.approved()
        receipt = {'episode_id': approved['id'], 'mp4_sha256': 'fixture-final', 'audio': {'audio_sha256': 'fixture-audio'}}
        with patch('d6_harness.final_video_receipt', return_value=receipt):
            self.flow.complete_video(approved['id'], 'final.mp4', 'audio.json', final=True)
            self.flow.complete_video(approved['id'], 'final.mp4', 'audio.json', final=True)
        self.assertEqual(len(self.flow.state['completed_videos']), 1)
        self.assertEqual(self.flow.state['source_queue'][0]['status'], 'used')
        with patch('d6_harness.final_video_receipt', return_value=dict(receipt, mp4_sha256='changed')):
            with self.assertRaisesRegex(FlowError, 'different final'):
                self.flow.complete_video(approved['id'], 'changed.mp4', 'audio.json', final=True)

    def test_return_to_hooks_invalidates_script_review_but_preserves_source(self):
        self.flow.start(); self.choose_source_hook()
        current = self.flow.state['current']; old = current['review_id']; source = copy.deepcopy(current['cards'])
        self.flow.revise('hooks', 'The promise needs a different angle.')
        self.assertEqual(current['status'], 'waiting_hooks')
        self.assertEqual(current['cards'], source)
        self.assertNotIn('scripts', current)
        self.assertNotIn('selected_hook', current)
        with self.assertRaises(FlowError):
            self.flow.choose(old, 1)

    def test_stale_changed_source_stops_before_writing(self):
        self.seed_queue()
        saved = self.flow.state['source_queue'][0]
        saved['source']['checked_at'] = '2000-01-01T00:00:00+00:00'
        self.flow.fetcher = lambda url, domains: ('A different page with no original evidence', url)
        with self.assertRaisesRegex(FlowError, 'source changed'):
            self.flow.start(source=saved['id'])
        self.assertNotIn('hooks', self.writer.calls)
        self.assertEqual(self.flow.state['current']['status'], 'error')

    def test_crawler_mode_never_falls_back_for_hook_library(self):
        self.crawler()
        with self.assertRaisesRegex(FlowError, 'separate crawler procedure'):
            self.flow.refresh_library()
        self.assertEqual(self.writer.calls, [])

    def test_prior_script_body_cannot_be_reused_under_a_new_hook(self):
        approved = self.approved()
        self.flow.start()
        self.flow.choose(self.flow.state['current']['review_id'], 1)
        original_call = self.writer.call
        def writer(role, prompt, schema, research=False):
            result, meta = original_call(role, prompt, schema, research)
            if role == 'narrations':
                hook = self.flow.state['current']['selected_hook']['text']
                result['scripts'][0]['text'] = hook + '\n\n' + approved['text'].split('\n\n', 1)[1]
            return result, meta
        with patch.object(self.writer, 'call', side_effect=writer):
            with self.assertRaisesRegex(FlowError, 'duplicates or incomplete'):
                self.flow.choose(self.flow.state['current']['review_id'], 1)
        self.assertEqual(len(self.flow.state['approved']), 1)


if __name__ == '__main__':
    unittest.main()
