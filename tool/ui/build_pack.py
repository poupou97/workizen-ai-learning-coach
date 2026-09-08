#!/usr/bin/env python3
"""ĐƯỜNG DỰNG PACK DUY NHẤT — chữ và hình ra cùng một lần, hoặc không ra.

    python3 tool/ui/build_pack.py 6            # dựng một lớp
    python3 tool/ui/build_pack.py --all
    python3 tool/ui/build_pack.py 6 --verify   # chỉ kiểm, không dựng

LỖI TOÀN VẸN ĐÃ GẶP: `build_lesson_index.py` sinh lại `lessonReadings.content`
mà KHÔNG có mục hình; hình chỉ quay lại khi ai đó nhớ chạy tiếp
`build_lesson_figures.py`. Đã xảy ra thật: dựng lại mục lục lớp 10–12 xong,
`L1-M` tụt về 0 hình cho ba lớp ấy mà không có lỗi nào, không có cảnh báo nào.

Một bước dựng KHÔNG được âm thầm làm giảm năng lực của bước khác. Ở đây phụ
thuộc ấy được MÃ HOÁ (index → figures), không dựa vào trí nhớ của người chạy.

⭐ BẤT BIẾN KIỂM ĐƯỢC, KHÔNG PHẢI NGƯỠNG ƯỚC LỆ:

  1. Pack có kho hình (DB có ≥1 hình cho lớp này) mà mục lục KHÔNG có bài nào
     mang hình  ⇒  FAIL. Đây đúng là dấu vết của «đã dựng lại index, quên hình».
  2. Mọi mục hình trong `content` phải TỒN TẠI trong kho hình của lớp ấy ⇒
     không có tham chiếu treo, không có ô ảnh vỡ trên máy trẻ.
  3. Pack tự khai `figuresPending` (bước index đặt, bước figures xoá) ⇒ FAIL.
     Cờ này bắt được cả trường hợp kho hình chưa từng tồn tại, nơi phép đếm ở
     (1) không có gì để so.

Hình trong kho mà không bài nào dùng thì KHÔNG bị coi là lỗi: đó là hình của
những bài bị giữ lại vì thiếu bằng chứng, nằm im và vô hại.

Ngưỡng phần trăm bị cố ý tránh: «giảm dưới 10% thì cho qua» là một cánh cửa để
mất dữ liệu im lặng.
"""
import argparse
import json
import os
import sqlite3
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
PACK_DIR = os.path.join(ROOT, 'assets', 'pack')
FIG_DIR = os.path.join(ROOT, 'poc-out', 'packs', 'figures')


def index_path(grade, pack_dir=PACK_DIR):
    return os.path.join(pack_dir, f'lesson-index-g{grade}.json')


def figures_path(grade, fig_dir=FIG_DIR):
    return os.path.join(fig_dir, f'figures-g{grade}.db')


def figure_ids(grade, fig_dir=FIG_DIR):
    """Id hình có trong kho của lớp. `None` = lớp chưa có kho (hợp lệ)."""
    p = figures_path(grade, fig_dir)
    if not os.path.exists(p):
        return None
    try:
        db = sqlite3.connect(f'file:{p}?mode=ro', uri=True)
        try:
            return {r[0] for r in db.execute('SELECT id FROM fig')}
        finally:
            db.close()
    except sqlite3.Error:
        return None


