#!/usr/bin/env python3
"""CỔNG ATTACH — phụ thuộc dựng phải BỀN và TỰ KIỂM, không dựa vào trí nhớ.

    python3 tool/corpus/attach_gate.py            # kiểm
    python3 tool/corpus/attach_gate.py --generate # sinh phần còn thiếu

⭐ SỰ CỐ THẬT, 2026-09-09. Bộ attach đầy đủ (238 cuốn) nằm ở
`/private/tmp/wal-census/attach`. Máy khởi động lại ⇒ macOS xoá `/private/tmp`
⇒ bộ ấy BỐC HƠI. Chỗ mặc định trong repo chỉ có 39/238 cuốn. Chạy lại lệnh dựng
chuẩn lúc ấy sẽ sinh ra một pack NHỎ HƠN mà KHÔNG có lỗi nào: bài không có
attach chỉ bị đếm vào `NO_ATTACH` rồi bỏ qua trong im lặng.

Đúng kiểu hỏng đã làm lớp 3 tụt 232 → 44 bài trong khi cả ba bất biến đều ĐẠT.

Ba điều luật này bắt buộc:

  1. ĐẦU VÀO DỰNG CHUẨN KHÔNG BAO GIỜ NẰM Ở `/tmp`. Sinh ra và đọc từ
     `poc-out/`, nơi sống qua reboot.
  2. SO TẬP HỢP, KHÔNG SO SỐ ĐẾM. «Đủ 238 tệp» vẫn có thể là 238 cuốn SAI.
     Điều kiện là: TẬP MONG ĐỢI ⊆ TẬP ĐANG CÓ.
  3. KHÔNG HARD-CODE 238. Con số ấy là quan sát của hôm nay, không phải hằng số
     của sản phẩm. Suy ra từ chính sổ sách chuẩn — sách nào cần attach thì sổ
     sách nói, không phải tôi nói.
"""
import argparse
import glob
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
CURRICULUM = os.path.join(ROOT, 'poc-out', 'graph', 'curriculum-structure.json')
# Chỗ BỀN: trong repo, sống qua reboot. KHÔNG phải /tmp.
DEFAULT_ROOT = os.path.join(ROOT, 'poc-out', 'trusted-corpus', 'tc-v2', 'tc2-p1')


def expected_books(grade=None, curriculum=CURRICULUM):
    """Sách CẦN attach — suy từ sổ sách chuẩn, đúng cách bước dựng mục lục duyệt.

    Điều kiện trùng khít `build_lesson_index`: `docType == 'SGK'` và có ít nhất
    một bài mang số. Sổ sách đổi thì con số này đổi theo — đó là chủ ý.
    """
    with open(curriculum, encoding='utf-8') as fh:
        docs = json.load(fh)['documents']
    out = set()
    for d in docs:
        if d.get('docType') != 'SGK':
            continue
        if grade is not None and d.get('grade') != grade:
            continue
        if not any(l.get('number') is not None for l in (d.get('lessons') or [])):
            continue
        out.add(d['sourceDocumentId'])
    return out


def lesson_counts(curriculum=CURRICULUM):
    """`{sách: số bài trong sổ}` — để phát hiện attach CŨ so với sổ sách."""
    with open(curriculum, encoding='utf-8') as fh:
        docs = json.load(fh)['documents']
    return {d['sourceDocumentId']:
            sum(1 for l in (d.get('lessons') or []) if l.get('number') is not None)
            for d in docs}


def entry_problem(path, book, counts=None):
    """`None` = tệp attach dùng được. Ngược lại là LÝ DO nói thẳng."""
    try:
        with open(path, encoding='utf-8') as fh:
            d = json.load(fh)
    except (OSError, ValueError) as e:
        return f'không đọc được ({type(e).__name__})'
    if d.get('book') != book:
        return f'tệp mang tên sách khác: «{d.get("book")}»'
    if not (d.get('pages') or []):
        return 'không có trang nào'
    if counts is not None:
        want = counts.get(book)
        got = (d.get('counts') or {}).get('canonical_lesson_count')
        if want is not None and got is not None and want != got:
            return (f'CŨ so với sổ sách: attach dựng khi sổ có {got} bài, '
                    f'nay sổ có {want}')
    return None


