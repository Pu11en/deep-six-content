import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
from d6_lifecycle import final_video_receipt


class FinalVideoReceiptTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.mp4 = self.root / 'finished.mp4'
        self.mp4.write_bytes(b'Fixture MP4 bytes; media probing is mocked.')
        self.manifest = self.root / 'audio.json'
        main = self.source('main')
        main['supporting_references'] = [self.source('legacy-support')]
        self.episode = {'id': 'fixture-episode', 'text': 'Exact approved words.',
                        'hook': 'Exact approved words.', 'source': main,
                        'supporting_sources': [self.source('support')]}
        self.audio = {'approved_narration_id': self.episode['id'],
                      'script_sha256': hashlib.sha256(self.episode['text'].encode()).hexdigest(),
                      'audio_sha256': 'audio-fingerprint', 'request_sha256': 'request-fingerprint',
                      'duration_seconds': 78.6, 'path': str(self.root / 'approved.mp3'),
                      'legacy_approval': False}
        self.probe = {'streams': [{'codec_type': 'video'}, {'codec_type': 'audio'}],
                      'format': {'duration': '80.0'}}

    @staticmethod
    def source(name):
        return {'source_id': name, 'url': 'https://extension.example/' + name,
                'title': name, 'publisher': 'University extension', 'lesson': name + ' lesson',
                'page_digest': name + '-digest'}

    def receipt(self, final=True):
        result = subprocess.CompletedProcess([], 0, json.dumps(self.probe), '')
        with patch('d6_audio.verify_approved_audio', return_value=self.audio), patch('d6_lifecycle.subprocess.run', return_value=result):
            return final_video_receipt(self.root, self.episode, self.mp4, self.manifest, final)

    def test_final_declaration_is_required_before_any_media_check(self):
        with patch('d6_audio.verify_approved_audio') as verify, patch('d6_lifecycle.subprocess.run') as probe:
            with self.assertRaisesRegex(ValueError, '--final'):
                final_video_receipt(self.root, self.episode, self.mp4, self.manifest)
            verify.assert_not_called()
            probe.assert_not_called()

    def test_audio_from_another_episode_is_rejected(self):
        self.audio['approved_narration_id'] = 'another-episode'
        with self.assertRaisesRegex(ValueError, 'another episode'):
            self.receipt()

    def test_audio_for_a_different_same_id_script_is_rejected(self):
        self.audio['script_sha256'] = 'different-words'
        with self.assertRaisesRegex(ValueError, 'saved approved script'):
            self.receipt()

    def test_audio_only_file_is_not_a_finished_video(self):
        self.probe['streams'] = [{'codec_type': 'audio'}]
        with self.assertRaisesRegex(ValueError, 'no video stream'):
            self.receipt()

    def test_cover_art_is_not_a_video_stream(self):
        self.probe['streams'] = [{'codec_type': 'video', 'disposition': {'attached_pic': 1}},
                                 {'codec_type': 'audio'}]
        with self.assertRaisesRegex(ValueError, 'no video stream'):
            self.receipt()

    def test_silent_video_is_not_complete(self):
        self.probe['streams'] = [{'codec_type': 'video'}]
        with self.assertRaisesRegex(ValueError, 'no audio stream'):
            self.receipt()

    def test_short_preview_does_not_consume_sources(self):
        self.probe['format']['duration'] = '12.0'
        with self.assertRaisesRegex(ValueError, 'shorter than the approved narration'):
            self.receipt()

    def test_valid_final_receipt_binds_file_audio_words_and_all_sources(self):
        receipt = self.receipt()
        self.assertEqual(receipt['mp4_sha256'], hashlib.sha256(self.mp4.read_bytes()).hexdigest())
        self.assertEqual(receipt['audio']['audio_sha256'], self.audio['audio_sha256'])
        self.assertEqual(receipt['duration_seconds'], 80.0)
        self.assertTrue(receipt['declared_final'])
        self.assertEqual({source['source_id'] for source in receipt['sources']},
                         {'main', 'support', 'legacy-support'})
        self.assertEqual(receipt['hook_sha256'], hashlib.sha256('exact approved words.'.encode()).hexdigest())
        self.assertEqual(receipt['script_sha256'], hashlib.sha256('exact approved words.'.encode()).hexdigest())
        self.assertFalse((self.root / 'state.json').exists())


if __name__ == '__main__':
    unittest.main()
