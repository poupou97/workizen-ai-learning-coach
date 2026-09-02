"""WAL-30 SHADOW — chạy lặp N lần/scenario qua claude -p (json → usage thật)."""
import json, subprocess, time, os

N = 5
MODEL = 'haiku'
scen = json.load(open('poc-out/shadow/scenarios.json'))['scenarios']
os.makedirs('poc-out/shadow/runs', exist_ok=True)
for s in scen:
    for i in range(N):
        out_path = f"poc-out/shadow/runs/{s['id']}_{i}.json"
        if os.path.exists(out_path):
            continue
        t0 = time.time()
        r = subprocess.run(
            ['claude', '-p', s['prompt'], '--model', MODEL,
             '--output-format', 'json'],
            capture_output=True, text=True, timeout=120)
        dt = time.time() - t0
        rec = {'scenario': s['id'], 'run': i, 'model': MODEL,
               'wallSeconds': round(dt, 2), 'exit': r.returncode,
               'raw': r.stdout, 'stderr': r.stderr[-500:]}
        json.dump(rec, open(out_path, 'w'), ensure_ascii=False)
        print(f"{s['id']} #{i}: {dt:.1f}s exit={r.returncode}")
print('DONE', len(scen) * N)
