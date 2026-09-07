#!/usr/bin/env python3
"""WAL-148 KS-A stories-v0 — candidate extractor đa-môn, SOURCE-BOUND (§6).

Mọi item = CANDIDATE (chưa phải curated fact). PRECISION>RECALL: pattern hẹp,
confidence từ chất-lượng-OCR (tỉ lệ dấu tiếng Việt hợp lệ), noise bìa/nghị
định bị loại. KHÔNG LLM. Output: poc-out/stories/candidates-v0.json.
"""
import json, os, re, sys, collections, unicodedata

VER = 'stories-v0.1'
SAMPLE = [
 '06-sgk-ngu-van-6-tap-mot','10-sgk-ngu-van-10-tap-hai','03-sgk-tieng-viet-3-tap-mot',
 '10-sgk-lich-su-10','04-sgk-lich-su-va-dia-li-4','07-sgk-lich-su-va-dia-li-7',
 '04-sgk-khoa-hoc-4','06-sgk-khoa-hoc-tu-nhien-6','10-sgk-vat-li-10','10-sgk-hoa-hoc-10',
 '10-sgk-sinh-hoc-10','06-sgk-toan-6-tap-mot','10-sgk-tin-hoc-10','06-sgk-cong-nghe-6',
 '04-sgk-dao-duc-4','06-sgk-giao-duc-cong-dan-6','06-sgk-am-nhac-6','06-sgk-mi-thuat-6',
]

NOISE = re.compile(r'NĐ-CP|QĐ-BGDĐT|QĐ-TTg|Bản quyền|NHÀ XUẤT BẢN|ISBN|Tái bản|Chủ biên|Hội đồng|thẩm định', re.I)
NAME = r"[A-ZĐ][a-zà-ỹ]+(?:[\s\-][A-ZĐa-zà-ỹ][a-zà-ỹ\-]*){0,4}"
P_BIRTH = re.compile(r'(' + NAME + r')\s*\(\s*(\d{3,4})\s*[–\-]\s*(\d{3,4})\s*\)')
# v0.1: (năm–năm) sau TRIỀU ĐẠI/SỰ KIỆN không phải năm sinh-mất
# ⭐ Bốn cách một THỨ bị nhận nhầm thành một NGƯỜI — đo được trên corpus thật,
# không phải phòng xa. Mỗi cái sửa hẹp đúng chỗ nó sinh ra:
#
#   «Tượng Hoàng đế Sác-lơ-ma-nhơ (742–814)»  ← chú thích ảnh: BỨC TƯỢNG
#   «Xuân Phái Bùi Xuân Phái (1920–1988)»     ← OCR dính caption vào thân bài
#   «nhà văn Đan Mạch»                        ← QUỐC TỊCH đi sau vai
#   «ở Thăng Long (1527–1592)»                ← ĐỊA DANH đứng trước khoảng năm
#
# Hai cái đầu ĐANG tới tay trẻ (nằm trong 21 người của pack); hai cái sau thì
# chưa, nhưng cùng một họ nên sửa luôn.

# Danh từ chỉ VẬT MÔ TẢ người — bức tượng không phải con người.
DEPICTION = re.compile(r'^(Tượng|Chân dung|Bức tranh|Bức ảnh|Hình|Ảnh|Tranh)\s+')

# Quốc gia/quốc tịch hay đi ngay sau «nhà văn/nhạc sĩ…» trong SGK.
COUNTRYISH = re.compile(
    r'^(Đan Mạch|Thuỵ Điển|Thụy Điển|Thuỵ Sĩ|Na Uy|Phần Lan|Hà Lan|Bồ Đào Nha|'
    r'Tây Ban Nha|Hy Lạp|Ấn Độ|Trung Quốc|Nhật Bản|Hàn Quốc|Triều Tiên|'
    r'Việt Nam|Cam-pu-chia|Cô-oét|In-đô-nê-xi-a|Ma-lai-xi-a|Xin-ga-po|'
    r'Thái Lan|Mi-an-ma|Lào|Nga|Anh|Pháp|Đức|Ý|I-ta-li-a|Mỹ|Hoa Kỳ|Áo|Ba Lan)$')

