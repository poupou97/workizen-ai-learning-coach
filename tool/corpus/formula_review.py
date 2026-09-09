#!/usr/bin/env python3
"""WAL-239 — MẪU ĐỐI CHIẾU BỐN BÊN cho `FormulaSourceBlock`.

    python3 tool/corpus/formula_review.py --n 60 --seed 20260916 \
        --stage /private/tmp/wal-stage-formula

Founder Gate: soi bốn thứ cạnh nhau —

    BẢN IN NGUỒN · OCR HIỆN TẠI · KHỐI CÔNG THỨC · ĐẦU RA ĐƯỢC CHỌN

Mẫu ĐÓNG BĂNG trước khi soi: `sample.json` ghi xong mới dựng ảnh.

Phân tầng theo Founder: Toán · Vật lí · Hoá học · và nơi khác có ký hiệu, kèm
các họ ký hiệu (phân số · luỹ thừa · căn · chỉ số · chữ Hy Lạp · vectơ ·
phương trình · bất phương trình · biểu thức hình học · đơn vị · ký hiệu khoa
học · ion/công thức hoá học) — họ nhận bằng CHÍNH CHỮ OCR ở đó, không đoán.

Phân loại (Founder chốt):

    SOURCE_FAITHFUL      khối hiện đúng công thức in, trọn vẹn
    TRUNCATED            cắt mất tử/mẫu/căn/mũ/chỉ số/dấu/nhãn
    PROSE_CONTAMINATED   khung ôm cả văn xuôi không thuộc công thức
    SYMBOL_MISSING       thiếu ký hiệu so với bản in
    WRONG_REGION         khung chỉ vào chỗ khác, không phải công thức ấy
    ORDER_WRONG          khối đứng sai chỗ trong dòng đọc
    AMBIGUOUS            không kết luận được. `UNKNOWN != VALID`.
"""
import argparse
import collections
import json
import os
import random
import re
import sys
import textwrap

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))

VERDICTS = ('SOURCE_FAITHFUL', 'TRUNCATED', 'PROSE_CONTAMINATED', 'SYMBOL_MISSING',
            'WRONG_REGION', 'ORDER_WRONG', 'AMBIGUOUS')

#: Họ ký hiệu — nhận bằng chính chữ OCR nằm trong vùng. Đây là PHÂN TẦNG lấy
#: mẫu, KHÔNG phải kết luận về nội dung.
FAMILIES = (
    ('phan_so', re.compile(r'[/⁄]|\bfrac\b')),
    ('luy_thua', re.compile(r'[\^²³⁴⁵⁶⁰¹]|\*\*')),
    ('can', re.compile(r'[√∛]|\bsqrt\b|\bV\d')),
    ('chi_so', re.compile(r'[₀₁₂₃₄₅₆₇₈₉]|[A-Za-z]\d(?![\d.])')),
    ('hy_lap', re.compile(r'[αβγδεθλμπρστφωΩΔΣΦΨ∆]')),
    ('vecto', re.compile(r'[→⃗]|\bvec\b')),
    ('phuong_trinh', re.compile(r'=')),
    ('bat_phuong_trinh', re.compile(r'[<>≤≥≠]')),
    ('hoa_hoc', re.compile(r'\b(?:[A-Z][a-z]?\d+){1,}|[⁺⁻]|\bmol\b')),
    ('khoa_hoc', re.compile(r'10[\^\-−]|·10|\.10')),
    ('don_vi', re.compile(r'\b(?:cm|mm|km|kg|mol|eV|Hz|N/m|m/s)\b')),
)


def families(text):
    t = text or ''
    got = [n for n, rx in FAMILIES if rx.search(t)]
    return got or ['khong_ro']


def pdf_path(book):
    for p in (f'{ROOT}/poc-out/pdf/{book[:2]}/{book}.pdf',
              f'{ROOT}/poc-out/pdf/{book}.pdf'):
        if os.path.exists(p):
            return p
    return None


from subject import subject  # noqa: E402  (khớp theo ĐOẠN, xem module)


def frame(stage):
    """Mọi `FormulaSourceBlock` ĐÃ VÀO dòng đọc của khu dàn dựng, kèm chữ OCR
    mà nó đã bỏ đi — lấy từ pack CANONICAL đang phục vụ để so «trước/sau»."""
    import glob
    sys.path.insert(0, HERE)
    import formula_source as fs
    from lesson_reading import page_paragraphs
    OCR = os.path.join(ROOT, 'poc-out/graph/ocr-body')
    regs = fs.regions_index()
    rows = []
    for p in sorted(glob.glob(os.path.join(stage, 'lesson-index-g*.json'))):
        with open(p, encoding='utf-8') as fh:
            idx = json.load(fh)
        for r in idx.get('lessonReadings') or []:
            content = r.get('content') or []
            for i, e in enumerate(content):
                if not (isinstance(e, dict) and e.get('t') == 'formula'):
                    continue
                pg = e['page']
                try:
                    with open(f'{OCR}/{r["book"]}/p{pg:03d}.json', encoding='utf-8') as f2:
                        lines = json.load(f2)['lines']
                except (OSError, ValueError, KeyError):
                    lines = []
                box = e['src']['region']
                dropped = [q['text'] for q in page_paragraphs(lines)
                           if fs.owned_by_formula(q, [box])]
                before = next((c['v'] for c in reversed(content[:i])
                               if c.get('t') in ('text', 'heading')), '')
                after = next((c['v'] for c in content[i + 1:]
                              if c.get('t') in ('text', 'heading')), '')
                rows.append(dict(id=e['id'], book=r['book'], lesson=r.get('lesson'),
                                 page=pg, box=box, ident=e.get('ident'),
                                 subject=subject(r['book']),
                                 ocr=' ⏎ '.join(dropped)[:340],
                                 fam=families(' '.join(dropped)),
                                 before=(before or '')[-110:],
                                 after=(after or '')[:110]))
    return rows


