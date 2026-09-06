#!/usr/bin/env python3
"""Round 5 · Lane A1 - the repair framework's contract, as tests.

These are the guarantees another lane may build on: an observation is immutable, a candidate is never
trusted by itself, validation is unanimous among non-abstainers, `insufficient` is not a soft yes, a
withhold reason nobody repaired keeps the block withheld, and the ledger is append-only.
"""
import json
import os
import sys
import tempfile
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', 'corpus'))

from repair import engine, ledger as ledger_mod, model, registry  # noqa: E402


def obs(value='observed', source='stack-a', block='bk:p001:tc2:001'):
    return model.Observation(block_id=block, source=source, value=value,
                             provenance=dict(book='bk', page=1, bbox=[0, 0, 1, 0.1]))


class ModelContractTests(unittest.TestCase):
    def test_observation_is_immutable_and_carries_its_disposition(self):
        o = obs()
        self.assertEqual(o.disposition, model.Disposition.ORIGINAL_OBSERVATION)
        with self.assertRaises(Exception):
            o.value = 'overwritten'
        with self.assertRaises(TypeError):
            o.provenance['book'] = 'other'

    def test_observation_id_is_deterministic_and_content_addressed(self):
        self.assertEqual(obs('x').observation_id, obs('x').observation_id)
        self.assertNotEqual(obs('x').observation_id, obs('y').observation_id)

    def test_candidate_must_cite_an_observation(self):
        with self.assertRaises(ValueError):
            model.RepairCandidate(block_id='b', failure_class='f', original_observations=(),
                                  proposed_value='v', rule_id='r')

    def test_candidate_disposition_is_never_trusted(self):
        c = model.RepairCandidate(block_id='b', failure_class='f', original_observations=(obs(),),
                                  proposed_value='v', rule_id='r', confidence=1.0)
        self.assertEqual(c.disposition, model.Disposition.REPAIRED_CANDIDATE)
        self.assertNotIn(c.disposition, model.Disposition.SERVABLE)

    def test_independent_support_excludes_its_own_layer(self):
        c = model.RepairCandidate(block_id='b', failure_class='f', original_observations=(obs(),),
                                  proposed_value='v', rule_id='r',
                                  supporting_signals=(model.Signal('A.vi_lexicon', 'supports', 0.9),
                                                      model.Signal('D.consistency', 'supports', 0.7),
                                                      model.Signal('B.layout', 'abstains')))
        self.assertEqual(c.independent_support(), ['A', 'D'])
        self.assertEqual(c.independent_support(exclude_layers=('A',)), ['D'])

    def test_signal_verdict_is_validated(self):
        with self.assertRaises(ValueError):
            model.Signal('A.x', 'probably')
        with self.assertRaises(ValueError):
            model.ValidationResult('v', 'maybe')
        with self.assertRaises(ValueError):
            model.Disposition.check('NEARLY_TRUSTED')


