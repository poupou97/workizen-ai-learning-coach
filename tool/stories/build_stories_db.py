#!/usr/bin/env python3
"""WAL-151 KS-D — stories.db: SQLite + FTS5 local-first theo pack
architecture (WAL-83). CHỈ nạp VERIFIED (cổng §28); title derive tất định
từ chính item — KHÔNG LLM, KHÔNG thêm claim."""
import json, os, re, sqlite3, time

VER = 'stories-db-v1'

def title_of(i):
    t = i['type']
    if t == 'PERSON':
        y = f" ({i['birthYear']}–{i['deathYear']})" if i.get('birthYear') else ''
        if not y:
            # Không có năm sinh-mất để đứng riêng làm ngữ cảnh (VD tên phiên
            # âm nước ngoài "Hen Krit-chừn Gioa-chim G-ram" đọc vô nghĩa nếu
            # đứng một mình) — SGK tự in "<tên phiên âm> (<tên gốc/biệt danh>)"
            # ngay trong câu nguồn; lấy lại NGUYÊN VĂN phần trong ngoặc đó
            # (không suy luận, không LLM) làm ngữ cảnh thay thế.
            m = re.search(re.escape(i['name']) + r'\s*\(([^)]+)\)',
                           i['source']['textEvidence'])
            if m:
                y = f" ({m.group(1)})"
        return i['name'] + y
    if t == 'QUOTE':
        return '«' + i['quote'][:80] + ('…' if len(i['quote']) > 80 else '') + '»'
    if t == 'EVENT':
        return f"Năm {i['year']}" + (f" ({i['monthDay']})" if i.get('monthDay') else '')
    if t == 'INVENTION_DISCOVERY':
        who = (i.get('person') + ' — ') if i.get('person') else ''
        return who + (i.get('what') or '')[:80]
    return (i.get('quote') or i['source']['textEvidence'])[:80]

def main():
    items = json.load(open('poc-out/stories/verified-v0.json'))
    persons = {p['personId']: p for p in
               json.load(open('poc-out/stories/persons-v0.json'))}
    os.makedirs('assets/pack', exist_ok=True)
    path = 'assets/pack/sam-stories.db'
    if os.path.exists(path):
        os.remove(path)
    db = sqlite3.connect(path)
    db.executescript('''
      CREATE TABLE meta(k TEXT PRIMARY KEY, v TEXT);
      CREATE TABLE story(
        id TEXT PRIMARY KEY, type TEXT NOT NULL, title TEXT NOT NULL,
        body TEXT NOT NULL,             -- textEvidence (SOURCE FACT nguyên gốc)
        personId TEXT, personName TEXT,
        year INT, monthDay TEXT, subject TEXT NOT NULL, grade INT NOT NULL,
        status TEXT NOT NULL,           -- luôn VERIFIED trong pack này
        sourceDocumentId TEXT NOT NULL, pagePdf INT NOT NULL,
        curatedBy TEXT, verifyVersion TEXT);
      CREATE TABLE person(
        personId TEXT PRIMARY KEY, canonicalName TEXT NOT NULL,
        birthYear INT, deathYear INT, subjects TEXT, refCount INT);
      CREATE VIRTUAL TABLE story_fts USING fts5(
        title, body, personName, subject, content=story, content_rowid=rowid);
      CREATE INDEX idx_story_monthday ON story(monthDay) WHERE monthDay IS NOT NULL;
      CREATE INDEX idx_story_type ON story(type);
    ''')
    for i in items:
        pid = i.get('personId')
        pname = i.get('name') or i.get('person')
        db.execute('INSERT INTO story VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)', (
            i['id'], i['type'], title_of(i), i['source']['textEvidence'],
            pid, pname, i.get('year') or i.get('birthYear'),
            i.get('monthDay'), i['source']['subject'], i['source']['grade'],
            i['status'], i['source']['sourceDocumentId'],
            i['source']['pagePdf'], i.get('curatedBy'),
            i.get('verifyVersion')))
    used_pids = {i.get('personId') for i in items if i.get('personId')}
    for pid in used_pids:
        p = persons.get(pid)
        if not p:
            continue
        db.execute('INSERT INTO person VALUES(?,?,?,?,?,?)', (
            pid, p['canonicalName'], p.get('birthYear'), p.get('deathYear'),
            ','.join(p['subjects']), len(p['sourceRefs'])))
    db.execute("INSERT INTO story_fts(rowid,title,body,personName,subject) "
               "SELECT rowid,title,body,personName,subject FROM story")
    db.execute("INSERT INTO meta VALUES('version', ?)", (VER,))
    db.commit()

    # ── truy vấn nghiệm thu + bench nhẹ ──
    def q(sql, *a):
        t0 = time.perf_counter()
        rows = db.execute(sql, a).fetchall()
        return rows, (time.perf_counter() - t0) * 1000
    n = db.execute('SELECT COUNT(*) FROM story').fetchone()[0]
    np_ = db.execute('SELECT COUNT(*) FROM person').fetchone()[0]
    print(f'{path}: {n} story · {np_} person · {os.path.getsize(path)//1024}KB')
    rows, ms = q("SELECT title FROM story_fts WHERE story_fts MATCH ? LIMIT 3", 'Beethoven')
    print(f'FTS «Beethoven» {ms:.2f}ms →', [r[0] for r in rows])
    rows, ms = q("SELECT title,subject FROM story WHERE monthDay=?", '09-02')
    print(f'Ngày-này-năm-xưa 02/09 {ms:.2f}ms →', rows)
    rows, ms = q("SELECT title FROM story WHERE type='QUOTE' AND length(body)<300")
    print(f'Loading-quote pool {ms:.2f}ms →', [r[0][:60] for r in rows])
    rows, ms = q("SELECT canonicalName,subjects FROM person ORDER BY refCount DESC LIMIT 5")
    print('Top person:', rows)
    db.close()

if __name__ == '__main__':
    main()
