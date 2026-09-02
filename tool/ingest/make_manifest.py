"""K-12 §XXV — BatchManifest per grade: máy đọc được, resume không cần memory."""
import json, os, sys, glob
from collections import Counter

grade = int(sys.argv[1])
reg = [d for d in json.load(open('poc-out/registry/source-registry.json'))
       ['documents'] if d['grade'] == grade and d['ocrState'] != 'DUPLICATE']
struct = {d['sourceDocumentId']: d for d in json.load(
    open('poc-out/graph/curriculum-structure.json'))['documents']}
m = {'batchId': f'grade-{grade:02d}', 'documents': len(reg),
     'ocr': dict(Counter(d['ocrState'] for d in reg)),
     'pages': sum(d['pageCount'] or 0 for d in reg),
     'lessons': sum(struct.get(d['sourceDocumentId'], {}).get('lessonCount', 0)
                    for d in reg),
     'lessonsTitled': sum(1 for d in reg for l in
                          struct.get(d['sourceDocumentId'], {}).get('lessons', [])
                          if l.get('title')),
     'unitsK12': 0, 'roleDist': {}, 'anomalies': []}
roles = Counter()
for d in reg:
    p = f"poc-out/units-k12/{d['sourceDocumentId']}.json"
    if os.path.exists(p):
        j = json.load(open(p))
        m['unitsK12'] += len(j['units'])
        roles.update(u['role'] for u in j['units'])
        if not j['offsetCalibrated'] and j['units']:
            m['anomalies'].append(f"{d['sourceDocumentId']}: offset UNCALIBRATED")
m['roleDist'] = dict(roles)
os.makedirs('poc-out/registry/manifests', exist_ok=True)
json.dump(m, open(f'poc-out/registry/manifests/grade-{grade:02d}.json', 'w'),
          ensure_ascii=False, indent=1)
print(json.dumps(m, ensure_ascii=False))
