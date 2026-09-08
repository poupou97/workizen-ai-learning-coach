#!/usr/bin/env python3
"""DÒNG ĐỌC — cấu trúc của nguồn phải đi tới pack NGUYÊN VẸN và ĐÚNG THỨ TỰ.

Lỗi đã sửa: `interleave` dính mọi khối chữ liền nhau thành một
(`stream[-1]['v'] += ...`). Đo toàn corpus: nguồn 215.714 khối, pack 14.119
(6,5%), 16.680 tiêu đề mục mất sạch, và 2.944/2.944 bài đều có «số khối chữ ≤
số ảnh + 1» — dòng đọc chỉ bị cắt ở chỗ chèn ảnh, chưa bao giờ theo đoạn.

⛔ «Pack có nhiều hơn một đoạn» KHÔNG phải bằng chứng giữ được cấu trúc: một
bản sửa cắt bừa chuỗi phẳng ra làm mười cũng qua được phép thử ấy. Nên ở đây
đo SO KHỚP NGUỒN → PACK.
"""
import importlib.util
import os
import sys
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(HERE, '..', 'corpus'))
import read_structure as rs  # noqa: E402

_spec = importlib.util.spec_from_file_location(
    'blf', os.path.join(ROOT, 'tool', 'ui', 'build_lesson_figures.py'))
blf = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(blf)


def _page(pdf, paras, ):
    """`paras` = [(seq, y, text)]."""
    return dict(pagePdf=pdf,
                paragraphs=[dict(seq=s, y=y, text=t) for s, y, t in paras])


def _fig(fid, y, page):
    return dict(id=fid, bbox=(0.1, y, 0.5, 0.2), w=640, h=400, page=page,
                caption=None)


def _kinds(stream):
    return [i['t'] for i in stream]


def _texts(stream):
    return [i.get('v') or i.get('id') for i in stream]


class Preservation(unittest.TestCase):

    def test_hai_khoi_chu_lien_nhau_KHONG_bi_dinh_lam_mot(self):
        p = _page(1, [(0, 0.1, 'Đoạn một.'), (1, 0.3, 'Đoạn hai.')])
        stream = blf.interleave([p], {})
        self.assertEqual(_texts(stream), ['Đoạn một.', 'Đoạn hai.'])

    def test_tieu_de_muc_cua_sach_duoc_danh_dau(self):
        p = _page(1, [(0, 0.1, 'I. MỞ ĐẦU'), (1, 0.2, 'Thân bài ở đây.'),
                      (2, 0.3, '2. Con lắc đơn'), (3, 0.4, 'a) Trường hợp một')])
        self.assertEqual(_kinds(blf.interleave([p], {})),
                         ['heading', 'text', 'heading', 'heading'])

    def test_KHONG_bia_cap_bac_cho_tieu_de(self):
        # Parser chỉ biết «đây là một mục». Không có h1/h2/h3 trong dòng đọc.
        p = _page(1, [(0, 0.1, 'I. MỞ ĐẦU')])
        self.assertEqual(set(blf.interleave([p], {})[0]), {'t', 'v'})


