#!/usr/bin/env python3
"""Round 6 · Workstream C — the contract of REPAIR -> PRODUCT, as tests.

Round 5's repair path was validated and unreachable: no file outside `tool/corpus/repair/` and
`tool/tests/` imported the `repair` package, so «no served text changed anywhere» was a certainty of
the wiring rather than a measurement. These tests are the guarantees of the wire that now exists.

The one sentence they all defend: **a `ValidatedRepair` crosses into the product-shaped pipeline and
does NOT become trusted.** Every test below is one door through which it could have.
"""
import json
import os
import sys
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..', '..'))
sys.path.insert(0, os.path.join(HERE, '..', 'corpus'))

import tsl_to_lesson_document as bridge                                    # noqa: E402
from repair import ledger as ledger_mod, model, tsl_projection as tp       # noqa: E402
from repair.model import Disposition, Verdict                              # noqa: E402
from repair.validated import (ProvenanceLaundering, RepairIntegrityError,  # noqa: E402
                              SourceGrounding, TrustEscalation, ValidatedRepair,
                              assert_repair_not_strengthened)

BOOK = '05-sgk-lich-su-va-dia-li-5'
BID = f'{BOOK}:p039:tc2-p1:000'
OBSERVED = 'Chiến thắng Bạch Đằng của Ngô Quyền (938)'
VERIFIER = 'Chiến thắng Bạch Đăng của Ngô Quyền (938)'
PROV = dict(book=BOOK, page=39, page_printed=37, bbox=[0.07, 0.06, 0.83, 0.08],
            extraction='docling-2.126+ocrmac', ocr_conf=1.0, pipeline='tc2-p1')


def observations(value=OBSERVED):
    return (model.Observation(block_id=BID, source='docling-ocrmac', value=value, provenance=PROV),
            model.Observation(block_id=BID, source='current-xycut', value=VERIFIER, provenance=PROV))


def candidate(proposed=OBSERVED, rule='lanec.tone-corroboration-v1', covers=('agree_tones',)):
    obs = observations()
    return model.RepairCandidate(
        block_id=BID, failure_class='vi_tone_disagreement', original_observations=obs,
        proposed_value=proposed, rule_id=rule,
        supporting_signals=(model.Signal('E.human_print_read', model.SignalVerdict.SUPPORTS, 1.0),
                            model.Signal('D.in_corpus_majority', model.SignalVerdict.ABSTAINS)),
        confidence=0.9, provenance=dict(PROV, covers_reasons=covers, changed=proposed != OBSERVED),
        detected=dict(kind='tone disagreement on one token'))


def validation(verdict=Verdict.VALIDATED, vid='lanec.history-text-validator-v1'):
    return model.ValidationResult(vid, verdict, evidence=[dict(kind='independent signal layer', value='E')])


def entry(disposition=Disposition.VALIDATED_REPAIR, stage='dispose', cand=None, val=None):
    cand = cand if cand is not None else candidate()
    return model.LedgerEntry(block_id=BID, failure_class='vi_tone_disagreement', disposition=disposition,
                             observations=cand.original_observations, candidate=cand,
                             validation=val if val is not None else validation(), stage=stage,
                             final_value=cand.proposed_value, reasons=('repaired:' + cand.rule_id,))


def a_repair(**kw):
    return ValidatedRepair.from_entry(entry(**kw), source_version=dict(pipeline='tc2-p1', sdm_version='sdm-v3'))


