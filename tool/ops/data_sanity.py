#!/usr/bin/env python3
"""Đo năng lực + bất biến kho TỪ DỮ LIỆU, để hai máy so được với nhau.

Vì sao có tệp này: các con số đầu bài của dự án (`SAM_READY`,
`OPENABLE_RECORDS`…) tới nay chỉ nằm trong `docs/`. Tài liệu không phải phép
đo — và di trú máy là đúng lúc cái khác biệt ấy thành đắt. Chạy CÙNG một lệnh
trên Mac và trên Windows rồi so từng dòng; lệch dòng nào thì dừng ở dòng đó.

Chỉ dùng thư viện chuẩn, không phụ thuộc hệ điều hành, đầu ra tất định.

    python3 tool/ops/data_sanity.py
"""
import collections
import glob
import hashlib
import json
import os
import sys

CAPS = ('samReady', 'runtimeGuidedReady', 'answerCheckReady', 'misconceptionReady')


def capabilities(repo):
    """Đếm cờ năng lực trong fixture thật. Cờ nằm ở `provenance.capability`."""
    fs = sorted(glob.glob(os.path.join(repo, 'assets/fixtures/real/*.json')))
    c, has = collections.Counter(), 0
    for p in fs:
        with open(p, encoding='utf-8') as fh:
            d = json.load(fh)
        cap = (d.get('provenance') or {}).get('capability')
        if not cap:
            continue
        has += 1
        for k in CAPS:
            if cap.get(k) is True:
                c[k] += 1
    return len(fs), has, c


def pack(repo):
    """Đếm bản ghi trong pack.

    ĐẾM THEO VỊ TRÍ MẢNG, không theo khoá: khoá `(book, lesson)` từng gộp mất
    12 bài lớp 5 và làm báo sai mẫu số một lần rồi.
    """
    tot, keys, books = 0, set(), set()
    for p in sorted(glob.glob(os.path.join(repo, 'assets/pack/lesson-index-g*.json'))):
        with open(p, encoding='utf-8') as fh:
            d = json.load(fh)
        for _subj, bl in sorted(d['subjects'].items()):
            for b in bl:
                books.add(b['sourceDocumentId'])
                for L in b.get('lessons') or []:
                    tot += 1
                    keys.add((b['sourceDocumentId'], b.get('volume'), L.get('no')))
    return tot, len(keys), len(books)


def tree(repo, rel):
    """Số tệp + tổng byte của một nhánh. Bỏ qua nhánh không có."""
    root = os.path.join(repo, rel)
    if not os.path.isdir(root):
        return None
    n = b = 0
    for base, dirs, files in os.walk(root):
        dirs[:] = [d for d in dirs if d != '.git']
        for f in files:
            p = os.path.join(base, f)
            if os.path.isfile(p) and not os.path.islink(p):
                n += 1
                b += os.path.getsize(p)
    return n, b


def main():
    repo = sys.argv[1] if len(sys.argv) > 1 else '.'
    out = []
    nfix, has, c = capabilities(repo)
    out.append(f'fixture-real-files      {nfix}')
    out.append(f'fixture-with-capability {has}')
    for k in CAPS:
        out.append(f'{k:<23} {c[k]}')

    tot, dis, books = pack(repo)
    out.append(f'pack-records-by-position {tot}')
    out.append(f'pack-records-distinct    {dis}')
    out.append(f'pack-books               {books}')

    for rel in ('assets/pack', 'assets/fixtures', 'poc-out/graph',
                'poc-out/trusted-corpus', 'poc-out/pedagogy',
                'poc-out/units-k12', 'nguon-chi-thuc'):
        t = tree(repo, rel)
        out.append(f'{rel:<24} ' + ('THIẾU' if t is None else f'{t[0]} tệp {t[1]} byte'))

    body = '\n'.join(out)
    print(body)
    print('-' * 52)
    print('SANITY-DIGEST ' + hashlib.sha256(body.encode()).hexdigest()[:16])
    print('Hai máy phải in ra CÙNG digest. Lệch ⇒ dừng, so từng dòng ở trên.')


if __name__ == '__main__':
    main()
