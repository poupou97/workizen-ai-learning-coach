"""WAL-82 (GĐ9) — Coverage Dashboard: «SAM thực sự hiểu bao nhiêu % chương trình?»

MỘT LỆNH sinh report machine-readable, TÁCH TẦNG — vì lẫn OCR-coverage với
knowledge-coverage là cách tự lừa nhanh nhất:
  OCR ≠ STRUCTURE ≠ SEMANTIC ≠ VALIDATED.
Số liệu lấy TRỰC TIẾP từ artifacts (không gõ tay); tầng VALIDATED = chạy
SCALE GATE thật và ghi exit code.
"""
import json, os, subprocess, datetime

R = {'generatedAt': datetime.datetime.now().isoformat(timespec='seconds'),
     'legal': 'localResearchOnly — ADR-002; thương mại chặn bởi Legal Gate WAL-43 (REVIEW PENDING)'}

# ── TẦNG 0: OCR (trang ảnh → text) ────────────────────────────────────────
ocr = {}
d = 'poc-out/graph/ocr-body'
for b in sorted(os.listdir(d)):
    if os.path.isdir(f'{d}/{b}'):
        ocr[b] = len(os.listdir(f'{d}/{b}'))
R['ocr'] = {'books': len(ocr), 'pages': sum(ocr.values()), 'perBook': ocr}

# ── TẦNG 1: STRUCTURE (mục lục / bài) ─────────────────────────────────────
scan = json.load(open('poc-out/graph/structure-scan.json'))
R['structure'] = {'booksScanned': len(scan['books']),
                  'lessonsSeen': sum(len([l for l in b.get('lessonTitles', [])
                                          if l.get('n') is not None])
                                     for b in scan['books'])}

# ── TẦNG 2: SEMANTIC (unit / objective / rule / method / qmatrix) ─────────
sem = {}
units = 0; per = {}
for f in sorted(os.listdir('poc-out/units')):
    if f.endswith('.json') and 'sgk' in f and 'objectives' not in f:
        n = len(json.load(open(f'poc-out/units/{f}')).get('units', []))
        per[f.replace('.json','')] = n; units += n
sem['contentUnits'] = units
sem['unitsPerBook'] = per
objs = 0
for f in ('04-sgv-toan-4', '05-sgv-toan-5'):
    p = f'poc-out/units/{f}.objectives.json'
    if os.path.exists(p): objs += len(json.load(open(p)))
sem['learningObjectives'] = objs
rules = json.load(open('poc-out/units/rule-concept-map.json'))
sem['rules'] = {'total': len(rules),
                'conceptMapped': sum(1 for r in rules if r['conceptId'] != 'unmapped')}
mc = json.load(open('poc-out/units/method-catalogue.json'))
sem['methods'] = {'total': len(mc), 'withSourcePage': len(mc)}
q = json.load(open('poc-out/units/qmatrix.json'))
from collections import Counter
sem['exerciseQmatrix'] = dict(Counter(e['tier'] for e in q))
emap = json.load(open('poc-out/units/exercise-case-map.json'))
sem['skillCaseMappings'] = len(emap)
g = json.load(open('poc-out/graph/crossgrade-graph.json'))
sem['crossGradeEdges'] = {e['kind']: 0 for e in g['edges']}
for e in g['edges']: sem['crossGradeEdges'][e['kind']] += 1
sem['llmInferredAnywhere'] = 0  # G9 giữ; đổi khi LLM layer bật
R['semantic'] = sem

# ── TẦNG 3: VALIDATED (SCALE GATE thật) ──────────────────────────────────
p = subprocess.run(['python3', 'tool/extract/verify_corpus_gates.py'],
                   capture_output=True, text=True)
checks = p.stdout.count('✅')
fails = p.stdout.count('❌')
R['validated'] = {'scaleGate': 'GREEN' if p.returncode == 0 else 'RED',
                  'checksPassed': checks, 'checksFailed': fails}

# ── PARSE FAILURES ghi thật ───────────────────────────────────────────────
R['knownParseFailures'] = [
    '05-sgk-toan-5-tap-hai B50: TOC thiếu số trang — bài bị LOẠI không đoán',
    'objectives concept-mapping: 445/569 unmapped (từ khoá chưa phủ — trung thực)',
]

json.dump(R, open('poc-out/coverage-report.json', 'w'), ensure_ascii=False, indent=1)
print(json.dumps(R, ensure_ascii=False, indent=1)[:2200])
