#!/usr/bin/env python3
"""Round 5 · Lane D — PACK SNAPSHOT → REBUILD → DELTA (Founder order §13).

Why this exists: `tool/ui/pack_provenance.py` now derives `attachmentRule` from
`tool/ui/lesson_attach.RULE` (round 4 fix a281ea5), which moved to `capped-toc-v2`,
while every pack on disk still stamps `capped-toc-v1`. `pack_provenance.py verify`
therefore FAILS on all 12 default packs: the provenance is stale. §13 approves a
rebuild — **but only behind a snapshot**, so the OLD baseline stays reproducible.

The order of operations is the point:

    snapshot  →  rebuild  →  verify  →  delta  →  (audit a sample of the delta)

`snapshot` is refused if it would overwrite an existing snapshot; `rebuild` is
refused if no snapshot of the current packs exists. That is the whole guard: a
rebuild can never be the first thing that happens to a pack.

Subcommands
-----------
    packs.py snapshot <dir> [--pack-dir DIR] [--note TEXT]
        Copy all 12 packs + record file sha256, the full buildProvenance, the
        verify result, the baseline metrics measured against them, and the
        pipeline version (repo HEAD, builder commit, attachment rule). Writes
        MANIFEST.json, BASELINE-METRICS.json, SHA256SUMS and README.md.

    packs.py rebuild <snapshot-dir> [--grades 1,2,…] [--pack-dir DIR]
        Run tool/ui/build_lesson_index.py for each grade with DEFAULT flags,
        capture stdout/rc/timing, then re-verify. Writes REBUILD-RUN.json into
        the snapshot dir's sibling `after/`.

    packs.py verify [--pack-dir DIR]
        Thin wrapper over pack_provenance.verify_file for all 12 packs.

    packs.py metrics [--pack-dir DIR] [--out FILE]
        The baseline metrics only (per grade, per activity family).

    packs.py delta <before-dir> [--pack-dir DIR] [--out FILE] [--md FILE]
        Classify every activity of every family as unchanged / content-changed /
        moved-lesson / appeared / disappeared, per grade and per family.
        Identity is content-independent (book + page + kind), so a block whose
        lesson attachment changed is a MOVE, not a delete + an add.

    packs.py restore <snapshot-dir> [--pack-dir DIR]
        Put the snapshotted packs back on disk and check their sha256 — the
        executable form of "the OLD baseline is still reproducible".

Rules this file is written under: Lane D owns tool/corpus/legacy/**; it CALLS
tool/ui/build_lesson_index.py and pack_provenance.py, and never edits pipeline
code. Packs and any verbatim SGK text stay in gitignored directories — this tool
writes counts and hashes into the repo, never content.
"""
import argparse
import collections
import hashlib
import json
import os
import platform
import shutil
import subprocess
import sys
import time
from datetime import datetime, timezone

HERE = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.abspath(os.path.join(HERE, '..', '..', '..'))
sys.path.insert(0, os.path.join(REPO_ROOT, 'tool', 'ui'))
sys.path.insert(0, HERE)

import pack_provenance  # noqa: E402  (tool/ui — called, never edited)
import lesson_attach    # noqa: E402

GRADES = tuple(range(1, 13))
SCHEMA = 'lane-d-pack-snapshot-v1'
DEFAULT_PACK_DIR = os.path.join(REPO_ROOT, 'assets', 'pack')
BUILDER = os.path.join(REPO_ROOT, 'tool', 'ui', 'build_lesson_index.py')

# Every activity family in a pack, with the identity that survives a re-attachment.
# `key` = the fields that make this activity THIS activity regardless of which lesson
# it ends up attached to; `content` = the fields whose change means the text moved.
FAMILIES = {
    'toanExercises':   dict(shape='by_lesson', key=('book', 'page', 'expr'),          content=('expr', 'skillCaseId')),
    'tvReadings':      dict(shape='list',      key=('book', 'page', 'passage'),       content=('passage', 'questions')),
    'tvWritings':      dict(shape='list',      key=('book', 'page', 'prompt'),        content=('prompt',)),
    'suSources':       dict(shape='list',      key=('book', 'pagePdf', 'excerpt'),    content=('excerpt', 'attribution', 'samGloss')),
    'khoaExperiments': dict(shape='list',      key=('book', 'pagePdf', 'title'),      content=('title', 'chuanBi', 'tienHanh', 'duDoan', 'quanSat')),
    'diaMaps':         dict(shape='list',      key=('book', 'asset'),                 content=('caption', 'questions', 'bboxFrac')),
    'sourceAssets':    dict(shape='list',      key=('asset',),                        content=('printedCaption', 'samGloss', 'bboxFrac')),
}
NON_ACTIVITY = ('subjects', 'books')


