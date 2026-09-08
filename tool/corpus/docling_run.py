#!/usr/bin/env python3
"""B3 — CHẠY TRI GIÁC DOCLING TRÊN CORPUS, GHI VÀO KHU TẠM.

    python3 tool/corpus/docling_run.py --pages b3-pages.json --workers 6

⭐ TÁCH ĐẮT KHỎI RẺ. Docling là bước ĐẮT (~2 s/trang, 16.800 trang). Cổng tin
cậy là bước RẺ. Nên ở đây CHỈ ghi lại ĐỀ XUẤT THÔ; cổng chạy ở bước sau, đọc
lại từ khu tạm. Sửa luật cổng KHÔNG phải chạy lại tri giác.

⭐ GHI THÊM, KHÔNG GHI ĐÈ. Mỗi worker ghi JSONL riêng, mỗi trang một dòng, đẩy
đĩa ngay. Máy sập giữa chừng thì phần đã chạy vẫn còn; chạy lại bỏ qua trang đã
có. KHÔNG có bước nào ở đây đụng vào `assets/pack` hay dữ liệu canonical.
"""
import argparse
import json
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
OUT = os.path.join(ROOT, 'poc-out', 'docling')


def shard_path(k):
    return os.path.join(OUT, f'proposals-w{k}.jsonl')


def done_keys():
    """Trang đã có đề xuất — để chạy lại không làm lại từ đầu."""
    seen = set()
    if not os.path.isdir(OUT):
        return seen
    for fn in sorted(os.listdir(OUT)):
        if not (fn.startswith('proposals-w') and fn.endswith('.jsonl')):
            continue
        with open(os.path.join(OUT, fn), encoding='utf-8') as fh:
            for line in fh:
                try:
                    d = json.loads(line)
                except ValueError:
                    continue              # dòng cụt do sập giữa chừng
                seen.add((d['book'], d['page']))
    return seen


def run_shard(args):
    k, pages, pdfs = args
    import fitz
    from docling.document_converter import DocumentConverter
    conv = DocumentConverter()
    tmp = os.path.join(OUT, f'.page-w{k}.pdf')
    n = 0
    with open(shard_path(k), 'a', encoding='utf-8') as fh:
        for book, pp in pages:
            t0 = time.time()
            try:
                src = fitz.open(pdfs[book])
                if not (1 <= pp <= src.page_count):
                    src.close()
                    continue
                r = src[pp - 1].rect
                W, H = r.width, r.height
                one = fitz.open()
                one.insert_pdf(src, from_page=pp - 1, to_page=pp - 1)
                one.save(tmp)
                one.close()
                src.close()
                d = conv.convert(tmp).document
                items = []
                for it, _ in d.iterate_items():
                    prov = getattr(it, 'prov', None)
                    if not prov:
                        continue
                    bb = prov[0].bbox
                    items.append(dict(
                        label=str(getattr(it, 'label', None)),
                        box=[round(min(bb.l, bb.r) / W, 4), round(1 - max(bb.t, bb.b) / H, 4),
                             round(max(bb.l, bb.r) / W, 4), round(1 - min(bb.t, bb.b) / H, 4)],
                        text=(getattr(it, 'text', '') or '')[:60]))
                rec = dict(book=book, page=pp, items=items,
                           secs=round(time.time() - t0, 2))
            except Exception as e:                       # noqa: BLE001
                # ⚠ MỘT TRANG HỎNG KHÔNG ĐƯỢC GIẾT CẢ MẺ. Ghi lại lỗi để đếm
                # được, rồi đi tiếp — đây là bước tri giác, không phải bước
                # ghi dữ liệu thật.
                rec = dict(book=book, page=pp, items=[], error=str(e)[:200],
                           secs=round(time.time() - t0, 2))
            fh.write(json.dumps(rec, ensure_ascii=False) + '\n')
            fh.flush()
            n += 1
    return k, n


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--pages', required=True, help='JSON: [[book, page], ...]')
    ap.add_argument('--workers', type=int, default=6)
    ap.add_argument('--limit', type=int, default=0)
    a = ap.parse_args()

    os.makedirs(OUT, exist_ok=True)
    with open(a.pages, encoding='utf-8') as fh:
        want = [(b, int(p)) for b, p in json.load(fh)]
    reg = json.load(open(os.path.join(ROOT, 'poc-out', 'registry',
                                      'source-registry.json'), encoding='utf-8'))
    docs = reg['documents'] if isinstance(reg, dict) else reg
    pdfs = {d['sourceDocumentId']: os.path.join(ROOT, d['path']) for d in docs
            if d.get('path')}

    have = done_keys()
    todo = [k for k in want if k not in have and k[0] in pdfs]
    if a.limit:
        todo = todo[:a.limit]
    print(f'cần {len(want)} · đã có {len(have)} · còn {len(todo)}', flush=True)
    if not todo:
        return 0

    shards = [todo[i::a.workers] for i in range(a.workers)]
    import multiprocessing as mp
    t0 = time.time()
    with mp.Pool(a.workers) as pool:
        for k, n in pool.imap_unordered(run_shard,
                                        [(i, s, pdfs) for i, s in enumerate(shards)]):
            print(f'  worker {k}: {n} trang', flush=True)
    dt = time.time() - t0
    print(f'xong {len(todo)} trang trong {dt/60:.1f} phút '
          f'({dt/max(len(todo),1):.2f} s/trang hiệu dụng)')
    return 0


if __name__ == '__main__':
    sys.exit(main())
