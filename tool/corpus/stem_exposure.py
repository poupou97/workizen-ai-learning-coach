#!/usr/bin/env python3
"""WAL-239 — TRẺ ĐANG THẤY GÌ Ở ĐÚNG CHỖ SÁCH IN CÔNG THỨC.

    python3 tool/corpus/stem_exposure.py [--kind formula|code]

⭐ ĐO TỪ NGUỒN, KHÔNG ĐO HÌNH DẠNG CHỮ. Vòng trước đã bác bỏ mọi tín hiệu dựa
trên dáng vẻ ký tự (xem `stem_audit.py`). Ở đây vị trí công thức đến TỪ BỐ CỤC
TRANG — Docling khoanh 4.885 vùng `formula` và phiên âm ĐÚNG 0% trong số đó:
nó biết công thức nằm ở đâu, không đọc nội dung. Đó chính là điều làm phép đo
này dùng được: vùng là bằng chứng nguồn độc lập với chữ mà OCR sinh ra.

Câu hỏi: ở đúng toạ độ ấy, dòng đọc của trẻ đang hiện ra cái gì?

    KHÔNG CÓ CHỮ NÀO   vùng công thức không sinh chữ ⇒ trẻ mất nội dung, nhưng
                       KHÔNG bị đọc nội dung sai
    CÓ CHỮ             trẻ đang đọc một bản phiên âm — đúng hay sai thì chỉ
                       SOI MẮT so với bản in mới biết. Module này KHÔNG kết luận.

⚠ Vùng `formula` là ĐỀ XUẤT bố cục, chưa phải sự thật: một phần trong 4.885 có
thể không phải công thức. Vì thế bước sau là mẫu đóng băng + soi mắt, không
phải nhân con số này lên.
"""
import argparse
import collections
import json
import glob
import os
import sys
import warnings

warnings.filterwarnings('ignore')
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
from lesson_reading import page_paragraphs  # noqa: E402

OCR = os.path.join(ROOT, 'poc-out/graph/ocr-body')
SUBJ = [('toan', 'Toán'), ('vat-li', 'Vật lí'), ('hoa-hoc', 'Hoá học'),
        ('tin-hoc', 'Tin học'), ('khoa-hoc-tu-nhien', 'KHTN'),
        ('sinh-hoc', 'Sinh học'), ('cong-nghe', 'Công nghệ')]
INSIDE = 0.60      # đoạn văn nằm trong vùng chừng này thì coi là CỦA vùng ấy


def subject(book):
    s = book.split('-', 2)[-1]
    for k, n in SUBJ:
        if k in s:
            return n
    return 'môn khác'


def regions(kind):
    out = collections.defaultdict(list)
    for p in glob.glob(os.path.join(ROOT, 'poc-out/docling/proposals-w*.jsonl')):
        with open(p, encoding='utf-8') as fh:
            for line in fh:
                r = json.loads(line)
                for it in r.get('items') or []:
                    if it['label'] == kind:
                        out[(r['book'], r['page'])].append(it['box'])
    return out


def lines_of(book, page):
    try:
        with open(f'{OCR}/{book}/p{page:03d}.json', encoding='utf-8') as fh:
            return json.load(fh)['lines']
    except (OSError, ValueError, KeyError):
        return []


def _frac(inner, outer):
    """Phần diện tích của `inner` nằm trong `outer` — mẫu số là CHÍNH `inner`."""
    ix = min(inner[0] + inner[2], outer[0] + outer[2]) - max(inner[0], outer[0])
    iy = min(inner[1] + inner[3], outer[1] + outer[3]) - max(inner[1], outer[1])
    if ix <= 0 or iy <= 0:
        return 0.0
    return (ix * iy) / max(inner[2] * inner[3], 1e-9)


def wh(box):
    """`page_paragraphs` trả GÓC `[x0,y0,x1,y1]`; vùng Docling là `[x,y,w,h]`."""
    return [box[0], box[1], box[2] - box[0], box[3] - box[1]]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--kind', default='formula', choices=('formula', 'code'))
    ap.add_argument('--out', default=None)
    a = ap.parse_args()
    reg = regions(a.kind)
    st = collections.Counter()
    bysub = collections.defaultdict(collections.Counter)
    rows = []
    pages = sorted(reg)
    for i, (book, page) in enumerate(pages):
        if i % 400 == 0:
            print(f'  {i}/{len(pages)} trang…', flush=True)
        lines = lines_of(book, page)
        paras = page_paragraphs(lines) if lines else []
        s = subject(book)
        for box in reg[(book, page)]:
            hit = [p for p in paras if _frac(wh(p['box']), box) >= INSIDE]
            st['VUNG'] += 1
            bysub[s]['VUNG'] += 1
            if not lines:
                st['KHONG_CO_DU_LIEU_DONG'] += 1
                bysub[s]['KHONG_CO_DU_LIEU_DONG'] += 1
            elif hit:
                st['CO_CHU'] += 1
                bysub[s]['CO_CHU'] += 1
                rows.append(dict(book=book, page=page, box=box, subject=s,
                                 text=' ⏎ '.join(p['text'] for p in hit)[:400]))
            else:
                st['KHONG_CO_CHU'] += 1
                bysub[s]['KHONG_CO_CHU'] += 1
    n = st['VUNG']
    print(f'\n=== VÙNG «{a.kind}» = {n} ===')
    for k in ('CO_CHU', 'KHONG_CO_CHU', 'KHONG_CO_DU_LIEU_DONG'):
        print(f'  {k:24s} {st[k]:5d}  {st[k] / n:6.1%}')
    print('\ntheo môn:')
    for s, c in sorted(bysub.items(), key=lambda kv: -kv[1]['VUNG']):
        v = c['VUNG']
        print(f'  {s:12s} vùng {v:5d} · trẻ đang đọc chữ ở đó {c["CO_CHU"]:5d} = {c["CO_CHU"] / v:6.1%}')
    out = a.out or os.path.join(ROOT, f'poc-out/docling/stem-exposure-{a.kind}.json')
    json.dump(rows, open(out, 'w'), ensure_ascii=False)
    print(f'\n{len(rows)} vùng CÓ CHỮ → {out}')
    print('⚠ CÓ CHỮ chưa nghĩa là SAI. Đúng hay sai phải soi mắt so với bản in.')
    return 0


if __name__ == '__main__':
    sys.exit(main())