# ------------------------------------------------------------------ helpers
def now_utc():
    return datetime.now(timezone.utc).replace(microsecond=0).strftime('%Y-%m-%dT%H:%M:%SZ')


def sha256_file(path, chunk=1 << 20):
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        for b in iter(lambda: f.read(chunk), b''):
            h.update(b)
    return h.hexdigest()


def _digest(v):
    """A short, stable digest of any JSON value — never the value itself.

    Verbatim SGK text never leaves the gitignored pack; every identity and every
    content comparison in this tool is over hashes (Founder D4).
    """
    s = json.dumps(v, ensure_ascii=False, sort_keys=True, separators=(',', ':'))
    return hashlib.sha256(s.encode('utf-8')).hexdigest()[:16]


def _git(args, cwd=REPO_ROOT):
    try:
        r = subprocess.run(['git'] + list(args), cwd=cwd, capture_output=True, text=True, timeout=30)
    except (OSError, subprocess.SubprocessError):
        return None
    return r.stdout.strip() if r.returncode == 0 else None


def pack_path(pack_dir, grade):
    return os.path.join(pack_dir, f'lesson-index-g{grade}.json')


def load_pack(pack_dir, grade):
    p = pack_path(pack_dir, grade)
    if not os.path.exists(p):
        return None
    with open(p, encoding='utf-8') as f:
        return json.load(f)


def pipeline_version():
    """Everything that decides what a rebuild would produce."""
    return {
        'repoHead': _git(['rev-parse', 'HEAD']) or 'unknown',
        'repoBranch': _git(['rev-parse', '--abbrev-ref', 'HEAD']) or 'unknown',
        'repoDirty': bool(_git(['status', '--porcelain'])),
        'builderCommit': _git(['log', '-n', '1', '--format=%H', '--', 'tool/ui/build_lesson_index.py']) or 'unknown',
        'builderVersion': pack_provenance.builder_version(BUILDER),
        'packProvenanceCommit': _git(['log', '-n', '1', '--format=%H', '--', 'tool/ui/pack_provenance.py']) or 'unknown',
        'lessonAttachCommit': _git(['log', '-n', '1', '--format=%H', '--', 'tool/ui/lesson_attach.py']) or 'unknown',
        'attachmentRule': lesson_attach.RULE,
        'provenanceSchema': pack_provenance.SCHEMA,
        'python': platform.python_version(),
        'platform': platform.platform(),
    }


# ------------------------------------------------------------------ metrics
def iter_activities(pack):
    """(family, lesson, key_digest, content_digest, book) for every activity in a pack."""
    for fam, spec in FAMILIES.items():
        blob = pack.get(fam)
        if not blob:
            continue
        if spec['shape'] == 'by_lesson':
            items = [(int(les), e) for les, arr in blob.items() for e in (arr or [])]
        else:
            items = [(e.get('lesson'), e) for e in blob]
        for lesson, e in items:
            e = e or {}
            key = _digest([fam] + [e.get(k) for k in spec['key']])
            content = _digest([e.get(k) for k in spec['content']])
            yield fam, lesson, key, content, e.get('book') or e.get('sourceDocumentId') or ''


