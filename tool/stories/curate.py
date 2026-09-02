#!/usr/bin/env python3
"""WAL-149 KS-B — bước NGƯỜI CHẤM: promote item cụ thể → VERIFIED.

Curation list dưới đây do reviewer (Claude, 2026-09-02) chấm TAY từ evidence
đã đọc trực tiếp trong 2 vòng chấm KS-A — mỗi mục match theo
(type, doc, page, mảnh-text-bắt-buộc-có-trong-evidence). Item không khớp
list giữ nguyên trạng thái máy. VERIFIED mang curatedBy + version.
"""
import json, hashlib

CURATOR = 'claude-review-2026-09-02'

# (type, docId, page, mảnh evidence bắt buộc)
VERIFY = [
 # ── QUOTE (tư liệu in rõ nguồn — đã xem tận mắt) ──
 ('QUOTE','10-sgk-lich-su-10',14,'Dân ta phải biết sử ta'),
 ('QUOTE','10-sgk-lich-su-10',108,'Đoàn kết, đoàn kết, đại đoàn kết'),
 # ── PERSON (anchor năm sinh-mất, đã đối chiếu evidence) ──
 ('PERSON','06-sgk-ngu-van-6-tap-mot',20,'Tô Hoài'),
 ('PERSON','06-sgk-ngu-van-6-tap-mot',26,'Xanh-to E-xu-pe-ri'),
 ('PERSON','06-sgk-ngu-van-6-tap-mot',47,'Ta-go'),
 ('PERSON','06-sgk-ngu-van-6-tap-mot',66,'An-đéc-xen'),
 ('PERSON','06-sgk-ngu-van-6-tap-mot',74,'Thạch Lam'),
 ('PERSON','06-sgk-ngu-van-6-tap-mot',85,'Lu-i Xe-pun-ve-da'),
 ('PERSON','06-sgk-ngu-van-6-tap-mot',94,'Lâm Thị Mỹ Dạ'),
 ('PERSON','10-sgk-ngu-van-10-tap-hai',58,'Sê-khốp'),
 ('PERSON','10-sgk-ngu-van-10-tap-hai',124,'Pri-sơ-vin'),
 ('PERSON','10-sgk-ngu-van-10-tap-hai',11,'Nguyễn Trãi'),
 ('PERSON','06-sgk-am-nhac-6',33,'Beethoven'),
 ('PERSON','06-sgk-am-nhac-6',46,'Brahms'),
 ('PERSON','06-sgk-am-nhac-6',30,'Văn Ký'),
 ('PERSON','06-sgk-mi-thuat-6',14,'Bùi Xuân Phái'),
 ('PERSON','07-sgk-lich-su-va-dia-li-7',23,'Mác-tin Lu-thơ'),
 ('PERSON','07-sgk-lich-su-va-dia-li-7',79,'Lê Thánh Tông'),
 ('PERSON','07-sgk-lich-su-va-dia-li-7',82,'Nguyễn Chích'),
 ('PERSON','07-sgk-lich-su-va-dia-li-7',47,'Lê Văn Hưu'),
 ('PERSON','07-sgk-lich-su-va-dia-li-7',11,'Sác-lơ-ma-nhơ'),
 ('PERSON','06-sgk-khoa-hoc-tu-nhien-6',98,'G-ram'),
 ('PERSON','06-sgk-toan-6-tap-mot',9,'Cantor'),
 # ── EVENT (năm + sự kiện, đã đối chiếu) ──
 ('EVENT','06-sgk-ngu-van-6-tap-mot',20,'Tô Hoài xuất bản truyện'),
 ('EVENT','07-sgk-lich-su-va-dia-li-7',48,'Ngô Quyền'),
 ('EVENT','10-sgk-sinh-hoc-10',133,'Robin Warren'),
 ('EVENT','07-sgk-lich-su-va-dia-li-7',15,'Bô-lô-na'),
 ('EVENT','07-sgk-lich-su-va-dia-li-7',92,'Huyền Trân'),
 ('EVENT','10-sgk-lich-su-10',44,'Hen-ri Pho'),
 ('EVENT','04-sgk-lich-su-va-dia-li-4',88,'Tuyên ngôn Độc lập'),
 ('EVENT','07-sgk-lich-su-va-dia-li-7',164,'Nam Cực'),
 ('EVENT','06-sgk-am-nhac-6',64,'lá cờ Tố quốc tung bay'),
 # ── INVENTION / DISCOVERY ──
 ('INVENTION_DISCOVERY','10-sgk-lich-su-10',43,'E-đi-xơn'),
 # kim-chỉ-nam LS&ĐL7 p16: v0.1 loại vì thiếu người/năm gần (false-negative
 # chấp nhận được — precision>recall); không lật máy trong batch này.
 ('INVENTION_DISCOVERY','07-sgk-lich-su-va-dia-li-7',168,'châu Mỹ'),
 ('INVENTION_DISCOVERY','10-sgk-tin-hoc-10',15,'World Wide Web'),
 ('INVENTION_DISCOVERY','04-sgk-lich-su-va-dia-li-4',88,'con đường cứu nước'),
 ('INVENTION_DISCOVERY','10-sgk-hoa-hoc-10',14,'proton'),
 ('INVENTION_DISCOVERY','10-sgk-lich-su-10',28,'kim loại không bị ăn mòn'),
]

def iid(i):
    h = hashlib.sha1(i['source']['textEvidence'].encode()).hexdigest()[:8]
    return f"{i['type'][:3].lower()}:{i['source']['sourceDocumentId']}" \
           f":p{i['source']['pagePdf']}:{h}"

def main():
    items = json.load(open('poc-out/stories/curated-v0.json'))
    hit = 0
    unmatched = list(VERIFY)
    for i in items:
        i['id'] = iid(i)
        for v in list(unmatched):
            t, doc, page, frag = v
            if (i['type'] == t and i['source']['sourceDocumentId'] == doc
                    and i['source']['pagePdf'] == page
                    and frag in i['source']['textEvidence']):
                if i['status'] == 'REJECTED':
                    break  # máy đã bác — người không lật mù trong batch này
                i['status'] = 'VERIFIED'
                i['curatedBy'] = CURATOR
                unmatched.remove(v)
                hit += 1
                break
    json.dump(items, open('poc-out/stories/curated-v0.json', 'w'),
              ensure_ascii=False, indent=1)
    ver = [i for i in items if i['status'] == 'VERIFIED']
    json.dump(ver, open('poc-out/stories/verified-v0.json', 'w'),
              ensure_ascii=False, indent=1)
    import collections
    print(f'VERIFIED: {len(ver)} (match {hit}/{len(VERIFY)} mục curation)')
    print('theo loại:', dict(collections.Counter(i["type"] for i in ver)))
    print('theo môn:', dict(collections.Counter(i["source"]["subject"] for i in ver)))
    if unmatched:
        print('KHÔNG KHỚP (kiểm lại page/frag):')
        for v in unmatched: print('  ', v)

if __name__ == '__main__':
    main()
