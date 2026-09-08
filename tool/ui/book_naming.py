#!/usr/bin/env python3
"""TÊN SÁCH TRÊN GIÁ — đủ để trẻ phân biệt hai cuốn khác nhau.

Đo trên máy thật (lớp 11, giá sách của Founder): hai ô cạnh nhau đều ghi
«Công nghệ 11 · CÔNG NGHỆ CHĂN NUÔI · 14 bài» và «… · 22 bài». Đó là HAI CUỐN
KHÁC NHAU — một là SGK, một là Chuyên đề học tập — nhưng tên hiện ra y hệt.

Đếm toàn tập: 18 cuốn không phân biệt được bằng tên.

  15 cuốn mang dấu hiệu bộ «chuyen-de-hoc-tap» trong định danh mà tên không
     nói ra: 9 cuốn mất chữ «Chuyên đề», 6 cuốn mất luôn TÊN MÔN («Chuyên đề
     11» cho hai cuốn Tin học).
   3 cuốn có `-tap-N` trong định danh mà `volumeLabel` rỗng (Tiếng Anh 3, 6) —
     registry chỉ đọc `volume` khi định danh KẾT THÚC ở đó, nên
     `…-tap-1-global-success` không được nhận.

⭐ KHÔNG SUY DẤU TIẾNG VIỆT TỪ SLUG. `tin-hoc` → «Tin học» ở đây KHÔNG phải
suy ra chữ: nó lấy nguyên `subject` CÓ DẤU của cuốn anh em cùng lõi định danh
trong chính dữ liệu. Không có cuốn anh em ⇒ GIỮ NGUYÊN TÊN CŨ, không đặt tên
mới. «Thiếu tên» còn sửa được; «sai tên» thì trẻ tin nhầm.
"""
import re
import unicodedata

SERIES_SLUG = 'chuyen-de-hoc-tap'
SERIES_LABEL = 'Chuyên đề'

_ID = re.compile(r'^\d{2}-sgk-(?:' + SERIES_SLUG + r'-)?(.+?)-(\d{1,2})(?:-.+)?$')
_VOLUME = re.compile(r'-tap-(\d{1,2})(?:-|$)')


def fold(s):
    s = unicodedata.normalize('NFD', (s or '').lower())
    return re.sub(r'[̀-ͯ]', '', s).replace('đ', 'd').replace(' ', '-')


def has_series(sid):
    """Cuốn thuộc bộ «Chuyên đề học tập» — đọc từ định danh, không đoán."""
    return f'-{SERIES_SLUG}-' in f'-{sid or ""}'


def core_of(sid):
    """Lõi định danh: phần MÔN, đã bỏ dấu hiệu bộ và số lớp. `None` nếu lạ."""
    m = _ID.match(sid or '')
    return m.group(1) if m else None


def volume_label(sid):
    """«Tập N» khi định danh nói ra, kể cả khi còn đuôi phía sau."""
    m = _VOLUME.search(sid or '')
    return f'Tập {int(m.group(1))}' if m else None


def subject_names_by_core(books):
    """`{lõi: tên môn CÓ DẤU}` lấy từ cuốn KHÔNG thuộc bộ Chuyên đề.

    Chỉ nhận khi tên môn gấp lại khớp chính lõi ấy — hai nguồn độc lập phải
    đồng ý, đúng luật đã dùng cho nhãn phân môn.
    """
    out = {}
    for b in books:
        sid = b.get('sourceDocumentId')
        if has_series(sid):
            continue
        core = core_of(sid)
        subj = b.get('subject')
        if not core or not subj or core in out:
            continue
        if fold(subj) == core:
            out[core] = subj
    return out


def display_title(sid, title, grade, names_by_core):
    """Tên hiện trên giá. Trả lại chính `title` khi không chứng minh được gì."""
    title = (title or '').strip()
    if not has_series(sid):
        return title
    if title.startswith(SERIES_LABEL + ' ·'):
        return title                      # đã nói ra bộ rồi
    if title == f'{SERIES_LABEL} {grade}':
        # Tên môn bị nuốt mất — chỉ lấy lại được nếu có cuốn anh em cùng lõi.
        name = names_by_core.get(core_of(sid))
        return f'{SERIES_LABEL} · {name} {grade}' if name else title
    return f'{SERIES_LABEL} · {title}' if title else title
