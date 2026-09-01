#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""WAL-41 — RAG retrieval POC: metadata-only vs +graph vs +BM25, ở HAI mức hạt.

Falsify: "graph quyết ĐÂU, retrieval quyết GÌ" — nếu graph-first LÀM MẤT bằng
chứng hữu ích thì báo cáo, không bảo vệ luận đề.
Corpus: unit tay-biên từ các trang ĐÃ ĐỌC (trích OCR thật, trang IN thật).
"""
import json, math, re
from collections import Counter

# ── CORPUS — atomic units (role tách); section = gộp theo (book,page,muc) ──
UNITS = [
 # Toán 4 tr.62 Bài 57 — ca chia hết (grade 4)
 dict(id='t4-62-rule', book='toan4', grade=4, page=62, lesson='t4-bai57', muc='bai57',
      role='RULE', concept='quy-dong', case='denominator-divisible',
      text='quy đồng mẫu số trường hợp có một mẫu số chia hết cho mẫu số còn lại lấy mẫu số lớn làm mẫu số chung giữ nguyên phân số có mẫu số lớn'),
 dict(id='t4-62-ex', book='toan4', grade=4, page=62, lesson='t4-bai57', muc='bai57',
      role='EXAMPLE', concept='quy-dong', case='denominator-divisible',
      text='ví dụ quy đồng một phần hai và ba phần tư mẫu số bốn chia hết cho hai lấy mẫu số chung là bốn'),
 # Toán 5 tr.20 Bài 6 — ca không chia hết (grade 5)
 dict(id='t5-20-rule', book='toan5', grade=5, page=20, lesson='t5-bai6', muc='bai6a',
      role='RULE', concept='quy-dong', case='denominator-non-divisible',
      text='hai mẫu số năm và hai không chia hết cho nhau lấy mẫu số chung là tích của hai mẫu số quy đồng mẫu số hai phân số'),
 dict(id='t5-20-ex', book='toan5', grade=5, page=20, lesson='t5-bai6', muc='bai6a',
      role='EXAMPLE', concept='quy-dong', case='denominator-non-divisible',
      text='ví dụ cộng hai phân số khác mẫu số ba phần năm và một phần hai quy đồng rồi cộng hai tử số'),
 # Toán 5 tr.38-39 Bài 11 — so sánh số thập phân (mục a: khám phá+quy tắc)
 dict(id='t5-38-ex', book='toan5', grade=5, page=38, lesson='t5-bai11', muc='bai11a',
      role='EXAMPLE', concept='so-sanh-so-thap-phan', case='integer-part-differs',
      text='ba phẩy năm lớn hơn hai phẩy bảy mươi lăm phần nguyên có ba lớn hơn hai so sánh chiều dài cây cầu'),
 dict(id='t5-39-rule', book='toan5', grade=5, page=39, lesson='t5-bai11', muc='bai11a',
      role='RULE', concept='so-sanh-so-thap-phan', case=None,
      text='muốn so sánh hai số thập phân nếu phần nguyên khác nhau phần nguyên lớn hơn thì số đó lớn hơn nếu phần nguyên bằng nhau so sánh phần thập phân lần lượt từ hàng phần mười hàng phần trăm'),
 dict(id='t5-39-exer', book='toan5', grade=5, page=39, lesson='t5-bai11', muc='bai11a',
      role='EXERCISE', concept='so-sanh-so-thap-phan', case=None,
      text='so sánh hai số thập phân ba mươi bảy phẩy hai chín và ba mươi sáu phẩy chín hai sắp xếp các số theo thứ tự từ bé đến lớn'),
 # Toán 5 tr.40 — MỤC SAU: số thập phân bằng nhau (tri thức TƯƠNG LAI với học sinh đang ở tr.39)
 dict(id='t5-40-rule', book='toan5', grade=5, page=40, lesson='t5-bai11', muc='bai11b',
      role='RULE', concept='so-sanh-so-thap-phan', case='unequal-decimal-length',
      text='số thập phân bằng nhau nếu viết thêm hoặc bỏ chữ số không ở tận cùng bên phải phần thập phân thì được một số thập phân bằng nó so sánh bảy mươi sáu phẩy ba và bảy mươi sáu phẩy ba mươi'),
 # Toán 5 tr.11-12 Bài 3 — ôn tập (reinforces, KHÔNG dạy)
 dict(id='t5-11-exer', book='toan5', grade=5, page=11, lesson='t5-bai3', muc='bai3',
      role='EXERCISE', concept='quy-dong', case=None,
      text='ôn tập phân số luyện tập rút gọn quy đồng so sánh phân số'),
 # TV5 tr.65-66 — từ đa nghĩa
 dict(id='tv5-66-rule', book='tv5', grade=5, page=66, lesson='tv5-tuan7', muc='tudanghia',
      role='RULE', concept='tu-da-nghia', case=None,
      text='từ đa nghĩa là từ có nhiều nghĩa trong đó có một nghĩa gốc và một hoặc một số nghĩa chuyển các nghĩa của một từ đa nghĩa luôn có mối liên hệ với nhau'),
 dict(id='tv5-65-exer', book='tv5', grade=5, page=65, lesson='tv5-tuan7', muc='tudanghia',
      role='EXERCISE', concept='tu-da-nghia', case=None,
      text='đọc đoạn thơ và các nghĩa của từ mắt tìm nghĩa thích hợp nghĩa nào là nghĩa gốc nghĩa nào là nghĩa chuyển'),
 # Toán 9 tr.119 glossary — TRI THỨC TƯƠNG LAI thật (distractor cho grade 5)
 dict(id='t9-119-glos', book='toan9', grade=9, page=119, lesson='t9-glossary', muc='glossary',
      role='DEFINITION', concept='can-bac-hai', case=None,
      text='căn bậc hai của số thực không âm phương trình bất phương trình hệ thức lượng trong tam giác vuông'),
]

# ── GRAPH (từ CurriculumEdge đã có trong domain) ──
PREREQ = {'t5-bai6': ['t4-bai57'], 't5-bai11': ['t5-bai3'], }   # xuyên lớp!
# stage: bài đã dạy tới (theo thứ tự corpus thật)
STAGES = {
 'grade4@bai57':  dict(grade=4, taught=['t4-bai57']),
 'grade5@bai6':   dict(grade=5, taught=['t5-bai3', 't5-bai6', 't4-bai57']),
 'grade5@bai11a': dict(grade=5, taught=['t5-bai3', 't5-bai6', 't4-bai57', 't5-bai11'],
                       taught_muc=['bai57', 'bai6a', 'bai3', 'bai11a']),  # CHƯA học mục b (tr.40)!
 'tv5@tuan7':     dict(grade=5, taught=['tv5-tuan7']),
}

# ── QUERIES + ground truth ──
QUERIES = [
 dict(q='cách quy đồng khi hai mẫu số không chia hết cho nhau', stage='grade5@bai6',
      concept='quy-dong', expect=['t5-20-rule'], forbid_future=True),
 dict(q='con quên cách quy đồng dạng một mẫu chia hết cho mẫu kia', stage='grade5@bai6',
      concept='quy-dong', expect=['t4-62-rule'],  # ⭐ cần đơn vị LỚP 4 — xuyên lớp
      forbid_future=True),
 dict(q='so sánh bảy mươi sáu phẩy ba và bảy mươi sáu phẩy ba mươi', stage='grade5@bai11a',
      concept='so-sanh-so-thap-phan', expect=[],  # ⭐ tr.40 là MỤC CHƯA HỌC ⇒ đúng = fail closed
      future_ids=['t5-40-rule'], forbid_future=True),
 dict(q='vì sao ba phẩy năm lớn hơn hai phẩy bảy mươi lăm', stage='grade5@bai11a',
      concept='so-sanh-so-thap-phan', expect=['t5-38-ex', 't5-39-rule'], forbid_future=True),
 dict(q='nghĩa gốc nghĩa chuyển của từ mắt', stage='tv5@tuan7',
      concept='tu-da-nghia', expect=['tv5-66-rule', 'tv5-65-exer'], forbid_future=True),
 dict(q='căn bậc hai là gì', stage='grade5@bai6', concept=None,
      expect=[], future_ids=['t9-119-glos'], forbid_future=True),  # grade 9 ⇒ fail closed
]

def tok(s): return re.findall(r'\w+', s.lower())

def bm25_scores(query, docs, k1=1.5, b=0.75):
    qs = tok(query); N = len(docs)
    dl = {d['id']: len(tok(d['text'])) for d in docs}
    avdl = sum(dl.values())/max(N,1)
    df = Counter(t for d in docs for t in set(tok(d['text'])))
    def score(d):
        tf = Counter(tok(d['text'])); s = 0
        for t in qs:
            if t not in tf: continue
            idf = math.log(1 + (N-df[t]+0.5)/(df[t]+0.5))
            s += idf * tf[t]*(k1+1)/(tf[t]+k1*(1-b+b*dl[d['id']]/avdl))
        return s
    return sorted(((score(d), d) for d in docs), key=lambda x: -x[0])

MIN_SCORE = 2.0  # ngưỡng fail-closed: dưới mức này coi như NO_EVIDENCE (đo được, không đoán)

def scope_metadata(stage, concept):
    st = STAGES[stage]
    return [u for u in UNITS if u['grade'] <= st['grade']
            and (concept is None or u['concept'] == concept)]

def scope_graph(stage, concept):
    st = STAGES[stage]
    lessons = set(st['taught'])
    for l in list(lessons): lessons.update(PREREQ.get(l, []))
    out = [u for u in UNITS if u['lesson'] in lessons
           and (concept is None or u['concept'] == concept)]
    if 'taught_muc' in st:  # độ mịn MỤC — ranh giới ca của concept #2
        out = [u for u in out if u['lesson'] not in st['taught'] or u['muc'] in st['taught_muc']
               or u['lesson'] != 't5-bai11']
        out = [u for u in out if not (u['lesson']=='t5-bai11' and u['muc'] not in st['taught_muc'])]
    return out

def run(variant, q):
    concept = q['concept']
    if variant.startswith('metadata'):
        docs = scope_metadata(q['stage'], concept)
    else:
        docs = scope_graph(q['stage'], concept)
    if variant.endswith('bm25'):
        scored = bm25_scores(q['q'], docs)
        return [d['id'] for sc, d in scored[:3] if sc >= MIN_SCORE]
    return [d['id'] for d in docs[:3]]

def evaluate():
    rows = []
    for v in ['metadata', 'metadata+bm25', 'graph', 'graph+bm25']:
        recall_hit = recall_tot = leak = at1 = 0
        for q in QUERIES:
            got = run(v, q)
            exp = q['expect']
            recall_tot += len(exp)
            recall_hit += len(set(got) & set(exp))
            fut = set(q.get('future_ids', []))
            if set(got) & fut: leak += 1
            if exp and got and got[0] == exp[0]: at1 += 1
        rows.append((v, f'{recall_hit}/{recall_tot}', leak, at1))
    print(f"{'variant':12} {'SourceRecall':13} {'FutureLeak':11} {'Top1'}")
    for r in rows: print(f"{r[0]:12} {r[1]:13} {r[2]:<11} {r[3]}")
    print()
    # chi tiết từng query cho variant tốt nhất + đối chứng metadata
    for v in ['metadata+bm25', 'graph+bm25']:
        print(f"── {v}")
        for q in QUERIES:
            got = run(v, q)
            fut = set(q.get('future_ids', []))
            mark = '💥LEAK' if set(got) & fut else ('✅' if set(got) >= set(q['expect']) and (q['expect'] or not (set(got) & fut)) else '·')
            print(f"  {mark} [{q['stage']}] {q['q'][:46]:46} → {got}")

if __name__ == '__main__':
    evaluate()
