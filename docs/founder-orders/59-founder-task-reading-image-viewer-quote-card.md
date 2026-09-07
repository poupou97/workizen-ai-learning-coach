# FOUNDER TASK ORDER — PR #123
## READING EXPERIENCE × IMAGE VIEWER × QUOTE CARD × PERSON ASSETS

PR #123 · CI GREEN · MERGE CHƯA ĐƯỢC PHÉP.

Mục tiêu: (1) ảnh trong bài xem chi tiết được; (2) tap → fullscreen zoom/pan;
(3) câu nói danh nhân render dạng Quote; (4) quote có portrait khi được;
(5) thiếu ảnh local ĐƯỢC PHÉP tìm web; (6) ảnh web phải có provenance/licence/
identity; (7) KHÔNG tự gán câu nói; (8) bám concept vừa audit; (9) kiểm Nokia.

P0 READING MODE IMAGE — ảnh không zoom được là UX gap, phải sửa.
P0.1 TAP → FULLSCREEN: pinch zoom · zoom in/out · pan · double-tap zoom ·
     reset · close/back. Gesture tự nhiên Android. Không xây image editor.
P0.2 READING CONTINUITY: back phải giữ ĐÚNG vị trí đọc, không reset lesson.
P0.3 INLINE QUALITY: đúng aspect ratio, không stretch/crop mất nội dung,
     affordance nhẹ (không nút ZOOM to trên từng ảnh).
P0.4 GENERIC LearningImageViewer — không hardcode Bài 17; reuse được.
P0.5 LICENCE KHÔNG ĐỔI: CAN DISPLAY INTERNALLY != CAN DISTRIBUTE;
     ZOOM CAPABILITY != DISTRIBUTION RIGHT. Không nới D4 vì có viewer mới.

P1 QUOTE: đủ semantic/source ⇒ KHÔNG render như body paragraph, render QUOTE CARD.
P1.1 Composition: portrait · quote mark · quote text · tên · nguồn · năm ·
     provenance. Educational, child-friendly, respectful. Không social poster.
P1.2 QUOTE TRUTH: QUOTE-LIKE TEXT != VERIFIED ATTRIBUTED QUOTE. Không để LLM
     đoán người nói rồi gắn tên. Chưa xác minh người nói ⇒ render «TRÍCH DẪN»
     nhưng KHÔNG tự thêm tên.
P1.3 KHÔNG TỰ SỬA QUOTE: không viết lại/hiện đại hoá/ghép câu/tự dịch rồi gọi
     là nguyên văn/thêm attribution suy đoán. Dùng ngoặc kép ⇒ phải trace được.
P1.4 QUOTE BLOCK MODEL: không `if text.startsWith("“")` trong Widget; dùng
     typed semantic block; không tạo parallel architecture.

P2 PORTRAIT: asset priority APP-OWNED → PUBLIC DOMAIN → OPEN LICENSE →
   TRUSTWORTHY OFFICIAL → WEB CANDIDATE → APPROVED ILLUSTRATION → NO PORTRAIT.
P2.1 ĐƯỢC PHÉP SEARCH WEB khi thiếu local. Search chỉ để DISCOVER; thumbnail
     kết quả KHÔNG phải source.
P2.2 Ưu tiên Wikimedia Commons/archive/museum/government/university/library/
     encyclopedia/official/public-domain.
P2.3 KHÔNG lấy ảnh mù quáng; phải truy về ORIGINAL SOURCE PAGE; lưu metadata:
     personId, personName, imageUrl, sourcePageUrl, sourceName, author, licence,
     licenceUrl, retrievedAt, portraitType, usageStatus.
P2.4 USAGE STATUS: APPROVED_FOR_PRODUCT · INTERNAL_ONLY · UNKNOWN_RIGHTS ·
     REJECTED. Chỉ APPROVED_FOR_PRODUCT là production asset.
     FOUND ON INTERNET != FREE TO SHIP.
P2.5 VERIFY IDENTITY: không dựa filename/alt/title. SEARCH RESULT != VERIFIED
     IDENTITY. Không xác minh được ⇒ NO PORTRAIT tốt hơn WRONG PORTRAIT.
