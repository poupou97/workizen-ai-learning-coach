#!/usr/bin/env python3
"""WAL-210 — tests for tool/ui/lesson_attach.py (audit gates G2 + G3) on SYNTHETIC TOCs.

Run:  python3 -m unittest discover -s tool/tests -v
  or: python3 -m pytest tool/tests"""
import os
import sys
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', 'ui'))
import lesson_attach as la  # noqa: E402


def L(number, page_start, title=None):
    return dict(number=number, pageStart=page_start, title=title or f'Bài {number}')


def H(number, printed, source='header', confidence=0.85):
    return dict(number=number, page_printed=printed, source=source, confidence=confidence)


# A truncated TOC (like KHTN 8: 22 of 47 lessons) — gaps 5,5,4,4,4 → median 4 → cap 10
TRUNCATED = [L(1, 6), L(2, 11), L(3, 16), L(4, 20), L(5, 24), L(6, 28)]
# A TOC with unranged canonical lessons (like Khoa học 4: Bài 2 and 3 have no pageStart)
HOLEY = [L(1, 5), L(2, None), L(3, None), L(4, 17), L(5, 21), L(6, 25), L(7, 29), L(8, 31)]


class CapTests(unittest.TestCase):
    def test_cap_is_2_5x_median_min_8_same_as_pattern_router(self):
        self.assertEqual(la.cap_for([6, 11, 16, 20, 24, 28]), 10)      # median 4 → 10
        self.assertEqual(la.cap_for([1, 3, 5, 7]), 8)                   # median 2 → 5 → min 8
        self.assertEqual(la.cap_for([1, 9, 17]), 20)                    # median 8 → 20
        self.assertEqual(la.cap_for([1]), 8)                            # single lesson → min
        self.assertEqual(la.cap_for([]), 8)

    def test_ranges_end_at_next_start_or_cap(self):
        ranges, cap, info = la.capped_ranges(TRUNCATED)
        self.assertEqual(cap, 10)
        self.assertEqual([(r['number'], r['lo'], r['hi'], r['hi_source']) for r in ranges],
                         [(1, 6, 11, 'next_start'), (2, 11, 16, 'next_start'), (3, 16, 20, 'next_start'),
                          (4, 20, 24, 'next_start'), (5, 24, 28, 'next_start'), (6, 28, 38, 'cap')])
        self.assertEqual((info['canonical'], info['toc_ranged'], info['repaired'], info['unranged']), (6, 6, 0, []))

    def test_long_gap_is_capped_not_swallowed(self):
        ranges, cap, _ = la.capped_ranges([L(1, 6), L(2, 10), L(3, 14), L(4, 18), L(5, 22), L(6, 26), L(7, 60)])
        r6 = next(r for r in ranges if r['number'] == 6)
        self.assertEqual((r6['lo'], r6['hi']), (26, 36))   # not 60


