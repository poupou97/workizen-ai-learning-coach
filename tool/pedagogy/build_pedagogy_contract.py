#!/usr/bin/env python3
"""HỢP ĐỒNG SƯ PHẠM — dữ liệu cho MỘT runtime dùng chung, không phải 10 kịch bản.

Đầu vào: cặp SGK↔SGV đã CHỨNG MINH (`sgk_sgv_pairing`) + trang SGV + bài SGK
trong pack. Đầu ra: một tệp JSON mỗi bài, chỉ chứa **chữ NGUYÊN VĂN của sách**
kèm xuất xứ. Không diễn đạt lại, không suy ra, không LLM.

⛔ THANG ĐÁNH GIÁ KHÔNG PHẢI ĐÁP ÁN. Đo được: SGV KHTN 6 in
«2. Đánh giá — H: Câu 1. Trả lời đúng 3 đồ vật trở lên» — đó là MỨC ĐẠT, nói
về mức độ trả lời chứ không nói ĐÁP ÁN là gì. SGV Khoa học 4 mới in đáp án
thật: «2. Đáp án và đánh giá — Câu 1 (B). Nước có tính chất không màu…».

Nên `ANSWER_FOR_TASK` chỉ được công nhận khi CẢ BA:
  1. SGV in NGUYÊN VĂN câu hỏi, và câu ấy trùng ≥50% từ với thân bài SGK
  2. có nhãn ĐÁP ÁN in ra («Đáp án», «Gợi ý trả lời», «Hướng dẫn trả lời»)
  3. sau nhãn ấy có đoạn gắn ĐÚNG SỐ CÂU đó

Thiếu bất kỳ điều nào ⇒ `UNKNOWN` và SAM **không được chấm** bài ấy. Đó là
GIẢM NĂNG LỰC, không phải lỗi.

⚠ SGV VIẾT CHO GIÁO VIÊN. Mọi trường hướng dẫn mang `audience: TEACHER`.
Biến nó thành lời SAM nói với trẻ là việc của tầng realization, không phải
của tệp này — ở đây chỉ chở nguyên văn nguồn.
"""
import argparse
import csv
import glob
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)

import sgk_sgv_pairing as P  # noqa: E402
import sgv_evidence as E  # noqa: E402

#: Nhãn ĐÁP ÁN in ra — mở vùng có thể chứa đáp án theo câu.
ANSWER_LABEL = re.compile(
    r'(đáp\s*án|gợi\s*ý\s*trả\s*lời|hướng\s*dẫn\s*trả\s*lời)', re.IGNORECASE)
#: Nhãn THANG ĐÁNH GIÁ — KHÔNG mở vùng đáp án (mức đạt ≠ đáp án).
RUBRIC_ONLY = re.compile(r'(hướng\s*dẫn\s*đánh\s*giá|^\s*\d?\s*\.?\s*đánh\s*giá)',
                         re.IGNORECASE)
#: Câu hỏi SGV in nguyên văn.
#: ⚠ PHẢI DỪNG TRƯỚC «Câu N» KẾ TIẾP. Bản đầu dùng `[^?]{8,220}\?` nên câu kết
#: bằng DẤU CHẤM bị nuốt sang câu sau: «…tế bào động vật. Câu 2. Màng nhân là
#: cấu trúc…» thành MỘT việc. Trẻ sẽ nhận một câu hỏi ghép của hai câu.
QUESTION = re.compile(
    r'C[âa]u\s*(\d{1,2})\s*[.:)]\s*(.{8,220}?)(?=\s*C[âa]u\s*\d{1,2}\s*[.:)]|$)',
    re.IGNORECASE | re.DOTALL)
#: ⭐ SỞ HỮU CỤC BỘ — đáp án in NGAY TRONG câu hỏi: «…thiết bị ra? (Đáp án: D)».
#: Không có cách nào gán nhầm sang câu khác: nó nằm trong chính câu ấy.
INLINE_ANS = re.compile(r'\(\s*(?:đáp\s*án|gợi\s*ý)\s*[:.]?\s*(.{1,160}?)\s*\)',
                        re.IGNORECASE | re.DOTALL)
