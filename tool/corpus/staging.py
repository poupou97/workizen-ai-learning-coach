#!/usr/bin/env python3
"""KHU DỰNG THỬ — một lần dựng đi trọn về MỘT nơi, hoặc không đi đâu cả.

Founder Gate 2026-09-09:

    DỰNG THỬ KHÔNG ĐƯỢC LÀM ĐỔI BẤT KỲ ĐẦU VÀO / INDEX / PACK CANONICAL NÀO.
    Một lần dựng hỏng, bị ngắt, hay thử nghiệm phải để trạng thái canonical
    GIỐNG TỪNG BYTE.

⛔ VÌ SAO PHẢI CÓ MODULE RIÊNG. Trước đây mỗi đầu ra tự chọn chỗ của nó:
index bài học theo `PACK_OUT_DIR`, còn kho ảnh theo `--out` với mặc định là
thư mục CANONICAL. Đặt `PACK_OUT_DIR` rồi chạy là được đúng một nửa dàn dựng:
index vào khu tạm, ảnh đè thẳng lên bản đang phục vụ. Không có lỗi nào, không
có cảnh báo nào — và người chạy tin rằng mình vừa «dựng thử».

Sửa bằng cách khôi phục tệp sau khi chạy là sai hướng: nó chỉ đúng khi lượt
dựng chạy hết. Lượt bị ngắt (Ctrl-C, hết pin, `disk I/O error` ở lớp 7 hôm
trước) là đúng lúc cần bảo vệ nhất thì lại không có ai khôi phục.

Nên ranh giới phải nằm ở CHỖ GHI, và phải ĐÓNG CHẶT.
"""
import os

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))

CANONICAL_PACK = 'assets/pack'
CANONICAL_FIGURES = 'poc-out/packs/figures'


def _abs(p):
    return p if os.path.isabs(p) else os.path.join(ROOT, p)


def pack_dir():
    """Nơi đặt `lesson-index-g<N>.json` cho lượt dựng này."""
    return _abs(os.environ.get('PACK_OUT_DIR', CANONICAL_PACK))


def is_staging():
    return os.path.realpath(pack_dir()) != os.path.realpath(_abs(CANONICAL_PACK))


def figures_dir(explicit=None):
    """Nơi đặt kho ảnh + manifest.

    `--out` nói rõ thì theo `--out`. Không nói mà đang dựng thử thì kho ảnh
    phải đi CÙNG index vào khu tạm — nếu không, một lần dựng lại tách làm hai
    nửa ở hai nơi, đúng lỗi mà module này sinh ra để chặn.
    """
    if explicit:
        return _abs(explicit)
    if is_staging():
        return os.path.join(pack_dir(), 'figures')
    return _abs(CANONICAL_FIGURES)


def canonical_roots():
    return [os.path.realpath(_abs(CANONICAL_PACK)),
            os.path.realpath(_abs(CANONICAL_FIGURES))]


def guard(path, what='đầu ra'):
    """Trả lại `path`, hoặc DỪNG HẲN nếu lượt dựng thử đang ghi vào chỗ thật.

    Kiểm bằng đường dẫn đã giải ký hiệu liên kết: một `PACK_OUT_DIR` trỏ vòng
    về `assets/pack` qua symlink vẫn là ghi vào chỗ thật.
    """
    if not is_staging():
        return path
    real = os.path.realpath(path)
    for root in canonical_roots():
        if real == root or real.startswith(root + os.sep):
            raise SystemExit(
                f'DỰNG THỬ ĐANG ĐỊNH GHI VÀO CHỖ THẬT — dừng.\n'
                f'  {what}: {real}\n'
                f'  khu dựng thử: {pack_dir()}\n'
                f'Dựng thử phải để trạng thái canonical giống từng byte.')
    return path


def require_promoted(disabled):
    """Pack CANONICAL không được thiếu một năng lực ĐÃ PROMOTE nào.

    2026-09-11: `FORMULA_SOURCE` từng là cờ BẬT thủ công. Một lượt dựng quên
    cờ ấy làm **28 bài Toán 5 TĂNG khối chữ** — mảnh OCR công thức («+»,
    «a)», «:(x7)») chảy ngược vào dòng đọc, trong khi số hình, số bài và mọi
    bất biến pack đều y hệt. Không lỗi, không cảnh báo.

    ⛔ Đây là họ lỗi «cấu hình vắng mặt», khác với «dữ liệu thiếu»: đường dựng
    chạy trót lọt và ra một pack TRÔNG hợp lệ. Không cổng nào sẵn có bắt được,
    vì mọi cổng đều đo pack chứ không đo CẤU HÌNH sinh ra pack.

    Khu dựng thử vẫn được phép tắt — tắt để đối chiếu chính là việc của nó.
    """
    if not disabled or is_staging():
        return
    raise SystemExit(
        'DỰNG CANONICAL THIẾU NĂNG LỰC ĐÃ PROMOTE — dừng.\n'
        f'  đang tắt: {", ".join(sorted(disabled))}\n'
        f'  đích: {pack_dir()}\n'
        'Năng lực đã promote nghĩa là pack đang phục vụ CÓ nó và client ĐANG\n'
        'dựng nó. Dựng thiếu là lặng lẽ trả chữ sai về cho trẻ.\n'
        'Muốn đối chiếu thì dựng vào khu tạm: PACK_OUT_DIR=<thư mục khác>.')
