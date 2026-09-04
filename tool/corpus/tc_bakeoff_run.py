#!/usr/bin/env python3
"""TC-v1 — PARSER BAKE-OFF runner: one page, one candidate, raw output + timing.

Every candidate is run on the SAME single-page PDF (cut from the source scan
with PyMuPDF, no re-encoding) or on the same 200-dpi render, and its native
output is saved untouched under
  poc-out/trusted-corpus/<ver>/bakeoff/raw/<candidate>/<book>-pNNN.json
together with wall-clock seconds. Normalisation to the Structured Document
Model happens later (tc_sdm.py) so that raw evidence is never lost.

Candidates (each needs its own interpreter — see the venv column):
  current-naive     Apple-Vision lines in the order the OCR file stores them
                    (top→bottom, left→right with 0.012 y-tolerance) — this is
                    the WAL-204 "generic extractor" order.        (system python3)
  current-xycut     tool/corpus/layout_extract.py (WAL-206).      (system python3)
  docling-ocrmac    Docling 2.x layout model (heron) + reading order, OCR via
                    ocrmac = Apple Vision (same OCR engine as current).
                                                                  (.venv-bakeoff)
  docling-rapidocr  Docling with its default RapidOCR engine.     (.venv-bakeoff)
  pymupdf4llm       PyMuPDF4LLM on the scanned page (expected: no text layer,
                    reports empty — recorded as a finding).       (.venv-bakeoff)
  marker            marker-pdf 2.x (Surya layout + OCR, force_ocr, lang vi).
                                                                  (.venv-bakeoff-marker)
  mineru            MinerU 3.x pipeline backend (DocLayout-YOLO + OCR).
                                                                  (.venv-bakeoff-mineru)
  vlm-mlx           A local VLM (mlx-vlm) asked to list blocks in reading order
                    with roles — used as "VLM-assisted parsing" AND as the
                    vision verifier candidate.                    (.venv-bakeoff-mlx)

Usage: <venv python> tool/corpus/tc_bakeoff_run.py <candidate> <book> <pdfPage> [--ver tc-v1]
"""
import argparse
import json
import os
import sys
import time

ROOT = os.environ.get('TC_ROOT', '/Users/alexnguyen/projects/workizen-ai-learning-coach')
PDF = f'{ROOT}/poc-out/pdf'
OCR = f'{ROOT}/poc-out/graph/ocr-body'


def pdf_path(book):
    p = f'{PDF}/{book[:2]}/{book}.pdf'
    if os.path.exists(p):
        return p
    p = f'{PDF}/{book}.pdf'
    return p if os.path.exists(p) else None


def page_pdf(book, page, ver):
    """Cut one page into its own PDF (no re-encoding of the scan)."""
    import fitz
    d = f'{ROOT}/poc-out/trusted-corpus/{ver}/pages'
    os.makedirs(d, exist_ok=True)
    out = f'{d}/{book}-p{page:03d}.pdf'
    if not os.path.exists(out):
        src = fitz.open(pdf_path(book))
        dst = fitz.open()
        dst.insert_pdf(src, from_page=page - 1, to_page=page - 1)
        dst.save(out)
        dst.close(); src.close()
    return out


def page_png(book, page, ver, dpi=200):
    import fitz
    d = f'{ROOT}/poc-out/trusted-corpus/{ver}/pages'
    os.makedirs(d, exist_ok=True)
    out = f'{d}/{book}-p{page:03d}-{dpi}.png'
    if not os.path.exists(out):
        doc = fitz.open(pdf_path(book))
        doc[page - 1].get_pixmap(dpi=dpi, colorspace=fitz.csRGB, alpha=False).save(out)
        doc.close()
    return out


# ---------------------------------------------------------------- candidates
def run_current_naive(book, page, ver):
    j = json.load(open(f'{OCR}/{book}/p{page:03d}.json'))
    return dict(lines=j['lines'], extraction_method=j.get('extraction_method'))


def run_current_xycut(book, page, ver):
    sys.path.insert(0, f'{ROOT}/tool/corpus')
    import layout_extract
    return layout_extract.extract_page(book, f'{OCR}/{book}/p{page:03d}.json')


def _docling(book, page, ver, engine):
    from docling.datamodel.base_models import InputFormat
    from docling.datamodel.pipeline_options import PdfPipelineOptions, OcrMacOptions, RapidOcrOptions
    from docling.document_converter import DocumentConverter, PdfFormatOption
    opts = PdfPipelineOptions()
    opts.do_ocr = True
    opts.do_table_structure = True
    opts.images_scale = 2.0
    if engine == 'ocrmac':
        opts.ocr_options = OcrMacOptions(lang=['vi-VT', 'en-US'], recognition='accurate', force_full_page_ocr=True)
    else:
        opts.ocr_options = RapidOcrOptions(force_full_page_ocr=True)
    conv = DocumentConverter(format_options={InputFormat.PDF: PdfFormatOption(pipeline_options=opts)})
    res = conv.convert(page_pdf(book, page, ver))
    doc = res.document
    return dict(docling=doc.export_to_dict(), markdown=doc.export_to_markdown(), status=str(res.status))


def run_docling_ocrmac(book, page, ver):
    return _docling(book, page, ver, 'ocrmac')


def run_docling_rapidocr(book, page, ver):
    return _docling(book, page, ver, 'rapidocr')