def pack_metrics(pack):
    """Counts only — never content. The baseline the OLD packs must stay reproducible against."""
    fam_counts, fam_lessons, per_book = {}, {}, collections.Counter()
    openable = collections.defaultdict(set)   # book -> lessons with >= 1 activity
    for fam, lesson, _k, _c, book in iter_activities(pack):
        fam_counts[fam] = fam_counts.get(fam, 0) + 1
        fam_lessons.setdefault(fam, set()).add((book, lesson))
        per_book[book] += 1
        if lesson is not None:
            openable[book].add(lesson)
    subjects = pack.get('subjects') or {}
    catalogue = sum(len(b.get('lessons') or []) for v in subjects.values() for b in v)
    prov = pack.get('buildProvenance') or {}
    return {
        'grade': pack.get('grade'),
        'version': pack.get('version'),
        'subjects': len(subjects),
        'books': len(pack.get('books') or []),
        'catalogueLessons': catalogue,
        'activityFamilies': {f: fam_counts.get(f, 0) for f in FAMILIES},
        'activitiesTotal': sum(fam_counts.values()),
        'familyLessonsCovered': {f: len(fam_lessons.get(f, ())) for f in FAMILIES},
        'openableLessons': sum(len(v) for v in openable.values()),
        'openableBooks': len(openable),
        'activitiesPerBook': dict(sorted(per_book.items())),
        'provenance': {k: prov.get(k) for k in ('packVersion', 'builderVersion', 'gitSha', 'builtAt', 'attachmentRule', 'contentHash', 'experimental')},
    }


def all_metrics(pack_dir, grades=GRADES):
    out, missing = {}, []
    for g in grades:
        pack = load_pack(pack_dir, g)
        if pack is None:
            missing.append(g)
            continue
        out[str(g)] = pack_metrics(pack)
    totals = collections.Counter()
    for m in out.values():
        for f, n in m['activityFamilies'].items():
            totals[f] += n
        totals['__activities'] += m['activitiesTotal']
        totals['__openable'] += m['openableLessons']
        totals['__catalogue'] += m['catalogueLessons']
    return {
        'schema': SCHEMA + '/metrics',
        'measuredAt': now_utc(),
        'packDir': pack_dir,
        'grades': sorted(out, key=int),
        'missingGrades': missing,
        'perGrade': out,
        'totals': {
            'activityFamilies': {f: totals[f] for f in FAMILIES},
            'activities': totals['__activities'],
            'openableLessons': totals['__openable'],
            'catalogueLessons': totals['__catalogue'],
        },
    }


def verify_all(pack_dir, grades=GRADES):
    rows = {}
    for g in grades:
        p = pack_path(pack_dir, g)
        rows[str(g)] = {'path': p, 'exists': os.path.exists(p),
                        'problems': pack_provenance.verify_file(p) if os.path.exists(p) else ['missing']}
    n_ok = sum(1 for r in rows.values() if not r['problems'])
    return {'schema': SCHEMA + '/verify', 'checkedAt': now_utc(),
            'attachmentRuleExpected': lesson_attach.RULE,
            'pass': n_ok == len(rows), 'ok': n_ok, 'total': len(rows), 'perGrade': rows}