def draw(rows, n, seed, per_book=4):
    rng = random.Random(seed)
    st = collections.defaultdict(list)
    for i, r in enumerate(rows):
        st[(r['subject'], r['fam'][0])].append(dict(r, _i=i))
    keys = sorted(st)
    quota = {k: max(2, round(n * len(st[k]) / len(rows))) for k in keys}
    while sum(quota.values()) > n:
        k = max(keys, key=lambda k: quota[k])
        if quota[k] <= 2:
            break
        quota[k] -= 1
    picked, cap = [], collections.Counter()
    for k in keys:
        bag = st[k][:]
        rng.shuffle(bag)
        got = 0
        for r in bag:
            if got >= quota[k]:
                break
            if cap[r['book']] >= per_book:
                continue
            cap[r['book']] += 1
            picked.append(r)
            got += 1
    rng.shuffle(picked)
    return picked


def sheets(picked, out_dir, cell=560, pad=None):
    # ⚠ VẼ ĐÚNG NHƯ ẢNH ĐÃ LƯU. Tự đặt đệm khác `crop_jpeg` thì bảng đối
    # chiếu soi một thứ mà trẻ không nhìn thấy — mẩu chữ ở mép có thể là
    # do MÌNH vẽ thừa chứ không phải do ảnh lưu.
    pad = 0.0 if pad is None else pad   # ĐÚNG như ảnh lưu của khối công thức
    import fitz
    from PIL import Image, ImageDraw
    os.makedirs(out_dir, exist_ok=True)
    docs, made, per = {}, [], 4
    row_h = 250
    for s in range(0, len(picked), per):
        chunk = picked[s:s + per]
        im = Image.new('RGB', (cell + 700, len(chunk) * row_h + 20), (255, 255, 255))
        dr = ImageDraw.Draw(im)
        for j, r in enumerate(chunk):
            y = j * row_h
            path = pdf_path(r['book'])
            if path and r['book'] not in docs:
                docs[r['book']] = fitz.open(path)
            doc = docs.get(r['book'])
            if doc and 1 <= r['page'] <= len(doc):
                pg = doc[r['page'] - 1]
                W, H = pg.rect.width, pg.rect.height
                b = r['box']
                clip = fitz.Rect(max(b[0] - pad, 0) * W, max(b[1] - pad, 0) * H,
                                 min(b[0] + b[2] + pad, 1) * W,
                                 min(b[1] + b[3] + pad, 1) * H)
                px = pg.get_pixmap(dpi=230, clip=clip)
                c = Image.frombytes('RGB', (px.width, px.height), px.samples)
                c.thumbnail((cell - 10, row_h - 54))
                im.paste(c, (6, y + 44))
            dr.text((8, y + 8),
                    f"#{r['_i']:05d} [{r['subject']}/{r['fam'][0]}] {r['book'][:32]} "
                    f"tr.{r['page']}" + (f" · số hiệu ({r['ident']})" if r['ident'] else ''),
                    fill=(0, 0, 0))
            dr.text((8, y + 26), 'BẢN IN NGUỒN = KHỐI CÔNG THỨC = ĐẦU RA ĐƯỢC CHỌN',
                    fill=(20, 120, 40))
            x = cell + 14
            dr.text((x, y + 8), 'OCR CŨ (đã bị bỏ):', fill=(180, 30, 30))
            for k, ln in enumerate(textwrap.wrap(r['ocr'], 78)[:6]):
                dr.text((x, y + 26 + k * 16), ln, fill=(0, 0, 0))
            dr.text((x, y + 128), 'THỨ TỰ ĐỌC — chữ TRƯỚC · chữ SAU:', fill=(90, 90, 90))
            for k, ln in enumerate(textwrap.wrap('◀ ' + r['before'], 78)[:2]):
                dr.text((x, y + 146 + k * 16), ln, fill=(70, 70, 70))
            for k, ln in enumerate(textwrap.wrap('▶ ' + r['after'], 78)[:2]):
                dr.text((x, y + 182 + k * 16), ln, fill=(70, 70, 70))
            dr.line([0, y + row_h - 6, cell + 700, y + row_h - 6], fill=(205, 205, 205))
        p = os.path.join(out_dir, f'sheet-{s // per:02d}.png')
        im.save(p)
        made.append(p)
    return made


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--n', type=int, default=60)
    ap.add_argument('--seed', type=int, default=20260916)
    ap.add_argument('--stage', default='/private/tmp/wal-stage-formula')
    ap.add_argument('--out', default=os.path.join(ROOT, 'poc-out', 'formula-review'))
    a = ap.parse_args()
    rows = frame(a.stage)
    if not rows:
        print('không có khối công thức nào trong khu dàn dựng', file=sys.stderr)
        return 1
    picked = draw(rows, a.n, a.seed)
    os.makedirs(a.out, exist_ok=True)
    with open(os.path.join(a.out, 'sample.json'), 'w', encoding='utf-8') as fh:
        json.dump(dict(seed=a.seed, frame=len(rows), verdicts=list(VERDICTS),
                       picked=picked), fh, ensure_ascii=False, indent=1)
    made = sheets(picked, a.out)
    st = collections.Counter((r['subject'], r['fam'][0]) for r in picked)
    print(f'khung {len(rows)} khối · mẫu {len(picked)} · {len(made)} bảng → {a.out}')
    for k in sorted(st):
        print(f'   {k[0]:10s} {k[1]:18s} {st[k]}')
    print(f'   sách khác nhau: {len({r["book"] for r in picked})}')
    return 0


if __name__ == '__main__':
    sys.exit(main())
