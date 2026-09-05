#!/usr/bin/env python3
"""Round 4 · Lane D — run ONE small legacy batch through the existing TC-v2 pipeline CLI (as-is).

    python3 tool/corpus/legacy/run_batch.py --batch tool/corpus/legacy/batches/batch-1.json
    python3 tool/corpus/legacy/run_batch.py --batch … --dry-run          # print the commands only
    python3 tool/corpus/legacy/run_batch.py --batch … --skip-docling     # re-run SDM/TSL/bridge on existing raw

Chain (Founder §8): ORIGINAL SOURCE (PDF page + OCR lines) → tc2_run (docling + xycut + naive raw) →
tc2_sdm (agreement gate · guards · role layer) → tc2_attach (header-based lesson identity) → tc2_tsl
(Trusted Structured Lesson: trusted blocks + withheld regions) → tsl_to_lesson_document (bridge).
Lane D never edits those scripts; it points them at a SHADOW ROOT via TC_ROOT so every byte they write
lands under poc-out/round4/legacy/<batch>/ while they read the corpus through symlinks:

    poc-out/round4/legacy/<batch>/tcroot/poc-out/graph            → main poc-out/graph          (read)
    poc-out/round4/legacy/<batch>/tcroot/poc-out/pdf              → main poc-out/pdf            (read)
    poc-out/round4/legacy/<batch>/tcroot/poc-out/trusted-corpus/tc-v1 → main tc-v1              (read: census)
    poc-out/round4/legacy/<batch>/tcroot/poc-out/trusted-corpus/tc-v2/<pipeline>/…              (WRITE)
    poc-out/round4/legacy/<batch>/lesson-documents/                                             (WRITE, bridge)
    poc-out/round4/legacy/<batch>/run-manifest.json      commands, exit codes, code sha, versions, sha256 of outputs

A page whose raw/SDM/TSL the pipeline cannot produce is simply absent → the lesson is WITHHELD in the
compare, never guessed. Nothing outside the batch directory is written; a second run of the same batch
id refuses to overwrite an existing run-manifest (use a new --version suffix).
"""
import argparse
import json
import os
import subprocess
import sys
import time
from datetime import datetime, timezone

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import common  # noqa: E402

CORPUS = os.path.abspath(os.path.join(HERE, '..'))          # tool/corpus (Lane A-pipeline code, called as-is)
# A re-run measures whether an IMPROVED pipeline rescues the same legacy lesson. --corpus points the run at
# another checkout of tool/corpus (e.g. Lane A-pipeline's branch) — Lane D still never edits pipeline code, it
# only chooses which build to call, and the manifest records the checkout + its git sha for both sides.
READ_LINKS = ('graph', 'pdf', 'units', 'units-k12', 'k12-census-exports', 'layout')


def shadow_root(batch_dir):
    return f'{batch_dir}/tcroot'


def make_shadow(batch_dir, main_root=common.MAIN_ROOT, pipeline='legacy-b1'):
    """Create the symlink tree once; idempotent; never touches the main poc-out."""
    root = shadow_root(batch_dir)
    po = f'{root}/poc-out'
    os.makedirs(f'{po}/trusted-corpus/tc-v2/{pipeline}', exist_ok=True)
    for name in READ_LINKS:
        src = f'{main_root}/poc-out/{name}'
        dst = f'{po}/{name}'
        if os.path.isdir(src) and not os.path.lexists(dst):
            os.symlink(src, dst)
    src = f'{main_root}/poc-out/trusted-corpus/tc-v1'
    dst = f'{po}/trusted-corpus/tc-v1'
    if os.path.isdir(src) and not os.path.lexists(dst):
        os.symlink(src, dst)
    return root


def pages_of(batch):
    pages = []
    for L in batch['lessons']:
        for p in L['pages_pdf']:
            pages.append(dict(book=L['book'], page=int(p)))
    # unique, deterministic
    seen = set(); out = []
    for p in pages:
        k = (p['book'], p['page'])
        if k not in seen:
            seen.add(k); out.append(p)
    return out


def books_of(batch):
    out = []
    for L in batch['lessons']:
        if L['book'] not in out:
            out.append(L['book'])
    return out


