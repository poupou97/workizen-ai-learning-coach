#!/usr/bin/env python3
"""BẢN KÊ DI TRÚ — và dụng cụ VERIFY chạy được trên cả macOS lẫn Windows.

Dữ liệu nặng của dự án KHÔNG nằm trong Git: `poc-out/` (15 GB) và
`nguon-chi-thuc/` (9,8 GB) có **0 tệp** được theo dõi. `git clone` trên máy
mới chỉ được MÃ. Nên bản sao lưu phải tự mang theo cách chứng minh nó đúng.

⛔ ĐỪNG BIẾN DI TRÚ MÁY THÀNH DI TRÚ OCR. Kho canonical được dựng bằng
`docling-2.126+ocrmac` — `ocrmac` bọc Apple Vision, CHỈ chạy trên macOS. Mọi
con số của dự án hiệu chỉnh trên đầu ra ấy. Chạy lại OCR bằng engine khác là
một KHO KHÁC, không phải một bản sao.

Hai mức kiểm, vì 25 GB mà băm từng byte thì quá lâu để làm thường xuyên:

  FULL   băm SHA-256 TỪNG TỆP — cho thư mục quý và nhỏ
  QUICK  ghi kích thước + mtime từng tệp, và băm CHỮ KÝ của bảng ấy —
         phát hiện thiếu tệp, lệch kích thước, cắt cụt; không phát hiện
         được hỏng bit trong một tệp giữ nguyên kích thước

⚠ CHỮ TIẾNG VIỆT TRONG TÊN TỆP. macOS lưu tên ở dạng NFD, Windows dùng NFC —
cùng một tên nhưng khác byte. Bản kê ghi tên đã chuẩn hoá **NFC** để hai máy
so được với nhau; tên thô giữ trong `rawName` khi hai dạng khác nhau.
"""
import argparse
import hashlib
import json
import os
import sys
import unicodedata

#: Thư mục băm TỪNG TỆP — quý, và đủ nhỏ để làm thường xuyên.
FULL = ['assets/pack', 'assets/fixtures', 'poc-out/trusted-corpus',
        'poc-out/graph', 'poc-out/pedagogy', 'poc-out/units-k12']
#: Thư mục chỉ ghi kích thước + mtime — hàng chục GB, phần lớn là PDF.
QUICK = ['nguon-chi-thuc', 'poc-out']


def sha256(path, buf=1 << 20):
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        while True:
            b = f.read(buf)
            if not b:
                break
            h.update(b)
    return h.hexdigest()


def walk(root, base):
    for dp, dns, fns in os.walk(root):
        dns[:] = [d for d in sorted(dns) if d not in ('__pycache__',)]
        for fn in sorted(fns):
            if fn == '.DS_Store':
                continue
            p = os.path.join(dp, fn)
            if os.path.islink(p):
                continue
            yield p, os.path.relpath(p, base)


def entry(p, rel, full):
    st = os.stat(p)
    nfc = unicodedata.normalize('NFC', rel)
    e = {'path': nfc, 'size': st.st_size, 'mtime': int(st.st_mtime)}
    if nfc != rel:
        e['rawName'] = rel          # macOS lưu NFD; giữ để truy nguyên
    if full:
        e['sha256'] = sha256(p)
    return e


def scan(base, dirs, full):
    out, skipped = [], []
    for d in dirs:
        root = os.path.join(base, d)
        if not os.path.isdir(root):
            skipped.append(d)
            continue
        for p, rel in walk(root, base):
            try:
                out.append(entry(p, rel, full))
            except OSError as e:
                skipped.append(f'{rel}: {e}')
    return out, skipped