# ------------------------------------------------------------------ snapshot
README = """# Packs BEFORE the round-5 rebuild — the reproducible OLD baseline

`{schema}` · snapshotted {when} · {n} packs · **nothing here is trusted teaching content**

Founder order §13 approves the pack rebuild *because the provenance is stale*, and requires that
after the rebuild **the OLD baseline is still reproducible**. This directory is that guarantee.
It is written once and never overwritten: a second snapshot must use a new directory.

## Why the rebuild was needed

`tool/ui/pack_provenance.py` derives `attachmentRule` from `tool/ui/lesson_attach.RULE`, which is
`{rule_now}`. Every pack in this snapshot stamps `{rule_then}`. `pack_provenance.py verify`
therefore failed on **{n_fail} of {n}** of them — recorded verbatim in `MANIFEST.json` →
`verifyAtSnapshot`. The packs were not wrong; their manifests described a rule they were not built
with, which is a provenance lie, and a lie in a manifest is exactly what a rebuild is for.

## What is here

| file | what it holds |
|---|---|
| `packs/lesson-index-g<N>.json` | the 12 pack files, byte-for-byte as they were on disk |
| `SHA256SUMS` | sha256 of each of those files (`shasum -c SHA256SUMS` from `packs/`) |
| `MANIFEST.json` | per pack: file sha256, size, the full `buildProvenance`, the verify result at snapshot time |
| `BASELINE-METRICS.json` | the metrics measured against these packs: per grade, per activity family, openable lessons, catalogue lessons |
| `PIPELINE-VERSION.json` | repo HEAD, builder commit, `lesson_attach` commit + rule, provenance schema, interpreter and platform |

Pack content is derived from copyrighted SGK, so this directory lives under gitignored `poc-out/`
and is never committed (Founder D4). What the repo carries is counts and hashes.

## How to reproduce the OLD baseline

```bash
# 1. put the old packs back on disk (checks every sha256 as it goes)
python3 tool/corpus/legacy/packs.py restore {selfdir}

# 2. re-measure them — output is byte-identical to BASELINE-METRICS.json
#    except for the `measuredAt` / `packDir` fields
python3 tool/corpus/legacy/packs.py metrics --out /tmp/old-metrics.json

# 3. re-observe the failure that motivated the rebuild
python3 tool/ui/pack_provenance.py verify assets/pack/lesson-index-g*.json   # exits 1
```

`restore` refuses to write a pack whose stored sha256 does not match, so a corrupted snapshot fails
loudly rather than quietly restoring something else.

## How to get back to the NEW packs

```bash
for g in $(seq 1 12); do python3 tool/ui/build_lesson_index.py $g; done
python3 tool/ui/pack_provenance.py verify assets/pack/lesson-index-g*.json   # exits 0
```

The rebuild is deterministic apart from `builtAt` (and therefore `packVersion`); `contentHash` is
the field to compare across builds.

## What this snapshot does not claim

- It does not say the OLD packs were correct. Round 4 measured **0.727 false trust** on an audited
  sample of what the old product served (`docs/research/legacy-reprocess/ROUND4-BATCH-1-REPORT.md` §5).
- It does not say the NEW packs are correct either. A rebuild fixes a manifest, not a corpus.
- It sets no threshold. `trusted` and `eligible for teaching` stay 0 until the Founder sets a record.
"""


