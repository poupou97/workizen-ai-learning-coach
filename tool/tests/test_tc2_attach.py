#!/usr/bin/env python3
"""Round 4 · Lane A-pipeline — tests for the attachment additions of tool/corpus/tc2_attach.py and
tool/ui/lesson_attach.py (failure class 4: lesson attachment / identity;
docs/research/PIPELINE-ROUND4-FAILURE-CLASS-FIXES.md §4).

Synthetic OCR lines and TOCs only (no SGK text, Founder D4).

Run:  python3 -m unittest discover -s tool/tests -v"""
import os
import sys
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', 'corpus'))
sys.path.insert(0, os.path.join(HERE, '..', 'ui'))
import tc2_attach  # noqa: E402
import lesson_attach as la  # noqa: E402


def line(text, y, x=0.15, h=0.015):
    return dict(text=text, x=x, y=y, w=0.3, h=h)


BACK_COVER = [line('HUÂN CHƯƠNG HỒ CHÍ MINH', 0.19), line('TOÁN 4', 0.24), line('BỘ SÁCH GIÁO KHOA LỚP 4 - MẪU', 0.56, h=0.023),
              line('1. Môn mẫu 4, tập một', 0.59), line('9. Môn mẫu khác 4', 0.59, x=0.47), line('Website: https://example.invalid', 0.76),
              line('ISBN 978-0-00-000000-0', 0.85), line('9780000 000000', 0.90, x=0.74)]
LESSON_PAGE = [line('Bài 21', 0.07, h=0.03), line('TIÊU ĐỀ BÀI MẪU', 0.07, x=0.3, h=0.03), line('Một đoạn văn mẫu dài hơn hai mươi kí tự.', 0.15),
               line('Một đoạn văn mẫu khác cũng dài hơn hai mươi kí tự.', 0.2), line('75', 0.95, x=0.9)]


class CoverTests(unittest.TestCase):
    def test_back_cover_is_end_matter_and_never_a_lesson(self):
        info = tc2_attach.page_info('00-sgk-mau', 122, n_pages=122, lines=BACK_COVER)
        self.assertEqual(info['kind'], 'back_cover')
        self.assertGreaterEqual(info['cover_marks'], tc2_attach.COVER_MIN_MARKS)

    def test_a_single_mark_is_not_a_cover(self):
        # a lesson page that happens to print an ISBN-like line (one mark) stays a page
        lines = LESSON_PAGE + [line('ISBN 978-0-00-000000-0', 0.5)]
        info = tc2_attach.page_info('00-sgk-mau', 100, n_pages=122, lines=lines)
        self.assertEqual(info['kind'], 'page')

    def test_cover_marks_in_the_middle_of_a_book_are_not_a_cover(self):
        info = tc2_attach.page_info('00-sgk-mau', 60, n_pages=122, lines=BACK_COVER)
        self.assertNotIn(info['kind'], ('back_cover', 'front_cover'))

    def test_lesson_page_is_a_page_with_a_header(self):
        info = tc2_attach.page_info('00-sgk-mau', 76, n_pages=122, lines=LESSON_PAGE)
        self.assertEqual(info['kind'], 'page')
        self.assertEqual(info['header']['number'], 21)


class SystematicOffsetTests(unittest.TestCase):
    def infos(self, diffs, toc):
        """pages with headers whose printed page = TOC start + diff"""
        out, pages = {}, []
        for i, (n, d) in enumerate(diffs):
            p = 10 + 4 * i
            out[p] = dict(kind='page', header=dict(number=n), printed=toc[n]['pageStart'] + d)
            pages.append(p)
        return pages, out

    def test_consistent_offset_is_detected(self):
        toc = {n: dict(pageStart=6 + 4 * (n - 1)) for n in range(1, 9)}
        pages, infos = self.infos([(n, -2) for n in range(1, 8)] + [(8, -1)], toc)
        self.assertEqual(tc2_attach._systematic_toc_offset(pages, infos, toc, off=None), -2)

    def test_no_offset_when_headers_agree_with_the_toc_or_are_too_few(self):
        toc = {n: dict(pageStart=6 + 4 * (n - 1)) for n in range(1, 9)}
        pages, infos = self.infos([(n, 0) for n in range(1, 9)], toc)
        self.assertEqual(tc2_attach._systematic_toc_offset(pages, infos, toc, off=None), 0)
        pages, infos = self.infos([(1, -2), (2, -2), (3, -2)], toc)
        self.assertEqual(tc2_attach._systematic_toc_offset(pages, infos, toc, off=None), 0)     # < 5 headers
        pages, infos = self.infos([(1, -2), (2, -2), (3, 0), (4, 0), (5, 1), (6, -1)], toc)
        self.assertEqual(tc2_attach._systematic_toc_offset(pages, infos, toc, off=None), 0)     # no value at ≥ 60 %


class LessonAttachOffsetTests(unittest.TestCase):
    """tool/ui/lesson_attach.py (pack builder): a systematic (header − TOC) offset shifts the TOC starts before the
    conflict test, so a TV5-shaped book (badge 2 pages before the TOC start) is no longer conflicted on every lesson."""

    def L(self, number, page_start):
        return dict(number=number, pageStart=page_start, title=f'Bài {number}')

    def H(self, number, printed, source='header', confidence=0.85):
        return dict(number=number, page_printed=printed, source=source, confidence=confidence)

    def test_tv5_shape_shifts_toc_starts_and_clears_conflicts(self):
        toc = [self.L(n, 8 + 6 * (n - 1)) for n in range(1, 9)]
        headers = [self.H(n, 8 + 6 * (n - 1) - 2) for n in range(1, 8)]        # 7 of 8 headers, all −2
        ranges, cap, info = la.capped_ranges(toc, headers)
        self.assertEqual(info['toc_offset'], -2)
        self.assertEqual(info['conflicted'], [])
        by = {r['number']: r for r in ranges}
        self.assertEqual(by[1]['lo'], 6)
        self.assertEqual(by[2]['lo'], 12)
        b = la.BookAttach('tv5-mau', toc, header_lessons=headers)
        self.assertEqual(b.attach(6)['lesson'], 1)                            # the badge page belongs to its lesson
        self.assertEqual(b.attach(11)['lesson'], 1)
        self.assertEqual(b.attach(12)['lesson'], 2)

    def test_without_a_systematic_offset_v1_behaviour_is_unchanged(self):
        toc = [self.L(n, 6 + 5 * (n - 1)) for n in range(1, 7)]
        ranges, cap, info = la.capped_ranges(toc, [self.H(3, 22)])            # one header 6 pages off → conflict as before
        self.assertEqual(info['toc_offset'], 0)
        self.assertEqual(info['conflicted'], [3])
        self.assertEqual(la.systematic_toc_offset({1: 6, 2: 11}, [self.H(1, 4), self.H(2, 9)]), 0)   # < 5 headers

    def test_rule_id_names_the_revision(self):
        self.assertEqual(la.RULE, 'capped-toc-v2')


if __name__ == '__main__':
    unittest.main()
