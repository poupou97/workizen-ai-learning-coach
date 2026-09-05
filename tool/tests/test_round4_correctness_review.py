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


def ctx(**kw):
    base = dict(prev_role=None, prev_text=None, box=None, docType='SGK', inside_picture=False,
                xy_hint=None, big_digit=False, answer_section=False)
    base.update(kw)
    return base


def blk(text, bbox=(0.12, 0.6, 0.5, 0.03), native_label=None):
    return dict(text=text, role='TEXT', bbox=list(bbox), native_label=native_label, colour=None)


class F2UppercaseAttributionTests(unittest.TestCase):
    """F2 — the `attribution` role was unreachable for an UPPERCASE line: the two `upper_ratio >= 0.7`
    heading rules run far earlier. The fallback is worse than «body»: `heading` is COLOUR_HEAVY_EXEMPT and
    then becomes the `heading_path` of every following block in the lesson."""

    def test_an_uppercase_attribution_is_an_attribution_not_a_heading(self):
        for t in ('(THEO TÁC GIẢ MẪU)', '(NGUỒN: CƠ QUAN MẪU)', '(DẪN THEO TÀI LIỆU MẪU)',
                  '(SÁCH MẪU, NXB MẪU, 2014)'):
            role, _, _, _ = tc2_sdm.assign_role(blk(t), ctx())
            self.assertEqual(role, 'attribution', t)

    def test_the_title_case_form_still_works(self):
        for t in ('(Theo Tác giả Mẫu, Sách Mẫu, NXB Mẫu, 2017)', '(Nguồn: Tài liệu mẫu)'):
            self.assertEqual(tc2_sdm.assign_role(blk(t), ctx())[0], 'attribution', t)

    def test_an_attribution_never_becomes_a_heading_path(self):
        # `heading_path` is only extended for role == 'heading', so keeping the line out of `heading`
        # is what keeps it out of every following block's heading path
        import inspect
        src = inspect.getsource(tc2_sdm.build_page)
        self.assertIn("if role == 'heading':", src)
        self.assertNotIn('attribution', src.split('# heading path')[1].split('# guards')[0])

    def test_a_docling_caption_keeps_its_caption_role(self):
        role, _, _, _ = tc2_sdm.assign_role(blk('(Theo Tác giả Mẫu)', native_label='caption'), ctx())
        self.assertEqual(role, 'caption')

    def test_in_an_sgv_the_line_stays_teacher_text_and_withheld(self):
        role, _, _, _ = tc2_sdm.assign_role(blk('(THEO TÁC GIẢ MẪU)'), ctx(docType='SGV'))
        self.assertEqual(role, 'teacher_text')

    def test_a_line_that_opens_like_an_attribution_but_asks_a_question_is_still_a_question(self):
        # moving the test earlier must not take a question away from the question rules
        role, _, _, _ = tc2_sdm.assign_role(blk('(Theo em) vì sao mẫu vật lại thay đổi?'), ctx())
        self.assertEqual(role, 'question')

    def test_prose_and_bare_names_still_stay_body(self):
        for t in ('(MỘT TÊN RIÊNG MẪU, 1960)', 'Theo dòng thời gian, mọi thứ đều đổi thay rất nhiều.'):
            self.assertEqual(tc2_sdm.assign_role(blk(t), ctx())[0], 'body', t)


def cap_block(i, bbox, text='Hình 1. Mẫu'):
    return dict(id=f'b:{i:03d}', bbox=list(bbox), text=text,
                role=dict(value='caption', coarse='CAPTION', method='lexicon', confidence=0.9, evidence=[]))


