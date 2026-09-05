#!/usr/bin/env python3
"""Round 4 · Lane A-pipeline — one test class per finding of the independent correctness review of
branch `lane-a/round4-pipeline-failure-classes` (posted in full on PR #77; summarised in
docs/research/PIPELINE-ROUND4-FAILURE-CLASS-FIXES.md §13).

Every test here FAILED before the fix it pins. The findings about lesson attachment (F13, F14) live in
tool/tests/test_tc2_attach.py, beside the cover rule they are about.

Synthetic strings and blocks only — no SGK text (Founder D4). Where a real word appears it is a marker
word of the printed furniture («PHẦN», «CHƯƠNG», «HUÂN CHƯƠNG»), never lesson content.

Run:  python3 -m unittest discover -s tool/tests -v"""
import os
import sys
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', 'corpus'))
import tc2_sdm  # noqa: E402
import tsl_to_lesson_document as br  # noqa: E402


class F7ChapterMarkerBoundaryTests(unittest.TestCase):
    """F7 — `CHAPTER_HDR`'s `([IVX]+|\\d{1,2})` had no trailing boundary, so the roman alternative bit into
    the next word and invented a chapter out of an ordinary section name. These are CHILD-FACING labels."""

    def label(self, text):
        m = br.CHAPTER_HDR.search(text)
        return (br.chapter_label(m), text[m.end():]) if m else None

    def test_an_ordinary_section_name_is_not_a_chapter(self):
        # «PHẦN VĂN», «PHẦN TIẾNG VIỆT» are standard Ngữ văn TOC section names; the roman group used to
        # eat their first letter — «Phần V» + title «ĂN HỌC»
        for t in ('PHẦN VĂN HỌC', 'PHẦN VĂN', 'PHẦN XÃ HỘI', 'PHẦN TIẾNG VIỆT'):
            self.assertIsNone(self.label(t), t)

    def test_a_chapter_word_followed_by_a_word_starting_with_a_numeral_letter_is_not_a_chapter(self):
        self.assertIsNone(self.label('CHƯƠNG VIỆT NAM CUỐI THẾ KỈ XIX'))
        self.assertIsNone(self.label('CHƯƠNG XÃ HỘI HIỆN ĐẠI'))

    def test_a_medal_is_not_a_chapter(self):
        # «HUÂN CHƯƠNG» is the medal, not a chapter marker — it needs a boundary the space alone gave it
        for t in ('HUÂN CHƯƠNG I', 'HUÂN CHƯƠNG II', 'Huân chương I'):
            self.assertIsNone(self.label(t), t)

    def test_real_chapter_markers_still_match(self):
        for t, want in (('CHƯƠNG I', 'Chương I'), ('CHƯƠNG II - TIÊU ĐỀ MẪU', 'Chương II'),
                        ('CHƯƠNG 3. TIÊU ĐỀ MẪU', 'Chương 3'), ('PHẦN I - TIÊU ĐỀ MẪU', 'Phần I'),
                        ('PHẦN 2: TIÊU ĐỀ MẪU', 'Phần 2'), ('CHỦ ĐỀ 3. TIÊU ĐỀ MẪU', 'Chủ đề 3'),
                        ('CHƯƠNG VII TIÊU ĐỀ MẪU', 'Chương VII')):
            got = self.label(t)
            self.assertIsNotNone(got, t)
            self.assertEqual(got[0], want, t)


class F9ChapterToneClassTests(unittest.TestCase):
    """F9 — the tone class did not match its own comment («the same tone variants as the lesson banner»):
    `Ề` was listed twice, four of the six Ê-family forms were missing and `Ù` was missing from `CH`."""

    def test_every_tone_variant_of_the_banner_is_read(self):
        for t in ('CHỦ ĐỀ 1', 'CHỦ ĐẾ 2', 'CHỦ ĐỂ 3', 'CHỦ ĐỄ 4', 'CHỦ ĐỆ 5', 'CHỦ ĐÊ 6',
                  'CHÙ ĐỀ 7', 'CHÚ ĐỀ 8', 'CHŨ ĐỀ 9', 'CHỤ ĐỀ 10', 'CHU ĐE 11'):
            m = br.CHAPTER_HDR.search(t)
            self.assertIsNotNone(m, t)
            self.assertEqual(br.chapter_label(m), 'Chủ đề ' + t.split()[-1], t)

    def test_a_word_that_is_not_the_banner_is_not_a_chapter(self):
        for t in ('CHÚ Ý 1', 'CHÀO ĐỀ 2', 'CHỦ ĐỀ'):
            self.assertIsNone(br.CHAPTER_HDR.search(t), t)


class F8TocTitleTrailingNumberTests(unittest.TestCase):
    """F8 — `clean_toc_title`'s unconditional trailing 1–3-digit strip is written for a lesson line
    (title · leader · page number) but is applied to chapter titles, which often carry no page number:
    a History chapter title lost the last digit of its year."""

    def test_a_year_at_the_end_of_a_title_is_not_a_page_number(self):
        self.assertEqual(br.clean_toc_title('TIÊU ĐỀ MẪU TỪ 1858 ĐẾN NĂM 1945'),
                         'TIÊU ĐỀ MẪU TỪ 1858 ĐẾN NĂM 1945')
        self.assertEqual(br.clean_toc_title('TIÊU ĐỀ MẪU 1930 - 1945'), 'TIÊU ĐỀ MẪU 1930 - 1945')

    def test_a_page_number_behind_a_leader_is_still_stripped(self):
        self.assertEqual(br.clean_toc_title('TIÊU ĐỀ MẪU ..... 93'), 'TIÊU ĐỀ MẪU')
        self.assertEqual(br.clean_toc_title('TIÊU ĐỀ MẪU .93'), 'TIÊU ĐỀ MẪU')
        self.assertEqual(br.clean_toc_title('TIÊU ĐỀ MẪU … 5'), 'TIÊU ĐỀ MẪU')
        self.assertEqual(br.clean_toc_title('TIÊU ĐỀ MẪU 5'), 'TIÊU ĐỀ MẪU')

    def test_a_year_followed_by_a_page_number_keeps_the_year(self):
        self.assertEqual(br.clean_toc_title('TIÊU ĐỀ MẪU ĐẾN NĂM 1945 ..... 93'), 'TIÊU ĐỀ MẪU ĐẾN NĂM 1945')


if __name__ == '__main__':
    unittest.main()
