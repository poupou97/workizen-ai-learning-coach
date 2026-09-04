#!/usr/bin/env python3
"""TC-v2 — SLICE REPORT: per-book trusted-block rate, withheld share by reason code, roles, Trusted
Structured Lessons (FULL / PARTIAL / NONE), attachment repairs, denominators, and the WAL-206 funnel
re-run on both sources (old units-layout vs tc-v2 TSL) as a MEASUREMENT — explicitly not the success
criterion.

Denominators are never collapsed: 3,679 = canonical K-12 SGK lessons (curriculum-structure lessonCount
sum) · 3,381 = SGK lessons with a usable page range in the same file. Per book both are reported, plus
the repaired ranged count and the header-detected count (the candidate new canonical count for the
PARTIAL books).

Funnel steps (same names as tool/corpus/wal206_funnel.py; old numbers read from
poc-out/p0-experiment/funnel-exact.json / funnel-variant.json written by WAL-206):
  TOC lessons → lessons with ≥ 1 trusted PASSAGE/QUESTION (old: units-layout) / ≥ 1 trusted body or question
  block (new: TSL) → attached → with a recognised activity pattern (fable_activity_taxonomy.classify on
  QUESTION-role trusted blocks) → pattern in the WAL-204 scope (READ_TEXT/SELECT_MCQ/WRITE_TEXT) → passes the
  WAL-206 content gate at source (pattern_router.reading_ok on the question + nearest preceding trusted
  body block). No pack is built and no Dart consumer is touched.

Usage: <venv python> tool/corpus/tc2_slice_report.py --pipeline tc2-p1 [--json out] [--md out]
"""
import argparse
import glob
import json
import os
import re
import sys
from collections import Counter, defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, '..', 'ui'))
import tc2_run  # noqa: E402
import tc2_attach  # noqa: E402
import tc2_tsl  # noqa: E402
from fable_activity_taxonomy import classify  # noqa: E402
import pattern_router  # noqa: E402

ROOT = tc2_run.ROOT
SCOPE = {'READ_TEXT', 'SELECT_MCQ', 'WRITE_TEXT'}
EXPLAIN = {'EXPLAIN_SHORT', 'COMPARE', 'CLASSIFY_SORT'}


def book_stats(book, pipeline):
    files = sorted(glob.glob(f'{tc2_run.outdir(pipeline)}/sdm/{book}/p*.sdm.json'))
    st = Counter(); reasons = Counter(); roles = Counter(); roles_trusted = Counter(); pages = 0; feats = Counter(); enum_restored = 0; secs = []
    for f in files:
        s = json.load(open(f)); pages += 1; secs.append(s['source'].get('docling_seconds') or 0)
        for k, v in s['features'].items():
            if v:
                feats[k] += 1
        for ob in s['blocks']:
            r = ob['role']['value']; roles[r] += 1
            if not ob['learning']:
                continue
            st['learning'] += 1; st[ob['trust']['status']] += 1
            if ob['trust']['status'] == 'TRUSTED':
                roles_trusted[r] += 1
            for x in ob['trust']['reasons']:
                reasons[x] += 1
            enum_restored += bool(ob.get('enumerator_restored'))
    return dict(pages=pages, learning_blocks=st['learning'], trusted=st['TRUSTED'], withheld=st['WITHHELD'], conflict=st['CONFLICT'],
                trusted_rate=round(st['TRUSTED'] / max(1, st['learning']), 3), withheld_by_reason=dict(reasons.most_common()), roles=dict(roles.most_common()), roles_trusted=dict(roles_trusted.most_common()),
                page_features=dict(feats), enumerators_restored=enum_restored, docling_sec_total=round(sum(secs), 1))