def a_tsl(*, withheld_reasons=('agree_tones',), served_text=None, repairs=None, region_repair=None,
          served_repair=None, role='body'):
    """A minimal but structurally REAL TSL: `tc2_tsl.py`'s own shape, not a shape invented for a test."""
    blocks = [dict(id=f'{BOOK}:p039:tc2-p1:001', page=39, page_printed=37, order=1,
                   role=dict(value='heading', coarse='HEADING', confidence=0.9, method='lexicon'),
                   text='Bài 8', bbox=[0.1, 0.1, 0.3, 0.05], heading_path=['Bài 8'],
                   refers_figure=False, enumerator_restored=False, provenance=dict(PROV))]
    if served_text is not None:
        b = dict(id=BID, page=39, page_printed=37, order=0,
                 role=dict(value=role, coarse='BODY', confidence=0.9, method='lexicon'),
                 text=served_text, bbox=PROV['bbox'], heading_path=[], refers_figure=False,
                 enumerator_restored=False, provenance=dict(PROV))
        if served_repair:
            b['repair'] = served_repair
        blocks.append(b)
    wh = []
    if served_text is None:
        w = dict(id=BID, page=39, page_printed=37, order=0, role=role, bbox=PROV['bbox'],
                 reasons=list(withheld_reasons), status='WITHHELD', text_len=len(OBSERVED),
                 provenance=dict(PROV), text=None)
        if region_repair:
            w['repair'] = region_repair
            w['disposition'] = region_repair['disposition']
        wh.append(w)
    t = dict(book=BOOK, lesson=8, title='NƯỚC TA DƯỚI ÁCH ĐÔ HỘ', pipeline='tc2-p1', docType='SGK',
             boundary=dict(page_start=38, page_end=41, confidence=0.9, header_found=True, source='header',
                           attach_methods={'header': 4}),
             sourceability='PARTIAL',
             stats=dict(learning_blocks=len(blocks) + len(wh), trusted=len(blocks), withheld=len(wh)),
             blocks=blocks, withheld=wh, figures=[], answer_keys_included=False)
    if repairs is not None:
        t['repairs'] = repairs
    return t


def rows_for(*entries, restore_of=None):
    """Write real entries through a real (in-memory) append-only ledger, then read them back as the
    JSONL rows a consumer sees. Nothing here hand-writes a ledger row."""
    lg = ledger_mod.Ledger()
    written = [lg.append(e) for e in entries]
    if restore_of is not None:
        lg.supersede(written[restore_of], disposition=Disposition.TRUSTED, stage='restore',
                     reasons=('restored',))
    return [dict(r, run=dict(lane='test', baseline='tc2-p1', pipeline='tc2-p1',
                             framework=model.FRAMEWORK_VERSION)) for r in lg.to_json()]


