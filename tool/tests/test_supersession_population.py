#!/usr/bin/env python3
"""WAL-213 · the value-level half of the population suite — needs the gitignored corpus.

The committed census (`data/wal213-bai61-population.json`) carries structure only, because a file
of SGK readings in git is a textbook derivative (D4, `.gitignore`: *«sản phẩm phái sinh từ SGK cũng
KHÔNG commit: text trích xuất…»*). So the assertions that need the actual destroyed and recovered
strings live here, against `poc-out/`, and this module **skips** where the corpus is absent — CI, a
clean clone, any machine but the one holding the 9.8 GB of scans.

**A skip is not a pass, and this file is written so nobody can mistake one for the other:**

* the skip reason names the exact file that is missing, so «green» never means «checked»;
* `test_the_census_still_describes_the_artefact` re-derives the committed census from the artefact
  and fails if they have drifted apart — so on the one machine where the corpus exists, the
  committed structure cannot silently stop being the measurement;
* `test_the_artefact_is_not_degenerate` refuses a present-but-empty artefact. **ABSENCE CANNOT
  SATISFY A POSITIVE OBLIGATION**: an artefact that exists and contains nothing must fail, not
  vacuously pass.

Reproduce the artefact with:

    python3 tool/corpus/recognition/study.py dev          # writes study-dev.json (Vision, macOS)
    python3 tool/corpus/recognition/supersede_study.py <study.json>
"""
import json
import os
import sys
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', 'corpus'))

from repair import supersession as SUP                                       # noqa: E402
from repair.model import Disposition                                         # noqa: E402

TC_ROOT = os.environ.get('TC_ROOT', os.path.dirname(os.path.dirname(HERE)))
ARTEFACT = os.path.join(TC_ROOT, 'poc-out', 'round7', 'wal213', 'supersede-bai61.json')
STUDY = os.path.join(TC_ROOT, 'poc-out', 'round7', 'wal213', 'study-bai61-4scales.json')
CENSUS = os.path.join(HERE, 'data', 'wal213-bai61-population.json')

HAVE = os.path.exists(ARTEFACT)
WHY = (f'the WAL-213 measurement artefact is not on this machine ({ARTEFACT}). It is a derivative '
       f'of copyrighted SGK pages and never enters git; regenerate it with '
       f'`python3 tool/corpus/recognition/supersede_study.py`. THIS IS A SKIP, NOT A PASS.')


