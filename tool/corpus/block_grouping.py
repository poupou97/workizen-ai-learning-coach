#!/usr/bin/env python3
"""GOM DÒNG THÀNH KHỐI — và cách ĐO xem luật gom nào đúng.

Luật đang chạy (`lesson_reading.blocks`) ghép tham lam và chỉ neo vào DÒNG
CUỐI của khối. Hệ quả là TRÔI NGANG bắc cầu: A(x .09–.50) → B(x .46–.90) →
C(x .86–.95) nối được hết, dù A và C không hề chồng nhau. Đo trên máy: một
khối 23 dòng trải `x=0.092..0.900` nuốt cả cột trái lẫn dải hình của trang.

⛔ KHÔNG thay một ngưỡng ma này bằng một ngưỡng ma khác. Nên ở đây có NHIỀU
luật ứng viên, và một bộ nhãn ĐỌC ĐƯỢC TỪ HÌNH HỌC TRANG để chấm chúng:

  FALSE_MERGE  khối chứa ≥2 CỤM x rời hẳn nhau (chồng nhau = 0), mỗi cụm ≥2
               dòng. Không cần ngưỡng: hai cụm không chồng nhau một chút nào
               thì không thể là một cột chữ.
  FALSE_SPLIT  hai khối cùng cột (chồng ≥90% cạnh hẹp hơn), cách nhau đúng
               một khoảng dòng bình thường, mà khối trên KHÔNG kết câu và
               khối dưới MỞ ĐẦU bằng chữ thường ⇒ một đoạn bị cắt đôi.

Hai nhãn ấy là bằng chứng, không phải ý thích: cái đầu thuần hình học, cái
sau cộng thêm một sự thật về chính tả tiếng Việt.
"""
import re
import statistics

XGAP = 0.04          # dung sai chồng x của luật CŨ (giữ để so sánh)
YGAP = 1.8           # khoảng cách dọc tối đa, tính theo chiều cao dòng
SAME_COL = 0.90      # chồng bao nhiêu thì coi là cùng một cột (dùng CHẤM, không phải gom)
ENDS_SENTENCE = re.compile(r'[.!?:;…»"]\s*$')
STARTS_LOWER = re.compile(r'^\s*[a-zà-ỹ]')


def _span(l):
    return l['x'], l['x'] + (l.get('w') or 0)


def _ov(a, b):
    return min(a[1], b[1]) - max(a[0], b[0])


def _near_y(l, last, ygap=YGAP):
    h = l.get('h') or 0.02
    return 0 <= l['y'] - last['y'] <= ygap * max(h, last.get('h') or h)


def group(lines, rule='last', ygap=YGAP):
    """Gom dòng thành khối theo `rule`. Trả về list các list dòng.

    - `last`  : luật ĐANG CHẠY — chồng với DÒNG CUỐI (dung sai `XGAP`)
    - `accum` : chồng với DẢI X TÍCH LUỸ của khối, ít nhất nửa cạnh hẹp hơn
    - `core`  : chồng với LÕI của khối (giao của mọi dòng đã có) > 0
    - `align` : mép trái HOẶC mép phải thẳng hàng với khối (dung sai `XGAP`)
    """
    ls = sorted([l for l in lines if (l.get('text') or '').strip()],
                key=lambda l: (l['y'], l['x']))
    out, meta = [], []
    for l in ls:
        s = _span(l)
        for b, m in zip(out, meta):
            if not _near_y(l, b[-1], ygap):
                continue
            if rule == 'last':
                ok = _ov(s, _span(b[-1])) > -XGAP
            elif rule == 'accum':
                ov = _ov(s, m['acc'])
                narrow = min(s[1] - s[0], m['acc'][1] - m['acc'][0])
                ok = narrow > 0 and ov >= 0.5 * narrow
            elif rule == 'core':
                ok = _ov(s, m['core']) > 0
            elif rule == 'median':
                import statistics as _st
                mx0 = _st.median([sp[0] for sp in m['spans']])
                mx1 = _st.median([sp[1] for sp in m['spans']])
                ov = _ov(s, (mx0, mx1))
                narrow = min(s[1] - s[0], mx1 - mx0)
                ok = narrow > 0 and ov >= 0.5 * narrow
            elif rule == 'corefrac':
                ov = _ov(s, m['core'])
                cw = m['core'][1] - m['core'][0]
                ok = cw > 0 and ov >= 0.5 * cw
            elif rule == 'first':
                ov = _ov(s, m['first'])
                narrow = min(s[1] - s[0], m['first'][1] - m['first'][0])
                ok = narrow > 0 and ov >= 0.5 * narrow
            elif rule == 'align':
                ok = (abs(s[0] - m['acc'][0]) <= XGAP or abs(s[1] - m['acc'][1]) <= XGAP)
            else:
                raise ValueError(rule)
            if ok:
                b.append(l)
                m['acc'] = (min(m['acc'][0], s[0]), max(m['acc'][1], s[1]))
                m['core'] = (max(m['core'][0], s[0]), min(m['core'][1], s[1]))
                m['spans'].append(s)
                break
        else:
            out.append([l])
            meta.append(dict(acc=s, core=s, first=s, spans=[s]))
    return out


