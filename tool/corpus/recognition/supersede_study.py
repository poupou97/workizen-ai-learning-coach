#!/usr/bin/env python3
"""WAL-213 · the measurement: does a recovered digit reach a repaired block once it SUPERSEDES?

Round 7's number is `10 -> 10, delta 0`, measured with `study.block_projection`, which adds the
recovered tokens beside the destroyed ones. This driver measures the same blocks a **third** way,
so the comparison is three-cornered and the first two columns stay byte-reproducible:

    BEFORE      the page pass alone                       — round 5's projection, unchanged
    ADD         page pass + recovered tokens              — round 7's projection, unchanged
    SUPERSEDE   the resolution of the supersession set    — this contract

`study.py` is not modified. Everything here reads its output plus the page raster, so the round-7
numbers keep coming out of the same code that produced them.

It writes two artefacts:

  * the full result, to `poc-out/` — INTERNAL/RESEARCH ONLY, gitignored, because it carries verbatim
    SGK readings (D4);
  * a **census** to `tool/tests/data/wal213-bai61-population.json`, which is committed and carries
    **no SGK text and no values at all** — only structure: coverage class, counts, failure class,
    scale counts, and booleans. That is what makes the population-adequacy guard runnable on a
    clean clone, where the corpus is absent by design.

Usage:
    python3 tool/corpus/recognition/supersede_study.py \\
        poc-out/round7/wal213/study-bai61-4scales.json
"""
from __future__ import annotations

import hashlib
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from mathfix import detect as D                                    # noqa: E402
from mathfix import extract as E                                   # noqa: E402
from mathfix import runner as R                                    # noqa: E402
from mathfix import validate as VAL                                # noqa: E402
from mathfix.inkmask import InkMask                                # noqa: E402
from mathfix.tokens import Token, load_tokens, median_height       # noqa: E402
from recognition import study as S                                 # noqa: E402
from recognition import supersede as X                             # noqa: E402
from recognition import vision as V                                # noqa: E402
from repair import supersession as SUP                             # noqa: E402

#: Where the CORPUS lives (PDFs, OCR, SDMs). Gitignored, machine-local, D4.
ROOT = os.environ.get('TC_ROOT', os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))))))
#: Where THIS CHECKOUT lives. Deliberately NOT `TC_ROOT`: the census is a committed artefact and
#: must land in the working tree being tested, even when the corpus it was measured on is another
#: clone's `poc-out/`. Conflating the two writes the census into whichever checkout happened to own
#: the corpus, which is how an artefact and the code that reads it drift apart.
REPO_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.dirname(os.path.abspath(__file__)))))   # tool/corpus/recognition/<this> -> repo root
CENSUS_PATH = os.path.join(REPO_ROOT, 'tool', 'tests', 'data', 'wal213-bai61-population.json')
CENSUS_VERSION = 'wal213-population-v1'


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, 'rb') as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b''):
            h.update(chunk)
    return h.hexdigest()


def _tokens_by_region(page_doc, tokens, mask, mh):
    """The recovered tokens of each region, rebuilt the way `study.study_page` built them.

    `study.py` writes `recovered_tokens` as a flat list in region order, two per recovered region
    (numerator then denominator), so they are re-keyed here rather than re-run: the reading is not
    recomputed, only attributed.
    """
    from recognition import boxes as B
    out, i = {}, 0
    flat = page_doc.get('recovered_tokens') or []
    next_index = max((t.index for t in tokens), default=-1) + 1
    for row in page_doc['regions']:
        if row['population'] != 'recovery' or not row['value']:
            continue
        pair = flat[i:i + 2]
        i += 2
        toks = []
        for rec in pair:
            # `study.study_page` writes `bbox=[t.x, t.y, t.w, t.h]` — TOKEN form, not corner form.
            # Reading it as `(x0, y0, x1, y1)` produces a token of plausible shape and wrong size,
            # and the ADD column then silently stops reproducing round 7. Caught by comparing this
            # column against `study-bai61-4scales.json` block for block; the check stays in
            # `assert_add_column_reproduces_round7`.
            x, y, w, h = rec['bbox']
            toks.append(Token(text=rec['text'], x=x, y=y, w=w, h=h, conf=1.0,
                              index=next_index, engine=rec.get('engine', X.CROP_ENGINE)))
            next_index += 1
        if not toks:                                     # geometry unavailable: rebuild the boxes
            bxs = {b.kind: b for b in B.fraction_boxes(row['bar'], mh)}
            for kind, val in (('numerator', row['value'].split('/')[0]),
                              ('denominator', row['value'].split('/')[-1])):
                bx = bxs[kind]
                x0, y0, x1, y1 = S.tight_box(mask, bx)
                toks.append(Token(text=val, x=x0, y=y0, w=x1 - x0, h=y1 - y0, conf=1.0,
                                  index=next_index, engine=X.CROP_ENGINE))
                next_index += 1
        out[row['key']] = toks
    return out


