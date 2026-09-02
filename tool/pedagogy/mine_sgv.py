#!/usr/bin/env python3
"""WAL-127 sgv-pedagogy-v1 — mine SGV thành pedagogy findings có provenance.

Nguyên tắc: KHÔNG bịa field khi sách không nói (§3). Mỗi finding gắn
sourceDocumentId + pdfPage + field + authority=SOURCE_EXPLICIT + extractionMethod.
Text chỉ giữ HEADLINE ≤140 ký tự trong poc-out (localResearchOnly — WAL-43).
"""
import json, os, re, sys, collections

VER = 'sgv-pedagogy-v1'

# Trường sư phạm (§3) — pattern dòng-đầu-mục. OCR noise: I/II/III có thể thành
# 'Ш', 'L', '|' (đã gặp ở sgv-muctieu-v1) ⇒ cho phép 0-4 ký tự rác đầu dòng.
J = r'^.{0,4}'
FIELDS = {
    'objective':       J + r'M[ỤU]C TI[ÊE]U\b',
    'requiredOutcome': J + r'YÊU C[ẦA]U C[ẦA]N Đ[ẠA]T\b',
    'preparation':     J + r'(CHU[ẨA]N B[ỊI]|ĐỒ DÙNG D[ẠA]Y H[ỌO]C)\b',
    'activityFlow':    J + r'(HO[ẠA]T Đ[ỘO]NG D[ẠA]Y H[ỌO]C|T[IỔ] CH[ỨU]C HO[ẠA]T Đ[ỘO]NG|TI[ẾE]N TRÌNH)\b',
    'assessment':      J + r'(ĐÁNH GIÁ|KI[ỂE]M TRA, ĐÁNH GIÁ)\b',
}
# Intent hoạt động (GDPT 2018) — dòng bắt đầu mục con trong HOẠT ĐỘNG.
INTENTS = {
    'ACTIVATE':  r'^\s*(\d+[.)]\s*)?(Ho[ạa]t đ[ộo]ng\s+)?[Kk]h[ởo]i đ[ộo]ng',
    'DISCOVER':  r'^\s*(\d+[.)]\s*)?(Ho[ạa]t đ[ộo]ng\s+)?([Kk]hám phá|[Hh]ình thành ki[ếe]n th[ứu]c)',
    'PRACTICE':  r'^\s*(Ti[ếe]t\s+\d+[.:]?\s*)?(\d+[.)]\s*)?(Ho[ạa]t đ[ộo]ng\s+)?[Ll]uy[ệe]n t[ậa]p',
    'APPLY':     r'^\s*(\d+[.)]\s*)?(Ho[ạa]t đ[ộo]ng\s+)?[Vv][ậa]n d[ụu]ng',
    'GAME':      r'^\s*(\d+[.)]\s*)?[Tt]rò ch[ơo]i',
    'CONSOLIDATE': r'^\s*(\d+[.)]\s*)?[Cc][ủu]ng c[ốo]',
    'REFLECT':   r'^\s*(\d+[.)]\s*)?([Nn]h[ìi]n l[ạa]i|[Ss]uy ng[ẫa]m|[Tt]ự đánh giá)',
}
# Đối tượng đặc biệt (không phải heading, quét theo DÒNG)
LINE_SIGNALS = {
    'misconceptionCandidate': r'(d[ễe]\s+(nh[ầa]m|sai|l[ẫa]n)|sai l[ầa]m|nh[ầa]m l[ẫa]n|HS có th[ểe]\s+\S{0,24}(nh[ầa]m|sai|lúng túng))',
    'teacherNote':            r'^\s*[-•*]?\s*L[ưu]u ý\b',
    'suggestedQuestion':      r'(GV có th[ểe] h[ỏo]i|câu h[ỏo]i g[ợo]i (ý|m[ởo])|đ[ặa]t câu h[ỏo]i)',
    'expectedResponse':       r'(D[ự]\s*ki[ếe]n|[Kk][ếe]t qu[ả] (là|:)|[Đđ]áp án)',
    'orgGroup':               r'(theo nhóm|nhóm \d|c[ặa]p đôi|làm vi[ệe]c nhóm)',
    'orgPair':                r'c[ặa]p đôi|theo c[ặa]p',
    'orgWholeClass':          r'c[ả] l[ớo]p',
    'orgIndividual':          r'(cá nhân|t[ự] làm|đ[ộo]c l[ậa]p)',
    'differentiation':        r'(HS khá, gi[ỏo]i|HS còn l[úu]ng t[úu]ng|tu[ỳy] (theo )?đ[ốo]i t[ượ]ng|phân hoá)',
    'perExerciseGuide':       r'^\s*Bài \d+\s*[:.]',
}
LESSON = re.compile(r'^\s*(BÀI|Bài)\s+(\d+)\b')

