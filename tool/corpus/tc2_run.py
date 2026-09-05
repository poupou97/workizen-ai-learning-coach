#!/usr/bin/env python3
"""TC-v2 — SCIENCE SLICE runner (versioned · resumable · deterministic).

Why: the Founder approved ONE bounded, versioned slice (Khoa học 4–5, KHTN 6–9 SGK + a
≤ 100-page SGV sample) to validate the chain Source → SDM → block trust → Role Layer →
guards → lesson attachment → Trusted Structured Lesson. Nothing outside
poc-out/trusted-corpus/tc-v2/<pipeline>/ is written; tc-v1 and every older output stay
untouched (read-only).

Per page three raw candidates are produced in the SAME wrapper shape as TC-v1's bake-off
(`{candidate, book, page, seconds, python, error, result}`) so tc_sdm / tc_score /
tc_cascade work unchanged with `--ver tc-v2/<pipeline>`:
  docling-ocrmac  Docling 2.126 layout model + Apple Vision (ocrmac) text — PRIMARY.
                  Converter options are byte-identical to tc_bakeoff_run._docling; the
                  converter is created ONCE per worker (models loaded once).
  current-xycut   WAL-206 layout_extract.extract_page on the existing OCR lines — VERIFIER.
  current-naive   the OCR lines in file order (WAL-204 order) — kept for old-vs-new.

Layout:
  poc-out/trusted-corpus/tc-v2/<pipeline>/bakeoff/raw/<candidate>/<book>-pNNN.json
  poc-out/trusted-corpus/tc-v2/<pipeline>/logs/run-<shard>.log      (per-page seconds)
  poc-out/trusted-corpus/tc-v2/<pipeline>/manifest.json             (--manifest)
Resumable: a page whose raw docling file exists is skipped. Single-page PDFs are cut into a
temp dir and deleted after conversion (no 0.5 GB of page PDFs).

Usage (bake-off venv python for docling; system python3 is enough for --fast / --manifest):
  python3 tool/corpus/tc2_run.py --pipeline tc2-p1 --pages P.json --fast          # xycut + naive (seconds)
  .venv-bakeoff/bin/python tool/corpus/tc2_run.py --pipeline tc2-p1 --pages P.json --workers 2   # docling, spawns shards
  python3 tool/corpus/tc2_run.py --pipeline tc2-p1 --pages P.json --manifest
  python3 tool/corpus/tc2_run.py --pipeline tc2-p1 --make-pages slice   # → pages-slice.json (all OCR pages of the 6 SGK books)
  python3 tool/corpus/tc2_run.py --pipeline tc2-p2 --make-pages 06-sgk-khoa-hoc-tu-nhien-6:61-64 --out DIR   # one bounded batch
"""
import argparse
import glob
import json
import os
import platform
import re
import subprocess
import sys
import tempfile
import time
from datetime import datetime, timezone

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import tc2_paths  # noqa: E402
ROOT = tc2_paths.ROOT
OCR = f'{ROOT}/poc-out/graph/ocr-body'
PDF = f'{ROOT}/poc-out/pdf'
SLICE_BOOKS = ['04-sgk-khoa-hoc-4', '05-sgk-khoa-hoc-5', '06-sgk-khoa-hoc-tu-nhien-6', '07-sgk-khoa-hoc-tu-nhien-7', '08-sgk-khoa-hoc-tu-nhien-8', '09-sgk-khoa-hoc-tu-nhien-9']
SGV_BOOKS = ['04-sgv-khoa-hoc-4', '05-sgv-khoa-hoc-5', '06-sgv-khoa-hoc-tu-nhien-6', '07-sgv-khoa-hoc-tu-nhien-7', '08-sgv-khoa-hoc-tu-nhien-8', '09-sgv-khoa-hoc-tu-nhien-9']
DOCLING_OPTS = dict(lang=['vi-VT', 'en-US'], recognition='accurate', force_full_page_ocr=True, images_scale=2.0, do_table_structure=True, do_ocr=True)


def outdir(pipeline):
    return tc2_paths.out_root(pipeline)


