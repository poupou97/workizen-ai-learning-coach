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
import collections
import hashlib
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
import docling_pack  # noqa: E402
from lesson_reading import lesson_reading  # noqa: E402
from read_structure import block_kind  # noqa: E402

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
    """Dòng nội dung: KHỐI của nguồn giữ nguyên là khối, hình chèn đúng y của nó.

    ⭐⭐ ĐÂY LÀ CHỖ CẤU TRÚC ĐỌC TỪNG BỊ LÀM PHẲNG.

    Bản trước dính mọi khối chữ liền nhau thành một: `stream[-1]['v'] += ...`.
    Đo được trên toàn corpus: nguồn có 215.714 khối, pack ghi ra 14.119 (6,5%),
    và 2.944/2.944 bài đều có «số khối chữ ≤ số ảnh + 1» — nghĩa là dòng đọc
    chưa bao giờ được ngắt theo đoạn, nó chỉ bị cắt ở chỗ chèn ảnh. Vật lí 11
    Bài 5: nguồn 67 khối, pack 1 khối, 4.980 ký tự liền một mạch.

    16.680 tiêu đề mục của sách («I.», «1.», «a)») cũng biến mất trong đống ấy.

    Ở đây KHÔNG gộp nữa. Khối nào của nguồn ra khối ấy, đúng thứ tự đọc, và
    khối mở đầu bằng đánh số mục được đánh dấu `heading` — biết tới đâu ghi
    tới đó, KHÔNG suy ra cấp bậc h1/h2/h3 từ chỗ không có bằng chứng.
    """
    stream = []
    for p in pages:
        # ⚠ THỨ TỰ CHỮ LÀ THỨ TỰ ĐỌC, KHÔNG PHẢI THỨ TỰ Y.
        # `page_paragraphs` đã trả về theo dải đọc (`seq`) đúng vì lý do ở #141:
        # xếp khối theo y thuần làm khung phụ chen vào giữa câu. Bản trước ở đây
        # xếp theo `q['y']` — lỗi ấy bị che vì mọi khối chữ đều bị dính lại làm
        # một. Bỏ gộp mà giữ nguyên cách xếp cũ là làm lỗi #141 sống lại.
        paras = sorted(p.get('paragraphs') or [], key=lambda q: q['seq'])
        items = [((float(i), 0.0), dict(t=block_kind(q['text']), v=q['text']))
                 for i, q in enumerate(paras)]
        for f in figs_by_page.get(p['pagePdf'], []):
            # Hình neo vào KHỐI CHỮ GẦN NHẤT PHÍA TRÊN nó theo y — vị trí hình
            # là chuyện hình học, còn thứ tự chữ là chuyện dải đọc. Không có
            # khối nào ở trên ⇒ hình mở đầu trang.
            fy = f['bbox'][1]
            above = [(q['y'], i) for i, q in enumerate(paras) if q['y'] <= fy]
            pos = (max(above)[1] + 0.5) if above else -0.5
            # Hai hình cùng neo vào một khối ⇒ tách bằng chính y của chúng.
            # Không có khoá phụ này thì thứ tự rơi về thứ tự dò, tức là ngẫu
            # nhiên với trẻ đang đọc.
            items.append(((pos, fy), dict(t='img', id=f['id'], w=f['w'],
                                          h=f['h'], page=f['page'],
                                          caption=f['caption'])))
        for _, it in sorted(items, key=lambda z: z[0]):
            stream.append(it)
    return stream


