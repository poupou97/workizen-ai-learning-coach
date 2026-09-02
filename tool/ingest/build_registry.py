"""K-12 MASTER §IV — SOURCE REGISTRY: inventory toàn corpus, không đoán.

Metadata tất định từ filename-scheme thật (NN-loai-mon-...-tap-X.pdf) +
pypdf pageCount + checksum (sha1 4MB đầu + size — scheme ghi rõ) + trạng
thái OCR/parse từ artifacts hiện có. Không match scheme ⇒ UNKNOWN.
Registry là STATE resumability (§XXVI): mọi stage sau đọc/ghi vào đây.
"""
import hashlib, json, os, re, glob

SUBJECTS = {
    'toan': 'Toán', 'tieng-viet': 'Tiếng Việt', 'ngu-van': 'Ngữ văn',
    'khoa-hoc-tu-nhien': 'KHTN', 'khoa-hoc': 'Khoa học',
    'lich-su-va-dia-li': 'LS&ĐL', 'lich-su': 'Lịch sử', 'dia-li': 'Địa lí',
    'vat-li': 'Vật lí', 'hoa-hoc': 'Hoá học', 'sinh-hoc': 'Sinh học',
    'tin-hoc': 'Tin học', 'cong-nghe': 'Công nghệ', 'dao-duc': 'Đạo đức',
    'giao-duc-cong-dan': 'GDCD', 'giao-duc-kinh-te-va-phap-luat': 'GDKT&PL',
    'giao-duc-quoc-phong-va-an-ninh': 'GDQP', 'giao-duc-the-chat': 'GDTC',
    'am-nhac': 'Âm nhạc', 'mi-thuat': 'Mĩ thuật',
    'hoat-dong-trai-nghiem-huong-nghiep': 'HĐTN-HN',
    'hoat-dong-trai-nghiem': 'HĐTN', 'tu-nhien-va-xa-hoi': 'TN&XH',
    'tieng-anh': 'Tiếng Anh', 'tieng-phap': 'Tiếng Pháp',
    'tieng-han': 'Tiếng Hàn', 'tieng-nhat': 'Tiếng Nhật',
    'tieng-trung-quoc': 'Tiếng Trung', 'tieng-nga': 'Tiếng Nga',
    'tieng-duc': 'Tiếng Đức',
    'toan-chuyen-de': 'Toán CĐ', 'chuyen-de': 'Chuyên đề',
}
NAME = re.compile(r'^(\d{2})-(sgk|sgv|shs|sbt|bt|vbt)-?(.+?)(?:-(\d{1,2}))?'
                  r'(?:-tap-(mot|hai|ba|1|2|3))?$')

def parse_name(stem):
    m = NAME.match(stem)
    if not m:
        m2 = re.match(r'^(\d{2})-(.+?)(?:-tap-(mot|hai|ba|1|2|3))?$', stem)
        if not m2:
            return None
        grade, rest, vol = m2.groups()
        subject = next((v for k, v in sorted(SUBJECTS.items(),
                        key=lambda x: -len(x[0])) if k in rest), 'UNKNOWN')
        return {'grade': int(grade), 'docType': 'UNKNOWN',
                'subject': subject,
                'volume': {'mot': 1, '1': 1, 'hai': 2, '2': 2, 'ba': 3,
                           '3': 3}.get(vol) if vol else None,
                'nameExtra': None}
    grade, dtype, rest, gnum, vol = m.groups()
    subject = None
    for k in sorted(SUBJECTS, key=len, reverse=True):
        if rest == k or rest.startswith(k + '-') or rest.endswith('-' + k) \
           or k in rest:
            subject = SUBJECTS[k]
            rest_extra = rest.replace(k, '').strip('-')
            break
    else:
        rest_extra = rest
    return {'grade': int(grade), 'docType': {'sgk': 'SGK', 'sgv': 'SGV', 'shs': 'SGK',
            'sbt': 'WORKBOOK', 'bt': 'WORKBOOK', 'vbt': 'WORKBOOK'}[dtype],
            'subject': subject or 'UNKNOWN',
            'volume': {'mot': 1, '1': 1, 'hai': 2, '2': 2, 'ba': 3, '3': 3
                       }.get(vol) if vol else None,
            'nameExtra': rest_extra or None}

def checksum(path):
    h = hashlib.sha1()
    with open(path, 'rb') as f:
        h.update(f.read(4 * 1024 * 1024))
    return f'sha1_4mb:{h.hexdigest()[:16]}:size:{os.path.getsize(path)}'

def page_count(path):
    try:
        import pypdf
        return len(pypdf.PdfReader(path).pages)
    except Exception:
        return None

scan = {b['id']: b for b in
        json.load(open('poc-out/graph/structure-scan.json'))['books']}
UNITS_DONE = {os.path.basename(f)[:-5] for f in glob.glob('poc-out/units/*.json')
              if 'sgk' in f and 'objectives' not in f}
OBJ_DONE = {os.path.basename(f).replace('.objectives.json', '')
            for f in glob.glob('poc-out/units/*.objectives.json')}

reg = []
pdfs = sorted(glob.glob('poc-out/pdf/**/*.pdf', recursive=True))
for p in pdfs:
    stem = os.path.basename(p)[:-4]
    meta = parse_name(stem) or {}
    pc = page_count(p)
    ocr_dir = f'poc-out/graph/ocr-body/{stem}'
    ocr_pages = len(os.listdir(ocr_dir)) if os.path.isdir(ocr_dir) else 0
    sb = scan.get(stem)
    lessons = len([l for l in (sb or {}).get('lessonTitles', [])
                   if l.get('n') is not None]) if sb else None
    ocr_state = ('DONE' if pc and ocr_pages >= pc - 2 else
                 'PARTIAL' if ocr_pages else 'PENDING')
    reg.append({
        'sourceDocumentId': stem,
        'path': p,
        'grade': meta.get('grade'),
        'subject': meta.get('subject', 'UNKNOWN'),
        'docType': meta.get('docType', 'UNKNOWN'),
        'volume': meta.get('volume'),
        'nameExtra': meta.get('nameExtra'),
        'publisher': 'UNKNOWN',       # filename không chứng minh — không đoán
        'editionYear': 'UNKNOWN',
        'pageCount': pc,
        'fileSize': os.path.getsize(p),
        'checksum': checksum(p),
        'structureScan': 'DONE' if sb else 'MISSING',
        'lessonTitles': lessons,
        'ocrState': ocr_state,
        'ocrPages': ocr_pages,
        'unitsExtracted': stem in UNITS_DONE,
        'objectivesExtracted': stem in OBJ_DONE,
        'legal': 'localResearchOnly',
    })

json.dump({'schemaVersion': 'registry-v1', 'documents': reg},
          open('poc-out/registry/source-registry.json', 'w'),
          ensure_ascii=False, indent=1)

from collections import Counter
print(f'registry: {len(reg)} documents')
print('docType:', dict(Counter(r["docType"] for r in reg)))
print('subject UNKNOWN:', sum(1 for r in reg if r['subject'] == 'UNKNOWN'))
unk = [r['sourceDocumentId'] for r in reg if r['subject'] == 'UNKNOWN'][:10]
print('  vd:', unk)
print('grade None:', sum(1 for r in reg if r['grade'] is None))
print('structureScan MISSING:', sum(1 for r in reg if r['structureScan'] == 'MISSING'))
print('ocr:', dict(Counter(r['ocrState'] for r in reg)))
print('pages tổng:', sum(r['pageCount'] or 0 for r in reg))