class RepairTests(unittest.TestCase):
    def test_header_start_repairs_an_unranged_canonical_lesson(self):
        ranges, cap, info = la.capped_ranges(HOLEY, [H(1, 5, 'both', 0.95), H(2, 9), H(3, 13)])
        by = {r['number']: r for r in ranges}
        self.assertEqual((by[1]['lo'], by[1]['hi'], by[1]['start_source']), (5, 9, 'toc'))
        self.assertEqual((by[2]['lo'], by[2]['hi'], by[2]['start_source']), (9, 13, 'header'))
        self.assertEqual((by[3]['lo'], by[3]['hi']), (13, 17))
        self.assertIsNone(by[1]['ambiguous_after'])                    # hole closed by the repair
        self.assertEqual(info['repaired'], 2); self.assertEqual(info['unranged'], [])

    def test_toc_sourced_or_too_low_confidence_header_entries_are_ignored(self):
        ranges, _, info = la.capped_ranges(HOLEY, [H(2, 9, 'header', 0.5), H(3, 13, 'toc', 0.6)])
        self.assertEqual(info['repaired'], 0); self.assertEqual(info['unranged'], [2, 3])

    def test_0_6_header_is_accepted_only_when_bracketed_by_known_starts(self):
        # LS&ĐL 5 shape: Bài 3 header missed → Bài 4 header gets 0.6; Bài 3 TOC 16 < 20 < Bài 5 header 25 → accepted
        toc = [L(1, 5), L(2, 9), L(3, 16), L(4, None), L(5, None), L(6, None), L(7, 32)]
        hl = [H(1, 5, 'both', 0.95), H(2, 9, 'both', 0.95), H(4, 20, 'header', 0.6), H(5, 25), H(6, 29)]
        self.assertEqual(la.accepted_header_starts({1: 5, 2: 9, 3: 16, 7: 32}, hl), {1: 5, 2: 9, 4: 20, 5: 25, 6: 29})
        ranges, _, info = la.capped_ranges(toc, hl)
        self.assertEqual(info['repaired'], 3); self.assertEqual(info['unranged'], [])
        # not bracketed (page before Bài 3's start) → ignored; no higher neighbour → ignored
        self.assertNotIn(4, la.accepted_header_starts({1: 5, 2: 9, 3: 16, 7: 32}, [H(4, 12, 'header', 0.6), H(5, 25)]))
        self.assertNotIn(8, la.accepted_header_starts({1: 5, 2: 9, 3: 16, 7: 32}, [H(8, 40, 'header', 0.6)]))

    def test_non_canonical_header_start_terminates_the_previous_range(self):
        # KHTN 8 shape: TOC ends at Bài 6 (p28), headers found Bài 7 at p31 and Bài 8 at p35
        ranges, cap, info = la.capped_ranges(TRUNCATED, [H(7, 31), H(8, 35)])
        r6 = next(r for r in ranges if r['number'] == 6)
        self.assertEqual((r6['lo'], r6['hi'], r6['hi_source']), (28, 31, 'header_terminator'))
        self.assertEqual(info['terminators'], 2)
        self.assertEqual({r['number'] for r in ranges}, {1, 2, 3, 4, 5, 6})   # no range for 7/8

    def test_toc_vs_header_start_conflict_marks_the_lesson(self):
        ranges, _, info = la.capped_ranges(TRUNCATED, [H(3, 22)])            # TOC says 16, header says 22
        r3 = next(r for r in ranges if r['number'] == 3)
        self.assertTrue(r3['conflicted']); self.assertEqual(info['conflicted'], [3])
        self.assertEqual(r3['lo'], 16)                                        # TOC start kept
        ranges, _, info = la.capped_ranges(TRUNCATED, [H(3, 17)])            # ±1 is agreement
        self.assertEqual(info['conflicted'], [])

    def test_repair_can_be_switched_off(self):
        old = la.HEADER_REPAIR
        try:
            la.HEADER_REPAIR = False
            ranges, _, info = la.capped_ranges(HOLEY, [H(2, 9), H(3, 13)])
            self.assertEqual(info['repaired'], 0); self.assertEqual(info['unranged'], [2, 3])
        finally:
            la.HEADER_REPAIR = old


