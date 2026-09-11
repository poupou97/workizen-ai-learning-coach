#!/usr/bin/env python3
"""MỘT bộ dựng cho MỌI bài — không phải 10 kịch bản viết tay.

Đầu vào cho từng bài: (a) dòng đọc canonical (`lesson_reading`, cùng đường mà
pack đang dùng), (b) hợp đồng sư phạm suy từ SGV đã ghép CHỨNG MINH. Đầu ra:
`LessonDocument` đúng lược đồ `wal-lesson-fixture-v1` mà client đã đọc được.

⛔ DỮ LIỆU RIÊNG TỪNG BÀI thì được; LOGIC RIÊNG TỪNG BÀI thì không. Tệp này
không có một nhánh `if book == …` nào. Bài khác nhau chỉ khác ở BẰNG CHỨNG.

⚠ KHOÁ CHẤM ĐIỂM — quyết định fail-closed của vòng POC. Đo được: trong 589 bài
ghép CONFIDENT chỉ 46 bài có VIỆC của trẻ chứng minh được, và chỉ **6 việc /
3 bài** có đáp án gắn theo danh sách đánh số — soi tay thì quá nửa số ấy VẪN
là đáp án của câu khác («Trong khí quyển, khí nitrogen phổ biến thứ mấy?» nhận
đáp án «Hợp chất của nitrogen có ý nghĩa quan trọng…»). Không đủ để nói với
một đứa trẻ rằng em sai. Nên `evidencePolicy = none`, `answerKeysIncluded =
false`, và `check_answer` nằm trong `forbiddenTutorActions` của MỌI bài.
"""
import argparse
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, 'tool', 'corpus'))

from lesson_reading import lesson_reading  # noqa: E402
from subject import subject as subject_of  # noqa: E402

SCHEMA = 'wal-lesson-fixture-v1'
#: Mục tiêu do CHÍNH SGK in cho trẻ đọc — KHÔNG lấy mục tiêu của SGV, vì SGV
#: viết cho giáo viên («Trình bày các yêu cầu HS cần đạt…»). Đọc lời người lớn
#: cho trẻ nghe rồi gọi là có-nguồn là nhầm tầng.
#: «MỤC TIÊU» in trong SGK thì HỢP LỆ — SGK là sách của trẻ. «MỤC TIÊU» in
#: trong SGV thì không, vì đó là mục của phần hướng dẫn giáo viên.
#: Khối QUY TẮC do chính SGK in cho trẻ. Đây là chỗ DUY NHẤT trong bài mà
#: sách NÓI THẲNG một quy tắc — cơ sở duy nhất để dựng `TeachingMethod` với
#: `origin: sourceStated`. Không có khối này ⇒ không có method ⇒ fail closed.
RULE_HEADER = re.compile(r'(em đã học|ghi nhớ|kết luận|kiến thức cốt lõi)',
                         re.IGNORECASE)
#: Câu TRẦN THUẬT trong khối quy tắc — không lấy câu hỏi, không lấy mệnh lệnh.
RULE_SENT = re.compile(
    r'([A-ZĐÀÁÂÃÈÉÊÌÍÒÓÔÕÙÚĂĐĨŨƠƯẠ-ỹ][^.?!]{40,220}\.)')

SGK_OBJECTIVE = re.compile(
    r'(sau bài học này|học xong bài này|yêu cầu cần đạt|\bMỤC TIÊU\b)')
GEN = 'tool/pedagogy/build_sam_workspace.py@v1'


def _pack_lesson(book, lesson, cache={}):
    if not cache:
        import glob
        for p in sorted(glob.glob(os.path.join(ROOT, 'assets/pack',
                                               'lesson-index-g*.json'))):
            g = json.load(open(p, encoding='utf-8'))
            for r in g.get('lessonReadings') or []:
                cache[(r['book'], r['lesson'])] = (r, g.get('grade'))
    return cache.get((book, lesson), (None, None))


def _role(text):
    """Vai trò đọc được từ CHÍNH chữ — không suy diễn ngoài nguồn."""
    t = (text or '').strip()
    if t.endswith('?'):
        return 'question', 'question'
    if t.isupper() and len(t) < 90:
        return 'heading', 'heading'
    return 'body', 'paragraph'