def run_pymupdf4llm(book, page, ver):
    import pymupdf4llm
    import fitz
    p = page_pdf(book, page, ver)
    md = pymupdf4llm.to_markdown(p, page_chunks=True)
    doc = fitz.open(p)
    words = doc[0].get_text('words')
    return dict(chunks=[dict(text=c.get('text', ''), meta={k: str(v) for k, v in c.get('metadata', {}).items()}) for c in md], native_words=len(words))


def run_marker(book, page, ver):
    from marker.converters.pdf import PdfConverter
    from marker.models import create_model_dict
    from marker.config.parser import ConfigParser
    from marker.output import text_from_rendered
    cfg = ConfigParser({'output_format': 'json', 'force_ocr': True, 'languages': 'vi,en', 'disable_image_extraction': True})
    conv = PdfConverter(config=cfg.generate_config_dict(), artifact_dict=create_model_dict(), processor_list=cfg.get_processors(), renderer=cfg.get_renderer())
    rendered = conv(page_pdf(book, page, ver))
    js = json.loads(rendered.model_dump_json())
    return dict(marker=js)


def run_mineru(book, page, ver):
    import subprocess, tempfile, glob
    p = page_pdf(book, page, ver)
    out = tempfile.mkdtemp(prefix='mineru-')
    exe = os.path.join(os.path.dirname(sys.executable), 'mineru')
    lang = os.environ.get('MINERU_LANG', 'latin')
    cmd = [exe, '-p', p, '-o', out, '-b', 'pipeline', '-m', 'ocr', '-l', lang, '-d', os.environ.get('MINERU_DEVICE', 'cpu'), '-f', 'false', '-t', 'false']
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=1800)
    res = dict(cmd=' '.join(cmd), rc=r.returncode, stderr=r.stderr[-3000:], files=[])
    for f in glob.glob(f'{out}/**/*', recursive=True):
        if f.endswith('_middle.json'):
            res['middle'] = json.load(open(f))
        elif f.endswith('_content_list.json'):
            res['content_list'] = json.load(open(f))
        elif f.endswith('.md'):
            res['markdown'] = open(f).read()
        res['files'].append(os.path.relpath(f, out))
    return res


VLM_PROMPT = (
    'Bạn là bộ phân tích bố cục trang sách giáo khoa Việt Nam. Hãy liệt kê MỌI khối văn bản trên trang theo đúng THỨ TỰ ĐỌC của một học sinh, '
    'mỗi khối một dòng theo định dạng: ROLE | x,y,w,h | TEXT. ROLE thuộc {heading, body, question, caption, sidebar, table, figure_label, footnote, page_number, objective}. '
    'x,y,w,h là toạ độ tương đối 0–1 của khối (góc trên-trái, rộng, cao). TEXT là nguyên văn (giữ dấu tiếng Việt). Không bịa, không tóm tắt, không dịch.'
)


def run_vlm_mlx(book, page, ver):
    from mlx_vlm import load, generate
    from mlx_vlm.prompt_utils import apply_chat_template
    from mlx_vlm.utils import load_config
    model_id = os.environ.get('VLM_MODEL', 'mlx-community/Qwen2.5-VL-3B-Instruct-4bit')
    model, processor = load(model_id)
    config = load_config(model_id)
    img = page_png(book, page, ver, dpi=int(os.environ.get('VLM_DPI', '120')))
    prompt = apply_chat_template(processor, config, VLM_PROMPT, num_images=1)
    out = generate(model, processor, prompt, [img], max_tokens=int(os.environ.get('VLM_MAX_TOKENS', '3000')), temperature=0.0, verbose=False)
    text = out.text if hasattr(out, 'text') else str(out)
    return dict(model=model_id, image=img, text=text)


CANDIDATES = {
    'current-naive': run_current_naive, 'current-xycut': run_current_xycut,
    'docling-ocrmac': run_docling_ocrmac, 'docling-rapidocr': run_docling_rapidocr,
    'pymupdf4llm': run_pymupdf4llm, 'marker': run_marker, 'mineru': run_mineru, 'vlm-mlx': run_vlm_mlx,
}


def run_one(candidate, book, page, ver, force=False):
    d = f'{ROOT}/poc-out/trusted-corpus/{ver}/bakeoff/raw/{candidate}'
    os.makedirs(d, exist_ok=True)
    out = f'{d}/{book}-p{page:03d}.json'
    if os.path.exists(out) and not force:
        print('exists', out, flush=True); return
    t0 = time.time()
    try:
        res = CANDIDATES[candidate](book, page, ver)
        err = None
    except Exception:
        import traceback
        res = None; err = traceback.format_exc()[-4000:]
    dt = time.time() - t0
    json.dump(dict(candidate=candidate, book=book, page=page, seconds=round(dt, 2), python=sys.executable, error=err, result=res),
              open(out, 'w'), ensure_ascii=False, default=str)
    print(f'{candidate} {book} p{page:03d} {dt:.1f}s {"ERROR" if err else "ok"}', flush=True)
    if err:
        print(err[-1500:], flush=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('candidate'); ap.add_argument('book', nargs='?'); ap.add_argument('page', nargs='?', type=int)
    ap.add_argument('--ver', default='tc-v1'); ap.add_argument('--force', action='store_true')
    ap.add_argument('--batch', default=None, help='JSON file [{book,page}] — run all pages in ONE process (models loaded once; per-page seconds exclude model load after the first page)')
    a = ap.parse_args()
    if a.batch:
        pages = json.load(open(a.batch))
        for p in pages:
            run_one(a.candidate, p['book'], int(p['page']), a.ver, a.force)
        return
    run_one(a.candidate, a.book, a.page, a.ver, a.force)


if __name__ == '__main__':
    main()
