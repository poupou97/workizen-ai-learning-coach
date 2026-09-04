#!/usr/bin/env python3
"""Fable 5.1 independent challenge — corpus-derived K-12 activity taxonomy (v2, precision-first).

v1 matched keywords anywhere in a unit and over-labelled (e.g. "kết quả" or
"hình 3" anywhere triggered a pattern → COMPUTE_SOLVE in 23 subjects). v2
classifies by the LEADING DIRECTIVE of each unit: after stripping the
number prefix ("1.", "a)"), stage label ("Luyện tập", "Vận dụng", "Hoạt
động 2"), and politeness ("Em hãy", "Hãy", "Các em"), the first ~90
characters must START with (or contain within the directive clause) an
interaction verb. Answer-shape patterns (MCQ options, true/false, blanks)
are detected structurally. A unit may carry several labels; lesson-level
counts are UNIQUE per pattern plus a union.

Excludes known noise: back-cover catalog lines parsed as exercises, bare
stage labels, ISBN/price lines.

Output: poc-out/k12-census-exports/fable-taxonomy.json + fable-pattern-coverage.csv
"""
import csv
import glob
import json
import re
from collections import Counter, defaultdict

CATALOG = re.compile(r'^\s*\d{1,2}\.\s*(Toán|Ngữ văn|Tiếng Anh|Tiếng Việt|Chuyên đề|Chuyên để|Giáo dục|Mĩ thuật|Mì thuật|Mi thuật|Âm nhạc|Công nghệ|Tin học|Lịch sử|Địa lí|Khoa học|Hoạt động trải nghiệm|Đạo đức|Sinh học|Vật lí|Hoá học|Hóa học|Tự nhiên|Tiếng Trung|Tiếng Nhật|Tiếng Pháp|Tiếng Hàn|Tiếng Nga|Tiếng Đức)\b')
NOISE = re.compile(r'ISBN|Giá:|Website:|nxbgd|Số ĐKXB|Mã số:', re.IGNORECASE)
STAGE_ONLY = re.compile(r'^\s*(LUYỆN TẬP( CHUNG)?|Luyện tập( và Vận dụng| - Vận dụng)?|LUYỆN TẬP VÀ VẬN DỤNG|Vận dụng|VẬN DỤNG|Khởi động|KHỞI ĐỘNG|Khám phá|KHÁM PHÁ|Thực hành|THỰC HÀNH)\s*$')
PREFIX = re.compile(
    r'^\s*(?:(?:\d{1,2}|[a-eA-E])[\.\)]\s*)*'                                   # 1.  a)
    r'(?:(?:KHỞI ĐỘNG|KHÁM PHÁ|LUYỆN TẬP(?: CHUNG| VÀ VẬN DỤNG)?|VẬN DỤNG|THỰC HÀNH|HOẠT ĐỘNG(?: \d+)?|Khởi động|Khám phá|Luyện tập(?: và Vận dụng| - Vận dụng)?|Vận dụng|Thực hành|Hoạt động(?: \d+)?|Nhiệm vụ \d+)[\s:\-–•]*)*'
    r'(?:(?:Em|Các em|Chúng ta)\s+)?(?:hãy\s+|cùng\s+)?', re.IGNORECASE)

