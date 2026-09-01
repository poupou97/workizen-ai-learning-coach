# WAL-89/90/91 — QĐ 2422 + CV 5588: nguồn authoritative cho AI Curriculum lớp 1–12

**Ngày:** 2026-09-01 · Theo Founder Task Order cùng ngày · Trích xuất: `tool/extract/parse_qd2422.py`
(tất định) → `poc-out/vbqd/qd2422-extracted.json` (ngoài git — sản phẩm phái sinh chờ legal).

## 1. Phân loại thẩm quyền — ba tài liệu, BA hạng khác nhau

| | QĐ 2422/QĐ-BGDĐT | CV 5588/BGDĐT-GDPT | Prompt Phụ lục II (KHDH) |
|---|---|---|---|
| Cơ quan | Bộ GDĐT | Bộ GDĐT (KT. Bộ trưởng, Thứ trưởng TT Phạm Ngọc Thưởng ký) | KHÔNG rõ tác giả — KHÔNG phải văn bản nhà nước |
| Ngày | 18/8/2026 | 19/8/2026 | không có |
| Bản chất | **QUYẾT ĐỊNH ban hành Khung nội dung giáo dục AI** — normative cho nội dung: mục tiêu, YCCĐ, khung 12 lớp, hệ mã chính thức | **CÔNG VĂN hướng dẫn triển khai** từ 2026-2027, gửi các Sở — chỉ đạo hành chính, KHÔNG phải luật | **prompt LLM vận hành** để soạn Phụ lục III có tích hợp NLS/AI |
| Hạng nguồn | PRIMARY/OFFICIAL | PRIMARY/OFFICIAL (hướng dẫn) | ANECDOTAL/OPERATIONAL — **F10: cấm coi là nguồn nhà nước** |
| Quan hệ | CV 5588 §II.1: nội dung "bám sát… Khung ban hành kèm QĐ 2422" ⇒ 2422 là gốc nội dung, 5588 là cách triển khai | | trỏ thêm TT 02/2025 + CV 3456 (khung Năng lực số) — **ta CHƯA có 2 nguồn này** [OPEN] |
| Neo pháp lý được viện dẫn | | NQ 71-NQ/TW · NQ 57-NQ/TW · **Luật AI 134/2025/QH15** · **Luật BVDLCN 91/2025/QH15** · CT 17/CT-TTg | |

**Source Registry** (checksum SHA-256/16): QĐ 2422 `ce35ebd7c6106d79` · CV 5588 `bddab78dc44df51b`
· KHDH `11358b06c18ff199`. Local: `nguon-chi-thuc/van ban quy dinh/`. Cả hai PDF là BẢN SCAN
(không text layer) → Apple Vision OCR. `legalInterpretationStatus: LEGAL INTERPRETATION / REVIEW PENDING`.

## 2. QĐ 2422 — cấu trúc CHÍNH XÁC đã phát hiện

51 trang: I-Quan điểm (tr.1–3) · II-Mục tiêu chung + từng cấp (tr.3–5) · III-YCCĐ
(phẩm chất/NL chung + **NL đặc thù** tr.6–8 + quan hệ + phương diện tr.8–9) ·
IV-Khung: bảng khái quát Chủ đề×Lớp theo cấp (tr.9–13) + **nội dung cụ thể TỪNG LỚP
1→12** (tr.14–51).

**Hệ định danh CHÍNH THỨC** (văn bản TỰ ĐỊNH NGHĨA ở tr.13–14 — không phải ta bịa):
- 4 thành phần năng lực: **NLa/NLb/NLc/NLd** ↔ 4 mạch nội dung **A/B/C/D**
  (Tư duy lấy con người làm trung tâm · Đạo đức AI · Các kĩ thuật và ứng dụng AI · Thiết kế hệ thống AI).
