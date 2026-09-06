# Track B — Round 5 · Lane B (EXPERIENCE) · KHTN 6 Bài 17 + phản hồi Founder trên máy

**Ngày:** 2026-09-06 · **Nhánh:** `lane-b/round5-experience` → base `integration/round5-2026-09-06`
· **Trạng thái:** READY FOR FOUNDER REVIEW — chưa merge gì.

Vòng này có **hai nửa**. Nửa đầu theo §12 (Trực quan); nửa sau là **phản hồi trực tiếp của
Founder sau khi cầm máy**, đã được đặt lên ưu tiên cao nhất.

---

## PHẦN I — TRỰC QUAN: từ chữ thành sơ đồ thật

Founder §12: «Trực quan vẫn chưa tới khung concept — chỉ được cải thiện bằng **cấu trúc có
kiểu, bám nguồn**. Không có sự thật hình ảnh do LLM sinh.» Vòng 4 đóng ở **70–80 %** vì
Trực quan là **chữ** ở chỗ khung concept là **sơ đồ minh hoạ**.

Không đổi nguồn sự thật — đổi **cách vẽ** dữ liệu đã tin được:

| # | Việc | Trẻ thấy gì | Ở đâu |
|---|---|---|---|
| 1 | **`ProcessStep[]` → dòng chảy thật** | nút trên MỘT trục liên tục + mũi tên giữa các nút + vạch màu bên trái mỗi thẻ + dải tổng quan **chạm được**; bước bị giữ lại là nút **rỗng** chỉ trang. Trước đây là danh sách đánh số. | `views/process_flow_view.dart` (mới) |
| 2 | **`ComparisonSemantic` → SƠ ĐỒ TƯ DUY** | đúng hình khung concept khung 5: nút trung tâm ở giữa, **2 nhánh trên + 2 nhánh dưới**, mỗi nhánh một thẻ màu mang **chữ sách** («Lọc — Dùng để tách — tách chất rắn không tan ra khỏi chất lỏng»), nối bằng nhánh cong. Bảng vẫn còn sau nút chuyển «Sơ đồ tư duy / Bảng». | `views/mindmap_view.dart` (mới) |
| 3 | **`ConceptRelation[]` → cùng sơ đồ tư duy** | nút trung tâm tất định (khái niệm gặp nhiều nhất) + nhánh mang nhãn quan hệ | `visual_view.dart` |
| 4 | **Chip hình bám nguồn** | «📖 Sách chỉ tới Hình 17.3 — xem trong Đọc» — chỉ hiện khi lời sách nêu «Hình N.M» **và** tài liệu có **đúng một** chú thích mang nguyên văn chuỗi đó. Bước 3 nêu «Hình 17.4», không có chú thích khớp ⇒ **không chip** (fail closed, kiểm trên máy). | `process_flow_view.dart` |
| 5 | **Màu là trang trí, và màn nói đúng thế** | «màu chỉ để phân biệt, không phải điểm số»; mọi cặp nền/chữ bị kiểm **WCAG ≥ 4.5:1** bằng test | `mindmap_view.dart` |
| 6 | **KHÔNG emoji theo nghĩa** | khung concept có emoji cho từng nhóm chất; chọn emoji = suy ra nội dung nguồn không nói ⇒ từ chối, ghi lý do trong mã | — |

**Vì sao KHÔNG hiện ảnh trong nút bước:** liên kết ảnh↔chú thích (`captionBlockId`) đang là
lỗi đã báo A-pipeline (vòng 4 §5.6). Chỉ **chỗ** trong sách thì trung thực; chỉ **sai ảnh**
thì là một lời hứa sai với trẻ.

**Renderer không biết bài nào.** Hai renderer là hàm thuần trên `SemanticData`; có test soi
mã cấm mọi danh tính bài/sách (`if lesson == "KHTN6_BAI17"` là phản mẫu Founder gọi tên).
Chúng **sống được** qua kiến trúc VisualSpec của lane E2 — E2 nhận renderer, không phải viết lại.

**Hai lỗi máy thật tìm ra và đã sửa (lượt 1 → lượt 2):**
- **D1** — thẻ «SAM đề xuất» ghim 6 dòng ⇒ chrome chiếm **920/1920 px (48 %)** và **nút trung
  tâm của sơ đồ tư duy nằm khuất sau thẻ**. Sửa: thẻ vào đầu vùng cuộn (đúng luật vòng 4 đã
  áp cho Đọc) ⇒ **73 %** chiều cao cho sơ đồ; cả sơ đồ nằm gọn một màn.
- **D2** — «Vì sao SAM chọn sơ đồ này» vẫn nói «SAM xếp thành **bảng**» trong khi trẻ đang
  nhìn **sơ đồ tư duy**.

## PHẦN II — GIÁ SÁCH và SÁCH

