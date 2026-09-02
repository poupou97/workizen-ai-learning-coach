#!/bin/bash
# K-12 vòng XL cho MỌI doc đã có OCR — idempotent, resume tự nhiên (§XXVI).
set -u
cd "$(dirname "$0")/../.."
echo "=== [1/5] registry refresh ==="
python3 tool/ingest/build_registry.py | tail -3
echo "=== [2/5] structural-alt (NO_TOC) ==="
python3 tool/ingest/mine_structure_alt.py | tail -2
echo "=== [3/5] lesson titles ==="
python3 tool/ingest/mine_lesson_titles.py | head -1
echo "=== [4/5] generic units (mọi doc có OCR, trừ 6 sách gate Toán/TV cũ) ==="
ls poc-out/graph/ocr-body/ | grep -v -E "^(04-sgk-toan-4-tap-(mot|hai)|05-sgk-toan-5-tap-(mot|hai)|05-sgk-tieng-viet-5-tap-(mot|hai))$" \
  | xargs python3 tool/ingest/extract_units_generic.py > /tmp/k12-extract.log 2>&1
grep -c "→ {" /tmp/k12-extract.log | xargs echo "docs extracted:"
echo "=== [5/5] manifests các lớp có dữ liệu ==="
for g in 1 2 3 4 5 6 7 8 9 10 11 12; do
  python3 tool/ingest/make_manifest.py $g 2>/dev/null | python3 -c "
import json,sys
m=json.load(sys.stdin)
if m['unitsK12'] or m['ocr'].get('DONE'): print(m['batchId'], '·', m['ocr'], '· units:', m['unitsK12'], '· lessonsTitled:', m['lessonsTitled'], '/', m['lessons'])"
done
