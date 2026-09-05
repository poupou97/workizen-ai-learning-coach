#!/usr/bin/env python3
"""Round 4 · Lane A-pipeline — the cross-lane fixes Lane C asked for in
`docs/research/lane-c/05-GOLDEN-SLICE-2-GATE.md` §«Contradictions and requests»
(see docs/research/PIPELINE-ROUND4-FAILURE-CLASS-FIXES.md §6).

Each test names the request it locks in. Synthetic text only — no SGK text (Founder D4); the two
real-book strings that appear are the TOC banner words themselves, not lesson content.

Run:  python3 -m unittest discover -s tool/tests -v"""
import json
import os
import sys
import tempfile
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', 'corpus'))
import tc2_attach  # noqa: E402
import tc2_sdm  # noqa: E402
import tsl_to_lesson_document as br  # noqa: E402


class LessonHeaderToneTests(unittest.TestCase):
    """Request 2 — the banner OCRs «BÀI» as «BÃI» on 5 of 28 LS&ĐL 5 lessons; the class had no Ã."""

    def test_the_tilde_banner_is_a_lesson_header(self):
        for t in ('BÃI 7. TIÊU ĐỀ MẪU', 'BÀI 7. TIÊU ĐỀ MẪU', 'BẢI 7', 'Bãi 7', 'Bài 7'):
            m = tc2_attach.LESSON_HDR.match(t)
            self.assertIsNotNone(m, t)
            self.assertEqual(int(m.group(2)), 7, t)
        self.assertIsNotNone(tc2_attach.BAI_ALONE.match('BÃI'))

    def test_the_sdm_reads_the_same_banners(self):
        self.assertIsNotNone(tc2_sdm.LESSON_HDR.match('BÃI 12'))
        self.assertIsNone(tc2_sdm.LESSON_HDR.match('BÃO 12'))       # not a lesson banner

    def test_a_word_that_is_not_the_banner_is_not_a_header(self):
        for t in ('BAY 3', 'Bãi biển đẹp', 'BÃI'):
            self.assertIsNone(tc2_attach.LESSON_HDR.match(t), t)


class ColourHeavyBlockLevelTests(unittest.TestCase):
    """Request 3 — the page-level colour guard withheld 15/15 learning-text blocks of LS&ĐL 5 p038."""

    def test_white_column_text_on_a_colour_heavy_page_is_not_withheld(self):
        self.assertFalse(tc2_sdm.colour_heavy_withholds(True, 'body', dict(share=0.01)))
        self.assertFalse(tc2_sdm.colour_heavy_withholds(True, 'question', dict(share=0.24)))

    def test_a_block_printed_on_colour_is_still_withheld(self):
        self.assertTrue(tc2_sdm.colour_heavy_withholds(True, 'body', dict(share=0.25)))
        self.assertTrue(tc2_sdm.colour_heavy_withholds(True, 'body', dict(share=0.9)))

    def test_no_mask_fails_closed_and_a_plain_page_never_fires(self):
        self.assertTrue(tc2_sdm.colour_heavy_withholds(True, 'body', None))       # no PDF / no numpy
        self.assertFalse(tc2_sdm.colour_heavy_withholds(False, 'body', None))     # census never flagged the page
        self.assertFalse(tc2_sdm.colour_heavy_withholds(True, 'heading', dict(share=0.99)))   # exempt role


