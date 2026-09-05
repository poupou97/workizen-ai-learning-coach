#!/usr/bin/env python3
"""Round 5 · Lane A1 — regression cases from the Founder's 97-row audit, plus the STEM guard holes.

**These are regression cases, not a tuning set.** The Founder's rule is binding: measuring on the 97 rows is
allowed, tuning a rule so it happens to fix these strings is not. Every rule these cases exercise is
general (an unattested reading is not evidence; a double tone mark is illegal; a guard must name real
elements), and every one was re-measured on the 16-page held-out gold split - the numbers are in
`docs/research/VIETNAMESE-REPAIR-RESULT.md`.

Defects covered here:
  2 «Lý Thái Tổ → Lý Thái Tô»   Vietnamese tone, proper noun          (valid-syllable sub-class)
  3 «bản sắc → bán sắc»          Vietnamese tone, meaning inverted     (valid-syllable sub-class)
  4 «Cộng hoà → Cộng hoa»        Vietnamese tone                       (NOT repairable by layer A - asserted)
  5 «cây ổi → cây ỗi»            Vietnamese tone                       (invalid/unattested sub-class)
  7 «chem_guard blocks a Physics heading»                              (guard precision)
  8 «incomplete multiple choice because a sibling was withheld»        (group disposition)
  STEM §4 «a FORMULA label must not buy trust»
  STEM §2 «per-line geometry survives the flattening»

The Vietnamese cases need the corpus lexicon; they skip (loudly) when it has not been built.
"""
import os
import sys
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', 'corpus'))

import tc2_sdm  # noqa: E402
from repair import engine, groups, model  # noqa: E402
from repair.repairers import vi_text  # noqa: E402
from repair.vi import lexicon as vi_lexicon, syllable  # noqa: E402

LEX_DIR = os.environ.get('VI_LEXICON_DIR', vi_lexicon.DEFAULT_DIR)
HAVE_LEX = os.path.exists(os.path.join(LEX_DIR, 'corpus.json'))


class StubDocument:
    """The book around the block, as layer D sees it: which forms and which two-word sequences this book
    prints on other pages. A real `DocumentContext` computes these from the book's own OCR; the stub lets a
    regression case state the document evidence explicitly."""

    def __init__(self, tokens=(), bigrams=()):
        self._t = {t: n for t, n in tokens}
        self._b = {(a, b): n for a, b, n in bigrams}

    def token_pages(self, token, within_lesson=False):
        return self._t.get((token or '').lower(), 0)

    def bigram_pages(self, a, b, within_lesson=False):
        return self._b.get(((a or '').lower(), (b or '').lower()), 0)


def ctx(book='05-sgk-lich-su-va-dia-li-5', role='body', page_forms=None, document=None,
        disposition=model.Disposition.TRUSTED):
    lex = vi_lexicon.load() if HAVE_LEX else None
    return engine.RepairContext(
        block_id=f'{book}:p001:tc2-p2:000',
        observations=(model.Observation(f'{book}:p001:tc2-p2:000', 'docling-ocrmac', 'x'),),
        disposition=disposition, role=role,
        page=dict(book=book, page=1), document=document, lexicon=lex,
        extra=dict(page_forms=page_forms or {}))


@unittest.skipUnless(HAVE_LEX, f'Vietnamese lexicon not built at {LEX_DIR} '
                               f'(python3 tool/corpus/repair/vi/lexicon_build.py --out ...)')
