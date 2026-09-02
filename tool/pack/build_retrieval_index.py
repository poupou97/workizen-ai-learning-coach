"""WAL-81 (GĐ8) — retrieval index trên corpus ĐÃ QUA QA + benchmark 7 chỉ số.

Chỉ index batch đã qua SCALE GATE (luật GĐ7: không qua gate không được đếm).
Graph quyết ĐÂU (scope theo LearningStage — luật visible() của G2), retrieval
quyết GÌ (BM25 trong scope). Không vector — chưa có failure nào vector giải
(WAL-41); thêm embedding phải có benefit đo được trên failure cụ thể.

Benchmark §7 (GRAPH-GUIDED-...-RAG.md): Source Recall · Curriculum Precision ·
SkillCase Precision · Citation Correctness · Unsupported Claim Rate ·
Future-Knowledge Leakage (≈0 điều kiện sống) · Method Permission Violation (≈0).
Đối chứng: chạy CẢ biến thể no-filter để chứng minh filter là thứ giữ luật.
"""
import json, math, re, sqlite3, os
from collections import defaultdict

BOOKS = ['05-sgk-toan-5-tap-mot', '05-sgk-toan-5-tap-hai',
         '04-sgk-toan-4-tap-mot', '04-sgk-toan-4-tap-hai',
         '05-sgk-tieng-viet-5-tap-mot', '05-sgk-tieng-viet-5-tap-hai']

units = []
for b in BOOKS:
    grade = 4 if b.startswith('04') else 5
    vol = 2 if 'tap-hai' in b else 1
    for u in json.load(open(f'poc-out/units/{b}.json'))['units']:
        u.update(book=b, grade=grade, vol=vol)
        units.append(u)

# ── index SQLite FTS5 (định dạng pack ADR-006) ─────────────────────────────
db = 'poc-out/pack/sam-units.db'
if os.path.exists(db): os.remove(db)
con = sqlite3.connect(db)
con.executescript('''
CREATE TABLE unit(id TEXT PRIMARY KEY, book TEXT, grade INT, vol INT,
                  lesson INT, role TEXT, page INT, text TEXT);
CREATE VIRTUAL TABLE unit_fts USING fts5(text, content='unit', content_rowid='rowid');
''')
for u in units:
    con.execute('INSERT INTO unit VALUES (?,?,?,?,?,?,?,?)',
                (u['id'], u['book'], u['grade'], u['vol'], u['lesson'] or 0,
                 u['role'], u['pagePrinted'], u['text']))
con.execute("INSERT INTO unit_fts(rowid, text) SELECT rowid, text FROM unit")
con.commit()
size = os.path.getsize(db)
print(f'index: {len(units)} unit → {db} ({size:,} B)')

def visible(u, stage):
    g, vol, lesson = stage
    if u['grade'] != g: return u['grade'] < g
    if u['vol'] != vol: return u['vol'] < vol
    return (u['lesson'] or 10**6) <= lesson

def tok(s): return re.findall(r'\w+', s.lower())

def bm25(query, docs, k1=1.5, b=0.75):
    qs = tok(query)
    N = len(docs) or 1
    avg = sum(len(tok(d['text'])) for d in docs) / N
    df = defaultdict(int)
    for d in docs:
        for w in set(tok(d['text'])): df[w] += 1
    def score(d):
        ws = tok(d['text']); L = len(ws) or 1
        s = 0
        for q in qs:
            f = ws.count(q)
            if not f: continue
            idf = math.log(1 + (N - df[q] + .5) / (df[q] + .5))
            s += idf * f * (k1+1) / (f + k1*(1 - b + b*L/avg))
        return s
    return sorted(docs, key=score, reverse=True)

# method exposure cho Method-Permission check
methods = json.load(open('poc-out/units/method-catalogue.json'))
def method_units_beyond(stage):
    ids = set()
    for m in methods:
        if not visible({'grade': m['grade'], 'vol': 1 if 'tap-mot' in m['book'] else 2,
                        'lesson': m['lesson']}, stage):
            ids.add((m['book'], m['lesson'], m['pagePrinted']))
    return ids

# ── ground truth: 8 query tất định từ tri thức đã đo ───────────────────────
QUERIES = [
  {'q': 'quy đồng mẫu số hai phân số', 'stage': (4, 2, 61), 'grade_ok': {4},
   'lesson_expect': {60, 61}},
  {'q': 'quy đồng mẫu số hai phân số', 'stage': (5, 1, 6), 'grade_ok': {4, 5},
   'lesson_expect': {6, 60, 61}},
  {'q': 'cộng hai phân số khác mẫu số', 'stage': (5, 1, 6), 'grade_ok': {4, 5},
   'lesson_expect': {6}},
  {'q': 'so sánh các số thập phân', 'stage': (5, 1, 11), 'grade_ok': {5},
   'lesson_expect': {10, 11}},
  {'q': 'nhân một số thập phân với một số thập phân', 'stage': (5, 1, 21),
   'grade_ok': {5}, 'lesson_expect': {21}},
  {'q': 'chia một số thập phân cho một số tự nhiên', 'stage': (5, 1, 22),
   'grade_ok': {5}, 'lesson_expect': {22}},
  {'q': 'thể tích của hình lập phương', 'stage': (5, 2, 53), 'grade_ok': {5},
   'lesson_expect': {52, 53}},
  {'q': 'làm tròn số thập phân', 'stage': (5, 1, 13), 'grade_ok': {5},
   'lesson_expect': {13}},
]

def run(variant):
    K = 5
    recall = curr_prec_ok = curr_tot = cite_ok = 0
    leak = unsupported = mpv = 0
    for t in QUERIES:
        pool = [u for u in units if visible(u, t['stage'])] \
               if variant == 'graph+bm25' else units
        top = bm25(t['q'], pool)[:K]
        if any((u['lesson'] or 0) in t['lesson_expect'] and
               u['grade'] in t['grade_ok'] for u in top):
            recall += 1
        for u in top:
            curr_tot += 1
            if u['grade'] in t['grade_ok']: curr_prec_ok += 1
            if isinstance(u['pagePrinted'], int): cite_ok += 1
            if not u['provenance'].get('assertion'): unsupported += 1
            if not visible(u, t['stage']): leak += 1
            if (u['book'], u['lesson'], u['pagePrinted']) in \
               method_units_beyond(t['stage']) and u['role'] == 'RULE':
                mpv += 1
    n = len(QUERIES)
    print(f"{variant:12s} SourceRecall {recall}/{n} · CurrPrecision "
          f"{curr_prec_ok}/{curr_tot} · Citation {cite_ok}/{curr_tot} · "
          f"Unsupported {unsupported} · LEAK {leak} · MethodViolation {mpv}")

print('\nBenchmark 7 chỉ số (K=5, 8 query ground-truth):')
run('graph+bm25')
run('no-filter')  # đối chứng — leak phải >0 để chứng minh filter là thứ giữ luật