class LedgerTests(unittest.TestCase):
    def test_append_only_refuses_a_duplicate_entry(self):
        lg = ledger_mod.Ledger()
        e = model.LedgerEntry(block_id='b', failure_class='f',
                              disposition=model.Disposition.WITHHELD, observations=(obs(),))
        lg.append(e)
        with self.assertRaises(ledger_mod.LedgerConflict):
            lg.append(e)

    def test_supersede_keeps_the_prior_row(self):
        lg = ledger_mod.Ledger()
        first = lg.append(model.LedgerEntry(block_id='b', failure_class='f',
                                            disposition=model.Disposition.WITHHELD, observations=(obs(),)))
        second = lg.supersede(first, disposition=model.Disposition.TRUSTED, reasons=('restored',))
        self.assertEqual(second.prior_entry_id, first.entry_id)
        self.assertEqual([e.disposition for e in lg.by_block('b')],
                         [model.Disposition.WITHHELD, model.Disposition.TRUSTED])

    def test_the_ledger_computes_the_false_correction_rate_and_attributes_it(self):
        """The P0 metric, straight off the ledger, with per-signal attribution."""
        lg = ledger_mod.Ledger()
        for bid, observed, served, sig in (('b1', 'wrong', 'right', 'A.vi_lexicon'),          # repaired
                                           ('b2', 'right', 'other', 'A.vi_lexicon'),          # FALSE CORRECTION
                                           ('b3', 'wrong', 'other', 'D.in_document')):        # still wrong
            o = model.Observation(bid, 'stack-a', observed)
            cand = model.RepairCandidate(block_id=bid, failure_class='vi_text',
                                         original_observations=(o,), proposed_value=served, rule_id='r',
                                         supporting_signals=(model.Signal(sig, 'supports', 1.0),))
            lg.append(model.LedgerEntry(block_id=bid, failure_class='vi_text',
                                        disposition=model.Disposition.VALIDATED_REPAIR,
                                        observations=(o,), candidate=cand, final_value=served))
        truth = {'b1': 'right', 'b2': 'right', 'b3': 'right'}
        rep = lg.false_correction_report(truth.get)
        self.assertEqual(rep['changed'], 3)
        self.assertEqual(rep['totals']['false_correction'], 1)
        self.assertAlmostEqual(rep['false_correction_rate'], 0.3333, places=3)
        self.assertAlmostEqual(rep['correction_precision'], 0.3333, places=3)
        self.assertEqual(rep['by_signal']['A.vi_lexicon'], dict(repaired=1, false_correction=1))
        self.assertEqual(rep['by_signal']['D.in_document'], dict(still_wrong=1))

    def test_file_ledger_round_trips_as_jsonl(self):
        with tempfile.TemporaryDirectory() as d:
            p = os.path.join(d, 'sub', 'ledger.jsonl')
            with ledger_mod.Ledger(p, run=dict(lane='a1')) as lg:
                lg.append(model.LedgerEntry(block_id='b', failure_class='f',
                                            disposition=model.Disposition.VALIDATED_REPAIR,
                                            observations=(obs(),), final_value='fixed'))
            rows = ledger_mod.read(p)
            self.assertEqual(len(rows), 1)
            self.assertEqual(rows[0]['final_value'], 'fixed')
            self.assertEqual(rows[0]['run']['lane'], 'a1')
            self.assertEqual(rows[0]['observations'][0]['disposition'],
                             model.Disposition.ORIGINAL_OBSERVATION)
            json.dumps(rows)   # a consumer in another lane needs nothing but json


class _Registered(unittest.TestCase):
    def setUp(self):
        self._snap = registry.snapshot()
        registry.reset()

    def tearDown(self):
        registry.restore(self._snap)


class RegistryTests(_Registered):
    def test_duplicate_plugin_id_is_refused(self):
        registry.repairer('fc', 'r1')(lambda ctx: ())
        with self.assertRaises(registry.DuplicatePlugin):
            registry.repairer('fc', 'r1')(lambda ctx: ())

    def test_describe_lists_what_a_run_used(self):
        registry.repairer('fc', 'r1')(lambda ctx: ())
        registry.validator('fc', 'v1')(lambda c, ctx: None)
        registry.signal('A.demo')(lambda v, ctx: None)
        d = registry.describe()
        self.assertEqual(d['failure_classes']['fc'], dict(repairers=['r1'], validators=['v1']))
        self.assertEqual(d['signals'], ['A.demo'])


