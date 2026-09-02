"""WAL-74 batch ④ — SCALE GATE tự động trên corpus thật.

Chạy: python3 tool/extract/verify_corpus_gates.py  (exit≠0 = gate ĐỎ)

Không nằm trong `flutter test` vì corpus + sản phẩm phái sinh ở NGOÀI git
(ADR-002). Suite Dart giữ luật trên fixture; script này giữ luật trên DỮ LIỆU
THẬT. Cả hai phải xanh trước khi mở rộng semantic ingestion (Founder Delta §7).
"""
import json, sys

FAILS = []
def check(name, ok, detail=''):
    print(f"  {'✅' if ok else '❌'} {name}" + (f' — {detail}' if detail else ''))
    if not ok:
        FAILS.append(name)

def load(p):
    return json.load(open(p))

def main():
    units = []
    for b in ['05-sgk-toan-5-tap-mot', '04-sgk-toan-4-tap-mot',
              '04-sgk-toan-4-tap-hai', '05-sgk-tieng-viet-5-tap-mot',
              '05-sgk-tieng-viet-5-tap-hai']:
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
    check('học sinh ở B57-L4: 0 rule phân số lọt',
          len(at_b57) == 0, f'chặn {len(phanso)} rule (B60+ L4 và L5)')
    at_b6_l5 = [u for u in phanso if visible(u, 5, 1, 6)]
    check('học sinh ở B6-L5: thấy rule lớp 4 (đã học), KHÔNG thấy lớp 5 sau đó',
          all(u['grade'] == 4 or (u['grade'] == 5 and (u['lesson'] or 0) <= 6)
              for u in at_b6_l5), f'{len(at_b6_l5)} rule hợp lệ')
    tv = [u for u in rules if u['book'].startswith('05-sgk-tieng-viet')]
    at_tv_b9 = [u for u in tv if visible(u, 5, 2, 9)]
    check('TV5 ở b9-t2: rule b11/b13 (liên kết bằng kết-từ/đại-từ) bị chặn',
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
    if objs:
        print('\nG5 learning objectives (SGV MỤC TIÊU, Toán 4-5)')
        check('mọi objective gán được bài', all(o['lesson'] for o in objs))
        check('mọi objective mang sourceStated',
              all(o['origin'] == 'sourceStated' for o in objs))
        check('concept unmapped giữ trung thực (không đoán 100%)',
              any(o['conceptId'] == 'unmapped' for o in objs),
              f"{sum(1 for o in objs if o['conceptId']!='unmapped')}/{len(objs)} mapped")

    # G6 — cross-grade graph (WAL-77): thứ-tự không được đội lốt lời-sách
    _gp = 'poc-out/graph/crossgrade-graph.json'
    if _os.path.exists(_gp):
        g = json.load(open(_gp))
        print('\nG6 cross-grade graph')
        check('mọi cạnh mang origin', all(e.get('origin') for e in g['edges']))
        check('BUILDS_ON không bao giờ tự nhận sourceStated',
              all(e['origin'] != 'sourceStated' for e in g['edges']
                  if e['kind'] == 'BUILDS_ON'))
        check('REQUIRES chỉ tồn tại khi sourceStated',
              all(e['origin'] == 'sourceStated' for e in g['edges']
                  if e['kind'] == 'REQUIRES'))
        check('mọi cạnh có evidence lần ngược được',
              all(e.get('evidence') for e in g['edges']))

    # G7 — method catalogue (WAL-78): không method nào thiếu trang nguồn
    _mp = 'poc-out/units/method-catalogue.json'
    if _os.path.exists(_mp):
        ms = load(_mp)
        print('\nG7 method catalogue')
        check('mọi method có trang nguồn', all(m.get('pagePrinted') for m in ms))
        check('mọi method origin sourceStated (RULE lời sách)',
              all(m['origin'] == 'sourceStated' for m in ms))
        check('quy-dong có method ở CẢ lớp 4 và lớp 5 (ca chuẩn WAL-1)',
              {4, 5} <= {m['grade'] for m in ms if m['conceptId'] == 'quy-dong'})

    # G8 — Q-matrix (WAL-79): bất định được GIỮ, không ép đầy-đủ-biết
    _qp = 'poc-out/units/qmatrix.json'
    if _os.path.exists(_qp):
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

    print('\n' + ('🟢 SCALE GATE: TẤT CẢ XANH' if not FAILS
                  else f'🔴 GATE ĐỎ: {FAILS}'))
    sys.exit(1 if FAILS else 0)

if __name__ == '__main__':
    main()