# --------------------------------------------------------------------------- the type
class ValidatedRepairContractTests(unittest.TestCase):
    def test_disposition_is_validated_repair_and_there_is_no_way_to_make_it_trusted(self):
        vr = a_repair()
        self.assertEqual(vr.disposition, Disposition.VALIDATED_REPAIR)
        self.assertFalse(vr.servable)
        # not a field: it cannot be set on construction, in a dict, or after the fact
        self.assertNotIn('disposition', {f.name for f in vr.__dataclass_fields__.values()})
        with self.assertRaises(Exception):
            vr.disposition = Disposition.TRUSTED
        self.assertEqual(vr.to_json()['disposition'], Disposition.VALIDATED_REPAIR)
        self.assertIs(vr.to_json()['servable'], False)

    def test_a_restore_row_is_refused_outright(self):
        e = entry(disposition=Disposition.TRUSTED, stage='restore')
        with self.assertRaises(TrustEscalation):
            ValidatedRepair.from_entry(e)

    def test_an_unvalidated_row_is_refused(self):
        for d, v in ((Disposition.REPAIRED_CANDIDATE, Verdict.INSUFFICIENT),
                     (Disposition.SUSPECT, Verdict.REJECTED),
                     (Disposition.WITHHELD, Verdict.REJECTED)):
            with self.assertRaises(RepairIntegrityError):
                ValidatedRepair.from_entry(entry(disposition=d, val=validation(v)))
        # even a VALIDATED_REPAIR row whose validation is not `validated` is refused: the two must agree
        with self.assertRaises(RepairIntegrityError):
            ValidatedRepair.from_entry(entry(val=validation(Verdict.REJECTED)))

    def test_it_keeps_all_ten_things_the_round_requires(self):
        j = a_repair().to_json()
        self.assertTrue(j['originalObservations'] and j['originalObservations'][0]['value'] == OBSERVED)
        self.assertEqual(j['candidate']['rule_id'], 'lanec.tone-corroboration-v1')
        self.assertEqual(j['sourceGrounding']['blockId'], BID)
        self.assertEqual(j['failureClass'], 'vi_tone_disagreement')
        self.assertEqual(j['repairMethod'], 'lanec.tone-corroboration-v1')
        self.assertEqual((j['validatorId'], j['validatorVersion']),
                         ('lanec.history-text-validator-v1', 'v1'))
        self.assertEqual(j['validation']['verdict'], Verdict.VALIDATED)
        self.assertEqual(j['repairVersion'], 'repair-v1/lanec.tone-corroboration-v1')
        self.assertEqual(j['sourceVersion']['sdm_version'], 'sdm-v3')
        self.assertEqual(j['disposition'], Disposition.VALIDATED_REPAIR)

    def test_the_grounding_is_lane_e1s_type_not_a_copy_of_it(self):
        vr = a_repair()
        self.assertIsInstance(vr.source_grounding, SourceGrounding)
        self.assertEqual(vr.to_json()['sourceGrounding'], vr.source_grounding.to_json())
        self.assertEqual(vr.source_grounding.locator_kind, 'page-geometry')

    def test_there_is_no_constructor_from_a_presentation_form(self):
        for name in ('from_text', 'from_latex', 'from_summary', 'from_string', 'from_display'):
            self.assertFalse(hasattr(ValidatedRepair, name), name)
        with self.assertRaises(RepairIntegrityError):
            ValidatedRepair.from_json('Chiến thắng Bạch Đằng (938)')
        with self.assertRaises(RepairIntegrityError):       # a record without its trace is not a record
            ValidatedRepair.from_json(dict(disposition=Disposition.VALIDATED_REPAIR, blockId=BID))

    def test_a_round_trip_never_returns_a_stronger_record(self):
        before = a_repair().to_json()
        after = ValidatedRepair.from_json(before).to_json()
        self.assertEqual(before, after)
        self.assertTrue(assert_repair_not_strengthened(before, after))

    def test_serialisation_cannot_launder_a_repair_into_a_trusted_one(self):
        before = a_repair().to_json()
        for tampered in (dict(before, disposition=Disposition.TRUSTED),
                         dict(before, disposition=Disposition.HUMAN_VERIFIED)):
            with self.assertRaises(TrustEscalation):
                ValidatedRepair.from_json(tampered)
            with self.assertRaises(ProvenanceLaundering):
                assert_repair_not_strengthened(before, tampered)
        with self.assertRaises(ProvenanceLaundering):
            assert_repair_not_strengthened(dict(before, servable=False), dict(before, servable=True))
        capped = dict(before, caps=[tp.CAP_TRUST_GATE])
        with self.assertRaises(ProvenanceLaundering):        # dropping a cap drops the reason
            assert_repair_not_strengthened(capped, before)

    def test_the_block_projection_carries_no_value(self):
        b = a_repair(cand=candidate(proposed='Bạch Đằng (938)')).to_block_json()
        for k in bridge.REPAIR_FORBIDDEN_KEYS:
            self.assertNotIn(k, b)
        self.assertNotIn('Bạch Đằng (938)', json.dumps(b, ensure_ascii=False))


