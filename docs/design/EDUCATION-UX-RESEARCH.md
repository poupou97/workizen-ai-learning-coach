# Nghiên cứu UX giáo dục — pattern bên ngoài + DNA Workizen

**Ngày:** 2026-09-01 · **Phương pháp:** web research sản phẩm hiện hành + đọc source OATutor/skillcoco
+ đọc tài sản nghiên cứu Workizen nội bộ (Hub `docs/ux/*`, DeepTutor research, Tổng Tài design tokens).
**Luật:** trích NGUYÊN TẮC TƯƠNG TÁC, không clone giao diện.

## 1. Trả lời 11 câu hỏi nghiên cứu của Founder

| Câu hỏi | Trả lời từ bằng chứng | Nguồn |
|---|---|---|
| Học sinh biết PHẢI LÀM GÌ thế nào? | Một hành-động-kế-tiếp DUY NHẤT do hệ đề xuất, không phải menu. WAL đã có `AdaptiveDecision` — Mission Center chỉ việc hiển thị nó. Duolingo chứng minh cả mặt tốt (path tuyến tính rõ) lẫn mặt xấu (engagement-first làm GIẢM học thật khi nới luật streak 2024) | Duolingo case study + trophy.so; domain WAL |
| Tránh thành "blank chatbot"? | Tutor xuất hiện TRONG ngữ cảnh bài đang làm, mở lời bằng câu hỏi về bài đó ("Con thử tới đâu rồi?" — pattern Khanmigo), không có ô hỏi tự do làm mặc định. Board `intro-1` cũ ghi "Ask Tutor — Hỏi bất kỳ" phải sửa thành tutor-trong-ngữ-cảnh | Khanmigo Socratic restraint |
| Gợi ý lộ dần thế nào? | Thang: nhắc hướng → scaffold (CÂU HỎI CON phải trả lời — OATutor) → làm mẫu một bước → lời giải. Mỗi nấc là một sự kiện log (F3); scaffold sinh bằng chứng thay vì chỉ tiêu thụ | OATutor HintSystem + WAL SupportLevel |
| Hiện mastery không giả-chính-xác? | KHÔNG hiện số (0.87 là fake precision). Hiện mức + độ phủ: "vững 2/3 dạng, còn 1 dạng chưa thử". ConceptClaim 6 mức là đúng vocabulary hiển thị; thanh % là anti-pattern | Founder Decision 1; Khan mastery levels |
| Hiện lỗ hổng mà trẻ không thấy "mình dốt"? | Ngôn ngữ dạng-bài chứ không ngôn ngữ năng lực: "dạng này MỚI với con" (caseTransitionGap ≠ hỏng); thất bại có mặt định danh mascot "Không sao!"/"Mình thử lại nhé!"; không đỏ, không điểm trừ hiện hình | domain caseTransitionGap + mascot sheet + nghiên cứu rejection-sensitivity |
| Daily mission cấu trúc? | 3 khối từ domain thật: ①ôn tới hạn (ReviewSchedule) ②tiếp tục mạch đang học (AdaptiveDecision) ③một thử-thách-phủ (ca chưa quan sát — tăng coverage). Mission = bằng chứng cần thu, không phải nội dung cần xem. skillcoco: SR queue ngang hàng nội dung mới | skillcoco README; domain WAL |
| Camera → tutoring chuyển tiếp? | Photomath: scan→nhận diện→bước giải là chuẩn kỳ vọng; WAL khác biệt ở chỗ CHÈN chẩn đoán trước khi dạy (nhận ca → tra mastery → decide) và fail-closed khi mờ ("chưa chắc — chụp lại gần hơn?") thay vì đoán | Photomath flow + WAL caseUnknown |
| Voice cho trẻ nhỏ? | Điểm vào hẹp: ĐỌC gợi ý/lời giảng thành tiếng (OATutor có sẵn math-to-speech per-hint), không phải voice-chat tự do. POC riêng | OATutor ttsPlayer |
| AI bị ràng buộc dạy-không-đưa-đáp-án hiển thị ra sao? | Khanmigo: hỏi "đã thử gì?" thay vì trả lời. WAL mạnh hơn: ràng buộc nằm TRONG kiến trúc (TutorScope lọc trước) — UX chỉ cần trung thực: "Tớ sẽ gợi ý từng bước, không đưa đáp án" nói MỘT lần lúc onboarding, sau đó hành vi tự chứng minh | Khanmigo + TutorScope |
| Parent UX nói về ĐỘ BẤT ĐỊNH? | Ước lượng phải trông như ước lượng (nguyên tắc Hub: "~$0.03 không bao giờ trông như hoá đơn"). Claim 6 mức + citation ("3 lần tự làm, gần nhất 30/8") thay vì %; "chưa đủ bằng chứng" là một trạng thái HIỂN THỊ ĐƯỢC, không phải màn hình trống | Hub honest-states + ADR-005 |
| Parent trả lời "tối nay giúp con gì?" trong vài giây? | Màn hình phụ huynh mở bằng đúng MỘT khuyến nghị (từ `weakestObservedCases`/`reviewDue` + ParentExplanation), chi tiết xếp sau. Khan/IXL cho thấy dashboard nhiều-số làm loãng; "next steps suggestion" là phần được khen | Khan parent dashboard, IXL analytics |

