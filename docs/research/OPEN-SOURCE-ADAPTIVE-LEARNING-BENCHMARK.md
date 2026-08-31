# Benchmark OSS adaptive learning — đối chiếu với kiến trúc Workizen

**Đêm 2026-08-31.** Đọc mã nguồn, không chạy repo (§21: source inspection đủ trả lời).
P0 xong (4 repo). P1 (ednet · OpenTutor · KT-PSP) **chưa làm**.

---

# Executive Summary

Ba kết luận làm đổi kiến trúc, xếp theo mức ảnh hưởng:

**① BKT runtime là 14 DÒNG — không cần phụ thuộc nào.**
Toàn bộ engine của OATutor (Berkeley CAHL) là `src/models/BKT/BKT-brain.js`, **14 dòng**.
pyBKT là thư viện **khớp tham số** (EM trên dataset lớn), không phải engine runtime.
Workizen chưa có dữ liệu để khớp ⇒ chỉ cần luật cập nhật. Và pyBKT là **Python** —
không chạy được trên điện thoại; kiến trúc local-first tự loại nó khỏi runtime.

**② BKT KHÔNG biểu diễn được mastery từng phần theo ca — mâu thuẫn với mã tôi vừa viết.**
Chi tiết ở §Architecture Conflicts. Đây là phát hiện quan trọng nhất đêm nay.

**③ `LearningStyle` là anti-pattern, và một repo trong danh sách đang mắc.**
skillcoco định nghĩa `LearningStyle: "visual" | "textual" | …` như thuộc tính bền của
người học. Giả thuyết learning-styles là một trong những ý tưởng **bị bác bỏ kỹ nhất**
trong nghiên cứu giáo dục. Founder đã cảnh báo trong addendum §7; bằng chứng ủng hộ
cảnh báo đó. **REJECT.**

---

# Repository Matrix

| Repo | SHA | Hoạt động | Ngôn ngữ | Vai trò |
|---|---|---|---|---|
| OATutor-SJSU | `2ecca828` | 2025-08-08 | JS/React | tutor loop + BKT runtime + chọn bài |
| pyBKT | `06fc180` | 2026-08-05 | Python/C++ | **khớp tham số** BKT (không phải runtime) |
| skillcoco | `805c6c7` | 2026-08-06 | TS/Rust | học kỹ năng công nghệ, gamification |
| EduStudio | `d5862bd` | 2026-01-06 | Python | vườn mô hình KT/CD, schema dữ liệu |

# License Matrix

| Repo | License mã | Nghiên cứu | Tái dùng mã | Hạn chế thương mại |
|---|---|---|---|---|
| OATutor-SJSU | **MIT** | ✅ | ✅ có ghi công | không |
| pyBKT | **MIT** | ✅ | ✅ | không |
| skillcoco | **MIT** | ✅ | ✅ | không |
| EduStudio | **MIT** | ✅ | ✅ | không |

⚠️ **License của MÃ không phủ DATASET.** EdNet, ASSISTments, Junyi có điều khoản riêng —
phải đọc riêng nếu dùng dữ liệu. Chưa tải dataset nào.

---

# OATutor Findings

`BKT-brain.js` toàn văn — cập nhật hậu nghiệm Bayes + chuyển trạng thái:
```js
if (isCorrect) { num = M*(1-slip);  mg = (1-M)*guess; }
else           { num = M*slip;      mg = (1-M)*(1-guess); }
post = num / (num + mg);
M    = post + (1 - post) * transit;
```

Chọn bài (`defaultHeuristic.js`, 20 dòng): bỏ bài đã làm và bài đã đạt
`MASTERY_THRESHOLD`, chọn bài có **mastery thấp nhất**, hoà thì random.
`experimentalHeuristic.js` khác **đúng một ký tự** (`>` → `<`): chọn bài **sắp thành thạo**.

⭐ **OATutor KHÔNG có prerequisite graph, không có cross-grade, không có case.** Nó chọn
trong một tập bài phẳng theo mastery. ⇒ Curriculum Graph của Workizen là **phần bổ sung
thật**, không phải phát minh lại.

# pyBKT Findings

Tham số: `prior · learns · guesses · slips · forgets`. Biến thể `multilearn` `multiprior`
`multipair` `multigs` — khoá theo một **cột lớp tuỳ ý** (mặc định `template_id`).

`initial_distn = [1 - prior, prior]` ⇒ **một trạng thái ẩn hai mức cho mỗi `skill_name`**.
`multilearn`/`multigs` chỉ đổi **tham số**, không tạo trạng thái riêng.

⭐ `multigs` giải quyết đúng ghi chú của tôi hôm qua: trắc nghiệm 4 lựa chọn có
`P(guess) ≈ 0.25` theo cấu trúc, tự luận gần 0. **Không cần tự nghĩ ra.**

# SkillCoco Findings

Miền khác (kỹ năng công nghệ, không phải K-12). Hai thứ **không nên bắt chước**:
`LearningStyle` bền (§Executive Summary ③) và gamification điểm số
(`+10/quiz · +50/module · +100/milestone`) — tối ưu engagement, trái §F doctrine gốc.

# EduStudio Findings

