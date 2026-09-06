# 06 · PRODUCT REALITY — what actually changed for a human being

> **INTERNAL / RESEARCH ONLY — DO NOT PUBLISH.**

This file answers one question plainly and then refuses to let it be misread:
**what can a child use now that they could not before?**

---

## 1. THE CHILD — the plain answer

**A child can now *see the shape of a lesson* instead of reading a description of it.**

Concretely, on KHTN 6 Bài 17 («Tách chất khỏi hỗn hợp»), on the real Nokia 6.1 that was walked in
this round *(OBSERVED — 36 frames, `screenshots/`, hashes verified)*:

| Before round 5 | After round 5 |
|---|---|
| «Trực quan» showed **text pretending to be a diagram** | A **real mindmap** — hub + four coloured branches + curved edges — and a **real process flow** with nodes, edges and arrows, both compiled from typed `SemanticData` |
| The figure reference was a plain line of text | A **source-grounded figure chip** that **fails closed** when the grounding is absent |
| First lesson content began **820 px** down the screen — 42.7 % of the phone consumed before any lesson content | **712 px** with the assistant peeking, **634 px** collapsed |
| **Seven** occurrences of three view names on one screen, in **two different word sets** («Học **với** SAM» / «Học **cùng** SAM») | **Four** labels |
| A pinned recommendation card **covered the mindmap's own hub** (48 % chrome) | Fixed — 27 % chrome, re-walked on the device |
| Dismissing the assistant made SAM **vanish entirely** | Fixed — three genuine states COLLAPSED → PEEK → EXPANDED, with re-peek when the recommendation moves to a different view |

**That is the whole list.** It is real, it was found and fixed on a physical phone, and it is
**presentation of the same data**.

### What a child did **not** get

- **Not one accuracy correction from this round.** The repair path is not wired into the pipeline
  *(PROVEN structurally: no file outside `tool/corpus/repair/` and `tool/tests/` imports the
  `repair` package)*. The main checkout's packs are still the old ones. **No APK built on this
  Mac carries any of this round's accuracy corrections.**
- **Nothing merged.** All ten round-5 PRs are open; round 4's PR #73 is also still open.
- **Nothing became trustworthy.** `trusted` = **0**, `eligible for teaching` = **0** — unchanged,
  by Founder gate. Source Trust remains **0 of 97** visible elements.
- **The two Founder-named defects are still there.** `II → I1` and `3×10⁸ → 3×10°` are born at
  OCR recognition and no round-5 mechanism reaches them.
- **Bài 17's trust status is unchanged** — still `WITHHELD`-heavy, still 0 trusted. What improved
  is what it **shows**, not what it **claims**.
- **NOT CAPTURED:** whether the round-5 debug APK is still installed on the Nokia today. The
  device protocol forbids interrupting the Founder's use of the phone, and no check was made
  after the walk.

### The honest boundary sentence

> **This round made the same data look better and be better understood. It did not make the data
> a child reads any more correct.**

---

## 2. THE PARENT

