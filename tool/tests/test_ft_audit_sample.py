#!/usr/bin/env python3
"""WAL-210 — tests for the pure helpers of tool/corpus/ft_audit_sample.py (no corpus needed).

Run:  python3 -m unittest discover -s tool/tests -v"""
import os
import random
import sys
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', 'corpus'))
import ft_audit_sample as fa  # noqa: E402


class HelperTests(unittest.TestCase):
    def test_norm_and_sim(self):
        self.assertEqual(fa.norm('  Tách  chất, khỏi hỗn hợp! '), 'tách chất khỏi hỗn hợp')
        self.assertEqual(fa.sim('Tiến hành:', 'Tiến hành: Lấy một cốc nước'), 1.0)     # containment
        self.assertLess(fa.sim('Chuẩn bị', 'Kết luận'), 0.6)
        self.assertEqual(fa.sim('', 'x'), 0.0)

    def test_allocation_is_proportional_with_floor_and_deterministic(self):
        strata = {('khoa', 'b1'): 100, ('tv', 'b2'): 300, ('dia', 'b3'): 2}
        alloc = fa.allocate(strata, 40, 3)
        self.assertEqual(alloc[('dia', 'b3')], 2)          # floor capped at stratum size
        self.assertEqual(alloc[('khoa', 'b1')], 10); self.assertEqual(alloc[('tv', 'b2')], 30)
        self.assertEqual(alloc, fa.allocate(dict(reversed(list(strata.items()))), 40, 3))

    def test_seeded_sampling_is_reproducible(self):
        pool = list(range(50))
        a = random.Random(20260905).sample(pool, 7); b = random.Random(20260905).sample(pool, 7)
        self.assertEqual(a, b)
        self.assertNotEqual(a, random.Random(1).sample(pool, 7))

    def test_link_lines_matches_substrings_and_unions_bbox(self):
        fa._ocr[('bk', 5)] = [dict(text='Chuẩn bị: nước, 2 cốc thuỷ tinh', x=0.1, y=0.5, w=0.5, h=0.02),
                              dict(text='Tiến hành:', x=0.1, y=0.53, w=0.1, h=0.02),
                              dict(text='Lấy một cốc nước, cho 1 thìa đất vào cốc.', x=0.1, y=0.56, w=0.7, h=0.02),
                              dict(text='61', x=0.9, y=0.95, w=0.02, h=0.015)]
        idx, bbox, cov = fa.link_lines('bk', 5, 'Lấy một cốc nước, cho 1 thìa đất vào cốc. Khuấy mạnh cho hỗn hợp trong cốc đục đều lên.')
        self.assertEqual(idx, [2]); self.assertEqual(bbox[:2], [0.1, 0.56]); self.assertGreater(cov, 0.3)
        idx, bbox, cov = fa.link_lines('bk', 5, 'Tiến hành')
        self.assertEqual(idx, [1])
        idx, bbox, cov = fa.link_lines('bk', 5, 'không có dòng nào khớp cả')
        self.assertEqual((idx, bbox, cov), ([], None, 0.0))

    def test_blocks_of_pack_decomposes_activities_and_skips_router_entries(self):
        pack = dict(khoaExperiments=[dict(book='06-b', page=60, pagePdf=61, lesson=17, title='T', chuanBi='c', tienHanh=['s1', 's2'], duDoan=None, quanSat='q')],
                    tvReadings=[dict(book='05-tv', lesson=1, page=8, passage='p' * 20, questions=[dict(prompt='Q1?', page=8)], source='pattern-router-v2-layout')],
                    tvWritings=[], suSources=[dict(book='05-su', page=18, pagePdf=20, lesson=3, excerpt='e', attribution='(a)', samGloss='sam')],
                    toanExercises={}, diaMaps=[], sourceAssets=[dict(asset='m.png', sourceDocumentId='05-su', pagePdf=12, pagePrinted=10, lesson=1, printedCaption='Hình 1')])
        fa._units.clear()
        blocks = fa.blocks_of_pack(pack, 6)
        kinds = [(b['family'], b['kind']) for b in blocks]
        self.assertEqual(kinds, [('khoaExperiments', 'title'), ('khoaExperiments', 'chuanBi'), ('khoaExperiments', 'step1'), ('khoaExperiments', 'step2'), ('khoaExperiments', 'quanSat'),
                                 ('suSources', 'excerpt'), ('suSources', 'attribution'), ('sourceAssets', 'caption')])
        self.assertTrue(all(b['activityId'] == blocks[0]['activityId'] for b in blocks[:5]))
        self.assertFalse(any('sam' in (b['text'] or '') for b in blocks))          # samGloss never sampled


if __name__ == '__main__':
    unittest.main()
