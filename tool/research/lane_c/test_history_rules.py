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
        ev, mentions, held = hr.derive_events(doc)
        self.assertEqual(held, [])
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
        ev, mentions, _ = hr.derive_events(doc)
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
        at, held = hr.derive_attributions(doc)
        self.assertEqual(held, [])
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
        a = hr.derive_attributions(doc)[0][0]
        self.assertEqual((a['form'], a['storyBlockIds'], a['publisher'], a['year'], a['complete']), ('quote', ['s1', 's2'], 'NXB Mẫu Hai', 2018, True))

    def test_plain_paragraph_is_not_an_attribution(self):
        doc = {'blocks': [para('p', '[MẪU] Theo sách, năm 2018 có nhiều chuyện.')]}
        self.assertEqual(hr.derive_attributions(doc)[0], [])


def ledger(*entries):
    return hr.Verbatim([dict(block=b, verdict=v, slips=list(sl)) for b, v, *sl in entries], path='test-ledger.json')


class VerbatimGateTest(unittest.TestCase):
    """Round 5 §11 — a TRUSTED flag no longer licenses quoting a block: the print must have been read."""

    EV = '[MẪU] Nhân vật A (101), Nhân vật B (205), Nhân vật C (300).'

    def test_no_ledger_is_v1_behaviour(self):
        doc = {'blocks': [para('p1', self.EV)]}
        ev, _, held = hr.derive_events(doc, hr.Verbatim(None))
        self.assertEqual(len(ev), 3)
        self.assertEqual(held, [])
        self.assertEqual({e['verbatimStatus'] for e in ev}, {hr.VERBATIM_UNKNOWN})

    def test_events_from_a_slipped_block_are_withheld_with_their_reason(self):
        doc = {'blocks': [para('p1', self.EV)]}
        led = ledger(('p1', 'slip', {'pipeline': 'A', 'printed': 'Ạ'}))
        ev, _, held = hr.derive_events(doc, led)
        self.assertEqual(ev, [])
        self.assertEqual(len(held), 3)
        self.assertTrue(all(h['withheldReason'].endswith(hr.VERBATIM_DIFFERS) for h in held))
        self.assertEqual(held[0]['slips'], [{'pipeline': 'A', 'printed': 'Ạ'}])

    def test_events_from_an_unjudged_block_are_withheld_too(self):
        doc = {'blocks': [para('p1', self.EV)]}
        led = ledger(('other', 'verbatim'))
        ev, _, held = hr.derive_events(doc, led)
        self.assertEqual((len(ev), len(held)), (0, 3))
        self.assertTrue(all(h['withheldReason'].endswith(hr.VERBATIM_UNKNOWN) for h in held))

    def test_a_verified_block_still_yields(self):
        doc = {'blocks': [para('p1', self.EV)]}
        ev, _, held = hr.derive_events(doc, ledger(('p1', 'verbatim_glyph')))
        self.assertEqual((len(ev), len(held)), (3, 0))
        self.assertEqual({e['verbatimStatus'] for e in ev}, {hr.VERBATIM_OK})

    def _story(self):
        return {'blocks': [para('h', 'CHUYỆN MẪU', typ='heading'),
                           para('s1', '[MẪU] Đoạn một.'),
                           para('a', '(Theo Tác Giả Mẫu, Sách mẫu, NXB Mẫu, 2005)')]}

    def test_attribution_from_a_slipped_block_is_withheld(self):
        at, held = hr.derive_attributions(self._story(), ledger(('h', 'verbatim'), ('s1', 'verbatim'),
                                                                ('a', 'slip', {'pipeline': 'Mẫu', 'printed': 'Mâu'})))
        self.assertEqual(at, [])
        self.assertEqual(len(held), 1)
        self.assertEqual(held[0]['slips'], [{'pipeline': 'Mẫu', 'printed': 'Mâu'}])

    def test_a_slipped_story_title_is_not_quoted_and_the_story_is_incomplete(self):
        at, held = hr.derive_attributions(self._story(), ledger(('h', 'slip', {'pipeline': 'CHUYỆN', 'printed': 'CHUYÊN'}),
                                                                ('s1', 'verbatim'), ('a', 'verbatim')))
        self.assertEqual((len(at), held), (1, []))
        self.assertIsNone(at[0]['title'])                     # never quoted back at the child
        self.assertEqual(at[0]['titleBlockId'], 'h')          # but still traceable
        self.assertTrue(at[0]['titleVerbatimWithheld'])
        self.assertFalse(at[0]['complete'])

    def test_apply_records_the_gate_and_v1_stays_reproducible(self):
        doc = {'title': 'T', 'book': 'b', 'lesson': 1, 'blocks': [para('p1', self.EV)], 'semantic': []}
        out_v1, rep_v1 = hr.apply(json.loads(json.dumps(doc)))
        self.assertEqual(rep_v1['version'], hr.VERSION_V1)
        self.assertFalse(rep_v1['verbatimGate'])
        self.assertEqual(len(out_v1['semantic'][0]['events']), 3)
        out_v2, rep_v2 = hr.apply(json.loads(json.dumps(doc)), verbatim=ledger(('p1', 'slip')))
        self.assertEqual(rep_v2['version'], hr.VERSION_V2)
        self.assertEqual(out_v2['semantic'], [])
        gate = out_v2['provenance']['historyRules']['verbatimGate']
        self.assertEqual((gate['enabled'], gate['eventsWithheld']), (True, 3))

    def test_short_block_id(self):
        self.assertEqual(hr._short('05-x:p039:tc2-p1:000'), 'p039:tc2-p1:000')
        self.assertEqual(hr._short('p039:tc2-p1:000'), 'p039:tc2-p1:000')


