#!/usr/bin/env python3
"""Round 4 · Lane D — LEGACY REPROCESS SCOREBOARD (measurement only; no threshold, no PASS/FAIL).

    python3 tool/corpus/legacy/scoreboard.py
    python3 tool/corpus/legacy/scoreboard.py --registry … --legacy-out … --out-md … --out-json …

Reads (never writes) the registry of legacy lessons in scope and every batch directory under
poc-out/round4/legacy/, and answers exactly the Founder's scoreboard questions:

    total legacy lessons in scope · pending · reprocessed · independently audited ·
    trusted · partial · withheld · rejected · eligible for teaching

with denominators stated beside every count (D5: canonical 3,679 historical · ranged 3,381 · in scope 243),
plus OLD vs NEW false-trust rates per failure class with Wilson 95 % CIs.

THE THREE RULES THIS FILE ENCODES
  1. REPROCESSED ≠ TRUSTED. `reprocessed` counts lessons the pipeline produced a Trusted Structured Lesson
     for. `trusted` counts lessons that ALSO cleared an independent audit against a FOUNDER-SET threshold.
     No threshold record exists (`docs/research/legacy-reprocess/THRESHOLDS.json` absent) → trusted = 0,
     and the reason is printed, not hidden. The tool never invents a threshold.
  2. `eligible_for_teaching` is `trusted` ∧ a Founder teaching authorisation in the same record → 0 today.
     Legacy content is never a trusted teaching source on the pipeline's own say-so.
  3. Withheld is a RESULT, not a failure: a lesson whose blocks the pipeline refused to serve is counted
     as withheld / partial, never guessed and never quietly dropped.

Lesson state (mechanical, from the batch outputs alone):
    PENDING       in the registry, in no batch
    REJECTED      the batch ran but produced no TSL for the lesson (the pipeline refused the lesson)
    WITHHELD      a TSL exists but 0 learning blocks are trusted — nothing can be served
    PARTIAL       some learning blocks trusted, some withheld (sourceability PARTIAL)
    FULL          every learning block trusted (sourceability FULL) — still only a *candidate* for trust
"""
import argparse
import collections
import glob
import json
import os
import sys
from datetime import datetime, timezone

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import common  # noqa: E402

SCOREBOARD_VERSION = 'legacy-scoreboard-v1'
STATES = ('PENDING', 'REJECTED', 'WITHHELD', 'PARTIAL', 'FULL')

# The five annotated fields → the Founder's failure classes.
FIELD_CLASS = (
    ('display', 'display_fidelity'),
    ('teaching_critical', 'teaching_critical_fidelity'),
    ('reading_order', 'reading_order'),
    ('role', 'role_fidelity'),
    ('attachment', 'lesson_attachment'),
)
# The two remaining Founder classes are not separate verdict fields: the annotator tags them on the row that
# carries them. A row counts against the class when the annotator tagged it — the denominator stays the same
# judged-served base, so OLD and NEW are compared on one scale.
FORMULA_DISPLAY_TAGS = ('math_flattened', 'enumerator_dropped')
FORMULA_TEACHING_TAGS = ('fraction', 'formula', 'unit', 'number')
FIGURE_DISPLAY_TAGS = ('figure_text',)
FIGURE_KINDS = ('caption', 'figure')
DERIVED_CLASSES = ('formula_number_unit', 'figure_caption')


# ---------------------------------------------------------------- inputs
def read_jsonl(path):
    with open(path, encoding='utf-8') as f:
        return [json.loads(l) for l in f if l.strip()]


def latest(paths):
    """Newest version of a versioned artefact (…​.json, …​.v2.json): the last name in sorted order."""
    return sorted(paths)[-1] if paths else None


def load_registry(path):
    reg = common.load_json(path)
    if not reg:
        raise SystemExit(f'registry not found: {path} — run tool/corpus/legacy/registry.py first')
    return reg