- 13 chủ đề: A1–A3, B1–B3, C1–C5, D1–D2 (tên CURATED từ header tràn dòng, id SOURCE_EXPLICIT).
- Mã YCCĐ: `<lớp>.<chủ đề>.<MR?><stt>` — ví dụ nguồn cho: `6.A1.2` = cốt lõi thứ 2, `6.A1.MR1` =
  **MỞ RỘNG** thứ 1. ⇒ **core/extended được mã hoá NGAY TRONG mã** (F3 giải quyết tại nguồn).
- ⭐ Nguồn nói mã *"chỉ dùng để định danh"* ⇒ **F4 là luật của chính văn bản**: KHÔNG được suy
  prerequisite/thứ tự dạy từ mã.

**Trích xuất tất định (đếm được):** **267 YCCĐ** = 179 cốt lõi + 88 mở rộng, đủ 12 lớp
(lớp 1: 17+1 → lớp 12: 12+11), 265 SOURCE_EXPLICIT + **2 INFERRED_OCR_CORRECTED**
(tr.36: Vision đọc "9" thành "2" với conf=1.00 — thêm bằng chứng confidence vô dụng làm gate;
khôi phục theo ngữ cảnh section, đánh dấu INFERRED không giả làm nguyên văn). 1 chuẩn hoá
chữ-mã (Ạ→A). Ma trận chủ đề×lớp có cấu trúc xoay thật: A1/D2 phủ cả 12 lớp; B1 chỉ
[1,2,5,6,8], C2 chỉ [4,6,9,10,11,12] — các ô vắng ĐÃ KIỂM là sự thật nguồn (0 hit trong
OCR thô), không phải parser sót.

**Giới hạn ghi thật:** cột "Nội dung" (cột giữa bảng) chưa trích riêng; chính tả OCR trong
text YCCĐ chưa hiệu đính (mã + cấu trúc là phần tất định); tên chủ đề = CURATED.

## 3. KẾT LUẬN THẨM ĐỊNH: QĐ 2422 DÙNG ĐƯỢC làm nguồn authoritative AI Curriculum

Đủ cả 4 tiêu chí: cơ quan ban hành đúng thẩm quyền · phủ trọn lớp 1–12 · định nghĩa
learning outcome CHÍNH THỨC (267 mã) · **hệ mã ổn định, máy-đọc-được, tự văn bản định nghĩa**.
Đây là nguồn hiếm: cấu trúc hơn CẢ SGK (SGK không có mã outcome).

## 4. Ma trận CV 5588 → SAM (POLICY ≠ LEGAL ≠ PRODUCT CHOICE)

| Yêu cầu chính thức (CV 5588) | Loại | SAM hiện có | Kết |
|---|---|---|---|
| "tư duy phản biện, kiểm chứng thông tin", "kiểm chứng kết quả do AI tạo ra" | POLICY | SAM ADMIT_UNCERTAINTY + mời trẻ soát lại SAM + confirm-screen | **MATCH** |
| "đánh giá chú trọng quá trình… mức độ đóng góp thực chất"; "đánh giá dựa trên minh chứng từ quá trình học tập" (§III.3) | POLICY | LearningEvidence 7 loại + 4 chiều + claim-gate; QĐ 2422 tr.8 còn nói "tổng hợp NHIỀU minh chứng" | **MATCH** (hội tụ độc lập) |
| "khai báo" việc dùng AI theo yêu cầu | POLICY | log hỗ trợ đầy đủ ⇒ SAM TỰ SINH được bản khai báo trung thực từ log — **product implication mới, chưa build** | **PARTIAL** |
| "không yêu cầu tài khoản cá nhân/công cụ chưa rà soát"; "không… mua tài khoản, thiết bị" | POLICY (điều kiện trường học) | ADR-006 local-first; chưa có chế độ trường học | **PARTIAL** — ràng buộc PHÂN PHỐI kênh B2School |
| học liệu "có phiên bản NGOẠI TUYẾN" cho vùng hạ tầng yếu | POLICY | **ADR-006 local-first pack = đúng hướng này** | **MATCH** |
| "lồng ghép KHÔNG làm thay đổi hoặc gia tăng YCCĐ của môn học" | POLICY | = bất biến F5 của Task Order — TutorScope đã fail-closed theo stage | **MATCH** |
| bảo vệ DLCN, SHTT, an toàn thông tin; quy trình sự cố | **LEGAL** (Luật 91/2025, 134/2025) | CHILD-SAFETY-PRIVACY-ARCHITECTURE (REVIEW PENDING) | **PARTIAL — LEGAL REVIEW PENDING** |
| 12 tiết cốt lõi/lớp/năm; 3 hình thức triển khai | POLICY (trường học) | N/A cho app gia đình; định cỡ content pack | **NOT_APPLICABLE** (trực tiếp) |
| CONFLICT nào? | | | **KHÔNG phát hiện CONFLICT nào** giữa CV5588/QĐ2422 và doctrine SAM |

