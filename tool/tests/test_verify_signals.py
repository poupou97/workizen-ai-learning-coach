#!/usr/bin/env python3
"""Round 5 · Lane A4 — the multi-signal verification contract, as tests.

Two kinds of test here, and the split matters:

* **Contract tests** run everywhere. They assert the things that must be true whatever the data says: that
  A4 reuses A1's dispositions instead of defining its own, that external evidence cannot be recorded
  without a URL and a timestamp, that no validator validates its own layer, that an anomaly without a
  proposal produces `SUSPECT` and two disagreeing candidates produce `CONFLICT`.
* **Regression tests for the six named defects.** The ones that need only a rule (`I1` → `II`, the
  watermark tail, the injection generator) run everywhere; the ones that need the 62,729-page corpus index
  **skip when it is absent**, because that index is gitignored and a fresh clone does not have it. A test
  that silently passed without the corpus would be a test that measures nothing — the clean-clone lesson.

Two assertions here are **assertions of abstention**, which is unusual and deliberate. `Cộng hoà → Cộng
hoa` must NOT be corrected by cross-corpus, because the corpus itself carries the same slip; and «Đăng
Khoa» must NOT be corrected, because a function word beside a name says nothing about the name. Both are
cases where the useful behaviour is silence, and silence is only a guarantee if something checks it.
"""
import os
import sys
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', 'corpus'))

from repair import model as rmodel  # noqa: E402
from verify import (crosscorpus as xc, enumerator as EN, evalsets as es, external as EX,  # noqa: E402
                    furniture as FU, human as HU, index as ix, paths, router as R, trust)

HAS_INDEX = os.path.exists(f'{paths.OUT}/xcorpus-index-heldout.json')
SKIP_INDEX = unittest.skipUnless(HAS_INDEX, 'needs the gitignored corpus index (poc-out/round5/verify)')


def obs(value, block='bk:p001:tc2-p1:001', source='docling-ocrmac'):
    return rmodel.Observation(block_id=block, source=source, value=value)


# --------------------------------------------------------------------------- reuse, not duplication
class ReuseContractTests(unittest.TestCase):
    def test_a4_does_not_define_its_own_dispositions(self):
        self.assertIs(trust.Disposition, rmodel.Disposition)
        for name in ('SUSPECT', 'HUMAN_VERIFIED', 'CONFLICT', 'TRUSTED', 'WITHHELD'):
            self.assertIn(getattr(trust.Disposition, name), rmodel.Disposition.ALL)

    def test_founder_aliases_map_onto_a1s_states(self):
        self.assertEqual(trust.RAW, rmodel.Disposition.ORIGINAL_OBSERVATION)
        self.assertEqual(trust.CORRECTION_PROPOSED, rmodel.Disposition.REPAIRED_CANDIDATE)

    def test_a4_does_not_widen_what_may_be_served(self):
        # a human is a source, not an oracle, and no production trust gate exists yet
        self.assertEqual(trust.SERVABLE, rmodel.Disposition.SERVABLE)
        self.assertNotIn(trust.Disposition.HUMAN_VERIFIED, trust.SERVABLE)
        self.assertNotIn(trust.Disposition.SUSPECT, trust.SERVABLE)
        self.assertNotIn(trust.Disposition.CONFLICT, trust.SERVABLE)

    def test_a4_registers_into_a1s_registry(self):
        import verify
        from repair import registry
        d = verify.load_plugins(which=('crosscorpus', 'llm', 'external'))
        self.assertIn('D.cross_corpus', d['signals'])
        self.assertIn('G.llm_semantic', d['signals'])
        self.assertIn('H.external', d['signals'])
        self.assertIn('xcorpus.token-v1', registry.providers()['token'])
        self.assertIn('xcorpus.block-v1', registry.providers()['block'])