def pdf_path(book):
    p = f'{PDF}/{book[:2]}/{book}.pdf'
    if os.path.exists(p):
        return p
    p = f'{PDF}/{book}.pdf'
    return p if os.path.exists(p) else None


def raw_path(pipeline, cand, book, page):
    return tc2_paths.own_raw_path(cand, book, page, pipeline)


def raw_exists(pipeline, cand, book, page, reuse=True):
    """True when a usable raw file exists for this page — in this run's root or, with reuse, in an earlier
    pipeline version (tc2_paths fallback chain)."""
    return tc2_paths.raw_path(cand, book, page, pipeline, allow_fallback=reuse)[0] is not None


def write_raw(pipeline, cand, book, page, seconds, result, err=None):
    p = raw_path(pipeline, cand, book, page)
    os.makedirs(os.path.dirname(p), exist_ok=True)
    tmp = p + '.tmp'
    json.dump(dict(candidate=cand, book=book, page=page, seconds=round(seconds, 3), python=sys.executable, error=err, result=result, pipeline=pipeline),
              open(tmp, 'w'), ensure_ascii=False, default=str)
    os.replace(tmp, p)


# ---------------------------------------------------------------- page lists
def make_pages(kind, pipeline):
    """`slice` = the six science SGK books. Round 4 (Lane D asked for a bounded, arbitrary batch):
    `<book>` = every OCR page of one book, `<book>:FROM-TO` = a PDF page range of one book. The file is
    named after the request so two batches never overwrite each other."""
    lo = hi = None
    if kind == 'slice':
        books, name = SLICE_BOOKS, 'slice'
    else:
        book, _, rng = kind.partition(':')
        if not os.path.isdir(f'{OCR}/{book}'):
            raise SystemExit(f'kinds: slice | <book> | <book>:FROM-TO   (no OCR pages for book {book!r})')
        if rng:
            m = re.fullmatch(r'(\d+)-(\d+)', rng)
            if not m:
                raise SystemExit('page range must be FROM-TO in PDF pages, e.g. 06-sgk-khoa-hoc-tu-nhien-6:61-64')
            lo, hi = int(m.group(1)), int(m.group(2))
        books, name = [book], kind.replace(':', '-')
    pages = []
    for b in books:
        for f in sorted(glob.glob(f'{OCR}/{b}/p*.json')):
            n = int(re.search(r'p(\d+)\.json', f).group(1))
            if lo is not None and not (lo <= n <= hi):
                continue
            pages.append(dict(book=b, page=n))
    if not pages:
        raise SystemExit(f'no pages for {kind!r}')
    os.makedirs(outdir(pipeline), exist_ok=True)
    out = f'{outdir(pipeline)}/pages-{name}.json'
    json.dump(pages, open(out, 'w'))
    print(len(pages), 'pages →', out)
    return out


# ---------------------------------------------------------------- fast candidates
def run_fast(pipeline, pages, force=False, reuse=True):
    import layout_extract
    n = 0
    t0 = time.time()
    for p in pages:
        book, page = p['book'], int(p['page'])
        ocr = f'{OCR}/{book}/p{page:03d}.json'
        if not os.path.exists(ocr):
            continue
        if force or not raw_exists(pipeline, 'current-xycut', book, page, reuse):
            t = time.time()
            try:
                res = layout_extract.extract_page(book, ocr); err = None
            except Exception as e:  # pragma: no cover
                res = None; err = repr(e)
            write_raw(pipeline, 'current-xycut', book, page, time.time() - t, res, err)
        if force or not raw_exists(pipeline, 'current-naive', book, page, reuse):
            t = time.time()
            j = json.load(open(ocr))
            write_raw(pipeline, 'current-naive', book, page, time.time() - t, dict(lines=j['lines'], extraction_method=j.get('extraction_method')))
        n += 1
    print(f'fast candidates: {n} pages in {time.time() - t0:.1f}s')