⚠️ **F9 giữ nghiêm:** các dòng POLICY là hướng dẫn ngành giáo dục cho TRƯỜNG HỌC —
không tự động là nghĩa vụ pháp lý của một app tư nhân. Không nói "nhà nước bắt buộc SAM…".
Và **KHÔNG claim văn bản nhà nước endorse kiến trúc SAM** — chỉ ghi nhận HỘI TỤ.

## 5. Quyết định kiến trúc graph (falsify 4 phương án) → ADR-008 PROPOSED

- **A. Graph AI RIÊNG — FALSIFY.** Hạ tầng thứ hai = hai code path retrieval, hai claim-gate,
  hai pack layer; trong khi cấu trúc QĐ 2422 (domain→topic→outcome, tiến trình theo lớp) đẳng
  cấu với mô hình đã có (concept→SkillCase→LearningStage). Chi phí không mua được gì.
- **B. AI là domain thường trong graph HỢP NHẤT — SỐNG SÓT** làm nền: outcome 2422 → node
  có mã chính thức first-class; mạch/chủ đề → cấu trúc domain; lớp → LearningStage đã có.
- **C. Overlay thuần xuyên môn — FALSIFY** ở vai trò nguồn cấu trúc: QĐ 2422 là TIẾN TRÌNH
  ĐỘC LẬP có mã riêng, không phải thuộc tính rải trên môn khác. Overlay không chứa nổi 267 mã.
- **D. HYBRID (giả thuyết Founder) — MODIFY:** đúng về NGỮ NGHĨA (tiến trình authoritative
  riêng + cạnh tích hợp xuyên môn — CV5588 §2.2 chính là nhu cầu đó), nhưng KHÔNG cần hạ tầng
  mới: = phương án B + **một loại `CurriculumEdge` mới `aiIntegration`** (outcome AI ↔ objective
  môn học), citable chỉ khi có nguồn. Bất biến F5 nằm ở tầng edge: không có edge = không tích hợp.
- **Ba-graph audit:** kiến trúc hiện tại đã tách đúng CURRICULUM (curriculum/) ≠ CONTENT
  (corpus/ContentUnit) ≠ STUDENT STATE (student/) — QĐ 2422 đi vào CURRICULUM; không phát hiện lẫn.
- **Versioning:** `Provenance.sourceId` + pack version phủ được sourceVersion; **mapping
  bake-at-write-time (WAL-72 replay audit) đã bảo đảm** REPLAY MUST NOT SILENTLY REINTERPRET
  — evidence cũ giữ mã 2422-v2026; khung mới = nguồn MỚI, không ghi đè. Không thêm trường version mới (chưa có bằng chứng cần).

## 6. LearningEvidence — gap analysis 10 loại minh chứng AI-literacy

Kết: **KHÔNG cần EvidenceKind mới.** 10 loại (nhận diện AI, giải thích giới hạn, kiểm chứng
kết quả AI, so sánh nguồn, nhận thiên lệch, bảo vệ DLCN, khai báo trợ giúp, cải tiến sản phẩm
AI, thiết kế hệ AI, quyết định sau AI) đều là **NỘI DUNG của bài tập** (exercise mapped tới
SkillCase thuộc outcome 2422) — không phải loại sự kiện mới: "trẻ kiểm chứng một câu trả lời
AI" = `independentAttempt` trên bài dạng-kiểm-chứng. Gap thật nằm ở tầng CONTENT (chưa có
SkillCase/bài tập AI-literacy nào) — là việc của ingestion, không phải đổi kiến trúc.
Riêng "khai báo trợ giúp": log hiện tại ĐÃ là bản khai báo — thiếu mỗi tầng XUẤT trình bày.