def pack_shape(grade, pack_dir=PACK_DIR):
    """Hình dạng năng lực của pack — thứ bất biến so sánh."""
    p = index_path(grade, pack_dir)
    if not os.path.exists(p):
        return dict(openable=0, with_images=0, images=0, image_ids=set(),
                    distinct=0, lessons=set(), pending=False)
    with open(p, encoding='utf-8') as fh:
        d = json.load(fh)
    rs = d.get('lessonReadings') or []
    ids, with_img = set(), 0
    for r in rs:
        imgs = [i for i in (r.get('content') or []) if i.get('t') == 'img']
        if imgs:
            with_img += 1
        ids.update(i.get('id') for i in imgs if i.get('id'))
    # ⚠ NĂNG LỰC ĐO BẰNG BÀI PHÂN BIỆT ĐƯỢC, KHÔNG PHẢI SỐ BẢN GHI.
    # Bản ghi trùng nhau y hệt (cùng sách, cùng số bài, cùng dải) không cho trẻ
    # thêm gì. Đo được: một lần dựng bỏ đi bản ghi trùng của Tin học 5 Bài 8
    # (38–49) làm số bản ghi tụt 252 → 251, trong khi số bài mở được KHÔNG đổi.
    # Đếm theo bản ghi thì việc dọn trùng đọc ra thành mất năng lực.
    return dict(openable=len(rs), with_images=with_img, images=len(ids),
                image_ids=ids, pending=bool(d.get('figuresPending')),
                distinct=len({(r.get('book'), r.get('lesson'),
                               r.get('pagePdfStart')) for r in rs}),
                lessons={(r.get('book'), r.get('lesson')) for r in rs})


def unrouted_books(grade, pack_dir=PACK_DIR):
    """Sách trên giá mà bấm vào KHÔNG ra mục lục nào.

    Giá sách mở màn theo `books[].subject`; mục lục nằm trong `subjects[môn]`.
    Hai chỗ lệch nhau thì cuốn ấy hiện đủ bìa, đủ «N bài», bấm vào ra màn rỗng.
    Đã xảy ra thật: Tin học 11 và 12, 60 bài, không lỗi nào báo.
    """
    p = index_path(grade, pack_dir)
    if not os.path.exists(p):
        return []
    with open(p, encoding='utf-8') as fh:
        d = json.load(fh)
    holders = {}
    for subj, blist in (d.get('subjects') or {}).items():
        for bl in blist:
            holders.setdefault(bl.get('sourceDocumentId'), set()).add(subj)
    return [b for b in (d.get('books') or [])
            if b.get('subject') not in holders.get(b.get('sourceDocumentId'), set())]


def ambiguous_books(grade, pack_dir=PACK_DIR):
    """Nhóm ≥2 cuốn KHÁC NHAU mà tên hiện trên giá giống hệt nhau."""
    p = index_path(grade, pack_dir)
    if not os.path.exists(p):
        return []
    with open(p, encoding='utf-8') as fh:
        d = json.load(fh)
    seen = {}
    for b in (d.get('books') or []):
        key = (b.get('title'), b.get('volumeLabel'), b.get('variantLabel'))
        seen.setdefault(key, []).append(b.get('sourceDocumentId'))
    return [(k, v) for k, v in sorted(seen.items(), key=lambda kv: str(kv[0]))
            if len(v) > 1]


def verify(grade, pack_dir=PACK_DIR, fig_dir=FIG_DIR):
    """`[]` = đạt. Mỗi phần tử là một vi phạm bất biến, nói rõ vì sao."""
    problems = []
    shape = pack_shape(grade, pack_dir)
    store = figure_ids(grade, fig_dir)

    for b in unrouted_books(grade, pack_dir):
        problems.append(
            f'lớp {grade}: «{b.get("title")}» ({b.get("sourceDocumentId")}) lên '
            f'giá dưới môn «{b.get("subject")}» nhưng mục lục KHÔNG nằm ở môn '
            f'ấy — bấm vào ra màn rỗng')

    if shape.get('pending'):
        problems.append(
            f'lớp {grade}: pack tự khai `figuresPending` — mới dựng chữ, chưa '
            f'nạp hình. Chạy `build_pack.py {grade}`, đừng chạy lẻ index.')

    if store is None:
        # Lớp chưa dựng kho hình là hợp lệ — nhưng khi ấy mục lục cũng không
        # được mang mục hình nào, nếu không là tham chiếu treo.
        if shape['images']:
            problems.append(
                f'lớp {grade}: mục lục có {shape["images"]} mục hình nhưng '
                f'KHÔNG có kho hình — mọi ô ảnh sẽ trống trên máy trẻ')
        return problems

    if store and shape['with_images'] == 0 and shape['openable']:
        problems.append(
            f'lớp {grade}: kho có {len(store)} hình nhưng KHÔNG bài nào mang '
            f'hình trong dòng đọc — dấu vết của «dựng lại index, quên hình»')

    dangling = shape['image_ids'] - store
    if dangling:
        problems.append(
            f'lớp {grade}: {len(dangling)} mục hình không có trong kho '
            f'(ví dụ {sorted(dangling)[:2]}) — ô ảnh vỡ')
    return problems


