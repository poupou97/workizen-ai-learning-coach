#!/usr/bin/env python3
"""Round 4 · Lane A-pipeline — tests for the Role Layer additions of tool/corpus/tc2_sdm.py
(failure class 3: role classification; docs/research/PIPELINE-ROUND4-FAILURE-CLASS-FIXES.md §3).

Synthetic blocks only (no SGK text, Founder D4).

Run:  python3 -m unittest discover -s tool/tests -v"""
import os
import sys
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', 'corpus'))
import tc2_sdm  # noqa: E402


def blk(order, role, text, bbox, colour=0.6):
    return dict(order=order, text=text, bbox=bbox, colour=dict(share=colour), role=dict(value=role, coarse=tc2_sdm.COARSE[role], method='x', confidence=0.7, evidence=[]))


class QuestionBoxTests(unittest.TestCase):
    def test_numbered_line_under_a_question_in_the_same_tinted_box_is_a_question(self):
        # Bài 17 p61 shape: «1. …?» (question) then «2. Lấy một số ví dụ …» labelled sidebar by the narrow-right-box rule
        q = blk(0, 'question', '1. Câu hỏi mẫu thứ nhất?', [0.62, 0.78, 0.28, 0.07])
        s = blk(1, 'sidebar', '2. Lấy một số ví dụ mẫu về quá trình.', [0.62, 0.86, 0.28, 0.06])
        n = tc2_sdm.question_box_pass([q, s], med_h=0.015)
        self.assertEqual(n, 1)
        self.assertEqual((s['role']['value'], s['role']['coarse'], s['role']['method']), ('question', 'QUESTION', 'context'))

    def test_not_applied_without_the_box_or_the_number_or_the_question(self):
        q = blk(0, 'question', '1. Câu hỏi mẫu?', [0.62, 0.78, 0.28, 0.07])
        far = blk(1, 'sidebar', '2. Dòng ở xa.', [0.62, 0.95, 0.28, 0.02])            # more than two line heights below
        white = blk(1, 'sidebar', '2. Dòng không màu.', [0.62, 0.86, 0.28, 0.06], colour=0.0)
        other_x = blk(1, 'sidebar', '2. Dòng cột khác.', [0.12, 0.86, 0.28, 0.06])   # different left edge
        plain = blk(1, 'sidebar', 'Không đánh số.', [0.62, 0.86, 0.28, 0.06])
        body_prev = blk(0, 'body', 'Đoạn văn.', [0.62, 0.78, 0.28, 0.07])
        for prev, cur in ((q, far), (q, white), (q, other_x), (q, plain), (body_prev, blk(1, 'sidebar', '2. Sau đoạn văn.', [0.62, 0.86, 0.28, 0.06]))):
            before = cur['role']['value']
            self.assertEqual(tc2_sdm.question_box_pass([prev, cur], med_h=0.015), 0)
            self.assertEqual(cur['role']['value'], before)


class RoleSignalFlagTests(unittest.TestCase):
    def test_flag_is_off_by_default_and_recorded_on_the_page(self):
        self.assertIsNone(tc2_sdm.ROLE_SIGNAL if not os.environ.get('TC2_ROLE_SIGNAL') else None)
        import inspect
        src = inspect.getsource(tc2_sdm.build_page)
        self.assertIn('role_signal=role_signal or None', src)     # every SDM page records which rules (if any) were applied

    def test_signal_pass_is_a_no_op_without_a_pdf(self):
        blocks = [blk(0, 'body', 'Một dòng mẫu.', [0.1, 0.1, 0.5, 0.02])]
        self.assertEqual(tc2_sdm.role_signal_pass('00-sgk-khong-ton-tai', 1, blocks, 'v3'), 0)
        self.assertEqual(blocks[0]['role']['value'], 'body')


if __name__ == '__main__':
    unittest.main()