def _project(tokens, regions, bbox, mask, mh):
    """`study.block_projection`'s inner projection, verbatim in behaviour, on a token list."""
    btoks = [t for t in tokens if S._inside(bbox, t.cx, t.cy, pad=0.004)]
    brs = [r for r in regions if S._inside(bbox, r.bar.cx, r.bar.cy, pad=0.004)]
    cand = E.math_line_candidate(btoks, brs, mask)
    if not brs:
        return cand, 'NO_REGION'
    bar_len = sorted(r.bar.length for r in brs)[len(brs) // 2]
    bb = (bbox[0], bbox[1], bbox[0] + bbox[2], bbox[1] + bbox[3])
    verdict, _ = VAL.validate(cand, mask, bb, median_height(btoks) or mh, bar_len)
    return cand, verdict


def run_page(page_doc, *, pipeline='tc2-p3'):
    """Everything WAL-213 measures for one page."""
    book, page = page_doc['book'], page_doc['page']
    mask = InkMask.from_pdf(V.pdf_path(book), page, dpi=300)
    tokens = load_tokens(book, page)
    mh = median_height(tokens) or 0.018
    regions = D.find_fraction_regions(mask, tokens)
    rec_by_region = _tokens_by_region(page_doc, tokens, mask, mh)

    rels, notes = [], []
    for row in page_doc['regions']:
        if row['population'] != 'recovery' or not row['value']:
            continue
        # The block a region belongs to is decided below; the relation itself is page-scoped until
        # then, so it is built against a page-level id and re-bound per block.
        s, why = X.supersession_for_row(row, tokens, mh, f'{book}:p{page:03d}', book=book,
                                        page=page, pipeline=pipeline)
        if s is None:
            notes.append(dict(region=row['key'], kind='ADDITION', reason=why))
            continue
        rels.append((row, s))

    resolved = [s for _, s in rels if s.resolved]
    refused = [s for _, s in rels if not s.resolved]
    current_tokens, refused_keys, audit = X.resolve_tokens(
        tokens, [s for _, s in rels], rec_by_region)
    add_tokens = list(tokens) + [t for ts in rec_by_region.values() for t in ts]

    regions_add = D.find_fraction_regions(mask, add_tokens)
    regions_sup = D.find_fraction_regions(mask, current_tokens)

    sdm_path = S.sdm_pages().get((book, page))
    blocks = []
    if sdm_path:
        with open(sdm_path) as fh:
            sdm = json.load(fh)
        for blk in sdm.get('blocks') or []:
            bbox = blk.get('bbox')
            if not bbox:
                continue
            bregs = [r for r in regions if S._inside(bbox, r.bar.cx, r.bar.cy, pad=0.004)]
            if not bregs:
                continue
            here = [(row, s) for row, s in rels
                    if S._inside(bbox, row['bar'][0] + row['bar'][2] / 2.0,
                                 row['bar'][1] + row['bar'][3] / 2.0, pad=0.004)]
            before_c, before_v = _project(tokens, regions, bbox, mask, mh)
            add_c, add_v = _project(add_tokens, regions_add, bbox, mask, mh)
            block_refused = [s.region.region_key for _, s in here if not s.resolved]
            if block_refused:
                sup_value, sup_verdict = None, 'REFUSED_UNRESOLVED_SUPERSESSION'
            else:
                sup_c, sup_verdict = _project(current_tokens, regions_sup, bbox, mask, mh)
                sup_value = sup_c.proposed_value
            status = (blk.get('trust') or {}).get('status')
            reasons = list((blk.get('trust') or {}).get('reasons') or [])
            blocks.append(dict(
                block_id=blk.get('id'), role=(blk.get('role') or {}).get('value'), status=status,
                reasons=reasons,
                eligible=bool(status == 'WITHHELD' and reasons and set(reasons) <= R.MATH_REASONS),
                regions=len(bregs), supersessions=len(here),
                resolved=sum(1 for _, s in here if s.resolved),
                refused=len(block_refused),
                before=dict(value=before_c.proposed_value, verdict=before_v),
                add=dict(value=add_c.proposed_value, verdict=add_v),
                supersede=dict(value=sup_value, verdict=sup_verdict,
                               refused_regions=block_refused),
                sdm=os.path.relpath(sdm_path, ROOT)))

    return dict(book=book, page=page, sdm=os.path.relpath(sdm_path, ROOT) if sdm_path else None,
                supersessions=[s.to_json() for _, s in rels], notes=notes, blocks=blocks,
                counts=dict(recovered=len(rels) + len(notes), relations=len(rels),
                            additions=len(notes), resolved=len(resolved), refused=len(refused),
                            audit=audit))


def run(study_path, *, out_path=None, census_path=CENSUS_PATH):
    with open(study_path) as fh:
        study = json.load(fh)
    pages = [run_page(p) for p in study['pages']]
    doc = dict(version=SUP.SUPERSESSION_VERSION, study=os.path.relpath(study_path, ROOT),
               studySha256=sha256_file(study_path), scales=study.get('scales'), pages=pages)
    assert_add_column_reproduces_round7(doc, study)
    if out_path:
        os.makedirs(os.path.dirname(out_path), exist_ok=True)
        with open(out_path, 'w') as fh:
            json.dump(doc, fh, ensure_ascii=False, indent=1)
    if census_path:
        write_census(doc, census_path, study_path)
    return doc


# ---------------------------------------------------------------- the committed census
def census(doc, study_path):
    """The D4-safe projection of the real population.

    **No SGK text, no readings, no values, no bboxes.** Only the structure the contract is about:
    per region, its failure class, how many observations it would supersede, the coverage class,
    how many scales agreed, whether the halves were seen stacked, whether the replacement says
    something different, and the resulting disposition. That is enough for the population-adequacy
    guard and for every structural test, and it is not a derived copy of the textbook.
    """
    rows, blocks = [], []
    for p in doc['pages']:
        for s in p['supersessions']:
            rows.append(dict(
                regionKey=s['supersessionId'].split('#')[1],
                page=p['page'],
                failureClass=s['failureClass'],
                engine=s['engine'],
                supersededObservations=len(s['superseded']),
                coverage=s['coverage'],
                coverageFraction=s['coverageFraction'],
                disposition=s['disposition'],
                resolved=s['resolved'],
                changed=s['changed'],
                servable=s['servable'],
                agreeingScales=s['region']['minAgreeing'],
                stacked=s['region']['stacked'],
            ))
        for n in p['notes']:
            rows.append(dict(regionKey=n['region'], page=p['page'], failureClass=None,
                             engine=X.CROP_ENGINE, supersededObservations=0, coverage=SUP.NONE,
                             coverageFraction=0.0, disposition=None, resolved=False, changed=None,
                             servable=False, agreeingScales=None, stacked=None, kind='ADDITION'))
        for b in p['blocks']:
            blocks.append(dict(page=p['page'], regions=b['regions'],
                               supersessions=b['supersessions'], resolved=b['resolved'],
                               refused=b['refused'], eligible=b['eligible'],
                               beforeProposed=bool(b['before']['value']),
                               addProposed=bool(b['add']['value']),
                               supersedeProposed=bool(b['supersede']['value']),
                               beforeVerdict=b['before']['verdict'],
                               addVerdict=b['add']['verdict'],
                               supersedeVerdict=b['supersede']['verdict']))
    return dict(
        censusVersion=CENSUS_VERSION,
        supersessionVersion=doc['version'],
        source=dict(study=doc['study'], studySha256=doc['studySha256'], scales=doc['scales'],
                    book='04-sgk-toan-4-tap-hai', lesson='Bài 61', pages=[p['page'] for p in doc['pages']]),
        note=('D4: this file carries NO SGK text, readings, values or page geometry — only the '
              'structure of the supersession population. The readings live in poc-out/, which is '
              'gitignored, and the printed pages are never distributed.'),
        totals=dict(regions=len(rows),
                    supersessions=sum(1 for r in rows if r.get('kind') != 'ADDITION'),
                    additions=sum(1 for r in rows if r.get('kind') == 'ADDITION'),
                    resolved=sum(1 for r in rows if r['resolved']),
                    refused=sum(1 for r in rows if r.get('kind') != 'ADDITION' and not r['resolved']),
                    blocks=len(blocks)),
        regions=rows, blocks=blocks)


def write_census(doc, path, study_path):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    c = census(doc, study_path)
    with open(path, 'w') as fh:
        json.dump(c, fh, ensure_ascii=False, indent=1, sort_keys=False)
        fh.write('\n')
    return c


class ReproductionFailure(AssertionError):
    """The BEFORE or ADD column stopped reproducing round 7. A before -> after comparison whose
    «before» is not the published «before» compares nothing."""


def assert_add_column_reproduces_round7(doc, study):
    """The two columns this driver did NOT invent must come out identical to `study.py`'s.

    This is not ceremony. The first version of `_tokens_by_region` read `study.py`'s
    `bbox=[x, y, w, h]` as `(x0, y0, x1, y1)`; every token was still a token, every block still had
    a verdict, and the ADD column quietly dropped from 3 proposals to 2 — a number of the right type
    and the wrong quantity, which round 7 named as the failure no check but a re-derivation catches.
    So the re-derivation is the check.
    """
    old = {b['block_id']: b for p in study['pages'] for b in (p.get('blocks') or [])}
    new = {b['block_id']: b for p in doc['pages'] for b in p['blocks']}
    if not old:
        raise ReproductionFailure(
            'the study artefact carries no block projection, so there is nothing to reproduce '
            'against. ABSENCE CANNOT SATISFY A POSITIVE OBLIGATION: this check may not pass by '
            'having no subject.')
    if set(old) != set(new):
        raise ReproductionFailure(f'block sets differ: {len(old)} vs {len(new)}')
    bad = []
    for k, o in old.items():
        n = new[k]
        if o['before']['value'] != n['before']['value'] or o['before']['verdict'] != n['before']['verdict']:
            bad.append((k, 'before', o['before'], n['before']))
        if o['after']['value'] != n['add']['value'] or o['after']['verdict'] != n['add']['verdict']:
            bad.append((k, 'add', o['after'], n['add']))
    if bad:
        raise ReproductionFailure(f'{len(bad)} block(s) no longer reproduce round 7: {bad[:3]}')
    return len(old)


def summarise(doc):
    reg = [s for p in doc['pages'] for s in p['supersessions']]
    blocks = [b for p in doc['pages'] for b in p['blocks']]
    def proposed(key):
        return sum(1 for b in blocks if b[key]['value'])
    return dict(
        regions_recovered=sum(p['counts']['recovered'] for p in doc['pages']),
        supersessions=len(reg), additions=sum(p['counts']['additions'] for p in doc['pages']),
        resolved=sum(1 for s in reg if s['resolved']),
        refused=sum(1 for s in reg if not s['resolved']),
        superseded_observations=sum(len(s['superseded']) for s in reg if s['resolved']),
        conflicted_observations=sum(len(s['superseded']) for s in reg if not s['resolved']),
        blocks=len(blocks),
        blocks_proposed_before=proposed('before'), blocks_proposed_add=proposed('add'),
        blocks_proposed_supersede=proposed('supersede'),
        blocks_refused_by_contract=sum(1 for b in blocks if b['refused']),
        coverage=dict(FULL=sum(1 for s in reg if s['coverage'] == SUP.FULL),
                      PARTIAL=sum(1 for s in reg if s['coverage'] == SUP.PARTIAL)),
        by_failure_class={k: sum(1 for s in reg if s['failureClass'] == k)
                          for k in sorted({s['failureClass'] for s in reg})},
    )


if __name__ == '__main__':
    study_path = sys.argv[1] if len(sys.argv) > 1 else \
        f'{ROOT}/poc-out/round7/wal213/study-bai61-4scales.json'
    out = sys.argv[2] if len(sys.argv) > 2 else f'{ROOT}/poc-out/round7/wal213/supersede-bai61.json'
    doc = run(study_path, out_path=out)
    print(json.dumps(summarise(doc), ensure_ascii=False, indent=1))
    print('->', out)
    print('->', CENSUS_PATH)
