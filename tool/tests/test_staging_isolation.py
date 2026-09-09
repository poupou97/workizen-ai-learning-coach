#!/usr/bin/env python3
"""RANH GIỚI CÁCH LY — dựng thử để canonical GIỐNG TỪNG BYTE.

Founder Gate 2026-09-09: «Mutation-test the isolation boundary. Do not rely on
restoring files afterward.»

Khôi phục tệp sau khi chạy chỉ đúng khi lượt dựng chạy hết. Lượt bị NGẮT là
đúng lúc cần bảo vệ nhất thì lại không còn ai khôi phục — nên bài kiểm ở đây
cắt ngang một lượt dựng thật rồi mới băm lại chỗ canonical.
"""
import hashlib
import json
import os
import subprocess
import sys
import tempfile
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, 'tool', 'corpus'))
import staging  # noqa: E402

PACK = os.path.join(ROOT, 'assets', 'pack')
FIGS = os.path.join(ROOT, 'poc-out', 'packs', 'figures')


def fingerprint(*dirs):
    """Băm tên + kích thước + nội dung mọi tệp — đủ bắt cả ghi đè lẫn xoá."""
    h = hashlib.sha256()
    for d in dirs:
        for base, _, names in os.walk(d):
            for n in sorted(names):
                p = os.path.join(base, n)
                h.update(os.path.relpath(p, ROOT).encode())
                h.update(str(os.path.getsize(p)).encode())
                with open(p, 'rb') as fh:
                    while True:
                        b = fh.read(1 << 20)
                        if not b:
                            break
                        h.update(b)
    return h.hexdigest()


class RanhGioi(unittest.TestCase):
    """Phép đo thuần, không cần corpus."""

    def setUp(self):
        self._old = os.environ.get('PACK_OUT_DIR')

    def tearDown(self):
        os.environ.pop('PACK_OUT_DIR', None)
        if self._old is not None:
            os.environ['PACK_OUT_DIR'] = self._old

    def test_khong_dat_thi_van_la_duong_canonical(self):
        os.environ.pop('PACK_OUT_DIR', None)
        self.assertFalse(staging.is_staging())
        self.assertEqual(os.path.realpath(staging.pack_dir()),
                         os.path.realpath(PACK))
        self.assertEqual(os.path.realpath(staging.figures_dir()),
                         os.path.realpath(FIGS))

    def test_dung_thu_thi_KHO_ANH_DI_THEO_index(self):
        """Lỗi gốc: index dời sang khu tạm mà kho ảnh vẫn đè bản đang phục vụ."""
        os.environ['PACK_OUT_DIR'] = '/tmp/wal-stage-test'
        self.assertTrue(staging.is_staging())
        self.assertTrue(staging.figures_dir().startswith('/tmp/wal-stage-test'))
        self.assertNotEqual(os.path.realpath(staging.figures_dir()),
                            os.path.realpath(FIGS))

    def test_dung_thu_ma_ghi_vao_cho_that_thi_DUNG_HAN(self):
        os.environ['PACK_OUT_DIR'] = '/tmp/wal-stage-test'
        for p, what in ((os.path.join(PACK, 'lesson-index-g6.json'), 'index'),
                        (os.path.join(FIGS, 'figures-g6.db'), 'kho ảnh')):
            with self.assertRaises(SystemExit, msg=f'{what} phải bị chặn'):
                staging.guard(p, what)

    def test_SYMLINK_vong_ve_cho_that_cung_bi_chan(self):
        """Kiểm bằng chuỗi đường dẫn thì một liên kết mềm lách qua được."""
        d = tempfile.mkdtemp()
        link = os.path.join(d, 'pack')
        os.symlink(PACK, link)
        os.environ['PACK_OUT_DIR'] = d
        with self.assertRaises(SystemExit):
            staging.guard(os.path.join(link, 'lesson-index-g6.json'), 'index')

    def test_duong_dan_trong_khu_tam_thi_cho_qua(self):
        os.environ['PACK_OUT_DIR'] = '/tmp/wal-stage-test'
        p = '/tmp/wal-stage-test/figures/figures-g6.db'
        self.assertEqual(staging.guard(p), p)

    def test_TEN_GIONG_MA_KHAC_THU_MUC_thi_khong_bi_chan_nham(self):
        """`assets/pack-thu-nghiem` không phải `assets/pack`."""
        os.environ['PACK_OUT_DIR'] = '/tmp/wal-stage-test'
        p = os.path.join(ROOT, 'assets', 'pack-thu-nghiem', 'x.json')
        self.assertEqual(staging.guard(p), p)


@unittest.skipUnless(os.path.exists(os.path.join(PACK, 'lesson-index-g6.json')),
                     'cần corpus — CI không có')
class DungThuThat(unittest.TestCase):
    """Chạy một lượt dựng thật rồi băm lại chỗ canonical."""

    def test_dung_thu_BI_NGAT_van_de_canonical_nguyen_ven(self):
        before = fingerprint(PACK, FIGS)
        d = tempfile.mkdtemp(prefix='wal-stage-')
        env = dict(os.environ, PACK_OUT_DIR=d)
        # Chép index sang khu tạm để bước dựng hình có đầu vào hợp lệ.
        import shutil
        shutil.copy(os.path.join(PACK, 'lesson-index-g6.json'),
                    os.path.join(d, 'lesson-index-g6.json'))
        pr = subprocess.Popen(
            [sys.executable, os.path.join(ROOT, 'tool/ui/build_lesson_figures.py'),
             '6', '--limit', '4'],
            cwd=ROOT, env=env, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        try:
            pr.wait(timeout=25)          # đủ lâu để đã ghi ảnh, chưa chắc xong
        except subprocess.TimeoutExpired:
            pr.kill()                     # ⭐ NGẮT GIỮA CHỪNG — đúng ca cần bảo vệ
            pr.wait()
        # ⚠ CHỐNG XANH RỖNG: một lượt dựng chết ngay từ dòng đầu cũng để canonical
        # nguyên vẹn, và bài kiểm này sẽ xanh mà chẳng chứng minh gì. Phải thấy
        # khu tạm CÓ SẢN PHẨM thì phép so mới có nghĩa.
        made = os.path.join(d, 'figures', 'figures-g6.db')
        self.assertTrue(os.path.exists(made) and os.path.getsize(made) > 50_000,
                        'lượt dựng thử không sinh ra gì — phép so vô nghĩa')
        # Ngoài băm toàn cục, kiểm thẳng cái đã từng bị ghi đè thật.
        with open(os.path.join(FIGS, 'figures-g6.manifest.json'), encoding='utf-8') as fh:
            self.assertGreater(json.load(fh)['figures'], 900,
                               'manifest canonical lớp 6 đã bị lượt dựng thử ghi đè')
        self.assertEqual(before, fingerprint(PACK, FIGS),
                         'lượt dựng thử đã làm đổi trạng thái canonical')
        shutil.rmtree(d, ignore_errors=True)


if __name__ == '__main__':
    unittest.main()
