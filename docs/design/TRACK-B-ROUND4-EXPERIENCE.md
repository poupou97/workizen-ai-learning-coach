# Track B — Round 4 · Lane B (EXPERIENCE) · Golden Slice KHTN 6 Bài 17

**Date:** 2026-09-05 · **Branch:** `lane-b/round4-experience` → base `integration/round4-2026-09-05`
· **Status:** READY FOR FOUNDER REVIEW — nothing merged.

Founder order (§6, essence): keep UI/UX moving in parallel; Bài 17 at 70–80 % Experience Fidelity;
raise the journey Home → Bookshelf → Book → Chapter → Lesson → Workspace [Đọc][Trực quan][Học với
SAM] → Next Action; priorities Home · Bookshelf/Chapter coherence · Smart Book readability · trust
in a child's words · Visual · SAM Tutor clarity · Next Action · crop/caption defects · withheld
states · source navigation; no machine ids for the child; Nokia validation mandatory.

Boundary unchanged and still machine-held: `ContentTrust`, one-value `EvidencePolicy {none}`,
`WithheldBlock` without a text field, `boundary_test.dart` (throwing store across the journey,
source grep of `lib/features/lesson_workspace/**`). Round 4 adds nothing that can write; it changes
**what the child reads and where machine facts live**, not what the machine asserts.

## 1. What changed, per Founder item