# --------------------------------------------------------------------------- the projection
class ProjectionTests(unittest.TestCase):
    def test_a_validated_repair_crosses_and_the_region_stays_withheld_and_textless(self):
        out, rep = tp.project(a_tsl(), rows_for(entry()))
        self.assertEqual((rep['validated_repairs'], rep['crossed'], rep['trusted_repairs']), (1, 1, 0))
        w = out['withheld'][0]
        self.assertIsNone(w['text'])
        self.assertEqual(w['disposition'], Disposition.VALIDATED_REPAIR)
        self.assertEqual(w['repair']['method'], 'lanec.tone-corroboration-v1')
        self.assertEqual(out['stats']['repair']['trusted'], 0)
        self.assertEqual(out['blocks'], a_tsl()['blocks'])     # the served set is untouched

    def test_the_input_tsl_is_never_mutated(self):
        t = a_tsl()
        snapshot = json.dumps(t, ensure_ascii=False, sort_keys=True)
        tp.project(t, rows_for(entry()))
        self.assertEqual(json.dumps(t, ensure_ascii=False, sort_keys=True), snapshot)

    def test_nothing_is_lost_and_nothing_is_promoted(self):
        out, _ = tp.project(a_tsl(), rows_for(entry()))
        before = {b['id'] for b in a_tsl()['blocks']} | {w['id'] for w in a_tsl()['withheld']}
        after = {b['id'] for b in out['blocks']} | {w['id'] for w in out['withheld']}
        self.assertEqual(before, after)
        self.assertLessEqual(len(out['blocks']), len(a_tsl()['blocks']))

    def test_a_laboratory_restore_is_capped_not_honoured(self):
        out, rep = tp.project(a_tsl(), rows_for(entry(), restore_of=0))
        self.assertEqual(rep['trusted_repairs'], 0)
        self.assertEqual(len(rep['capped']), 1)
        w = out['withheld'][0]
        self.assertIn(tp.CAP_TRUST_GATE, w['reasons'])
        self.assertIn(tp.CAP_TRUST_GATE, w['repair']['caps'])
        self.assertEqual(w['repair']['disposition'], Disposition.VALIDATED_REPAIR)
        self.assertIsNone(w['text'])

    def test_serving_the_proposed_value_is_refused_and_nothing_is_written(self):
        changed = candidate(proposed='Chiến thắng Bạch Đằng của Ngô Quyền (939)')
        rows = rows_for(entry(cand=changed))
        with self.assertRaises(tp.UnTrustedRepairServed):
            tp.project(a_tsl(served_text=changed.proposed_value), rows)

    def test_withhold_mode_demotes_that_block_and_drops_its_text(self):
        changed = candidate(proposed='Chiến thắng Bạch Đằng của Ngô Quyền (939)')
        rows = rows_for(entry(cand=changed))
        out, rep = tp.project(a_tsl(served_text=changed.proposed_value), rows,
                              on_served_repair='withhold')
        self.assertEqual([v['kind'] for v in rep['violations']], ['repair_served'])
        self.assertNotIn(BID, [b['id'] for b in out['blocks']])
        w = next(x for x in out['withheld'] if x['id'] == BID)
        self.assertIsNone(w['text'])
        self.assertIn(tp.REASON_NOT_TRUSTED, w['reasons'])

    def test_serving_the_observation_is_a_finding_not_a_violation(self):
        """The lesson serves the ORIGINAL text while a validator says it is wrong. Nothing was laundered;
        this is pre-existing false trust, and acting on it changes accounting workstream A owns."""
        changed = candidate(proposed='Chiến thắng Bạch Đằng của Ngô Quyền (939)')
        out, rep = tp.project(a_tsl(served_text=OBSERVED), rows_for(entry(cand=changed)))
        self.assertEqual(rep['violations'], [])
        self.assertEqual([f['kind'] for f in rep['findings']], ['served_unrepaired'])
        self.assertEqual([b['id'] for b in out['blocks'] if b['id'] == BID], [BID])
        self.assertNotIn('repair', out['blocks'][-1])          # a served block never carries a record

    def test_a_detected_but_unrepaired_failure_is_reported_never_silently_dropped(self):
        e = entry(disposition=Disposition.SUSPECT, val=validation(Verdict.INSUFFICIENT))
        out, rep = tp.project(a_tsl(served_text=OBSERVED), rows_for(e))
        self.assertEqual(rep['validated_repairs'], 0)
        self.assertIn(tp.block_key(BID), rep['detected_unrepaired'])
        self.assertEqual([f['kind'] for f in rep['findings']], ['detected_unrepaired'])

    def test_the_join_is_pipeline_agnostic(self):
        """A TSL id embeds the pipeline and the ledger was written against another one. Joining on the
        raw id matches nothing, and «no repairs found» is indistinguishable from «no repairs exist»."""
        rows = rows_for(entry())
        for r in rows:
            r['block_id'] = r['block_id'].replace(':tc2-p1:', ':tc2-p9:')
            if r.get('candidate'):
                r['candidate']['block_id'] = r['block_id']
        _, rep = tp.project(a_tsl(), rows)
        self.assertEqual(rep['crossed'], 1)

    def test_there_is_no_mode_that_serves_an_ungated_repair(self):
        for kw in (dict(on_served_repair='serve'), dict(on_served_repair='trust'),
                   dict(on_served_unrepaired='trust'), dict(on_detected_unrepaired='serve')):
            with self.assertRaises(ValueError):
                tp.project(a_tsl(), rows_for(entry()), **kw)

    def test_the_version_chain_is_on_every_record(self):
        out, rep = tp.project(a_tsl(), rows_for(entry()))
        self.assertEqual(rep['source_tsl_sha256'], tp.canonical_sha256(a_tsl()))
        sv = out['repairs'][0]['sourceVersion']
        for k in ('pipeline', 'sourceTslSha256', 'ledgerRun', 'projection', 'framework'):
            self.assertIn(k, sv)
        self.assertEqual(out['repairProjection']['productionTrustThreshold'], None)