class EnginePolicyTests(_Registered):
    def _ctx(self, disposition=model.Disposition.TRUSTED, reasons=()):
        return engine.RepairContext(block_id='bk:p001:tc2:001', observations=(obs(), obs('observd', 'stack-b')),
                                    disposition=disposition, withhold_reasons=tuple(reasons))

    def _propose(self, signals=(), covers=()):
        def fn(ctx):
            yield model.RepairCandidate(block_id=ctx.block_id, failure_class='vi_text',
                                        original_observations=ctx.observations, proposed_value='repaired',
                                        rule_id='demo-v1', supporting_signals=signals, confidence=0.9,
                                        provenance=dict(covers_reasons=tuple(covers)),
                                        detected=dict(what='demo'))
        registry.repairer('vi_text', 'demo')(fn)

    def test_no_validator_means_the_repair_stays_a_candidate_and_the_block_is_not_served(self):
        self._propose()
        out = engine.RepairEngine().run_block(self._ctx())
        self.assertEqual(out.disposition, model.Disposition.SUSPECT)
        self.assertNotIn(out.disposition, model.Disposition.SERVABLE)
        self.assertFalse(out.restorable)
        self.assertEqual(len(out.candidates), 1)

    def test_insufficient_is_not_a_soft_yes(self):
        self._propose()
        registry.validator('vi_text', 'v')(lambda c, ctx: model.ValidationResult('v', model.Verdict.INSUFFICIENT))
        out = engine.RepairEngine().run_block(self._ctx())
        self.assertEqual(out.disposition, model.Disposition.SUSPECT)
        self.assertNotIn(out.disposition, model.Disposition.SERVABLE)

    def test_a_withheld_block_whose_repair_is_not_confirmed_stays_withheld(self):
        self._propose()
        out = engine.RepairEngine().run_block(self._ctx(model.Disposition.WITHHELD, ('agree_tones',)))
        self.assertEqual(out.disposition, model.Disposition.WITHHELD)

    def test_contradicting_evidence_produces_CONFLICT_not_a_quiet_withhold(self):
        self._propose(signals=(model.Signal('D.consistency', 'objects', 1.0),))
        registry.validator('vi_text', 'v')(lambda c, ctx: model.ValidationResult('v', model.Verdict.REJECTED))
        out = engine.RepairEngine().run_block(self._ctx())
        self.assertEqual(out.disposition, model.Disposition.CONFLICT)
        self.assertEqual([s.signal_id for s in out.candidates[0].contradicting()], ['D.consistency'])
        self.assertEqual(out.candidates[0].to_json()['contradictory_evidence'][0]['verdict'], 'objects')

    def test_one_rejection_beats_any_number_of_validations(self):
        self._propose()
        registry.validator('vi_text', 'yes')(lambda c, ctx: model.ValidationResult('yes', model.Verdict.VALIDATED))
        registry.validator('vi_text', 'no')(lambda c, ctx: model.ValidationResult('no', model.Verdict.REJECTED))
        out = engine.RepairEngine().run_block(self._ctx())
        self.assertNotIn(out.disposition, model.Disposition.SERVABLE)

    def test_a_validated_repair_of_a_withheld_block_is_restorable(self):
        self._propose(covers=('agree_tones',))
        registry.validator('vi_text', 'yes')(lambda c, ctx: model.ValidationResult('yes', model.Verdict.VALIDATED))
        eng = engine.RepairEngine()
        out = eng.run_block(self._ctx(model.Disposition.WITHHELD, ('agree_tones',)))
        self.assertEqual(out.disposition, model.Disposition.VALIDATED_REPAIR)
        self.assertTrue(out.restorable)
        self.assertEqual(out.final_value, 'repaired')
        eng.restore(out)
        self.assertEqual(eng.ledger.latest(out.block_id).disposition, model.Disposition.TRUSTED)

    def test_a_withhold_reason_nobody_repaired_keeps_the_block_withheld(self):
        self._propose(covers=('agree_tones',))
        registry.validator('vi_text', 'yes')(lambda c, ctx: model.ValidationResult('yes', model.Verdict.VALIDATED))
        out = engine.RepairEngine().run_block(
            self._ctx(model.Disposition.WITHHELD, ('agree_tones', 'math_guard')))
        self.assertEqual(out.disposition, model.Disposition.WITHHELD)
        self.assertIn('math_guard', out.reasons)
        self.assertFalse(out.restorable)

    def test_a_detected_but_unrepaired_failure_stops_serving_a_trusted_block(self):
        self._propose()
        registry.validator('vi_text', 'v')(lambda c, ctx: model.ValidationResult('v', model.Verdict.INSUFFICIENT))
        out = engine.RepairEngine().run_block(self._ctx(model.Disposition.TRUSTED))
        self.assertNotIn(out.disposition, model.Disposition.SERVABLE)

    def test_the_addendum_names_map_onto_the_existing_states(self):
        self.assertEqual(model.Disposition.check('RAW'), model.Disposition.ORIGINAL_OBSERVATION)
        self.assertEqual(model.Disposition.check('CORRECTION_PROPOSED'), model.Disposition.REPAIRED_CANDIDATE)
        for extra in ('SUSPECT', 'HUMAN_VERIFIED', 'CONFLICT'):
            self.assertEqual(model.Disposition.check(extra), extra)
            self.assertNotIn(extra, model.Disposition.SERVABLE)

    def test_another_lane_can_veto_a_repair_through_the_provider_hook(self):
        seen = []

        @registry.token_signal_provider('a4.demo')
        def provider(observed, proposed, ctx):
            seen.append((observed, proposed))
            return model.Signal('A4.cross_corpus', 'objects', 1.0, dict(why='demo veto'))

        self.assertEqual(registry.describe()['providers']['token'], ['a4.demo'])
        sig = registry.token_signals('a', 'b', None)
        self.assertEqual([s.verdict for s in sig], ['objects'])
        self.assertEqual(seen, [('a', 'b')])

    def test_a_provider_that_raises_cannot_take_the_run_down(self):
        @registry.token_signal_provider('a4.broken')
        def provider(observed, proposed, ctx):
            raise RuntimeError('boom')
        self.assertEqual(registry.token_signals('a', 'b', None), [])

    def test_a_block_with_nothing_detected_keeps_its_pipeline_disposition(self):
        out = engine.RepairEngine().run_block(self._ctx(model.Disposition.TRUSTED))
        self.assertEqual(out.disposition, model.Disposition.TRUSTED)
        self.assertEqual(out.entries, ())

    def test_the_ledger_records_the_whole_trace(self):
        self._propose(signals=(model.Signal('A.vi_lexicon', 'supports', 0.9),), covers=('agree_tones',))
        registry.validator('vi_text', 'yes')(lambda c, ctx: model.ValidationResult(
            'yes', model.Verdict.VALIDATED, evidence=[dict(kind='demo')]))
        eng = engine.RepairEngine()
        out = eng.run_block(self._ctx(model.Disposition.WITHHELD, ('agree_tones',)))
        eng.restore(out)
        rows = [e.to_json() for e in eng.ledger.entries]
        self.assertEqual([r['disposition'] for r in rows],
                         [model.Disposition.REPAIRED_CANDIDATE, model.Disposition.VALIDATED_REPAIR,
                          model.Disposition.VALIDATED_REPAIR, model.Disposition.TRUSTED])
        trace = rows[-2]
        self.assertEqual(trace['candidate']['rule_id'], 'demo-v1')
        self.assertEqual(trace['candidate']['supporting_signals'][0]['layer'], 'A')
        self.assertEqual(trace['observations'][0]['value'], 'observed')     # source observation intact
        self.assertEqual(trace['final_value'], 'repaired')

    def test_a_repairer_returning_the_wrong_type_fails_loudly(self):
        registry.repairer('vi_text', 'bad')(lambda ctx: ['not a candidate'])
        with self.assertRaises(TypeError):
            engine.RepairEngine().run_block(self._ctx())


class SignalContributionTests(_Registered):
    def test_decisive_counts_the_only_supporting_layer(self):
        c_solo = model.RepairCandidate(block_id='b', failure_class='f', original_observations=(obs(),),
                                       proposed_value='v', rule_id='r',
                                       supporting_signals=(model.Signal('A.vi_lexicon', 'supports', 1.0),
                                                           model.Signal('D.consistency', 'abstains')))
        c_pair = model.RepairCandidate(block_id='b2', failure_class='f', original_observations=(obs(),),
                                       proposed_value='v', rule_id='r',
                                       supporting_signals=(model.Signal('A.vi_lexicon', 'supports', 1.0),
                                                           model.Signal('D.consistency', 'supports', 1.0)))
        sc = engine.SignalContribution()
        sc.observe(c_solo, validated=True, correct=True)
        sc.observe(c_pair, validated=True, correct=False)
        t = sc.table()
        self.assertEqual(t['A']['decisive'], 1)
        self.assertEqual(t['A']['right'], 1)
        self.assertEqual(t['A']['wrong'], 1)
        self.assertEqual(t['D']['abstains'], 1)
        self.assertEqual(t['D']['decisive'], 0)


if __name__ == '__main__':
    unittest.main()