def git_sha(cwd):
    try:
        return subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=cwd, text=True).strip()
    except Exception:  # noqa: BLE001
        return None


def commands(batch, batch_dir, python=common.BAKEOFF_PYTHON, corpus=None):
    """The exact commands, in order. Env TC_ROOT = shadow root for the pipeline steps; the bridge runs
    against the main root (it only reads curriculum/units-k12 and writes to --out)."""
    corpus = corpus or CORPUS
    P = batch['pipeline']
    pages = f'{batch_dir}/pages.json'
    books = books_of(batch)
    env = dict(TC_ROOT=shadow_root(batch_dir))
    cmds = [
        dict(step='attach', cmd=[python, f'{corpus}/tc2_attach.py', '--pipeline', P] + books, env=env),
        dict(step='fast', cmd=[python, f'{corpus}/tc2_run.py', '--pipeline', P, '--pages', pages, '--fast'], env=env),
        dict(step='docling', cmd=[python, f'{corpus}/tc2_run.py', '--pipeline', P, '--pages', pages, '--shard', '0', '--nshards', '1'], env=env),
        dict(step='manifest', cmd=[python, f'{corpus}/tc2_run.py', '--pipeline', P, '--pages', pages, '--manifest'], env=env),
        dict(step='sdm', cmd=[python, f'{corpus}/tc2_sdm.py', '--pipeline', P, '--pages', pages], env=env),
        dict(step='tsl', cmd=[python, f'{corpus}/tc2_tsl.py', '--pipeline', P] + books, env=env),
    ]
    return cmds


def bridge_commands(batch, batch_dir, python=common.BAKEOFF_PYTHON, corpus=None):
    corpus = corpus or CORPUS
    P = batch['pipeline']
    out = []
    for L in batch['lessons']:
        tsl = f'{shadow_root(batch_dir)}/poc-out/trusted-corpus/tc-v2/{P}/lessons/{L["book"]}/bai-{int(L["lesson"]):02d}.tsl.json'
        out.append(dict(step=f'bridge:{L["book"]}:L{L["lesson"]}', tsl=tsl,
                        cmd=[python, f'{corpus}/tsl_to_lesson_document.py', '--tsl', tsl, '--out', f'{batch_dir}/lesson-documents', '--audit-status', 'notAudited'],
                        env=dict(TC_ROOT=common.MAIN_ROOT)))
    return out


