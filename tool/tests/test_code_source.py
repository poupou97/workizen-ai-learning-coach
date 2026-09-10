#!/usr/bin/env python3
"""WAL-239 — mã nguồn giữ nguyên DÒNG, và CHỈ mã nguồn.

Hai nửa của bộ test này quan trọng ngang nhau:

  * mã nguồn phải giữ được dòng · nội dung · thụt lề đo được
  * VĂN XUÔI KHÔNG ĐƯỢC ĐỔI MỘT CHỮ — Founder: «fixing code MUST NOT globally
    preserve arbitrary OCR newlines in normal prose and damage Read UX.»
"""
import os
import sys
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, 'tool', 'corpus'))

import code_source as cs                      # noqa: E402
from lesson_reading import page_paragraphs    # noqa: E402


def L(x, y, w, text, h=0.012):
    return dict(x=x, y=y, w=w, h=h, text=text)


#: Một chương trình in kèm CỘT SỐ DÒNG RIÊNG ở lề trái — ca `code_poc._gutter`
#: bóc được, nên thụt lề đo được.
COT_SO_RIENG = [
    L(0.145, 0.300, 0.010, '1'), L(0.170, 0.300, 0.250, 'def f(n) :'),
    L(0.145, 0.320, 0.010, '2'), L(0.210, 0.320, 0.180, 'if n == 0:'),
    L(0.145, 0.340, 0.010, '3'), L(0.250, 0.340, 0.150, 'return 1'),
    L(0.145, 0.360, 0.010, '4'), L(0.210, 0.360, 0.200, 'return n * f(n-1)'),
]
VUNG = [0.140, 0.290, 0.300, 0.090]


class GiuDongMaNguon(unittest.TestCase):

    def test_dung_lai_dong_thu_tu_va_thut_le(self):
        text, why = cs.code_text(COT_SO_RIENG, VUNG)
        self.assertEqual(why, 'OK_BO_COT_SO_DONG')
        # SỐ DÒNG IN được in lại — nó là chữ của sách, không phải rác bố cục.
        self.assertEqual(text.split('\n'), [
            '1 def f(n) :',
            '2     if n == 0:',
            '3         return 1',
            '4     return n * f(n-1)'])

    def test_so_dong_IN_khong_duoc_mat(self):
        """Bóc cột số để ĐO thụt lề thì phải TRẢ LẠI. Đo được: 32 trang hụt
        đúng các chữ số ấy trước khi sửa."""
        text, _ = cs.code_text(COT_SO_RIENG, VUNG)
        for n in ('1', '2', '3', '4'):
            self.assertTrue(any(ln.startswith(n + ' ') for ln in text.split('\n')),
                            f'mất số dòng {n}')

    def test_so_dong_canh_PHAI_theo_so_rong_nhat(self):
        lines = []
        for i, code in enumerate(['a = 1', 'b = 2', 'c = 3', 'd = 4',
                                  'e = 5', 'f = 6', 'g = 7', 'h = 8',
                                  'i = 9', 'j = 10', 'k = 11']):
            y = 0.30 + i * 0.005
            lines.append(L(0.145, y, 0.012, str(i + 1), h=0.004))
            lines.append(L(0.200, y, 0.10, code, h=0.004))
        text, _ = cs.code_text(lines, [0.14, 0.29, 0.30, 0.09])
        got = text.split('\n')
        self.assertEqual(got[0], ' 1 a = 1')
        self.assertEqual(got[10], '11 k = 11')

    def test_noi_dung_khong_bi_dung_vao(self):
        """Ký tự của sách phải sang y nguyên — kể cả chỗ trông như lỗi in."""
        lines = [L(0.20, 0.30, 0.30, '>>> a,b = 10,3'),
                 L(0.20, 0.32, 0.30, '>>> print(a//b, a%b)')]
        text, _ = cs.code_text(lines, VUNG)
        self.assertIn('>>> a,b = 10,3', text)
        self.assertIn('>>> print(a//b, a%b)', text)

    def test_so_dong_GỘP_vào_dòng_mã_thì_BỎ_thụt_lề(self):
        """`UNKNOWN != VALID`. Đoán thụt lề Python là đổi chương trình."""
        lines = [L(0.155, 0.300, 0.30, '1 def g(n):'),
                 L(0.155, 0.320, 0.30, '2 return n'),
                 L(0.155, 0.340, 0.30, '3 print(g(2))')]
        text, why = cs.code_text(lines, VUNG)
        self.assertEqual(why, 'THUT_LE_KHONG_DO_DUOC')
        self.assertEqual(text.split('\n'),
                         ['1 def g(n):', '2 return n', '3 print(g(2))'])
        self.assertNotIn('    ', text)

    def test_it_dong_qua_thi_KHONG_dung(self):
        self.assertEqual(cs.code_text([L(0.2, 0.3, 0.3, 'print(1)')], VUNG)[0], None)

    def test_mot_dong_chi_thuoc_MOT_vung(self):
        """Chồng vùng không được làm chữ hiện hai lần."""
        a = [0.140, 0.290, 0.300, 0.090]
        b = [0.140, 0.290, 0.320, 0.100]
        outside, groups = cs.owned_lines(COT_SO_RIENG, [a, b])
        self.assertEqual(len(groups[0][1]), 8)
        self.assertEqual(groups[1][1], [])
        self.assertEqual(outside, [])


