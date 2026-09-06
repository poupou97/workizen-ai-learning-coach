#!/usr/bin/env python3
"""The round-6 recognition study — one script, three populations, six metrics.

Populations, kept apart and never summed (the D5 denominator rule):

  DEV       the fraction-dense Toán pages round 5 hand-checked and tuned on
            (Toán 4 tập hai p080-083 / p116-122, Toán 5 tập một p020-024).
  HOLDOUT   a seeded random sample of Toán pages with both an OCR page and a PDF, drawn AFTER
            the consensus rule was frozen. Nothing in this package was tuned on it.
  SDM       every Toán page in the corpus that has an SDM as well as a PDF — the population
            round 5's «274 of 336 fraction-bearing blocks» lives in, so the before -> after can
            be stated on the same kind of object (a BLOCK, not a region).

Two things are measured on every population and reported separately, because one without the
other is meaningless:

  RECOVERY  regions whose digits the whole-page OCR never read. What the round is trying to
            reach. Correctness is decided by the contact sheet, never by the recogniser.
  CONTROL   regions the whole-page OCR already read. The re-crop must return the same value;
            a disagreement is a candidate FALSE RECOGNITION. Without this half, «recovered N»
            is unfalsifiable.
"""
import glob
import json
import os
import random
import sys
from collections import Counter, defaultdict

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from mathfix import detect as D                      # noqa: E402
from mathfix import extract as E                     # noqa: E402
from mathfix import validate as VAL                  # noqa: E402
from mathfix.inkmask import InkMask                  # noqa: E402
from mathfix.tokens import Token, load_tokens, median_height   # noqa: E402
from recognition import census as CE                 # noqa: E402
from recognition import vision as V                  # noqa: E402

ROOT = os.environ.get('TC_ROOT', '/Users/alexnguyen/projects/workizen-ai-learning-coach')
OCR_BODY = f'{ROOT}/poc-out/graph/ocr-body'
OUT = f'{ROOT}/poc-out/round6/recognition'

DEV_PAGES = ([('04-sgk-toan-4-tap-hai', p) for p in range(80, 84)]
             + [('04-sgk-toan-4-tap-hai', p) for p in range(116, 123)]
             + [('05-sgk-toan-5-tap-mot', p) for p in range(20, 25)])


def toan_books():
    return sorted(b for b in os.listdir(OCR_BODY)
                  if '-sgk-toan-' in b and os.path.exists(V.pdf_path(b)))


def book_pages(book):
    return sorted(int(os.path.basename(p)[1:4]) for p in glob.glob(f'{OCR_BODY}/{book}/p*.json'))


def holdout_pages(n=24, seed=20260906):
    """Drawn with a seed recorded here, so the draw is reproducible and cannot be re-rolled."""
    pairs = [(b, p) for b in toan_books() for p in book_pages(b)]
    pairs = [x for x in pairs if x not in set(DEV_PAGES)]
    random.Random(seed).shuffle(pairs)
    return sorted(pairs[:n])


#: Books deliberately excluded from every holdout: they are what round 5 and this lane tuned on.
DEV_BOOKS = frozenset({'04-sgk-toan-4-tap-hai', '05-sgk-toan-5-tap-mot'})


def dense_holdout_pages(n=12, seed=20260906, min_regions=6, books=None):
    """A holdout of pages that actually contain numeric printed fractions.

    The unbiased all-grade sample measured first (`holdout_pages`) returns 0 recoveries out of 66
    regions, and the contact sheet says why: on a random Toán page across grades 2-12 most
    detected bar regions are **not numeric stacked fractions** — they are algebraic fractions
    whose halves carry letters (out of scope by construction: a half is named only by a bare digit
    run), column-arithmetic rules, table rules and illustration line art. Both numbers are
    reported; neither replaces the other.

    The selection rule is declared before the draw and is about the DETECTOR, not the recogniser:
    a page qualifies when the raster detector finds at least `min_regions` bar regions, in a book
    this lane never tuned on. Nothing about what the recogniser would say enters the choice.
    """
    from mathfix.inkmask import InkMask
    books = books or [b for b in toan_books() if b not in DEV_BOOKS and int(b[:2]) <= 6]
    pairs = [(b, p) for b in books for p in book_pages(b)]
    random.Random(seed).shuffle(pairs)
    out = []
    for book, page in pairs:
        if len(out) >= n:
            break
        try:
            mask = InkMask.from_pdf(V.pdf_path(book), page, dpi=300)
            tokens = load_tokens(book, page)
            if len(D.find_fraction_regions(mask, tokens)) >= min_regions:
                out.append((book, page))
        except Exception:
            continue
    return sorted(out)