#: Đoạn đáp án gắn số câu, trong vùng đã mở bằng nhãn đáp án.
ANSWER = re.compile(
    r'C[âa]u\s*(\d{1,2})\s*(?:\(\s*(B|H|VD\s*\d?)\s*\))?\s*[.:]\s*'
    r'(.{10,400}?)(?=\s*C[âa]u\s*\d{1,2}\s*[.:(]|$)', re.IGNORECASE | re.DOTALL)
#: Mục tiêu / hoạt động in ra — chở nguyên văn, gắn cờ người đọc.
OBJ = re.compile(r'(?:M[ỤU]C TI[ÊE]U|Y[ÊE]U C[ẦA]U C[ẦA]N Đ[ẠA]T)\s*(.{20,600}?)'
                 r'(?=\s*(?:II|2|B[.\s]|CHU[ẨA]N B[ỊI]|HO[ẠA]T Đ[ỘO]NG)\b|$)',
                 re.IGNORECASE | re.DOTALL)
MISCONCEPT = re.compile(
    r'([^.]{0,80}(?:sai lầm|nhầm lẫn|dễ nhầm|HS có thể nhầm)[^.]{0,200}\.)',
    re.IGNORECASE)

TASK_MIN = 0.5
#: Đáp án trùng chừng này với chính câu hỏi ⇒ KHÔNG phải đáp án.
ECHO_MAX = 0.8


#: Nhãn mở DANH SÁCH CÂU HỎI — «1. Câu hỏi», «1. Đề bài».
QLIST = re.compile(r'\d?\s*\.?\s*(c[âa]u\s*hỏi|đề\s*bài)\b', re.IGNORECASE)


def qa_blocks(raw):
    """Cặp (khối CÂU HỎI, khối ĐÁP ÁN) LIỀN KỀ — sở hữu bằng CẤU TRÚC.

    ⛔ CỬA SỔ VĂN BẢN KHÔNG CHỨNG MINH ĐƯỢC SỞ HỮU. Bản đầu lấy 2 600 ký tự
    sau bất kỳ nhãn «Đáp án» nào rồi khớp theo SỐ CÂU — và số câu ĐẶT LẠI ở
    mỗi mục, nên đáp án nhảy sang câu khác. Đo được: Hoá 11 Bài 4 «Trong khí
    quyển, khí nitrogen phổ biến thứ mấy?» nhận đáp án «Hợp chất của nitrogen
    có ý nghĩa quan trọng trong sản xuất nông nghiệp…»; Tin học 7 Bài 3 hỏi về
    thiết bị ra, nhận đáp án về tạo thư mục.

    Sách in HAI KHỐI LIỀN NHAU: «1. Câu hỏi · Câu 1… Câu 2…» rồi «2. Đáp án
    và đánh giá · Câu 1 (B)… Câu 2 (H)…». Chỉ khi hai khối ấy KỀ NHAU thì số
    câu mới nói cùng một danh sách.
    """
    out = []
    for q in QLIST.finditer(raw):
        a = ANSWER_LABEL.search(raw, q.end())
        if not a:
            continue
        head = raw[max(0, a.start() - 40):a.start() + 12]
        if RUBRIC_ONLY.search(head) and not re.search(r'đáp\s*án', head, re.I):
            continue                      # thang đánh giá ≠ đáp án
        nxt = QLIST.search(raw, a.end())
        out.append((raw[q.end():a.start()],
                    raw[a.end():nxt.start() if nxt else len(raw)]))
    return out


