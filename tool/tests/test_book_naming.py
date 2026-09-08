#!/usr/bin/env python3
"""TÊN SÁCH phải đủ để trẻ phân biệt hai cuốn khác nhau.

Đo trên máy thật (giá sách lớp 11): hai ô cạnh nhau ghi y hệt «Công nghệ 11 ·
CÔNG NGHỆ CHĂN NUÔI» — một là SGK, một là Chuyên đề học tập. Toàn tập: 18 cuốn
không phân biệt được bằng tên.
"""
import json
import os
import sys
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(HERE, '..', 'ui'))
import book_naming as bn  # noqa: E402


def _books():
    return [
        {'sourceDocumentId': '11-sgk-tin-hoc-11-dinh-huong-khoa-hoc-may-tinh',
         'subject': 'Tin học', 'title': 'Tin học 11'},
        {'sourceDocumentId': '11-sgk-cong-nghe-11-cong-nghe-chan-nuoi',
         'subject': 'Công nghệ', 'title': 'Công nghệ 11'},
    ]


class BookNaming(unittest.TestCase):

    def test_bo_sach_doc_tu_dinh_danh_khong_doan(self):
        self.assertTrue(bn.has_series(
            '11-sgk-chuyen-de-hoc-tap-cong-nghe-11-cong-nghe-co-khi'))
        self.assertFalse(bn.has_series('11-sgk-cong-nghe-11-cong-nghe-co-khi'))

    def test_loi_bo_qua_dau_hieu_bo_va_phan_phan_mon(self):
        a = '11-sgk-chuyen-de-hoc-tap-tin-hoc-11-dinh-huong-khoa-hoc-may-tinh'
        b = '11-sgk-tin-hoc-11-dinh-huong-khoa-hoc-may-tinh'
        self.assertEqual(bn.core_of(a), 'tin-hoc')
        self.assertEqual(bn.core_of(b), 'tin-hoc')

    def test_nhan_tap_van_doc_duoc_khi_con_duoi_phia_sau(self):
        # registry chỉ đọc `volume` khi định danh KẾT THÚC ở đó, nên
        # `…-tap-1-global-success` mất nhãn và hai cuốn Tiếng Anh 6 trùng tên.
        self.assertEqual(
            bn.volume_label('06-sgk-tieng-anh-6-tap-1-global-success'), 'Tập 1')
        self.assertEqual(
            bn.volume_label('06-sgk-tieng-anh-6-tap-2-global-success'), 'Tập 2')
        self.assertIsNone(bn.volume_label('11-sgk-vat-li-11'))

    def test_lay_lai_ten_mon_bi_nuot_tu_cuon_anh_em(self):
        names = bn.subject_names_by_core(_books())
        sid = '11-sgk-chuyen-de-hoc-tap-tin-hoc-11-dinh-huong-khoa-hoc-may-tinh'
        self.assertEqual(bn.display_title(sid, 'Chuyên đề 11', 11, names),
                         'Chuyên đề · Tin học 11')

    def test_them_ten_bo_khi_ten_khong_noi_ra(self):
        names = bn.subject_names_by_core(_books())
        sid = '11-sgk-chuyen-de-hoc-tap-cong-nghe-11-cong-nghe-chan-nuoi'
        self.assertEqual(bn.display_title(sid, 'Công nghệ 11', 11, names),
                         'Chuyên đề · Công nghệ 11')

    def test_khong_them_hai_lan(self):
        names = bn.subject_names_by_core(_books())
        sid = '11-sgk-chuyen-de-hoc-tap-am-nhac-11'
        self.assertEqual(bn.display_title(sid, 'Chuyên đề · Âm nhạc 11', 11, names),
                         'Chuyên đề · Âm nhạc 11')

    def test_khong_co_cuon_anh_em_thi_GIU_NGUYEN_khong_bia_ten(self):
        # ⭐ «Thiếu tên» còn sửa được; «sai tên» thì trẻ tin nhầm.
        sid = '11-sgk-chuyen-de-hoc-tap-tin-hoc-11-dinh-huong-khoa-hoc-may-tinh'
        self.assertEqual(bn.display_title(sid, 'Chuyên đề 11', 11, {}),
                         'Chuyên đề 11')

    def test_sach_khong_thuoc_bo_thi_khong_dong_vao(self):
        names = bn.subject_names_by_core(_books())
        self.assertEqual(bn.display_title('11-sgk-vat-li-11', 'Vật lí 11', 11, names),
                         'Vật lí 11')

    def test_ten_mon_phai_khop_loi_moi_duoc_lam_nguon(self):
        # Cuốn có `subject` suy từ phần phân môn («Khoa học» cho một cuốn Tin
        # học) KHÔNG được làm nguồn tên cho cuốn khác.
        bad = [{'sourceDocumentId': '11-sgk-tin-hoc-11-dinh-huong-khoa-hoc-may-tinh',
                'subject': 'Khoa học', 'title': 'Khoa học 11'}]
        self.assertEqual(bn.subject_names_by_core(bad), {})

    def test_tren_pack_that_khong_dung_cuon_ngoai_pham_vi(self):
        """Chạy trên pack có thật trên máy này — nếu có."""
        changed = []
        for g in range(1, 13):
            p = os.path.join(ROOT, 'assets', 'pack', f'lesson-index-g{g}.json')
            if not os.path.exists(p):
                continue
            with open(p, encoding='utf-8') as fh:
                d = json.load(fh)
            names = bn.subject_names_by_core(d['books'])
            for b in d['books']:
                sid = b['sourceDocumentId']
                if bn.display_title(sid, b['title'], g, names) != b['title']:
                    changed.append(sid)
                elif not b.get('volumeLabel') and bn.volume_label(sid):
                    changed.append(sid)
        # Mọi cuốn còn phải sửa đều PHẢI mang bằng chứng trong chính định danh.
        for sid in changed:
            self.assertTrue(bn.has_series(sid) or bn.volume_label(sid), sid)


if __name__ == '__main__':
    unittest.main()
