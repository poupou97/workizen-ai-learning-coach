"""WAL-74 batch ④ — SCALE GATE tự động trên corpus thật.

Chạy: python3 tool/extract/verify_corpus_gates.py  (exit≠0 = gate ĐỎ)

Không nằm trong `flutter test` vì corpus + sản phẩm phái sinh ở NGOÀI git
(ADR-002). Suite Dart giữ luật trên fixture; script này giữ luật trên DỮ LIỆU
THẬT. Cả hai phải xanh trước khi mở rộng semantic ingestion (Founder Delta §7).
"""
import json, sys

# ⭐⭐ WAL-223 S5/S6/S7 — VẮNG MẶT KHÔNG THOẢ MÃN ĐƯỢC NGHĨA VỤ DƯƠNG.
#
# Trước đây phán quyết cuối chỉ đọc `FAILS`, nên MỘT PHÉP KIỂM KHÔNG BAO GIỜ
# CHẠY KHÔNG PHÂN BIỆT ĐƯỢC VỚI MỘT PHÉP KIỂM ĐÃ ĐẠT. Bốn họ cổng (G5–G8) biến
# mất khi thiếu tệp, và script vẫn in «🟢 TẤT CẢ XANH» rồi exit 0.
#
# Ba sổ, không phải một:
#   FAILS    — đã kiểm, và SAI
#   VACUOUS  — đã chạy, nhưng mẫu số = 0 nên câu trả lời rỗng nghĩa
#   SKIPPED  — chưa từng chạy vì thiếu tệp
# Chỉ khi cả ba đều rỗng thì «TẤT CẢ XANH» mới là một câu đúng.
FAILS = []
VACUOUS = []
SKIPPED = []


def check(name, ok, detail=''):
    print(f"  {'✅' if ok else '❌'} {name}" + (f' — {detail}' if detail else ''))
    if not ok:
        FAILS.append(name)


def check_over(name, population, ok, detail=''):
    """A check whose truth only means anything over a NON-EMPTY population.

    `all(...)` and `len(x) == 0` are both true of an empty list — which is also
    exactly what a broken extractor produces. So the population comes first and
    the verdict second.
    """
    if population == 0:
        print(f'  ⚪ {name} — KHÔNG KIỂM ĐƯỢC: mẫu số = 0'
              + (f' ({detail})' if detail else ''))
        VACUOUS.append(name)
        return
    check(name, ok, f'{detail} · mẫu số {population}' if detail else f'mẫu số {population}')


def skip(family, reason):
    print(f'\n⚪ {family} — KHÔNG CHẠY: {reason}')
    SKIPPED.append(family)

def load(p):
    return json.load(open(p))