def _cleanup(tmp_path):
    """Tệp `.building` sót lại chiếm chỗ và làm người sau tưởng kho đang dựng."""
    try:
        if tmp_path and os.path.exists(tmp_path):
            os.remove(tmp_path)
    except OSError:
        pass


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('grade', type=int)
    ap.add_argument('--limit', type=int, default=0)
    ap.add_argument('--out', default=None,
                    help='thư mục pack (mặc định poc-out/packs/figures — KHÔNG phải assets/)')
    a = ap.parse_args()

    idx_path = os.path.join(ROOT, f'assets/pack/lesson-index-g{a.grade}.json')
    idx = json.load(open(idx_path, encoding='utf-8'))
    readings = idx.get('lessonReadings') or []
    if a.limit:
        readings = readings[:a.limit]
    pdfs = pdf_map()

    out_dir = a.out or os.path.join(ROOT, 'poc-out/packs/figures')
    os.makedirs(out_dir, exist_ok=True)
    db_path = os.path.join(out_dir, f'figures-g{a.grade}.db')
    # ⭐ DỰNG SANG TỆP TẠM RỒI MỚI ĐỔI TÊN.
    # Bản trước XOÁ kho cũ ngay từ đầu, nên một lần dựng hỏng giữa chừng (đã xảy
    # ra thật: `disk I/O error` ở lớp 7) làm mất luôn kho ĐANG CHẠY TỐT. Cùng bài
    # học nguyên tử với `GradePackInstaller`: bản cũ phải sống sót qua một lần
    # dựng thất bại.
    tmp_path = db_path + '.building'
    if os.path.exists(tmp_path):
        os.remove(tmp_path)
    db = sqlite3.connect(tmp_path)
    db.execute('CREATE TABLE fig (id TEXT PRIMARY KEY, book TEXT, lesson INT, '
               'page INT, w INT, h INT, jpeg BLOB)')

    # Gộp toàn bộ ~1.500 ảnh vào MỘT giao dịch làm nhật ký hoàn tác phình tới
    # vài chục MB, và commit khi ấy đã ném `disk I/O error` thật (lớp 4, 5, 7).
    # Chốt theo lô để nhật ký luôn nhỏ.
    COMMIT_EVERY = 50

    DL_TRUSTED = docling_pack.readable_by_page()
    DL_STATS = collections.Counter()
    if DL_TRUSTED:
        print(f'  + {sum(len(v) for v in DL_TRUSTED.values())} vùng Docling đáng tin trên {len(DL_TRUSTED)} trang')

    n_fig = n_les = n_cap = 0
    for r in readings:
        pdf = pdfs.get(r['book'])
        if not pdf:
            continue
        pages = range(r['pagePdfStart'], r['pagePdfEnd'] + 1)
        lb = lines_for(r['book'], pages)
        figs = lesson_figures(pdf, r['book'], pages, lb)
        # ⭐ CỘNG THÊM, KHÔNG THAY THẾ (B3). Vùng D giữ nguyên; vùng Docling
        # đã qua cổng tin cậy VÀ nối được danh tính thì thêm vào sau, bỏ những
        # vùng trùng hình D đã có. Không có tệp tin cậy ⇒ danh sách rỗng ⇒
        # đường dựng chạy y như trước.
        n_d = len(figs)
        figs += docling_pack.extra_figures(r['book'], pages,
                                           [f['bbox'] for f in figs], DL_TRUSTED,
                                           stats=DL_STATS)
        DL_STATS['CHI_D'] += n_d
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
            if n_fig % COMMIT_EVERY == 0:
                db.commit()
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
    os.replace(tmp_path, db_path)      # nguyên tử: không có nửa kho ở chỗ thật
    # Hình đã vào `content` ⇒ pack không còn dở dang.
    idx.pop('figuresPending', None)
    json.dump(idx, open(idx_path, 'w'), ensure_ascii=False)
    # MANIFEST — máy cài pack phải kiểm được TRƯỚC KHI kích hoạt: đúng tệp
    # không, đủ byte không, băm có khớp không. Nửa tệp mà vẫn nạp thì trẻ mở bài
    # ra thấy ảnh vỡ, và không ai biết vì sao.
    raw = open(db_path, 'rb').read()
    digest = hashlib.sha256(raw).hexdigest()
    manifest = dict(grade=a.grade, file=os.path.basename(db_path),
                    version=f'g{a.grade}-{digest[:12]}', size=len(raw),
                    sha256=digest, figures=n_fig, lessons=n_les,
                    captions=n_cap, builder='lesson-figures-v1',
                    bridge=dict(sorted(DL_STATS.items())))
    mpath = os.path.join(out_dir, f'figures-g{a.grade}.manifest.json')
    with open(mpath, 'w', encoding='utf-8') as fh:
        json.dump(manifest, fh, ensure_ascii=False, indent=1)
    print(f'lớp {a.grade}: {n_fig} hình ({n_cap} có chú thích của sách) trong '
          f'{n_les}/{len(readings)} bài · {manifest["file"]} '
          f'{len(raw)/1048576:.0f} MB · {manifest["version"]}')


if __name__ == '__main__':
    try:
        sys.exit(main())
    except BaseException:
        # Hỏng giữa chừng ⇒ dọn tệp tạm. Kho ĐANG CHẠY TỐT không bị đụng tới:
        # nó chỉ bị thay ở bước `os.replace` cuối cùng.
        import glob as _g
        for _t in _g.glob(os.path.join(ROOT, 'poc-out/packs/figures/*.building')):
            _cleanup(_t)
        raise
