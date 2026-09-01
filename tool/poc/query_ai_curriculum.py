"""WAL-92 — POC truy vấn AI Curriculum (QĐ 2422) LOCAL, graph-first, fail-closed.

Luật kế thừa WAL-41: lọc THEO CẤU TRÚC (lớp/mạch/chủ đề) trước, text sau;
F8: truy vấn ở lớp g KHÔNG BAO GIỜ trả outcome lớp > g như thể được phép.
Mọi câu trả lời truy về mã + trang. 0 LLM, 0 embedding (chưa đo thấy cần).
"""
import json, sys, unicodedata

D = json.load(open('poc-out/vbqd/qd2422-extracted.json'))
OUT = D['outcomes']

def _n(s):
    s = unicodedata.normalize('NFD', s.lower())
    return ''.join(c for c in s if not unicodedata.combining(c))

def for_grade(g, include_extended=True):
    """«Lớp g cần năng lực AI gì?» — chỉ lớp g, không lộ lớp trên (F8)."""
    return [o for o in OUT if o['grade'] == g
            and (include_extended or not o['extended'])]

def search(term, up_to_grade=None):
    """Tìm theo text, CHẶN trần lớp — fail closed khi vượt."""
    t = _n(term)
    hits = [o for o in OUT if t in _n(o['text'])]
    if up_to_grade is not None:
        hits = [o for o in hits if o['grade'] <= up_to_grade]
    return hits

def progression(strand):
    """Tiến trình một mạch qua 12 lớp — thứ tự LỚP, không phải thứ tự mã (F4)."""
    return sorted((o for o in OUT if o['strand'] == strand),
                  key=lambda o: (o['grade'], o['topic'], o['extended'], o['code']))

def beyond_grade(code, current_grade):
    """«Khái niệm này có vượt lớp hiện tại không?» — tra bằng MÃ."""
    o = next((x for x in OUT if x['code'] == code), None)
    if o is None:
        return None  # không có mã ⇒ fail closed, không đoán
    return o['grade'] > current_grade

def cite(o):
    return f"[{o['code']} · tr.{o['page']}{' · MR' if o['extended'] else ''}]"

if __name__ == '__main__':
    print('=== Q1: Lớp 3 cần năng lực AI gì? (cốt lõi) ===')
    for o in for_grade(3, include_extended=False)[:5]:
        print(f"  {cite(o)} {o['text'][:80]}")
    print(f"  … tổng {len(for_grade(3, include_extended=False))} cốt lõi + "
          f"{len(for_grade(3)) - len(for_grade(3, include_extended=False))} mở rộng")

    print('\n=== Q2: Lớp 7 hiểu gì về kiểm chứng kết quả AI? ===')
    for o in search('kiểm chứng', up_to_grade=7):
        print(f"  {cite(o)} {o['text'][:80]}")

    print('\n=== Q3: tiến trình mạch D (thiết kế hệ AI) — 5 mốc ===')
    pro = progression('D')
    for o in [pro[0], pro[len(pro)//4], pro[len(pro)//2], pro[3*len(pro)//4], pro[-1]]:
        print(f"  L{o['grade']:2d} {cite(o)} {o['text'][:70]}")

    print('\n=== Q4: outcome nào đỡ hoạt động «nhận diện thông tin giả do AI tạo»? ===')
    for o in search('giả mạo', up_to_grade=12)[:4]:
        print(f"  {cite(o)} {o['text'][:80]}")

    print('\n=== Q5 (F8): «thuật toán» hỏi ở TRẦN LỚP 3 — có lộ lớp trên không? ===')
    l3 = search('thuật toán', up_to_grade=3)
    all_g = search('thuật toán')
    print(f"  trần lớp 3: {len(l3)} hit {[o['code'] for o in l3]}")
    print(f"  không trần: {len(all_g)} hit (lớp {sorted({o['grade'] for o in all_g})})")
    assert all(o['grade'] <= 3 for o in l3), 'F8 VỠ: lộ outcome lớp trên!'
    leak = [o for o in l3 if o['grade'] > 3]
    print(f"  F8: {'❌ LEAK' if leak else '✅ KHÔNG lộ lớp trên'}")

    print('\n=== Q6: beyond_grade — 9.C4.MR2 với học sinh lớp 5? ===')
    print(f"  vượt lớp: {beyond_grade('9.C4.MR2', 5)} · mã không tồn tại: "
          f"{beyond_grade('7.Z9.1', 5)} (None = fail closed)")

    import os
    raw = os.path.getsize('poc-out/vbqd/qd2422-extracted.json')
    import gzip
    gz = len(gzip.compress(open('poc-out/vbqd/qd2422-extracted.json','rb').read()))
    print(f"\n=== BYTES (ADR-006, đo không ước) ===")
    print(f"  structured JSON: {raw:,} B · gzip: {gz:,} B ({gz/raw:.0%}) · "
          f"{len(OUT)} outcome ⇒ ~{raw//len(OUT)} B/outcome thô")