Schema tương tác tối thiểu, dùng chung cho **mọi** mô hình KT/CD:
```
stu_id · exer_id · label · start_timestamp · cost_time · cpt_seq
```
⭐ **`cpt_seq` là token_seq** — một bài tập ánh xạ **NHIỀU** concept. Đó là Q-matrix, và
nó là giả định nền của cả họ mô hình. `cost_time` là trường hạng nhất ở mọi dataset.

Vườn mô hình: KT (`dkt` `akt` `dkt_forget` `deep_irt` `dimkt` `gkt`…) · CD (`dina` `irt`
`ncdm` `cdgk`…). Đáng chú ý: **`gkt`** (Graph KT) dùng đồ thị khái niệm — gần Workizen nhất.

**Trả lời §8:** schema Workizen hôm nay **KHÔNG khoá cửa**, với một điều kiện: evidence
phải ghi `concept_ids` **dạng danh sách** kèm cách quy công/quy lỗi, và phải có
`cost_time`. Thiếu hai thứ đó thì không mô hình nào ở trên dùng được dữ liệu của ta.

---

# Architecture Conflicts

## ⭐⭐ XUNG ĐỘT 1 — mastery đặt ở Concept thì không biểu diễn được caseTransitionGap

**CURRENT:** tôi viết mastery gắn vào `Concept` (`quy-dong`), SkillCase chỉ dùng để lọc
phương pháp.

**EVIDENCE:** BKT có **một** trạng thái ẩn cho mỗi `skill_name`. Đặt
`skill_name = Concept` thì học sinh có **một** con số mastery cho `quy-dong`.

**PROBLEM:** không thể biểu diễn *"vững ca chia hết, chưa vững ca không chia hết"* — mà
đó chính là `caseTransitionGap` tôi vừa dựng chốt vàng cho. **Mã hiện tại tự mâu thuẫn:**
`DiagnosticOutcome.caseTransitionGap` tồn tại, nhưng mô hình mastery không có chỗ chứa
bằng chứng để kết luận nó.

**PROPOSED:** mastery đo **theo SkillCase**; mastery của Concept là **giá trị suy ra**
(tổng hợp từ các ca).
```
skill_name (BKT) = SkillCase          ← nơi có trạng thái ẩn
Concept.mastery  = f(các case của nó) ← suy ra, không lưu độc lập
```
Giữ nguyên bất biến "concept identity xuyên lớp": *ca* thuộc về *concept*, và concept
vẫn là một, không tách thành `grade4-` / `grade5-`.

**CONSEQUENCE:** ✅ biểu diễn được mastery từng phần · ✅ dùng thẳng BKT chuẩn ·
✅ hợp Q-matrix của EduStudio · ⚠️ cần luật tổng hợp case→concept (chưa có evidence chọn
luật nào; đề xuất khởi đầu: **min**, vì "vững nhất ở ca yếu nhất" là phát biểu an toàn
cho một đứa trẻ) · ⚠️ ca chưa có bằng chứng phải là `unknown`, không phải 0.

## XUNG ĐỘT 2 — misconception không lấy được từ corpus

Đo trên SGV (35 trang): **không có** tài liệu nào ghi lỗi sai thường gặp.
⇒ `Misconception` là **evidence tích luỹ lúc chạy**, không phải entity trích từ sách.
Ngày ra mắt sẽ có **tập rỗng** — thiết kế phải chạy được với tập đó.

---

# Ma trận quyết định

| Mẫu hình | Nguồn | Quyết định |
|---|---|---|
| Luật cập nhật BKT (14 dòng, viết bằng Dart) | OATutor | **ADOPT NOW** |
| `multigs` — guess/slip theo dạng bài | pyBKT | **ADOPT PRINCIPLE** |
| Chọn bài theo mastery thấp nhất + ngưỡng | OATutor | **ADOPT PRINCIPLE** |
| Q-matrix: exercise → nhiều concept | EduStudio | **ADOPT NOW** (schema) |
| `cost_time` là trường hạng nhất | EduStudio | **ADOPT NOW** |
| mastery theo SkillCase, concept là suy ra | phân tích BKT | **POC** |
| pyBKT làm phụ thuộc runtime | pyBKT | **REJECT** — Python, không chạy trên máy |
| Khớp tham số ngoại tuyến bằng pyBKT | pyBKT | **RESEARCH LATER** — khi có dữ liệu thật |
| `forgets` / spaced repetition | pyBKT `dkt_forget` | **RESEARCH LATER** |
| Graph KT | EduStudio `gkt` | **RESEARCH LATER** |
| DKT / AKT | EduStudio | **REJECT** cho V1 |
| `LearningStyle` bền | skillcoco | **REJECT** — giả thuyết đã bị bác bỏ |
| Điểm gamification | skillcoco | **REJECT** — tối ưu engagement |

# Workizen đang phát minh lại thứ gì?

**Có một:** tôi định tự nghĩ cách xử lý `P(guess)` khác nhau giữa trắc nghiệm và tự luận.
pyBKT đã có `multigs` từ lâu.

**Không phải phát minh lại:** Curriculum Graph · SkillCase · cross-grade prerequisite ·
ràng buộc sư phạm cho method. **Không repo nào trong bốn repo có những thứ này.**
OATutor gần nhất về tutor loop nhưng chọn bài trong tập phẳng.

# Chưa làm

P1: ednet (event taxonomy) · OpenTutor · KT-PSP (process-level KT — có thể ảnh hưởng
mạnh tới Camera Tutor). Chưa chạy repo nào. Chưa tải dataset nào.
