#!/usr/bin/env python3
"""Round 5 · Lane D — tests for tool/corpus/legacy/regression.py (the surviving-defect corpus).

A regression probe is only worth having if it can still say PRESENT. These tests build synthetic
TSLs that reproduce each round-4 defect exactly and assert the probe catches it, then remove the
defect and assert the probe stops claiming it — including the CHANGED case, which exists so a
probe can never turn "the text is different now" into "the text is right now".

Run:  python3 -m unittest discover -s tool/tests -v
"""
import json
import os
import shutil
import sys
import tempfile
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import _lane_d_sandbox  # noqa: E402,F401  — MUST precede anything that reaches legacy/common.py

sys.path.insert(0, os.path.join(HERE, '..', 'corpus', 'legacy'))
import regression  # noqa: E402

PIPE = 'test-pipe'


def block(bid, page, role, text, printed=1, conf=0.9):
    return {'id': bid, 'page': page, 'page_printed': printed, 'order': 0,
            'role': {'value': role, 'coarse': role.upper(), 'confidence': conf, 'method': 'test'},
            'text': text, 'bbox': [0, 0, 1, 0.1]}


class ProbeTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp(prefix='lane-d-regr-')

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def write_tsl(self, book, lesson, blocks, withheld=(), pages=None):
        d = os.path.join(self.tmp, 'tcroot', 'poc-out', 'trusted-corpus', 'tc-v2', PIPE, 'lessons', book)
        os.makedirs(d, exist_ok=True)
        pages = pages if pages is not None else sorted({b['page'] for b in blocks})
        with open(os.path.join(d, f'bai-{int(lesson):02d}.tsl.json'), 'w', encoding='utf-8') as f:
            json.dump({'book': book, 'lesson': lesson, 'pipeline': PIPE, 'sourceability': 'PARTIAL',
                       'boundary': {'pages': pages, 'page_start': pages[0], 'page_end': pages[-1]},
                       'blocks': blocks, 'withheld': list(withheld), 'figures': []}, f, ensure_ascii=False)

    def verdict(self, defect_id):
        rows = {r['defect']: r for r in regression.check(self.tmp, PIPE)}
        return rows[defect_id]['verdict'], rows[defect_id]

    # ---------------------------------------------------------------- R1
    def test_R1_imprint_page_attached_and_served_is_PRESENT(self):
        self.write_tsl('04-sgk-toan-4-tap-hai', 73, [
            block('b:p117:x:000', 117, 'heading', 'Bài 73'),
            block('b:p121:x:001', 121, 'heading', 'Chịu trách nhiệm xuất bản:'),
            block('b:p121:x:002', 121, 'body', 'Cơ sở in: Công ty ABC'),
        ])
        v, r = self.verdict('R1-imprint-as-lesson-body')
        self.assertEqual(v, 'PRESENT')
        self.assertEqual(r['data']['imprintBlocks'], 2)

    def test_R1_is_FIXED_when_the_tail_page_is_no_longer_attached(self):
        self.write_tsl('04-sgk-toan-4-tap-hai', 73,
                       [block('b:p117:x:000', 117, 'heading', 'Bài 73')], pages=[117, 118])
        self.assertEqual(self.verdict('R1-imprint-as-lesson-body')[0], 'FIXED')

    def test_R1_is_FIXED_when_the_page_is_attached_but_serves_nothing(self):
        self.write_tsl('04-sgk-toan-4-tap-hai', 73,
                       [block('b:p117:x:000', 117, 'heading', 'Bài 73')], pages=[117, 121])
        self.assertEqual(self.verdict('R1-imprint-as-lesson-body')[0], 'FIXED')

    def test_R1_is_CHANGED_not_FIXED_when_the_page_still_serves_other_text(self):
        """Serving something else off the imprint page is not a fix — and the probe must not say it is."""
        self.write_tsl('04-sgk-toan-4-tap-hai', 73, [
            block('b:p117:x:000', 117, 'heading', 'Bài 73'),
            block('b:p121:x:001', 121, 'body', 'Một câu văn nào đó không phải trang bản quyền.'),
        ])
        self.assertEqual(self.verdict('R1-imprint-as-lesson-body')[0], 'CHANGED')

    # ---------------------------------------------------------------- R2
    def test_R2_dangling_operator_and_bare_denominator_are_PRESENT(self):
        self.write_tsl('05-sgk-toan-5-tap-mot', 6, [
            block('b:p022:x:002', 22, 'body', '10'),
            block('b:p022:x:016', 22, 'body', 'b) 10 +'),
            block('b:p022:x:020', 22, 'body', 'Tính rồi so sánh kết quả.'),
        ])
        v, r = self.verdict('R2-fraction-fragment-served')
        self.assertEqual(v, 'PRESENT')
        self.assertEqual(len(r['data']['hits']), 2)

    def test_R2_is_FIXED_when_the_fragments_are_withheld(self):
        self.write_tsl('05-sgk-toan-5-tap-mot', 6,
                       [block('b:p022:x:020', 22, 'body', 'Tính rồi so sánh kết quả.')],
                       withheld=[{'page': 22, 'reasons': ['math_guard']}])
        self.assertEqual(self.verdict('R2-fraction-fragment-served')[0], 'FIXED')

    def test_R2_does_not_fire_on_an_intact_fraction_expression(self):
        self.write_tsl('05-sgk-toan-5-tap-mot', 6,
                       [block('b:p022:x:016', 22, 'body', 'b) 3/10 + 5/21')])
        self.assertEqual(self.verdict('R2-fraction-fragment-served')[0], 'FIXED')

    # ---------------------------------------------------------------- R3
    def test_R3_tone_corrupted_title_is_PRESENT(self):
        self.write_tsl('05-sgk-toan-5-tap-mot', 6,
                       [block('b:p021:x:001', 21, 'heading', 'CỘNG, TRỪ HẠI PHẬN SỐ KHÁC MẪU SỐ', conf=0.88)])
        v, r = self.verdict('R3-tone-slip-in-lesson-title')
        self.assertEqual(v, 'PRESENT')
        self.assertEqual(r['data']['hits'][0]['conf'], 0.88)

    def test_R3_is_FIXED_when_the_title_is_served_as_printed(self):
        self.write_tsl('05-sgk-toan-5-tap-mot', 6,
                       [block('b:p021:x:001', 21, 'heading', 'CỘNG, TRỪ HAI PHÂN SỐ KHÁC MẪU SỐ')])
        self.assertEqual(self.verdict('R3-tone-slip-in-lesson-title')[0], 'FIXED')

    def test_R3_is_CHANGED_when_the_heading_is_some_third_string(self):
        self.write_tsl('05-sgk-toan-5-tap-mot', 6,
                       [block('b:p021:x:001', 21, 'heading', 'CỘNG TRỪ PHÂN SỐ')])
        self.assertEqual(self.verdict('R3-tone-slip-in-lesson-title')[0], 'CHANGED',
                         'a different wrong string is not a fix')

    # ---------------------------------------------------------------- R7c
    def test_R7c_is_FIXED_when_verse_is_withheld_by_line_structure(self):
        self.write_tsl('05-sgk-tieng-viet-5-tap-mot', 25,
                       [block('b:p123:x:001', 123, 'heading', 'Bài 25')],
                       withheld=[{'page': 123, 'reasons': ['line_structure']}])
        v, r = self.verdict('R7c-verse-flattened-to-prose')
        self.assertEqual(v, 'FIXED')
        self.assertEqual(r['data']['withheldVerseRegions'], 1)

    def test_R7c_is_CHANGED_when_long_single_run_bodies_are_served_with_no_verse_withhold(self):
        self.write_tsl('05-sgk-tieng-viet-5-tap-mot', 25,
                       [block('b:p123:x:001', 123, 'body', 'x' * 200)])
        self.assertEqual(self.verdict('R7c-verse-flattened-to-prose')[0], 'CHANGED')

    # ---------------------------------------------------------------- absent
    def test_a_lesson_not_in_the_batch_is_ABSENT_not_FIXED(self):
        """The most dangerous failure mode of a regression corpus: an empty run reading as a clean one."""
        for r in regression.check(self.tmp, PIPE):
            self.assertEqual(r['verdict'], 'ABSENT')


