#!/usr/bin/env python3
"""WAL-213 · the supersession contract, as tests.

Two suites, and the split is the point.

**A. The contract** — pure structure, no corpus, runs anywhere. Every invariant the ticket names,
plus a mutation check for each guard: a guard that cannot be shown to go RED for the right reason
is a guard nobody has tested, only exercised.

**B. The real population** — the 17 recovered regions of Toán 4 Bài 61 p081-083, read from the
committed census `data/wal213-bai61-population.json`. Round 7's structural finding was that *the
tests were not missing, the populations were*: the `titleCase` tests were fed only their own
precondition and stayed green for four rounds. So this suite is fed the real distribution — 4 that
resolve, 13 that do not — and carries a **population-adequacy guard** that goes red when the
population degenerates, including when it is empty.

The census carries **no SGK text, no readings, no values** (D4). Value-level behaviour is asserted
in `test_supersession_population.py`, which needs the gitignored corpus and says so out loud.
"""
import copy
import json
import os
import sys
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', 'corpus'))

from repair import model                                                     # noqa: E402
from repair import supersession as SUP                                       # noqa: E402
from repair.model import Disposition, Observation, RepairCandidate, ValidationResult, Verdict  # noqa: E402

CENSUS = os.path.join(HERE, 'data', 'wal213-bai61-population.json')

BLOCK = '07-sgk-mau-7:p032:tc2-p1:009'


# ---------------------------------------------------------------- builders (synthetic, structural)
def obs(value, bbox, source='apple-vision-page-v1', block=BLOCK):
    return Observation(block_id=block, source=source, value=value, provenance=dict(bbox=bbox))


def evidence(key='r000', box=(0.10, 0.10, 0.30, 0.20), scales=(6.0, 10.0), stacking=6.0):
    return SUP.RegionEvidence(region_key=key, boxes=dict(numerator=box, denominator=box),
                              agreeing_scales=dict(numerator=scales, denominator=scales),
                              stacking_scale=stacking, detector='test', bar=(0.1, 0.15, 0.2, 0.001))


def candidate(superseded, value='3/10', block=BLOCK):
    return RepairCandidate(block_id=block, failure_class='DIGIT_LOSS',
                           original_observations=superseded, proposed_value=value,
                           rule_id='recognition.recrop-supersede-v1',
                           supporting_signals=(model.Signal('B.region_stacking', 'supports', 1.0),),
                           provenance=dict(book='07-sgk-mau-7', page=32, bbox=(0.1, 0.1, 0.3, 0.2)))


def supersession(superseded=None, value='3/10', key='r000', box=(0.10, 0.10, 0.30, 0.20),
                 block=BLOCK, engine='apple-vision-crop-v1'):
    superseded = superseded or (obs('1O', (0.12, 0.12, 0.20, 0.18)),)
    ev = evidence(key, box)
    new = Observation(block_id=block, source=engine, value=value,
                      provenance=dict(bbox=ev.envelope, engine=engine))
    return SUP.Supersession(block_id=block, superseded=superseded, superseding=new, engine=engine,
                            region=ev, candidate=candidate(superseded, value, block),
                            failure_class='DIGIT_LOSS', reason='test')


# ================================================================= A · the contract
class TestRegionEvidence(unittest.TestCase):
    def test_an_empty_evidence_bag_does_not_construct(self):
        """ABSENCE CANNOT SATISFY A POSITIVE OBLIGATION, applied to the evidence itself."""
        with self.assertRaises(SUP.SupersessionError):
            SUP.RegionEvidence(region_key='r000')

    def test_evidence_with_only_scales_constructs_and_only_boxes_constructs(self):
        """The MUTATION check for the rule above: it must refuse the empty bag and nothing else."""
        self.assertTrue(SUP.RegionEvidence(region_key='r0', agreeing_scales=dict(n=(6.0, 10.0))))
        self.assertTrue(SUP.RegionEvidence(region_key='r0', boxes=dict(n=(0, 0, 1, 1))))

    def test_stacked_is_false_without_a_stacking_scale(self):
        self.assertFalse(evidence(stacking=None).stacked)
        self.assertTrue(evidence(stacking=6.0).stacked)

    def test_covers_is_area_of_the_envelope(self):
        ev = evidence(box=(0.0, 0.0, 1.0, 1.0))
        self.assertAlmostEqual(ev.covers((0.0, 0.0, 0.5, 1.0)), 1.0)
        self.assertAlmostEqual(ev.covers((0.5, 0.0, 1.5, 1.0)), 0.5)
        self.assertEqual(ev.covers(None), 0.0)


