#!/usr/bin/env python3
"""LANE C (round 4) — tests for the PROPOSED History rules (tool/research/lane_c/history_rules.py).

Synthetic documents only («[MẪU]» strings) — no SGK text enters the repo (D4). The real Bài 8 document is
exercised in `test_real_document_if_present`, which skips on a clean clone.

Run:  python3 -m unittest tool/research/lane_c/test_history_rules.py -v
"""
import json
import os
import re
import sys
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import history_rules as hr  # noqa: E402
import make_history_synthetic_fixture as syn  # noqa: E402

REPO = os.path.abspath(os.path.join(HERE, '..', '..', '..'))
REAL = os.path.join(REPO, 'assets', 'fixtures', 'real', 'lesson-05-sgk-lich-su-va-dia-li-5-b8.json')


def para(bid, text, page=39, printed=37, trust='fixtureSynthetic', typ='paragraph', **kw):
    return {'id': bid, 'type': typ, 'text': text, 'trust': trust, 'sourceRef': {'book': 'b', 'pagePdf': page, 'pagePrinted': printed, 'bbox': [0.1, 0.1, 0.8, 0.05], 'blockId': bid}, **kw}


class EventsTest(unittest.TestCase):
    def test_enumerated_pairs_with_dash_forms_and_tcn(self):
        doc = {'blocks': [para('p1', '[MẪU] Sau khi X thôn tính nước Âu Lạc (179 TCN). Hai Bà Trưng (40 - 43), Bà Triệu (248), Lý Bí - Triệu Quang Phục (542 – 602). Chiến thắng của Ngô Quyền (938) đã kết thúc.')]}
        ev, mentions = hr.derive_events(doc)
        self.assertEqual([e['title'] for e in ev], ['Âu Lạc', 'Hai Bà Trưng', 'Bà Triệu', 'Lý Bí - Triệu Quang Phục', 'Ngô Quyền'])
        self.assertEqual([(e['yearStart'], e['yearEnd'], e['era']) for e in ev], [(179, 179, 'TCN'), (40, 43, 'CN'), (248, 248, 'CN'), (542, 602, 'CN'), (938, 938, 'CN')])
        self.assertEqual(ev[1]['when'], '40 - 43')                      # verbatim, dash not normalised
        self.assertEqual(ev[3]['when'], '542 – 602')
        self.assertTrue(ev[4]['text'].startswith('Chiến thắng của Ngô Quyền'))  # clause, not just the actor
        for e in ev:                                                      # char span points at the actor…(year)
            self.assertEqual(doc['blocks'][0]['text'][e['charSpan'][0]:e['charSpan'][1]].split('(')[0].strip(), e['title'])
        self.assertEqual(mentions, [])

    def test_narrative_years_are_counted_not_promoted(self):
        doc = {'blocks': [para('p1', '[MẪU] Mùa xuân năm 544, Lý Bí lên ngôi. Năm 937, sau khi …')]}
        ev, mentions = hr.derive_events(doc)
        self.assertEqual(ev, [])
        self.assertEqual([m['year'] for m in mentions], [544, 937])

    def test_no_actor_no_event(self):
        doc = {'blocks': [para('p1', '[MẪU] hơn 1 000 năm (1000) trôi qua.')]}      # lowercase run before the parenthesis
        self.assertEqual(hr.derive_events(doc)[0], [])

    def test_withheld_blocks_never_yield(self):
        doc = {'blocks': [{'id': 'w', 'type': 'withheld', 'trust': 'withheld', 'reasons': ['page_feature:color_heavy'], 'sourceRef': {'book': 'b', 'pagePdf': 38, 'bbox': [0, 0, 1, 1]}}]}
        self.assertEqual(hr.derive_events(doc)[0], [])


class AttributionTest(unittest.TestCase):
    def test_story_closed_by_theo_line_with_withheld_part(self):
        doc = {'blocks': [
            para('h', 'CHUYỆN MẪU', typ='heading'),
            {'id': 'w', 'type': 'withheld', 'trust': 'withheld', 'reasons': ['box_boundary'], 'sourceRef': {'book': 'b', 'pagePdf': 40, 'bbox': [0, 0, 1, 1]}},
            para('s2', '[MẪU] Đoạn hai.'),
            para('a', '(Theo Tác Giả Mẫu, Sách mẫu, NXB Mẫu, 2005)'),
            para('c', '[MẪU] Hình 2. Chú thích', typ='caption'),
        ]}
        at = hr.derive_attributions(doc)
        self.assertEqual(len(at), 1)
        a = at[0]
        self.assertEqual((a['form'], a['publisher'], a['year'], a['titleBlockId'], a['storyBlockIds'], a['withheldPartIds'], a['complete']),
                         ('theo', 'NXB Mẫu', 2005, 'h', ['s2'], ['w'], False))

    def test_quote_form_and_cross_page_story(self):
        doc = {'blocks': [
            para('h', 'CHUYỆN', typ='heading', page=40),
            para('s1', '[MẪU] Đoạn một.', page=40),
            {'id': 'img', 'type': 'image', 'trust': 'fixtureSynthetic', 'crop': 'x.png', 'sourceRef': {'book': 'b', 'pagePdf': 41, 'bbox': [0, 0, 1, 1]}},
            para('s2', '[MẪU] Đoạn hai, trang sau.', page=41),
            para('a', '(Tác Giả Mẫu, Bài thơ mẫu, NXB Mẫu Hai, 2018)', page=41),
        ]}
        a = hr.derive_attributions(doc)[0]
        self.assertEqual((a['form'], a['storyBlockIds'], a['publisher'], a['year'], a['complete']), ('quote', ['s1', 's2'], 'NXB Mẫu Hai', 2018, True))

    def test_plain_paragraph_is_not_an_attribution(self):
        doc = {'blocks': [para('p', '[MẪU] Theo sách, năm 2018 có nhiều chuyện.')]}
        self.assertEqual(hr.derive_attributions(doc), [])