# (pattern, regex applied to the DIRECTIVE HEAD = first 90 chars after prefix strip)
HEAD_PATTERNS = [
    ('EXPERIMENT',       r'^(thí nghiệm|tiến hành thí nghiệm|làm thí nghiệm|chuẩn bị:)'),
    ('CODE',             r'^(viết chương trình|lập trình|viết (đoạn )?mã|tạo (một )?chương trình)'),
    ('COMPUTE_SOLVE',    r'^(tính(?!\s+(chất|thẩm|toàn|năng|cách|đa dạng|kỉ luật|thống nhất|khả thi|sáng tạo|bền vững|độc lập))\b|giải(?!\s+thích)\b|đặt tính|rút gọn|quy đồng|tìm x|tìm số|viết số|đọc số|làm tròn|so sánh (các )?số|thực hiện phép|tính nhẩm|đo\b)'),
    ('PROVE',            r'^(chứng minh|chứng tỏ)'),
    ('DICTATION',        r'^(nghe\s*[-–]\s*viết|chính tả)'),
    ('READ_TEXT',        r'^(đọc(?! nhạc)(?! số)|đọc (thầm|thành tiếng|bài|đoạn|văn bản))'),
    ('WRITE_TEXT',       r'^(viết (đoạn|bài|một|đơn|thư|lại|tiếp|về|câu|từ|báo cáo|nhật)|kể lại bằng lời|làm (bài )?văn|tập viết|luyện viết)'),
    ('SOURCE_REASONING', r'^(khai thác (tư liệu|đoạn|hình)|dựa vào (tư liệu|đoạn trích|thông tin|nội dung)|đọc (tư liệu|đoạn tư liệu))'),
    ('MAP_SPATIAL',      r'^(dựa vào (bản đồ|lược đồ|atlat)|quan sát (bản đồ|lược đồ)|xác định (trên|vị trí)|chỉ trên (bản đồ|lược đồ))'),
    ('DATA_CHART',       r'^(dựa vào (bảng|biểu đồ|số liệu)|quan sát (bảng số liệu|biểu đồ)|vẽ biểu đồ|nhận xét (bảng|biểu đồ)|phân tích (bảng|biểu đồ|số liệu))'),
    ('DIAGRAM_COMPLETE', r'^(hoàn thành (sơ đồ|bảng|phiếu)|lập (bảng|sơ đồ|phiếu|danh sách)|vẽ sơ đồ|điền vào (bảng|sơ đồ)|hoàn thiện (sơ đồ|bảng))'),
    ('DRAW_CREATE',      r'^(vẽ|tô màu|tạo hình|thiết kế|làm (một )?sản phẩm|sáng tạo|trang trí|nặn|cắt|xé dán|gấp|tạo (ra )?(một )?)'),
    ('OBSERVE',          r'^(quan sát|nhìn (vào )?(hình|tranh)|xem (hình|tranh|video))'),
    ('COMPARE',          r'^(so sánh|đối chiếu|phân biệt)'),
    ('CLASSIFY_SORT',    r'^(phân loại|sắp xếp|xếp (các|những|vào|theo|lại)|nhóm (các|những|thành)|chia (các|những) .{0,30}(thành|theo) nhóm)'),
    ('MATCH',            r'^(nối|ghép)'),
    ('FILL_BLANK',       r'^(điền|hoàn thành câu|chọn từ (ngữ )?(thích hợp|phù hợp)|tìm từ)'),
    ('SELECT_MCQ',       r'^(chọn|khoanh|đánh dấu|câu nào|phương án nào|ý nào|đáp án nào)'),
    ('TRUE_FALSE',       r'^(đúng hay sai|đúng, sai|em (có )?đồng tình|nhận định nào đúng|đồng tình hay)'),
    ('EXPLAIN_SHORT',    r'^(nêu|cho biết|giải thích|vì sao|tại sao|trình bày (những|các|đặc điểm|vai trò|nguyên nhân|ý nghĩa)|nhận xét|phân tích|đánh giá|kể tên|liệt kê|mô tả|xác định|dự đoán|em có (biết|nghĩ)|theo em|thế nào là|là gì)'),
    ('ORAL_SHARE',       r'^(kể(?! tên)|nói|chia sẻ|trao đổi|thảo luận|giới thiệu|thuyết trình|trình bày (trước|với|cho|ý kiến)|hỏi|đóng góp ý kiến|phát biểu|nói và nghe)'),
    ('ROLEPLAY_GAME',    r'^(đóng vai|sắm vai|chơi trò chơi|trò chơi|xử lí tình huống|xử lý tình huống|em sẽ (làm gì|xử lí|nói gì)|nếu (là|em))'),
    ('RESEARCH_PROJECT', r'^(sưu tầm|tìm hiểu|tìm kiếm|tìm (thêm )?thông tin|điều tra|khảo sát|phỏng vấn|thu thập|dự án|thực hiện dự án)'),
    ('PLAN_REFLECT',     r'^(lập kế hoạch|xây dựng kế hoạch|tự đánh giá|rèn luyện|cam kết|ghi (lại|vào|nhật kí)|suy ngẫm|em đã học được)'),
    ('HANDS_ON_TOOL',    r'^(thực hành|thao tác|sử dụng (phần mềm|máy tính|công cụ|dụng cụ|thiết bị)|mở (tệp|phần mềm)|khởi động (phần mềm|máy)|nhiệm vụ \d|tạo (tệp|thư mục|bảng tính|bài trình chiếu))'),
    ('AUDIO_PERFORM',    r'^(hát|nghe|múa|vận động theo|gõ đệm|đọc nhạc|hoà tấu|độc tấu|biểu diễn|luyện (tập )?(hát|gõ|đọc nhạc|kĩ thuật gảy|kĩ thuật bấm)|thể hiện (bài hát|tiết tấu))'),
    ('PHYSICAL',         r'^(khởi động (chung|chuyên môn|xoay)|xoay các khớp|tập (động tác|bài tập)|thực hiện (động tác|kĩ thuật|bài tập)|di chuyển|chạy|nhảy|ném|bật|dẫn bóng|chuyền bóng|đứng|ngồi|tư thế|luyện tập (kĩ thuật|động tác|cá nhân|nhóm|cặp)|trò chơi vận động)'),
]
COMPILED = [(n, re.compile(rx, re.IGNORECASE)) for n, rx in HEAD_PATTERNS]
# Structural answer-shape detectors over the whole unit (not just head)
MCQ_OPTIONS = re.compile(r'(^|\s)A[\.\)]\s+\S.{2,}?\sB[\.\)]\s+\S.{2,}?\sC[\.\)]\s+\S', re.DOTALL)
BLANK = re.compile(r'(…|\.\.\.\.|_{3,})')