class TestSupersessionType(unittest.TestCase):
    def test_it_needs_something_to_supersede(self):
        """A recovery with nothing to replace is an ADDITION and may not borrow the authority of a
        replacement."""
        ev = evidence()
        new = Observation(block_id=BLOCK, source='apple-vision-crop-v1', value='3/10',
                          provenance=dict(bbox=ev.envelope))
        with self.assertRaises(SUP.SupersessionError):
            SUP.Supersession(block_id=BLOCK, superseded=(), superseding=new,
                             engine='apple-vision-crop-v1', region=ev,
                             candidate=candidate((obs('x', (0, 0, 1, 1)),)))

    def test_a_source_cannot_supersede_its_own_observation(self):
        with self.assertRaises(SUP.SupersessionError):
            supersession(engine='apple-vision-page-v1')

    def test_the_engine_must_match_the_superseding_observation(self):
        ev = evidence()
        new = Observation(block_id=BLOCK, source='engine-a', value='3/10',
                          provenance=dict(bbox=ev.envelope))
        with self.assertRaises(SUP.SupersessionError):
            SUP.Supersession(block_id=BLOCK, superseded=(obs('1O', (0.12, 0.12, 0.2, 0.18)),),
                             superseding=new, engine='engine-b', region=ev,
                             candidate=candidate((obs('1O', (0.12, 0.12, 0.2, 0.18)),)))

    def test_the_source_observation_is_carried_whole_and_never_written_to(self):
        """«Never overwrite a source observation» is structural: the exact object goes in and the
        exact object, unchanged, comes out."""
        original = obs('1O', (0.12, 0.12, 0.20, 0.18))
        s = supersession((original,))
        self.assertIs(s.superseded[0], original)
        self.assertEqual(s.superseded[0].value, '1O')
        with self.assertRaises(Exception):
            s.superseded[0].provenance['bbox'] = (0, 0, 0, 0)
        with self.assertRaises(Exception):
            object.__setattr__  # sanity: frozen dataclass
            s.superseded[0].value = 'edited'

    def test_full_coverage_gives_SUPERSEDED_and_partial_gives_CONFLICT(self):
        inside = obs('1O', (0.12, 0.12, 0.20, 0.18))
        self.assertEqual(supersession((inside,)).disposition, Disposition.SUPERSEDED)
        self.assertEqual(supersession((inside,)).coverage, SUP.FULL)
        straddling = obs('0) 1 3', (0.02, 0.12, 0.20, 0.18))       # starts left of the crop
        s = supersession((straddling,))
        self.assertEqual(s.coverage, SUP.PARTIAL)
        self.assertEqual(s.disposition, Disposition.CONFLICT)
        self.assertFalse(s.resolved)
        self.assertIn('overwriting', s.residual_reason)

    def test_disposition_cannot_be_declared_clean_by_a_caller(self):
        """There is no argument, field or setter by which PARTIAL becomes SUPERSEDED."""
        s = supersession((obs('0) 1 3', (0.02, 0.12, 0.20, 0.18)),))
        self.assertNotIn('disposition', {f.name for f in __import__('dataclasses').fields(s)})
        with self.assertRaises(Exception):
            s.disposition = Disposition.SUPERSEDED

    def test_an_observation_with_no_bbox_covers_nothing(self):
        """Fail closed: a replacement we cannot point at on the page has not been shown to cover
        anything, so it may not stand alone."""
        blind = Observation(block_id=BLOCK, source='apple-vision-page-v1', value='1O')
        s = supersession((blind,))
        self.assertEqual(s.coverage, SUP.NONE)
        self.assertEqual(s.disposition, Disposition.CONFLICT)

    def test_servable_is_never_true_and_is_not_a_field(self):
        s = supersession()
        self.assertFalse(s.servable)
        self.assertNotIn('servable', {f.name for f in __import__('dataclasses').fields(s)})
        d = s.to_json()
        d['servable'] = True
        with self.assertRaises(SUP.TrustEscalation):
            SUP.Supersession.from_json(d)

    def test_TRUSTED_is_unreachable(self):
        s = supersession()
        self.assertIn(s.disposition, (Disposition.SUPERSEDED, Disposition.CONFLICT))
        d = s.to_json()
        d['disposition'] = Disposition.TRUSTED
        with self.assertRaises(SUP.TrustEscalation):
            SUP.Supersession.from_json(d)

    def test_there_is_no_constructor_from_a_presentation_form(self):
        for name in ('from_text', 'from_line', 'from_reading', 'from_latex', 'from_summary'):
            self.assertFalse(hasattr(SUP.Supersession, name), name)
        with self.assertRaises(SUP.SupersessionError):
            SUP.Supersession.from_json('3/10')

    def test_from_json_requires_the_whole_trace(self):
        full = supersession().to_json()
        for key in ('blockId', 'engine', 'region', 'superseded', 'superseding', 'candidate'):
            d = copy.deepcopy(full)
            d.pop(key)
            with self.assertRaises(SUP.SupersessionError, msg=key):
                SUP.Supersession.from_json(d)

    def test_block_projection_carries_no_value_on_either_side(self):
        b = supersession().to_block_json()
        blob = json.dumps(b, ensure_ascii=False)
        for forbidden in ('3/10', '1O', 'proposedValue', 'text', 'value', 'supersededValue'):
            self.assertNotIn(forbidden, blob, forbidden)
        self.assertEqual(b['supersededObservations'], 1)
        self.assertFalse(b['servable'])


