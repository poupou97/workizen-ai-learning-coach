#!/usr/bin/env python3
"""WAL-149 KS-B verify-v1 — gán review state cho candidates (§28) với 3 guard
rút từ vòng chấm tay KS-A. PRECISION>RECALL: nghi ngờ ⇒ REVIEW_REQUIRED,
không bao giờ tự lên VERIFIED (VERIFIED chỉ qua curation list — người chấm).

States: CANDIDATE → AUTO_VERIFIED | REVIEW_REQUIRED | REJECTED.
"""
import json, re, collections, unicodedata

VER = 'verify-v1'

SPEECH_VERBS = re.compile(
    r'(nói|viết|tuyên bố|căn dặn|khẳng định|trả lời|nhận xét|tổng kết|'
    r'kể|hỏi|dạy|khuyên|phát biểu|nhấn mạnh|chỉ rõ)\b')
BOOKISH = re.compile(r'(kí|ký|truyện|sử|tập|toàn thư|sách|báo|tạp chí)\b', re.I)
MODAL = re.compile(r'(có thể|sẽ|cần|nên|muốn)\s*$')
EVENT_VERB = re.compile(
    r'(thành lập|ra đời|sinh|mất|qua đời|khởi nghĩa|xuất bản|hoàn thành|'
    r'chế tạo|phát minh|tìm ra|phát hiện|đọc bản|tuyên|ký|chiếm|đánh|'
    r'lên ngôi|dời đô|mở khoa thi|thám hiểm|đặt chân|phóng)')
STATSY = re.compile(r'(xếp thứ|tỉ lệ|thống kê|%|số liệu|dân số)')
PLACE_PREFIX = re.compile(
    r'^(Hy Lạp|Việt Nam|nước|Liên Xô|Trung Quốc|Ấn Độ|Nhật Bản|Pháp|Anh|Đức|Nga|Mỹ)\s+')
FICTION_SUBJECTS = {'Ngữ văn', 'Tiếng Việt'}

def slug(name):
    n = unicodedata.normalize('NFC', name.strip())
    return 'p:' + re.sub(r'[\s\-]+', '-', n.casefold())

def verify(i):
    t, src, ev = i['type'], i['source'], i['source']['textEvidence']
    reasons = []
    if t == 'PERSON':
        name = PLACE_PREFIX.sub('', i.get('name', '')).strip()
        i['name'] = name
        if len(name) < 3:
            return 'REJECTED', ['tên rỗng sau trim']
        if i.get('birthYear'):
            return 'AUTO_VERIFIED', ['anchor năm sinh-mất']
        if len(name.split()) >= 2:
            return 'AUTO_VERIFIED', ['role-intro + tên đầy đủ']
        if i.get('role'):
            # tên nước ngoài một từ (Aristotle, Cantor…) + role rõ ⇒ đủ neo
            return 'AUTO_VERIFIED', ['role-intro + tên riêng một từ']
        return 'REVIEW_REQUIRED', ['tên một từ không role — dễ nhầm']
    if t == 'QUOTE':
        person = i.get('person', '')
        if BOOKISH.search(person):
            i['type'] = 'SOURCE_EXCERPT'
            return 'AUTO_VERIFIED', ['attribution là TÊN SÁCH → hạ thành trích văn bản']
        before_quote = ev.split('"')[0] if '"' in ev else ev[:60]
        has_verb = bool(SPEECH_VERBS.search(before_quote))
        mentioned_before = person.split()[-1] in before_quote if person else False
        if has_verb and mentioned_before:
            return 'AUTO_VERIFIED', ['động-từ-nói trước quote + người được nhắc trước']
        # ca Ga-li-lê: «(Tên)» sau quote có thể là tác giả sách trích
        return 'REVIEW_REQUIRED', [
            'attribution chỉ từ (Tên) sau quote — nguy cơ dịch-giả/tác-giả-sách']
    if t == 'EVENT':
        y = i.get('year') or 0
        if y > 2010 and STATSY.search(ev):
            return 'REJECTED', ['số liệu thống kê hiện đại, không phải sự kiện đáng nhớ']
        if not EVENT_VERB.search(ev):
            return 'REVIEW_REQUIRED', ['thiếu động-từ-sự-kiện trong evidence']
        i['todayEligible'] = bool(i.get('monthDay'))
        return 'AUTO_VERIFIED', ['năm + động-từ-sự-kiện']
    if t == 'INVENTION_DISCOVERY':
        ctx_before = ev[:ev.find(i.get('verb', '')) if i.get('verb') else 40]
        if MODAL.search(ctx_before.strip()):
            return 'REJECTED', ['modal khả-năng, không phải sự kiện khám phá']
        if src['subject'] in FICTION_SUBJECTS and not re.search(
                r'nhà (khoa học|bác học|văn|thơ)|\(\d{4}', ev):
            return 'REVIEW_REQUIRED', ['môn văn-cảnh-truyện, không marker người-thật']
        if i.get('person') or re.search(r'\b1\d{3}\b', ev):
            return 'AUTO_VERIFIED', ['có người/năm gắn khám phá']
        return 'REVIEW_REQUIRED', ['thiếu người và năm']
    if t == 'SOURCE_EXCERPT':
        return 'AUTO_VERIFIED', ['trích văn bản có nguồn']
    return 'REVIEW_REQUIRED', ['loại chưa có rule']

def main():
    items = json.load(open('poc-out/stories/candidates-v0.json'))
    persons = collections.defaultdict(list)
    for i in items:
        st, why = verify(i)
        i['status'], i['verifyReasons'], i['verifyVersion'] = st, why, VER
        if i['type'] == 'PERSON' and st != 'REJECTED':
            persons[slug(i['name'])].append(i)
    # entity resolution v0: một canonical person ← nhiều sourceRefs
    canon = {}
    for pid, group in persons.items():
        canon[pid] = dict(
            personId=pid,
            canonicalName=max((g['name'] for g in group), key=len),
            birthYear=next((g.get('birthYear') for g in group if g.get('birthYear')), None),
            deathYear=next((g.get('deathYear') for g in group if g.get('deathYear')), None),
            subjects=sorted({g['source']['subject'] for g in group}),
            sourceRefs=[g['source'] for g in group],
            status='AUTO_VERIFIED',
        )
        for g in group:
            g['personId'] = pid
    json.dump(items, open('poc-out/stories/curated-v0.json', 'w'),
              ensure_ascii=False, indent=1)
    json.dump(list(canon.values()), open('poc-out/stories/persons-v0.json', 'w'),
              ensure_ascii=False, indent=1)
    st = collections.Counter((i['type'], i['status']) for i in items)
    by_status = collections.Counter(i['status'] for i in items)
    print('trạng thái:', dict(by_status))
    for (t, s), n in sorted(st.items()):
        print(f'  {t:20} {s:16} {n}')
    multi = [p for p in canon.values() if len(p['subjects']) > 1]
    print(f'persons: {len(canon)} canonical (từ {sum(len(v) for v in persons.values())} mentions); đa-môn: {len(multi)}')
    for p in multi[:5]:
        print('  đa-môn:', p['canonicalName'], p['subjects'])
    today = [i for i in items if i.get('todayEligible')]
    print(f'todayEligible (có monthDay + verb): {len(today)}')

if __name__ == '__main__':
    main()
