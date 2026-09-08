#!/usr/bin/env python3
"""B3 — DANH TÍNH TÁCH KHỎI VÙNG. `REGION_TRUST != IDENTITY_LINK`.

Founder chốt ở cổng B3: hai thứ này là HAI PHÉP ĐO, không được biến cái này
thành cái kia. Một vùng có thể ĐÁNG TIN mà DANH TÍNH VẪN PHẢI GIỮ LẠI:

    REGION_TRUST = TRUSTED
    IDENTITY_LINK = WITHHELD          ⟵ trạng thái hợp lệ, không phải lỗi

⭐ NHÂN CHỨNG: Công nghệ 11 (chuyên đề) trang 25. «Hình 6.1. Một số loại động
vật cảnh phổ biến» là chú thích CHUNG cho BA ảnh riêng, mỗi ảnh có nhãn con IN
NGAY DƯỚI: «a) Chó Bắc Kinh lai Nhật», «b) Mèo Anh lông ngắn», «c) Gà tre Tân
Châu». Gán cả ba cùng một danh tính «Hình 6.1» thì không bịa, nhưng THÔ — và
đúng cái nhãn con bị mất mới là thứ trẻ cần: trẻ cần biết CON NÀO là mèo Anh.

Luật, theo đúng thứ tự Founder ra:

  1. KHÔNG BỊA danh tính hình con. Không tự sinh «Hình 6.1a».
  2. Nếu nhãn con CÓ IN và giữ được đúng nguyên văn ⇒ nối vào.
  3. Nếu không ⇒ `IDENTITY_LINK = WITHHELD`.
  4. Mất nhãn con mà làm ảnh hiện ra SAI LỆCH cho trẻ ⇒ không đưa vào dòng đọc.

«SAI TÊN > THIẾU TÊN» — tên sai tệ hơn thiếu tên.
"""
import re

# «a) Chó Bắc Kinh lai Nhật» · «b)» · «(c) Gà tre» — chữ cái đơn mở đầu dòng.
SUBLABEL = re.compile(r'^\s*[\(\[]?\s*([a-hjklmnđ])\s*[\)\.]\s*(.{0,80})$',
                      re.IGNORECASE)
SUB_GAP = 0.06            # nhãn con in ngay dưới ảnh, cùng khoảng cách chú thích

RESOLVED, WITHHELD, CONFLICT = 'RESOLVED', 'WITHHELD', 'CONFLICT'


def _overlap(a0, a1, b0, b1):
    return min(a1, b1) - max(a0, b0)


def sublabels(lines, block_lines=None):
    """Dòng NHÃN CON in trong sách, kèm hình học của chính dòng ấy.

    ⚠ Chỉ nhận dòng đứng trong KHỐI NGẮN (≤2 dòng) — hệt cổng chú thích. Một
    câu thân bài mở đầu bằng «b) Vì sao…» là ĐỀ BÀI, không phải nhãn ảnh.
    """
    out = []
    for l in lines:
        t = (l.get('text') or '').strip()
        if not t:
            continue
        if (block_lines or {}).get(id(l), 1) > 2:
            continue
        m = SUBLABEL.match(t)
        if not m:
            continue
        out.append(dict(letter=m.group(1).lower(), text=t, x=l['x'], y=l['y'],
                        w=l.get('w') or 0, h=l.get('h') or 0))
    return out


def sublabel_for(bbox, subs, cap=None):
    """Nhãn con in NGAY DƯỚI vùng, chồng ngang với nó, và NẰM TRÊN chú thích
    chung (nếu có) — vì nhãn con thuộc về ảnh, chú thích chung thuộc về cả cụm.
    """
    x, y, w, h = bbox
    best = None
    for s in subs:
        d = s['y'] - (y + h)
        if not (-0.01 <= d <= SUB_GAP):
            continue
        if _overlap(x, x + w, s['x'], s['x'] + s['w']) <= 0:
            continue
        if cap is not None and s['y'] > cap['y'] + 1e-9:
            continue                       # nằm dưới chú thích chung ⇒ không phải nhãn của ảnh này
        if best is None or d < best[0]:
            best = (d, s)
    return best[1] if best else None


def link(bbox, *, caption, shared, subs):
    """`(trạng thái, danh tính, lý do)` cho MỘT vùng đã được tin.

    `caption` = chú thích in kề bên (cổng tin cậy đã trả về).
    `shared`  = chú thích ấy đang được MẤY vùng cùng viện dẫn trên trang này.
    `subs`    = các nhãn con in trên trang.
    """
    if caption is None:
        return WITHHELD, None, 'vùng đáng tin nhưng không có chú thích để nối'
    if shared <= 1:
        return RESOLVED, dict(kind=caption.get('kind'), num=caption.get('num'),
                              text=caption.get('text'), sub=None), 'chú thích riêng của vùng'
    s = sublabel_for(bbox, subs, cap=caption)
    if s is None:
        # ⭐ KHÔNG tự sinh «Hình 6.1a». Không có nhãn in thì GIỮ LẠI danh tính.
        return WITHHELD, None, f'chú thích chung cho {shared} vùng, không có nhãn con in'
    return RESOLVED, dict(kind=caption.get('kind'), num=caption.get('num'),
                          text=caption.get('text'), sub=s['text']), 'nhãn con in trong sách'


def readable(region_trust, identity_state, *, shared):
    """Vùng có được vào DÒNG ĐỌC của trẻ không.

    Founder: «If losing the sublabel makes the displayed asset pedagogically
    misleading, WITHHOLD that asset from learner-facing Read.»

    Một MẢNH của cụm hình mà không nói được nó là mảnh nào thì hiện ra là sai
    lệch — giữ lại. Vùng có chú thích riêng thì luôn nối được, nên luật này chỉ
    chạm đúng vào cụm nhiều mảnh.
    """
    if region_trust != 'TRUSTED':
        return False
    if identity_state == RESOLVED:
        return True
    return False