class TestRoundTrip(unittest.TestCase):
    def test_a_round_trip_changes_nothing(self):
        for s in (supersession(), supersession((obs('0) 1 3', (0.02, 0.12, 0.20, 0.18)),))):
            before = s.to_json()
            after = SUP.Supersession.from_json(before).to_json()
            self.assertEqual(before, after)
            self.assertTrue(SUP.assert_supersession_not_strengthened(before, after))

    def test_serialisation_may_not_strengthen_the_disposition(self):
        before = supersession((obs('0) 1 3', (0.02, 0.12, 0.20, 0.18)),)).to_json()
        after = copy.deepcopy(before)
        after['disposition'] = Disposition.SUPERSEDED
        with self.assertRaises(SUP.TrustEscalation):
            SUP.assert_supersession_not_strengthened(before, after)

    def test_the_audit_set_may_not_shrink(self):
        """A superseded observation that disappears across a round trip is a contradiction that
        became invisible — worse than one never recorded, because the record now looks complete."""
        before = supersession((obs('a', (0.12, 0.12, 0.16, 0.18)),
                               obs('b', (0.17, 0.12, 0.20, 0.18)))).to_json()
        after = copy.deepcopy(before)
        after['superseded'] = after['superseded'][:1]
        with self.assertRaises(SUP.TrustEscalation):
            SUP.assert_supersession_not_strengthened(before, after)

    def test_resolved_servable_and_coverage_may_not_improve(self):
        before = supersession((obs('0) 1 3', (0.02, 0.12, 0.20, 0.18)),)).to_json()
        for key, value in (('resolved', True), ('servable', True), ('coverage', SUP.FULL)):
            after = copy.deepcopy(before)
            after[key] = value
            with self.assertRaises(SUP.TrustEscalation, msg=key):
                SUP.assert_supersession_not_strengthened(before, after)

    def test_the_guard_passes_when_nothing_strengthened(self):
        """MUTATION check for the guard: it must accept an honest round trip, or it is a guard that
        only ever says no."""
        before = supersession().to_json()
        after = copy.deepcopy(before)
        after['reason'] = 'reworded'
        self.assertTrue(SUP.assert_supersession_not_strengthened(before, after))


