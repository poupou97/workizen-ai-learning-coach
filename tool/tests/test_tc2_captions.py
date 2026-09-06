#!/usr/bin/env python3
"""Round 4 · Lane A-pipeline — tests for the figure/caption relation (failure class 5) in tool/corpus/tc2_sdm.py and the
crop-padding rule of tool/corpus/tsl_to_lesson_document.py (docs/research/PIPELINE-ROUND4-FAILURE-CLASS-FIXES.md §5).

Synthetic blocks only (no SGK text, Founder D4).

Run:  python3 -m unittest discover -s tool/tests -v"""
import os
import sys
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', 'corpus'))
import tc2_sdm  # noqa: E402
import tsl_to_lesson_document as br  # noqa: E402


def cap(i, bbox, text='Hình 1.1 Mẫu'):
    return dict(id=f'b:{i:03d}', bbox=bbox, text=text, role=dict(value='caption', coarse='CAPTION', method='lexicon', confidence=0.9, evidence=[]))


class CaptionForPictureTests(unittest.TestCase):
    MED = 0.015

    def test_caption_directly_below_wins_over_a_farther_one(self):
        pic = [0.1, 0.3, 0.4, 0.2]
        near = cap(1, [0.15, 0.51, 0.3, 0.015]); far = cap(2, [0.15, 0.62, 0.3, 0.015])
        self.assertEqual(tc2_sdm.caption_for_picture(pic, [far, near], self.MED), 'b:001')

    def test_a_caption_beside_the_picture_is_not_linked(self):
        pic = [0.1, 0.3, 0.4, 0.2]
        beside = cap(1, [0.6, 0.35, 0.3, 0.015])       # no horizontal overlap
        self.assertIsNone(tc2_sdm.caption_for_picture(pic, [beside], self.MED))

    def test_caption_inside_the_lower_band_of_a_grown_picture_box(self):
        # Docling grows the picture box over its caption (KH4 p30, Vật lí 10 p30, Toán 12 p20)
        pic = [0.1, 0.3, 0.8, 0.6]
        inside = cap(1, [0.5, 0.88, 0.06, 0.012])
        self.assertEqual(tc2_sdm.caption_for_picture(pic, [inside], self.MED), 'b:001')

    def test_one_caption_serves_side_by_side_pictures(self):
        left = [0.1, 0.3, 0.3, 0.2]; right = [0.45, 0.3, 0.45, 0.2]
        shared = cap(1, [0.3, 0.51, 0.3, 0.015])
        self.assertEqual(tc2_sdm.caption_for_picture(left, [shared], self.MED), 'b:001')
        self.assertEqual(tc2_sdm.caption_for_picture(right, [shared], self.MED), 'b:001')

    def test_above_only_when_very_close(self):
        pic = [0.1, 0.3, 0.4, 0.2]
        above_near = cap(1, [0.15, 0.275, 0.3, 0.015]); above_far = cap(2, [0.15, 0.20, 0.3, 0.015])
        self.assertEqual(tc2_sdm.caption_for_picture(pic, [above_far, above_near], self.MED), 'b:001')
        self.assertIsNone(tc2_sdm.caption_for_picture(pic, [above_far], self.MED))


class CaptionContinuationTests(unittest.TestCase):
    def test_short_line_right_of_a_caption_label_on_the_same_line_is_its_continuation(self):
        label = cap(1, [0.28, 0.74, 0.08, 0.012], 'Hình 17.1')
        text = dict(id='b:002', bbox=[0.37, 0.735, 0.35, 0.02], text='Một số hiện tượng mẫu', role=dict(value='body', coarse='BODY', method='default', confidence=0.6, evidence=[]))
        n = tc2_sdm.caption_continuation_pass([label, text], med_h=0.015)
        self.assertEqual(n, 1)
        self.assertEqual((text['role']['value'], text['role']['coarse'], text['continues']), ('caption', 'CAPTION', 'b:001'))

    def test_sentences_numbered_items_and_far_blocks_are_not_continuations(self):
        label = cap(1, [0.28, 0.74, 0.08, 0.012], 'Hình 17.1')
        for t, bb in (('Một câu đầy đủ có dấu chấm.', [0.37, 0.735, 0.35, 0.02]), ('2. Một mục đánh số', [0.37, 0.735, 0.35, 0.02]),
                      ('Dòng ở xa bên phải', [0.5, 0.735, 0.35, 0.02]), ('Dòng ở hàng khác', [0.37, 0.80, 0.35, 0.02])):
            blk = dict(id='b:002', bbox=bb, text=t, role=dict(value='body', coarse='BODY', method='default', confidence=0.6, evidence=[]))
            self.assertEqual(tc2_sdm.caption_continuation_pass([label, blk], med_h=0.015), 0, t)
            self.assertEqual(blk['role']['value'], 'body')


class CropPadTests(unittest.TestCase):
    def test_padding_stops_short_of_neighbouring_text(self):
        fig = [0.1, 0.3, 0.4, 0.2]
        below = [0.1, 0.505, 0.4, 0.02]          # a text line 0.005 under the figure
        right = [0.52, 0.3, 0.3, 0.1]            # a paragraph 0.02 to the right
        L, T, R, B = br.crop_pads(fig, [below, right], pad=0.012, gap=0.003)
        self.assertEqual((L, T), (0.012, 0.012))
        self.assertAlmostEqual(B, 0.002, places=6)
        self.assertAlmostEqual(R, 0.017 if 0.017 < 0.012 else 0.012, places=6)

    def test_no_neighbours_means_full_padding_and_never_negative(self):
        self.assertEqual(br.crop_pads([0.1, 0.3, 0.4, 0.2], [], pad=0.012), (0.012, 0.012, 0.012, 0.012))
        touching = [0.1, 0.5, 0.4, 0.02]
        self.assertEqual(br.crop_pads([0.1, 0.3, 0.4, 0.2], [touching], pad=0.012)[3], 0.0)


if __name__ == '__main__':
    unittest.main()