def build(span, sgk_words):
    raw = E.page_text(span['sgv'], span['start'], span['end'])
    if not raw:
        return None
    tasks = []
    for qblock, ablock in qa_blocks(raw):
        qs = QUESTION.findall(qblock)
        answers = {int(n): (lv or '', a.strip())
                   for n, lv, a in ANSWER.findall(ablock)}
        # ⛔ HAI DANH SÁCH PHẢI KHỚP 1:1. Đo được: ghép theo số câu trong khối
        # liền kề VẪN gán nhầm ở ~một nửa ca — «Trong khí quyển, khí nitrogen
        # phổ biến thứ mấy?» nhận đáp án «Hợp chất của nitrogen có ý nghĩa
        # quan trọng…». Vì nhiều bộ SGV không in đáp án thành danh sách đánh
        # số song song; số trùng chỉ là trùng hợp. Lệch số lượng ⇒ BỎ HẾT.
        qnums = {int(n) for n, _ in qs}
        if set(answers) != qnums:
            answers = {}
        for n, q in qs:
            qt = P.toks(q)
            if not qt or len(qt & sgk_words) / len(qt) < TASK_MIN:
                continue                  # bài SGK không in ⇒ không phải việc của trẻ
            num = int(n)
            lv, ans = answers.get(num, ('', ''))
            inline = INLINE_ANS.search(q)
            if inline:                    # sở hữu cục bộ thắng: nằm trong chính câu
                lv, ans = '', inline.group(1).strip()
                q = INLINE_ANS.sub('', q).strip()
                qt_src = q
        # ⚠ ĐÁP ÁN KHÔNG ĐƯỢC LÀ CHÍNH CÂU HỎI. Đo được ở KHTN 6 Bài 21: vùng
        # đáp án chớm vào khối câu hỏi nên «đáp án» của việc 3 trùng hệt câu
        # hỏi. Trả lại nguyên câu hỏi rồi gọi đó là đáp án là bịa có vỏ nguồn.
            if ans:
                at = P.toks(ans)
                if at and len(at & qt) / len(at) >= ECHO_MAX:
                    lv, ans = '', ''
            if any(t['prompt'] == q.strip() for t in tasks):
                continue                  # cùng một việc in lại ở nhiều chỗ
            tasks.append(dict(
                taskNo=num, prompt=q.strip(), promptOwnership='TASK_LINKED',
                answerOwnership=('INLINE' if inline else
                                 ('NUMBERED_LIST' if ans else 'NONE')),
                expectedResponse=ans or None,
                answerTrust=('SOURCE_EXPLICIT' if ans else 'UNKNOWN'),
                assessmentLevel=lv.upper().replace(' ', '') or None))
    obj = OBJ.search(raw)
    mis = MISCONCEPT.search(raw)
    gradable = [t for t in tasks if t['expectedResponse']]
    return dict(
        schema='pedagogy-contract-v1',
        book=span['sgk'], lesson=span['lesson'],
        sgvBook=span['sgv'], sgvPages=f"{span['start']}-{span['end'] - 1}",
        objective=(dict(text=obj.group(1).strip()[:600],
                        trust='SOURCE_EXPLICIT', audience='TEACHER')
                   if obj else None),
        misconception=(dict(text=mis.group(1).strip()[:300],
                            trust='SOURCE_EXPLICIT', audience='TEACHER')
                       if mis else None),
        tasks=tasks,
        allowedTutorActions=(['orient', 'present_task', 'check_answer', 'next']
                             if gradable else ['orient', 'present_task', 'next']),
        forbiddenTutorActions=([] if gradable else ['check_answer'])
        + ([] if mis else ['name_misconception']),
        provenance=dict(pairing='sgk-sgv-pairing-v1 · L1+L2+L3',
                        extractor='pedagogy-contract-v1'))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--out', default='poc-out/pedagogy/contracts')
    a = ap.parse_args()
    spans = E.spans()
    out = os.path.join(ROOT, a.out)
    # ⚠ DỌN TRƯỚC. Không dọn thì tệp của lượt TRƯỚC ở lại, và bản đếm đọc thư
    # mục sẽ trộn hai luật khác nhau — đúng lỗi đã dính một lần ở vòng này.
    if os.path.isdir(out):
        for f in glob.glob(os.path.join(out, '*.json')):
            os.remove(f)
    os.makedirs(out, exist_ok=True)
    n_task = n_grad = 0
    made = []
    for i, s in enumerate(spans):
        if i % 100 == 0:
            print(f'  {i}/{len(spans)}…', file=sys.stderr, flush=True)
        W = E.sgk_words(s['sgk'], s['lesson'])
        if not W:
            continue
        c = build(s, W)
        if not c or not c['tasks']:
            continue
        n_task += 1
        if any(t['expectedResponse'] for t in c['tasks']):
            n_grad += 1
            made.append(c)
        with open(os.path.join(out, f"{c['book']}-b{c['lesson']}.json"), 'w',
                  encoding='utf-8') as f:
            json.dump(c, f, ensure_ascii=False, indent=1)
    print(f'\nmẫu số {len(spans)} bài CONFIDENT')
    print(f'  có ≥1 VIỆC của trẻ (câu hỏi SGV in trùng bài SGK): {n_task}')
    print(f'  trong đó có ĐÁP ÁN gắn đúng câu ấy               : {n_grad}')
    print(f'contracts → {a.out}')


if __name__ == '__main__':
    main()