class TestObservationSet(unittest.TestCase):
    def _set(self, *observations):
        return SUP.ObservationSet(BLOCK, observations)

    def test_exactly_one_current_observation_per_region(self):
        destroyed = obs('1O', (0.12, 0.12, 0.20, 0.18))
        st = self._set(destroyed).with_supersession(supersession((destroyed,)))
        r = st.resolve()
        cur = r.current_for('r000')
        self.assertEqual(cur.value, '3/10')
        self.assertEqual(cur.source, 'apple-vision-crop-v1')
        self.assertEqual([o.value for o in r.superseded], ['1O'])
        self.assertEqual(list(r.conflicted), [])
        self.assertTrue(r.usable)

    def test_the_superseded_observation_is_invisible_to_a_validator_and_visible_to_an_auditor(self):
        destroyed = obs('1O', (0.12, 0.12, 0.20, 0.18))
        st = self._set(destroyed).with_supersession(supersession((destroyed,)))
        r = st.resolve()
        self.assertNotIn(destroyed.observation_id, [o.observation_id for o in r.current])
        self.assertIn(destroyed.observation_id, [o.observation_id for o in r.audit_only])
        trail = json.dumps(st.audit_trail(), ensure_ascii=False)
        self.assertIn('1O', trail)

    def test_a_partial_supersession_removes_BOTH_readings_and_fails_the_block_closed(self):
        """The whole reason this contract exists: a block holding an undecided contradiction has no
        text anybody may name, so neither half is current."""
        straddling = obs('0) 1 3', (0.02, 0.12, 0.20, 0.18))
        s = supersession((straddling,))
        st = self._set(straddling).with_supersession(s)
        r = st.resolve()
        self.assertFalse(r.usable)
        self.assertEqual(len(r.current), 0)
        self.assertEqual({o.value for o in r.conflicted}, {'0) 1 3', '3/10'})
        with self.assertRaises(SUP.SupersessionConflict):
            r.current_for('r000')

    def test_two_regions_may_together_supersede_one_observation(self):
        """The real Bài 61 shape: `0) 1 3` is covered by two recovered regions. Coverage is combined
        by AREA, never by order, and it still has to reach FULL."""
        wide = obs('12', (0.10, 0.10, 0.30, 0.20))
        left = supersession((wide,), value='8/14', key='rA', box=(0.10, 0.10, 0.20, 0.20))
        right = supersession((wide,), value='2/7', key='rB', box=(0.20, 0.10, 0.30, 0.20))
        st = self._set(wide).with_supersession(left).with_supersession(right)
        r = st.resolve()
        self.assertTrue(r.usable)
        self.assertEqual([o.value for o in r.superseded], ['12'])
        self.assertEqual(sorted(o.value for o in r.current), ['2/7', '8/14'])

    def test_two_regions_that_do_not_together_cover_it_are_a_conflict(self):
        wide = obs('0) 1 3', (0.00, 0.10, 0.30, 0.20))
        left = supersession((wide,), value='8/14', key='rA', box=(0.10, 0.10, 0.20, 0.20))
        right = supersession((wide,), value='2/7', key='rB', box=(0.20, 0.10, 0.30, 0.20))
        st = self._set(wide).with_supersession(left).with_supersession(right)
        r = st.resolve()
        self.assertFalse(r.usable)
        self.assertEqual(len(r.current), 0)

    def test_two_overlapping_replacements_are_refused_not_ordered(self):
        wide = obs('12', (0.10, 0.10, 0.30, 0.20))
        a = supersession((wide,), value='8/14', key='rA', box=(0.10, 0.10, 0.25, 0.20))
        b = supersession((wide,), value='2/7', key='rB', box=(0.15, 0.10, 0.30, 0.20))
        st = self._set(wide).with_supersession(a).with_supersession(b)
        with self.assertRaises(SUP.SupersessionConflict):
            st.resolve()

    def test_superseding_an_observation_the_block_never_made_is_refused(self):
        stranger = obs('elsewhere', (0.5, 0.5, 0.6, 0.6))
        with self.assertRaises(SUP.SupersessionError):
            self._set(obs('1O', (0.12, 0.12, 0.20, 0.18))).with_supersession(supersession((stranger,)))

    def test_resolution_is_conservative(self):
        a = obs('1O', (0.12, 0.12, 0.20, 0.18))
        b = obs('prose', (0.40, 0.40, 0.60, 0.45))
        st = self._set(a, b).with_supersession(supersession((a,)))
        self.assertTrue(st.assert_conserved())
        r = st.resolve()
        self.assertEqual(len(r.current) + len(r.superseded) + len(r.conflicted),
                         len(st.observations))

    def test_with_supersession_does_not_mutate_the_set_it_came_from(self):
        a = obs('1O', (0.12, 0.12, 0.20, 0.18))
        st = self._set(a)
        st2 = st.with_supersession(supersession((a,)))
        self.assertEqual(len(st.supersessions), 0)
        self.assertEqual(len(st2.supersessions), 1)
        self.assertEqual(len(st.resolve().superseded), 0)

    def test_a_cycle_raises(self):
        """A -> B -> A. Impossible within one engine (a source may not supersede itself), so the
        cycle is built across two, which is exactly how one would arise in practice: a second
        recogniser «restoring» what the first replaced."""
        a = Observation(block_id=BLOCK, source='apple-vision-page-v1', value='p',
                        provenance=dict(bbox=(0.10, 0.10, 0.20, 0.20)))
        evb = evidence('rB', (0.10, 0.10, 0.20, 0.20))
        b = Observation(block_id=BLOCK, source='engine-b', value='q',
                        provenance=dict(bbox=evb.envelope))
        first = SUP.Supersession(block_id=BLOCK, superseded=(a,), superseding=b, engine='engine-b',
                                 region=evb, candidate=candidate((a,), 'q'))
        eva = evidence('rA', (0.10, 0.10, 0.20, 0.20))
        back = SUP.Supersession(block_id=BLOCK, superseded=(b,), superseding=a,
                                engine='apple-vision-page-v1', region=eva,
                                candidate=candidate((b,), 'p'))
        st = SUP.ObservationSet(BLOCK, (a, b), (first, back))
        with self.assertRaises(SUP.SupersessionConflict):
            st.resolve()

    def test_the_acyclic_check_accepts_an_honest_chain(self):
        """MUTATION check: a chain A -> B -> C must NOT raise, or the cycle test passes for the
        wrong reason."""
        a = Observation(block_id=BLOCK, source='apple-vision-page-v1', value='p',
                        provenance=dict(bbox=(0.10, 0.10, 0.20, 0.20)))
        evb = evidence('rB', (0.10, 0.10, 0.20, 0.20))
        b = Observation(block_id=BLOCK, source='engine-b', value='q',
                        provenance=dict(bbox=evb.envelope))
        evc = evidence('rC', (0.10, 0.10, 0.20, 0.20))
        c = Observation(block_id=BLOCK, source='engine-c', value='r',
                        provenance=dict(bbox=evc.envelope))
        first = SUP.Supersession(block_id=BLOCK, superseded=(a,), superseding=b, engine='engine-b',
                                 region=evb, candidate=candidate((a,), 'q'))
        second = SUP.Supersession(block_id=BLOCK, superseded=(b,), superseding=c, engine='engine-c',
                                  region=evc, candidate=candidate((b,), 'r'))
        r = SUP.ObservationSet(BLOCK, (a, b, c), (first, second)).resolve()
        self.assertEqual([o.value for o in r.current], ['r'])
        self.assertEqual(sorted(o.value for o in r.superseded), ['p', 'q'])


