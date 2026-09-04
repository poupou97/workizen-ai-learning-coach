# SAM Learning Visualizer — research + challenge (Founder Product Addition, 2026-09-04)

**Status:** RESEARCH DONE, WAL-185 shipped, Founder đã review (§9). **CAPABILITY HYPOTHESIS
VẪN MỞ — CHƯA CHỨNG MINH TOÀN BỘ**, chỉ một phần đã proven. Không code template mới trước
khi corpus có bằng chứng — xem §4. Không xây thêm UI/ticket Visualizer chỉ vì nghiên cứu
này tồn tại — xem §9 điều kiện kích hoạt lại.

**Mode đã theo:** UNDERSTAND INTENT → AUDIT HUB → RESEARCH SAM → CHALLENGE → VERDICT.

## 1. Founder hypothesis (tóm tắt)

SAM nên chọn REPRESENTATION (timeline/mindmap/process/map/comparison/…) dựa trên
content semantics + LearningIntent + subject + age, không ép mọi kiến thức thành đoạn
văn hay Mindmap mặc định. Không phải UI subsystem mới — tái dùng Lesson Workspace hiện có.

## 2. Audit Hub — SỬA hai điểm audit cũ (HUB-TO-SAM-CAPABILITY-REUSE-MATRIX.md) sai

Audit trước (WAL-110) ghi "Smart Canvas 39 files (map-annotate/mindmap)" và "Smart Tools
17 files mindmap" — cả hai **sai vị trí/mô tả**:

- `lib/features/canvas/` thật có **11 files**, là "Canvas Conversation": nét bút → phân
  loại Ý ĐỊNH bằng vision-LLM (question/spelling/math/diagram/pseudocode). Không phải
  visual representation. **NOT SUITABLE**, object-model gắn thẳng `drift` schema của Hub.
- Mindmap thật nằm ở `lib/features/output/` ("Output Engine", **52 files**, ADR-050/054
  bên Hub) — `smart_tools/` thật là registry gọi-hàm chat (calendar/checklist/email/maps),
  không liên quan.

## 3. Output Engine — cái gì tái dùng được, cái gì không

**Đã có (tốt, đáng học pattern):**
- Model TYPED, không phải free text: `MindmapBody{root, branches: List<MindNode>}`,
  `MindNode{label, children, cite}` (`output_bodies.dart:213-254`).
- Pipeline có RETRIEVAL trước khi generate: BM25 trên chunk store đã đánh dấu `[p.N]` →
  `KnowledgeContext{summary,highlights,facts}` → MỘT lần gọi LLM → `OutputSpec` JSON theo
  contract cố định (`output_engine.dart:42-160`, `output_generator.dart:90-103`). Không
  phải "PDF → prompt tự do → hiển thị hết như thật" — đã tránh đúng thứ order §20 cấm.
- Provenance THẬT, per-node: `OutputCitation{docId, docName, page, timeMs}`, chip `[p.N]`
  bấm được (`CiteChip`), **chỉ parse từ page-marker đã được engine xác minh, không đoán
  từ chữ LLM** (`output_spec.dart:127-132`). Đây là pattern nên copy Ý TƯỞNG, không phải
  code.

**KHÔNG có (phá vỡ giả định của Founder order §5/§9.5):**
- **Không có generic renderer.** Mỗi `OutputKind` (summary/infographic/mindmap/…) là MỘT
  widget viết tay riêng, dispatch qua `Map<OutputKind, WidgetBuilder>`
  (`output_view.dart:108-115`). Thêm "Timeline" = thêm kind + generator + typed body +
  widget + markdown writer hoàn toàn mới — không "cắm" được vào renderer có sẵn.
- **Không có graph-layout engine.** Mindmap hiển thị bằng `Column`/`Row`/`Padding` thụt lề
  cố định theo độ sâu — KHÔNG radial, KHÔNG force-directed, dù doc-comment generator nói
  vậy (`render/output_view.dart:779-878` vs `generators/mindmap_generator.dart:6`). Không
  có `graphview` hay lib layout đồ thị nào trong deps.