# --------------------------------------------------------------------------- evidence
class EvidenceTests(unittest.TestCase):
    def test_external_evidence_requires_url_and_timestamp(self):
        with self.assertRaises(ValueError):
            trust.EvidenceRef(kind='external_page', source='https://example.org/x', claim='c')
        with self.assertRaises(ValueError):
            trust.EvidenceRef(kind='external_page', source='not-a-url', claim='c',
                              retrieved_at='2026-09-06T00:00:00+00:00')
        ok = trust.EvidenceRef(kind='external_page', source='https://example.org/x', claim='c',
                               authority='reference', retrieved_at='2026-09-06T00:00:00+00:00')
        self.assertEqual(ok.relation, 'supports')

    def test_contradicting_evidence_is_first_class(self):
        e = trust.EvidenceRef(kind='corpus_occurrence', source='b/p1', claim='c', relation='contradicts',
                              authority='corpus')
        self.assertTrue(e.contradicts)
        a = trust.AnomalySignal(block_id='b', detector_id='G.llm_semantic/haiku', reason='r', evidence=[e])
        self.assertEqual(len(a.contradicting()), 1)
        self.assertEqual(a.as_signal().verdict, rmodel.SignalVerdict.OBJECTS)


# --------------------------------------------------------------------------- TrustDecision
class TrustDecisionTests(unittest.TestCase):
    def _cand(self, value, layer='D', rule='r1'):
        return rmodel.RepairCandidate(
            block_id='b', failure_class='vi_tone_disagreement', original_observations=(obs('x', 'b'),),
            proposed_value=value, rule_id=rule,
            supporting_signals=(rmodel.Signal(f'{layer}.x', rmodel.SignalVerdict.SUPPORTS, 0.5),))

    def test_anomaly_without_a_proposal_is_suspect_not_withheld(self):
        a = trust.AnomalySignal(block_id='b', detector_id='D.cross_corpus/xcorpus-v1', reason='r')
        d = trust.TrustDecision(block_id='b', anomalies=(a,))
        self.assertEqual(d.disposition, trust.Disposition.SUSPECT)
        self.assertFalse(d.servable)

    def test_two_candidates_proposing_different_values_conflict(self):
        v = rmodel.ValidationResult('v', rmodel.Verdict.VALIDATED)
        d = trust.TrustDecision(block_id='b', candidates=(self._cand('A'), self._cand('B', rule='r2')),
                                validations=(v,))
        self.assertEqual(d.disposition, trust.Disposition.CONFLICT)

    def test_an_unvalidated_candidate_is_a_proposal_and_never_served(self):
        d = trust.TrustDecision(block_id='b', candidates=(self._cand('A'),))
        self.assertEqual(d.disposition, trust.CORRECTION_PROPOSED)
        self.assertFalse(d.servable)

    def test_a_validated_repair_that_leaves_a_withhold_reason_stays_withheld(self):
        v = rmodel.ValidationResult('v', rmodel.Verdict.VALIDATED)
        d = trust.TrustDecision(block_id='b', candidates=(self._cand('A'),), validations=(v,),
                                withhold_reasons=('page_feature:color_heavy',))
        self.assertEqual(d.disposition, trust.Disposition.WITHHELD)


# --------------------------------------------------------------------------- validators refuse their layer
class ValidatorIndependenceTests(unittest.TestCase):
    def _ctx(self, text='x'):
        from repair import engine
        return engine.RepairContext(block_id='b', observations=(obs(text, 'b'),))

    def test_cross_corpus_will_not_validate_a_cross_corpus_only_candidate(self):
        cand = rmodel.RepairCandidate(
            block_id='b', failure_class=xc.FC_TONE, original_observations=(obs('x', 'b'),),
            proposed_value='y', rule_id=xc.RULE_STRICT,
            supporting_signals=(rmodel.Signal(xc.SIGNAL_ID, rmodel.SignalVerdict.SUPPORTS, 0.9),))
        r = xc.validate(cand, self._ctx())
        self.assertEqual(r.verdict, rmodel.Verdict.INSUFFICIENT)

    def test_an_llm_may_not_validate_an_llm_proposal(self):
        from verify import llm as L
        cand = rmodel.RepairCandidate(
            block_id='b', failure_class=L.FC_TONE, original_observations=(obs('x', 'b'),),
            proposed_value='y', rule_id='llm.x',
            supporting_signals=(rmodel.Signal(L.SIGNAL_ID, rmodel.SignalVerdict.SUPPORTS, 0.9),))
        r = L.llm_validator(cand, self._ctx())
        self.assertEqual(r.verdict, rmodel.Verdict.INSUFFICIENT)

    def test_an_objection_rejects_whatever_supports_it(self):
        cand = rmodel.RepairCandidate(
            block_id='b', failure_class=xc.FC_TONE, original_observations=(obs('x', 'b'),),
            proposed_value='y', rule_id=xc.RULE_STRICT,
            supporting_signals=(rmodel.Signal('A.vi_lexicon', rmodel.SignalVerdict.SUPPORTS, 0.9),
                                rmodel.Signal('E.human', rmodel.SignalVerdict.OBJECTS, 0.9)))
        self.assertEqual(xc.validate(cand, self._ctx()).verdict, rmodel.Verdict.REJECTED)


