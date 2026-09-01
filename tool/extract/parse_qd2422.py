"""WAL-90 — trích xuất TẤT ĐỊNH khung QĐ 2422/QĐ-BGDĐT (18/8/2026).

Hệ mã CHÍNH THỨC (văn bản tự định nghĩa ở tr.14): <lớp>.<chủ đề>.<MR?><stt>
  6.A1.2  = YCCĐ cốt lõi thứ 2, chủ đề A1, lớp 6
  6.A1.MR1= YCCĐ mở rộng thứ 1  (MR trong mã ⇒ extended — F3 giải quyết tại nguồn)
Văn bản cũng nói mã "chỉ dùng để định danh" ⇒ F4: KHÔNG suy prerequisite từ mã.

Luật: GIỮ NGUYÊN mã chính thức (chỉ chuẩn hoá nhiễu OCR ở VỊ TRÍ chữ cái chủ đề,
có đếm và báo cáo); mã có lớp KHÁC section đang đọc ⇒ F2 LỖI TO, không giấu.
Mọi outcome mang provenance trang. Trường không có trong nguồn: không bịa.
"""
import json, os, re, sys, unicodedata

SRC = 'poc-out/vbqd/qd2422'
# nhiễu OCR ở vị trí chữ cái mạch: Ạ/Á/À/Ả/Ã→A … chỉ áp cho 1 ký tự đầu chủ đề
def norm_letter(ch):
    base = unicodedata.normalize('NFD', ch)[0].upper()
    return base if base in 'ABCD' else None

# Tên chủ đề CHUẨN — ghép từ nhiều lần xuất hiện của header tràn-dòng trong
# bản OCR, kiểm tay từng tên (status: CURATED_FROM_SOURCE; id là SOURCE_EXPLICIT).
TOPIC_NAMES = {
    'A1': 'Tính chủ động của con người',
    'A2': 'AI vì sự tiến bộ của con người',
    'A3': 'Công dân trong kỉ nguyên AI',
    'B1': 'Các khía cạnh đạo đức của AI',
    'B2': 'Sử dụng AI an toàn và có trách nhiệm',
    'B3': 'Nguyên tắc đạo đức và trách nhiệm xã hội',
    'C1': 'Đặc điểm chính của AI',
    'C2': 'Ứng dụng AI trong học tập và cuộc sống',
    'C3': 'Công nghệ AI',
    'C4': 'Dữ liệu trong AI',
    'C5': 'Kĩ thuật và thuật toán AI',
    'D1': 'Nhận diện và hình thành giải pháp',
    'D2': 'Cấu trúc và tương tác, cải tiến hệ thống',
}

CODE = re.compile(r'(\d{1,2})\s*\.\s*([A-DẠÁÀẢÃĂÂ])\s*(\d)\s*\.\s*(MR)?\s*(\d{1,2})\s*[.,]')
GRADE_HDR = re.compile(r'^\s*LỚP\s+(\d{1,2})\s*$')
STRAND_HDR = re.compile(r'^\s*([A-D])\.\s+(\S.{3,60})$')
TOPIC_HDR = re.compile(r'^\s*([A-D])(\d)\.\s+(\S.*)$')