P2.6 PHÂN LOẠI: HISTORICAL_PHOTO · PORTRAIT_PHOTO · PORTRAIT_PAINTING ·
     ILLUSTRATION · AI_GENERATED_ILLUSTRATION. Không trình bày illustration
     như historical photo.
P2.7 QUOTE / PERSON / IMAGE là BA truth riêng. Verified quote + verified person
     + no eligible portrait ⇒ QUOTE CARD WITHOUT PORTRAIT. Không block quote
     vì thiếu ảnh.
P2.8 PERSON ASSET REUSABLE: Person{identity, portrait, portraitType, source,
     licence, usageStatus}; Quote → Person → Portrait.

P3 WEB IMAGE cho learning illustration khi local không có (nhân vật, địa danh,
   bản đồ, hiện tượng, sinh vật, công trình, thiết bị, tác phẩm).
P3.1 KHÔNG dùng ảnh chỉ vì «đẹp» — kiểm RELEVANCE/IDENTITY/SOURCE/LICENCE/CONTEXT.
P3.2 KHÔNG MASS DOWNLOAD, không crawl corpus, không build image library cho
     3.679 bài. Chỉ GENERIC PIPELINE + BOUNDED VERTICAL SLICE.

P4 CACHE/PACKAGING: không hotlink tuỳ tiện; APPROVED_FOR_PRODUCT qua asset
   pipeline giữ metadata; INTERNAL_ONLY phải mang status theo asset.

P5 CONCEPT ALIGNMENT: kiểm concept trước khi thiết kế viewer/quote/portrait.
P5.1 GIỮ token vừa audit: purple ≈ #6A36EE, card radius ≈ 14, button ≈ 15–16,
     subject colors có evidence. Font: CONCEPT UNRESOLVED, APP system Roboto,
     KEEP TEMPORARILY. Không đoán font, không research web tìm font.
P5.2 Quote Card cùng Design Language với Home/Timetable/Reading/Workspace.

P6 READING MODE UX AUDIT trên Nokia (image size, aspect, caption, density,
   hierarchy, quote visibility, source display, spacing, continuity, viewer nav).
   Chỉ sửa gap liên quan Reading UX; không redesign toàn Lesson Workspace.

P7 TESTS: image (tap→viewer, pinch, pan, double-tap, close, reading position,
   aspect, missing image, licence metadata) · quote (verified→card, portrait,
   no-portrait, unknown attribution, provenance, source, paraphrase≠verbatim,
   person reuse) · web image (approved usable, internal-only không thành
   production, unknown-rights không tự lên approved, metadata giữ, portraitType
   giữ, thiếu asset không vỡ bài).

P8 NOKIA: build đúng HEAD PR #123; đi trọn LESSON→ĐỌC→TAP→FULLSCREEN→PINCH→
   PAN→DOUBLE TAP→BACK→SAME POSITION. Evidence: inline, fullscreen, zoomed,
   Quote Card, Quote Card + portrait.
P8.1 QUOTE VERTICAL SLICE end-to-end. Corpus chưa đủ điều kiện ⇒ KHÔNG fake rồi
   gọi production-ready; được dùng CLEARLY LABELLED FIXTURE/PROTOTYPE.
   Report ghi REAL vs FIXTURE vs PROTOTYPE.

P9 JIRA: kiểm trước khi tạo; có issue Reading/Media/Quote thì update; chưa có
   thì tạo bounded backlog (Reading Image Viewer, Quote Card, Person Asset/
   Portrait provenance, Web Image Asset Pipeline). Không tạo hàng chục ticket.
   Implementation xong mà content chưa có ⇒ COMPONENT IMPLEMENTED,
   CONTENT COVERAGE REMAINS.

P10 REPORT 13 mục.

FOUNDER RULES: LOCAL IMAGE NOT FOUND → WEB SEARCH ALLOWED. Nhưng
FOUND ON INTERNET != FREE TO SHIP · SEARCH RESULT != ORIGINAL SOURCE ·
SEARCH RESULT != VERIFIED IDENTITY · CORRECT PERSON IMAGE != VERIFIED QUOTE ·
QUOTE-LIKE TEXT != VERIFIED ATTRIBUTED QUOTE · ZOOM CAPABILITY != DISTRIBUTION
RIGHT.

KHÔNG MERGE. READY FOR FOUNDER REVIEW.