def funnel_new(book, docs):
    """WAL-206 funnel steps computed on the TSL documents of one book (no pack build)."""
    toc_lessons = {d['lesson'] for d in docs}
    recovered = set(); attached = set(); patterned_any = set(); patterned_scope = set(); explain = set(); gate_pass = set(); gate_pass_explain = set(); gate_reasons = Counter()
    for d in docs:
        n = d['lesson']
        blocks = d['blocks']
        bodies = [b for b in blocks if b['role']['value'] == 'body' and len(b['text']) >= 120]
        qs = [b for b in blocks if b['role']['value'] == 'question']
        if bodies or qs:
            recovered.add(n); attached.add(n)
        labs_all = set()
        for q in qs:
            t = pattern_router.clean(q['text'])
            if not t:
                continue
            labs = classify(t)
            labs_all |= labs
            if not labs:
                continue
            ctx = next((b for b in reversed(bodies) if (b['page'], b['order']) < (q['page'], q['order'])), None)
            if labs & SCOPE:
                bad = pattern_router.reading_ok(t, ctx['text']) if ctx else 'no_context'
                if not bad and len(t) >= pattern_router.MIN_PROMPT:
                    gate_pass.add(n)
                else:
                    gate_reasons[bad] += 1
            if labs & EXPLAIN and not (labs & SCOPE):
                bad = pattern_router.reading_ok(t, ctx['text']) if ctx else 'no_context'
                if not bad and len(t) >= pattern_router.MIN_PROMPT:
                    gate_pass_explain.add(n)
                else:
                    gate_reasons['explain:' + str(bad)] += 1
        if labs_all:
            patterned_any.add(n)
        if labs_all & SCOPE:
            patterned_scope.add(n)
        if labs_all & EXPLAIN:
            explain.add(n)
    return dict(toc_lessons=len(toc_lessons), recovered=len(recovered), attached=len(attached), patterned_any=len(patterned_any), patterned_scope=len(patterned_scope), explain_only=len(explain - patterned_scope),
                gate_pass_exact=len(gate_pass), gate_pass_variant=len(gate_pass | gate_pass_explain), gate_reasons=dict(gate_reasons.most_common(12)))


