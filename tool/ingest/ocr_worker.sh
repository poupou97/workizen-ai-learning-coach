#!/bin/bash
# K-12 OCR worker — đọc registry, OCR mọi doc PENDING trong dải lớp cho trước.
# Resume miễn phí: swift ocr_pdf cache theo source_hash từng trang.
# Dùng: ocr_worker.sh <grade_from> <grade_to>
set -u
FROM=$1; TO=$2
LOG=poc-out/registry/ocr-progress-g$FROM-$TO.log
python3 -c "
import json
r=json.load(open('poc-out/registry/source-registry.json'))['documents']
docs=[d for d in r if d['grade'] and $FROM<=d['grade']<=$TO and d['ocrState']!='DONE' and d['pageCount']]
docs.sort(key=lambda d:(d['grade'], 0 if d['docType']=='SGK' else 1, d['sourceDocumentId']))
for d in docs: print(d['sourceDocumentId'], d['path'], d['pageCount'])
" | while read -r stem path pages; do
  echo "[$(date +%H:%M:%S)] OCR $stem ($pages tr)" >> "$LOG"
  swift tool/ocr/ocr_pdf.swift "$path" 1 "$pages" "poc-out/graph/ocr-body/$stem" >> "$LOG" 2>&1
  echo "[$(date +%H:%M:%S)] DONE $stem rc=$?" >> "$LOG"
done
echo "WORKER g$FROM-$TO HOÀN TẤT" >> "$LOG"