- `fl_chart` chỉ dùng cho dashboard usage nội bộ (ops), không dùng cho content — biểu đồ
  trong infographic là `Container` cao thấp viết tay.

**Extractability:** ~60-70% (spec/body/render model — cố ý không import Flutter/Riverpod
để chạy được cả trong build script, `output_spec.dart:10-11`) portable dạng tham khảo
kiến trúc; ~30-40% (BM25 retrieval, Riverpod, `drift`) là hạ tầng riêng của Hub, không
mang sang được và cũng không cần — SAM có nguồn sự thật khác hẳn (corpus JSON đã mine,
không phải document upload của người dùng).

## 4. ⭐⭐ Corpus SAM có sẵn cấu trúc gì — bằng chứng quyết định POC nào chạy được NGAY

Kiểm trực tiếp corpus, không suy đoán:

- **Lịch sử (`poc-out/units-k12/04-sgk-lich-su-va-dia-li-4.json`)**: 285 unit, TOÀN BỘ là
  `role: SECTION_TEXT/ACTIVITY/NOTE` + `text` OCR thô, nhiễu (vd. "tuyến Huyết Xác định
  nhiệm vụ học tập nguồn từ đâu?"). **KHÔNG có field ngày/sự kiện/nguyên nhân nào tách
  riêng.** Dựng Timeline từ đây HÔM NAY nghĩa là LLM phải tự suy ra ngày/sự kiện từ văn
  bản nhiễu rồi trình bày như sự thật — đúng thứ order §20 cấm ("PDF → giant prompt →
  display as fact"). **ADR-009 (2026-09-01) đã tiên liệu đúng ca này**: *"Map/Timeline/Lab
  vẫn CHƯA tạo cho tới khi corpus chạm Sử/Địa/Lý-Hoá — gate bằng bằng chứng, không bằng
  dự đoán."* Corpus ĐÃ chạm Sử (sách có thật, hiện trên Giá sách), nhưng CHƯA có cấu trúc
  sự kiện — cổng ADR-009 đặt ra **vẫn đúng, chưa mở được**.
- **Khoa học (`KhoaExperiment`, `lib/features/subjects/lesson_index.dart:99-123`)**: ĐÃ
  typed, ĐÃ tách bước — `chuanBi: String`, **`tienHanh: List<String>`** (các bước tiến
  hành, verbatim từ SGK, "thiếu bước ⇒ không thành object"), `duDoan`/`quanSat`, cùng
  `book`/`page`/`lesson` cho provenance. Đây CHÍNH LÀ dữ liệu Process/Flow — sẵn sàng
  NGAY, không cần LLM, không cần trích xuất mới. Tôi đã xác nhận sống trên Nokia thật
  (walk WAL-178 cùng phiên): màn Thí nghiệm hiện đúng CHUẨN BỊ/TIẾN HÀNH/EM QUAN SÁT ĐƯỢC
  từ đúng field này.
- **Địa lý (`DiaMap`, `lesson_index.dart:126+`)**: bìa bản đồ SGK đã crop (`SOURCE_ASSET`,
  human-curation), `asset`/`caption`/`questions`/`pagePdf` — dữ liệu Map/Spatial sẵn sàng
  NGAY, cũng không cần LLM.

**Kết luận: đảo cặp POC đề xuất trong order §24.** Không dùng "A. History Timeline" vì
corpus chưa đủ cấu trúc (đúng gate ADR-009). Dùng **Khoa học Process/Flow** (đã typed,
đã verbatim, đã có provenance) làm case đầu; **Địa lý Map/Spatial** (`DiaMap`, cũng sẵn
sàng, và khác HẲN hình dạng dữ liệu — ảnh+annotation, không phải chuỗi bước) làm case
falsify thứ hai. Cả hai — ZERO fabrication, zero LLM-required cho structure, provenance
có sẵn ngay từ model hiện tại.

## 5. Kiến trúc — KHÔNG xây Representation Resolver song song

SAM đã có ĐÚNG hình dạng vấn đề này rồi: **ADR-009 (`resolveSurface()`)** — chuỗi
`LearningActivity (ngữ nghĩa) → resolveSurface() (điểm ánh xạ DUY NHẤT) → Interaction
Surface (widget)`. Council order §19's "VisualRepresentationRequest → Plan → VisualModel →
Renderer" là **cùng một hình dạng**, khác tên. Xây một resolver mới song song sẽ tạo HAI
điểm ánh xạ semantics→widget trong cùng một app — đúng thứ ADR-009 tự cảnh báo
("resolveSurface có thể phình khi nhiều môn — tách theo subject-family adapter", không
phải "thêm resolver thứ hai").

**Quyết định kiến trúc**: mở rộng family Surface đã có, không phải xây layer mới.
`resolveSurface()`/`LearningActivity` hiện KHÔNG dùng cho khối Khoa học/Địa lý (chúng đi
qua `LessonActivity`/`ExperimentActivity` — taxonomy khác, đã ghi nhận từ P0 audit
WAL-182: WAL-97 là taxonomy song song, ngắt kết nối với luồng thật). Vì vậy: thêm một
NHÁNH nhỏ, cùng tinh thần (typed input → MỘT hàm chọn representation → widget), gắn vào
ĐÚNG chỗ `_activityAction`/`ExperimentActivity` đã sống (`subject_home_screen.dart`),
KHÔNG hồi sinh `resolveSurface()` (đã bị bỏ vì lệch luồng thật — xem WAL-182 reconciliation
2026-09-04) và KHÔNG tạo resolver hoàn toàn mới.

## 6. Trace ≠ Evidence — tiền lệ đã có, không cần luật mới

ADR-009 đã có CHÍNH XÁC pattern cần: **READ gate** của Reader — "đọc xong KHÔNG phát
LearningEvent (đọc ≠ mastery)". Xem một Process/Flow hay Map là TRACE theo đúng khuôn
này — không gọi `validateCandidateEvidence`. Chỉ khi trẻ TƯƠNG TÁC thật (xếp thứ tự bước,
điền ô thiếu) mới tạo `CandidateEvidence` — dùng ĐÚNG cổng đã có (WAL-178), không hệ
tính riêng.

## 7. CHALLENGE — trả lời §22

- *"Generic Mindmap có đủ chưa?"* — KHÔNG: corpus Khoa học/Địa lý có cấu trúc RÕ RÀNG
  không phải cây phân loại (chuỗi bước; ảnh+điểm đánh dấu) — ép vào Mindmap mất đúng
  hình dạng dữ liệu.
- *"Hub renderer tái dùng được không?"* — KHÔNG nguyên khối (không generic, không layout
  engine) — chỉ tái dùng Ý TƯỞNG (typed body + citation chip), không tái dùng code.
- *"Timeline cần typed model riêng?"* — CÓ, và corpus CHƯA sẵn sàng cấp dữ liệu cho nó —
  hoãn, không xây trước bằng chứng (đúng luật ADR-009 đã có).
- *"Tự động chọn representation có sớm không?"* — CÓ, với >2 template — bounded POC chỉ
  chứng minh 2 case (Process/Flow, Map), KHÔNG xây bộ chọn tự động 15 template ngay.
  Ở POC này, mapping content→template gần như 1-1 theo LOẠI ACTIVITY đã có
  (`ExperimentActivity`→Process, `DiaMap`-backed activity→Map) — resolver "thật" (đọc
  content semantics để chọn) là việc SAU KHI có ≥3 template thật, không phải trước.

## 8. Verdict

**B — ACCEPT WITH CHANGES.**

1. Đảo cặp POC: Khoa học Process/Flow + Địa lý Map/Spatial (KHÔNG History Timeline —
   corpus chưa đủ cấu trúc, đúng gate ADR-009 đã đặt).
2. Không xây Representation Resolver mới — mở rộng đúng chỗ `_activityAction` đã sống,
   cùng tinh thần ADR-009, không hồi sinh `resolveSurface()`.
3. Tái dùng Ý TƯỞNG kiến trúc Output Engine (typed body, citation chip, retrieval-trước-
   generate nếu sau này cần LLM) — KHÔNG import code Hub (30-40% là hạ tầng Hub-specific,
   phần còn lại vẫn cần viết lại theo model corpus SAM).
4. TRACE ≠ EVIDENCE dùng đúng khuôn READ gate của Reader (ADR-009) — không luật mới.
5. Age-density: dùng chung nguyên tắc AGE-ADAPTIVE-UX.md đã có (band 1-2/3-5/6-9/10-12),
   không xây engine tuổi riêng cho visualizer.

## 9. Founder Review (2026-09-04) — chốt trạng thái sau WAL-185

**PASS** cho research + WAL-185 (CI xanh, Nokia verify còn hiệu lực). Nhưng khoanh vùng rõ
để không ai đọc nhầm sau này: WAL-185 chứng minh *"SAM giải thích được vì sao một
representation ĐÃ CÓ là phù hợp"* — KHÔNG chứng minh toàn bộ giả thuyết *"structured
curriculum knowledge → reusable, source-grounded representation, tái dùng qua nhiều loại
nội dung khác nhau"*. Giữ SAM Learning Visualizer là **capability hypothesis MỞ**, không
phải hạng mục đã ship xong.

**Đã chứng minh (PROVEN):**
- `ExperimentActivity` → Process representation.
- `DiaMap` → Spatial representation.
- SAM tự giải thích lựa chọn representation (WAL-185).

**CHƯA chứng minh (UNPROVEN) — không xây chỉ để "đóng" giả thuyết, chờ áp lực nội dung thật:**
- Generic representation composition (một renderer nhận nhiều hình dạng khác nhau).
- Automatic semantic template selection (bộ chọn tự động từ nội dung).
- Mindmap education adaptation, Comparison, Cause-Effect, Concept Map, Review Sheet.

**BỊ CHẶN (BLOCKED):** History Timeline — chờ corpus có cấu trúc sự kiện (§4).

**Điều kiện kích hoạt lại** (audit kiến trúc lần nữa CHỈ KHI một trong các điều sau xảy ra
thật, không suy đoán trước):
- xuất hiện case thứ BA thật sự khác hình dạng cả Process lẫn Spatial;
- CÙNG một representation cần dùng lại ở NHIỀU môn khác nhau;
- mapping activity→screen bắt đầu LẶP logic (dấu hiệu cần trừu tượng hoá);
- corpus Lịch sử có cấu trúc sự kiện/ngày tháng thật;
- MỘT nội dung cần representation KHÁC NHAU tuỳ LearningIntent (xem falsification bên dưới);
- hoặc surface hiện có không diễn đạt được một trải nghiệm học tập cần thiết.

**Falsification quan trọng nhất cho tương lai** (chưa ép chạy — chờ corpus cho phép):
CÙNG MỘT nội dung + KHÁC LearningIntent ⇒ KHÁC representation hữu ích. Ví dụ khi corpus
Lịch sử đủ cấu trúc: cùng một bài, PREPARE ⇒ dòng thời gian ngắn + nhân vật chính; REVIEW ⇒
nguyên nhân/kết quả + review sheet gọn; LOOKUP ⇒ representation chi tiết theo nguồn. Đây sẽ
chứng minh giả thuyết Founder SÂU HƠN nhiều so với việc chỉ ánh xạ ActivityType→Screen đã
có — nhưng KHÔNG ép chạy test này trước khi có dữ liệu nguồn thật.

**Doctrine giữ nguyên cho phần còn lại của giả thuyết:** REUSE BEFORE BUILD · SOURCE
STRUCTURE BEFORE VISUALIZATION · NO STRUCTURED FACT ⇒ NO AUTHORITATIVE VISUAL FACT · xây
trừu tượng hoá khi case thứ ba tạo áp lực thật, không xây trước.