def run(cmd, env, log):
    t0 = time.time()
    e = dict(os.environ); e.update(env)
    p = subprocess.run(cmd, env=e, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    log.write(f'$ {" ".join(cmd)}\n{p.stdout}\n[rc={p.returncode} {time.time() - t0:.1f}s]\n\n'); log.flush()
    return p.returncode, time.time() - t0, p.stdout[-2000:]


def inventory(batch_dir, pipeline):
    """sha256 of every pipeline output of this batch (attach, sdm, tsl, lesson documents)."""
    root = f'{shadow_root(batch_dir)}/poc-out/trusted-corpus/tc-v2/{pipeline}'
    inv = {}
    for sub in ('attach', 'sdm', 'lessons'):
        d = f'{root}/{sub}'
        for dp, _, fs in os.walk(d):
            for f in sorted(fs):
                if f.endswith('.json'):
                    p = f'{dp}/{f}'
                    inv[os.path.relpath(p, batch_dir)] = common.sha256_file(p)
    d = f'{batch_dir}/lesson-documents'
    if os.path.isdir(d):
        for f in sorted(os.listdir(d)):
            if f.endswith('.json'):
                inv[os.path.relpath(f'{d}/{f}', batch_dir)] = common.sha256_file(f'{d}/{f}')
    return inv


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--batch', required=True)
    ap.add_argument('--version', default='', help='suffix for a re-run of the same batch spec (e.g. rerun-tc2-p2) — a new directory, old outputs kept')
    ap.add_argument('--pipeline', default=None, help='override the pipeline id of the spec (e.g. tc2-p2 after Lane A ships)')
    ap.add_argument('--python', default=common.BAKEOFF_PYTHON)
    ap.add_argument('--corpus', default=CORPUS, help='checkout of tool/corpus to CALL (default: this one) — e.g. Lane A-pipeline\'s branch for a tc2-p2 re-run')
    ap.add_argument('--corpus-ref', default=None, help='the ref the --corpus tree was exported from, when it is not itself a checkout (recorded in the manifest)')
    ap.add_argument('--dry-run', action='store_true')
    ap.add_argument('--skip-docling', action='store_true')
    ap.add_argument('--only', default=None, help='comma list of steps to run (attach,fast,docling,manifest,sdm,tsl,bridge)')
    a = ap.parse_args(argv)
    batch = common.load_json(a.batch)
    if a.pipeline:
        batch['pipeline'] = a.pipeline
    name = batch['batch'] + (f'-{a.version}' if a.version else '')
    batch_dir = f'{common.LEGACY_OUT}/{name}'
    manifest_path = f'{batch_dir}/run-manifest.json'
    corpus = os.path.abspath(a.corpus)
    cmds = commands(batch, batch_dir, a.python, corpus) + bridge_commands(batch, batch_dir, a.python, corpus)
    if a.dry_run:
        for c in cmds:
            print(c['step'], 'TC_ROOT=' + c['env'].get('TC_ROOT', '<main>'), ' '.join(c['cmd']))
        return 0
    if os.path.exists(manifest_path) and not a.only:
        raise SystemExit(f'{manifest_path} exists — a batch run is never overwritten; pass --version <suffix> for a new run')
    os.makedirs(batch_dir, exist_ok=True)
    make_shadow(batch_dir, pipeline=batch['pipeline'])
    common.dump_json(pages_of(batch), f'{batch_dir}/pages.json')
    common.dump_json(batch, f'{batch_dir}/batch-spec.json')
    only = set(a.only.split(',')) if a.only else None
    started = datetime.now(timezone.utc).isoformat(timespec='seconds')
    results = []
    with open(f'{batch_dir}/run.log', 'a', encoding='utf-8') as log:
        log.write(f'# {started} batch={name} pipeline={batch["pipeline"]} corpus={corpus} code={git_sha(corpus)}\n')
        for c in cmds:
            step = c['step'].split(':')[0]
            if only and step not in only:
                continue
            if a.skip_docling and step == 'docling':
                results.append(dict(step=c['step'], skipped=True)); continue
            if step == 'bridge' and not os.path.exists(c['tsl']):
                results.append(dict(step=c['step'], rc=None, note='no TSL produced for this lesson → WITHHELD (nothing guessed)', tsl=c['tsl'])); continue
            rc, secs, tail = run(c['cmd'], c['env'], log)
            results.append(dict(step=c['step'], rc=rc, seconds=round(secs, 1), tail=tail.strip().splitlines()[-3:]))
            print(f'{c["step"]:<42} rc={rc} {secs:.1f}s')
    tc2_manifest = common.load_json(f'{shadow_root(batch_dir)}/poc-out/trusted-corpus/tc-v2/{batch["pipeline"]}/manifest.json', {})
    prev = common.load_json(manifest_path, {}) if a.only else {}
    man = dict(batch=name, spec=os.path.relpath(a.batch, common.REPO_ROOT), pipeline=batch['pipeline'], started=prev.get('started', started),
               updated=datetime.now(timezone.utc).isoformat(timespec='seconds'), pipeline_corpus=corpus, pipeline_code_sha=git_sha(corpus) or a.corpus_ref, pipeline_code_ref=a.corpus_ref, lane_d_code_sha=git_sha(HERE),
               python=a.python, versions=tc2_manifest.get('versions'), docling_options=tc2_manifest.get('docling_options'), tc2_summary=tc2_manifest.get('summary'),
               shadow_root=shadow_root(batch_dir), pages=len(pages_of(batch)), books=books_of(batch), steps=(prev.get('steps', []) + results), outputs=inventory(batch_dir, batch['pipeline']))
    common.dump_json(man, manifest_path)
    print(f'run manifest → {manifest_path} ({len(man["outputs"])} outputs)')
    return 0


if __name__ == '__main__':
    sys.exit(main())
