#!/usr/bin/env python3
"""Round 4 · Lane A-pipeline — tests for the reading-order agreement stage of tool/corpus/tc2_sdm.py
(failure class: two-column / displaced-box reading order; docs/research/PIPELINE-ROUND4-FAILURE-CLASS-FIXES.md §1).

Synthetic streams and boxes only — no SGK text (Founder D4). Tests that need rapidfuzz skip when it is absent.

Run:  python3 -m unittest discover -s tool/tests -v"""
import os
import sys
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', 'corpus'))
import tc2_sdm  # noqa: E402


def A(vpos, ok=True):
    """agreement record of an aligned block"""
    return dict(vpos=vpos, vend=vpos + 10, order_ok=ok, ok=ok, reason=None if ok else 'agree_order')


NOALIGN = dict(vpos=None, vend=None, order_ok=None, ok=False, reason='agree_text')


class LisTests(unittest.TestCase):
    def test_longest_nondecreasing_keeps_the_shared_order(self):
        self.assertEqual(tc2_sdm.longest_nondecreasing([0, 5, 7, 8, 9, 1, 2, 3]), {0, 1, 2, 3, 4})     # displaced group (three blocks) excluded
        # an exact tie (two blocks vs two blocks) has no evidence either way: the later group is the one excluded — deterministic, fail closed
        self.assertEqual(len(tc2_sdm.longest_nondecreasing([0, 5, 7, 1, 2])), 3)
        self.assertEqual(tc2_sdm.longest_nondecreasing([0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 1, 2, 3]), set(range(11)))
        self.assertEqual(tc2_sdm.longest_nondecreasing([]), set())
        self.assertEqual(tc2_sdm.longest_nondecreasing([3, 3, 3]), {0, 1, 2})                          # ties are non-decreasing

    def test_adjacent_swap_excludes_exactly_one_block(self):
        keep = tc2_sdm.longest_nondecreasing([0, 10, 30, 20, 40])
        self.assertEqual(len(keep), 4)
        self.assertTrue(keep == {0, 1, 2, 4} or keep == {0, 1, 3, 4})

    def test_the_tc2_p1_tolerance_rule_would_have_missed_the_swap(self):
        # documented regression: the old «min of the two previous offsets» rule never flags an adjacent swap
        seq = [0, 10, 30, 20, 40]
        flagged_old = [i for i in range(1, len(seq)) if seq[i] < min(seq[max(0, i - 2):i])]
        self.assertEqual(flagged_old, [])
        self.assertEqual(len(tc2_sdm.longest_nondecreasing(seq)), 4)