class TestObligations(unittest.TestCase):
    """The guards, and a mutation check for each: a guard must be shown to go RED for the right
    reason, not merely to have been called."""

    def test_an_empty_population_FAILS(self):
        with self.assertRaises(SUP.PopulationInadequate):
            SUP.assert_population_adequate([])

    def test_a_population_of_only_resolvable_cases_FAILS(self):
        clean = [supersession() for _ in range(5)]
        with self.assertRaises(SUP.PopulationInadequate):
            SUP.assert_population_adequate(clean)

    def test_a_population_of_only_unresolvable_cases_FAILS(self):
        dirty = [supersession((obs('0) 1 3', (0.02, 0.12, 0.20, 0.18)),)) for _ in range(5)]
        with self.assertRaises(SUP.PopulationInadequate):
            SUP.assert_population_adequate(dirty)

    def test_a_population_where_nothing_changes_FAILS(self):
        same = supersession((obs('3/10', (0.12, 0.12, 0.20, 0.18)),), value='3/10')
        other = supersession((obs('3/10', (0.02, 0.12, 0.20, 0.18)),), value='3/10')
        self.assertFalse(same.changed)
        with self.assertRaises(SUP.PopulationInadequate):
            SUP.assert_population_adequate([same, other])

    def test_a_population_containing_both_kinds_PASSES(self):
        """The mutation check: the guard must accept an adequate population, or it says no to
        everything and proves nothing."""
        self.assertTrue(SUP.assert_population_adequate(
            [supersession(), supersession((obs('0) 1 3', (0.02, 0.12, 0.20, 0.18)),))]))

    def test_no_supersession_needed_cannot_be_satisfied_by_emptiness(self):
        with self.assertRaises(SUP.PopulationInadequate):
            SUP.assert_no_supersession_needed([], [])

    def test_no_supersession_needed_passes_only_with_a_real_population(self):
        self.assertTrue(SUP.assert_no_supersession_needed([obs('x', (0, 0, 1, 1))], []))
        with self.assertRaises(SUP.SupersessionError):
            SUP.assert_no_supersession_needed([obs('x', (0, 0, 1, 1))], [supersession()])


class TestLedgerBridge(unittest.TestCase):
    def test_it_writes_round_five_ledger_rows_chained(self):
        a = obs('1O', (0.12, 0.12, 0.20, 0.18))
        first, second = SUP.ledger_entries(supersession((a,)))
        self.assertEqual(first.disposition, Disposition.SUPERSEDED)
        self.assertEqual(second.disposition, Disposition.REPAIRED_CANDIDATE)
        self.assertEqual(second.prior_entry_id, first.entry_id)
        self.assertNotIn(Disposition.TRUSTED, (first.disposition, second.disposition))

    def test_a_partial_supersession_writes_CONFLICT_not_SUPERSEDED(self):
        first, _ = SUP.ledger_entries(supersession((obs('0) 1 3', (0.02, 0.12, 0.20, 0.18)),)))
        self.assertEqual(first.disposition, Disposition.CONFLICT)
        self.assertTrue(any('overwriting' in r for r in first.reasons))

    def test_the_rows_survive_the_existing_ledger_reader(self):
        """No fourth provenance universe: `ledger.entry_from_json` already parses these."""
        from repair import ledger as L
        for e in SUP.ledger_entries(supersession((obs('1O', (0.12, 0.12, 0.20, 0.18)),))):
            back = L.entry_from_json(e.to_json())
            self.assertEqual(back.entry_id, e.entry_id)
            self.assertEqual(back.disposition, e.disposition)

    def test_assert_not_trusted_refuses_anything_that_is_not_this_relation(self):
        class Fake:
            servable = True
            disposition = Disposition.TRUSTED
            validation = None
        with self.assertRaises(SUP.TrustEscalation):
            SUP.assert_not_trusted(Fake())


class TestVocabularyIsReused(unittest.TestCase):
    """No fourth provenance universe. Every type this module holds is round 5's own."""

    def test_the_types_are_the_round_five_types(self):
        s = supersession()
        self.assertIsInstance(s.superseded[0], model.Observation)
        self.assertIsInstance(s.superseding, model.Observation)
        self.assertIsInstance(s.candidate, model.RepairCandidate)
        self.assertIs(SUP.Disposition, model.Disposition)

    def test_every_disposition_it_can_produce_is_in_the_frozen_set(self):
        for d in (Disposition.SUPERSEDED, Disposition.CONFLICT):
            self.assertIn(d, Disposition.ALL)
            self.assertNotIn(d, Disposition.SERVABLE)

    def test_a_validation_result_must_be_the_round_five_type(self):
        with self.assertRaises(SUP.SupersessionError):
            SUP.Supersession(block_id=BLOCK, superseded=(obs('a', (0.12, 0.12, 0.2, 0.18)),),
                             superseding=Observation(block_id=BLOCK, source='e', value='b',
                                                     provenance=dict(bbox=(0.1, 0.1, 0.3, 0.2))),
                             engine='e', region=evidence(),
                             candidate=candidate((obs('a', (0.12, 0.12, 0.2, 0.18)),)),
                             validation={'verdict': 'validated'})

    def test_a_validated_supersession_still_is_not_trusted(self):
        a = obs('1O', (0.12, 0.12, 0.20, 0.18))
        ev = evidence()
        s = SUP.Supersession(
            block_id=BLOCK, superseded=(a,),
            superseding=Observation(block_id=BLOCK, source='apple-vision-crop-v1', value='3/10',
                                    provenance=dict(bbox=ev.envelope)),
            engine='apple-vision-crop-v1', region=ev, candidate=candidate((a,)),
            validation=ValidationResult('test.validator-v1', Verdict.VALIDATED))
        self.assertFalse(s.servable)
        self.assertEqual(s.disposition, Disposition.SUPERSEDED)
        self.assertTrue(SUP.assert_not_trusted(s))


