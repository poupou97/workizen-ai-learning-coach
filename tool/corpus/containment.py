#!/usr/bin/env python3
"""VÙNG NUỐT VẬT THỂ KHÁC — chốt an toàn thứ ba của bộ chọn hình.

Founder Gate 2026-09-09 (vòng an toàn CUỐI, có giới hạn):

    Một vùng Docling ứng cử thay chỗ mà CHỨA hoặc chồng đáng kể một vật thể
    nguồn khác có ý nghĩa độc lập ⇒ nếu không giải được an toàn: KHÔNG THAY.

⛔ HÌNH HỌC CHỈ ĐỀ CỬ, KHÔNG PHÁN QUYẾT. Hai hộp lồng nhau chưa nói được gì:
một hình có chú giải bên trong, một bảng có ô, một sơ đồ có nhãn — đều là hộp
chứa hộp mà vẫn là MỘT vật thể. Phán quyết phải dựa vào BẰNG CHỨNG IN:

    · trong khung có MỘT DÒNG CHÚ THÍCH IN KHÁC  → sách đã đặt tên vật thể thứ hai
    · trong khung có HÌNH NGUỒN KHÁC CÓ TÊN KHÁC → hai vật thể có tên riêng
    · trong khung có VÙNG ĐÁNG TIN KHÁC TÊN KHÁC → hai danh tính đã giải riêng

Hai ca thật đã soi bằng mắt sinh ra chốt này:

    Tin học 6 tr.20  — khung mang tên «Hình 2.3» nuốt trọn «Hình 2.2»
    Chuyên đề Hoá 12 tr.25 — khung mang tên «Hình 5.4» nuốt sơ đồ quy trình
                              và hộp «EM CÓ BIẾT»

⭐ HỎNG VỀ PHÍA GIỮ D. Không cắt gọt hộp Docling cho vừa phép đo: cắt theo
phỏng đoán là bịa ra một vùng mà không nguồn nào chứng nhận.
"""
INSIDE = 0.80             # vật thể kia nằm trong khung chừng này thì tính là bị nuốt
GREW = 1.25               # khung Docling to hơn hình D chừng này mới đáng xét


def _norm(t):
    return ' '.join((t or '').split()).strip().lower()


def _inside_frac(inner, outer):
    """Phần diện tích của `inner` nằm trong `outer` — mẫu số là CHÍNH `inner`.

    Lấy mẫu số là `outer` thì một vật thể nhỏ luôn ra tỉ lệ bé và không bao giờ
    bị coi là bị nuốt — đúng lỗi đã sửa ở `table_ownership`.
    """
    ix = min(inner[0] + inner[2], outer[0] + outer[2]) - max(inner[0], outer[0])
    iy = min(inner[1] + inner[3], outer[1] + outer[3]) - max(inner[1], outer[1])
    if ix <= 0 or iy <= 0:
        return 0.0
    return (ix * iy) / max(inner[2] * inner[3], 1e-9)


def _line_box(a):
    return [a['x'], a['y'], a.get('w') or 0, a.get('h') or 0]


def swallowed(cand_box, cand_caption, d_box, *, anchors=(), d_figs=(),
              trusted=(), have_lines=True):
    """Bằng chứng khung ứng cử đang nuốt một vật thể nguồn khác.

    Trả `(nhãn, mô tả)`. `nhãn = None` nghĩa là không thấy vật thể thứ hai nào.

    `d_box` = hình D mà khung này đòi thay; `d_figs` = các hình D KHÁC cùng
    trang; `anchors` = dòng chú thích in của trang; `trusted` = vùng Docling
    đáng tin khác cùng trang.
    """
    cap = _norm(cand_caption)

    # (1) Sách in một cái TÊN KHÁC ngay bên trong khung.
    for a in anchors:
        t = _norm(a.get('text'))
        if not t or t == cap:
            continue
        if _inside_frac(_line_box(a), cand_box) >= INSIDE:
            return 'CONTAINS_SEPARATE_CAPTION', a.get('text')

    # (2) Một hình NGUỒN khác, có tên in riêng, nằm gọn trong khung.
    for f in d_figs:
        fb = f.get('bbox')
        if not fb or fb == d_box:
            continue
        fc = _norm(f.get('caption'))
        if not fc or fc == cap:
            continue           # không tên thì không chứng minh được là vật riêng
        if _inside_frac(fb, cand_box) >= INSIDE:
            return 'CONTAINS_OTHER_NAMED_VISUAL', f.get('caption')

    # (3) Một vùng đã giải danh tính riêng nằm gọn trong khung.
    for r in trusted:
        rb = r.get('box')
        if not rb or rb == list(cand_box):
            continue
        rc = _norm((r.get('ident') or {}).get('text'))
        if not rc or rc == cap:
            continue
        if _inside_frac(rb, cand_box) >= INSIDE:
            return 'CONTAINS_OTHER_TRUSTED_REGION', (r.get('ident') or {}).get('text')

    # (4) Khung phình to hẳn so với hình D mà trang KHÔNG có dữ liệu dòng nào —
    #     không có gì để tra thì không kết luận được là an toàn.
    if not have_lines and d_box:
        a_c = cand_box[2] * cand_box[3]
        a_d = max(d_box[2] * d_box[3], 1e-9)
        if a_c / a_d >= GREW:
            return 'AMBIGUOUS_CONTAINMENT', 'trang không có dữ liệu dòng'
    return None, None