def cmd_snapshot(args):
    out = os.path.abspath(args.dir)
    if os.path.exists(out) and os.listdir(out):
        print(f'REFUSED: {out} exists and is not empty — a snapshot is never overwritten.', file=sys.stderr)
        print('         Use a new directory; the old baseline must stay reproducible.', file=sys.stderr)
        return 2
    pack_dir = os.path.abspath(args.pack_dir)
    os.makedirs(os.path.join(out, 'packs'), exist_ok=True)

    ver = verify_all(pack_dir)
    met = all_metrics(pack_dir)
    pipe = pipeline_version()

    entries, sums = {}, []
    rule_then = set()
    for g in GRADES:
        src = pack_path(pack_dir, g)
        if not os.path.exists(src):
            entries[str(g)] = {'present': False}
            continue
        dst = os.path.join(out, 'packs', os.path.basename(src))
        shutil.copy2(src, dst)
        h = sha256_file(dst)
        if h != sha256_file(src):
            print(f'REFUSED: pack g{g} changed while being copied', file=sys.stderr)
            return 3
        pack = load_pack(pack_dir, g)
        prov = pack.get('buildProvenance') or {}
        rule_then.add(prov.get('attachmentRule'))
        sums.append(f'{h}  lesson-index-g{g}.json')
        entries[str(g)] = {
            'present': True, 'file': os.path.basename(src), 'sha256': h,
            'bytes': os.path.getsize(dst), 'mtime': datetime.fromtimestamp(os.path.getmtime(src), timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ'),
            'buildProvenance': prov,
            'verifyProblems': ver['perGrade'][str(g)]['problems'],
        }

    manifest = {
        'schema': SCHEMA,
        'snapshotOf': 'assets/pack/lesson-index-g<N>.json (the 12 default packs)',
        'snapshotAt': now_utc(),
        'snapshotDir': out,
        'sourcePackDir': pack_dir,
        'note': args.note or '',
        'reason': 'Founder §13: rebuild approved because the provenance is stale — snapshot first, '
                  'the OLD baseline must stay reproducible.',
        'pipelineVersion': pipe,
        'verifyAtSnapshot': ver,
        'packs': entries,
        'baselineMetricsFile': 'BASELINE-METRICS.json',
    }
    _write_json(manifest, os.path.join(out, 'MANIFEST.json'))
    _write_json(met, os.path.join(out, 'BASELINE-METRICS.json'))
    _write_json(pipe, os.path.join(out, 'PIPELINE-VERSION.json'))
    with open(os.path.join(out, 'SHA256SUMS'), 'w', encoding='utf-8') as f:
        f.write('\n'.join(sums) + '\n')
    with open(os.path.join(out, 'README.md'), 'w', encoding='utf-8') as f:
        f.write(README.format(schema=SCHEMA, when=manifest['snapshotAt'],
                              n=sum(1 for e in entries.values() if e.get('present')),
                              n_fail=ver['total'] - ver['ok'],
                              rule_now=lesson_attach.RULE,
                              rule_then=', '.join(sorted(str(r) for r in rule_then)) or 'unknown',
                              selfdir=out))
    print(f'snapshot → {out}')
    print(f'  packs {sum(1 for e in entries.values() if e.get("present"))}/12 · '
          f'verify at snapshot: {ver["ok"]}/{ver["total"]} OK ({"PASS" if ver["pass"] else "FAIL"})')
    print(f'  attachmentRule stamped: {sorted(str(r) for r in rule_then)} · code says {lesson_attach.RULE!r}')
    print(f'  activities {met["totals"]["activities"]} · openable lessons {met["totals"]["openableLessons"]}')
    return 0


def _write_json(obj, path):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(obj, f, ensure_ascii=False, indent=1, sort_keys=False)
        f.write('\n')


# ------------------------------------------------------------------ rebuild
def cmd_rebuild(args):
    snap = os.path.abspath(args.snapshot)
    man = os.path.join(snap, 'MANIFEST.json')
    if not os.path.exists(man):
        print(f'REFUSED: no snapshot manifest at {man} — snapshot before you rebuild (§13).', file=sys.stderr)
        return 2
    manifest = json.load(open(man, encoding='utf-8'))
    pack_dir = os.path.abspath(args.pack_dir)

    # The snapshot must describe the packs that are actually on disk right now, or
    # the "OLD baseline" it preserves is not the baseline being replaced.
    drift = []
    for g in GRADES:
        e = manifest['packs'].get(str(g)) or {}
        p = pack_path(pack_dir, g)
        if not e.get('present'):
            continue
        if not os.path.exists(p):
            drift.append(f'g{g}: missing on disk')
        elif sha256_file(p) != e['sha256']:
            drift.append(f'g{g}: sha256 on disk != snapshot')
    if drift:
        print('REFUSED: the packs on disk are not the ones in the snapshot:', file=sys.stderr)
        for d in drift:
            print('  - ' + d, file=sys.stderr)
        return 3

    grades = [int(x) for x in args.grades.split(',')] if args.grades else list(GRADES)
    env = dict(os.environ)
    for k in ('PATTERN_ROUTER', 'UNITS_SOURCE', 'ROUTE_EXPLAIN'):
        env.pop(k, None)                       # DEFAULT build: no experiment flags
    env['ATTACH_LOG_DIR'] = args.attach_log_dir

    runs = []
    t_all = time.time()
    for g in grades:
        t = time.time()
        r = subprocess.run([sys.executable, BUILDER, str(g)], cwd=REPO_ROOT, env=env,
                           capture_output=True, text=True)
        runs.append({'grade': g, 'rc': r.returncode, 'seconds': round(time.time() - t, 2),
                     'stdout': r.stdout.strip().splitlines()[-6:], 'stderr': r.stderr.strip()[-2000:]})
        print(f'  g{g}: rc={r.returncode} {round(time.time() - t, 1)}s')
        if r.returncode != 0:
            print(r.stderr[-2000:], file=sys.stderr)

    ver = verify_all(pack_dir, grades)
    met = all_metrics(pack_dir, grades)
    out = {
        'schema': SCHEMA + '/rebuild',
        'ranAt': now_utc(),
        'seconds': round(time.time() - t_all, 1),
        'snapshotDir': snap,
        'packDir': pack_dir,
        'gradesRequested': grades,
        'flags': 'DEFAULT (PATTERN_ROUTER / UNITS_SOURCE / ROUTE_EXPLAIN unset)',
        'attachLogDir': args.attach_log_dir,
        'pipelineVersion': pipeline_version(),
        'runs': runs,
        'allRcZero': all(r['rc'] == 0 for r in runs),
        'verifyAfter': ver,
        'metricsAfter': met,
        'newPackSha256': {str(g): sha256_file(pack_path(pack_dir, g)) for g in grades if os.path.exists(pack_path(pack_dir, g))},
    }
    dest = args.out or os.path.join(os.path.dirname(snap), 'after', 'REBUILD-RUN.json')
    _write_json(out, dest)
    print(f'rebuild → {dest}')
    print(f'  {sum(1 for r in runs if r["rc"] == 0)}/{len(runs)} builds rc=0 · '
          f'verify after: {ver["ok"]}/{ver["total"]} OK ({"PASS" if ver["pass"] else "FAIL"})')
    return 0 if (out['allRcZero'] and ver['pass']) else 1


# ------------------------------------------------------------------ delta
def _index(pack):
    """key_digest -> (family, lesson, content_digest, book). Duplicate keys keep a list."""
    idx = collections.defaultdict(list)
    for fam, lesson, key, content, book in iter_activities(pack):
        idx[key].append((fam, lesson, content, book))
    return idx


def delta_pack(before, after):
    """Classify every activity. Identity ignores the lesson, so a re-attachment is a MOVE."""
    b, a = _index(before), _index(after)
    rows = []
    for key in set(b) | set(a):
        bl, al = b.get(key, []), a.get(key, [])
        # Pair positionally within a key (duplicates are rare and identical by construction).
        for i in range(max(len(bl), len(al))):
            bi = bl[i] if i < len(bl) else None
            ai = al[i] if i < len(al) else None
            if bi and not ai:
                rows.append(dict(key=key, family=bi[0], book=bi[3], verdict='disappeared',
                                 lessonBefore=bi[1], lessonAfter=None))
            elif ai and not bi:
                rows.append(dict(key=key, family=ai[0], book=ai[3], verdict='appeared',
                                 lessonBefore=None, lessonAfter=ai[1]))
            else:
                moved = bi[1] != ai[1]
                changed = bi[2] != ai[2]
                verdict = 'moved-lesson' if moved else ('content-changed' if changed else 'unchanged')
                rows.append(dict(key=key, family=ai[0], book=ai[3], verdict=verdict,
                                 lessonBefore=bi[1], lessonAfter=ai[1], contentChanged=changed))
    return rows


VERDICTS = ('unchanged', 'content-changed', 'moved-lesson', 'appeared', 'disappeared')


def cmd_delta(args):
    before_dir = os.path.join(os.path.abspath(args.before), 'packs')
    if not os.path.isdir(before_dir):
        print(f'REFUSED: no snapshotted packs at {before_dir}', file=sys.stderr)
        return 2
    pack_dir = os.path.abspath(args.pack_dir)

    per_grade, all_rows = {}, []
    for g in GRADES:
        b = load_pack(before_dir, g)
        a = load_pack(pack_dir, g)
        if b is None or a is None:
            per_grade[str(g)] = {'missing': {'before': b is None, 'after': a is None}}
            continue
        rows = delta_pack(b, a)
        for r in rows:
            r['grade'] = g
        all_rows += rows
        by_fam = collections.defaultdict(collections.Counter)
        for r in rows:
            by_fam[r['family']][r['verdict']] += 1
        bm, am = pack_metrics(b), pack_metrics(a)
        per_grade[str(g)] = {
            'verdicts': dict(collections.Counter(r['verdict'] for r in rows)),
            'byFamily': {f: dict(c) for f, c in sorted(by_fam.items())},
            'activitiesBefore': bm['activitiesTotal'], 'activitiesAfter': am['activitiesTotal'],
            'openableLessonsBefore': bm['openableLessons'], 'openableLessonsAfter': am['openableLessons'],
            'catalogueLessonsBefore': bm['catalogueLessons'], 'catalogueLessonsAfter': am['catalogueLessons'],
            'contentHashBefore': (b.get('buildProvenance') or {}).get('contentHash'),
            'contentHashAfter': (a.get('buildProvenance') or {}).get('contentHash'),
            'contentIdentical': (b.get('buildProvenance') or {}).get('contentHash') == (a.get('buildProvenance') or {}).get('contentHash'),
            'attachmentRuleBefore': (b.get('buildProvenance') or {}).get('attachmentRule'),
            'attachmentRuleAfter': (a.get('buildProvenance') or {}).get('attachmentRule'),
        }

    by_fam_total = collections.defaultdict(collections.Counter)
    for r in all_rows:
        by_fam_total[r['family']][r['verdict']] += 1
    totals = collections.Counter(r['verdict'] for r in all_rows)
    moved = [r for r in all_rows if r['verdict'] == 'moved-lesson']
    out = {
        'schema': SCHEMA + '/delta',
        'computedAt': now_utc(),
        'beforeDir': os.path.abspath(args.before), 'afterPackDir': pack_dir,
        'identity': {f: FAMILIES[f]['key'] for f in FAMILIES},
        'identityNote': 'identity deliberately excludes `lesson`, so a re-attached activity is a MOVE, '
                        'not a disappearance plus an appearance',
        'totals': dict(totals),
        'activitiesBefore': sum(v.get('activitiesBefore', 0) for v in per_grade.values()),
        'activitiesAfter': sum(v.get('activitiesAfter', 0) for v in per_grade.values()),
        'byFamily': {f: dict(c) for f, c in sorted(by_fam_total.items())},
        'perGrade': per_grade,
        'movedRows': [{k: r[k] for k in ('grade', 'family', 'book', 'lessonBefore', 'lessonAfter', 'key')} for r in moved],
        'appearedRows': [{k: r[k] for k in ('grade', 'family', 'book', 'lessonAfter', 'key')} for r in all_rows if r['verdict'] == 'appeared'],
        'disappearedRows': [{k: r[k] for k in ('grade', 'family', 'book', 'lessonBefore', 'key')} for r in all_rows if r['verdict'] == 'disappeared'],
        'changedRows': [{k: r[k] for k in ('grade', 'family', 'book', 'lessonAfter', 'key')} for r in all_rows if r['verdict'] == 'content-changed'],
    }
    dest = args.out or os.path.join(REPO_ROOT, 'poc-out', 'round5', 'legacy', 'pack-delta.json')
    _write_json(out, dest)
    print(f'delta → {dest}')
    n = sum(totals.values())
    for v in VERDICTS:
        print(f'  {v:16s} {totals.get(v, 0):5d}  ({(totals.get(v, 0) / n if n else 0):.1%})')
    ident = [g for g, v in per_grade.items() if v.get('contentIdentical')]
    print(f'  content-identical grades: {len(ident)}/12 {sorted(ident, key=int)}')
    if args.md:
        _write_delta_md(out, args.md)
        print(f'markdown → {args.md}')
    return 0


def _write_delta_md(d, path):
    L = []
    L.append('| grade | activities before | after | unchanged | content-changed | moved lesson | appeared | disappeared | content hash identical |')
    L.append('|---|---|---|---|---|---|---|---|---|')
    for g in sorted(d['perGrade'], key=int):
        v = d['perGrade'][g]
        if 'verdicts' not in v:
            continue
        c = v['verdicts']
        L.append(f'| g{g} | {v["activitiesBefore"]} | {v["activitiesAfter"]} | '
                 f'{c.get("unchanged", 0)} | {c.get("content-changed", 0)} | {c.get("moved-lesson", 0)} | '
                 f'{c.get("appeared", 0)} | {c.get("disappeared", 0)} | {"yes" if v["contentIdentical"] else "**no**"} |')
    t = d['totals']
    L.append(f'| **all** | **{d["activitiesBefore"]}** | **{d["activitiesAfter"]}** | '
             f'**{t.get("unchanged", 0)}** | **{t.get("content-changed", 0)}** | **{t.get("moved-lesson", 0)}** | '
             f'**{t.get("appeared", 0)}** | **{t.get("disappeared", 0)}** | |')
    L.append('')
    L.append('| activity family | unchanged | content-changed | moved lesson | appeared | disappeared |')
    L.append('|---|---|---|---|---|---|')
    for f, c in d['byFamily'].items():
        L.append(f'| `{f}` | {c.get("unchanged", 0)} | {c.get("content-changed", 0)} | {c.get("moved-lesson", 0)} | '
                 f'{c.get("appeared", 0)} | {c.get("disappeared", 0)} |')
    os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
    with open(path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(L) + '\n')


# ------------------------------------------------------------------ restore / verify / metrics
def cmd_restore(args):
    snap = os.path.abspath(args.snapshot)
    manifest = json.load(open(os.path.join(snap, 'MANIFEST.json'), encoding='utf-8'))
    pack_dir = os.path.abspath(args.pack_dir)
    os.makedirs(pack_dir, exist_ok=True)
    n = 0
    for g in GRADES:
        e = manifest['packs'].get(str(g)) or {}
        if not e.get('present'):
            continue
        src = os.path.join(snap, 'packs', e['file'])
        if sha256_file(src) != e['sha256']:
            print(f'REFUSED: snapshotted g{g} does not match its recorded sha256 — snapshot corrupt', file=sys.stderr)
            return 3
        shutil.copy2(src, pack_path(pack_dir, g))
        n += 1
    print(f'restored {n} pack(s) → {pack_dir} (every sha256 checked)')
    v = verify_all(pack_dir)
    print(f'  verify on the restored packs: {v["ok"]}/{v["total"]} OK — '
          f'{"PASS" if v["pass"] else "FAIL (expected: this is the stale-provenance state)"}')
    return 0


def cmd_verify(args):
    v = verify_all(os.path.abspath(args.pack_dir))
    for g in sorted(v['perGrade'], key=int):
        r = v['perGrade'][g]
        print(('OK   ' if not r['problems'] else 'FAIL ') + f'g{g}' + ('' if not r['problems'] else '  ' + '; '.join(r['problems'])))
    print(f'{v["ok"]}/{v["total"]} — {"PASS" if v["pass"] else "FAIL"}')
    if args.out:
        _write_json(v, args.out)
    return 0 if v['pass'] else 1


def cmd_metrics(args):
    m = all_metrics(os.path.abspath(args.pack_dir))
    if args.out:
        _write_json(m, args.out)
        print(f'metrics → {args.out}')
    print(json.dumps(m['totals'], ensure_ascii=False, indent=1))
    return 0


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    sub = ap.add_subparsers(dest='cmd', required=True)

    s = sub.add_parser('snapshot'); s.add_argument('dir'); s.add_argument('--pack-dir', default=DEFAULT_PACK_DIR); s.add_argument('--note', default=''); s.set_defaults(fn=cmd_snapshot)
    s = sub.add_parser('rebuild'); s.add_argument('snapshot'); s.add_argument('--grades', default=''); s.add_argument('--pack-dir', default=DEFAULT_PACK_DIR); s.add_argument('--out', default=''); s.add_argument('--attach-log-dir', default=os.path.join(REPO_ROOT, 'poc-out', 'round5', 'legacy', 'attach-log')); s.set_defaults(fn=cmd_rebuild)
    s = sub.add_parser('delta'); s.add_argument('before'); s.add_argument('--pack-dir', default=DEFAULT_PACK_DIR); s.add_argument('--out', default=''); s.add_argument('--md', default=''); s.set_defaults(fn=cmd_delta)
    s = sub.add_parser('restore'); s.add_argument('snapshot'); s.add_argument('--pack-dir', default=DEFAULT_PACK_DIR); s.set_defaults(fn=cmd_restore)
    s = sub.add_parser('verify'); s.add_argument('--pack-dir', default=DEFAULT_PACK_DIR); s.add_argument('--out', default=''); s.set_defaults(fn=cmd_verify)
    s = sub.add_parser('metrics'); s.add_argument('--pack-dir', default=DEFAULT_PACK_DIR); s.add_argument('--out', default=''); s.set_defaults(fn=cmd_metrics)

    a = ap.parse_args(argv)
    return a.fn(a)


if __name__ == '__main__':
    sys.exit(main())