# ---------------------------------------------------------------- end to end
class TestEndToEnd(unittest.TestCase):
    """WAL-213 requires the relation to be expressible «recogniser output, block record, trust
    decision, and whatever the app eventually consumes». These are the joints."""

    def _repair(self, sup=None, resolved=True):
        from repair.validated import ValidatedRepair, grounding_for
        superseded = (obs('1O', (0.12, 0.12, 0.20, 0.18)) if resolved
                      else obs('0) 1 3', (0.02, 0.12, 0.20, 0.18)),)
        superseded = superseded if isinstance(superseded, tuple) else (superseded,)
        s = sup or supersession(superseded)
        cand = s.candidate
        val = ValidationResult('wal213.region-stacking-v1', Verdict.VALIDATED)
        return ValidatedRepair(
            block_id=BLOCK, failure_class='DIGIT_LOSS', original_observations=s.superseded,
            candidate=cand, validation=val, source_grounding=grounding_for(cand),
            repair_method=cand.rule_id, validator_id='wal213.region-stacking-v1',
            validator_version='v1', repair_version='repair-v1/' + cand.rule_id,
            caps=('trust_gate:founder_decision_absent',), supersession=s), s

    def test_a_validated_repair_can_carry_the_relation_and_is_still_not_trusted(self):
        vr, s = self._repair()
        self.assertIs(vr.supersession, s)
        self.assertFalse(vr.servable)
        self.assertEqual(vr.disposition, Disposition.VALIDATED_REPAIR)

    def test_a_repair_without_one_reads_back_exactly_as_before(self):
        """Every round-5/6 repair has no supersession. The field is optional and last so an existing
        record is unchanged by this work."""
        from repair.validated import ValidatedRepair
        vr, _ = self._repair()
        d = vr.to_json()
        d['supersession'] = None
        back = ValidatedRepair.from_json(d)
        self.assertIsNone(back.supersession)
        self.assertIsNone(back.to_block_json()['supersedes'])

    def test_the_relation_survives_the_repair_round_trip(self):
        from repair.validated import ValidatedRepair
        vr, _ = self._repair()
        before = json.loads(json.dumps(vr.to_json(), ensure_ascii=False, default=list))
        after = json.loads(json.dumps(ValidatedRepair.from_json(before).to_json(),
                                      ensure_ascii=False, default=list))
        self.assertEqual(before, after)

    def test_dropping_the_relation_across_a_round_trip_is_laundering(self):
        from repair.validated import assert_repair_not_strengthened
        from semantic.graph import ProvenanceLaundering
        vr, _ = self._repair()
        before = vr.to_json()
        after = copy.deepcopy(before)
        after['supersession'] = None
        with self.assertRaises(ProvenanceLaundering):
            assert_repair_not_strengthened(before, after)

    def test_strengthening_the_relation_inside_the_repair_is_caught(self):
        from repair.validated import assert_repair_not_strengthened
        vr, _ = self._repair(resolved=False)
        before = vr.to_json()
        self.assertEqual(before['supersession']['disposition'], Disposition.CONFLICT)
        after = copy.deepcopy(before)
        after['supersession']['disposition'] = Disposition.SUPERSEDED
        after['supersession']['resolved'] = True
        with self.assertRaises(SUP.TrustEscalation):
            assert_repair_not_strengthened(before, after)

    def test_the_honest_round_trip_still_passes(self):
        """Mutation check for the two above."""
        from repair.validated import assert_repair_not_strengthened
        vr, _ = self._repair()
        before = vr.to_json()
        self.assertTrue(assert_repair_not_strengthened(before, copy.deepcopy(before)))

    def test_a_look_alike_supersession_is_refused(self):
        """No fourth provenance universe. A dict that serialises the same way, or a duck-typed
        stand-in that answers every question, is still not the type — and a repair built on one
        would carry a relation nothing else in the framework can re-decide."""
        from repair.validated import RepairIntegrityError, ValidatedRepair, grounding_for
        vr, s = self._repair()
        base = dict(block_id=vr.block_id, failure_class=vr.failure_class,
                    original_observations=vr.original_observations, candidate=vr.candidate,
                    validation=vr.validation, source_grounding=grounding_for(vr.candidate),
                    repair_method=vr.repair_method, validator_id=vr.validator_id,
                    validator_version=vr.validator_version, repair_version=vr.repair_version)

        class LookAlike:
            block_id = BLOCK
            servable = False
            disposition = Disposition.SUPERSEDED
            validation = None

            def to_json(self):
                return s.to_json()

            def to_block_json(self):
                return s.to_block_json()

        for fake in (s.to_json(), LookAlike(), 'a supersession'):
            with self.assertRaises(RepairIntegrityError, msg=type(fake).__name__):
                ValidatedRepair(**base, supersession=fake)

    def test_a_supersession_for_another_block_is_refused(self):
        from repair.validated import RepairIntegrityError, ValidatedRepair, grounding_for
        vr, _ = self._repair()
        elsewhere = '07-sgk-mau-7:p032:tc2-p1:999'
        other = supersession((obs('1O', (0.12, 0.12, 0.20, 0.18), block=elsewhere),),
                             block=elsewhere)
        with self.assertRaises(RepairIntegrityError):
            ValidatedRepair(block_id=vr.block_id, failure_class=vr.failure_class,
                            original_observations=vr.original_observations, candidate=vr.candidate,
                            validation=vr.validation, source_grounding=grounding_for(vr.candidate),
                            repair_method=vr.repair_method, validator_id=vr.validator_id,
                            validator_version=vr.validator_version,
                            repair_version=vr.repair_version, supersession=other)

    def test_the_block_projection_reaches_the_bridge_and_carries_no_value(self):
        import tsl_to_lesson_document as br
        vr, _ = self._repair()
        block = dict(id=BLOCK, repair=vr.to_block_json())
        out = br.repair_of(block)
        self.assertIsNotNone(out['supersedes'])
        self.assertEqual(out['supersedes']['supersededObservations'], 1)
        blob = json.dumps(out['supersedes'], ensure_ascii=False)
        self.assertNotIn('3/10', blob)
        self.assertNotIn('1O', blob)

    def test_the_bridge_refuses_a_supersession_carrying_a_reading(self):
        import tsl_to_lesson_document as br
        vr, _ = self._repair()
        for key in ('supersededValue', 'supersedingValue', 'text', 'value', 'proposedValue'):
            rec = vr.to_block_json()
            rec['supersedes'] = dict(rec['supersedes'])
            rec['supersedes'][key] = '3/10'
            with self.assertRaises(br.BridgeRefusal, msg=key):
                br.repair_of(dict(id=BLOCK, repair=rec))

    def test_the_bridge_refuses_a_full_record_riding_on_a_block(self):
        import tsl_to_lesson_document as br
        vr, s = self._repair()
        rec = vr.to_block_json()
        rec['supersession'] = s.to_json()
        with self.assertRaises(br.BridgeRefusal):
            br.repair_of(dict(id=BLOCK, repair=rec))

    def test_the_bridge_refuses_a_trusted_or_servable_supersession(self):
        import tsl_to_lesson_document as br
        vr, _ = self._repair()
        for patch in ({'disposition': Disposition.TRUSTED}, {'servable': True},
                      {'disposition': Disposition.VALIDATED_REPAIR}):
            rec = vr.to_block_json()
            rec['supersedes'] = {**rec['supersedes'], **patch}
            with self.assertRaises(br.BridgeRefusal, msg=str(patch)):
                br.repair_of(dict(id=BLOCK, repair=rec))

    def test_the_bridge_accepts_the_honest_projection(self):
        """Mutation check: the allowlist must let the real shape through."""
        import tsl_to_lesson_document as br
        vr, _ = self._repair(resolved=False)
        out = br.repair_of(dict(id=BLOCK, repair=vr.to_block_json()))
        self.assertEqual(out['supersedes']['disposition'], Disposition.CONFLICT)


