#!/usr/bin/env python3
"""B3 — CỘNG THÊM vùng đáng tin của Docling vào hình của D. KHÔNG THAY THẾ.

Luật di trú Founder chốt:

    NỘI DUNG D AN TOÀN  +  VÙNG DOCLING ĐÁNG TIN  =  NỘI DUNG CANONICAL MỚI

Không bao giờ: D → Docling thay trọn gói.

Chỉ vùng đạt CẢ HAI phép đo mới vào dòng đọc của trẻ:
`REGION_TRUST = TRUSTED` VÀ `IDENTITY_LINK = RESOLVED`. Vùng đáng tin mà danh
tính còn giữ lại thì nằm trong corpus canonical, KHÔNG hiện cho trẻ — mất nhãn
con làm ảnh hiện ra sai lệch.

Thiếu tệp `trusted.jsonl` thì hàm này trả về rỗng và đường dựng chạy y như cũ.
Đó là chủ ý: bước tri giác hỏng KHÔNG được làm hỏng dữ liệu đang tốt.
"""
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
TRUSTED = os.path.join(ROOT, 'poc-out', 'docling', 'trusted.jsonl')
DEDUP_IOU = 0.5           # trùng chừng này với vùng D ⇒ cùng một hình


def _iou(a, b):
    ix = min(a[0] + a[2], b[0] + b[2]) - max(a[0], b[0])
    iy = min(a[1] + a[3], b[1] + b[3]) - max(a[1], b[1])
    if ix <= 0 or iy <= 0:
        return 0.0
    inter = ix * iy
    return inter / max(a[2] * a[3] + b[2] * b[3] - inter, 1e-9)


def readable_by_page(path=TRUSTED):
    """`{(sách, trang): [vùng, ...]}` — chỉ vùng đủ điều kiện vào dòng đọc."""
    out = {}
    if not os.path.exists(path):
        return out
    with open(path, encoding='utf-8') as fh:
        for line in fh:
            try:
                r = json.loads(line)
            except ValueError:
                continue
            if not r.get('readable'):
                continue
            out.setdefault((r['book'], r['page']), []).append(r)
    return out


def caption_of(r):
    """Chú thích hiện cho trẻ — CHỮ SÁCH IN, không phải chữ máy đặt.

    Có nhãn con thì nhãn con là thứ nói đúng ảnh NÀY («b) Mèo Anh lông ngắn»);
    không có thì dùng chú thích của hình.
    """
    ident = r.get('ident') or {}
    return ident.get('sub') or ident.get('text') or None


def extra_figures(book, pages, existing, index, stats=None):
    """Vùng Docling THÊM vào, đã loại những vùng D đã có.

    `existing` = bbox các hình D đã nhận, để không đưa hai bản của cùng một hình.

    `stats` = `Counter` đếm CẦU NỐI DI TRÚ ngay trong lúc dựng: `MOI` (chỉ
    Docling có) và `CA_HAI` (D đã có rồi). Đếm ở đây vì đây là chỗ DUY NHẤT biết
    cả hai phía; đo lại sau bằng một lượt quét nữa vừa đắt vừa dễ lệch.
    """
    out = []
    for pp in pages:
        for k, r in enumerate(index.get((book, pp), [])):
            bbox = r['box']
            if any(_iou(bbox, e) > DEDUP_IOU for e in existing):
                if stats is not None:
                    stats['CA_HAI'] += 1
                continue
            if stats is not None:
                stats['MOI'] += 1
            out.append(dict(id=f'{book}:p{pp:03d}:dl{k:02d}', book=book, page=pp,
                            bbox=bbox, area=round(bbox[2] * bbox[3], 5),
                            caption=caption_of(r), source='docling',
                            kind=r.get('kind') or 'picture'))
            existing.append(bbox)
    return out


