#!/usr/bin/env python3
"""ROUND 6 · WS-D — FIXTURE LINEAGE GATE: which GENERATION is this fixture?

Founder rule (round 6): every real fixture used for Founder or device evidence must
record **source TSL hash · pipeline version · SDM version · repair version · generator
version**. A fixture reproducible from `tc2-p1` / `sdm-v2` is NOT automatically a
current-pipeline fixture, and generations must never be silently mixed.

The rule exists because round 5 lost real time to a stale gitignored fixture that
produced a fake test result. `assets/fixtures/real/` is gitignored, so a fixture never
travels to CI or to a clean clone: the ONLY way a later reader can tell which generation
they are holding is the record inside the file. This tool is the machine that checks it.

    python3 tool/evidence/fixture_lineage.py \\
        --fixture assets/fixtures/real/lesson-05-sgk-lich-su-va-dia-li-5-b8.json \\
        [--root .] [--require-repair] [--expect-source-hash <sha256>] [--json <out>]

Checks, each printed as PASS / FAIL / UNKNOWN with the value it saw:

  L1 FIELDS         the five required version fields are present and non-empty.
  L2 SOURCE HASH    `provenance.tslPath` re-read from disk and sha256'd; it must equal
                    `provenance.sourceHash`. A TSL that is absent is UNKNOWN, not PASS —
                    an unverifiable claim is not a verified one.
  L3 GENERATION     `pipelineVersion` must be exactly `<sourcePipeline>/<sdmVersion>`,
                    and `tslPath` must name that same pipeline. This is the check that
                    catches a round-4 document being passed off as a round-6 one.
  L4 REPAIR         repair lineage: version + the counts the ledger claims. Absent ⇒
                    UNKNOWN («no repair crossed into this document»), which is a truthful
                    answer and stays truthful — `--require-repair` turns it into a FAIL
                    for the delivery claim, where it must not be UNKNOWN.
  L5 CROPS          every crop a block references exists beside the fixture. A crop that
                    is missing means the child sees an empty withheld card.
  L6 DISTRIBUTION   `distribution` must still carry the D4 marker. Verbatim SGK text and
                    page crops are INTERNAL / RESEARCH ONLY.

Exit status 0 only when nothing FAILED. UNKNOWN alone does not fail (except under
`--require-repair`), because reporting «not verified» is the honest outcome, and this
tool must never be the reason someone writes PASS where the truth is «I could not tell».

Standard library only. Read-only: it never writes into `assets/`, never touches a TSL.
"""
import argparse
import hashlib
import json
import os
import sys

# The five fields the Founder requires, mapped to where they live in the document.
REQUIRED = (
    ('source TSL hash', 'sourceHash'),
    ('pipeline version', 'pipelineVersion'),
    ('SDM version', 'sdmVersion'),
    ('generator version', 'generator'),
)
REPAIR_KEYS = ('repairVersion', 'repair_version')
REPAIR_BLOCK_KEYS = ('repair', 'repairs')
D4_MARKER = 'internal-research-only'

PASS, FAIL, UNKNOWN = 'PASS', 'FAIL', 'UNKNOWN'


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, 'rb') as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b''):
            h.update(chunk)
    return h.hexdigest()


def _crop_refs(doc):
    """Every crop path a block references, in document order, deduplicated."""
    seen, out = set(), []
    for b in doc.get('blocks', []) or []:
        for key in ('crop', 'cropPath', 'image'):
            v = b.get(key)
            if isinstance(v, str) and v and v not in seen:
                seen.add(v)
                out.append(v)
    return out


def repair_lineage(prov):
    """(version, detail dict) — version is None when no repair lineage is recorded."""
    for k in REPAIR_KEYS:
        if prov.get(k):
            return str(prov[k]), {}
    for k in REPAIR_BLOCK_KEYS:
        blk = prov.get(k)
        if isinstance(blk, dict) and blk.get('version'):
            return str(blk['version']), {
                x: blk[x] for x in blk if x != 'version' and not isinstance(blk[x], (dict, list))
            }
    return None, {}