def _best_block(blocks, text):
    """Khối SGK khớp nhất với một chuỗi — để bước dạy TRỎ VỀ chữ có thật."""
    import sys as _s
    _s.path.insert(0, os.path.join(ROOT, 'tool', 'pedagogy'))
    from sgk_sgv_pairing import toks
    T = toks(text)
    if not T:
        return None
    best, score = None, 0.0
    for b in blocks:
        B = toks(b.get('text') or '')
        if not B:
            continue
        # ⚠ ĐỘ PHỦ, KHÔNG PHẢI JACCARD. Khối SGK thường dài hơn câu hỏi nhiều
        # (cả đoạn dẫn + câu hỏi), nên Jaccard phạt oan đúng khối chứa nó:
        # đo lần đầu chỉ trỏ được 2/10 bài. Cái cần hỏi là «khối này có CHỨA
        # câu hỏi không», tức bao nhiêu phần của CÂU HỎI nằm trong khối.
        j = len(T & B) / len(T)
        if j > score:
            best, score = b, j
    return best if score >= 0.6 else None


def _loop(blocks, contract):
    """VÒNG DẠY KHÔNG CHẤM — chỉ `explain` + `next`, KHÔNG có `ask`.

    Founder 2026-09-11: một vòng học không chấm vẫn là SAM_READY nếu nó thật
    và chạy hết đường. Nên ở đây CỐ Ý không sinh `AskStep`: `AskStep` đòi
    `acceptable`/`hints`/`feedbackMatched`/`scaffold`/`keySource` — toàn bộ
    máy móc chấm điểm mà nguồn KHÔNG chống đỡ nổi. Không có bước hỏi thì
    không có chỗ nào để lỡ tay phán đúng/sai.

    Mọi chữ SAM nói là chữ của SGK, trỏ về block có thật.
    """
    # Khối TSL không chắc có khoá `text` (khối bị giữ lại thì không có chữ).
    obj = next((b for b in blocks if SGK_OBJECTIVE.search(b.get('text') or '')), None)
    task = None
    for t in contract['tasks']:
        task = _best_block(blocks, t['prompt'])
        if task:
            break
    # ⚠ VIỆC là bắt buộc; MỤC TIÊU thì không. Vòng dạy cần: bài có danh tính
    # → việc trẻ nhìn thấy → hành vi được phép → hành động kế tiếp. Nhiều bài
    # SGK không in mục tiêu cho trẻ (Lịch sử 10 Bài 9) — thiếu nó không làm
    # vòng học mất thật.
    #
    # ⭐ SỞ HỮU VIỆC XÉT Ở MỨC KHỐI, KHÔNG PHẢI MỨC BÀI. Đo được: «Phương án
    # nào chỉ gồm các thiết bị ra?» qua được phép so với TOÀN BÀI Tin học 7
    # Bài 3 nhờ từ chung, nhưng không khối nào của bài ấy chứa nó (phủ 0,33).
    # Đó là sở hữu SAI, và giao cho trẻ một việc không có trong bài của em.
    if not task:
        return None, dict(samReady=False, runtimeGuidedReady=False,
                          answerCheckReady=False, misconceptionReady=False,
                          reason='VIỆC KHÔNG TRỎ ĐƯỢC VỀ MỘT KHỐI CỦA BÀI SGK')
    steps = []
    if obj:
        steps.append({'type': 'explain', 'id': 'e1', 'text': obj['text'],
                      'sourceBlockId': obj['id'], 'mascot': 'sam-explain'})
    steps += [
        {'type': 'explain', 'id': 'e2', 'text': task['text'],
         'sourceBlockId': task['id'], 'mascot': 'sam-explain'},
        {'type': 'next', 'id': 'n1', 'label': 'Đọc lại phần này trong sách',
         'target': 'read', 'anchorBlockId': task['id']},
    ]
    return (dict(samMode='runtimeGuided', trust='trustedStructuredLesson',
                 evidencePolicy='none', steps=steps),
            dict(samReady=True,
                 # ⭐ SAM_READY ≠ RUNTIME_GUIDED_READY. `resolveBinding` đòi
                 # Concept + SkillCase + TeachingMethod có `origin:
                 # sourceStated` và trích được trang. Hợp đồng sư phạm hiện
                 # tại KHÔNG cấp ba thứ đó — sinh chúng bằng máy là bịa CHÂN
                 # LÍ CHƯƠNG TRÌNH. Nên không tạo binding giả; runtime giữ
                 # nhãn prototype và nói thẳng với trẻ là chưa ràng buộc được.
                 runtimeGuidedReady=False,
                 answerCheckReady=False,
                 misconceptionReady=False,
                 reason='RUNTIME_GUIDED: KHÔNG CÓ Concept/SkillCase/Method '
                        'SOURCE_STATED ⇒ không tạo SemanticBinding · '
                        'ANSWER_CHECK: TASK_ANSWER_OWNERSHIP_UNPROVEN · '
                        'MISCONCEPTION: KHÔNG CÓ NGUỒN GỌI TÊN LỖI'))


