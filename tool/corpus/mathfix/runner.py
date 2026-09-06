#!/usr/bin/env python3
"""Run detect → extract → validate over real pages, and record every step.

This is the measurement harness, not a pipeline stage: it reads the SDM pages a run already
produced (read-only), works out what the math layer WOULD do to each withheld block, and writes
the whole ledger — original observations, candidate, every validator's verdict and evidence — to
`poc-out/round5/mathfix/`. Nothing is written back into any pipeline output.

Why a projection rather than an edit: `tool/corpus/tc2_sdm.py` belongs to Lane A1 in round 5, so
the repairer registers against A1's registry (see `plugin.py`) instead of editing the SDM. The
projection is what makes «coverage change on Toán» measurable before that wiring lands.
"""
import json
import os

from . import detect as D
from . import expression as X
from . import extract as E
from . import sci_notation as SN
from . import validate as V
from .inkmask import InkMask
from .tokens import load_tokens, median_height

ROOT = os.environ.get('TC_ROOT', '/Users/alexnguyen/projects/workizen-ai-learning-coach')
PDF_DIR = f'{ROOT}/poc-out/pdf'
OUT = f'{ROOT}/poc-out/round5/mathfix'

# The guards that say «this block carries arithmetic the pipeline would not vouch for». A block
# withheld for a reason OUTSIDE this set (furniture, figure_text, teacher_text, answer_leak…) is
# withheld for something this lane has no business overturning, and is never touched.
MATH_REASONS = frozenset({'math_guard', 'unit_guard', 'agree_text', 'agree_numbers', 'agree_order',
                          'low_ocr_conf'})


def pdf_path(book):
    p = f'{PDF_DIR}/{book[:2]}/{book}.pdf'
    return p if os.path.exists(p) else f'{PDF_DIR}/{book}.pdf'


def _inside(bbox, x, y, pad=0.0):
    bx, by, bw, bh = bbox
    return (bx - pad) <= x <= (bx + bw + pad) and (by - pad) <= y <= (by + bh + pad)


def page_report(book, page, sdm=None, dpi=300):
    """The full math-layer ledger for one page.

    `sdm` is a loaded SDM page dict, or None to report regions only (no block projection).
    """
    mask = InkMask.from_pdf(pdf_path(book), page, dpi=dpi)
    tokens = load_tokens(book, page)
    regions = D.find_fraction_regions(mask, tokens)
    mh = median_height(tokens) or 0.018

    out = dict(book=book, page=page, dpi=dpi, mask=[mask.width, mask.height],
               median_text_height=round(mh, 5),
               regions=[_region_row(r) for r in regions],
               token_kinds=_token_census(tokens),
               destroyed_exponents=[dict(text=t.text, bbox=[t.x, t.y, t.w, t.h],
                                         matched=f.matched, expected=f.expected_exponent)
                                    for t in tokens for f in SN.find_destroyed_exponents(t.text)],
               blocks=[])
    if not sdm:
        return out

    for blk in sdm.get('blocks') or []:
        bbox = blk.get('bbox')
        if not bbox:
            continue
        status = (blk.get('trust') or {}).get('status')
        reasons = list((blk.get('trust') or {}).get('reasons') or [])
        btoks = [t for t in tokens if _inside(bbox, t.cx, t.cy, pad=0.004)]
        bregs = [r for r in regions if _inside(bbox, r.bar.cx, r.bar.cy, pad=0.004)]
        if not bregs:
            continue                      # no printed fraction in this block: not this lane's
        row = dict(block_id=blk.get('id'), role=(blk.get('role') or {}).get('value'),
                   status=status, reasons=reasons,
                   original_text=blk.get('text'),
                   regions=len(bregs),
                   regions_extractable=sum(1 for r in bregs if r.extractable),
                   eligible=bool(status == 'WITHHELD' and reasons
                                 and set(reasons) <= MATH_REASONS))
        cand = E.math_line_candidate(btoks, bregs, mask)
        row['rule_id'] = cand.rule_id
        row['proposed_value'] = cand.proposed_value
        row['candidate_reason'] = cand.reason
        row['original_observations'] = cand.original_observations
        row['supporting_signals'] = cand.supporting_signals
        bar_len = sorted(r.bar.length for r in bregs)[len(bregs) // 2]
        bb = (bbox[0], bbox[1], bbox[0] + bbox[2], bbox[1] + bbox[3])
        verdict, results = V.validate(cand, mask, bb, median_height(btoks) or mh, bar_len)
        row['verdict'] = verdict
        row['validations'] = [dict(validator_id=r.validator_id, verdict=r.verdict,
                                   evidence=r.evidence) for r in results]
        row['disposition'] = ('VALIDATED REPAIR' if (verdict == 'RESTORE' and row['eligible'])
                              else 'WITHHELD')

        # The canonical object. A refused region still produces one — named, boxed, crop-bearing —
        # so a consumer knows a FORMULA was withheld here rather than reading «empty, no letters».
        # The AST is attached whenever the VALIDATORS confirmed it, even where the block's other
        # withhold reasons keep it out of service: whether a structure is sound and whether a block
        # is eligible to be served are two different questions, and conflating them would hide the
        # first behind the second.
        expr = X.MathExpression(
            source_block_id=blk.get('id'), book=book, page_pdf=page,
            page_printed=sdm.get('printed_page'), bbox=tuple(bbox),
            ast=(cand.ast if verdict == 'RESTORE' else None),
            observations=tuple(X.TokenGeometry(
                text=o.get('text', ''), bbox=tuple(o['bbox']),
                source=('apple-vision-ocr-line' if o['kind'] == 'ocr_line' else 'page-raster-300dpi'),
                index=o.get('index', -1), conf=o.get('conf', 1.0))
                for o in cand.original_observations),
            source_geometry=X.geometry_from_sdm_block(blk, btoks),
            original_text=blk.get('text'), rule_id=cand.rule_id,
            validations=tuple(row['validations']),
            provenance=dict(lane='A2', pipeline=sdm.get('pipeline'),
                            detector='mathfix.stacked-fraction-raster-v1'),
            disposition=(X.VALIDATED_REPAIR if row['disposition'] == 'VALIDATED REPAIR'
                         else X.WITHHELD),
            reasons=tuple([cand.reason] if cand.reason else
                          [r['validator_id'] for r in row['validations'] if r['verdict'] == 'FAIL']))
        row['math_expression'] = expr.to_json()
        out['blocks'].append(row)
    return out


def _region_row(r):
    return dict(kind=r.kind, extractable=r.extractable, reason=r.reason,
                bar=[round(r.bar.x0, 5), round(r.bar.y0, 5), round(r.bar.length, 5),
                     round(r.bar.thickness, 6)],
                bbox=[round(v, 5) for v in r.bbox],
                numerator=r.numerator.stripped if r.numerator else None,
                denominator=r.denominator.stripped if r.denominator else None,
                value=(f'{r.numerator.stripped}/{r.denominator.stripped}' if r.extractable else None))


def _token_census(tokens):
    out = {}
    for t in tokens:
        k = D.classify_token(t)
        if k:
            out[k] = out.get(k, 0) + 1
    return out


def write_report(report, out_dir=None):
    d = out_dir or OUT
    os.makedirs(d, exist_ok=True)
    p = f"{d}/{report['book']}-p{report['page']:03d}.json"
    with open(p, 'w') as fh:
        json.dump(report, fh, ensure_ascii=False, indent=1)
    return p
