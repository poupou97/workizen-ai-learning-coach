"""WAL-111 §4 — CORPUS ANALYSIS TRƯỚC UX: «SGK thực sự yêu cầu HS làm gì?»

Thống kê trên snapshot K12 (126.5k units): role theo lớp/môn, động-từ-hành-động
mở đầu EXERCISE/ACTIVITY theo band, mật độ text theo band. Số nuôi FILE 1+2.
"""
import json, glob, re, unicodedata
from collections import Counter, defaultdict

def strip(s):
    s = unicodedata.normalize('NFD', s.lower().replace('đ','d'))
    return ''.join(c for c in s if not unicodedata.combining(c))

# động từ hành động GDPT (đã strip) — mining trên câu lệnh bài tập
VERBS = ['chon','noi','dien','tinh','viet','doc','ke','quan sat','ve','tim',
         'so sanh','sap xep','phan loai','giai','chung minh','thuc hanh',
         'do','lap bang','ghep','dat cau','tra loi','neu','trinh bay',
         'thao luan','dong vai','hat','nghe','noi va nghe','danh gia',
         'nhan xet','giai thich','du doan','thi nghiem','lap','xac dinh',
         'hoan thanh','gach','khoanh','to mau','cat dan','suu tam','van dung']

BAND = lambda g: '1-2' if g<=2 else '3-5' if g<=5 else '6-9' if g<=9 else '10-12'
reg = {d['sourceDocumentId']: d for d in
       json.load(open('poc-out/registry/source-registry.json'))['documents']}

role_by_band = defaultdict(Counter)
role_by_subj = defaultdict(Counter)
verb_by_band = defaultdict(Counter)
len_by_band = defaultdict(list)
units_by_subj = Counter()
for f in glob.glob('poc-out/units-k12/*.json'):
    j = json.load(open(f))
    d = reg.get(j['sourceDocumentId'], {})
    g = d.get('grade') or 0
    subj = j.get('subject') or 'UNKNOWN'
    b = BAND(g)
    for u in j['units']:
        role_by_band[b][u['role']] += 1
        role_by_subj[subj][u['role']] += 1
        units_by_subj[subj] += 1
        len_by_band[b].append(len(u['text']))
        if u['role'] in ('EXERCISE','ACTIVITY'):
            st = strip(u['text'])
            st = re.sub(r'^(khoi dong|kham pha|luyen tap|van dung|thuc hanh|hoat dong)\s*','',st)
            st = re.sub(r'^\d{1,2}\s*[.．]?\s*','',st)
            for v in VERBS:
                if st.startswith(v):
                    verb_by_band[b][v] += 1
                    break

print('== ROLE theo BAND ==')
for b in ('1-2','3-5','6-9','10-12'):
    total = sum(role_by_band[b].values())
    avg = sum(len_by_band[b])/len(len_by_band[b]) if len_by_band[b] else 0
    print(f'{b}: {total:,} units · độ dài TB {avg:.0f} ký tự ·',
          dict(role_by_band[b].most_common(6)))
print('\n== TOP ĐỘNG TỪ HÀNH ĐỘNG theo BAND (EXERCISE+ACTIVITY) ==')
for b in ('1-2','3-5','6-9','10-12'):
    tot = sum(verb_by_band[b].values())
    top = ', '.join(f'{v}:{c}' for v,c in verb_by_band[b].most_common(12))
    print(f'{b} ({tot:,} matched): {top}')
print('\n== UNITS theo MÔN (top 15) ==')
for s,c in units_by_subj.most_common(15): print(f'  {s}: {c:,}')
print('\n== ROLE đặc thù môn (EXPERIMENT/OBSERVATION/READING/SOURCE_TEXT) ==')
for s, rc in sorted(role_by_subj.items()):
    special = {k:v for k,v in rc.items() if k in ('EXPERIMENT','OBSERVATION','READING','SOURCE_TEXT','EXAMPLE','RULE_CANDIDATE','NOTE') and v>5}
    if special: print(f'  {s}: {special}')