def main():
    ap = argparse.ArgumentParser(); ap.add_argument('--pipeline', default='tc2-p1'); ap.add_argument('--json', default=None); ap.add_argument('--md', default=None); ap.add_argument('--no-build', action='store_true')
    a = ap.parse_args()
    docs_meta = {d['sourceDocumentId']: d for d in json.load(open(f'{ROOT}/poc-out/graph/curriculum-structure.json'))['documents']}
    sgk_all = [d for d in docs_meta.values() if d.get('docType') == 'SGK']
    den = dict(canonical_3679=sum(len(d.get('lessons', [])) for d in sgk_all), ranged_3381=sum(1 for d in sgk_all for l in d.get('lessons', []) if l.get('pageStart')))
    books = {}
    fun_new_total = Counter(); tsl_total = Counter()
    for b in tc2_run.SLICE_BOOKS:
        att = tc2_attach.attach_book(b, a.pipeline)
        docs, summ = tc2_tsl.build_book(b, a.pipeline, write=not a.no_build)
        fn = funnel_new(b, docs)
        bs = book_stats(b, a.pipeline)
        c = att['counts']
        books[b] = dict(stats=bs, attach=c, tsl=summ, funnel_new=fn, repaired_lessons=[dict(number=l['number'], page_printed=l['page_printed'], source=l['source'], title=(l.get('title') or '')[:60]) for l in att['lessons'] if l['source'] == 'header'])
        fun_new_total.update({k: v for k, v in fn.items() if isinstance(v, int)})
        tsl_total.update({k: v for k, v in summ.items() if isinstance(v, int)})
    old = {}
    for k in ('exact', 'variant'):
        p = f'{ROOT}/poc-out/p0-experiment/funnel-{k}.json'
        old[k] = json.load(open(p)) if os.path.exists(p) else None
    out = dict(pipeline=a.pipeline, denominators=den, books=books, totals=dict(funnel_new=dict(fun_new_total), tsl=dict(tsl_total)), funnel_old=old)
    if a.json:
        json.dump(out, open(a.json, 'w'), ensure_ascii=False, indent=1)
    L = [f'# TC-v2 Science Slice — {a.pipeline} (MEASURED)', '', f"Denominators (never collapsed): **{den['canonical_3679']} canonical SGK lessons** (curriculum-structure) · **{den['ranged_3381']} ranged SGK lessons** (pageStart present).", '',
         '## Per book — blocks', '', '| book | pages | learning blocks | trusted | withheld | conflict | trusted rate | enumerators restored | top withheld reasons |', '|---|---|---|---|---|---|---|---|---|']
    for b, v in books.items():
        s = v['stats']
        L.append(f"| {b} | {s['pages']} | {s['learning_blocks']} | {s['trusted']} | {s['withheld']} | {s['conflict']} | {s['trusted_rate']:.3f} | {s['enumerators_restored']} | {dict(list(s['withheld_by_reason'].items())[:5])} |")
    L += ['', '## Per book — lessons and denominators', '', '| book | TOC status | canonical (lessonCount) | TOC ranged (old) | header-detected | header-only (TOC repair) | repaired ranged (new) | beyond canonical | rejected headers | pages no lesson | TSL FULL / PARTIAL / NONE |', '|---|---|---|---|---|---|---|---|---|---|---|']
    for b, v in books.items():
        c = v['attach']; t = v['tsl']
        L.append(f"| {b} | {c['structure_status']} | {c['canonical_lesson_count']} | {c['toc_ranged']} | {c['header_detected']} | {c['header_only']} | {c['repaired_ranged']} | {c['beyond_canonical']} (max Bài {c['max_lesson_number']}) | {c['rejected_headers']} | {c['pages_no_lesson']} ({c['page_kinds']}) | {t['FULL']} / {t['PARTIAL']} / {t['NONE']} |")
    L += ['', '## Trusted Structured Lessons — Hybrid Smart Book projection (both modes, same block sequence)', '', '| book | lessons | native blocks | withheld regions (= source_crop in with_images = withheld_ref in no_images) | withheld by reason |', '|---|---|---|---|---|']
    for b, v in books.items():
        t = v['tsl']
        L.append(f"| {b} | {t['lessons']} | {t['hsb_native']} | {t['hsb_crop_or_ref']} | {dict(list(sorted(t['withheld_by_reason'].items(), key=lambda kv: -kv[1]))[:6])} |")
    L += ['', '## WAL-206 funnel, old source vs new source (MEASUREMENT, not the success criterion)', '',
          '| step | OLD units-layout (WAL-206 exact) | OLD (WAL-206 variant + EXPLAIN) | NEW tc-v2 TSL |', '|---|---|---|---|']
    oe, ov, fn = old.get('exact') or {}, old.get('variant') or {}, fun_new_total
    L.append(f"| TOC lessons (6 books) | {oe.get('toc')} | {ov.get('toc')} | {fn['toc_lessons']} (repaired: header ∪ TOC) |")
    L.append(f"| recovered (≥ 1 trusted passage/question) | {oe.get('recovered')} | {ov.get('recovered')} | {fn['recovered']} |")
    L.append(f"| attached | {oe.get('attached')} | {ov.get('attached')} | {fn['attached']} |")
    L.append(f"| with any recognised pattern | {oe.get('patternedAny')} | {ov.get('patternedAny')} | {fn['patterned_any']} |")
    L.append(f"| with a pattern in the exact scope | {oe.get('patternedScope')} | {ov.get('patternedScope')} | {fn['patterned_scope']} |")
    L.append(f"| EXPLAIN/OBSERVE only | — | — | {fn['explain_only']} |")
    L.append(f"| routed / gate-at-source pass (exact) | {oe.get('routed')} (content-valid {oe.get('contentValid')}) | — | {fn['gate_pass_exact']} |")
    L.append(f"| routed / gate-at-source pass (variant +EXPLAIN) | — | {ov.get('routed')} (content-valid {ov.get('contentValid')}, device-valid {ov.get('deviceValid')}) | {fn['gate_pass_variant']} |")
    L += ['', 'NEW = lessons whose Trusted Structured Lesson carries a TRUSTED question block passing the same WAL-206 content gate against the nearest preceding trusted body block; no pack was built, nothing was walked on a device, and the QUESTION role precision measured on gold applies to every such count.', '']
    L += ['## TOC repairs (header-only lessons per book)', '']
    for b, v in books.items():
        if v['repaired_lessons']:
            L.append(f"- **{b}**: " + '; '.join(f"Bài {r['number']} (p.{r['page_printed']}) {r['title']}" for r in v['repaired_lessons']))
    md = '\n'.join(L) + '\n'
    if a.md:
        open(a.md, 'w').write(md)
    print(md[:6000])


if __name__ == '__main__':
    main()
