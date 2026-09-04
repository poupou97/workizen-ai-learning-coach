#!/usr/bin/env python3
"""MASTER K-12 ORDER — Readiness Matrix: Grade x Subject, nhiều tầng tách bạch.

Không trộn các tầng làm MỘT con số. Founder Review 2026-09-04 yêu cầu tách:
  SOURCE COVERAGE != STRUCTURAL QUALITY != COMPILED PACK != BROWSABLE
  != LEARNABLE (semantic/pedagogy) != EVIDENCE-CAPABLE (activity wired) != ADAPTIVE

Nguồn dữ liệu (không trích gì mới, thuần đọc lại output đã có):
  - poc-out/graph/curriculum-structure.json  (Source đã OCR + parse)
  - tool/corpus/toc_health.py --json          (Structural quality, TƯƠI — không
    dùng structureStatus lưu trong curriculum-structure.json vì field đó CŨ,
    không khớp flags tính lại — đã xác nhận lệch cho nhiều sách TV/Toán)
  - poc-out/coverage-report.json              (Semantic/Pedagogy tier — content
    units/objectives/methods; hiện chỉ có cho 6 sách)
  - assets/pack/lesson-index-g<N>.json        (Compiled pack + activity wiring —
    ai file nào KHÔNG có trên máy này thì lớp đó coi như chưa compile)

Chạy:  python3 tool/corpus/readiness_matrix.py            # bảng tổng hợp theo môn
       python3 tool/corpus/readiness_matrix.py --json out.json   # xuất đầy đủ
"""
import glob
import json
import subprocess
import sys
from collections import defaultdict

GRADES = range(1, 13)


def load_toc_health():
    out = subprocess.run(
        [sys.executable, 'tool/corpus/toc_health.py', '--json'],
        capture_output=True, text=True, check=True).stdout
    return json.loads(out)


def load_semantic_books():
    try:
        rep = json.load(open('poc-out/coverage-report.json'))
    except FileNotFoundError:
        return set()
    return set(rep.get('semantic', {}).get('unitsPerBook', {}).keys())


def load_pack(grade):
    path = f'assets/pack/lesson-index-g{grade}.json'
    try:
        return json.load(open(path))
    except FileNotFoundError:
        return None


ACT_KEYS = ['toanExercises', 'tvReadings', 'tvWritings', 'suSources',
            'khoaExperiments', 'diaMaps']


def activities_by_book(pack):
    """book -> tổng số hoạt động đã nối, gộp mọi loại."""
    counts = defaultdict(int)
    if pack is None:
        return counts
    tv = pack.get('toanExercises', {})
    if isinstance(tv, dict):
        for lst in tv.values():
            for e in lst:
                counts[e.get('book', '')] += 1
    for key in ('tvReadings', 'tvWritings', 'suSources', 'khoaExperiments'):
        for e in pack.get(key, []):
            counts[e.get('book', '')] += 1
    for e in pack.get('diaMaps', []):
        counts[e.get('book', pack.get('subject', ''))] += 1
    return counts


def main():
    struct = json.load(open('poc-out/graph/curriculum-structure.json'))['documents']
    struct_by_id = {d['sourceDocumentId']: d for d in struct if d['docType'] == 'SGK'}
    health = {h['sourceDocumentId']: h for h in load_toc_health()}
    semantic_books = load_semantic_books()

    rows = []
    for grade in GRADES:
        pack = load_pack(grade)
        pack_books_by_subject = defaultdict(set)
        pack_lessons_by_subject = defaultdict(int)
        if pack:
            for subj, blist in pack.get('subjects', {}).items():
                for b in blist:
                    pack_books_by_subject[subj].add(b['sourceDocumentId'])
                    pack_lessons_by_subject[subj] += len(b['lessons'])
        pack_book_ids = {b['sourceDocumentId'] for blist in pack.get(
            'subjects', {}).values() for b in blist} if pack else set()
        acts = activities_by_book(pack) if pack else {}
        shelf_books = {b['sourceDocumentId']: b for b in (
            pack.get('books', []) if pack else [])}

        subj_docs = defaultdict(list)
        for sid, d in struct_by_id.items():
            if d.get('grade') == grade:
                subj_docs[d.get('subject')].append(sid)

        for subj, sids in subj_docs.items():
            n_books = len(sids)
            n_ok = sum(1 for s in sids if health.get(s, {}).get('flags') == ['OK'])
            n_notoc = sum(1 for s in sids if 'NO_TOC' in health.get(s, {}).get('flags', []))
            n_partial = n_books - n_ok - n_notoc
            n_source_lessons = sum(len(struct_by_id[s].get('lessons', [])) for s in sids)
            n_compiled = sum(1 for s in sids if s in pack_book_ids)
            n_lessons_compiled = pack_lessons_by_subject.get(subj, 0)
            n_on_shelf = sum(1 for s in sids if s in shelf_books)
            n_semantic = sum(1 for s in sids if s in semantic_books)
            n_activities = sum(acts.get(s, 0) for s in sids)
            rows.append(dict(
                grade=grade, subject=subj, books=n_books,
                tocOk=n_ok, tocPartial=n_partial, tocNoToc=n_notoc,
                sourceLessons=n_source_lessons,
                booksCompiled=n_compiled, lessonsCompiled=n_lessons_compiled,
                booksOnShelf=n_on_shelf,
                booksWithSemanticExtraction=n_semantic,
                activitiesWired=n_activities,
            ))
    return rows


def render_table(rows):
    hdr = (f"{'Lớp':>4} {'Môn':<14} {'sách':>4} {'TOC-OK':>7} {'PARTIAL':>8} "
           f"{'NO_TOC':>7} {'bàiNguồn':>9} {'compile':>8} {'bàiPack':>8} "
           f"{'lênGiá':>7} {'semantic':>9} {'hđộng':>6}")
    print(hdr)
    print('-' * len(hdr))
    for r in sorted(rows, key=lambda r: (r['grade'], -r['books'])):
        print(f"{r['grade']:>4} {r['subject']:<14.14} {r['books']:>4} "
              f"{r['tocOk']:>7} {r['tocPartial']:>8} {r['tocNoToc']:>7} "
              f"{r['sourceLessons']:>9} {r['booksCompiled']:>8} "
              f"{r['lessonsCompiled']:>8} {r['booksOnShelf']:>7} "
              f"{r['booksWithSemanticExtraction']:>9} {r['activitiesWired']:>6}")


if __name__ == '__main__':
    rows = main()
    if '--json' in sys.argv:
        idx = sys.argv.index('--json')
        path = sys.argv[idx + 1] if len(sys.argv) > idx + 1 else 'poc-out/readiness-matrix.json'
        json.dump(rows, open(path, 'w'), ensure_ascii=False, indent=1)
        print(f'{len(rows)} dòng -> {path}')
    else:
        render_table(rows)