- **Giá sách** (khung concept 1, vòng 4 đứng 65–75 %): thêm ô «Tìm sách, môn học…» (so khớp
  **bỏ dấu**, gõ «toan» ra «Toán») + hàng chip «Tất cả · ✨ Có bài học SAM · <môn>». Không
  khớp gì ⇒ **nói thật**, không để giá rỗng. **«Yêu thích» của khung concept KHÔNG dựng** —
  nó cần ghi hồ sơ, nằm ngoài ranh giới không-ghi của Track B.
- **Sách** (concept-chuong khung 3): hai tab «Chương | Bài học». `widgets/lesson_row.dart`
  dùng chung với màn Chương ⇒ một vốn từ, một luật màu.
- **D3** (máy thật, lượt 2): KHTN 6 có 55 bài và **đúng một** bài có Bài học SAM ⇒ 54 hàng
  «Chưa có Bài học SAM» che mất hàng duy nhất đáng mở. Sửa: chip «Tất cả (55) | ✨ Bài học
  SAM (1)». Lọc **chỉ ẩn hàng** — thứ tự vẫn là thứ tự mục lục in (có test).

## PHẦN III — PHẢN HỒI FOUNDER: màn Workspace lặp lại và tốn chiều dọc

Chi tiết đầy đủ: **`TRACK-B-ROUND5-WORKSPACE-DUPLICATION.md`**. Tóm tắt theo mẫu thẻ nghiệm thu:

**CURRENT PROBLEM (bằng chứng, không phải cảm giác).** Đo hai cách độc lập:
cây widget ở khung Nokia (392.7×698.2 dp) cho chrome ghim ở **Học với SAM = 411 dp = 58.9 %
khung nhìn**, nhãn View nhìn thấy **7** trên một màn; máy thật cho **Y nội dung bài đầu tiên
= 820 px = 42.7 % màn hình**. Bản đồ trùng lặp 13 mục xác định **4 mục TRÙNG thật**: bong bóng
màn chọn, CTA đổi View trên thẻ đề xuất (lặp đúng cái tab ngay trên nó), chân dung SAM ở chỗ
SAM không nói, «Về mục lục» của thẻ kết. Phát hiện phụ: ba View được gọi bằng **hai bộ chữ**
(«Học với SAM» ở tab vs «Học cùng SAM» ở thẻ) — trẻ đọc **sáu nhãn cho ba thứ**.

**OPTION A · ICON** — 💡 + chấm báo ở hàng tiêu đề; chạm ⇒ bottom sheet.
*Mạnh:* 0 dòng chi phí, lời dài có chỗ thở. *Yếu:* 💡 xa cụm tab nên liên hệ không gian yếu;
**làm tiêu đề bài xuống hai dòng** trên bài này. → **634 px (33.0 %)**.

**OPTION B · PEEK CHIP** — «💡 SAM gợi ý: Xem Đọc ⌄»; chạm bung tại chỗ; «Để sau» ⇒ 💡 về
hàng tiêu đề. *Mạnh:* **phương án DUY NHẤT nói ĐÍCH ĐẾN với 0 chạm**; tiêu đề giữ một dòng;
vùng chạm cả dòng. *Yếu:* tốn 1 dòng khi đang hé. → **712 px (37.1 %)**, thu gọn còn **634 px**.

**OPTION C · INLINE TAB** — 💡 nằm **trong nhãn tab đích** («📖 Đọc 💡»).
*Mạnh:* gọn nhất, gợi ý dính đúng thứ sẽ chạm. *Yếu:* **không giải thích được «vì sao» tại
chỗ** — muốn hiểu phải sang View đó. → **565 px (29.4 %)**.

**WINNER — B (PEEK), và lý do không phải là pixel.** C thắng về chỗ (−255 px) nhưng thua ở
đúng tiêu chí Founder đặt ra làm ràng buộc cứng: *«learner phải còn cảm thấy ứng dụng biết
mình đang ở đâu và đề xuất mình nên làm gì tiếp theo»*. C chỉ để lại một biểu tượng; A cũng
thế, và còn làm tiêu đề bài xuống hai dòng. **Chỉ B trả lời được câu «SAM đang đề xuất gì»
mà không cần chạm** — và nó vẫn trả lại **186 px** khi trẻ đã bỏ qua. B cũng là phương án
duy nhất có đủ ba trạng thái thật: COLLAPSED (💡 ở tiêu đề) → PEEK (một dòng có đích) →
EXPANDED (vì sao + một CTA + «Để sau»), và **hé lại một lần khi đề xuất trỏ sang View khác**.