**No change.** *(OBSERVED — no parent-facing surface appears in the round-5 device walk, and no
lane's scope includes the parent surfaces.)*

The parent-facing session summary and learning-map surfaces built in earlier rounds are unchanged
by round 5. **Evidence Reality remains 0 of 0** — there are zero validator-permitted interactions
out of zero possible, so there is nothing new for a parent to be shown that would be honest.

**UNAVAILABLE:** no parent-surface measurement was taken in round 5.

---

## 3. SAM (the tutor)

**Pedagogy Reality is flat at 7 / 17 tutor steps runtime-guided.** *(MEASURED, unchanged from
round 4.)*

What changed *around* SAM rather than *in* SAM:

- **SAM no longer occupies a fixed block of the screen.** The recommendation moved from a pinned
  card to an assistant with three states. The Founder selected **option B · peek**.
- **SAM's «why» stopped lying about the medium.** Defect D2: the explanation said «bảng» while a
  mindmap was on screen. Fixed.
- **SAM's explanation stopped asserting a lesson-specific rule as universal.** «vì sao SAM chọn
  sơ đồ này» was keyed on the **Dart type**, so every `ProcessSemantic` was told the book used
  «·» bullets — Bài 17's own rule, asserted for every lesson. **No test caught it: the type is
  right, the widget renders, the sentence is false.** Now keyed on the **rule id**.
- **A structural guarantee about what SAM's renderers can know.** A renderer can no longer branch
  on lesson identity — not because it *should not*, but because at the render boundary block ids
  are replaced by opaque handles and **there is nothing left to read**.

**What SAM still cannot do:** answer freely (no chat), teach from anything the Founder has
authorised as trusted (there is no trust threshold), or use any repaired content (the repair path
is not connected).

---

## 4. INTERNAL / RESEARCH ONLY — the largest category this round

Everything below is real, measured, and **reaches no user**:

| Capability | State | Why it is not product |
|---|---|---|
| A1's repair framework, plugin registry, ledger, Vietnamese repairers | built, CI-green, measured | **not imported by anything outside `tool/corpus/repair/`** |
| A2's math AST, six validators, 10/10 restores | built, CI-green, holdout-verified | the TSL→LessonDocument bridge **has no `formula` role**; the app's block union has no formula member and **fails closed on the whole document** |
| A4's five verification signals + router | built, CI-green, measured | registers into A1's package, which is itself unconnected |
| A3's threshold instrument + sensitivity curve | built, 25 tests | **no point on the curve was chosen — deliberately.** `THRESHOLDS.json` does not exist |
| E1's semantic foundation + K-12 census | built, 285 tests | **LEARNER_READY = 0** by its own census |
| C's `prose-dated-events-v1` / `story-attribution-v1` | PROPOSED, History-only | **falsified as general rules**; correctly never entered the universal bridge |
| D's rebuilt packs (12/12 verify PASS) | built, hash-verified | **not merged**; the main checkout still has the old packs |

**This is the round's central asymmetry and the reason round 6's North Star is what it is:
the capability curve went up sharply and the delivery curve did not move at all.**

---

## 5. THE STRUCTURAL REASONS DELIVERY WAS ZERO — with the line that causes each

*(PROVEN — three of these were re-verified first-hand by the archive builder on the round-6 base
checkout; see `evidence/structural-spot-checks.md`.)*

| Blocker | Location | Consequence |
|---|---|---|
| A single unrecognised block kind rejects the **entire** LessonDocument | `lib/core/lesson_model/lesson_document.dart:1017-1018` — `if (blk == null) return null; // một block hỏng ⇒ không tài liệu nửa vời` | **Deliberate fail-closed design, not a defect.** But it means a pack emitting a new block kind **blanks the lesson** on an older app: **packs and app must ship together.** |
| The TSL→LessonDocument bridge has **no `formula` role** | `tool/corpus/tsl_to_lesson_document.py` — `ROLE_MAP` holds 11 keys, none of them `formula`; the string `formula` appears **0 times** in the file | A validated `MathExpression` has **no path** from corpus to app today |
| The app has **no rich-text capability at all** | `lib/**`, `pubspec.yaml` — **0** Dart files contain `RichText`, `TextSpan` or `Text.rich`; no math, markdown, LaTeX, SVG or WebView dependency | **A superscript or a fraction cannot render correctly even when the data is right** |
| The repair package is imported by nothing outside itself | `tool/corpus/repair/**` | "No served text changed anywhere" is a **certainty of the wiring** |

---

## 6. THE FOUNDER'S OWN TEN CHECKPOINT QUESTIONS — the product-facing answers

Full answers are in `reports/ROUND5-CONSOLIDATED-REPORT-2026-09-06.md` §11. The two that decide
product reality:

**«Trẻ nhìn thấy sản phẩm tốt hơn ở đâu?»** — In three concrete places, all verified on a real
Nokia 6.1 across 36 frames: **Trực quan finally reached the board** (70–80 % → 85–90 %); **the
workspace stops repeating itself** (820 → 712 px peek / 634 px collapsed; six labels for three
views → four); and **five defects only the device could find** were fixed, including a pinned card
covering the very hub of the mindmap it was recommending. **But this is better presentation of
the same data.**

**«Legacy data có tiến gần teaching-ready không?»** — **Closer on measurable accuracy, not closer
to teaching-ready**, and the gap is structural rather than a matter of degree. Three named
reasons: the repair path is not wired in; **R13** means the denominators everyone reports are not
the population a child reads from; and the mutilated-structure class is still open on the lesson
path. **The pack machinery, by contrast, *is* ready** — verify 0/12 FAIL → **12/12 PASS**, the old
baseline reproduced three times, the rebuild's content delta **exactly zero**.

---

## 7. ONE THING THAT GOT WORSE FOR A CHILD, ON PURPOSE

**41 geometry-rebuilt expressions and 10 whole exercise lists left the packs.**

`tool/extract/rebuild_fractions.py:124` stamps every row it writes `status: 'INFERRED'` — «dựng từ
hình học ⇒ KHÔNG phải nguyên văn» — and the pack builder was copying only
`expr / skillCaseId / page / book`. So **41 expressions shipped as if printed in the book**,
carrying a `skillCaseId`, into the exercise path a child is taught from.

Lane D chose **fail closed**: a non-verbatim upstream record is not emitted at all. **10 lessons
lose their exercise list entirely.** Nothing was deleted upstream, every drop is counted and
logged with a reason, and the rows return the moment provenance can travel with them.

**Per the Founder's rule that a coverage drop caused by removing wrong content is a correctness
gain, this is recorded as a gain — with the count named.** A child in those 10 lessons now sees
fewer exercises, and none of them is invented.