# ================================================================= B · the real population
def load_census():
    with open(CENSUS) as fh:
        return json.load(fh)


class TestRealPopulation(unittest.TestCase):
    """The 17 recovered regions of Toán 4 Bài 61, from the committed census.

    Round 7: *the tests were not missing, the populations were.* These assertions are made against
    the measured distribution, not against a fixture built to satisfy them.
    """

    @classmethod
    def setUpClass(cls):
        cls.census = load_census()
        cls.regions = cls.census['regions']
        cls.blocks = cls.census['blocks']

    def test_the_census_is_the_real_run(self):
        src = self.census['source']
        self.assertEqual(src['book'], '04-sgk-toan-4-tap-hai')
        self.assertEqual(src['pages'], [81, 82, 83])
        self.assertEqual(src['scales'], [6.0, 10.0, 14.0, 20.0])
        self.assertEqual(len(src['studySha256']), 64)

    def test_the_population_is_ADEQUATE_and_the_guard_would_say_so(self):
        """The adequacy obligation, evaluated on the real distribution rather than asserted."""
        self.assertGreaterEqual(len(self.regions), 1)
        resolved = [r for r in self.regions if r['resolved']]
        unresolved = [r for r in self.regions if not r['resolved'] and r.get('kind') != 'ADDITION']
        changed = [r for r in self.regions if r.get('changed')]
        self.assertTrue(resolved, 'no resolvable supersession in the real population')
        self.assertTrue(unresolved, 'no unresolvable supersession in the real population')
        self.assertTrue(changed, 'no supersession in the real population changes the value')

    def test_the_measured_distribution_is_17_regions_4_resolved_13_refused(self):
        t = self.census['totals']
        self.assertEqual(t['regions'], 17)
        self.assertEqual(t['supersessions'], 17)
        self.assertEqual(t['resolved'], 4)
        self.assertEqual(t['refused'], 13)
        self.assertEqual(t['additions'], 0)
        self.assertEqual(sum(1 for r in self.regions if r['coverage'] == SUP.FULL), 4)
        self.assertEqual(sum(1 for r in self.regions if r['coverage'] == SUP.PARTIAL), 13)

    def test_the_failing_case_is_in_the_population(self):
        """The case this contract exists for: a recovered reading whose destroyed observation
        carries other printed content, so it cannot stand alone."""
        partial = [r for r in self.regions if r['coverage'] == SUP.PARTIAL]
        self.assertTrue(partial)
        self.assertTrue(all(r['disposition'] == Disposition.CONFLICT for r in partial))
        self.assertTrue(all(not r['resolved'] for r in partial))
        self.assertTrue(any(r['supersededObservations'] >= 1 for r in partial))

    def test_every_class_of_recognition_failure_is_represented(self):
        classes = {r['failureClass'] for r in self.regions if r.get('failureClass')}
        self.assertEqual(classes, {'DIGIT_LOSS', 'SEGMENTATION', 'FRACTION_STRUCTURE'})

    def test_nothing_in_the_real_population_is_servable_or_trusted(self):
        for r in self.regions:
            self.assertFalse(r['servable'], r['regionKey'])
            self.assertIn(r['disposition'], (Disposition.SUPERSEDED, Disposition.CONFLICT, None))
            self.assertNotEqual(r['disposition'], Disposition.TRUSTED)

    def test_a_resolved_supersession_had_independent_agreement_behind_it(self):
        for r in self.regions:
            if r['resolved']:
                self.assertGreaterEqual(r['agreeingScales'], 2, r['regionKey'])
                self.assertTrue(r['stacked'], r['regionKey'])

    def test_the_contract_refuses_blocks_rather_than_serving_a_contradiction(self):
        refused = [b for b in self.blocks if b['supersedeVerdict'] == 'REFUSED_UNRESOLVED_SUPERSESSION']
        self.assertEqual(len(refused), 8)
        self.assertTrue(all(b['refused'] > 0 for b in refused))
        self.assertTrue(all(not b['supersedeProposed'] for b in refused))

    def test_the_honest_number_no_recovered_digit_became_a_repaired_block(self):
        """`10 -> 10, delta 0` — STILL. Recorded as an assertion so that the day it changes, this
        test fails and somebody has to write down why."""
        before = sum(1 for b in self.blocks if b['beforeProposed'])
        add = sum(1 for b in self.blocks if b['addProposed'])
        supersede = sum(1 for b in self.blocks if b['supersedeProposed'])
        self.assertEqual((before, add, supersede), (2, 3, 2))

    def test_the_ADD_path_produced_a_proposal_the_contract_refuses(self):
        """The one block round 7's ADD path changed is the one the contract now refuses: the change
        was a concatenation of two contradictory readings, not a repair."""
        both = [b for b in self.blocks
                if b['addProposed'] and not b['beforeProposed']]
        self.assertEqual(len(both), 1)
        self.assertEqual(both[0]['supersedeVerdict'], 'REFUSED_UNRESOLVED_SUPERSESSION')

    def test_the_census_carries_no_SGK_text(self):
        """D4. A census that leaked a reading would be a textbook derivative in git."""
        blob = json.dumps(self.census, ensure_ascii=False)
        for key in ('text', 'value', 'proposedValue', 'baselineValue', 'supersededValue', 'bbox'):
            self.assertNotIn(f'"{key}"', blob, key)
        self.assertNotIn('/', ''.join(str(r.get('changed')) for r in self.regions))


