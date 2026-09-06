#!/usr/bin/env python3
"""WAL-218 — MUTATION CHECKS on the Golden-chain coverage gate.

A gate that passes because the SHAPE changed rather than because the PROPERTY
holds is worth very little; this repo has caught exactly that twice, including
an equivalence a mutation satisfied. So the gate itself is mutated here, and
every mutation must go red.

The property under test, in one line:

    ABSENCE CANNOT SATISFY A POSITIVE OBLIGATION.

which is the same shape as round 7's gate printing `0/0 present · PASS` because
the thing it guarded was absent. Each test below breaks the gate in one specific
way and asserts the exit code:

    0  the run is honest about what it did and did not verify
    1  the run CLAIMED Golden verification and the claim is false
    2  the ledger cannot support any statement at all

Run:  python3 -m unittest discover -s tool/tests -v
"""
import json
import os
import subprocess
import sys
import tempfile
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, '..', '..'))
TOOL = os.path.join(REPO, 'tool', 'ci', 'golden_chain_verdict.py')
REAL_REGISTRY = os.path.join(REPO, 'tool', 'ci', 'golden-chain-obligations.json')

FIXTURE = 'assets/fixtures/real/lesson-05-sgk-lich-su-va-dia-li-5-b8.json'
LEDGER = 'build/golden-chain'


def _registry(n_obligations=9, n_mirrors=9, fixture=FIXTURE):
    return {
        'fixture': fixture,
        'fixtureIsGitignored': True,
        'ledgerDir': LEDGER,
        'obligations': [
            {'id': 'GC-%02d' % i, 'test': 't.dart', 'claim': 'claim %d' % i}
            for i in range(1, n_obligations + 1)
        ],
        'syntheticMirrors': [
            {'id': 'SYN-%02d' % i, 'test': 'm.dart'}
            for i in range(1, n_mirrors + 1)
        ],
    }


class _World:
    """A throwaway repo root: a registry, a ledger, maybe a fixture."""

    def __init__(self, tmp, registry=None, fixture_on_disk=True):
        self.root = tmp
        self.registry = registry or _registry()
        os.makedirs(os.path.join(tmp, LEDGER), exist_ok=True)
        self.registry_path = os.path.join(tmp, 'registry.json')
        with open(self.registry_path, 'w', encoding='utf-8') as fh:
            json.dump(self.registry, fh)
        if fixture_on_disk:
            p = os.path.join(tmp, self.registry['fixture'])
            os.makedirs(os.path.dirname(p), exist_ok=True)
            with open(p, 'w', encoding='utf-8') as fh:
                fh.write('{}')

    def record(self, rid, exercised, fixture_present=None, kind=None):
        if fixture_present is None:
            fixture_present = exercised
        rec = {
            'id': rid,
            'kind': kind or ('syntheticMirror' if rid.startswith('SYN') else 'goldenChain'),
            'exercised': exercised,
            'reason': None if exercised else 'fixture absent',
            'fixture': None if rid.startswith('SYN') else self.registry['fixture'],
            'fixturePresent': None if rid.startswith('SYN') else fixture_present,
        }
        with open(os.path.join(self.root, LEDGER, rid + '.json'), 'w', encoding='utf-8') as fh:
            json.dump(rec, fh)

    def fill(self, golden_exercised, fixture_present=None):
        for o in self.registry['obligations']:
            self.record(o['id'], golden_exercised, fixture_present)
        for m in self.registry['syntheticMirrors']:
            self.record(m['id'], True)

    def drop_fixture(self):
        os.remove(os.path.join(self.root, self.registry['fixture']))

    def run(self, *args):
        r = subprocess.run(
            [sys.executable, TOOL, '--registry', self.registry_path,
             '--ledger', LEDGER] + list(args),
            cwd=self.root, capture_output=True, text=True,
        )
        return r.returncode, r.stdout + r.stderr


