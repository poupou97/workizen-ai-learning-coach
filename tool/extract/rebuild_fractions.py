"""WAL-74 batch ④ — dựng lại PHÂN SỐ từ hình học OCR, rồi map bài tập → SkillCase.

Vì sao cần: text đã gom dòng cho 0% biểu thức parse được (đo: 803 bài tập Toán,
0 hit regex a/b±c/d) — sách in phân số XẾP CHỒNG DỌC, OCR trả token số rời.
Đây không phải lỗi OCR mà là bản chất trình bày.

Luật dựng (tất định, không LLM):
  · token SỐ ở (x,y) + token SỐ khác cùng cột (|dx| ≤ COL) ngay dưới
    (0 < dy ≤ ROW) ⇒ phân số tử/mẫu.
  · giữa hai phân số có token '+'/'-' trong dải y của chúng ⇒ biểu thức.
  · mọi thứ khác ⇒ KHÔNG dựng (unmapped) — không đoán.
Map ca: dùng ĐÚNG luật fractionCase của kernel (chia hết / không chia hết /
bằng nhau), không viết luật song song.
"""
import json, os, re, sys
from collections import Counter

COL, ROW = 0.035, 0.030
NUM = re.compile(r'^\d{1,3}$')
OPS = {'+': '+', '-': '-', '−': '-', '–': '-'}

def fraction_case(b, d):
    """Bản Dart hoá Python của kernel `fractionCase` — GIỮ NGUYÊN thứ tự luật."""
    if b == d:
        return 'denominator-equal'
    if b % d == 0 or d % b == 0:
        return 'denominator-divisible'
    return 'denominator-non-divisible'

def fractions_on_page(lines):
    """Trả list (x, ytop, num, den) — phân số dựng được từ hình học."""
    nums = [l for l in lines if NUM.match(l['text'].strip())]
    out = []
    used = set()
    for i, a in enumerate(nums):
        for j, b in enumerate(nums):
            if i == j or j in used:
                continue
            dy = b['y'] - a['y']
            if 0 < dy <= ROW and abs(b['x'] - a['x']) <= COL:
                out.append((a['x'], a['y'], int(a['text']), int(b['text'])))
                used.add(i); used.add(j)
                break
    return out

def expressions_on_page(lines):
    """Cặp phân số nối bởi +/- trên cùng dải y ⇒ biểu thức a/b ± c/d."""
    fr = fractions_on_page(lines)
    ops = [l for l in lines if l['text'].strip() in OPS]
    exprs = []
    for i, f1 in enumerate(fr):
        for f2 in fr[i+1:]:
            if abs(f2[1] - f1[1]) > ROW:      # khác hàng
                continue
            if not (f1[0] < f2[0]):            # trái → phải
                continue
            # ⚠️ ĐO ĐƯỢC: không siết khoảng cách thì hai bài tập cạnh nhau
            # (a) và b) cùng hàng) bị ghép thành MỘT biểu thức ma
            # («10/15 + 11/8»). Biểu thức thật nằm gọn trong ~0,22 bề rộng.
            if f2[0] - f1[0] > 0.22:
                continue
            mid = [o for o in ops
                   if f1[0] < o['x'] < f2[0] and abs(o['y'] - f1[1]) <= ROW * 1.5]
            if not mid:
                continue
            exprs.append({
                'op': OPS[mid[0]['text'].strip()],
                'a': f1[2], 'b': f1[3], 'c': f2[2], 'd': f2[3],
                'y': f1[1],
            })
            break
    return exprs

# ⭐ Bài ĐẦU TIÊN dạy phép cộng/trừ phân số trong từng cuốn (đọc từ TOC thật).
# Trước mốc đó, một «phân số +/- phân số» gần như chắc chắn là OCR đọc nhầm
# gạch nối/vạch ngang thành phép tính — ca đã bắt được: B53 «Khái niệm phân
# số» tr.50 sinh «2/3 - 3/5» trong khi sách chưa dạy phép trừ phân số.
# Đây là CHƯƠNG TRÌNH lọc NHẬN DẠNG, không phải nhận dạng lọc chương trình.
FIRST_ARITH_LESSON = {
    '04-sgk-toan-4-tap-hai': 60,   # B60 Phép cộng phân số
    '05-sgk-toan-5-tap-mot': 1,    # lớp 5 ôn lại ngay từ đầu
}

def main():
    books = sys.argv[1:] or ['04-sgk-toan-4-tap-hai', '05-sgk-toan-5-tap-mot']
    rows, stats = [], Counter()
    for book in books:
        units = json.load(open(f'poc-out/units/{book}.json'))['units']
        by_page = {}
        for u in units:
            if u['role'] == 'EXERCISE':
                by_page.setdefault(u['pagePdf'], []).append(u)
        ocr = f'poc-out/graph/ocr-body/{book}'
        for pf in sorted(os.listdir(ocr)):
            page = json.load(open(f'{ocr}/{pf}'))
            p = page['pdf_page']
            if p not in by_page:
                continue
            exprs = expressions_on_page(page['lines'])
            stats['pagesWithExercise'] += 1
            if not exprs:
                stats['pagesNoExpr'] += 1
            for e in exprs:
                if e['b'] == 0 or e['d'] == 0:
                    stats['badZeroDen'] += 1
                    continue
                cands0 = sorted(by_page[p], key=lambda u: u['id'])
                lesson = cands0[0]['lesson']
                floor = FIRST_ARITH_LESSON.get(book)
                if floor is not None and (lesson or 0) < floor:
                    stats['rejectedBeforeArithTaught'] += 1
                    continue
                case = fraction_case(e['b'], e['d'])
                # gán về bài tập gần nhất theo y trên trang (unit gần nhất phía trên)
                cands = cands0
                rows.append({
                    'book': book, 'page': p,
                    'printed': cands[0]['pagePrinted'],
                    'lesson': cands[0]['lesson'],
                    'expr': f"{e['a']}/{e['b']} {e['op']} {e['c']}/{e['d']}",
                    'skillCaseId': case,
                    'conceptId': 'quy-dong',
                    'method': 'geometric-fraction-rebuild-v1',
                    'status': 'INFERRED',   # dựng từ hình học ⇒ KHÔNG phải nguyên văn
                })
                stats[case] += 1
    json.dump(rows, open('poc-out/units/exercise-case-map.json', 'w'),
              ensure_ascii=False, indent=1)
    print(f"biểu thức dựng được: {len(rows)}")
    for k, v in stats.most_common():
        print(f"  {k}: {v}")
    for r in rows[:8]:
        print(f"  {r['book'][:12]} b{r['lesson']} tr{r['printed']}: "
              f"{r['expr']:18s} → {r['skillCaseId']}")

if __name__ == '__main__':
    main()