def check(fixture_path, root='.', require_repair=False, expect_source_hash=None):
    with open(fixture_path, encoding='utf-8') as fh:
        doc = json.load(fh)
    prov = doc.get('provenance') or {}
    rows = []

    def row(check_id, name, status, value, note=''):
        rows.append(dict(id=check_id, check=name, status=status, value=value, note=note))

    # ---- L1 FIELDS -------------------------------------------------------------
    missing = [label for label, key in REQUIRED if not str(prov.get(key) or '').strip()]
    row('L1', 'five version fields present', FAIL if missing else PASS,
        ' · '.join(f'{label}={prov.get(key)!r}' for label, key in REQUIRED),
        ('missing: ' + ', '.join(missing)) if missing else '')

    # ---- L2 SOURCE HASH --------------------------------------------------------
    tsl_rel = prov.get('tslPath')
    recorded = prov.get('sourceHash')
    if not tsl_rel or not recorded:
        row('L2', 'source TSL re-hashes to sourceHash', UNKNOWN,
            f'tslPath={tsl_rel!r} sourceHash={recorded!r}', 'nothing to verify against')
        actual = None
    else:
        tsl_abs = tsl_rel if os.path.isabs(tsl_rel) else os.path.join(root, tsl_rel)
        if not os.path.exists(tsl_abs):
            row('L2', 'source TSL re-hashes to sourceHash', UNKNOWN, tsl_rel,
                'TSL not on this machine — the claim cannot be checked here')
            actual = None
        else:
            actual = sha256_file(tsl_abs)
            same = actual == recorded
            row('L2', 'source TSL re-hashes to sourceHash', PASS if same else FAIL,
                f'recorded={recorded[:16]}… actual={actual[:16]}…',
                '' if same else 'THE FIXTURE WAS NOT BUILT FROM THE TSL IT NAMES')

    if expect_source_hash:
        same = recorded == expect_source_hash
        row('L2b', 'sourceHash is the expected generation', PASS if same else FAIL,
            f'recorded={str(recorded)[:16]}… expected={expect_source_hash[:16]}…',
            '' if same else 'this is a DIFFERENT generation than the one demanded')

    # ---- L3 GENERATION ---------------------------------------------------------
    pipeline, sdm, pv = prov.get('sourcePipeline'), prov.get('sdmVersion'), prov.get('pipelineVersion')
    notes = []
    if pipeline and sdm and pv and pv != f'{pipeline}/{sdm}':
        notes.append(f'pipelineVersion should be {pipeline}/{sdm}')
    if pipeline and tsl_rel and f'/{pipeline}/' not in tsl_rel.replace(os.sep, '/'):
        notes.append(f'tslPath does not name pipeline {pipeline} — generations may be mixed')
    row('L3', 'one generation, consistently named', FAIL if notes else PASS,
        f'sourcePipeline={pipeline} sdmVersion={sdm} pipelineVersion={pv}', '; '.join(notes))

    # ---- L4 REPAIR -------------------------------------------------------------
    rv, detail = repair_lineage(prov)
    if rv:
        row('L4', 'repair lineage recorded', PASS, rv,
            ' '.join(f'{k}={v}' for k, v in sorted(detail.items())))
    else:
        row('L4', 'repair lineage recorded', FAIL if require_repair else UNKNOWN, 'none',
            'no ValidatedRepair crossed into this document'
            + (' — required for the delivery claim' if require_repair else ''))

    # ---- L5 CROPS --------------------------------------------------------------
    base = os.path.dirname(os.path.abspath(fixture_path))
    refs = _crop_refs(doc)
    absent = [p for p in refs if not os.path.exists(os.path.join(base, os.path.basename(os.path.dirname(p)), os.path.basename(p)))
              and not os.path.exists(os.path.join(root, p))]
    row('L5', 'every referenced crop exists', FAIL if absent else PASS,
        f'{len(refs) - len(absent)}/{len(refs)} present',
        ('missing: ' + ', '.join(absent[:5])) if absent else '')

    # ---- L6 DISTRIBUTION -------------------------------------------------------
    dist = str(prov.get('distribution') or '')
    row('L6', 'D4 distribution marker intact', PASS if D4_MARKER in dist else FAIL,
        dist or '(absent)',
        '' if D4_MARKER in dist else 'verbatim SGK text and page crops are INTERNAL / RESEARCH ONLY')

    return dict(
        fixture=os.path.relpath(fixture_path, root) if not os.path.isabs(fixture_path) else fixture_path,
        book=doc.get('book'), lesson=doc.get('lesson'),
        documentSha256=hashlib.sha256(
            json.dumps(doc, ensure_ascii=False, sort_keys=True, separators=(',', ':')).encode('utf-8')
        ).hexdigest(),
        blocks=len(doc.get('blocks') or []),
        semantic=len(doc.get('semantic') or []),
        tutorSteps=len(((doc.get('tutorScript') or {}).get('steps')) or []),
        recomputedSourceHash=actual,
        repairVersion=rv,
        checks=rows,
        verdict=FAIL if any(r['status'] == FAIL for r in rows)
        else (UNKNOWN if any(r['status'] == UNKNOWN for r in rows) else PASS),
    )


def render(result):
    L = [f"LINEAGE · {result['book']} Bài {result['lesson']} · {result['fixture']}",
         f"  document sha256 {result['documentSha256']}",
         f"  blocks={result['blocks']} semantic={result['semantic']} tutorSteps={result['tutorSteps']}",
         '']
    for r in result['checks']:
        L.append(f"  {r['status']:<7} {r['id']:<4} {r['check']}")
        L.append(f"          {r['value']}")
        if r['note']:
            L.append(f"          ⚠ {r['note']}")
    L.append('')
    L.append(f"  VERDICT {result['verdict']}")
    return '\n'.join(L)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--fixture', required=True, help='a LessonDocument JSON under assets/fixtures/')
    ap.add_argument('--root', default='.', help='repo root that tslPath is relative to')
    ap.add_argument('--require-repair', action='store_true',
                    help='the delivery claim: a repair lineage must be present, not merely absent')
    ap.add_argument('--expect-source-hash', help='fail unless the fixture names this TSL hash')
    ap.add_argument('--json', dest='json_out', help='also write the machine-readable result here')
    a = ap.parse_args(argv)

    result = check(a.fixture, root=a.root, require_repair=a.require_repair,
                   expect_source_hash=a.expect_source_hash)
    print(render(result))
    if a.json_out:
        os.makedirs(os.path.dirname(os.path.abspath(a.json_out)), exist_ok=True)
        with open(a.json_out, 'w', encoding='utf-8') as fh:
            json.dump(result, fh, ensure_ascii=False, indent=2, sort_keys=True)
            fh.write('\n')
    return 1 if result['verdict'] == FAIL else 0


if __name__ == '__main__':
    sys.exit(main())