# ── EN adapter (sgv-pedagogy-en-v1) — khung Global Success PHÁT HIỆN TỪ DỮ LIỆU
# (không đoán trước): mỗi activity một block Goal/Input/Procedure/Outcome.
EN_LESSON = re.compile(r'^\s*LESSON\s+(\d+)\b')
EN_FIELDS = {
    'goal':        r'(?i)^\s*Goal:',
    'input':       r'(?i)^\s*Input:',
    'procedure':   r'(?i)^\s*Procedure:',
    'outcome':     r'(?i)^\s*Outcome:',
    'objective':   r'(?i)^\s*(objectives?|aims?)\b\s*:?\s*$|(?i)^\s*By the end of th',
    'audioScript': r'(?i)^\s*Audio script:',
    'pictureCues': r'(?i)^\s*-?\s*Picture cues:',
    'anticipated': r'(?i)anticipated (problem|difficult)|common (errors|mistakes)',
}
EN_INTENTS = {
    'ACTIVATE': r'^\s*Warm-up\b',
    'REVIEW':   r'^\s*Review\b|^\s*Fun corner\b',
}
EN_SKILL = [
    ('LISTENING', r'^\s*\d+\.\s*Listen\b'),
    ('READING',   r'^\s*\d+\.\s*Read\b'),
    ('SPEAKING',  r"^\s*\d+\.\s*(Let's talk|Say|Ask and answer|Point and say|Practise saying)"),
    ('WRITING',   r'^\s*\d+\.\s*(Write|Complete|Trace)\b'),
    ('SINGING',   r"^\s*\d+\.\s*(Let's sing|Sing|Chant)\b"),
    ('GAME',      r"^\s*\d+\.\s*(Play|Let's play|Game)\b"),
]

def mine_en(doc):
    did = doc['sourceDocumentId']
    base = f'poc-out/graph/ocr-body/{did}'
    if not os.path.isdir(base):
        return None
    findings = []
    lesson = None
    for fn in sorted(os.listdir(base)):
        if not fn.endswith('.json'):
            continue
        page = int(fn[1:4])
        try:
            d = json.load(open(f'{base}/{fn}'))
        except Exception:
            continue
        for l in d.get('lines', []):
            line = l['text']
            m = EN_LESSON.match(line)
            if m:
                lesson = int(m.group(1))
            for field, pat in EN_FIELDS.items():
                if re.match(pat, line):
                    findings.append(dict(field=field, page=page,
                                         headline=line.strip()[:140], lesson=lesson))
            for intent, pat in EN_INTENTS.items():
                if re.match(pat, line):
                    findings.append(dict(field='intent', intent=intent, page=page,
                                         headline=line.strip()[:140], lesson=lesson))
            for skill, pat in EN_SKILL:
                if re.match(pat, line):
                    findings.append(dict(field='skillActivity', skill=skill, page=page,
                                         headline=line.strip()[:140], lesson=lesson))
    for f in findings:
        f.update(sourceDocumentId=did, subject=doc['subject'], grade=doc['grade'],
                 authority='SOURCE_EXPLICIT', extractionMethod='sgv-pedagogy-en-v1')
    return findings

def mine(doc):
    did = doc['sourceDocumentId']
    base = f'poc-out/graph/ocr-body/{did}'
    if not os.path.isdir(base):
        return None
    findings = []
    lesson = None
    for fn in sorted(os.listdir(base)):
        if not fn.endswith('.json'):
            continue
        page = int(fn[1:4])
        try:
            d = json.load(open(f'{base}/{fn}'))
        except Exception:
            continue
        lines = [l['text'] for l in d.get('lines', [])]
        for i, line in enumerate(lines):
            m = LESSON.match(line)
            if m:
                # tiêu đề thường là dòng KẾ (in hoa) — như khung Toán 1 đã mổ
                nxt = lines[i+1].strip() if i+1 < len(lines) else ''
                lesson = {'no': int(m.group(2)),
                          'title': nxt[:80] if nxt and sum(c.isupper() for c in nxt if c.isalpha()) > len([c for c in nxt if c.isalpha()])*0.6 else None,
                          'page': page}
            for field, pat in FIELDS.items():
                if re.match(pat, line):
                    findings.append(dict(field=field, page=page, headline=line.strip()[:140],
                                         lesson=lesson and lesson['no']))
            for intent, pat in INTENTS.items():
                if re.match(pat, line):
                    findings.append(dict(field='intent', intent=intent, page=page,
                                         headline=line.strip()[:140], lesson=lesson and lesson['no']))
            for sig, pat in LINE_SIGNALS.items():
                if re.search(pat, line):
                    findings.append(dict(field=sig, page=page, headline=line.strip()[:140],
                                         lesson=lesson and lesson['no']))
    for f in findings:
        f.update(sourceDocumentId=did, subject=doc['subject'], grade=doc['grade'],
                 authority='SOURCE_EXPLICIT', extractionMethod=VER)
    return findings

def main():
    reg = json.load(open('poc-out/registry/source-registry.json'))['documents']
    by_id = {d['sourceDocumentId']: d for d in reg}
    ids = json.load(open('poc-out/pedagogy-sample-ids.json'))
    summary = {}
    for did in ids:
        doc = by_id[did]
        is_en = 'tiếng anh' in doc['subject'].lower() or 'tieng-anh' in did
        fs = mine_en(doc) if is_en else mine(doc)
        if fs is None:
            summary[did] = 'NO_OCR'
            continue
        json.dump(fs, open(f'poc-out/pedagogy/findings/{did}.json', 'w'), ensure_ascii=False)
        c = collections.Counter(f['field'] for f in fs)
        ic = collections.Counter(f.get('intent') for f in fs if f['field'] == 'intent')
        summary[did] = {'total': len(fs), 'fields': dict(c), 'intents': dict(ic)}
    json.dump(summary, open('poc-out/pedagogy/mining-summary.json', 'w'), ensure_ascii=False, indent=1)
    for did, s in summary.items():
        if isinstance(s, str):
            print(f'{did}: {s}'); continue
        top = ' '.join(f"{k}:{v}" for k, v in sorted(s['fields'].items(), key=lambda x: -x[1])[:7])
        print(f"{did} [{s['total']}] {top}")
        if s['intents']:
            print('   intents:', dict(sorted(s['intents'].items(), key=lambda x: -x[1])))

if __name__ == '__main__':
    main()
