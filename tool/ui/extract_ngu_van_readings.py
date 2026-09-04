#!/usr/bin/env python3
"""WAL-192 POC — Ngữ văn: đoạn văn + câu hỏi từ «Đọc văn bản» → «Trả lời câu hỏi».

⚠️ KẾT QUẢ: FALSIFIED — KHÔNG wire vào build_lesson_index.py. Giữ file này làm
hồ sơ nghiên cứu (POC âm tính có bằng chứng), không phải công cụ production.
Xem docs/research/LEARNABLE-COVERAGE-SCALE-STRATEGY.md §"Ngữ văn — kết luận
sau gold-set 5 lớp" cho điểm số đầy đủ theo PASSAGE PRECISION/RECALL/QUESTION
BOUNDARY/PROVENANCE/FALSE CONTENT INCLUSION (Founder Delta 2026-09-04).

Lý do dừng, ngắn gọn: mốc bắt-đầu/kết-thúc đoạn văn generalize tốt qua 5 lớp,
nhưng lọc NHIỄU hộp chiến-lược-đọc (sidebar box) không giải được bằng danh
sách từ khoá cố định — NHÃN hộp bắt được, nhưng NỘI DUNG hộp (câu hỏi/gợi ý
bên trong, vd "Sự xuất hiện của nhân vật Kim Trọng.") là văn Việt tự do, đọc
giống hệt một câu trần thuật thật, không phân biệt được nếu không có dữ liệu
layout/cột (không có trong OCR dòng-theo-dòng đang dùng). Vá thêm từng cụm từ
mới mỗi khi gặp ca lạ đúng là kiểu "tích luỹ heuristic riêng từng sách" mà
Founder yêu cầu dừng lại — không biến thành maintenance trap.

Gold-set falsification trước khi wire vào build_lesson_index.py (Founder Delta
2026-09-04): đo PASSAGE PRECISION/RECALL, QUESTION BOUNDARY, PROVENANCE, và
quan trọng nhất FALSE CONTENT INCLUSION trên 5+ cuốn thật, lớp 6-10, cố tình
chọn ca khó (footnote dày, sidebar box, đoạn dài nhiều trang, bó 3 VĂN BẢN).

Mốc bắt đầu: dòng chứa "ĐỌC VĂN BẢN" (không phân biệt hoa/thường — mốc RÕ, ít
nhập nhằng hơn "N. " của tiểu học). Mốc kết: "TRẢ LỜI CÂU HỎI" / "SAU KHI ĐỌC" /
"VĂN BẢN <N+1>" / "TRƯỚC KHI ĐỌC" kế tiếp — bất kỳ cái nào tới trước, trần tối
đa 15 trang (fail closed — không để chạy tràn nếu không thấy mốc kết).

LOẠI NHIỄU — loại hẳn, KHÔNG cố sửa (thà thiếu còn hơn lẫn — false inclusion
nặng hơn missed content):
  - dòng chỉ có số (số trang OCR còn sót);
  - dòng bắt đầu bằng "(N)" — chú thích cuối trang, KHÔNG phải lời truyện;
  - dòng đúng bằng một nhãn hộp chiến-lược-đọc đã biết (danh sách cố định,
    KHÔNG đoán nhãn mới — nhãn lạ không loại được thì để nguyên, chấp nhận
    một chút nhiễu còn hơn loại nhầm lời truyện thật).
"""
import glob
import json
import re
import sys

SIDEBAR_LABELS = {
    'theo dõi', 'dự đoán', 'suy luận', 'hình dung', 'đối chiếu',
    'tưởng tượng', 'liên hệ', 'chú thích', 'khái quát hóa',
}
FOOTNOTE_LINE = re.compile(r'^\(\d+\)')
DIGITS_ONLY = re.compile(r'^\d+$')
Q_RE = re.compile(r'^\d+\.\s+\S')
# Nhãn mục (ĐỌC/VIẾT/NÓI VÀ NGHE...) đôi khi tự đánh số như câu hỏi thật
# ("1. ĐỌC") — loại nếu phần sau số quá ngắn, câu hỏi thật luôn là một câu.
MIN_Q_CHARS = 15
START_RE = re.compile(r'ĐỌC VĂN BẢN', re.IGNORECASE)
END_RES = [re.compile(p, re.IGNORECASE) for p in
           [r'TRẢ LỜI CÂU HỎI', r'SAU KHI ĐỌC', r'^VĂN BẢN\s*\d', r'TRƯỚC KHI ĐỌC']]