def batch_dirs(legacy_out):
    """Batch directories oldest run first, so a lesson's state comes from the LATEST run that touched it —
    a re-run on an improved build supersedes the run it re-ran, whatever the directories are named.

    Round 5: `legacy_out` may be a comma-separated list of roots (poc-out/round4/legacy,poc-out/round5/legacy).
    The rounds live in separate trees — round 4's outputs are never moved or overwritten — but the scoreboard
    must count a lesson once across all of them, so the ordering is global rather than per root."""
    ds = []
    for root in legacy_roots(legacy_out):
        ds += [d for d in glob.glob(f'{root}/batch-*') if os.path.isdir(d) and os.path.exists(f'{d}/batch-spec.json')]
    return sorted(ds, key=lambda d: ((common.load_json(f'{d}/run-manifest.json', {}) or {}).get('started') or '', d))


def legacy_roots(legacy_out):
    return [r.strip().rstrip('/') for r in str(legacy_out).split(',') if r.strip()]


def batch_label(batch_dir, roots):
    """`round5/legacy/batch-2` rather than `batch-2` — but ONLY when more than one root is in scope.

    With two rounds counted together, two batches can share a name and the round is part of the identity;
    with one root the round is already in the document's title and the prefix is noise."""
    for root in roots:
        if batch_dir.startswith(root + os.sep):
            rel = os.path.relpath(batch_dir, root)
            if len(roots) == 1:
                return rel
            return os.path.join(os.path.basename(os.path.dirname(root)), os.path.basename(root), rel)
    return os.path.basename(batch_dir)


def restore_record(batch_dir):
    """RESTORE PRECISION for a batch, or an explicit statement that no restore stage ran.

    Founder §9: report restored / falsely-withheld / restore precision. When no repair or guard change
    produced a restore for this batch there is nothing to report, and the scoreboard must say that in
    words — a blank cell reads as zero, and zero restores and no-restore-stage are different facts."""
    rows = common.load_json(f'{batch_dir}/restore/restore-rows.json')
    prec = common.load_json(f'{batch_dir}/restore/restore-precision.json')
    if not rows:
        return dict(ran=False, why='no build change restored a reviewed withheld region here, and no REPAIRED '
                                   'stage exists yet')
    out = dict(ran=True, mechanism=rows.get('restoreMechanism'),
               reviewedWithheldRegions=rows.get('reviewedWithheldRegions'),
               restored=rows.get('restored'),
               falselyWithheldTotal=rows.get('falselyWithheldTotal'),
               falselyWithheldRecovered=rows.get('falselyWithheldRecovered'),
               falselyWithheldRecoveryRate=rows.get('falselyWithheldRecoveryRate'),
               wronglyRestoredCandidates=rows.get('wronglyRestoredCandidates'))
    if prec:
        out.update(restorePrecision=prec.get('restorePrecision'),
                   restorePrecisionValue=prec.get('restorePrecisionValue'),
                   precisionCounts=prec.get('counts'),
                   falselyWithheldRecoveredAndCorrect=prec.get('falselyWithheldRecoveredAndCorrect'))
    else:
        out.update(restorePrecision='— not yet judged (the restored regions have no fresh blind verdict)',
                   restorePrecisionValue=None)
    return out


def orphan_record(batch_dir):
    """Withheld regions that ORPHANED a sibling — a teaching-critical failure caused by the safety
    mechanism itself (Founder evaluation-set defect 8). A withheld block cannot be scored "safe" on
    its own; the scoreboard has to say what it left behind."""
    d = common.load_json(f'{batch_dir}/orphan/orphans.json')
    if not d:
        return None
    return {k: d.get(k) for k in ('findings', 'kinds', 'teachingCriticalFindings',
                                  'withheldRegionsThatOrphanASibling', 'withheldRegionsTotal',
                                  'orphaningShareOfWithheld', 'orphaningShareFormatted', 'doctrine')}


def over_withheld(batch_dir):
    """FALSE WITHHELD, from the annotator's own review of the withheld regions.

    Round 5 makes this a first-class metric, not a footnote: 19 of 30 on the evaluation set. The
    annotator's note begins with OVER / SAFE / UNSURE (round 5) or carries «OVER-withheld» inline
    (round 4); both conventions are read by the same parser Lane D uses for restore precision."""
    sys.path.insert(0, HERE)
    import restore as _restore
    p = latest(glob.glob(f'{batch_dir}/audit/annotated-new-*.jsonl'))
    if not p:
        return None
    rows = [r for r in read_jsonl(p) if not r.get('servedAsTrusted', True)]
    if not rows:
        return None
    c = collections.Counter(_restore._base_verdict(r.get('notes')) for r in rows)
    n = c['OVER'] + c['SAFE']
    return dict(file=os.path.basename(p), reviewed=len(rows), counts=dict(c),
                falseWithheld=c['OVER'], judged=n,
                rate=(round(c['OVER'] / n, 4) if n else None),
                formatted=common.fmt_rate(c['OVER'], n) if n else '— (n = 0)')


