# VISUAL TOKEN GAP REPORT — lệnh 57

Ngày 2026-09-07 · nhánh `feat/timetable-home-personalization` (PR #123)

**Phương pháp (§8.2):** mọi con số dưới đây là **phép đo pixel** trên ảnh concept
trong repo (`concept/concept-ai-first/*.png`), không phải chọn bằng mắt. Chỗ nào
không đủ bằng chứng thì ghi **UNRESOLVED** và không tự đặt giá trị.

---

## Bảng gap

| TOKEN / ELEMENT | CONCEPT | CURRENT (trước) | VERDICT | ACTION |
|---|---|---|---|---|
| **Primary purple** | `#6A36EE` | `#7C4DFF` | **DIFFERENT** | ✅ ALIGNED |
| Nền trang | `#F9F9FD` | `#F7F7FC` | gần khớp | ✅ ALIGNED |
| Surface tím nhạt | `#F5F1FE` | `#F3EEFF` | gần khớp | ✅ ALIGNED |
| **Card radius** | ~12–15 | `20` | **DIFFERENT** | ✅ ALIGNED → 14 |
| Button radius | ~15 (nền cao 48) | `16` | **MATCH** | giữ |
| **Subject colors** | có quy định | không có | **DIFFERENT** | ✅ ALIGNED (5 môn) |
| Accent vàng | mẫu chỉ 10 px | `#FFB800` | **UNRESOLVED** | giữ nguyên |
| **Font family** | không xác minh được | *không khai font* | **UNRESOLVED + DESIGN GAP** | ghi nhận |
| Text primary/secondary | chưa đo tách bạch | `#2D2D3A` / `#55556A` | UNRESOLVED | giữ |
| Success / Warning / Error | mẫu <5 px mỗi màu | có token | UNRESOLVED | giữ |

---

## Bằng chứng cho từng thay đổi

### Tím thương hiệu — thay đổi đáng kể nhất

Mode của pixel tím bão hoà, đo **độc lập trên bốn màn**:

| màn | mode |
|---|---|
| 05 Home | `#6A34EE` |
| 04 Timetable | `#6B38EB` |
| 07 Subject Home | `#6934F2` |
| 02 Learner Profile | `#693AED` |

Cụm rất chặt ⇒ chốt **`#6A36EE`**. Token cũ `#7C4DFF` **sáng hơn và ngả xanh
hơn** rõ rệt. Không tìm thấy quyết định nào của Founder thay thế màu concept,
nên theo §8.13 «chưa supersede thì ƯU TIÊN BÁM CONCEPT».

### Bán kính thẻ

Đo trên 05 Home: nút CTA r≈15 trên nền cao 48 → token 16 **khớp**. Thẻ trắng
lớn r≈15, thẻ tím nhạt r≈12 → thẻ ≈ **14**, không phải 20.

⚠️ Trong concept **thẻ bo ÍT hơn nút**. Trong code trước lệnh này thì ngược lại
(thẻ 20 > nút 16). Đó là dấu hiệu của thứ implementation tự nới qua các vòng —
đúng nghi ngờ §8.8 của Founder về «nhiều card tím bo tròn».

### Màu theo môn (§8.10)

Concept **có** quy định, đo ở hàng «Các môn của con»:

`Toán #F2EDFD` · `Tiếng Việt #EBF9F3` · `Khoa học #E9F1FE` ·
`Sử & Địa #FEEFE2` · `GDCD #F4F0FE` · `AI học #E5E8FD`

Trước lệnh này thẻ Home dùng **bảng màu tôi tự chế** (5 cặp gradient chọn tay).
Nay dùng đúng màu concept; môn concept **chưa** quy định (KHTN, Ngữ văn, Tin
học… của cấp 2) trả `null` và rơi về sắc trung tính tất định — **không giả vờ
là màu concept**.

---

## ⚠️ UNRESOLVED — và vì sao không tự đặt

### Font family (§8.3, §8.4)

**App:** `pubspec.yaml` **không có khối `fonts:` nào**, `lib/` **không có
`fontFamily` nào**, không có `ThemeData`/`textTheme` tuỳ biến. Flutter rơi về
font hệ thống — trên Nokia là **Roboto**. Đây là sự thật kiểm chứng được, và
có test khoá.

**Concept:** **không xác minh được.** Repo chỉ có ảnh PNG; không có design
source (Figma/Sketch), không có tệp font, và không tài liệu nào nêu tên font.
Suy font từ hình dáng chữ trong ảnh nén là đúng thứ §8.4 cấm.

**Verdict theo lệnh 58 §4 — giữ trung thực:**

```
FONT FAMILY
Concept : UNRESOLVED
App     : system Roboto
Decision: KEEP TEMPORARILY
Reason  : no verifiable design source
```

Không gọi MATCH. Cũng không gọi DIFFERENT — chưa biết font concept thì không
có gì để so.

⇒ Backlog: **WAL-225** «TYPOGRAPHY SOURCE / FONT FAMILY — UNRESOLVED». Cần một
trong: Figma/design source · font specification · original editable design ·
quyết định của Founder.

### Accent / success / warning / error

Mẫu pixel trong concept quá nhỏ (2–10 px mỗi màu) — không đủ để chốt HEX. Giữ
nguyên token và ghi UNRESOLVED thay vì đặt một con số trông có vẻ đo được.

---

## §8.6 — hard-coded style

Đã đưa về token: bảng gradient tự chế trong `mission_center_screen.dart` (5 cặp
màu viết tay) → `WalSubjectColors`, nguồn là concept.

Còn lại: các `Color(0x…)` rải rác trong màn learner-facing vẫn tồn tại (scrim,
bóng đổ, viền mảnh). Chưa gom hết — §8.6 nói «không bắt buộc refactor toàn app».

---

## §8.12 — BEFORE / AFTER trên Nokia (lệnh 58 §7)

| | |
|---|---|
| git SHA | `0a76468` (HEAD PR #123) |
| build | `flutter build apk --profile` (`--release` vẫn bị R8/ML Kit chặn) |
| device | Nokia 6.1, Android, 1080×1920, gesture nav |
| xác minh | kéo APK đã cài về, grep `libapp.so` thấy `radiusBookCover` ⇒ APK = HEAD |

Ảnh: `~/Desktop/wal-evidence/order58-final-2026-09-07/`
A1 Home BEFORE · A2 Home AFTER · B2 Timetable AFTER · C Profile AFTER ·
D Lesson Workspace AFTER.

### ⭐ Bằng chứng KHÁCH QUAN — đo trên chính ảnh chụp máy

| | tím chủ đạo |
|---|---|
| BEFORE | `#7C4DFF` (124 027 px) |
| AFTER | `#6A36EE` (122 472 px) |
| CONCEPT | `#6A36EE` |

Không phải «trông gần concept hơn» — **bằng đúng giá trị concept**.

### Quét regression (lệnh 58 §2)

| tìm | kết quả |
|---|---|
| `#7C4DFF` hardcode | **0** (chỉ còn trong comment lịch sử) |
| `circular(20)` kiểu cũ | **0** |
| `Color(0x…)` trong màn learner-facing | 6, đều là scrim/bóng/viền trong suốt — không phải màu thương hiệu |
| cùng component khác radius | **1 đã sửa**: bìa sách bo 8 ở Giá sách vs 6 trên Home ⇒ gom về `radiusBookCover` |
| Timetable như module lạ | không — cùng surface, cùng tím, cùng radius, cùng typography |
| Lesson Workspace đổi ngoài ý muốn | không |
| contrast giảm | không thấy |
| Home quá sặc sỡ vì subject color | không — màu concept là các sắc RẤT nhạt (#F2EDFD…), dùng làm nền thẻ, không phải khối màu

---

## Kết luận theo tiêu chí Founder

Token đã bám concept ở những chỗ **đo được**: tím thương hiệu, nền, surface,
bán kính thẻ, màu theo môn. Font vẫn là **DESIGN GAP chưa giải được** vì thiếu
nguồn.

⇒ Theo đúng cách Founder đặt vấn đề: **IMPLEMENTED, BUT DESIGN GAP REMAINS**
(font). Chưa gọi UI DONE.