def fraction_topic_pages(n=12, seed=20260906, books=None):
    """A holdout of pages that TEACH fractions, in books this lane never tuned on.

    The two earlier holdouts are both reported and both are near-zero, and the contact sheets say
    the same thing twice: the population was wrong, not the recogniser. The unbiased all-grade
    sample is dominated by algebraic fractions (out of scope: a half is named only by a bare digit
    run) and by detector false positives; the «dense» sample, selected on `>= 6 detected bar
    regions`, drew grades 1-3, where the dense bar regions are COLUMN-ARITHMETIC RULES — those
    books teach no fractions at all. Selecting on the detector selected the detector's own errors.

    So this holdout is selected on CONTENT, by a rule fixed before the draw: the page's own OCR
    text contains «phân số». Nothing about the detector or the recogniser enters the choice.
    """
    books = books or [b for b in toan_books() if b not in DEV_BOOKS]
    pairs = []
    for book in books:
        for page in book_pages(book):
            try:
                with open(f'{OCR_BODY}/{book}/p{page:03d}.json') as fh:
                    doc = json.load(fh)
            except Exception:
                continue
            if any('phân số' in (ln.get('text') or '').lower() for ln in doc.get('lines') or []):
                pairs.append((book, page))
    random.Random(seed).shuffle(pairs)
    return sorted(pairs[:n])


def sdm_pages():
    """Every Toán page with an SDM, and the SDM this study reads for it.

    Several pipeline runs wrote an SDM for the same page; the newest one on disk is used, and the
    path is recorded per page so the number can be reproduced against exactly that file.
    """
    best = {}
    for path in glob.glob(f'{ROOT}/poc-out/**/*.sdm.json', recursive=True):
        parts = path.split('/')
        book = parts[-2]
        if '-toan-' not in book or not os.path.exists(V.pdf_path(book)):
            continue
        page = int(parts[-1][1:4])
        prev = best.get((book, page))
        if prev is None or os.path.getmtime(path) > os.path.getmtime(prev):
            best[(book, page)] = path
    return dict(sorted(best.items()))


# ---------------------------------------------------------------- one page, end to end
def study_page(book, page, sdm_path=None, dpi=300, scales=V.DEFAULT_SCALES):
    """Regions before and after, plus the block-level projection when an SDM is given."""
    from recognition import boxes as B
    from recognition import consensus as C

    mask = InkMask.from_pdf(V.pdf_path(book), page, dpi=dpi)
    tokens = load_tokens(book, page)
    regions = D.find_fraction_regions(mask, tokens)
    mh = median_height(tokens) or 0.018

    jobs, meta = [], {}
    for i, r in enumerate(regions):
        bar = [r.bar.x0, r.bar.y0, r.bar.length, r.bar.thickness]
        bxs = B.fraction_boxes(bar, mh)
        prefix = f'{i:03d}|'
        jobs.extend(V.make_jobs(book, page, bxs, scales=scales, key_prefix=prefix))
        meta[i] = (r, bar, prefix)
    results = V.run(jobs)

    rows, recovered_tokens = [], []
    next_index = (max((t.index for t in tokens), default=-1)) + 1
    for i, (r, bar, prefix) in meta.items():
        fr = C.read_fraction(f'{book}:p{page:03d}:r{i:03d}',
                             V.by_scale(results, prefix, 'numerator'),
                             V.by_scale(results, prefix, 'denominator'),
                             V.by_scale(results, prefix, 'region'))
        cls, note = CE.classify_region(r, tokens, mask.height)
        baseline = f'{r.numerator.stripped}/{r.denominator.stripped}' if r.extractable else None
        rows.append(dict(key=fr.region_key, book=book, page=page,
                         bar=[round(v, 5) for v in bar],
                         population='control' if r.extractable else 'recovery',
                         failure_class=cls, failure_note=note,
                         baseline_reason=r.reason or 'ok', baseline_value=baseline,
                         verdict=fr.verdict, value=fr.value if fr.ok else None,
                         reason=fr.reason,
                         numerator_scales=list(fr.numerator.agreeing_scales),
                         denominator_scales=list(fr.denominator.agreeing_scales),
                         region_scale=fr.region_agreement_scale))
        if fr.ok and not r.extractable:
            # The recovered halves become OBSERVATIONS with their own engine name. They are not
            # OCR lines and are never labelled as such: `Token.engine` is what a validator and a
            # reviewer read to know a digit came from a crop and not from the page pass.
            n_box, d_box, _ = B.fraction_boxes(bar, mh)
            for box, val in ((n_box, fr.numerator.value), (d_box, fr.denominator.value)):
                x0, y0, x1, y1 = tight_box(mask, box)
                recovered_tokens.append(Token(
                    text=val, x=x0, y=y0, w=x1 - x0, h=y1 - y0,
                    conf=1.0, index=next_index, engine='apple-vision-crop-v1'))
                next_index += 1

    out = dict(book=book, page=page, regions=rows,
               recovered_tokens=[dict(text=t.text, bbox=[t.x, t.y, t.w, t.h], engine=t.engine)
                                 for t in recovered_tokens])
    if sdm_path:
        out['blocks'] = block_projection(book, page, sdm_path, mask, tokens, regions,
                                         recovered_tokens, mh)
    return out