## 7. TeachingAct — ASK_FOR_VERIFICATION…: KHÔNG thêm act mới

Đối chiếu taxonomy WAL-67 (17 act có prior art): ASK_FOR_VERIFICATION/ASK_FOR_SOURCE/
ASK_FOR_REASONING là **tham số nội dung của act hỏi-đáp đã có** (probe/pump/prompt);
REFLECT_ON_AI_USE/DECLARE_ASSISTANCE là **LearningActivity** (nhiệm vụ), không phải nước đi
đối thoại. Giữ ở mức giả thuyết trong doc — không sửa taxonomy khi chưa có bài tập thật cần nó.

## 8. KHDH — use case GIÁO VIÊN: RESEARCH LATER / OUT OF MVP

Prompt vận hành (không phải nguồn nhà nước — F10). Workflow hợp lệ và ĐÚNG nguyên tắc
(giữ nguyên giáo án; không ép tích hợp; "AI hỗ trợ → phân tích → kiểm chứng → tự quyết" —
trùng vòng SAM). Nhưng: persona GIÁO VIÊN chưa có trong scope sản phẩm (student+parent).
**Quyết định: RESEARCH LATER, OUT OF MVP** — giá trị tương lai rõ (Khung 2422 đã máy-đọc-được
là nguyên liệu chính của workflow này). Cần thêm nguồn TT 02/2025 + CV 3456 [OPEN].

## 9. Legal (nối WAL-43) — LEGAL INTERPRETATION / REVIEW PENDING

Luật SHTT VN Điều 15 loại "văn bản quy phạm pháp luật, văn bản hành chính" khỏi phạm vi bảo
hộ quyền tác giả ⇒ khả năng cao TÁI SỬ DỤNG NỘI DUNG QĐ 2422/CV 5588 trong app là hợp pháp —
**NHƯNG đây là diễn giải của agent, KHÔNG tự chứng nhận**: giữ extraction ngoài git cho tới
khi legal review xác nhận; DISTRIBUTION RIGHTS tách khỏi SOURCE STATUS. (Khác hẳn SGK — SGK
là tác phẩm có bản quyền NXB.)

## 10. Falsification F1–F10 — trạng thái

| F | Kết quả |
|---|---|
| F1 mã parse sai | chốt: mã trùng/malformed → LỖI TO; 1 ca Ạ→A đếm công khai |
| F2 outcome nhầm lớp | **BẮT ĐƯỢC 2 ca THẬT** (OCR 9→2, conf=1.00) — khôi phục INFERRED, không giấu |
| F3 core/extended lẫn | giải quyết tại nguồn (MR trong mã) + assert hồi quy |
| F4 mã → prerequisite | cấm bởi CHÍNH nguồn ("chỉ dùng để định danh") — ghi vào schema note |
| F5 ép AI vào môn | bất biến nằm trong CV5588 §2.2 nguyên văn; kiến trúc: không edge = không tích hợp |
| F6 suy diễn đội lốt | trường status SOURCE_EXPLICIT / INFERRED_OCR_CORRECTED trong từng record |
| F7 evidence bị diễn giải lại | bake-at-write-time (WAL-72) phủ; test bổ sung khi có pack thật |
| F8 lộ kiến thức lớp trên | POC truy vấn WAL-92 (tool/poc/query_ai_curriculum.py) |
| F9 hướng dẫn ≠ luật | bảng ma trận tách POLICY/LEGAL/PRODUCT; không nói "bắt buộc" |
| F10 KHDH ≠ nguồn nhà nước | phân loại ANECDOTAL/OPERATIONAL ngay §1 |