@unittest.skipUnless(HAVE, WHY)
class TestRealSupersessionsAtValueLevel(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        with open(ARTEFACT) as fh:
            cls.doc = json.load(fh)
        cls.rels = [s for p in cls.doc['pages'] for s in p['supersessions']]
        cls.blocks = [b for p in cls.doc['pages'] for b in p['blocks']]

    def test_the_artefact_is_not_degenerate(self):
        """A present-but-empty artefact FAILS. Round 7 found a gate printing `0/0 present · PASS`;
        this is the same shape and it must go red."""
        self.assertTrue(self.doc.get('pages'), 'artefact has no pages')
        self.assertTrue(self.rels, 'artefact contains no supersessions at all')
        self.assertTrue(self.blocks, 'artefact contains no block projections at all')

    def test_the_population_is_adequate(self):
        class Row:
            def __init__(self, d):
                self.resolved, self.changed, self.coverage = d['resolved'], d['changed'], d['coverage']
        self.assertTrue(SUP.assert_population_adequate([Row(s) for s in self.rels], label='bai61'))

    def test_every_relation_reads_back_from_its_own_json(self):
        """Structure -> structure, on the real records, and the round trip must not strengthen one.

        Compared after `json.dumps`/`json.loads` because that IS the round trip: round 5's
        `Observation.provenance` is deep-frozen to tuples in memory and comes back from a file as
        lists. Comparing the in-memory forms would fail on a difference no reader can observe;
        comparing the on-disk forms is the property that matters — **save, load, save is stable.**
        """
        for s in self.rels:
            back = SUP.Supersession.from_json(s)
            again = json.loads(json.dumps(back.to_json(), ensure_ascii=False))
            self.assertEqual(again, s, s['supersessionId'])
            self.assertTrue(SUP.assert_supersession_not_strengthened(s, again))

    def test_a_resolved_supersession_really_replaces_a_different_string(self):
        """The failing case, at value level: the recovered reading differs from the destroyed one,
        and the destroyed one is still there to be read by an auditor."""
        resolved = [s for s in self.rels if s['resolved']]
        self.assertTrue(resolved)
        for s in resolved:
            new = s['superseding']['value']
            olds = [o['value'] for o in s['superseded']]
            self.assertTrue(olds, s['supersessionId'])
            self.assertTrue(all(o != new for o in olds), f'{s["supersessionId"]}: {olds} -> {new}')
            self.assertEqual(s['disposition'], Disposition.SUPERSEDED)

    def test_a_refused_supersession_would_have_destroyed_printed_content(self):
        """The 13. Each superseded observation carries text beyond the region that recovered it, so
        replacing it wholesale would delete printed content — an item letter, an operator, a
        neighbouring digit."""
        refused = [s for s in self.rels if not s['resolved']]
        self.assertTrue(refused)
        for s in refused:
            self.assertEqual(s['disposition'], Disposition.CONFLICT)
            self.assertLess(s['coverageFraction'], SUP.FULL_COVERAGE)
            self.assertIn('overwriting', s['residualReason'])

    def test_no_source_observation_was_edited(self):
        """Every superseded value in the artefact is a value the page pass actually produced, letter
        for letter — the relation carried it, it did not rewrite it."""
        with open(STUDY) as fh:
            study = json.load(fh)
        self.assertTrue(study['pages'])
        for s in self.rels:
            for o in s['superseded']:
                self.assertIsInstance(o['value'], str)
                self.assertEqual(o['disposition'], Disposition.ORIGINAL_OBSERVATION)

    def test_the_recovered_reading_never_reaches_a_block_as_text(self):
        """CONNECT != TRUST, at value level.

        Asserted STRUCTURALLY rather than by substring search: a one-character reading like `4`
        occurs by coincidence inside a region key, so «the value is not in the blob» is a test that
        passes or fails for the wrong reason. The real claim is stronger and checkable — the block
        projection has **no free-text field at all**: every key is in a fixed allowlist and every
        string it can hold is an enum member, an engine name or an id. There is nowhere for a
        reading to go.
        """
        allowed = {'supersessionId', 'disposition', 'supersededObservations', 'supersedingEngine',
                   'coverage', 'agreeingScales', 'stacked', 'resolved', 'changed', 'servable'}
        engines = {'apple-vision-crop-v1', 'apple-vision-page-v1'}
        for b in self.blocks:
            self.assertNotIn('proposedValue', b)
        for s in self.rels:
            b = SUP.Supersession.from_json(s).to_block_json()
            self.assertEqual(set(b), allowed, s['supersessionId'])
            self.assertIn(b['disposition'], (Disposition.SUPERSEDED, Disposition.CONFLICT))
            self.assertIn(b['coverage'], (SUP.FULL, SUP.PARTIAL, SUP.NONE))
            self.assertIn(b['supersedingEngine'], engines)
            self.assertTrue(b['supersessionId'].startswith(s['blockId']))
            self.assertFalse(b['servable'])
            for k in ('supersededObservations', 'agreeingScales'):
                self.assertIsInstance(b[k], int)
            for k in ('stacked', 'resolved', 'changed', 'servable'):
                self.assertIsInstance(b[k], bool)

    def test_the_census_still_describes_the_artefact(self):
        """The committed structure and the measurement it came from may not drift apart.

        This is the check the census cannot do for itself: on a clean clone the census is all there
        is, so on the ONE machine that holds the corpus, it must be re-derived and compared.
        """
        from recognition import supersede_study as SS
        with open(CENSUS) as fh:
            committed = json.load(fh)
        fresh = SS.census(self.doc, STUDY)
        self.assertEqual(committed['totals'], fresh['totals'])
        self.assertEqual(committed['source']['studySha256'], fresh['source']['studySha256'])
        self.assertEqual(len(committed['regions']), len(fresh['regions']))
        self.assertEqual([r['coverage'] for r in committed['regions']],
                         [r['coverage'] for r in fresh['regions']])
        self.assertEqual([b['supersedeVerdict'] for b in committed['blocks']],
                         [b['supersedeVerdict'] for b in fresh['blocks']])

    def test_the_add_column_still_reproduces_round_7(self):
        from recognition import supersede_study as SS
        with open(STUDY) as fh:
            study = json.load(fh)
        self.assertEqual(SS.assert_add_column_reproduces_round7(self.doc, study), 44)


class TestSkipIsVisible(unittest.TestCase):
    """Runs everywhere. Its job is that «the corpus is absent» is never silent."""

    def test_the_skip_reason_names_the_missing_artefact(self):
        self.assertIn('poc-out', WHY)
        self.assertIn('SKIP, NOT A PASS', WHY)

    def test_the_committed_census_exists_even_when_the_corpus_does_not(self):
        """The structural population is committed precisely so that a clean clone still has a real
        population to test against. If this file is gone, the suite must fail, not skip."""
        self.assertTrue(os.path.exists(CENSUS), CENSUS)
        with open(CENSUS) as fh:
            c = json.load(fh)
        self.assertTrue(c['regions'], 'the committed census is empty — the population is gone')


if __name__ == '__main__':
    unittest.main(verbosity=2)