class AttachTests(unittest.TestCase):
    def test_pages_beyond_the_cap_belong_to_no_lesson(self):
        b = la.BookAttach('book', TRUNCATED)
        self.assertEqual(b.attach(30)['lesson'], 6)
        self.assertEqual(b.attach(37)['lesson'], 6)
        r = b.attach(38)
        self.assertIsNone(r['lesson']); self.assertEqual(r['reason'], la.BEYOND_CAP)
        r = b.attach(116)
        self.assertIsNone(r['lesson']); self.assertEqual(r['reason'], la.BEYOND_CAP)

    def test_pages_beyond_a_header_terminator_are_withheld(self):
        b = la.BookAttach('khtn8', TRUNCATED, header_lessons=[H(7, 31)])
        self.assertEqual(b.attach(30)['lesson'], 6)
        r = b.attach(32)
        self.assertIsNone(r['lesson']); self.assertEqual(r['reason'], la.BEYOND_HEADER_END)

    def test_before_first_lesson_and_unknown_page(self):
        b = la.BookAttach('book', TRUNCATED)
        self.assertEqual(b.attach(3)['reason'], la.BEFORE_FIRST)
        self.assertEqual(b.attach(None)['reason'], la.PAGE_UNKNOWN)
        self.assertEqual(la.BookAttach('empty', [L(1, None)]).attach(5)['reason'], la.NO_TOC_RANGES)

    def test_unranged_successor_makes_later_pages_ambiguous(self):
        b = la.BookAttach('kh4', HOLEY)
        self.assertEqual(b.attach(5)['reason'], la.ATTACHED)            # the start page itself is safe
        self.assertEqual(b.attach(5)['lesson'], 1)
        r = b.attach(10)                                                # could be Bài 2 → withheld
        self.assertIsNone(r['lesson']); self.assertEqual(r['reason'], la.SUCCESSOR_UNRANGED); self.assertEqual(r['toc_lesson'], 1)
        self.assertEqual(b.attach(18)['lesson'], 4)                     # Bài 4→5 has no hole
        self.assertEqual(b.range_of(1)['unranged_successors'], [2, 3])

    def test_page_level_continuation_does_not_lift_the_ambiguity(self):
        b = la.BookAttach('kh4', HOLEY, header_pages={9: dict(lesson=1, method='continuation')})
        r = b.attach(8, pdf_page=9)
        self.assertIsNone(r['lesson']); self.assertEqual(r['reason'], la.SUCCESSOR_UNRANGED)

    def test_repaired_start_moves_the_page_to_the_right_lesson(self):
        # Khoa học 4 p11: TOC says Bài 1 (start 5, Bài 2 unranged); header found Bài 2 at printed 8
        b = la.BookAttach('kh4', HOLEY, header_pages={11: dict(lesson=2, method='continuation')}, header_lessons=[H(1, 5, 'both', 0.95), H(2, 8), H(3, 13)])
        r = b.attach(10, pdf_page=11)
        self.assertEqual((r['lesson'], r['reason'], r['start_source']), (2, la.ATTACHED_REPAIRED, 'header'))
        self.assertEqual(b.attach(5, pdf_page=6)['reason'], la.ATTACHED)

    def test_positive_header_disagreement_withholds_never_moves(self):
        # KHTN 8 p100: TOC Bài 22-shape lesson 6 (start 28), header says Bài 7 — not canonical → withheld
        b = la.BookAttach('khtn8', TRUNCATED, header_pages={30: dict(lesson=7, method='header')}, header_lessons=[H(7, 29)])
        r = b.attach(29, pdf_page=30)
        self.assertIsNone(r['lesson']); self.assertEqual(r['reason'], la.HEADER_DISAGREES); self.assertEqual(r['header_lesson'], 7)
        # canonical header lesson whose start lies at/after the TOC lesson's start → positive disagreement
        b2 = la.BookAttach('x', TRUNCATED, header_pages={19: dict(lesson=4, method='header')}, header_lessons=[H(4, 18)])
        r = b2.attach(18, pdf_page=19)                                   # TOC: Bài 3 [16,20); header Bài 4 starts 18 → conflict… no: start 18 vs TOC 20 is 2 apart → conflicted lesson 4
        self.assertIsNone(r['lesson']); self.assertEqual(r['reason'], la.HEADER_DISAGREES)

    def test_stale_header_chain_is_overruled_by_the_toc(self):
        # LS&ĐL 5 shape: header chain says "Bài 2 continues" up to p21 because the Bài 3 header was missed;
        # TOC says Bài 3 starts p16 and headers found Bài 4 at p20 → page 18 is Bài 3
        toc = [L(1, 5), L(2, 9), L(3, 16), L(4, None), L(5, None), L(6, None), L(7, 32)]
        hl = [H(1, 5, 'both', 0.95), H(2, 9, 'both', 0.95), H(4, 20), H(5, 25), H(6, 29)]
        b = la.BookAttach('lsdl5', toc, header_pages={20: dict(lesson=2, method='continuation')}, header_lessons=hl)
        r = b.attach(18, pdf_page=20)
        self.assertEqual((r['lesson'], r['reason']), (3, la.ATTACHED_HEADER_STALE))
        self.assertEqual(b.range_of(3)['hi'], 20)                        # ended by the repaired Bài 4 start

    def test_header_no_lesson_and_start_conflict_withhold(self):
        b = la.BookAttach('x', TRUNCATED, header_pages={2: dict(lesson=None, method='none', kind='front_matter')}, header_lessons=[H(3, 22)])
        self.assertEqual(b.attach(6, pdf_page=2)['reason'], la.HEADER_NO_LESSON)
        r = b.attach(17)
        self.assertIsNone(r['lesson']); self.assertEqual(r['reason'], la.START_CONFLICT)


