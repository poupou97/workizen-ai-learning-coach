"""Trích cấu trúc sách từ trang MỤC LỤC — TẤT ĐỊNH, 0 lượt gọi LLM.

Luật hình học đọc từ trang thật (Toán 5 tập một, PDF trang 5):
  cột SỐ CHỦ ĐỀ  x ≈ 0.17
  cột NỘI DUNG   x ≈ 0.23   ("Bài N. <tên>" hoặc TÊN CHỦ ĐỀ viết hoa)
  cột TRANG      x ≈ 0.86

Mọi thứ trích ở đây là SOURCE_DERIVED: NXB tự khẳng định, có số trang, nên
`citableAsTextbookFact` = true. KHÔNG có suy luận nào trong tệp này — đó là
chủ đích: suy luận thuộc về tầng LLM và phải mang nhãn khác.
"""
import json, re, sys, unicodedata

def norm(s): return unicodedata.normalize('NFC', s).strip()

def parse(page_json, *, x_theme=0.17, x_body=0.23, x_page=0.86, tol=0.05):
    lines = json.load(open(page_json))['lines']
    body  = [l for l in lines if abs(l['x'] - x_body)  < tol]
    pages = [l for l in lines if abs(l['x'] - x_page)  < tol and l['text'].strip().isdigit()]
    themes= [l for l in lines if abs(l['x'] - x_theme) < 0.03 and l['text'].strip().isdigit()]

    def page_at(y):
        """Số trang cùng HÀNG — ghép theo y, không theo thứ tự trong mảng."""
        c = [p for p in pages if abs(p['y'] - y) < 0.012]
        return int(c[0]['text']) if c else None

    chapters, cur = [], None
    for l in sorted(body, key=lambda l: l['y']):
        t = norm(l['text'])
        m = re.match(r'B[àa]i\s*(\d+)\s*[.．]\s*(.+)', t)
        if m:
            if cur is None:      # bài xuất hiện trước khi có chủ đề nào
                cur = {'number': None, 'title': None, 'page_start': None, 'lessons': []}
                chapters.append(cur)
            cur['lessons'].append({
                'number': int(m.group(1)), 'title': m.group(2).strip(),
                'page_start': page_at(l['y']),
            })
        elif t == t.upper() and len(t) > 4:      # tên chủ đề viết hoa
            n = [x for x in themes if abs(x['y'] - l['y']) < 0.015]
            cur = {'number': int(n[0]['text']) if n else None,
                   'title': t, 'page_start': page_at(l['y']), 'lessons': []}
            chapters.append(cur)

    # khoảng trang của bài = tới trang bắt đầu của bài kế tiếp
    flat = [ls for c in chapters for ls in c['lessons']]
    for a, b in zip(flat, flat[1:]):
        if a['page_start'] and b['page_start']:
            a['page_end'] = b['page_start'] - 1
    return chapters

if __name__ == '__main__':
    ch = parse(sys.argv[1])
    print(json.dumps(ch, ensure_ascii=False, indent=2))