def curriculum(blocks, book, lesson, title):
    """Ngữ nghĩa chương trình SUY TỪ NGUỒN — hoặc `None`, không bịa.

    ⛔ KHÔNG DỰNG MÔ HÌNH CHƯƠNG TRÌNH XUYÊN BÀI. Mọi trường ở đây là CỤC BỘ
    TRONG BÀI, đúng hình dạng mà nguyên mẫu KHTN 6 Bài 17 đã dùng:

      · `condition` của ca   = CÂU QUY TẮC NGUYÊN VĂN sách in
      · `requiresConcepts`   = {chính khái niệm của bài} ⇒ cổng tiên quyết
                               đúng một cách TỰ THAM CHIẾU, không cần biết
                               bài trước đã dạy gì
      · `requiresTerminology`= {} — RỖNG CỐ Ý. Sách không in ra «phương pháp
                               này đòi những thuật ngữ nào»; khai bừa là bịa
                               tiên quyết.
      · `terminologyIntroduced` = từ CÓ TRONG chính câu quy tắc, không thêm

    Không có khối quy tắc in ⇒ trả `None`. `runtimeGuidedReady` = false.
    """
    for i, b in enumerate(blocks):
        t = b.get('text') or ''
        if not RULE_HEADER.search(t):
            continue
        m = RULE_SENT.search(t)
        if not m:
            continue
        rule = m.group(1).strip()
        ref = b['sourceRef']
        terms = sorted({w for w in re.findall(r'[a-zà-ỹ]{3,}', rule.lower())})[:24]
        cid = f'{book}:b{lesson}:concept'
        return dict(
            conceptId=cid, canonicalName=title,
            textbookTerms=terms,
            skillCaseId=f'{book}:b{lesson}:case',
            condition=rule,
            methodId=f'{book}:b{lesson}:method',
            methodName=rule[:120],
            ruleBlockId=b['id'],
            pagePdf=ref['pagePdf'], pagePrinted=ref.get('pagePrinted'),
            extractionMethod='source-rule-block-v1',
            origin='sourceStated')
    return None


