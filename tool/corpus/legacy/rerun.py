#!/usr/bin/env python3
"""Round 4 · Lane D — RE-RUN DELTA: did an improved pipeline actually rescue the legacy data?

    python3 tool/corpus/legacy/rerun.py --base-dir poc-out/round4/legacy/batch-1 \
        --rerun-dir poc-out/round4/legacy/batch-1-rerun-tc2-p2 --out <dir>

The same batch spec, the same original source, two pipeline builds. Two measurements:

  1. COVERAGE — per lesson, learning blocks · trusted · withheld · withheld reasons on both sides.
     More withholding is not automatically better and not automatically worse: it is the price paid,
     and it is stated beside what it bought.

  2. RESCUE, row by row — every audited row of the base run is looked up in the re-run by page +
     bbox overlap (the same geometric matching the OLD-vs-NEW compare uses) and classified:

        still_trusted_identical   the same text is still served as trusted   (a defect SURVIVES / good content KEPT)
        still_trusted_changed     served as trusted, different text          (re-read — needs a fresh judgement)
        now_withheld              the re-run refuses to serve that region    (a defect CAUGHT / good content LOST)
        now_unattached            the page is no longer part of this lesson  (attachment change)
        now_absent                nothing in the re-run covers the region

     Read against annotator verdicts this gives, per failure class, the rescue rate
     (WRONG rows no longer served as they were) and the collateral rate (OK rows no longer served).
     A row that merely changed is NOT counted as rescued — an unjudged new text is not a fixed one.

Lane D never edits pipeline code; run_batch.py --corpus chooses which build to call and the manifest
records both shas. Nothing is overwritten: the re-run is its own batch directory.
"""
import argparse
import collections
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import common  # noqa: E402
import compare  # noqa: E402

RERUN_VERSION = 'legacy-rerun-delta-v1'
OUTCOMES = ('still_trusted_identical', 'still_trusted_changed', 'now_withheld', 'now_unattached', 'now_absent')
# A row's defect can no longer reach a child in the same form when the region is withheld, unattached or gone.
NOT_SERVED_AS_BEFORE = ('now_withheld', 'now_unattached', 'now_absent')
CLASS_FIELD = (('display', 'display_fidelity'), ('teaching_critical', 'teaching_critical_fidelity'),
               ('reading_order', 'reading_order'), ('role', 'role_fidelity'), ('attachment', 'lesson_attachment'),
               ('false_trust', 'false_trust'))


def read_jsonl(p):
    with open(p, encoding='utf-8') as f:
        return [json.loads(l) for l in f if l.strip()]


def pipeline_of(batch_dir):
    m = common.load_json(f'{batch_dir}/run-manifest.json', {})
    return m.get('pipeline') or (common.load_json(f'{batch_dir}/batch-spec.json', {}) or {}).get('pipeline')


def lesson_docs(batch_dir):
    d = f'{batch_dir}/lesson-documents'
    out = {}
    if not os.path.isdir(d):
        return out
    for f in sorted(os.listdir(d)):
        if f.endswith('.json'):
            j = common.load_json(f'{d}/{f}')
            if j:
                out[(j['book'], int(j['lesson']))] = j
    return out


def tsl_of(batch_dir, pipeline, book, lesson):
    return common.load_json(f'{batch_dir}/tcroot/poc-out/trusted-corpus/tc-v2/{pipeline}/lessons/{book}/bai-{int(lesson):02d}.tsl.json')


def coverage(batch_dir):
    """Per lesson: what the run offers and what it refuses."""
    out = {}
    for (book, n), doc in lesson_docs(batch_dir).items():
        p = doc.get('provenance') or {}
        st = p.get('tslStats') or {}
        t, w = int(st.get('trusted') or 0), int(st.get('withheld') or 0)
        out[f'{book}#{n}'] = dict(book=book, lesson=n, sourceability=p.get('sourceability'), pages=[p.get('pagePdfStart'), p.get('pagePdfEnd')],
                                  learning_blocks=int(st.get('learning_blocks') or 0), trusted=t, withheld=w,
                                  served_share=(round(t / (t + w), 4) if (t + w) else None), withheld_by_reason=st.get('withheld_by_reason') or {},
                                  source_hash=p.get('sourceHash'), pipeline_version=p.get('pipelineVersion'))
    return out


