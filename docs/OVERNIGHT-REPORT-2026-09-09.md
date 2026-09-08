# BÁO CÁO CUỐI PHIÊN — 2026-09-09 · B3 CANONICAL ADDITIVE DOCLING ROLLOUT

`main` = `7e38263` · PR #163 (B2.1) và #164 (B3) đã merge · CI xanh · cây git sạch

---

## B3 STATUS

**HOÀN THÀNH.** Không dừng ở checkpoint dở: cả 12 lớp tri giác đủ 100% và đã
dựng lại, nên không lớp nào phải giữ pack cũ vì thiếu dữ liệu.

Kiến trúc chạy đúng như Founder chốt:

```
SOURCE → đề xuất Docling → CỔNG TIN CẬY → bằng chứng in
      → REGION_TRUST / IDENTITY_LINK → corpus canonical → pack
```

`NỘI DUNG D AN TOÀN + VÙNG DOCLING ĐÁNG TIN = CANONICAL MỚI`. Không có chỗ nào
thay D bằng Docling. Docling chỉ chạy lúc dựng dữ liệu, **không có trong app**.

## DATA

| | |
|---|---|
| trang đã tri giác | **16.800 / 16.800** (229 cuốn) |
| trang lỗi | **0** |
| thời gian | 159 phút, 6 luồng, **0,57 s/trang hiệu dụng**, offline |
| đề xuất hình + bảng | 52.279 |

Khu tạm: `poc-out/docling/proposals-w{0..5}.jsonl` (JSONL nối thêm, flush từng
dòng). Bước tri giác tách hẳn khỏi bước cổng — **sửa luật cổng không phải chạy
lại 16.800 trang**.

## TRUST

| | số | tỉ lệ |
|---|---|---|
| REGION_TRUSTED | **8.537** | 16,3% |
| REGION_WITHHELD | 43.203 | 82,6% |
| REGION_CONFLICT | 539 | 1,0% |

Cổng **an toàn mà yếu** — 16,3%. Đó là con số phải báo, không phải con số để giấu.

**Theo dải lớp** (báo, KHÔNG tối ưu theo lớp — không có luật nào theo lớp trong code):

| dải | đề xuất | trusted | vào dòng đọc |
|---|---|---|---|
| 1–3 | 8.595 | 74 | 64 |
| 4–8 | 19.219 | 2.536 | 2.266 |
| 9–12 | 24.465 | 5.927 | 5.403 |

## IDENTITY

`REGION_TRUST != IDENTITY_LINK` là bất biến, có code và test riêng.

| | số |
|---|---|
| IDENTITY_RESOLVED | 7.733 |
| IDENTITY_WITHHELD | 804 |
| vùng nằm trong cụm dùng chung chú thích | 1.207 |
| — nối được nhờ **nhãn con SÁCH IN** | 403 |
| — giữ lại danh tính ⇒ **không vào dòng đọc** | 804 |

**Không sinh một danh tính hình con nào.** Nhân chứng Công nghệ 11 tr.25: ba
ảnh nhận đúng «a) Chó Bắc Kinh lai Nhật» / «b) Mèo Anh lông ngắn» / «c) Gà tre
Tân Châu», không có «Hình 6.1a».

## TABLE / FIGURE

| | số |
|---|---|
| FIGURE_TRUSTED | 7.883 |
| **TABLE_TRUSTED** | **654** |
| TABLE_STRUCTURED | **CHƯA — không bật vì đã có ảnh vùng bảng** |

Bảng giữ luật bằng chứng riêng: chú thích BẢNG in ở TRÊN, chú thích HÌNH in ở
DƯỚI. Chặn cả hai phía cho «đồng bộ» thì mất toàn bộ bảng.

## BUILD / PACK

**Cầu nối di trú** (đếm ngay lúc dựng, không quét lại):

| CHỈ D | **MỚI — chỉ Docling có** | CẢ HAI |
|---|---|---|
| 16.093 | **4.345** | 3.887 |

**Pack — không mất gì, thêm thật:**

| | trước | sau |
|---|---|---|
| bản ghi mở được | 2.974 | **2.974** |
| bài riêng mở được | 2.778 | **2.778** |
| bài có hình | 2.602 | **2.715** (+113) |
| hình phân biệt | 13.540 | **17.724** (+4.184) |

**Bất biến pack 12/12 lớp: ĐẠT.** Lớp 1 và 2 ra **đúng hash cũ**
(`g1-612eca8466b1`, `g2-b6afb7e1dab7`) — nơi không có vùng đáng tin thì đường
dựng không đổi một byte.

An toàn khi dựng: kho hình ghi tệp tạm rồi `os.replace` nguyên tử; thiếu
`trusted.jsonl` ⇒ đường dựng chạy y như cũ; bản sao pack cũ ở
`/private/tmp/wal-b3-backup`.

## TEST / CI

**1.309 test xanh.** CI xanh trên cả #163 và #164.

Kiểm đột biến trong phiên: **18/18 bị bắt**. Hai con **sống sót lần đầu** và đã
sửa: fixture nhãn con đặt đúng biên `SUB_GAP` nên bị phép đo khoảng cách loại
trước; test độ phủ chỉ khẳng định CỜ mà không khẳng định SỐ ĐẾM.

## MERGED

* **#163** — B2.1 mở rộng bằng chứng chú thích in + sửa lỗi trích dẫn câu thân bài
* **#164** — B3 canonical additive rollout (`docling_run` · `docling_gate` ·
  `docling_identity` · `docling_pack` · `docling_promote` · `docling_census`)

