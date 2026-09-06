#!/usr/bin/env python3
"""Phase B (WAL-215) — the question-promotion veto in `tc2_sdm.assign_role`.

Founder order 47 §PHASE B/C, on the root cause PHASE-A-ROOT-CAUSE-AUDIT.md §5 named: five of the
twelve teaching-critical errors are a NON-QUESTION SERVED AS A QUESTION, and all five survive both
counterfactuals (perfect recognition, perfect segmentation), so nothing upstream explains them.

Three rules, each of which refuses a QUESTION promotion the block's own structure contradicts:

  P1  the extractor's own `section_header` / `title` label is no longer discarded because the line
      ends in «?» — a question-form section title is a HEADING (ROLE-DEFINITION-SPEC-v1, QUESTION
      §exclusion), not a task.
  P2  a leading directive verb closed by a FULL STOP opens a remark, not a task.
  P3  `SIDEBAR_LABEL` matches the labels AS PRINTED; its vowel classes used to omit the tone-marked
      forms, so the pattern fired mainly where the OCR was wrong.

WHAT THESE TESTS ARE FOR. Every rule here is a NARROWING of a promotion, so the way it fails is by
being too wide: it can silently demote a real question and take a task away from a child. Each rule
therefore carries BOTH directions — the shape it must veto AND the neighbouring shape it must leave
alone. The negative cases are not decoration; two of them are shapes measured in the corpus
(«Nhận xét» as a directive verb governing an object is a real task, and an enumerated question the
extractor happened to label a section header is a real task).

Synthetic text only — every string below was written for this test, not taken from a book (D4).

Run:  python3 -m unittest discover -s tool/tests -v
"""
import os
import sys
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', 'corpus'))
import tc2_sdm  # noqa: E402


def block(text, native_label=None, bbox=(0.12, 0.30, 0.50, 0.03), colour=0.0, role='TEXT'):
    return dict(text=text, native_label=native_label, role=role,
                bbox=list(bbox), colour={'share': colour})


def role_of(text, native_label=None, ctx=None, **kw):
    return tc2_sdm.assign_role(block(text, native_label, **kw), ctx or {})[0]


class P1SectionHeaderVetoTests(unittest.TestCase):
    """The extractor's own structural label beats the question lexicon."""

    def test_a_question_form_section_title_is_a_heading(self):
        # The failing case. Before this rule the heading branch carried `not ends with "?"`, so the
        # label was thrown away and the block was served to a child as a task.
        self.assertEqual(role_of('Khi nào thì hai đại lượng này bằng nhau?', 'section_header'), 'heading')
        self.assertEqual(role_of('Bao nhiêu phần trăm là đủ?', 'title'), 'heading')

    def test_the_known_limit_a_title_opening_with_an_interrogative_the_lexicon_knows(self):
        # DELIBERATE and stated rather than hidden: «Vì sao …?» is in the question lexicon's opener
        # list, so a section title of that shape is NOT rescued. Widening the rule to cover it would
        # be a guess — no such row exists in the measured population — and it would put every
        # «Vì sao …?» prompt the extractor mislabels at risk. Recorded as a remaining gap.
        self.assertEqual(role_of('Vì sao lại có hiện tượng này?', 'title'), 'question')

    def test_the_label_alone_is_not_enough_an_enumerated_question_is_still_a_question(self):
        # An exercise item the extractor happened to label a section header stays a task.
        self.assertEqual(role_of('1. Nêu ba ví dụ về hiện tượng này?', 'section_header'), 'question')
        self.assertEqual(role_of('2. Tính chu vi của hình này?', 'title'), 'question')

    def test_a_title_that_opens_with_a_directive_verb_is_still_a_question(self):
        # A task set in display type is a task. This clause is what keeps the rule from swallowing
        # every prompt the extractor mislabels.
        self.assertEqual(role_of('Nêu đặc điểm của hiện tượng này?', 'section_header'), 'question')
        self.assertEqual(role_of('Hãy so sánh hai kết quả trên?', 'section_header'), 'question')

    def test_the_rule_changes_nothing_for_a_title_that_does_not_end_in_a_question_mark(self):
        self.assertEqual(role_of('Đặc điểm chung của nhóm này', 'section_header'), 'heading')
        self.assertEqual(role_of('Một dòng dài hơn một trăm ký tự thì không còn là tiêu đề mục nữa, '
                                 'vì nó đã là một đoạn văn xuôi thật sự rồi và cần được đọc như thế.',
                                 'section_header'), 'body')

    def test_a_block_with_no_structural_label_is_untouched(self):
        self.assertEqual(role_of('Khi nào thì hai đại lượng này bằng nhau?'), 'question')


class P2RemarkLeadInVetoTests(unittest.TestCase):
    """A leading directive verb closed by a full stop is a label, not an instruction."""

    def test_a_remark_marker_closed_by_a_full_stop_is_not_a_question(self):
        self.assertEqual(role_of('Nhận xét. Cách làm trên gồm hai bước rõ ràng.'), 'body')
        self.assertEqual(role_of('Quan sát. Hai kết quả trên khác nhau ở phần cuối.'), 'body')

    def test_the_same_verb_governing_an_object_is_still_a_question(self):
        # Measured in the corpus: «Nhận xét <object> …» is a real task. A veto keyed on the WORD
        # rather than on the stop would demote it, and this assertion is the reason the rule is
        # keyed on punctuation.
        self.assertEqual(role_of('Nhận xét đặc điểm của vật trong hai trường hợp trên.'), 'question')
        self.assertEqual(role_of('Quan sát hình bên và cho biết điều gì đã xảy ra.'), 'question')

    def test_a_block_that_actually_ends_in_a_question_mark_is_still_a_question(self):
        # `is_q` is deliberately outside the veto: however a line opens, if it asks, it asks.
        self.assertEqual(role_of('Nhận xét. Cách làm trên có đúng không?'), 'question')

    def test_the_veto_needs_the_stop_immediately_after_the_verb(self):
        self.assertEqual(role_of('Nhận xét ba cách làm. Sau đó ghi lại kết quả.'), 'question')