def locate(row, tsl):
    """Where the audited row's region ends up in the re-run's TSL."""
    if tsl is None:
        return 'now_unattached', None, None
    page, bb = row.get('pagePdf'), (row.get('source') or {}).get('bbox') or row.get('bbox')
    if page not in (tsl.get('boundary') or {}).get('pages', []):
        return 'now_unattached', None, None
    if not bb:
        return 'now_absent', None, None
    best, best_cov = None, 0.0
    for b in tsl['blocks']:
        if b['page'] != page:
            continue
        c = max(compare.overlap_frac(bb, b['bbox']), compare.overlap_frac(b['bbox'], bb))
        if c > best_cov:
            best, best_cov = b, c
    hw, hw_cov = None, 0.0
    for w in tsl['withheld']:
        if w['page'] != page:
            continue
        c = max(compare.overlap_frac(bb, w['bbox']), compare.overlap_frac(w['bbox'], bb))
        if c > hw_cov:
            hw, hw_cov = w, c
    if best is not None and best_cov >= 0.5 and best_cov >= hw_cov:
        same = common.norm(row.get('text')) == common.norm(best['text'])
        return ('still_trusted_identical' if same else 'still_trusted_changed'), best, round(best_cov, 3)
    if hw is not None and hw_cov >= 0.5:
        return 'now_withheld', hw, round(hw_cov, 3)
    return 'now_absent', None, (round(best_cov, 3) if best is not None else None)


def rescue(annotated, rerun_dir, rerun_pipeline):
    """Row-level outcome of every audited row of the base run inside the re-run."""
    tsls = {}
    rows = []
    for r in annotated:
        if not r.get('servedAsTrusted', True):
            continue                                        # withheld regions are reviewed on their own terms
        key = (r['book'], int(r['lesson']))
        if key not in tsls:
            tsls[key] = tsl_of(rerun_dir, rerun_pipeline, *key)
        outcome, blk, cov = locate(r, tsls[key])
        rows.append(dict(sampleId=r['sampleId'], book=r['book'], lesson=r['lesson'], pagePdf=r.get('pagePdf'), kind=r.get('kind'),
                         outcome=outcome, coverage=cov, new_block=(blk or {}).get('id'),
                         new_withheld_reasons=((blk or {}).get('reasons') if outcome == 'now_withheld' else None),
                         new_role=((blk or {}).get('role') or {}).get('value') if outcome.startswith('still_trusted') else None,
                         verdicts={cls: (r.get(field) or '').strip().upper() for cls, field in CLASS_FIELD},
                         notes=r.get('notes', '')))
    return rows


def summarise(rows):
    """Per failure class: of the rows judged WRONG / OK on the base run, what the re-run now does with them."""
    per_class = {}
    for cls, _ in CLASS_FIELD:
        block = {}
        for verdict in ('WRONG', 'OK'):
            sel = [r for r in rows if r['verdicts'][cls] == verdict]
            c = collections.Counter(r['outcome'] for r in sel)
            changed = sum(c[o] for o in NOT_SERVED_AS_BEFORE)
            k, n = changed, len(sel)
            p, lo, hi = common.wilson(k, n)
            block[verdict] = dict(n=n, outcomes=dict(c), no_longer_served_as_before=k, rate=p, lo=lo, hi=hi)
        per_class[cls] = block
    per_class['_all'] = dict(rows=len(rows), outcomes=dict(collections.Counter(r['outcome'] for r in rows)))
    return per_class


