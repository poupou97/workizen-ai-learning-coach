# ADR-002 — Bảo vệ corpus SGK bằng nhiều lớp, và đính chính cơ chế nguy hiểm

**Ngày:** 2026-09-01 · **Trạng thái:** ACCEPTED (L2, agent tự quyết)
**Bằng chứng:** dry-run `git add -A -n` trên repo cha thật + sandbox 4 ca đo tách lớp

---

## CURRENT

Doctrine hiện hành (`BASE-CLONE-PLAN.md` §Ba điểm, `TEXTBOOK-LICENSING-QUESTIONS.md` §5)
phát biểu: *"một lệnh `git add -A` ở `~/projects` là đủ để đẩy 9,8GB sách bản quyền lên
GitHub công khai."*

Câu đó định hướng sự chú ý vào **lệnh `git add`**. Không lệnh nào trong repo đo lại nó.

## EVIDENCE

**Đo 1 — dry-run trên repo cha thật** (`git add -A -n workizen-ai-learning-coach`, không
đụng index):

```
warning: adding embedded git repository: workizen-ai-learning-coach
add 'workizen-ai-learning-coach/'
```

**Một** entry gitlink. **0 byte corpus.** Git không đệ quy vào repo lồng.

**Đo 2 — sandbox tách từng lớp** (repo cha/con giả, PDF giả):

| Ca | nested `.git` | `.gitignore` con | `git add -A` ở cha thêm gì |
|---|---|---|---|
| A | có | có | không có corpus |
| B | **không** | có | không có corpus |
| C | **không** | **không** | 🔴 **thêm cả PDF** |
| D | có | **không** | không có corpus |

**Đo 3 — lớp thứ ba, tình cờ.** Corpus 9,8GB nằm trong **12 tệp `.zip`**; `.gitignore`
của repo cha có sẵn dòng `*.zip`. Phần **không** phải zip chỉ 6 tệp / 11MB, và đó là văn
bản công khai của Bộ GD&ĐT, không phải SGK của NXBGDVN.

## PROBLEM

Đây đúng cái bẫy `§4.5` đã dạy: **nhiều lớp chắn độc lập cho cùng một kết quả.** Mỗi lớp
một mình đã đủ chặn (ca B và D). Gỡ một lớp **không lộ ra gì**. Ai chỉ thử một ca sẽ kết
luận sai về lớp nào đang chịu lực.

Hệ quả thật của việc mô tả sai cơ chế: người đọc đi canh `git add -A`, trong khi thứ thực
sự mong manh là **sự tồn tại của `.git` con và `.gitignore` con**. Xoá nhầm một trong hai
— re-clone, dọn thư mục, copy corpus ra ngoài ranh giới repo — thì **không lệnh nào báo**.

Nói sai cơ chế tốn kém ngang không cảnh báo. Cùng lỗi với doctrine hết hạn ở `CLAUDE.md`
gốc: một cổng tưởng tượng chặn cứng y như cổng thật.

## PROPOSED

**Giữ nguyên mọi lớp đang có. Không nới lỏng gì.** Bổ sung:

1. **Phát biểu lại rủi ro cho đúng.** Không phải *"`git add -A` đẩy 9,8GB"*, mà: *"corpus
   được ba lớp độc lập che; thảm hoạ chỉ xảy ra khi `.git` con VÀ `.gitignore` con cùng
   mất — và lúc đó không có tín hiệu nào."*
2. **Biến lớp chắn tình cờ thành có chủ đích.** `.gitignore` repo cha chặn corpus hiện chỉ
   nhờ trùng hợp định dạng `*.zip`. Thêm dòng tường minh cho thư mục dự án.
3. **Giữ cả đường dẫn typo cũ** (`workizen-ai-learning-coarch/`) trong lớp chắn của repo
   cha — thư mục cũ có thể tái xuất từ backup, clone cũ, hoặc thao tác tay.

## CONSEQUENCE

✅ Rủi ro được mô tả đúng chỗ mong manh thật · ✅ lớp chắn repo cha thành có chủ đích ·
✅ ma trận 4 ca đo được, tái lập được — không phải suy luận

⚠️ ADR này **không** cho phép nới bất kỳ lớp nào. `TECHNICAL_POC_ALLOWED_BY_FOUNDER` và
`COMMERCIAL_USE_LEGAL_REVIEW_PENDING` **không đổi**.
⚠️ Không lớp nào trong ba lớp có test tự động canh giữ. Đây là bảo vệ theo quy ước, không
phải theo kiểm chứng — ghi nhận là nợ, chưa trả trong ADR này.