def caption_relation(batch_dir):
    """The figure-caption RELATION, which round 4 could measure only in words (batch-1 report §5a).
    A caption can be character-perfect and still teach nothing when it is served with no tie to its figure."""
    p = latest(glob.glob(f'{batch_dir}/audit/annotated-kind-caption-*.jsonl'))
    if not p:
        return None
    rows = read_jsonl(p)
    c = collections.Counter((r.get('figure_relation') or '').strip().upper() or 'UNSET' for r in rows)
    if not (c['OK'] + c['DETACHED'] + c['NA'] + c['UNSURE']):
        return None      # a caption sample annotated before the field existed (round 4) has nothing to say
    n = c['OK'] + c['DETACHED']
    return dict(file=os.path.basename(p), rows=len(rows), counts=dict(c),
                detached=c['DETACHED'], judged=n,
                detached_rate=(round(c['DETACHED'] / n, 4) if n else None))


def lesson_key(book, lesson):
    return f'{book}#{int(lesson)}'


def doc_filename(book, lesson):
    return f'lesson-{book}-b{int(lesson)}.json'


def batch_lessons(batch_dir):
    """One record per lesson of the batch: state, sourceability, trusted/withheld block counts, hashes."""
    spec = common.load_json(f'{batch_dir}/batch-spec.json', {})
    manifest = common.load_json(f'{batch_dir}/run-manifest.json', {})
    out = []
    for L in spec.get('lessons', []):
        book, n = L['book'], int(L['lesson'])
        doc = common.load_json(f'{batch_dir}/lesson-documents/{doc_filename(book, n)}')
        rec = dict(book=book, lesson=n, title=L.get('title'), risk=L.get('risk', []), batch=spec.get('batch'),
                   pipeline=manifest.get('pipeline') or spec.get('pipeline'), pages_pdf=L.get('pages_pdf', []))
        if not doc:
            rec.update(state='REJECTED', sourceability=None, reason='no TSL / LessonDocument produced — the pipeline refused this lesson (nothing guessed)')
            out.append(rec); continue
        p = doc.get('provenance') or {}
        st = p.get('tslStats') or {}
        trusted, withheld = int(st.get('trusted') or 0), int(st.get('withheld') or 0)
        state = 'WITHHELD' if trusted == 0 else ('FULL' if withheld == 0 else 'PARTIAL')
        rec.update(state=state, sourceability=p.get('sourceability'), learning_blocks=int(st.get('learning_blocks') or 0),
                   trusted_blocks=trusted, withheld_blocks=withheld, withheld_by_reason=st.get('withheld_by_reason') or {},
                   figures=st.get('figures'), audit_status=p.get('auditStatus'), licence=doc.get('licence'),
                   source_hash=p.get('sourceHash'), pipeline_version=p.get('pipelineVersion'),
                   pages_pdf_new=[p.get('pagePdfStart'), p.get('pagePdfEnd')])
        out.append(rec)
    return spec, manifest, out


def audit_rows(batch_dir):
    """Annotated audit rows of a batch, by side. Newest version of each file wins."""
    rows = {'OLD': [], 'NEW': []}
    for side, pat in (('OLD', 'annotated-old-*.jsonl'), ('NEW', 'annotated-new-*.jsonl')):
        p = latest(glob.glob(f'{batch_dir}/audit/{pat}'))
        if p:
            rows[side] = read_jsonl(p)
    return rows


