#!/usr/bin/env python3
"""ROUND 6 · WS-D — tests for tool/evidence/fixture_lineage.py.

Run:  python3 -m unittest discover -s tool/tests -v

No corpus needed: every fixture here is built in a temp dir, so these run on a clean
clone. That is deliberate — the tool exists precisely because `assets/fixtures/real/`
is gitignored and never reaches CI, so the tool itself must.
"""
import hashlib
import json
import os
import sys
import tempfile
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', 'evidence'))
import fixture_lineage as fl  # noqa: E402

TSL_BYTES = b'{"book":"05-sgk-lich-su-va-dia-li-5","lesson":8}\n'
TSL_HASH = hashlib.sha256(TSL_BYTES).hexdigest()
TSL_REL = 'poc-out/trusted-corpus/tc-v2/tc2-p3/lessons/05-sgk-lich-su-va-dia-li-5/bai-08.tsl.json'


def provenance(**over):
    p = dict(
        trust='trustedStructuredLesson',
        book='05-sgk-lich-su-va-dia-li-5',
        pagePdfStart=38, pagePdfEnd=41,
        generator='tool/corpus/tsl_to_lesson_document.py@v1',
        sourcePipeline='tc2-p3',
        sdmVersion='sdm-v3',
        pipelineVersion='tc2-p3/sdm-v3',
        tslPath=TSL_REL,
        sourceHash=TSL_HASH,
        repairVersion='repair@v1',
        distribution='internal-research-only (Founder D4) — không phân phối, không commit',
    )
    p.update(over)
    return p


def write_case(root, prov, blocks=None):
    """A repo-shaped temp dir: the TSL where provenance says it is, the fixture in assets."""
    tsl_abs = os.path.join(root, TSL_REL)
    os.makedirs(os.path.dirname(tsl_abs), exist_ok=True)
    with open(tsl_abs, 'wb') as fh:
        fh.write(TSL_BYTES)
    fixdir = os.path.join(root, 'assets', 'fixtures', 'real')
    os.makedirs(os.path.join(fixdir, 'crops'), exist_ok=True)
    doc = dict(schema='lesson-document-v1', book=prov['book'], lesson=8,
               title='Đấu tranh giành độc lập thời kì Bắc thuộc',
               provenance=prov, blocks=blocks or [], semantic=[], tutorScript=None)
    path = os.path.join(fixdir, 'lesson-05-sgk-lich-su-va-dia-li-5-b8.json')
    with open(path, 'w', encoding='utf-8') as fh:
        json.dump(doc, fh, ensure_ascii=False)
    return path


def status_of(result, check_id):
    return next(r['status'] for r in result['checks'] if r['id'] == check_id)