# Giới từ chỉ NƠI CHỐN ngay trước tên ⇒ tên ấy là địa danh, không phải người.
LOCATIVE = re.compile(r'(?:^|\s)(ở|tại|vùng|kinh đô|thành phố|nước|xứ|đất)\s*$')


# Câu dẫn có động từ nói + dấu hai chấm ⇒ người nói nằm TRONG CÂU, không nằm
# trong ngoặc dẫn nguồn phía sau.
SPEECH_LEAD = re.compile(
    r'\b(tuyên bố|nói|viết|khẳng định|phát biểu|căn dặn|dạy|kể|đáp|trả lời)'
    r'\s*:\s*$')

# «Tên khác, Tác phẩm, NXB…» ⇒ trong ngoặc là DANH SÁCH BIÊN SOẠN.
COMPILER_LIST = re.compile(r'^\s*[A-ZĐ][^,]{2,40},\s*[^,]{2,60},')


def clean_name(name):
    """Gỡ hai kiểu bẩn của tên do OCR/chú thích sinh ra.

    1. Danh từ chỉ vật mô tả ở đầu («Tượng Hoàng đế X» → «Hoàng đế X»).
    2. Tiền tố lặp lại đúng bằng hậu tố — OCR dính chú thích ảnh vào thân bài
       nên tên chạy hai lần: «Bùi Xuân Phái Bùi Xuân Phái», và bản bắt lệch
       «Xuân Phái Bùi Xuân Phái». Cả hai đều có prefix == suffix, bỏ prefix là
       còn đúng tên.
    """
    name = DEPICTION.sub('', name).strip()
    t = name.split()
    # ⚠ Đòi khối lặp ÍT NHẤT 2 từ. Một âm tiết trùng là tín hiệu quá yếu: bản
    # vá đầu của tôi cắt «Nguyễn Văn Nguyễn» thành «Văn Nguyễn» — một cái tên
    # Việt hoàn toàn bình thường. Test bắt được.
    for k in range(len(t) // 2, 1, -1):
        if t[:k] == t[-k:] and len(t) > k:
            return ' '.join(t[k:])
    return name


DYNASTY = re.compile(r'^(Nguyên|Đinh|Lý|Trần|Trân|Minh|Thanh|Tống|Đường|Hán|Tuỳ|Tùy|Ngô|Lê|Nguyễn|Hồ|Mạc|Mỹ|Anh|Pháp|Đức|Nga|Nhật)$')
EVENTISH = re.compile(r'(Khởi nghĩa|Chiến tranh|Kháng chiến|Cách mạng|thời kì|Thời kì|triều|Triều|nhà)\b')
# v0.1: tên bị nuốt động từ — cắt tại từ thường tiếng Việt đi sau tên
VERB_TAIL = re.compile(r'\s+(đã|không|mà|là|được|và|khi|sau|trước|cùng|vẫn|chuyên|từng|nói|viết|sáng tác|đặt)\b.*$')
P_INTRO = re.compile(r'(nhà (?:thơ|văn|bác học|khoa học|toán học|vật lí|hoá học|sử học|giáo dục|soạn nhạc)|nhạc sĩ|hoạ sĩ|họa sĩ|danh nhân|anh hùng)\s+(' + NAME + r')')
P_QUOTE = re.compile(r'"([^"]{15,220})"\s*[\.\s]*\(\s*(' + NAME + r')(?:\s*,\s*([^)]{3,80}))?\)')
P_EVENT = re.compile(r'([Nn]ăm\s+(\d{3,4})|[Nn]gày\s+(\d{1,2})[\-/](\d{1,2})[\-/](\d{4})|[Nn]gày\s+(\d{1,2})\s+tháng\s+(\d{1,2})\s+năm\s+(\d{4}))[\s,:]([^.]{15,180}\.)')
P_INV = re.compile(r'(' + NAME + r')?[^.]{0,60}(phát minh ra|sáng chế ra|tìm ra|khám phá ra|phát hiện ra)\s+([^.]{5,120}\.)')

# ⭐⭐ WAL-194 — CẮT THEO SỐ KÝ TỰ THÌ RƠI VÀO GIỮA TỪ.
#
# Cửa sổ bằng chứng cắt bằng offset ký tự cố định (`m.start()-60`, `m.end()+120`)
# rơi vào giữa từ bất cứ khi nào nó rơi vào giữa từ. Đó là lý do phần bị mất dài
# ngắn khác nhau (1–3 ký tự) chứ không phải một off-by-N cố định.
#
# Hậu quả không nhỏ: màn chuyện dán nhãn khối này là «TRÍCH NGUYÊN VĂN TỪ
# NGUỒN». Một mảnh cụt đầu cụt đuôi thì KHÔNG phải nguyên văn.
# Đo trên pack hiện tại: 8/38 cụt đầu, 15/38 cụt đuôi.
_WORDCH = re.compile(r'[^\W_]', re.UNICODE)


_SENT_END = re.compile(r'[.!?…]["»\')\]]?')


def snap_sentence(text, start, end, grow=220):
    """Nới cửa sổ tới RANH GIỚI CÂU, trong giới hạn `grow` ký tự mỗi phía.

    ⭐ Vì sao cần: `snap()` mới chỉ vá được chữ cụt (WAL-194). Mảnh vẫn mở đầu
    và kết thúc giữa CÂU — đo trên pack: 13/38 mở giữa câu, 23/38 đóng giữa
    câu. Màn chuyện dán nhãn khối này là «TRÍCH NGUYÊN VĂN TỪ NGUỒN»; một mảnh
    cụt giữa câu tuy đúng từng chữ nhưng đọc ra vẫn là văn vỡ.

    Chỉ NỚI RA, không bao giờ thu vào — như `snap()`, để mảnh mà bước curate
    đòi phải có vẫn còn nguyên. Không tới được ranh giới câu trong `grow` ký tự
    thì lùi về ranh giới TỪ; phần dư ấy được UI đánh dấu bằng dấu «…» chứ không
    im lặng nhận là câu trọn vẹn.
    """
    start = max(0, start)
    end = min(len(text), end)

    # lùi đầu: tìm dấu kết câu gần nhất TRƯỚC start, rồi bắt đầu ngay sau nó
    lo = max(0, start - grow)
    best = None
    for m in _SENT_END.finditer(text, lo, start):
        best = m.end()
    if best is not None:
        start = best
    elif lo == 0:
        start = 0
    while start < len(text) and text[start].isspace():
        start += 1

    # nới đuôi: tới dấu kết câu đầu tiên SAU end
    m = _SENT_END.search(text, end, min(len(text), end + grow))
    if m:
        end = m.end()

    return snap(text, start, end)


def snap(text, start, end):
    """Nới cửa sổ ra HAI PHÍA tới ranh giới từ gần nhất.

    CHỈ NỚI RA, không bao giờ thu vào — chữ thêm vào vẫn là chữ nguyên văn của
    trang, và vì cửa sổ chỉ rộng thêm nên mọi mảnh mà bước curate đòi phải có
    vẫn còn nguyên trong bằng chứng.
    """
    start = max(0, start)
    end = min(len(text), end)
    while start > 0 and _WORDCH.match(text[start - 1]):
        start -= 1
    while end < len(text) and _WORDCH.match(text[end]):
        end += 1
    return text[start:end]


def clip(t, n):
    """Cắt còn <= n ký tự nhưng LÙI VỀ ranh giới từ — không để cap sinh ra
    đúng cái lỗi mà `snap` vừa sửa."""
    if len(t) <= n:
        return t
    cut = t[:n]
    i = len(cut)
    while i > 0 and _WORDCH.match(cut[i - 1]):
        i -= 1
    return (cut[:i] if i else cut).rstrip()


def viet_quality(t):
    """Tỉ lệ ký tự chữ hợp lệ + có dấu — thơ OCR vỡ rơi điểm."""
    letters = [c for c in t if c.isalpha()]
    if len(letters) < 10: return 0.0
    good = sum(1 for c in letters if unicodedata.name(c, '').startswith('LATIN'))
    words = t.split()
    diac = sum(1 for w in words if any(0x300 <= ord(unicodedata.normalize('NFD', c)[-1]) <= 0x36F for c in w if c.isalpha()))
    return round(min(1.0, good/len(letters)) * (0.5 + 0.5*min(1.0, diac/max(3,len(words)*0.25))), 2)

def mine(did, reg):
    base = f'poc-out/graph/ocr-body/{did}'
    if not os.path.isdir(base): return None
    r = reg[did]
    out = []
    def add(typ, page, text_ev, **kw):
        conf = viet_quality(text_ev)
        out.append(dict(type=typ, status='CANDIDATE', confidence=conf,
                        source=dict(sourceDocumentId=did, grade=r['grade'],
                                    subject=r['subject'], pagePdf=page,
                                    textEvidence=clip(text_ev, 300),
                                    extractionVersion=VER), **kw))
    for fn in sorted(os.listdir(base)):
        if not fn.endswith('.json'): continue
        page = int(fn[1:4])
        try: d = json.load(open(f'{base}/{fn}'))
        except Exception: continue
        text = ' '.join(l['text'] for l in d.get('lines', []))
        if page <= 3 or NOISE.search(text[:400]):
            continue  # bìa/pháp lý — nguồn nhiễu chính đo được ở probe
        for m in P_BIRTH.finditer(text):
            name, b, dth = m.group(1), int(m.group(2)), int(m.group(3))
            if not (700 <= b <= 2010 and b < dth <= 2026 and 15 <= dth - b < 110):
                continue  # OCR corruption / khoảng phi-nhân ⇒ loại
            name = clean_name(VERB_TAIL.sub('', name).strip())
            if DYNASTY.match(name) or EVENTISH.search(name) or len(name) < 3:
                continue  # triều đại/sự kiện mang (năm–năm) — không phải người
            if COUNTRYISH.match(name):
                continue  # quốc gia, không phải người
            if LOCATIVE.search(text[max(0, m.start() - 24):m.start()]):
                continue  # «ở Thăng Long (1527–1592)» — khoảng năm của NƠI CHỐN
            add('PERSON', page, snap_sentence(text, m.start() - 60, m.end() + 120),
                name=name, birthYear=b, deathYear=dth)
        for m in P_INTRO.finditer(text):
            name = clean_name(VERB_TAIL.sub('', m.group(2)).strip())
            if len(name) < 3 or EVENTISH.search(name):
                continue
            if COUNTRYISH.match(name):
                continue  # «nhà văn Đan Mạch» — bắt trúng QUỐC TỊCH, không phải tên
            add('PERSON', page, snap_sentence(text, m.start() - 40, m.end() + 120),
                name=name, role=m.group(1))
        for m in P_QUOTE.finditer(text):
            person = clean_name(m.group(2).strip())
            # «Theo X» / tên sách = TRÍCH VĂN BẢN, không phải lời danh nhân
            before = text[max(0, m.start(2)-8):m.start(2)]
            is_excerpt = ('Theo' in before or person.startswith('Theo')
                          or person.lower().startswith(('truyện', 'ca dao',
                              'tục ngữ', 'sách', 'báo')))
            # ⭐⭐ NGƯỜI BIÊN SOẠN KHÔNG PHẢI NGƯỜI PHÁT NGÔN.
            #
            # Ca thật: «…ông vẫn tuyên bố: "Dù sao Trái Đất vẫn quay!". (Lê
            # Nguyên Long, Phạm Ngọc Toàn, Tiếng Việt 4, …NXB Giáo dục…)».
            # Người nói là Ga-li-lê, đã nêu ngay trong câu trước; ngoặc đơn là
            # THƯ MỤC của sách giáo khoa. Gắn «— Lê Nguyên Long» làm người nói
            # là gán lời cho người chỉ biên soạn.
            #
            # Hai tín hiệu, đều đọc được từ chính văn bản:
            #   · câu trước đã có ĐỘNG TỪ NÓI + dấu hai chấm ⇒ người nói ở đó,
            #     không ở trong ngoặc
            #   · trong ngoặc có TỪ HAI TÊN TRỞ LÊN trước tên tác phẩm ⇒ danh
            #     sách biên soạn, không phải một người phát ngôn
            lead = text[max(0, m.start() - 60):m.start()]
            if SPEECH_LEAD.search(lead) or COMPILER_LIST.match(m.group(3) or ''):
                is_excerpt = True
            add('SOURCE_EXCERPT' if is_excerpt else 'QUOTE', page,
                snap_sentence(text, m.start() - 40, m.end() + 40),
                quote=m.group(1), person=person.removeprefix('Theo').strip(),
                citedSource=m.group(3))
        for m in P_EVENT.finditer(text):
            body = m.group(9)
            # v0.1: loại ngôn-ngữ-bài-tập/caption — đòi dấu hiệu SỰ KIỆN
            if re.search(r'em hãy|quan sát|bài tập|biểu đồ|bảng số liệu|lớp \d', body, re.I):
                continue
            year = int(m.group(2) or m.group(5) or m.group(8))
            md = None
            if m.group(3):
                md = f'{int(m.group(4)):02d}-{int(m.group(3)):02d}'
            elif m.group(6):
                md = f'{int(m.group(7)):02d}-{int(m.group(6)):02d}'
            add('EVENT', page, clip(m.group(0), 260), year=year, monthDay=md)
        for m in P_INV.finditer(text):
            ctx = text[max(0, m.start()-50):m.start(2)]
            # mục-đích/bài-tập: «em/học sinh… để tìm ra…» ⇒ không phải khám phá
            if re.search(r'\b(em|con|học sinh|chúng ta|để|nhằm|giúp)\s*$', ctx) or \
               re.search(r'em hãy|thí nghiệm đơn giản|bài tập', ctx, re.I):
                continue
            person = m.group(1)
            if person:
                person = VERB_TAIL.sub('', person).strip() or None
            # v0.1 precision-first: đòi NĂM hoặc PERSON hợp lệ gần đó
            window = text[max(0,m.start()-80):m.end()+40]
            if not person and not re.search(r'\b1\d{3}\b|\b20[0-2]\d\b', window):
                continue
            add('INVENTION_DISCOVERY', page, m.group(0)[:260],
                person=person, verb=m.group(2), what=m.group(3)[:120])
    return out

def main():
    reg = {d['sourceDocumentId']: d for d in
           json.load(open('poc-out/registry/source-registry.json'))['documents']}
    all_items, missing = [], []
    for did in SAMPLE:
        r = mine(did, reg) if did in reg else None
        if r is None: missing.append(did); continue
        all_items += r
    json.dump(all_items, open('poc-out/stories/candidates-v0.json','w'),
              ensure_ascii=False, indent=1)
    by = collections.Counter((i['type'], i['source']['subject']) for i in all_items)
    byt = collections.Counter(i['type'] for i in all_items)
    print(f'{len(all_items)} candidates | thiếu OCR: {missing}')
    print('theo type:', dict(byt))
    subj = collections.Counter(i['source']['subject'] for i in all_items)
    print('theo môn:', dict(subj.most_common()))
    hi = [i for i in all_items if i['confidence'] >= 0.75]
    print(f'confidence ≥0.75: {len(hi)}')
    print('\n── VÍ DỤ CHẤT LƯỢNG CAO ──')
    seen = set()
    for i in sorted(all_items, key=lambda x: -x['confidence']):
        if i['type'] in seen and len(seen) >= 4: continue
        if list(seen).count(i['type']) : pass
        key = i['type']
        if sum(1 for s in seen if s == key) >= 3: continue
        seen.add(key)
        s = i['source']
        head = {'SOURCE_EXCERPT': '[trích] '+str(i.get('quote'))[:50], 'PERSON': i.get('name'), 'QUOTE': f"{i.get('person')}: «{str(i.get('quote'))[:60]}…»",
                'EVENT': f"{i.get('year')} — {i['source']['textEvidence'][:50]}",
                'INVENTION_DISCOVERY': f"{i.get('person') or '?'} {i.get('verb')} {str(i.get('what'))[:45]}"}.get(i['type'],'')
        print(f"  [{i['type'][:6]}|c{i['confidence']}] {s['subject']} {s['grade']} p{s['pagePdf']}: {head}")
        if len(seen) >= 4 and sum(byt[t] > 0 for t in byt) <= len(seen): break
    mani = dict(version=VER, totalCandidates=len(all_items),
                byType=dict(byt),
                bySubject=dict(subj),
                sampleBooks=len(SAMPLE))
    json.dump(mani, open('poc-out/stories/manifest-v0.json','w'),
              ensure_ascii=False, indent=1)
    print('manifest:', VER, len(all_items))

if __name__ == '__main__':
    main()
