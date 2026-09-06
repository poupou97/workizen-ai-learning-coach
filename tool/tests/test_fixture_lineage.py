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