class VanXuoiKhongDuocDoi(unittest.TestCase):

    PROSE = [L(0.10, 0.20, 0.80, 'Thuật toán duyệt đồ thị theo chiều rộng được'),
             L(0.10, 0.22, 0.80, 'thiết kế gần giống bản không đệ quy.')]

    def test_khong_co_vung_ma_thi_giong_het_duong_cu(self):
        lines = self.PROSE + COT_SO_RIENG
        self.assertEqual(page_paragraphs(lines), page_paragraphs(lines, code_regions=()))

    def test_chu_ngoai_vung_khong_bi_ngat_dong(self):
        got = page_paragraphs(self.PROSE + COT_SO_RIENG, code_regions=[VUNG])
        van = [q for q in got if q.get('kind') != 'code']
        self.assertTrue(van, 'văn xuôi phải còn')
        for q in van:
            self.assertNotIn('\n', q['text'])

    def test_ma_thanh_MOT_doan_rieng_mang_nhan_code(self):
        got = page_paragraphs(self.PROSE + COT_SO_RIENG, code_regions=[VUNG])
        code = [q for q in got if q.get('kind') == 'code']
        self.assertEqual(len(code), 1)
        self.assertEqual(code[0]['text'].count('\n'), 3)

    def test_khong_dung_duoc_thi_TRA_CHU_VE_khong_nuot_mat(self):
        """Vùng chỉ ôm một dòng ⇒ `code_paragraph` trả None. Chữ vẫn phải còn."""
        mot = [L(0.20, 0.30, 0.30, 'print(1)')]
        got = page_paragraphs(self.PROSE + mot, code_regions=[VUNG])
        self.assertEqual([q for q in got if q.get('kind') == 'code'], [])
        self.assertIn('print(1)', ' '.join(q['text'] for q in got))

    def test_thu_tu_doc_giu_nguyen(self):
        """Khối mã phải đứng đúng chỗ nó đứng trên trang, không dồn xuống cuối."""
        sau = [L(0.10, 0.50, 0.80, 'Đoạn chương trình trên cho kết quả 6.')]
        got = sorted(page_paragraphs(self.PROSE + COT_SO_RIENG + sau,
                                     code_regions=[VUNG]), key=lambda q: q['seq'])
        kinds = [q.get('kind') or 'van' for q in got]
        self.assertEqual(kinds.index('code'), 1, f'thứ tự sai: {kinds}')


class ChotHaiCot(unittest.TestCase):
    """Trang mã kèm CỘT CHÚ GIẢI bên phải — lỗi do chính bản vá sinh ra."""

    HAI_COT = [
        L(0.208, 0.067, 0.155, 'if k >= len (T):'),
        L(0.637, 0.067, 0.259, 'Bước 2. Thực hiện thao tác'),
        L(0.249, 0.086, 0.375, 'T.extend( [None]* (k - len(T) + 1))'),
        L(0.622, 0.086, 0.066, '- chèn,'),
        L(0.208, 0.106, 0.086, 'T[k] = v'),
        L(0.635, 0.103, 0.063, 'thứ k.'),
    ]

    def test_nhan_ra_cot_thu_hai_va_KHONG_dung_khoi(self):
        self.assertTrue(cs.two_column(self.HAI_COT))
        text, why = cs.code_text(self.HAI_COT, [0.145, 0.060, 0.755, 0.060])
        self.assertIsNone(text)
        self.assertEqual(why, 'HAI_COT')

    def test_ma_sach_mot_cot_KHONG_bi_bat_nham(self):
        self.assertFalse(cs.two_column(COT_SO_RIENG))

    def test_COT_SO_DONG_khong_bi_nham_la_cot_thu_hai(self):
        """Chốt từng bắt nhầm 50,9% số vùng vì cột số dòng cũng để lại khe lặp."""
        so_dong = []
        for i, code in enumerate(['def f(n) :', 'if n == 0:', 'return 1', 'return n']):
            y = 0.30 + i * 0.02
            so_dong.append(L(0.145, y, 0.010, str(i + 1)))
            so_dong.append(L(0.230, y, 0.20, code))
        self.assertFalse(cs.two_column(so_dong))

    def test_can_le_thua_MOT_LAN_khong_bi_coi_la_cot(self):
        """Cột thì LẶP LẠI; căn lề thưa một lần thì không."""
        mot_lan = [L(0.20, 0.30, 0.10, 'x = 1'), L(0.60, 0.30, 0.20, '# ghi chú'),
                   L(0.20, 0.32, 0.15, 'y = x + 1'),
                   L(0.20, 0.34, 0.15, 'print(y)')]
        self.assertFalse(cs.two_column(mot_lan))

    def test_that_bai_dong_thi_TRA_CHU_VE_duong_cu(self):
        got = page_paragraphs(self.HAI_COT, code_regions=[[0.145, 0.060, 0.755, 0.060]])
        self.assertEqual([q for q in got if q.get('kind') == 'code'], [])
        ca = ' '.join(q['text'] for q in got)
        for l in self.HAI_COT:
            self.assertIn(l['text'], ca, 'chữ của sách không được mất khi chặn')


if __name__ == '__main__':
    unittest.main()
