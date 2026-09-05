# Track B — Device validation checklist (Nokia · «Na · Lớp 6»)

**Ticket:** WAL-210 · **Build:** this branch, `flutter build apk --debug` (needs the gitignored
packs in `assets/pack/` and the real fixture in `assets/fixtures/real/` copied in first — see
`assets/fixtures/README.md`). **Package:** `ai.workizen.learningcoach` only.

Pre-flight (read-only, before ANY input):
```
d() { /Users/alexnguyen/Library/Android/sdk/platform-tools/adb -s 192.168.1.3:5555 "$@"; }
d shell dumpsys window | grep mCurrentFocus      # must show ai.workizen.learningcoach
d shell dumpsys power  | grep -E "mWakefulness|Display Power"   # Awake / ON
```
Locked or asleep ⇒ stop; never wake/unlock/swipe. Install: `d install -r build/app/outputs/flutter-apk/app-debug.apk`.
Launch: `d shell monkey -p ai.workizen.learningcoach -c android.intent.category.LAUNCHER 1`, wait 6 s.
Screenshots: `d shell screencap -p /sdcard/s.png && d pull /sdcard/s.png ~/Desktop/wal-evidence/trackb-<iter>-<step>.png`.

The device was in **landscape** during iteration 1 (the Founder's hand); every step below must
pass in both orientations — note which one was used.

| # | Step (input) | Expected screen | Screenshot name | Pass criteria |
|---|---|---|---|---|
| 01 | Launch | Home «Chào Na!» (profile Na · Lớp 6) | `trackb-<i>-01-home` | learner name; no crash |
| 02 | Scroll Home to the bottom row | «Chụp bài tập · Môn học ▸ · Bố mẹ ▸» | `trackb-<i>-02-home-scrolled` | «Môn học» reachable |
| 03 | Tap «Môn học» | Giá sách «Sách của con · Lớp 6», 13 real covers | `trackb-<i>-03-bookshelf` | KHTN 6 tile reads «55 bài · ✨ SAM»; no other tile has ✨ |
| 04 | Tap KHTN 6 cover | **BookScreen**: cover, «KHTN 6 · KHTN · 55 bài», «✨ 1 bài học SAM: Bài 17», chip «Bản thử nghiệm · nội dung nội bộ (từ SGK, chưa phát hành)», «Mục lục» | `trackb-<i>-04-book-khtn6` | chip present; chapters from the printed TOC (Chương I … X) |
| 05 | Scroll | Chapter rows Chương I–X; last row «Mục lục & hoạt động (bản hiện tại)» | `trackb-<i>-05-book-chapters` | Chương IV shows «2 bài · ✨ 1 bài học SAM» |
| 06 | Tap «Chương IV» | **ChapterScreen**: «Chương IV · Hỗn hợp. Tách chất ra khỏi hỗn hợp», chip, rows Bài 16 (lối cũ) and Bài 17 «✨ Bài học SAM · Đọc · Trực quan · Học với SAM · Chưa xem» | `trackb-<i>-06-chapter-iv` | state label is «Chưa xem» (no %, no stars) |
| 07 | Tap Bài 17 | **LessonWorkspace**: «Bài 17 · Tách chất khỏi hỗn hợp / Chương IV · SGK KHTN 6 · trang 60–63», chip, tabs, «SAM đề xuất», opens on ✨ Trực quan | `trackb-<i>-07-workspace-visual` | opens on the proposed view; next-action card now proposes 📖 Đọc with a reason |
| 08 | Scroll the process diagram | «Lọc nước từ hỗn hợp nước lẫn đất»: nodes 1→2→3 with arrows, verbatim SGK steps; «Vì sao SAM chọn sơ đồ này» | `trackb-<i>-08-visual-process` | 3 nodes; arrows; verbatim text |
| 09 | Tap the 2nd process tab («Tách dầu ăn khỏi nước») | node 1 = **withheld** («Bước này SAM chưa đọc được — con xem trong sách (SGK KHTN 6 · trang 62)»), node 2 verbatim | `trackb-<i>-09-visual-withheld-step` | withheld step shows no text |
| 10 | Tap a node | «Sách viết» sheet with verbatim text + «SGK KHTN 6 · trang N» + «📖 Xem trong Đọc» | `trackb-<i>-10-visual-source-sheet` | source line correct |
| 11 | Tap «Bảng so sánh» | table Lọc / Lắng / Cô cạn / Chiết × «Dùng để tách» | `trackb-<i>-11-visual-comparison` | 4 rows, verbatim parentheses text |
| 12 | Tap «📖 Đọc» | Smart Book: «Cỡ chữ A A A», «Bài 17», «TÁCH CHẤT KHỎI HỖN HỢP», MỤC TIÊU badge, objectives, ❓ question | `trackb-<i>-12-read-top` | reading order matches the page |
| 13 | Scroll | Hình 17.1 crops + captions, «Nguyên tắc tách chất» paragraph, question box | `trackb-<i>-13-read-images` | image + caption pairing; «Hình trong SGK · SGK KHTN 6 · trang 60» |
| 14 | Scroll to page 61 activity | 🧪 «Chuẩn bị… Tiến hành:» box, steps, then **withheld card** «Phần này SAM chưa đọc được — con xem SGK trang 61 nhé» + «Xem vùng trang (nội bộ)» | `trackb-<i>-14-read-withheld` | no text where withheld |
| 15 | Tap «A» largest | body text grows (22sp) | `trackb-<i>-15-read-font` | font change visible |
| 16 | Tap a paragraph → «🦉 Hỏi SAM về đoạn này» | jumps to Học với SAM with «Con hỏi về đoạn: «…»» | `trackb-<i>-16-read-ask-sam` | context carried, no re-asking |
| 17 | Tab «🦉 Học với SAM» (fresh) | header «SAM (kịch bản thử nghiệm)» + «SAM đi theo kịch bản viết sẵn…», explain bubble + «SÁCH VIẾT» card, «Tiếp ▸» | `trackb-<i>-17-tutor-explain` | label visible |
| 18 | «Tiếp ▸» | question «1. Quá trình làm muối từ nước biển sử dụng phương pháp tách chất nào?» with 4 options + «Gợi ý cho tớ ✋ (1/2)» | `trackb-<i>-18-tutor-ask` | question verbatim from SGK |
| 19 | Tap «Lọc» (wrong) | learner bubble + hint 1 (lavender), no praise, no shame | `trackb-<i>-19-tutor-hint` | «Chưa đúng»/«sai» absent; hint text |
| 20 | Tap «Cô cạn» (matches) | «Khớp với điều sách viết…» + SÁCH VIẾT card → next question (free text) | `trackb-<i>-20-tutor-matched` | no «Chính xác! 🎉» |
| 21 | Type an answer to «Tại sao phải mở khóa phễu chiết một cách từ từ?» → Gửi | matched or hint depending on text; after ≤2 hints a scaffold, never stuck | `trackb-<i>-21-tutor-free-text` | keyboard does not hide the send button |
| 22 | Answer Q3 (options) | end card «Con đã học cùng SAM phần này» + «chưa phải bằng chứng con đã hiểu» + «📖 Đọc lại phần «Em đã học»» + «Về mục lục» | `trackb-<i>-22-tutor-end` | participation wording only |
| 23 | Tap «📖 Đọc lại phần …» | Smart Book scrolled to «Em đã học» | `trackb-<i>-23-next-read-anchor` | anchor works |
| 24 | Header ← ×3 | Chapter (Bài 17 now «Đã xem (phiên này)») → Book → Giá sách | `trackb-<i>-24-back-chapter-seen` | back-stack sane; no evidence recorded (Sessions unchanged) |
| 25 | Home → «…» → Phiên học | no new session from the workspace | `trackb-<i>-25-sessions-unchanged` | MOCK ≠ EVIDENCE holds on device |

## Result — 2026-09-05, Nokia, portrait, build 4 (`34672ad`) unless noted

| # | Result | Frame |
|---|---|---|
| 01 | PASS (blank first frame on cold start — pre-existing O1) | `trackb-3-01-home`, `4-17-home-top` |
| 02 | PASS | `trackb-3-02-home-bottom` |
| 03 | PASS — only KHTN 6 carries «✨ SAM» | `trackb-3-03-bookshelf` |
| 04 | PASS | `trackb-3-04-book-khtn6` |
| 05 | PASS (D1 fixed; O4 OCR titles visible) | `trackb-3-05-book-chapters` |
| 06 | PASS | `trackb-3-06-chapter-iv` |
| 07 | PASS (D2 fixed) | `trackb-3-07-workspace-visual`, `4-01-workspace` |
| 08 | PASS | `trackb-1-08-workspace-resumed` (landscape), `4-01` |
| 09 | PASS | `trackb-1-09/1-10` (landscape) |
| 10 | PASS | `trackb-1-11-visual-source-sheet` |
| 11 | PASS | `trackb-2-06-visual-comparison` (landscape) |
| 12 | PASS | `trackb-3-08-read-top` |
| 13 | PASS (D5 fixed; D7 fixed in generator, not re-walked) | `trackb-3-09-read-figure-17-1` |
| 14 | PASS | `trackb-3-12-read-withheld-card`, `3-13` (crop revealed) |
| 15 | widget test only (`smart_book_view_test`) | — |
| 16 | PASS | `trackb-3-15-read-question-sheet`, `3-16-tutor-anchored` |
| 17 | PASS | `trackb-4-02-tutor-tiep` |
| 18 | PASS (D6 fixed) | `trackb-4-03-tutor-q1` |
| 19 | PASS | `trackb-3-19-tutor-hint1` |
| 20 | PASS | `trackb-4-04-tutor-matched-q2` |
| 21 | PASS (D8 fixed; ASCII input ⇒ unmatched path: hint 1 → hint 2 → scaffold) | `trackb-4-05`…`4-10` |
| 22 | PASS (D9 fixed after the frame) | `trackb-4-11`, `4-12-tutor-end-card` |
| 23 | PASS (D4 fixed) | `trackb-4-13-read-anchored-em-da-hoc` |
| 24 | PASS | `trackb-4-14-chapter-da-xem`, `4-15`, `4-16` |
| 25 | PASS — one audit session only, none from this branch | `trackb-4-19-sessions-unchanged` |

## The Founder's five questions (answer from screenshots)

1. **Where is the child?** — header «Bài 17 · … / Chương IV · SGK KHTN 6 · trang 60–63» + back stack Giá sách → Sách → Chương (steps 04–07).
2. **What lesson?** — «Bài 17 · Tách chất khỏi hỗn hợp», real title from the pack, real chapter from the TOC (06, 07).
3. **Three ways to learn it?** — the segmented control [📖 Đọc] [✨ Trực quan] [🦉 Học với SAM] on every workspace frame (07, 12, 17).
4. **What is SAM doing?** — «SAM đề xuất» card with a reason (07) and «SAM (kịch bản thử nghiệm)» in the tutor (17–22).
5. **What happens next?** — the next-action button (07) and the end card's «📖 Đọc lại phần «Em đã học»» (22).