class GoldenChainVerdictTest(unittest.TestCase):

    def world(self, **kw):
        tmp = tempfile.mkdtemp(prefix='wal218-')
        self.addCleanup(lambda: subprocess.run(['rm', '-rf', tmp]))
        return _World(tmp, **kw)

    # ------------------------------------------------------------------ baseline

    def test_fixture_present_and_all_exercised_is_the_only_VERIFIED(self):
        w = self.world()
        w.fill(True)
        rc, out = w.run('--min-obligations', '9')
        self.assertEqual(rc, 0, out)
        self.assertIn('GOLDEN CHAIN VERIFIED', out)
        rc, out = w.run('--min-obligations', '9', '--require-verified')
        self.assertEqual(rc, 0, out)

    # ---------------------------------------------------- the defect WAL-218 names

    def test_fixture_absent_is_UNVERIFIED_and_a_claim_of_PASS_goes_red(self):
        """The measured defect: nine skips, and `All tests passed!` regardless."""
        w = self.world(fixture_on_disk=False)
        w.fill(False)
        rc, out = w.run('--min-obligations', '9')
        self.assertEqual(rc, 0, out)
        self.assertIn('GOLDEN CHAIN UNVERIFIED', out)
        self.assertIn('0/9', out)
        self.assertNotIn('GOLDEN CHAIN VERIFIED', out)
        # …and a run that DARES to claim verification is red.
        rc, out = w.run('--min-obligations', '9', '--require-verified')
        self.assertEqual(rc, 1, out)

    def test_synthetic_mirrors_never_count_towards_the_golden_total(self):
        """SYNTHETIC PASS != GOLDEN VERIFIED — nine green mirrors change nothing."""
        w = self.world(fixture_on_disk=False)
        w.fill(False)          # all nine mirrors exercised, no Golden obligation
        rc, out = w.run('--min-obligations', '9')
        self.assertIn('synthetic mirrors       : 9/9', out)
        self.assertIn('exercised on REAL       : 0', out)
        self.assertIn('GOLDEN CHAIN UNVERIFIED', out)
        self.assertEqual(rc, 0, out)
        self.assertEqual(w.run('--require-verified')[0], 1)

    # ------------------------------------------------------------ the mutations

    def test_deleting_a_test_does_not_improve_coverage(self):
        """Mutation: a declared obligation leaves no record. Even with the fixture."""
        w = self.world()
        w.fill(True)
        os.remove(os.path.join(w.root, LEDGER, 'GC-07.json'))
        rc, out = w.run('--min-obligations', '9')
        self.assertEqual(rc, 2, out)
        self.assertIn('GC-07', out)
        self.assertIn('LEDGER BROKEN', out)

    def test_shrinking_the_registry_is_the_zero_over_zero_PASS_shape(self):
        """Mutation: drop obligations until the denominator flatters the run."""
        w = self.world(registry=_registry(n_obligations=2, n_mirrors=2))
        w.fill(True)
        rc, out = w.run('--min-obligations', '9')
        self.assertEqual(rc, 2, out)
        self.assertIn('floor is 9', out)
        # And the floor is what does the work: without it the shrunken registry
        # would have read as a clean VERIFIED. This is the whole failure mode.
        rc, out = w.run('--min-obligations', '0')
        self.assertEqual(rc, 0, out)
        self.assertIn('GOLDEN CHAIN VERIFIED', out)

    def test_an_empty_registry_can_never_be_verified(self):
        """Mutation: zero obligations. `0/0` must not read as done."""
        w = self.world(registry=_registry(n_obligations=0, n_mirrors=0))
        rc, out = w.run('--min-obligations', '0')
        self.assertIn('GOLDEN CHAIN UNVERIFIED', out)
        self.assertEqual(w.run('--min-obligations', '0', '--require-verified')[0], 1)

    def test_a_gate_that_records_exercised_without_the_fixture_is_a_contradiction(self):
        """Mutation: rewrite goldenChainGate to always record `exercised: true`."""
        w = self.world(fixture_on_disk=False)
        w.fill(True, fixture_present=True)   # the ledger lies
        rc, out = w.run('--min-obligations', '9')
        self.assertEqual(rc, 2, out)
        self.assertIn('fixture is not there', out)
        self.assertEqual(w.run('--min-obligations', '9', '--require-verified')[0], 2)

    def test_a_stale_ledger_from_a_machine_that_had_the_fixture_is_not_coverage(self):
        """Mutation: run with the fixture, delete it, do not re-run the suite."""
        w = self.world()
        w.fill(True)
        w.drop_fixture()
        rc, out = w.run('--min-obligations', '9')
        self.assertEqual(rc, 2, out)
        self.assertIn('stale ledger is not coverage', out)

    def test_a_record_admitting_the_fixture_was_absent_cannot_claim_exercised(self):
        """Mutation: subtler lie — `exercised: true`, `fixturePresent: false`."""
        w = self.world()
        w.fill(True, fixture_present=False)
        rc, out = w.run('--min-obligations', '9')
        self.assertEqual(rc, 2, out)

    def test_no_ledger_at_all_is_an_error_not_an_empty_pass(self):
        """Mutation: never run the suite. Nothing measured is not everything fine."""
        w = self.world()
        rc, out = w.run('--ledger', 'build/does-not-exist', '--min-obligations', '9')
        self.assertEqual(rc, 2, out)
        self.assertIn('has not verified anything', out)

    def test_an_id_no_registry_row_declares_is_rejected(self):
        """Mutation: smuggle a green row in under a name nobody declared."""
        w = self.world()
        w.fill(True)
        w.record('GC-99', True)
        rc, out = w.run('--min-obligations', '9')
        self.assertEqual(rc, 2, out)
        self.assertIn('GC-99', out)

    def test_duplicate_obligation_ids_are_rejected(self):
        reg = _registry()
        reg['obligations'][1]['id'] = reg['obligations'][0]['id']
        w = self.world(registry=reg)
        w.fill(True)
        rc, out = w.run('--min-obligations', '9')
        self.assertEqual(rc, 2, out)
        self.assertIn('duplicate', out)

    # ------------------------------------------------- the shipped registry itself

    def test_the_repo_registry_declares_the_nine_measured_obligations(self):
        with open(REAL_REGISTRY, encoding='utf-8') as fh:
            reg = json.load(fh)
        self.assertGreaterEqual(len(reg['obligations']), 9)
        self.assertEqual(reg['fixture'], FIXTURE)
        self.assertTrue(reg['fixtureIsGitignored'])
        self.assertTrue(reg['ledgerDir'].startswith('build/'))
        ids = [o['id'] for o in reg['obligations']]
        self.assertEqual(len(set(ids)), len(ids))
        for o in reg['obligations']:
            self.assertTrue(os.path.exists(os.path.join(REPO, o['test'])), o['id'])
            self.assertTrue(o['claim'].strip(), o['id'])

    def test_ci_pins_the_floor_and_proves_the_claim_gate_is_live(self):
        with open(os.path.join(REPO, '.github', 'workflows', 'ci.yml'), encoding='utf-8') as fh:
            ci = fh.read()
        self.assertIn('--min-obligations 9', ci)
        self.assertIn('--require-verified', ci)
        self.assertIn('rm -rf build/golden-chain', ci)

    def test_the_golden_fixture_is_not_in_the_git_tree(self):
        """D4 is not negotiable: no version of WAL-218 ends with book content in git."""
        r = subprocess.run(['git', 'ls-files', '--', FIXTURE],
                           cwd=REPO, capture_output=True, text=True)
        self.assertEqual(r.stdout.strip(), '', 'the SGK fixture is tracked by git')


if __name__ == '__main__':
    unittest.main()