class TailScanTests(unittest.TestCase):
    """The R1 CLASS on any book, not the R1 row on one book."""

    def setUp(self):
        self.tmp = tempfile.mkdtemp(prefix='lane-d-tail-')
        self.args = type('A', (), dict(batch_dir=self.tmp, pipeline=PIPE, out=''))()

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def _batch(self, book, lesson, blocks, pages):
        with open(os.path.join(self.tmp, 'batch-spec.json'), 'w', encoding='utf-8') as f:
            json.dump({'batch': 't', 'lessons': [{'book': book, 'lesson': lesson, 'risk': ['last_lesson_of_book']}]}, f)
        d = os.path.join(self.tmp, 'tcroot', 'poc-out', 'trusted-corpus', 'tc-v2', PIPE, 'lessons', book)
        os.makedirs(d, exist_ok=True)
        with open(os.path.join(d, f'bai-{lesson:02d}.tsl.json'), 'w', encoding='utf-8') as f:
            json.dump({'book': book, 'lesson': lesson, 'boundary': {'pages': pages},
                       'blocks': blocks, 'withheld': [], 'figures': []}, f, ensure_ascii=False)

    def test_an_unnumbered_attached_page_serving_imprint_text_is_the_defect(self):
        b = [block('x:p128:x:000', 128, 'body', 'Tính giá trị của biểu thức.', printed=127),
             dict(block('x:p133:x:000', 133, 'heading', 'Chịu trách nhiệm xuất bản:'), page_printed=None)]
        self._batch('04-sgk-toan-4-tap-mot', 37, b, [128, 133])
        regression.cmd_tail_scan(self.args)
        # re-run with an out file so the counts can be asserted
        self.args.out = os.path.join(self.tmp, 'scan.json')
        regression.cmd_tail_scan(self.args)
        d = json.load(open(self.args.out, encoding='utf-8'))
        self.assertEqual(d['lessonsWithTailDefect'], 1)
        self.assertEqual(d['rows'][0]['attachedPagesWithoutPrintedNumber'], [133])
        self.assertEqual(d['rows'][0]['attachedPagesServingImprintText'], [133])

    def test_a_numbered_lesson_page_is_not_a_tail_defect(self):
        b = [block('x:p128:x:000', 128, 'body', 'Tính giá trị của biểu thức.', printed=127)]
        self._batch('04-sgk-toan-4-tap-mot', 37, b, [128])
        self.args.out = os.path.join(self.tmp, 'scan.json')
        regression.cmd_tail_scan(self.args)
        d = json.load(open(self.args.out, encoding='utf-8'))
        self.assertEqual(d['lessonsWithTailDefect'], 0)
        self.assertEqual(d['rows'][0]['attachedPagesWithoutPrintedNumber'], [])


if __name__ == '__main__':
    unittest.main()