## HAI KẾT LUẬN CỦA CHÍNH TÔI BỊ CORPUS BÁC BỎ

1. **«Lớp 1–3 = 0% bằng chứng in»** — đo trên 63 trang, tôi gọi đó là TRẦN của
   kiến trúc. Toàn corpus: **74 vùng đáng tin, 64 vào dòng đọc** ở lớp 1–3. Là
   ảo ảnh của mẫu nhỏ. Founder chặn đúng chỗ khi cấm luật theo lớp.
2. **Họ chú thích «dấu nguồn»** («Thêu⁽⁴⁾») — nghiệm thu trên 63 trang với 15 ca,
   3 ca soi mắt đúng. Trên 1.900 trang thật: **7/7 SAI** (tên bài «PHÉP CỘNG
   (qua 10)», trích nguồn «…NXB Trẻ, 2004)», thân bài điền khuyết «a book. I am
   (3)»). **Hai ảnh đã kịp mang tên bịa vào pack lớp 3** trước khi bị bắt. Đã rút
   họ ấy, dựng lại. Phần tăng thật của B2.1 vì thế phải đính chính xuống:
   DEV 7→9 (không phải 14), hồi quy 8→10 (không phải 15), **holdout tươi 4→4 —
   đóng góp bằng không**.

## DEVICE

**Nợ, chưa trả.** Nokia kết nối được (`192.168.1.3:5555`) nhưng **màn hình tắt,
đang ở màn khoá** suốt phiên. Không chạm màn khoá.

Khi máy mở, kiểm đúng 5 ca Founder chỉ định:
1. một hình **mới do Docling thêm** (ví dụ Tin học 3 «Hình 26. Nháy chuột…»)
2. một **bảng** (KHTN 6 «Bảng 41.1. Độ lớn một số lực»)
3. một **sơ đồ có nhãn bên trong**
4. một sách **lớp trên** (lớp 11 hoặc 12)
5. một trang **tiểu học GIỮ LẠI đúng** mảng ghép nhập nhằng (Đạo đức 2 tr.43)

## BLOCKER

* **WAL-240** — máy khoá; kiểm bằng mắt lớp 11 (Home Next Action, TKB, tên môn,
  routing, Read structure) vẫn nợ.
* **FORMULA / CODE** — Docling thấy **4.885** vùng công thức, **875** vùng mã.
  Chưa xử lý theo đúng lệnh Founder. `STEM_SAFE` = **UNKNOWN**.

## METRIC — KHÔNG BỊA XANH

| metric | giá trị |
|---|---|
| OPENABLE_RECORDS | 2.974 |
| DISTINCT_OPENABLE | 2.778 |
| STRUCTURED_READ | 2.974 |
| DOCLING_PROPOSED_REGIONS | 52.279 |
| DOCLING_TRUSTED_REGIONS | 8.537 |
| NET_NEW_TRUSTED_REGIONS | **4.345** |
| REGION_TRUST_COVERAGE | 16,3% |
| IDENTITY_LINK_RESOLVED / WITHHELD / CONFLICT | 7.733 / 804 / 0 |
| TABLE_DETECTED / TRUSTED / STRUCTURED | 2.985 / 654 / **chưa** |
| FIGURE_CROP_VALID | **UNKNOWN** — mới soi tay 9 vùng, đều đúng; 8.537 vùng thì 9 mẫu không kết luận được |
| MULTIMODAL_FAITHFUL_VALIDATED | **UNKNOWN** — chưa có phép xác minh diện rộng |
| STEM_SAFE | **UNKNOWN** |
| LEARNABLE | **0** |

## NỢ ĐÃ ĐO, CHƯA SỬA

* **Chú thích lặp trong dòng đọc**: 30/41 hình D và 24/35 hình Docling ở lớp 3 có
  chú thích xuất hiện HAI LẦN (một trong ảnh, một trong dòng chữ). **Cùng tỉ lệ
  ⇒ không phải hồi quy của B3**, là nợ sẵn có của `interleave`.
* **Chú thích thật dài 3 dòng** rơi khỏi cổng khối ≤2 dòng (Lịch sử 11 tr.22).
* **Chú thích thật 66 ký tự** vượt mức 60 (Mĩ thuật 10 tr.36).

## NEXT TOMORROW

1. Trả nợ device khi Founder mở khoá — 5 ca ở mục DEVICE.
2. Xác minh diện rộng `FIGURE_CROP_VALID` trên mẫu ngẫu nhiên đủ lớn của 8.537
   vùng, để quyết có bắc cầu được `MULTIMODAL_FAITHFUL_VALIDATED` hay không.
3. WAL-236: từ `TABLE_TRUSTED` 654 tiến sang `TABLE_STRUCTURED` (hàng/cột).
4. Chờ Founder ưu tiên FORMULA / CODE (4.885 + 875 vùng đã đo).

**Lệnh chạy lại nếu cần:**

```
python3 tool/corpus/docling_run.py --pages <b3-pages.json> --workers 6   # bỏ qua trang đã có
python3 tool/corpus/docling_gate.py
python3 tool/corpus/docling_promote.py --pages <b3-pages.json> --build   # chỉ lớp đủ 100%
python3 tool/ui/build_pack.py --all --verify
```

Danh sách trang: `poc-out/docling/b3-pages.json`. Bản sao pack trước B3:
`/private/tmp/wal-b3-backup`.