def verify(base, man_path, deep):
    """So cây thật với bản kê. Trả số lỗi — 0 là ĐẠT.

    Chạy được trên Windows: chỉ dùng `os`, `hashlib`, `unicodedata`. Tên tệp
    so ở dạng NFC hai phía nên NFD của macOS không gây báo động giả.
    """
    man = json.load(open(man_path, encoding='utf-8'))
    bad = {'thiếu': [], 'lệch kích thước': [], 'sai băm': [], 'thừa': []}
    seen = set()
    for grp in ('full', 'quick'):
        for f in man[grp]['files']:
            rel = f['path']
            seen.add(rel)
            p = os.path.join(base, rel)
            if not os.path.isfile(p):
                # macOS ghi NFD; thử lại bằng dạng thô nếu bản kê có
                alt = os.path.join(base, f.get('rawName') or '')
                if not (f.get('rawName') and os.path.isfile(alt)):
                    bad['thiếu'].append(rel)
                    continue
                p = alt
            if os.path.getsize(p) != f['size']:
                bad['lệch kích thước'].append(rel)
                continue
            if 'sha256' in f and (deep or grp == 'full'):
                if sha256(p) != f['sha256']:
                    bad['sai băm'].append(rel)
    for d in man['full']['dirs'] + man['quick']['dirs']:
        root = os.path.join(base, d)
        if not os.path.isdir(root):
            continue
        for p, rel in walk(root, base):
            if unicodedata.normalize('NFC', rel) not in seen:
                bad['thừa'].append(rel)
    n = sum(len(v) for v in bad.values())
    for k, v in bad.items():
        print(f'  {k:16s} {len(v):>6,}' + (f'   vd: {v[0][:70]}' if v else ''))
    print(f'{"ĐẠT — bản sao đọc được và khớp bản kê" if n == 0 else f"⛔ {n} sai lệch"}')
    return n


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--base', default='.')
    ap.add_argument('--verify', metavar='MANIFEST',
                    help='so cây tại --base với bản kê này')
    ap.add_argument('--deep', action='store_true',
                    help='băm cả nhóm QUICK khi verify (chậm, ~25 GB)')
    ap.add_argument('--out', default='MIGRATION-MANIFEST.json')
    ap.add_argument('--quick-only', action='store_true',
                    help='bỏ băm từng tệp — dùng để kiểm nhanh bản đã chép')
    a = ap.parse_args()
    base = os.path.abspath(a.base)
    if a.verify:
        return sys.exit(1 if verify(base, a.verify, a.deep) else 0)

    full_files, sk1 = ([], []) if a.quick_only else scan(base, FULL, True)
    full_set = {f['path'] for f in full_files}
    quick_all, sk2 = scan(base, QUICK, False)
    # tệp đã băm đầy đủ thì không lặp lại ở bảng nhanh
    quick_files = [f for f in quick_all if f['path'] not in full_set]

    sig = hashlib.sha256()
    for f in sorted(quick_files, key=lambda x: x['path']):
        sig.update(f"{f['path']}\0{f['size']}\n".encode())

    man = {
        'schema': 'migration-manifest-v1',
        'ocrEngine': 'docling-2.126+ocrmac (macOS Vision — KHÔNG chạy trên Windows)',
        'full': {'dirs': FULL, 'count': len(full_files),
                 'bytes': sum(f['size'] for f in full_files),
                 'files': full_files},
        'quick': {'dirs': QUICK, 'count': len(quick_files),
                  'bytes': sum(f['size'] for f in quick_files),
                  'tableSha256': sig.hexdigest(), 'files': quick_files},
        'skipped': sk1 + sk2,
    }
    with open(os.path.join(base, a.out), 'w', encoding='utf-8') as f:
        json.dump(man, f, ensure_ascii=False)
    g = lambda n: f'{n / 1e9:.2f} GB'
    print(f"FULL  {man['full']['count']:>7,} tệp · {g(man['full']['bytes'])}"
          f"  (băm SHA-256 từng tệp)")
    print(f"QUICK {man['quick']['count']:>7,} tệp · {g(man['quick']['bytes'])}"
          f"  (kích thước+mtime · chữ ký {man['quick']['tableSha256'][:16]}…)")
    if man['skipped']:
        print(f"BỎ QUA: {man['skipped'][:5]}", file=sys.stderr)
    print(f"→ {a.out}")


if __name__ == '__main__':
    main()