**SPACE SAVED (đo trên máy, Học với SAM, cùng bài + cùng trạng thái + cùng chuỗi chạm):**
820 px → 712 px khi đang hé (**−108 px, −13.2 %**), → 634 px sau «Để sau» (**−186 px,
−22.7 %**). Cây widget: chrome ghim 411 dp → 281 dp; nhãn View 7 → 4 (tutor: 6 → 3).

**AI DISCOVERABILITY — tốt hơn.** Hiện tại: lý do hiện sẵn (0 chạm) nhưng **CTA lặp lại tab**
và **chân dung SAM ở chỗ SAM không nói**, nên «SAM» trở thành đồ trang trí thường trực. B:
đích đến vẫn 0 chạm, «vì sao» 1 chạm, và 🦉 được trả lại cho chỗ SAM **thực sự nói**. Có test
đi qua **cả bốn** phương án bắt buộc dấu hiệu đề xuất **nhìn thấy được** ở cả ba View — không
phương án nào được phép chỉ-giấu-đi.

**DUPLICATION removed:** CTA đổi View lặp tab (**bỏ**), chân dung SAM trên thẻ đề xuất (**bỏ**),
hàng «Đã mở ● ○ ○» (**gộp** vào lớp trợ giúp). Nhãn View trên một màn **7 → 4**.

**REAL DEVICE — có.** Nokia 6.1 / Android 10, «Na · Lớp 6». **5 lượt, 36 frame, 28 bước, 0
hạ cấp** (`docs/design/track-b-evidence/round5/MANIFEST.json`). Bốn bản build từ **cùng một
commit**, chỉ khác `--dart-define=WAL_ASSIST`. Giao thức giữ nguyên: hai screencap ≥ 20 s
trước mỗi lượt — vòng này so **theo pixel** chứ không chỉ theo hash, nên phân biệt được «đồng
hồ nhích một phút» với «Founder đang cầm máy»; không đánh thức, không mở khoá, không đổi hồ
sơ/cài đặt/dữ liệu; `com.workizen.tongtai` không bị chạm. Một frame lỡ chụp trúng bảng chọn
hồ sơ của Founder đã **xoá ngay**. Máy đã được **cài lại bản mặc định** (hành vi hiện tại).

**OPEN RISKS.**
1. B chưa được **trẻ thật** dùng; «0 chạm biết đích, 1 chạm biết vì sao» là suy luận từ bố
   cục, không phải quan sát hành vi.
2. «Đề xuất mới ⇒ hé lại» hiện kích hoạt khi `next.view` **đổi**; nếu runtime sau này đổi lý
   do mà không đổi View, trẻ sẽ không được hé lại. Cần luật rõ hơn từ phía runtime.
3. Bỏ hàng «Đã mở ● ○ ○» là **mất một dấu hiệu tiến trình phiên** mà vòng 4 cố tình thêm.
   Nếu Founder muốn giữ, chỗ rẻ nhất là dòng phụ trong trạng thái EXPANDED.
4. Màn chọn vẫn còn bong bóng và **hai bộ chữ** cho ba View — đã chỉ ra, **chưa sửa** (sửa
   tên là chạm vào `WorkspaceView.label` thuộc `lib/core/**`, không phải làn B).

**RECOMMENDED NEXT STEP.** (a) Founder chọn giữa **B** (đề nghị của làn này) và **C** (nếu
pixel quan trọng hơn khả năng giải thích tại chỗ); (b) cho phép thống nhất **một bộ tên** cho
ba View — việc này chạm `lib/core`, cần một quyết định; (c) bỏ bong bóng màn chọn; (d) sau khi
chốt, gỡ cờ `WAL_ASSIST` và ba nhánh không được chọn.

## PHẦN IV — NĂM ĐIỂM SỐ

| # | Điểm | Giá trị | Cơ sở |
|---|---|---|---|
| 1 | **Experience Fidelity** | xem bảng dưới | so từng khung với hai bảng concept |
| 2 | **Source Reality** | **97 phần tử** (78 TSL · 10 fixtureFromTrustedCorpus · 5 prototype · 4 withheld) | **KHÔNG ĐỔI** — làn này không đổi nội dung nào |
| 3 | **Source Trust** | **0 / 97** | `THRESHOLDS.json` vẫn chưa tồn tại; không có cổng nào để qua |
| 4 | **Pedagogy Reality** | **7 / 17** bước tutor có runtime ràng buộc, **đọc trên máy** | không đổi — làn này không đổi runtime |
| 5 | **Evidence Reality** | **0** trên **0 khả dĩ** | `EvidencePolicy.none`, không validator nào áp cho Bài 17 |

### Experience Fidelity — trước → sau, có cơ sở

