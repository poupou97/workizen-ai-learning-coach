#!/usr/bin/env python3
"""Round 4 · Lane A-pipeline — tests for the attachment additions of tool/corpus/tc2_attach.py and
tool/ui/lesson_attach.py (failure class 4: lesson attachment / identity;
docs/research/PIPELINE-ROUND4-FAILURE-CLASS-FIXES.md §4).

Synthetic OCR lines and TOCs only (no SGK text, Founder D4).

Run:  python3 -m unittest discover -s tool/tests -v"""
import json
import os
import shutil
import sys
import tempfile
import warnings
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
# the SGV back cover of the same series prints «BỘ SÁCH GIÁO VIÊN» and carries neither ISBN nor barcode
BACK_COVER_SGV = [line('HUÂN CHƯƠNG HỒ CHÍ MINH', 0.19), line('BỘ SÁCH GIÁO VIÊN LỚP 4 - MẪU', 0.56, h=0.023),
                  line('1. Môn mẫu 4, tập một - SGV', 0.59), line('9. Môn mẫu khác 4 - SGV', 0.59, x=0.47),
                  line('Website: https://example.invalid', 0.76)]
LESSON_PAGE = [line('Bài 21', 0.07, h=0.03), line('TIÊU ĐỀ BÀI MẪU', 0.07, x=0.3, h=0.03), line('Một đoạn văn mẫu dài hơn hai mươi kí tự.', 0.15),
               line('Một đoạn văn mẫu khác cũng dài hơn hai mươi kí tự.', 0.2), line('75', 0.95, x=0.9)]


class CoverTests(unittest.TestCase):
    def test_back_cover_is_end_matter_and_never_a_lesson(self):
        info = tc2_attach.page_info('00-sgk-mau', 122, n_pages=122, lines=BACK_COVER)
        self.assertEqual(info['kind'], 'back_cover')
        self.assertGreaterEqual(info['cover_marks'], tc2_attach.COVER_MIN_MARKS)

    def test_the_sgv_back_cover_of_the_same_series_is_also_a_cover(self):
        # measured: 7 of the 42 attached books are SGV and print «BỘ SÁCH GIÁO VIÊN» with no ISBN/barcode
        info = tc2_attach.page_info('00-sgv-mau', 290, n_pages=290, lines=BACK_COVER_SGV)
        self.assertEqual(info['kind'], 'back_cover')

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

    # ---- round-4 correctness review, F13: two marks of ORDINARY CONTENT ended the book -------------
    def test_a_price_line_and_a_website_line_are_not_a_cover(self):
        """`Giá:` is routine in a Toán word problem and `Website:` in an «Em có biết» box; two of them are
        not cover furniture. Before the fix this page was `back_cover` and ended the book."""
        lines = [line('Bài toán mẫu về mua bán hàng hoá trong cửa hàng.', 0.15),
                 line('Giá : 15 000 đồng một quyển vở mẫu.', 0.22),
                 line('Em có biết', 0.60), line('Website: https://vi.example.invalid', 0.66),
                 line('Một đoạn văn mẫu dài hơn hai mươi kí tự nữa.', 0.75), line('110', 0.95, x=0.9)]
        info = tc2_attach.page_info('00-sgk-mau', 112, n_pages=123, lines=lines)
        self.assertEqual(info['kind'], 'page')

    def test_a_medal_and_a_publisher_line_on_a_page_that_prints_a_lesson_banner_are_not_a_cover(self):
        """«HUÂN CHƯƠNG» is ordinary Lịch sử prose. A page that prints its own lesson banner is never a cover."""
        lines = [line('Bài 23', 0.07, h=0.03), line('TIÊU ĐỀ BÀI MẪU', 0.07, x=0.35, h=0.03),
                 line('Nhà nước đã trao tặng HUÂN CHƯƠNG cho tập thể mẫu.', 0.30),
                 line('Sách do NHÀ XUẤT BẢN GIÁO DỤC in và phát hành.', 0.40), line('118', 0.95, x=0.9)]
        info = tc2_attach.page_info('00-sgk-mau', 118, n_pages=123, lines=lines)
        self.assertEqual(info['kind'], 'page')
        self.assertEqual(info['header']['number'], 23)

    def test_a_tail_contents_page_carrying_cover_marks_is_matter_not_a_cover(self):
        # the cover test used to run BEFORE front/back/TOC classification, so a tail «MỤC LỤC» page with two
        # marks was reported `back_cover` — and ended the book
        lines = [line('MỤC LỤC', 0.06, h=0.03)] + \
                [line(f'Bài {n}. Tiêu đề mẫu {n} .......... {n * 4}', 0.12 + 0.03 * n) for n in range(1, 6)] + \
                [line('Website: https://example.invalid', 0.80), line('ISBN 978-0-00-000000-0', 0.86)]
        info = tc2_attach.page_info('00-sgk-mau', 120, n_pages=123, lines=lines)
        self.assertIn(info['kind'], ('front_matter', 'toc'))


