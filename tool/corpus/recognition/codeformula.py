#!/usr/bin/env python3
"""Docling's formula enrichment, measured head to head on the same crops — bounded, and honest.

Why this file exists: round 5 recorded that `do_formula_enrichment` exists in the installed
Docling and is never set (`tool/corpus/tc_bakeoff_run.py:94-101`), and named it «the cheapest new
candidate». That is a claim about a thing nobody had run. This runs it, on the same printed
regions the crop recogniser is measured on, and reports what it costs and what it reads.

What was checked before running anything:

  · `docling.datamodel.pipeline_options.PdfPipelineOptions` carries `do_formula_enrichment`,
    default **False**, and `code_formula_options` pointing at `docling-project/CodeFormulaV2`
    with `scale=2.0`. Docling 2.126.0, already a dependency of this repo.
  · **Licence: CDLA-Permissive-2.0** (from the model card), 0.64 GB of weights. Permissive, and
    not the GPL-3 that disqualified Marker/Surya. It is still a *new model dependency* and a
    Founder decision, which is why this file measures it rather than adopting it.
  · The trust hole round 5 warned about is CLOSED on this base: `tc2_sdm.role_guards` now emits
    `formula_unvalidated` for a `formula`-role block that does not carry `formula_structured`,
    so enabling enrichment can no longer mint a trusted formula from a label alone.

And the rule that governs the result whatever it is: **CodeFormulaV2 is a VLM.** Its output is a
`RepairCandidate` and never a source of truth — `LLM OUTPUT != TRUTH`. It may only ever be
accepted through the same deterministic validators as any other candidate.
"""
import json
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

ROOT = os.environ.get('TC_ROOT', '/Users/alexnguyen/projects/workizen-ai-learning-coach')
OUT = f'{ROOT}/poc-out/round6/recognition'
REPO = 'docling-project/CodeFormulaV2'
PROMPT = '<formula>'          # docling's own prompt for a formula region


def load_model(device=None):
    import torch
    from transformers import AutoModelForImageTextToText, AutoProcessor
    dev = device or ('mps' if torch.backends.mps.is_available() else 'cpu')
    proc = AutoProcessor.from_pretrained(REPO)
    model = AutoModelForImageTextToText.from_pretrained(REPO, dtype=torch.float32).to(dev).eval()
    return proc, model, dev


def read_crop(proc, model, dev, image, max_new_tokens=96):
    import torch
    msgs = [{'role': 'user', 'content': [{'type': 'image'}, {'type': 'text', 'text': PROMPT}]}]
    text = proc.apply_chat_template(msgs, add_generation_prompt=True)
    inputs = proc(text=text, images=[image], return_tensors='pt').to(dev)
    with torch.no_grad():
        out = model.generate(**inputs, max_new_tokens=max_new_tokens, do_sample=False)
    got = proc.batch_decode(out[:, inputs['input_ids'].shape[1]:], skip_special_tokens=False)[0]
    for junk in ('</formula>', '<end_of_utterance>', '<loc_0><loc_0><loc_500><loc_500>', '</s>'):
        got = got.replace(junk, '')
    return got.strip()


LATEX_FRAC = None


def latex_to_fraction(s):
    """`\\frac{3}{10}` -> `3/10`, and nothing else. A reading this cannot reduce to a bare printed
    fraction is reported as-is and counted as «not comparable», never massaged into agreement."""
    import re
    global LATEX_FRAC
    if LATEX_FRAC is None:
        LATEX_FRAC = re.compile(r'^\s*\\d?frac\s*\{\s*(\d{1,4})\s*\}\s*\{\s*(\d{1,4})\s*\}\s*$')
    m = LATEX_FRAC.match((s or '').replace('\\dfrac', '\\frac'))
    return f'{m.group(1)}/{m.group(2)}' if m else None


def run(pages, truth, scale=6.0, out_name='codeformula'):
    """`pages` are `(book, page)`; `truth` maps a region key to the hand-verified printed value."""
    import pymupdf
    from PIL import Image
    from mathfix import detect as D
    from mathfix.inkmask import InkMask
    from mathfix.tokens import load_tokens, median_height
    from recognition import boxes as B
    from recognition import vision as V

    proc, model, dev = load_model()
    rows, t_model = [], 0.0
    for book, page in pages:
        mask = InkMask.from_pdf(V.pdf_path(book), page, dpi=300)
        tokens = load_tokens(book, page)
        regions = D.find_fraction_regions(mask, tokens)
        mh = median_height(tokens) or 0.018
        doc = pymupdf.open(V.pdf_path(book))
        pg = doc[page - 1]
        W, H = pg.rect.width, pg.rect.height
        for i, r in enumerate(regions):
            key = f'{book}:p{page:03d}:r{i:03d}'
            box = B.fraction_boxes([r.bar.x0, r.bar.y0, r.bar.length, r.bar.thickness], mh)[2]
            pix = pg.get_pixmap(dpi=int(72 * scale),
                                clip=pymupdf.Rect(box.x0 * W, box.y0 * H, box.x1 * W, box.y1 * H))
            img = Image.frombytes('RGB', (pix.width, pix.height), pix.samples)
            t0 = time.time()
            raw = read_crop(proc, model, dev, img)
            t_model += time.time() - t0
            rows.append(dict(key=key, raw=raw, reduced=latex_to_fraction(raw),
                             truth=truth.get(key),
                             baseline=(f'{r.numerator.stripped}/{r.denominator.stripped}'
                                       if r.extractable else None)))
            print(f'{key[-4:]} {time.time()-t0:5.1f}s  {raw[:60]!r}  truth={truth.get(key)}',
                  flush=True)
    payload = dict(model=REPO, device=dev, scale=scale, seconds_in_model=round(t_model, 1),
                   regions=len(rows), rows=rows)
    os.makedirs(OUT, exist_ok=True)
    path = f'{OUT}/{out_name}.json'
    with open(path, 'w') as fh:
        json.dump(payload, fh, ensure_ascii=False, indent=1)
    print('->', path)
    return path


#: exactly which tiles a human read, and which population on each. Nothing outside this set is
#: scored, because a truth set assembled from the pipeline's own output is not a truth set.
VERIFIED = {
    ('05-sgk-toan-5-tap-mot', 22): ('control', 'recovery'),   # both contact sheets read tile by tile
    ('04-sgk-toan-4-tap-hai', 83): ('recovery',),             # Bài 61: the recovered sheet was read
}


def truth_from_study(study_path, verified=None):
    """Hand-verified values only — a region enters the truth set when a human read its tile.

    For a CONTROL region the printed value is the baseline the whole-page OCR read AND the contact
    sheet confirmed. That second half is not a formality: on Toán 5 tập một p23 the baseline reads
    `4/5` where the page prints `14/5`, so a truth set taken from the baseline alone would have
    scored a correct reading as an error.
    """
    verified = verified or VERIFIED
    with open(study_path) as fh:
        doc = json.load(fh)
    out = {}
    for p in doc['pages']:
        pops = verified.get((p['book'], p['page']))
        if not pops:
            continue
        for r in p['regions']:
            if r['population'] not in pops:
                continue
            v = r['baseline_value'] if r['population'] == 'control' else r['value']
            if v:
                out[r['key']] = v
    return out


if __name__ == '__main__':
    run(sorted(VERIFIED), truth_from_study(f'{OUT}/study-dev.json'))