class NamedToneDefects(unittest.TestCase):
    """Both OCR stacks agree on the wrong reading - the class round 4 could not close at all."""

    def _resolve(self, observed, left, right, **kw):
        c = ctx(**kw)
        return vi_text.resolve_token(observed, observed, left, right, c, vi_text.Config(), agreed=True,
                                     in_block={})[0]

    def test_defect5_cay_oi_an_unattested_reading_is_repaired(self):
        """«cây ỗi» - «ỗi» is attested on 0 of 62,729 pages, so the observed reading is not evidence of
        anything and the strict served-block bar does not apply."""
        self.assertEqual(vi_lexicon.load().unigram('ỗi').pages, 0)
        self.assertEqual(self._resolve('ỗi', 'cây', None), 'ổi')

    def test_defect2_ly_thai_to_is_repaired_when_the_book_agrees(self):
        """«Thái Tô» → «Thái Tổ»: both readings are legal, common Vietnamese words, so the corpus
        collocation alone is not allowed to rewrite a served block (thái·tổ 53 pages, thái·tô 0). The book
        itself must also print «Thái Tổ» - which a Lịch sử volume does - and then the repair validates."""
        lex = vi_lexicon.load()
        self.assertGreater(lex.bigram('thái', 'tổ').pages, 20)
        self.assertEqual(lex.bigram('thái', 'tô').pages, 0)
        doc = StubDocument(tokens=[('tổ', 6)], bigrams=[('thái', 'tổ', 4)])
        self.assertEqual(self._resolve('Tô', 'Thái', None, document=doc), 'Tổ')

    def test_defect2_is_NOT_repaired_when_only_the_corpus_says_so(self):
        """The same case with no in-document evidence must abstain: a word the corpus merely finds
        commoner is not a reason to rewrite what a page actually printed."""
        self.assertIsNone(self._resolve('Tô', 'Thái', None))

    def test_defect3_ban_sac_is_repaired_when_the_book_agrees(self):
        """«bán sắc» → «bản sắc» - the meaning is inverted, and the right-hand collocation is decisive
        (bản·sắc 301 pages, bán·sắc 0), confirmed by the book's own other pages."""
        doc = StubDocument(tokens=[('bản', 20)], bigrams=[('bản', 'sắc', 3)])
        self.assertEqual(self._resolve('bán', None, 'sắc', document=doc), 'bản')

    def test_defect4_cong_hoa_is_NOT_repaired_and_that_is_the_honest_answer(self):
        """«Cộng hoà» → «Cộng hoa» is **not** repairable by layer A, and the repairer must abstain rather
        than guess: the corpus itself carries the same slip (cộng·hoa 268 pages vs cộng·hoà 303), because
        the corpus IS this OCR. Reported as a limit, not tuned away."""
        lex = vi_lexicon.load()
        self.assertGreater(lex.bigram('cộng', 'hoa').pages, 100)
        self.assertIsNone(self._resolve('hoa', 'Cộng', None))

    def test_the_two_sub_classes_are_different_problems(self):
        """An illegal or unattested reading («ỗi», «thủỷ») is a different problem from a valid word in the
        wrong place («Tô», «bán»): the first is decided deterministically, the second only by context."""
        self.assertFalse(syllable.is_legal('thủỷ'))
        self.assertTrue(syllable.is_legal('bán'))
        self.assertTrue(syllable.is_legal('tô'))
        self.assertEqual(syllable.detone_variants('thủỷ'), ['thuỷ', 'thủy'])

    def test_a_repair_never_rewrites_a_word_into_a_different_word(self):
        self.assertEqual(syllable.edit_kind('phẫu', 'phễu'), 'quality')
        self.assertEqual(syllable.edit_kind('tiền', 'tiến'), 'tone')
        self.assertEqual(syllable.edit_kind('lọc', 'nước'), 'other')


class ChemGuardPrecision(unittest.TestCase):
    """Defect 7. On the 54 gold pages `chem_guard` fired 5 times and was wrong 5 times - «A4» (paper size),
    «B1» (a vitamin), «D0»/«S0»/«NA1» (map labels). The fix makes the mechanism discriminate; it does not
    switch it off."""

    def test_it_no_longer_fires_on_a_capital_next_to_a_digit(self):
        for t in ('kích thước A4', 'vitamin B1', 'KID DONAN1 D0/p 00002', 'C S0', 'BRU-NA1',
                  'BÀI 22. LỰC', 'tốc độ 3 x 108 m/s'):
            self.assertFalse(tc2_sdm.chem_like(t), t)

    def test_it_still_fires_on_a_flattened_chemical_formula(self):
        for t in ('khí CO2 trong không khí', 'H2O là nước', 'dung dịch NH3', 'O2 và N2',
                  'Fe2O3', 'CaCO3', 'Ca, 5 % khối lượng'):
            self.assertTrue(tc2_sdm.chem_like(t), t)

    def test_a_subscript_is_never_zero_or_one(self):
        self.assertFalse(tc2_sdm.chem_formula_like('B1'))
        self.assertFalse(tc2_sdm.chem_formula_like('S0'))
        self.assertTrue(tc2_sdm.chem_formula_like('CO2'))

    def test_every_letter_run_must_be_a_real_element(self):
        self.assertFalse(tc2_sdm.chem_formula_like('A4'))          # A is not an element
        self.assertTrue(tc2_sdm.chem_formula_like('CaCO3'))


