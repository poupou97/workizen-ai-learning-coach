#!/usr/bin/env python3
"""WAL-115 — UNIT ECONOMICS / AI COST từ SỐ ĐO THẬT (không phỏng đoán số đo).

Nguồn đo:
- poc-out/shadow/runs/*.json — 50 run LLM THẬT (haiku qua claude -p, usage +
  total_cost_usd từ CLI). Đây là chi phí MỘT LƯỢT CAN THIỆP generative.
- MODE A (production hôm nay): engine tất định — 0 LLM call THEO CẤU TRÚC
  (test Dart giữ: lib/core không import network/LLM).

Phần MÔ HÌNH HOÁ (khai tường minh, không trộn với số đo):
- turns/session và sessions/ngày theo 3 usage profile — GIẢ ĐỊNH khai rõ,
  neo vào hình phiên thật của slice (ladder ≤2 hint + 1 worked + reveal-gate).
"""
import glob, json, statistics

runs = []
for f in sorted(glob.glob('poc-out/shadow/runs/*.json')):
    rec = json.load(open(f))
    raw = json.loads(rec['raw'])
    u = raw.get('usage', {})
    runs.append(dict(
        cost=raw.get('total_cost_usd') or 0.0,
        tin=u.get('input_tokens', 0),
        cache_read=u.get('cache_read_input_tokens', 0),
        cache_create=u.get('cache_creation_input_tokens', 0),
        tout=u.get('output_tokens', 0),
        lat=rec['wallSeconds'],
    ))
n = len(runs)
costs = sorted(r['cost'] for r in runs)
lats = sorted(r['lat'] for r in runs)
mean_cost = statistics.mean(costs)
p95_cost = costs[int(n * .95) - 1]
mean_out = statistics.mean(r['tout'] for r in runs)
mean_cr = statistics.mean(r['cache_read'] for r in runs)
mean_cc = statistics.mean(r['cache_create'] for r in runs)

print(f'=== ĐO THẬT (N={n} run haiku, usage CLI) ===')
print(f'cost/turn: μ=${mean_cost:.4f} · p95=${p95_cost:.4f} · min=${costs[0]:.4f} · max=${costs[-1]:.4f}')
print(f'tokens/turn: out μ={mean_out:.0f} · cache_read μ={mean_cr:.0f} · cache_create μ={mean_cc:.0f}')
print(f'latency: μ={statistics.mean(lats):.1f}s · p95={lats[int(n*.95)-1]:.1f}s')
print('⚠️ harness = claude CLI (system prompt CLI ~17k cached) — cost/turn này là')
print('   TRẦN THÔ; API trực tiếp với cage prompt (~1-2k tokens) sẽ thấp hơn. Giữ')
print('   số ĐO làm baseline, KHÔNG tự chiết khấu.')

# ---- MÔ HÌNH 3 MODE × 3 PROFILE (giả định khai tường minh) ------------------
# Hình phiên từ slice thật (ladder AssistancePolicy): 1 phiên tutor ≈
#   6-10 lượt tương tác; can thiệp dạy (hint/worked) ≤ 3 (ladder ±1 + cap).
MODES = {
    'A-deterministic (production hôm nay)': 0.0,   # LLM turns/session — CẤU TRÚC
    'B-minimal-generative (hint realize)':  2.0,   # ≤2 hint climbs (policy cap)
    'C-LLM-heavy (mọi lượt qua LLM)':       8.0,   # ≈ mọi tương tác
}
PROFILES = {                       # sessions/ngày (giả định khai rõ)
    'nhẹ (1 phiên/ngày)': 1,
    'vừa (2 phiên/ngày)': 2,
    'nặng (4 phiên/ngày)': 4,
}
print('\n=== COST/LEARNER/THÁNG (30 ngày) — cost/turn ĐO × turns MÔ HÌNH ===')
hdr = 'mode'.ljust(38) + ''.join(k.ljust(22) for k in PROFILES)
print(hdr)
for mode, llm_turns in MODES.items():
    row = mode.ljust(38)
    for _, sess in PROFILES.items():
        monthly = mean_cost * llm_turns * sess * 30
        row += f'${monthly:,.2f}/tháng'.ljust(22)
    print(row)
print('\nKẾT LUẬN CHẾ ĐỘ (đề xuất, quyết định = Founder):')
print('- MODE A: $0 LLM COGS theo cấu trúc ⇒ Student Free credible vô điều kiện.')
print(f'- MODE B: ~${mean_cost*2*2*30:.2f}/learner/tháng (vừa) — cần cage-prompt')
print('  gọn + cache để hạ; latency p95 ~22s hiện KHÔNG đạt cho hint inline.')
print(f'- MODE C: ~${mean_cost*8*4*30:.2f}/learner/tháng (nặng) — không bền cho')
print('  free tier; củng cố deterministic-first + KEEP SHADOW (WAL-30).')