# ---------------------------------------------------------------- docling
def make_converter():
    from docling.datamodel.base_models import InputFormat
    from docling.datamodel.pipeline_options import PdfPipelineOptions, OcrMacOptions
    from docling.document_converter import DocumentConverter, PdfFormatOption
    opts = PdfPipelineOptions()
    opts.do_ocr = True
    opts.do_table_structure = True
    opts.images_scale = 2.0
    opts.ocr_options = OcrMacOptions(lang=['vi-VT', 'en-US'], recognition='accurate', force_full_page_ocr=True)
    return DocumentConverter(format_options={InputFormat.PDF: PdfFormatOption(pipeline_options=opts)})


def run_docling(pipeline, pages, shard, nshards, force=False, reuse=True):
    import fitz
    conv = make_converter()
    logd = f'{outdir(pipeline)}/logs'; os.makedirs(logd, exist_ok=True)
    log = open(f'{logd}/run-docling-{shard}of{nshards}.log', 'a')
    tmpd = tempfile.mkdtemp(prefix='tc2-pages-', dir=os.environ.get('TC2_TMP') or None)
    mine = [p for i, p in enumerate(pages) if i % nshards == shard]
    done = skipped = errs = 0
    for p in mine:
        book, page = p['book'], int(p['page'])
        out = raw_path(pipeline, 'docling-ocrmac', book, page)
        if raw_exists(pipeline, 'docling-ocrmac', book, page, reuse) and not force:
            skipped += 1; continue
        src = pdf_path(book)
        if not src:
            write_raw(pipeline, 'docling-ocrmac', book, page, 0, None, 'no pdf'); errs += 1; continue
        one = f'{tmpd}/{book}-p{page:03d}.pdf'
        t0 = time.time(); err = None; res = None
        try:
            s = fitz.open(src); d = fitz.open(); d.insert_pdf(s, from_page=page - 1, to_page=page - 1); d.save(one); d.close(); s.close()
            r = conv.convert(one)
            doc = r.document
            res = dict(docling=doc.export_to_dict(), markdown=doc.export_to_markdown(), status=str(r.status))
        except Exception:
            import traceback
            err = traceback.format_exc()[-4000:]; errs += 1
        finally:
            try:
                os.remove(one)
            except OSError:
                pass
        dt = time.time() - t0
        write_raw(pipeline, 'docling-ocrmac', book, page, dt, res, err)
        done += 1
        log.write(f'{datetime.now(timezone.utc).isoformat(timespec="seconds")} {book} p{page:03d} {dt:.2f}s {"ERROR" if err else "ok"}\n'); log.flush()
    log.write(f'# shard {shard}/{nshards} done={done} skipped={skipped} errors={errs}\n'); log.close()
    try:
        os.rmdir(tmpd)
    except OSError:
        pass
    print(f'shard {shard}/{nshards}: done={done} skipped={skipped} errors={errs}', flush=True)


# ---------------------------------------------------------------- manifest
def git_sha():
    try:
        return subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=HERE, text=True).strip()
    except Exception:
        return None


def versions():
    v = {}
    try:
        import importlib.metadata as m
        for pkg in ('docling', 'ocrmac', 'pymupdf', 'rapidfuzz'):
            try:
                v[pkg] = m.version(pkg)
            except Exception:
                v[pkg] = None
    except Exception:
        pass
    v['python'] = sys.version.split()[0]
    v['macos'] = platform.mac_ver()[0]
    try:
        v['macos_build'] = subprocess.check_output(['sw_vers', '-buildVersion'], text=True).strip()
    except Exception:
        pass
    return v