class LineageTest(unittest.TestCase):
    def test_complete_current_generation_passes(self):
        with tempfile.TemporaryDirectory() as root:
            path = write_case(root, provenance())
            r = fl.check(path, root=root, require_repair=True)
            self.assertEqual(r['verdict'], fl.PASS, r)
            self.assertEqual(r['repairVersion'], 'repair@v1')
            self.assertEqual(r['recomputedSourceHash'], TSL_HASH)
            self.assertEqual(r['hashMethod'], 'bytes')

    def test_canonical_json_hash_is_accepted_and_NAMED(self):
        """⭐ MEASURED: the committed bridge records file-BYTE digests; the round-6 repair
        path records CANONICAL-JSON digests. Both are legitimate and they differ, so a
        reviewer running `shasum -a 256` on a repair-path artefact gets a number that does
        not match and concludes it was tampered with. The gate accepts either and SAYS
        WHICH — an unnamed hash method is how a good artefact gets called a forgery.
        """
        canonical = fl.sha256_canonical(json.loads(TSL_BYTES.decode()))
        self.assertNotEqual(canonical, TSL_HASH)
        with tempfile.TemporaryDirectory() as root:
            path = write_case(root, provenance(sourceHash=canonical))
            r = fl.check(path, root=root)
            self.assertEqual(status_of(r, 'L2'), fl.PASS)
            self.assertEqual(r['hashMethod'], 'canonical')
            self.assertEqual(r['sourceDigests']['bytes'], TSL_HASH)

    def test_repair_lineage_accepts_the_projection_stamp(self):
        """The round-6 repair path stamps `projection` + `framework`, not `version`."""
        with tempfile.TemporaryDirectory() as root:
            prov = provenance()
            del prov['repairVersion']
            prov['repair'] = dict(projection='tsl-repair-projection-v1', framework='repair-v1',
                                  validatedRepairs=9, onBlocks=6, trusted=0)
            path = write_case(root, prov)
            r = fl.check(path, root=root, require_repair=True)
            self.assertEqual(status_of(r, 'L4'), fl.PASS)
            self.assertEqual(r['repairVersion'], 'tsl-repair-projection-v1')

    def test_wrong_source_hash_is_a_hard_fail(self):
        """⭐ The round-5 stale-fixture trap: the file claims a TSL it was not built from."""
        with tempfile.TemporaryDirectory() as root:
            path = write_case(root, provenance(sourceHash='0' * 64))
            r = fl.check(path, root=root)
            self.assertEqual(status_of(r, 'L2'), fl.FAIL)
            self.assertIsNone(r['hashMethod'], 'neither method may be claimed')
            self.assertEqual(r['verdict'], fl.FAIL)

    def test_absent_tsl_is_unknown_not_pass(self):
        """An unverifiable claim is not a verified one — and must not read as one."""
        with tempfile.TemporaryDirectory() as root:
            path = write_case(root, provenance())
            os.remove(os.path.join(root, TSL_REL))
            r = fl.check(path, root=root)
            self.assertEqual(status_of(r, 'L2'), fl.UNKNOWN)
            self.assertEqual(r['verdict'], fl.UNKNOWN)

    def test_pipeline_name_alone_never_passes_a_generation(self):
        """⭐ MEASURED 2026-09-06: the pipeline NAME does not discriminate generations.

        The round-5 rerun of LS&ĐL 5 Bài 8 sits under `tc-v2/tc2-r5/` yet DECLARES
        `pipeline: tc2-p1`, and its block ids still embed `tc2-p1`. So two documents
        can both read `sourcePipeline: tc2-p1` and be different generations. The gate
        must surface the disagreement instead of quietly passing on the name.
        """
        with tempfile.TemporaryDirectory() as root:
            path = write_case(root, provenance(sourcePipeline='tc2-p1', sdmVersion='sdm-v2',
                                               pipelineVersion='tc2-p1/sdm-v2'))
            r = fl.check(path, root=root)          # TSL path says tc2-p3, document says tc2-p1
            self.assertEqual(status_of(r, 'L3'), fl.PASS)   # internally consistent…
            self.assertEqual(status_of(r, 'L3b'), fl.UNKNOWN)  # …but NOT a verified generation
            self.assertEqual(r['verdict'], fl.UNKNOWN)
            # the sha256 is the authority, and it is what pins the generation
            self.assertEqual(status_of(fl.check(path, root=root,
                                                expect_source_hash='1' * 64), 'L2b'), fl.FAIL)

    def test_generation_root_is_read_from_the_tsl_path(self):
        for rel, want in (
            ('poc-out/trusted-corpus/tc-v2/tc2-p1/lessons/x/bai-01.tsl.json', 'tc2-p1'),
            ('poc-out/round5/lane-c/x/root/poc-out/trusted-corpus/tc-v2/tc2-r5/lessons/y/'
             'bai-08.tsl.json', 'tc2-r5'),
            ('somewhere/else/bai-01.tsl.json', None),
        ):
            self.assertEqual(fl.generation_root(rel), want, rel)

    def test_pipeline_version_must_equal_pipeline_slash_sdm(self):
        with tempfile.TemporaryDirectory() as root:
            path = write_case(root, provenance(pipelineVersion='tc2-p3/sdm-v2'))
            r = fl.check(path, root=root)
            self.assertEqual(status_of(r, 'L3'), fl.FAIL)

    def test_missing_version_field_fails(self):
        for key in ('sourceHash', 'pipelineVersion', 'sdmVersion', 'generator'):
            with self.subTest(field=key), tempfile.TemporaryDirectory() as root:
                path = write_case(root, provenance(**{key: ''}))
                r = fl.check(path, root=root)
                self.assertEqual(status_of(r, 'L1'), fl.FAIL)

    def test_no_repair_is_unknown_but_required_for_delivery(self):
        """A truthful «no repair here» stays truthful; only the delivery claim demands one."""
        with tempfile.TemporaryDirectory() as root:
            prov = provenance()
            del prov['repairVersion']
            path = write_case(root, prov)
            self.assertEqual(status_of(fl.check(path, root=root), 'L4'), fl.UNKNOWN)
            self.assertEqual(
                status_of(fl.check(path, root=root, require_repair=True), 'L4'), fl.FAIL)

    def test_repair_block_form_is_accepted_with_its_counts(self):
        with tempfile.TemporaryDirectory() as root:
            prov = provenance()
            del prov['repairVersion']
            prov['repair'] = dict(version='repair@v1', validatedRepairs=6, demoted=2)
            path = write_case(root, prov)
            r = fl.check(path, root=root)
            self.assertEqual(status_of(r, 'L4'), fl.PASS)
            self.assertEqual(r['repairVersion'], 'repair@v1')

    def test_expected_generation_can_be_pinned(self):
        with tempfile.TemporaryDirectory() as root:
            path = write_case(root, provenance())
            self.assertEqual(fl.check(path, root=root, expect_source_hash=TSL_HASH)['verdict'],
                             fl.PASS)
            self.assertEqual(
                status_of(fl.check(path, root=root, expect_source_hash='1' * 64), 'L2b'), fl.FAIL)

    def test_missing_crop_fails(self):
        """A crop that is not there means the child sees an empty withheld card."""
        with tempfile.TemporaryDirectory() as root:
            path = write_case(root, provenance(),
                              blocks=[dict(id='b1', type='withheld',
                                           crop='crops/05-sgk-lich-su-va-dia-li-5-p039-withheld-000.png')])
            r = fl.check(path, root=root)
            self.assertEqual(status_of(r, 'L5'), fl.FAIL)
            open(os.path.join(root, 'assets', 'fixtures', 'real', 'crops',
                              '05-sgk-lich-su-va-dia-li-5-p039-withheld-000.png'), 'wb').close()
            self.assertEqual(status_of(fl.check(path, root=root), 'L5'), fl.PASS)

    def test_d4_distribution_marker_is_mandatory(self):
        with tempfile.TemporaryDirectory() as root:
            path = write_case(root, provenance(distribution='public'))
            r = fl.check(path, root=root)
            self.assertEqual(status_of(r, 'L6'), fl.FAIL)

    def test_document_hash_is_stable_and_content_sensitive(self):
        with tempfile.TemporaryDirectory() as root:
            path = write_case(root, provenance())
            a = fl.check(path, root=root)['documentSha256']
            self.assertEqual(a, fl.check(path, root=root)['documentSha256'])
            path2 = write_case(root, provenance(), blocks=[dict(id='b1', type='paragraph')])
            self.assertNotEqual(a, fl.check(path2, root=root)['documentSha256'])

    def test_cli_exit_status_is_the_gate(self):
        import contextlib
        import io
        with tempfile.TemporaryDirectory() as root:
            path = write_case(root, provenance())
            out = os.path.join(root, 'out', 'lineage.json')
            with contextlib.redirect_stdout(io.StringIO()):
                ok = fl.main(['--fixture', path, '--root', root, '--require-repair',
                              '--json', out])
            self.assertEqual(ok, 0)
            with open(out, encoding='utf-8') as fh:
                self.assertEqual(json.load(fh)['verdict'], fl.PASS)
            bad = write_case(root, provenance(sourceHash='0' * 64))
            with contextlib.redirect_stdout(io.StringIO()):
                self.assertEqual(fl.main(['--fixture', bad, '--root', root]), 1)