def tight_box(mask, box):
    """Shrink a crop box to the ink actually inside it.

    A recovered digit must enter the pipeline as a token the size of a DIGIT, not the size of the
    window it was read in. Measured on the 113-page SDM population with the crop box used as the
    token box: `numerator_ambiguous` rose from 2 blocks to 27 and `prose_token_in_block` from 29 to
    44, because an over-wide box reaches into the neighbouring fraction's strip and `detect`
    correctly refuses a strip holding two digit candidates. The geometry has to be honest for the
    reading to be usable.
    """
    px0, py0 = int(box.x0 * mask.width), int(box.y0 * mask.height)
    px1, py1 = int(box.x1 * mask.width), int(box.y1 * mask.height)
    ext = mask.ink_extent(px0, py0, px1, py1)
    if ext is None:
        return box.bbox
    rows = [y for y in range(py0, py1) if mask.row_runs(y, ext[0], ext[1] + 1, min_len=1)]
    if not rows:
        return box.bbox
    return (ext[0] / mask.width, rows[0] / mask.height,
            (ext[1] + 1) / mask.width, (rows[-1] + 1) / mask.height)


def _inside(bbox, x, y, pad=0.0):
    bx, by, bw, bh = bbox
    return (bx - pad) <= x <= (bx + bw + pad) and (by - pad) <= y <= (by + bh + pad)