## 2. DNA Workizen tái dùng (đọc từ tài sản thật)

| Nguồn | Nguyên tắc mang sang WAL |
|---|---|
| Hub `01-ux-principles.md` | Honest states (ước lượng trông như ước lượng — thành luật hiển thị confidence) · Calm by default (không badge đỏ) · fast-to-value · decline là đường hạng nhất · one-hand |
| Hub `design-principles.md` | "Warm world × serious tool" · **luật mascot: được ở màn thân thiện, CẤM ở màn nghiêm trọng** — WAL: mascot cấm ở màn claim bằng chứng với phụ huynh & màn quyền riêng tư; "cute but not childish, never baby-talk" |
| Tổng Tài `DESIGN-TOKENS.md` | Màu-theo-miền để định vị nhận thức + **bài học WCAG đo được: màu nền -500 ≠ màu chữ -700** (2.31:1 vs 4.5:1) — WAL áp ngay từ token đầu tiên |
| Hub DeepTutor research | Learner model = vài trăm dòng Dart thuần (đã thành sự thật: kernel WAL); DeepTutor = blueprint tầng learning-science, REFERENCE-ONLY |
| Hub snap-and-understand | Chuỗi camera đã local phần lớn trên Hub (ML-Kit OCR, chunking); bar "không thay pipeline nếu chưa benchmark thắng" — trùng doctrine WAL |
| ADR-060 mission-control-ui-doctrine (compute) | Tồn tại doctrine Mission Control cấp workspace — đọc khi làm Mission Center để không phát minh ngược |

## 3. Pattern BÁC (không mang vào WAL)
- **Engagement-first metrics** (streak dễ hơn ⇒ ở lại app nhiều hơn, HỌC ÍT ĐI — Duolingo 2024, đo được). Mission của WAL đo bằng BẰNG CHỨNG THU ĐƯỢC, không bằng ngày mở app.
- **Thanh % mastery** — fake precision, vi phạm Decision 1.
- **Điểm số real-time đập vào mặt** — hại trẻ rejection-sensitive (ghi nhận từ nghiên cứu parent-dashboard).
- **Blank chatbot làm bề mặt chính** — lệnh Founder trực tiếp.
- **LearningStyle** như thuộc tính bền của trẻ — đã REJECT bằng văn liệu.

Sources: [Khanmigo reviews](https://aiteacherhacks.com/khanmigo-review/) · [kidsaitools Khanmigo](https://www.kidsaitools.com/en/articles/khanmigo-review-parents-complete-2026) · [Photomath](https://photomath.com/) · [Photomath wiki](https://en.wikipedia.org/wiki/Photomath) · [Duolingo gamification case study](https://trophy.so/blog/duolingo-gamification-case-study) · [Why gamification fails 2026](https://medium.com/design-bootcamp/why-gamification-fails-new-findings-for-2026-fff0d186722f) · [Khan parent dashboard](https://support.khanacademy.org/hc/en-us/articles/360039664491) · [OpenEd IXL](https://opened.co/tools/ixl)