def main():
    grade = None
    strand = {}   # A → tên mạch (lấy lần đầu gặp)
    topics = {}   # A1 → tên chủ đề
    outcomes = []
    errors = []
    normalized = 0
    cur = None  # outcome đang gom text

    def flush():
        nonlocal cur
        if cur:
            cur['text'] = re.sub(r'\s+', ' ', cur['text']).strip()
            outcomes.append(cur)
            cur = None

    pages = sorted(f for f in os.listdir(SRC) if f.endswith('.json'))
    for pf in pages:
        d = json.load(open(f'{SRC}/{pf}'))
        page = d['pdf_page']
        if page < 14:  # phần I-IV.1 là văn xuôi/bảng khái quát — ngoài phạm vi mã
            continue
        for l in d['lines']:
            t = l['text'].strip()
            m = GRADE_HDR.match(t)
            if m:
                flush()
                grade = int(m.group(1))
                continue
            m = STRAND_HDR.match(t)
            if m and l['x'] < 0.30:
                flush()
                strand.setdefault(m.group(1), m.group(2).strip())
                continue
            m = TOPIC_HDR.match(t)
            if m and l['x'] < 0.22:
                # header chủ đề ở cột trái (tên có thể tràn dòng — lấy phần đầu)
                topics.setdefault(f'{m.group(1)}{m.group(2)}', m.group(3).strip())
                # KHÔNG continue: dòng này không chứa mã outcome nên vô hại
            m = CODE.search(t)
            if m:
                flush()
                g = int(m.group(1))
                letter = norm_letter(m.group(2))
                if letter is None:
                    errors.append(f'p{page}: F1 mã hỏng không cứu được: "{t[:60]}"')
                    continue
                if m.group(2) != letter:
                    normalized += 1
                code = f'{g}.{letter}{m.group(3)}.{"MR" if m.group(4) else ""}{m.group(5)}'
                if grade is None:
                    errors.append(f'p{page}: F2 mã {code} trước mọi header LỚP')
                    continue
                status = 'SOURCE_EXPLICIT'
                note = None
                if g != grade:
                    # Khôi phục HẸP: OCR hay đọc 9→2. Chỉ nhận khi thay số lớp
                    # bằng lớp của section; ghi INFERRED, không giả làm nguyên văn.
                    fixed = f'{grade}.{letter}{m.group(3)}.{"MR" if m.group(4) else ""}{m.group(5)}'
                    note = f'OCR đọc lớp "{g}" trong mã; section là LỚP {grade} — khôi phục thành {fixed}'
                    errors.append(f'p{page}: F2-RECOVERED {code} → {fixed} (INFERRED)')
                    code, g = fixed, grade
                    status = 'INFERRED_OCR_CORRECTED'
                cur = {
                    'code': code, 'grade': g,
                    'strand': letter, 'topic': f'{letter}{m.group(3)}',
                    'extended': bool(m.group(4)),
                    'text': t[m.end():], 'page': page,
                    'status': status,
                    **({'note': note} if note else {}),
                }
            elif cur is not None:
                # dòng tiếp của outcome — dừng nếu là header bảng lặp lại
                if t in ('Chủ đề', 'Nội dung', 'Yêu cầu cần đạt') or t.isdigit():
                    continue
                cur['text'] += ' ' + t
    flush()

    # F3 kiểm chéo: extended ⟺ MR trong mã (theo định nghĩa nguồn — tautology có chủ đích,
    # giữ làm chốt hồi quy nếu parser đổi)
    for o in outcomes:
        assert o['extended'] == ('MR' in o['code'].split('.')[2]), o['code']

    # trùng mã = F1
    seen = {}
    for o in outcomes:
        if o['code'] in seen:
            errors.append(f"F1 mã trùng: {o['code']} (p{seen[o['code']]} và p{o['page']})")
        seen[o['code']] = o['page']

    out = {
        'source': {
            'sourceId': 'vn-moet-qd2422-2026',
            'documentNumber': '2422/QĐ-BGDĐT',
            'title': 'Khung nội dung giáo dục trí tuệ nhân tạo cho học sinh phổ thông',
            'issuingAuthority': 'Bộ Giáo dục và Đào tạo',
            'issuedDate': '2026-08-18',
            'sourceType': 'OFFICIAL',
            'authorityLevel': 'PRIMARY/OFFICIAL — quyết định ban hành khung',
            'localFile': 'nguon-chi-thuc/van ban quy dinh/20_QD2422_….pdf',
            'sha256_16': 'ce35ebd7c6106d79',
            'extractionMethod': 'apple-vision-ocr + parse_qd2422.py (deterministic)',
            'legalInterpretationStatus': 'LEGAL INTERPRETATION / REVIEW PENDING',
            'ocrLetterNormalizations': normalized,
        },
        'strands': strand,
        'topics': {k: TOPIC_NAMES.get(k, v) for k, v in topics.items()},
        'topicNameStatus': 'CURATED_FROM_SOURCE (header tràn dòng — ghép đa lần xuất hiện, kiểm tay)',
        'knownLimitations': [
            'Cột "Nội dung" (cột giữa) CHƯA trích riêng — text outcome là cột YCCĐ;'
            ' vài mảnh cột giữa có thể lẫn vào text do OCR trộn dòng (đánh dấu chờ đối soát).',
            'Chính tả OCR trong text outcome chưa hiệu đính — mã và cấu trúc là phần tất định.',
        ],
        'outcomes': outcomes, 'errors': errors,
    }
    json.dump(out, open('poc-out/vbqd/qd2422-extracted.json', 'w'),
              ensure_ascii=False, indent=1)

    by_grade = {}
    for o in outcomes:
        k = o['grade']
        by_grade.setdefault(k, [0, 0])
        by_grade[k][o['extended']] += 1
    print(f"OUTCOMES: {len(outcomes)} · chủ đề: {len(topics)} · mạch: {len(strand)}")
    for g in sorted(by_grade):
        c, mr = by_grade[g]
        print(f"  Lớp {g:2d}: {c:3d} cốt lõi + {mr:2d} mở rộng")
    print(f"chuẩn hoá chữ-mã do OCR: {normalized}")
    print(f"LỖI ({len(errors)}):")
    for e in errors:
        print(' ⚠️', e)

if __name__ == '__main__':
    main()
