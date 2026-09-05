"""Test cho tool/evidence/retain.py — dữ liệu tổng hợp, không cần máy, không
cần git (git thiếu ⇒ trường `null`, không đổ).

    python3 -m unittest discover -s tool/evidence -v
"""
import json
import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import retain  # noqa: E402


class RetainTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = self.tmp.name
        self.frames = os.path.join(self.root, 'frames')
        os.makedirs(self.frames)
        with open(os.path.join(self.frames, 'r-1-01-home.png'), 'wb') as f:
            f.write(b'\x89PNG fake')
        packs = os.path.join(self.root, 'assets', 'pack')
        os.makedirs(packs)
        with open(os.path.join(packs, 'lesson-index-g6.json'), 'w') as f:
            json.dump({'grade': 6, 'buildProvenance': {
                'packVersion': 'g6-test-abc', 'contentHash': 'h', 'experimental': False}}, f)
        with open(os.path.join(packs, 'lesson-index-g7.json'), 'w') as f:
            json.dump({'grade': 7}, f)  # không provenance
        self.packs = packs

    def tearDown(self):
        self.tmp.cleanup()

    def _manifest(self, steps):
        sp = os.path.join(self.root, 'steps.json')
        with open(sp, 'w') as f:
            json.dump(steps, f)
        argv = ['--round', 'r', '--frames', self.frames, '--steps', sp,
                '--packs', self.packs, '--no-device', '--root', self.root,
                '--out', os.path.join(self.root, 'M.json')]
        code = retain.main(argv)
        return code, json.load(open(os.path.join(self.root, 'M.json')))

    def test_pass_with_existing_frame_is_kept(self):
        code, m = self._manifest({'iterations': [{'iter': 1, 'steps': [
            {'step': '01', 'result': 'PASS', 'frames': ['r-1-01-home.png']}]}]})
        self.assertEqual(code, 0)
        s = m['iterations'][0]['steps'][0]
        self.assertEqual(s['result'], 'PASS')
        self.assertFalse(s['downgraded'])
        self.assertEqual(m['summary']['steps']['PASS'], 1)
        self.assertEqual(m['frames'][0]['file'], 'r-1-01-home.png')
        self.assertEqual(len(m['frames'][0]['sha256']), 64)

    def test_pass_without_frame_is_downgraded(self):
        code, m = self._manifest({'iterations': [{'iter': 1, 'steps': [
            {'step': '02', 'result': 'PASS', 'frames': ['missing.png']},
            {'step': '03', 'result': 'PASS'}]}]})
        self.assertEqual(code, 1, 'có bước bị hạ cấp ⇒ exit 1')
        steps = m['iterations'][0]['steps']
        for s in steps:
            self.assertTrue(s['downgraded'])
            self.assertTrue(s['result'].startswith('UNVERIFIED'))
        self.assertEqual(steps[0]['missingFrames'], ['missing.png'])
        self.assertEqual(m['summary']['downgraded'], 2)

    def test_fail_and_skip_are_not_downgraded(self):
        code, m = self._manifest({'iterations': [{'iter': 1, 'steps': [
            {'step': '04', 'result': 'FAIL', 'frames': ['r-1-01-home.png']},
            {'step': '05', 'result': 'SKIP'}]}]})
        self.assertEqual(code, 0)
        self.assertEqual(m['summary']['steps']['FAIL'], 1)
        self.assertEqual(m['summary']['steps']['SKIP'], 1)

    def test_pack_versions_and_missing_provenance(self):
        _, m = self._manifest({'iterations': []})
        by = {p['file']: p for p in m['packs']}
        self.assertEqual(by['lesson-index-g6.json']['packVersion'], 'g6-test-abc')
        self.assertTrue(by['lesson-index-g6.json']['provenance'])
        self.assertIsNone(by['lesson-index-g7.json']['packVersion'])
        self.assertFalse(by['lesson-index-g7.json']['provenance'])

    def test_no_device_is_recorded_as_skipped(self):
        _, m = self._manifest({'iterations': []})
        self.assertEqual(m['device'], {'skipped': True})

    def test_lock_screen_frame_name_warns(self):
        with open(os.path.join(self.frames, 'lockscreen-oops.png'), 'wb') as f:
            f.write(b'x')
        _, m = self._manifest({'iterations': []})
        self.assertTrue(any('lock' in w for w in m['warnings']))


if __name__ == '__main__':
    unittest.main()
