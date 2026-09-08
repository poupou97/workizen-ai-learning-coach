#!/usr/bin/env python3
"""B3 — KIỂM ĐẾM TOÀN CORPUS, đúng các trường Founder yêu cầu ở cổng B3.

    python3 tool/corpus/docling_census.py

⚠ KHÔNG dùng SỐ ĐỀ XUẤT THÔ làm độ phủ sản phẩm. Đề xuất là thứ model nói;
độ phủ là thứ trẻ thật sự mở ra thấy. Hai con số khác mẫu số, không được gộp.
"""
import collections
import glob
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
DL = os.path.join(ROOT, 'poc-out', 'docling')


def band(g):
    return '1-3' if g <= 3 else ('4-8' if g <= 8 else '9-12')


def main():
    grade = {}
    reg = json.load(open(os.path.join(ROOT, 'poc-out', 'registry',
                                      'source-registry.json'), encoding='utf-8'))
    for d in (reg['documents'] if isinstance(reg, dict) else reg):
        grade[d['sourceDocumentId']] = d.get('grade') or 0

    # ── tri giác thô ────────────────────────────────────────────────
    pages, errs, labels = 0, 0, collections.Counter()
    for fn in glob.glob(os.path.join(DL, 'proposals-w*.jsonl')):
        with open(fn, encoding='utf-8') as fh:
            for line in fh:
                try:
                    d = json.loads(line)
                except ValueError:
                    continue
                pages += 1
                errs += bool(d.get('error'))
                for it in d.get('items') or []:
                    labels[it['label']] += 1

    # ── sau cổng ────────────────────────────────────────────────────
    c = collections.Counter()
    subfig = collections.Counter()
    tp = os.path.join(DL, 'trusted.jsonl')
    if os.path.exists(tp):
        with open(tp, encoding='utf-8') as fh:
            for line in fh:
                r = json.loads(line)
                b = band(r.get('grade') or 0)
                c['DE_XUAT'] += 1
                c['REGION_' + r['region_trust']] += 1
                c[f'BAND_{b}_DE_XUAT'] += 1
                if r['region_trust'] != 'TRUSTED':
                    continue
                c['IDENTITY_' + r['identity']] += 1
                c[f'BAND_{b}_TRUSTED'] += 1
                c[('TABLE' if r['kind'] == 'table' else 'FIGURE') + '_TRUSTED'] += 1
                if r['readable']:
                    c['VAO_DONG_DOC'] += 1
                    c[f'BAND_{b}_DOC_DUOC'] += 1
                if r.get('shared', 0) > 1:
                    subfig['CUM_HINH_CON'] += 1
                    subfig['NOI_DUOC_NHAN_CON' if r['identity'] == 'RESOLVED'
                           else 'GIU_LAI_DANH_TINH'] += 1

    # ── cầu nối di trú, lấy từ manifest lúc dựng ────────────────────
    bridge = collections.Counter()
    for fn in sorted(glob.glob(os.path.join(ROOT, 'poc-out', 'packs', 'figures',
                                            'figures-g*.manifest.json'))):
        m = json.load(open(fn, encoding='utf-8'))
        for k, v in (m.get('bridge') or {}).items():
            bridge[k] += v

    out = dict(
        TRANG_DA_CHAY=pages, TRANG_LOI=errs,
        DE_XUAT_HINH_BANG=c['DE_XUAT'],
        REGION_TRUSTED=c['REGION_TRUSTED'], REGION_WITHHELD=c['REGION_WITHHELD'],
        REGION_CONFLICT=c['REGION_CONFLICT'],
        IDENTITY_RESOLVED=c['IDENTITY_RESOLVED'],
        IDENTITY_WITHHELD=c['IDENTITY_WITHHELD'],
        VAO_DONG_DOC=c['VAO_DONG_DOC'],
        FIGURE_TRUSTED=c['FIGURE_TRUSTED'], TABLE_TRUSTED=c['TABLE_TRUSTED'],
        SUBFIGURE=dict(subfig),
        THEO_DAI_LOP={b: dict(de_xuat=c[f'BAND_{b}_DE_XUAT'],
                              trusted=c[f'BAND_{b}_TRUSTED'],
                              doc_duoc=c[f'BAND_{b}_DOC_DUOC'])
                      for b in ('1-3', '4-8', '9-12')},
        CAU_NOI=dict(CHI_D=bridge['CHI_D'], MOI=bridge['MOI'], CA_HAI=bridge['CA_HAI']),
        FORMULA=labels.get('formula', 0), CODE=labels.get('code', 0),
        NHAN_THO=dict(labels.most_common()),
    )
    print(json.dumps(out, ensure_ascii=False, indent=1))
    return 0


if __name__ == '__main__':
    sys.exit(main())