# ---------------------------------------------------------------- rates
def judged(rows, field):
    """Served rows with an OK/WRONG verdict in `field` (UNSURE / NA are excluded and counted beside)."""
    served = [r for r in rows if r.get('servedAsTrusted', True)]
    ok = [r for r in served if (r.get(field) or '').strip().upper() == 'OK']
    wrong = [r for r in served if (r.get(field) or '').strip().upper() == 'WRONG']
    other = len(served) - len(ok) - len(wrong)
    return len(wrong), len(ok) + len(wrong), other


def tagged(row, display_tags, teaching_tags=(), kinds=()):
    d = (row.get('display_error_class') or '').split(',')
    t = (row.get('teaching_critical_class') or '').split(',')
    d = {x.strip() for x in d if x.strip()}
    t = {x.strip() for x in t if x.strip()}
    if d & set(display_tags) or t & set(teaching_tags):
        return True
    return bool(kinds) and (row.get('kind') or '') in kinds and any(
        (row.get(f) or '').strip().upper() == 'WRONG' for _, f in FIELD_CLASS)


def derived_rate(rows, cls):
    """Tag-derived class: numerator = rows the annotator tagged; denominator = judged served rows (display)."""
    served = [r for r in rows if r.get('servedAsTrusted', True)]
    base = [r for r in served if (r.get('display_fidelity') or '').strip().upper() in ('OK', 'WRONG')]
    if cls == 'formula_number_unit':
        k = sum(1 for r in base if tagged(r, FORMULA_DISPLAY_TAGS, FORMULA_TEACHING_TAGS))
        applicable = [r for r in base if (r.get('precheck') or {}).get('hasNumbers')]
        k_app = sum(1 for r in applicable if tagged(r, FORMULA_DISPLAY_TAGS, FORMULA_TEACHING_TAGS))
    else:
        k = sum(1 for r in base if tagged(r, FIGURE_DISPLAY_TAGS, (), FIGURE_KINDS))
        applicable = [r for r in base if (r.get('kind') or '') in FIGURE_KINDS or tagged(r, FIGURE_DISPLAY_TAGS)]
        k_app = sum(1 for r in applicable if tagged(r, FIGURE_DISPLAY_TAGS, (), FIGURE_KINDS))
    return dict(wrong=k, judged=len(base), applicable_wrong=k_app, applicable=len(applicable))


def class_rates(rows):
    """WRONG rate per failure class with a Wilson 95 % CI. Denominator is stated per class."""
    out = {}
    for cls, field in FIELD_CLASS:
        k, n, other = judged(rows, field)
        p, lo, hi = common.wilson(k, n)
        out[cls] = dict(basis='verdict field', field=field, wrong=k, judged=n, na_or_unsure=other, rate=p, lo=lo, hi=hi)
    for cls in DERIVED_CLASSES:
        d = derived_rate(rows, cls)
        p, lo, hi = common.wilson(d['wrong'], d['judged'])
        pa, loa, hia = common.wilson(d['applicable_wrong'], d['applicable'])
        out[cls] = dict(basis='annotator tag', wrong=d['wrong'], judged=d['judged'], rate=p, lo=lo, hi=hi,
                        applicable_wrong=d['applicable_wrong'], applicable=d['applicable'], applicable_rate=pa, applicable_lo=loa, applicable_hi=hia)
    served = [r for r in rows if r.get('servedAsTrusted', True)]
    out['_meta'] = dict(rows=len(rows), served=len(served), withheld_rows=len(rows) - len(served),
                        activities=len({r.get('activityId') for r in served}))
    return out


# ---------------------------------------------------------------- thresholds (Founder-only)
def load_thresholds(path):
    """A Founder threshold record makes `trusted` computable. Absent → trusted stays 0 and says why."""
    t = common.load_json(path)
    if not t:
        return None, f'no Founder threshold record at {os.path.relpath(path, common.REPO_ROOT) if path.startswith(common.REPO_ROOT) else path} — `trusted` and `eligible for teaching` stay 0 by definition'
    return t, None


def trusted_count(lessons, thresholds):
    if not thresholds:
        return 0, 0
    trusted = 0
    for L in lessons:
        if L['state'] != 'FULL' or not L.get('audited'):
            continue
        ft = (L.get('audit') or {}).get('false_trust_rate')
        cap = thresholds.get('max_false_trust_rate')
        if ft is not None and cap is not None and ft <= cap:
            trusted += 1
    return trusted, (trusted if thresholds.get('teachingAuthorised') else 0)


