"""WAL-83 — SAM KNOWLEDGE PACK compiler POC + benchmark A/B (ADR-006).

Nguồn liệu THẬT hiện có:
  · AI curriculum QĐ 2422: 267 outcome (qd2422-extracted.json)
  · ContentUnit tay-biên WAL-41: Toán 4-5 (rag_retrieval_poc.UNITS)
  · Bài học Toán 5: toan5_lessons.json
  · GĐ1 structure scan (structure-scan.json) — nếu đã có
Định dạng đo: (1) SQLite + FTS5 (ứng viên chính — Flutter đọc được qua sqlite3)
             (2) JSON + gzip (đối chứng)
A/B: FULL (một pack) vs MODULAR (core + module theo lớp).
LUẬT ADR-006: đo bytes, không ước từ cỡ PDF; ngoại suy phải ghi rõ NGOẠI SUY.
"""
import gzip, json, os, sqlite3, sys, time
sys.path.insert(0, 'tool/poc')
from rag_retrieval_poc import UNITS  # 12 unit tay-biên có provenance

OUT = 'poc-out/pack'

def load_sources():
    ai = json.load(open('poc-out/vbqd/qd2422-extracted.json'))
    lessons = json.load(open('poc-out/toan5_lessons.json'))
    scan = None
    if os.path.exists('poc-out/graph/structure-scan.json'):
        scan = json.load(open('poc-out/graph/structure-scan.json'))
    return ai, lessons, scan

SCHEMA = """
CREATE TABLE meta(k TEXT PRIMARY KEY, v TEXT);
CREATE TABLE ai_outcome(code TEXT PRIMARY KEY, grade INT, strand TEXT,
  topic TEXT, extended INT, text TEXT, page INT, status TEXT);
CREATE TABLE content_unit(id TEXT PRIMARY KEY, grade INT, role TEXT,
  case_id TEXT, text TEXT, source TEXT, page INT);
CREATE TABLE lesson(book_id TEXT, grade INT, number INT, title TEXT,
  page_start INT);
CREATE TABLE book(id TEXT PRIMARY KEY, grade INT, kind TEXT, subject TEXT,
  pages INT, lessons INT, status TEXT);
CREATE VIRTUAL TABLE fts USING fts5(kind, ref, body);
"""

def build_db(path, ai_outcomes, units, lessons, books, scan_lessons):
    if os.path.exists(path):
        os.remove(path)
    db = sqlite3.connect(path)
    db.execute('PRAGMA page_size=512')  # pack nhỏ: trang 4KB mặc định phí 8×
    db.executescript(SCHEMA)
    db.executemany('INSERT INTO ai_outcome VALUES(?,?,?,?,?,?,?,?)',
        [(o['code'], o['grade'], o['strand'], o['topic'], int(o['extended']),
          o['text'], o['page'], o['status']) for o in ai_outcomes])
    db.executemany('INSERT INTO content_unit VALUES(?,?,?,?,?,?,?)',
        [(u['id'], u.get('grade'), u.get('role'), u.get('case') or u.get('case_id'),
          u['text'], u.get('source', 'toan-kntt'), u.get('page')) for u in units])
    db.executemany('INSERT INTO lesson VALUES(?,?,?,?,?)', lessons)
    db.executemany('INSERT INTO book VALUES(?,?,?,?,?,?,?)', books)
    db.executemany('INSERT INTO fts VALUES(?,?,?)',
        [('ai', o['code'], o['text']) for o in ai_outcomes] +
        [('unit', u['id'], u['text']) for u in units] +
        [('lesson', l[0], l[3]) for l in lessons + scan_lessons])
    db.execute("INSERT INTO meta VALUES('packVersion','poc-2026-09-01')")
    db.execute("INSERT INTO meta VALUES('sources','vn-moet-qd2422-2026;toan45-kntt-wal41;k12-scan-gd1')")
    db.commit()
    # bytes từng bảng — đo bằng dbstat, không ước
    stat = {r[0]: r[1] for r in db.execute(
        "SELECT name, sum(pgsize) FROM dbstat GROUP BY name")}
    db.close()
    return os.path.getsize(path), stat

def main():
    ai, lessons_t5, scan = load_sources()
    outcomes = ai['outcomes']
    units = UNITS
    lessons = [('toan5-t1', 5, l['number'], l['title'], l['page_start'])
               for l in lessons_t5]
    books, scan_lessons = [], []
    if scan:
        for b in scan['books']:
            books.append((b['id'], b['grade'], b['kind'], b['subject'],
                          b['pages'], b['lessons'], b['status']))
        # GĐ1 chưa trích tên bài từng dòng vào JSON (chỉ đếm) — ghi thật
    os.makedirs(OUT, exist_ok=True)

    # ---- A. FULL pack ----
    full_size, full_stat = build_db(f'{OUT}/sam-full.db', outcomes, units,
                                    lessons, books, scan_lessons)

    # ---- B. MODULAR: core + per-grade ----
    mod_sizes = {}
    core_size, _ = build_db(f'{OUT}/sam-core.db', [], [], [], books, [])
    mod_sizes['core'] = core_size
    for g in sorted({o['grade'] for o in outcomes}):
        og = [o for o in outcomes if o['grade'] == g]
        ug = [u for u in units if u.get('grade') == g]
        lg = lessons if g == 5 else []
        s, _ = build_db(f'{OUT}/sam-g{g:02d}.db', og, ug, lg, [], [])
        mod_sizes[f'g{g:02d}'] = s

    # ---- JSON+gzip đối chứng ----
    blob = json.dumps({'ai': outcomes, 'units': units, 'lessons': lessons,
                       'books': books}, ensure_ascii=False).encode()
    jz = len(gzip.compress(blob, 9))

    # ---- đo latency truy vấn trên FULL ----
    db = sqlite3.connect(f'{OUT}/sam-full.db')
    t0 = time.perf_counter()
    for _ in range(200):
        db.execute("SELECT * FROM ai_outcome WHERE grade=5").fetchall()
    t_grade = (time.perf_counter() - t0) / 200 * 1000
    t0 = time.perf_counter()
    for _ in range(200):
        db.execute("SELECT ref FROM fts WHERE fts MATCH 'kiểm chứng'").fetchall()
    t_fts = (time.perf_counter() - t0) / 200 * 1000
    db.close()

    report = {
        'inputs': {'aiOutcomes': len(outcomes), 'contentUnits': len(units),
                   'lessonsToan5': len(lessons),
                   'booksGD1': len(books) if books else 'GĐ1 CHƯA XONG'},
        'full': {'bytes': full_size, 'perTable': full_stat},
        'modular': {'bytes': mod_sizes,
                    'total': sum(mod_sizes.values()),
                    'grade5Student': mod_sizes['core'] + mod_sizes.get('g05', 0)},
        'jsonGzip': jz,
        'latencyMs': {'byGrade': round(t_grade, 3), 'fts': round(t_fts, 3)},
    }
    json.dump(report, open(f'{OUT}/report.json', 'w'), ensure_ascii=False, indent=1)
    print(json.dumps(report, ensure_ascii=False, indent=1))

if __name__ == '__main__':
    main()