class P3SidebarLabelAsPrintedTests(unittest.TestCase):
    """The pattern has to match the label the book prints, not only the one the OCR breaks."""

    PRINTED = ('Em có biết', 'EM CÓ BIẾT', 'Em có thể', 'EM CÓ THỂ',
               'Ghi nhớ', 'GHI NHỚ', 'Lưu ý', 'Em đã học', 'EM ĐÃ HỌC')
    OCR_VARIANTS = ('Em có biêt', 'EM CÓ BIÊT', 'Em có the', 'EM CÓ THẾ')

    def test_every_correctly_printed_label_matches(self):
        for label in self.PRINTED:
            with self.subTest(label=label):
                self.assertIsNotNone(tc2_sdm.SIDEBAR_LABEL.match(label))

    def test_the_ocr_corrupted_forms_still_match(self):
        # The old pattern matched THESE and not the printed ones. Keeping them is what makes the
        # change a widening rather than a swap.
        for label in self.OCR_VARIANTS:
            with self.subTest(label=label):
                self.assertIsNotNone(tc2_sdm.SIDEBAR_LABEL.match(label))

    def test_it_does_not_match_prose_that_merely_begins_with_the_same_words(self):
        for text in ('Em có bao nhiêu quyển vở?', 'Em cố gắng hơn nhé.', 'Ghi lại kết quả vào vở.'):
            with self.subTest(text=text):
                self.assertIsNone(tc2_sdm.SIDEBAR_LABEL.match(text))

    def test_a_correctly_printed_label_now_opens_the_box_context(self):
        # This is where the miss actually cost content: `box_pass` collects its labels by
        # SIDEBAR_LABEL, so a label the pattern could not read left every block under it without a
        # box, and the question lexicon won inside a side box.
        label = dict(text='EM CÓ THỂ', bbox=[0.69, 0.53, 0.12, 0.02], colour={'share': 0.6},
                     role=dict(value='stage_label', coarse='HEADING', method='lexicon',
                               confidence=0.95, evidence=[]))
        inside = dict(text='1. Tự làm được một việc đơn giản trong đời sống.',
                      bbox=[0.69, 0.56, 0.22, 0.06], colour={'share': 0.6},
                      role=dict(value='question', coarse='QUESTION', method='lexicon',
                                confidence=0.78, evidence=[]))
        tc2_sdm.box_pass([label, inside], mask=None)
        self.assertEqual(inside['role']['value'], 'sidebar')
        self.assertEqual(inside['role']['method'], 'geometry+label')

    def test_the_box_does_not_reach_a_block_off_the_colour_or_off_the_column(self):
        label = dict(text='EM CÓ THỂ', bbox=[0.69, 0.53, 0.12, 0.02], colour={'share': 0.6},
                     role=dict(value='stage_label', coarse='HEADING', method='lexicon',
                               confidence=0.95, evidence=[]))
        white = dict(text='Một câu văn xuôi trong cột chính.', bbox=[0.69, 0.56, 0.22, 0.06],
                     colour={'share': 0.0},
                     role=dict(value='body', coarse='BODY', method='default', confidence=0.6, evidence=[]))
        far_left = dict(text='Một câu văn xuôi khác.', bbox=[0.08, 0.56, 0.22, 0.06],
                        colour={'share': 0.6},
                        role=dict(value='body', coarse='BODY', method='default', confidence=0.6, evidence=[]))
        tc2_sdm.box_pass([label, white, far_left], mask=None)
        self.assertEqual(white['role']['value'], 'body')
        self.assertEqual(far_left['role']['value'], 'body')


class VetoIsNarrowTests(unittest.TestCase):
    """The whole population of shapes this change may NOT touch."""

    UNTOUCHED = (
        ('Nêu ba đặc điểm của hiện tượng này.', None, 'question'),
        ('1. Tính diện tích của hình bên.', None, 'question'),
        ('Hình 5.4. Sơ đồ minh hoạ cho ví dụ trên', None, 'caption'),
        ('Bước 1. Chuẩn bị dụng cụ.', None, 'instruction'),
        ('Một đoạn văn xuôi bình thường của bài học, không hỏi và không sai khiến điều gì cả.',
         None, 'body'),
        ('A. Một phương án lựa chọn', None, 'option'),
    )

    def test_shapes_the_veto_must_not_reach(self):
        for text, lab, expected in self.UNTOUCHED:
            with self.subTest(text=text[:40]):
                self.assertEqual(role_of(text, lab), expected)

    def test_no_rule_promotes_anything_to_question(self):
        # All three rules are refusals. If any of them ever ADDS a question, the change has grown a
        # second job and this assertion is where that shows up.
        import inspect
        src = inspect.getsource(tc2_sdm.assign_role)
        head = src[:src.index('# questions')]
        self.assertNotIn("'question', 'lexicon'", head)


if __name__ == '__main__':
    unittest.main()