# ────────────────────────────────────────────────────────────────────────
# BỘ CHỌN HÌNH — «TRUSTED DOCLING ƯU TIÊN → D DỰ PHÒNG → GIỮ LẠI»
# ────────────────────────────────────────────────────────────────────────
#
# Founder Gate 2026-09-09 duyệt ĐỔI CHÍNH SÁCH CHỌN, không phải bỏ D.
#
# Bằng chứng: `FIGURE_CROP_VALID` D 78,2% · Docling 100,0% (n=33 tươi). Trong
# 19 ca lỗi còn nhìn thấy: D_BAD_DOCLING_GOOD 13 · DOCLING_FAILURE 0. Nhân
# chứng cùng-một-bài: Toán 7 biểu đồ hình quạt — bản D CẮT MẤT CHÚ GIẢI, bản
# Docling của CHÍNH biểu đồ ấy giữ đủ tiêu đề và chú giải.
#
# ⛔ «CÙNG MỘT HÌNH NGUỒN» KHÔNG ĐƯỢC ĐỊNH NGHĨA BẰNG CHỒNG HỘP.
# Hai hộp chồng nhau có thể là hai hình khác nhau nằm cạnh nhau, hoặc một hình
# và một mảnh của nó. Bằng chứng phải từ NGUỒN:
#
#     cả hai cùng viện dẫn MỘT DÒNG CHÚ THÍCH SÁCH IN, trên CÙNG MỘT TRANG.
#
# Hình học chỉ được làm bằng chứng PHỤ (phải có chồng nhau), không được làm
# quyền phán quyết.
#
# ⭐ VÀ `REGION_TRUST != IDENTITY_LINK` VẪN GIỮ NGUYÊN: một vùng Docling sạch
# mà danh tính còn giữ lại thì KHÔNG được thay chỗ một hình D đã có danh tính,
# dù hộp có chồng nhau. Không bịa danh tính để giành quyền hiển thị.


def _norm_cap(t):
    return ' '.join((t or '').split()).strip().lower()


def same_source_visual(d_fig, dl_row):
    """Hai bên có đang nói về CÙNG MỘT hình của sách không.

    Ba vế, phải đủ: cùng trang · cùng dòng chú thích IN · và có chồng nhau.
    Thiếu chú thích ở bất kỳ bên nào ⇒ KHÔNG chứng minh được ⇒ False.
    """
    if d_fig.get('page') != dl_row.get('page'):
        return False
    a = _norm_cap(d_fig.get('caption'))
    b = _norm_cap((dl_row.get('ident') or {}).get('text'))
    if not a or not b or a != b:
        return False
    x, y, w, h = d_fig['bbox']
    return _iou([x, y, w, h], dl_row['box']) > 0


def _sub_of(r):
    return ((r.get('ident') or {}).get('sub') or '').strip().lower() or None


PART_INSIDE = 0.9         # vùng Docling nằm gọn trong hình D chừng này
PART_AREA = 0.4           # ...mà chỉ chiếm chừng này diện tích ⇒ là MỘT MẢNH


def partial_claim(d_fig, dl_row):
    """Vùng Docling có đang đòi tên của cả hình trong khi chỉ là MỘT MẢNH không.

    ⛔ Họ hỏng đo được trên mẫu 55 ca đối chiếu ba bên (3 ca, 5,5%): sách in một
    hình gồm nhiều ô — «Hình 12.6. Quây úm cho gà con» (3 ô), «Hình 8.7. Các
    bước là quần áo» (5 ô) — Docling đề xuất ĐÚNG MỘT ô, rồi thừa hưởng tên của
    cả hình. Trẻ mất các ô còn lại VÀ nhận một cái tên sai phạm vi.

    `naming_conflict` không bắt được vì ở đây chỉ có MỘT vùng Docling đòi.

    Bằng chứng là quan hệ BAO HÀM, không phải chồng lấn: chú thích in nằm dưới
    CẢ hình, nên tên thuộc về cả hình. Nằm gọn bên trong mà nhỏ hơn hẳn ⇒ mảnh.
    Chiều ngược lại (D nằm trong Docling) là Docling BÙ phần D cắt thiếu —
    990/3.403 cặp, và đó chính là cái ta muốn.

    Ngưỡng 0,4 chọn trên chính mẫu 55 ca ⇒ tỉ lệ sót phải đo lại bằng MẪU MỚI.
    """
    if _sub_of(dl_row):
        # Có nhãn con IN thì mảnh ấy có TÊN RIÊNG của sách — không mượn của ai.
        return False
    d = d_fig['bbox']
    dl = dl_row['box']
    ix = min(d[0] + d[2], dl[0] + dl[2]) - max(d[0], dl[0])
    iy = min(d[1] + d[3], dl[1] + dl[3]) - max(d[1], dl[1])
    if ix <= 0 or iy <= 0:
        return False
    a_dl = max(dl[2] * dl[3], 1e-9)
    a_d = max(d[2] * d[3], 1e-9)
    return (ix * iy) / a_dl >= PART_INSIDE and a_dl / a_d < PART_AREA