def build(book, lesson, contract, out_dir):
    rec, grade = _pack_lesson(book, lesson)
    if rec is None:
        return None, 'KHÔNG CÓ TRONG PACK'
    doc, _ = lesson_reading(book, rec['pagePdfStart'], rec['pagePdfEnd'],
                            printed_start=rec.get('pageStart'),
                            title=rec.get('title'))
    if not doc:
        return None, 'KHÔNG DỰNG ĐƯỢC DÒNG ĐỌC'
    blocks = []
    for pg in doc['pages']:
        for q in sorted(pg.get('paragraphs') or [], key=lambda x: x['seq']):
            b = q.get('box')
            if not b or not (q.get('text') or '').strip():
                continue
            role, btype = _role(q['text'])
            bid = f"{book}:p{pg['pagePdf']:03d}:sam:{len(blocks):03d}"
            blocks.append({
                'id': bid, 'type': btype, 'trust': 'trustedStructuredLesson',
                'sourceRole': role, 'text': q['text'],
                'sourceRef': {
                    'book': book, 'pagePdf': pg['pagePdf'],
                    'pagePrinted': pg.get('pagePrinted'),
                    'bbox': [round(b[0], 4), round(b[1], 4),
                             round(b[2] - b[0], 4), round(b[3] - b[1], 4)],
                    'blockId': bid, 'extraction': 'lesson-reading-canonical',
                    'pipeline': 'pack-canonical'},
            })
    if not blocks:
        return None, 'KHÔNG CÓ KHỐI CHỮ'
    script, cap = _loop(blocks, contract)
    cur = curriculum(blocks, book, lesson, rec.get('title') or '')
    cap['runtimeGuidedReady'] = bool(script and cur)
    if cur:
        cap['reason'] = cap['reason'].replace(
            'RUNTIME_GUIDED: KHÔNG CÓ Concept/SkillCase/Method SOURCE_STATED '
            '⇒ không tạo SemanticBinding · ',
            'RUNTIME_GUIDED: có quy tắc in ⇒ binding suy từ nguồn · ')
    d = {
        'schema': SCHEMA, 'book': book,
        'bookTitle': (rec.get('bookTitle') or book), 'subject': subject_of(book),
        'grade': grade, 'lesson': lesson, 'title': rec.get('title') or '',
        'evidencePolicy': 'none', 'licence': 'internalResearchOnly',
        'provenance': {
            'trust': 'trustedStructuredLesson', 'book': book,
            'pagePdfStart': rec['pagePdfStart'], 'pagePdfEnd': rec['pagePdfEnd'],
            'generator': GEN, 'sourcePipeline': 'pack-canonical',
            'pipelineVersion': 'pack-canonical/pedagogy-contract-v1',
            'docType': 'SGK', 'sourceability': 'PARTIAL',
            # ⭐ KHOÁ CỨNG: mọi tài liệu của vòng này KHÔNG mang khoá chấm.
            'answerKeysIncluded': False,
            'auditStatus': 'notAudited', 'auditRef': None,
            'distribution': 'internal-research-only',
            # ⭐ CAPABILITY NẰM TRONG DỮ LIỆU, không chỉ trong tài liệu.
            # Client phải đọc được rằng SAM ở bài này KHÔNG được phán đúng/sai.
            'capability': cap,
            'pedagogySource': {
                'sgvBook': contract['sgvBook'], 'sgvPages': contract['sgvPages'],
                'pairing': contract['provenance']['pairing'],
                'tasksOwned': len(contract['tasks']),
                'answerWithheld': True,
                'withholdReason': 'TASK_ANSWER_OWNERSHIP_UNPROVEN'},
        },
        'blocks': blocks,
    }
    if cur:
        d['curriculum'] = cur
    if script:
        d['tutorScript'] = script
    os.makedirs(out_dir, exist_ok=True)
    p = os.path.join(out_dir, f'lesson-{book}-b{lesson}.json')
    with open(p, 'w', encoding='utf-8') as f:
        json.dump(d, f, ensure_ascii=False, indent=1)
    return p, None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--picks', default='poc-out/pedagogy/poc10.json')
    ap.add_argument('--contracts', default='poc-out/pedagogy/contracts')
    ap.add_argument('--out', default='assets/fixtures/real')
    a = ap.parse_args()
    picks = json.load(open(os.path.join(ROOT, a.picks), encoding='utf-8'))
    ok = 0
    for book, lesson in picks:
        cp = os.path.join(ROOT, a.contracts, f'{book}-b{lesson}.json')
        if not os.path.exists(cp):
            print(f'  ⛔ {book} B{lesson}: KHÔNG CÓ HỢP ĐỒNG')
            continue
        contract = json.load(open(cp, encoding='utf-8'))
        dest = os.path.join(ROOT, a.out, f'lesson-{book}-b{lesson}.json')
        # ⚠ KHÔNG GHI ĐÈ TÀI LIỆU ĐÃ CÓ. Lượt đầu của tôi đè mất hai fixture
        # dựng từ TSL (KHTN 6 Bài 9 và 10) — chúng mang `semantic` cho tab
        # Trực quan mà bộ dựng này không sinh ra. Đè = mất năng lực đang chạy.
        if os.path.exists(dest):
            # HỢP NHẤT, KHÔNG GHI ĐÈ: tài liệu dựng từ TSL mang `semantic` cho
            # tab Trực quan mà bộ dựng này không sinh ra. Chỉ THÊM vòng dạy và
            # cờ năng lực nếu chưa có; mọi thứ khác giữ nguyên từng byte.
            d = json.load(open(dest, encoding='utf-8'))
            if d.get('tutorScript') is None:
                script, cap = _loop(d['blocks'], contract)
                d['provenance']['capability'] = cap
                if script:
                    d['tutorScript'] = script
                    d['provenance'].setdefault('pedagogySource', {}).update(
                        sgvBook=contract['sgvBook'], sgvPages=contract['sgvPages'],
                        pairing=contract['provenance']['pairing'],
                        tasksOwned=len(contract['tasks']),
                        answerWithheld=True,
                        withholdReason='TASK_ANSWER_OWNERSHIP_UNPROVEN')
                with open(dest, 'w', encoding='utf-8') as f:
                    json.dump(d, f, ensure_ascii=False, indent=1)
                print(f"  + {book[:36]:36s} B{lesson:<3d} THÊM vòng dạy vào tài liệu TSL")
            else:
                print(f'  = {book[:36]:36s} B{lesson:<3d} GIỮ nguyên')
            ok += 1
            continue
        p, err = build(book, lesson, contract, os.path.join(ROOT, a.out))
        print(f"  {'✓' if p else '⛔'} {book[:38]:38s} B{lesson:<3d} "
              f"{os.path.basename(p) if p else err}")
        ok += bool(p)
    print(f'\n{ok}/{len(picks)} tài liệu dựng được bằng MỘT bộ dựng')


if __name__ == '__main__':
    main()