class SyntheticBook:
    """A whole synthetic book on disk (OCR pages + curriculum structure) so `attach_book` can be run
    end to end. No SGK text (Founder D4): every string is generated.

    `printed = pdf - 2`; a page is a lesson page when `headers[pdf]` names a lesson number."""

    def __init__(self, n_pages, headers, toc, book='00-sgk-mau', extra=None):
        self.book = book
        self.dir = tempfile.mkdtemp(prefix='tc2-attach-test-')
        os.makedirs(os.path.join(self.dir, 'ocr', book))
        for p in range(1, n_pages + 1):
            lines = []
            if p in headers:
                lines += [line(f'Bài {headers[p]}', 0.07, h=0.03), line('TIÊU ĐỀ BÀI MẪU', 0.07, x=0.35, h=0.03)]
            lines += [line('Một đoạn văn mẫu dài hơn hai mươi kí tự.', 0.20),
                      line('Một đoạn văn mẫu khác cũng dài hơn hai mươi kí tự.', 0.30)]
            lines += (extra or {}).get(p, [])
            lines.append(line(str(p - 2), 0.95, x=0.9))
            with open(os.path.join(self.dir, 'ocr', book, f'p{p:03d}.json'), 'w', encoding='utf-8') as f:
                json.dump({'lines': lines}, f, ensure_ascii=False)
        curr = {'documents': [{'sourceDocumentId': book, 'docType': 'SGK', 'grade': 4, 'subject': 'Mẫu',
                               'lessonCount': max(toc) if toc else 0,
                               'lessons': [{'number': n, 'title': f'Tiêu đề mẫu {n}', 'pageStart': s} for n, s in sorted(toc.items())]}]}
        self.curr = os.path.join(self.dir, 'curriculum-structure.json')
        with open(self.curr, 'w', encoding='utf-8') as f:
            json.dump(curr, f, ensure_ascii=False)

    def attach(self):
        old_ocr, old_curr = tc2_attach.OCR, tc2_attach.CURR
        tc2_attach.OCR, tc2_attach.CURR = os.path.join(self.dir, 'ocr'), self.curr
        try:
            with warnings.catch_warnings():
                warnings.simplefilter('ignore', ResourceWarning)   # tc2_attach reads with a bare open()
                res = tc2_attach.attach_book(self.book, pipeline='tc2-test', write=False)
        finally:
            tc2_attach.OCR, tc2_attach.CURR = old_ocr, old_curr
        return {r['page']: r for r in res['pages']}, res

    def close(self):
        shutil.rmtree(self.dir, ignore_errors=True)