class AttributionRoleTests(unittest.TestCase):
    """Request 5 — «(Theo …)» and publisher lines were served as body (4 / 4 of Lane C's disagreements)."""

    def ctx(self, **kw):
        base = dict(prev_role=None, prev_text=None, box=None, docType='SGK', inside_picture=False,
                    xy_hint=None, big_digit=False, answer_section=False)
        base.update(kw)
        return base

    def blk(self, text, bbox=(0.12, 0.6, 0.5, 0.03)):
        return dict(text=text, role='TEXT', bbox=list(bbox), native_label=None, colour=None)

    def test_a_theo_line_is_an_attribution(self):
        for t in ('(Theo Tác giả Mẫu, Sách Mẫu, NXB Mẫu, 2017)', '(Nguồn: Tài liệu mẫu)', '(Phỏng theo Tác giả Mẫu)'):
            role, method, conf, ev = tc2_sdm.assign_role(self.blk(t), self.ctx())
            self.assertEqual(role, 'attribution', t)
        self.assertEqual(tc2_sdm.COARSE['attribution'], 'BODY')      # scored as BODY, exactly like the gold's own role
        self.assertEqual(br.ROLE_MAP['attribution'][0], 'paragraph')  # same LessonBlock type; only `sourceRole` differs

    def test_a_publisher_line_in_brackets_is_an_attribution(self):
        role, _, _, _ = tc2_sdm.assign_role(self.blk('(Sách Mẫu, NXB Mẫu, 2014)'), self.ctx())
        self.assertEqual(role, 'attribution')

    def test_prose_and_bare_names_stay_body(self):
        # fail closed: a parenthesised proper name alone is NOT promoted (Lane C's «(Hồ Chí Minh …)» — a recorded gap)
        for t in ('(Một Tên Riêng Mẫu, 1960)', 'Theo dòng thời gian, đất nước ta đã đổi thay rất nhiều so với trước.'):
            role, _, _, _ = tc2_sdm.assign_role(self.blk(t), self.ctx())
            self.assertEqual(role, 'body', t)


class DashSubQuestionTests(unittest.TestCase):
    """Request 5 — a «… em hãy:» lead and its dash sub-items were served as body."""

    def ctx(self, **kw):
        base = dict(prev_role=None, prev_text=None, box=None, docType='SGK', inside_picture=False,
                    xy_hint=None, big_digit=False, answer_section=False)
        base.update(kw)
        return base

    def blk(self, text):
        return dict(text=text, role='TEXT', bbox=[0.12, 0.6, 0.5, 0.03], native_label=None, colour=None)

    def test_a_lead_ending_in_hay_colon_is_a_question(self):
        role, _, _, ev = tc2_sdm.assign_role(self.blk('Dựa vào thông tin trong bài mẫu, em hãy:'), self.ctx())
        self.assertEqual(role, 'question')

    def test_a_dash_sub_item_under_a_lead_is_a_question(self):
        c = self.ctx(prev_role='question', prev_text='Dựa vào thông tin trong bài mẫu, em hãy:')
        role, _, _, ev = tc2_sdm.assign_role(self.blk('– Nêu một vài chi tiết của ví dụ mẫu.'), c)
        self.assertEqual(role, 'question')
        self.assertIn('dash sub-item under a question lead', ev)

    def test_a_dash_line_without_a_lead_is_not_promoted(self):
        # dialogue in a reading: the same shape, no question lead above it → body, as before
        c = self.ctx(prev_role='body', prev_text='Một đoạn văn mẫu kể chuyện.')
        role, _, _, _ = tc2_sdm.assign_role(self.blk('– Nêu chuyện cho tôi nghe đi.'), c)
        self.assertEqual(role, 'body')


class FigureDependentPhrasingTests(unittest.TestCase):
    """Request 4 — «quan sát các hình từ 1 đến 3» carries no «Hình N», so the guard trusted it."""

    def test_look_verb_plus_figure_noun_without_a_number_is_a_figure_reference(self):
        for t in ('Quan sát các hình từ 1 đến 3 và cho biết điều gì đã xảy ra?',
                  'Dựa vào lược đồ, em hãy mô tả lại diễn biến.',
                  'Đọc thông tin và quan sát hình, hãy kể lại câu chuyện.'):
            self.assertIsNotNone(tc2_sdm.FIG_REF.search(t), t)

    def test_a_numbered_reference_still_matches_and_plain_prose_does_not(self):
        self.assertIsNotNone(tc2_sdm.FIG_REF.search('Xem Hình 2 để biết thêm.'))
        self.assertIsNone(tc2_sdm.FIG_REF.search('Quan sát bầu trời vào buổi sáng sớm.'))


