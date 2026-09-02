"""WAL-74 — map RULE unit → conceptId, TẤT ĐỊNH ở mức tự tin được.

Luật: chỉ map CONCEPT (từ khoá bề mặt rõ ràng); KHÔNG map SkillCase từ text
quy tắc (đó là việc của applicability phân tích BÀI TẬP — WAL-33); không match
⇒ 'unmapped', không đoán. Mọi mapping mang extraction method để không đội lốt.
"""
import json, sys, unicodedata

def strip(s):
    # 'đ' (U+0111) KHÔNG phân rã qua NFD — phải thay tay, nếu không mọi từ
    # khoá chứa 'đ' đều trượt (bug thật: 'quy đồng', 'đổi chỗ' từng unmapped).
    s = unicodedata.normalize('NFD', s.lower().replace('đ', 'd').replace('Đ', 'd'))
    return ''.join(c for c in s if not unicodedata.combining(c))

# (từ khoá đã strip, conceptId) — thứ tự = ưu tiên; từ khoá phải ĐỦ ĐẶC TRƯNG
KEYS = [
    ('quy dong mau so', 'quy-dong'),
    ('cong (hoac tru) hai phan so', 'quy-dong'),  # B6 Toán 5: câu rule hợp nhất cộng-trừ-khác-mẫu, cốt lõi là quy đồng
    ('cong hai phan so', 'cong-phan-so'),
    ('tru hai phan so', 'tru-phan-so'),
    ('nhan hai phan so', 'nhan-phan-so'),
    ('chia hai phan so', 'chia-phan-so'),
    ('cong hai so thap phan', 'cong-so-thap-phan'),
    ('tru hai so thap phan', 'tru-so-thap-phan'),
    ('nhan mot so thap phan', 'nhan-so-thap-phan'),
    ('chia mot so thap phan', 'chia-so-thap-phan'),
    ('chia mot so tu nhien cho mot so thap phan', 'chia-so-thap-phan'),
    ('dien tich hinh tam giac', 'dien-tich-tam-giac'),
    ('dien tich hinh thang', 'dien-tich-hinh-thang'),
    ('dien tich hinh tron', 'dien-tich-hinh-tron'),
    ('chu vi hinh tron', 'chu-vi-hinh-tron'),
    ('doi cho cac so hang', 'tinh-chat-giao-hoan-cong'),
    ('doi cho cac thua so', 'tinh-chat-giao-hoan-nhan'),
    ('trung binh cong', 'so-trung-binh-cong'),
    # tập hai (batch ⑤) — từ khoá đọc từ RULE thật in ra khi chạy:
    ('ti so phan tram cua hai so', 'ti-so-phan-tram'),
    ('the tich cua hinh hop chu nhat', 'the-tich-hinh-hop-chu-nhat'),
    ('the tich cua hinh lap phuong', 'the-tich-hinh-lap-phuong'),
    ('van toc cua chuyen dong', 'van-toc'),
]

out = []
for book in sys.argv[1:]:
    d = json.load(open(f'poc-out/units/{book}.json'))
    for u in d['units']:
        if u['role'] not in ('RULE', 'RULE_CANDIDATE'):
            continue
        t = strip(u['text'])
        concept = next((c for k, c in KEYS if k in t[:120]), 'unmapped')
        out.append({'unitId': u['id'], 'book': book, 'lesson': u['lesson'],
                    'page': u['pagePrinted'], 'role': u['role'],
                    'conceptId': concept,
                    'method': 'deterministic-keyword-v1',
                    'head': u['text'][:60]})
json.dump(out, open('poc-out/units/rule-concept-map.json', 'w'),
          ensure_ascii=False, indent=1)
mapped = [o for o in out if o['conceptId'] != 'unmapped']
print(f'RULE map: {len(mapped)}/{len(out)} mapped')
for o in out:
    flag = '  ' if o['conceptId'] != 'unmapped' else '⚠️'
    print(f"{flag} {o['book'][:12]} b{o['lesson']:>2} → {o['conceptId']:26s} {o['head'][:44]}")