if __name__ == '__main__':
    unittest.main()


class CropCoverageTest(unittest.TestCase):
    """ROUND 7 · WS-R — the gate that would have caught the round-6 Golden #1 defect.

    Round 6 placed LS&ĐL 5 Bài 8 with **17 withheld regions and no page crops**, and the
    lineage gate said PASS. It said PASS because L5 counts crop REFERENCES: a document that
    references none has none absent. The gate was green *because* the thing it guards was
    missing — the same shape as the timeline test round 6 had to correct one layer up.

    A withheld card without a crop tells a child «something is missing here» and shows
    nothing. With a crop it shows the printed page. The population that must be measured is
    therefore the withheld regions that CAN be cropped, not the paths someone remembered to
    write down.
    """

    @staticmethod
    def withheld(order, crop=None, page=38, bbox=(0.1, 0.2, 0.3, 0.04)):
        b = dict(id=f'05-sgk-lich-su-va-dia-li-5:p{page:03d}:tc2-p1:{order:03d}',
                 type='withheld', trust='withheld', reason='agree_tones',
                 sourceRef=dict(book='05-sgk-lich-su-va-dia-li-5', pagePdf=page,
                                pagePrinted=page - 2, bbox=list(bbox)),
                 relations=dict(order=order))
        if crop:
            b['crop'] = crop
        return b

    def test_L5_reads_PASS_on_the_very_document_that_shipped_the_defect(self):
        """⭐ The regression pin. L5 PASS and L5b FAIL on the SAME document — that gap is
        exactly what shipped, and if L5b is ever removed this assertion is what notices."""
        with tempfile.TemporaryDirectory() as root:
            blocks = [self.withheld(o) for o in range(3, 20)]      # 17, as round 6 placed
            path = write_case(root, provenance(), blocks=blocks)
            r = fl.check(path, root=root)
            self.assertEqual(status_of(r, 'L5'), fl.PASS, 'L5 counts references, so it passes')
            l5 = next(x for x in r['checks'] if x['id'] == 'L5')
            self.assertEqual(l5['value'], '0/0 present')
            self.assertEqual(status_of(r, 'L5b'), fl.FAIL)
            l5b = next(x for x in r['checks'] if x['id'] == 'L5b')
            self.assertEqual(l5b['value'], '0/17 have a crop')
            self.assertEqual(r['verdict'], fl.FAIL)

    def test_L5b_passes_only_when_every_croppable_region_carries_one(self):
        with tempfile.TemporaryDirectory() as root:
            names = [f'crops/05-sgk-lich-su-va-dia-li-5-p038-withheld-{o:03d}.png'
                     for o in range(3, 6)]
            blocks = [self.withheld(o, crop=n) for o, n in zip(range(3, 6), names)]
            path = write_case(root, provenance(), blocks=blocks)
            for n in names:
                open(os.path.join(root, 'assets', 'fixtures', 'real', n), 'wb').close()
            r = fl.check(path, root=root)
            self.assertEqual(status_of(r, 'L5'), fl.PASS)
            self.assertEqual(status_of(r, 'L5b'), fl.PASS)
            # remove ONE crop reference and the coverage gate must go red again
            blocks[1].pop('crop')
            path = write_case(root, provenance(), blocks=blocks)
            self.assertEqual(status_of(fl.check(path, root=root), 'L5b'), fl.FAIL)

    def test_the_waiver_is_UNKNOWN_and_never_PASS(self):
        """`--allow-missing-crops` exists for a machine with no source PDF. It must not be
        a way to write PASS where the truth is «the child sees nothing»."""
        with tempfile.TemporaryDirectory() as root:
            path = write_case(root, provenance(), blocks=[self.withheld(3)])
            r = fl.check(path, root=root, allow_missing_crops=True)
            self.assertEqual(status_of(r, 'L5b'), fl.UNKNOWN)
            self.assertNotEqual(status_of(r, 'L5b'), fl.PASS)
            self.assertIn('WAIVED', next(x for x in r['checks'] if x['id'] == 'L5b')['note'])
            self.assertEqual(r['verdict'], fl.UNKNOWN)

    def test_a_region_with_no_geometry_is_not_croppable(self):
        """No page and no bbox ⇒ nothing to cut. Counting it would make the gate demand a
        crop that cannot exist, and a gate nobody can satisfy gets deleted."""
        with tempfile.TemporaryDirectory() as root:
            blk = dict(id='b-nogeom', type='withheld', trust='withheld',
                       sourceRef=dict(book='x', pagePdf=None, bbox=None))
            path = write_case(root, provenance(), blocks=[blk])
            r = fl.check(path, root=root)
            self.assertEqual(status_of(r, 'L5b'), fl.UNKNOWN)
            self.assertEqual(next(x for x in r['checks'] if x['id'] == 'L5b')['value'],
                             '0/1 croppable')

    def test_served_blocks_are_not_in_the_crop_population(self):
        """Only WITHHELD regions are counted: a served paragraph shows its own text."""
        with tempfile.TemporaryDirectory() as root:
            served = dict(id='p1', type='paragraph', trust='trustedStructuredLesson',
                          text='…', sourceRef=dict(pagePdf=38, bbox=[0, 0, 1, 0.1]))
            path = write_case(root, provenance(), blocks=[served])
            r = fl.check(path, root=root)
            self.assertEqual(status_of(r, 'L5b'), fl.PASS)
            self.assertEqual(next(x for x in r['checks'] if x['id'] == 'L5b')['value'],
                             '0 withheld regions')


