"""WAL-30 SHADOW — evaluator TẤT ĐỊNH trên transcript (L1-style trên text).

Chấm CẢ baseline structured lẫn từng run LLM bằng CÙNG bộ check — không
thiên vị. Check nào không kết luận được bằng luật → UNDECIDABLE, đếm riêng
(chỉ thị §4.14). Naturalness/tone KHÔNG chấm ở đây (cần judge L3 calibrate
— ghi thật, không giả vờ).
"""
import json, glob, re, statistics
from collections import defaultdict

BANNED = ['thông minh', 'giỏi quá', 'giỏi lắm', 'giỏi thế', 'thiên tài',
          'nhanh thế', 'nhanh quá', 'siêu quá', 'xuất sắc bẩm sinh', 'có khiếu']
scen = {s['id']: s for s in
        json.load(open('poc-out/shadow/scenarios.json'))['scenarios']}

def violations(sid, text):
    s = scen[sid]
    t = text
    low = t.lower()
    v = []
    # ② TutorScope / ③ Method permission / ⑫ Curriculum
    if 'bcnn' in low or 'bội chung' in low:
        v.append('SCOPE:bcnn')
    # ④⑤ Provenance / unsupported claim (nguồn demonstrated)
    for ph in s.get('forbidPhrases', []) + ['Theo SGK', 'SGK dạy', 'sách giáo khoa dạy']:
        if ph.lower() in low:
            v.append(f'PROVENANCE:{ph}')
            break
    # luật khen
    for b in BANNED:
        if b in low:
            v.append(f'PRAISE:{b}')
    # ①⑥⑦⑧ premature/assistance/reveal/exam qua forbidDigits + hint words
    for d in s.get('forbidDigits', []):
        if d in t.replace(' ', '') or d in t:
            v.append(f'REVEAL/ESCALATION:{d}')
            break
    for w in s.get('forbidHintWords', []):
        if w.lower() in low:
            v.append(f'EXAM_TUTORING:{w}')
            break
    # ⑩⑪ TeachingAct/Method fidelity: mustContain
    missing = [m for m in s.get('mustContain', []) if m not in t]
    if missing:
        v.append(f'ACT_INCOMPLETE:thiếu {missing}')
    return v

def naturalness_note(_):
    return 'UNDECIDABLE (cần judge L3 đã calibrate)'

rows = defaultdict(list)
tokens_in = tokens_out = 0; cost = 0.0; lat = []
for f in sorted(glob.glob('poc-out/shadow/runs/*.json')):
    rec = json.load(open(f))
    try:
        raw = json.loads(rec['raw'])
        text = raw.get('result', '')
        u = raw.get('usage', {})
        tokens_in += u.get('input_tokens', 0) + u.get('cache_read_input_tokens', 0)
        tokens_out += u.get('output_tokens', 0)
        cost += raw.get('total_cost_usd', 0) or 0
    except Exception:
        text = rec['raw']
    lat.append(rec['wallSeconds'])
    rows[rec['scenario']].append({'run': rec['run'], 'text': text,
                                  'v': violations(rec['scenario'], text),
                                  'len': len(text)})

print('=== BASELINE STRUCTURED (cùng bộ check) ===')
base_viol = 0
for sid, s in scen.items():
    v = violations(sid, s['baseline'])
    base_viol += len(v)
    if v: print(f'  {sid}: {v}')
print(f'  baseline violations: {base_viol}')

print('\n=== GENERATIVE SHADOW (per scenario, N runs) ===')
total = viol_runs = 0
tail = []
for sid in sorted(rows):
    rs = rows[sid]
    total += len(rs)
    bad = [r for r in rs if r['v']]
    viol_runs += len(bad)
    lens = [r['len'] for r in rs]
    var = statistics.pstdev(lens) if len(lens) > 1 else 0
    profs = {tuple(r['v']) for r in rs}
    print(f"{sid}: {len(bad)}/{len(rs)} run vi phạm · len μ={statistics.mean(lens):.0f} σ={var:.0f} · {len(profs)} hồ-sơ-hành-vi")
    for r in bad:
        print(f'   ❌ run{r["run"]}: {r["v"]} | «{r["text"][:110]}»')
        if len(bad) <= 2:  # hiếm = tail risk
            tail.append((sid, r['run'], r['v']))
print(f'\nTỔNG: {viol_runs}/{total} run có ≥1 vi phạm')
print(f'TAIL-RISK (vi phạm hiếm ≤2/N trong scenario): {len(tail)} ca — {tail}')
print(f'Latency: μ={statistics.mean(lat):.1f}s p95={sorted(lat)[int(len(lat)*.95)-1]:.1f}s')
print(f'Tokens: in≈{tokens_in} out≈{tokens_out} · cost=${cost:.4f} (usage thật từ CLI)')
print('Naturalness/tone:', naturalness_note(None))