def transfer_annotations(annotated, rows, rerun_pipeline, base_pipeline):
    """Carry a verdict to the re-run ONLY where the re-run serves the identical text in the same region.

    That is the whole licence: same region, same characters, so the judgement made from the page render still
    describes what a child would see. Rows the re-run withholds, unattaches or drops carry NO verdict forward —
    they are not claims any more. Rows served with CHANGED text carry no verdict either: they are new claims and
    must be annotated. Every transferred row records where its verdict came from."""
    by_id = {r['sampleId']: r for r in annotated}
    out = []
    for d in rows:
        if d['outcome'] != 'still_trusted_identical':
            continue
        src = dict(by_id[d['sampleId']])
        src['packVersion'] = rerun_pipeline
        src['tslBlockId'] = d['new_block']
        src['source'] = dict(src.get('source') or {}, tslBlockId=d['new_block'])
        src['verdictTransferredFrom'] = dict(sampleId=d['sampleId'], pipeline=base_pipeline, rule='identical served text in the same region', coverage=d['coverage'])
        out.append(src)
    return out


def build(base_dir, rerun_dir, annotated_path):
    base_pipe, rerun_pipe = pipeline_of(base_dir), pipeline_of(rerun_dir)
    base_cov, rerun_cov = coverage(base_dir), coverage(rerun_dir)
    annotated = read_jsonl(annotated_path) if annotated_path and os.path.exists(annotated_path) else []
    rows = rescue(annotated, rerun_dir, rerun_pipe)
    bm = common.load_json(f'{base_dir}/run-manifest.json', {})
    rm = common.load_json(f'{rerun_dir}/run-manifest.json', {})
    return dict(version=RERUN_VERSION, base=dict(dir=os.path.basename(base_dir), pipeline=base_pipe, code_sha=bm.get('pipeline_code_sha'), corpus=bm.get('pipeline_corpus')),
                rerun=dict(dir=os.path.basename(rerun_dir), pipeline=rerun_pipe, code_sha=rm.get('pipeline_code_sha'), corpus=rm.get('pipeline_corpus')),
                annotated=dict(path=os.path.basename(annotated_path) if annotated_path else None, rows=len(annotated), served_rows=len(rows)),
                coverage=dict(base=base_cov, rerun=rerun_cov), rescue_rows=rows, rescue=summarise(rows))