class TestPopulationAdequacyGuardBites(unittest.TestCase):
    """The mutation check for the population itself.

    Round 7's `fixture_lineage` L5 printed `0/0 present · PASS`. The obligation here is that the
    real-population suite could not have gone green on a degenerate census, so each degeneration is
    applied and the guard is required to notice.
    """

    def setUp(self):
        self.census = load_census()

    def _rels(self, regions):
        """Rebuild guard-shaped objects from census rows. The census carries no values, so a
        stand-in observation is used for `changed`; the coverage and resolution come from the
        measurement."""
        class Row:
            def __init__(self, r):
                self.resolved = r['resolved']
                self.changed = bool(r.get('changed'))
                self.coverage = r['coverage']
        return [Row(r) for r in regions]

    def test_the_real_census_passes_the_guard(self):
        self.assertTrue(SUP.assert_population_adequate(self._rels(self.census['regions']),
                                                       label='bai61'))

    def test_an_emptied_census_FAILS(self):
        with self.assertRaises(SUP.PopulationInadequate):
            SUP.assert_population_adequate(self._rels([]), label='bai61-emptied')

    def test_a_census_with_the_refusals_removed_FAILS(self):
        kept = [r for r in self.census['regions'] if r['resolved']]
        self.assertTrue(kept)
        with self.assertRaises(SUP.PopulationInadequate):
            SUP.assert_population_adequate(self._rels(kept), label='bai61-only-clean')

    def test_a_census_with_the_clean_cases_removed_FAILS(self):
        kept = [r for r in self.census['regions'] if not r['resolved']]
        self.assertTrue(kept)
        with self.assertRaises(SUP.PopulationInadequate):
            SUP.assert_population_adequate(self._rels(kept), label='bai61-only-refused')


if __name__ == '__main__':
    unittest.main(verbosity=2)
