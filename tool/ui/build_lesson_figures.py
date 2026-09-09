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
import decoration  # noqa: E402
import figure_funnel  # noqa: E402
import table_ownership  # noqa: E402
import staging  # noqa: E402
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
        # ⭐ BẢNG KHÔNG ĐƯỢC HIỆN HAI LẦN. Máy thật bắt được: trẻ đọc «STT 1 2 3
        # 4 5 6», «1986 1998 1998 2010» — bảng bẹp thành văn xuôi — rồi mới thấy
        # ảnh bảng đúng ngay bên dưới. Đo được 277/290 bài dính lỗi này.
        #
        # Chỉ bỏ khối chữ NẰM GỌN TRONG một vùng bảng đáng tin: chính ảnh ấy đã
        # hiện nó ra rồi nên không mất gì. Văn xuôi quanh bảng GIỮ NGUYÊN —
        # không có bằng chứng sở hữu thì không xoá chữ của sách.
        tabs = table_ownership.table_regions(figs_by_page.get(p['pagePdf'], []))
        keep = [q for q in paras
                if not (tabs and table_ownership.owned_by_table(q, tabs))]
        items = [((float(i), 0.0), dict(t=block_kind(q['text']), v=q['text']))
                 for i, q in enumerate(keep)]
        paras = keep
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

    # ⭐ AN TOÀN DỰNG (WAL-230): dựng thử KHÔNG được chạm dữ liệu đang phục vụ.
    # Bản trước đọc VÀ GHI thẳng `assets/pack/` bất kể `PACK_OUT_DIR`, nên một
    # lượt «dựng sang chỗ khác để đối chiếu» vẫn ghi đè index canonical tại chỗ.
    # Kho .db thì có `--out`, còn index thì không — hai nửa của một lần dựng đi
    # về hai nơi khác nhau mà không có gì báo.
    pack_dir = staging.pack_dir()
    idx_path = staging.guard(
        os.path.join(pack_dir, f'lesson-index-g{a.grade}.json'), 'index bài học')
    if not os.path.exists(idx_path):
        # ĐÓNG CHẶT: không lặng lẽ lùi về pack canonical. Thiếu index dàn dựng
        # nghĩa là bước trước chưa chạy — dựng tiếp là dựng lên dữ liệu sai.
        raise SystemExit(
            f'{idx_path}: không có index bài học.\n'
            f'Chạy build_lesson_index.py với CÙNG PACK_OUT_DIR={pack_dir} trước.')
    idx = json.load(open(idx_path, encoding='utf-8'))
    readings = idx.get('lessonReadings') or []
    if a.limit:
        readings = readings[:a.limit]
    pdfs = pdf_map()

    # Kho ảnh phải đi CÙNG index. Mặc định cũ trỏ thẳng thư mục canonical,
    # nên `PACK_OUT_DIR` chỉ dời được một nửa lượt dựng.
    out_dir = staging.figures_dir(a.out)
    os.makedirs(out_dir, exist_ok=True)
    db_path = staging.guard(os.path.join(out_dir, f'figures-g{a.grade}.db'),
                            'kho ảnh')
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
    SELECTOR_SHADOW = os.environ.get('SELECTOR_SHADOW') == '1'
    SEL_LOG = [] if os.environ.get('SELECTOR_LOG') else None
    if SELECTOR_SHADOW:
        print('  ⚠ CHẾ ĐỘ BÓNG: chỉ đếm quyết định chọn hình, KHÔNG đổi pack')
    if DL_TRUSTED:
        print(f'  + {sum(len(v) for v in DL_TRUSTED.values())} vùng Docling đáng tin trên {len(DL_TRUSTED)} trang')

    n_fig = n_les = n_cap = n_dec = n_sec = 0
    pending = []
    book_pages = {}
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
        # ⭐ BỘ CHỌN HÌNH (Founder Gate 2026-09-09): vùng Docling ĐÁNG TIN và
        # NỐI ĐƯỢC DANH TÍNH được ưu tiên khi CHỨNG MINH ĐƯỢC cùng một hình
        # nguồn — bằng chú thích in, không bằng chồng hộp. Không chứng minh
        # được ⇒ D là dự phòng. `SELECTOR_SHADOW=1` chỉ đếm, không đổi đầu ra.
        # Chú thích IN của từng trang: bằng chứng để biết một khung ứng cử có
        # đang nuốt một vật thể mang TÊN KHÁC hay không.
        anchors = {pp: figure_funnel.caption_anchors(
                       ls, extended=True,
                       block_lines=figure_funnel.block_line_counts(ls))
                   for pp, ls in lb.items()}
        figs = docling_pack.select(figs, r['book'], pages, DL_TRUSTED,
                                   stats=DL_STATS, shadow=SELECTOR_SHADOW,
                                   log=SEL_LOG, anchors=anchors)
        DL_STATS['CHI_D'] += n_d
        recs = []
        for f in figs:
            try:
                jpeg, (w, h) = crop_jpeg(pdf, f['page'], f['bbox'])
            except Exception as e:            # trang hỏng / PDF lỗi ⇒ bỏ hình, giữ chữ
                print(f"  ! {f['id']}: {e}", file=sys.stderr)
                continue
            recs.append(dict(id=f['id'], book=f['book'], page=f['page'], w=w, h=h,
                             jpeg=jpeg, bbox=f['bbox'], caption=f['caption'],
                             source=f.get('source', 'D'), kind=f.get('kind'),
                             hash=decoration.image_hash(jpeg),
                             inside=[l for l in (lb.get(f['page']) or [])
                                     if (l.get('text') or '').strip()
                                     and decoration._inside(f['bbox'], l)]))
        for pp2 in pages:
            book_pages.setdefault(r['book'], {}).setdefault(pp2, lb.get(pp2) or [])
        pending.append((r, recs))

    # ⭐ LƯỢT HAI — ĐỒ TRANG TRÍ CHỈ NHẬN RA ĐƯỢC KHI NHÌN CẢ CUỐN.
    # «Dải này in lại trên bao nhiêu trang của chính cuốn này» là bằng chứng
    # của cả quyển, không phải của một bài. Nên phải cắt xong hết rồi mới lọc.
    # Đo được: 17/35 ca hỏng trong mẫu 120 là đồ trang trí, cả 17 đều từ D.
    reps = decoration.repeat_index([x for _, rs in pending for x in rs])
    # ⭐ HỌ THỨ HAI — băng mục và dải trang. Nhận bằng VAI TRÒ TRONG SÁCH:
    # vùng chứa NHÃN MỤC mà chính cuốn ấy in lại trên nhiều trang, hoặc chứa
    # CHÍNH SỐ TRANG ở mép. Không nhận bằng dáng vẻ — «ít mực» và «dẹt» đều
    # đã bị số liệu bác bỏ (xem `decoration.py`).
    heads = {b: decoration.heading_reps(pg) for b, pg in book_pages.items()}
    for r, recs in pending:
        by_page = {}
        for f in recs:
            if decoration.is_page_furniture(f, reps):
                n_dec += 1
                continue
            if (f.get('source') != 'docling' and decoration.is_section_furniture(
                    f['bbox'], f.get('inside'), heads.get(f['book'], {}))):
                n_sec += 1
                continue
            db.execute('INSERT OR REPLACE INTO fig VALUES (?,?,?,?,?,?,?)',
                       (f['id'], f['book'], r['lesson'], f['page'], f['w'], f['h'],
                        f['jpeg']))
            by_page.setdefault(f['page'], []).append(
                dict(id=f['id'], bbox=f['bbox'], w=f['w'], h=f['h'], page=f['page'],
                     caption=f['caption'], kind=f.get('kind'),
                     source=f.get('source')))
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
    if SEL_LOG is not None:
        with open(os.environ['SELECTOR_LOG'], 'a', encoding='utf-8') as fh:
            for x in SEL_LOG:
                fh.write(json.dumps(x, ensure_ascii=False) + '\n')
    raw = open(db_path, 'rb').read()
    digest = hashlib.sha256(raw).hexdigest()
    manifest = dict(grade=a.grade, file=os.path.basename(db_path),
                    version=f'g{a.grade}-{digest[:12]}', size=len(raw),
                    sha256=digest, figures=n_fig, lessons=n_les,
                    captions=n_cap, builder='lesson-figures-v1',
                    bridge=dict(sorted(DL_STATS.items())),
                    pageFurnitureRemoved=n_dec,
                    sectionFurnitureRemoved=n_sec)
    mpath = staging.guard(os.path.join(out_dir, f'figures-g{a.grade}.manifest.json'),
                          'manifest')
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