def render_md(d):
    b, r = d['base'], d['rerun']
    o = [f"# Re-run delta — `{b['pipeline']}` → `{r['pipeline']}` ({d['version']})\n",
         f"Same batch spec, same original source, two pipeline builds. base `{b['dir']}` (code {(b['code_sha'] or 'n/a')[:12]}) → re-run `{r['dir']}` (code {(r['code_sha'] or 'n/a')[:12]}). "
         'Measurement only — no threshold, no PASS/FAIL. REPROCESSED ≠ TRUSTED on either side.\n',
         '## 1. Coverage — what each build serves and what it refuses\n',
         '| lesson | pages | learning blocks | trusted (base → re-run) | withheld (base → re-run) | served share | new withhold reasons |', '|---|---|---|---|---|---|---|']
    tb = tr = wb = wr = 0
    for k in sorted(set(d['coverage']['base']) | set(d['coverage']['rerun'])):
        a = d['coverage']['base'].get(k, {}); c = d['coverage']['rerun'].get(k, {})
        tb += a.get('trusted', 0); tr += c.get('trusted', 0); wb += a.get('withheld', 0); wr += c.get('withheld', 0)
        new_reasons = sorted(set(c.get('withheld_by_reason', {})) - set(a.get('withheld_by_reason', {})))
        o.append(f"| {common.book_label(a.get('book') or c.get('book'))} Bài {a.get('lesson') or c.get('lesson')} | {a.get('pages')} → {c.get('pages')} | {a.get('learning_blocks')} → {c.get('learning_blocks')} | "
                 f"{a.get('trusted')} → {c.get('trusted')} | {a.get('withheld')} → {c.get('withheld')} | "
                 f"{(a.get('served_share') or 0):.0%} → {(c.get('served_share') or 0):.0%} | {', '.join(new_reasons) or '—'} |")
    o.append(f"| **total** | | | **{tb} → {tr}** | **{wb} → {wr}** | **{tb / max(1, tb + wb):.0%} → {tr / max(1, tr + wr):.0%}** | |\n")
    o += [f"## 2. Rescue — the {d['annotated']['served_rows']} audited served rows of the base run, looked up in the re-run\n",
          'A row is counted as *no longer served as before* only when the re-run withholds it, drops the page from the lesson, or does not extract it. '
          'A row whose text merely CHANGED is not counted — an unjudged new text is not a fixed one.\n',
          '| failure class | base verdict WRONG: n | of those, no longer served as before | base verdict OK: n | of those, no longer served (collateral) |', '|---|---|---|---|---|']
    for cls, _ in CLASS_FIELD:
        w = d['rescue'][cls]['WRONG']; k = d['rescue'][cls]['OK']
        wf = f"{w['no_longer_served_as_before']} / {w['n']} = {w['rate']:.3f} [{w['lo']:.3f}, {w['hi']:.3f}]" if w['n'] else '— (n = 0)'
        kf = f"{k['no_longer_served_as_before']} / {k['n']} = {k['rate']:.3f} [{k['lo']:.3f}, {k['hi']:.3f}]" if k['n'] else '— (n = 0)'
        o.append(f"| {cls} | {w['n']} | {wf} | {k['n']} | {kf} |")
    o += ['', f"Row outcomes overall: {d['rescue']['_all']['outcomes']}\n",
          '## 3. What still needs a fresh judgement\n',
          'Rows served with CHANGED text are new claims: they carry no verdict yet and must be annotated before the re-run can be scored on the same footing as the base run.\n']
    changed = [r for r in d['rescue_rows'] if r['outcome'] == 'still_trusted_changed']
    survived = [r for r in d['rescue_rows'] if r['outcome'] == 'still_trusted_identical' and r['verdicts'].get('false_trust') == 'WRONG']
    o.append(f'- {len(changed)} rows changed text and are unjudged.')
    o.append(f'- {len(survived)} rows judged false-trust WRONG on the base run are served IDENTICALLY by the re-run — those defects survive:')
    for r in survived[:20]:
        o.append(f"  - `{r['sampleId']}` {common.book_label(r['book'])} Bài {r['lesson']} p{r['pagePdf']} {r['kind']} — {r['notes'][:150]}")
    return '\n'.join(o) + '\n'


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--base-dir', default=f'{common.LEGACY_OUT}/batch-1')
    ap.add_argument('--rerun-dir', required=True)
    ap.add_argument('--annotated', default=None, help='annotated NEW rows of the base run (default: the newest in <base-dir>/audit)')
    ap.add_argument('--out', default=None, help='output directory (default: <rerun-dir>/delta)')
    ap.add_argument('--transfer-out', default=None, help='write the carried-over verdicts as an annotated JSONL for the re-run (identical rows only)')
    a = ap.parse_args(argv)
    ann = a.annotated
    if ann is None:
        import glob
        c = sorted(glob.glob(f'{a.base_dir}/audit/annotated-new-*.jsonl'))
        ann = c[-1] if c else None
    d = build(a.base_dir, a.rerun_dir, ann)
    out = a.out or f'{a.rerun_dir}/delta'
    p = common.write_new_version(d, f'{out}/delta.json')
    md = render_md(d)
    with open(p.replace('.json', '.md'), 'w', encoding='utf-8') as f:
        f.write(md)
    print(md)
    print(f'→ {p}')
    if a.transfer_out:
        t = transfer_annotations(read_jsonl(ann), d['rescue_rows'], d['rerun']['pipeline'], d['base']['pipeline'])
        os.makedirs(os.path.dirname(a.transfer_out), exist_ok=True)
        with open(a.transfer_out, 'w', encoding='utf-8') as f:
            for r in t:
                f.write(json.dumps(r, ensure_ascii=False) + '\n')
        print(f'{len(t)} verdicts transferred (identical rows only) → {a.transfer_out}')
    return 0


if __name__ == '__main__':
    sys.exit(main())