SURFACE = {
    'EXPERIMENT': 'ExperimentScreen', 'COMPUTE_SOLVE': 'TutorScreen (Toán fractions only today)',
    'SELECT_MCQ': 'QuizSelect', 'TRUE_FALSE': 'QuizSelect (2-option)', 'READ_TEXT': 'ReaderScreen',
    'WRITE_TEXT': 'ComposeLiteScreen', 'SOURCE_REASONING': 'SourceReaderScreen', 'MAP_SPATIAL': 'MapReaderScreen',
}
MODALITY = {
    'AUDIO_PERFORM': 'Audio/Voice', 'PHYSICAL': 'Movement', 'DRAW_CREATE': 'Drawing/Camera',
    'ORAL_SHARE': 'Voice (text fallback possible)', 'ROLEPLAY_GAME': 'Group/Voice', 'HANDS_ON_TOOL': 'External software/equipment',
    'RESEARCH_PROJECT': 'Out-of-app research + text report', 'DICTATION': 'Audio',
}
# Tier for "what would it take" — used later for the 5-bucket verdict
TIER = {
    'EXPERIMENT': 'SURFACE_EXISTS', 'READ_TEXT': 'SURFACE_EXISTS', 'WRITE_TEXT': 'SURFACE_EXISTS',
    'SOURCE_REASONING': 'SURFACE_EXISTS', 'MAP_SPATIAL': 'SURFACE_EXISTS', 'SELECT_MCQ': 'SURFACE_EXISTS', 'TRUE_FALSE': 'SURFACE_EXISTS',
    'COMPUTE_SOLVE': 'SURFACE_EXISTS_NARROW', 'PROVE': 'NEW_TEXT_SURFACE', 'MATCH': 'NEW_TEXT_SURFACE', 'FILL_BLANK': 'NEW_TEXT_SURFACE',
    'EXPLAIN_SHORT': 'NEW_TEXT_SURFACE', 'COMPARE': 'NEW_TEXT_SURFACE', 'CLASSIFY_SORT': 'NEW_TEXT_SURFACE',
    'OBSERVE': 'NEW_TEXT_SURFACE', 'DIAGRAM_COMPLETE': 'NEW_TEXT_SURFACE', 'DATA_CHART': 'NEW_TEXT_SURFACE',
    'PLAN_REFLECT': 'NEW_TEXT_SURFACE', 'CODE': 'NEW_TEXT_SURFACE',
    'DRAW_CREATE': 'MULTIMODAL', 'ORAL_SHARE': 'MULTIMODAL', 'ROLEPLAY_GAME': 'MULTIMODAL', 'AUDIO_PERFORM': 'MULTIMODAL',
    'DICTATION': 'MULTIMODAL', 'PHYSICAL': 'MULTIMODAL', 'HANDS_ON_TOOL': 'MULTIMODAL', 'RESEARCH_PROJECT': 'MULTIMODAL',
}


def classify(text):
    labels = set()
    t = text.strip()
    head = PREFIX.sub('', t, count=1)[:90].lower().strip()
    for name, rx in COMPILED:
        if rx.search(head):
            labels.add(name)
    if MCQ_OPTIONS.search(t):
        labels.add('SELECT_MCQ')
    if BLANK.search(t) and len(t) < 400:
        labels.add('FILL_BLANK')
    return labels


