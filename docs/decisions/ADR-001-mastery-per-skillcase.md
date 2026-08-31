# ADR-001 — Mastery đo theo SkillCase, mastery của Concept là giá trị suy ra

**Ngày:** 2026-08-31 (overnight run) · **Trạng thái:** ACCEPTED (L2, agent tự quyết)
**Bằng chứng:** đọc mã pyBKT + OATutor · `OPEN-SOURCE-ADAPTIVE-LEARNING-BENCHMARK.md`

---

## CURRENT

Mastery gắn vào `Concept` (`quy-dong`). `SkillCase` chỉ dùng để **lọc phương pháp**
(`TutorScope`), không mang trạng thái học tập.

## EVIDENCE

BKT — cả bản pyBKT lẫn bản 14 dòng của OATutor — giữ **một trạng thái ẩn hai mức cho mỗi
`skill_name`**: `initial_distn = [1 - prior, prior]`. Các biến thể `multilearn` /
`multigs` chỉ thay đổi **tham số** theo lớp ngữ cảnh, **không tạo trạng thái riêng**.

## PROBLEM

Nếu `skill_name = Concept` thì học sinh có **một** con số mastery cho `quy-dong`. Không
có chỗ nào chứa được phát biểu *"vững ca chia hết, chưa vững ca không chia hết"*.

Nhưng đó **chính là** `DiagnosticOutcome.caseTransitionGap` mà tôi đã dựng chốt vàng cho
ở `4f74e23`. ⇒ **Mã hiện tại tự mâu thuẫn:** có một chẩn đoán mà mô hình trạng thái
không thể sinh ra bằng chứng để kết luận. Đây là lỗi logic, không phải lựa chọn thiết kế.

Bằng chứng nguồn cho thấy mâu thuẫn này có thật, không phải giả tưởng: SGV Toán 4 giới
hạn Bài 57 vào *"trường hợp có một mẫu số chia hết cho mẫu số còn lại"*, còn SGK Toán 5
dạy ca *"không chia hết"*. Một học sinh học xong lớp 4 **đúng là** vững ca này và chưa
gặp ca kia.

## PROPOSED

```
skill (đơn vị BKT)  = SkillCase       ← nơi giữ trạng thái ẩn
Concept.mastery     = f(các ca của nó) ← SUY RA, không lưu độc lập
```

Bất biến **giữ nguyên**: concept identity xuyên lớp. Ca thuộc về concept; concept vẫn là
một, không tách `grade4-` / `grade5-`. Thay đổi là **nơi đặt trạng thái**, không phải
danh tính khái niệm.

Luật tổng hợp khởi đầu: **min các ca CÓ bằng chứng**.
Lý do chọn `min`: với một đứa trẻ, *"em ấy vững nhất ở mức của ca yếu nhất"* là phát biểu
an toàn. `mean` sẽ giấu một ca hỏng sau một ca vững — đúng thứ ta đang cố tránh.
⚠️ Chưa có bằng chứng thực nghiệm chọn `min` thay vì luật khác. Ghi là **giả thuyết**.

Ca **chưa có bằng chứng** là `unknown`, **không phải 0**. Chưa gặp ≠ làm sai.

## CONSEQUENCE

✅ biểu diễn được mastery từng phần · ✅ dùng thẳng BKT chuẩn, không chế biến ·
✅ hợp Q-matrix của EduStudio (một bài tập → nhiều concept) ·
✅ `caseTransitionGap` nay **suy ra được** thay vì chỉ tồn tại như một tên gọi

⚠️ Số lượng đơn vị mastery tăng (mỗi concept vài ca). Với K-12 vẫn nhỏ — không phải lo.
⚠️ Cần luật tổng hợp; `min` là giả thuyết cần đo lại khi có dữ liệu thật.
⚠️ Chốt vàng ở `bc205bb` và `4f74e23` **giữ nguyên hiệu lực** — ADR này không đụng tới
ranh giới sư phạm, chỉ đụng tới nơi đặt trạng thái.
