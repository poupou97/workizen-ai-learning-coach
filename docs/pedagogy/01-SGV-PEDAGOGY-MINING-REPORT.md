# 01 — SGV PEDAGOGY MINING REPORT (Phase 1, sample)

> WAL-127 · Founder Order 2026-09-02 #2 §3/§27 · extractor `sgv-pedagogy-v1` + `sgv-pedagogy-en-v1`
> (`tool/pedagogy/mine_sgv.py`, deterministic, không LLM). Findings + provenance đầy đủ nằm ở
> `poc-out/pedagogy/` (localResearchOnly — không commit text dẫn xuất; report này chỉ số đếm +
> trích ≤1 dòng để minh hoạ, kèm trang).
> **KHÔNG claim 220 SGV giống sample** — đây là kết quả trên 17 cuốn được chọn có chủ đích.

## 1. Sample strategy

220 SGV OCR DONE. Chọn 17 cuốn = mỗi (family × band) một cuốn khi corpus có, ưu tiên lớp thấp
nhất trong band + 2 cuốn ngoài 5 family (Âm nhạc 1, Tiếng Pháp 9) để đo variance cấu trúc:

| Family | 1-2 | 3-5 | 6-9 | 10-12 |
|---|---|---|---|---|
| TOÁN | toan-1 | toan-3 | toan-6 | toan-10 |
| TV/VĂN | tieng-viet-1-t1 | tieng-viet-3-t2 | ngu-van-6-t2 | ngu-van-10-t2 |
| KHOA | — (gap) | khoa-hoc-4 | — (gap) | hoa-hoc-10 |
| SỬ | — | — | — (gap) | lich-su-10 |
| NN | tieng-anh-1 GS | tieng-anh-3 GS | tieng-anh-7 GS | tieng-anh-11 GS |

## 2. SGV structure findings (đo được, không assume)

**Khung VN (KNTT)** — xác nhận trên Toán/TV/Khoa/Sử/Văn: `Bài N` + TIÊU ĐỀ IN HOA + `(k tiết)`
→ `MỤC TIÊU` (Kiến thức / Phát triển năng lực) → `CHUẨN BỊ` → `HOẠT ĐỘNG DẠY HỌC` chia theo
`Tiết n` → mục intent đánh số (`1. Khám phá`, `2. Hoạt động`, `Tiết 2. Luyện tập`) → hướng dẫn
TỪNG BÀI TẬP (`Bài k:`) gồm kịch bản lời GV, câu hỏi gợi ý, kết quả dự kiến. (Ví dụ khung đầy đủ:
`01-sgv-toan-1` p21-22.) OCR noise đã xử lý: số mục La Mã I/II/III thành «Ш»/«L» (cho 0-4 ký tự rác đầu dòng).

**Khung EN (Global Success, Tiểu học)** — KHÁC HOÀN TOÀN, phát hiện từ header-frequency (không đoán
trước): mỗi activity một block **`Goal:` / `Input:` / `Procedure:` / `Outcome:`** (594 block/2 cuốn 1+3)
+ `LESSON N (Period N)` + `Warm-up` + `Audio script:` + `Picture cues:` + activity đặt tên theo skill
(«Listen and tick», «Read and match»…). Đây là cấu trúc sư phạm CÓ MÁY ĐỌC ĐƯỢC GIÀU NHẤT corpus —
gần như một LearningExperienceBlueprint viết sẵn.

**EN THCS/THPT (GS 7, 11)** — format ĐỔI THEO CẤP: không còn Goal-block; giàu `Objectives`
(133 hit lớp 7, 44 lớp 11) theo unit. ⇒ NN cần adapter THEO CẤP, không một adapter cho cả dải.

## 3. Field coverage (số finding / family, sample)

| Field | TOÁN | TV/VĂN | KHOA | SỬ | NN | KHÁC |
|---|---|---|---|---|---|---|
| objective | 155 | 118 | 17* | 15 | 267 | 8 |
| requiredOutcome (YCCĐ) | 0 | 6 | 32 | 0 | — | 0 |
| preparation | 122† | 96 | 44 | 0 | — | 5 |
| activityFlow | 122 | 124 | 35† | 13† | — | 9† |
| intent (mục hoạt động) | 982 | 237 | 35 | 24 | 242 | 22 |
| perExerciseGuide (`Bài k:`) | 1.418 | ~40 | 85 | 26 | — | — |
| teacherNote (Lưu ý) | 469 | 47 | 10 | 9 | — | 19 |
| misconceptionCandidate | 13 | 17 | 3 | 3 | 0 | 3 |
| suggestedQuestion | 117 | 136 | 37 | 27 | — | 12 |
| expectedResponse (dự kiến/đáp án) | 179 | 158 | 65 | 14 | — | — |
| organization (nhóm/cặp/cá nhân/lớp) | 401+ | 1.167+ | 117 | 132 | pair-group dày | 71 |
| differentiation (phân hoá/khá-giỏi) | 17 | 1 | 1 | 0 | — | 0 |
| assessment (mục ĐÁNH GIÁ) | 2 | 2 | 1 | 2 | — | 2 |
| Goal/Input/Procedure/Outcome | — | — | — | — | 594×4 | — |
| skillActivity (EN) | — | — | — | — | 781 | — |