# --------------------------------------------------------------------------- defect F: I1 and the watermark
class CaseFTests(unittest.TestCase):
    OBSERVED = 'I1 - Định luật khúc xạ ánh sáng, Ô C S ỐNG'
    PRINTED = 'II – Định luật khúc xạ ánh sáng'

    def test_enumerator_reads_I1_as_II(self):
        self.assertEqual(EN.analyse(self.OBSERVED), ('I1', 'II'))

    def test_a_plain_number_is_never_turned_into_a_numeral(self):
        # «11 - Bài tập» is eleven. Guessing here would be exactly the failure this lane bounds.
        self.assertIsNone(EN.analyse('11 - Bài tập'))
        self.assertIsNone(EN.repair_glyphs('11'))
        self.assertIsNone(EN.analyse('II – Định luật khúc xạ ánh sáng'))

    def test_the_watermark_tail_is_removed_and_nothing_else_is(self):
        cleaned, removed = FU.strip_known(self.OBSERVED)
        self.assertEqual(cleaned, 'I1 - Định luật khúc xạ ánh sáng')
        self.assertEqual([p for p, _, _ in removed], ['Ô C S ỐNG'])

    def test_both_signals_together_reach_the_printed_heading(self):
        cleaned, _ = FU.strip_known(self.OBSERVED)
        tok, fixed = EN.analyse(cleaned)
        self.assertEqual(cleaned.replace(tok, fixed, 1), 'II - Định luật khúc xạ ánh sáng')

    def test_ordinary_prose_is_not_mistaken_for_a_watermark(self):
        # «cuộc sống» is an exact substring of «…VỚI CUỘC SỐNG» and two of the commonest words in
        # Vietnamese. A similarity-only rule deletes it out of a lesson; this one must not.
        for text in ('Kể tên các nguồn năng lượng trong cuộc sống',
                     'Em có thể vận dụng vào cuộc sống',
                     'Sự sống trên Trái Đất',
                     'Chương II. ÁNH SÁNG',
                     'Hình 5.2 Đường truyền của chùm tia sáng'):
            self.assertEqual(FU.strip_known(text)[1], [], text)


# --------------------------------------------------------------------------- the injection generator
class InjectionTests(unittest.TestCase):
    def test_no_corruption_carries_two_tone_marks_or_a_stray_mark(self):
        import unicodedata
        for tok in ('ổi', 'Tổ', 'đấu', 'hoà', 'bản', 'Đằng', 'KĨ', 'người'):
            for cand in es._vowel_edits(tok):
                nfc = unicodedata.normalize('NFC', cand)
                self.assertFalse(any(unicodedata.category(c) == 'Mn' for c in nfc), (tok, cand))
                tones = sum(1 for c in unicodedata.normalize('NFD', cand) if c in ''.join(es.TONES))
                self.assertLessEqual(tones, 1, (tok, cand))

    def test_a_corruption_is_always_a_different_string(self):
        for tok in ('ổi', 'Tổ', 'bản'):
            self.assertNotIn(tok, es._vowel_edits(tok))


# --------------------------------------------------------------------------- normalisation
class NormalisationTests(unittest.TestCase):
    def test_the_two_valid_orthographies_are_one_word(self):
        # «hoà»/«hòa» and «thuỷ»/«thủy» are both correct. Counting them apart would make the correct
        # old-style spelling look like a rare anomaly, and «correcting» it is a display-fidelity act.
        self.assertEqual(ix.norm_token('hoà'), ix.norm_token('hòa'))
        self.assertEqual(ix.norm_token('thuỷ'), ix.norm_token('thủy'))

    def test_a_punctuation_gap_breaks_adjacency(self):
        # «đồi mồi,...), phải» must not be read as the bigram `mồi phải`
        toks = ix.tokens_with_adjacency('đồi mồi,...), phải theo')
        forms = [t for t, _ in toks]
        adj = dict(zip(forms, [a for _, a in toks]))
        self.assertTrue(adj['mồi'])          # «đồi mồi» is adjacent
        self.assertFalse(adj['phải'])        # «mồi , ) phải» is not

    def test_variants_share_a_diacritic_stripped_key(self):
        self.assertEqual(ix.key_of('tổ'), ix.key_of('tô'))
        self.assertEqual(ix.key_of('hán'), ix.key_of('hân'))     # vowel quality, not only tone


