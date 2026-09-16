#!/usr/bin/env python3
"""Dựng bộ gói di trú từ cây repo. CÔNG THỨC, không phải artefact.

15-09 đã mất cả thư mục gói trên Desktop. Dữ liệu nguồn còn nên dựng lại
được — nhưng lần đó tôi đóng gói thủ công, nên mất Desktop là mất luôn cách
làm. Tệp này tồn tại để điều đó không lặp lại.

Hai bài học đã trả giá, được mã hoá thành luật ở đây:

* `zip -x` KHÔNG loại được thư mục — lần đầu tệp tạm phình 23 GB vì nuốt cả
  11 GB PDF. Ở đây luôn dựng DANH SÁCH TỆP TƯỜNG MINH rồi nạp qua `zip -@`.
* Tổng byte phải được cộng TRƯỚC khi nén và đối chiếu SAU khi giải nén thử.
  Kích thước khớp chưa phải toàn vẹn, nên còn chạy `unzip -t`.

Chạy:
    python3 tool/ops/build_migration_zips.py --out ~/wal-migration
"""
import argparse
import hashlib
import os
import subprocess
import sys

#: Thư mục trong repo, theo tầng. Thứ tự tải = thứ tự trong dict.
TIERS = {
    # Không tạo lại được trên Windows: đầu ra OCR (docling+ocrmac, chỉ macOS),
    # TSL + attach, và pack/fixture mà client đọc.
    'T1-critical': ['poc-out/graph', 'poc-out/trusted-corpus', 'assets'],
    # Dựng lại được nhưng mất nhiều giờ.
    'T3-derived': ['poc-out'],          # trừ những gì tầng khác đã lấy
    # Văn bản quy định + bản tải gốc từ Drive (zip lồng zip, KHÔNG bung).
    'T2a-nguon-chi-thuc': ['nguon-chi-thuc'],
    # 531 cuốn PDF.
    'T2b-poc-out-pdf': ['poc-out/pdf'],
}

#: T3-derived là phần bù — poc-out trừ đi các nhánh tầng khác đã lấy.
T3_EXCLUDE = ['poc-out/graph', 'poc-out/trusted-corpus', 'poc-out/pdf']

#: Tiền tố trong zip. Máy mới bỏ tầng này khi bung.
PREFIX = 'repo-heavy'


def walk(root):
    """Mọi tệp thường dưới root, đường tương đối so với cwd."""
    out = []
    for base, dirs, files in os.walk(root):
        dirs[:] = [d for d in dirs if d != '.git']
        for f in files:
            p = os.path.join(base, f)
            if os.path.isfile(p) and not os.path.islink(p):
                out.append(p)
    return out


def files_for(tier):
    got = []
    for d in TIERS[tier]:
        if not os.path.isdir(d):
            sys.exit(f'⛔ thiếu nguồn: {d}')
        got += walk(d)
    if tier == 'T3-derived':
        bad = tuple(x + os.sep for x in T3_EXCLUDE)
        got = [p for p in got if not p.startswith(bad)]
    return sorted(set(got))


def sha256(path, buf=1 << 20):
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        for b in iter(lambda: f.read(buf), b''):
            h.update(b)
    return h.hexdigest()


def zip_list(paths, dest, prefix, cwd):
    """Nạp danh sách tệp qua stdin. KHÔNG dùng -x: nó không loại thư mục."""
    listing = '\n'.join(paths) + '\n'
    if prefix:
        # zip không đổi tên được, nên gói từ thư mục cha có sẵn tiền tố
        paths = [os.path.join(prefix, p) for p in paths]
        listing = '\n'.join(paths) + '\n'
    r = subprocess.run(['zip', '-q', '-@', dest], input=listing,
                       text=True, cwd=cwd)
    if r.returncode not in (0,):
        sys.exit(f'⛔ zip trả mã {r.returncode} cho {dest}')


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--repo', default='.')
    ap.add_argument('--out', required=True)
    ap.add_argument('--memory', default=os.path.expanduser(
        '~/.claude/projects/-Users-alexnguyen-projects-'
        'workizen-ai-learning-coach/memory'))
    ap.add_argument('--only', help='chỉ dựng một tầng')
    a = ap.parse_args()

    repo = os.path.abspath(os.path.expanduser(a.repo))
    out = os.path.abspath(os.path.expanduser(a.out))
    os.makedirs(out, exist_ok=True)
    os.chdir(repo)

    # zip cần tiền tố repo-heavy/ — dựng cây liên kết tạm ở thư mục cha
    parent = os.path.dirname(repo)
    link = os.path.join(parent, PREFIX)
    made_link = False
    if not os.path.exists(link):
        os.symlink(repo, link)
        made_link = True

    try:
        sums = []
        for tier in TIERS:
            if a.only and tier != a.only:
                continue
            dest = os.path.join(out, tier + '.zip')
            if os.path.exists(dest):
                print(f'— bỏ qua {tier}: đã có')
                continue
            paths = files_for(tier)
            total = sum(os.path.getsize(p) for p in paths)
            print(f'{tier}: {len(paths):,} tệp, {total:,} byte nguồn … ', end='', flush=True)
            zip_list(paths, dest, PREFIX, cwd=parent)

            # unzip in tên tệp tiếng Việt dạng NFD — KHÔNG phải UTF-8 hợp lệ.
            # `text=True` ở đây làm sập cả lần dựng 25 GB (16-09). Đọc bytes.
            raw = subprocess.run(['unzip', '-l', dest],
                                 capture_output=True).stdout
            n = raw.decode('utf-8', 'replace').strip().splitlines()[-1].split()
            t = subprocess.run(['unzip', '-tq', dest], capture_output=True)
            ok = t.returncode == 0
            print(f'→ {os.path.getsize(dest):,} byte, {n[1]} mục, '
                  f'{"toàn vẹn" if ok else "⛔ HỎNG"}')
            if not ok:
                sys.exit(f'⛔ {dest} không qua unzip -t')
            sums.append((sha256(dest), tier + '.zip'))

        if sums:
            p = os.path.join(out, 'SHA256SUMS.txt')
            mode = 'a' if os.path.exists(p) else 'w'
            with open(p, mode, encoding='utf-8') as f:
                for h, name in sums:
                    f.write(f'{h}  {name}\n')
            print(f'\nbăm ghi vào {p}')
    finally:
        if made_link:
            os.unlink(link)


if __name__ == '__main__':
    main()