MAX_PAGES = 15
# ⭐ Câu hỏi thật luôn nằm SÁT mốc kết đoạn văn — không quét xa. Quét xa từng
# bắt nhầm câu hỏi của bài KHÁC khi không gặp mốc kết thứ hai kịp thời (false
# inclusion — sai còn nặng hơn thiếu, theo đúng yêu cầu).
MAX_QUESTION_PAGES = 2


SIDEBAR_PREFIX = re.compile(
    r'^(theo dõi|dự đoán|suy luận|hình dung|đối chiếu|tưởng tượng|liên hệ|'
    r'chú thích|khái quát hóa)\b', re.IGNORECASE)


def is_noise(line):
    t = line.strip()
    if DIGITS_ONLY.match(t):
        return True
    if FOOTNOTE_LINE.match(t):
        return True
    if t.lower() in SIDEBAR_LABELS:
        return True
    # ⭐ Nhãn hộp chiến-lược-đọc đôi khi dính liền câu hỏi của hộp trên CÙNG
    # một dòng OCR ("THEO DỖI Chú ý các chi tiết mở đầu câu chuyện.") — loại
    # cả dòng thay vì cố tách, vì không tách được tin cậy (fail closed).
    if SIDEBAR_PREFIX.match(t):
        return True
    return False


def load_pages(book):
    pages = {}
    for f in sorted(glob.glob(f'poc-out/graph/ocr-body/{book}/p*.json')):
        j = json.load(open(f))
        pdf = int(re.search(r'p(\d+)\.json', f).group(1))
        printed = None
        for l in j['lines']:
            if DIGITS_ONLY.match(l['text'].strip()):
                printed = int(l['text'].strip())
        pages[pdf] = dict(lines=j['lines'], printed=printed)
    return pages


def extract(book):
    pages = load_pages(book)
    ordered = sorted(pages)
    results = []
    i = 0
    while i < len(ordered):
        pdf = ordered[i]
        lines = [l['text'] for l in pages[pdf]['lines']]
        start_idx = next((k for k, t in enumerate(lines) if START_RE.search(t)), None)
        if start_idx is None:
            i += 1
            continue
        # thu đoạn văn từ ngay sau mốc bắt đầu, quét tới khi gặp mốc kết
        # hoặc chạm trần MAX_PAGES — fail closed, không chạy tràn vô hạn.
        passage_lines = []
        q_lines = []
        stopped_at = None
        q_pages_seen = 0
        start_pdf, start_printed = pdf, pages[pdf]['printed']
        mode = 'passage'
        for j in range(i, min(i + MAX_PAGES, len(ordered))):
            p2 = ordered[j]
            ls = [l['text'] for l in pages[p2]['lines']]
            begin = start_idx + 1 if p2 == pdf else 0
            if mode == 'question':
                q_pages_seen += 1
                if q_pages_seen > MAX_QUESTION_PAGES:
                    break
            page_had_question = False
            for t in ls[begin:]:
                if any(r.search(t) for r in END_RES):
                    if mode == 'passage':
                        mode = 'question'
                        stopped_at = p2
                        continue
                    else:
                        stopped_at = p2
                        break
                if is_noise(t):
                    continue
                if mode == 'passage':
                    passage_lines.append(t)
                else:
                    m = Q_RE.match(t.strip())
                    if m and len(t.strip()) - len(m.group(0)) + 1 >= MIN_Q_CHARS:
                        q_lines.append(t.strip())
                        page_had_question = True
            if mode == 'question' and stopped_at is not None and p2 != stopped_at:
                break
            # Fail closed: một trang KHÔNG có câu hỏi nào ngay sau mốc kết
            # ⇒ khối câu hỏi đã hết thật, không phải OCR bỏ sót — dừng, không
            # đoán tiếp sang nội dung bài khác.
            if mode == 'question' and not page_had_question and q_lines:
                break
        passage = ' '.join(passage_lines).strip()
        if len(passage) >= 200 and q_lines:
            results.append(dict(
                book=book, startPagePdf=start_pdf, startPagePrinted=start_printed,
                passageChars=len(passage), passage=passage[:4000],
                questions=q_lines[:8],
            ))
        i = i + 1
    return results


if __name__ == '__main__':
    book = sys.argv[1]
    out = extract(book)
    for r in out:
        print(f"=== {r['book']} pdf{r['startPagePdf']} (in.{r['startPagePrinted']}) "
              f"chars={r['passageChars']} qs={len(r['questions'])} ===")
        print('PASSAGE HEAD:', r['passage'][:200])
        print('PASSAGE TAIL:', r['passage'][-200:])
        for q in r['questions']:
            print('  Q:', q[:120])
        print()
