import hashlib
import json
from pathlib import Path
import sys
import subprocess
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
from d6_audio import (generate, reserve_voice, AudioError, authorize, episode_lock,
                      review_audio, verify_approved_audio, probe)


class AudioTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.path = self.root / 'comparison.json'
        self.spec = {'approved_narration_id': 'fixture-episode', 'kind': 'audition',
                     'approved_script_file': 'approved.txt',
                     'voice_id': 'fixture', 'model_id': 'fixture', 'seed': 1,
                     'voice_settings': {}, 'output_format': 'mp3_44100_128', 'variants': []}
        for name in ('original', 'refined'):
            (self.root / (name + '.txt')).write_text('Fixture script ' + name)
            self.spec['variants'].append({'name': name, 'text_file': name+'.txt',
                                         'audio_file': name+'.mp3', 'status': 'prepared'})
        (self.root / 'approved.txt').write_text('Fixture script original Fixture script refined Same hook')
        self.save()

    def save(self, authorize_job=True):
        self.path.write_text(json.dumps(self.spec))
        if authorize_job:
            authorize(self.path, 'Fixture user explicitly requests these outputs.', 3, 1000)

    def test_insufficient_balance_makes_no_generation_request(self):
        with patch('d6_audio.remaining', return_value=1), patch('d6_audio.request') as request:
            with self.assertRaises(AudioError):
                generate(self.path)
            request.assert_not_called()

    def test_completed_comparison_is_not_billed_again(self):
        with patch('d6_audio.remaining', return_value=1000), patch('d6_audio.request', return_value=(b'fixture audio', 'fixture-request')) as request, patch('d6_audio.probe', return_value={'duration_seconds': 10}):
            generate(self.path)
            generate(self.path)
            self.assertEqual(request.call_count, 2)

    def test_interrupted_request_cannot_be_silently_retried(self):
        with patch('d6_audio.remaining', return_value=1000), patch('d6_audio.request', side_effect=AudioError('interrupted')) as request:
            with self.assertRaises(AudioError):
                generate(self.path)
            with self.assertRaises(AudioError):
                generate(self.path)
            self.assertEqual(request.call_count, 1)

    def test_existing_audio_is_never_overwritten(self):
        (self.root/'original.mp3').write_bytes(b'keep')
        with patch('d6_audio.request') as request:
            with self.assertRaises(AudioError):
                generate(self.path)
            request.assert_not_called()
        self.assertEqual((self.root/'original.mp3').read_bytes(), b'keep')

    def test_three_voice_samples_use_three_distinct_voices_once(self):
        (self.root/'third.txt').write_text('Same hook')
        self.spec['variants'].append({'name':'third','text_file':'third.txt','audio_file':'third.mp3','status':'prepared'})
        for n, variant in enumerate(self.spec['variants']):
            variant['voice_id'] = 'voice' + str(n)
        self.save()
        with patch('d6_audio.remaining', return_value=1000), patch('d6_audio.request', return_value=(b'fixture audio','request')) as request, patch('d6_audio.probe', return_value={'duration_seconds':10}):
            generate(self.path)
            generate(self.path)
            self.assertEqual(request.call_count,3)
            self.assertEqual([c.args[0].split('/text-to-speech/')[1].split('?')[0] for c in request.call_args_list], ['voice0','voice1','voice2'])

    def test_more_than_three_requests_are_blocked(self):
        self.spec['variants'] *= 2
        self.save(authorize_job=False)
        with patch('d6_audio.request') as request:
            with self.assertRaises(AudioError):
                generate(self.path)
            request.assert_not_called()

    def test_voice_rotation_cycles_once_per_narration_and_survives_restart(self):
        rotation = self.root/'rotation.json'
        rotation.write_text(json.dumps({'voices':[{'name':n,'voice_id':n} for n in ('Tyler','Chris','Liam')], 'next_index':0,'assignments':{}}))
        self.assertEqual(reserve_voice(rotation,'one')['name'],'Tyler')
        self.assertEqual(reserve_voice(rotation,'one')['name'],'Tyler')
        self.assertEqual(reserve_voice(rotation,'two')['name'],'Chris')
        self.assertEqual(reserve_voice(rotation,'three')['name'],'Liam')
        self.assertEqual(reserve_voice(rotation,'four')['name'],'Tyler')

    def test_single_full_narration_uses_rotation_without_extra_generation(self):
        rotation=self.root/'rotation.json'
        rotation.write_text(json.dumps({'voices':[{'name':'Tyler','voice_id':'tyler'}], 'next_index':0,'assignments':{}}))
        self.spec['variants']=self.spec['variants'][:1]
        self.spec.update(voice_rotation_file='rotation.json',approved_narration_id='one',kind='full_narration')
        (self.root/'approved.txt').write_text('Fixture script original')
        self.save()
        with patch('d6_audio.remaining',return_value=1000), patch('d6_audio.request',return_value=(b'fixture audio','request')) as request, patch('d6_audio.probe',return_value={'duration_seconds':10}):
            generate(self.path)
            generate(self.path)
            self.assertEqual(request.call_count,1)
            self.assertIn('/text-to-speech/tyler?',request.call_args.args[0])

    def full_script(self):
        self.spec['variants'] = self.spec['variants'][:1]
        self.spec['kind'] = 'full_narration'
        (self.root / 'approved.txt').write_text('Fixture script original')
        self.save()

    def render(self):
        with patch('d6_audio.remaining', return_value=1000), patch('d6_audio.request', return_value=(b'fixture audio', 'request')), patch('d6_audio.probe', return_value={'duration_seconds': 10}):
            return generate(self.path)

    def test_missing_authorization_blocks_before_any_provider_call(self):
        self.save(authorize_job=False)
        with patch('d6_audio.remaining') as balance, patch('d6_audio.request') as request:
            with self.assertRaisesRegex(AudioError, 'authorization'):
                generate(self.path)
            balance.assert_not_called()
            request.assert_not_called()

    def test_edited_payload_needs_new_exact_authorization(self):
        spec = json.loads(self.path.read_text())
        spec['voice_settings']['stability'] = 0.2
        self.path.write_text(json.dumps(spec))
        with patch('d6_audio.request') as request:
            with self.assertRaisesRegex(AudioError, 'authorization'):
                generate(self.path)
            request.assert_not_called()

    def test_full_script_drift_is_blocked_but_delivery_tags_allowed(self):
        self.full_script()
        (self.root / 'original.txt').write_text('[curious] Fixture script original')
        authorize(self.path, 'Fixture authorizes this delivery test.', 1, 1000)
        self.render()
        (self.root / 'original.txt').write_text('[curious] Different claim')
        with patch('d6_audio.request') as request:
            with self.assertRaisesRegex(AudioError, 'canonical approved script'):
                generate(self.path)
            request.assert_not_called()

    def test_duplicate_output_paths_are_blocked_before_any_request(self):
        self.spec['variants'][1]['audio_file'] = 'original.mp3'
        self.save(authorize_job=False)
        with patch('d6_audio.request') as request:
            with self.assertRaisesRegex(AudioError, 'unique'):
                generate(self.path)
            request.assert_not_called()

    def test_direct_generate_respects_episode_lock(self):
        with episode_lock(self.path), patch('d6_audio.request') as request:
            with self.assertRaisesRegex(AudioError, 'Another audio operation'):
                generate(self.path)
            request.assert_not_called()

    def test_second_manifest_cannot_repeat_paid_request(self):
        self.full_script()
        self.render()
        second = self.root / 'other.json'
        spec = dict(self.spec)
        spec['variants'] = [dict(self.spec['variants'][0], audio_file='other.mp3')]
        second.write_text(json.dumps(spec))
        authorize(second, 'Fixture requests another file.', 1, 1000)
        with patch('d6_audio.request') as request:
            with self.assertRaisesRegex(AudioError, 'already has a receipt'):
                generate(second)
            request.assert_not_called()

    def test_completed_settings_cannot_be_silently_relabelled(self):
        self.render()
        for key, value in [('model_id', 'changed'), ('voice_id', 'changed'), ('seed', 99), ('voice_settings', {'stability': 0.8})]:
            with self.subTest(field=key):
                spec = json.loads(self.path.read_text())
                old = spec[key]
                spec[key] = value
                self.path.write_text(json.dumps(spec))
                with patch('d6_audio.request') as request:
                    with self.assertRaisesRegex(AudioError, 'request settings changed'):
                        generate(self.path)
                    request.assert_not_called()
                spec[key] = old
                self.path.write_text(json.dumps(spec))

    def test_full_audio_review_binds_exact_hashes_and_rejects_stale_review(self):
        self.full_script()
        spec = self.render()
        with patch('d6_audio.probe', return_value={'duration_seconds': 10}):
            review_audio(self.path, 'approve', spec['review_id'], 'original', 'User explicitly likes the full recording.')
            verified = verify_approved_audio(self.path)
            self.assertEqual(verified['audio_sha256'], hashlib.sha256(b'fixture audio').hexdigest())
            self.assertFalse(verified['legacy_approval'])
            with self.assertRaisesRegex(AudioError, 'stale'):
                review_audio(self.path, 'approve', spec['review_id'], 'original', 'Duplicate answer')
            (self.root / 'original.mp3').write_bytes(b'changed')
            with self.assertRaisesRegex(AudioError, 'missing or changed'):
                verify_approved_audio(self.path)

    def test_audition_preference_is_not_full_audio_approval(self):
        spec = self.render()
        with patch('d6_audio.probe', return_value={'duration_seconds': 10}):
            with self.assertRaisesRegex(AudioError, 'audition'):
                review_audio(self.path, 'approve', spec['review_id'], 'original', 'Nice voice')

    def test_rejected_full_audio_is_not_approved(self):
        self.full_script()
        spec = self.render()
        with patch('d6_audio.probe', return_value={'duration_seconds': 10}):
            review_audio(self.path, 'reject', spec['review_id'], 'original', 'Pronunciation is wrong.')
            with self.assertRaisesRegex(AudioError, 'explicit audio approval'):
                verify_approved_audio(self.path)

    def test_changed_approval_fingerprint_invalidates_review(self):
        self.full_script()
        spec = self.render()
        with patch('d6_audio.probe', return_value={'duration_seconds': 10}):
            review_audio(self.path, 'approve', spec['review_id'], 'original', 'Approved full recording.')
            spec = json.loads(self.path.read_text())
            spec['audio_review']['request_sha256'] = 'old'
            self.path.write_text(json.dumps(spec))
            with self.assertRaisesRegex(AudioError, 'approval no longer matches'):
                verify_approved_audio(self.path)

    def test_missing_probe_is_detected_before_billing(self):
        with patch('d6_audio.shutil.which', return_value=None), patch('d6_audio.request') as request:
            with self.assertRaisesRegex(AudioError, 'ffprobe is unavailable'):
                generate(self.path)
            request.assert_not_called()

    def test_received_audio_is_not_billed_again_after_failed_probe(self):
        self.full_script()
        with patch('d6_audio.remaining', return_value=1000), patch('d6_audio.request', return_value=(b'fixture audio', 'request')) as request, patch('d6_audio.probe', side_effect=AudioError('probe failed')):
            with self.assertRaisesRegex(AudioError, 'probe failed'):
                generate(self.path)
            self.assertEqual(json.loads(self.path.read_text())['variants'][0]['status'], 'received')
            with self.assertRaisesRegex(AudioError, 'may have been billed'):
                generate(self.path)
            self.assertEqual(request.call_count, 1)
            self.assertEqual((self.root / 'original.mp3').read_bytes(), b'fixture audio')

    def test_interrupted_final_review_save_recovers_without_generation(self):
        spec = self.render()
        spec.pop('review_id')
        spec['status'] = 'prepared'
        self.path.write_text(json.dumps(spec))
        with patch('d6_audio.request') as request:
            recovered = generate(self.path)
            self.assertEqual(recovered['status'], 'waiting_audio_review')
            self.assertTrue(recovered['review_id'].startswith('AUD-'))
            request.assert_not_called()

    def test_legacy_full_approval_verifies_without_rewriting_manifest(self):
        self.full_script()
        spec = self.render()
        spec.pop('kind')
        spec['variants'][0].pop('request_sha256')
        spec['status'] = 'audio_approved'
        spec['audio_review'] = {'status': 'approved', 'approved_variant': 'original', 'feedback': 'Historical approval'}
        self.path.write_text(json.dumps(spec))
        before = self.path.read_bytes()
        with patch('d6_audio.probe', return_value={'duration_seconds': 10}):
            checked = verify_approved_audio(self.path)
        self.assertTrue(checked['legacy_approval'])
        self.assertEqual(self.path.read_bytes(), before)

    def test_canonical_file_must_match_saved_human_approval_when_state_exists(self):
        self.full_script()
        folder = self.root / '01-content' / 'audio'
        folder.mkdir(parents=True)
        state = self.root / '01-content' / 'harness' / 'runtime' / 'state.json'
        state.parent.mkdir(parents=True)
        state.write_text(json.dumps({'approved': [{'id': 'fixture-episode', 'text': 'Human chose other words.'}]}))
        spec = dict(self.spec, approved_script_file=str(self.root / 'approved.txt'))
        spec['variants'] = [dict(self.spec['variants'][0], text_file=str(self.root / 'original.txt'))]
        manifest = folder / 'new.json'
        manifest.write_text(json.dumps(spec))
        with patch('d6_audio.request') as request:
            with self.assertRaisesRegex(AudioError, 'saved human-approved narration'):
                authorize(manifest, 'Explicit user instruction', 1, 1000)
            request.assert_not_called()

    def test_probe_rejects_nonfinite_duration(self):
        result = subprocess.CompletedProcess([], 0, json.dumps({'streams': [{'codec_name': 'mp3'}],
                                                               'format': {'duration': 'NaN'}}), '')
        with patch('d6_audio.subprocess.run', return_value=result):
            with self.assertRaises(AudioError):
                probe(self.root / 'fixture.mp3')
