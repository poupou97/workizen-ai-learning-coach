#!/usr/bin/env python3
"""ContentNode — CẤU TRÚC NGUỒN của một cuốn sách, không phải cách dạy.

⭐ RANH GIỚI (Founder): **SOURCE STRUCTURE ≠ PEDAGOGY.**
File này chỉ mô tả *sách được tổ chức thế nào*:

    Book → Unit/Theme/Week/Chapter/… → Lesson → Activity

Nó **không** quyết định dạy ra sao. Việc chọn Experience Pattern và Surface là
của Learning Experience Factory, và diễn ra ở mức **HOẠT ĐỘNG**, không phải ở
mức bài (xem `docs/research/SAM-LEARNING-EXPERIENCE-FACTORY.md` §4).

Vì sao không đóng cứng một cây: corpus đã bác bỏ điều đó.
  · Tiếng Việt : Sách → TUẦN  → Bài → (Đọc / Nói và nghe / Viết)
  · GDTC       : Sách → CHỦ ĐỀ → Bài  (số bài ĐÁNH LẠI mỗi chủ đề)
  · Khoa học   : Sách → CHỦ ĐỀ → Bài
  · Tiếng Anh  : Sách → UNIT

⭐ ĐỊNH DANH BỀN không được dựa vào số bài hiển thị. Nó dựa vào
**provenance nguồn + vị trí trong cây**: cùng một `sourceDocumentId`, cùng một
đường đi theo vai trò và thứ tự, cộng trang in khi có. Số bài chỉ là dữ liệu
HIỂN THỊ — GDTC có 5 bài mang số 1, Tiếng Việt đánh lại số bài mỗi tuần.
"""
import json
import sys

# Vai trò MÁY ĐỌC ĐƯỢC. Danh sách này còn được corpus bác bỏ/tinh chỉnh tiếp —
# thêm vai trò phải có bằng chứng từ sách thật, không thêm cho đẹp.
ROLES = ('BOOK', 'UNIT', 'THEME', 'WEEK', 'CHAPTER', 'TOPIC', 'LESSON',
         'ACTIVITY')

# Từ khoá mục lục (thứ đo được) → vai trò (thứ máy dùng).
_ROLE_OF_UNIT_KIND = {
    'bai': 'LESSON',
    'chuDe': 'THEME',
    'chuyenDe': 'TOPIC',
    'tuan': 'WEEK',
    'unit': 'UNIT',
}


class ContentNode:
    """Một nút cấu trúc nguồn. KHÔNG mang thông tin sư phạm nào."""

    __slots__ = ('role', 'number', 'title', 'page_start', 'children',
                 'source_document_id', 'ordinal')

    def __init__(self, role, source_document_id, ordinal, number=None,
                 title=None, page_start=None):
        if role not in ROLES:
            raise ValueError(f'vai trò lạ: {role}')
        self.role = role
        self.source_document_id = source_document_id
        self.ordinal = ordinal          # vị trí trong CÙNG cha, bắt đầu từ 1
        self.number = number            # số IN TRÊN SÁCH — chỉ để hiển thị
        self.title = title
        self.page_start = page_start
        self.children = []

    def add(self, child):
        child.ordinal = len(self.children) + 1
        self.children.append(child)
        return child

    def path(self, prefix=''):
        """Đường đi theo VAI TRÒ + THỨ TỰ — phần bền của định danh."""
        step = f'{self.role.lower()}:{self.ordinal}'
        return f'{prefix}/{step}' if prefix else step

    def stable_id(self, prefix=''):
        """`<sách>#<đường đi>[@trang in]`.

        Không dùng `number`: số bài lặp lại (GDTC 5 bài số 1) và đổi nghĩa theo
        họ sách. Trang in được thêm khi có, vì nó là toạ độ đo được và giúp
        định danh sống sót khi thứ tự đọc đổi nhẹ.
        """
        p = self.path(prefix)
        page = f'@{self.page_start}' if self.page_start is not None else ''
        return f'{self.source_document_id}#{p}{page}'

    def to_json(self, prefix=''):
        p = self.path(prefix)
        out = {'role': self.role, 'id': self.stable_id(prefix)}
        if self.number is not None:
            out['number'] = self.number      # HIỂN THỊ, không phải định danh
        if self.title:
            out['title'] = self.title
        if self.page_start is not None:
            out['pageStart'] = self.page_start
        if self.children:
            out['children'] = [c.to_json(p) for c in self.children]
        return out

    def walk(self, role=None):
        for c in self.children:
            if role is None or c.role == role:
                yield c
            yield from c.walk(role)


def build_tree(source_document_id, entries):
    """Dựng cây từ đầu ra của bộ đọc mục lục.

    Hai họ mục lục cho hai hình dạng khác nhau, và cả hai đều hợp lệ:
      · họ DANH SÁCH: «Chủ đề 1» mở một nhánh, các «Bài» sau đó là con của nó;
      · họ BẢNG    : mỗi dòng mang sẵn số TUẦN ⇒ nhóm bài theo tuần.
    Không có nhánh cha nào ⇒ bài treo thẳng dưới sách. Đó là trạng thái THẬT
    của nhiều cuốn, không phải lỗi.
    """
    root = ContentNode('BOOK', source_document_id, 1)
    parent = root
    week_nodes = {}

    for e in entries:
        role = _ROLE_OF_UNIT_KIND.get(e.get('unitKind'), 'LESSON')
        node = ContentNode(role, source_document_id, 0,
                           number=e.get('number'), title=e.get('title'),
                           page_start=e.get('pageStart'))
        if role != 'LESSON':
            parent = root.add(node)      # mở nhánh mới ở mức sách
            continue

        week = e.get('week')
        if week is not None:
            key = ('WEEK', week)
            if key not in week_nodes:
                week_nodes[key] = root.add(
                    ContentNode('WEEK', source_document_id, 0, number=week))
            week_nodes[key].add(node)
        else:
            parent.add(node)
    return root


def main():
    """In cây của một cuốn — để mắt người soi được cấu trúc máy đọc ra."""
    sys.path.insert(0, 'tool/corpus')
    from toc_columns import parse_book

    ocr_dir = sys.argv[1]
    sid = ocr_dir.rstrip('/').split('/')[-1]
    entries, used = parse_book(ocr_dir, tuple(int(a) for a in sys.argv[2:]))
    tree = build_tree(sid, entries)
    print(f'{sid} · trang mục lục dùng: {used}')

    def show(n, depth=0):
        if depth:
            num = '' if n.number is None else f' {n.number}'
            page = '' if n.page_start is None else f' · tr.{n.page_start}'
            print(f"{'  ' * depth}{n.role}{num}{page} · {(n.title or '')[:44]}")
        for c in n.children:
            show(c, depth + 1)

    show(tree)
    lessons = list(tree.walk('LESSON'))
    print(f'\n{len(lessons)} LESSON · định danh mẫu: '
          f'{lessons[0].stable_id() if lessons else "—"}')


if __name__ == '__main__':
    main()