# --------------------------------------------------------------------------- router
class RouterTests(unittest.TestCase):
    def test_a_router_that_escalates_everything_would_fail_this(self):
        rt = R.route('b', 'Trời hôm nay rất đẹp và các bạn nhỏ cùng nhau ra sân chơi.', role='body')
        self.assertFalse(rt.human)
        self.assertIn('D.cross_corpus', rt.path)
        self.assertNotIn('H.external', rt.path)

    def test_a_teaching_critical_tone_disagreement_reaches_a_human(self):
        rt = R.route('b', 'Trận Bạch Đăng năm 938.', role='question',
                     block=dict(guards=['agree_tones'],
                                agreement=dict(tone_disagreements=[['đăng', 'đằng']])))
        self.assertTrue(rt.human)

    def test_external_is_never_routed_for_a_source_bound_question(self):
        rt = R.route('b', 'Giữ gìn bán sắc văn hoá dân tộc.', role='body', budget='full')
        self.assertNotIn('H.external', rt.path)
        self.assertIn('source-bound', rt.skipped['H.external'] + ' source-bound'
                      if 'printed page' in rt.skipped['H.external'] else 'source-bound')

    def test_a_conflict_always_reaches_a_human(self):
        rt = R.route('b', 'x', role='body')
        esc, why = R.escalate_after(rt, 'CONFLICT')
        self.assertTrue(esc)

    def test_a_silently_lost_numeric_block_is_treated_as_teaching_critical(self):
        # Lane D R13: role=`empty` reaches neither `blocks` nor `withheld` of the TSL and carries no
        # reason code, and the lost blocks are the printed arithmetic.
        rt = R.route('b', '40 613 + 47 519 = ?', role='empty')
        self.assertEqual(rt.teaching_consequence, 'teaching_critical')


# --------------------------------------------------------------------------- human workflow
class HumanWorkflowTests(unittest.TestCase):
    def _rec(self, **kw):
        base = dict(record_id='r1', source_block_id='b:p1:tc2-p1:001', original='cây ỗi',
                    proposed='cây ổi', reason='sai dấu', reporter_type='learner')
        base.update(kw)
        return HU.CorrectionRecord(**base)

    def test_a_learner_report_is_a_detection_not_a_correction(self):
        r = self._rec()
        self.assertTrue(r.is_detection_only)
        status, why = HU.triage(r)
        self.assertEqual(status, 'NEEDS_SOURCE')
        self.assertEqual(r.as_signal().verdict, rmodel.SignalVerdict.OBJECTS)

    def test_a_page_reading_alone_is_not_enough_because_humans_are_wrong_too(self):
        r = self._rec(reporter_type='internal_reviewer', source_evidence='print')
        self.assertTrue(r.establishes_print)
        self.assertEqual(HU.triage(r)[0], 'VALIDATING')
        self.assertEqual(HU.triage(r, independent_layers=('D',))[0], 'ACCEPTED')

    def test_a_user_can_never_overwrite_canonical_truth(self):
        r = self._rec(reporter_type='parent', source_evidence='photo', status='ACCEPTED')
        cand = HU.to_candidate(r, (obs('cây ỗi', r.source_block_id),))
        self.assertEqual(cand.disposition, rmodel.Disposition.REPAIRED_CANDIDATE)
        with self.assertRaises(ValueError):
            HU.to_candidate(self._rec(), (obs('x'),))

    def test_a_founder_report_is_a_policy_act_not_a_correction(self):
        self.assertEqual(HU.triage(self._rec(reporter_type='founder'))[0], 'REJECTED')


