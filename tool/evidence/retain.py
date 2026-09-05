#!/usr/bin/env python3
"""ROUND 3 §6 — EVIDENCE RETENTION: một tuyên bố «đã kiểm trên máy thật» phải
truy được về (a) frame nào, (b) bản build nào, (c) máy nào, (d) lúc nào —
hoặc bị hạ cấp. Công cụ này sinh MANIFEST.json cho một vòng thiết bị.

    python3 tool/evidence/retain.py \\
        --round round3 \\
        --frames docs/design/track-b-evidence/round3 \\
        --steps docs/design/track-b-evidence/round3/steps.json \\
        [--apk build/app/outputs/flutter-apk/app-debug.apk] \\
        [--packs assets/pack] [--fixture assets/fixtures/real/<file>.json] \\
        [--device 192.168.1.3:5555 | --no-device] [--adb <path>] \\
        [--out docs/design/track-b-evidence/round3/MANIFEST.json]

Manifest ghi: thời điểm sinh; git SHA + nhánh + trạng thái sạch/bẩn; sha256
của APK; `packVersion`/`contentHash` của từng pack `lesson-index-g*.json`
(từ `buildProvenance`); provenance của fixture bài học; metadata máy
(`ro.product.model`, `ro.build.version.release`, `ro.serialno` KHÔNG ghi) qua
`adb shell getprop` — chỉ đọc, không gửi input; sha256 + kích thước của từng
frame; bảng bước-checklist → kết quả + frame; và phần `claims` kiểm chéo: bước
nào khai frame mà frame không tồn tại ⇒ `result` bị HẠ CẤP thành
`UNVERIFIED (missing frame)` — máy hạ, người không phải nhớ.

Chỉ thư viện chuẩn. Không xoá, không sửa frame. Không đọc PDF. File
`steps.json` do người đi checklist viết:
    {"device": "Nokia 6.1 (192.168.1.3:5555)", "iterations": [
      {"iter": 1, "build": {"gitSha": "…"}, "steps": [
        {"step": "01", "expect": "Home «Chào Na!»", "result": "PASS",
         "frames": ["round3-1-01-home.png"], "note": "…"}]}]}
"""
from __future__ import annotations

import argparse
import datetime as _dt
import hashlib
import json
import os
import subprocess
import sys

FRAME_EXT = ('.png', '.jpg', '.jpeg', '.webp')
FORBIDDEN_NAME_HINTS = ('lock', 'lockscreen', 'notification', 'notif')


def sha256_of(path: str) -> str:
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        for chunk in iter(lambda: f.read(1 << 20), b''):
            h.update(chunk)
    return h.hexdigest()


def run(cmd: list[str], timeout: int = 20) -> str | None:
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
    except (OSError, subprocess.TimeoutExpired):
        return None
    if r.returncode != 0:
        return None
    return r.stdout.strip()


def git_info(root: str) -> dict:
    sha = run(['git', '-C', root, 'rev-parse', 'HEAD'])
    branch = run(['git', '-C', root, 'rev-parse', '--abbrev-ref', 'HEAD'])
    status = run(['git', '-C', root, 'status', '--porcelain', '--untracked-files=no'])
    return {
        'sha': sha,
        'branch': branch,
        'dirty': None if status is None else bool(status.strip()),
    }


def pack_versions(packs_dir: str | None) -> list[dict]:
    if not packs_dir or not os.path.isdir(packs_dir):
        return []
    out = []
    for name in sorted(os.listdir(packs_dir)):
        if not (name.startswith('lesson-index-g') and name.endswith('.json')):
            continue
        p = os.path.join(packs_dir, name)
        try:
            j = json.load(open(p, encoding='utf-8'))
        except (OSError, ValueError):
            out.append({'file': name, 'error': 'unreadable'})
            continue
        prov = j.get('buildProvenance') if isinstance(j, dict) else None
        out.append({
            'file': name,
            'sha256': sha256_of(p),
            'packVersion': (prov or {}).get('packVersion'),
            'contentHash': (prov or {}).get('contentHash'),
            'experimental': (prov or {}).get('experimental'),
            'provenance': prov is not None,
        })
    return out


def fixture_info(path: str | None) -> dict | None:
    if not path or not os.path.isfile(path):
        return None
    try:
        j = json.load(open(path, encoding='utf-8'))
    except (OSError, ValueError):
        return {'file': os.path.basename(path), 'error': 'unreadable'}
    prov = j.get('provenance') or {}
    return {
        'file': os.path.basename(path),
        'sha256': sha256_of(path),
        'book': j.get('book'),
        'lesson': j.get('lesson'),
        'trust': prov.get('trust'),
        'sourcePipeline': prov.get('sourcePipeline'),
        'generator': prov.get('generator'),
        'blocks': len(j.get('blocks') or []),
        'semantic': len(j.get('semantic') or []),
        'tutorSteps': len((j.get('tutorScript') or {}).get('steps') or []),
    }


def device_info(adb: str, serial: str | None) -> dict:
    """Chỉ `getprop` (đọc). Không `input`, không `keyevent`."""
    if not serial:
        return {'skipped': True}
    base = [adb, '-s', serial, 'shell', 'getprop']
    model = run(base + ['ro.product.model'])
    release = run(base + ['ro.build.version.release'])
    sdk = run(base + ['ro.build.version.sdk'])
    return {
        'serial': serial,
        'model': model,
        'androidRelease': release,
        'sdk': sdk,
        'reachable': model is not None,
    }