# ---------------------------------------------------------------- build
def build(registry_path, legacy_out, thresholds_path):
    reg = load_registry(registry_path)
    roots = legacy_roots(legacy_out)
    in_scope = {lesson_key(l['book'], l['lesson']): l for l in reg['lessons']}
    batches = []
    lessons_by_key = {}
    for bd in batch_dirs(legacy_out):
        spec, manifest, ls = batch_lessons(bd)
        rows = audit_rows(bd)
        audited_keys = {lesson_key(r['book'], r['lesson']) for r in rows['NEW']}
        for L in ls:
            k = lesson_key(L['book'], L['lesson'])
            L['audited'] = k in audited_keys
            L['in_scope'] = k in in_scope
            mine = [r for r in rows['NEW'] if lesson_key(r['book'], r['lesson']) == k]
            if mine:
                served = [r for r in mine if r.get('servedAsTrusted', True)]
                ftk, ftn, _ = judged(mine, 'false_trust')
                L['audit'] = dict(rows=len(mine), served=len(served), withheld_reviewed=len(mine) - len(served),
                                  false_trust_wrong=ftk, false_trust_judged=ftn, false_trust_rate=(round(ftk / ftn, 4) if ftn else None))
            lessons_by_key[k] = L
        batches.append(dict(batch=spec.get('batch'), dir=batch_label(bd, roots), pipeline=manifest.get('pipeline') or spec.get('pipeline'),
                            restore=restore_record(bd), caption_relation=caption_relation(bd),
                            orphan=orphan_record(bd), over_withheld=over_withheld(bd),
                            started=manifest.get('started'), pipeline_code_sha=manifest.get('pipeline_code_sha'), pages=manifest.get('pages'),
                            lessons=ls, old_vs_new=dict(OLD=class_rates(rows['OLD']), NEW=class_rates(rows['NEW'])),
                            audit_rows=dict(OLD=len(rows['OLD']), NEW=len(rows['NEW'])),
                            transferred_verdicts=sum(1 for r in rows['NEW'] if r.get('verdictTransferredFrom'))))
    thresholds, why = load_thresholds(thresholds_path)
    all_lessons = list(lessons_by_key.values())
    counts = collections.Counter(L['state'] for L in all_lessons)
    reprocessed = sum(1 for L in all_lessons if L['state'] in ('FULL', 'PARTIAL', 'WITHHELD'))
    audited = sum(1 for L in all_lessons if L.get('audited'))
    trusted, eligible = trusted_count(all_lessons, thresholds)
    n_scope = len(in_scope)
    scoreboard = dict(
        total_in_scope=n_scope,
        pending=n_scope - len([k for k in lessons_by_key if k in in_scope]),
        reprocessed=reprocessed,
        independently_audited=audited,
        trusted=trusted,
        partial=counts['PARTIAL'],
        withheld=counts['WITHHELD'],
        rejected=counts['REJECTED'],
        eligible_for_teaching=eligible,
        full_sourceability=counts['FULL'],
        out_of_scope_reprocessed=sum(1 for L in all_lessons if not L['in_scope']),
    )
    return dict(version=SCOREBOARD_VERSION, generated_by='tool/corpus/legacy/scoreboard.py',
                generated=datetime.now(timezone.utc).isoformat(timespec='seconds'),
                legacy_roots=roots,
                registry=dict(path=os.path.basename(registry_path), version=reg.get('version'), sha256=common.sha256_file(registry_path)),
                denominators=reg['denominators'], scope_definition=reg.get('scope_definition'),
                thresholds=dict(present=bool(thresholds), record=thresholds, note=why),
                scoreboard=scoreboard, states=dict(counts), batches=batches,
                registry_summary={k: reg['summary'][k] for k in ('in_113', 'in_sam_units', 'both', 'non_canonical', 'unranged', 'by_subject', 'risk', 'old_pack_activities', 'old_units')})