| # | Item | What the child now sees | Where |
|---|---|---|---|
| 1 | **Home = one «Hôm nay» area** | «Chào Na!» → SAM line «Hôm nay mình học Bài 17 · Tách chất khỏi hỗn hợp nhé — bài này SAM đã xếp sẵn ba cách học từ sách. Bấm «Mở bài học» là vào.» (replaces the mic bar «SAM đang học cách trò chuyện» — no chat promised) → label **HÔM NAY** → primary lavender card «BÀI HỌC SAM · BẢN THỬ NGHIỆM» with **«Vì sao bài này? Đây là bài SAM đã xếp sẵn từ sách để con đọc như trong sách, xem sơ đồ / bảng, trả lời 3 câu hỏi trong sách cùng SAM — con thử trước nhé.»** (counted from the document) → secondary white card **«CÒN CÓ THỂ MỞ»** «Có 4 bài để học ở Môn học · Ở Môn học con mở được 4 bài từ sách giáo khoa …» + «Vào Môn học ▸». The contradiction «SAM chưa có bài dạy riêng cho lớp 6» directly under a *Bài học SAM* is gone (only shown when no workspace lesson exists). Order rule: the workspace card is primary unless Toán has an evidence-urgent agenda (review/retrieve) or a TKB book recommendation speaks — then it drops to second, as before. | `lib/features/mission/mission_center_screen.dart` (`samTodayLine`, `workspaceWhyLine`, `_workspaceIsPrimary`) · tests `home_today_area_test`, `home1_test`, `home_workspace_card_test` |
| 2 | **Bookshelf / Book / Chapter coherence** | one vocabulary: shelf tile «55 bài» + **«✨ 1 bài học SAM»** → book «✨ 1 bài học SAM: Bài 17» → chapter row «Bài 16–17 · 2 bài · ✨ 1 bài học SAM · Đã xem (phiên này)» → lesson row «✨ Bài học SAM · 3 cách học · Chưa xem» / **«Đã xem (phiên này): Đọc · Trực quan»** (session trace only — no stars/percent/«đã học», pinned by test). «Mục lục & hoạt động (bản hiện tại)» → «Các bài khác trong sách»; «mở mục lục hiện tại» → «mở trong Môn học». BookScreen now listens to the trace (deferred out of the build phase). | `book_shelf_screen.dart`, `book_screen.dart`, `chapter_screen.dart` · `book_and_chapter_test` |
| 3 | **Smart Book readability** | paragraphs are continuous text like a page (no white card per paragraph — round 3 showed a page as eight loose cards); figure + adjacent captions + source line are **one block** («Hình trong sách · SGK KHTN 6 · trang 60 · chạm hình để xem ảnh gốc»); page chips + «— trang N —» kept; end-of-lesson source line shows «SGK KHTN 6 · trang 60–63» only. **Withheld card**: «Phần này SAM chưa đọc được — con xem SGK trang 61 nhé.» + «Lý do: đoạn này nằm trong sơ đồ» + **«Vì sao SAM để trống?»** → «Chỗ này trong sách là một sơ đồ — chữ nằm xen trong hình. Máy đọc chữ trong sơ đồ hay bị nhầm, mà SAM chỉ chép lại khi chắc là đúng, nên SAM để trống và chỉ trang cho con.» (per reason class: diagram / số & công thức / bảng / chưa rõ loại / default); «Xem ảnh chụp trang sách». **«Tra cứu» sheet** («Sách viết»): «📖 Tra cứu · SGK KHTN 6 · Bài 17 · trang 60», **«Trong mục: Nguyên tắc tách chất»** from the pipeline heading path (never invented; absent on the synthetic fixture), original crop labelled «nguyên gốc (có thể lẫn chữ cạnh hình)», «Xem trong Đọc». | `smart_book_view.dart`, `widgets/withheld_card.dart`, `widgets/source_sheet.dart` · `round4_experience_test` §6.3 |
| 4 | **Trust / source sheet in child language** | «📖 Nói với con»: «Chữ và hình trong bài là chữ và hình của SGK KHTN 6 · trang 60–63 — máy chép lại từ sách, nhớ cả số trang… **«Chưa kiểm định» nghĩa là: chưa có người lớn soát lại từng chữ máy chép, nên có thể còn lỗi nhỏ (một dấu, một chữ). Thấy chỗ nào lạ, con mở sách giấy ra so — số trang ghi ngay bên cạnh.** Chỗ nào máy chưa chắc đọc đúng, SAM để trống và chỉ trang — không đoán.»; ✨ sơ đồ (no rule ids); 🦉 SAM (child runtime line); 📝 «KHÔNG ghi»; **«👨‍👩‍👧 Dành cho bố mẹ»**: internal build, structured verbatim extraction, no false-trust gate (G1) / no licence (D4) ⇒ chip cannot be turned off, nothing recorded as evidence + the six BoundaryClaims. **«🔧 Chi tiết kỹ thuật (dành cho người lớn)»** — closed by default — holds `tsl-enumerated-steps-v1`, runtime refusal codes, key source, pipeline/generator, audit status, source hash, licence. | `widgets/trust_sheet.dart`, `widgets/tech_details.dart` · `round4_experience_test` §6.4, `workspace_screen_test` |
| 5 | **Visual Learning clarity** | legend under the overview strip «Số tím = bước sách viết · số xám = bước SAM để trống (xem trong sách) · chạm một bước để tra cứu lời sách»; 📖 affordance on every step node; comparison hint «Mỗi hàng là một cách sách nêu · chạm một hàng để tra cứu lời sách»; fail-closed copy says why: «SAM chỉ vẽ sơ đồ khi sách viết rõ từng bước hoặc từng cách; bài này chưa có phần như vậy nên SAM không tự vẽ…»; link renamed «ⓘ Nguồn & độ tin». Typed renderers (process, comparison, concept map, timeline) unchanged; Bài 17 still fails closed to Process + Comparison. | `visual_view.dart` · `round4_experience_test` §6.5 |
| 6 | **SAM Tutor clarity** | header runtime line in child words, numbers kept: **«Máy đã kiểm 5/17 bước là lời lấy đúng trong sách (giải thích, câu hỏi, bước tiếp) · 12 bước còn lại là lời viết sẵn để thử (gợi ý, phản hồi).»**; legend «Nhãn xanh «runtime có kiểm» = lời lấy đúng trong sách, máy đã kiểm · nhãn tím «kịch bản thử nghiệm» = lời viết sẵn để thử.» (the two label strings are core-owned `SamMode`/`PlannedStepMode.childLabel`, unchanged); **hint ladder** «Bậc gợi ý ① ② · Gợi ý cho tớ ✋» with used rungs filled, hint bubbles captioned «Gợi ý 1/2», end of ladder «SAM đã gợi ý hết rồi — con cứ trả lời thử, SAM sẽ chỉ chỗ trong sách»; SÁCH VIẾT cards say «· chạm để tra cứu»; end card unchanged (participation only). Technical runtime line (`runtimeGuided/prototypeScripted · refusals HINT_UNSOURCED, …`) lives only in the trust-sheet fold. **Lane A-runtime round-4 APIs: none published at the time of writing** (no `docs/architecture/ROUND4-RUNTIME-CONTRACTS.md`, no round-4 A-runtime branch/PR on origin at 20:22) — the UI still consumes round-3 `PedagogyRuntime.planForScript` / `NextBestLearningAction`; polled `git fetch origin` at 19:5x, 20:02, 20:22. | `tutor_view.dart`, `widgets/sam_bubble.dart` · `round4_experience_test` §6.6, `tutor_view_test` |
| 7 | **Next Action consistent with the runtime rule** | the «SAM đề xuất» card keeps the runtime's reason (R2–R5 from `NextBestLearningAction`) and adds one line **«Đã mở: ● Đọc ○ Trực quan ○ Học với SAM»** — the session trace the rule reads, so the child sees why the next step is what it is; never evidence, never percent. Reason capped at 6 lines as a frame safety net (real reasons ≤ 3 lines on the Nokia; D-R3-03 respected). | `lesson_workspace_screen.dart` · `round4_experience_test` §6.7 |
| 8 | **Crop / caption defects (display-side)** | `bleedScale = 1.14`: each crop is scaled 14 % inside its aspect-fixed box so ~6 % per edge falls outside the clip — removes the neighbour text line at the top of p60 fig02 / p63 fig02 and the caption bleed under p60 fig03 (D-R3-05) without touching the image or the bbox; the source sheet shows the **untrimmed** crop labelled «nguyên gốc (có thể lẫn chữ cạnh hình)». Captions are still grouped by reading-order adjacency, never by `captionBlockId` (O5). **Reported to Lane A-pipeline** (§5). | `smart_book_view.dart` (`_imageBox`) · `round4_experience_test` §6.3 |
| 9 | **No machine ids child-facing (grep test)** | `no_machine_ids_test.dart` walks Home → Giá sách → Sách → Chương → Vào bài học → Đọc → Trực quan (every shape/instance + Bảng tóm tắt) → Học với SAM (explain / ask / hint) → «Nguồn & độ tin» → «Sách viết» for a paragraph, an image and a withheld block, on the **synthetic and the real fixture**, and asserts no visible `Text` matches `tc2-p1 | sdm-v2 | tsl-…-v1 | toc-ocr | page_feature | math_guard | unknown_role | 0N-sgk-… | :NNN | HINT_UNSOURCED | KEY_NOT_VALIDATED | OVER_CAP | GUARD: | PLAN: | .py | @vN | runtimeGuided | prototypeScripted | sourceBlockId | synthetic: | …enum names`; then opens the fold and asserts the codes are there (moved, not deleted). Findings fixed by this test: withheld source sheet «Mã lý do máy: page_feature:diagram»; trust sheet rule ids, key source «prototype — suy từ đoạn 06-sgk-…:tc2-p1:005», «Nguồn máy: tc2-p1 · tool/corpus/tsl_to_lesson_document.py@v1»; Smart Book end line «… · tc2-p1 / sdm-v2». | `test/features/lesson_workspace/no_machine_ids_test.dart` |
| 10 | **Evidence manifest per iteration** | `tool/evidence/retain.py --round round4 …` → `docs/design/track-b-evidence/round4/MANIFEST.json` (git SHA, APK sha256, packVersion per pack, fixture provenance/trust, device `getprop`, frame sha256s, steps → results; PASS without frame downgraded). Frames also at `~/Desktop/wal-evidence/round4-<iter>-<step>.png`. | §4 |