class ChapterChuDeTests(unittest.TestCase):
    """Request 6 — `toc-ocr-chapters-v1` knew only «CHƯƠNG <roman>» ⇒ 0 chapters for «Chủ đề» books."""

    TOC_CHU_DE = ('MỤC LỤC TRANG LỜI NÓI ĐẦU .. 3 '
                  'CHỦ ĐỀ 1. TIÊU ĐỀ CHỦ ĐỀ MỘT ..... ... 5 Bài 1. Tiêu đề mẫu một 5 Bài 2. Tiêu đề mẫu hai 9 '
                  'CHỦ ĐẾ 2. TIÊU ĐỀ CHỦ ĐỀ HAI .25 Bài 3. Tiêu đề mẫu ba 25 ')
    TOC_CHUONG = ('MỤC LỤC Hướng dẫn sử dụng sách 2 '
                  'CHƯƠNG I - TIÊU ĐỀ CHƯƠNG MỘT Bài 1. Tiêu đề mẫu một 7 Bài 2. Tiêu đề mẫu hai 11 '
                  'CHƯƠNG II - TIÊU ĐỀ CHƯƠNG HAI Bài 3. Tiêu đề mẫu ba 28 ')

    def chapters(self, toc_text):
        with tempfile.TemporaryDirectory() as d:
            p = os.path.join(d, 'u.json')
            with open(p, 'w', encoding='utf-8') as f:
                json.dump({'units': [{'text': toc_text}]}, f, ensure_ascii=False)
            return br.chapters_from_toc('00-sgk-mau', units_path=p)

    def test_chu_de_books_now_report_chapters(self):
        ch = self.chapters(self.TOC_CHU_DE)
        self.assertEqual([c['label'] for c in ch], ['Chủ đề 1', 'Chủ đề 2'])
        self.assertEqual([c['lessonNos'] for c in ch], [[1, 2], [3]])
        self.assertEqual(ch[0]['title'], 'TIÊU ĐỀ CHỦ ĐỀ MỘT')      # dot leaders and the page number stripped
        self.assertEqual(ch[0]['derivation'], 'toc-ocr-chapters-v2')

    def test_the_tone_slipped_banner_is_still_a_chapter(self):
        # LS&ĐL 5's own TOC prints «CHỦ ĐẾ 6» — the same display-font slip as «BÃI»
        self.assertEqual(self.chapters(self.TOC_CHU_DE)[1]['label'], 'Chủ đề 2')

    def test_a_single_dot_leader_glued_to_the_page_number_is_still_stripped(self):
        # LS&ĐL 5 prints «CHỦ ĐỀ 5. TÌM HIỂU THẾ GIỚI .93 Bài 22.» — the page number must not enter the title
        self.assertEqual(self.chapters(self.TOC_CHU_DE)[1]['title'], 'TIÊU ĐỀ CHỦ ĐỀ HAI')

    def test_chuong_books_are_unchanged(self):
        ch = self.chapters(self.TOC_CHUONG)
        self.assertEqual([c['label'] for c in ch], ['Chương I', 'Chương II'])
        self.assertEqual([c['title'] for c in ch], ['TIÊU ĐỀ CHƯƠNG MỘT', 'TIÊU ĐỀ CHƯƠNG HAI'])
        self.assertEqual([c['lessonNos'] for c in ch], [[1, 2], [3]])

    def test_no_toc_means_no_chapters(self):
        self.assertEqual(self.chapters('không có mục lục ở đây'), [])


class GoldErrataTests(unittest.TestCase):
    """Request 1 — the gold's lesson numbers on LS&ĐL 5 p041 and p080 contradicted the printed banners.

    Lane C's second reviewer and this lane's own banner scan of all 123 pages agree with the pipeline:
    «BÀI 8» is printed on PDF 38 and «BÀI 9» on PDF 42, so PDF 41 is Bài 8; «BÀI 18» on PDF 78 and
    «BÀI 19» on PDF 84, so PDF 80 is Bài 18. The gold's own titles were already the right lessons'.
    The correction is recorded in the file, never silent."""

    GOLD = os.path.join(HERE, '..', 'corpus', 'tc_gold')

    def gold(self, name):
        with open(os.path.join(self.GOLD, name), encoding='utf-8') as f:
            return json.load(f)

    def test_the_corrected_numbers_carry_their_errata(self):
        for name, number, was in (('05-sgk-lich-su-va-dia-li-5-p041.json', 8, 9),
                                  ('05-sgk-lich-su-va-dia-li-5-p080.json', 18, 17)):
            les = self.gold(name)['lesson']
            self.assertEqual(les['number'], number, name)
            err = les.get('errata')
            self.assertIsNotNone(err, name)
            self.assertEqual(err['was']['number'], was, name)
            self.assertEqual(err['now']['number'], number, name)
            for k in ('id', 'date', 'reportedBy', 'verifiedBy', 'why', 'effect'):
                self.assertTrue(err.get(k), f'{name}: errata.{k}')


if __name__ == '__main__':
    unittest.main()
