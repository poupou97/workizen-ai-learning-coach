"""Đọc BƯỚC của một khối thí nghiệm SGK.

⭐⭐ SÁCH TIỂU HỌC DÙNG «- », KHTN 6-9 DÙNG «•».

Bộ trích thí nghiệm viết cho Khoa học 4/5 rồi mở sang KHTN 6-9 mà không đổi ký
tự đầu dòng. Đo được trên KHTN 6: 8/16 khối tìm đủ «Chuẩn bị» + «Tiến hành»
nhưng KHÔNG đọc được bước nào nên bị bỏ — trong đó có chính Bài 17, bài đang
hiện trên Home của trẻ.

Tách khỏi `build_lesson_index.py` để test gọi được: tệp ấy chạy code ở mức
module (đọc `sys.argv`) nên không import được từ test.
"""

STEP_BULLETS = ('•', '- ', '– ', '+ ')


def step_body(line):
    """Phần chữ của một dòng bước, hoặc None nếu dòng ấy không phải bước."""
    for b in STEP_BULLETS:
        if line.startswith(b):
            return line[len(b):].strip()
    return None


def is_real_step(body):
    """Fail closed: nhãn hình/ký hiệu lạc («- AgNO3») không phải một bước."""
    return len(body) >= 10 and ' ' in body


def continues_step(prev_step, line):
    """Dòng nối của một bước xuống dòng giữa câu.

    «• Lấy một cốc nước… cho hỗn hợp đục» / «đều lên. Dừng khuấy và quan sát.»
    Dòng nối KHÔNG mang dấu đầu dòng. Không ghép thì bước bị cắt giữa câu —
    đúng lỗi «trích nguyên văn nhưng cụt» đã sửa ở kho chuyện.
    """
    c = line.strip()
    if not c or c.startswith('(') or c.endswith(':'):
        return False          # nhãn hình «(b)», tiêu đề khối «Chuẩn bị:»
    if ' ' not in c and len(c) < 12:
        return False          # nhãn trần một từ («Muối ăn» đã bị chặn bởi dấu
                              # chấm cuối bước trước, nhưng đừng dựa vào may)
    return bool(prev_step) and not prev_step.endswith(('.', '?', '!'))