| Màn / View | Vòng 4 | Vòng 5 | Cơ sở |
|---|---|---|---|
| **Trực quan** | 70–80 % | **85–90 %** | **khoảng cách lớn nhất của vòng 4 đã đóng**: sơ đồ tư duy đúng hình khung concept (nút trung tâm + 4 nhánh màu + nhánh cong), quy trình là nút+cạnh+mũi tên, chip hình bám nguồn, cả sơ đồ nằm gọn một màn sau D1. Còn thiếu so với bảng: emoji theo nghĩa trong nút (**từ chối có lý do**), và thẻ «Ghi nhớ cùng SAM» của bảng (chỗ đó ta để «Vì sao SAM chọn sơ đồ này» — trung thực hơn) |
| Giá sách | 65–75 % | **80–85 %** | ô tìm + chip lọc = phần lớn khoảng cách còn lại của khung 1; còn thiếu «Yêu thích» (cố ý không dựng) |
| Sách | 70–80 % | **80–88 %** | hai tab «Chương \| Bài học» đúng concept-chuong khung 3 + chip lọc bài học SAM |
| Đọc | 85–90 % | **85–90 %** | không đổi vòng này |
| Chương | 75–85 % | **75–85 %** | không đổi (dùng chung `LessonRow`) |
| Vào bài học (picker) | 80–90 % | **80–90 %** | không đổi — nhưng đã chỉ ra chỗ trùng, chờ quyết định |
| Học với SAM | 80–88 % | **80–88 %** | nội dung không đổi; **chỗ** thì đổi (chrome 58.9 % → 40.2 % ở phương án B) |
| Next Action / trợ giúp | 80–90 % | **chưa chốt** | ba phương án đo xong, chờ Founder chọn |
| Home | 70–80 % | **70–80 %** | không đổi |
| Lát cắt nghiên cứu | 65–75 % | **65–75 %** | không đổi (Lane C sở hữu) |
| **Tổng** | **80–85 %** | **85–88 %** | Trực quan **hết là chỗ nghẽn**; chỗ nghẽn mới là mật độ màn Workspace, đã đo và có ba phương án |

## PHẦN V — TRẢ VỀ CÁC LÀN KHÁC

1. **Founder — chọn phương án trợ giúp** (B đề nghị) và cho phép **thống nhất tên ba View**
   (chạm `lib/core/lesson_model/next_action.dart`).
2. **Lane E2** — hai renderer vòng 5 là hàm thuần trên `SemanticData`, **không biết bài nào**
   (có test). Nếu VisualSpec cần một họ hình dạng, «nút trung tâm + nhánh có nhãn» và «dòng
   chảy nút+cạnh» đã có bản dựng chạy được trên máy để mượn.
3. **A-pipeline** — liên kết ảnh↔chú thích (`captionBlockId`) vẫn sai; vì thế chip hình chỉ
   dám **chỉ chỗ**, không dám **hiện ảnh**. Sửa được thì Trực quan lên tiếp.
4. **Lane A2** — hợp đồng `MathExpression` đề nghị ở `STEM-RENDERING-NOTE-ROUND5.md` §5, kèm
   cảnh báo: `fromJson` hạ **cả tài liệu** khi gặp khối lạ ⇒ `FormulaBlock` mới sẽ làm trắng
   bài trên app cũ.
5. **A-pipeline / Founder** — `LessonDocument.titleCase` vẫn hạ chữ hoa của danh từ riêng
   («thời kì **b**ắc thuộc»); mang từ vòng 4, chưa sửa (core-owned).

## PHẦN VI — CỔNG

`flutter analyze` sạch · `flutter test` **995 passed / 1 skipped / 0 failed** (nền của nhánh
này: 961/1 khi bắt đầu; 985/1 sau khi khôi phục WIP). Test mới:
`round5_visual_test.dart` (sơ đồ, chip hình, tương phản màu, fail-closed, **renderer không
biết bài nào**), `workspace_density_test.dart` (đo mật độ + so A/B/C + cấm động cơ thứ hai +
cấm giấu hết), cùng các case thêm vào `book_shelf_test`, `book_and_chapter_test`,
`round4_experience_test`, `no_machine_ids_test`.

## PHẦN VII — CÁCH DỰNG BỐN BẢN ĐỂ SO

```
cp <main>/assets/pack/{lesson-index-g*.json,*.png,sam-units.db,sam-stories.db} assets/pack/
cp <main>/assets/pack/covers/* assets/pack/covers/
cp <main>/assets/fixtures/real/*.json assets/fixtures/real/          # gitignore; ĐỪNG sinh lại Bài 17
cp <main>/assets/fixtures/real/crops/*.png assets/fixtures/real/crops/
flutter analyze && flutter test
flutter build apk --debug                                   # HIỆN TẠI (card)
flutter build apk --debug --dart-define=WAL_ASSIST=icon     # A
flutter build apk --debug --dart-define=WAL_ASSIST=peek     # B  ← đề nghị
flutter build apk --debug --dart-define=WAL_ASSIST=inlineTab # C
```