def actual_books(attach_root=DEFAULT_ROOT, counts=None):
    """Sách có tệp attach DÙNG ĐƯỢC (không chỉ có mặt)."""
    out = set()
    for p in glob.glob(os.path.join(attach_root, 'attach', '*.json')):
        book = os.path.basename(p)[:-5]
        if entry_problem(p, book, counts) is None:
            out.add(book)
    return out


def verify(grade=None, attach_root=DEFAULT_ROOT, curriculum=CURRICULUM):
    """`[]` = đạt. Mỗi phần tử là một vi phạm, nói rõ vì sao.

    ⭐ SO TẬP HỢP. Đếm đủ mà sai cuốn thì vẫn là hỏng.
    """
    want = expected_books(grade, curriculum)
    counts = lesson_counts(curriculum)
    problems = []
    missing, broken = [], []
    for book in sorted(want):
        p = os.path.join(attach_root, 'attach', f'{book}.json')
        if not os.path.exists(p):
            missing.append(book)
            continue
        why = entry_problem(p, book, counts)
        if why:
            broken.append(f'{book}: {why}')
    if missing:
        problems.append(
            f'THIẾU ATTACH cho {len(missing)}/{len(want)} cuốn '
            f'(ví dụ {missing[:3]}) — dựng tiếp sẽ ra pack NHỎ HƠN mà không báo lỗi')
    if broken:
        problems.append(
            f'ATTACH HỎNG/CŨ ở {len(broken)} cuốn: {broken[:3]}')
    return problems


def generate(books, attach_root=DEFAULT_ROOT, log=print):
    """Sinh lại attach cho `books`. Tất định: cùng nguồn ⇒ cùng đầu ra."""
    sys.path.insert(0, HERE)
    import tc2_attach
    import tc2_paths
    tc2_paths.set_out_root(attach_root)
    ok, fail = [], []
    for b in sorted(books):
        try:
            tc2_attach.attach_book(b, write=True)
            ok.append(b)
        except Exception as e:                       # noqa: BLE001
            fail.append(f'{b}: {type(e).__name__}: {e}')
    if log:
        log(f'  sinh được {len(ok)} cuốn' + (f' · THẤT BẠI {len(fail)}' if fail else ''))
        for f in fail[:5]:
            log(f'    ✗ {f}')
    return ok, fail


def ensure(grade=None, attach_root=DEFAULT_ROOT, curriculum=CURRICULUM,
           log=print, only_missing=False):
    """Sinh lại attach rồi KIỂM LẠI. Trả về danh sách vi phạm còn lại.

    ⭐ MẶC ĐỊNH SINH LẠI TẤT CẢ, KHÔNG CHỈ CUỐN THIẾU.

    Bài học 2026-09-09: chỗ bền còn sót 39 tệp cũ từ một lượt dựng nào đó không
    ai truy được. Chúng qua được phép kiểm hợp lệ nên bị BỎ QUA, và kéo theo
    một bản dựng lệch: Vật lí 11 trong tệp cũ chỉ dò được 8/26 đầu bài, còn
    sinh lại từ nguồn hôm nay thì đủ 26. Một đầu vào dựng mà mỗi cuốn một đời
    thì không phải đầu vào tất định.

    Sinh lại cả 238 cuốn mất ~12 giây. Rẻ hơn nhiều so với một pack lệch.
    """
    want = expected_books(grade, curriculum)
    counts = lesson_counts(curriculum)
    todo = (want - actual_books(attach_root, counts)) if only_missing else want
    if todo:
        if log:
            log(f'  sinh attach cho {len(todo)}/{len(want)} cuốn từ nguồn chuẩn')
        generate(todo, attach_root, log=log)
    return verify(grade, attach_root, curriculum)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--grade', type=int, default=None)
    ap.add_argument('--root', default=DEFAULT_ROOT)
    ap.add_argument('--generate', action='store_true')
    a = ap.parse_args()
    problems = (ensure(a.grade, a.root) if a.generate
                else verify(a.grade, a.root))
    want = expected_books(a.grade)
    have = actual_books(a.root, lesson_counts())
    print(f'  mong đợi {len(want)} cuốn · dùng được {len(want & have)} · '
          f'thiếu {len(want - have)}')
    for p in problems:
        print(f'  ✗ {p}', file=sys.stderr)
    if problems:
        print('CỔNG ATTACH: KHÔNG ĐẠT', file=sys.stderr)
        return 1
    print('CỔNG ATTACH: ĐẠT')
    return 0


if __name__ == '__main__':
    sys.exit(main())