class F1CaptionDeadZoneTests(unittest.TestCase):
    """F1 — a caption whose TOP is still inside the picture but whose CENTRE has crossed below its bottom
    edge matched none of inside / below / above and silently lost its link — exactly the «Docling grew the
    picture over its caption» case the docstring claims to handle."""

    PIC = [0.1, 0.3, 0.4, 0.24]        # bottom edge at y = 0.54
    MED = 0.015

    def link(self, centre_y, h=0.02):
        c = cap_block(1, [0.15, round(centre_y - h / 2, 4), 0.3, h])
        return tc2_sdm.caption_for_picture(self.PIC, [c], self.MED)

    def test_the_dead_zone_straddling_the_bottom_edge_is_linked(self):
        # measured before the fix: 0.540 and 0.550 linked, 0.545 did not
        for centre in (0.535, 0.540, 0.545, 0.550, 0.560):
            self.assertEqual(self.link(centre), 'b:001', centre)

    def test_a_caption_straddling_the_top_edge_is_linked(self):
        # centre 0.295 (above the box, which starts at 0.30) but its bottom edge 0.305 is inside it —
        # the mirror image of the dead zone, and equally unmatched before the fix
        c = cap_block(1, [0.15, 0.285, 0.3, 0.02])
        self.assertEqual(tc2_sdm.caption_for_picture(self.PIC, [c], self.MED), 'b:001')

    def test_a_caption_whose_centre_sits_high_inside_the_picture_is_still_figure_text(self):
        c = cap_block(1, [0.15, 0.30, 0.3, 0.02])       # centre 0.31, well above the picture's lower band
        self.assertIsNone(tc2_sdm.caption_for_picture(self.PIC, [c], self.MED))

    def test_the_distance_limits_are_unchanged(self):
        self.assertIsNone(self.link(0.60))                       # far below (> 2.5 median line heights)
        c = cap_block(1, [0.15, 0.20, 0.3, 0.015])               # far above (> 1 median line height)
        self.assertIsNone(tc2_sdm.caption_for_picture(self.PIC, [c], self.MED))
        beside = cap_block(1, [0.6, 0.35, 0.3, 0.015])           # no horizontal overlap
        self.assertIsNone(tc2_sdm.caption_for_picture(self.PIC, [beside], self.MED))


class F5DashSubItemEnumeratorTests(unittest.TestCase):
    """F5 — `num_directive` was computed with `ENUM.match(t)` on the UN-stripped text while `core` was
    dash-stripped, so a dash sub-item carrying its OWN enumerator could only be promoted through the
    `^`-anchored QHINT and never through DIRECTIVE_ANY."""

    def test_a_dash_item_with_its_own_enumerator_is_a_question(self):
        c = ctx(prev_role='body', prev_text='Một đoạn văn mẫu.')
        for t in ('– 1. Em thử vẽ lại sơ đồ mẫu ở trên', '- 2. Em thử so sánh hai mẫu vật ở trên'):
            role, _, _, _ = tc2_sdm.assign_role(blk(t), c)
            self.assertEqual(role, 'question', t)

    def test_a_bare_dash_line_without_a_lead_is_still_body(self):
        # the fail-closed rule the dash machinery exists for: dialogue in a reading is NOT a question
        c = ctx(prev_role='body', prev_text='Một đoạn văn mẫu kể chuyện.')
        for t in ('– Em thử vẽ lại sơ đồ mẫu ở trên', '– Nêu chuyện cho tôi nghe đi.'):
            self.assertEqual(tc2_sdm.assign_role(blk(t), c)[0], 'body', t)

    def test_an_undashed_enumerated_directive_is_unchanged(self):
        c = ctx(prev_role='body', prev_text='Một đoạn văn mẫu.')
        self.assertEqual(tc2_sdm.assign_role(blk('1. Em thử vẽ lại sơ đồ mẫu ở trên'), c)[0], 'question')