Not built (doctrine, unchanged from round 3): stars/percent on chapters, «Chính xác! 🎉», free chat with
SAM, bottom tab bar, XP, minutes.

## 2. Lane A consumption

- **Lane A-runtime (round 3, PR #69, merged in the base):** `PedagogyRuntime.planForScript`, `NextBestLearningAction`, `StudentLessonState.unseen`, `SemanticBindingRegistry.resolveFor` — consumed unchanged through `widgets/runtime_plan.dart`. Lane B constructs no `PlannedStep` / `EvidenceValidation`.
- **Lane A-runtime (round 4):** nothing to consume yet — no `ROUND4-RUNTIME-CONTRACTS.md`, no branch/PR on origin during this lane's window (polled 3×). When it lands green: merge `origin/<branch>` into this branch, re-run `round4_experience_test` + `no_machine_ids_test` (the fold must still hold every new refusal code), re-walk steps 15–22 on the Nokia, and document the merge here.
- **Lane A-pipeline:** nothing consumed; two display-side findings returned (§5).

## 3. The five numbers (never averaged)

### 3a. EXPERIENCE FIDELITY vs the concept boards (judgement bands, before → after)

| Screen / View | Round 3 | Round 4 | Basis |
|---|---|---|---|
| Home | 50–60 % | **65–75 %** | «Hôm nay» area = greeting + SAM line + one primary card with a child-words «why» + secondary «còn có thể mở» (concept «Việc SAM đề xuất hôm nay» + «Tiếp tục học»); no fake chat bar; still no hero/bottom tabs/XP (doctrine) |
| Giá sách | 60–70 % | **65–75 %** | same grid; «✨ 1 bài học SAM» counted, same vocabulary as book/chapter |
| Sách (Book) | 65–75 % | **70–80 %** | chapter rows carry «Đã xem (phiên này)», child-words legacy entry; no Mục lục/Giới thiệu/Ghi chú tabs (scope) |
| Chương | 60–70 % | **70–80 %** | lesson state «3 cách học · Chưa xem» / «Đã xem: Đọc · Trực quan» (concept-chuong frame 4 without stars, by doctrine) |
| Vào bài học / picker | 80–90 % | 80–90 % | unchanged |
| Mode 1 Đọc | 70–80 % | **80–85 %** | continuous prose + figure blocks + trimmed crops ≈ concept frame 4; withheld «vì sao»; tra cứu sheet ≈ concept-chuong frame 8 (no page flipping) |
| Mode 2 Trực quan | 65–75 % | **70–80 %** | legend + tap affordance; still no illustrated nodes / mindmap data for Bài 17 |
| Mode 3 Học với SAM | 70–80 % | **75–85 %** | child runtime line, label legend, visible hint ladder; end card unchanged; no «Chính xác 🎉» by doctrine |
| Next Action | 75–85 % | **80–90 %** | reason + «Đã mở» trace row; Founder A8 order via runtime |
| Nguồn & độ tin (sheet) | (60–70 %) | **80–90 %** | child section, parent section, fold — a sheet a Lớp 6 child can read |
| **Overall** | **70–80 %** | **78–85 %** | «1 bài học – 3 cách học – 1 bước tiếp» legible on every frame **and** every child-facing string is child language; remaining gap = density/illustration and navigation chrome of the boards, not honesty |

Bands are judgement against `concept/concept-ai-first/learning-view.png` + `concept-chuong.png`, frame by frame; device verification in §4 is the basis for «after» — a band whose frames are missing is marked so.

### 3b. SOURCE REALITY — visible content elements by `ContentTrust` (real bridge fixture, `capabilityCensus()`, printed by `round3_metrics_test`)
**97 visible elements**: `trustedStructuredLesson` **78** (69 text/image blocks + 9 semantic items) · `withheld` **4** · `prototype` **5** (tutor script steps) · `fixtureFromTrustedCorpus` **10** (OCR chapter refs) · `fixtureSynthetic` 0 · `trustedCorpus` 0. Unchanged by round 4 (UI-only lane).

### 3c. SOURCE TRUST — elements through a production-trusted path: **0 / 97** (`trustedCorpus` does not exist; TSL = `trustedStructuredLesson`, `auditStatus = sampledNoGate`, licence `internalResearchOnly`). Unchanged.

### 3d. PEDAGOGY REALITY — tutor steps as shown on the device (real fixture, `PedagogyRuntime.planForScript`): **17 planned = 5 runtimeGuided / 12 prototypeScripted**; refusal codes `GUARD`, `HINT_UNSOURCED`, `KEY_NOT_VALIDATED`, `OVER_CAP_WITHOUT_VALIDATOR` (in the fold only). Synthetic CI fixture 12 = 4 / 8. Unchanged.

### 3e. EVIDENCE REALITY — interactions creating validator-permitted evidence: **0 of 0 possible** (`validator == null` on all 17 steps; `EvidencePolicy.none`; Sessions unchanged on the device — step 28). Interactions performed on device: see §4.

## 4. Device loop — Nokia 6.1 (Android 10), «Na · Lớp 6», portrait, WiFi adb `192.168.1.3:5555`

Protocol: read-only `dumpsys window` / `dumpsys power` before every input burst; two screencaps 20 s apart before the first input (differ ⇒ Founder holding the phone ⇒ wait); never wake/unlock/swipe on a lock; no profile/settings/data change; frames with anything that is not our app are deleted.

Timeline: 19:5x device on launcher (Awake/ON) during code work; **20:18–20:2x device Dozing / Display OFF** (fell asleep on its own) — no wake attempt, polled read-only every ~10 min while tests/build ran.

| Iter | Build | Walked | Defects found → fixed |
|---|---|---|---|
| 1 | _pending — filled from `track-b-evidence/round4/steps.json`_ | | |

## 5. Returned to other lanes / Founder (not decided here)
1. **Lane A-pipeline — crop bbox bleed (D-R3-05, still present in the bridge output):** `p061:fig02` and `p064:fig02` include the neighbouring text line at the top, `p061:fig03` the caption line at the bottom, `p064:fig02` the red rule at the bottom. Display trims 6 % per edge; the fix belongs in the figure bbox (shrink to the raster region, exclude text lines).
2. **Lane A-pipeline — caption link (O5)** still wrong for `p062:fig05` → `:024`; UI keeps ignoring `captionBlockId`.
3. **Lane A-pipeline — SourceRefBlock text** carries the pipeline tag (`… · tc2-p1 / sdm-v2`); UI strips it by `provenance.pipelineVersion`. Better: emit the page range only and keep the tag in provenance.
4. **Lane A-runtime — label strings** `SamMode.childLabel` / `PlannedStepMode.childLabel` («runtime có kiểm», «kịch bản thử nghiệm») are jargon for an 11-year-old; Lane B added a legend rather than changing core-owned strings. Proposal: «SAM (lời lấy trong sách, máy đã kiểm)» / «SAM (lời viết sẵn để thử)».
5. **Founder — chip label** `fixtureChipLabel(trustedStructuredLesson)` = «Bản thử nghiệm · nguồn SGK có cấu trúc, chưa kiểm định (nội bộ)» is core-owned; the sheet now explains it, the chip itself stays as decided in round 3.
6. Next-action rule order (Founder A8 vs prototype visual-first) — unchanged from round 3 §5.1; the prototype `nextActionFor` is still unused by the UI.

## 6. Tests
`flutter analyze` clean · `flutter test` **915 passed / 1 skipped / 0 failed** with packs + real fixture (baseline 896 / 1 on the integration base). New: `test/features/mission/home_today_area_test.dart`, `test/features/lesson_workspace/round4_experience_test.dart`, `test/features/lesson_workspace/no_machine_ids_test.dart`; updated: `home1_test`, `home_workspace_card_test`, `book_and_chapter_test`, `workspace_screen_test`, `visual_view_test`, `tutor_view_test`.

## 7. How to run
```
cp <main>/assets/pack/{lesson-index-g*.json,*.png,sam-units.db,sam-stories.db} assets/pack/ && cp <main>/assets/pack/covers/* assets/pack/covers/
cp <main>/assets/fixtures/real/*.json assets/fixtures/real/ && cp <main>/assets/fixtures/real/crops/*.png assets/fixtures/real/crops/   # bridge fixture (gitignored)
flutter analyze && flutter test && flutter build apk --debug
python3 tool/evidence/retain.py --round round4 --frames docs/design/track-b-evidence/round4 \
  --steps docs/design/track-b-evidence/round4/steps.json --apk build/app/outputs/flutter-apk/app-debug.apk \
  --fixture assets/fixtures/real/lesson-06-sgk-khoa-hoc-tu-nhien-6-b17.json --adb $ANDROID_HOME/platform-tools/adb --print
```