def frames_info(frames_dir: str) -> tuple[list[dict], list[str]]:
    out, warnings = [], []
    if not os.path.isdir(frames_dir):
        return out, [f'frames dir missing: {frames_dir}']
    for name in sorted(os.listdir(frames_dir)):
        if not name.lower().endswith(FRAME_EXT):
            continue
        p = os.path.join(frames_dir, name)
        st = os.stat(p)
        low = name.lower()
        if any(h in low for h in FORBIDDEN_NAME_HINTS):
            warnings.append(f'frame name suggests lock/notification content: {name}')
        out.append({
            'file': name,
            'sha256': sha256_of(p),
            'bytes': st.st_size,
            'mtime': _dt.datetime.fromtimestamp(st.st_mtime, _dt.timezone.utc).isoformat(),
        })
    return out, warnings


def cross_check(steps_doc: dict, frame_names: set[str]) -> tuple[list[dict], dict]:
    """Bước khai frame không tồn tại ⇒ HẠ CẤP. Trả (iterations, summary)."""
    iterations = []
    counts = {'PASS': 0, 'FAIL': 0, 'SKIP': 0, 'UNVERIFIED': 0, 'OTHER': 0}
    for it in steps_doc.get('iterations') or []:
        steps_out = []
        for s in it.get('steps') or []:
            frames = list(s.get('frames') or [])
            missing = [f for f in frames if f not in frame_names]
            result = str(s.get('result') or 'OTHER').upper()
            downgraded = False
            if result == 'PASS' and (not frames or missing):
                result = 'UNVERIFIED (missing frame)'
                downgraded = True
            key = result.split(' ')[0]
            counts[key if key in counts else 'OTHER'] += 1
            steps_out.append({
                **{k: v for k, v in s.items() if k != 'frames'},
                'frames': frames,
                'missingFrames': missing,
                'result': result,
                'downgraded': downgraded,
            })
        iterations.append({**{k: v for k, v in it.items() if k != 'steps'}, 'steps': steps_out})
    return iterations, counts


def build_manifest(a: argparse.Namespace) -> dict:
    root = os.path.abspath(a.root)
    frames, warnings = frames_info(a.frames)
    steps_doc = {}
    if a.steps and os.path.isfile(a.steps):
        steps_doc = json.load(open(a.steps, encoding='utf-8'))
    elif a.steps:
        warnings.append(f'steps file missing: {a.steps}')
    iterations, counts = cross_check(steps_doc, {f['file'] for f in frames})
    apk = None
    if a.apk and os.path.isfile(a.apk):
        apk = {'file': os.path.relpath(a.apk, root), 'sha256': sha256_of(a.apk),
               'bytes': os.path.getsize(a.apk)}
    elif a.apk:
        warnings.append(f'apk missing: {a.apk}')
    return {
        'schema': 'wal-evidence-manifest-v1',
        'round': a.round,
        'generatedAt': _dt.datetime.now(_dt.timezone.utc).isoformat(),
        'git': git_info(root),
        'apk': apk,
        'packs': pack_versions(a.packs),
        'fixture': fixture_info(a.fixture),
        'device': device_info(a.adb, None if a.no_device else a.device),
        'declaredDevice': steps_doc.get('device'),
        'frames': frames,
        'iterations': iterations,
        'summary': {
            'frames': len(frames),
            'steps': counts,
            'downgraded': sum(1 for it in iterations for s in it['steps'] if s['downgraded']),
        },
        'retentionRules': [
            'no lock-screen / personal-notification frames',
            'no raw PDF pages; SGK crops inside frames are internal (Founder D4)',
            'a PASS without an existing frame is downgraded to UNVERIFIED',
        ],
        'warnings': warnings,
    }


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--round', required=True)
    ap.add_argument('--frames', required=True, help='thư mục chứa frame')
    ap.add_argument('--steps', help='steps.json: bước → kết quả → frame')
    ap.add_argument('--apk')
    ap.add_argument('--packs', default='assets/pack')
    ap.add_argument('--fixture')
    ap.add_argument('--device', default='192.168.1.3:5555')
    ap.add_argument('--no-device', action='store_true')
    ap.add_argument('--adb', default=os.environ.get('ADB', 'adb'))
    ap.add_argument('--root', default='.')
    ap.add_argument('--out', help='mặc định <frames>/MANIFEST.json')
    ap.add_argument('--print', action='store_true', help='in tóm tắt')
    a = ap.parse_args(argv)
    m = build_manifest(a)
    out = a.out or os.path.join(a.frames, 'MANIFEST.json')
    os.makedirs(os.path.dirname(out) or '.', exist_ok=True)
    with open(out, 'w', encoding='utf-8') as f:
        json.dump(m, f, ensure_ascii=False, indent=2)
        f.write('\n')
    if a.print:
        print(json.dumps(m['summary'], ensure_ascii=False))
        for w in m['warnings']:
            print('WARN', w, file=sys.stderr)
    return 1 if m['summary']['downgraded'] else 0


if __name__ == '__main__':
    sys.exit(main())