def main():
    units = []
    for b in ['05-sgk-toan-5-tap-mot', '05-sgk-toan-5-tap-hai',
              '04-sgk-toan-4-tap-mot', '04-sgk-toan-4-tap-hai',
              '05-sgk-tieng-viet-5-tap-mot', '05-sgk-tieng-viet-5-tap-hai']:
        d = load(f'poc-out/units/{b}.json')
        grade = 4 if b.startswith('04') else 5
        vol = 2 if 'tap-hai' in b else 1
        for u in d['units']:
            u.update(book=b, grade=grade, vol=vol)
            units.append(u)
    rules = [u for u in units if u['role'] == 'RULE']
    print(f"corpus: {len(units)} unit · {len(rules)} RULE")

    # G1 — PROVENANCE: mọi unit có assertion + truy được vị trí nguồn
    print('\nG1 provenance')
    check('mọi unit có assertion',
          all(u['provenance'].get('assertion') in ('EXPLICIT', 'DEMONSTRATED')
              for u in units))
    check('RULE = EXPLICIT, còn lại = DEMONSTRATED',
          all((u['provenance']['assertion'] == 'EXPLICIT') ==
              u['role'].startswith('RULE') for u in units))
    check('mọi unit truy được trang PDF',
          all(isinstance(u['pagePdf'], int) for u in units))

    # G2 — LEAK: trần bài chặn tri thức tương lai, XUYÊN SÁCH và XUYÊN LỚP
    print('\nG2 chống rò tri-thức-tương-lai')
    def visible(u, g, vol, lesson):
        if u['grade'] != g: return u['grade'] < g
        if u['vol'] != vol: return u['vol'] < vol
        return (u['lesson'] or 10**6) <= lesson
    phanso = [u for u in rules if 'phân số' in u['text'][:80].lower()]
    at_b57 = [u for u in phanso if visible(u, 4, 2, 57)]
    # Mẫu số là SỐ RULE PHÂN SỐ tìm được. Extraction hỏng ⇒ 0 rule ⇒ «0 rule
    # lọt» đúng một cách rỗng, và mọi cổng rò tri thức đều xanh.
    check_over('học sinh ở B57-L4: 0 rule phân số lọt',
               len(phanso), len(at_b57) == 0,
               f'chặn {len(phanso)} rule (B60+ L4 và L5)')
    at_b6_l5 = [u for u in phanso if visible(u, 5, 1, 6)]
    check_over('học sinh ở B6-L5: thấy rule lớp 4 (đã học), KHÔNG thấy lớp 5 sau đó',
               len(at_b6_l5),
               all(u['grade'] == 4 or (u['grade'] == 5 and (u['lesson'] or 0) <= 6)
                   for u in at_b6_l5), f'{len(at_b6_l5)} rule hợp lệ')
    tv = [u for u in rules if u['book'].startswith('05-sgk-tieng-viet')]
    at_tv_b9 = [u for u in tv if visible(u, 5, 2, 9)]
    check_over('TV5 ở b9-t2: rule b11/b13 (liên kết bằng kết-từ/đại-từ) bị chặn',
               len(tv),
               all((u['lesson'] or 0) <= 9 or u['vol'] == 1 for u in at_tv_b9),
               f'{len(at_tv_b9)}/{len(tv)} rule hiện')

    # G3 — EXERCISE → SkillCase: đúng theo SỰ THẬT BÀI HỌC, unmapped trung thực
    print('\nG3 exercise → skill case')
    emap = load('poc-out/units/exercise-case-map.json')
    check('mọi mapping mang status INFERRED (dựng từ hình học, không nguyên văn)',
          all(r['status'] == 'INFERRED' for r in emap))
    same_den = [r for r in emap
                if r['lesson'] == 60 and r['printed'] in (74, 75, 76)]
    check('B60 phần «cùng mẫu số» (tr.74-76) ⇒ TOÀN denominator-equal',
          len(same_den) > 0 and all(r['skillCaseId'] == 'denominator-equal'
                                    for r in same_den),
          f'{len(same_den)} biểu thức, khớp sự thật bài học')
    unlike = [r for r in emap if r['lesson'] == 60 and r['printed'] >= 78]
    check('B60 phần «khác mẫu số» (tr.78+) có ca KHÁC equal',
          any(r['skillCaseId'] != 'denominator-equal' for r in unlike),
          f'{len(unlike)} biểu thức')
    check('mẫu số 0 không bao giờ vào map',
          all('/0' not in r['expr'] for r in emap))

    # G4 — TRUNG THỰC: không tự phong coverage
    print('\nG4 trung thực (unmapped giữ unmapped)')
    rmap = load('poc-out/units/rule-concept-map.json')
    unmapped = [r for r in rmap if r['conceptId'] == 'unmapped']
    check('RULE→concept giữ unmapped thay vì đoán',
          len(unmapped) > 0, f'{len(unmapped)}/{len(rmap)} unmapped trung thực')
    # mẫu số ĐÚNG là bài tập TRONG PHẠM VI LUẬT (chương phân số), không phải
    # toàn bộ 1.706 bài tập — phần lớn là đọc/tìm/chọn/viết, không có biểu thức.
    # phạm vi ĐO TỪ TOC THẬT: chương phân số lớp 4 = B53 (khái niệm) → B66,
    # cộng ôn tập cuối năm B73; lớp 5 = B6 + ôn tập B29.
    # tập hai: B69 «Ôn tập các phép tính với số TN, phân số, số thập phân»
    # + B75 «Ôn tập chung» — đọc từ header OCR thật (title TOC parse = None).
    fr_lessons = {('04-sgk-toan-4-tap-hai', l) for l in range(53, 67)} | \
                 {('04-sgk-toan-4-tap-hai', 73)} | \
                 {('05-sgk-toan-5-tap-mot', 6), ('05-sgk-toan-5-tap-mot', 29)} | \
                 {('05-sgk-toan-5-tap-hai', 69), ('05-sgk-toan-5-tap-hai', 75)}
    inscope = [u for u in units if u['role'] == 'EXERCISE'
               and (u['book'], u['lesson']) in fr_lessons]
    ex_total = sum(1 for u in units if u['role'] == 'EXERCISE')
    print(f"     ℹ️  EXERCISE dựng được: {len(emap)} biểu thức = "
          f"{len(emap)/len(inscope):.0%} bài tập TRONG chương phân số "
          f"({len(inscope)}) · {len(emap)/ex_total:.0%} toàn bộ ({ex_total}) — "
          f"phần còn lại KHÔNG đoán")
    check('mapping không vượt phạm vi luật (chỉ chương phân số)',
          all((r['book'], r['lesson']) in fr_lessons for r in emap))
    # ⭐ CHƯƠNG TRÌNH LỌC NHẬN DẠNG: không sinh phép tính mà sách chưa dạy
    first_arith = {'04-sgk-toan-4-tap-hai': 60, '05-sgk-toan-5-tap-mot': 1,
                   '05-sgk-toan-5-tap-hai': 36}  # đầu tập — phép PS dạy từ trước
    check('không có phép cộng/trừ phân số TRƯỚC bài đầu tiên dạy nó',
          all((r['lesson'] or 0) >= first_arith.get(r['book'], 0) for r in emap),
          'ca đã bắt: B53 «Khái niệm phân số» sinh «2/3 - 3/5» — loại')

    # G5 — LearningObjective (WAL-76): nguồn nói thẳng, unmapped trung thực
    import os as _os
    _objfiles = ['poc-out/units/05-sgv-toan-5.objectives.json',
                 'poc-out/units/04-sgv-toan-4.objectives.json']
    objs = []
    for _objp in _objfiles:
        if _os.path.exists(_objp):
            objs += load(_objp)
    if not objs:
        skip('G5 learning objectives', f'không có tệp nào trong {_objfiles}')
    else:
        print('\nG5 learning objectives (SGV MỤC TIÊU, Toán 4-5)')
        check('mọi objective gán được bài', all(o['lesson'] for o in objs))
        check('mọi objective mang sourceStated',
              all(o['origin'] == 'sourceStated' for o in objs))
        check('concept unmapped giữ trung thực (không đoán 100%)',
              any(o['conceptId'] == 'unmapped' for o in objs),
              f"{sum(1 for o in objs if o['conceptId']!='unmapped')}/{len(objs)} mapped")

    # G6 — cross-grade graph (WAL-77): thứ-tự không được đội lốt lời-sách
    _gp = 'poc-out/graph/crossgrade-graph.json'
    if not _os.path.exists(_gp):
        skip('G6 cross-grade graph', f'thiếu {_gp}')
    else:
        g = json.load(open(_gp))
        print('\nG6 cross-grade graph')
        # Đồ thị 0 cạnh làm cả bốn câu dưới đúng — và 0 cạnh cũng chính là thứ
        # một builder hỏng sinh ra. Mẫu số đi trước.
        _E = g['edges']
        _bo = [e for e in _E if e['kind'] == 'BUILDS_ON']
        _rq = [e for e in _E if e['kind'] == 'REQUIRES']
        check_over('mọi cạnh mang origin', len(_E),
                   all(e.get('origin') for e in _E))
        check_over('BUILDS_ON không bao giờ tự nhận sourceStated', len(_bo),
                   all(e['origin'] != 'sourceStated' for e in _bo))
        check_over('REQUIRES chỉ tồn tại khi sourceStated', len(_rq),
                   all(e['origin'] == 'sourceStated' for e in _rq))
        check_over('mọi cạnh có evidence lần ngược được', len(_E),
                   all(e.get('evidence') for e in _E))

    # G7 — method catalogue (WAL-78): không method nào thiếu trang nguồn
    _mp = 'poc-out/units/method-catalogue.json'
    if not _os.path.exists(_mp):
        skip('G7 method catalogue', f'thiếu {_mp}')
    else:
        ms = load(_mp)
        print('\nG7 method catalogue')
        check('mọi method có trang nguồn', all(m.get('pagePrinted') for m in ms))
        check('mọi method origin sourceStated (RULE lời sách)',
              all(m['origin'] == 'sourceStated' for m in ms))
        check('quy-dong có method ở CẢ lớp 4 và lớp 5 (ca chuẩn WAL-1)',
              {4, 5} <= {m['grade'] for m in ms if m['conceptId'] == 'quy-dong'})

    # G8 — Q-matrix (WAL-79): bất định được GIỮ, không ép đầy-đủ-biết
    _qp = 'poc-out/units/qmatrix.json'
    if not _os.path.exists(_qp):
        skip('G8 Q-matrix', f'thiếu {_qp}')
    else:
        q = load(_qp)
        print('\nG8 Q-matrix')
        check('mọi entry mang mapping version', all(e.get('version') for e in q))
        check('bất định được giữ (unresolved/unmapped > 0 — trung thực)',
              any(e['tier'] != 'mapped-case' for e in q))
        check('mapped-case luôn có đủ concept + case',
              all(r.get('conceptId') and r.get('skillCaseId') not in (None, 'unresolved')
                  for e in q if e['tier'] == 'mapped-case'
                  for r in e['requirements']))
        check('concept-only không bao giờ tự nhận case',
              all(r['skillCaseId'] == 'unresolved'
                  for e in q if e['tier'] == 'concept-only'
                  for r in e['requirements']))

    # G9 — WAL-80: ba lớp lỗi còn thiếu của bộ 9 + tổng kết harness
    print('\nG9 knowledge QA (WAL-80)')
    # (7) nguồn mâu thuẫn: không hai method trùng định danh
    if not _os.path.exists('poc-out/units/method-catalogue.json'):
        skip('G9 (7) nguồn mâu thuẫn', 'thiếu method-catalogue.json')
    else:
        mc = load('poc-out/units/method-catalogue.json')
        ids = [m['methodId'] for m in mc]
        check_over('không nguồn mâu thuẫn: methodId duy nhất',
                   len(ids), len(ids) == len(set(ids)))
    # (8) knowledge-bịa-từ-OCR: đối-chứng-âm — không expr nào từ trang đầu sách
    # (mục lục/hướng dẫn, trang in < 6) lọt vào exercise-case-map
    check('đối-chứng-âm: 0 biểu thức từ trang mục-lục/hướng-dẫn (in < 6)',
          all(r['printed'] >= 6 for r in emap))
    # (9) LLM không căn cứ: hiện trạng phải là 0 llmInferred toàn corpus phái sinh
    _llm = 0
    for _f in ['poc-out/units/rule-concept-map.json',
               'poc-out/units/exercise-case-map.json',
               'poc-out/units/method-catalogue.json',
               'poc-out/units/qmatrix.json']:
        if _os.path.exists(_f):
            _llm += open(_f).read().count('llmInferred')
    check('0 suy luận LLM trong corpus phái sinh (báo cáo riêng khi xuất hiện)',
          _llm == 0, f'llmInferred: {_llm}')
    print('     ℹ️  bản đồ 9 lớp lỗi → check: ①map-sai-bài=G5+offset ②rò-tương-lai=G2'
          ' ③sai-concept=G3-B60 ④sai-case=G3 ⑤tiên-quyết-giả=G6 ⑥thiếu-provenance='
          'G1/G4/G7 ⑦nguồn-mâu-thuẫn=G9 ⑧bịa-từ-OCR=G9-đối-chứng-âm ⑨LLM-không-căn-cứ=G9')

    # ⭐⭐ PHÁN QUYẾT. Trước đây câu này chỉ đọc `FAILS`, nên một lần chạy mà bốn
    # họ cổng không hề tồn tại vẫn in ra «TẤT CẢ XANH». Chính DÒNG CHỮ ẤY là lời
    # nói dối, chứ không phải các phép kiểm.
    print()
    if FAILS:
        print(f'🔴 GATE ĐỎ: {FAILS}')
    elif SKIPPED or VACUOUS:
        print('🟡 SCALE GATE: KHÔNG ĐẦY ĐỦ — không có phép kiểm nào SAI, '
              'nhưng cũng KHÔNG đủ căn cứ để nói «tất cả xanh».')
        if SKIPPED:
            print(f'   chưa từng chạy ({len(SKIPPED)}): {SKIPPED}')
        if VACUOUS:
            print(f'   mẫu số = 0 ({len(VACUOUS)}): {VACUOUS}')
        print('   Dựng đủ artefact rồi chạy lại, hoặc gọi với --require-complete '
              'nếu chỗ gọi có KHẲNG ĐỊNH là đã kiểm đầy đủ.')
    else:
        print('🟢 SCALE GATE: TẤT CẢ XANH')

    if FAILS:
        sys.exit(1)
    # Một lần chạy không đầy đủ KHÔNG phải lỗi — corpus nằm ngoài git nên máy
    # thiếu artefact là chuyện thường. Nó chỉ không được phép đội lốt «đã kiểm».
    if (SKIPPED or VACUOUS) and '--require-complete' in sys.argv:
        print('   --require-complete: chỗ gọi khẳng định đã kiểm đầy đủ, '
              'nhưng lần chạy này thì không.')
        sys.exit(2)
    sys.exit(0)

if __name__ == '__main__':
    main()