def manifest(pipeline, pages_files):
    d = outdir(pipeline)
    m_path = f'{d}/manifest.json'
    m = json.load(open(m_path)) if os.path.exists(m_path) else dict(pipeline=pipeline, created=datetime.now(timezone.utc).isoformat(timespec='seconds'))
    m.update(git_sha=git_sha(), versions=versions(), docling_options=DOCLING_OPTS, xycut='layout-xycut-v1 (tool/corpus/layout_extract.py)',
             docling_artifacts=os.environ.get('DOCLING_ARTIFACTS_PATH'), updated=datetime.now(timezone.utc).isoformat(timespec='seconds'),
             candidates=['docling-ocrmac', 'current-xycut', 'current-naive'])
    status = {}
    secs = []
    total = 0
    for pf in pages_files:
        for p in json.load(open(pf)):
            book, page = p['book'], int(p['page']); total += 1
            st = {}
            for cand in m['candidates']:
                rp, src = tc2_paths.raw_path(cand, book, page, pipeline)
                if rp is not None:
                    try:
                        r = json.load(open(rp))
                        st[cand] = 'error' if r.get('error') else ('ok' if src == pipeline else f'ok:{src}')
                        if cand == 'docling-ocrmac' and not r.get('error') and r.get('seconds') is not None and src == pipeline:
                            secs.append(r['seconds'])
                    except Exception:
                        st[cand] = 'corrupt'
                else:
                    st[cand] = 'missing'
            status.setdefault(book, {})[f'p{page:03d}'] = st
    secs.sort()
    m['pages'] = status
    m['summary'] = dict(pages=total, docling_ok=sum(1 for b in status.values() for s in b.values() if (s.get('docling-ocrmac') or '').startswith('ok')),
                        docling_reused=sum(1 for b in status.values() for s in b.values() if (s.get('docling-ocrmac') or '').startswith('ok:')),
                        docling_error=sum(1 for b in status.values() for s in b.values() if s.get('docling-ocrmac') == 'error'),
                        docling_missing=sum(1 for b in status.values() for s in b.values() if s.get('docling-ocrmac') == 'missing'),
                        xycut_ok=sum(1 for b in status.values() for s in b.values() if (s.get('current-xycut') or '').startswith('ok')),
                        docling_sec_median=(secs[len(secs) // 2] if secs else None), docling_sec_p90=(secs[int(0.9 * len(secs))] if secs else None),
                        docling_sec_total=round(sum(secs), 1), docling_sec_mean=(round(sum(secs) / len(secs), 3) if secs else None))
    # storage
    sz = 0
    for cand in m['candidates']:
        for f in glob.glob(f'{d}/bakeoff/raw/{cand}/*.json'):
            sz += os.path.getsize(f)
    m['summary']['raw_bytes'] = sz
    json.dump(m, open(m_path, 'w'), ensure_ascii=False, indent=1)
    print(json.dumps(m['summary'], indent=1))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--pipeline', default='tc2-p1'); ap.add_argument('--pages', action='append', default=[])
    ap.add_argument('--make-pages', default=None); ap.add_argument('--fast', action='store_true'); ap.add_argument('--workers', type=int, default=0)
    ap.add_argument('--shard', type=int, default=None); ap.add_argument('--nshards', type=int, default=1); ap.add_argument('--manifest', action='store_true'); ap.add_argument('--force', action='store_true')
    ap.add_argument('--out', default=None, help='pipeline output root (default poc-out/trusted-corpus/tc-v2/<pipeline>; env TC2_OUT_ROOT)')
    ap.add_argument('--no-reuse-raw', action='store_true', help='do not reuse raw candidate files of earlier pipeline versions')
    a = ap.parse_args()
    if a.out:
        tc2_paths.set_out_root(a.out)
    reuse = not a.no_reuse_raw
    if a.make_pages:
        make_pages(a.make_pages, a.pipeline); return
    pages = [p for pf in a.pages for p in json.load(open(pf))]
    if a.fast:
        run_fast(a.pipeline, pages, a.force, reuse)
    if a.shard is not None:
        run_docling(a.pipeline, pages, a.shard, a.nshards, a.force, reuse); return
    if a.workers:
        procs = []
        for i in range(a.workers):
            cmd = [sys.executable, os.path.abspath(__file__), '--pipeline', a.pipeline, '--shard', str(i), '--nshards', str(a.workers)] + [x for pf in a.pages for x in ('--pages', pf)] + (['--force'] if a.force else []) + (['--out', a.out] if a.out else []) + (['--no-reuse-raw'] if a.no_reuse_raw else [])
            procs.append(subprocess.Popen(cmd))
        rc = [p.wait() for p in procs]
        print('workers exit codes', rc)
    if a.manifest:
        manifest(a.pipeline, a.pages)


if __name__ == '__main__':
    main()
