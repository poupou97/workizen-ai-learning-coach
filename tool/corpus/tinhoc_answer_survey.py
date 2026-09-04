#!/usr/bin/env python3
"""WAL-192 research artifact — Tin học SGV 'Đáp án' format census (3-12).

Not wired into build_lesson_index.py; this is the source of the numbers cited
in docs/research/LEARNABLE-COVERAGE-SCALE-STRATEGY.md §"Tin học — full-chain
validation" and WAL-192. Answers Founder's ANSWER-coverage / pedagogical-role-
distribution ask with real script-measured numbers instead of hand-picked
anecdotes.

Key finding: the answer-key surface format is NOT uniform across grades even
within one subject/programme (GDPT 2018) — grades 6/9/11/12 share one clean
"N. Đáp án: X[, Y, Z]." convention right after a "Câu hỏi (hoạt động củng cố
kiến thức)" header (one regex, no per-book tuning); grades 3/4/5/7/8/10 each
use a different surface shape (open descriptive answer, inline "(Đáp án: A)"
embedded in the question line, "Đúng/Sai/Không" instead of letters, bare
"Hoạt động N" headers with unclear pedagogical role). Do NOT extend the regex
to cover the other 6 grades without new evidence — that is exactly the
per-book-heuristic accumulation Founder's decision rule says to stop at.

Deliberately does NOT attempt SGK<->SGV question-text linkage (needs
per-lesson page alignment + content-match verification, out of scope for
this bounded census — see WAL-192 backlog before any implementation).
"""
import glob
import json
import re

GRADES = range(3, 13)
HEADER_RE = re.compile(
    r'(Câu hỏi \(hoạt động củng cố kiến thức\)|Hoạt động luyện tập|'
    r'Hoạt động vận dụng|Hoạt động củng cố kiến thức|Hoạt động \d+[:\.]?)',
    re.IGNORECASE)
ANSWER_RE = re.compile(r'^\d+\.\s*Đáp án:\s*(.+)$')


def classify_header(h):
    hl = h.lower()
    if 'câu hỏi' in hl or 'củng cố' in hl:
        return 'CAU_HOI_CUNG_CO (closed self-check)'
    if 'luyện tập' in hl:
        return 'LUYEN_TAP (practice)'
    if 'vận dụng' in hl:
        return 'VAN_DUNG (open/apply)'
    if 'hoạt động' in hl:
        return 'HOAT_DONG_N (bare — role unclear without more context)'
    return 'UNKNOWN'


def survey_book(path):
    blocks = []
    current_header = None
    for f in sorted(glob.glob(f'{path}/*.json')):
        j = json.load(open(f))
        lines = [l['text'] for l in j['lines']]
        for t in lines:
            hm = HEADER_RE.search(t)
            if hm:
                current_header = hm.group(1)
            am = ANSWER_RE.match(t.strip())
            if am:
                ans = am.group(1).strip().rstrip('.')
                is_multi = bool(re.search(r'[A-D]\s*,\s*[A-D]', ans))
                blocks.append(dict(
                    file=f, header=current_header,
                    header_class=classify_header(current_header or ''),
                    answer_raw=ans, multi_select=is_multi,
                ))
    return blocks


def main():
    total_by_grade = {}
    for g in GRADES:
        paths = glob.glob(f'poc-out/graph/ocr-body/{g:02d}-sgv-tin-hoc-{g}')
        if not paths:
            continue
        total_by_grade[g] = survey_book(paths[0])

    print(f"{'Grade':>5} {'AnswerBlocks':>13} {'ClosedSelfCheck':>16} "
          f"{'Practice':>9} {'Multi-select':>13} {'BareHoatDong':>13}")
    for g, blocks in total_by_grade.items():
        closed = sum(1 for b in blocks if b['header_class'].startswith('CAU_HOI'))
        practice = sum(1 for b in blocks if b['header_class'].startswith('LUYEN_TAP'))
        multi = sum(1 for b in blocks if b['multi_select'])
        bare = sum(1 for b in blocks if b['header_class'].startswith('HOAT_DONG_N'))
        print(f"{g:>5} {len(blocks):>13} {closed:>16} {practice:>9} "
              f"{multi:>13} {bare:>13}")

    print()
    print("=== Sample BARE 'Hoạt động N' answer blocks (role unclear — needs "
          "manual SGV-text cross-check before trusting) ===")
    shown = 0
    for g, blocks in total_by_grade.items():
        for b in blocks:
            if b['header_class'].startswith('HOAT_DONG_N') and shown < 8:
                print(f"grade {g} {b['file']}: header={b['header']!r} "
                      f"answer={b['answer_raw'][:60]!r}")
                shown += 1


if __name__ == '__main__':
    main()