class RegexPortabilityTest(unittest.TestCase):
    def test_rx_never_emits_identity_escapes(self):
        for s in ('40 - 43', 'Lý Bí - Triệu Quang Phục', 'a.b (c)', 'x/y'):
            p = hr._rx(s)
            self.assertNotIn('\\-', p); self.assertNotIn('\\ ', p)
            re.compile(p)
        self.assertTrue(re.fullmatch(hr._rx('40 - 43'), '40–43'.lower()))
        self.assertTrue(re.fullmatch(hr._rx('40 - 43'), '40 – 43'))


class ApplyTest(unittest.TestCase):
    def test_synthetic_fixture_end_to_end(self):
        import tempfile
        with tempfile.TemporaryDirectory() as d:
            p = syn.build(d)
            doc = json.load(open(p, encoding='utf-8'))
        tl = [s for s in doc['semantic'] if s['type'] == 'timeline'][0]
        self.assertEqual(tl['derivation'], hr.RULE_EVENTS)
        self.assertEqual(tl['trust'], 'fixtureSynthetic')
        self.assertEqual(len(tl['events']), 5)
        self.assertEqual(len(tl['sources']), 1)
        hrp = doc['provenance']['historyRules']
        self.assertEqual((hrp['events'], hrp['attributions'], hrp['attributionsComplete'], hrp['tutorSteps']), (5, 1, 1, 7))
        self.assertEqual(hrp['titleDerivation']['source'], 'toc')
        self.assertEqual(doc['title'], 'Đấu tranh mẫu thời kì mẫu (giả lập)')
        self.assertEqual(len(hrp['figureDependentQuestions']), 1)
        self.assertEqual(len(hrp['withheldQuestionsNotUsed']), 1)
        s = doc['tutorScript']
        self.assertEqual([x['id'] for x in s['steps']], ['e1', 'q1', 'q2', 'q3', 'e2', 'q4', 'n1'])
        for x in s['steps']:
            if x['type'] == 'ask':
                self.assertNotIn(x['promptBlockId'], hrp['figureDependentQuestions'])
                for h in x['hints']:
                    for pat in x['acceptable']:
                        self.assertIsNone(re.search(pat, h.lower(), re.I), (x['id'], h))
        # a second run gives the same bytes (deterministic)
        out2, _ = hr.apply(json.load(open(os.path.join(REPO, 'assets', 'fixtures', 'synthetic', 'lesson-05-sgk-lich-su-va-dia-li-5-b8.synthetic.json'), encoding='utf-8')))
        self.assertEqual(json.dumps(out2, sort_keys=True), json.dumps(out2, sort_keys=True))

    def test_fewer_than_three_events_no_script(self):
        doc = {'title': 'T', 'book': 'b', 'lesson': 1, 'blocks': [para('p1', '[MẪU] Nhân vật A (101), Nhân vật B (205).')], 'semantic': []}
        out, rep = hr.apply(doc)
        self.assertNotIn('tutorScript', out)
        self.assertEqual(len(out['semantic'][0]['events']), 2)

    def test_real_document_if_present(self):
        if not os.path.exists(REAL):
            self.skipTest('fixture thật chưa sinh trên máy này (poc-out)')
        doc = json.load(open(REAL, encoding='utf-8'))
        hrp = doc['provenance']['historyRules']
        self.assertEqual((hrp['events'], hrp['attributions'], hrp['attributionsComplete'], hrp['narrativeYearMentionsNotEvents']), (7, 3, 2, 2))
        tl = [s for s in doc['semantic'] if s['type'] == 'timeline'][0]
        self.assertEqual(len({e['sourceBlockId'] for e in tl['events']}), 1)
        self.assertEqual([e['yearStart'] for e in tl['events']], [40, 248, 542, 713, 766, 905, 938])
        self.assertEqual(doc['title'], 'Đấu tranh giành độc lập thời kì Bắc thuộc')


if __name__ == '__main__':
    unittest.main()
