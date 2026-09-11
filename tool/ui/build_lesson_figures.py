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
import map_ownership  # noqa: E402
import table_ownership  # noqa: E402
import formula_source  # noqa: E402
import staging  # noqa: E402
from lesson_reading import CODE_OFF, lesson_reading, page_paragraphs  # noqa: E402
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



def _grey_render(pdf, page_pdf):
    """`render(box) -> (ảnh xám phẳng, w, h)` cho `formula_source.fit_region`.

    Dựng ở dpi thấp: câu hỏi chỉ là «mực có chạm mép không», không cần nét.
    """
    import fitz

    def render(box):
        doc = fitz.open(pdf)
        try:
            pg = doc[page_pdf - 1]
            r = pg.rect
            clip = fitz.Rect(box[0] * r.width, box[1] * r.height,
                             (box[0] + box[2]) * r.width,
                             (box[1] + box[3]) * r.height)
            px = pg.get_pixmap(dpi=60, clip=clip, colorspace=fitz.csGRAY)
            return list(px.samples), px.width, px.height
        finally:
            doc.close()
    return render



def promoted_off(env=None):
    """Tên các năng lực ĐÃ PROMOTE đang bị tắt ở lượt dựng này.

    ⭐ MẶC ĐỊNH PHẢI LÀ RỖNG. Đó chính là bất biến mà vụ 2026-09-11 phá: khi
    `FORMULA_SOURCE` còn là cờ BẬT thủ công, một lượt dựng quên cờ ra pack
    thiếu khối công thức mà không có gì báo. Nay quên cờ = đầy đủ; muốn thiếu
    phải nói rõ, và nói rõ khi dựng canonical thì `staging.require_promoted`
    dừng hẳn.

    `CodeSource` đọc từ chính module sở hữu hành vi (`lesson_reading.CODE_OFF`)
    chứ không đọc lại tên biến môi trường — hai chỗ giữ một tên là cách chúng
    trôi khỏi nhau.
    """
    env = os.environ if env is None else env
    off = []
    if env.get('FORMULA_SOURCE') == '0' or env.get('FORMULA_SHADOW') == '1':
        off.append('FormulaSource')
    if CODE_OFF:
        off.append('CodeSource')
    return off


