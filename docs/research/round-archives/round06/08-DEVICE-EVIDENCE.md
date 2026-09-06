# 08 · DEVICE EVIDENCE

> **INTERNAL / RESEARCH ONLY — DO NOT PUBLISH.** The 7 frames in `screenshots/` show verbatim SGK
> text rendered inside the app. Under Founder rule **D4** they are internal research material. They
> also carry the learner display name **«Na»** — the Founder's own learner profile on the Founder's
> own device.

---

## 0. THE DISTINCTION THAT MATTERS MOST

**Widget tests and emulators are not real-device evidence.**

Round 6 produced both kinds and this archive keeps them apart:

| Kind | What it proves | What it cannot |
|---|---|---|
| **Widget test** — the 281 dp / 289 dp / 233 dp density figures, measured at a simulated Nokia viewport (392.7 × 698.2 dp) and **runnable in CI** | that the tree lays out as claimed at that viewport | that a real Android renders it that way, or that a child can use it |
| **Real device walk** — Nokia 6.1, 7 frames | what a child actually sees and can touch | nothing about the pipeline or the corpus |

**Every device claim in this archive comes from the second row.** Where a number came from the
widget tree, `05-METRICS-BEFORE-AFTER.md` §6 says so.

---

## 1. THE DEVICE, THE BUILD, THE LESSON, THE LEARNER

*(**PROVEN** — read from `manifests/round6-device-MANIFEST.json`, schema `wal-evidence-manifest-v1`,
`generatedAt 2026-09-06T04:30:13Z`; all 7 frame hashes recomputed by the archive builder.)*

| Field | Value |
|---|---|
| **Device** | **Nokia 6.1**, `Plate2_00WW` |
| OS | **Android 10**, SDK **29** |
| Connection | adb over WiFi, `192.168.1.3:5555` |
| Package | `ai.workizen.learningcoach` *(the phone also carries `com.workizen.tongtai` — do not grep «workizen» to identify it)* |
| **Build** | git **`eac69ea1ad37a6b343e162be9e55d82df7f6db7e`**, branch `ws-d/round6-golden-delivery`, **dirty: false** |
| **APK** | `app-debug.apk`, sha256 **`7b2b2b79a5518a16b9c1605412ebc6064b14326325cdc2d52d1786289e1c1237`**, 245,952,191 bytes |
| **Packs** | **rebuilt before the walk** — `g*-20260906T0424Z-eac69ea1`, `attachmentRule: capped-toc-v2`, verify **12/12 OK** *(PROVEN — all 12 archived pack files hash-match the manifest)* |
| **Lesson** | **LS&ĐL 5 Bài 8** · SGK pages 36–39 · **real fixture**, lineage **PASS** |
| **Fixture** | `lesson-05-sgk-lich-su-va-dia-li-5-b8.json`, sha256 **`a904d0052aa9ff7d…`** · **52 blocks · semantic 0 · tutorSteps 0** *(PROVEN — recomputed)* |
| **Learner state** | **«Na»** — the Founder's own profile, **preserved** (`adb install -r`, not uninstalled) |
| Idle check | **0 of 2,073,600 pixels** differed over 6 seconds ⇒ nobody was using the phone |
| Manifest warnings | **none** |

---

## 2. THE FLOW TESTED — nine steps

| # | Expectation | Result | Frame |
|---|---|---|---|
| 01 | Home, the Founder's profile intact | **PASS** | `round6-01-home.png` |
| 02 | Research-slice card carrying the **real title from the printed table of contents** | **PASS** | `round6-02-home-research.png` |
| 03 | «Vào bài học»: **one** word set for three views; three cards counted from the lesson's own data; experimental chip | **PASS** | `round6-03-picker.png` |
| 04 | **Option B · PEEK** — one line, real SGK text immediately | **PASS** | `round6-04-read-peek.png` |
| 05 | **Option B · EXPANDED** — why + «Đã mở ● ○ ○» + CTA + «Để sau», opening **in place** | **PASS** | `round6-05-read-expanded.png` |
| 06 | **Option B · COLLAPSED** — 💡 moves into the title row and **does not vanish** (round 5's D5) | **PASS** | `round6-06-read-collapsed.png` |
| 07 | «Học với SAM» says honestly it has no script; chrome equal to the other two views | **PASS** | `round6-07-tutor.png` |
| 08 | Per-pixel idle check: nobody is using the device | **UNVERIFIED (downgraded — no frame)** | — |
| **09** | **The 17 gaps carry page crops** | **FAIL** | `round6-04-read-peek.png` |

---

## 3. THE ONE FAIL — recorded as a FAIL, and returned to its owner

**Step 09: the 17 honest gaps have no page crops.** WS-C's document was built with `--no-crops` (or
without a PDF in its sandbox). The gaps show a reason and a page number where an **image of the
printed page was available all along**: WS-D's own bridge builds **20 crops** from the same TSL.

**Status: gap `G1`, returned to WS-C — not patched by WS-D.** This is the round's honest FAIL and it
is not written down as a partial pass.

*(A second, smaller gap `G2`: WS-C's `bookTitle`/`subject` render long («Lịch sử và Địa lí 5»)
because `poc-out/graph/curriculum-structure.json` did not resolve in its sandbox. **Not wrong, just
long.**)*

---

## 4. THE STEP TALLY — this archive reports the manifest, not the prose