class Ordering(unittest.TestCase):
    """⭐ Bốn ca Founder yêu cầu + thứ tự đọc không được thua thứ tự y."""

    def test_chi_co_chu(self):
        p = _page(1, [(0, 0.1, 'A'), (1, 0.5, 'B')])
        self.assertEqual(_texts(blf.interleave([p], {})), ['A', 'B'])

    def test_chu_roi_MOT_hinh(self):
        p = _page(1, [(0, 0.1, 'A')])
        s = blf.interleave([p], {1: [_fig('f1', 0.5, 1)]})
        self.assertEqual(_texts(s), ['A', 'f1'])

    def test_hinh_nam_GIUA_hai_doan(self):
        p = _page(1, [(0, 0.1, 'A'), (1, 0.8, 'B')])
        s = blf.interleave([p], {1: [_fig('f1', 0.4, 1)]})
        self.assertEqual(_texts(s), ['A', 'f1', 'B'])

    def test_NHIEU_hinh_giu_dung_thu_tu_theo_y(self):
        p = _page(1, [(0, 0.1, 'A'), (1, 0.9, 'B')])
        s = blf.interleave([p], {1: [_fig('f2', 0.7, 1), _fig('f1', 0.3, 1)]})
        self.assertEqual(_texts(s), ['A', 'f1', 'f2', 'B'])

    def test_tieu_de_roi_chu_roi_hinh(self):
        p = _page(1, [(0, 0.1, 'I. MỞ ĐẦU'), (1, 0.2, 'Thân bài.')])
        s = blf.interleave([p], {1: [_fig('f1', 0.6, 1)]})
        self.assertEqual(_kinds(s), ['heading', 'text', 'img'])

    def test_hinh_khong_co_khoi_nao_o_tren_thi_mo_dau_trang(self):
        p = _page(1, [(0, 0.5, 'A')])
        s = blf.interleave([p], {1: [_fig('f1', 0.1, 1)]})
        self.assertEqual(_texts(s), ['f1', 'A'])

    def test_NHIEU_TRANG_giu_dung_thu_tu_trang(self):
        p1 = _page(1, [(0, 0.1, 'A')])
        p2 = _page(2, [(0, 0.1, 'B')])
        s = blf.interleave([p1, p2], {1: [_fig('f1', 0.5, 1)],
                                      2: [_fig('f2', 0.5, 2)]})
        self.assertEqual(_texts(s), ['A', 'f1', 'B', 'f2'])

    def test_CHU_theo_DAI_DOC_chu_khong_theo_Y(self):
        # ⭐ Lỗi #141: xếp khối theo y thuần làm khung phụ chen vào giữa câu.
        # Khung phụ (`seq` 2) nằm CAO hơn đoạn thứ hai (`seq` 1) trên trang.
        p = _page(1, [(0, 0.10, 'Câu mở đầu'),
                      (1, 0.60, 'câu tiếp theo của cùng một mạch'),
                      (2, 0.30, 'KHUNG PHỤ bên lề')])
        self.assertEqual(
            _texts(blf.interleave([p], {})),
            ['Câu mở đầu', 'câu tiếp theo của cùng một mạch', 'KHUNG PHỤ bên lề'])


class Alignment(unittest.TestCase):
    """Phép đo của `STRUCTURED_READ` — bám vào khối của NGUỒN."""

    def test_giu_nguyen_ven_thi_preserved_bang_source(self):
        src = ['A', 'B', 'C']
        pack = [dict(t='text', v='A'), dict(t='img', id='f'),
                dict(t='text', v='B'), dict(t='text', v='C')]
        self.assertEqual(rs.align(src, pack),
                         dict(source=3, preserved=3, merged=0, dropped=0,
                              order_violations=0))

    def test_dinh_hai_khoi_lam_mot_bi_dem_la_MERGED(self):
        src = ['A', 'B']
        pack = [dict(t='text', v='A B')]
        got = rs.align(src, pack)
        self.assertEqual(got['merged'], 2)
        self.assertEqual(got['preserved'], 0)

    def test_mat_khoi_bi_dem_la_DROPPED(self):
        self.assertEqual(rs.align(['A', 'B'], [dict(t='text', v='A')])['dropped'], 1)

    def test_khoi_TRUNG_NOI_DUNG_khong_sinh_vi_pham_thu_tu_gia(self):
        # Nhãn trục «-A» xuất hiện hai lần trong cùng một bài — có thật.
        src = ['-A', 'giữa', '-A']
        pack = [dict(t='text', v='-A'), dict(t='text', v='giữa'),
                dict(t='text', v='-A')]
        self.assertEqual(rs.align(src, pack)['order_violations'], 0)

    def test_dao_thu_tu_that_thi_BI_BAT(self):
        src = ['A', 'B']
        pack = [dict(t='text', v='B'), dict(t='text', v='A')]
        self.assertEqual(rs.align(src, pack)['order_violations'], 1)

    def test_cat_bua_chuoi_phang_KHONG_qua_duoc_phep_do(self):
        # ⛔ Chống gaming: cắt một khối nguồn ra làm ba đoạn giả.
        src = ['Một câu dài liền mạch của sách giáo khoa']
        pack = [dict(t='text', v='Một câu dài'), dict(t='text', v='liền mạch của'),
                dict(t='text', v='sách giáo khoa')]
        got = rs.align(src, pack)
        self.assertEqual(got['preserved'], 0)
        self.assertEqual(got['dropped'], 1)


if __name__ == '__main__':
    unittest.main()