class ToneProbeTest(unittest.TestCase):
    """The probe is a MEASUREMENT of a candidate signal — these pin what it can and cannot see."""

    def setUp(self):
        sys.path.insert(0, HERE)
        import tone_repair_probe as tp
        self.tp = tp

    def test_tone_only_pairs_collapse(self):
        for a, b in (('đằng', 'đăng'), ('hóa', 'hoá'), ('BĨ', 'BÍ'), ('TRỮ', 'TRỪ'), ('đầu', 'đấu'), ('hiếu', 'hiểu')):
            self.assertEqual(self.tp.strip_tone(a), self.tp.strip_tone(b), (a, b))

    def test_vowel_quality_pairs_do_not_collapse(self):
        # «HÂN» vs «HÁN» differs in vowel quality, not tone — the probe must NOT claim it
        self.assertNotEqual(self.tp.strip_tone('HÂN'), self.tp.strip_tone('HÁN'))
        self.assertNotEqual(self.tp.strip_tone('PHẢ'), self.tp.strip_tone('PHÂ'))

    def test_context_scoping_separates_two_uses_of_one_token(self):
        keys = dict(self.tp.keyed('Theo Đăng Khoa và sông Bạch Đằng'))
        self.assertIn(('theo', 'đăng'), keys)
        self.assertIn(('bach', 'đăng'), {(a, b) for a, b in keys})

    def test_recase_follows_the_token_it_replaces(self):
        self.assertEqual(self.tp.recase('kì', 'KĨ'), 'KÌ')
        self.assertEqual(self.tp.recase('đấu', 'Đầu'), 'Đấu')
        self.assertEqual(self.tp.recase('đấu', 'đầu'), 'đấu')

    def test_a_candidate_needs_support_and_never_repairs_an_attested_form_under_the_strict_rule(self):
        ev = {('bach', 'đăng'): __import__('collections').Counter({'đằng': 7, 'đăng': 1})}
        strict = self.tp.candidates('sông Bạch Đăng', ev, 2, 'strict-unattested', 2)
        self.assertEqual(strict, [])                       # «đăng» is attested ⇒ the strict rule refuses
        dom = self.tp.candidates('sông Bạch Đăng', ev, 2, 'dominant-majority', 2)
        self.assertEqual([(c['observed'], c['proposed']) for c in dom], [('Đăng', 'Đằng')])