class F4FigRefOverMatchTests(unittest.TestCase):
    """F4 — the look-verb clause matched «đọc/xem … bảng» where «bảng» is an arithmetic table the child
    recites, not a printed figure. Fail-closed, so it costs recall, not trust — tightened narrowly."""

    def test_an_arithmetic_table_is_not_a_figure_reference(self):
        for t in ('Đọc bảng chia 3 và học thuộc bảng chia đó.', 'Đọc bảng nhân 5.',
                  'Học thuộc và đọc bảng cộng trong phạm vi 10.'):
            self.assertIsNone(tc2_sdm.FIG_REF.search(t), t)

    def test_lane_c_request_4_still_matches(self):
        for t in ('Quan sát các hình từ 1 đến 3 và cho biết điều gì đã xảy ra?',
                  'Dựa vào lược đồ, em hãy mô tả lại diễn biến.',
                  'Đọc thông tin và quan sát hình, hãy kể lại câu chuyện.',
                  'Xem Hình 2 để biết thêm.',
                  'Đọc bảng số liệu mẫu rồi nhận xét.',
                  'Xem bảng bên dưới rồi trả lời.'):
            self.assertIsNotNone(tc2_sdm.FIG_REF.search(t), t)

    def test_plain_prose_still_does_not_match(self):
        self.assertIsNone(tc2_sdm.FIG_REF.search('Quan sát bầu trời vào buổi sáng sớm.'))


class F3RoleChangeReDerivesGuardsTests(unittest.TestCase):
    """F3 — the post-pass re-derivation recomputed only `figure_dependent`, `answer_leak` and
    `teacher_text`, so a block promoted INTO a colour-heavy-exempt role kept a guard reason its new role
    is exempt from: a «Hình 17.1» label was TRUSTED while its continuation sentence, now also `caption`,
    stayed WITHHELD citing `page_feature:color_heavy`."""

    def ob(self, role, text, guards, colour=0.6):
        return dict(id='b:001', text=text, colour=dict(share=colour), refers_figure=False,
                    role=dict(value=role, coarse=tc2_sdm.COARSE[role], method='x', confidence=0.7, evidence=[]),
                    guards=list(guards), trust=dict(status='WITHHELD', reasons=list(guards)), learning=True)

    def test_a_promotion_into_an_exempt_role_drops_the_colour_guard(self):
        o = self.ob('caption', 'Một chú thích mẫu', ['page_feature:color_heavy'])   # role already promoted
        tc2_sdm.rederive_trust([o], dict(color_heavy=True, diagram=False))
        self.assertEqual(o['guards'], [])
        self.assertEqual(o['trust']['status'], 'TRUSTED')

    def test_a_block_that_is_still_body_keeps_the_colour_guard(self):
        o = self.ob('body', 'Một đoạn văn mẫu', ['page_feature:color_heavy'])
        tc2_sdm.rederive_trust([o], dict(color_heavy=True, diagram=False))
        self.assertEqual(o['guards'], ['page_feature:color_heavy'])
        self.assertEqual(o['trust']['status'], 'WITHHELD')

    def test_the_diagram_guard_is_re_derived_too(self):
        o = self.ob('caption', 'Chú thích ngắn', ['page_feature:diagram'])
        tc2_sdm.rederive_trust([o], dict(color_heavy=False, diagram=True), {'b:001': True})
        self.assertNotIn('page_feature:diagram', o['guards'])
        o2 = self.ob('body', 'Chú thích ngắn', ['page_feature:diagram'])
        tc2_sdm.rederive_trust([o2], dict(color_heavy=False, diagram=True), {'b:001': True})
        self.assertIn('page_feature:diagram', o2['guards'])

    def test_guards_that_do_not_depend_on_the_role_are_never_dropped(self):
        o = self.ob('caption', 'Một chú thích mẫu', ['agree_tones', 'page_feature:color_heavy', 'low_ocr_conf'])
        tc2_sdm.rederive_trust([o], dict(color_heavy=True, diagram=False))
        self.assertEqual(sorted(o['guards']), ['agree_tones', 'low_ocr_conf'])
        self.assertEqual(o['trust']['status'], 'WITHHELD')

    def test_a_chemistry_guard_follows_the_role_it_was_derived_for(self):
        o = self.ob('body', 'khí CO2 và H2O', [])
        tc2_sdm.rederive_trust([o], dict(color_heavy=False, diagram=False))
        self.assertIn('chem_guard', o['guards'])
        o2 = self.ob('table', 'khí CO2 và H2O', ['chem_guard'])
        tc2_sdm.rederive_trust([o2], dict(color_heavy=False, diagram=False))
        self.assertNotIn('chem_guard', o2['guards'])


