# WAL-67 — TeachingAct: đối chiếu văn liệu + falsification Method↔Act (CHƯA ADR)

**Ngày:** 2026-09-01 · [ACADEMIC]=văn liệu (kiểm trích dẫn khi ADR) · [OSS]=mã đã đọc · [WAL]=domain hiện có

## 1. Ánh xạ 17 act ứng viên của Founder ↔ construct có sẵn trong văn liệu

| Act ứng viên | Prior art | Ghi chú |
|---|---|---|
| OBSERVE / WAIT | [ACADEMIC] wait-time (Rowe); contingent tutoring chỉ can thiệp khi cần (Wood) | im lặng là một nước đi có tên |
| ASK / PROMPT_RECALL | [ACADEMIC] AutoTutor **pump** ("What else?") / **prompt** (mớm từ cụ thể) | tách pump/prompt của AutoTutor tinh hơn ASK gộp |
| DIAGNOSTIC_PROBE | [ACADEMIC] model tracing (Anderson); CAT item-selection; [WAL] isolateSkills đã là probe thô | hỏi vì THÔNG TIN, không vì đúng-sai |
| SMALL_HINT / STRATEGIC_HINT | [ACADEMIC] AutoTutor **hint**; [OSS] OATutor hint ladder + sub-hints tuần tự | hai mức của một thang |
| CONTRAST_CASES | [WAL] `LearningAction.contrastCases` (đã có test!) | WAL đi trước văn liệu tutor-move ở act này |
| EXPLAIN_CONCEPT / ASSERTION | [ACADEMIC] AutoTutor **assertion** — nước đi CUỐI chu trình pump→hint→prompt→assertion | giảng là biện pháp cuối, không phải đầu |
| DEMONSTRATE_STEP / WORKED_EXAMPLE | [ACADEMIC] modeling (cognitive apprenticeship, Collins); worked-example effect (Sweller) | |
| ASK_EXPLANATION | [ACADEMIC] self-explanation effect (Chi) | trẻ giảng lại = bằng chứng mạnh |
| ASK_VERIFICATION | [PRIMARY] CV 5588: "kiểm chứng kết quả do AI tạo ra" là YÊU CẦU chính thức | act có chỗ dựa pháp quy |
| REFLECT | [ACADEMIC] reflection (cognitive apprenticeship) | |
| STEP_BACK / YOUR_TURN | [ACADEMIC] **fading** (Collins/Wood) | rút lui là nước đi sư phạm, không phải vắng mặt |
| REVEAL_STEP / REVEAL_ANSWER | [OSS] OATutor bottom-out hint + penalty AnswerReveal; [WAL] SupportLevel.fullSolution | đã có ngữ nghĩa evidence |

**Kết luận 1:** 17/17 act có prior art hoặc đã tồn tại trong WAL — **TeachingAct không phải
phát minh**; đóng góp (nếu có) là RÀNG KIỂU giữa Act ↔ SupportLevel ↔ evidence.

## 2. Falsification Method↔TeachingAct — **M:N XÁC NHẬN**

- **1 Method × N Act** [WAL, dựng được ngay]: method "lấy tích hai mẫu" chở được:
  EXPLAIN (giảng luật) · DEMONSTRATE_STEP (làm mẫu 4×5) · WORKED_EXAMPLE (giải trọn 3/4+2/5)
  · SMALL_HINT ("mẫu chung tìm từ hai mẫu số thế nào nhỉ?") · ASK_EXPLANATION ("vì sao con
  nhân 4 với 5?") · CONTRAST_CASES (so với ca chia hết). SupportLevel hiện tại đã cắt NGANG
  mọi method — bằng chứng cấu trúc rằng trục Act độc lập trục Method.
- **1 Act × N Method** [WAL]: CONTRAST_CASES chạy cho quy-dong (chia hết vs không) VÀ
  so-sanh-so-thap-phan (ba-ca vs khác-độ-dài) — không đổi một dòng ngữ nghĩa act.
- **Act KHÔNG CẦN Method** [quyết định phân tầng]: OBSERVE · WAIT · DIAGNOSTIC_PROBE ·
  REFLECT · STEP_BACK — nước đi thuần sư phạm, Method là tham số TUỲ CHỌN của Act.
  ⇒ quan hệ đúng: `TeachingAct(method?: TeachingMethod)` — không phải Act thuộc Method
  hay Method thuộc Act.

## 3. LearningAction hiện tại LAI ba tầng — khuyến nghị TÁCH (chưa ADR)

Soi từng giá trị [WAL]: `teach/practice/review/advance/rest` = **MỤC TIÊU vòng ngoài**
(outer loop VanLehn — chọn LÀM GÌ TIẾP); `contrastCases` = **nước đi vòng trong** (inner
loop — can thiệp TRONG bài); `diagnosePrerequisite/isolateSkills` = **chiến lược probe**.
Khớp 1:1 khung VanLehn ⇒ kiến trúc đề xuất (falsify ở POC trước khi ADR):

```
outer:  LearningGoal   (teach · practice · review · assess · advance)     ← decide() hiện tại
inner:  TeachingAct    (17 act, có thang assistance)                       ← MỚI — WAL-68 chọn độ sâu
domain: TeachingMethod (đã có, taught-for-case)                            ← tham số tuỳ chọn của Act
```
Tương thích: enum `LearningAction` giữ nguyên (đổi tên là phá 115+ test không lý do);
tầng Act thêm MỚI bên cạnh, ánh xạ dần.

## 4. Checkpoint cho WAL-48 (điều §M đòi)

Wireframe slice ĐƯỢC PHÉP dựa trên: (a) chu trình pump→hint→prompt→assertion làm khung
hội thoại tutor; (b) YOUR_TURN/STEP_BACK là act có thật — SAM lùi lại là tính năng;
(c) mọi act phát ra đều ghi LearningEvent tương ứng (scaffold sinh bằng chứng); (d) độ sâu
act do assistance model chọn (WAL-68). CHƯA được phép: coi taxonomy 17 act là chốt —
tên/mức chờ POC + ADR.