# --------------------------------------------------------------------------- the bridge
class BridgeRepairTests(unittest.TestCase):
    def projected(self, **kw):
        out, _ = tp.project(a_tsl(**kw), rows_for(entry()))
        return out

    def test_the_repair_reaches_the_document_and_the_value_does_not(self):
        changed = candidate(proposed='Chiến thắng Bạch Đằng của Ngô Quyền (939)')
        out, _ = tp.project(a_tsl(), rows_for(entry(cand=changed)))
        doc = bridge.convert(out, book_meta=dict(subject='Lịch sử và Địa lí', grade=5), chapters=[])
        blk = next(b for b in doc['blocks'] if b['id'] == BID)
        self.assertEqual(blk['type'], 'withheld')
        self.assertNotIn('text', blk)
        self.assertEqual(blk['disposition'], Disposition.VALIDATED_REPAIR)
        self.assertEqual(blk['repair']['validatorId'], 'lanec.history-text-validator-v1')
        self.assertEqual(doc['provenance']['repair']['trusted'], 0)
        self.assertEqual(doc['provenance']['blockCounts']['validatedRepairsOnBlocks'], 1)
        # the strong check: the proposed value appears NOWHERE in the serialised document
        self.assertNotIn(changed.proposed_value, json.dumps(doc, ensure_ascii=False))

    def test_a_served_block_carrying_a_repair_is_refused(self):
        vr = a_repair()
        t = a_tsl(served_text=OBSERVED, served_repair=vr.to_block_json(), repairs=[vr.to_json()])
        with self.assertRaises(bridge.BridgeRefusal):
            bridge.convert(t, chapters=[])

    def test_a_repair_record_claiming_trusted_is_refused(self):
        vr = a_repair()
        bad = dict(vr.to_block_json(), disposition=Disposition.TRUSTED)
        t = a_tsl(region_repair=bad, repairs=[dict(vr.to_json(), disposition=Disposition.TRUSTED)])
        with self.assertRaises(bridge.BridgeRefusal):
            bridge.convert(t, chapters=[])

    def test_a_repair_record_carrying_a_value_is_refused(self):
        vr = a_repair()
        for key in ('proposedValue', 'text', 'latex', 'structuredValue'):
            bad = dict(vr.to_block_json())
            bad[key] = 'Chiến thắng Bạch Đằng (939)'
            t = a_tsl(region_repair=bad, repairs=[vr.to_json()])
            with self.assertRaises(bridge.BridgeRefusal):
                bridge.convert(t, chapters=[])

    def test_a_repair_nobody_can_look_up_is_refused(self):
        t = a_tsl(region_repair=a_repair().to_block_json(), repairs=[])
        with self.assertRaises(bridge.BridgeRefusal):
            bridge.convert(t, chapters=[])

    def test_a_formula_role_says_no_carrier_not_unknown_role(self):
        t = a_tsl(served_text='S = v × t', role='formula')
        doc = bridge.convert(t, chapters=[])
        blk = next(b for b in doc['blocks'] if b['id'] == BID)
        self.assertEqual(blk['type'], 'withheld')
        self.assertEqual(blk['reasons'], ['no_carrier:formula'])
        self.assertNotIn('text', blk)
        self.assertEqual(doc['provenance']['blockCounts']['noCarrierWithheld'], 1)
        self.assertEqual(doc['provenance']['blockCounts']['unknownRoleWithheld'], 0)
        # behaviour-neutral for the app: withheld_card.dart matches 'formula' before 'unknown_role'
        self.assertIn('formula', blk['reasons'][0])