\* Khoa học 4 dùng «YÊU CẦU CẦN ĐẠT» thay «MỤC TIÊU» — hai truyền thống đặt tên cùng tồn tại.
† con số gộp một phần; chi tiết trong `poc-out/pedagogy/mining-summary.json`.

## 4. Pedagogical intent distribution (VN)

Toán 6: PRACTICE 137 · APPLY 95 · DISCOVER 77 · CONSOLIDATE 76 — intent-dày nhất sample.
Toán 1/3: PRACTICE > DISCOVER > ACTIVATE; TV 1: CONSOLIDATE 76 · ACTIVATE 46 (củng cố âm/vần);
Sử 10 + Âm nhạc 1: APPLY đứng đầu; Văn: DISCOVER đứng đầu.
**⇒ F2 có evidence: phân bố intent KHÁC THEO MÔN — một sequence chung cho mọi môn là sai.**

Top chuỗi intent trong MỘT bài (thứ tự trang): `ACTIVATE→DISCOVER` (45), `ACTIVATE→CONSOLIDATE` (20),
`ACTIVATE→PRACTICE` (19), `PRACTICE→APPLY(→PRACTICE)` (12), `DISCOVER→APPLY` (5)… — chuỗi NGẮN và
đa dạng; khởi động rồi-đi-đâu phụ thuộc môn/bài. Không thấy một khuôn 5 bước cứng.

## 5. Misconceptions (mỏ quan trọng nhất cho WAL-128 §18)

**39 candidate có (doc, trang, bài)** — ví dụ thật: Toán 3 p190 «HS hay mắc sai lầm khi tính chu vi
hình chữ nhật bằng 3 lần chu vi của một hình vuông»; Toán 3 p129 (chia dạng đầy đủ khi HS nhầm);
Toán 3 p84 (dễ nhầm khi đếm cạnh); TV 3 p58 (âm dễ lẫn do phát âm địa phương — misconception
NGỮ ÂM THEO VÙNG, loại SAM chưa từng model). Ngoài ra **teacherNote «Lưu ý» 560+ dòng CHƯA phân
loại** — phần lớn là hướng dẫn dạy, một phần là misconception ngầm ⇒ việc phân loại là bước sau
(WAL-128), KHÔNG gộp bừa vào misconception.

## 6. Assessment patterns — YẾU trong sample

Mục «ĐÁNH GIÁ» chỉ ~9 hit toàn sample (KNTT không có mục đánh giá riêng per-bài như CTST/CD?).
UNKNOWN: cần đối chiếu bộ sách khác trước khi kết luận «SGV ít nói về đánh giá».

## 7. Khác biệt theo môn (tóm)

TOÁN = per-exercise script + teacherNote dày (mỏ hint/misconception); TV/VĂN = organization dày
nhất (cả lớp/nhóm/cặp 1.167+ — thách thức chuyển 1-learner lớn nhất, §4); KHOA = YCCĐ + quan sát/
thí nghiệm; SỬ = suggestedQuestion + APPLY + làm-việc-cá-nhân-với-nguồn nhiều hơn dự đoán;
NN = blueprint-sẵn (Goal/Input/Procedure/Outcome) nhưng đổi format theo cấp.

## 8. Khác biệt theo lớp

Cùng môn Toán: lớp 1 dạy qua thao tác vật thật (đếm ong, que tính — perExerciseGuide 520);
lớp 6 chuyển hẳn sang intent 4 pha PRACTICE/APPLY/DISCOVER/CONSOLIDATE (392); lớp 10 PRACTICE-nặng.
Lời «dự kiến kết quả» giảm dần theo lớp — HS lớn, SGV tin GV hơn.

## 9. Source gaps (quan trọng cho PED-D)

- **KHÔNG có SGV KHTN 6-9** trong corpus (0 cuốn) — pedagogy KHTN THCS phải lấy từ SGK + nguồn khác.
- **SGV Sử chỉ 10-12** (3 cuốn); Lịch sử & Địa lí 4-9: KHÔNG có SGV.
- SGV NN chỉ Global Success — chưa có bộ khác để đối chiếu.
- Đây là giới hạn NGUỒN, không phải giới hạn extractor.

## 10. UNKNOWN giữ nguyên UNKNOWN

Publisher/edition phần lớn UNKNOWN (registry); intent ngoài 7 loại VN + 2 loại EN chưa mine
(REFLECT chỉ 1 hit — có thể pattern chưa đúng, chưa kết luận «SGV không có reflection»);
expectedResponse regex precision thấp (khớp cả prose nhắc «đáp án») — dùng làm signal, không làm số chính.

## 11. Limits

Sample 17/220; một bộ sách chiếm ưu thế (KNTT/GS); OCR 1 lượt Apple Vision (lỗi dấu má tồn tại);
extractor match dòng-đầu-mục nên mục vỡ dòng có thể sót; chưa mine SGV cấp THPT đủ dày.

## 12. Feed-forward

→ WAL-128: PedagogicalPattern lấy intent taxonomy ĐO ĐƯỢC ở §4 (không phải 18 intent lý thuyết);
misconception model seed = 39 candidate §5; organization §7 là input cho «intent extraction, không
copy 1:1» (§4 order). → WAL-117/130: NN adapter phải THEO CẤP. → PED-D: gap nguồn §9 quyết định
môn nào validate bằng SGV, môn nào phải bằng SGK.
