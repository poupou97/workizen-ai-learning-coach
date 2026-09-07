#!/usr/bin/env python3
"""Dựng HÌNH của bài vào pack theo lớp + dòng nội dung xen kẽ chữ–hình.

    python3 tool/ui/build_lesson_figures.py <grade> [--limit N]

Founder dogfood #140: bài mở được nhưng CHỈ CÓ CHỮ. Đo lại đường hình thì mất
ngay ở tầng dò — chỉ 12/238 sách có dữ liệu hình (Docling), pack có 0.

Ở đây dò tất định từ chính trang sách (`lesson_figures`), cắt, và ghi:

  · `assets/pack/figures-g<N>.db`  — SQLite, một bảng ảnh JPEG (blob)
  · `lessonReadings[].content`     — DÒNG NỘI DUNG có thứ tự: chữ, hình, chữ…

⭐ HÌNH ĐỨNG ĐÚNG CHỖ NÓ THUỘC VỀ. Gom hết xuống cuối bài thì trẻ đọc xong mới
thấy hình và không biết hình nào nói về đoạn nào. Ở đây hình được chèn theo
TOẠ ĐỘ Y THẬT của nó giữa các khối chữ cùng trang.

⭐ MỘT DB MỖI LỚP. Đo được ~4,4 hình/bài, ~33 KB/hình ⇒ ~31 MB một lớp nhưng
~367 MB cả 12 lớp. App chỉ dùng lớp của trẻ, nên tách theo lớp là đúng hình
dạng bài toán chứ không phải mẹo tiết kiệm.
"""
import argparse
import json
import os
import sqlite3
import sys
import warnings

warnings.filterwarnings('ignore')
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, 'tool', 'corpus'))
from lesson_figures import lesson_figures, crop_jpeg  # noqa: E402
from lesson_reading import lesson_reading  # noqa: E402

OCR = os.path.join(ROOT, 'poc-out/graph/ocr-body')


def pdf_map():
    import glob
    m = {}
    for p in glob.glob(os.path.join(ROOT, 'poc-out/pdf/*/*.pdf')):
        m[os.path.basename(p)[:-4]] = p
    for p in glob.glob(os.path.join(ROOT, 'poc-out/pdf/*.pdf')):
        m.setdefault(os.path.basename(p)[:-4], p)
    return m


def lines_for(book, pages):
    out = {}
    for pp in pages:
        try:
            with open(f'{OCR}/{book}/p{pp:03d}.json', encoding='utf-8') as fh:
                out[pp] = json.load(fh)['lines']
        except (OSError, ValueError, KeyError):
            pass
    return out


def interleave(pages, figs_by_page):
    """Dòng nội dung: mỗi trang đọc theo khối, hình chèn vào đúng y của nó."""
    stream = []
    for p in pages:
        items = [(q['y'], dict(t='text', v=q['text'])) for q in p.get('paragraphs') or []]
        for f in figs_by_page.get(p['pagePdf'], []):
            items.append((f['bbox'][1], dict(t='img', id=f['id'], w=f['w'], h=f['h'],
                                             page=f['page'], caption=f['caption'])))
        for _, it in sorted(items, key=lambda z: z[0]):
            if it['t'] == 'text' and stream and stream[-1]['t'] == 'text':
                stream[-1]['v'] += ' ' + it['v']      # khối liền nhau, không có hình xen
            else:
                stream.append(it)
    return stream


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('grade', type=int)
    ap.add_argument('--limit', type=int, default=0)
    a = ap.parse_args()

    idx_path = os.path.join(ROOT, f'assets/pack/lesson-index-g{a.grade}.json')
    idx = json.load(open(idx_path, encoding='utf-8'))
    readings = idx.get('lessonReadings') or []
    if a.limit:
        readings = readings[:a.limit]
    pdfs = pdf_map()

    db_path = os.path.join(ROOT, f'assets/pack/figures-g{a.grade}.db')
    if os.path.exists(db_path):
        os.remove(db_path)
    db = sqlite3.connect(db_path)
    db.execute('CREATE TABLE fig (id TEXT PRIMARY KEY, book TEXT, lesson INT, '
               'page INT, w INT, h INT, jpeg BLOB)')

    n_fig = n_les = n_cap = 0
    for r in readings:
        pdf = pdfs.get(r['book'])
        if not pdf:
            continue
        pages = range(r['pagePdfStart'], r['pagePdfEnd'] + 1)
        lb = lines_for(r['book'], pages)
        figs = lesson_figures(pdf, r['book'], pages, lb)
        by_page = {}
        for f in figs:
            try:
                jpeg, (w, h) = crop_jpeg(pdf, f['page'], f['bbox'])
            except Exception as e:            # trang hỏng / PDF lỗi ⇒ bỏ hình, giữ chữ
                print(f"  ! {f['id']}: {e}", file=sys.stderr)
                continue
            db.execute('INSERT OR REPLACE INTO fig VALUES (?,?,?,?,?,?,?)',
                       (f['id'], f['book'], r['lesson'], f['page'], w, h, jpeg))
            by_page.setdefault(f['page'], []).append(
                dict(id=f['id'], bbox=f['bbox'], w=w, h=h, page=f['page'],
                     caption=f['caption']))
            n_fig += 1
            n_cap += bool(f['caption'])
        # dựng lại dòng đọc để có khối + y (pack chỉ giữ chuỗi chữ phẳng)
        doc, _ = lesson_reading(r['book'], r['pagePdfStart'], r['pagePdfEnd'],
                                printed_start=r.get('pageStart'), title=r.get('title'))
        if not doc:
            continue
        r['content'] = interleave(doc['pages'], by_page)
        if by_page:
            n_les += 1
    db.commit()
    db.close()
    json.dump(idx, open(idx_path, 'w'), ensure_ascii=False)
    size = os.path.getsize(db_path) / 1048576
    print(f'lớp {a.grade}: {n_fig} hình ({n_cap} có chú thích của sách) trong '
          f'{n_les}/{len(readings)} bài · figures-g{a.grade}.db {size:.0f} MB')


if __name__ == '__main__':
    sys.exit(main())