class F10SharedCaptionTests(unittest.TestCase):
    """F10 — `caption_for_picture` deliberately lets ONE caption serve side-by-side pictures, but the
    bridge built `caption_of` keyed by caption id, so the second figure overwrote the first."""

    BOOK = '06-sgk-mau-6'

    def tsl(self, figs):
        cap_id = f'{self.BOOK}:p011:tc2-p1:009'
        blocks = [{'id': cap_id, 'page': 11, 'page_printed': 10, 'order': 9,
                   'role': {'value': 'caption', 'coarse': 'CAPTION', 'confidence': 0.9, 'method': 'lexicon'},
                   'text': '[MẪU] Chú thích chung', 'bbox': [0.1, 0.5, 0.7, 0.02], 'heading_path': [],
                   'refers_figure': False, 'enumerator_restored': False}]
        return cap_id, {'book': self.BOOK, 'lesson': 9, 'title': '[MẪU]', 'pipeline': 'tc2-p1', 'docType': 'SGK',
                        'boundary': {'pages': [11]}, 'sourceability': 'PARTIAL', 'answer_keys_included': False,
                        'blocks': blocks, 'withheld': [], 'figures': figs}

    def figure(self, n, bbox):
        return {'id': f'{self.BOOK}:p011:fig{n:02d}', 'page': 11, 'bbox': list(bbox),
                'caption': f'{self.BOOK}:p011:tc2-p1:009', 'labels': 0}

    def test_both_side_by_side_figures_keep_the_shared_caption(self):
        left, right = self.figure(0, [0.1, 0.3, 0.35, 0.18]), self.figure(1, [0.5, 0.3, 0.35, 0.18])
        cap_id, tsl = self.tsl([left, right])
        crops = {left['id']: {'crop': 'crops/a.png', 'aspect': 1.4}, right['id']: {'crop': 'crops/b.png', 'aspect': 1.4}}
        doc = br.convert(tsl, tsl_rel_path='x.json', tsl_sha256='ab' * 32, crops=crops)
        images = [b for b in doc['blocks'] if b['type'] == 'image']
        self.assertEqual(len(images), 2)
        for im in images:
            self.assertEqual(im['captionBlockId'], cap_id)
        caption = next(b for b in doc['blocks'] if b['id'] == cap_id)
        # `captionOf` is a single id in the consumer model, so it names the FIRST figure deterministically
        self.assertEqual(caption['relations']['captionOf'], left['id'])

    def test_caption_of_never_names_a_figure_the_document_dropped(self):
        tiny, kept = self.figure(0, [0.1, 0.3, 0.02, 0.02]), self.figure(1, [0.5, 0.3, 0.35, 0.18])
        cap_id, tsl = self.tsl([tiny, kept])
        doc = br.convert(tsl, tsl_rel_path='x.json', tsl_sha256='ab' * 32,
                         crops={kept['id']: {'crop': 'crops/b.png', 'aspect': 1.4}})
        caption = next(b for b in doc['blocks'] if b['id'] == cap_id)
        self.assertEqual(caption['relations']['captionOf'], kept['id'])


def ocr_line(text, y, x=0.15, w=0.30, h=0.015):
    return dict(text=text, x=x, y=y, w=w, h=h)