class FormulaTrustHole(unittest.TestCase):
    """Founder STEM §4. Dormant today (Docling formula enrichment is off, FORMULA recall 0.000) - these
    tests exist so that switching it on cannot silently turn formula recognition into trusted content."""

    def test_a_formula_label_alone_does_not_buy_confidence(self):
        role, method, conf, ev = tc2_sdm.assign_role(
            dict(role='FORMULA', text='Tốc độ ánh sáng v = 1 5 + 1 2 = 7 10 trong chân không',
                 bbox=[0.1, 0.45, 0.6, 0.05], native_label='formula'),
            dict(prev_role=None, prev_text=None, box=None, docType='SGK'))
        self.assertEqual(role, 'formula')
        self.assertLess(conf, 0.95)
        self.assertIn('structure NOT validated: label only', ev)

    def test_an_unvalidated_formula_block_is_withheld(self):
        g = tc2_sdm.role_guards('formula', 'v = 1 5 + 1 2 = 7 10', False, None, {})
        self.assertIn('formula_unvalidated', g)
        self.assertEqual(tc2_sdm.trust_status('formula', [x for x in g]), 'WITHHELD')

    def test_a_formula_label_does_not_waive_the_math_unit_chem_guards(self):
        g = tc2_sdm.role_guards('formula', 'H2O và 1/5 giờ', False, None, {})
        self.assertIn('math_guard', g)
        self.assertIn('chem_guard', g)

    def test_the_exemption_is_earned_by_a_validated_structure_not_by_a_role_name(self):
        g = tc2_sdm.role_guards('formula', 'H2O', False, None, {}, formula_structured=True)
        self.assertNotIn('formula_unvalidated', g)
        self.assertNotIn('chem_guard', g)


class LineGeometrySurvives(unittest.TestCase):
    """Founder STEM §2: flat text may stay as a projection, but it may no longer be the only
    representation. Additive - no trust decision depends on these fields."""

    LINES = [dict(text='3/10 + 5/21', x=0.1, y=0.5, w=0.30, h=0.02, conf=1.0),
             dict(text='= 10⁸ m/s', x=0.1, y=0.53, w=0.24, h=0.02, conf=0.9)]

    def test_lines_keep_their_own_boxes_and_confidence(self):
        lg = tc2_sdm.line_geometry(self.LINES)
        self.assertEqual([l['text'] for l in lg], ['3/10 + 5/21', '= 10⁸ m/s'])
        self.assertEqual(lg[0]['bbox'], [0.1, 0.5, 0.3, 0.02])
        self.assertEqual(lg[1]['conf'], 0.9)

    def test_token_boxes_are_present_and_declared_estimated(self):
        toks = tc2_sdm.token_geometry(tc2_sdm.line_geometry(self.LINES))
        self.assertEqual([t['text'] for t in toks], ['3/10', '+', '5/21', '=', '10⁸', 'm/s'])
        self.assertTrue(all(t['estimated'] for t in toks))
        self.assertTrue(all(t['bbox'][2] > 0 for t in toks))
        # tokens are ordered left to right within their line, which is what a structured STEM model needs
        first_line = [t for t in toks if t['line'] == 0]
        self.assertEqual([t['bbox'][0] for t in first_line], sorted(t['bbox'][0] for t in first_line))