# --------------------------------------------------------------------------- the real lesson
GOLDEN_TSL = (f'{ROOT}/poc-out/round5/lane-c/tc2-lsdl5/v1/root/poc-out/trusted-corpus/tc-v2/tc2-r5'
              f'/lessons/05-sgk-lich-su-va-dia-li-5/bai-08.tsl.json')
GOLDEN_LEDGER = f'{ROOT}/poc-out/round5/lane-c/tc2-lsdl5/v1/report/repair-ledger.jsonl'


@unittest.skipUnless(os.path.exists(GOLDEN_TSL) and os.path.exists(GOLDEN_LEDGER),
                     'the real LS&ĐL 5 Bài 8 corpus artefacts are not in this checkout')
class GoldenOneTests(unittest.TestCase):
    """GATE C on the real lesson, from the real ledger. No fixture, and no `if lesson == 8` anywhere."""

    @classmethod
    def setUpClass(cls):
        tsl = json.load(open(GOLDEN_TSL, encoding='utf-8'))
        rows = ledger_mod.read(GOLDEN_LEDGER)
        cls.out, cls.rep = tp.project(tsl, rows)
        cls.doc = bridge.convert(cls.out, tsl_sha256=tp.canonical_sha256(cls.out),
                                 book_meta=dict(subject='Lịch sử và Địa lí', grade=5), chapters=[])

    def test_validated_repairs_cross_and_none_becomes_trusted(self):
        self.assertGreaterEqual(self.rep['crossed'], 1)
        self.assertEqual(self.rep['trusted_repairs'], 0)
        self.assertEqual(self.rep['violations'], [])
        self.assertEqual(self.doc['provenance']['repair']['trusted'], 0)

    def test_the_block_with_all_seven_dated_events_carries_its_repair_and_no_text(self):
        blk = next(b for b in self.doc['blocks'] if b['id'].endswith('p039:tc2-p1:000'))
        self.assertEqual(blk['type'], 'withheld')
        self.assertNotIn('text', blk)
        self.assertEqual(blk['disposition'], Disposition.VALIDATED_REPAIR)
        self.assertEqual(blk['repair']['method'], 'lanec.tone-corroboration-v1')
        self.assertFalse(blk['repair']['changed'])      # a DISPOSITION repair: nothing is rewritten
        self.assertFalse(blk['repair']['servable'])
        rec = next(r for r in self.out['repairs'] if r['blockId'].endswith('p039:tc2-p1:000'))
        self.assertEqual([o['source'] for o in rec['originalObservations']],
                         ['docling-ocrmac', 'current-xycut'])
        self.assertNotEqual(rec['originalObservations'][0]['value'],
                            rec['originalObservations'][1]['value'])

    def test_the_rejected_attribution_stays_withheld(self):
        """Lane C's opposite result must survive integration: two signals objected, the candidate was
        rejected, so the attribution is withheld rather than half-corrected."""
        blk = next(b for b in self.doc['blocks'] if b['id'].endswith('p041:tc2-p1:002'))
        self.assertEqual(blk['type'], 'withheld')
        self.assertNotIn('repair', blk)

    def test_no_served_text_of_the_lesson_changed(self):
        before = {b['id']: b['text'] for b in json.load(open(GOLDEN_TSL, encoding='utf-8'))['blocks']}
        for b in self.doc['blocks']:
            if b['id'] in before and b['type'] not in ('withheld', 'table'):
                self.assertEqual(b['text'], before[b['id']])


if __name__ == '__main__':
    unittest.main()
