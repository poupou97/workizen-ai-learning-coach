#!/usr/bin/env python3
"""AN TOÀN DỰNG — dựng thử KHÔNG được chạm pack đang phục vụ (WAL-230).

Vụ attach hồi 2026-09-09 dạy đúng một điều: cái nguy hiểm không phải bước dựng
sai, mà là bước dựng sai GHI ĐÈ dữ liệu đang tốt trước khi ai kịp đối chiếu.
"""
import os
import re
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, '..', 'ui', 'build_lesson_figures.py')


class DungThu(unittest.TestCase):
    def setUp(self):
        with open(SRC, encoding='utf-8') as fh:
            self.src = fh.read()

    def test_index_di_theo_PACK_OUT_DIR(self):
        """Kho .db theo `--out` mà index vẫn theo `assets/pack` thì một lần dựng
        đi về hai nơi — nửa thử nghiệm, nửa canonical."""
        self.assertIn("os.environ.get('PACK_OUT_DIR'", self.src)
        m = re.search(r"idx_path = os\.path\.join\((\w+),", self.src)
        self.assertIsNotNone(m, 'không tìm thấy chỗ dựng đường dẫn index')
        self.assertEqual(m.group(1), 'pack_dir',
                         'index phải theo thư mục pack đang dựng')

    def test_KHONG_ghi_thang_assets_pack(self):
        self.assertNotIn("f'assets/pack/lesson-index-g{a.grade}.json'", self.src)

    def test_thieu_index_thi_DUNG_HAN_chu_khong_lui_ve_canonical(self):
        """Lùi âm thầm về pack canonical là cách hỏng tệ nhất: chạy xong, xanh,
        và dữ liệu thử nghiệm nằm trong chỗ thật."""
        self.assertIn('raise SystemExit', self.src)
        i = self.src.index('idx_path = os.path.join(pack_dir')
        j = self.src.index('idx = json.load(open(idx_path')
        self.assertIn('raise SystemExit', self.src[i:j],
                      'phải dừng NGAY khi thiếu index, trước khi đọc')


if __name__ == '__main__':
    unittest.main()