def main():
    struct = json.load(open('poc-out/graph/curriculum-structure.json'))
    meta = {d['sourceDocumentId']: d for d in struct['documents']}
    per_pattern = defaultdict(set)
    lesson_labels = defaultdict(set)
    lessons_seen = set()
    units_total = units_labeled = 0
    for fp in glob.glob('poc-out/units-k12/*-sgk-*.json'):
        j = json.load(open(fp))
        sid = j['sourceDocumentId']
        for u in j['units']:
            if u.get('lesson') is None or u['role'] == 'SECTION_TEXT':
                continue
            t = u['text'].strip()
            if (CATALOG.match(t) and len(t) < 120) or STAGE_ONLY.match(t) or NOISE.search(t):
                continue
            key = (sid, u['lesson'])
            lessons_seen.add(key)
            units_total += 1
            labels = classify(t)
            if u['role'] == 'EXPERIMENT': labels.add('EXPERIMENT')
            if u['role'] == 'READING': labels.add('READ_TEXT')
            if u['role'] == 'SOURCE_TEXT': labels.add('SOURCE_REASONING')
            if labels:
                units_labeled += 1
            for n in labels:
                per_pattern[n].add(key)
                lesson_labels[key].add(n)

    labeled_lessons = {k for k in lessons_seen if lesson_labels.get(k)}
    rows = []
    for name, _ in HEAD_PATTERNS:
        ls = per_pattern[name]
        grades = sorted({meta.get(s, {}).get('grade') for s, _ in ls} - {None})
        subjects = Counter(meta.get(s, {}).get('subject', '?') for s, _ in ls)
        rows.append(dict(pattern=name, unique_lessons=len(ls), n_grades=len(grades), grade_list=grades,
                         n_subjects=len(subjects), top_subjects=subjects.most_common(5),
                         existing_surface=SURFACE.get(name, '—'), modality=MODALITY.get(name, 'Text/tap'), tier=TIER[name]))
    rows.sort(key=lambda r: -r['unique_lessons'])
    prio = {n: i for i, (n, _) in enumerate(HEAD_PATTERNS)}
    primary = {k: min(v, key=lambda n: prio[n]) for k, v in lesson_labels.items() if v}

    out = dict(units_total=units_total, units_labeled=units_labeled,
               lessons_with_clean_units=len(lessons_seen), lessons_labeled=len(labeled_lessons),
               lessons_unlabeled=len(lessons_seen) - len(labeled_lessons),
               patterns=rows, primary={f'{s}|{l}': p for (s, l), p in primary.items()},
               labels={f'{s}|{l}': sorted(v) for (s, l), v in lesson_labels.items()})
    json.dump(out, open('poc-out/k12-census-exports/fable-taxonomy.json', 'w'), ensure_ascii=False)
    with open('poc-out/k12-census-exports/fable-pattern-coverage.csv', 'w', newline='') as f:
        w = csv.writer(f)
        w.writerow(['pattern', 'unique_lessons', 'pct_of_3679', 'n_grades', 'grades', 'n_subjects', 'top_subjects', 'existing_surface', 'modality', 'tier'])
        for r in rows:
            w.writerow([r['pattern'], r['unique_lessons'], round(100 * r['unique_lessons'] / 3679, 1), r['n_grades'],
                        ';'.join(map(str, r['grade_list'])), r['n_subjects'],
                        '; '.join(f'{s}:{c}' for s, c in r['top_subjects']), r['existing_surface'], r['modality'], r['tier']])

    print(f'clean units: {units_total}, labeled units: {units_labeled} ({100*units_labeled/units_total:.0f}%)')
    print(f'lessons with clean units: {len(lessons_seen)}; labeled: {len(labeled_lessons)}; unlabeled: {len(lessons_seen)-len(labeled_lessons)}')
    print(f"{'pattern':<18}{'lessons':>8}{'%3679':>7}{'gr':>4}{'subj':>5}  tier / surface")
    for r in rows:
        print(f"{r['pattern']:<18}{r['unique_lessons']:>8}{100*r['unique_lessons']/3679:>7.1f}{r['n_grades']:>4}{r['n_subjects']:>5}  {r['tier']} / {r['existing_surface']}")
    print('\nPRIMARY label distribution:')
    for p, c in Counter(primary.values()).most_common():
        print(f'  {p:<18}{c:>6}')
    print('\nTIER by primary label (unique lessons):')
    for t, c in Counter(TIER[p] for p in primary.values()).most_common():
        print(f'  {t:<24}{c:>6}')


if __name__ == '__main__':
    main()