# --------------------------------------------------------------------------- external appropriateness
class ExternalTests(unittest.TestCase):
    def test_a_source_bound_question_is_never_appropriate_for_an_external_lookup(self):
        for kind in ('orthography_variant', 'reading_order', 'role', 'attachment',
                     'common_word_meaning'):
            ok, why = EX.appropriate(kind)
            self.assertFalse(ok, kind)
            self.assertIn('printed page', why)

    def test_a_stable_public_fact_is(self):
        for kind in ('stem_constant', 'proper_noun_person', 'dictionary_word'):
            self.assertTrue(EX.appropriate(kind)[0], kind)

    def test_an_external_claim_cannot_be_built_for_a_source_bound_question(self):
        with self.assertRaises(ValueError):
            EX.ExternalClaim(block_id='b', span='hoà', kind='orthography_variant', question='?')


# --------------------------------------------------------------------------- corpus-dependent regressions
@SKIP_INDEX
class CrossCorpusRegressionTests(unittest.TestCase):
    """The named defects that need the 62,729-page index. Skipped without it, never silently passed."""

    @classmethod
    def setUpClass(cls):
        cls.idx = ix.CrossCorpusIndex.load(f'{paths.OUT}/xcorpus-index-heldout.json')

    def test_the_corpus_writes_dau_more_often_than_dau_which_is_why_frequency_is_not_truth(self):
        # `đầu` 30k vs `đấu` 5.6k: a token-frequency majority rule rewrites the CORRECT «cuộc đấu tranh».
        self.assertGreater(self.idx.count('đầu'), self.idx.count('đấu'))

    def test_the_proper_noun_prior_separates_names_from_common_words(self):
        self.assertGreater(self.idx.proper_ratio('đặng'), 0.8)
        self.assertGreater(self.idx.proper_ratio('hán'), 0.8)
        self.assertLess(self.idx.proper_ratio('đấu'), 0.1)
        self.assertLess(self.idx.proper_ratio('đầu'), 0.1)

    def test_oi_is_unattested_in_the_whole_corpus(self):
        self.assertEqual(self.idx.count('ỗi'), 0)
        self.assertGreater(self.idx.count('ổi'), 50)


if __name__ == '__main__':
    unittest.main()


# --------------------------------------------------------------------------- assertions of ABSTENTION
@unittest.skipUnless(os.path.exists(f'{paths.OUT}/xcorpus-report.json'),
                     'needs the measured cross-corpus report (run tool/corpus/verify/run_xcorpus.py)')
class MeasuredAbstentionTests(unittest.TestCase):
    """The two cases where the useful behaviour is **silence**, asserted against the measured run.

    Silence is only a guarantee if something checks it, and both of these are silences a naive frequency
    rule would break.
    """

    @classmethod
    def setUpClass(cls):
        import json
        with open(f'{paths.OUT}/xcorpus-report.json', encoding='utf-8') as fh:
            cls.report = json.load(fh)

    def _case(self, policy, cid):
        return {c['case']: c for c in self.report['policies'][policy]['poc_cases']}[cid]

    def test_cong_hoa_is_never_corrected_because_the_corpus_carries_the_same_slip(self):
        # Lane A1 measured the same thing from the other side (268 vs 303 pages) and asserts the same
        # abstention. A naive cross-corpus majority would have "corrected" toward the wrong form.
        for policy in self.report['policies']:
            self.assertFalse(self._case(policy, 'D')['proposed'], f'{policy}: case D must abstain')

    def test_the_founder_named_tone_cases_are_still_caught_at_the_recall_setting(self):
        for cid in ('B', 'C', 'E'):
            self.assertTrue(self._case('recall', cid)['correct_proposal'], f'case {cid} regressed')

    def test_no_policy_proposes_a_change_to_text_that_is_already_correct(self):
        for policy in self.report['policies']:
            for c in self.report['policies'][policy]['poc_cases']:
                self.assertEqual(c['false_corrections_on_correct_text'], [],
                                 f"{policy}/{c['case']}: proposed a change to the printed text")

    def test_the_proper_noun_false_correction_rate_stays_zero_on_the_holdout(self):
        for policy in self.report['policies']:
            pn = self.report['policies'][policy]['holdout_injected']['proper_noun']
            self.assertEqual(pn['false'], 0, f'{policy}: a proper noun was falsely corrected')