class ExpectedGenerationAcrossHashMethodsTest(unittest.TestCase):
    """ROUND 7 · WS-R — L2b compared one string to one string while L2 had already
    established that TWO hash methods legitimately coexist (round 6 §4.2a). MEASURED:
    `golden_delivery.py --tsl` computes its expectation as `canonical or bytes` and the
    committed bridge stamps `bytes`, so L2b FAILED on a document built from precisely the
    TSL demanded — which is why the crop-carrying rebuild could not be placed.

    The gate is not loosened: a cross-method match is accepted ONLY when BOTH sides are
    digests this run recomputed from the file at `tslPath`.
    """

    def test_cross_method_expectation_passes_for_the_same_bytes_and_says_so(self):
        canonical = fl.sha256_canonical(json.loads(TSL_BYTES.decode()))
        with tempfile.TemporaryDirectory() as root:
            path = write_case(root, provenance(sourceHash=TSL_HASH))   # recorded = bytes
            r = fl.check(path, root=root, expect_source_hash=canonical)  # expected = canonical
            self.assertEqual(status_of(r, 'L2b'), fl.PASS)
            note = next(x for x in r['checks'] if x['id'] == 'L2b')['note']
            self.assertIn('recorded=bytes', note)
            self.assertIn('expected=canonical', note)

    def test_a_different_generation_still_fails_under_either_method(self):
        """The mutation: one byte of the TSL moves BOTH digests, so no cross-method
        reading can rescue a substituted generation."""
        other = hashlib.sha256(TSL_BYTES + b' ').hexdigest()
        other_canonical = fl.sha256_canonical(dict(book='other', lesson=99))
        with tempfile.TemporaryDirectory() as root:
            path = write_case(root, provenance(sourceHash=TSL_HASH))
            for h in (other, other_canonical, '1' * 64):
                with self.subTest(expected=h[:8]):
                    self.assertEqual(
                        status_of(fl.check(path, root=root, expect_source_hash=h), 'L2b'),
                        fl.FAIL)

    def test_without_the_tsl_on_disk_a_mismatch_is_still_a_fail(self):
        """Nothing to recompute ⇒ nothing to reconcile. Absence must not become licence."""
        canonical = fl.sha256_canonical(json.loads(TSL_BYTES.decode()))
        with tempfile.TemporaryDirectory() as root:
            path = write_case(root, provenance(sourceHash=TSL_HASH))
            os.remove(os.path.join(root, TSL_REL))
            r = fl.check(path, root=root, expect_source_hash=canonical)
            self.assertEqual(status_of(r, 'L2'), fl.UNKNOWN)
            self.assertEqual(status_of(r, 'L2b'), fl.FAIL)