def _run(script, *args):
    cmd = [sys.executable, os.path.join(HERE, script), *map(str, args)]
    r = subprocess.run(cmd, cwd=ROOT)
    if r.returncode != 0:
        raise SystemExit(f'{script} thất bại (mã {r.returncode}) — dừng, '
                         f'không để pack ở trạng thái dở dang')


def build(grade, attach_root=None):
    if attach_root:
        os.environ['ATTACH_ROOT'] = attach_root
    # Nói cho bước index biết nó đang chạy TRONG đường dựng, để nó không phải
    # cảnh báo người dùng về một thứ orchestrator đã lo.
    os.environ['WAL_PACK_ORCHESTRATED'] = '1'
    # THỨ TỰ LÀ MỘT PHỤ THUỘC, KHÔNG PHẢI THÓI QUEN: index sinh lại `content`
    # rỗng hình, figures nạp hình vào lại. Chạy lẻ bước đầu là mất hình.
    _run('build_lesson_index.py', grade)
    _run('build_lesson_figures.py', grade)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('grades', nargs='*', type=int)
    ap.add_argument('--all', action='store_true')
    ap.add_argument('--verify', action='store_true', help='chỉ kiểm bất biến')
    ap.add_argument('--attach', default=None)
    a = ap.parse_args()

    grades = list(range(1, 13)) if a.all else (a.grades or [])
    if not grades:
        ap.error('cần số lớp, hoặc --all')

    bad = []
    for g in grades:
        if not a.verify:
            before = pack_shape(g)
            build(g, a.attach)
            after = pack_shape(g)
            if before['with_images'] and not after['with_images']:
                bad.append(f'lớp {g}: TRƯỚC có {before["with_images"]} bài mang hình, '
                           f'SAU còn 0 — bước dựng làm mất năng lực')
            # ⭐ MẤT BÀI CŨNG LÀ MẤT NĂNG LỰC, KHÔNG CHỈ MẤT HÌNH.
            # Đã xảy ra thật (2026-09-08): dựng lại lớp 3 và 6 mà QUÊN
            # `--attach` ⇒ mọi sách rơi vào `NO_ATTACH`, lớp 3 tụt 232 → 44 bài.
            # Ba bất biến cũ đều ĐẠT: không hình treo, không cờ pending, kho
            # hình vẫn có bài dùng. Pack «hợp lệ» mà mất 80% số bài của trẻ.
            if after['distinct'] < before['distinct']:
                bad.append(
                    f'lớp {g}: TRƯỚC {before["distinct"]} bài mở được, SAU '
                    f'{after["distinct"]} — bước dựng làm TỤT. Kiểm `--attach` '
                    f'trước khi tin con số mới.')
        bad += verify(g)

    for b in bad:
        print(f'  ✗ {b}', file=sys.stderr)
    if bad:
        print(f'\nBẤT BIẾN PACK KHÔNG ĐẠT ({len(bad)}). '
              f'Pack ở trạng thái này sẽ mất hình trên máy trẻ.', file=sys.stderr)
        return 1
    for g in grades:
        s = pack_shape(g)
        # Tên trùng KHÔNG phải lỗi dựng: 9 cuốn cố ý không có nhãn phân biệt vì
        # bìa không xác minh chéo được. Nhưng phải ĐẾM ĐƯỢC, không im lặng.
        amb = ambiguous_books(g)
        note = f' · ⚠ {sum(len(v) for _, v in amb)} cuốn trùng tên' if amb else ''
        print(f'  lớp {g:>2}: {s["openable"]:>4} bài mở được · '
              f'{s["with_images"]:>4} bài có hình · {s["images"]:>5} hình{note}')
    print('BẤT BIẾN PACK: ĐẠT')
    return 0


if __name__ == '__main__':
    sys.exit(main())