def block_projection(book, page, sdm_path, mask, tokens, regions, recovered, mh):
    """The 274-of-336 question, on blocks: does the block become proposable AFTER the re-crop?

    `mathfix.extract.math_line_candidate` is run twice on the same block — once with the tokens
    the page pass produced, once with those PLUS the recovered digits — and the two candidates
    are compared. Nothing is written back into any pipeline output; this is a projection, exactly
    as round 5's was, so the «before» numbers stay reproducible.
    """
    from mathfix import runner as R
    with open(sdm_path) as fh:
        sdm = json.load(fh)
    aug_tokens = list(tokens) + list(recovered)
    aug_regions = D.find_fraction_regions(mask, aug_tokens)
    out = []
    for blk in sdm.get('blocks') or []:
        bbox = blk.get('bbox')
        if not bbox:
            continue
        bregs = [r for r in regions if _inside(bbox, r.bar.cx, r.bar.cy, pad=0.004)]
        if not bregs:
            continue
        status = (blk.get('trust') or {}).get('status')
        reasons = list((blk.get('trust') or {}).get('reasons') or [])
        eligible = bool(status == 'WITHHELD' and reasons and set(reasons) <= R.MATH_REASONS)

        def project(toks, regs):
            btoks = [t for t in toks if _inside(bbox, t.cx, t.cy, pad=0.004)]
            brs = [r for r in regs if _inside(bbox, r.bar.cx, r.bar.cy, pad=0.004)]
            cand = E.math_line_candidate(btoks, brs, mask)
            if not brs:
                return cand, 'NO_REGION', []
            bar_len = sorted(r.bar.length for r in brs)[len(brs) // 2]
            bb = (bbox[0], bbox[1], bbox[0] + bbox[2], bbox[1] + bbox[3])
            verdict, results = VAL.validate(cand, mask, bb, median_height(btoks) or mh, bar_len)
            return cand, verdict, results

        before_c, before_v, _ = project(tokens, regions)
        after_c, after_v, after_r = project(aug_tokens, aug_regions)
        out.append(dict(
            block_id=blk.get('id'), role=(blk.get('role') or {}).get('value'),
            status=status, reasons=reasons, eligible=eligible,
            original_text=blk.get('text'), regions=len(bregs),
            before=dict(value=before_c.proposed_value, reason=before_c.reason, verdict=before_v),
            after=dict(value=after_c.proposed_value, reason=after_c.reason, verdict=after_v,
                       validations=[dict(validator_id=r.validator_id, verdict=r.verdict,
                                         evidence=r.evidence) for r in after_r]),
            sdm=os.path.relpath(sdm_path, ROOT)))
    return out


# ---------------------------------------------------------------- drivers
def run_pages(pairs, name, sdm_by_page=None, dpi=300):
    os.makedirs(OUT, exist_ok=True)
    pages, failures = [], []
    for book, page in pairs:
        try:
            pages.append(study_page(book, page, (sdm_by_page or {}).get((book, page)), dpi=dpi))
        except Exception as exc:
            failures.append(dict(book=book, page=page, error=f'{type(exc).__name__}: {exc}'))
            continue
        r = pages[-1]['regions']
        print(f"{book[:26]:26s} p{page:3d} regions={len(r):3d} "
              f"recovery_read={sum(1 for x in r if x['population'] == 'recovery' and x['value'])} "
              f"control_same={sum(1 for x in r if x['population'] == 'control' and x['value'] == x['baseline_value'])} "
              f"control_differs={sum(1 for x in r if x['population'] == 'control' and x['value'] and x['value'] != x['baseline_value'])}",
              flush=True)
    path = f'{OUT}/study-{name}.json'
    with open(path, 'w') as fh:
        json.dump(dict(name=name, pages=pages, failures=failures), fh, ensure_ascii=False, indent=1)
    print('->', path)
    return path


def summarise(path):
    with open(path) as fh:
        doc = json.load(fh)
    rows = [r for p in doc['pages'] for r in p['regions']]
    ctrl = [r for r in rows if r['population'] == 'control']
    rec = [r for r in rows if r['population'] == 'recovery']
    same = [r for r in ctrl if r['value'] and r['value'] == r['baseline_value']]
    diff = [r for r in ctrl if r['value'] and r['value'] != r['baseline_value']]
    read = [r for r in rec if r['value']]
    return dict(
        pages=len(doc['pages']), failures=len(doc['failures']), regions=len(rows),
        control=len(ctrl), control_reproduced=len(same), control_disagreed=len(diff),
        control_refused=len(ctrl) - len(same) - len(diff),
        recovery=len(rec), recovery_read=len(read),
        recoverable_fraction_rate=round(len(read) / len(rec), 4) if rec else None,
        control_disagreement_rate=round(len(diff) / len(ctrl), 4) if ctrl else None,
        failure_classes=dict(Counter(r['failure_class'] for r in rec)),
        recovery_by_class=dict(Counter(r['failure_class'] for r in read)),
        refusal_reasons=dict(Counter(r['verdict'] for r in rec if not r['value'])),
        control_refusal_reasons=dict(Counter(r['verdict'] for r in ctrl if not r['value'])),
        disagreements=[dict(key=r['key'], baseline=r['baseline_value'], recrop=r['value'])
                       for r in diff],
    )


if __name__ == '__main__':
    which = sys.argv[1] if len(sys.argv) > 1 else 'dev'
    if which == 'dev':
        run_pages(DEV_PAGES, 'dev')
    elif which == 'holdout':
        n = int(sys.argv[2]) if len(sys.argv) > 2 else 24
        run_pages(holdout_pages(n), 'holdout')
    elif which == 'holdout2':
        n = int(sys.argv[2]) if len(sys.argv) > 2 else 12
        run_pages(dense_holdout_pages(n), 'holdout2')
    elif which == 'holdout3':
        n = int(sys.argv[2]) if len(sys.argv) > 2 else 12
        run_pages(fraction_topic_pages(n), 'holdout3')
    elif which == 'sdm':
        by = sdm_pages()
        run_pages(list(by), 'sdm', sdm_by_page=by)
    elif which == 'summary':
        print(json.dumps(summarise(sys.argv[2]), ensure_ascii=False, indent=1))