# ---------------------------------------------------------------- render
def fmt(x, key='rate'):
    if not x or not x.get('judged' if key == 'rate' else 'applicable'):
        return '— (n = 0)'
    if key == 'rate':
        return f"{x['wrong']} / {x['judged']} = {x['rate']:.3f} [{x['lo']:.3f}, {x['hi']:.3f}]"
    return f"{x['applicable_wrong']} / {x['applicable']} = {x['applicable_rate']:.3f} [{x['applicable_lo']:.3f}, {x['applicable_hi']:.3f}]"


def render_over_withheld(b):
    """FALSE WITHHELD and the orphaned siblings — the half of the ledger that a falling false-trust
    rate hides. Round 5 is judged on five directions at once, and two of them live here."""
    w, orph = b.get('over_withheld'), b.get('orphan')
    if not w and not orph:
        return []
    o = [f"\n### False withheld — batch `{b['dir']}`\n"]
    if w:
        o += ['| measure | value | of what |', '|---|---|---|',
              f"| withheld regions reviewed | {w['reviewed']} | every withheld region in the audit sample |",
              f"| **FALSE WITHHELD (over-withheld)** | **{w['formatted']}** | clean, legible text refused for a reason that did not apply to it |",
              f"| safe refusals | {w['counts'].get('SAFE', 0)} | genuinely damaged, ambiguous or figure-dependent |",
              f"| unclassifiable | {w['counts'].get('UNSURE', 0)} | excluded from the rate, counted here |", '']
    if orph:
        o += ['Withholding is not automatically safe. A withheld block that leaves a sibling stranded — one option '
              'of a multiple-choice, a caption cut from its figure, a hole in an enumerated run — makes what IS '
              'served wrong, not merely smaller, and is counted **teaching-critical** (`tool/corpus/legacy/orphan.py`).\n',
              '| measure | value |', '|---|---|',
              f"| structures mutilated by withholding | **{orph['teachingCriticalFindings']}** |",
              f"| kinds | {orph['kinds']} |",
              f"| **withheld regions that orphan a sibling** | **{orph['orphaningShareFormatted']}** |", '']
    return o


def render_restore(b):
    """RESTORED · FALSELY-WITHHELD RECOVERED · RESTORE PRECISION — or the reason there are none."""
    r = b.get('restore') or {}
    o = [f"\n### Restore — batch `{b['dir']}`\n"]
    if not r.get('ran'):
        o.append(f"**No restore stage ran** — {r.get('why', '')}. `restored`, `falsely-withheld recovered` "
                 'and `RESTORE PRECISION` are **empty, not zero** — see «What this scoreboard does not say».\n')
        return o
    o += [f"Restore mechanism: {r.get('mechanism')}\n",
          '| measure | value | of what |', '|---|---|---|',
          f"| reviewed withheld regions | {r.get('reviewedWithheldRegions')} | the withheld regions the earlier audit reviewed |",
          f"| **restored** | **{r.get('restored')}** | of those, served again by this build |",
          f"| falsely withheld (earlier audit) | {r.get('falselyWithheldTotal')} | reviewed regions judged OVER-withheld |",
          f"| **falsely-withheld recovered** | **{r.get('falselyWithheldRecovered')}** | {r.get('falselyWithheldRecoveryRate')} |",
          f"| restored that the earlier audit called a SAFE refusal | {r.get('wronglyRestoredCandidates')} | the dangerous direction — judged fresh, never inherited |",
          f"| **RESTORE PRECISION** | **{r.get('restorePrecision')}** | correctly restored / all restored, from a fresh blind judgement of what is served NOW |"]
    if r.get('precisionCounts'):
        o.append(f"| — fresh verdicts | {r['precisionCounts']} | UNSURE excluded from the precision and counted beside |")
    if r.get('falselyWithheldRecoveredAndCorrect') is not None:
        o.append(f"| falsely-withheld recovered AND correct | {r['falselyWithheldRecoveredAndCorrect']} | "
                 'the only cell that means coverage went up without a new wrong claim |')
    o.append('')
    return o