class ImprintPageIsEndMatter(unittest.TestCase):
    """Defect 6: «imprint / back matter → lesson heading» - end matter still leaking into a lesson after
    round 4's cover fix. Reproduced over the 42 attached books: **26 attach their imprint page to the
    book's last lesson**. The round-4 cover rule could not catch it because an imprint page carries exactly
    ONE cover mark (ISBN) and none of the three weak ones - «Website:», «Giá:», «HUÂN CHƯƠNG» are back-cover
    furniture, not colophon furniture."""

    IMPRINT = ['Chịu trách nhiệm xuất bản:', 'Tổng Giám đốc HOÀNG LÊ BÁCH',
               'Chịu trách nhiệm nội dung:', 'Biên tập viên: NGUYỄN VĂN A',
               'Trình bày bìa: TRẦN B', 'Chế bản: Công ty CP Dịch vụ xuất bản Giáo dục',
               'In 100 000 cuốn, khổ 19 x 26,5 cm', 'Số ĐKXB: 01-2023/CXBIPH/12-345/GD',
               'In xong và nộp lưu chiểu tháng 5 năm 2023', 'ISBN 978-604-0-12345-6']

    def _lines(self, texts, y0=0.1):
        return [dict(text=t, x=0.1, y=y0 + i * 0.03, w=0.6, h=0.02, conf=1.0)
                for i, t in enumerate(texts)]

    def test_an_imprint_page_in_the_tail_is_end_matter_not_a_lesson_page(self):
        import tc2_attach
        info = tc2_attach.page_info('bk', 125, n_pages=126, lines=self._lines(self.IMPRINT))
        self.assertEqual(info['kind'], 'imprint')
        self.assertGreaterEqual(info['imprint_marks'], 2)

    def test_one_imprint_phrase_alone_is_not_enough(self):
        import tc2_attach
        info = tc2_attach.page_info('bk', 125, n_pages=126,
                                    lines=self._lines(['Bản quyền thuộc về tác giả bài đọc',
                                                       'Một đoạn văn bình thường của bài học.']))
        self.assertNotEqual(info['kind'], 'imprint')

    def test_a_page_that_prints_its_own_lesson_banner_is_never_end_matter(self):
        import tc2_attach
        lines = [dict(text='BÀI 28. ÔN TẬP', x=0.1, y=0.06, w=0.6, h=0.05, conf=1.0)] + \
            self._lines(self.IMPRINT, y0=0.2)
        info = tc2_attach.page_info('bk', 125, n_pages=126, lines=lines)
        self.assertNotEqual(info['kind'], 'imprint')

    def test_in_the_first_pages_it_is_front_matter_and_ends_nothing(self):
        """A false positive at the front would delete the whole book, so the front case is front_matter -
        which the attach loop skips without setting `ended`."""
        import tc2_attach
        info = tc2_attach.page_info('bk', 2, n_pages=126, lines=self._lines(self.IMPRINT))
        self.assertEqual(info['kind'], 'front_matter')


class StructuralGroupDisposition(unittest.TestCase):
    """Defect 8: withholding one option leaves the served question WRONG, not merely smaller."""

    def _sdm(self):
        def b(order, role, text, bid):
            return dict(id=bid, order=order, role=dict(value=role, coarse=role.upper()), text=text,
                        trust=dict(status='TRUSTED', reasons=[]), learning=True, bbox=[0, 0, 1, 0.1])
        return dict(book='bk', page=7, figures=[], blocks=[
            b(0, 'question', 'Câu 1. Nước sôi ở nhiệt độ nào?', 'bk:p007:tc2:000'),
            b(1, 'option', 'A. 90 °C', 'bk:p007:tc2:001'),
            b(2, 'option', 'B. 100 °C', 'bk:p007:tc2:002'),
            b(3, 'body', 'Một đoạn văn không liên quan.', 'bk:p007:tc2:003'),
        ])

    def test_a_question_and_its_options_are_one_group(self):
        gs = groups.structural_groups(self._sdm())
        qo = [g for g in gs if g['kind'] == 'question_options']
        self.assertEqual(len(qo), 1)
        self.assertEqual(qo[0]['members'],
                         ['bk:p007:tc2:000', 'bk:p007:tc2:001', 'bk:p007:tc2:002'])

    def test_a_served_question_missing_an_option_is_reported_as_mutilated(self):
        gs = groups.structural_groups(self._sdm())
        servable = {'bk:p007:tc2:000': True, 'bk:p007:tc2:001': True, 'bk:p007:tc2:002': False,
                    'bk:p007:tc2:003': True}
        mut = groups.mutilated(gs, servable)
        self.assertEqual(len(mut), 1)
        self.assertEqual(mut[0]['kind'], 'question_options')
        self.assertEqual((mut[0]['served'], mut[0]['withheld']), (2, 1))

    def test_the_group_rule_withholds_the_whole_question_not_a_mutilated_one(self):
        gs = groups.structural_groups(self._sdm())
        servable = {'bk:p007:tc2:000': True, 'bk:p007:tc2:001': True, 'bk:p007:tc2:002': False,
                    'bk:p007:tc2:003': True}
        reasons = {}
        changed = groups.apply_group_rule(gs, servable, reasons)
        self.assertEqual(sorted(changed), ['bk:p007:tc2:000', 'bk:p007:tc2:001'])
        self.assertFalse(any(servable[m] for m in gs[0]['members']))
        self.assertTrue(servable['bk:p007:tc2:003'])          # an unrelated block is untouched
        self.assertEqual(reasons['bk:p007:tc2:000'], ['group_incomplete:question_options'])
        self.assertEqual(groups.mutilated(gs, servable), [])

    def test_a_whole_group_that_is_already_consistent_is_left_alone(self):
        gs = groups.structural_groups(self._sdm())
        servable = {m: True for g in gs for m in g['members']}
        self.assertEqual(groups.apply_group_rule(gs, servable, {}), {})


if __name__ == '__main__':
    unittest.main()