class IdentityTests(unittest.TestCase):
    def test_non_canonical_lesson_is_dropped(self):
        tv = [L(1, 10), L(2, 15), L(3, 19), L(4, 24), L(6, 32), L(7, 36)]   # Bài 5 missing from the TOC
        b = la.BookAttach('tv5-tap-hai', tv)
        self.assertEqual(b.check_upstream(5, 28), (False, la.NOT_CANONICAL))
        self.assertEqual(b.check_upstream(23, 100), (False, la.NOT_CANONICAL))
        self.assertEqual(b.check_upstream(None, 12), (False, la.NOT_CANONICAL))
        self.assertEqual(b.check_upstream(2, 16), (True, la.RANGE_OK))

    def test_upstream_range_crosscheck_is_counted_not_dropped(self):
        b = la.BookAttach('tv5', [L(1, 10), L(2, 15), L(3, None), L(4, 24)])
        self.assertEqual(b.check_upstream(1, 40), (True, la.RANGE_MISMATCH))
        self.assertEqual(b.check_upstream(3, 20), (True, la.UNRANGED_LESSON))
        self.assertEqual(b.check_upstream(2, None), (True, la.PAGE_UNKNOWN))


class RegistryTests(unittest.TestCase):
    def test_registry_counts_reasons_and_logs_drops_and_moves(self):
        docs = [dict(sourceDocumentId='b1', lessons=HOLEY), dict(sourceDocumentId='b2', lessons=TRUNCATED)]
        reg = la.AttachRegistry(docs, attach_dir='/nonexistent', use_headers=True)
        self.assertEqual(reg.attach('khoaExperiments', 'b1', 5, 6)['lesson'], 1)
        self.assertIsNone(reg.attach('khoaExperiments', 'b1', 10, 11)['lesson'])
        self.assertIsNone(reg.attach('khoaExperiments', 'b2', 116, 117)['lesson'])
        self.assertTrue(reg.check_upstream('tvReadings', 'b2', 2, 12))
        self.assertFalse(reg.check_upstream('tvReadings', 'b2', 23, 12))
        self.assertTrue(reg.check_upstream('tvReadings', 'b2', 1, 30))       # mismatch: kept + flagged
        s = reg.summary()
        self.assertEqual(s['rule'], 'capped-toc-v1')
        self.assertEqual(s['counts']['khoaExperiments'], {la.ATTACHED: 1, la.SUCCESSOR_UNRANGED: 1, la.BEYOND_CAP: 1})
        self.assertEqual(s['counts']['tvReadings'], {la.RANGE_OK: 1, la.NOT_CANONICAL: 1, la.RANGE_MISMATCH: 1})
        self.assertEqual((s['dropped'], s['flagged'], s['moved']), (3, 1, 0))
        self.assertEqual([d['reason'] for d in reg.dropped], [la.SUCCESSOR_UNRANGED, la.BEYOND_CAP, la.NOT_CANONICAL])
        self.assertFalse(s['books']['b1']['headerData'])
        self.assertEqual(reg.attach('suSources', 'unknown-book', 5)['reason'], la.NO_TOC_RANGES)

    def test_registry_reads_header_files_and_records_moves(self):
        import json, tempfile
        d = tempfile.mkdtemp()
        # page_printed in the file is deliberately WRONG (banner digit); page_pdf − printed_offset must win
        json.dump(dict(counts=dict(printed_offset=1),
                       pages=[dict(page=11, lesson=2, method='continuation', kind='page')],
                       lessons=[dict(number=1, page_printed=5, page_pdf=6, source='both', confidence=0.95),
                                dict(number=2, page_printed=2, page_pdf=9, source='header', confidence=0.85)]),
                  open(os.path.join(d, 'b1.json'), 'w'))
        self.assertEqual(la.load_header_data('b1', d)[1][1]['page_printed'], 8)
        reg = la.AttachRegistry([dict(sourceDocumentId='b1', lessons=HOLEY)], attach_dir=d)
        r = reg.attach('khoaExperiments', 'b1', 10, 11)
        self.assertEqual((r['lesson'], r['reason']), (2, la.ATTACHED_REPAIRED))
        self.assertEqual(reg.summary()['moved'], 1)
        self.assertEqual(reg.moved[0]['legacyLesson'], 1)
        self.assertTrue(reg.summary()['books']['b1']['headerData'])


if __name__ == '__main__':
    unittest.main()