class BookTruncationTests(unittest.TestCase):
    """Round-4 correctness review, F13 — `back_cover` set `ended = True` for the rest of the book, so ONE
    false positive silently deleted the tail: every later page became `back_matter` with `lesson=None`."""

    TOC = {1: 1, 2: 5, 3: 9, 4: 13, 5: 17, 6: 21}
    HEADERS = {3: 1, 7: 2, 11: 3, 15: 4, 19: 5, 23: 6}
    FALSE_MARKS = [line('Giá : 15 000 đồng một quyển vở mẫu.', 0.45),
                   line('Website: https://vi.example.invalid', 0.55)]
    REAL_COVER = [line('BỘ SÁCH GIÁO KHOA LỚP 4 - MẪU', 0.56, h=0.023),
                  line('Website: https://example.invalid', 0.76),
                  line('ISBN 978-0-00-000000-0', 0.85)]

    def book(self, extra):
        return SyntheticBook(25, self.HEADERS, self.TOC, extra=extra)

    def test_ordinary_content_in_the_tail_does_not_delete_the_last_lesson(self):
        b = self.book({22: self.FALSE_MARKS})
        try:
            pages, _ = b.attach()
        finally:
            b.close()
        self.assertEqual(pages[22]['kind'], 'page')
        self.assertEqual(pages[22]['lesson'], 5)
        for p in (23, 24, 25):
            self.assertEqual(pages[p]['lesson'], 6, f'p{p} lost its lesson')
            self.assertEqual(pages[p]['kind'], 'page')

    def test_a_real_cover_ends_the_book_but_a_printed_lesson_banner_re_opens_it(self):
        """Truncation is never irreversible: the printed banner is this module's truth, so a lesson header
        after a cover verdict resumes the book instead of being deleted by it."""
        b = self.book({22: self.REAL_COVER})
        try:
            pages, _ = b.attach()
        finally:
            b.close()
        self.assertEqual(pages[22]['kind'], 'back_cover')
        self.assertIsNone(pages[22]['lesson'])
        self.assertEqual(pages[23]['lesson'], 6)
        self.assertTrue(pages[23].get('resumed_after_end'))
        self.assertEqual(pages[24]['lesson'], 6)

    def test_real_end_matter_stays_end_matter(self):
        """No lesson banner after the cover ⇒ nothing is resumed (the class-4 gain is kept)."""
        headers = {k: v for k, v in self.HEADERS.items() if k != 23}
        b = SyntheticBook(25, headers, {n: s for n, s in self.TOC.items() if n != 6}, extra={22: self.REAL_COVER})
        try:
            pages, _ = b.attach()
        finally:
            b.close()
        for p in (22, 23, 24, 25):
            self.assertIsNone(pages[p]['lesson'], f'p{p}')
            self.assertIn(pages[p]['kind'], ('back_cover', 'back_matter'))


class TocRangeFallbackTests(unittest.TestCase):
    """Round-4 correctness review, F14 — the «never skips more than 4 lessons» bound was applied to
    `max(due)`, so a legitimate `current+1` sitting next to a far outlier skipped the fallback entirely
    and the page silently kept the WRONG (previous) lesson."""

    HEADERS = {3: 1, 7: 2, 11: 3}          # Bài 4 starts on pdf 15 with no detectable banner

    def test_a_near_due_lesson_is_used_even_beside_a_far_outlier(self):
        toc = {1: 1, 2: 5, 3: 9, 4: 13, 30: 2}      # Bài 30's TOC start is an OCR misread, far too early
        b = SyntheticBook(20, self.HEADERS, toc)
        try:
            pages, _ = b.attach()
        finally:
            b.close()
        self.assertEqual(pages[15]['lesson'], 4)
        self.assertEqual(pages[15]['method'], 'toc_range')

    def test_a_far_outlier_alone_still_never_fires(self):
        toc = {1: 1, 2: 5, 3: 9, 30: 2}
        b = SyntheticBook(20, self.HEADERS, toc)
        try:
            pages, _ = b.attach()
        finally:
            b.close()
        self.assertEqual(pages[15]['lesson'], 3)
        self.assertEqual(pages[15]['method'], 'continuation')


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