class RepairPluginSignalsTest(unittest.TestCase):
    """Lane C's signals for A1's repair framework. These are PURE — they do not need the framework, so they
    run on a clean clone; the end-to-end run is exercised by `repair_plugin.py` itself and skips without it."""

    def setUp(self):
        sys.path.insert(0, HERE)
        import repair_plugin as rp
        self.rp = rp

    def test_corpus_signal_supports_objects_abstains(self):
        from collections import Counter
        ev = {('bach', 'đăng'): Counter({'đằng': 7, 'đăng': 2})}
        k = ('bach', 'đăng')
        self.assertEqual(self.rp.corpus_signal('Đăng', 'Đằng', ev, k)[0], 'supports')
        self.assertEqual(self.rp.corpus_signal('Đằng', 'Đăng', ev, k)[0], 'objects')
        self.assertEqual(self.rp.corpus_signal('x', 'y', ev, ('never', 'seen'))[0], 'abstains')

    def test_human_signal_on_a_no_op_repair(self):
        led = {'b': {'block': 'b', 'verdict': 'verbatim_glyph', 'slips': []}}
        self.assertEqual(self.rp.human_signal('b', 'text', [], led)[0], 'supports')
        led2 = {'b': {'block': 'b', 'verdict': 'slip', 'slips': [{'pipeline': 'A', 'printed': 'Á'}]}}
        self.assertEqual(self.rp.human_signal('b', 'text', [], led2)[0], 'objects')
        self.assertEqual(self.rp.human_signal('unread', 'text', [], led)[0], 'abstains')

    def test_human_signal_is_scoped_to_the_occurrence(self):
        # «Theo Đăng Khoa … sông Bạch Đăng»: the print shows a slip only at the SECOND «Đăng»
        text = 'Theo Đăng Khoa và sông Bạch Đăng'
        led = {'b': {'block': 'b', 'verdict': 'slip',
                     'slips': [{'pipeline': 'Đăng', 'printed': 'Đằng', 'context': 'Bạch —'}]}}
        river = [dict(index=6, observed='Đăng', proposed='Đằng')]
        author = [dict(index=1, observed='Đăng', proposed='Đặng')]
        self.assertEqual(self.rp.human_signal('b', text, river, led)[0], 'supports')
        v, _, d = self.rp.human_signal('b', text, author, led)
        self.assertEqual(v, 'objects')
        self.assertIn('no slip at this', d['reason'])

    def test_human_signal_objects_when_a_repair_leaves_the_block_non_verbatim(self):
        text = 'Bạch Đăng Văn hóa'
        led = {'b': {'block': 'b', 'verdict': 'slip', 'slips': [
            {'pipeline': 'Đăng', 'printed': 'Đằng', 'context': 'Bạch —'},
            {'pipeline': 'hóa', 'printed': 'hoá', 'context': 'Văn —'}]}}
        half = [dict(index=1, observed='Đăng', proposed='Đằng')]
        v, _, d = self.rp.human_signal('b', text, half, led)
        self.assertEqual(v, 'objects')
        self.assertEqual(d['uncovered'], ['hóa→hoá'])

    def test_subsequence_check_for_the_column_linearisation_signal(self):
        primary = ['sau', 'khi', 'trieu', 'da']
        merged = ['sau', 'khi', 'trieu', 'chinh', 'quyen', 'da']     # verifier merged a second column in
        self.assertTrue(self.rp.tokens_in_order(primary, merged))
        self.assertFalse(self.rp.tokens_in_order(primary, ['sau', 'khi', 'da', 'trieu']))

    def test_slip_context_matching(self):
        self.assertTrue(self.rp._slip_matches_occurrence({'context': 'Bạch —'}, 'Bạch'))
        self.assertTrue(self.rp._slip_matches_occurrence({}, 'anything'))
        self.assertFalse(self.rp._slip_matches_occurrence({'context': 'Bạch —'}, 'Theo'))

    def test_end_to_end_needs_lane_a1(self):
        if not self.rp.available():
            self.skipTest('Lane A1 repair framework not on the path (tool/corpus/repair)')
        self.assertTrue(hasattr(self.rp, 'register'))


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