def render_caption_relation(b):
    c = b.get('caption_relation')
    if not c:
        return []
    return [f"\n### Figure-caption RELATION — batch `{b['dir']}` (quota sample, within-class only)\n",
            'Round 4 found captions that are character-perfect and still teach nothing, and had no field to record them '
            '(batch-1 report §5a). `figure_relation` is that field.\n',
            '| measure | value |', '|---|---|',
            f"| caption blocks judged | {c['rows']} |",
            f"| verdicts | {c['counts']} |",
            f"| **detached from their figure** | **{c['detached']} / {c['judged']}"
            + (f" = {c['detached_rate']:.3f}" if c['detached_rate'] is not None else '') + '** |',
            '\nThis is a rate **within the caption class**, from a quota sample. It is never pooled with the '
            'stratified rates above.\n']


def render_md(sb):
    s = sb['scoreboard']
    d = sb['denominators']
    o = ['# Legacy reprocess scoreboard — rounds 4 + 5 (Lane D)\n',
         f"`{sb['version']}` · generated {sb['generated']} · source registry `{sb['registry']['version']}` ({sb['registry']['sha256'][:12]}) · **measurement only — no threshold, no PASS/FAIL**\n",
         'Legacy content is never a trusted teaching source. REPROCESSED ≠ TRUSTED: a reprocessed lesson is a *candidate* until it clears an independent audit against a threshold **the Founder sets**.\n',
         '## Denominators (D5 — never summed, never mixed)\n',
         '| denominator | N | definition |', '|---|---|---|']
    for k, v in d.items():
        o.append(f"| {k} | {v['value']:,} | {v['definition']} |")
    o += ['\n## Scoreboard\n', '| measure | count | of what |', '|---|---|---|',
          f"| total legacy lessons in scope | **{s['total_in_scope']}** | 113 baseline ∪ sam-units lessons; = {s['total_in_scope'] / d['canonical']['value']:.1%} of the {d['canonical']['value']:,} canonical historical lessons |",
          f"| pending | **{s['pending']}** | in scope, in no batch yet |",
          f"| reprocessed (from original source) | **{s['reprocessed']}** | of {s['total_in_scope']} in scope = {s['reprocessed'] / s['total_in_scope']:.1%} |",
          f"| independently audited | **{s['independently_audited']}** | of {s['reprocessed']} reprocessed |",
          f"| trusted | **{s['trusted']}** | {sb['thresholds']['note'] or 'against the Founder threshold record'} |",
          f"| partial (some blocks served, some withheld) | **{s['partial']}** | of {s['reprocessed']} reprocessed |",
          f"| withheld (nothing servable) | **{s['withheld']}** | of {s['reprocessed']} reprocessed |",
          f"| rejected (pipeline produced no lesson) | **{s['rejected']}** | of the lessons attempted |",
          f"| **eligible for teaching** | **{s['eligible_for_teaching']}** | requires `trusted` ∧ a Founder teaching authorisation |",
          f"\nFull-sourceability lessons (every learning block trusted): {s['full_sourceability']}. Reprocessed lessons outside the registry scope: {s['out_of_scope_reprocessed']}.\n"]
    for b in sb['batches']:
        o += [f"## Batch `{b['dir']}` (spec `{b['batch']}`) — pipeline `{b['pipeline']}` ({b['pages']} pages, code {(b['pipeline_code_sha'] or 'n/a')[:60]})\n",
              '| lesson | risk | state | learning blocks | trusted | withheld | withheld reasons | audited rows |', '|---|---|---|---|---|---|---|---|']
        for L in b['lessons']:
            a = L.get('audit') or {}
            o.append(f"| {common.book_label(L['book'])} Bài {L['lesson']} | {', '.join(L['risk'])} | **{L['state']}** | {L.get('learning_blocks', '—')} | {L.get('trusted_blocks', '—')} | "
                     f"{L.get('withheld_blocks', '—')} | {L.get('withheld_by_reason') or '—'} | {a.get('served', 0)} served + {a.get('withheld_reviewed', 0)} withheld |")
        old_n = b['old_vs_new']['OLD']['_meta']['served']
        basis = (f"OLD = {old_n} served blocks of the old units + packs" if old_n else
                 "OLD = not re-sampled for this batch — the product side is unchanged, see the batch it re-runs")
        note = ''
        if b.get('transferred_verdicts'):
            note = (f"\n**{b['transferred_verdicts']} of the NEW verdicts were carried over** from the batch this one re-runs, and only where this build serves the "
                    'identical text in the same region (tool/corpus/legacy/rerun.py). That makes this a *conditional* rate over the rows that survived, '
                    'not a fresh stratified sample of this build — read it beside the re-run delta, not as a replacement for it.\n')
        o += [f"\n### OLD vs NEW false trust per failure class — batch `{b['dir']}`\n",
              'rate = WRONG / (OK + WRONG) among **served** rows (what the side actually showed a child), Wilson 95 % · NA / UNSURE excluded and counted beside · no threshold applied.\n',
              f"{basis} · NEW = {b['old_vs_new']['NEW']['_meta']['served']} served blocks of the new Trusted Structured Lessons "
              f"(+ {b['old_vs_new']['NEW']['_meta']['withheld_rows']} withheld regions reviewed separately). The two sides are different block sets — the comparable quantity is *the share of what each side served that is wrong*.\n" + note,
              '| failure class | basis | OLD | NEW |', '|---|---|---|---|']
        for cls, _ in FIELD_CLASS:
            o.append(f"| {cls} | verdict field | {fmt(b['old_vs_new']['OLD'][cls])} | {fmt(b['old_vs_new']['NEW'][cls])} |")
        for cls in DERIVED_CLASSES:
            o.append(f"| {cls} | annotator tag / all judged | {fmt(b['old_vs_new']['OLD'][cls])} | {fmt(b['old_vs_new']['NEW'][cls])} |")
            o.append(f"| {cls} (rows where the class applies) | annotator tag / applicable | {fmt(b['old_vs_new']['OLD'][cls], 'applicable')} | {fmt(b['old_vs_new']['NEW'][cls], 'applicable')} |")
        o += render_over_withheld(b)
        o += render_restore(b)
        o += render_caption_relation(b)
        o.append('')
    o += ['## What this scoreboard does not say\n',
          '- It does not say any legacy lesson may be taught. `eligible for teaching` is 0 and stays 0 until the Founder sets a threshold record and authorises teaching.',
          '- It does not compare against the 3,679 / 3,381 denominators as a coverage claim: 243 lessons are in Lane D scope; the rest have never been reprocessed.',
          '- Withheld is not failure. A withheld block is the pipeline refusing to guess — the safe outcome for legacy data.',
          '- Rates are per served block on a small audited sample; the CIs are wide and are shown so they cannot be read as precision.',
          '- An **empty** restore section is not a zero. It means no build change restored a reviewed withheld region and no REPAIRED stage exists yet; a batch with restores states its RESTORE PRECISION, and a restore by a loosened guard is never summed with a restore by a validated repair.',
          '- `restored` counts regions the earlier audit had already reviewed as withheld. It is not the total number of regions this build serves that the previous one did not.\n']
    return '\n'.join(o) + '\n'


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--registry', default=f'{common.LEGACY_OUT}/registry.json')
    ap.add_argument('--legacy-out', default=common.LEGACY_OUT,
                    help='one or more comma-separated legacy output roots, e.g. '
                         'poc-out/round4/legacy,poc-out/round5/legacy — a lesson is counted once across all of them')
    ap.add_argument('--thresholds', default=f'{common.REPO_ROOT}/docs/research/legacy-reprocess/THRESHOLDS.json')
    ap.add_argument('--out-md', default=f'{common.REPO_ROOT}/docs/research/legacy-reprocess/LEGACY-REPROCESS-SCOREBOARD.md')
    ap.add_argument('--out-json', default=f'{common.REPO_ROOT}/docs/research/legacy-reprocess/LEGACY-REPROCESS-SCOREBOARD.json')
    ap.add_argument('--print', action='store_true')
    a = ap.parse_args(argv)
    sb = build(a.registry, a.legacy_out, a.thresholds)
    md = render_md(sb)
    if a.print:
        print(md)
        return 0
    common.dump_json(sb, a.out_json)
    os.makedirs(os.path.dirname(a.out_md), exist_ok=True)
    with open(a.out_md, 'w', encoding='utf-8') as f:
        f.write(md)
    print(json.dumps(sb['scoreboard'], ensure_ascii=False, indent=1))
    print(f'→ {a.out_md}\n→ {a.out_json}')
    return 0


if __name__ == '__main__':
    sys.exit(main())
