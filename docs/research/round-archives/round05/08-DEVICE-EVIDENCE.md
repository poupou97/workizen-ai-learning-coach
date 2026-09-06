# 08 · DEVICE EVIDENCE

> **INTERNAL / RESEARCH ONLY — DO NOT PUBLISH.** The 36 frames in `screenshots/` contain SGK page
> crops and publisher cover artwork rendered inside the app. Under Founder rule **D4** these are
> internal research material and must not be distributed. They also carry the learner display
> name **«Na»** — the Founder's own learner profile on the Founder's own device.

---

## 0. THE DISTINCTION THAT MATTERS MOST

**Widget tests and emulators are not real-device evidence.**

Round 5 produced all three kinds and they are kept apart throughout this archive:

| Kind | What it can prove | What it cannot |
|---|---|---|
| **Widget test** (e.g. the 411 dp pinned-chrome measurement at a simulated 392.7 × 698.2 dp viewport) | that the tree lays out as claimed at a given viewport | that a real Android renders it that way, that fonts/DPI/insets behave, or that a human can use it |
| **Machine-generated widget transcript** (Lane E2's substitute for its §27 checkpoint across three subjects) | that a real widget produces the described structure | anything about the device — **E2 explicitly did not walk the device** |
| **Real device walk** (Lane B, Nokia 6.1) | what a child actually sees and can touch | nothing about the pipeline or the corpus |

**Every device claim in this archive comes from the third row.** Lane E2's transcript is recorded
as a **substitution**, not as device evidence.

---

## 1. THE DEVICE, THE BUILD, THE LEARNER

*(**PROVEN** — read from `manifests/round5-device-MANIFEST.json`, schema `wal-evidence-manifest-v1`,
`generatedAt 2026-09-06T01:47:09Z`; every frame hash recomputed by the archive builder.)*

| Field | Value |
|---|---|
| **Device** | **Nokia 6.1** |
| OS | **Android 10**, SDK **29** |
| Connection | adb over WiFi, `192.168.1.3:5555`, portrait |
| **Learner state** | **«Na · Lớp 6»** — the Founder's real learner profile, untouched |
| Lesson walked | **KHTN 6 · Bài 17 · «Tách chất khỏi hỗn hợp»**, SGK pages 60–63, real TSL fixture |
| Fixture | `lesson-06-sgk-khoa-hoc-tu-nhien-6-b17.json`, sha256 `30e51c76…`, **73 blocks · 3 semantic · 5 tutor steps**, trust `trustedStructuredLesson`, pipeline `tc2-p1`, generator `tool/corpus/tsl_to_lesson_document.py@v1` |
| Also walked | the LS&ĐL 5 research slice (Lane C timeline), in its own honest section |
| Manifest git sha | `406e897b22d4542763addd40bc24f81cbb6dac1c`, branch `lane-b/round5-experience` (**dirty: true** — recorded, not hidden) |
| Final APK | `build/app/outputs/flutter-apk/app-debug.apk`, sha256 `e3b3b43399ad90d5…`, 270,053,980 bytes |
| Packs on device | **12 lesson-index packs**, each with `packVersion`, `contentHash` and `provenance: true` — all `g*-20260905T0437Z-07a24504` |

**Totals: 5 iterations · 36 frames · 28 steps · PASS 28 / FAIL 0 / SKIP 0 / UNVERIFIED 0 ·
0 downgraded · 0 manifest warnings.** *(PROVEN — recomputed.)*

---

## 2. THE FIVE ITERATIONS — flow tested, build, result

**Iteration 1 — the full journey · git `2a87b88` · APK `471f03eb…` · 10 steps · all PASS**

| # | What was checked | Frames |
|---|---|---|
| 01 | Home «Chào Na!» + SAM line + HÔM NAY section | 2 |
| 02 | Into the lesson → Đọc, experimental chip, «SAM đề xuất» card with the «Đã mở» trace | 1 |
| 03 | Trực quan: the 1→2→3 overview strip **in colour**, shape chips | 1 |
| 04 | The process is a **diagram**: nodes + continuous axis + arrows + colour bars; chip «Sách chỉ tới Hình 17.3» | 2 |
| 05 | The comparison opens as a **mindmap**: centre node + 4 coloured branch nodes | 3 |
| 06 | Tapping a mindmap node ⇒ «Sách viết» verbatim sheet + «Xem trong Đọc» + the technical fold | 1 |
| 07 | The figure chip on step 2 jumps back into Đọc **at the right place** («Hình 17.3») | 2 |
| 08 | Học với SAM: the runtime line in a child's words — «Máy đã kiểm 7/17 bước…» | 1 |
| 09 | Home has its own section «SAM ĐANG TẬP ĐỌC SÁCH KHÁC» for the research slice | 1 |
| 10 | LS&ĐL 5 slice → Trực quan → Timeline (Lane C) still intact | 1 |

**Iteration 2 — after the first defect fixes · git `65c68d0` · APK `d98ffcd2…` · 8 steps · all PASS**
Home after reinstall · the «Vào bài học» screen with three data-counted cards · **D1 fixed**: the
«SAM đề xuất» card scrolls with the diagram ⇒ pinned chrome ~525/1920 px (**73 % for the
diagram**) · **D1+D2 fixed**: the whole mindmap fits one screen · bookshelf search box + chips ·
the «Có bài học SAM» chip filters to exactly KHTN 6 · the Book screen's two tabs · the lesson tab
lists the table of contents directly.

**Iteration 3 — the D3 fix · git `9a74320` · APK `8c386b6c…` · 2 steps · all PASS**
**D3 fixed**: the lesson tab has chips «Tất cả (55) | ✨ Bài học SAM (1)»; filtering gives exactly
one Bài 17 row with an accent background and the trace «Đã xem (phiên này): Đọc».

**Iteration 4 — the workspace A/B/C comparison · git `d8147c9` · 6 steps · all PASS**
**Four builds from one commit**, differing only by `--dart-define=WAL_ASSIST=…`. CURRENT (card) ·
**A · icon** (icon + dot in the title row, sheet on tap) · **B · peek** (one line «SAM gợi ý: Xem
Đọc», title still one line; expands in place) · **C · inlineTab** (badge on the destination tab,
no extra row). This iteration is what produced the measured density table in
`05-METRICS-BEFORE-AFTER.md` §10.

**Iteration 5 — the D4/D5 fixes re-walked · git `7b1420e` · 2 steps · all PASS**
**D4 fixed**: the badge sits inside the tab label and the whole tab is the touch target.
**D5 fixed**: after «Để sau» the peek line disappears **but the icon remains** in the title row —
SAM no longer vanishes.

---

## 3. THE FIVE DEFECTS THE DEVICE FOUND THAT NO TEST DID

| # | Defect | Fixed & re-walked |
|---|---|---|
| **D1** | The pinned card **hid the mindmap's hub** — 48 % chrome | ✔ iteration 2 (→ 27 % chrome) |
| **D2** | The «why» said «bảng» while showing a **mindmap** | ✔ iteration 2 |
| **D3** | **54 «chưa có» rows buried** the one SAM lesson | ✔ iteration 3 |
| **D4** | A **21 dp badge floating between tabs** | ✔ iteration 5 |
| **D5** | Dismissing made **SAM vanish entirely** | ✔ iteration 5 |

**All five were found by a human holding the phone.** None was reachable by the widget tests that
were already green.

---

## 4. THE PROTOCOL, AND WHERE IT COST SOMETHING

*(Recorded because a protocol that never costs anything is not being followed.)*

- **Idle checks compared per-pixel**, so a clock tick was distinguishable from the Founder picking
  up the phone.
- **One frame that caught the profile sheet was deleted.** *(That is why 36 frames exist and not
  37.)*
- Retention rules, as recorded in the manifest: **no lock-screen or personal-notification
  frames** · **no raw PDF pages; SGK crops inside frames are internal (Founder D4)** · **a PASS
  without an existing frame is downgraded to UNVERIFIED**.
- **0 downgraded claims and 0 manifest warnings** — every PASS has its frame.

---

## 5. GAPS — recorded as gaps, not filled in

| Gap | Status |
|---|---|
| **APK sha256 for iterations 4 and 5** | **NOT CAPTURED.** The manifest records `gitSha` and a note («four builds from the same commit, only `--dart-define=WAL_ASSIST` differs»; «two patches D4 and D5, re-walking exactly the two changed surfaces») but **no `apkSha256`** for those two iterations. Iterations 1–3 have both. |
| **The integrated-build walk** | **NOT PERFORMED.** As in round 4, the device walk is against Lane B's branch build, not the composed round-6 base. |
| **Lane E2's device walk** | **DEFERRED** — Lane B owns the device loop. `VisualSpecView` was handed over as a six-line mount; the §27 checkpoint was substituted by a **machine-generated widget transcript** across three subjects. **This is not device evidence and is not counted as such.** |
| **Whether the round-5 APK is still installed on the Nokia** | **UNAVAILABLE.** Not checked after the walk; the device protocol forbids interrupting the Founder's use of the phone. |
| **Manifest `git.dirty`** | `true` on the manifest's own commit — the working tree was not clean when the manifest was generated. Recorded, not hidden. |
| **Parent-surface device evidence** | **UNAVAILABLE** — no parent surface was walked in round 5. |

---

## 6. WHERE THE FRAMES LIVE, AND WHAT WAS DONE ABOUT PERSONAL DATA

- **In the repository:** `docs/design/track-b-evidence/round5/` — 36 PNGs + `MANIFEST.json` +
  `steps.json`.
- **On the Founder's Desktop:** `~/Desktop/wal-evidence/` — the same 36 files.
- **Verified by the archive builder:** all 36 repository frames hash-match the manifest, **and**
  the Desktop copies are **byte-identical** to the repository copies. *(PROVEN — see
  `evidence/device-frame-verification.txt`.)*

**Personal-data review.** The archive builder opened **3 of the 36 frames** (`round5-1-01-home`,
`round5-2-02-picker`, `round5-2-05-shelf-search`) and found no lock-screen content, no
notifications, no third-party app content and no personal identifiers beyond the learner display
name **«Na»**, which is the Founder's own learner profile and appears by design in the product
greeting («Chào Na!»). **The remaining 33 frames rely on the Lane B retention protocol recorded in
the manifest** — this is stated so the reliance is visible.

**No frame was excluded from this archive on personal-data grounds.** All **36** are included in
`screenshots/`. The one frame that did contain the profile sheet was deleted by Lane B **before**
the manifest was generated, and is therefore not part of the 36.

---

## 7. WHAT THE DEVICE EVIDENCE PROVES — and what it does not

**Proves:** that on a real Nokia 6.1, a child opening Bài 17 sees a real mindmap and a real
process flow; that the workspace density numbers (820 → 712 / 634 px) are device measurements,
not simulations; that four different assistant designs exist and were compared by a human on the
phone; that five defects were fixed and **re-walked**, not merely patched.

**Does not prove:** anything about accuracy. The device ran the **round-4-era `tc2-p1` fixture**
and the **2026-09-05 packs**. **No frame in this archive shows a single round-5 accuracy
correction, because none of them reached a build.**