class R7cVerseLayoutTests(unittest.TestCase):
    """R7c (Lane D, measured on their legacy batch-1 re-run) — the block-level colour fix served a poem
    again, and the poem's verse lines arrive JOINED into one prose paragraph, because a block's text is one
    string. Line-break-significant text is withheld rather than delivered mangled (fail closed): the
    withheld region still carries its crop, so the printed verse survives as an image."""

    COL = 0.62      # the page's text width

    def page(self, widths):
        return [ocr_line('x' * 40, 0.2, w=self.COL) for _ in range(6)] + \
               [ocr_line('y' * 40, 0.5, w=w) for w in widths]

    def verse(self):
        return [ocr_line('Tôi đạp vỡ màu nâu', 0.50, w=0.22),
                ocr_line('Bầu trời trong quả trứng', 0.53, w=0.26),
                ocr_line('Bỗng thấy nhiều gió lộng', 0.56, w=0.27),
                ocr_line('Bỗng thấy nhiều nắng reo', 0.59, w=0.27)]

    def prose(self):
        return [ocr_line('Công cuộc đấu tranh chống ngoại xâm của Nhà nước mẫu và Nhà', 0.50, w=self.COL),
                ocr_line('Âu Lạc còn được phản ánh sinh động qua một số truyền thuyết', 0.53, w=self.COL),
                ocr_line('Thánh Gióng, Sự tích nỏ thần,...', 0.56, w=0.31)]

    def test_verse_lines_are_recognised(self):
        self.assertTrue(tc2_sdm.verse_layout(self.verse(), self.COL))

    def test_justified_prose_is_not_verse(self):
        self.assertFalse(tc2_sdm.verse_layout(self.prose(), self.COL))

    def test_sentences_on_their_own_lines_are_not_verse(self):
        # «AH vuông góc với DC. / AH là đường cao. / Độ dài AH là chiều cao.» — maths prose, not verse
        lines = [ocr_line('Đoạn AB vuông góc với CD.', 0.50, w=0.22),
                 ocr_line('Đoạn AB là đường cao.', 0.53, w=0.20),
                 ocr_line('Độ dài AB là chiều cao mẫu.', 0.56, w=0.24)]
        self.assertFalse(tc2_sdm.verse_layout(lines, self.COL))

    def test_two_lines_or_lowercase_starts_are_not_verse(self):
        self.assertFalse(tc2_sdm.verse_layout(self.verse()[:2], self.COL))
        low = [dict(l, text=l['text'].lower()) for l in self.verse()]
        self.assertFalse(tc2_sdm.verse_layout(low, self.COL))

    def test_no_page_width_fails_open_not_closed(self):
        # unknown geometry must not withhold everything
        self.assertFalse(tc2_sdm.verse_layout(self.verse(), None))

    def test_the_guard_withholds_prose_roles_and_spares_typographic_ones(self):
        self.assertIn('line_structure', tc2_sdm.role_guards('body', 'Một dòng mẫu', False, None, {}, verse=True))
        self.assertIn('line_structure', tc2_sdm.role_guards('sidebar', 'Một dòng mẫu', False, None, {}, verse=True))
        for role in ('heading', 'stage_label', 'page_number', 'figure_text'):
            self.assertNotIn('line_structure', tc2_sdm.role_guards(role, 'Một dòng mẫu', False, None, {}, verse=True), role)
        self.assertNotIn('line_structure', tc2_sdm.role_guards('body', 'Một dòng mẫu', False, None, {}, verse=False))

    def test_the_guard_survives_a_role_change_and_nothing_is_rewritten(self):
        o = dict(id='b:001', text='Tôi đạp vỡ màu nâu Bầu trời trong quả trứng', colour=None, refers_figure=False,
                 role=dict(value='body', coarse='BODY', method='x', confidence=0.7, evidence=[]),
                 guards=['line_structure'], trust=dict(status='WITHHELD', reasons=['line_structure']), learning=True)
        before = o['text']
        tc2_sdm.rederive_trust([o], {}, verse_by_id={'b:001': True})
        self.assertEqual(o['trust']['status'], 'WITHHELD')
        self.assertEqual(o['guards'], ['line_structure'])
        self.assertEqual(o['text'], before)        # withheld, never reflowed and never repaired


if __name__ == '__main__':
    unittest.main()