| Source | Tally |
|---|---|
| The consolidated report and WS-D's own table | **8 PASS / 1 FAIL** |
| **`MANIFEST.json` `summary`, which is the artefact** | **PASS 7 · FAIL 1 · UNVERIFIED 1 · downgraded 1** *(PROVEN)* |

**Both are honest, and the difference is a rule doing its job.** Step 08 produced no frame, and the
manifest's own retention rule states: *«a PASS without an existing frame is downgraded to
UNVERIFIED».* The tool downgraded it; the prose counted it as passed.

**The archive reports the manifest's tally**, because the manifest is what a later reader can check.
It is a *stricter* reading, not a contradictory one — and it is exactly the behaviour the retention
rule exists to produce.

---

## 5. TWO THINGS THE DEVICE SHOWED THAT NO TEST DID

**(a) SAM tells the child to leave the lesson they just opened.** In all three views the suggestion
read **«SAM gợi ý: Về mục lục»**, and its reason **«Con đã đi qua các cách học của bài này»** —
while the row directly beneath it read **`● Đọc ○ Trực quan ○ Học với SAM`**. The child had opened
**one**. The runtime treats «the other two views have nothing to show» as «already visited».
**Two lines contradicting each other on one card**, and it was *moving «Đã mở» into the expanded
state* that exposed it. Born in `lib/core/agenda/**` — **returned to its owner, not patched here.**

**(b) The lesson title is lowercased at the display layer.** The screen reads «… thời kì **b**ắc
thuộc». A sentence-case rule is being applied to **a historical proper noun, in an app for
children.**

> **The archive builder confirmed this is a display defect, not a data defect: the shipped fixture's
> `title` field reads «Đấu tranh giành độc lập thời kì Bắc thuộc», with a capital B.** *(PROVEN.)*

---

## 6. WHAT THE FRAMES ACTUALLY EVIDENCE

- `round6-04-read-peek.png` alone carries four of the round's claims: **Option B PEEK** (one line,
  no card, no portrait, no repeated CTA) · **real SGK text on pages 36–39** · **an honest gap with
  its reason and a «Vì sao SAM để trống?» affordance and no page crop (G1)** · and **both device-only
  findings above.**
- `round6-03-picker.png` shows the **one word set** and the two honest zeros («Chưa có sơ đồ…»,
  «Chưa có kịch bản…») — *measured on the device, not in a test.*
- `round6-07-tutor.png` shows «Học với SAM» admitting it has no script, at chrome equal to the other
  two views.

---

## 7. PERSONAL-DATA REVIEW

The archive builder opened **2 of the 7 frames** (`round6-01-home.png`, `round6-04-read-peek.png`).

**Found:** the learner display name **«Na»**, which appears by design in the product greeting
(«Chào Na!») and is the Founder's own learner profile; verbatim SGK text (D4 — the reason this
archive is INTERNAL).

**Also found, and recorded rather than glossed:** the Android **status bar carries notification
icons**, including a mail icon. **No notification content, sender, subject or preview is visible** —
only the icons themselves. That is not a leak of personal content, but it is not literally "no
notifications" either, so it is stated here.

**No frame was excluded.** All **7** are in `screenshots/`. The remaining 5 frames rely on the WS-D
retention protocol recorded in the manifest — *stated so the reliance is visible.*

**Retention rules, as recorded in the manifest:** no lock-screen or personal-notification frames ·
no raw PDF pages, SGK crops inside frames are internal (D4) · a PASS without an existing frame is
downgraded to UNVERIFIED. **Manifest warnings: none.**

---

## 8. WHERE THE EVIDENCE LIVES — and a near-miss worth recording

| What | Where | In this archive? |
|---|---|---|
| 7 frames + `MANIFEST.json` + `steps.json` | `~/Desktop/wal-evidence/round6-ws-d/` | **YES** — `screenshots/` and `manifests/` |
| Golden #1 + Bài 17 real fixtures | `~/Desktop/wal-evidence/round6-artefacts/fixtures-real/` | **YES** — `evidence/round6-artefacts/` |
| The 12 GATE E packs, and the 12 stale ones | `~/Desktop/wal-evidence/round6-artefacts/packs*/` | **YES** — `evidence/round6-artefacts/` |

**The near-miss:** `assets/fixtures/real/` and `assets/pack/` are **gitignored**, and the round's
deliverables existed **only inside an ephemeral scratchpad worktree**. The coordinator copied them
to the Desktop before that worktree could be removed. **Had it been cleaned first, GATE E's
artefacts would have been unrecoverable** — the frames would have shown a lesson nobody could
re-derive.

Recorded in `10-OPEN-RISKS-BLOCKERS.md` §4.

---

## 9. WHAT THE DEVICE EVIDENCE PROVES — and what it does not

**Proves:** that on a real Nokia 6.1 a child opens LS&ĐL 5 Bài 8 and reads **real SGK text with
honest gaps**; that Option B ships as one presentation in three states with equal chrome; that the
app states its zeros in a child's words; and — via the fixture hash — that **what was on the phone
is exactly what is archived here**.

**Does not prove:** that the child learns more. `PEDAGOGY REALITY` is unchanged at 7/17,
`EVIDENCE REALITY` 0 of 0, and **the timeline and the tutor script are gone.** *Nothing here is a
measurement on a child.*