class ResequenceTests(unittest.TestCase):
    def test_displaced_group_returns_under_its_anchor_in_group_order(self):
        # primary order: title(0) body1(1) body2(2) body3(3) | displaced group: box-label(4) box-line(5), verifier says they follow the title
        agree = [A(0), A(300), A(400), A(500), A(20, ok=False), A(40, ok=False)]
        boxes = [[0.1, 0.05, 0.6, 0.03], [0.1, 0.30, 0.8, 0.05], [0.1, 0.40, 0.8, 0.05], [0.1, 0.50, 0.8, 0.05],
                 [0.2, 0.12, 0.1, 0.02], [0.2, 0.15, 0.6, 0.04]]
        self.assertEqual(tc2_sdm.resequence(agree, boxes), [0, 4, 5, 1, 2, 3])
        self.assertTrue(agree[4]['moved'] and agree[5]['moved'])

    def test_move_contradicting_column_geometry_is_refused(self):
        # verifier wants block 3 (y=0.60, same column) placed before block 1 (y=0.30): geometry says no → primary slot kept
        agree = [A(0), A(100), A(200), A(50, ok=False)]
        boxes = [[0.1, 0.05, 0.8, 0.03], [0.1, 0.30, 0.8, 0.05], [0.1, 0.45, 0.8, 0.05], [0.1, 0.60, 0.8, 0.05]]
        self.assertEqual(tc2_sdm.resequence(agree, boxes), [0, 1, 2, 3])
        self.assertFalse(agree[3]['moved'])
        self.assertEqual(agree[3]['reason'], 'agree_order')      # still withheld — only the card position is decided by geometry

    def test_side_by_side_pair_read_right_to_left_by_the_verifier_stays(self):
        # KHTN 7 p20 shape: primary reads a) (x=0.2) then b) (x=0.45); the verifier stream has b) BEFORE a), so a) is the
        # LIS complement and would be moved after b) — the row-band check (a following block must lie to the right) refuses
        agree = [A(0), A(1007, ok=False), A(1001)]
        boxes = [[0.1, 0.05, 0.8, 0.03], [0.20, 0.70, 0.08, 0.015], [0.45, 0.70, 0.08, 0.015]]
        self.assertEqual(tc2_sdm.resequence(agree, boxes), [0, 1, 2])
        self.assertFalse(agree[1]['moved'])
        # the mirror case — the verifier is right (primary read b) first) — IS moved: a) lands before b)
        agree = [A(0), A(1001, ok=False), A(1007)]
        boxes = [[0.1, 0.05, 0.8, 0.03], [0.20, 0.70, 0.08, 0.015], [0.45, 0.70, 0.08, 0.015]]
        self.assertEqual(tc2_sdm.resequence(agree, boxes), [0, 1, 2])   # index 1 = a) already first; anchor 0 → same slot
        agree = [A(0), A(1007), A(1001, ok=False)]
        boxes = [[0.1, 0.05, 0.8, 0.03], [0.45, 0.70, 0.08, 0.015], [0.20, 0.70, 0.08, 0.015]]
        self.assertEqual(tc2_sdm.resequence(agree, boxes), [0, 2, 1])   # a) (index 2, left) moves before b) (right)

    def test_unaligned_blocks_keep_primary_order_and_are_never_dragged(self):
        agree = [A(0), dict(NOALIGN), A(100), dict(NOALIGN), A(50, ok=False)]
        boxes = [[0.1, 0.05, 0.8, 0.03], [0.1, 0.15, 0.4, 0.1], [0.1, 0.30, 0.8, 0.05], [0.5, 0.15, 0.4, 0.1], [0.1, 0.20, 0.8, 0.04]]
        seq = tc2_sdm.resequence(agree, boxes)
        self.assertEqual([i for i in seq if agree[i]['vpos'] is None], [1, 3])
        self.assertLess(seq.index(1), seq.index(2))
        self.assertEqual(seq, [0, 4, 1, 2, 3]) if agree[4]['moved'] else self.assertEqual(seq, [0, 1, 2, 3, 4])

    def test_agreement_marks_lis_complement_as_order_disagreement(self):
        if tc2_sdm.fuzz is None:
            self.skipTest('rapidfuzz not installed')
        # primary blocks in Docling order (three body paragraphs, then the displaced box); the verifier stream has the
        # box (P4, P5) right after the title
        prim = [dict(text=t, role='BODY') for t in ('tieu de bai hoc mau', 'doan than thu nhat cua bai mau', 'doan than thu hai cua bai mau',
                                                    'doan than thu ba cua bai mau', 'muc tieu', 'trinh bay duoc mot so cach don gian')]
        ver = dict(blocks=[dict(id=f'c{i}', text=t, role='BODY') for i, t in enumerate(('tieu de bai hoc mau', 'muc tieu', 'trinh bay duoc mot so cach don gian',
                                                                                     'doan than thu nhat cua bai mau', 'doan than thu hai cua bai mau', 'doan than thu ba cua bai mau'))])
        ag = tc2_sdm.agreement(prim, ver)
        self.assertEqual([a['order_ok'] for a in ag], [True, True, True, True, False, False])
        self.assertEqual([a['reason'] for a in ag], [None, None, None, None, 'agree_order', 'agree_order'])


class AlignTests(unittest.TestCase):
    def setUp(self):
        if tc2_sdm.fuzz is None:
            self.skipTest('rapidfuzz not installed')

    def test_repeated_label_aligns_to_the_next_occurrence_not_the_first(self):
        st = 'cach tiep can   doan mot dai dai dai   cach tiep can   doan hai dai dai dai'
        s, start, end = tc2_sdm.align_in_stream('cach tiep can', st, last_pos=0)
        self.assertEqual(start, 0)
        s2, start2, _ = tc2_sdm.align_in_stream('cach tiep can', st, last_pos=end + 5)
        self.assertGreater(start2, start)
        self.assertGreaterEqual(s2, tc2_sdm.TEXT_SIM)

    def test_displaced_block_still_found_earlier_when_nothing_follows(self):
        st = 'muc tieu cua bai hoc nay   than bai thu nhat   than bai thu hai'
        # last_pos already at the end of the stream (Docling appended the box): the global search finds it at the start
        s, start, _ = tc2_sdm.align_in_stream('muc tieu cua bai hoc nay', st, last_pos=len(st) - 8)
        self.assertEqual(start, 0)
        self.assertGreaterEqual(s, tc2_sdm.TEXT_SIM)

    def test_earliest_acceptable_beats_a_later_exact_match(self):
        # verifier OCR variant («hoa» vs «hoá»-like one-char slip) at the top; the exact words also occur later in a paragraph
        st = 'nguyen to hoa hoc   den nay nguoi ta da tim ra 118 nguyen to hoa hoc moi nguyen to'
        s, start, _ = tc2_sdm.align_in_stream('nguyen to hoa hoc', 'nguyen to hoa hocx   den nay nguoi ta da tim ra 118 nguyen to hoa hoc moi', last_pos=0)
        self.assertEqual(start, 0)


if __name__ == '__main__':
    unittest.main()
