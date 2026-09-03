"""K-12 §VI — CANONICAL STRUCTURE toàn kho từ structure-scan (531 sách).

SourceDocument → Lesson(number, title?, pageStart) — mức TOC đã đo GĐ1.
KHÔNG hardcode Lesson==Period (§XVI): đây là CurriculumLesson từ mục lục;
tiết/activity vào sau từ OCR body. Title None giữ None (UNKNOWN ≠ bịa).
Gate: doc không lesson nào = NO_TOC (báo PARTIAL, không giấu — §XXII).
"""
import json
import os
import sys
from collections import Counter

scan = json.load(open('poc-out/graph/structure-scan.json'))['books']
reg = {d['sourceDocumentId']: d for d in
       json.load(open('poc-out/registry/source-registry.json'))['documents']}

# WAL-172: đọc lại mục lục bằng bộ đọc nhận HAI HỌ (danh sách có từ khoá +
# bảng có dòng tiêu đề cột) và trang NỐI TIẾP. Bản mới chỉ được thay bản cũ khi
# KHÔNG làm mất nội dung dùng được — `choose()` giữ luật ấy, và cuốn nào thua
# thì giữ nguyên bản cũ kèm cờ REVIEW_REQUIRED để điều tra, không im lặng.
sys.path.insert(0, 'tool/corpus')
from toc_columns import parse_book, lessons_of, choose  # noqa: E402

out, status, source = [], Counter(), Counter()
for b in scan:
    doc = reg.get(b['id'], {})
    lessons = [{'number': l['n'], 'title': l.get('title'),
                'pageStart': l.get('p')}
               for l in b.get('lessonTitles', []) if l.get('n') is not None]

    grade = doc.get('grade')
    ocr_dir = f"poc-out/graph/ocr/{grade:02d}/{b['id']}" if grade else None
    if ocr_dir and os.path.isdir(ocr_dir):
        try:
            entries, _ = parse_book(ocr_dir, tuple(b.get('tocPages') or ()))
            fresh = [{'number': e['number'], 'title': e.get('title'),
                      'pageStart': e.get('pageStart'),
                      **({'unitKind': e['unitKind']} if e.get('unitKind') else {}),
                      **({'week': e['week']} if e.get('week') is not None else {})}
                     for e in lessons_of(entries)]
            lessons, pick = choose(lessons, fresh)
        except Exception as e:  # bộ đọc hỏng ⇒ GIỮ bản cũ, báo ra
            pick = f'PARSER_ERROR:{type(e).__name__}'
        source[pick.split(':')[0]] += 1

    st = 'OK' if lessons else 'NO_TOC'
    missing_page = sum(1 for l in lessons if not l['pageStart'])
    if lessons and missing_page:
        st = 'PARTIAL'
    status[st] += 1
    out.append({'sourceDocumentId': b['id'],
                'grade': doc.get('grade'), 'subject': doc.get('subject'),
                'docType': doc.get('docType'), 'volume': doc.get('volume'),
                'lessons': lessons, 'lessonCount': len(lessons),
                'lessonsMissingPage': missing_page, 'structureStatus': st})

json.dump({'schemaVersion': 'structure-v1', 'documents': out},
          open('poc-out/graph/curriculum-structure.json', 'w'),
          ensure_ascii=False, indent=1)
total_lessons = sum(d['lessonCount'] for d in out)
titled = sum(1 for d in out for l in d['lessons'] if l['title'])
print(f'structure: {len(out)} docs · {total_lessons} lessons · status {dict(status)}')
print(f'lesson có title: {titled}/{total_lessons} (title None giữ None — không bịa)')
by_grade = Counter((d['grade'], d['structureStatus']) for d in out)
no_toc = [d['sourceDocumentId'] for d in out if d['structureStatus'] == 'NO_TOC'][:8]
print('NO_TOC ví dụ:', no_toc)
print('nguồn mục lục:', dict(source))