def interleave(pages, figs_by_page, fml_by_page=None):
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
        # ⭐ BẢN ĐỒ CŨNG KHÔNG ĐƯỢC HIỆN HAI LẦN. Sau khi vòng danh tính giao
        # được tấm bản đồ, trẻ vẫn đọc tiếp «PINÓM PÊNII», «LAI CHÂU», «CHÚ
        # GIÁI MẶT ĐỌ DÂN SỐ…» — địa danh, toạ độ, chú giải VẼ TRONG chính tấm
        # ảnh ấy. Phạm vi CỐ Ý HẸP: chỉ vật mà sách GỌI TÊN là bản đồ/lược đồ
        # (3 375 đoạn / 118 trang). Bản rộng «mọi vùng hình» đã bị đo bác bỏ —
        # lý do đầy đủ trong `map_ownership`.
        maps = map_ownership.map_regions(figs_by_page.get(p['pagePdf'], []))
        # ⭐ CÔNG THỨC CŨNG KHÔNG ĐƯỢC HIỆN HAI LẦN — và ở đây lý do nặng hơn
        # bảng: chuỗi OCR của công thức KHÔNG CHỈ thừa, nó SAI. Đo 53 ca soi
        # mắt so với bản in: 88,7% hại, Toán 23/23. «x²/9 + y²/5 = 1» tới tay
        # trẻ thành «5 = 1.». Nên chữ mà một vùng công thức sở hữu bị GIỮ LẠI,
        # dù có dựng được ảnh hay không (Founder Gate: B mặc định, D dự phòng).
        # Quyền sở hữu tính NGAY Ở ĐÂY, chỗ có đoạn văn thật — không mang
        # `id()` qua hai lượt dựng, vì đó là hai bộ đối tượng khác nhau.
        # Dùng TOÀN BỘ vùng (kể cả vùng không dựng được ảnh): vùng không an
        # toàn vẫn phải giữ lại chữ sai của nó (D).
        fml = (fml_by_page or {}).get(p['pagePdf']) or {}
        fregs = fml.get('regions') or []
        # ⚠ KHỐI MÃ MIỄN NHIỄM VỚI CẢ BA LUẬT SỞ HỮU TRÊN, và đây là rủi ro do
        # CHÍNH thay đổi này sinh ra: trước kia dòng mã nằm lẫn trong một đoạn
        # văn rộng cả trang nên không vùng nào sở hữu nổi; giờ nó khớp GỌN vào
        # vùng mã, nên một vùng bảng chồng lên là nuốt trọn cả chương trình.
        # Vùng mã là bằng chứng nguồn riêng, không phải chữ thừa của bảng.
        keep = [q for q in paras
                if q.get('kind') == 'code'
                or (not (fregs and formula_source.owned_by_formula(q, fregs))
                    and not (tabs and table_ownership.owned_by_table(q, tabs))
                    and not (maps and map_ownership.owned_by_map(q, maps)))]
        # ⚠ KHỐI MÃ KHÔNG BAO GIỜ LÀ TIÊU ĐỀ. `block_kind` nhận tiêu đề mục
        # bằng cách nhìn đánh số đầu khối («1.», «a)») — mà mã nguồn in kèm
        # cột số dòng thì mở đầu đúng như thế. Bằng chứng loại khối đã có sẵn
        # từ hình học, đừng đoán lại bằng chính tả.
        items = [((float(i), 0.0),
                  dict(t='text' if q.get('kind') == 'code' else block_kind(q['text']),
                       v=q['text']))
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
        for b in (fml.get('blocks') or []):
            # Neo như hình: theo khối chữ gần nhất PHÍA TRÊN. Thứ tự đọc của
            # nguồn phải giữ — TEXT TRƯỚC → CÔNG THỨC → TEXT SAU.
            above = [(q['y'], i) for i, q in enumerate(paras) if q['y'] <= b['y']]
            pos = (max(above)[1] + 0.5) if above else -0.5
            items.append(((pos, b['y']),
                          dict(t='formula', id=b['id'], w=b['w'], h=b['h'],
                               page=b['page'], src=b['src'], trust=b['trust'],
                               ident=b['ident'])))
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
    # ⭐ WAL-239 — CÔNG THỨC TỚI VỚI TRẺ BẰNG ẢNH TRANG IN (Founder Gate: B).
    # `FORMULA_SHADOW=1` chỉ ĐẾM, không đổi dòng đọc. Thiếu tệp đề xuất ⇒ rỗng
    # ⇒ đường dựng chạy y như cũ.
    # ⭐ ĐÃ PROMOTE ⇒ BẬT MẶC ĐỊNH. Trước 2026-09-11 đây là cờ BẬT thủ công
    # (`!= '1'`), nên một lượt dựng quên cờ ra pack thiếu khối công thức mà
    # KHÔNG lỗi nào báo — 28 bài Toán 5 nhận lại mảnh OCR «+», «a)», «:(x7)».
    # Nay theo đúng quy ước của `WAL_CODE_OFF`: năng lực đã promote thì cờ là
    # cờ TẮT, và tắt nó khi dựng canonical thì `require_promoted` dừng hẳn.
    FORMULA_OFF = os.environ.get('FORMULA_SOURCE') == '0'
    FORMULA_SHADOW = os.environ.get('FORMULA_SHADOW') == '1'
    staging.require_promoted(promoted_off())
    FML_REGIONS = {} if FORMULA_OFF else formula_source.regions_index()
    FML_STATS = collections.Counter()
    if FML_REGIONS:
        print(f'  + {sum(len(v) for v in FML_REGIONS.values())} vùng công thức '
              f'trên {len(FML_REGIONS)} trang', file=sys.stderr)
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
        # ⭐ KHỐI CÔNG THỨC — cắt từ chính trang in. KHÔNG dựng lại nội dung.
        fml = {}
        for pp2 in pages:
            regs = FML_REGIONS.get((r['book'], pp2)) or []
            if not regs:
                continue
            paras = page_paragraphs(lb.get(pp2) or [])
            blks, _ = formula_source.blocks(r['book'], pp2, regs, paras)
            FML_STATS['VUNG'] += len(regs)
            FML_STATS['KHOI_DUNG_DUOC'] += len(blks)
            # Bỏ vì HAI lý do khác nhau — không gộp: vùng không cắt an toàn
            # được, và vùng không chứng minh được sở hữu (dựng khối lúc ấy là
            # rơi vào C). Gộp hai cái làm một là giấu mất một họ.
            FML_STATS['BO_VUNG_KHONG_AN_TOAN'] += sum(
                1 for r2 in regs if not formula_source.safe_region(r2))
            FML_STATS['BO_TRANH_C'] += (len(regs) - len(blks)) - sum(
                1 for r2 in regs if not formula_source.safe_region(r2))
            FML_STATS['CHU_BI_GIU_LAI'] += sum(
                1 for q in paras if formula_source.owned_by_formula(q, regs))
            ok = []
            for b in blks:
                try:
                    # ⭐ CẮT VỪA VẶN, KHÔNG DÙNG ĐỆM CỐ ĐỊNH. Vùng Docling cắt
                    # hụt phía trên của phân số cao («mv₁²/2» còn mỗi «/2»),
                    # mà nới đều thì kéo văn xuôi hàng xóm vào. Hỏi chính
                    # trang in: mực chạm mép nào thì nới đúng mép ấy.
                    # ⚠ KHÔNG đặt tên `ok`: biến ấy đang là danh sách gom khối
                    # ở ngay vòng ngoài. Trùng tên làm nó thành `bool` và cả
                    # lượt dựng chết ở `ok.append` — bắt được vì tôi kiểm dòng
                    # lỗi trong log thay vì chỉ đếm số lớp đã xong.
                    fit, fit_ok = formula_source.fit_region(
                        None, b['bbox'], _grey_render(pdf, pp2))
                    if not fit_ok:
                        FML_STATS['BO_CAT_KHONG_TRON'] += 1
                        continue          # ĐÓNG CHẶT: không hiện công thức cụt
                    b['bbox'] = fit
                    # ⭐ XUẤT XỨ PHẢI NÓI ĐÚNG VÙNG ĐÃ CẮT. Giữ hộp gốc ở đây
                    # là ghi sai lý lịch: ai dựng lại ảnh từ `src.region` sẽ ra
                    # một ảnh CỤT khác với ảnh trẻ đang xem. Chính chỗ này đã
                    # làm bảng đối chiếu của tôi báo nhầm 4 ca «cắt cụt».
                    b['src'] = dict(b['src'], region=[round(v, 4) for v in fit],
                                    fitted=True)
                    jpeg, (w, h) = crop_jpeg(pdf, pp2, fit, pad=0.0)
                except Exception as e:        # cắt hỏng ⇒ ĐÓNG CHẶT, không khối
                    print(f"  ! {b['id']}: {e}", file=sys.stderr)
                    FML_STATS['CAT_HONG'] += 1
                    continue
                b.update(w=w, h=h, jpeg=jpeg)
                ok.append(b)
            fml[pp2] = dict(regions=regs, blocks=ok)
        for pp2 in pages:
            book_pages.setdefault(r['book'], {}).setdefault(pp2, lb.get(pp2) or [])
        pending.append((r, recs, fml))

    # ⭐ LƯỢT HAI — ĐỒ TRANG TRÍ CHỈ NHẬN RA ĐƯỢC KHI NHÌN CẢ CUỐN.
    # «Dải này in lại trên bao nhiêu trang của chính cuốn này» là bằng chứng
    # của cả quyển, không phải của một bài. Nên phải cắt xong hết rồi mới lọc.
    # Đo được: 17/35 ca hỏng trong mẫu 120 là đồ trang trí, cả 17 đều từ D.
    reps = decoration.repeat_index([x for _, rs, _ in pending for x in rs])
    # ⭐ HỌ THỨ HAI — băng mục và dải trang. Nhận bằng VAI TRÒ TRONG SÁCH:
    # vùng chứa NHÃN MỤC mà chính cuốn ấy in lại trên nhiều trang, hoặc chứa
    # CHÍNH SỐ TRANG ở mép. Không nhận bằng dáng vẻ — «ít mực» và «dẹt» đều
    # đã bị số liệu bác bỏ (xem `decoration.py`).
    heads = {b: decoration.heading_reps(pg) for b, pg in book_pages.items()}
    for r, recs, fml in pending:
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
        # Ghi ảnh công thức vào cùng kho ảnh của lớp — một đường lưu trữ đã
        # chứng minh, không dựng đường mới.
        for pp2, fm in ({} if FORMULA_SHADOW else (fml or {})).items():
            for b in fm['blocks']:
                db.execute('INSERT OR REPLACE INTO fig VALUES (?,?,?,?,?,?,?)',
                           (b['id'], r['book'], r.get('lesson'), b['page'],
                            b['w'], b['h'], b['jpeg']))
                FML_STATS['KHOI_VAO_PACK'] += 1
        r['content'] = interleave(doc['pages'], by_page,
                                  None if FORMULA_SHADOW else fml)
        if FORMULA_SHADOW and fml:
            FML_STATS['BONG_KHONG_DOI_DAU_RA'] += 1
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
                    formula=dict(sorted(FML_STATS.items())),
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