def x_clusters(block):
    """Cụm dòng nối nhau qua chồng x. ≥2 cụm rời hẳn ⇒ khối gom nhầm."""
    spans = sorted((_span(l) for l in block))
    clusters = []
    for s in spans:
        for c in clusters:
            if _ov(s, c['span']) > 0:
                c['span'] = (min(c['span'][0], s[0]), max(c['span'][1], s[1]))
                c['n'] += 1
                break
        else:
            clusters.append(dict(span=s, n=1))
    # gộp lại các cụm đã chạm nhau sau khi nới
    merged = True
    while merged:
        merged = False
        for i in range(len(clusters)):
            for j in range(i + 1, len(clusters)):
                if _ov(clusters[i]['span'], clusters[j]['span']) > 0:
                    clusters[i]['span'] = (min(clusters[i]['span'][0], clusters[j]['span'][0]),
                                           max(clusters[i]['span'][1], clusters[j]['span'][1]))
                    clusters[i]['n'] += clusters[j]['n']
                    clusters.pop(j)
                    merged = True
                    break
            if merged:
                break
    return clusters


def disjoint_pairs(blocks_):
    """Khối chứa ÍT NHẤT một cặp dòng KHÔNG chồng x chút nào.

    ⚠ Nhãn `false_merges` (≥2 CỤM rời, mỗi cụm ≥2 dòng) BỎ LỌT một kiểu hỏng
    thật: một khối rộng nuốt dần mọi dòng hẹp nằm trong nó — mọi dòng đều nối
    được qua các dòng rộng nên chỉ thành MỘT cụm. Đo được: luật `accum` biến
    khối 23 dòng của Vật lí 11 trang 21 thành khối 42 dòng mà `false_merges`
    vẫn báo 0. Nhãn này bắt đúng chỗ ấy: trong một cột chữ thật, không có hai
    dòng nào rời hẳn nhau.
    """
    n = 0
    for b in blocks_:
        spans = [_span(l) for l in b]
        if any(_ov(spans[i], spans[j]) <= 0
               for i in range(len(spans)) for j in range(i + 1, len(spans))):
            n += 1
    return n


def false_merges(blocks_):
    """Khối chắc chắn gom nhầm: ≥2 cụm x RỜI HẲN, mỗi cụm ≥2 dòng."""
    n = 0
    for b in blocks_:
        cs = [c for c in x_clusters(b) if c['n'] >= 2]
        if len(cs) >= 2:
            n += 1
    return n


def _median_line_gap(b):
    ys = sorted(l['y'] for l in b)
    gaps = [ys[i + 1] - ys[i] for i in range(len(ys) - 1)]
    return statistics.median(gaps) if gaps else None


def false_splits(blocks_):
    """Đoạn bị cắt đôi: cùng cột, cách nhau một khoảng dòng bình thường, câu
    chưa kết mà khối sau mở đầu bằng chữ thường."""
    bs = sorted(blocks_, key=lambda b: min(l['y'] for l in b))
    n = 0
    for i, a in enumerate(bs):
        ga = _median_line_gap(a)
        if ga is None:
            continue
        abot = max(l['y'] for l in a)
        aspan = (min(l['x'] for l in a), max(l['x'] + (l.get('w') or 0) for l in a))
        atxt = sorted(a, key=lambda l: l['y'])[-1].get('text') or ''
        if ENDS_SENTENCE.search(atxt):
            continue
        for c in bs[i + 1:]:
            ctop = min(l['y'] for l in c)
            if not (0 < ctop - abot <= 1.5 * ga):
                continue
            cspan = (min(l['x'] for l in c), max(l['x'] + (l.get('w') or 0) for l in c))
            narrow = min(aspan[1] - aspan[0], cspan[1] - cspan[0])
            if narrow <= 0 or _ov(aspan, cspan) < SAME_COL * narrow:
                continue
            ctxt = sorted(c, key=lambda l: l['y'])[0].get('text') or ''
            if STARTS_LOWER.match(ctxt):
                n += 1
            break
    return n