def naming_conflict(claims):
    """Nhóm vùng Docling cùng đòi thay MỘT hình D — có tách được không.

    ⛔ CẠM BẪY HÌNH CON, đo được trên corpus: 161 hình D bị nhiều vùng Docling
    cùng viện dẫn một chú thích. Thả cho thay chỗ thì «Hình 8. Luyện tập tung và
    bắt bóng trên cao» biến thành SÁU ảnh khác nhau CÙNG MANG MỘT TÊN. Đó là
    SAI TÊN, tệ hơn THIẾU TÊN.

    Chỉ tách khi sách IN nhãn con phân biệt cho từng vùng. 13/161 nhóm đạt;
    148 nhóm còn lại giữ hình D gộp — sách in một tên thì hiện một ảnh.
    """
    if len(claims) < 2:
        return False
    subs = [_sub_of(r) for _, r in claims]
    return not (all(subs) and len(set(subs)) == len(subs))


def select(figs, book, pages, index, stats=None, shadow=False, log=None):
    """Danh sách hình HIỆN CHO TRẺ, sau khi chọn giữa hai đường.

    `shadow=True`: ĐẾM quyết định của chính sách MỚI nhưng vẫn ra ĐÚNG ĐẦU RA
    CỦA CHÍNH SÁCH ĐANG CHẠY (D thắng khi chồng hộp, Docling chỉ thêm ở chỗ
    trống) — để chạy thử toàn corpus mà pack không đổi một byte.

    ⚠ Bóng KHÔNG phải là «chỉ giữ D». Bản đầu tôi viết vậy và nó lặng lẽ bỏ
    luôn phần Docling đang có: lớp 6 tụt 913 → 709 hình. Bóng mà đổi đầu ra thì
    không còn là bóng.
    """
    def bump(k):
        if stats is not None:
            stats[k] += 1

    out = list(figs)
    taken = [f['bbox'] for f in out]

    def _add(pp, k, r):
        box = r['box']
        out.append(dict(id=f'{book}:p{pp:03d}:dl{k:02d}', book=book, page=pp,
                        bbox=box, area=round(box[2] * box[3], 5),
                        caption=caption_of(r), source='docling',
                        kind=r.get('kind') or 'picture'))
        taken.append(box)

    for pp in pages:
        rows = list(enumerate(index.get((book, pp), [])))
        # PHA 1 — ai đòi thay hình D nào. Phải biết TOÀN nhóm trước khi quyết,
        # vì nguy hiểm nằm ở SỐ LƯỢNG vùng cùng đòi, không ở từng vùng một.
        claims, by_id = {}, {}
        for k, r in rows:
            for f in out:
                if f.get('source') != 'docling' and same_source_visual(f, r):
                    claims.setdefault(id(f), []).append((k, r))
                    by_id[id(f)] = f
                    break
        blocked = set()
        for fid, grp in claims.items():
            if naming_conflict(grp):
                blocked.update(k for k, _ in grp)
                continue
            for k, r in grp:                 # một mảnh cũng không được mượn tên
                if partial_claim(by_id[fid], r):
                    blocked.add(k)

        for k, r in rows:
            box = r['box']
            same = [f for f in out if f.get('source') != 'docling'
                    and same_source_visual(f, r)]
            if k in blocked:
                bump('PART_OF_NAMED_FIGURE')
                if not shadow:
                    continue          # giữ hình D gộp, BỎ mảnh mượn tên
                # BÓNG: rơi xuống đúng luật cũ, không được rẽ hướng.
            elif same:
                bump('DOCLING_SUPERSEDES_D')
                if log is not None:
                    # Ghi CẶP để dựng mẫu đối chiếu ba bên: NGUỒN · D · DOCLING.
                    log.append(dict(book=book, page=pp,
                                    d_bbox=[round(v, 4) for v in same[0]['bbox']],
                                    dl_bbox=[round(v, 4) for v in box],
                                    caption=(r.get('ident') or {}).get('text'),
                                    kind=r.get('kind') or 'picture'))
                if not shadow:
                    for f in same:
                        out.remove(f)
                        if f['bbox'] in taken:
                            taken.remove(f['bbox'])
                    _add(pp, k, r)
                    continue
                # BÓNG: rơi xuống đúng luật cũ, không được rẽ hướng.
            elif any(_iou(box, e) > DEDUP_IOU for e in taken):
                bump('D_FALLBACK')
                continue
            else:
                bump('DOCLING_NEW')
            # luật cũ: chồng nhiều thì bỏ, còn lại thì thêm.
            if not any(_iou(box, e) > DEDUP_IOU for e in taken):
                _add(pp, k, r)
    return out
